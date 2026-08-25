"""
MonitoringService: High-level service layer for baseline data loading,
live inference logging, and executing model drift and residual health checks.
"""

import os
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
import numpy as np
import pandas as pd

from src.utils.config import AppConfig, load_config
from src.utils.logger import get_logger
from src.data.ingestion import DataIngestor
from src.features.builder import FeatureEngineer
from src.monitoring.drift_detector import DriftDetector, ModelHealthReport

logger = get_logger("services.monitoring_service")


class MonitoringService:
    """
    Service layer for managing reference distributions, inference logging buffers,
    and generating model health & drift reports.
    """

    KEY_MONITORING_FEATURES: List[str] = [
        "price",
        "discount",
        "promotion",
        "lag_1",
        "lag_7",
        "lag_28",
        "rolling_mean_7",
        "rolling_mean_28",
        "store_type",
        "product_category",
    ]

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or load_config()
        self.detector = DriftDetector()
        self._lock = threading.Lock()

        # Load reference baseline dataset
        self._ref_df: Optional[pd.DataFrame] = None
        self._ref_preds: Optional[np.ndarray] = None
        self._recent_logs: List[Dict[str, Any]] = []

        self._initialize_baseline()

    def _initialize_baseline(self) -> None:
        """Loads and pre-calculates reference feature distributions from sample sales dataset."""
        try:
            raw_path = self.config.data.raw_data_path
            if Path(raw_path).exists():
                ingestor = DataIngestor(self.config.data)
                raw_df = ingestor.load_data(raw_path)

                engineer = FeatureEngineer()
                self._ref_df = engineer.transform(raw_df)

                # Generate reference synthetic predictions for baseline if target exists
                if "units_sold" in self._ref_df.columns:
                    # Baseline reference predictions can be approximated by lag_1 or rolling_mean_7
                    if "lag_1" in self._ref_df.columns:
                        self._ref_preds = self._ref_df["lag_1"].dropna().to_numpy()
                    else:
                        self._ref_preds = self._ref_df["units_sold"].dropna().to_numpy()

                logger.info(
                    f"MonitoringService initialized baseline from '{raw_path}' ({len(self._ref_df)} records)."
                )
            else:
                logger.warning(
                    f"Baseline data not found at '{raw_path}'. MonitoringService using empty reference."
                )
                self._ref_df = pd.DataFrame()
                self._ref_preds = np.array([])
        except Exception as e:
            logger.error(f"Failed to initialize monitoring baseline: {e}")
            self._ref_df = pd.DataFrame()
            self._ref_preds = np.array([])

    def log_inference_event(
        self,
        features: Dict[str, Any],
        prediction: float,
        actual: Optional[float] = None,
    ) -> None:
        """
        Logs a live inference request to the in-memory monitoring buffer.

        Args:
            features: Dictionary of input feature values.
            prediction: Predicted target value.
            actual: Optional ground truth target value if available.
        """
        event = dict(features)
        event["__prediction"] = float(prediction)
        if actual is not None:
            event["__actual"] = float(actual)

        with self._lock:
            self._recent_logs.append(event)
            # Retain last 1,000 requests in buffer
            if len(self._recent_logs) > 1000:
                self._recent_logs.pop(0)

    def get_drift_report(
        self, current_df: Optional[pd.DataFrame] = None
    ) -> ModelHealthReport:
        """
        Generates comprehensive model health and drift report.

        Args:
            current_df: Optional current DataFrame. If None, uses in-memory inference buffer or sample split.

        Returns:
            ModelHealthReport: Aggregated health report.
        """
        ref_df = self._ref_df if self._ref_df is not None else pd.DataFrame()

        # If current_df not provided, construct from recent logs or split reference
        if current_df is None or len(current_df) == 0:
            with self._lock:
                if len(self._recent_logs) >= 5:
                    curr_df = pd.DataFrame(self._recent_logs)
                else:
                    # Fallback: split baseline into reference (first 80%) and current (last 20%)
                    if len(ref_df) > 20:
                        split_idx = int(len(ref_df) * 0.8)
                        ref_df_split = ref_df.iloc[:split_idx]
                        curr_df = ref_df.iloc[split_idx:]
                        ref_df = ref_df_split
                    else:
                        curr_df = ref_df.copy()

        else:
            curr_df = current_df

        # Filter monitoring features present in dataframes
        valid_features = [
            f for f in self.KEY_MONITORING_FEATURES if f in ref_df.columns and f in curr_df.columns
        ]
        if not valid_features:
            valid_features = [
                c for c in ref_df.columns if c in curr_df.columns and c not in ["date", "units_sold"]
            ][:10]

        # Extract predictions & actuals if available
        ref_preds = self._ref_preds
        curr_preds = (
            curr_df["__prediction"].to_numpy()
            if "__prediction" in curr_df.columns
            else (curr_df["lag_1"].to_numpy() if "lag_1" in curr_df.columns else None)
        )

        actuals = (
            curr_df["__actual"].to_numpy()
            if "__actual" in curr_df.columns
            else (curr_df["units_sold"].dropna().to_numpy() if "units_sold" in curr_df.columns else None)
        )
        preds_for_res = (
            curr_preds
            if curr_preds is not None
            else (curr_df["lag_1"].dropna().to_numpy() if "lag_1" in curr_df.columns else None)
        )

        # Truncate actuals & predictions to matching length if evaluating residuals
        if actuals is not None and preds_for_res is not None:
            min_len = min(len(actuals), len(preds_for_res))
            actuals = actuals[:min_len]
            preds_for_res = preds_for_res[:min_len]

        report = self.detector.evaluate_health(
            reference_df=ref_df,
            current_df=curr_df,
            reference_preds=ref_preds,
            current_preds=curr_preds,
            actuals=actuals,
            predictions=preds_for_res,
            key_features=valid_features,
        )

        return report
