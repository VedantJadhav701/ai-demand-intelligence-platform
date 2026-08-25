"""
Unit tests for EDA modules (profiling, temporal analysis, segmentation, correlation, visualization, and pipeline).
"""

from pathlib import Path
import pytest
import pandas as pd

from src.eda.profiling import DataProfiler
from src.eda.temporal import TemporalAnalyzer
from src.eda.segmentation import BusinessSegmenter
from src.eda.correlation import CorrelationAnalyzer
from src.eda.visualization import EDAVisualizer
from src.eda.pipeline import EDAPipeline, EDAReport
from src.data.ingestion import DataIngestor
from src.utils.config import load_config


@pytest.fixture
def sample_sales_df() -> pd.DataFrame:
    """Fixture providing loaded sample sales dataset."""
    config = load_config()
    ingestor = DataIngestor(config.data)
    return ingestor.load_data(config.data.raw_data_path)


def test_data_profiler(sample_sales_df: pd.DataFrame):
    """Test data profiler output metrics."""
    profiler = DataProfiler()
    report = profiler.profile(sample_sales_df)

    assert report.total_rows == len(sample_sales_df)
    assert report.total_columns == len(sample_sales_df.columns)
    assert "units_sold" in report.distributions
    assert report.distributions["units_sold"].mean > 0


def test_temporal_analyzer(sample_sales_df: pd.DataFrame):
    """Test temporal analyzer for trend, seasonality, and volatility."""
    analyzer = TemporalAnalyzer()
    report = analyzer.analyze(sample_sales_df)

    assert report.trend.daily_avg_demand > 0
    assert "Monday" in report.seasonality.day_of_week_avg
    assert report.volatility.volatility_category in ["Low", "Moderate", "High"]


def test_business_segmenter(sample_sales_df: pd.DataFrame):
    """Test store, product, and category segmentation."""
    segmenter = BusinessSegmenter()
    report = segmenter.segment(sample_sales_df)

    assert len(report.store_segments) > 0
    assert len(report.product_segments) > 0
    assert report.top_revenue_store != ""
    assert report.top_volume_product != ""


def test_correlation_analyzer(sample_sales_df: pd.DataFrame):
    """Test feature correlation and business impact calculations."""
    analyzer = CorrelationAnalyzer()
    report = analyzer.analyze(sample_sales_df)

    assert "units_sold" in report.correlation_matrix
    assert report.business_impact.promo_sales_uplift_pct is not None or report.business_impact.price_demand_correlation is not None


def test_eda_visualizer(sample_sales_df: pd.DataFrame, tmp_path: Path):
    """Test chart generation and PNG export."""
    visualizer = EDAVisualizer(output_dir=tmp_path)
    paths = visualizer.generate_all_plots(sample_sales_df)

    assert len(paths) >= 4
    for p in paths:
        assert Path(p).exists()
        assert Path(p).stat().st_size > 0


def test_eda_pipeline(sample_sales_df: pd.DataFrame, tmp_path: Path):
    """Test complete EDA pipeline execution."""
    pipeline = EDAPipeline(output_dir=tmp_path)
    report = pipeline.run(sample_sales_df)

    assert isinstance(report, EDAReport)
    assert report.profiling.total_rows == len(sample_sales_df)
    assert len(report.saved_figure_paths) >= 4
