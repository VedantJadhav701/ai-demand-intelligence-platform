"""
Unit tests for TimeSeriesSplitter.
"""

import pytest
import pandas as pd
import numpy as np

from src.evaluation.splitter import TimeSeriesSplitter, SplitResult


@pytest.fixture
def dummy_timeseries_df() -> pd.DataFrame:
    """Fixture providing 50 days of time-series records."""
    dates = pd.date_range("2026-01-01", periods=50, freq="D")
    return pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "value": np.arange(50)})


def test_chronological_splitting(dummy_timeseries_df: pd.DataFrame):
    """Test chronological partitioning of train/val pool and test set."""
    splitter = TimeSeriesSplitter(test_size=0.2, n_splits=3, date_col="date")
    res = splitter.split(dummy_timeseries_df)

    assert isinstance(res, SplitResult)
    assert len(res.folds) == 3

    # Check zero overlap between train_val_indices and test_indices
    overlap = set(res.train_val_indices).intersection(set(res.test_indices))
    assert len(overlap) == 0

    # Check chronological ordering: max(train_val_dates) < min(test_dates)
    train_val_dates = dummy_timeseries_df.iloc[res.train_val_indices]["date"]
    test_dates = dummy_timeseries_df.iloc[res.test_indices]["date"]
    assert train_val_dates.max() < test_dates.min()


def test_walk_forward_folds_chronology(dummy_timeseries_df: pd.DataFrame):
    """Test that walk-forward folds have expanding training and strict chronological validation."""
    splitter = TimeSeriesSplitter(test_size=0.2, n_splits=3, date_col="date")
    res = splitter.split(dummy_timeseries_df)

    for i, fold in enumerate(res.folds):
        tr_indices = fold.train_indices
        val_indices = fold.val_indices

        # Zero overlap in fold
        assert len(set(tr_indices).intersection(set(val_indices))) == 0

        # Train dates precede validation dates
        tr_max_date = dummy_timeseries_df.iloc[tr_indices]["date"].max()
        val_min_date = dummy_timeseries_df.iloc[val_indices]["date"].min()
        assert tr_max_date < val_min_date

        # Check expanding window property: Fold i+1 train set includes Fold i train set
        if i > 0:
            prev_tr = set(res.folds[i - 1].train_indices)
            curr_tr = set(tr_indices)
            assert prev_tr.issubset(curr_tr)


def test_final_test_set_isolation_from_cv_folds(dummy_timeseries_df: pd.DataFrame):
    """
    Verifies that no test index or test date appears in any walk-forward CV fold's
    training or validation set.
    """
    splitter = TimeSeriesSplitter(test_size=0.2, n_splits=3, date_col="date")
    res = splitter.split(dummy_timeseries_df)

    test_indices_set = set(res.test_indices)
    test_dates_set = set(dummy_timeseries_df.iloc[res.test_indices]["date"])

    for fold in res.folds:
        fold_train_set = set(fold.train_indices)
        fold_val_set = set(fold.val_indices)

        # Assert no test index is present in fold train or fold val
        assert len(fold_train_set.intersection(test_indices_set)) == 0
        assert len(fold_val_set.intersection(test_indices_set)) == 0

        # Assert no test date is present in fold train dates or val dates
        tr_dates = set(dummy_timeseries_df.iloc[fold.train_indices]["date"])
        val_dates = set(dummy_timeseries_df.iloc[fold.val_indices]["date"])
        assert len(tr_dates.intersection(test_dates_set)) == 0
        assert len(val_dates.intersection(test_dates_set)) == 0
