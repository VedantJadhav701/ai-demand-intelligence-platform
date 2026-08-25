"""
Error Analysis module for evaluating store, product, category, and temporal forecast errors.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field

from src.evaluation.metrics import calculate_wape, calculate_mae, calculate_rmse
from src.utils.logger import get_logger

logger = get_logger("evaluation.error_analysis")


class SegmentErrorSummary(BaseModel):
    segment_name: str
    segment_value: str
    horizon: int
    total_count: int
    total_actual: float
    total_predicted: float
    mae: float
    rmse: float
    wape: float
    bias: float  # (pred - actual)


class ErrorAnalysisReport(BaseModel):
    store_errors: List[SegmentErrorSummary] = Field(default_factory=list)
    product_errors: List[SegmentErrorSummary] = Field(default_factory=list)
    category_errors: List[SegmentErrorSummary] = Field(default_factory=list)
    worst_performing_store: str = ""
    worst_performing_product: str = ""


class ErrorAnalyzer:
    """Class for analyzing model error distributions across stores, products, and categories."""

    def analyze(self, predictions_df: pd.DataFrame) -> ErrorAnalysisReport:
        """
        Analyzes prediction errors aggregated by store_id, product_id, category, and horizon.

        Args:
            predictions_df: DataFrame containing 'store_id', 'product_id', 'horizon', 'actual', 'prediction'.

        Returns:
            ErrorAnalysisReport: Structured report holding error breakdowns.
        """
        if predictions_df.empty:
            logger.warning("Empty predictions DataFrame passed to ErrorAnalyzer.")
            return ErrorAnalysisReport()

        logger.info("Executing Error Analysis across store and product segments...")
        df = predictions_df.copy()
        df["abs_error"] = (df["prediction"] - df["actual"]).abs()
        df["bias"] = df["prediction"] - df["actual"]

        store_errors: List[SegmentErrorSummary] = []
        product_errors: List[SegmentErrorSummary] = []
        category_errors: List[SegmentErrorSummary] = []

        # 1. Store Error Analysis
        if "store_id" in df.columns:
            for (store_id, horizon), grp in df.groupby(["store_id", "horizon"]):
                actuals = grp["actual"].values
                preds = grp["prediction"].values
                store_errors.append(
                    SegmentErrorSummary(
                        segment_name="store_id",
                        segment_value=str(store_id),
                        horizon=int(horizon),
                        total_count=len(grp),
                        total_actual=round(float(np.sum(actuals)), 2),
                        total_predicted=round(float(np.sum(preds)), 2),
                        mae=round(calculate_mae(actuals, preds), 4),
                        rmse=round(calculate_rmse(actuals, preds), 4),
                        wape=round(calculate_wape(actuals, preds), 4),
                        bias=round(float(np.mean(grp["bias"])), 4),
                    )
                )

        # 2. Product Error Analysis
        if "product_id" in df.columns:
            for (prod_id, horizon), grp in df.groupby(["product_id", "horizon"]):
                actuals = grp["actual"].values
                preds = grp["prediction"].values
                product_errors.append(
                    SegmentErrorSummary(
                        segment_name="product_id",
                        segment_value=str(prod_id),
                        horizon=int(horizon),
                        total_count=len(grp),
                        total_actual=round(float(np.sum(actuals)), 2),
                        total_predicted=round(float(np.sum(preds)), 2),
                        mae=round(calculate_mae(actuals, preds), 4),
                        rmse=round(calculate_rmse(actuals, preds), 4),
                        wape=round(calculate_wape(actuals, preds), 4),
                        bias=round(float(np.mean(grp["bias"])), 4),
                    )
                )

        # 3. Category Error Analysis
        if "product_category" in df.columns:
            for (cat, horizon), grp in df.groupby(["product_category", "horizon"]):
                actuals = grp["actual"].values
                preds = grp["prediction"].values
                category_errors.append(
                    SegmentErrorSummary(
                        segment_name="product_category",
                        segment_value=str(cat),
                        horizon=int(horizon),
                        total_count=len(grp),
                        total_actual=round(float(np.sum(actuals)), 2),
                        total_predicted=round(float(np.sum(preds)), 2),
                        mae=round(calculate_mae(actuals, preds), 4),
                        rmse=round(calculate_rmse(actuals, preds), 4),
                        wape=round(calculate_wape(actuals, preds), 4),
                        bias=round(float(np.mean(grp["bias"])), 4),
                    )
                )

        worst_store = max(store_errors, key=lambda s: s.wape).segment_value if store_errors else ""
        worst_prod = max(product_errors, key=lambda p: p.wape).segment_value if product_errors else ""

        report = ErrorAnalysisReport(
            store_errors=store_errors,
            product_errors=product_errors,
            category_errors=category_errors,
            worst_performing_store=worst_store,
            worst_performing_product=worst_prod,
        )

        logger.info("Error analysis completed successfully.")
        return report
