"""
Pydantic models for API request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum

# Base models
class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class SuccessResponse(BaseModel):
    """Standard success response format."""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# Enums
class ReportTypeEnum(str, Enum):
    """Report type enumeration."""
    HISTORICAL = "HISTORICAL"
    REACH = "REACH"
    AD_SPEED = "AD_SPEED"


class QuickReportTypeEnum(str, Enum):
    """Quick report type enumeration."""
    delivery = "delivery"
    inventory = "inventory"
    sales = "sales"
    reach = "reach"
    programmatic = "programmatic"


class OutputFormatEnum(str, Enum):
    """Output format enumeration."""
    json = "json"
    csv = "csv"
    summary = "summary"


# Request models
class QuickReportRequest(BaseModel):
    """Request model for quick reports."""
    report_type: QuickReportTypeEnum
    days_back: int = Field(default=30, ge=1, le=365, description="Number of days to look back")
    format: OutputFormatEnum = Field(default=OutputFormatEnum.json)
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_type": "delivery",
                "days_back": 30,
                "format": "json"
            }
        }


class CustomReportRequest(BaseModel):
    """Request model for custom reports."""
    name: str = Field(..., min_length=1, max_length=255)
    dimensions: List[str] = Field(..., min_items=1)
    metrics: List[str] = Field(..., min_items=1)
    report_type: ReportTypeEnum = Field(default=ReportTypeEnum.HISTORICAL)
    days_back: int = Field(default=30, ge=1, le=365)
    run_immediately: bool = Field(default=True)
    format: OutputFormatEnum = Field(default=OutputFormatEnum.json)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Custom Delivery Report",
                "dimensions": ["DATE", "AD_UNIT_NAME"],
                "metrics": ["TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS", "TOTAL_LINE_ITEM_LEVEL_CLICKS"],
                "report_type": "HISTORICAL",
                "days_back": 7,
                "run_immediately": True,
                "format": "json"
            }
        }


class DateRangeRequest(BaseModel):
    """Request model for custom date ranges."""
    start_date: date
    end_date: date
    
    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            }
        }


# Response models
class ReportInfo(BaseModel):
    """Basic report information."""
    id: str
    name: str
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class QuickReportResponse(SuccessResponse):
    """Response model for quick reports."""
    report_type: str
    days_back: int
    total_rows: int
    dimensions: List[str]
    metrics: List[str]
    data: Union[List[Dict[str, Any]], str]  # JSON data or CSV string
    execution_time: Optional[float] = None


class CustomReportResponse(SuccessResponse):
    """Response model for custom reports."""
    action: str  # "created", "created_and_executed", "created_but_execution_failed"
    report_id: str
    name: str
    status: str
    created_at: Optional[datetime] = None
    total_rows: Optional[int] = None
    execution_time: Optional[float] = None
    execution_error: Optional[str] = None
    data: Optional[Union[List[Dict[str, Any]], str]] = None


class ReportListResponse(SuccessResponse):
    """Response model for report lists."""
    total_reports: int
    reports: List[ReportInfo]
    page: int = 1
    page_size: int = 20
    total_pages: int = 1


class DimensionsMetricsResponse(SuccessResponse):
    """Response model for dimensions and metrics."""
    report_type: str
    dimensions: Optional[List[str]] = None
    metrics: Optional[List[str]] = None


class CommonCombination(BaseModel):
    """Model for common dimension-metric combinations."""
    name: str
    description: str
    dimensions: List[str]
    metrics: List[str]
    use_case: str


class CommonCombinationsResponse(SuccessResponse):
    """Response model for common combinations."""
    combinations: List[CommonCombination]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"
    gam_connection: str
    components: Dict[str, str]


class StatusResponse(BaseModel):
    """Status response with detailed information."""
    api_status: str
    gam_status: str
    auth_status: str
    config_status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    uptime: Optional[float] = None
    version: str = "1.0.0"