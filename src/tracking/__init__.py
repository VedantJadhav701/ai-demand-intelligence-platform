"""
Tracking package for MLflow experiment tracking, dataset metadata, and Model Registry management.
"""

from src.tracking.metadata import get_git_metadata, extract_dataset_metadata
from src.tracking.artifacts import log_run_artifacts
from src.tracking.mlflow_tracker import MLflowTracker
from src.tracking.model_registry import ModelRegistrar, RegisteredModelInfo

__all__ = [
    "get_git_metadata",
    "extract_dataset_metadata",
    "log_run_artifacts",
    "MLflowTracker",
    "ModelRegistrar",
    "RegisteredModelInfo",
]
