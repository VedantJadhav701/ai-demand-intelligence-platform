"""
Models package containing dataset builder, base forecaster interface, baselines, ML models, and model factory.
"""

from src.models.base import BaseForecaster
from src.models.dataset import ForecastingDataset, ForecastingDatasetBuilder
from src.models.baselines import NaiveForecaster, SeasonalNaiveForecaster
from src.models.ml_models import (
    RidgeRegressionForecaster,
    RandomForestForecaster,
    XGBoostForecaster,
    LightGBMForecaster,
    CatBoostForecaster,
)
from src.models.factory import ModelFactory

__all__ = [
    "BaseForecaster",
    "ForecastingDataset",
    "ForecastingDatasetBuilder",
    "NaiveForecaster",
    "SeasonalNaiveForecaster",
    "RidgeRegressionForecaster",
    "RandomForestForecaster",
    "XGBoostForecaster",
    "LightGBMForecaster",
    "CatBoostForecaster",
    "ModelFactory",
]
