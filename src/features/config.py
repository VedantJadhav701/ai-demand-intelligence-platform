"""
Feature Engineering Configuration schema using Pydantic.
"""

from typing import List
from pydantic import BaseModel, Field


class FeatureConfig(BaseModel):
    date_col: str = "date"
    target_col: str = "units_sold"
    group_cols: List[str] = Field(default_factory=lambda: ["store_id", "product_id"])

    # Temporal feature flags
    include_temporal: bool = True

    # Lag features
    lags: List[int] = Field(default_factory=lambda: [1, 7, 14, 28])

    # Rolling window sizes and statistics
    rolling_windows: List[int] = Field(default_factory=lambda: [7, 14, 28])
    rolling_stats: List[str] = Field(
        default_factory=lambda: ["mean", "std", "min", "max"]
    )

    # Optional price and discount changes
    include_diff_features: bool = True

    # Categorical columns
    categorical_cols: List[str] = Field(
        default_factory=lambda: [
            "store_type",
            "product_category",
            "store_id",
            "product_id",
        ]
    )
