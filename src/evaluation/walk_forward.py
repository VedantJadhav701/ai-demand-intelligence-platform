"""
Walk-Forward Evaluator executing cross-validation and final test evaluations.
"""

import time
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from pydantic import BaseModel

from src.models.base import BaseForecaster
from src.models.dataset import ForecastingDataset
from src.evaluation.splitter import SplitResult, FoldSplit
from src.evaluation.metrics import calculate_all_metrics, MetricResult
from src.evaluation.predictions import PredictionStore
from src.utils.logger import get_logger

logger = get_logger("evaluation.walk_forward")


class FoldResult(BaseModel):
    fold_index: int
    train_dates: Tuple[str, str]
    val_dates: Tuple[str, str]
    train_count: int
    val_count: int
    metrics: MetricResult
    train_time_sec: float
    inference_time_sec: float


class WalkForwardResult(BaseModel):
    model_name: str
    horizon: int
    mean_metrics: MetricResult
    fold_results: List[FoldResult]
    total_train_time_sec: float
    total_inference_time_sec: float


class FinalTestResult(BaseModel):
    model_name: str
    horizon: int
    test_dates: Tuple[str, str]
    test_count: int
    metrics: MetricResult
    train_time_sec: float
    inference_time_sec: float


class WalkForwardEvaluator:
    """Class for performing walk-forward cross validation and final test set evaluations."""

    def __init__(self, prediction_store: Optional[PredictionStore] = None):
        self.prediction_store = prediction_store or PredictionStore()

    def evaluate_cv(
        self,
        model: BaseForecaster,
        dataset: ForecastingDataset,
        split_result: SplitResult,
    ) -> WalkForwardResult:
        """
        Evaluates model across walk-forward CV folds.

        Args:
            model: Unfitted or reusable BaseForecaster model instance.
            dataset: ForecastingDataset container.
            split_result: SplitResult containing walk-forward folds.

        Returns:
            WalkForwardResult: Aggregated cross-validation result.
        """
        logger.info(
            f"Evaluating model '{model.name}' on horizon h={dataset.horizon} across {len(split_result.folds)} CV folds..."
        )

        fold_results: List[FoldResult] = []
        total_train_time = 0.0
        total_inf_time = 0.0

        for fold_split in split_result.folds:
            # Extract train & val feature matrices and target series
            X_tr = dataset.X.iloc[fold_split.train_indices].copy()
            y_tr = dataset.y.iloc[fold_split.train_indices].copy()

            X_val = dataset.X.iloc[fold_split.val_indices].copy()
            y_val = dataset.y.iloc[fold_split.val_indices].copy()
            meta_val = dataset.meta.iloc[fold_split.val_indices].copy()

            # Train timing
            t0 = time.perf_counter()
            model.fit(X_tr, y_tr)
            train_time = time.perf_counter() - t0

            # Inference timing
            t1 = time.perf_counter()
            preds_val = model.predict(X_val)
            inf_time = time.perf_counter() - t1

            total_train_time += train_time
            total_inf_time += inf_time

            # Compute fold metrics
            metrics = calculate_all_metrics(y_val.values, preds_val)

            # Record predictions
            self.prediction_store.add_predictions(
                meta=meta_val,
                actuals=y_val.values,
                predictions=preds_val,
                model_name=model.name,
                horizon=dataset.horizon,
                fold=fold_split.fold_index,
            )

            fold_results.append(
                FoldResult(
                    fold_index=fold_split.fold_index,
                    train_dates=fold_split.train_dates,
                    val_dates=fold_split.val_dates,
                    train_count=len(X_tr),
                    val_count=len(X_val),
                    metrics=metrics,
                    train_time_sec=round(train_time, 4),
                    inference_time_sec=round(inf_time, 4),
                )
            )

        # Aggregate mean metrics across folds
        mean_mae = float(np.mean([f.metrics.mae for f in fold_results]))
        mean_rmse = float(np.mean([f.metrics.rmse for f in fold_results]))
        mean_mape = float(np.mean([f.metrics.mape for f in fold_results]))
        mean_smape = float(np.mean([f.metrics.smape for f in fold_results]))
        mean_wape = float(np.mean([f.metrics.wape for f in fold_results]))

        mean_metrics = MetricResult(
            mae=round(mean_mae, 4),
            rmse=round(mean_rmse, 4),
            mape=round(mean_mape, 4),
            smape=round(mean_smape, 4),
            wape=round(mean_wape, 4),
        )

        return WalkForwardResult(
            model_name=model.name,
            horizon=dataset.horizon,
            mean_metrics=mean_metrics,
            fold_results=fold_results,
            total_train_time_sec=round(total_train_time, 4),
            total_inference_time_sec=round(total_inf_time, 4),
        )

    def evaluate_test(
        self,
        model: BaseForecaster,
        dataset: ForecastingDataset,
        split_result: SplitResult,
    ) -> FinalTestResult:
        """
        Evaluates fitted or re-trained model on the untouched final test set.

        Args:
            model: Forecaster model instance.
            dataset: ForecastingDataset container.
            split_result: SplitResult containing test indices.

        Returns:
            FinalTestResult: Performance metrics on untouched test set.
        """
        logger.info(
            f"Evaluating model '{model.name}' on untouched final test set (horizon h={dataset.horizon})..."
        )

        # Train on full train/val pool
        X_tr = dataset.X.iloc[split_result.train_val_indices].copy()
        y_tr = dataset.y.iloc[split_result.train_val_indices].copy()

        X_te = dataset.X.iloc[split_result.test_indices].copy()
        y_te = dataset.y.iloc[split_result.test_indices].copy()
        meta_te = dataset.meta.iloc[split_result.test_indices].copy()

        t0 = time.perf_counter()
        model.fit(X_tr, y_tr)
        train_time = time.perf_counter() - t0

        t1 = time.perf_counter()
        preds_te = model.predict(X_te)
        inf_time = time.perf_counter() - t1

        metrics = calculate_all_metrics(y_te.values, preds_te)

        # Record test predictions (fold=0)
        self.prediction_store.add_predictions(
            meta=meta_te,
            actuals=y_te.values,
            predictions=preds_te,
            model_name=model.name,
            horizon=dataset.horizon,
            fold=0,
        )

        return FinalTestResult(
            model_name=model.name,
            horizon=dataset.horizon,
            test_dates=split_result.test_dates,
            test_count=len(X_te),
            metrics=metrics,
            train_time_sec=round(train_time, 4),
            inference_time_sec=round(inf_time, 4),
        )
