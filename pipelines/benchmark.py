"""
Phase 3 Benchmark Pipeline Runner.
Executes multi-horizon forecasting benchmark across baselines and ML models
using walk-forward cross validation and untouched final test set evaluation.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

from src.utils.config import load_config, AppConfig
from src.utils.logger import get_logger, setup_logger
from src.data.ingestion import DataIngestor
from src.data.validation import DataValidator
from src.features.builder import FeatureEngineer
from src.models.dataset import ForecastingDatasetBuilder
from src.models.factory import ModelFactory
from src.evaluation.splitter import TimeSeriesSplitter
from src.evaluation.walk_forward import WalkForwardEvaluator
from src.evaluation.predictions import PredictionStore
from src.evaluation.leaderboard import Leaderboard
from src.evaluation.error_analysis import ErrorAnalyzer

logger = setup_logger("pipelines.benchmark", log_level="INFO")


def run_benchmark(config_dir: str = "configs") -> Dict[str, Any]:
    """
    Executes the complete Phase 3 benchmarking pipeline.

    Args:
        config_dir: Directory containing configuration files.

    Returns:
        Dict[str, Any]: Benchmark execution summary.
    """
    logger.info("=================================================================")
    logger.info(" Starting Phase 3 Forecasting Benchmark Pipeline ")
    logger.info("=================================================================")

    # 1. Load Configuration
    config: AppConfig = load_config(config_dir=config_dir)
    output_dir = Path(config.experiment.output_dir)

    metrics_dir = output_dir / "metrics"
    preds_dir = output_dir / "predictions"
    reports_dir = output_dir / "reports"

    metrics_dir.mkdir(parents=True, exist_ok=True)
    preds_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    # 2. Ingest Data
    ingestor = DataIngestor(config.data)
    raw_df = ingestor.load_data(config.data.raw_data_path)

    # 3. Validate Data
    validator = DataValidator(config.data)
    validation_report = validator.validate(raw_df)
    if not validation_report.is_valid:
        raise ValueError(
            f"Data validation failed prior to benchmark: {validation_report.errors}"
        )

    # 4. Feature Engineering
    engineer = FeatureEngineer()
    dataset_builder = ForecastingDatasetBuilder(
        feature_engineer=engineer, model_config=config.model
    )

    # Containers for benchmark
    prediction_store = PredictionStore()
    evaluator = WalkForwardEvaluator(prediction_store=prediction_store)
    leaderboard = Leaderboard()

    models_to_test = [
        "naive",
        "seasonal_naive",
        "ridge_regression",
        "random_forest",
        "xgboost",
        "lightgbm",
        "catboost",
    ]

    horizons = config.model.forecast_horizons  # [1, 7, 14, 30]
    logger.info(f"Testing horizons: {horizons}")
    logger.info(f"Models: {models_to_test}")

    best_models_per_horizon: Dict[int, str] = {}

    # 5. Benchmark across horizons and models
    for h in horizons:
        logger.info(f"\n--- Benchmark Horizon h={h} days ---")

        # Build supervised dataset for horizon h
        ds = dataset_builder.build_dataset(raw_df, horizon=h)

        # Chronological Splitter (Train/Val CV pool & Final Test set)
        splitter = TimeSeriesSplitter(
            test_size=config.model.test_size,
            n_splits=config.model.n_splits,
            date_col="date",
        )
        split_result = splitter.split(ds.df)

        best_h_model_name = ""
        best_h_wape = float("inf")

        for m_name in models_to_test:
            model_inst = ModelFactory.create(m_name, model_config=config.model)

            # Walk-forward CV Evaluation
            cv_res = evaluator.evaluate_cv(model_inst, ds, split_result)
            leaderboard.add_cv_result(cv_res)

            logger.info(
                f"[Horizon {h:2d}d] {m_name:18s} | CV WAPE: {cv_res.mean_metrics.wape:6.2f}% | "
                f"MAE: {cv_res.mean_metrics.mae:6.2f} | RMSE: {cv_res.mean_metrics.rmse:6.2f}"
            )

            if cv_res.mean_metrics.wape < best_h_wape:
                best_h_wape = cv_res.mean_metrics.wape
                best_h_model_name = m_name

        best_models_per_horizon[h] = best_h_model_name
        logger.info(
            f"--> Horizon {h}d Best Model on CV: '{best_h_model_name}' (WAPE: {best_h_wape:.2f}%)"
        )

        # Evaluate best model on untouched Final Test set
        best_model_inst = ModelFactory.create(best_h_model_name, model_config=config.model)
        test_res = evaluator.evaluate_test(best_model_inst, ds, split_result)
        leaderboard.add_test_result(test_res)

        logger.info(
            f"[Horizon {h:2d}d TEST] Best Model '{best_h_model_name}' | Test WAPE: {test_res.metrics.wape:6.2f}% | "
            f"MAE: {test_res.metrics.mae:6.2f} | RMSE: {test_res.metrics.rmse:6.2f}"
        )

    # 6. Leaderboard Export
    csv_path = leaderboard.save_csv(metrics_dir / "model_leaderboard.csv")
    leaderboard_df = leaderboard.get_dataframe(sort_by="wape")

    logger.info("\n=================================================================")
    logger.info(" FINAL FORECASTING BENCHMARK LEADERBOARD (Sorted by WAPE)")
    logger.info("=================================================================")
    print("\n" + leaderboard_df.to_string(index=False) + "\n")

    # 7. Predictions Storage Export
    preds_df = prediction_store.to_dataframe()
    preds_csv = preds_dir / "validation_predictions.csv"
    preds_df.to_csv(preds_csv, index=False)
    logger.info(f"Saved validation predictions to {preds_csv.resolve()}")

    # 8. Error Analysis
    error_analyzer = ErrorAnalyzer()
    error_report = error_analyzer.analyze(preds_df)

    # 9. Save JSON Summary Report
    json_report_path = reports_dir / "phase3_benchmark.json"
    benchmark_summary = {
        "status": "COMPLETED",
        "dataset_rows": len(raw_df),
        "horizons_tested": horizons,
        "models_tested": models_to_test,
        "best_models_per_horizon": best_models_per_horizon,
        "leaderboard_csv": str(csv_path.resolve()),
        "predictions_csv": str(preds_csv.resolve()),
        "worst_performing_store": error_report.worst_performing_store,
        "worst_performing_product": error_report.worst_performing_product,
    }

    with open(json_report_path, "w", encoding="utf-8") as f:
        json.dump(benchmark_summary, f, indent=2)

    logger.info(f"Saved benchmark summary report to {json_report_path.resolve()}")
    logger.info("=================================================================")
    logger.info(" Phase 3 Benchmark Pipeline Completed Successfully ")
    logger.info("=================================================================")

    return benchmark_summary


if __name__ == "__main__":
    run_benchmark()
