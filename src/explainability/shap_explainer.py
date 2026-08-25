"""
SHAP Model Explainer module for computing tree model feature importance and local prediction explanations.
"""

from typing import Dict, Any, List, Tuple, Optional, Union
import numpy as np
import pandas as pd
import shap
from pydantic import BaseModel, Field

from src.models.base import BaseForecaster
from src.models.ml_models import (
    CatBoostForecaster,
    LightGBMForecaster,
    RandomForestForecaster,
)
from src.utils.logger import get_logger

logger = get_logger("explainability.shap_explainer")


class FeatureImpact(BaseModel):
    feature_name: str
    feature_value: Any
    shap_value: float


class LocalExplanation(BaseModel):
    prediction: float
    base_value: float
    top_positive: List[FeatureImpact] = Field(default_factory=list)
    top_negative: List[FeatureImpact] = Field(default_factory=list)
    feature_values: Dict[str, Any] = Field(default_factory=dict)
    shap_values: Dict[str, float] = Field(default_factory=dict)


class GlobalExplanation(BaseModel):
    model_name: str
    feature_names: List[str]
    mean_abs_shap: Dict[str, float] = Field(default_factory=dict)
    feature_ranking: List[Tuple[str, float]] = Field(default_factory=list)


class ModelExplainer:
    """
    SHAP Model Explainer for tree-based forecasters (CatBoost, LightGBM, Random Forest).
    Computes global feature importance and local instance-level SHAP attributions.
    """

    def __init__(self, forecaster: BaseForecaster, X_sample: pd.DataFrame):
        self.forecaster = forecaster
        self.raw_X = X_sample.copy()
        self.model_name = forecaster.name
        self.explainer: Optional[shap.Explainer] = None
        self.shap_values_matrix: Optional[np.ndarray] = None
        self.base_value: float = 0.0
        self.feature_names: List[str] = []
        self.processed_X: Optional[pd.DataFrame] = None

        self._fit_explainer()

    def _fit_explainer(self) -> None:
        """Extracts underlying tree model and preprocessed feature matrix, then builds SHAP TreeExplainer."""
        logger.info(f"Fitting SHAP Explainer for model '{self.model_name}'...")

        if isinstance(self.forecaster, CatBoostForecaster):
            cb_model = self.forecaster.model
            X_clean = self.raw_X.copy()
            if "date" in X_clean.columns:
                X_clean = X_clean.drop(columns=["date"])
            for col in self.forecaster.cat_cols:
                if col in X_clean.columns:
                    X_clean[col] = X_clean[col].fillna("missing").astype(str)
            for col in X_clean.select_dtypes(include=[np.number]).columns:
                if X_clean[col].isna().any():
                    X_clean[col] = X_clean[col].fillna(0.0)

            self.processed_X = X_clean[self.forecaster.feature_columns]
            self.feature_names = list(self.processed_X.columns)

            self.explainer = shap.TreeExplainer(cb_model)
            shap_obj = self.explainer(self.processed_X)
            self.shap_values_matrix = shap_obj.values
            self.base_value = float(
                shap_obj.base_values[0]
                if isinstance(shap_obj.base_values, np.ndarray)
                else shap_obj.base_values
            )

        elif isinstance(self.forecaster, LightGBMForecaster):
            lgb_model = self.forecaster.model
            X_clean = self.raw_X.copy()
            if "date" in X_clean.columns:
                X_clean = X_clean.drop(columns=["date"])
            for col in X_clean.select_dtypes(include=["object", "category"]).columns:
                X_clean[col] = X_clean[col].astype("category")

            self.processed_X = X_clean[self.forecaster.feature_columns]
            self.feature_names = list(self.processed_X.columns)

            self.explainer = shap.TreeExplainer(lgb_model)
            self.shap_values_matrix = self.explainer.shap_values(self.processed_X)
            if isinstance(self.shap_values_matrix, list):
                self.shap_values_matrix = self.shap_values_matrix[0]

            bv = self.explainer.expected_value
            self.base_value = float(bv[0] if isinstance(bv, (list, np.ndarray)) else bv)

        elif isinstance(self.forecaster, RandomForestForecaster):
            pipe = self.forecaster.pipeline
            preprocessor = pipe.named_steps["preprocessor"]
            rf_model = pipe.named_steps["regressor"]

            X_clean = self.raw_X.copy()
            if "date" in X_clean.columns:
                X_clean = X_clean.drop(columns=["date"])

            X_trans = preprocessor.transform(X_clean)
            try:
                feature_names = list(preprocessor.get_feature_names_out())
            except Exception:
                feature_names = [f"feature_{i}" for i in range(X_trans.shape[1])]

            self.processed_X = pd.DataFrame(X_trans, columns=feature_names)
            self.feature_names = feature_names

            self.explainer = shap.TreeExplainer(rf_model)
            self.shap_values_matrix = self.explainer.shap_values(self.processed_X)

            bv = self.explainer.expected_value
            self.base_value = float(bv[0] if isinstance(bv, (list, np.ndarray)) else bv)
        else:
            raise ValueError(
                f"SHAP explanation is not directly supported for model '{self.model_name}'."
            )

        logger.info(
            f"SHAP Explainer successfully fit for '{self.model_name}'. Matrix shape: {self.shap_values_matrix.shape}"
        )

    def get_global_explanation(self) -> GlobalExplanation:
        """Calculates mean absolute SHAP values and feature ranking."""
        mean_abs = np.mean(np.abs(self.shap_values_matrix), axis=0)
        mean_dict: Dict[str, float] = {}

        for feat, val in zip(self.feature_names, mean_abs):
            mean_dict[feat] = round(float(val), 4)

        ranking = sorted(mean_dict.items(), key=lambda x: x[1], reverse=True)

        return GlobalExplanation(
            model_name=self.model_name,
            feature_names=self.feature_names,
            mean_abs_shap=mean_dict,
            feature_ranking=ranking,
        )

    def explain_instance(self, row_idx: int = 0, top_n: int = 5) -> LocalExplanation:
        """
        Generates local explanation for a specific prediction row.

        Args:
            row_idx: Index of row in processed_X to explain.
            top_n: Number of top positive and negative features to return.

        Returns:
            LocalExplanation: Structured local explanation instance.
        """
        if row_idx >= len(self.processed_X):
            raise IndexError(f"row_idx {row_idx} out of range for dataset length {len(self.processed_X)}.")

        shaps = self.shap_values_matrix[row_idx]
        feat_vals = self.processed_X.iloc[row_idx].to_dict()

        # Compute model prediction for instance
        instance_df = self.raw_X.iloc[[row_idx]]
        prediction = float(self.forecaster.predict(instance_df)[0])

        shap_dict: Dict[str, float] = {}
        impacts: List[FeatureImpact] = []

        for name, val, s_val in zip(self.feature_names, self.processed_X.iloc[row_idx], shaps):
            s_float = round(float(s_val), 4)
            shap_dict[name] = s_float
            impacts.append(
                FeatureImpact(
                    feature_name=name, feature_value=val, shap_value=s_float
                )
            )

        pos_impacts = sorted(
            [imp for imp in impacts if imp.shap_value > 0],
            key=lambda x: x.shap_value,
            reverse=True,
        )[:top_n]
        neg_impacts = sorted(
            [imp for imp in impacts if imp.shap_value < 0],
            key=lambda x: x.shap_value,
        )[:top_n]

        return LocalExplanation(
            prediction=round(prediction, 4),
            base_value=round(self.base_value, 4),
            top_positive=pos_impacts,
            top_negative=neg_impacts,
            feature_values={k: (str(v) if not isinstance(v, (int, float, bool)) else v) for k, v in feat_vals.items()},
            shap_values=shap_dict,
        )

    def verify_additivity(self, row_idx: int = 0, atol: float = 1e-1) -> Tuple[bool, float, float]:
        """
        Verifies numerical consistency: base_value + sum(shap_values) == prediction.

        Args:
            row_idx: Index of instance to verify.
            atol: Absolute numerical tolerance.

        Returns:
            Tuple[bool, float, float]: (is_consistent, predicted_val, shap_sum_val)
        """
        shaps = self.shap_values_matrix[row_idx]
        shap_sum = float(self.base_value + np.sum(shaps))

        # Model prediction
        instance_df = self.raw_X.iloc[[row_idx]]
        pred_val = float(self.forecaster.predict(instance_df)[0])

        is_consistent = bool(np.isclose(pred_val, shap_sum, atol=atol))
        return is_consistent, pred_val, round(shap_sum, 4)
