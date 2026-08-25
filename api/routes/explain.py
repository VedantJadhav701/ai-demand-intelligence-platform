"""
Explainability endpoints for SHAP feature drivers and local prediction attributions.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from api.schemas import ExplainRequest, ExplainResponse
from api.dependencies import get_explainability_service
from src.services.explainability_service import ExplainabilityService
from src.services.model_service import UnsupportedHorizonError, ModelLoadError

router = APIRouter(tags=["Explainability"])


@router.post(
    "/explain",
    response_model=ExplainResponse,
    status_code=status.HTTP_200_OK,
    summary="Explain Demand Forecast with SHAP",
    description="Returns positive and negative SHAP feature driver contributions for a specific prediction request.",
)
def explain_forecast(
    req: ExplainRequest,
    explainability_service: ExplainabilityService = Depends(get_explainability_service),
) -> ExplainResponse:
    try:
        res = explainability_service.explain_forecast(
            horizon=req.horizon,
            store_id=req.store_id,
            product_id=req.product_id,
            date_str=req.date,
            features=req.features,
            top_n=req.top_n,
        )
        return ExplainResponse(**res)
    except UnsupportedHorizonError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ModelLoadError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Production model unavailable for SHAP explanation: {str(e)}",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid feature schema or SHAP request: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SHAP explanation error: {str(e)}",
        )
