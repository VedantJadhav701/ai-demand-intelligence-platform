"""
Model metadata endpoints.
"""

from fastapi import APIRouter, Depends, status

from api.schemas import ModelListResponse, ModelMetadata
from api.dependencies import get_model_service
from src.services.model_service import ModelService

router = APIRouter(tags=["Model Registry"])


@router.get(
    "/model",
    response_model=ModelListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Production Registered Models",
    description="Returns list of registered production models, supported horizons, and memory caching status.",
)
def list_models(
    model_service: ModelService = Depends(get_model_service),
) -> ModelListResponse:
    meta_list = model_service.get_model_metadata()
    models = [ModelMetadata(**m) for m in meta_list]
    return ModelListResponse(
        status="success",
        total_models=len(models),
        models=models,
    )
