"""
Dependency injection module for FastAPI service instances.
"""

from typing import Generator
from src.utils.config import load_config, AppConfig
from src.services.model_service import ModelService
from src.services.forecast_service import ForecastService
from src.services.explainability_service import ExplainabilityService

_config_instance: AppConfig = load_config()
_model_service_instance: ModelService = ModelService(config=_config_instance.experiment.mlflow)
_forecast_service_instance: ForecastService = ForecastService(
    model_service=_model_service_instance, model_config=_config_instance.model
)
_explainability_service_instance: ExplainabilityService = ExplainabilityService(
    model_service=_model_service_instance, forecast_service=_forecast_service_instance
)


def get_config() -> AppConfig:
    """Returns application configuration instance."""
    return _config_instance


def get_model_service() -> ModelService:
    """Returns ModelService singleton instance."""
    return _model_service_instance


def get_forecast_service() -> ForecastService:
    """Returns ForecastService singleton instance."""
    return _forecast_service_instance


def get_explainability_service() -> ExplainabilityService:
    """Returns ExplainabilityService singleton instance."""
    return _explainability_service_instance
