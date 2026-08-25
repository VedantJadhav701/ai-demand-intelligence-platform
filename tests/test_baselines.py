"""
Unit tests for Naive and Seasonal Naive baseline forecasters.
"""

import pytest
import pandas as pd
import numpy as np

from src.models.baselines import NaiveForecaster, SeasonalNaiveForecaster


def test_naive_forecaster():
    """Test NaiveForecaster predicts lag_1 values."""
    X = pd.DataFrame({"lag_1": [10.0, 20.0, 30.0], "store_id": ["S1", "S1", "S1"]})
    y = pd.Series([12.0, 22.0, 32.0])

    model = NaiveForecaster()
    model.fit(X, y)
    preds = model.predict(X)

    np.testing.assert_array_equal(preds, np.array([10.0, 20.0, 30.0]))


def test_seasonal_naive_forecaster():
    """Test SeasonalNaiveForecaster predicts lag_7 values."""
    X = pd.DataFrame(
        {"lag_1": [10.0, 20.0], "lag_7": [70.0, 80.0], "store_id": ["S1", "S1"]}
    )
    y = pd.Series([75.0, 85.0])

    model = SeasonalNaiveForecaster(seasonal_period=7)
    model.fit(X, y)
    preds = model.predict(X)

    np.testing.assert_array_equal(preds, np.array([70.0, 80.0]))


def test_seasonal_naive_no_series_crossing():
    """
    Verifies that Seasonal Naive predictions computed via FeatureEngineer
    never cross store_id or product_id series boundaries.
    """
    from src.features.builder import FeatureEngineer
    from src.features.config import FeatureConfig

    dates = pd.date_range("2026-01-01", periods=14, freq="D")
    rows = []
    for d in dates:
        # Store 1 has baseline 100, Store 2 has baseline 500
        rows.append(
            {
                "date": d.strftime("%Y-%m-%d"),
                "store_id": "STORE_1",
                "product_id": "P1",
                "units_sold": 100.0 + d.day,
            }
        )
        rows.append(
            {
                "date": d.strftime("%Y-%m-%d"),
                "store_id": "STORE_2",
                "product_id": "P1",
                "units_sold": 500.0 + d.day,
            }
        )

    df = pd.DataFrame(rows)
    engineer = FeatureEngineer(FeatureConfig(lags=[7]))
    df_feat = engineer.transform(df)

    model = SeasonalNaiveForecaster(seasonal_period=7)
    X = df_feat.drop(columns=["units_sold"])
    y = df_feat["units_sold"]
    model.fit(X, y)

    # Predict on Day 8 (2026-01-08) for STORE_1 and STORE_2
    day8_store1 = X[(X["date"] == pd.Timestamp("2026-01-08")) & (X["store_id"] == "STORE_1")]
    day8_store2 = X[(X["date"] == pd.Timestamp("2026-01-08")) & (X["store_id"] == "STORE_2")]

    pred_store1 = model.predict(day8_store1)[0]
    pred_store2 = model.predict(day8_store2)[0]

    # STORE_1 Day 8 prediction must match STORE_1 Day 1 actual (101.0)
    # STORE_2 Day 8 prediction must match STORE_2 Day 1 actual (501.0)
    assert pred_store1 == 101.0
    assert pred_store2 == 501.0
