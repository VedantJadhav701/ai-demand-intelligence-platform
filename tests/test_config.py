"""
Unit tests for configuration system loading and validation.
"""

import os
from pathlib import Path
import tempfile
import yaml

from src.utils.config import (
    load_config,
    AppConfig,
    DataConfig,
    ModelConfig,
    ExperimentConfig,
)


def test_default_config_loading():
    """Test loading configuration with default values."""
    config = load_config()
    assert isinstance(config, AppConfig)
    assert isinstance(config.data, DataConfig)
    assert isinstance(config.model, ModelConfig)
    assert isinstance(config.experiment, ExperimentConfig)
    assert "date" in config.data.required_columns
    assert config.model.primary_metric == "WAPE"


def test_yaml_config_loading(tmp_path: Path):
    """Test loading configuration overrides from YAML files."""
    data_yaml = tmp_path / "data.yaml"
    data_yaml.write_text(
        yaml.dump(
            {
                "raw_data_path": "custom/path.csv",
                "required_columns": ["date", "store_id", "product_id", "units_sold"],
            }
        ),
        encoding="utf-8",
    )

    config = load_config(config_dir=tmp_path)
    assert config.data.raw_data_path == "custom/path.csv"


def test_env_variable_overrides(monkeypatch):
    """Test environment variable overrides."""
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("RAW_DATA_PATH", "env/data.csv")
    monkeypatch.setenv("RANDOM_SEED", "99")

    config = load_config()
    assert config.app_env == "production"
    assert config.experiment.log_level == "DEBUG"
    assert config.data.raw_data_path == "env/data.csv"
    assert config.model.random_seed == 99
