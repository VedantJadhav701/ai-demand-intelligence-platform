"""
Data Profiling module for assessing data quality, cardinality, and numerical distributions.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from pydantic import BaseModel, Field

from src.utils.logger import get_logger

logger = get_logger("eda.profiling")


class ColumnDistribution(BaseModel):
    name: str
    count: int
    mean: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    q25: Optional[float] = None
    median: Optional[float] = None
    q75: Optional[float] = None
    max: Optional[float] = None
    skewness: Optional[float] = None


class DataProfilingReport(BaseModel):
    total_rows: int
    total_columns: int
    duplicate_rows: int
    missing_value_summary: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    cardinality: Dict[str, int] = Field(default_factory=dict)
    distributions: Dict[str, ColumnDistribution] = Field(default_factory=dict)


class DataProfiler:
    """Class for computing dataset data quality profiles and distribution summaries."""

    def profile(self, df: pd.DataFrame) -> DataProfilingReport:
        """
        Profiles input DataFrame for data quality, duplicate rows, cardinality, and distributions.

        Args:
            df: Input pandas DataFrame.

        Returns:
            DataProfilingReport: Pydantic model containing structured profiling metrics.
        """
        logger.info(
            f"Starting data profiling on DataFrame with shape {df.shape}"
        )
        total_rows = len(df)
        total_columns = len(df.columns)
        duplicate_rows = int(df.duplicated().sum())

        missing_summary: Dict[str, Dict[str, Any]] = {}
        cardinality: Dict[str, int] = {}
        distributions: Dict[str, ColumnDistribution] = {}

        for col in df.columns:
            series = df[col]
            missing_count = int(series.isna().sum())
            missing_pct = (
                float(missing_count / total_rows) if total_rows > 0 else 0.0
            )

            missing_summary[col] = {
                "missing_count": missing_count,
                "missing_pct": round(missing_pct, 4),
            }

            cardinality[col] = int(series.nunique(dropna=True))

            if pd.api.types.is_numeric_dtype(series) and not series.empty:
                valid_s = series.dropna()
                if not valid_s.empty:
                    distributions[col] = ColumnDistribution(
                        name=col,
                        count=len(valid_s),
                        mean=round(float(valid_s.mean()), 4),
                        std=round(float(valid_s.std()), 4)
                        if len(valid_s) > 1
                        else 0.0,
                        min=round(float(valid_s.min()), 4),
                        q25=round(float(valid_s.quantile(0.25)), 4),
                        median=round(float(valid_s.median()), 4),
                        q75=round(float(valid_s.quantile(0.75)), 4),
                        max=round(float(valid_s.max()), 4),
                        skewness=round(float(valid_s.skew()), 4)
                        if len(valid_s) > 2
                        else 0.0,
                    )

        report = DataProfilingReport(
            total_rows=total_rows,
            total_columns=total_columns,
            duplicate_rows=duplicate_rows,
            missing_value_summary=missing_summary,
            cardinality=cardinality,
            distributions=distributions,
        )

        logger.info("Data profiling completed successfully.")
        return report
