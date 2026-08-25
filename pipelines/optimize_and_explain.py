"""
Phase 4 CLI Pipeline Runner: Optuna Hyperparameter Optimization, Baseline Comparison,
Candidate Model Selection, Final Test Evaluation, and SHAP Explainability.
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
from src.evaluation.leaderboard import Leaderboard
from src.optimization.search import OptunaOptimizer, OptimizationSearchResult
from src.optimization.results import OptimizationResultsContainer
from src.explainability.shap_explainer import ModelExplainer
from src.explainability.report import ExplainabilityReporter

logger = setup_logger("pipelines.optimize_and_explain", log_level="INFO")


def run_phase4_pipeline(config_dir: str = "configs") -> Dict[str, Any]:
    """
    Executes Phase 4 Optimization and SHAP Explainability pipeline.

    Args:
        config_dir: Configuration directory path.

    Returns:
        Dict[str, Any]: Execution summary dictionary.
    """
    logger.info("=================================================================")
    logger.info(" Starting Phase 4 Optuna Optimization & SHAP Pipeline ")
    logger.info("=================================================================")

    # 1. Load Configuration
    config: AppConfig = load_config(config_dir=config_dir)
    seed = config.model.random_seed
    n_trials = config.model.optimization.n_trials
    horizons = config.model.forecast_horizons  # [1, 7, 14, 30]
    models_to_opt = config.model.optimization.models_to_optimize  # ['catboost', 'lightgbm', 'random_forest']

    # 2. Ingest and Validate Data
    ingestor = DataIngestor(config.data)
    raw_df = ingestor.load_data(config.data.raw_data_path)

    validator = DataValidator(config.data)
    validation_report = validator.validate(raw_df)
    if not validation_report.is_valid:
        raise ValueError(f"Data validation failed prior to Phase 4: {validation_report.errors}")

    # 3. Setup Dataset Builder and Evaluator
    engineer = FeatureEngineer()
    dataset_builder = ForecastingDatasetBuilder(
        feature_engineer=engineer, model_config=config.model
    )
    evaluator = WalkForwardEvaluator()
    phase3_leaderboard = Leaderboard()

    # Step 3a. Gather Phase 3 baseline CV metrics for comparison
    logger.info("\n--- Gathering Phase 3 Baseline Metrics for Comparison ---")
    for h in horizons:
        ds = dataset_builder.build_dataset(raw_df, horizon=h)
        splitter = TimeSeriesSplitter(
            test_size=config.model.test_size,
            n_splits=config.model.n_splits,
            date_col="date",
        )
        split_res = splitter.split(ds.df)

        for m_name in ["naive", "seasonal_naive"] + models_to_opt:
            m = ModelFactory.create(m_name, model_config=config.model)
            cv_res = evaluator.evaluate_cv(m, ds, split_res)
            phase3_leaderboard.add_cv_result(cv_res)

    phase3_df = phase3_leaderboard.get_dataframe(sort_by="wape")

    # 4. Run Optuna Optimization per horizon and model
    logger.info("\n=================================================================")
    logger.info(f" RUNNING OPTUNA HYPERPARAMETER OPTIMIZATION ({n_trials} trials/model)")
    logger.info("=================================================================")

    optimizer = OptunaOptimizer(seed=seed, sampler_name=config.model.optimization.sampler)
    results_container = OptimizationResultsContainer(
        output_dir=Path(config.experiment.output_dir) / "optimization"
    )

    best_candidate_per_horizon: Dict[int, Dict[str, Any]] = {}

    for h in horizons:
        logger.info(f"\n--- Optimizing Models for Horizon h={h} days ---")
        ds = dataset_builder.build_dataset(raw_df, horizon=h)
        splitter = TimeSeriesSplitter(
            test_size=config.model.test_size,
            n_splits=config.model.n_splits,
            date_col="date",
        )
        split_res = splitter.split(ds.df)

        h_opt_results: List[OptimizationSearchResult] = []
        for m_name in models_to_opt:
            opt_res: OptimizationSearchResult = optimizer.optimize_model(
                model_name=m_name,
                dataset=ds,
                split_result=split_res,
                n_trials=n_trials,
            )
            results_container.add_result(opt_res)
            h_opt_results.append(opt_res)

        # Collect all candidate options for horizon h from both Phase 3 baselines and Phase 4 Optuna trials
        p3_h_df = phase3_df[
            (phase3_df["Horizon"] == h) & (phase3_df["Eval Type"].str.upper() == "CV")
        ]

        candidates: List[Dict[str, Any]] = []

        # 1. Add Phase 3 baseline candidate options
        for _, row in p3_h_df.iterrows():
            m_key = row["Model"].lower().replace(" ", "_")
            candidates.append(
                {
                    "model": m_key,
                    "cv_wape": float(row["WAPE"]),
                    "source": "Phase 3 Baseline/Default",
                    "params": {},
                }
            )

        # 2. Add Phase 4 Optuna optimized candidate options
        for opt_res in h_opt_results:
            candidates.append(
                {
                    "model": opt_res.model,
                    "cv_wape": opt_res.best_wape,
                    "source": f"Phase 4 Optuna Optimized ({opt_res.total_trials} trials)",
                    "params": opt_res.best_params,
                }
            )

        # Select candidate with absolute lowest CV WAPE across BOTH Phase 3 and Phase 4
        candidates.sort(key=lambda c: c["cv_wape"])
        best_cand = candidates[0]

        best_h_model = best_cand["model"]
        best_h_wape = best_cand["cv_wape"]
        best_h_params = best_cand["params"]
        best_h_source = best_cand["source"]

        # Step 4a. Evaluate Selected Best Candidate Model ONCE on Untouched Final Test Set
        logger.info(
            f"--> Horizon {h}d Best Candidate: '{best_h_model}' via {best_h_source} (CV WAPE: {best_h_wape:.2f}%)"
        )
        candidate_inst = ModelFactory.create(best_h_model, **best_h_params)
        final_test_res = evaluator.evaluate_test(candidate_inst, ds, split_res)

        logger.info(
            f"--> Horizon {h}d Final Test WAPE: {final_test_res.metrics.wape:.2f}% | MAE: {final_test_res.metrics.mae:.2f}"
        )

        best_candidate_per_horizon[h] = {
            "model": best_h_model,
            "cv_wape": best_h_wape,
            "test_wape": final_test_res.metrics.wape,
            "source": best_h_source,
            "best_params": best_h_params,
        }

    # 5. Export Optimization Artifacts & Comparison Table
    opt_artifacts = results_container.export_artifacts()
    comp_df = results_container.build_comparison_table(phase3_df)

    logger.info("\n=================================================================")
    logger.info(" BASELINE VS OPTIMIZED COMPARISON TABLE ")
    logger.info("=================================================================")
    print("\n" + comp_df.to_string(index=False) + "\n")

    # 6. SHAP Explainability
    logger.info("\n=================================================================")
    logger.info(" RUNNING SHAP EXPLAINABILITY ON BEST CANDIDATE MODEL ")
    logger.info("=================================================================")

    # Use best candidate for horizon h=1 (or h=7) for detailed SHAP report
    shap_h = 1 if 1 in best_candidate_per_horizon else horizons[0]
    cand_info = best_candidate_per_horizon[shap_h]
    shap_model_name = cand_info["model"]
    shap_params = cand_info["best_params"]

    ds_shap = dataset_builder.build_dataset(raw_df, horizon=shap_h)
    splitter_shap = TimeSeriesSplitter(
        test_size=config.model.test_size,
        n_splits=config.model.n_splits,
        date_col="date",
    )
    split_shap = splitter_shap.split(ds_shap.df)

    # Train model on train/val pool
    shap_model = ModelFactory.create(shap_model_name, **shap_params)
    X_tr = ds_shap.X.iloc[split_shap.train_val_indices]
    y_tr = ds_shap.y.iloc[split_shap.train_val_indices]
    shap_model.fit(X_tr, y_tr)

    # Fit SHAP Explainer
    explainer = ModelExplainer(shap_model, ds_shap.X)
    global_exp = explainer.get_global_explanation()
    local_exp = explainer.explain_instance(row_idx=0, top_n=5)
    is_additive, pred_val, shap_sum = explainer.verify_additivity(row_idx=0)

    logger.info(f"SHAP Additivity Check for Instance 0: Consistent={is_additive} (Pred: {pred_val}, Base+SHAPs: {shap_sum})")
    logger.info("Top Global Features:")
    for rank, (feat, score) in enumerate(global_exp.feature_ranking[:5], 1):
        logger.info(f"  {rank}. {feat:20s} | Mean |SHAP|: {score:.4f}")

    # Export SHAP Reports
    reporter = ExplainabilityReporter(
        output_dir=Path(config.experiment.output_dir) / "explainability"
    )
    shap_artifacts = reporter.export_reports(explainer)

    # 7. Save Phase 4 JSON Report
    reports_dir = Path(config.experiment.output_dir) / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    phase4_json_path = reports_dir / "phase4_optimization_explainability.json"

    phase4_report = {
        "status": "COMPLETED",
        "n_trials_per_model": n_trials,
        "horizons_optimized": horizons,
        "best_candidate_per_horizon": best_candidate_per_horizon,
        "shap_model_used": shap_model_name,
        "shap_additivity_consistent": is_additive,
        "top_global_features": global_exp.feature_ranking[:5],
        "optimization_artifacts": {k: str(v.resolve()) for k, v in opt_artifacts.items()},
        "explainability_artifacts": {k: str(v.resolve()) for k, v in shap_artifacts.items()},
    }

    with open(phase4_json_path, "w", encoding="utf-8") as f:
        json.dump(phase4_report, f, indent=2)

    logger.info(f"Saved Phase 4 JSON report to {phase4_json_path.resolve()}")
    logger.info("=================================================================")
    logger.info(" Phase 4 Pipeline Completed Successfully ")
    logger.info("=================================================================")

    return phase4_report


if __name__ == "__main__":
    run_phase4_pipeline()
