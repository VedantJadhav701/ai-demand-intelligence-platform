"""
OptunaOptimizer managing studies, trial execution, and result collection per model and horizon.
"""

import time
from typing import Dict, Any, List, Optional
import optuna
from pydantic import BaseModel, Field

from src.models.dataset import ForecastingDataset
from src.evaluation.splitter import SplitResult
from src.optimization.objective import TimeSeriesObjective
from src.utils.logger import get_logger

logger = get_logger("optimization.search")


class OptimizationTrialRecord(BaseModel):
    model: str
    horizon: int
    trial_number: int
    wape: float
    mae: float
    rmse: float
    smape: float
    train_time_sec: float
    inference_time_sec: float
    params: Dict[str, Any]


class OptimizationSearchResult(BaseModel):
    model: str
    horizon: int
    best_wape: float
    best_params: Dict[str, Any]
    total_trials: int
    duration_sec: float
    trials: List[OptimizationTrialRecord] = Field(default_factory=list)


class OptunaOptimizer:
    """Class for configuring and running Optuna hyperparameter optimization studies."""

    def __init__(self, seed: int = 42, sampler_name: str = "TPESampler"):
        self.seed = seed
        self.sampler_name = sampler_name

    def optimize_model(
        self,
        model_name: str,
        dataset: ForecastingDataset,
        split_result: SplitResult,
        n_trials: int = 10,
    ) -> OptimizationSearchResult:
        """
        Runs Optuna study for a specified model and horizon.

        Args:
            model_name: Name of model ('catboost', 'lightgbm', 'random_forest').
            dataset: ForecastingDataset container for horizon h.
            split_result: TimeSeriesSplitter SplitResult containing CV folds.
            n_trials: Number of Optuna trials to run.

        Returns:
            OptimizationSearchResult: Optimization trial records and best parameters.
        """
        logger.info(
            f"Starting Optuna search for '{model_name}' on horizon h={dataset.horizon} ({n_trials} trials)..."
        )
        optuna.logging.set_verbosity(optuna.logging.WARNING)

        sampler = optuna.samplers.TPESampler(seed=self.seed)
        study = optuna.create_study(direction="minimize", sampler=sampler)

        objective = TimeSeriesObjective(
            model_name=model_name,
            dataset=dataset,
            split_result=split_result,
            seed=self.seed,
        )

        t0 = time.perf_counter()
        study.optimize(objective, n_trials=n_trials)
        duration = time.perf_counter() - t0

        best_trial = study.best_trial
        trial_records: List[OptimizationTrialRecord] = []

        for tr in study.trials:
            if tr.state == optuna.trial.TrialState.COMPLETE:
                trial_records.append(
                    OptimizationTrialRecord(
                        model=model_name,
                        horizon=dataset.horizon,
                        trial_number=tr.number,
                        wape=round(float(tr.value), 4),
                        mae=round(float(tr.user_attrs.get("mae", 0.0)), 4),
                        rmse=round(float(tr.user_attrs.get("rmse", 0.0)), 4),
                        smape=round(float(tr.user_attrs.get("smape", 0.0)), 4),
                        train_time_sec=round(
                            float(tr.user_attrs.get("train_time_sec", 0.0)), 4
                        ),
                        inference_time_sec=round(
                            float(tr.user_attrs.get("inference_time_sec", 0.0)), 4
                        ),
                        params=tr.params,
                    )
                )

        logger.info(
            f"Optuna search for '{model_name}' (h={dataset.horizon}d) completed in {duration:.2f}s. "
            f"Best WAPE: {best_trial.value:.2f}%"
        )

        return OptimizationSearchResult(
            model=model_name,
            horizon=dataset.horizon,
            best_wape=round(float(best_trial.value), 4),
            best_params=best_trial.params,
            total_trials=len(trial_records),
            duration_sec=round(duration, 2),
            trials=trial_records,
        )
