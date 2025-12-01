"""MCP Server response models (import shim for hyphenated directory)."""

# Direct import from the actual hyphenated directory
import sys
from pathlib import Path

# Get the actual mcp-server/models directory
models_dir = Path(__file__).parent.parent.parent / "mcp-server" / "models"

# Import the actual module by reading and executing it
import importlib.util

def _load_module(name, path):
    """Load a module from a file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load responses from the actual location
_responses = _load_module("responses", models_dir / "responses.py")

# Re-export all models
ReportResponse = _responses.ReportResponse
ErrorResponse = _responses.ErrorResponse
ErrorDetail = _responses.ErrorDetail
ListReportsResponse = _responses.ListReportsResponse
DimensionsMetricsResponse = _responses.DimensionsMetricsResponse
CombinationItem = _responses.CombinationItem
CombinationsResponse = _responses.CombinationsResponse
QuickReportTypeItem = _responses.QuickReportTypeItem
QuickReportTypesResponse = _responses.QuickReportTypesResponse

__all__ = [
    "ReportResponse",
    "ErrorResponse",
    "ErrorDetail",
    "ListReportsResponse",
    "DimensionsMetricsResponse",
    "CombinationItem",
    "CombinationsResponse",
    "QuickReportTypeItem",
    "QuickReportTypesResponse",
]
