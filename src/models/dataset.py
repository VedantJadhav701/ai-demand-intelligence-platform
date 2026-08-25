"""
Forecasting Dataset Builder for constructing horizon-specific supervised learning datasets
without temporal leakage.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any
import pandas as pd
import numpy as np

from src.utils.logger import get_logger
from src.features.builder import FeatureEngineer
from src.features.config import FeatureConfig
from src.utils.config import ModelConfig

logger = get_logger("models.dataset")


@dataclass
class ForecastingDataset:
    df: pd.DataFrame
    X: pd.DataFrame
    y: pd.Series
    meta: pd.DataFrame
    feature_names: List[str]
    categorical_features: List[str]
    horizon: int
    target_name: str


class ForecastingDatasetBuilder:
    """
    Constructs supervised time-series forecasting datasets for direct multi-horizon forecasting.
    Target y(t+h) represents actual units sold h steps ahead, while features X(t) strictly contain
    information available at or before time t.
    """

    def __init__(
        self,
        feature_engineer: Optional[FeatureEngineer] = None,
        model_config: Optional[ModelConfig] = None,
    ):
        self.feature_engineer = feature_engineer or FeatureEngineer()
        self.model_config = model_config or ModelConfig()

    def build_dataset(
        self,
        df: pd.DataFrame,
        horizon: int,
        target_col: Optional[str] = None,
        group_cols: Optional[List[str]] = None,
    ) -> ForecastingDataset:
        """
        Builds a supervised dataset for prediction horizon h.

        Args:
            df: Raw or validated pandas DataFrame.
            horizon: Forecast horizon step h (e.g., 1, 7, 14, 30 days).
            target_col: Target column name (default 'units_sold').
            group_cols: Series group identifier columns (default ['store_id', 'product_id']).

        Returns:
            ForecastingDataset: Container holding X, y, metadata, and feature definitions.
        """
        target = target_col or self.model_config.target_column
        groups = group_cols or ["store_id", "product_id"]
        date_col = "date"

        logger.info(f"Building forecasting dataset for horizon h={horizon}...")

        # Step 1. Apply Feature Engineering pipeline (lags, rolling stats, temporal)
        feat_df = self.feature_engineer.transform(df)

        # Ensure date is datetime and sorted chronologically per group
        feat_df[date_col] = pd.to_datetime(feat_df[date_col])
        sort_cols = [c for c in groups if c in feat_df.columns] + [date_col]
        feat_df = feat_df.sort_values(sort_cols).reset_index(drop=True)

        # Step 2. Drop initial row(s) where lag_1 is uncomputed (NaN)
        if "lag_1" in feat_df.columns:
            feat_df = feat_df.dropna(subset=["lag_1"]).reset_index(drop=True)

        # Step 3. Construct horizon target y[t+h] by shifting target by -horizon per group
        target_h_name = f"target_h{horizon}"

        if sort_cols and len(sort_cols) > 1:
            group_keys = [c for c in groups if c in feat_df.columns]
            feat_df[target_h_name] = (
                feat_df.groupby(group_keys)[target].shift(-horizon)
            )
        else:
            feat_df[target_h_name] = feat_df[target].shift(-horizon)

        # Step 3. Drop rows where future target is unavailable (tail end of series)
        valid_mask = feat_df[target_h_name].notna()
        valid_df = feat_df[valid_mask].copy().reset_index(drop=True)

        if valid_df.empty:
            raise ValueError(
                f"No valid rows remaining for horizon h={horizon}. Check dataset length vs horizon."
            )

        # Step 4. Separate metadata, target, and feature columns
        meta_cols = [c for c in [date_col, "store_id", "product_id", "units_sold"] if c in valid_df.columns]
        meta = valid_df[meta_cols].copy()
        y = valid_df[target_h_name].copy()

        # Feature matrix X must EXCLUDE target_h{h}, raw target (units_sold), and target-derived revenue
        exclude_cols = [target_h_name, target, "revenue"]

        feature_cols = [col for col in valid_df.columns if col not in exclude_cols]
        X = valid_df[feature_cols].copy()

        categorical_cols = [
            col
            for col in ["store_type", "product_category", "store_id", "product_id", "region"]
            if col in X.columns
        ]

        logger.info(
            f"Successfully built dataset for horizon h={horizon}: {len(X)} rows, {len(feature_cols)} features."
        )

        return ForecastingDataset(
            df=valid_df,
            X=X,
            y=y,
            meta=meta,
            feature_names=feature_cols,
            categorical_features=categorical_cols,
            horizon=horizon,
            target_name=target_h_name,
        )
