"""
Business Segmentation module for store, product, and product category analysis.
"""

from typing import Dict, Any, List
import pandas as pd
from pydantic import BaseModel, Field

from src.utils.logger import get_logger

logger = get_logger("eda.segmentation")


class StoreSegment(BaseModel):
    store_id: str
    store_type: str
    region: str
    total_units_sold: float
    total_revenue: float
    avg_daily_units: float
    is_high_revenue: bool


class ProductSegment(BaseModel):
    product_id: str
    product_category: str
    total_units_sold: float
    total_revenue: float
    avg_price: float
    is_high_volume: bool


class CategorySegment(BaseModel):
    category_name: str
    total_units_sold: float
    total_revenue: float
    revenue_share_pct: float


class SegmentationReport(BaseModel):
    store_segments: List[StoreSegment] = Field(default_factory=list)
    product_segments: List[ProductSegment] = Field(default_factory=list)
    category_segments: List[CategorySegment] = Field(default_factory=list)
    top_revenue_store: str = ""
    top_volume_product: str = ""


class BusinessSegmenter:
    """Class for segmenting demand and revenue across stores, products, and categories."""

    def segment(self, df: pd.DataFrame) -> SegmentationReport:
        """
        Segments DataFrame by store, product, and category.

        Args:
            df: Input pandas DataFrame.

        Returns:
            SegmentationReport: Structured segmentation report.
        """
        logger.info("Starting business segmentation analysis...")

        # 1. Store Segmentation
        store_segments: List[StoreSegment] = []
        if "store_id" in df.columns:
            store_grp = df.groupby("store_id")
            store_rev_map = store_grp["revenue"].sum() if "revenue" in df.columns else store_grp["units_sold"].sum()
            avg_store_rev = store_rev_map.mean() if not store_rev_map.empty else 0.0

            for store_id, group in store_grp:
                stype = str(group["store_type"].iloc[0]) if "store_type" in group.columns else "Unknown"
                region = str(group["region"].iloc[0]) if "region" in group.columns else "Unknown"
                units = float(group["units_sold"].sum()) if "units_sold" in group.columns else 0.0
                rev = float(group["revenue"].sum()) if "revenue" in group.columns else 0.0
                unique_dates = max(1, group["date"].nunique())
                avg_daily = float(units / unique_dates)

                store_segments.append(
                    StoreSegment(
                        store_id=str(store_id),
                        store_type=stype,
                        region=region,
                        total_units_sold=round(units, 2),
                        total_revenue=round(rev, 2),
                        avg_daily_units=round(avg_daily, 2),
                        is_high_revenue=(rev >= avg_store_rev),
                    )
                )

        # 2. Product Segmentation
        product_segments: List[ProductSegment] = []
        if "product_id" in df.columns:
            prod_grp = df.groupby("product_id")
            prod_units_map = prod_grp["units_sold"].sum() if "units_sold" in df.columns else pd.Series(dtype=float)
            avg_prod_units = prod_units_map.mean() if not prod_units_map.empty else 0.0

            for prod_id, group in prod_grp:
                pcat = str(group["product_category"].iloc[0]) if "product_category" in group.columns else "Unknown"
                units = float(group["units_sold"].sum()) if "units_sold" in group.columns else 0.0
                rev = float(group["revenue"].sum()) if "revenue" in group.columns else 0.0
                avg_p = float(group["price"].mean()) if "price" in group.columns else 0.0

                product_segments.append(
                    ProductSegment(
                        product_id=str(prod_id),
                        product_category=pcat,
                        total_units_sold=round(units, 2),
                        total_revenue=round(rev, 2),
                        avg_price=round(avg_p, 2),
                        is_high_volume=(units >= avg_prod_units),
                    )
                )

        # 3. Category Segmentation
        category_segments: List[CategorySegment] = []
        cat_col = "product_category" if "product_category" in df.columns else None
        if cat_col:
            cat_grp = df.groupby(cat_col)
            total_rev_all = float(df["revenue"].sum()) if "revenue" in df.columns else float(df["units_sold"].sum())
            total_rev_all = max(1e-6, total_rev_all)

            for cat_name, group in cat_grp:
                units = float(group["units_sold"].sum()) if "units_sold" in group.columns else 0.0
                rev = float(group["revenue"].sum()) if "revenue" in group.columns else 0.0
                share = float((rev if "revenue" in group.columns else units) / total_rev_all * 100)

                category_segments.append(
                    CategorySegment(
                        category_name=str(cat_name),
                        total_units_sold=round(units, 2),
                        total_revenue=round(rev, 2),
                        revenue_share_pct=round(share, 2),
                    )
                )

        # Top revenue store & top volume product
        top_store = max(store_segments, key=lambda s: s.total_revenue).store_id if store_segments else ""
        top_prod = max(product_segments, key=lambda p: p.total_units_sold).product_id if product_segments else ""

        report = SegmentationReport(
            store_segments=store_segments,
            product_segments=product_segments,
            category_segments=category_segments,
            top_revenue_store=top_store,
            top_volume_product=top_prod,
        )

        logger.info("Business segmentation completed successfully.")
        return report
