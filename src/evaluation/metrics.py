"""
Evaluation Metrics for time-series forecasting (MAE, RMSE, MAPE, sMAPE, WAPE).
Handles zero-demand observations explicitly without producing NaN/inf values.
"""

from typing import Dict
from pydantic import BaseModel
import numpy as np


class MetricResult(BaseModel):
    mae: float
    rmse: float
    mape: float
    smape: float
    wape: float


def calculate_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculates Mean Absolute Error (MAE)."""
    if len(y_true) == 0:
        return 0.0
    return float(np.mean(np.abs(y_true - y_pred)))


def calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculates Root Mean Squared Error (RMSE)."""
    if len(y_true) == 0:
        return 0.0
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculates Mean Absolute Percentage Error (MAPE).
    Handles zero actual demand by evaluating only over non-zero actuals.
    Returns percentage value (0.0 to 100.0+).
    """
    if len(y_true) == 0:
        return 0.0
    non_zero_mask = y_true != 0
    if not np.any(non_zero_mask):
        return 0.0
    abs_pct = np.abs((y_true[non_zero_mask] - y_pred[non_zero_mask]) / y_true[non_zero_mask])
    return float(np.mean(abs_pct) * 100.0)


def calculate_smape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculates Symmetric Mean Absolute Percentage Error (sMAPE).
    Formula: mean(2 * |y - ŷ| / (|y| + |ŷ|)) * 100%.
    Handles zero denominator explicitly.
    """
    if len(y_true) == 0:
        return 0.0
    denom = np.abs(y_true) + np.abs(y_pred)
    non_zero_mask = denom != 0
    if not np.any(non_zero_mask):
        return 0.0
    smape_vals = np.zeros_like(y_true, dtype=float)
    smape_vals[non_zero_mask] = (
        2.0 * np.abs(y_true[non_zero_mask] - y_pred[non_zero_mask]) / denom[non_zero_mask]
    )
    return float(np.mean(smape_vals) * 100.0)


def calculate_wape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculates Weighted Absolute Percentage Error (WAPE).
    Formula: sum(|y - ŷ|) / sum(|y|) * 100%.
    Handles zero total actual demand explicitly.
    """
    if len(y_true) == 0:
        return 0.0
    total_actual = float(np.sum(np.abs(y_true)))
    if total_actual == 0.0:
        return 0.0
    total_error = float(np.sum(np.abs(y_true - y_pred)))
    return float((total_error / total_actual) * 100.0)


def calculate_all_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> MetricResult:
    """
    Calculates all metrics for actual vs predicted demand arrays.

    Args:
        y_true: Array of actual demand values.
        y_pred: Array of predicted demand values.

    Returns:
        MetricResult: Structured container holding MAE, RMSE, MAPE, sMAPE, WAPE.
    """
    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)

    return MetricResult(
        mae=round(calculate_mae(yt, yp), 4),
        rmse=round(calculate_rmse(yt, yp), 4),
        mape=round(calculate_mape(yt, yp), 4),
        smape=round(calculate_smape(yt, yp), 4),
        wape=round(calculate_wape(yt, yp), 4),
    )
