"""
Model Factory for creating baseline and machine learning forecasters.
"""

from typing import Dict, Any, Optional
from src.models.base import BaseForecaster
from src.models.baselines import NaiveForecaster, SeasonalNaiveForecaster
from src.models.ml_models import (
    RidgeRegressionForecaster,
    RandomForestForecaster,
    XGBoostForecaster,
    LightGBMForecaster,
    CatBoostForecaster,
)
from src.utils.config import ModelConfig
from src.utils.logger import get_logger

logger = get_logger("models.factory")


class ModelFactory:
    """Factory class for instantiating forecasting models using standardized names."""

    _MODEL_MAP = {
        "naive": NaiveForecaster,
        "seasonal_naive": SeasonalNaiveForecaster,
        "ridge_regression": RidgeRegressionForecaster,
        "linear_regression": RidgeRegressionForecaster,  # Backward-compatibility alias
        "random_forest": RandomForestForecaster,
        "xgboost": XGBoostForecaster,
        "lightgbm": LightGBMForecaster,
        "catboost": CatBoostForecaster,
    }

    @classmethod
    def create(
        cls,
        model_name: str,
        model_config: Optional[ModelConfig] = None,
        **kwargs: Any,
    ) -> BaseForecaster:
        """
        Creates and returns a forecaster instance.

        Args:
            model_name: Identifier string of the model.
            model_config: ModelConfig instance for default parameters.
            **kwargs: Extra parameters passed to the model constructor.

        Returns:
            BaseForecaster: Instantiated model wrapper.
        """
        key = model_name.lower().strip()
        if key not in cls._MODEL_MAP:
            valid_models = list(cls._MODEL_MAP.keys())
            raise ValueError(
                f"Unknown model_name '{model_name}'. Valid models: {valid_models}"
            )

        model_cls = cls._MODEL_MAP[key]
        params = kwargs.copy()
        if model_config:
            params.setdefault("random_state", model_config.random_seed)
            if key == "seasonal_naive":
                params.setdefault("seasonal_period", model_config.seasonal_period)

        logger.info(f"Instantiating model '{model_name}' ({model_cls.__name__})")

        if key == "seasonal_naive":
            s_period = params.pop("seasonal_period", 7)
            return SeasonalNaiveForecaster(
                name="SeasonalNaive", seasonal_period=s_period, params=params
            )

        return model_cls(name=model_cls.__name__.replace("Forecaster", ""), params=params)

    @classmethod
    def get_supported_models(cls) -> Dict[str, str]:
        """Returns dictionary of supported model names and their corresponding class names."""
        return {k: v.__name__ for k, v in cls._MODEL_MAP.items()}
