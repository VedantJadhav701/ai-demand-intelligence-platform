"""
MLflowTracker class for initializing experiments, logging parameters, fold metrics,
dataset metadata, feature configurations, and saving model artifacts.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import pandas as pd
import numpy as np
import mlflow
import mlflow.catboost
import mlflow.lightgbm
import mlflow.sklearn
import mlflow.pyfunc

from src.models.base import BaseForecaster
from src.models.ml_models import (
    CatBoostForecaster,
    LightGBMForecaster,
    RandomForestForecaster,
    RidgeRegressionForecaster,
)
from src.models.baselines import NaiveForecaster, SeasonalNaiveForecaster
from src.utils.config import MLflowConfig, AppConfig
from src.tracking.metadata import get_git_metadata, extract_dataset_metadata
from src.utils.logger import get_logger

logger = get_logger("tracking.mlflow_tracker")


class ForecasterPyFuncWrapper(mlflow.pyfunc.PythonModel):
    """MLflow PyFunc wrapper around BaseForecaster instances."""

    def __init__(self, forecaster: BaseForecaster):
        self.forecaster = forecaster

    def predict(self, context, model_input: pd.DataFrame) -> np.ndarray:
        return self.forecaster.predict(model_input)


class MLflowTracker:
    """
    MLflow Tracker orchestrates MLflow experiment creation, run parameter/metric logging,
    feature configuration version tracking, and model artifact logging.
    """

    def __init__(self, config: Optional[MLflowConfig] = None, tracking_uri: Optional[str] = None):
        self.config = config or MLflowConfig()
        self.tracking_uri = tracking_uri or self.config.tracking_uri

        # Enable file store backend if file URI is used
        os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"

        # If sqlite URI is used, ensure database directory exists
        if self.tracking_uri.startswith("sqlite:///"):
            db_path = Path(self.tracking_uri.replace("sqlite:///", ""))
            if db_path.parent:
                db_path.parent.mkdir(parents=True, exist_ok=True)

        mlflow.set_tracking_uri(self.tracking_uri)

        # Set or create experiment
        self.experiment_name = self.config.experiment_name
        self.experiment = mlflow.get_experiment_by_name(self.experiment_name)
        if self.experiment is None:
            exp_id = mlflow.create_experiment(
                name=self.experiment_name,
                artifact_location=self.config.artifact_location,
            )
            self.experiment = mlflow.get_experiment(exp_id)

        mlflow.set_experiment(self.experiment_name)
        logger.info(
            f"MLflowTracker initialized. Tracking URI: '{self.tracking_uri}', Experiment: '{self.experiment_name}'"
        )

    def start_run(
        self,
        run_name: str,
        tags: Optional[Dict[str, str]] = None,
        nested: bool = False,
    ) -> mlflow.ActiveRun:
        """
        Starts an MLflow run with run_name and default/custom tags.

        Args:
            run_name: Human-readable run name (e.g. 'catboost_h1_phase4_optuna').
            tags: Custom tag dictionary.
            nested: Whether run is nested under a parent run.

        Returns:
            mlflow.ActiveRun: Active MLflow run object.
        """
        run_tags = {
            "feature_version": self.config.feature_version,
            "code_version": get_git_metadata().get("git_commit", "unknown"),
        }
        if tags:
            run_tags.update(tags)

        return mlflow.start_run(run_name=run_name, tags=run_tags, nested=nested)

    def log_feature_config(
        self,
        feature_version: Optional[str] = None,
        lags: Optional[List[int]] = None,
        rolling_windows: Optional[List[int]] = None,
        rolling_stats: Optional[List[str]] = None,
        include_temporal: bool = True,
        categorical_features: Optional[List[str]] = None,
    ) -> None:
        """Logs feature engineering configuration parameters and explicitly records excluded revenue."""
        f_version = feature_version or self.config.feature_version
        mlflow.log_params(
            {
                "feature_version": f_version,
                "lag_features": str(lags or [1, 7, 14, 28]),
                "rolling_features": str(rolling_windows or [7, 14, 28]),
                "rolling_statistics": str(rolling_stats or ["mean", "std", "min", "max"]),
                "include_temporal": include_temporal,
                "categorical_features": str(
                    categorical_features
                    or ["store_type", "product_category", "store_id", "product_id", "region"]
                ),
                "excluded_features": "units_sold, revenue (target leakage prevention)",
                "revenue": "excluded",
            }
        )

    def log_dataset_metadata(
        self, df: pd.DataFrame, dataset_path: str = "data/raw/sample_sales_data.csv"
    ) -> None:
        """Logs dataset metadata and fingerprint identifier to MLflow parameters."""
        meta = extract_dataset_metadata(df, dataset_path=dataset_path)
        mlflow.log_params(
            {
                "dataset_name": meta["dataset_name"],
                "dataset_identifier": meta["dataset_identifier"],
                "dataset_hash": meta["dataset_hash"],
                "row_count": meta["row_count"],
                "column_count": meta["column_count"],
                "date_min": meta["date_min"],
                "date_max": meta["date_max"],
                "store_count": meta["store_count"],
                "product_count": meta["product_count"],
            }
        )

    def log_model_params(self, forecaster: BaseForecaster, extra_params: Optional[Dict[str, Any]] = None) -> None:
        """Logs all model parameters and hyperparameters to MLflow."""
        params: Dict[str, Any] = {
            "model_name": forecaster.name,
            "model_class": forecaster.__class__.__name__,
        }

        # Model hyperparams
        model_params = forecaster.get_params()
        for k, v in model_params.items():
            if k not in ["verbose", "verbosity", "n_jobs", "random_state", "random_seed"]:
                params[f"param_{k}"] = v

        if extra_params:
            for k, v in extra_params.items():
                params[k] = str(v) if isinstance(v, (list, dict)) else v

        mlflow.log_params(params)

    def log_evaluation_metrics(
        self,
        cv_wape: float,
        cv_mae: float,
        cv_rmse: float,
        cv_smape: float,
        cv_mape: float,
        test_wape: Optional[float] = None,
        test_mae: Optional[float] = None,
        test_rmse: Optional[float] = None,
        test_smape: Optional[float] = None,
        test_mape: Optional[float] = None,
        training_time_sec: Optional[float] = None,
        inference_time_sec: Optional[float] = None,
        fold_metrics: Optional[List[Dict[str, float]]] = None,
    ) -> None:
        """Logs cross-validation metrics, final test metrics, fold-level metrics, and timings."""
        metrics: Dict[str, float] = {
            "cv_wape": float(cv_wape),
            "cv_mae": float(cv_mae),
            "cv_rmse": float(cv_rmse),
            "cv_smape": float(cv_smape),
            "cv_mape": float(cv_mape),
        }

        if test_wape is not None:
            metrics["test_wape"] = float(test_wape)
        if test_mae is not None:
            metrics["test_mae"] = float(test_mae)
        if test_rmse is not None:
            metrics["test_rmse"] = float(test_rmse)
        if test_smape is not None:
            metrics["test_smape"] = float(test_smape)
        if test_mape is not None:
            metrics["test_mape"] = float(test_mape)

        if training_time_sec is not None:
            metrics["training_time_seconds"] = float(training_time_sec)
        if inference_time_sec is not None:
            metrics["inference_time_seconds"] = float(inference_time_sec)

        # Fold-level validation metrics
        if fold_metrics:
            for i, f_dict in enumerate(fold_metrics, 1):
                for m_k, m_v in f_dict.items():
                    metrics[f"fold_{i}_{m_k.lower()}"] = float(m_v)

        mlflow.log_metrics(metrics)

    def log_model_artifact(
        self, forecaster: BaseForecaster, artifact_path: str = "model"
    ) -> Any:
        """
        Logs forecaster model artifact using MLflow PyFunc flavor.
        Logs the ForecasterPyFuncWrapper to preserve full feature preprocessing and type casting.

        Args:
            forecaster: Fitted BaseForecaster instance.
            artifact_path: Subdirectory inside MLflow run artifact store.

        Returns:
            Any: Saved model info.
        """
        logger.info(f"Logging model artifact '{forecaster.name}' to MLflow path '{artifact_path}'...")
        wrapper = ForecasterPyFuncWrapper(forecaster=forecaster)
        return mlflow.pyfunc.log_model(python_model=wrapper, artifact_path=artifact_path)
