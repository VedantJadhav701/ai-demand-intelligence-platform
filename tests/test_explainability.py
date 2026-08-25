"""
Unit tests for SHAP ModelExplainer, global/local explanations, and SHAP additivity verification.
"""

from pathlib import Path
import pytest
import pandas as pd
import numpy as np

from src.models.factory import ModelFactory
from src.models.dataset import ForecastingDatasetBuilder
from src.explainability.shap_explainer import (
    ModelExplainer,
    GlobalExplanation,
    LocalExplanation,
)
from src.explainability.report import ExplainabilityReporter


@pytest.fixture
def explainability_df() -> pd.DataFrame:
    """Fixture providing daily sales dataset for SHAP testing."""
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
                "discount": 0.1 if d.day % 2 == 0 else 0.0,
                "promotion": 1 if d.day % 2 == 0 else 0,
            }
        )
    return pd.DataFrame(rows)


@pytest.mark.parametrize("model_name", ["catboost", "lightgbm", "random_forest"])
def test_shap_explainer_dimensions_and_additivity(
    model_name: str, explainability_df: pd.DataFrame
):
    """Test SHAP Explainer dimension consistency and prediction additivity."""
    builder = ForecastingDatasetBuilder()
    ds = builder.build_dataset(explainability_df, horizon=1)

    model = ModelFactory.create(model_name, random_state=42)
    model.fit(ds.X, ds.y)

    explainer = ModelExplainer(model, ds.X)

    # 1. Dimension Check
    assert explainer.shap_values_matrix is not None
    assert explainer.shap_values_matrix.shape == (
        len(ds.X),
        len(explainer.feature_names),
    )

    # 2. Additivity Check
    is_additive, pred_val, shap_sum = explainer.verify_additivity(row_idx=0, atol=1e-1)
    assert is_additive is True
    assert pytest.approx(pred_val, abs=1e-1) == shap_sum


def test_global_and_local_explanations(explainability_df: pd.DataFrame):
    """Test GlobalExplanation ranking and LocalExplanation structure."""
    builder = ForecastingDatasetBuilder()
    ds = builder.build_dataset(explainability_df, horizon=1)

    model = ModelFactory.create("catboost", random_state=42)
    model.fit(ds.X, ds.y)

    explainer = ModelExplainer(model, ds.X)

    # Global explanation
    g_exp = explainer.get_global_explanation()
    assert isinstance(g_exp, GlobalExplanation)
    assert len(g_exp.feature_ranking) == len(explainer.feature_names)
    # Top feature mean |SHAP| should be >= second feature mean |SHAP|
    assert g_exp.feature_ranking[0][1] >= g_exp.feature_ranking[1][1]

    # Local explanation
    l_exp = explainer.explain_instance(row_idx=0, top_n=3)
    assert isinstance(l_exp, LocalExplanation)
    assert l_exp.prediction > 0
    assert isinstance(l_exp.top_positive, list)
    assert isinstance(l_exp.top_negative, list)


def test_explainability_reporter(explainability_df: pd.DataFrame, tmp_path: Path):
    """Test exporting explainability CSVs and PNG charts."""
    builder = ForecastingDatasetBuilder()
    ds = builder.build_dataset(explainability_df, horizon=1)

    model = ModelFactory.create("lightgbm", random_state=42)
    model.fit(ds.X, ds.y)

    explainer = ModelExplainer(model, ds.X)
    reporter = ExplainabilityReporter(output_dir=tmp_path)
    artifacts = reporter.export_reports(explainer)

    assert artifacts["global_importance_csv"].exists()
    assert artifacts["shap_values_csv"].exists()
    assert artifacts["feature_importance_png"].exists()
    assert artifacts["summary_plot_png"].exists()
