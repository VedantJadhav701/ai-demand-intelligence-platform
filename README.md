# AI Demand Intelligence & Forecasting Platform

Production-oriented AI Demand Intelligence and Forecasting Platform built for time-series forecasting, explainable AI, MLOps monitoring, and agentic analytics.

---

## Progress Overview

- **Phase 1**: Project setup, environment configuration, Pydantic YAML config system, data ingestion, data validation engine, structured logging, sample dataset, and unit tests.
- **Phase 2**: Exploratory Data Analysis (EDA) pipeline (data profiling, temporal time-series analysis, business segmentation, feature correlation analysis, chart visualization export) & Feature Engineering pipeline (temporal features, lag features, rolling statistics, price diffs, zero target leakage).
- **Phase 3**: Forecasting Baselines (Naive, Seasonal Naive), Machine Learning Models (Ridge Regression, Random Forest, XGBoost, LightGBM, CatBoost), and Time-Series Walk-Forward Evaluation pipeline.
- **Phase 4**: Optuna Hyperparameter Optimization (time-series walk-forward CV target, independent horizon tuning, baseline vs optimized comparison) & SHAP Explainability (tree explainer, global feature importance, local instance explanations, additivity validation).
- **Phase 5**: MLflow Experiment Tracking & Model Registry (experiment tracking, dataset metadata hash, feature versioning with target leakage protection, horizon-specific model registration `demand-catboost-h{1,7,14,30}`, candidate selection enforcement, production aliasing, manifest export, and model load verification).
- **Phase 6**: FastAPI Model Serving + Docker + Production Deployment Architecture (FastAPI endpoints `/health`, `/ready`, `/forecast`, `/batch_predict`, `/model`, `/metrics`, `/explain`, MLflow Model Registry alias integration, in-memory model caching, CORS readiness for Vercel/Next.js, Docker containerization for Render Web Service, API contract documentation).

---

## Directory Structure

```
ai-demand-intelligence-platform/
├── README.md
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── .dockerignore
├── Project_Context.md
├── api/
│   ├── __init__.py
│   ├── dependencies.py
│   ├── main.py
│   ├── schemas.py
│   └── routes/
│       ├── __init__.py
│       ├── explain.py
│       ├── forecast.py
│       ├── health.py
│       ├── metrics.py
│       └── model.py
├── configs/
│   ├── data.yaml
│   ├── experiment.yaml
│   └── model.yaml
├── data/
│   ├── raw/
│   │   └── sample_sales_data.csv
│   └── outputs/
│       ├── figures/
│       ├── metrics/
│       ├── model_registry/
│       │   ├── registration_report.json
│       │   └── selected_models.json
│       ├── optimization/
│       ├── explainability/
│       └── reports/
├── docker/
│   └── Dockerfile
├── docs/
│   └── api.md
├── pipelines/
│   ├── __init__.py
│   ├── benchmark.py
│   ├── optimize_and_explain.py
│   └── register_models.py
├── src/
│   ├── __init__.py
│   ├── data/
│   ├── eda/
│   ├── evaluation/
│   ├── explainability/
│   ├── features/
│   ├── models/
│   ├── optimization/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── explainability_service.py
│   │   ├── forecast_service.py
│   │   └── model_service.py
│   ├── tracking/
│   └── utils/
└── tests/
    ├── test_api.py
    ├── test_baselines.py
    ├── test_config.py
    ├── test_dataset.py
    ├── test_docker.py
    ├── test_eda.py
    ├── test_explainability.py
    ├── test_features.py
    ├── test_ingestion.py
    ├── test_leakage.py
    ├── test_metrics.py
    ├── test_models.py
    ├── test_optimization.py
    ├── test_splitter.py
    ├── test_tracking.py
    └── test_validation.py
```

---

## Production Deployment Architecture & Topology

```text
                    GITHUB
                       │
       ┌───────────────┴───────────────┐
       ▼                               ▼
    VERCEL                          RENDER
  (Frontend)                       (Backend)
  Next.js + React             FastAPI + Docker Container
       │                               │
       └────────────── API ────────────┘
                        │
                        ▼
                MLflow Model Registry
         models:/demand-catboost-h{h}@production
```

---

## Phase 6 FastAPI & Docker Infrastructure

### 1. Service Layer (`src/services/`)
- **`ModelService`**: Loads production registered models from MLflow (`models:/demand-catboost-h{1,7,14,30}@production`). Implements thread-safe in-memory model caching per horizon.
- **`ForecastService`**: Validates features, auto-extracts temporal date features, aligns model feature columns, and computes point / batch forecasts with latency tracking (`inference_time_ms`).
- **`ExplainabilityService`**: Integrates SHAP TreeExplainer to compute top positive and negative feature drivers safely.

### 2. FastAPI Endpoints (`api/`)
- `GET /health`: Lightweight process health check (`{"status": "healthy"}`).
- `GET /ready`: Readiness check testing MLflow connectivity and production model resolution.
- `POST /forecast`: Single-point demand prediction.
- `POST /batch_predict`: Multi-record demand predictions.
- `GET /model`: Metadata list of production registered models.
- `GET /metrics`: Phase 5 cross-validation and test evaluation metrics.
- `POST /explain`: SHAP feature drivers explanation.

---

## Execution Commands

### Local Development (Python + FastAPI)
```bash
conda run -n thermo_agent pytest -v
conda run -n thermo_agent python -m api.main
```

### Docker (Build & Run Locally)
```bash
docker build -t demand-intelligence-api .
docker run -p 8000:8000 --env-file .env demand-intelligence-api
```

---

## Status & Boundaries

- **Phase 1 - Phase 6 Status**: Completed & Verified (71/71 tests passing).
- **Backend Deployment Target**: Render Web Service
- **Frontend Integration Target**: Vercel (Next.js) via `NEXT_PUBLIC_API_URL`
- **Excluded**: Natural-language SLM analyst, Agentic analytics, Next.js frontend dashboard, Drift monitoring.
