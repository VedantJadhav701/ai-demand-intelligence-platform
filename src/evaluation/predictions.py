"""
Prediction storage and container structures for validation and test predictions.
"""

from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field


class PredictionRecord(BaseModel):
    date: str
    store_id: str
    product_id: str
    horizon: int
    actual: float
    prediction: float
    model: str
    fold: int  # 0 for final test set


class PredictionStore:
    """Class for collecting, formatting, and saving prediction records."""

    def __init__(self):
        self._records: List[Dict[str, Any]] = []

    def add_predictions(
        self,
        meta: pd.DataFrame,
        actuals: np.ndarray,
        predictions: np.ndarray,
        model_name: str,
        horizon: int,
        fold: int,
    ) -> None:
        """
        Adds prediction records for a specific fold and model evaluation.

        Args:
            meta: Metadata DataFrame containing 'date', 'store_id', 'product_id'.
            actuals: Array of actual target values.
            predictions: Array of predicted values.
            model_name: Name of evaluated model.
            horizon: Forecast horizon.
            fold: Fold index (0 for final test set).
        """
        dates = meta["date"].dt.strftime("%Y-%m-%d").values if "date" in meta.columns else ["N/A"] * len(actuals)
        stores = meta["store_id"].astype(str).values if "store_id" in meta.columns else ["N/A"] * len(actuals)
        prods = meta["product_id"].astype(str).values if "product_id" in meta.columns else ["N/A"] * len(actuals)

        for i in range(len(actuals)):
            self._records.append(
                {
                    "date": dates[i],
                    "store_id": stores[i],
                    "product_id": prods[i],
                    "horizon": int(horizon),
                    "actual": round(float(actuals[i]), 4),
                    "prediction": round(float(predictions[i]), 4),
                    "model": model_name,
                    "fold": int(fold),
                }
            )

    def to_dataframe(self) -> pd.DataFrame:
        """Converts stored prediction records to pandas DataFrame."""
        if not self._records:
            return pd.DataFrame(
                columns=[
                    "date",
                    "store_id",
                    "product_id",
                    "horizon",
                    "actual",
                    "prediction",
                    "model",
                    "fold",
                ]
            )
        return pd.DataFrame(self._records)

    def clear(self) -> None:
        self._records = []
