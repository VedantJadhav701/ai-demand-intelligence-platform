"""
Data Validation module for validating sales datasets against schema and business rules.
"""

from typing import Tuple, List, Dict, Any
import pandas as pd
import numpy as np

from src.utils.config import DataConfig
from src.utils.logger import get_logger
from src.data.schema import ValidationReport, DataSchema
from src.data.ingestion import DataIngestor

logger = get_logger("validation")


class DataValidator:
    """
    Validates sales datasets against required schemas, business constraints,
    numerical ranges, and time-series continuity rules without modifying raw data.
    """

    def __init__(self, data_config: DataConfig):
        self.config = data_config
        self.ingestor = DataIngestor(data_config)

    def validate(self, df: pd.DataFrame) -> ValidationReport:
        """
        Runs comprehensive validation suite on the input DataFrame.

        Args:
            df: Input pandas DataFrame to validate.

        Returns:
            ValidationReport: Report containing validation status, errors, warnings,
                              transformations, and summary metrics.
        """
        errors: List[str] = []
        warnings: List[str] = []
        transformations: List[str] = []
        summary_stats: Dict[str, Any] = {}

        # 1. Inspect Schema
        schema: DataSchema = self.ingestor.inspect_schema(df)
        summary_stats["total_rows"] = schema.total_rows
        summary_stats["total_columns"] = schema.total_columns

        # 2. Validate Required Columns
        if schema.missing_required_columns:
            errors.append(
                f"Missing required column(s): {', '.join(schema.missing_required_columns)}"
            )

        # Early exit if core required columns are missing
        if "date" in schema.missing_required_columns:
            return ValidationReport(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                transformations=transformations,
                schema_info=schema,
                summary_stats=summary_stats,
            )

        # 3. Validate Date Parsing & Format
        parsed_dates = None
        try:
            parsed_dates = pd.to_datetime(
                df["date"], format=self.config.date_format, errors="coerce"
            )
            invalid_dates_count = int(parsed_dates.isna().sum() - df["date"].isna().sum())
            if invalid_dates_count > 0:
                errors.append(
                    f"Found {invalid_dates_count} date values failing format '{self.config.date_format}'"
                )
            else:
                transformations.append(
                    f"Validated 'date' format '{self.config.date_format}' across {len(df)} rows"
                )

            valid_dates = parsed_dates.dropna()
            if not valid_dates.empty:
                summary_stats["min_date"] = str(valid_dates.min().date())
                summary_stats["max_date"] = str(valid_dates.max().date())
                summary_stats["date_range_days"] = int(
                    (valid_dates.max() - valid_dates.min()).days + 1
                )
        except Exception as e:
            errors.append(f"Failed to parse 'date' column: {str(e)}")

        # 4. Check Nulls in Required Key Columns
        for req_col in schema.present_required_columns:
            null_cnt = int(df[req_col].isna().sum())
            if null_cnt > 0:
                errors.append(
                    f"Required column '{req_col}' contains {null_cnt} missing/null values"
                )

        # 5. Check High Missing Value Percentages across columns
        for col, summary in schema.fields.items():
            if summary.missing_pct > self.config.validation_rules.max_missing_pct:
                warnings.append(
                    f"Column '{col}' has high missing value rate: {summary.missing_pct:.1%}"
                )

        # 6. Check Duplicate Records on Primary Key (date, store_id, product_id)
        pk_cols = [c for c in ["date", "store_id", "product_id"] if c in df.columns]
        if len(pk_cols) == 3:
            duplicate_mask = df.duplicated(subset=pk_cols, keep=False)
            duplicate_cnt = int(duplicate_mask.sum())
            if duplicate_cnt > 0:
                errors.append(
                    f"Found {duplicate_cnt} duplicate rows based on primary key ({', '.join(pk_cols)})"
                )
            summary_stats["duplicate_pk_count"] = duplicate_cnt

        # 7. Check Numerical Range & Business Constraints
        rules = self.config.validation_rules

        # 7a. Negative Sales Check
        if "units_sold" in df.columns:
            units = df["units_sold"].dropna()
            negative_sales = units[units < 0]
            if len(negative_sales) > 0 and not rules.allow_negative_sales:
                errors.append(
                    f"Found {len(negative_sales)} rows with negative units_sold (min: {negative_sales.min()})"
                )
            summary_stats["total_units_sold"] = (
                float(units.sum()) if not units.empty else 0.0
            )

        # 7b. Price Check
        if "price" in df.columns:
            prices = df["price"].dropna()
            invalid_prices = prices[prices <= rules.min_price]
            if len(invalid_prices) > 0:
                errors.append(
                    f"Found {len(invalid_prices)} rows with price <= {rules.min_price} (min: {invalid_prices.min()})"
                )

        # 7c. Discount Check
        if "discount" in df.columns:
            discounts = df["discount"].dropna()
            invalid_discounts = discounts[
                (discounts < rules.min_discount) | (discounts > rules.max_discount)
            ]
            if len(invalid_discounts) > 0:
                # Flag percentage scale warning only if all non-negative and max <= 100
                if (
                    discounts.min() >= 0
                    and discounts.max() > 1.0
                    and discounts.max() <= 100.0
                    and rules.max_discount == 1.0
                ):
                    warnings.append(
                        f"Discount values exceed 1.0 (max: {discounts.max()}); please confirm if discount is specified in 0-100 percentage scale."
                    )
                else:
                    errors.append(
                        f"Found {len(invalid_discounts)} rows with discount outside range [{rules.min_discount}, {rules.max_discount}]"
                    )

        # 7d. Inventory Check
        if "inventory" in df.columns:
            inv = df["inventory"].dropna()
            neg_inv = inv[inv < 0]
            if len(neg_inv) > 0:
                errors.append(
                    f"Found {len(neg_inv)} rows with negative inventory (min: {neg_inv.min()})"
                )

        # 8. Check Store / Product Identifiers Integrity
        for id_col in ["store_id", "product_id"]:
            if id_col in df.columns:
                str_series = df[id_col].astype(str).str.strip()
                empty_ids = str_series[str_series.isin(["", "nan", "none", "null"])]
                if len(empty_ids) > 0:
                    errors.append(
                        f"Found {len(empty_ids)} invalid/blank entries in '{id_col}'"
                    )

        # 9. Time Series Continuity Check per (store_id, product_id)
        if (
            rules.check_date_gaps
            and parsed_dates is not None
            and "store_id" in df.columns
            and "product_id" in df.columns
            and not errors
        ):
            gap_summary = self._check_date_continuity(df, parsed_dates)
            if gap_summary["total_gaps"] > 0:
                warnings.append(
                    f"Time-series continuity check detected {gap_summary['total_gaps']} missing date gaps across store-product series."
                )
            summary_stats["date_gaps"] = gap_summary

        is_valid = len(errors) == 0

        report = ValidationReport(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            transformations=transformations,
            schema_info=schema,
            summary_stats=summary_stats,
        )

        if is_valid:
            logger.info("Data validation PASSED with 0 errors.")
        else:
            logger.warning(
                f"Data validation FAILED with {len(errors)} error(s) and {len(warnings)} warning(s)."
            )

        return report

    def _check_date_continuity(
        self, df: pd.DataFrame, parsed_dates: pd.Series
    ) -> Dict[str, Any]:
        """Utility method to detect missing date gaps in daily time series per store & product."""
        temp_df = pd.DataFrame(
            {
                "store_id": df["store_id"],
                "product_id": df["product_id"],
                "date": parsed_dates,
            }
        ).dropna()

        total_gaps = 0
        series_analyzed = 0

        for (store, prod), group in temp_df.groupby(["store_id", "product_id"]):
            series_analyzed += 1
            sorted_dates = group["date"].sort_values().drop_duplicates()
            if len(sorted_dates) > 1:
                expected_range = pd.date_range(
                    start=sorted_dates.min(), end=sorted_dates.max(), freq="D"
                )
                missing_days = len(expected_range) - len(sorted_dates)
                if missing_days > 0:
                    total_gaps += missing_days

        return {"series_count": series_analyzed, "total_gaps": total_gaps}
