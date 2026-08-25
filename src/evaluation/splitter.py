"""
Chronological Time-Series Splitter for Walk-Forward CV and Final Test Set Reservation.
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import pandas as pd

from src.utils.logger import get_logger

logger = get_logger("evaluation.splitter")


@dataclass
class FoldSplit:
    fold_index: int
    train_indices: np.ndarray
    val_indices: np.ndarray
    train_dates: Tuple[str, str]
    val_dates: Tuple[str, str]


@dataclass
class SplitResult:
    train_val_indices: np.ndarray
    test_indices: np.ndarray
    folds: List[FoldSplit]
    test_dates: Tuple[str, str]


class TimeSeriesSplitter:
    """
    Chronological splitter that partitions time-series data into a final test set
    and K expanding walk-forward validation folds without temporal leakage.
    """

    def __init__(self, test_size: float = 0.2, n_splits: int = 3, date_col: str = "date"):
        self.test_size = test_size
        self.n_splits = n_splits
        self.date_col = date_col

    def split(self, df: pd.DataFrame) -> SplitResult:
        """
        Splits DataFrame chronologically into K walk-forward CV folds and a final test set.

        Args:
            df: Input DataFrame containing a date column.

        Returns:
            SplitResult: Object holding fold indices, dates, and test set partition.
        """
        if self.date_col not in df.columns:
            raise ValueError(f"Date column '{self.date_col}' missing from DataFrame.")

        # Ensure sorted chronologically
        dates_series = pd.to_datetime(df[self.date_col])
        unique_dates = np.sort(dates_series.unique())
        total_unique_dates = len(unique_dates)

        if total_unique_dates < self.n_splits + 2:
            raise ValueError(
                f"Insufficient unique dates ({total_unique_dates}) for n_splits={self.n_splits} and test set."
            )

        # Determine test cutoff index
        n_test_dates = max(1, int(np.round(total_unique_dates * self.test_size)))
        n_train_val_dates = total_unique_dates - n_test_dates

        train_val_dates = unique_dates[:n_train_val_dates]
        test_dates_arr = unique_dates[n_train_val_dates:]

        # Map to DataFrame row indices
        df_dates_arr = dates_series.values
        train_val_mask = np.isin(df_dates_arr, train_val_dates)
        test_mask = np.isin(df_dates_arr, test_dates_arr)

        train_val_indices = np.where(train_val_mask)[0]
        test_indices = np.where(test_mask)[0]

        test_date_min = str(pd.Timestamp(test_dates_arr[0]).date())
        test_date_max = str(pd.Timestamp(test_dates_arr[-1]).date())

        # Build K Walk-Forward Folds on train_val_dates
        # Divide train_val_dates into (n_splits + 1) blocks
        block_size = len(train_val_dates) // (self.n_splits + 1)
        if block_size < 1:
            block_size = 1

        folds: List[FoldSplit] = []

        for fold in range(1, self.n_splits + 1):
            if fold < self.n_splits:
                val_start_idx = block_size * fold
                val_end_idx = block_size * (fold + 1)
            else:
                val_start_idx = block_size * fold
                val_end_idx = len(train_val_dates)

            fold_train_dates = train_val_dates[:val_start_idx]
            fold_val_dates = train_val_dates[val_start_idx:val_end_idx]

            fold_train_mask = np.isin(df_dates_arr, fold_train_dates)
            fold_val_mask = np.isin(df_dates_arr, fold_val_dates)

            f_train_idx = np.where(fold_train_mask)[0]
            f_val_idx = np.where(fold_val_mask)[0]

            tr_min = str(pd.Timestamp(fold_train_dates[0]).date())
            tr_max = str(pd.Timestamp(fold_train_dates[-1]).date())
            val_min = str(pd.Timestamp(fold_val_dates[0]).date())
            val_max = str(pd.Timestamp(fold_val_dates[-1]).date())

            folds.append(
                FoldSplit(
                    fold_index=fold,
                    train_indices=f_train_idx,
                    val_indices=f_val_idx,
                    train_dates=(tr_min, tr_max),
                    val_dates=(val_min, val_max),
                )
            )

        logger.info(
            f"Time-series split complete: {len(train_val_indices)} train/val rows ({len(train_val_dates)} dates), "
            f"{len(test_indices)} test rows ({len(test_dates_arr)} dates), {len(folds)} CV folds."
        )

        return SplitResult(
            train_val_indices=train_val_indices,
            test_indices=test_indices,
            folds=folds,
            test_dates=(test_date_min, test_date_max),
        )
