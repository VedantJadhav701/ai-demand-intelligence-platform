"""
Unit tests for ModelFactory and all 7 forecasting model implementations.
"""

from typing import Tuple
import pytest
import pandas as pd
import numpy as np

from src.models.factory import ModelFactory
from src.utils.config import ModelConfig


@pytest.fixture
def dummy_train_val_data() -> Tuple[pd.DataFrame, pd.Series]:
    """Fixture providing a clean tabular dataset for model fit/predict testing."""
    dates = pd.date_range("2026-01-01", periods=20, freq="D")
    X = pd.DataFrame(
        {
            "date": dates.strftime("%Y-%m-%d"),
            "store_id": ["STORE_01"] * 20,
            "product_id": ["PROD_01"] * 20,
            "store_type": ["Supermarket"] * 20,
            "product_category": ["Electronics"] * 20,
            "lag_1": np.arange(10, 30, dtype=float),
            "lag_7": np.arange(5, 25, dtype=float),
            "rolling_mean_7": np.arange(10, 30, dtype=float),
            "day_of_week": [i % 7 for i in range(20)],
            "price": [20.0] * 20,
            "discount": [0.0] * 20,
        }
    )
    y = pd.Series(np.arange(12, 32, dtype=float))
    return X, y


@pytest.mark.parametrize(
    "model_name",
    [
        "naive",
        "seasonal_naive",
        "ridge_regression",
        "random_forest",
        "xgboost",
        "lightgbm",
        "catboost",
    ],
)
def test_all_models_fit_and_predict(
    model_name: str, dummy_train_val_data: Tuple[pd.DataFrame, pd.Series]
):
    """Verifies that every supported model instantiates, fits, and predicts non-negative arrays of expected shape."""
    X, y = dummy_train_val_data
    config = ModelConfig(random_seed=42)

    model = ModelFactory.create(model_name, model_config=config)
    assert model.is_fitted is False

    model.fit(X, y)
    assert model.is_fitted is True

    preds = model.predict(X)
    assert isinstance(preds, np.ndarray)
    assert len(preds) == len(X)
    assert np.all(preds >= 0.0)  # Demand predictions must be non-negative
