"""
Pytest configuration and shared fixtures for unit testing.
"""

import pytest
import pandas as pd
from src.utils.config import DataConfig, ValidationRulesConfig


@pytest.fixture
def data_config() -> DataConfig:
    """Fixture providing a standard DataConfig instance."""
    return DataConfig(
        raw_data_path="data/raw/sample_sales_data.csv",
        required_columns=["date", "store_id", "product_id", "units_sold"],
        optional_columns=["revenue", "price", "discount", "promotion", "holiday"],
        date_format="%Y-%m-%d",
        validation_rules=ValidationRulesConfig(
            allow_negative_sales=False,
            min_price=0.0,
            min_discount=0.0,
            max_discount=1.0,
            check_date_gaps=True,
            max_missing_pct=0.20,
        ),
    )


@pytest.fixture
def valid_df() -> pd.DataFrame:
    """Fixture returning a clean, valid sales DataFrame."""
    data = {
        "date": ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"],
        "store_id": ["STORE_01", "STORE_01", "STORE_01", "STORE_01"],
        "product_id": ["PROD_01", "PROD_01", "PROD_01", "PROD_01"],
        "units_sold": [100, 120, 110, 130],
        "revenue": [2000.0, 2400.0, 2200.0, 2600.0],
        "price": [20.0, 20.0, 20.0, 20.0],
        "discount": [0.0, 0.0, 0.0, 0.0],
        "promotion": [0, 0, 1, 1],
    }
    return pd.DataFrame(data)


@pytest.fixture
def invalid_df() -> pd.DataFrame:
    """Fixture returning an invalid sales DataFrame containing various data issues."""
    data = {
        "date": ["2026-01-01", "invalid-date", "2026-01-01", "2026-01-04"],
        "store_id": ["STORE_01", "STORE_01", "STORE_01", ""],
        "product_id": ["PROD_01", "PROD_01", "PROD_01", "PROD_01"],
        "units_sold": [-10, 120, 110, 130],
        "price": [-5.0, 20.0, 20.0, 0.0],
        "discount": [1.5, 0.0, 0.0, -0.1],
    }
    return pd.DataFrame(data)
