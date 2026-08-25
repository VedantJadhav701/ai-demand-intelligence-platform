"""
Unit tests for DataIngestor module.
"""

from pathlib import Path
import pytest
import pandas as pd

from src.data.ingestion import DataIngestor
from src.utils.config import DataConfig


def test_load_csv_data(data_config: DataConfig):
    """Test reading CSV dataset using DataIngestor."""
    ingestor = DataIngestor(data_config)
    df = ingestor.load_data(data_config.raw_data_path)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "date" in df.columns
    assert "units_sold" in df.columns


def test_load_non_existent_file(data_config: DataConfig):
    """Test error handling when loading non-existent file path."""
    ingestor = DataIngestor(data_config)
    with pytest.raises(FileNotFoundError):
        ingestor.load_data("non_existent_directory/file.csv")


def test_unsupported_file_format(data_config: DataConfig, tmp_path: Path):
    """Test error handling for unsupported file formats."""
    invalid_file = tmp_path / "data.txt_invalid"
    invalid_file.write_text("sample content", encoding="utf-8")
    ingestor = DataIngestor(data_config)
    with pytest.raises(ValueError, match="Unsupported file extension"):
        ingestor.load_data(invalid_file)


def test_inspect_schema(data_config: DataConfig, valid_df: pd.DataFrame):
    """Test schema inspection metadata extraction."""
    ingestor = DataIngestor(data_config)
    schema = ingestor.inspect_schema(valid_df)

    assert schema.total_rows == len(valid_df)
    assert schema.total_columns == len(valid_df.columns)
    assert len(schema.missing_required_columns) == 0
    assert "units_sold" in schema.present_required_columns
    assert "revenue" in schema.present_optional_columns
    assert "units_sold" in schema.fields
    assert schema.fields["units_sold"].min_val == 100
    assert schema.fields["units_sold"].max_val == 130
