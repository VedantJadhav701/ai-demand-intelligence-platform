"""
Unit tests for MLflow experiment tracking, metadata extraction, model registration,
14-day selection rule enforcement, model loading, and registry idempotency.
"""

import os
from pathlib import Path
import pytest
import pandas as pd
import numpy as np
import mlflow

from src.utils.config import load_config, MLflowConfig
from src.tracking.metadata import get_git_metadata, extract_dataset_metadata
from src.tracking.mlflow_tracker import MLflowTracker
from src.tracking.model_registry import ModelRegistrar
from src.models.factory import ModelFactory
from src.models.dataset import ForecastingDatasetBuilder


@pytest.fixture
def tracking_test_df() -> pd.DataFrame:
    """Fixture providing 30 days of daily sales data for tracking tests."""
    dates = pd.date_range("2026-01-01", periods=30, freq="D")
    rows = []
    for d in dates:
        rows.append(
            {
                "date": d.strftime("%Y-%m-%d"),
                "store_id": "S1",
                "product_id": "P1",
                "units_sold": float(50 + d.day * 2),
                "price": 20.0,
                "discount": 0.0,
            }
        )
    return pd.DataFrame(rows)


def test_metadata_and_git_extraction(tracking_test_df: pd.DataFrame):
    """Test dataset metadata extraction and git version tracking."""
    git_meta = get_git_metadata()
    assert "git_commit" in git_meta
    assert "git_branch" in git_meta

    ds_meta = extract_dataset_metadata(tracking_test_df, target_column="units_sold")
    assert ds_meta["row_count"] == 30
    assert ds_meta["column_count"] == 6
    assert ds_meta["target_column"] == "units_sold"
    assert len(ds_meta["dataset_hash"]) > 0


def test_mlflow_config_environment_overrides(tmp_path: Path):
    """Test MLflowConfig environment variable overrides."""
    custom_uri = f"file:{tmp_path}/custom_mlruns"
    custom_exp = "custom-test-experiment"

    os.environ["MLFLOW_TRACKING_URI"] = custom_uri
    os.environ["MLFLOW_EXPERIMENT_NAME"] = custom_exp

    try:
        config = load_config()
        assert config.experiment.mlflow.tracking_uri == custom_uri
        assert config.experiment.mlflow.experiment_name == custom_exp
    finally:
        os.environ.pop("MLFLOW_TRACKING_URI", None)
        os.environ.pop("MLFLOW_EXPERIMENT_NAME", None)


def test_mlflow_tracker_run_logging(tracking_test_df: pd.DataFrame, tmp_path: Path):
    """Test isolated MLflow run logging for parameters, feature config, metrics, and models."""
    test_uri = f"file:{tmp_path}/mlruns"
    cfg = MLflowConfig(tracking_uri=test_uri, experiment_name="test-tracking-exp")

    tracker = MLflowTracker(config=cfg)

    with tracker.start_run(
        run_name="catboost_h1_test", tags={"model": "catboost", "horizon": "1"}
    ) as run:
        run_id = run.info.run_id
        tracker.log_dataset_metadata(tracking_test_df)
        tracker.log_feature_config()

        model = ModelFactory.create("catboost", iterations=10)
        builder = ForecastingDatasetBuilder()
        ds = builder.build_dataset(tracking_test_df, horizon=1)
        model.fit(ds.X, ds.y)

        tracker.log_model_params(model)
        tracker.log_evaluation_metrics(
            cv_wape=12.5, cv_mae=15.0, cv_rmse=18.0, cv_smape=13.0, cv_mape=14.0
        )
        model_info = tracker.log_model_artifact(model, artifact_path="model")

        assert model_info is not None
        assert run_id is not None


def test_model_registration_and_14d_baseline_rule(
    tracking_test_df: pd.DataFrame, tmp_path: Path
):
    """Explicitly test 14-day horizon model receives selection_source='phase3_baseline'."""
    test_uri = f"file:{tmp_path}/mlruns"
    cfg = MLflowConfig(
        tracking_uri=test_uri,
        experiment_name="test-registry-exp",
        registry_name_prefix="demand",
    )

    tracker = MLflowTracker(config=cfg)
    registrar = ModelRegistrar(config=cfg, output_dir=tmp_path / "registry")

    # 1. Log & Register Horizon 14 Model (Phase 3 Baseline)
    with tracker.start_run(
        run_name="catboost_h14_phase3_baseline",
        tags={"model": "catboost", "horizon": "14", "selection_source": "phase3_baseline"},
    ) as run_h14:
        model_h14 = ModelFactory.create("catboost", iterations=10)
        builder = ForecastingDatasetBuilder()
        ds14 = builder.build_dataset(tracking_test_df, horizon=14)
        model_h14.fit(ds14.X, ds14.y)

        tracker.log_model_artifact(model_h14, artifact_path="model")

        reg_info_14 = registrar.register_candidate_model(
            run_id=run_h14.info.run_id,
            model_name="catboost",
            horizon=14,
            selection_source="phase3_baseline",
            cv_wape=11.42,
            test_wape=10.17,
        )

        assert reg_info_14.registry_name == "demand-catboost-h14"
        assert reg_info_14.selection_source == "phase3_baseline"

    # 2. Verify model can be loaded from registry
    success, preds, err = registrar.verify_model_loading(
        registry_name="demand-catboost-h14", alias="production"
    )
    assert success is True
    assert preds is not None
    assert len(preds) > 0


def test_registry_idempotency(tracking_test_df: pd.DataFrame, tmp_path: Path):
    """Test running model registration twice maintains historical runs and does not corrupt registry."""
    test_uri = f"file:{tmp_path}/mlruns"
    cfg = MLflowConfig(
        tracking_uri=test_uri,
        experiment_name="test-idempotency-exp",
        registry_name_prefix="demand",
    )

    tracker = MLflowTracker(config=cfg)
    registrar = ModelRegistrar(config=cfg, output_dir=tmp_path / "registry")

    # Run 1
    with tracker.start_run(run_name="catboost_h1_run1") as run1:
        model1 = ModelFactory.create("catboost", iterations=10)
        builder = ForecastingDatasetBuilder()
        ds = builder.build_dataset(tracking_test_df, horizon=1)
        model1.fit(ds.X, ds.y)
        tracker.log_model_artifact(model1, artifact_path="model")

        reg1 = registrar.register_candidate_model(
            run_id=run1.info.run_id,
            model_name="catboost",
            horizon=1,
            selection_source="phase4_optuna",
            cv_wape=11.8,
            test_wape=10.4,
        )
        assert reg1.version == "1"

    # Run 2 (Idempotency re-run)
    with tracker.start_run(run_name="catboost_h1_run2") as run2:
        model2 = ModelFactory.create("catboost", iterations=10)
        model2.fit(ds.X, ds.y)
        tracker.log_model_artifact(model2, artifact_path="model")

        reg2 = registrar.register_candidate_model(
            run_id=run2.info.run_id,
            model_name="catboost",
            horizon=1,
            selection_source="phase4_optuna",
            cv_wape=11.7,
            test_wape=10.3,
        )
        assert reg2.version == "2"

    # Both versions must exist in history and latest production alias points to version 2
    success, preds, err = registrar.verify_model_loading(
        registry_name="demand-catboost-h1", alias="production"
    )
    assert success is True
