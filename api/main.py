"""
FastAPI Main Application Entry Point.
Initializes FastAPI app, configures CORS, registers routers, and sets up middleware and logging.
"""

import os
import time
from typing import List

# Opt-out of MLflow FileStore deprecation exception for file-based model registry
os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import (
    health_router,
    forecast_router,
    model_router,
    metrics_router,
    explain_router,
    drift_router,
)
from src.utils.config import load_config
from src.utils.logger import setup_logger

logger = setup_logger("api.main", log_level="INFO")
config = load_config()

app = FastAPI(
    title="AI Demand Intelligence & Forecasting API",
    description=(
        "Production REST API for multi-horizon demand forecasting, MLflow model serving, "
        "model registry metadata, and SHAP explainability."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Configuration
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env and allowed_origins_env.strip() != "*":
    allowed_origins = [orig.strip() for orig in allowed_origins_env.split(",") if orig.strip()]
    logger.info(f"Configured CORS Allowed Origins: {allowed_origins}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    logger.info("Configured CORS Allowed Origins: ['*'] (Wildcard)")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time_ms = (time.perf_counter() - start_time) * 1000.0
    response.headers["X-Process-Time-Ms"] = str(round(process_time_ms, 2))
    return response


# Register Routers
app.include_router(health_router)
app.include_router(forecast_router)
app.include_router(model_router)
app.include_router(metrics_router)
app.include_router(explain_router)
app.include_router(drift_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred.",
            "error_type": exc.__class__.__name__,
        },
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=False)
