"""
Optimization Results container for exporting trial artifacts and producing baseline vs optimized comparison tables.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Union, Optional
import pandas as pd
from pydantic import BaseModel, Field

from src.optimization.search import OptimizationSearchResult, OptimizationTrialRecord
from src.utils.logger import get_logger

logger = get_logger("optimization.results")


class ComparisonRow(BaseModel):
    model: str
    horizon: int
    phase3_wape: float
    optimized_wape: float
    improvement_pct: float
    phase3_mae: float
    optimized_mae: float
    phase3_smape: float
    optimized_smape: float


class OptimizationResultsContainer:
    """Class for aggregating Optuna trial results, saving artifacts, and creating comparison tables."""

    def __init__(self, output_dir: Union[str, Path] = "data/outputs/optimization"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.search_results: List[OptimizationSearchResult] = []

    def add_result(self, result: OptimizationSearchResult) -> None:
        """Adds an OptimizationSearchResult instance."""
        self.search_results.append(result)

    def export_artifacts(self) -> Dict[str, Path]:
        """
        Exports optimization artifacts:
        - optimization_summary.csv
        - best_parameters.json
        - trial_results.csv

        Returns:
            Dict[str, Path]: Dictionary mapping artifact key to saved file Path.
        """
        summary_rows: List[Dict[str, Any]] = []
        trial_rows: List[Dict[str, Any]] = []
        best_params_json: Dict[str, Dict[str, Any]] = {}

        for sr in self.search_results:
            key = f"{sr.model}_h{sr.horizon}"
            best_params_json[key] = {
                "model": sr.model,
                "horizon": sr.horizon,
                "best_wape": sr.best_wape,
                "best_params": sr.best_params,
                "total_trials": sr.total_trials,
                "duration_sec": sr.duration_sec,
            }

            summary_rows.append(
                {
                    "Model": sr.model,
                    "Horizon": sr.horizon,
                    "Best CV WAPE (%)": sr.best_wape,
                    "Total Trials": sr.total_trials,
                    "Duration (s)": sr.duration_sec,
                }
            )

            for tr in sr.trials:
                row_dict = {
                    "Model": tr.model,
                    "Horizon": tr.horizon,
                    "Trial": tr.trial_number,
                    "WAPE (%)": tr.wape,
                    "MAE": tr.mae,
                    "RMSE": tr.rmse,
                    "sMAPE (%)": tr.smape,
                    "Train Time (s)": tr.train_time_sec,
                    "Inference Time (s)": tr.inference_time_sec,
                }
                # Flatten hyperparameter dict into columns
                for k, v in tr.params.items():
                    row_dict[f"param_{k}"] = v
                trial_rows.append(row_dict)

        # 1. Summary CSV
        summary_df = pd.DataFrame(summary_rows)
        summary_csv = self.output_dir / "optimization_summary.csv"
        summary_df.to_csv(summary_csv, index=False)

        # 2. Trial Results CSV
        trials_df = pd.DataFrame(trial_rows)
        trials_csv = self.output_dir / "trial_results.csv"
        trials_df.to_csv(trials_csv, index=False)

        # 3. Best Parameters JSON
        best_json_path = self.output_dir / "best_parameters.json"
        with open(best_json_path, "w", encoding="utf-8") as f:
            json.dump(best_params_json, f, indent=2)

        logger.info(f"Optimization artifacts saved to {self.output_dir.resolve()}")
        return {
            "summary_csv": summary_csv,
            "trials_csv": trials_csv,
            "best_params_json": best_json_path,
        }

    def build_comparison_table(
        self, phase3_leaderboard_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Builds baseline (Phase 3) vs Optimized comparison table.

        Args:
            phase3_leaderboard_df: DataFrame from Phase 3 leaderboard.

        Returns:
            pd.DataFrame: Formatted comparison table with Improvement % columns.
        """
        rows: List[Dict[str, Any]] = []

        for sr in self.search_results:
            # Find matching Phase 3 baseline row
            match = phase3_leaderboard_df[
                (phase3_leaderboard_df["Model"].str.lower() == sr.model.lower())
                & (phase3_leaderboard_df["Horizon"] == sr.horizon)
                & (phase3_leaderboard_df["Eval Type"].str.upper() == "CV")
            ]

            if not match.empty:
                b_wape = float(match.iloc[0]["WAPE"])
                b_mae = float(match.iloc[0]["MAE"])
                b_smape = float(match.iloc[0]["sMAPE"])
            else:
                b_wape = sr.best_wape
                b_mae = 0.0
                b_smape = 0.0

            opt_wape = sr.best_wape
            # Get best trial's MAE and sMAPE
            best_trial_rec = min(sr.trials, key=lambda t: t.wape) if sr.trials else None
            opt_mae = best_trial_rec.mae if best_trial_rec else 0.0
            opt_smape = best_trial_rec.smape if best_trial_rec else 0.0

            improvement = (
                ((b_wape - opt_wape) / b_wape * 100.0) if b_wape > 0 else 0.0
            )

            rows.append(
                {
                    "Model": sr.model,
                    "Horizon": sr.horizon,
                    "Phase 3 WAPE (%)": round(b_wape, 2),
                    "Optimized WAPE (%)": round(opt_wape, 2),
                    "Improvement (%)": round(improvement, 2),
                    "Phase 3 MAE": round(b_mae, 2),
                    "Optimized MAE": round(opt_mae, 2),
                    "Phase 3 sMAPE (%)": round(b_smape, 2),
                    "Optimized sMAPE (%)": round(opt_smape, 2),
                }
            )

        comp_df = pd.DataFrame(rows)
        return comp_df
