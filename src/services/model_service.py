"""
ModelService for resolving horizons, loading production models from MLflow Model Registry using aliases,
maintaining an in-process thread-safe model cache, and serving model metadata.
"""

import os
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import mlflow

from src.utils.config import MLflowConfig, AppConfig, load_config
from src.utils.logger import get_logger

logger = get_logger("services.model_service")


class ModelLoadError(Exception):
    """Raised when a model fails to load from MLflow Model Registry."""
    pass


class UnsupportedHorizonError(ValueError):
    """Raised when an unsupported forecast horizon is requested."""
    pass


class ModelService:
    """
    Service layer for managing horizon-specific MLflow model loading and caching.
    """

    SUPPORTED_HORIZONS: List[int] = [1, 7, 14, 30]

    def __init__(self, config: Optional[MLflowConfig] = None):
        self.config = config or MLflowConfig()
        self.tracking_uri = os.getenv("MLFLOW_TRACKING_URI", self.config.tracking_uri)
        self.prefix = os.getenv("MODEL_REGISTRY_PREFIX", self.config.registry_name_prefix).strip().rstrip("-")
        self.default_alias = os.getenv("MODEL_DEFAULT_ALIAS", "production")

        # Enable filesystem store if file URI is used
        os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"
        mlflow.set_tracking_uri(self.tracking_uri)

        self._model_cache: Dict[str, Any] = {}
        self._lock = threading.Lock()
        logger.info(
            f"ModelService initialized. Tracking URI: '{self.tracking_uri}', Prefix: '{self.prefix}', Default Alias: '{self.default_alias}'"
        )

    def get_registry_name(self, horizon: int) -> str:
        """Constructs horizon-specific registered model name (e.g. 'demand-catboost-h14')."""
        if horizon not in self.SUPPORTED_HORIZONS:
            raise UnsupportedHorizonError(
                f"Horizon {horizon}d is unsupported. Supported horizons: {self.SUPPORTED_HORIZONS}"
            )
        return f"{self.prefix}-catboost-h{horizon}"

    def get_model_uri(self, horizon: int, alias: Optional[str] = None) -> str:
        """Constructs MLflow model URI using alias (e.g. 'models:/demand-catboost-h14@production')."""
        reg_name = self.get_registry_name(horizon)
        target_alias = alias or self.default_alias
        return f"models:/{reg_name}@{target_alias}"

    def get_model(self, horizon: int, alias: Optional[str] = None, force_reload: bool = False) -> Any:
        """
        Retrieves loaded model from in-memory cache or loads it from MLflow Model Registry.

        Args:
            horizon: Forecast horizon in days (1, 7, 14, 30).
            alias: Model alias tag ('production', 'staging', 'candidate').
            force_reload: If True, bypasses cache and re-downloads model from registry.

        Returns:
            Any: Loaded PyFunc / Forecaster model instance.
        """
        reg_name = self.get_registry_name(horizon)
        target_alias = alias or self.default_alias
        cache_key = f"{reg_name}@{target_alias}"

        if not force_reload:
            with self._lock:
                if cache_key in self._model_cache:
                    logger.debug(f"Serving model '{cache_key}' from memory cache.")
                    return self._model_cache[cache_key]

        model_uri = self.get_model_uri(horizon, alias=target_alias)
        logger.info(f"Loading production model from MLflow registry: '{model_uri}'...")

        try:
            loaded_model = mlflow.pyfunc.load_model(model_uri)
            with self._lock:
                self._model_cache[cache_key] = loaded_model
            logger.info(f"Successfully cached model '{cache_key}'.")
            return loaded_model
        except Exception as e:
            logger.error(f"Failed to load model from '{model_uri}': {e}")
            raise ModelLoadError(f"Could not load model '{model_uri}': {str(e)}") from e

    def clear_cache(self) -> None:
        """Clears all cached models in memory."""
        with self._lock:
            self._model_cache.clear()
            logger.info("Cleared in-memory model cache.")

    def get_model_metadata(self) -> List[Dict[str, Any]]:
        """Returns metadata list of all supported horizon models."""
        metadata = []
        for h in self.SUPPORTED_HORIZONS:
            reg_name = self.get_registry_name(h)
            cached = f"{reg_name}@{self.default_alias}" in self._model_cache
            metadata.append(
                {
                    "horizon": h,
                    "name": reg_name,
                    "alias": self.default_alias,
                    "model_type": "catboost",
                    "feature_version": self.config.feature_version,
                    "cached_in_memory": cached,
                    "uri": self.get_model_uri(h),
                }
            )
        return metadata
