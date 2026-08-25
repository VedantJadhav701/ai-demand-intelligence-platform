"""
Explainability Reporter module for generating global feature importance tables,
local explanation JSONs, and SHAP summary charts.
"""

from pathlib import Path
from typing import Dict, Any, Union, List
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import shap

from src.explainability.shap_explainer import ModelExplainer
from src.utils.logger import get_logger

logger = get_logger("explainability.report")


class ExplainabilityReporter:
    """Class for saving global feature importance tables and rendering SHAP charts."""

    def __init__(self, output_dir: Union[str, Path] = "data/outputs/explainability"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        sns.set_theme(style="whitegrid", palette="muted")

    def export_reports(self, explainer: ModelExplainer) -> Dict[str, Path]:
        """
        Exports feature importance CSVs and SHAP charts.

        Args:
            explainer: Fitted ModelExplainer instance.

        Returns:
            Dict[str, Path]: Dictionary mapping artifact names to saved file paths.
        """
        logger.info(f"Exporting explainability artifacts for model '{explainer.model_name}'...")

        # 1. Global Feature Importance CSV
        global_exp = explainer.get_global_explanation()
        imp_df = pd.DataFrame(
            global_exp.feature_ranking, columns=["Feature", "Mean |SHAP|"]
        )
        imp_csv = self.output_dir / "global_feature_importance.csv"
        imp_df.to_csv(imp_csv, index=False)

        # 2. Raw SHAP values CSV
        shap_df = pd.DataFrame(
            explainer.shap_values_matrix, columns=explainer.feature_names
        )
        shap_csv = self.output_dir / "shap_values.csv"
        shap_df.to_csv(shap_csv, index=False)

        # 3. Feature Importance Bar Plot
        fig_imp = self.output_dir / "feature_importance.png"
        top_15 = imp_df.head(15)

        plt.figure(figsize=(9, 5))
        sns.barplot(
            x="Mean |SHAP|",
            y="Feature",
            data=top_15,
            hue="Feature",
            legend=False,
            palette="Blues_r",
        )
        plt.title(
            f"Global Feature Importance ({explainer.model_name})",
            fontsize=13,
            fontweight="bold",
        )
        plt.xlabel("Mean |SHAP Value| (Impact on Demand Forecast)")
        plt.tight_layout()
        plt.savefig(fig_imp, dpi=150)
        plt.close()

        # 4. SHAP Summary Plot
        fig_summary = self.output_dir / "summary_plot.png"
        plt.figure(figsize=(9, 5))
        try:
            shap.summary_plot(
                explainer.shap_values_matrix,
                explainer.processed_X,
                show=False,
                max_display=12,
            )
            plt.title(
                f"SHAP Summary Plot ({explainer.model_name})",
                fontsize=13,
                fontweight="bold",
            )
            plt.tight_layout()
            plt.savefig(fig_summary, dpi=150)
        except Exception as e:
            logger.warning(f"Failed to generate SHAP summary plot: {e}")
        finally:
            plt.close()

        logger.info(f"Explainability artifacts saved to {self.output_dir.resolve()}")

        return {
            "global_importance_csv": imp_csv,
            "shap_values_csv": shap_csv,
            "feature_importance_png": fig_imp,
            "summary_plot_png": fig_summary,
        }
