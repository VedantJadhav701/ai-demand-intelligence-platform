"""
Unit tests for ForecastingDatasetBuilder.
"""

import pytest
import pandas as pd

from src.models.dataset import ForecastingDatasetBuilder, ForecastingDataset
from src.features.builder import FeatureEngineer
from src.utils.config import ModelConfig


@pytest.fixture
def sample_raw_df() -> pd.DataFrame:
    """Fixture providing daily sales data across 30 days for 2 series."""
    dates = pd.date_range("2026-01-01", periods=30, freq="D")
    rows = []
    for d in dates:
        for s in ["STORE_01", "STORE_02"]:
            for p in ["PROD_01"]:
                rows.append(
                    {
                        "date": d.strftime("%Y-%m-%d"),
                        "store_id": s,
                        "product_id": p,
                        "units_sold": 100 + (d.day * 2),
                        "price": 20.0,
                        "discount": 0.0,
                    }
                )
    return pd.DataFrame(rows)


def test_build_forecasting_dataset_horizon_7(sample_raw_df: pd.DataFrame):
    """Test dataset creation for horizon h=7."""
    builder = ForecastingDatasetBuilder()
    ds = builder.build_dataset(sample_raw_df, horizon=7)

    assert isinstance(ds, ForecastingDataset)
    assert ds.horizon == 7
    assert ds.target_name == "target_h7"
    assert "target_h7" not in ds.X.columns
    assert "units_sold" not in ds.X.columns
    assert len(ds.X) == len(ds.y)
    assert len(ds.y) < len(sample_raw_df)  # Tail rows removed


def test_target_shifting_correctness(sample_raw_df: pd.DataFrame):
    """Test that target y[t+h] corresponds to future target value at t+h."""
    builder = ForecastingDatasetBuilder()
    ds = builder.build_dataset(sample_raw_df, horizon=1)

    # For row 0 in ds, get date and store
    row0_date = ds.meta.iloc[0]["date"]
    row0_store = ds.meta.iloc[0]["store_id"]
    row0_target = ds.y.iloc[0]

    target_date = (row0_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    matching = sample_raw_df[
        (sample_raw_df["store_id"] == row0_store)
        & (sample_raw_df["product_id"] == "PROD_01")
        & (sample_raw_df["date"] == target_date)
    ]
    assert row0_target == matching["units_sold"].values[0]
