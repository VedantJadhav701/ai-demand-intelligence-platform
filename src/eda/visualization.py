"""
Visualization module for generating reproducible EDA charts and saving figure artifacts.
"""

from pathlib import Path
from typing import List, Union
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

from src.utils.logger import get_logger

logger = get_logger("eda.visualization")


class EDAVisualizer:
    """Class for rendering and exporting reproducible EDA charts."""

    def __init__(self, output_dir: Union[str, Path] = "data/outputs/figures"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        sns.set_theme(style="whitegrid", palette="deep")

    def generate_all_plots(
        self, df: pd.DataFrame, target_col: str = "units_sold"
    ) -> List[str]:
        """
        Generates and exports all standard EDA figures.

        Args:
            df: Input pandas DataFrame.
            target_col: Target column name.

        Returns:
            List[str]: File paths of all saved figures.
        """
        logger.info(f"Generating EDA plots in directory: {self.output_dir.resolve()}")
        saved_files: List[str] = []

        plot_funcs = [
            self.plot_sales_trend,
            self.plot_day_of_week_seasonality,
            self.plot_store_product_segmentation,
            self.plot_correlation_heatmap,
            self.plot_promo_holiday_impact,
        ]

        for func in plot_funcs:
            try:
                path = func(df, target_col=target_col)
                if path:
                    saved_files.append(str(path))
            except Exception as e:
                logger.warning(f"Failed to generate plot {func.__name__}: {e}")

        logger.info(f"Successfully generated {len(saved_files)} EDA plots.")
        return saved_files

    def plot_sales_trend(
        self, df: pd.DataFrame, target_col: str = "units_sold"
    ) -> Union[str, Path]:
        """Plots daily demand trend with 7-day rolling average."""
        fig_path = self.output_dir / "sales_trend.png"
        temp_df = df.copy()
        temp_df["date"] = pd.to_datetime(temp_df["date"])
        daily = temp_df.groupby("date")[target_col].sum().sort_index()

        plt.figure(figsize=(10, 5))
        plt.plot(daily.index, daily.values, label="Daily Demand", alpha=0.5, color="#1f77b4")
        if len(daily) >= 7:
            rolling_7 = daily.rolling(7).mean()
            plt.plot(daily.index, rolling_7.values, label="7-Day Moving Avg", color="#d62728", linewidth=2)

        plt.title("Total Daily Demand Trend", fontsize=14, fontweight="bold")
        plt.xlabel("Date", fontsize=11)
        plt.ylabel("Units Sold", fontsize=11)
        plt.legend(loc="upper left")
        plt.tight_layout()
        plt.savefig(fig_path, dpi=150)
        plt.close()
        return fig_path

    def plot_day_of_week_seasonality(
        self, df: pd.DataFrame, target_col: str = "units_sold"
    ) -> Union[str, Path]:
        """Plots average demand by day of the week."""
        fig_path = self.output_dir / "day_of_week_seasonality.png"
        temp_df = df.copy()
        temp_df["date"] = pd.to_datetime(temp_df["date"])
        temp_df["day_name"] = temp_df["date"].dt.day_name()

        dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow_avg = temp_df.groupby("day_name")[target_col].mean().reindex(dow_order).dropna()

        plt.figure(figsize=(8, 4.5))
        sns.barplot(x=dow_avg.index, y=dow_avg.values, hue=dow_avg.index, legend=False, palette="Blues_d")
        plt.title("Average Demand by Day of Week", fontsize=14, fontweight="bold")
        plt.xlabel("Day of Week", fontsize=11)
        plt.ylabel("Mean Units Sold", fontsize=11)
        plt.xticks(rotation=15)
        plt.tight_layout()
        plt.savefig(fig_path, dpi=150)
        plt.close()
        return fig_path

    def plot_store_product_segmentation(
        self, df: pd.DataFrame, target_col: str = "units_sold"
    ) -> Union[str, Path]:
        """Plots side-by-side demand by store and product."""
        fig_path = self.output_dir / "store_product_segmentation.png"
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

        if "store_id" in df.columns:
            store_avg = df.groupby("store_id")[target_col].mean().sort_values(ascending=False)
            sns.barplot(x=store_avg.index, y=store_avg.values, ax=axes[0], hue=store_avg.index, legend=False, palette="viridis")
            axes[0].set_title("Average Demand by Store", fontweight="bold")
            axes[0].set_ylabel("Mean Units Sold")

        if "product_id" in df.columns:
            prod_avg = df.groupby("product_id")[target_col].mean().sort_values(ascending=False)
            sns.barplot(x=prod_avg.index, y=prod_avg.values, ax=axes[1], hue=prod_avg.index, legend=False, palette="magma")
            axes[1].set_title("Average Demand by Product", fontweight="bold")
            axes[1].set_ylabel("Mean Units Sold")

        plt.tight_layout()
        plt.savefig(fig_path, dpi=150)
        plt.close()
        return fig_path

    def plot_correlation_heatmap(
        self, df: pd.DataFrame, target_col: str = "units_sold"
    ) -> Union[str, Path]:
        """Plots heatmap of numerical feature correlations."""
        fig_path = self.output_dir / "correlation_heatmap.png"
        num_df = df.select_dtypes(include=[np.number])
        if num_df.empty or len(num_df.columns) < 2:
            return ""

        corr = num_df.corr().round(2)
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1, fmt=".2f", linewidths=0.5)
        plt.title("Feature Correlation Heatmap", fontsize=14, fontweight="bold")
        plt.tight_layout()
        plt.savefig(fig_path, dpi=150)
        plt.close()
        return fig_path

    def plot_promo_holiday_impact(
        self, df: pd.DataFrame, target_col: str = "units_sold"
    ) -> Union[str, Path]:
        """Plots demand comparison on promotion days and holidays."""
        fig_path = self.output_dir / "promo_holiday_impact.png"
        fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

        if "promotion" in df.columns:
            sns.boxplot(x="promotion", y=target_col, data=df, ax=axes[0], hue="promotion", legend=False, palette="Set2")
            axes[0].set_title("Demand Impact: Promotion", fontweight="bold")
            axes[0].set_xticks([0, 1])
            axes[0].set_xticklabels(["No Promo", "Active Promo"])

        if "holiday" in df.columns:
            sns.boxplot(x="holiday", y=target_col, data=df, ax=axes[1], hue="holiday", legend=False, palette="Set1")
            axes[1].set_title("Demand Impact: Holiday", fontweight="bold")
            axes[1].set_xticks([0, 1])
            axes[1].set_xticklabels(["Non-Holiday", "Holiday"])

        plt.tight_layout()
        plt.savefig(fig_path, dpi=150)
        plt.close()
        return fig_path
