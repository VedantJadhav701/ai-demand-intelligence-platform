"""
Configuration management system using Pydantic models and YAML config files.
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from src.utils.logger import get_logger

logger = get_logger("config")


class ValidationRulesConfig(BaseModel):
    allow_negative_sales: bool = False
    min_price: float = 0.0
    min_discount: float = 0.0
    max_discount: float = 1.0
    check_date_gaps: bool = True
    max_missing_pct: float = 0.20


class DataConfig(BaseModel):
    raw_data_path: str = "data/raw/sample_sales_data.csv"
    required_columns: List[str] = Field(
        default_factory=lambda: ["date", "store_id", "product_id", "units_sold"]
    )
    optional_columns: List[str] = Field(
        default_factory=lambda: [
            "revenue",
            "price",
            "discount",
            "promotion",
            "holiday",
            "store_type",
            "product_category",
            "inventory",
            "region",
        ]
    )
    date_format: str = "%Y-%m-%d"
    validation_rules: ValidationRulesConfig = Field(default_factory=ValidationRulesConfig)


class OptimizationConfig(BaseModel):
    n_trials: int = 10
    models_to_optimize: List[str] = Field(
        default_factory=lambda: ["catboost", "lightgbm", "random_forest"]
    )
    sampler: str = "TPESampler"


class ModelConfig(BaseModel):
    target_column: str = "units_sold"
    forecast_horizons: List[int] = Field(default_factory=lambda: [1, 7, 14, 30])
    seasonal_period: int = 7
    test_size: float = 0.2
    n_splits: int = 3
    primary_metric: str = "WAPE"
    secondary_metrics: List[str] = Field(
        default_factory=lambda: ["MAE", "sMAPE", "RMSE", "MAPE"]
    )
    random_seed: int = 42
    optimization: OptimizationConfig = Field(default_factory=OptimizationConfig)


class MLflowConfig(BaseModel):
    tracking_uri: str = "file:./mlruns"
    experiment_name: str = "demand-forecasting"
    registry_name_prefix: str = "demand"
    artifact_location: str = "./mlartifacts"
    feature_version: str = "phase4_v1"


class ExperimentConfig(BaseModel):
    experiment_name: str = "demand_intelligence_mvp"
    tracking_enabled: bool = True
    log_level: str = "INFO"
    log_dir: str = "logs"
    output_dir: str = "data/outputs"
    mlflow: MLflowConfig = Field(default_factory=MLflowConfig)


class AppConfig(BaseModel):
    app_env: str = "development"
    data: DataConfig = Field(default_factory=DataConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    experiment: ExperimentConfig = Field(default_factory=ExperimentConfig)


def _load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """Loads a YAML configuration file if it exists."""
    if not file_path.exists():
        logger.warning(f"Config file not found at {file_path}. Using default settings.")
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        content = yaml.safe_load(f)
        return content or {}


def load_config(
    config_dir: Optional[str | Path] = None,
    env_file: Optional[str | Path] = ".env",
) -> AppConfig:
    """
    Loads configuration from YAML files and environment variables.

    Args:
        config_dir: Directory containing YAML configuration files (configs/ by default).
        env_file: Path to .env file for environment variables.

    Returns:
        AppConfig: Validated application configuration instance.
    """
    # Load .env if present
    if env_file:
        env_path = Path(env_file)
        if env_path.exists():
            load_dotenv(env_path)

    base_dir = Path(config_dir) if config_dir else Path("configs")

    data_yaml = _load_yaml_file(base_dir / "data.yaml")
    model_yaml = _load_yaml_file(base_dir / "model.yaml")
    experiment_yaml = _load_yaml_file(base_dir / "experiment.yaml")

    data_config = DataConfig(**data_yaml) if data_yaml else DataConfig()
    model_config = ModelConfig(**model_yaml) if model_yaml else ModelConfig()
    experiment_config = (
        ExperimentConfig(**experiment_yaml) if experiment_yaml else ExperimentConfig()
    )

    # Environment variable overrides
    app_env = os.getenv("APP_ENV", "development")
    log_level = os.getenv("LOG_LEVEL", experiment_config.log_level)
    raw_data_path = os.getenv("RAW_DATA_PATH", data_config.raw_data_path)
    random_seed_env = os.getenv("RANDOM_SEED")

    # MLflow environment variable overrides
    mlflow_uri_env = os.getenv("MLFLOW_TRACKING_URI")
    if mlflow_uri_env:
        experiment_config.mlflow.tracking_uri = mlflow_uri_env

    mlflow_exp_env = os.getenv("MLFLOW_EXPERIMENT_NAME")
    if mlflow_exp_env:
        experiment_config.mlflow.experiment_name = mlflow_exp_env

    experiment_config.log_level = log_level
    data_config.raw_data_path = raw_data_path
    if random_seed_env is not None:
        model_config.random_seed = int(random_seed_env)

    config = AppConfig(
        app_env=app_env,
        data=data_config,
        model=model_config,
        experiment=experiment_config,
    )
    logger.info("Configuration loaded successfully.")
    return config
