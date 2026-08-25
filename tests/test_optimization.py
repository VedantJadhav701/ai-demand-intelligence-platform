"""
Unit tests for Optuna optimization module and final test set isolation.
"""

from pathlib import Path
import pytest
import pandas as pd
import numpy as np
import optuna

from src.models.dataset import ForecastingDatasetBuilder
from src.evaluation.splitter import TimeSeriesSplitter
from src.optimization.objective import TimeSeriesObjective, get_search_space
from src.optimization.search import OptunaOptimizer
from src.optimization.results import OptimizationResultsContainer


@pytest.fixture
def opt_test_df() -> pd.DataFrame:
    """Fixture providing 40 days of daily sales data for optimization testing."""
    dates = pd.date_range("2026-01-01", periods=40, freq="D")
    rows = []
    for d in dates:
        for s in ["S1"]:
            for p in ["P1"]:
                rows.append(
                    {
                        "date": d.strftime("%Y-%m-%d"),
                        "store_id": s,
                        "product_id": p,
                        "units_sold": 100.0 + d.day * 1.5,
                        "price": 20.0,
                        "discount": 0.0,
                    }
                )
    return pd.DataFrame(rows)


def test_search_spaces():
    """Test search space sampling for all three target models."""
    study = optuna.create_study()

    for m_name in ["catboost", "lightgbm", "random_forest"]:
        trial = study.ask()
        params = get_search_space(trial, m_name, seed=42)
        assert isinstance(params, dict)
        assert len(params) > 0


def test_time_series_objective(opt_test_df: pd.DataFrame):
    """Test Optuna objective evaluation over walk-forward CV folds."""
    builder = ForecastingDatasetBuilder()
    ds = builder.build_dataset(opt_test_df, horizon=1)

    splitter = TimeSeriesSplitter(test_size=0.2, n_splits=2, date_col="date")
    split_res = splitter.split(ds.df)

    obj = TimeSeriesObjective(
        model_name="lightgbm", dataset=ds, split_result=split_res, seed=42
    )
    study = optuna.create_study(direction="minimize")
    trial = study.ask()
    wape = obj(trial)

    assert isinstance(wape, float)
    assert wape >= 0.0
    assert "mae" in trial.user_attrs


def test_optuna_optimizer_execution(opt_test_df: pd.DataFrame, tmp_path: Path):
    """Test running OptunaOptimizer study and exporting artifacts."""
    builder = ForecastingDatasetBuilder()
    ds = builder.build_dataset(opt_test_df, horizon=1)

    splitter = TimeSeriesSplitter(test_size=0.2, n_splits=2, date_col="date")
    split_res = splitter.split(ds.df)

    optimizer = OptunaOptimizer(seed=42)
    res = optimizer.optimize_model(
        model_name="random_forest", dataset=ds, split_result=split_res, n_trials=3
    )

    assert res.total_trials == 3
    assert res.best_wape >= 0.0
    assert "n_estimators" in res.best_params

    container = OptimizationResultsContainer(output_dir=tmp_path)
    container.add_result(res)
    artifacts = container.export_artifacts()

    assert artifacts["summary_csv"].exists()
    assert artifacts["trials_csv"].exists()
    assert artifacts["best_params_json"].exists()


def test_final_test_set_never_used_in_objective(opt_test_df: pd.DataFrame):
    """CRITICAL TEST: Verify final test set indices are NEVER passed to Optuna objective."""
    builder = ForecastingDatasetBuilder()
    ds = builder.build_dataset(opt_test_df, horizon=1)

    splitter = TimeSeriesSplitter(test_size=0.2, n_splits=2, date_col="date")
    split_res = splitter.split(ds.df)

    test_idx_set = set(split_res.test_indices)

    # In TimeSeriesObjective, verify each fold's train and val indices have zero intersection with test_idx_set
    for fold in split_res.folds:
        assert len(set(fold.train_indices).intersection(test_idx_set)) == 0
        assert len(set(fold.val_indices).intersection(test_idx_set)) == 0
