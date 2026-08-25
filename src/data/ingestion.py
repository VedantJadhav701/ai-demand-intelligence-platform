"""
Data Ingestion module for reading CSV and Parquet files and inspecting dataset schemas.
"""

from pathlib import Path
from typing import Union
import pandas as pd

from src.utils.config import DataConfig
from src.utils.logger import get_logger
from src.data.schema import DataSchema, FieldSummary

logger = get_logger("ingestion")


class DataIngestor:
    """Class responsible for loading raw datasets and performing dynamic schema inspection."""

    def __init__(self, data_config: DataConfig):
        self.config = data_config

    def load_data(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """
        Loads dataset from a CSV or Parquet file into a pandas DataFrame.

        Args:
            file_path: Path to the dataset file (CSV or Parquet).

        Returns:
            pd.DataFrame: Loaded dataset.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file extension is unsupported or data is empty.
        """
        path = Path(file_path)
        if not path.exists():
            error_msg = f"Data file does not exist at: {path.resolve()}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        suffix = path.suffix.lower()
        logger.info(f"Loading raw data from {path.resolve()} (format: {suffix})")

        try:
            if suffix in [".csv", ".txt"]:
                df = pd.read_csv(path)
            elif suffix in [".parquet", ".pq"]:
                df = pd.read_parquet(path)
            else:
                raise ValueError(
                    f"Unsupported file extension '{suffix}'. Supported formats: .csv, .parquet"
                )
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            error_msg = f"Failed to parse data file {path}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e

        if df.empty:
            error_msg = f"Loaded dataset from {path} is empty."
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info(f"Successfully loaded dataset with shape: {df.shape}")
        return df

    def inspect_schema(self, df: pd.DataFrame) -> DataSchema:
        """
        Dynamically analyzes the schema of a DataFrame against the configured column definitions.

        Args:
            df: Input DataFrame.

        Returns:
            DataSchema: Object summarizing present/missing columns, unknown columns, and field statistics.
        """
        all_columns = list(df.columns)
        req_set = set(self.config.required_columns)
        opt_set = set(self.config.optional_columns)

        present_req = [col for col in self.config.required_columns if col in df.columns]
        missing_req = [col for col in self.config.required_columns if col not in df.columns]
        present_opt = [col for col in self.config.optional_columns if col in df.columns]
        unknown = [col for col in all_columns if col not in req_set and col not in opt_set]

        fields_summary = {}
        total_rows = len(df)

        for col in all_columns:
            series = df[col]
            missing_count = int(series.isna().sum())
            missing_pct = float(missing_count / total_rows) if total_rows > 0 else 0.0
            unique_count = int(series.nunique(dropna=True))

            min_val = None
            max_val = None
            if pd.api.types.is_numeric_dtype(series) and not series.empty:
                valid_s = series.dropna()
                if not valid_s.empty:
                    min_val = float(valid_s.min())
                    max_val = float(valid_s.max())

            fields_summary[col] = FieldSummary(
                name=col,
                dtype=str(series.dtype),
                missing_count=missing_count,
                missing_pct=round(missing_pct, 4),
                unique_count=unique_count,
                min_val=min_val,
                max_val=max_val,
            )

        schema = DataSchema(
            total_rows=total_rows,
            total_columns=len(all_columns),
            present_required_columns=present_req,
            missing_required_columns=missing_req,
            present_optional_columns=present_opt,
            unknown_columns=unknown,
            fields=fields_summary,
        )

        logger.info(
            f"Schema inspection complete: {len(present_req)}/{len(self.config.required_columns)} required, "
            f"{len(present_opt)}/{len(self.config.optional_columns)} optional present, "
            f"{len(missing_req)} missing required."
        )
        return schema
