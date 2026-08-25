"""
Unit tests for evaluation metrics (MAE, RMSE, MAPE, sMAPE, WAPE) and zero-demand safety.
"""

import pytest
import numpy as np

from src.evaluation.metrics import (
    calculate_mae,
    calculate_rmse,
    calculate_mape,
    calculate_smape,
    calculate_wape,
    calculate_all_metrics,
)


def test_metric_numerical_examples():
    """Test metric calculations against known analytical values."""
    y_true = np.array([100.0, 200.0, 300.0])
    y_pred = np.array([110.0, 190.0, 300.0])

    # Errors: |+10|, |-10|, |0| -> sum abs = 20.0
    mae = calculate_mae(y_true, y_pred)
    assert pytest.approx(mae, 0.01) == 20.0 / 3.0  # 6.6667

    rmse = calculate_rmse(y_true, y_pred)
    assert pytest.approx(rmse, 0.01) == np.sqrt((100 + 100 + 0) / 3.0)  # sqrt(66.6667) = 8.165

    wape = calculate_wape(y_true, y_pred)
    assert pytest.approx(wape, 0.01) == (20.0 / 600.0) * 100.0  # 3.3333%


def test_zero_demand_handling():
    """Test that zero actual demand handles division safely without NaN or Inf."""
    y_true = np.array([0.0, 0.0, 0.0])
    y_pred = np.array([0.0, 5.0, 0.0])

    mape = calculate_mape(y_true, y_pred)
    smape = calculate_smape(y_true, y_pred)
    wape = calculate_wape(y_true, y_pred)

    assert not np.isnan(mape) and not np.isinf(mape)
    assert not np.isnan(smape) and not np.isinf(smape)
    assert not np.isnan(wape) and not np.isinf(wape)


def test_calculate_all_metrics():
    """Test unified calculate_all_metrics call."""
    y_true = np.array([10.0, 20.0, 30.0])
    y_pred = np.array([10.0, 20.0, 30.0])

    res = calculate_all_metrics(y_true, y_pred)
    assert res.mae == 0.0
    assert res.rmse == 0.0
    assert res.wape == 0.0
    assert res.mape == 0.0
    assert res.smape == 0.0
