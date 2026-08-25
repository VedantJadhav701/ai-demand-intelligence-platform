"""
Temporal Analysis module for analyzing time-series trend, seasonality, volatility, and decomposition.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field
from statsmodels.tsa.seasonal import seasonal_decompose

from src.utils.logger import get_logger

logger = get_logger("eda.temporal")


class TrendSummary(BaseModel):
    start_date: str
    end_date: str
    total_days: int
    daily_avg_demand: float
    overall_growth_rate_pct: float
    is_upward_trend: bool


class SeasonalitySummary(BaseModel):
    day_of_week_avg: Dict[str, float] = Field(default_factory=dict)
    peak_day_of_week: str = ""
    trough_day_of_week: str = ""
    monthly_avg: Dict[str, float] = Field(default_factory=dict)


class VolatilitySummary(BaseModel):
    mean_demand: float
    std_demand: float
    coefficient_of_variation: float
    min_demand: float
    max_demand: float
    volatility_category: str  # Low, Moderate, High


class TemporalAnalysisReport(BaseModel):
    trend: TrendSummary
    seasonality: SeasonalitySummary
    volatility: VolatilitySummary
    decomposition_available: bool = False
    seasonal_period_used: Optional[int] = None


class TemporalAnalyzer:
    """Class for analyzing time-series trends, weekly/monthly patterns, demand volatility, and decomposition."""

    def analyze(
        self,
        df: pd.DataFrame,
        date_col: str = "date",
        target_col: str = "units_sold",
    ) -> TemporalAnalysisReport:
        """
        Runs complete temporal analysis on time-series sales DataFrame.

        Args:
            df: Input DataFrame.
            date_col: Name of date column.
            target_col: Target column name (default 'units_sold').

        Returns:
            TemporalAnalysisReport: Structured temporal metrics report.
        """
        logger.info("Starting temporal time-series analysis...")

        temp_df = df.copy()
        temp_df[date_col] = pd.to_datetime(temp_df[date_col])
        temp_df = temp_df.sort_values(date_col)

        # Aggregate daily target demand
        daily_series = (
            temp_df.groupby(date_col)[target_col].sum().sort_index()
        )

        # 1. Trend Analysis
        start_date = str(daily_series.index.min().date())
        end_date = str(daily_series.index.max().date())
        total_days = len(daily_series)
        daily_avg = float(daily_series.mean())

        # Simple linear slope trend approximation
        x = np.arange(total_days)
        y = daily_series.values
        if total_days > 1 and np.var(x) > 0:
            slope, _ = np.polyfit(x, y, 1)
            first_val = max(1.0, y[0])
            growth_rate = float((slope * total_days) / first_val * 100)
            is_upward = slope > 0
        else:
            growth_rate = 0.0
            is_upward = False

        trend_summary = TrendSummary(
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            daily_avg_demand=round(daily_avg, 2),
            overall_growth_rate_pct=round(growth_rate, 2),
            is_upward_trend=is_upward,
        )

        # 2. Seasonality Analysis
        temp_df["day_name"] = temp_df[date_col].dt.day_name()
        temp_df["month_name"] = temp_df[date_col].dt.strftime("%Y-%m")

        dow_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        dow_avg_s = temp_df.groupby("day_name")[target_col].mean()
        dow_avg = {
            day: round(float(dow_avg_s[day]), 2)
            for day in dow_order
            if day in dow_avg_s
        }

        peak_dow = max(dow_avg, key=dow_avg.get) if dow_avg else ""
        trough_dow = min(dow_avg, key=dow_avg.get) if dow_avg else ""

        month_avg_s = temp_df.groupby("month_name")[target_col].mean()
        month_avg = {
            m: round(float(v), 2) for m, v in month_avg_s.items()
        }

        seasonality_summary = SeasonalitySummary(
            day_of_week_avg=dow_avg,
            peak_day_of_week=peak_dow,
            trough_day_of_week=trough_dow,
            monthly_avg=month_avg,
        )

        # 3. Volatility Analysis
        std_val = float(daily_series.std()) if len(daily_series) > 1 else 0.0
        cv = float(std_val / daily_avg) if daily_avg > 0 else 0.0

        if cv < 0.2:
            vol_cat = "Low"
        elif cv < 0.5:
            vol_cat = "Moderate"
        else:
            vol_cat = "High"

        volatility_summary = VolatilitySummary(
            mean_demand=round(daily_avg, 2),
            std_demand=round(std_val, 2),
            coefficient_of_variation=round(cv, 4),
            min_demand=float(daily_series.min()),
            max_demand=float(daily_series.max()),
            volatility_category=vol_cat,
        )

        # 4. Decomposition check (requires >= 2 full periods, e.g., 14 days for period=7)
        decomp_avail = False
        period_used = None
        if len(daily_series) >= 14:
            try:
                # Test decomposition with weekly period (7)
                res = seasonal_decompose(
                    daily_series, model="additive", period=7
                )
                decomp_avail = True
                period_used = 7
            except Exception as e:
                logger.warning(f"Seasonal decomposition skipped: {e}")

        report = TemporalAnalysisReport(
            trend=trend_summary,
            seasonality=seasonality_summary,
            volatility=volatility_summary,
            decomposition_available=decomp_avail,
            seasonal_period_used=period_used,
        )

        logger.info("Temporal analysis completed successfully.")
        return report
