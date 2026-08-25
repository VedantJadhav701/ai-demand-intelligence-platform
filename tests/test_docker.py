"""
Integration tests for Docker container building, startup, health check, forecast inference, and clean shutdown.
"""

import subprocess
import time
import requests
import pytest

IMAGE_NAME = "demand-intelligence-api-test"
CONTAINER_NAME = "demand-intelligence-api-test-container"
PORT = 8899


@pytest.mark.skipif(
    subprocess.run(["docker", "info"], capture_output=True).returncode != 0,
    reason="Docker daemon is not running.",
)
def test_docker_build_run_and_inference():
    """Builds Docker image, starts container, verifies API endpoints, and cleans up."""
    # 1. Build Docker Image
    build_cmd = [
        "docker",
        "build",
        "-t",
        IMAGE_NAME,
        "-f",
        "Dockerfile",
        ".",
    ]
    # Remove empty string argument if any
    build_cmd = [c for c in build_cmd if c]

    logger_msg = f"Building Docker image '{IMAGE_NAME}'..."
    print(logger_msg)
    build_res = subprocess.run(build_cmd, capture_output=True, text=True)
    assert build_res.returncode == 0, f"Docker build failed: {build_res.stderr}"

    # Stop any leftover container
    subprocess.run(["docker", "rm", "-f", CONTAINER_NAME], capture_output=True)

    # 2. Run Container
    run_cmd = [
        "docker",
        "run",
        "-d",
        "--name",
        CONTAINER_NAME,
        "-p",
        f"{PORT}:{PORT}",
        "-e",
        f"PORT={PORT}",
        "-e",
        "ENVIRONMENT=test",
        IMAGE_NAME,
    ]
    run_res = subprocess.run(run_cmd, capture_output=True, text=True)
    assert run_res.returncode == 0, f"Docker run failed: {run_res.stderr}"

    try:
        # Give container a few seconds to start up
        base_url = f"http://localhost:{PORT}"
        healthy = False

        for _ in range(15):
            time.sleep(1)
            try:
                r = requests.get(f"{base_url}/health", timeout=2)
                if r.status_code == 200 and r.json().get("status") == "healthy":
                    healthy = True
                    break
            except Exception:
                pass

        assert healthy is True, "Docker container /health endpoint failed to respond."

        # Verify /ready
        r_ready = requests.get(f"{base_url}/ready", timeout=5)
        assert r_ready.status_code == 200, f"/ready failed: {r_ready.text}"

        # Verify /model
        r_model = requests.get(f"{base_url}/model", timeout=5)
        assert r_model.status_code == 200
        assert r_model.json().get("total_models") == 4

        # Verify /forecast
        forecast_payload = {
            "horizon": 7,
            "store_id": "STORE_17",
            "product_id": "PRODUCT_A",
            "date": "2026-08-23",
            "features": {"price": 20.0, "lag_1": 25.0, "rolling_mean_7": 23.5},
        }
        r_fc = requests.post(f"{base_url}/forecast", json=forecast_payload, timeout=5)
        assert r_fc.status_code == 200
        fc_data = r_fc.json()
        assert fc_data.get("forecast") >= 0.0
        assert fc_data.get("horizon") == 7

        # Verify /explain
        explain_payload = {
            "horizon": 7,
            "store_id": "STORE_17",
            "product_id": "PRODUCT_A",
            "date": "2026-08-23",
            "features": {"price": 20.0, "lag_1": 25.0},
            "top_n": 3,
        }
        r_exp = requests.post(f"{base_url}/explain", json=explain_payload, timeout=5)
        assert r_exp.status_code == 200
        exp_data = r_exp.json()
        assert "top_positive" in exp_data

    finally:
        # Clean up container
        subprocess.run(["docker", "rm", "-f", CONTAINER_NAME], capture_output=True)
