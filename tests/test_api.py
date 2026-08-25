"""
Unit and Integration tests for FastAPI Application endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test GET /health lightweight check."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_ready_endpoint():
    """Test GET /ready readiness check."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "models_status" in data
    assert len(data["models_status"]) == 4


def test_model_list_endpoint():
    """Test GET /model production model list."""
    response = client.get("/model")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["total_models"] == 4
    horizons = [m["horizon"] for m in data["models"]]
    assert horizons == [1, 7, 14, 30]


def test_metrics_endpoint():
    """Test GET /metrics performance metrics."""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["total_horizons"] == 4
    # Check 14d baseline rule metric
    m14 = [m for m in data["metrics"] if m["horizon"] == 14][0]
    assert m14["selection_source"] == "phase3_baseline"


def test_forecast_endpoint_valid():
    """Test POST /forecast with valid request."""
    payload = {
        "horizon": 7,
        "store_id": "STORE_17",
        "product_id": "PRODUCT_A",
        "date": "2026-08-23",
        "features": {
            "price": 20.0,
            "discount": 0.0,
            "lag_1": 25.0,
            "lag_7": 24.0,
            "rolling_mean_7": 23.5,
        },
    }
    response = client.post("/forecast", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction_id" in data
    assert data["horizon"] == 7
    assert data["store_id"] == "STORE_17"
    assert data["product_id"] == "PRODUCT_A"
    assert data["forecast"] >= 0.0
    assert data["model"] == "catboost"
    assert data["model_registry_name"] == "demand-catboost-h7"
    assert data["model_alias"] == "production"


def test_forecast_endpoint_invalid_horizon():
    """Test POST /forecast with invalid horizon."""
    payload = {
        "horizon": 5,  # Unsupported horizon
        "store_id": "S1",
        "product_id": "P1",
        "date": "2026-08-23",
        "features": {},
    }
    response = client.post("/forecast", json=payload)
    assert response.status_code in [400, 404, 422]


def test_batch_predict_endpoint():
    """Test POST /batch_predict with multiple records."""
    payload = {
        "records": [
            {
                "horizon": 1,
                "store_id": "S1",
                "product_id": "P1",
                "date": "2026-08-23",
                "features": {"price": 20.0, "lag_1": 25.0},
            },
            {
                "horizon": 14,
                "store_id": "S2",
                "product_id": "P2",
                "date": "2026-08-23",
                "features": {"price": 15.0, "lag_14": 22.0},
            },
        ]
    }
    response = client.post("/batch_predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_records"] == 2
    assert data["successful_predictions"] == 2
    assert len(data["predictions"]) == 2


def test_explain_endpoint_valid():
    """Test POST /explain with valid SHAP request."""
    payload = {
        "horizon": 7,
        "store_id": "STORE_17",
        "product_id": "PRODUCT_A",
        "date": "2026-08-23",
        "features": {
            "price": 20.0,
            "discount": 0.0,
            "lag_1": 25.0,
            "lag_7": 24.0,
            "rolling_mean_7": 23.5,
        },
        "top_n": 3,
    }
    response = client.post("/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction_id" in data
    assert "base_value" in data
    assert "top_positive" in data
    assert "top_negative" in data
    assert "shap_values" in data


def test_cors_headers():
    """Test CORS headers response for allowed origins."""
    headers = {"Origin": "http://localhost:3000"}
    response = client.options("/forecast", headers=headers)
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
