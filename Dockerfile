# Multi-stage Dockerfile for AI Demand Intelligence & Forecasting API
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=1000 \
    MLFLOW_ALLOW_FILE_STORE=true \
    PORT=8000

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --default-timeout=1000 --retries 10 --no-cache-dir -r requirements.txt

# Copy application source code & MLflow model registry artifacts
COPY pyproject.toml .
COPY configs/ ./configs/
COPY data/ ./data/
COPY src/ ./src/
COPY api/ ./api/
COPY pipelines/ ./pipelines/
COPY mlruns/ ./mlruns/
COPY mlartifacts/ ./mlartifacts/

# Expose Render PORT
EXPOSE ${PORT}

# Uvicorn command accepting dynamic $PORT
CMD exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT}
