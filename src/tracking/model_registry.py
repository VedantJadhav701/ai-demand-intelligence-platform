"""
ModelRegistrar class for registering horizon-specific production candidates, attaching metadata tags,
assigning production aliases, generating selected_models.json manifests, and verifying model loading.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List, Union
import pandas as pd
import numpy as np
import mlflow
from mlflow.tracking import MlflowClient
from pydantic import BaseModel

from src.utils.config import MLflowConfig
from src.utils.logger import get_logger

logger = get_logger("tracking.model_registry")


class RegisteredModelInfo(BaseModel):
    horizon: int
    model_name: str
    run_id: str
    registry_name: str
    version: str
    selection_source: str
    cv_wape: float
    test_wape: float
    feature_version: str
    dataset_identifier: str
    code_version: str
    aliases: List[str]


class ModelRegistrar:
    """
    ModelRegistrar handles registering horizon-specific model artifacts in MLflow Model Registry,
    attaching version tags, assigning aliases, generating manifests, and conducting model load tests.
    """

    def __init__(
        self,
        config: Optional[MLflowConfig] = None,
        tracking_uri: Optional[str] = None,
        output_dir: Union[str, Path] = "data/outputs/model_registry",
    ):
        self.config = config or MLflowConfig()
        self.tracking_uri = tracking_uri or self.config.tracking_uri
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"
        mlflow.set_tracking_uri(self.tracking_uri)
        self.client = MlflowClient(tracking_uri=self.tracking_uri)

    def get_registry_name(self, model_name: str, horizon: int) -> str:
        """Constructs horizon-specific registered model name (e.g. 'demand-catboost-h14')."""
        prefix = self.config.registry_name_prefix.strip().rstrip("-")
        m_clean = model_name.lower().replace("_", "")
        return f"{prefix}-{m_clean}-h{horizon}"

    def register_candidate_model(
        self,
        run_id: str,
        model_name: str,
        horizon: int,
        selection_source: str,
        cv_wape: float,
        test_wape: float,
        dataset_identifier: str = "sample_sales_data",
        code_version: str = "unknown",
        model_artifact_path: str = "model",
        aliases: Optional[List[str]] = None,
    ) -> RegisteredModelInfo:
        """
        Registers a trained model run in MLflow Model Registry, attaches metadata tags, and sets aliases.

        Args:
            run_id: MLflow run ID.
            model_name: Base model name ('catboost', etc.).
            horizon: Forecast horizon (1, 7, 14, 30).
            selection_source: Source of candidate ('phase3_baseline' or 'phase4_optuna').
            cv_wape: Cross-validation WAPE score.
            test_wape: Final test WAPE score.
            dataset_identifier: Dataset ID string.
            code_version: Git commit hash or code version string.
            model_artifact_path: Artifact path within run.
            aliases: List of aliases to assign ('production', 'staging', 'candidate').

        Returns:
            RegisteredModelInfo: Registration result object.
        """
        reg_name = self.get_registry_name(model_name, horizon)
        model_uri = f"runs:/{run_id}/{model_artifact_path}"

        logger.info(f"Registering model version '{reg_name}' from URI '{model_uri}'...")

        # 1. Create or register model version
        mv = mlflow.register_model(model_uri=model_uri, name=reg_name)

        # 2. Attach Model Version Tags
        tags = {
            "model": model_name,
            "horizon": str(horizon),
            "feature_version": self.config.feature_version,
            "dataset_identifier": dataset_identifier,
            "selection_source": selection_source,
            "cv_wape": str(round(cv_wape, 4)),
            "test_wape": str(round(test_wape, 4)),
            "code_version": code_version,
            "revenue": "excluded",
        }

        for k, v in tags.items():
            self.client.set_model_version_tag(
                name=reg_name, version=mv.version, key=k, value=v
            )

        # 3. Assign Aliases ('production', 'staging', 'candidate')
        alias_list = aliases or ["candidate", "staging", "production"]
        for alias in alias_list:
            try:
                self.client.set_registered_model_alias(
                    name=reg_name, alias=alias, version=mv.version
                )
                logger.info(
                    f"Assigned alias '{alias}' to registered model '{reg_name}' version {mv.version}."
                )
            except Exception as e:
                logger.warning(
                    f"Could not set alias '{alias}' on registered model '{reg_name}': {e}"
                )

        info = RegisteredModelInfo(
            horizon=horizon,
            model_name=model_name,
            run_id=run_id,
            registry_name=reg_name,
            version=str(mv.version),
            selection_source=selection_source,
            cv_wape=round(cv_wape, 4),
            test_wape=round(test_wape, 4),
            feature_version=self.config.feature_version,
            dataset_identifier=dataset_identifier,
            code_version=code_version,
            aliases=alias_list,
        )

        return info

    def generate_manifests(
        self, registered_models: List[RegisteredModelInfo]
    ) -> Tuple[Path, Path]:
        """
        Generates machine-readable selected_models.json and registration_report.json manifests.

        Args:
            registered_models: List of RegisteredModelInfo records.

        Returns:
            Tuple[Path, Path]: Paths to selected_models.json and registration_report.json.
        """
        selected_manifest: Dict[str, Dict[str, Any]] = {}
        report_manifest: Dict[str, Any] = {
            "status": "COMPLETED",
            "total_registered_models": len(registered_models),
            "registry_prefix": self.config.registry_name_prefix,
            "tracking_uri": self.tracking_uri,
            "models": [],
        }

        for reg in registered_models:
            selected_manifest[str(reg.horizon)] = {
                "model": reg.model_name,
                "source": reg.selection_source,
                "registry_name": reg.registry_name,
                "version": reg.version,
                "cv_wape": reg.cv_wape,
                "test_wape": reg.test_wape,
            }
            report_manifest["models"].append(reg.model_dump())

        manifest_path = self.output_dir / "selected_models.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(selected_manifest, f, indent=2)

        report_path = self.output_dir / "registration_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_manifest, f, indent=2)

        logger.info(f"Generated registry manifests at {self.output_dir.resolve()}")
        return manifest_path, report_path

    def verify_model_loading(
        self,
        registry_name: str,
        alias: str = "production",
        version: Optional[str] = None,
        X_fixture: Optional[pd.DataFrame] = None,
    ) -> Tuple[bool, Any, Optional[str]]:
        """
        Loads a registered model version from MLflow Model Registry and executes test prediction.

        Args:
            registry_name: Name of registered model (e.g. 'demand-catboost-h14').
            alias: Alias tag to load ('production', 'staging', 'candidate').
            version: Optional explicit version string.
            X_fixture: Sample DataFrame fixture for running inference test.

        Returns:
            Tuple[bool, Any, Optional[str]]: (is_successful, predictions, error_message)
        """
        if version:
            model_uri = f"models:/{registry_name}/{version}"
        else:
            model_uri = f"models:/{registry_name}@{alias}"

        logger.info(f"Verifying model loading from URI: '{model_uri}'...")

        try:
            loaded_model = mlflow.pyfunc.load_model(model_uri)

            # Create dummy feature row if fixture not provided
            if X_fixture is None:
                dummy_row = {
                    "day_of_week": 1,
                    "day_of_month": 15,
                    "week_of_year": 3,
                    "month": 1,
                    "quarter": 1,
                    "year": 2026,
                    "is_weekend": 0,
                    "is_month_start": 0,
                    "is_month_end": 0,
                    "lag_1": 25.0,
                    "lag_7": 24.0,
                    "lag_14": 22.0,
                    "lag_28": 20.0,
                    "rolling_mean_7": 23.5,
                    "rolling_std_7": 1.2,
                    "rolling_min_7": 20.0,
                    "rolling_max_7": 26.0,
                    "rolling_mean_14": 22.0,
                    "rolling_std_14": 1.5,
                    "rolling_min_14": 19.0,
                    "rolling_max_14": 27.0,
                    "rolling_mean_28": 21.0,
                    "rolling_std_28": 1.8,
                    "rolling_min_28": 18.0,
                    "rolling_max_28": 28.0,
                    "price": 20.0,
                    "discount": 0.0,
                    "price_change": 0.0,
                    "discount_change": 0.0,
                    "store_id": "S1",
                    "product_id": "P1",
                }
                X_fixture = pd.DataFrame([dummy_row])

            preds = loaded_model.predict(X_fixture)
            logger.info(
                f"Model load verification SUCCESS for '{model_uri}'. Prediction output: {preds}"
            )
            return True, preds, None
        except Exception as e:
            logger.error(f"Model load verification FAILED for '{model_uri}': {e}")
            return False, None, str(e)
