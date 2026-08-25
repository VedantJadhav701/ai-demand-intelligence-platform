"""
Unit tests for Phase 7 Monitoring & Drift Detection module.
"""

import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from api.main import app
from src.monitoring.drift_detector import (
    DriftDetector,
    FeatureDriftResult,
    PredictionDriftResult,
    ResidualAnalysisResult,
    ModelHealthReport,
)
from src.services.monitoring_service import MonitoringService

client = TestClient(app)


def test_psi_identical_distribution():
    detector = DriftDetector()
    np.random.seed(42)
    ref = np.random.normal(loc=10.0, scale=2.0, size=500)
    curr = np.random.normal(loc=10.0, scale=2.0, size=500)

    psi_val = detector.calculate_psi(ref, curr)
    assert psi_val < 0.10
    assert psi_val >= 0.0


def test_psi_shifted_distribution():
    detector = DriftDetector()
    np.random.seed(42)
    ref = np.random.normal(loc=10.0, scale=2.0, size=500)
    curr = np.random.normal(loc=25.0, scale=2.0, size=500)

    psi_val = detector.calculate_psi(ref, curr)
    assert psi_val >= 0.20


def test_ks_2samp_statistical_test():
    detector = DriftDetector()
    np.random.seed(42)
    ref = np.random.normal(loc=10.0, scale=2.0, size=300)
    curr = np.random.normal(loc=15.0, scale=2.0, size=300)

    ks_stat, p_val = detector.calculate_ks(ref, curr)
    assert ks_stat > 0.5
    assert p_val < 0.05


def test_feature_drift_detection():
    detector = DriftDetector()
    np.random.seed(42)

    ref_df = pd.DataFrame(
        {
            "price": np.random.normal(20, 2, 300),
            "lag_1": np.random.normal(50, 5, 300),
        }
    )
    curr_df = pd.DataFrame(
        {
            "price": np.random.normal(20, 2, 300),  # Stable
            "lag_1": np.random.normal(100, 5, 300),  # Shifted
        }
    )

    results = detector.detect_feature_drift(ref_df, curr_df, features=["price", "lag_1"])
    assert "price" in results
    assert "lag_1" in results

    assert results["price"].status == "NO_DRIFT"
    assert results["lag_1"].status == "SIGNIFICANT_DRIFT"


def test_prediction_drift_detection():
    detector = DriftDetector()
    np.random.seed(42)
    ref_preds = np.random.normal(100, 10, 400)
    curr_preds = np.random.normal(100, 10, 400)

    res = detector.detect_prediction_drift(ref_preds, curr_preds)
    assert res.status == "NO_DRIFT"
    assert abs(res.mean_reference - res.mean_current) < 5.0


def test_residual_analysis():
    detector = DriftDetector()
    # Balanced actuals vs predictions
    actuals = np.array([100.0, 110.0, 90.0, 120.0, 80.0])
    predictions = np.array([101.0, 109.0, 91.0, 119.0, 80.0])

    res = detector.analyze_residuals(actuals, predictions)
    assert res.sample_count == 5
    assert res.mae > 0.0
    assert res.wape > 0.0
    assert res.status == "HEALTHY"

    # Consistently underpredicting sample
    under_preds = np.array([90.0, 100.0, 80.0, 110.0, 70.0])
    res_under = detector.analyze_residuals(actuals, under_preds)
    assert res_under.status == "UNDERPREDICTING"


def test_monitoring_service_get_drift_report():
    service = MonitoringService()
    report = service.get_drift_report()

    assert isinstance(report, ModelHealthReport)
    assert report.overall_status in ["HEALTHY", "WARNING", "CRITICAL"]
    assert len(report.feature_drift) > 0


def test_api_drift_endpoint():
    response = client.get("/drift")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert data["overall_status"] in ["HEALTHY", "WARNING", "CRITICAL"]
    assert "summary_message" in data
    assert "feature_drift" in data
    assert len(data["feature_drift"]) > 0
