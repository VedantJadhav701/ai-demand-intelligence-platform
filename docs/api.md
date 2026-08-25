# AI Demand Intelligence & Forecasting API Specification

## 1. Overview & Deployment Architecture

- **Backend Target**: Render Web Service (FastAPI + Docker)
- **Frontend Target**: Vercel (Next.js + React)
- **Model Registry**: MLflow Model Registry (`models:/demand-catboost-h{horizon}@production`)
- **Base URL (Local)**: `http://localhost:8000`
- **Base URL (Production)**: `https://<render-backend-name>.onrender.com`
- **Frontend Integration Environment Variable**: `NEXT_PUBLIC_API_URL`

---

## 2. Authentication & CORS

- **Authentication**: Unauthenticated for MVP endpoints. Structure prepared for future Bearer Token / API Key header integration.
- **CORS Configuration**: Configured via `ALLOWED_ORIGINS` environment variable (e.g. `https://<vercel-frontend-domain>.vercel.app`).

---

## 3. Supported Forecast Horizons

The API serves multi-horizon demand forecasts using dedicated production models registered in MLflow:
- `1`: 1-Day Ahead Forecast (`demand-catboost-h1@production`)
- `7`: 7-Days Ahead Forecast (`demand-catboost-h7@production`)
- `14`: 14-Days Ahead Forecast (`demand-catboost-h14@production`)
- `30`: 30-Days Ahead Forecast (`demand-catboost-h30@production`)

---

## 4. Endpoints Specification

### 4.1 Health & Readiness Checks

#### `GET /health`
- **Description**: Lightweight process health check.
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "timestamp": "2026-08-23T01:40:00Z"
}
```

#### `GET /ready`
- **Description**: Deep readiness check verifying MLflow connectivity and production model availability.
- **Response `200 OK`**:
```json
{
  "status": "ready",
  "mlflow_tracking_uri": "file:./mlruns",
  "registry_prefix": "demand",
  "models_status": {
    "1d (demand-catboost-h1)": "READY",
    "7d (demand-catboost-h7)": "READY",
    "14d (demand-catboost-h14)": "READY",
    "30d (demand-catboost-h30)": "READY"
  },
  "timestamp": "2026-08-23T01:40:00Z"
}
```

---

### 4.2 Forecasting

#### `POST /forecast`
- **Description**: Generates single-point demand prediction.
- **Request Body**:
```json
{
  "horizon": 7,
  "store_id": "STORE_17",
  "product_id": "PRODUCT_A",
  "date": "2026-08-23",
  "features": {
    "price": 20.0,
    "discount": 0.0,
    "lag_1": 25.0,
    "lag_7": 24.0,
    "rolling_mean_7": 23.5
  }
}
```
- **Response `200 OK`**:
```json
{
  "prediction_id": "pred_a1b2c3d4e5f6",
  "forecast": 194.2,
  "horizon": 7,
  "store_id": "STORE_17",
  "product_id": "PRODUCT_A",
  "date": "2026-08-23",
  "model": "catboost",
  "model_registry_name": "demand-catboost-h7",
  "model_alias": "production",
  "feature_version": "phase4_v1",
  "inference_time_ms": 1.45,
  "forecast_timestamp": "2026-08-23T01:40:01Z"
}
```

#### `POST /batch_predict`
- **Description**: Generates demand predictions for multiple records.
- **Request Body**:
```json
{
  "records": [
    {
      "horizon": 1,
      "store_id": "S1",
      "product_id": "P1",
      "date": "2026-08-23",
      "features": { "price": 20.0, "lag_1": 25.0 }
    },
    {
      "horizon": 7,
      "store_id": "S1",
      "product_id": "P2",
      "date": "2026-08-23",
      "features": { "price": 15.0, "lag_7": 30.0 }
    }
  ]
}
```
- **Response `200 OK`**:
```json
{
  "total_records": 2,
  "successful_predictions": 2,
  "failed_predictions": 0,
  "total_latency_ms": 3.21,
  "predictions": [ ... ],
  "errors": []
}
```

---

### 4.3 Model & Performance Metrics

#### `GET /model`
- **Description**: Lists registered production models and caching status.
- **Response `200 OK`**:
```json
{
  "status": "success",
  "total_models": 4,
  "models": [
    {
      "horizon": 1,
      "name": "demand-catboost-h1",
      "alias": "production",
      "model_type": "catboost",
      "feature_version": "phase4_v1",
      "cached_in_memory": true,
      "uri": "models:/demand-catboost-h1@production"
    }
  ]
}
```

#### `GET /metrics`
- **Description**: Returns registered model performance metrics (CV and test WAPE scores).
- **Response `200 OK`**:
```json
{
  "status": "success",
  "total_horizons": 4,
  "metrics": [
    {
      "horizon": 1,
      "model": "catboost",
      "registry_name": "demand-catboost-h1",
      "selection_source": "phase4_optuna",
      "cv_wape": 11.83,
      "test_wape": 10.46
    },
    {
      "horizon": 14,
      "model": "catboost",
      "registry_name": "demand-catboost-h14",
      "selection_source": "phase3_baseline",
      "cv_wape": 11.42,
      "test_wape": 10.17
    }
  ]
}
```

---

### 4.4 Explainability

#### `POST /explain`
- **Description**: Computes positive and negative SHAP feature drivers for a prediction.
- **Request Body**:
```json
{
  "horizon": 7,
  "store_id": "STORE_17",
  "product_id": "PRODUCT_A",
  "date": "2026-08-23",
  "features": { "price": 20.0, "lag_1": 25.0, "rolling_mean_7": 23.5 },
  "top_n": 5
}
```
- **Response `200 OK`**:
```json
{
  "prediction_id": "pred_b2c3d4e5f6a1",
  "prediction": 194.2,
  "base_value": 150.0,
  "horizon": 7,
  "store_id": "STORE_17",
  "product_id": "PRODUCT_A",
  "date": "2026-08-23",
  "model": "catboost",
  "model_registry_name": "demand-catboost-h7",
  "model_alias": "production",
  "top_positive": [
    { "feature": "lag_1", "feature_value": 25.0, "shap_value": 15.3 }
  ],
  "top_negative": [
    { "feature": "price", "feature_value": 20.0, "shap_value": -3.5 }
  ],
  "shap_values": { "lag_1": 15.3, "price": -3.5 }
}
```

---

## 5. Error Status Codes

| Status Code | Meaning | Description |
| :--- | :--- | :--- |
| `400 Bad Request` | Invalid Request | Feature schema error, malformed input payload. |
| `404 Not Found` | Unsupported Horizon | Horizon requested is not in `[1, 7, 14, 30]`. |
| `422 Unprocessable Entity` | Pydantic Validation | Missing required JSON fields or data type mismatch. |
| `503 Service Unavailable` | Model / MLflow Error | MLflow Model Registry unreachable or model missing `@production` tag. |
| `500 Internal Error` | Server Error | Unhandled backend exception. |
