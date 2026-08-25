"""
DriftDetector: Statistical engine for computing Feature Drift (PSI, KS-test),
Prediction Drift, Residual Analysis, and Forecast Bias tracking.
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats
from pydantic import BaseModel, Field

from src.utils.logger import get_logger

logger = get_logger("monitoring.drift_detector")


class FeatureDriftResult(BaseModel):
    feature_name: str
    psi: float = Field(..., description="Population Stability Index")
    ks_statistic: Optional[float] = Field(None, description="KS test statistic")
    p_value: Optional[float] = Field(None, description="KS test p-value")
    status: str = Field(..., description="NO_DRIFT, MODERATE_DRIFT, or SIGNIFICANT_DRIFT")
    message: str


class PredictionDriftResult(BaseModel):
    mean_reference: float
    mean_current: float
    variance_reference: float
    variance_current: float
    psi: float
    ks_statistic: float
    p_value: float
    status: str
    message: str


class ResidualAnalysisResult(BaseModel):
    sample_count: int
    mae: float
    rmse: float
    wape: float
    mean_residual: float = Field(..., description="Mean forecast error (actual - predicted)")
    forecast_bias: float = Field(..., description="Normalized forecast bias: sum(error) / sum(|error|)")
    tracking_signal: float = Field(..., description="Tracking Signal: sum(error) / MAD")
    status: str = Field(..., description="HEALTHY, UNBIASED, OVERPREDICTING, or UNDERPREDICTING")


class ModelHealthReport(BaseModel):
    overall_status: str = Field(..., description="HEALTHY, WARNING, or CRITICAL")
    feature_drift: Dict[str, FeatureDriftResult]
    prediction_drift: Optional[PredictionDriftResult] = None
    residual_analysis: Optional[ResidualAnalysisResult] = None
    summary_message: str


class DriftDetector:
    """
    Statistical drift detection engine using Population Stability Index (PSI),
    Kolmogorov-Smirnov (KS) tests, and residual bias metrics.
    """

    PSI_MODERATE_THRESHOLD: float = 0.10
    PSI_HIGH_THRESHOLD: float = 0.25

    def __init__(
        self,
        psi_warning_thresh: float = 0.10,
        psi_critical_thresh: float = 0.25,
        ks_alpha: float = 0.05,
    ):
        self.psi_warning_thresh = psi_warning_thresh
        self.psi_critical_thresh = psi_critical_thresh
        self.ks_alpha = ks_alpha

    def calculate_psi(
        self, reference: np.ndarray, current: np.ndarray, num_buckets: int = 10
    ) -> float:
        """
        Calculates Population Stability Index (PSI) between reference and current samples.

        Args:
            reference: Baseline numerical array.
            current: Current numerical array.
            num_buckets: Number of quantiles/bins.

        Returns:
            float: Calculated PSI value.
        """
        ref_arr = np.asarray(reference, dtype=float)
        curr_arr = np.asarray(current, dtype=float)

        # Handle NaNs
        ref_clean = ref_arr[~np.isnan(ref_arr)]
        curr_clean = curr_arr[~np.isnan(curr_arr)]

        if len(ref_clean) == 0 or len(curr_clean) == 0:
            return 0.0

        # Check if constant arrays
        if np.all(ref_clean == ref_clean[0]) and np.all(curr_clean == curr_clean[0]):
            return 0.0 if ref_clean[0] == curr_clean[0] else 1.0

        # Quantile bin edges based on reference
        percentiles = np.linspace(0, 100, num_buckets + 1)
        breakpoints = np.percentile(ref_clean, percentiles)
        breakpoints = np.unique(breakpoints)

        if len(breakpoints) <= 1:
            # Fallback to equal spacing between min and max
            min_val = min(ref_clean.min(), curr_clean.min())
            max_val = max(ref_clean.max(), curr_clean.max())
            if min_val == max_val:
                return 0.0
            breakpoints = np.linspace(min_val, max_val, num_buckets + 1)

        # Count frequencies
        ref_counts, _ = np.histogram(ref_clean, bins=breakpoints)
        curr_counts, _ = np.histogram(curr_clean, bins=breakpoints)

        # Convert to proportions with smoothing epsilon to prevent division by zero
        eps = 1e-4
        ref_pct = (ref_counts + eps) / (len(ref_clean) + eps * len(ref_counts))
        curr_pct = (curr_counts + eps) / (len(curr_clean) + eps * len(curr_counts))

        # Calculate PSI sum: (curr % - ref %) * ln(curr % / ref %)
        psi_val = np.sum((curr_pct - ref_pct) * np.log(curr_pct / ref_pct))
        return float(np.maximum(0.0, psi_val))

    def calculate_ks(self, reference: np.ndarray, current: np.ndarray) -> Tuple[float, float]:
        """
        Calculates 2-sample Kolmogorov-Smirnov test statistic and p-value.

        Returns:
            Tuple[float, float]: (ks_statistic, p_value)
        """
        ref_arr = np.asarray(reference, dtype=float)
        curr_arr = np.asarray(current, dtype=float)

        ref_clean = ref_arr[~np.isnan(ref_arr)]
        curr_clean = curr_arr[~np.isnan(curr_arr)]

        if len(ref_clean) == 0 or len(curr_clean) == 0:
            return 0.0, 1.0

        res = stats.ks_2samp(ref_clean, curr_clean)
        return float(res.statistic), float(res.pvalue)

    def detect_feature_drift(
        self,
        reference_df: pd.DataFrame,
        current_df: pd.DataFrame,
        features: Optional[List[str]] = None,
    ) -> Dict[str, FeatureDriftResult]:
        """
        Computes feature drift across specified numerical features.

        Args:
            reference_df: Baseline reference DataFrame.
            current_df: Current monitoring DataFrame.
            features: List of feature names to test.

        Returns:
            Dict[str, FeatureDriftResult]: Drift results keyed by feature name.
        """
        target_cols = features or [
            c for c in reference_df.columns if c in current_df.columns and c not in ["date", "units_sold"]
        ]

        results = {}
        for col in target_cols:
            if col not in reference_df.columns or col not in current_df.columns:
                continue

            ref_series = reference_df[col]
            curr_series = current_df[col]

            # If categorical / object column, convert to frequency counts
            if ref_series.dtype == "object" or ref_series.dtype.name == "category":
                all_cats = list(set(ref_series.dropna().unique()).union(set(curr_series.dropna().unique())))
                ref_freq = ref_series.value_counts(normalize=True).reindex(all_cats, fill_value=0.0).values
                curr_freq = curr_series.value_counts(normalize=True).reindex(all_cats, fill_value=0.0).values
                eps = 1e-4
                ref_pct = (ref_freq + eps) / (1.0 + eps * len(all_cats))
                curr_pct = (curr_freq + eps) / (1.0 + eps * len(all_cats))
                psi_val = float(np.sum((curr_pct - ref_pct) * np.log(curr_pct / ref_pct)))
                ks_stat, p_val = None, None
            else:
                ref_vals = ref_series.to_numpy()
                curr_vals = curr_series.to_numpy()
                psi_val = self.calculate_psi(ref_vals, curr_vals)
                ks_stat, p_val = self.calculate_ks(ref_vals, curr_vals)

            # Determine status based on PSI
            if psi_val < self.psi_warning_thresh:
                status = "NO_DRIFT"
                msg = f"Feature '{col}' is stable (PSI = {psi_val:.4f})."
            elif psi_val < self.psi_critical_thresh:
                status = "MODERATE_DRIFT"
                msg = f"Feature '{col}' exhibits moderate drift (PSI = {psi_val:.4f})."
            else:
                status = "SIGNIFICANT_DRIFT"
                msg = f"Feature '{col}' exhibits significant drift (PSI = {psi_val:.4f})."

            results[col] = FeatureDriftResult(
                feature_name=col,
                psi=round(psi_val, 4),
                ks_statistic=round(ks_stat, 4) if ks_stat is not None else None,
                p_value=round(p_val, 4) if p_val is not None else None,
                status=status,
                message=msg,
            )

        return results

    def detect_prediction_drift(
        self, reference_preds: np.ndarray, current_preds: np.ndarray
    ) -> PredictionDriftResult:
        """
        Computes distribution shift metrics on model prediction outputs.

        Args:
            reference_preds: Baseline predictions array.
            current_preds: Current predictions array.

        Returns:
            PredictionDriftResult: Prediction drift analysis result.
        """
        ref_arr = np.asarray(reference_preds, dtype=float)
        curr_arr = np.asarray(current_preds, dtype=float)

        mean_ref = float(np.mean(ref_arr))
        mean_curr = float(np.mean(curr_arr))
        var_ref = float(np.var(ref_arr))
        var_curr = float(np.var(curr_arr))

        psi_val = self.calculate_psi(ref_arr, curr_arr)
        ks_stat, p_val = self.calculate_ks(ref_arr, curr_arr)

        if psi_val < self.psi_warning_thresh:
            status = "NO_DRIFT"
            msg = f"Predictions are stable (PSI = {psi_val:.4f})."
        elif psi_val < self.psi_critical_thresh:
            status = "MODERATE_DRIFT"
            msg = f"Predictions show moderate drift (PSI = {psi_val:.4f})."
        else:
            status = "SIGNIFICANT_DRIFT"
            msg = f"Predictions show significant drift (PSI = {psi_val:.4f})."

        return PredictionDriftResult(
            mean_reference=round(mean_ref, 4),
            mean_current=round(mean_curr, 4),
            variance_reference=round(var_ref, 4),
            variance_current=round(var_curr, 4),
            psi=round(psi_val, 4),
            ks_statistic=round(ks_stat, 4),
            p_value=round(p_val, 4),
            status=status,
            message=msg,
        )

    def analyze_residuals(
        self, actuals: np.ndarray, predictions: np.ndarray
    ) -> ResidualAnalysisResult:
        """
        Computes residual distribution, forecast bias, and tracking signal.

        Args:
            actuals: Ground truth values.
            predictions: Model forecast predictions.

        Returns:
            ResidualAnalysisResult: Residual and bias metrics.
        """
        y_act = np.asarray(actuals, dtype=float)
        y_pred = np.asarray(predictions, dtype=float)

        residuals = y_act - y_pred  # Error: actual - predicted
        abs_residuals = np.abs(residuals)

        mae = float(np.mean(abs_residuals))
        rmse = float(np.sqrt(np.mean(residuals**2)))
        sum_act = np.sum(np.abs(y_act))
        wape = float(np.sum(abs_residuals) / sum_act * 100.0) if sum_act > 0 else 0.0

        mean_res = float(np.mean(residuals))
        sum_abs_res = float(np.sum(abs_residuals))
        
        # Normalized Forecast Bias: sum(error) / sum(|error|) in range [-1.0, 1.0]
        forecast_bias = float(np.sum(residuals) / sum_abs_res) if sum_abs_res > 0 else 0.0

        # Tracking Signal: Cumulative Error / Mean Absolute Deviation (MAD)
        mad = mae
        tracking_signal = float(np.sum(residuals) / mad) if mad > 0 else 0.0

        if abs(forecast_bias) < 0.15:
            status = "HEALTHY"
        elif forecast_bias >= 0.15:
            status = "UNDERPREDICTING"
        else:
            status = "OVERPREDICTING"

        return ResidualAnalysisResult(
            sample_count=len(y_act),
            mae=round(mae, 4),
            rmse=round(rmse, 4),
            wape=round(wape, 4),
            mean_residual=round(mean_res, 4),
            forecast_bias=round(forecast_bias, 4),
            tracking_signal=round(tracking_signal, 4),
            status=status,
        )

    def evaluate_health(
        self,
        reference_df: pd.DataFrame,
        current_df: pd.DataFrame,
        reference_preds: Optional[np.ndarray] = None,
        current_preds: Optional[np.ndarray] = None,
        actuals: Optional[np.ndarray] = None,
        predictions: Optional[np.ndarray] = None,
        key_features: Optional[List[str]] = None,
    ) -> ModelHealthReport:
        """
        Evaluates overall model health by aggregating feature drift, prediction drift, and residual analysis.

        Returns:
            ModelHealthReport: Comprehensive health summary.
        """
        # 1. Feature Drift
        feat_results = self.detect_feature_drift(
            reference_df, current_df, features=key_features
        )

        # 2. Prediction Drift
        pred_result = None
        if reference_preds is not None and current_preds is not None:
            pred_result = self.detect_prediction_drift(reference_preds, current_preds)

        # 3. Residual Analysis
        res_result = None
        if actuals is not None and predictions is not None:
            res_result = self.analyze_residuals(actuals, predictions)

        # Overall Status Determination
        sig_drift_count = sum(1 for f in feat_results.values() if f.status == "SIGNIFICANT_DRIFT")
        mod_drift_count = sum(1 for f in feat_results.values() if f.status == "MODERATE_DRIFT")

        pred_sig = pred_result.status == "SIGNIFICANT_DRIFT" if pred_result else False
        res_unhealthy = res_result.status in ["UNDERPREDICTING", "OVERPREDICTING"] if res_result else False

        if sig_drift_count > 0 or pred_sig:
            overall = "CRITICAL"
            summary = f"Critical alert: {sig_drift_count} feature(s) and/or predictions exhibit significant drift."
        elif mod_drift_count > 0 or res_unhealthy:
            overall = "WARNING"
            summary = f"Warning: {mod_drift_count} feature(s) exhibit moderate drift or forecast bias detected."
        else:
            overall = "HEALTHY"
            summary = "Model health is optimal. No significant drift detected."

        return ModelHealthReport(
            overall_status=overall,
            feature_drift=feat_results,
            prediction_drift=pred_result,
            residual_analysis=res_result,
            summary_message=summary,
        )
