"""
Schema definitions and Pydantic models for data structures, schema metadata, and validation reports.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class FieldSummary(BaseModel):
    name: str
    dtype: str
    missing_count: int
    missing_pct: float
    unique_count: int
    min_val: Optional[Any] = None
    max_val: Optional[Any] = None


class DataSchema(BaseModel):
    total_rows: int
    total_columns: int
    present_required_columns: List[str]
    missing_required_columns: List[str]
    present_optional_columns: List[str]
    unknown_columns: List[str]
    fields: Dict[str, FieldSummary] = Field(default_factory=dict)


class ValidationReport(BaseModel):
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    transformations: List[str] = Field(default_factory=list)
    schema_info: Optional[DataSchema] = None
    summary_stats: Dict[str, Any] = Field(default_factory=dict)
