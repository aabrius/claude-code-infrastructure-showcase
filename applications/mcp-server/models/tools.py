"""
Pydantic models for MCP tool inputs and outputs.

These models provide:
- Input validation with Field constraints
- Output schema generation for structured responses
- Clear parameter descriptions for LLM discovery
"""

from typing import Annotated, List, Literal, Optional
from pydantic import BaseModel, Field


# =============================================================================
# INPUT MODELS
# =============================================================================

class QuickReportInput(BaseModel):
    """Input for gam_quick_report tool."""
    report_type: Literal["delivery", "inventory", "sales", "reach", "programmatic"] = Field(
        ...,
        description="Type of report to generate"
    )
    days_back: int = Field(
        30,
        ge=1,
        le=365,
        description="Number of days to look back from today"
    )
    format: Literal["json", "csv", "summary"] = Field(
        "json",
        description="Output format for the report data"
    )


class CreateReportInput(BaseModel):
    """Input for gam_create_report tool."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Report name for identification"
    )
    dimensions: List[str] = Field(
        ...,
        min_length=1,
        description="List of dimensions (e.g., ['DATE', 'AD_UNIT_NAME'])"
    )
    metrics: List[str] = Field(
        ...,
        min_length=1,
        description="List of metrics (e.g., ['AD_SERVER_IMPRESSIONS'])"
    )
    start_date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Start date in YYYY-MM-DD format"
    )
    end_date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="End date in YYYY-MM-DD format"
    )
    report_type: Literal["HISTORICAL", "REACH", "AD_SPEED"] = Field(
        "HISTORICAL",
        description="Report type (affects available metrics)"
    )
    run_immediately: bool = Field(
        True,
        description="Whether to execute the report immediately after creation"
    )


# =============================================================================
# OUTPUT MODELS
# =============================================================================

class QuickReportResponse(BaseModel):
    """Response from gam_quick_report tool."""
    success: bool = Field(..., description="Whether the operation succeeded")
    report_type: Optional[str] = Field(None, description="Type of report generated")
    days_back: Optional[int] = Field(None, description="Days of data included")
    total_rows: Optional[int] = Field(None, description="Number of data rows")
    dimensions: Optional[List[str]] = Field(None, description="Dimensions in report")
    metrics: Optional[List[str]] = Field(None, description="Metrics in report")
    generated_at: Optional[str] = Field(None, description="Generation timestamp")
    error: Optional[str] = Field(None, description="Error message if failed")
    message: Optional[str] = Field(None, description="Additional information")
    suggestion: Optional[str] = Field(None, description="Recovery action if error occurred")


class ListReportsResponse(BaseModel):
    """Response from gam_list_reports tool."""
    success: bool
    total_reports: Optional[int] = None
    reports: Optional[List[dict]] = None
    page: Optional[int] = Field(None, description="Current page number")
    page_size: Optional[int] = Field(None, description="Reports per page")
    total_pages: Optional[int] = Field(None, description="Total pages available")
    error: Optional[str] = None
    message: Optional[str] = None
    suggestion: Optional[str] = Field(None, description="Recovery action if error occurred")


class DimensionsMetricsResponse(BaseModel):
    """Response from gam_get_dimensions_metrics tool."""
    success: bool = True
    report_type: str
    dimensions: Optional[List[str]] = None
    metrics: Optional[List[str]] = None
    dimension_count: Optional[int] = None
    metric_count: Optional[int] = None
    suggestion: Optional[str] = Field(None, description="Recovery action if error occurred")


class CommonCombinationsResponse(BaseModel):
    """Response from gam_get_common_combinations tool."""
    success: bool = True
    combinations: dict
    total_combinations: int


class QuickReportTypesResponse(BaseModel):
    """Response from gam_get_quick_report_types tool."""
    success: bool = True
    quick_report_types: dict


class CreateReportResponse(BaseModel):
    """Response from gam_create_report tool."""
    success: bool
    action: Optional[str] = None
    report_id: Optional[str] = None
    name: Optional[str] = None
    dimensions: Optional[List[str]] = None
    metrics: Optional[List[str]] = None
    date_range: Optional[dict] = None
    report_type: Optional[str] = None
    created_at: Optional[str] = None
    raw_response: Optional[dict] = None
    error: Optional[str] = None
    message: Optional[str] = None
    suggestion: Optional[str] = Field(None, description="Recovery action if error occurred")


class RunReportResponse(BaseModel):
    """Response from gam_run_report tool."""
    success: bool
    report_id: Optional[str] = None
    status: Optional[str] = Field(None, description="Report status: PENDING, RUNNING, COMPLETED, FAILED")
    total_rows: Optional[int] = None
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    data_preview: Optional[List[dict]] = Field(None, description="First 10 rows of data")
    download_url: Optional[str] = Field(None, description="URL to download full report")
    error: Optional[str] = None
    message: Optional[str] = None
    suggestion: Optional[str] = Field(None, description="Recovery action if error occurred")


class ReportTypeInfo(BaseModel):
    """Information about a report type."""
    name: str
    description: str
    supported_metrics: str
    use_cases: List[str] = Field(default_factory=list)


class ReportTypesResponse(BaseModel):
    """Response from gam_get_report_types tool."""
    success: bool = True
    report_types: dict = Field(default_factory=dict)
    total_types: int = 3


class OperationStats(BaseModel):
    """Performance stats for a single operation."""
    count: int = 0
    errors: int = 0
    avg_time_ms: float = 0.0
    p50_ms: Optional[float] = None
    p95_ms: Optional[float] = None
    p99_ms: Optional[float] = None


class CacheStats(BaseModel):
    """Cache performance statistics."""
    hits: int = 0
    misses: int = 0
    hit_rate: float = 0.0
    total_size_mb: float = 0.0


class PerformanceStatsResponse(BaseModel):
    """Response from gam_get_performance_stats tool."""
    success: bool = True
    server_stats: dict = Field(default_factory=dict)
    operation_performance: dict = Field(default_factory=dict)
    cache_stats: Optional[dict] = None
    circuit_breaker_state: str = "CLOSED"
    error: Optional[str] = None
    message: Optional[str] = None


class DimensionInfo(BaseModel):
    """Detailed information about a dimension."""
    id: str
    name: str
    description: str
    category: str


class MetricInfo(BaseModel):
    """Detailed information about a metric."""
    id: str
    name: str
    description: str
    type: str = "number"


class EnhancedDimensionsMetricsResponse(BaseModel):
    """Enhanced response with detailed dimension/metric info."""
    success: bool = True
    report_type: str
    dimensions: Optional[List[DimensionInfo]] = None
    metrics: Optional[List[MetricInfo]] = None
    dimension_count: Optional[int] = None
    metric_count: Optional[int] = None
    suggestion: Optional[str] = None


class QuickReportTypeDetail(BaseModel):
    """Detailed quick report type with dimensions and metrics."""
    name: str
    description: str
    dimensions: List[str]
    metrics: List[str]


class EnhancedQuickReportTypesResponse(BaseModel):
    """Enhanced response with dimensions and metrics per type."""
    success: bool = True
    quick_report_types: dict = Field(default_factory=dict)


class FilterDefinition(BaseModel):
    """Filter definition for custom reports."""
    field: str = Field(..., description="Dimension field to filter on")
    operator: Literal["equals", "contains", "starts_with", "in", "greater_than", "less_than"] = Field(
        "equals", description="Filter operator"
    )
    value: Optional[str] = Field(None, description="Single value for comparison")
    values: Optional[List[str]] = Field(None, description="Multiple values for 'in' operator")


class GetReportResponse(BaseModel):
    """Response from gam_get_report tool."""
    success: bool
    report_id: Optional[str] = None
    name: Optional[str] = Field(None, description="Report display name")
    report_type: Optional[str] = Field(None, description="HISTORICAL, REACH, or AD_SPEED")
    dimensions: Optional[List[str]] = None
    metrics: Optional[List[str]] = None
    date_range: Optional[dict] = Field(None, description="Configured date range")
    filters: Optional[List[dict]] = Field(None, description="Active filters")
    labels: Optional[List[str]] = Field(None, description="Report labels/tags")
    schedule: Optional[dict] = Field(None, description="Schedule configuration if scheduled")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_run_at: Optional[str] = Field(None, description="Last execution timestamp")
    error: Optional[str] = None
    message: Optional[str] = None
    suggestion: Optional[str] = Field(None, description="Recovery action if error occurred")


class UpdateReportResponse(BaseModel):
    """Response from gam_update_report tool."""
    success: bool
    report_id: Optional[str] = None
    updated_fields: Optional[List[str]] = Field(None, description="Fields that were modified")
    name: Optional[str] = None
    dimensions: Optional[List[str]] = None
    metrics: Optional[List[str]] = None
    error: Optional[str] = None
    message: Optional[str] = None
    suggestion: Optional[str] = Field(None, description="Recovery action if error occurred")


class DeleteReportResponse(BaseModel):
    """Response from gam_delete_report tool."""
    success: bool
    report_id: Optional[str] = None
    deleted: bool = False
    error: Optional[str] = None
    message: Optional[str] = None
    suggestion: Optional[str] = Field(None, description="Recovery action if error occurred")


class AddLabelResponse(BaseModel):
    """Response from gam_add_report_label tool."""
    success: bool
    report_id: Optional[str] = None
    labels: Optional[List[str]] = Field(None, description="Current labels after operation")
    added: Optional[List[str]] = Field(None, description="Labels that were added")
    already_present: Optional[List[str]] = Field(None, description="Labels that already existed")
    error: Optional[str] = None
    message: Optional[str] = None
    suggestion: Optional[str] = Field(None, description="Recovery action if error occurred")


# =============================================================================
# TOOL ANNOTATIONS (behavioral hints for clients)
# =============================================================================

METADATA_ANNOTATIONS = {
    "title": "Metadata Discovery",
    "readOnlyHint": True,      # Does not modify any data
    "destructiveHint": False,   # No data is deleted or altered
    "idempotentHint": True,     # Same result on repeated calls
    "openWorldHint": False,     # Works with local/cached data
}

REPORT_GENERATION_ANNOTATIONS = {
    "title": "Report Generation",
    "readOnlyHint": False,      # Creates new reports in GAM
    "destructiveHint": False,   # Does not delete existing data
    "idempotentHint": False,    # Each call creates a NEW report
    "openWorldHint": True,      # Connects to external GAM API
}

LIST_REPORTS_ANNOTATIONS = {
    "title": "Report Discovery",
    "readOnlyHint": True,       # Only reads existing reports
    "destructiveHint": False,
    "idempotentHint": True,     # Same result on repeated calls
    "openWorldHint": True,      # Connects to external GAM API
}

RUN_REPORT_ANNOTATIONS = {
    "title": "Report Execution",
    "readOnlyHint": False,      # Executes/runs a report
    "destructiveHint": False,
    "idempotentHint": False,    # Each run produces new results
    "openWorldHint": True,      # Connects to external GAM API
}

PERFORMANCE_ANNOTATIONS = {
    "title": "Server Monitoring",
    "readOnlyHint": True,       # Only reads stats
    "destructiveHint": False,
    "idempotentHint": True,     # Same result on repeated calls
    "openWorldHint": False,     # Local server stats
}

REPORT_UPDATE_ANNOTATIONS = {
    "title": "Report Management",
    "readOnlyHint": False,      # Modifies reports
    "destructiveHint": False,   # Updates but doesn't delete
    "idempotentHint": True,     # Same update produces same result
    "openWorldHint": True,      # Connects to external GAM API
}

REPORT_DELETE_ANNOTATIONS = {
    "title": "Report Deletion",
    "readOnlyHint": False,      # Deletes data
    "destructiveHint": True,    # DESTRUCTIVE - deletes reports
    "idempotentHint": True,     # Deleting twice = same result
    "openWorldHint": True,      # Connects to external GAM API
}


# =============================================================================
# TAG SETS
# =============================================================================

METADATA_TAGS = {"metadata", "discovery", "start-here"}
REPORT_TAGS = {"reports", "data", "analytics"}
REPORT_MANAGEMENT_TAGS = {"reports", "management", "crud"}
MONITORING_TAGS = {"monitoring", "health", "performance"}
