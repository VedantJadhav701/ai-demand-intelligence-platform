"""
Unified EDA Pipeline orchestrating profiling, temporal analysis, segmentation, correlation, and figure exports.
"""

from pathlib import Path
from typing import List, Union
import pandas as pd
from pydantic import BaseModel, Field

from src.utils.logger import get_logger
from src.eda.profiling import DataProfiler, DataProfilingReport
from src.eda.temporal import TemporalAnalyzer, TemporalAnalysisReport
from src.eda.segmentation import BusinessSegmenter, SegmentationReport
from src.eda.correlation import CorrelationAnalyzer, CorrelationReport
from src.eda.visualization import EDAVisualizer

logger = get_logger("eda.pipeline")


class EDAReport(BaseModel):
    profiling: DataProfilingReport
    temporal: TemporalAnalysisReport
    segmentation: SegmentationReport
    correlation: CorrelationReport
    saved_figure_paths: List[str] = Field(default_factory=list)


class EDAPipeline:
    """Orchestrates all exploratory data analysis routines and produces a unified report."""

    def __init__(
        self,
        output_dir: Union[str, Path] = "data/outputs/figures",
    ):
        self.profiler = DataProfiler()
        self.temporal_analyzer = TemporalAnalyzer()
        self.segmenter = BusinessSegmenter()
        self.correlation_analyzer = CorrelationAnalyzer()
        self.visualizer = EDAVisualizer(output_dir=output_dir)

    def run(
        self,
        df: pd.DataFrame,
        date_col: str = "date",
        target_col: str = "units_sold",
    ) -> EDAReport:
        """
        Executes complete EDA pipeline.

        Args:
            df: Input pandas DataFrame.
            date_col: Name of date column.
            target_col: Name of target demand column.

        Returns:
            EDAReport: Comprehensive EDA report containing structured analysis and visualization paths.
        """
        logger.info("Executing EDA Pipeline...")

        # 1. Profiling
        profiling_report = self.profiler.profile(df)

        # 2. Temporal Analysis
        temporal_report = self.temporal_analyzer.analyze(
            df, date_col=date_col, target_col=target_col
        )

        # 3. Segmentation Analysis
        segmentation_report = self.segmenter.segment(df)

        # 4. Correlation Analysis
        correlation_report = self.correlation_analyzer.analyze(
            df, target_col=target_col
        )

        # 5. Visualization Generation
        fig_paths = self.visualizer.generate_all_plots(
            df, target_col=target_col
        )

        eda_report = EDAReport(
            profiling=profiling_report,
            temporal=temporal_report,
            segmentation=segmentation_report,
            correlation=correlation_report,
            saved_figure_paths=fig_paths,
        )

        logger.info(
            f"EDA Pipeline executed successfully. Generated {len(fig_paths)} charts."
        )
        return eda_report
