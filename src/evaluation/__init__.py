"""
Evaluation package for time-series splits, metrics, walk-forward evaluation, leaderboard, and error analysis.
"""

from src.evaluation.splitter import TimeSeriesSplitter, SplitResult, FoldSplit
from src.evaluation.metrics import (
    calculate_mae,
    calculate_rmse,
    calculate_mape,
    calculate_smape,
    calculate_wape,
    calculate_all_metrics,
    MetricResult,
)
from src.evaluation.predictions import PredictionStore, PredictionRecord
from src.evaluation.walk_forward import (
    WalkForwardEvaluator,
    WalkForwardResult,
    FoldResult,
    FinalTestResult,
)
from src.evaluation.leaderboard import Leaderboard, LeaderboardRow
from src.evaluation.error_analysis import ErrorAnalyzer, ErrorAnalysisReport

__all__ = [
    "TimeSeriesSplitter",
    "SplitResult",
    "FoldSplit",
    "calculate_mae",
    "calculate_rmse",
    "calculate_mape",
    "calculate_smape",
    "calculate_wape",
    "calculate_all_metrics",
    "MetricResult",
    "PredictionStore",
    "PredictionRecord",
    "WalkForwardEvaluator",
    "WalkForwardResult",
    "FoldResult",
    "FinalTestResult",
    "Leaderboard",
    "LeaderboardRow",
    "ErrorAnalyzer",
    "ErrorAnalysisReport",
]
