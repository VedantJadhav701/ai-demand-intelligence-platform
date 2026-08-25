"""
ForecastService for executing point and batch demand forecasting requests using ModelService.
"""

import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from src.services.model_service import ModelService, UnsupportedHorizonError, ModelLoadError
from src.utils.config import ModelConfig
from src.utils.logger import get_logger

logger = get_logger("services.forecast_service")


class ForecastService:
    """
    Service layer orchestrating single-point and batch demand forecasts.
    """

    def __init__(self, model_service: ModelService, model_config: Optional[ModelConfig] = None):
        self.model_service = model_service
        self.model_config = model_config or ModelConfig()

    def _prepare_feature_dataframe(
        self,
        store_id: str,
        product_id: str,
        date_str: str,
        features: Dict[str, Any],
        model: Optional[Any] = None,
    ) -> pd.DataFrame:
        """Constructs a validated pandas DataFrame row with temporal features for model inference."""
        dt = pd.to_datetime(date_str)

        row_dict = {
            "store_id": str(store_id),
            "product_id": str(product_id),
            "date": str(date_str),
            "day_of_week": int(dt.dayofweek),
            "day_of_month": int(dt.day),
            "week_of_year": int(dt.isocalendar().week),
            "month": int(dt.month),
            "quarter": int(dt.quarter),
            "year": int(dt.year),
            "is_weekend": int(dt.dayofweek >= 5),
            "is_month_start": int(dt.is_month_start),
            "is_month_end": int(dt.is_month_end),
            "price": 20.0,
            "discount": 0.0,
            "price_change": 0.0,
            "discount_change": 0.0,
        }
        # Merge user input features
        for k, v in features.items():
            row_dict[k] = v

        # Unwrap model if python_model
        if model is not None:
            unwrapped = model
            if hasattr(unwrapped, "unwrap_python_model"):
                unwrapped = unwrapped.unwrap_python_model().forecaster
            elif hasattr(unwrapped, "forecaster"):
                unwrapped = unwrapped.forecaster

            expected_cols = getattr(unwrapped, "feature_columns", None)
            if expected_cols:
                cat_cols = getattr(unwrapped, "cat_cols", ["store_type", "product_category", "region", "store_id", "product_id"])
                for col in expected_cols:
                    if col not in row_dict:
                        if col in cat_cols:
                            row_dict[col] = "missing"
                        else:
                            row_dict[col] = 0.0

        df = pd.DataFrame([row_dict])
        return df

    def predict_single(
        self,
        horizon: int,
        store_id: str,
        product_id: str,
        date_str: str,
        features: Dict[str, Any],
        alias: str = "production",
    ) -> Dict[str, Any]:
        """
        Generates point forecast for a single store/product record.

        Args:
            horizon: Forecast horizon (1, 7, 14, 30).
            store_id: Store identifier.
            product_id: Product identifier.
            date_str: Target forecast date (YYYY-MM-DD).
            features: Dictionary of input features.
            alias: Model alias tag.

        Returns:
            Dict[str, Any]: Structured forecast result dictionary.
        """
        start_t = time.perf_counter()

        model = self.model_service.get_model(horizon=horizon, alias=alias)
        reg_name = self.model_service.get_registry_name(horizon)

        X_df = self._prepare_feature_dataframe(store_id, product_id, date_str, features, model=model)

        try:
            raw_preds = model.predict(X_df)
            pred_val = float(raw_preds[0]) if isinstance(raw_preds, (np.ndarray, list)) else float(raw_preds)
            forecast_val = max(0.0, round(pred_val, 2))
        except Exception as e:
            logger.error(f"Inference execution error for {store_id}/{product_id} h={horizon}d: {e}")
            raise ValueError(f"Model inference failed: {str(e)}") from e

        latency_ms = (time.perf_counter() - start_t) * 1000.0
        pred_id = f"pred_{uuid.uuid4().hex[:12]}"

        return {
            "prediction_id": pred_id,
            "horizon": horizon,
            "store_id": store_id,
            "product_id": product_id,
            "date": date_str,
            "forecast": forecast_val,
            "model": "catboost",
            "model_registry_name": reg_name,
            "model_alias": alias,
            "feature_version": self.model_service.config.feature_version,
            "inference_time_ms": round(latency_ms, 2),
            "forecast_timestamp": datetime.utcnow().isoformat() + "Z",
        }

    def predict_batch(
        self, records: List[Dict[str, Any]], alias: str = "production"
    ) -> Dict[str, Any]:
        """
        Generates forecasts for a list of prediction records.

        Args:
            records: List of forecast request records.
            alias: Model alias tag.

        Returns:
            Dict[str, Any]: Batch prediction summary containing predictions and any per-record errors.
        """
        start_t = time.perf_counter()
        predictions = []
        errors = []

        for i, rec in enumerate(records):
            try:
                h = rec["horizon"]
                s_id = rec["store_id"]
                p_id = rec["product_id"]
                d_str = rec["date"]
                feats = rec.get("features", {})

                res = self.predict_single(
                    horizon=h,
                    store_id=s_id,
                    product_id=p_id,
                    date_str=d_str,
                    features=feats,
                    alias=alias,
                )
                res["record_index"] = i
                predictions.append(res)
            except Exception as e:
                errors.append(
                    {
                        "record_index": i,
                        "store_id": rec.get("store_id", "unknown"),
                        "product_id": rec.get("product_id", "unknown"),
                        "horizon": rec.get("horizon", 0),
                        "error": str(e),
                    }
                )

        total_latency_ms = (time.perf_counter() - start_t) * 1000.0

        return {
            "total_records": len(records),
            "successful_predictions": len(predictions),
            "failed_predictions": len(errors),
            "total_latency_ms": round(total_latency_ms, 2),
            "predictions": predictions,
            "errors": errors,
        }
