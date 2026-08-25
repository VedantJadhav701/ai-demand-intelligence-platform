"""
ExplainabilityService for serving SHAP feature importance and local instance-level predictions.
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np

from src.services.model_service import ModelService
from src.services.forecast_service import ForecastService
from src.explainability.shap_explainer import ModelExplainer
from src.utils.logger import get_logger

logger = get_logger("services.explainability_service")


class ExplainabilityService:
    """
    Service layer providing safe, structured SHAP explanation capabilities for model forecasts.
    """

    def __init__(self, model_service: ModelService, forecast_service: ForecastService):
        self.model_service = model_service
        self.forecast_service = forecast_service

    def explain_forecast(
        self,
        horizon: int,
        store_id: str,
        product_id: str,
        date_str: str,
        features: Dict[str, Any],
        alias: str = "production",
        top_n: int = 5,
    ) -> Dict[str, Any]:
        """
        Generates local SHAP explanation for a point forecast request.

        Args:
            horizon: Forecast horizon (1, 7, 14, 30).
            store_id: Store identifier.
            product_id: Product identifier.
            date_str: Target forecast date (YYYY-MM-DD).
            features: Input features dictionary.
            alias: Model alias.
            top_n: Number of top positive/negative drivers to return.

        Returns:
            Dict[str, Any]: Structured SHAP explanation response dictionary.
        """
        # 1. Generate point forecast
        fc_res = self.forecast_service.predict_single(
            horizon=horizon,
            store_id=store_id,
            product_id=product_id,
            date_str=date_str,
            features=features,
            alias=alias,
        )

        # 2. Retrieve loaded model instance
        pyfunc_model = self.model_service.get_model(horizon=horizon, alias=alias)

        # Unwrap ForecasterPyFuncWrapper or underlying forecaster if present
        if hasattr(pyfunc_model, "unwrap_python_model"):
            forecaster = pyfunc_model.unwrap_python_model().forecaster
        elif hasattr(pyfunc_model, "forecaster"):
            forecaster = pyfunc_model.forecaster
        elif hasattr(pyfunc_model, "_model_impl"):
            forecaster = getattr(pyfunc_model._model_impl, "python_model", pyfunc_model).forecaster
        else:
            forecaster = pyfunc_model

        # 3. Construct input feature DataFrame aligned with model features
        X_df = self.forecast_service._prepare_feature_dataframe(
            store_id=store_id, product_id=product_id, date_str=date_str, features=features, model=pyfunc_model
        )

        # 4. Fit SHAP explainer on single row
        explainer = ModelExplainer(forecaster=forecaster, X_sample=X_df)
        local_exp = explainer.explain_instance(row_idx=0, top_n=top_n)

        def _clean_val(v: Any) -> Any:
            if isinstance(v, (np.integer, int)):
                return int(v)
            elif isinstance(v, (np.floating, float)):
                return float(v)
            else:
                return str(v)

        # 5. Format SHAP response payload
        top_pos = [
            {
                "feature": imp.feature_name,
                "feature_value": _clean_val(imp.feature_value),
                "shap_value": float(imp.shap_value),
            }
            for imp in local_exp.top_positive
        ]
        top_neg = [
            {
                "feature": imp.feature_name,
                "feature_value": _clean_val(imp.feature_value),
                "shap_value": float(imp.shap_value),
            }
            for imp in local_exp.top_negative
        ]
        clean_shap_values = {k: float(v) for k, v in local_exp.shap_values.items()}

        return {
            "prediction_id": fc_res["prediction_id"],
            "prediction": float(fc_res["forecast"]),
            "base_value": float(local_exp.base_value),
            "horizon": horizon,
            "store_id": store_id,
            "product_id": product_id,
            "date": date_str,
            "model": fc_res["model"],
            "model_registry_name": fc_res["model_registry_name"],
            "model_alias": fc_res["model_alias"],
            "top_positive": top_pos,
            "top_negative": top_neg,
            "shap_values": clean_shap_values,
        }
