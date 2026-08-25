"""
Unit tests for Feature Engineer module, validating feature generation and strict target leakage prevention.
"""

import pytest
import pandas as pd
import numpy as np

from src.features.config import FeatureConfig
from src.features.builder import FeatureEngineer


@pytest.fixture
def series_df() -> pd.DataFrame:
    """Fixture providing a simple 10-day time-series dataset for exact numerical verification."""
    dates = pd.date_range("2026-01-01", periods=10, freq="D")
    data = {
        "date": dates.strftime("%Y-%m-%d"),
        "store_id": ["STORE_01"] * 10,
        "product_id": ["PROD_01"] * 10,
        "units_sold": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        "price": [10.0] * 5 + [12.0] * 5,
        "discount": [0.0] * 5 + [0.1] * 5,
    }
    return pd.DataFrame(data)


def test_temporal_features(series_df: pd.DataFrame):
    """Test calendar temporal feature generation."""
    config = FeatureConfig(lags=[1], rolling_windows=[3])
    engineer = FeatureEngineer(config)
    df_feat = engineer.transform(series_df)

    assert "day_of_week" in df_feat.columns
    assert "month" in df_feat.columns
    assert "is_weekend" in df_feat.columns
    assert "quarter" in df_feat.columns


def test_lag_features_correctness(series_df: pd.DataFrame):
    """Test exact values of lag_1 and lag_7."""
    config = FeatureConfig(lags=[1, 3], rolling_windows=[3])
    engineer = FeatureEngineer(config)
    df_feat = engineer.transform(series_df)

    # Day 0 (2026-01-01): lag_1 should be NaN
    assert pd.isna(df_feat.loc[0, "lag_1"])

    # Day 1 (2026-01-02): lag_1 should be units_sold of Day 0 (10)
    assert df_feat.loc[1, "lag_1"] == 10.0

    # Day 5 (2026-01-06): lag_1 should be units_sold of Day 4 (50)
    assert df_feat.loc[5, "lag_1"] == 50.0

    # Day 5 (2026-01-06): lag_3 should be units_sold of Day 2 (30)
    assert df_feat.loc[5, "lag_3"] == 30.0


def test_rolling_features_no_target_leakage(series_df: pd.DataFrame):
    """
    CRITICAL TEST: Verify that rolling features do NOT contain target leakage.
    For day t, rolling mean of window 3 must equal mean of target at (t-3, t-2, t-1),
    and must NOT include target at day t.
    """
    config = FeatureConfig(lags=[1], rolling_windows=[3], rolling_stats=["mean"])
    engineer = FeatureEngineer(config)
    df_feat = engineer.transform(series_df)

    # For Day 3 (row index 3, target=40), historical values before Day 3 are:
    # Day 0 (10), Day 1 (20), Day 2 (30).
    # Rolling mean(3) should be (10+20+30)/3 = 20.0 (NOT (20+30+40)/3 = 30.0!)
    assert df_feat.loc[3, "rolling_mean_3"] == 20.0

    # For Day 4 (row index 4, target=50), historical values before Day 4 are:
    # Day 1 (20), Day 2 (30), Day 3 (40).
    # Rolling mean(3) should be (20+30+40)/3 = 30.0
    assert df_feat.loc[4, "rolling_mean_3"] == 30.0

    # Explicit mutation test: altering target at day t must NOT affect rolling mean at day t
    mutated_df = series_df.copy()
    mutated_df.loc[3, "units_sold"] = 9999.0  # Spike target on Day 3
    df_mutated_feat = engineer.transform(mutated_df)

    # Day 3's rolling mean must remain 20.0!
    assert df_mutated_feat.loc[3, "rolling_mean_3"] == 20.0
    # Day 4's rolling mean should reflect the mutated Day 3 target
    assert df_mutated_feat.loc[4, "rolling_mean_3"] == (20 + 30 + 9999) / 3.0


def test_diff_features(series_df: pd.DataFrame):
    """Test price and discount change difference features."""
    engineer = FeatureEngineer()
    df_feat = engineer.transform(series_df)

    assert "price_change" in df_feat.columns
    assert "discount_change" in df_feat.columns
    # On index 5, price changes from 10.0 to 12.0 (+2.0)
    assert df_feat.loc[5, "price_change"] == 2.0
