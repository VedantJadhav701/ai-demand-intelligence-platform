"""
Dataset metadata extraction and Git code version metadata tracking.
"""

import hashlib
import subprocess
from pathlib import Path
from typing import Dict, Any
import pandas as pd

from src.utils.logger import get_logger

logger = get_logger("tracking.metadata")


def get_git_metadata() -> Dict[str, str]:
    """
    Extracts Git commit hash and branch name if Git is available.
    Returns fallback 'unknown' if Git is not initialized or unavailable.

    Returns:
        Dict[str, str]: Dictionary containing 'git_commit' and 'git_branch'.
    """
    try:
        commit = (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
            )
            .decode("utf-8")
            .strip()
        )
        branch = (
            subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                stderr=subprocess.DEVNULL,
            )
            .decode("utf-8")
            .strip()
        )
        return {"git_commit": commit, "git_branch": branch}
    except Exception:
        return {"git_commit": "unknown", "git_branch": "unknown"}


def extract_dataset_metadata(
    df: pd.DataFrame,
    dataset_path: str = "data/raw/sample_sales_data.csv",
    target_column: str = "units_sold",
) -> Dict[str, Any]:
    """
    Extracts deterministic metadata and fingerprint hash from input dataset.

    Args:
        df: Input pandas DataFrame.
        dataset_path: Path to dataset file.
        target_column: Name of target column.

    Returns:
        Dict[str, Any]: Metadata summary dictionary.
    """
    date_col = "date" if "date" in df.columns else None
    date_min = str(df[date_col].min()) if date_col else "unknown"
    date_max = str(df[date_col].max()) if date_col else "unknown"

    store_count = int(df["store_id"].nunique()) if "store_id" in df.columns else 1
    product_count = (
        int(df["product_id"].nunique()) if "product_id" in df.columns else 1
    )

    # Compute deterministic SHA256 hash over shape and column values
    hash_str = f"{len(df)}_{len(df.columns)}_{list(df.columns)}_{date_min}_{date_max}"
    dataset_hash = hashlib.sha256(hash_str.encode("utf-8")).hexdigest()[:16]

    return {
        "dataset_name": Path(dataset_path).name,
        "dataset_path": dataset_path,
        "dataset_identifier": f"{Path(dataset_path).stem}_{dataset_hash}",
        "dataset_hash": dataset_hash,
        "row_count": len(df),
        "column_count": len(df.columns),
        "date_min": date_min,
        "date_max": date_max,
        "store_count": store_count,
        "product_count": product_count,
        "target_column": target_column,
    }
