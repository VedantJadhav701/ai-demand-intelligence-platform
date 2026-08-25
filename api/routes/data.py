"""
FastAPI routes for sales data upload, dataset validation, summary profiling,
and store/product dropdown lists.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from src.services.data_service import DataService
from src.utils.logger import get_logger

logger = get_logger("api.routes.data")
data_router = APIRouter(prefix="/data", tags=["Data Upload & Summary"])

# Singleton DataService instance
_data_service = DataService()


class DatasetSummaryResponse(BaseModel):
    total_rows: int
    total_stores: int
    total_products: int
    date_range: str
    missing_pct: float
    data_quality: str
    stores: List[str]
    products: List[str]
    is_valid: bool
    warnings: List[str]


class FeatureLookupResponse(BaseModel):
    store_id: str
    product_id: str
    derived_features: Dict[str, Any]


@data_router.post(
    "/upload",
    response_model=DatasetSummaryResponse,
    summary="Upload Sales Data CSV/Excel",
    description="Uploads a CSV or Excel dataset, validates schema, builds features, and returns summary metrics.",
)
async def upload_sales_data(file: UploadFile = File(...)):
    """
    Accepts CSV/Excel sales dataset file upload.
    """
    try:
        content = await file.read()
        summary = _data_service.process_file_upload(content, file.filename or "uploaded.csv")
        return DatasetSummaryResponse(**summary)
    except Exception as e:
        logger.error(f"Failed to process file upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parsing uploaded file: {str(e)}",
        ) from e


@data_router.get(
    "/summary",
    response_model=DatasetSummaryResponse,
    summary="Get Current Dataset Summary",
    description="Returns profiling metrics (rows, store count, product count, quality status) for current dataset.",
)
async def get_dataset_summary():
    """
    Returns dataset summary metrics.
    """
    summary = _data_service.get_summary()
    return DatasetSummaryResponse(**summary)


@data_router.get(
    "/lookup-features",
    response_model=FeatureLookupResponse,
    summary="Lookup Derived Features for Store & Product",
    description="Automatically extracts latest historical lag and rolling features for selected store and product.",
)
async def lookup_derived_features(store_id: str, product_id: str):
    """
    Returns automatically derived historical features.
    """
    features = _data_service.get_latest_features_for_series(store_id, product_id)
    return FeatureLookupResponse(
        store_id=store_id,
        product_id=product_id,
        derived_features=features,
    )
