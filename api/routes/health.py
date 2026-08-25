"""
Health and Readiness check endpoints.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from api.schemas import HealthResponse, ReadinessResponse
from api.dependencies import get_model_service
from src.services.model_service import ModelService

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Lightweight API Health Check",
    description="Indicates whether the FastAPI service process is alive.",
)
def get_health() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Service Readiness Check",
    description="Verifies MLflow connectivity and ability to resolve registered production models.",
)
def get_readiness(model_service: ModelService = Depends(get_model_service)) -> ReadinessResponse:
    models_status = {}
    all_ready = True

    for h in model_service.SUPPORTED_HORIZONS:
        reg_name = model_service.get_registry_name(h)
        try:
            # Check if model can be resolved from cache or MLflow
            _ = model_service.get_model(horizon=h)
            models_status[f"{h}d ({reg_name})"] = "READY"
        except Exception as e:
            models_status[f"{h}d ({reg_name})"] = f"UNAVAILABLE ({str(e)})"
            all_ready = False

    if not all_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "message": "One or more production models are unavailable.",
                "models_status": models_status,
            },
        )

    return ReadinessResponse(
        status="ready",
        mlflow_tracking_uri=model_service.tracking_uri,
        registry_prefix=model_service.prefix,
        models_status=models_status,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )
