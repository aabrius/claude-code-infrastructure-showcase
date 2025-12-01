"""
Pydantic response models for MCP tools.

These models provide type safety and automatic serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ReportResponse(BaseModel):
    """Response model for report generation tools."""

    success: bool = True
    report_type: str
    total_rows: int = 0
    days_back: Optional[int] = None
    dimensions: List[str] = Field(default_factory=list)
    metrics: List[str] = Field(default_factory=list)
    data: Optional[List[Dict[str, Any]]] = None
    generated_at: datetime = Field(default_factory=datetime.now)
    degraded_mode: bool = False
    degraded_reason: Optional[str] = None


class ErrorDetail(BaseModel):
    """Error detail structure."""

    type: str
    message: str
    code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    suggestions: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Response model for error cases."""

    success: bool = False
    error: ErrorDetail

    @classmethod
    def create(
        cls,
        error_type: str,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ) -> "ErrorResponse":
        """Factory method to create error response."""
        return cls(
            error=ErrorDetail(
                type=error_type,
                message=message,
                code=error_code,
                details=details,
                suggestions=suggestions or [],
            )
        )


class ReportListItem(BaseModel):
    """Single report in list response."""

    id: Optional[str] = None
    name: Optional[str] = None
    created: Optional[str] = None
    updated: Optional[str] = None


class ListReportsResponse(BaseModel):
    """Response model for list reports tool."""

    success: bool = True
    total_reports: int = 0
    reports: List[ReportListItem] = Field(default_factory=list)


class DimensionsMetricsResponse(BaseModel):
    """Response model for dimensions/metrics metadata."""

    success: bool = True
    report_type: str = "HISTORICAL"
    dimensions: Optional[List[str]] = None
    metrics: Optional[List[str]] = None


class CombinationItem(BaseModel):
    """Single dimension-metric combination."""

    description: str
    dimensions: List[str]
    metrics: List[str]


class CombinationsResponse(BaseModel):
    """Response model for common combinations."""

    success: bool = True
    combinations: Dict[str, CombinationItem]


class QuickReportTypeItem(BaseModel):
    """Single quick report type."""

    name: str
    description: str


class QuickReportTypesResponse(BaseModel):
    """Response model for quick report types."""

    success: bool = True
    quick_report_types: Dict[str, QuickReportTypeItem]
