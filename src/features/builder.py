"""
Feature Engineering builder module for generating temporal, lag, and rolling features
with zero target leakage.
"""

from typing import Optional, List
import pandas as pd
import numpy as np

from src.utils.logger import get_logger
from src.features.config import FeatureConfig

logger = get_logger("features.builder")


class FeatureEngineer:
    """
    Constructs time-series features (temporal, lag, rolling statistics, price changes)
    while strictly preserving chronological order and preventing target leakage.
    """

    def __init__(self, config: Optional[FeatureConfig] = None):
        self.config = config or FeatureConfig()

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies feature engineering pipeline to input DataFrame.

        Args:
            df: Input raw or validated DataFrame.

        Returns:
            pd.DataFrame: Transformed DataFrame containing engineered feature columns.

        Raises:
            ValueError: If required key columns are missing.
        """
        logger.info("Starting Feature Engineering pipeline...")

        # Validate core inputs
        required = [self.config.date_col, self.config.target_col] + [
            c for c in self.config.group_cols if c in df.columns
        ]
        for col in [self.config.date_col, self.config.target_col]:
            if col not in df.columns:
                raise ValueError(f"Required feature column '{col}' missing from DataFrame.")

        # Copy and sort chronologically per series
        out_df = df.copy()
        out_df[self.config.date_col] = pd.to_datetime(out_df[self.config.date_col])

        group_cols = [c for c in self.config.group_cols if c in out_df.columns]
        if group_cols:
            out_df = out_df.sort_values(group_cols + [self.config.date_col]).reset_index(
                drop=True
            )
        else:
            out_df = out_df.sort_values(self.config.date_col).reset_index(drop=True)

        # 1. Temporal Features
        if self.config.include_temporal:
            out_df = self._add_temporal_features(out_df)

        # 2. Lag Features (Target Leakage Prevention: shift by lag >= 1)
        out_df = self._add_lag_features(out_df, group_cols)

        # 3. Rolling Statistics Features (Target Leakage Prevention: shift(1) before rolling)
        out_df = self._add_rolling_features(out_df, group_cols)

        # 4. Optional Price and Discount Changes
        if self.config.include_diff_features:
            out_df = self._add_diff_features(out_df, group_cols)

        logger.info(
            f"Feature Engineering complete. Output shape: {out_df.shape} (added {len(out_df.columns) - len(df.columns)} new features)."
        )
        return out_df

    def _add_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extracts standard temporal calendar features from date column."""
        dates = df[self.config.date_col]
        df["day_of_week"] = dates.dt.dayofweek
        df["day_of_month"] = dates.dt.day
        df["week_of_year"] = dates.dt.isocalendar().week.astype(int)
        df["month"] = dates.dt.month
        df["quarter"] = dates.dt.quarter
        df["year"] = dates.dt.year
        df["is_weekend"] = (dates.dt.dayofweek >= 5).astype(int)
        df["is_month_start"] = dates.dt.is_month_start.astype(int)
        df["is_month_end"] = dates.dt.is_month_end.astype(int)
        return df

    def _add_lag_features(self, df: pd.DataFrame, group_cols: List[str]) -> pd.DataFrame:
        """Adds lag features using shift(lag) per series group."""
        target = self.config.target_col
        for lag in self.config.lags:
            if lag < 1:
                raise ValueError(f"Lag value must be >= 1 to prevent leakage. Got {lag}")
            col_name = f"lag_{lag}"

            if group_cols:
                df[col_name] = df.groupby(group_cols)[target].shift(lag)
            else:
                df[col_name] = df[target].shift(lag)
        return df

    def _add_rolling_features(self, df: pd.DataFrame, group_cols: List[str]) -> pd.DataFrame:
        """
        Adds rolling statistic features.
        Target leakage prevention: shift(1) is applied prior to rolling window computation
        so that value at timestamp t only uses history from t-1 and earlier.
        """
        target = self.config.target_col
        for window in self.config.rolling_windows:
            for stat in self.config.rolling_stats:
                col_name = f"rolling_{stat}_{window}"
                if group_cols:
                    # Shift 1 first to prevent using current timestamp target in rolling calc!
                    shifted = df.groupby(group_cols)[target].shift(1)
                    grouped_shifted = shifted.groupby([df[c] for c in group_cols])
                    if stat == "mean":
                        df[col_name] = grouped_shifted.transform(
                            lambda s: s.rolling(window, min_periods=1).mean()
                        )
                    elif stat == "std":
                        df[col_name] = grouped_shifted.transform(
                            lambda s: s.rolling(window, min_periods=1).std()
                        ).fillna(0.0)
                    elif stat == "min":
                        df[col_name] = grouped_shifted.transform(
                            lambda s: s.rolling(window, min_periods=1).min()
                        )
                    elif stat == "max":
                        df[col_name] = grouped_shifted.transform(
                            lambda s: s.rolling(window, min_periods=1).max()
                        )
                else:
                    shifted = df[target].shift(1)
                    if stat == "mean":
                        df[col_name] = shifted.rolling(window, min_periods=1).mean()
                    elif stat == "std":
                        df[col_name] = shifted.rolling(window, min_periods=1).std().fillna(0.0)
                    elif stat == "min":
                        df[col_name] = shifted.rolling(window, min_periods=1).min()
                    elif stat == "max":
                        df[col_name] = shifted.rolling(window, min_periods=1).max()
        return df

    def _add_diff_features(self, df: pd.DataFrame, group_cols: List[str]) -> pd.DataFrame:
        """Adds price change and discount change features if present."""
        if "price" in df.columns:
            if group_cols:
                df["price_change"] = df.groupby(group_cols)["price"].diff().fillna(0.0)
            else:
                df["price_change"] = df["price"].diff().fillna(0.0)

        if "discount" in df.columns:
            if group_cols:
                df["discount_change"] = df.groupby(group_cols)["discount"].diff().fillna(0.0)
            else:
                df["discount_change"] = df["discount"].diff().fillna(0.0)
        return df
