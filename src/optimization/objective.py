"""
Time-series aware Optuna objective function running walk-forward CV per trial.
"""

from typing import Dict, Any
import optuna

from src.models.dataset import ForecastingDataset
from src.models.factory import ModelFactory
from src.evaluation.splitter import SplitResult
from src.evaluation.walk_forward import WalkForwardEvaluator
from src.utils.logger import get_logger

logger = get_logger("optimization.objective")


def get_search_space(trial: optuna.Trial, model_name: str, seed: int = 42) -> Dict[str, Any]:
    """
    Defines bounded hyperparameter search space per model type.

    Args:
        trial: Optuna trial object.
        model_name: Target model identifier ('catboost', 'lightgbm', 'random_forest').
        seed: Random seed.

    Returns:
        Dict[str, Any]: Sampled hyperparameter dictionary.
    """
    key = model_name.lower().strip()

    if key == "catboost":
        return {
            "depth": trial.suggest_int("depth", 4, 8),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
            "iterations": trial.suggest_int("iterations", 50, 200, step=25),
            "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1.0, 10.0),
            "random_seed": seed,
            "verbose": 0,
        }
    elif key == "lightgbm":
        return {
            "num_leaves": trial.suggest_int("num_leaves", 15, 63),
            "max_depth": trial.suggest_int("max_depth", 3, 8),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
            "n_estimators": trial.suggest_int("n_estimators", 50, 200, step=25),
            "min_child_samples": trial.suggest_int("min_child_samples", 5, 30),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "random_state": seed,
            "verbosity": -1,
        }
    elif key == "random_forest":
        return {
            "n_estimators": trial.suggest_int("n_estimators", 50, 150, step=25),
            "max_depth": trial.suggest_int("max_depth", 4, 12),
            "min_samples_split": trial.suggest_int("min_samples_split", 2, 10),
            "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 5),
            "random_state": seed,
            "n_jobs": -1,
        }
    else:
        raise ValueError(f"Model '{model_name}' is not supported for Optuna optimization.")


class TimeSeriesObjective:
    """
    Optuna objective wrapper that evaluates trial parameters using expanding
    walk-forward cross-validation on the train/val pool.
    """

    def __init__(
        self,
        model_name: str,
        dataset: ForecastingDataset,
        split_result: SplitResult,
        seed: int = 42,
    ):
        self.model_name = model_name
        self.dataset = dataset
        self.split_result = split_result
        self.seed = seed
        self.evaluator = WalkForwardEvaluator()

    def __call__(self, trial: optuna.Trial) -> float:
        """
        Executes an Optuna trial evaluation.

        Args:
            trial: Optuna trial object.

        Returns:
            float: Mean validation WAPE across walk-forward folds (minimized).
        """
        params = get_search_space(trial, self.model_name, seed=self.seed)

        # Create model with trial parameters
        model = ModelFactory.create(self.model_name, **params)

        # Run Walk-Forward Cross Validation strictly on train_val_indices
        cv_result = self.evaluator.evaluate_cv(
            model=model, dataset=self.dataset, split_result=self.split_result
        )

        # Record secondary metrics into trial user attributes
        trial.set_user_attr("mae", cv_result.mean_metrics.mae)
        trial.set_user_attr("rmse", cv_result.mean_metrics.rmse)
        trial.set_user_attr("smape", cv_result.mean_metrics.smape)
        trial.set_user_attr("wape", cv_result.mean_metrics.wape)
        trial.set_user_attr("train_time_sec", cv_result.total_train_time_sec)
        trial.set_user_attr("inference_time_sec", cv_result.total_inference_time_sec)

        return cv_result.mean_metrics.wape
