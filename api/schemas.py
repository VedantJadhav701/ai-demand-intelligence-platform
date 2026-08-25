"""
Pydantic Request and Response schemas for FastAPI endpoints.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class ForecastRequest(BaseModel):
    horizon: int = Field(..., description="Forecast horizon in days (1, 7, 14, or 30)", example=7)
    store_id: str = Field(..., description="Store identifier", example="STORE_17")
    product_id: str = Field(..., description="Product identifier", example="PRODUCT_A")
    date: str = Field(..., description="Target forecast date (YYYY-MM-DD)", example="2026-08-23")
    features: Dict[str, Any] = Field(
        default_factory=dict,
        description="Feature dictionary (lags, rolling stats, price, discount, etc.)",
        example={
            "price": 20.0,
            "discount": 0.0,
            "lag_1": 25.0,
            "lag_7": 24.0,
            "rolling_mean_7": 23.5,
        },
    )

    @field_validator("horizon")
    @classmethod
    def validate_horizon(cls, v: int) -> int:
        if v not in [1, 7, 14, 30]:
            raise ValueError(f"Horizon {v} is invalid. Must be one of [1, 7, 14, 30].")
        return v


class ForecastResponse(BaseModel):
    prediction_id: str
    forecast: float
    horizon: int
    store_id: str
    product_id: str
    date: str
    model: str
    model_registry_name: str
    model_alias: str
    feature_version: str
    inference_time_ms: float
    forecast_timestamp: str


class BatchForecastRequest(BaseModel):
    records: List[ForecastRequest] = Field(..., description="List of forecast request records")


class BatchForecastResponse(BaseModel):
    total_records: int
    successful_predictions: int
    failed_predictions: int
    total_latency_ms: float
    predictions: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]


class ModelMetadata(BaseModel):
    horizon: int
    name: str
    alias: str
    model_type: str
    feature_version: str
    cached_in_memory: bool
    uri: str


class ModelListResponse(BaseModel):
    status: str
    total_models: int
    models: List[ModelMetadata]


class HorizonMetrics(BaseModel):
    horizon: int
    model: str
    registry_name: str
    selection_source: str
    cv_wape: float
    test_wape: float


class MetricsResponse(BaseModel):
    status: str
    total_horizons: int
    metrics: List[HorizonMetrics]


class ExplainRequest(BaseModel):
    horizon: int = Field(..., description="Forecast horizon in days (1, 7, 14, or 30)", example=7)
    store_id: str = Field(..., description="Store identifier", example="STORE_17")
    product_id: str = Field(..., description="Product identifier", example="PRODUCT_A")
    date: str = Field(..., description="Target forecast date (YYYY-MM-DD)", example="2026-08-23")
    features: Dict[str, Any] = Field(default_factory=dict, description="Feature dictionary")
    top_n: int = Field(5, description="Number of top positive/negative features to report", example=5)

    @field_validator("horizon")
    @classmethod
    def validate_horizon(cls, v: int) -> int:
        if v not in [1, 7, 14, 30]:
            raise ValueError(f"Horizon {v} is invalid. Must be one of [1, 7, 14, 30].")
        return v


class FeatureDriver(BaseModel):
    feature: str
    feature_value: Any
    shap_value: float


class ExplainResponse(BaseModel):
    prediction_id: str
    prediction: float
    base_value: float
    horizon: int
    store_id: str
    product_id: str
    date: str
    model: str
    model_registry_name: str
    model_alias: str
    top_positive: List[FeatureDriver]
    top_negative: List[FeatureDriver]
    shap_values: Dict[str, float]


class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: str


class ReadinessResponse(BaseModel):
    status: str = "ready"
    mlflow_tracking_uri: str
    registry_prefix: str
    models_status: Dict[str, str]
    timestamp: str
