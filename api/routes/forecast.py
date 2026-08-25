"""
Forecasting endpoints for point and batch demand prediction.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from api.schemas import (
    ForecastRequest,
    ForecastResponse,
    BatchForecastRequest,
    BatchForecastResponse,
)
from api.dependencies import get_forecast_service
from src.services.forecast_service import ForecastService
from src.services.model_service import UnsupportedHorizonError, ModelLoadError

router = APIRouter(tags=["Forecasting"])


@router.post(
    "/forecast",
    response_model=ForecastResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Point Demand Forecast",
    description="Generates demand prediction for a single store, product, and horizon record.",
)
def predict_forecast(
    req: ForecastRequest,
    forecast_service: ForecastService = Depends(get_forecast_service),
) -> ForecastResponse:
    try:
        res = forecast_service.predict_single(
            horizon=req.horizon,
            store_id=req.store_id,
            product_id=req.product_id,
            date_str=req.date,
            features=req.features,
        )
        return ForecastResponse(**res)
    except UnsupportedHorizonError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ModelLoadError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Production model unavailable: {str(e)}",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid forecast request or features: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal forecasting error: {str(e)}",
        )


@router.post(
    "/batch_predict",
    response_model=BatchForecastResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Batch Demand Forecast",
    description="Generates demand predictions for multiple store/product forecast records.",
)
def predict_batch(
    req: BatchForecastRequest,
    forecast_service: ForecastService = Depends(get_forecast_service),
) -> BatchForecastResponse:
    try:
        raw_records = [r.model_dump() for r in req.records]
        res = forecast_service.predict_batch(raw_records)
        return BatchForecastResponse(**res)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch forecasting error: {str(e)}",
        )
