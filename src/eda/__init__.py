"""
Exploratory Data Analysis (EDA) package for profiling, temporal analysis,
business segmentation, correlation analysis, and visualization.
"""

from src.eda.profiling import DataProfiler, DataProfilingReport
from src.eda.temporal import TemporalAnalyzer, TemporalAnalysisReport
from src.eda.segmentation import BusinessSegmenter, SegmentationReport
from src.eda.correlation import CorrelationAnalyzer, CorrelationReport
from src.eda.visualization import EDAVisualizer
from src.eda.pipeline import EDAPipeline, EDAReport

__all__ = [
    "DataProfiler",
    "DataProfilingReport",
    "TemporalAnalyzer",
    "TemporalAnalysisReport",
    "BusinessSegmenter",
    "SegmentationReport",
    "CorrelationAnalyzer",
    "CorrelationReport",
    "EDAVisualizer",
    "EDAPipeline",
    "EDAReport",
]
