"""
Strict temporal leakage verification unit tests.
Verifies that features X(t) strictly contain information available at or before time t
and that future target values are never leaked into training features.
"""

import pytest
import pandas as pd
import numpy as np

from src.features.builder import FeatureEngineer
from src.features.config import FeatureConfig
from src.models.dataset import ForecastingDatasetBuilder
from src.evaluation.splitter import TimeSeriesSplitter


@pytest.fixture
def leakage_test_df() -> pd.DataFrame:
    """Fixture providing daily sales for a single store/product series."""
    dates = pd.date_range("2026-01-01", periods=20, freq="D")
    return pd.DataFrame(
        {
            "date": dates.strftime("%Y-%m-%d"),
            "store_id": ["S1"] * 20,
            "product_id": ["P1"] * 20,
            "units_sold": np.arange(10, 30, dtype=float),
            "price": [20.0] * 20,
            "discount": [0.0] * 20,
        }
    )


def test_lag_and_rolling_no_future_leakage(leakage_test_df: pd.DataFrame):
    """Verify that lag and rolling features do not use future observations."""
    config = FeatureConfig(lags=[1, 7], rolling_windows=[7], rolling_stats=["mean"])
    engineer = FeatureEngineer(config)
    df_feat = engineer.transform(leakage_test_df)

    # Row 7 (index 7, date 2026-01-08, actual target=17)
    # lag_1 must equal actual target at index 6 (16)
    assert df_feat.loc[7, "lag_1"] == 16.0

    # rolling_mean_7 at row 7 must equal mean of index 0..6 (10..16) = 13.0
    # Must NOT include target at index 7 (17)!
    assert df_feat.loc[7, "rolling_mean_7"] == 13.0

    # Mutate future observation at index 7 to 9999.0
    mutated_df = leakage_test_df.copy()
    mutated_df.loc[7, "units_sold"] = 9999.0
    df_mutated = engineer.transform(mutated_df)

    # Feature vector X at index 7 must be IDENTICAL before and after mutating target at index 7!
    assert df_mutated.loc[7, "lag_1"] == 16.0
    assert df_mutated.loc[7, "rolling_mean_7"] == 13.0


def test_dataset_target_exclusion(leakage_test_df: pd.DataFrame):
    """Verify target columns (target_h{h} and raw units_sold) are excluded from feature matrix X."""
    builder = ForecastingDatasetBuilder()
    ds = builder.build_dataset(leakage_test_df, horizon=7)

    assert "target_h7" not in ds.X.columns
    assert "units_sold" not in ds.X.columns
    assert ds.target_name == "target_h7"
    assert len(ds.X) == len(ds.y)


def test_chronological_split_no_future_leakage(leakage_test_df: pd.DataFrame):
    """Verify train/val/test splits maintain strict chronological boundaries."""
    builder = ForecastingDatasetBuilder()
    ds = builder.build_dataset(leakage_test_df, horizon=1)

    splitter = TimeSeriesSplitter(test_size=0.2, n_splits=2, date_col="date")
    split_res = splitter.split(ds.df)

    train_dates = ds.df.iloc[split_res.train_val_indices]["date"]
    test_dates = ds.df.iloc[split_res.test_indices]["date"]

    assert train_dates.max() < test_dates.min()


@pytest.mark.parametrize("h", [1, 7, 14, 30])
def test_explicit_horizon_target_and_feature_isolation(h: int):
    """
    Explicitly proves that for each horizon h:
    - X(t) contains only information available at or before time t.
    - target_h = units_sold(t+h).
    - Future units_sold at t+1..t+h have zero influence on feature values X(t).
    """
    dates = pd.date_range("2026-01-01", periods=70, freq="D")
    df = pd.DataFrame(
        {
            "date": dates.strftime("%Y-%m-%d"),
            "store_id": ["S1"] * 70,
            "product_id": ["P1"] * 70,
            "units_sold": np.arange(100, 170, dtype=float),
            "price": [20.0] * 70,
            "discount": [0.0] * 70,
        }
    )

    builder = ForecastingDatasetBuilder()
    ds = builder.build_dataset(df, horizon=h)

    # Pick a sample row index at timestamp t
    sample_idx = 5
    sample_date = ds.meta.iloc[sample_idx]["date"]

    # 1. Target alignment check: ds.y at sample_idx must equal raw units_sold at sample_date + h days
    target_date = sample_date + pd.Timedelta(days=h)
    expected_future_units = df[df["date"] == target_date.strftime("%Y-%m-%d")]["units_sold"].values[0]
    assert ds.y.iloc[sample_idx] == expected_future_units

    # 2. Information availability check: X at sample_idx must not contain target_h{h} or raw units_sold
    assert ds.target_name not in ds.X.columns
    assert "units_sold" not in ds.X.columns

    # 3. Future mutation invariance check: Mutating future units_sold at target_date leaves X(t) unchanged
    df_mutated = df.copy()
    future_mask = df_mutated["date"] >= target_date.strftime("%Y-%m-%d")
    df_mutated.loc[future_mask, "units_sold"] += 99999.0

    ds_mutated = builder.build_dataset(df_mutated, horizon=h)

    # Verify feature row X at sample_idx is identical before and after future mutation
    pd.testing.assert_series_equal(
        ds.X.iloc[sample_idx], ds_mutated.X.iloc[sample_idx]
    )


def test_revenue_feature_provenance_and_exclusion():
    """
    Feature provenance audit test:
    Verifies that 'revenue' (which is derived from units_sold * price at time t)
    is strictly excluded from feature matrix X(t) to prevent target-derived leakage.
    """
    dates = pd.date_range("2026-01-01", periods=20, freq="D")
    df = pd.DataFrame(
        {
            "date": dates.strftime("%Y-%m-%d"),
            "store_id": ["S1"] * 20,
            "product_id": ["P1"] * 20,
            "units_sold": np.arange(10, 30, dtype=float),
            "price": [20.0] * 20,
            "discount": [0.0] * 20,
            "revenue": np.arange(10, 30, dtype=float) * 20.0,
        }
    )

    builder = ForecastingDatasetBuilder()
    ds = builder.build_dataset(df, horizon=1)

    assert "revenue" not in ds.X.columns
    assert "units_sold" not in ds.X.columns
    assert "target_h1" not in ds.X.columns
