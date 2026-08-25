"""
Phase 5 CLI Pipeline Runner: MLflow Experiment Tracking, Model Registration,
Manifest Generation, and Model Load Verification.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

from src.utils.config import load_config, AppConfig
from src.utils.logger import setup_logger
from src.data.ingestion import DataIngestor
from src.data.validation import DataValidator
from src.features.builder import FeatureEngineer
from src.models.dataset import ForecastingDatasetBuilder
from src.models.factory import ModelFactory
from src.evaluation.splitter import TimeSeriesSplitter
from src.evaluation.walk_forward import WalkForwardEvaluator
from src.tracking.mlflow_tracker import MLflowTracker
from src.tracking.model_registry import ModelRegistrar, RegisteredModelInfo
from src.tracking.metadata import get_git_metadata, extract_dataset_metadata
from src.tracking.artifacts import log_run_artifacts

logger = setup_logger("pipelines.register_models", log_level="INFO")


def run_phase5_registration_pipeline(config_dir: str = "configs") -> Dict[str, Any]:
    """
    Executes Phase 5 MLflow Experiment Tracking and Model Registration pipeline.

    Args:
        config_dir: Configuration directory path.

    Returns:
        Dict[str, Any]: Execution summary report.
    """
    logger.info("=================================================================")
    logger.info(" Starting Phase 5 MLflow Tracking & Model Registration Pipeline ")
    logger.info("=================================================================")

    # 1. Load Configuration
    config: AppConfig = load_config(config_dir=config_dir)
    mlflow_cfg = config.experiment.mlflow

    # 2. Ingest and Validate Data
    ingestor = DataIngestor(config.data)
    raw_df = ingestor.load_data(config.data.raw_data_path)

    validator = DataValidator(config.data)
    val_report = validator.validate(raw_df)
    if not val_report.is_valid:
        raise ValueError(f"Data validation failed prior to Phase 5: {val_report.errors}")

    dataset_meta = extract_dataset_metadata(
        raw_df, dataset_path=config.data.raw_data_path, target_column=config.model.target_column
    )

    # 3. Setup Dataset Builder, Evaluator, Tracker & Registrar
    engineer = FeatureEngineer()
    dataset_builder = ForecastingDatasetBuilder(
        feature_engineer=engineer, model_config=config.model
    )
    evaluator = WalkForwardEvaluator()

    tracker = MLflowTracker(config=mlflow_cfg)
    registrar = ModelRegistrar(
        config=mlflow_cfg,
        output_dir=Path(config.experiment.output_dir) / "model_registry",
    )

    # 4. Define Selected Horizon Candidates (Phase 4 Results Rule: h14 MUST be Phase 3/default baseline)
    # Load Phase 4 JSON report if present, or use verified Phase 4 selection
    phase4_report_path = (
        Path(config.experiment.output_dir) / "reports" / "phase4_optimization_explainability.json"
    )
    if phase4_report_path.exists():
        with open(phase4_report_path, "r", encoding="utf-8") as f:
            p4_data = json.load(f)
            candidate_specs = p4_data.get("best_candidate_per_horizon", {})
    else:
        # Fallback to explicit Phase 4 candidate specifications
        candidate_specs = {
            "1": {
                "model": "catboost",
                "source": "Phase 4 Optuna Optimized (10 trials)",
                "best_params": {
                    "depth": 5,
                    "learning_rate": 0.0482,
                    "iterations": 125,
                    "l2_leaf_reg": 3.621,
                },
            },
            "7": {
                "model": "catboost",
                "source": "Phase 4 Optuna Optimized (10 trials)",
                "best_params": {
                    "depth": 5,
                    "learning_rate": 0.0482,
                    "iterations": 125,
                    "l2_leaf_reg": 3.621,
                },
            },
            "14": {
                "model": "catboost",
                "source": "Phase 3 Baseline/Default",
                "best_params": {},
            },
            "30": {
                "model": "catboost",
                "source": "Phase 4 Optuna Optimized (10 trials)",
                "best_params": {
                    "depth": 4,
                    "learning_rate": 0.1716,
                    "iterations": 200,
                    "l2_leaf_reg": 8.276,
                },
            },
        }

    registered_models: List[RegisteredModelInfo] = []
    load_verification_results: Dict[str, str] = {}

    # 5. Train, Log, and Register Selected Candidates per Horizon
    for h_str, spec in candidate_specs.items():
        h = int(h_str)
        m_name = spec["model"]
        source_str = spec.get("source", "unknown")
        params = spec.get("best_params", {})

        is_baseline = "Phase 3" in source_str
        selection_source_tag = "phase3_baseline" if is_baseline else "phase4_optuna"
        run_type_tag = "baseline" if is_baseline else "optuna"
        run_name = f"{m_name}_h{h}_{selection_source_tag}"

        logger.info(
            f"\n--- Tracking and Registering Candidate for Horizon h={h}d ({m_name} via {source_str}) ---"
        )

        ds = dataset_builder.build_dataset(raw_df, horizon=h)
        splitter = TimeSeriesSplitter(
            test_size=config.model.test_size,
            n_splits=config.model.n_splits,
            date_col="date",
        )
        split_res = splitter.split(ds.df)

        # Instantiate candidate model
        model_inst = ModelFactory.create(m_name, **params)

        # Run Walk-Forward Cross Validation
        cv_res = evaluator.evaluate_cv(model_inst, ds, split_res)

        # Fit model on train/val pool and run final test evaluation ONCE
        X_tr = ds.X.iloc[split_res.train_val_indices]
        y_tr = ds.y.iloc[split_res.train_val_indices]
        model_inst.fit(X_tr, y_tr)

        test_res = evaluator.evaluate_test(model_inst, ds, split_res)

        # Start MLflow Run
        tags = {
            "model": m_name,
            "horizon": str(h),
            "run_type": run_type_tag,
            "dataset": dataset_meta["dataset_identifier"],
            "feature_version": mlflow_cfg.feature_version,
            "selection_source": selection_source_tag,
        }

        with tracker.start_run(run_name=run_name, tags=tags) as run:
            run_id = run.info.run_id
            logger.info(f"MLflow Run started: ID='{run_id}', Name='{run_name}'")

            # Log Dataset Metadata & Feature Config
            tracker.log_dataset_metadata(raw_df, dataset_path=config.data.raw_data_path)
            tracker.log_feature_config(
                feature_version=mlflow_cfg.feature_version,
                lags=engineer.config.lags,
                rolling_windows=engineer.config.rolling_windows,
                rolling_stats=engineer.config.rolling_stats,
            )

            # Log Hyperparameters & General Config
            extra_params = {
                "horizon": h,
                "seasonal_period": config.model.seasonal_period,
                "random_seed": config.model.random_seed,
                "selection_source": selection_source_tag,
            }
            tracker.log_model_params(model_inst, extra_params=extra_params)

            # Log Metrics (CV, Test, Fold-level, Timing)
            fold_metrics_list = [
                {
                    "wape": f.metrics.wape,
                    "mae": f.metrics.mae,
                    "rmse": f.metrics.rmse,
                    "smape": f.metrics.smape,
                }
                for f in cv_res.fold_results
            ]
            tracker.log_evaluation_metrics(
                cv_wape=cv_res.mean_metrics.wape,
                cv_mae=cv_res.mean_metrics.mae,
                cv_rmse=cv_res.mean_metrics.rmse,
                cv_smape=cv_res.mean_metrics.smape,
                cv_mape=cv_res.mean_metrics.mape,
                test_wape=test_res.metrics.wape,
                test_mae=test_res.metrics.mae,
                test_rmse=test_res.metrics.rmse,
                test_smape=test_res.metrics.smape,
                test_mape=test_res.metrics.mape,
                training_time_sec=cv_res.total_train_time_sec,
                inference_time_sec=cv_res.total_inference_time_sec,
                fold_metrics=fold_metrics_list,
            )

            # Log Model Artifact
            model_info = tracker.log_model_artifact(model_inst, artifact_path="model")

            # Register Candidate Model in Model Registry
            reg_info = registrar.register_candidate_model(
                run_id=run_id,
                model_name=m_name,
                horizon=h,
                selection_source=selection_source_tag,
                cv_wape=cv_res.mean_metrics.wape,
                test_wape=test_res.metrics.wape,
                dataset_identifier=dataset_meta["dataset_identifier"],
                code_version=get_git_metadata().get("git_commit", "unknown"),
                aliases=["candidate", "staging", "production"],
            )

            registered_models.append(reg_info)

            # Conduct Real Model Loading Verification
            success, preds, err = registrar.verify_model_loading(
                registry_name=reg_info.registry_name, alias="production", X_fixture=ds.X.iloc[[0]]
            )
            load_status = "PASS" if success else f"FAIL ({err})"
            load_verification_results[f"{h}d"] = load_status

            logger.info(f"Model Load Test for '{reg_info.registry_name}': {load_status}")

    # 6. Export Selected Models Manifest & Registration Report JSON
    manifest_path, report_path = registrar.generate_manifests(registered_models)

    summary_report = {
        "status": "COMPLETED",
        "tracking_uri": mlflow_cfg.tracking_uri,
        "experiment_name": mlflow_cfg.experiment_name,
        "manifest_path": str(manifest_path.resolve()),
        "registration_report_path": str(report_path.resolve()),
        "registered_models": {r.registry_name: r.model_dump() for r in registered_models},
        "load_verification_results": load_verification_results,
    }

    logger.info("=================================================================")
    logger.info(" Phase 5 MLflow Tracking & Model Registration Completed ")
    logger.info("=================================================================")

    return summary_report


if __name__ == "__main__":
    run_phase5_registration_pipeline()
