"""
Correlation Analysis module for analyzing relationships between price, discount, promotion, holiday, and demand.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field

from src.utils.logger import get_logger

logger = get_logger("eda.correlation")


class BusinessImpact(BaseModel):
    promo_sales_uplift_pct: Optional[float] = None
    holiday_sales_uplift_pct: Optional[float] = None
    price_demand_correlation: Optional[float] = None
    discount_demand_correlation: Optional[float] = None


class CorrelationReport(BaseModel):
    correlation_matrix: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    business_impact: BusinessImpact = Field(default_factory=BusinessImpact)


class CorrelationAnalyzer:
    """Class for computing numerical feature correlations and evaluating business impact factors."""

    def analyze(
        self, df: pd.DataFrame, target_col: str = "units_sold"
    ) -> CorrelationReport:
        """
        Calculates correlation matrix and promo/holiday demand uplift metrics.

        Args:
            df: Input pandas DataFrame.
            target_col: Name of target column (default 'units_sold').

        Returns:
            CorrelationReport: Structured correlation analysis report.
        """
        logger.info("Starting correlation analysis...")

        # 1. Compute numerical correlation matrix
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        corr_matrix_dict: Dict[str, Dict[str, float]] = {}

        if len(num_cols) > 1:
            corr_df = df[num_cols].corr(method="pearson").fillna(0.0)
            for c1 in corr_df.columns:
                corr_matrix_dict[c1] = {}
                for c2 in corr_df.columns:
                    corr_matrix_dict[c1][c2] = round(float(corr_df.loc[c1, c2]), 4)

        # 2. Business Impact Analysis
        promo_uplift = None
        holiday_uplift = None
        price_corr = None
        disc_corr = None

        if target_col in df.columns:
            # Promo Uplift
            if "promotion" in df.columns:
                promo_df = df.groupby("promotion")[target_col].mean()
                if 0 in promo_df and 1 in promo_df and promo_df[0] > 0:
                    promo_uplift = round(
                        float((promo_df[1] - promo_df[0]) / promo_df[0] * 100), 2
                    )

            # Holiday Uplift
            if "holiday" in df.columns:
                hol_df = df.groupby("holiday")[target_col].mean()
                if 0 in hol_df and 1 in hol_df and hol_df[0] > 0:
                    holiday_uplift = round(
                        float((hol_df[1] - hol_df[0]) / hol_df[0] * 100), 2
                    )

            # Price Demand Correlation
            if "price" in df.columns and corr_matrix_dict:
                price_corr = corr_matrix_dict.get(target_col, {}).get("price")

            # Discount Demand Correlation
            if "discount" in df.columns and corr_matrix_dict:
                disc_corr = corr_matrix_dict.get(target_col, {}).get("discount")

        impact = BusinessImpact(
            promo_sales_uplift_pct=promo_uplift,
            holiday_sales_uplift_pct=holiday_uplift,
            price_demand_correlation=price_corr,
            discount_demand_correlation=disc_corr,
        )

        report = CorrelationReport(
            correlation_matrix=corr_matrix_dict, business_impact=impact
        )

        logger.info("Correlation analysis completed successfully.")
        return report
