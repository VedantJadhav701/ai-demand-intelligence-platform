"""
Baseline forecasting models (Naive and Seasonal Naive).
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

from src.models.base import BaseForecaster
from src.utils.logger import get_logger

logger = get_logger("models.baselines")


class NaiveForecaster(BaseForecaster):
    """
    Naive Forecaster predicting y(t+h) = actual(t).
    Uses lag_1 from feature matrix X if present, otherwise falls back to target mean.
    """

    def __init__(self, name: str = "Naive", params: Optional[Dict[str, Any]] = None):
        super().__init__(name=name, params=params)
        self.fallback_value: float = 0.0

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "NaiveForecaster":
        self.fallback_value = float(y.mean()) if not y.empty else 0.0
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError(f"Model {self.name} is not fitted yet.")

        if "lag_1" in X.columns:
            preds = X["lag_1"].fillna(self.fallback_value).values
        else:
            logger.warning(
                f"Column 'lag_1' not found in features for {self.name}. Using fallback mean value."
            )
            preds = np.full(len(X), self.fallback_value)

        return np.maximum(0.0, preds)


class SeasonalNaiveForecaster(BaseForecaster):
    """
    Seasonal Naive Forecaster predicting y(t+h) = actual(t+h-S).
    Uses lag_S (default lag_7 for weekly seasonality) from feature matrix X.
    """

    def __init__(
        self,
        name: str = "SeasonalNaive",
        seasonal_period: int = 7,
        params: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name=name, params=params)
        self.seasonal_period = seasonal_period
        self.fallback_value: float = 0.0

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "SeasonalNaiveForecaster":
        self.fallback_value = float(y.mean()) if not y.empty else 0.0
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError(f"Model {self.name} is not fitted yet.")

        seasonal_col = f"lag_{self.seasonal_period}"
        if seasonal_col in X.columns:
            preds = X[seasonal_col].fillna(self.fallback_value).values
        elif "lag_1" in X.columns:
            logger.warning(
                f"Column '{seasonal_col}' not found for {self.name}. Falling back to 'lag_1'."
            )
            preds = X["lag_1"].fillna(self.fallback_value).values
        else:
            preds = np.full(len(X), self.fallback_value)

        return np.maximum(0.0, preds)
