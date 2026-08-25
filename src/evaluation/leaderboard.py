"""
Model Leaderboard generator for ranking and comparing baseline and ML model performances.
"""

from pathlib import Path
from typing import List, Union, Optional
import pandas as pd
from pydantic import BaseModel

from src.evaluation.walk_forward import WalkForwardResult, FinalTestResult
from src.utils.logger import get_logger

logger = get_logger("evaluation.leaderboard")


class LeaderboardRow(BaseModel):
    model: str
    horizon: int
    mae: float
    rmse: float
    mape: float
    smape: float
    wape: float
    train_time_sec: float
    inference_time_sec: float
    evaluation_type: str  # "CV" or "Test"


class Leaderboard:
    """Class for storing evaluation results and exporting model leaderboards."""

    def __init__(self):
        self._rows: List[LeaderboardRow] = []

    def add_cv_result(self, result: WalkForwardResult) -> None:
        """Adds a WalkForwardResult (CV mean performance)."""
        self._rows.append(
            LeaderboardRow(
                model=result.model_name,
                horizon=result.horizon,
                mae=result.mean_metrics.mae,
                rmse=result.mean_metrics.rmse,
                mape=result.mean_metrics.mape,
                smape=result.mean_metrics.smape,
                wape=result.mean_metrics.wape,
                train_time_sec=result.total_train_time_sec,
                inference_time_sec=result.total_inference_time_sec,
                evaluation_type="CV",
            )
        )

    def add_test_result(self, result: FinalTestResult) -> None:
        """Adds a FinalTestResult (untouched test set performance)."""
        self._rows.append(
            LeaderboardRow(
                model=result.model_name,
                horizon=result.horizon,
                mae=result.metrics.mae,
                rmse=result.metrics.rmse,
                mape=result.metrics.mape,
                smape=result.metrics.smape,
                wape=result.metrics.wape,
                train_time_sec=result.train_time_sec,
                inference_time_sec=result.inference_time_sec,
                evaluation_type="Test",
            )
        )

    def get_dataframe(
        self,
        sort_by: str = "wape",
        ascending: bool = True,
        evaluation_type: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Returns leaderboard formatted as pandas DataFrame.

        Args:
            sort_by: Metric column name to sort by (default 'wape').
            ascending: Sort order.
            evaluation_type: Filter by "CV", "Test", or None for all.

        Returns:
            pd.DataFrame: Formatted leaderboard table.
        """
        if not self._rows:
            return pd.DataFrame(
                columns=[
                    "Model",
                    "Horizon",
                    "MAE",
                    "RMSE",
                    "MAPE",
                    "sMAPE",
                    "WAPE",
                    "Train Time (s)",
                    "Inference Time (s)",
                    "Eval Type",
                ]
            )

        data = [
            {
                "Model": r.model,
                "Horizon": r.horizon,
                "MAE": r.mae,
                "RMSE": r.rmse,
                "MAPE": r.mape,
                "sMAPE": r.smape,
                "WAPE": r.wape,
                "Train Time (s)": r.train_time_sec,
                "Inference Time (s)": r.inference_time_sec,
                "Eval Type": r.evaluation_type,
            }
            for r in self._rows
        ]
        df = pd.DataFrame(data)

        if evaluation_type:
            df = df[df["Eval Type"].str.upper() == evaluation_type.upper()].copy()

        sort_col_map = {
            "wape": "WAPE",
            "mae": "MAE",
            "rmse": "RMSE",
            "mape": "MAPE",
            "smape": "sMAPE",
        }
        target_sort_col = sort_col_map.get(sort_by.lower(), "WAPE")

        if target_sort_col in df.columns:
            df = df.sort_values(
                by=["Horizon", target_sort_col], ascending=[True, ascending]
            ).reset_index(drop=True)

        return df

    def save_csv(self, output_path: Union[str, Path]) -> Path:
        """Saves leaderboard to CSV file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        df = self.get_dataframe(sort_by="wape")
        df.to_csv(path, index=False)
        logger.info(f"Saved leaderboard CSV to {path.resolve()}")
        return path
