"""
Unit tests for DataValidator module.
"""

import pandas as pd
from src.data.validation import DataValidator
from src.utils.config import DataConfig


def test_valid_data_validation(data_config: DataConfig, valid_df: pd.DataFrame):
    """Test that a clean, valid DataFrame passes validation without errors."""
    validator = DataValidator(data_config)
    report = validator.validate(valid_df)

    assert report.is_valid is True
    assert len(report.errors) == 0
    assert report.summary_stats["total_rows"] == len(valid_df)
    assert report.summary_stats["min_date"] == "2026-01-01"
    assert report.summary_stats["max_date"] == "2026-01-04"


def test_missing_required_column(data_config: DataConfig, valid_df: pd.DataFrame):
    """Test validation failure when a required column is missing."""
    df_missing = valid_df.drop(columns=["units_sold"])
    validator = DataValidator(data_config)
    report = validator.validate(df_missing)

    assert report.is_valid is False
    assert any("Missing required column" in err for err in report.errors)
    assert "units_sold" in report.schema_info.missing_required_columns


def test_invalid_data_validation(data_config: DataConfig, invalid_df: pd.DataFrame):
    """Test validation failure with invalid dates, negative sales, invalid prices, and discounts."""
    validator = DataValidator(data_config)
    report = validator.validate(invalid_df)

    assert report.is_valid is False
    assert len(report.errors) > 0

    error_text = " ".join(report.errors)
    assert "date values failing format" in error_text
    assert "negative units_sold" in error_text
    assert "price <=" in error_text
    assert "discount outside range" in error_text
    assert "invalid/blank entries in 'store_id'" in error_text
    assert "duplicate rows based on primary key" in error_text


def test_no_silent_mutation(data_config: DataConfig, invalid_df: pd.DataFrame):
    """Test that validation does NOT mutate the original DataFrame in place."""
    df_copy = invalid_df.copy(deep=True)
    validator = DataValidator(data_config)
    _ = validator.validate(invalid_df)

    # Assert exact equality of raw data
    pd.testing.assert_frame_equal(invalid_df, df_copy)


def test_date_continuity_warning(data_config: DataConfig):
    """Test time-series continuity check detects missing dates and flags warnings."""
    # Dates missing Jan 2
    data = {
        "date": ["2026-01-01", "2026-01-03", "2026-01-04"],
        "store_id": ["STORE_01", "STORE_01", "STORE_01"],
        "product_id": ["PROD_01", "PROD_01", "PROD_01"],
        "units_sold": [100, 110, 130],
    }
    df = pd.DataFrame(data)
    validator = DataValidator(data_config)
    report = validator.validate(df)

    assert report.is_valid is True  # Date gap is a warning, not a critical schema error
    assert len(report.warnings) > 0
    assert any("time-series continuity" in w.lower() for w in report.warnings)
    assert report.summary_stats["date_gaps"]["total_gaps"] == 1
