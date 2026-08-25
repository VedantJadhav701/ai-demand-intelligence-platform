"""
Artifact logger module for uploading reports, leaderboard CSVs, and predictions to MLflow runs.
"""

from pathlib import Path
from typing import Union, List, Optional
import mlflow

from src.utils.logger import get_logger

logger = get_logger("tracking.artifacts")


def log_run_artifacts(
    file_paths: List[Union[str, Path]], artifact_path: Optional[str] = None
) -> None:
    """
    Logs list of local file paths as MLflow run artifacts.

    Args:
        file_paths: List of file paths to upload.
        artifact_path: Subdirectory inside MLflow run artifact store.
    """
    for fp in file_paths:
        path_obj = Path(fp)
        if path_obj.exists():
            try:
                mlflow.log_artifact(str(path_obj.resolve()), artifact_path=artifact_path)
                logger.info(f"Logged artifact '{path_obj.name}' to MLflow.")
            except Exception as e:
                logger.warning(f"Failed to log artifact '{path_obj.name}': {e}")
        else:
            logger.warning(f"Artifact file not found at {path_obj.resolve()}")
