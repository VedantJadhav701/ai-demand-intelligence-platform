"""
Data module containing schema definitions, data ingestion, and data validation routines.
"""

from src.data.schema import ValidationReport, DataSchema, FieldSummary
from src.data.ingestion import DataIngestor
from src.data.validation import DataValidator

__all__ = [
    "ValidationReport",
    "DataSchema",
    "FieldSummary",
    "DataIngestor",
    "DataValidator",
]
