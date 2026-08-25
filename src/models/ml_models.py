"""
Machine Learning Forecasting Models (Linear Regression, Random Forest, XGBoost, LightGBM, CatBoost).
"""

from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor

from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor

from src.models.base import BaseForecaster
from src.utils.logger import get_logger

logger = get_logger("models.ml_models")


def _prepare_feature_types(X: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """Helper to separate numeric and categorical features and drop non-feature date columns."""
    df_clean = X.copy()
    if "date" in df_clean.columns:
        df_clean = df_clean.drop(columns=["date"])

    num_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df_clean.select_dtypes(include=["object", "category"]).columns.tolist()
    return df_clean, num_cols, cat_cols


class RidgeRegressionForecaster(BaseForecaster):
    """Ridge Regression with Scikit-Learn Pipeline and ColumnTransformer."""

    def __init__(self, name: str = "RidgeRegression", params: Optional[Dict[str, Any]] = None):
        super().__init__(name=name, params=params)
        self.alpha = self.params.get("alpha", 1.0)
        self.pipeline: Optional[Pipeline] = None

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "RidgeRegressionForecaster":
        X_clean, num_cols, cat_cols = _prepare_feature_types(X)

        num_transformer = Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )
        cat_transformer = Pipeline(
            [
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
            ]
        )

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", num_transformer, num_cols),
                ("cat", cat_transformer, cat_cols),
            ]
        )

        self.pipeline = Pipeline(
            [
                ("preprocessor", preprocessor),
                ("regressor", Ridge(alpha=self.alpha, random_state=self.params.get("random_state", 42))),
            ]
        )

        self.pipeline.fit(X_clean, y)
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted or self.pipeline is None:
            raise ValueError(f"Model {self.name} is not fitted yet.")

        X_clean, _, _ = _prepare_feature_types(X)
        preds = self.pipeline.predict(X_clean)
        return np.maximum(0.0, preds)


class RandomForestForecaster(BaseForecaster):
    """Random Forest Regressor Forecaster."""

    def __init__(self, name: str = "RandomForest", params: Optional[Dict[str, Any]] = None):
        super().__init__(name=name, params=params)
        self.pipeline: Optional[Pipeline] = None

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "RandomForestForecaster":
        X_clean, num_cols, cat_cols = _prepare_feature_types(X)

        num_transformer = Pipeline([("imputer", SimpleImputer(strategy="median"))])
        cat_transformer = Pipeline(
            [
                ("imputer", SimpleImputer(strategy="most_frequent")),
                (
                    "encoder",
                    OrdinalEncoder(
                        handle_unknown="use_encoded_value", unknown_value=-1
                    ),
                ),
            ]
        )

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", num_transformer, num_cols),
                ("cat", cat_transformer, cat_cols),
            ]
        )

        rf_params = {
            "n_estimators": self.params.get("n_estimators", 100),
            "max_depth": self.params.get("max_depth", 10),
            "random_state": self.params.get("random_state", 42),
            "n_jobs": self.params.get("n_jobs", -1),
        }

        self.pipeline = Pipeline(
            [
                ("preprocessor", preprocessor),
                ("regressor", RandomForestRegressor(**rf_params)),
            ]
        )

        self.pipeline.fit(X_clean, y)
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted or self.pipeline is None:
            raise ValueError(f"Model {self.name} is not fitted yet.")

        X_clean, _, _ = _prepare_feature_types(X)
        preds = self.pipeline.predict(X_clean)
        return np.maximum(0.0, preds)


class XGBoostForecaster(BaseForecaster):
    """XGBoost Regressor Forecaster."""

    def __init__(self, name: str = "XGBoost", params: Optional[Dict[str, Any]] = None):
        super().__init__(name=name, params=params)
        self.pipeline: Optional[Pipeline] = None

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "XGBoostForecaster":
        X_clean, num_cols, cat_cols = _prepare_feature_types(X)

        num_transformer = Pipeline([("imputer", SimpleImputer(strategy="median"))])
        cat_transformer = Pipeline(
            [
                ("imputer", SimpleImputer(strategy="most_frequent")),
                (
                    "encoder",
                    OrdinalEncoder(
                        handle_unknown="use_encoded_value", unknown_value=-1
                    ),
                ),
            ]
        )

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", num_transformer, num_cols),
                ("cat", cat_transformer, cat_cols),
            ]
        )

        xgb_params = {
            "n_estimators": self.params.get("n_estimators", 100),
            "max_depth": self.params.get("max_depth", 6),
            "learning_rate": self.params.get("learning_rate", 0.1),
            "random_state": self.params.get("random_state", 42),
            "n_jobs": self.params.get("n_jobs", -1),
        }

        self.pipeline = Pipeline(
            [
                ("preprocessor", preprocessor),
                ("regressor", XGBRegressor(**xgb_params)),
            ]
        )

        self.pipeline.fit(X_clean, y)
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted or self.pipeline is None:
            raise ValueError(f"Model {self.name} is not fitted yet.")

        X_clean, _, _ = _prepare_feature_types(X)
        preds = self.pipeline.predict(X_clean)
        return np.maximum(0.0, preds)


class LightGBMForecaster(BaseForecaster):
    """LightGBM Regressor Forecaster."""

    def __init__(self, name: str = "LightGBM", params: Optional[Dict[str, Any]] = None):
        super().__init__(name=name, params=params)
        self.model: Optional[LGBMRegressor] = None
        self.feature_columns: List[str] = []

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "LightGBMForecaster":
        X_clean, num_cols, cat_cols = _prepare_feature_types(X)

        # Convert categorical columns to category dtype for native LightGBM handling
        for col in cat_cols:
            X_clean[col] = X_clean[col].astype("category")

        lgb_params = {
            "n_estimators": self.params.get("n_estimators", 100),
            "max_depth": self.params.get("max_depth", 6),
            "learning_rate": self.params.get("learning_rate", 0.1),
            "random_state": self.params.get("random_state", 42),
            "verbosity": self.params.get("verbosity", -1),
            "n_jobs": self.params.get("n_jobs", -1),
        }

        self.model = LGBMRegressor(**lgb_params)
        self.model.fit(X_clean, y)
        self.feature_columns = list(X_clean.columns)
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted or self.model is None:
            raise ValueError(f"Model {self.name} is not fitted yet.")

        X_clean, num_cols, cat_cols = _prepare_feature_types(X)
        for col in cat_cols:
            X_clean[col] = X_clean[col].astype("category")

        preds = self.model.predict(X_clean[self.feature_columns])
        return np.maximum(0.0, preds)


class CatBoostForecaster(BaseForecaster):
    """CatBoost Regressor Forecaster."""

    def __init__(self, name: str = "CatBoost", params: Optional[Dict[str, Any]] = None):
        super().__init__(name=name, params=params)
        self.model: Optional[CatBoostRegressor] = None
        self.feature_columns: List[str] = []
        self.cat_cols: List[str] = []

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "CatBoostForecaster":
        X_clean, num_cols, cat_cols = _prepare_feature_types(X)

        # Ensure categoricals are filled and strings
        for col in cat_cols:
            X_clean[col] = X_clean[col].fillna("missing").astype(str)

        # Fill NaNs in numeric features
        for col in num_cols:
            if X_clean[col].isna().any():
                X_clean[col] = X_clean[col].fillna(X_clean[col].median())

        cat_params = {
            "iterations": self.params.get("iterations", 100),
            "learning_rate": self.params.get("learning_rate", 0.1),
            "random_seed": self.params.get("random_seed", 42),
            "verbose": self.params.get("verbose", 0),
        }

        self.model = CatBoostRegressor(**cat_params)
        self.model.fit(X_clean, y, cat_features=cat_cols)
        self.feature_columns = list(X_clean.columns)
        self.cat_cols = cat_cols
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted or self.model is None:
            raise ValueError(f"Model {self.name} is not fitted yet.")

        X_clean, num_cols, cat_cols = _prepare_feature_types(X)
        for col in self.cat_cols:
            if col in X_clean.columns:
                X_clean[col] = X_clean[col].fillna("missing").astype(str)
        for col in num_cols:
            if col in X_clean.columns and X_clean[col].isna().any():
                X_clean[col] = X_clean[col].fillna(0.0)

        preds = self.model.predict(X_clean[self.feature_columns])
        return np.maximum(0.0, preds)
