"""
Abstract Base Forecaster interface for all baseline and machine learning forecasting models.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd


class BaseForecaster(ABC):
    """Abstract Base Class for all forecasting models."""

    def __init__(self, name: str, params: Optional[Dict[str, Any]] = None):
        self.name = name
        self.params = params or {}
        self.is_fitted = False

    @abstractmethod
    def fit(self, X: pd.DataFrame, y: pd.Series) -> "BaseForecaster":
        """
        Fits the model on features X and target y.

        Args:
            X: Feature matrix DataFrame at time t.
            y: Target demand Series at time t+h.

        Returns:
            self: Fitted forecaster instance.
        """
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Generates predictions for feature matrix X.

        Args:
            X: Feature matrix DataFrame at time t.

        Returns:
            np.ndarray: Predicted demand values at time t+h.
        """
        pass

    def get_params(self) -> Dict[str, Any]:
        """Returns hyperparameter dictionary of the forecaster."""
        return self.params.copy()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', fitted={self.is_fitted})>"
