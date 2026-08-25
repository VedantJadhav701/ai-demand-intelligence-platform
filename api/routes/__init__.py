"""
API router initialization package.
"""

from api.routes.health import router as health_router
from api.routes.forecast import router as forecast_router
from api.routes.model import router as model_router
from api.routes.metrics import router as metrics_router
from api.routes.explain import router as explain_router

__all__ = [
    "health_router",
    "forecast_router",
    "model_router",
    "metrics_router",
    "explain_router",
]
