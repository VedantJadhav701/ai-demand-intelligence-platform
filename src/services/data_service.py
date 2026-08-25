"""
DataService: Manages CSV/Excel sales data uploads, validation,
dataset summary extraction, and automatic feature retrieval per store/product.
"""

import io
import threading
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np

from src.utils.config import AppConfig, load_config
from src.utils.logger import get_logger
from src.data.ingestion import DataIngestor
from src.data.validation import DataValidator
from src.features.builder import FeatureEngineer

logger = get_logger("services.data_service")


class DataService:
    """
    Service layer for CSV/Excel data ingestion, schema validation,
    dataset profiling summary, and automatic feature retrieval for inference.
    """

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or load_config()
        self.ingestor = DataIngestor(self.config.data)
        self.validator = DataValidator(self.config.data)
        self.engineer = FeatureEngineer()
        self._lock = threading.Lock()

        self._current_raw_df: Optional[pd.DataFrame] = None
        self._current_engineered_df: Optional[pd.DataFrame] = None
        self._summary_cache: Optional[Dict[str, Any]] = None

        # Load default sample sales data on startup if present
        self._load_default_sample()

    def _load_default_sample(self) -> None:
        """Loads sample sales dataset as baseline data."""
        try:
            sample_path = self.config.data.raw_data_path
            if pd.io.common.file_exists(sample_path):
                df = self.ingestor.load_data(sample_path)
                self.process_dataset(df)
                logger.info(f"DataService pre-loaded sample dataset from '{sample_path}'.")
        except Exception as e:
            logger.warning(f"Could not pre-load sample dataset: {e}")

    def process_dataset(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validates raw dataset, runs feature engineering, and calculates summary metrics.

        Args:
            df: Input raw sales DataFrame.

        Returns:
            Dict[str, Any]: Summary dictionary with dataset profiling stats and store/product lists.
        """
        # 1. Validation
        val_report = self.validator.validate(df)
        if not val_report.is_valid:
            logger.warning(f"Dataset validation produced warnings: {val_report.errors}")

        # 2. Feature Engineering
        engineered_df = self.engineer.transform(df)

        # 3. Calculate Summary Statistics
        total_rows = len(df)
        total_missing = int(df.isna().sum().sum())
        total_cells = df.shape[0] * df.shape[1]
        missing_pct = round((total_missing / total_cells * 100.0), 2) if total_cells > 0 else 0.0

        store_col = "store_id" if "store_id" in df.columns else "store"
        product_col = "product_id" if "product_id" in df.columns else "product"
        date_col = "date" if "date" in df.columns else "date"

        stores = sorted(list(df[store_col].astype(str).unique())) if store_col in df.columns else ["S1"]
        products = sorted(list(df[product_col].astype(str).unique())) if product_col in df.columns else ["P1"]

        date_min = str(df[date_col].min())[:10] if date_col in df.columns else "N/A"
        date_max = str(df[date_col].max())[:10] if date_col in df.columns else "N/A"

        quality_status = "Good" if missing_pct < 5.0 and val_report.is_valid else "Warning"

        summary = {
            "total_rows": total_rows,
            "total_stores": len(stores),
            "total_products": len(products),
            "date_range": f"{date_min} to {date_max}",
            "date_min": date_min,
            "date_max": date_max,
            "missing_pct": missing_pct,
            "data_quality": quality_status,
            "stores": stores,
            "products": products,
            "is_valid": val_report.is_valid,
            "warnings": val_report.warnings,
        }

        with self._lock:
            self._current_raw_df = df
            self._current_engineered_df = engineered_df
            self._summary_cache = summary

        return summary

    def process_file_upload(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Parses uploaded CSV/Excel file bytes into DataFrame and processes it.

        Args:
            file_content: Raw byte content of file.
            filename: Original file name.

        Returns:
            Dict[str, Any]: Dataset summary dictionary.
        """
        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            df = pd.read_excel(io.BytesIO(file_content))
        else:
            df = pd.read_csv(io.BytesIO(file_content))

        return self.process_dataset(df)

    def get_summary(self) -> Dict[str, Any]:
        """Returns current dataset summary."""
        with self._lock:
            if self._summary_cache:
                return self._summary_cache
        # Return fallback empty summary
        return {
            "total_rows": 0,
            "total_stores": 0,
            "total_products": 0,
            "date_range": "N/A",
            "missing_pct": 0.0,
            "data_quality": "No Data",
            "stores": ["STORE_17", "STORE_12", "STORE_01"],
            "products": ["PRODUCT_A", "PRODUCT_B", "PRODUCT_C"],
            "is_valid": True,
            "warnings": [],
        }

    def get_latest_features_for_series(
        self, store_id: str, product_id: str
    ) -> Dict[str, Any]:
        """
        Automatically retrieves the latest engineered feature values (lags, rolling stats, price)
        from historical data for a specific store and product series.

        Args:
            store_id: Store identifier.
            product_id: Product identifier.

        Returns:
            Dict[str, Any]: Derived feature dictionary ready for forecast model input.
        """
        with self._lock:
            eng_df = self._current_engineered_df

        if eng_df is None or len(eng_df) == 0:
            # Fallback default features
            return {
                "price": 20.0,
                "discount": 0.0,
                "promotion": 0,
                "lag_1": 25.0,
                "lag_7": 24.0,
                "lag_14": 22.0,
                "lag_28": 20.0,
                "rolling_mean_7": 23.5,
                "rolling_std_7": 1.2,
                "rolling_min_7": 20.0,
                "rolling_max_7": 26.0,
                "rolling_mean_14": 22.0,
                "rolling_std_14": 1.5,
                "rolling_min_14": 19.0,
                "rolling_max_14": 27.0,
                "rolling_mean_28": 21.0,
                "rolling_std_28": 1.8,
                "rolling_min_28": 18.0,
                "rolling_max_28": 28.0,
            }

        # Filter by store and product if columns exist
        sub_df = eng_df
        if "store_id" in sub_df.columns:
            sub_df = sub_df[sub_df["store_id"].astype(str) == str(store_id)]
        if "product_id" in sub_df.columns and len(sub_df) > 0:
            sub_df = sub_df[sub_df["product_id"].astype(str) == str(product_id)]

        if len(sub_df) == 0:
            sub_df = eng_df  # Fallback to general latest row

        # Extract latest row
        latest_row = sub_df.iloc[-1].to_dict()

        # Build clean features dict
        feature_keys = [
            "price",
            "discount",
            "promotion",
            "lag_1",
            "lag_7",
            "lag_14",
            "lag_28",
            "rolling_mean_7",
            "rolling_std_7",
            "rolling_min_7",
            "rolling_max_7",
            "rolling_mean_14",
            "rolling_std_14",
            "rolling_min_14",
            "rolling_max_14",
            "rolling_mean_28",
            "rolling_std_28",
            "rolling_min_28",
            "rolling_max_28",
            "store_type",
            "product_category",
        ]

        extracted = {}
        for k in feature_keys:
            if k in latest_row and not pd.isna(latest_row[k]):
                val = latest_row[k]
                extracted[k] = float(val) if isinstance(val, (int, float, np.number)) else str(val)

        return extracted
