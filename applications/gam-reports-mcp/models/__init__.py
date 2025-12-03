# models/__init__.py
"""GAM Reports MCP - Complete Pydantic model mapping for GAM REST API."""

# Errors
from .errors import APIError, AuthenticationError, QuotaExceededError, ValidationError

# Enums
from .enums import (
    Visibility,
    ReportType,
    RelativeDateRange,
    Operation,
    TimePeriodColumn,
    TimeZoneSource,
    DayOfWeek,
    Frequency,
    DeliveryCondition,
    MetricValueType,
    ComparisonType,
    ReportState,
)

# Date Range
from .date_range import Date, FixedDateRange, DateRange

# Filters
from .filters import (
    IntList,
    StringList,
    DoubleList,
    Slice,
    ReportValue,
    Field_,
    FieldFilter,
    FilterList,
    Filter,
    DateRangeFilter,
    DomainFilter,
    AppFilter,
    AdStrategyFilter,
)

# Schedule
from .schedule import (
    TimeOfDay,
    WeeklySchedule,
    MonthlySchedule,
    Schedule,
    ScheduleOptions,
)

# Reports
from .reports import (
    Sort,
    Flag,
    ReportDefinition,
    Report,
    CreateReportRequest,
    ReportResponse,
    RunReportResponse,
    ReportRow,
    FetchRowsResponse,
)

# Dimensions and Metrics
from .dimensions import (
    Dimension,
    DimensionCategory,
    DataFormat,
    ReportType,
    ALLOWED_DIMENSIONS,
)
from .metrics import Metric, MetricCategory, ALLOWED_METRICS

# Knowledge Base
from .knowledge import (
    Domain,
    App,
    AdStrategy,
    ReportTemplate,
    KNOWN_DOMAINS,
    KNOWN_APPS,
    AD_STRATEGIES,
    REPORT_TEMPLATES,
)

# Size
from .size import Size, SizeType, COMMON_SIZES

__all__ = [
    # Errors
    "APIError",
    "AuthenticationError",
    "QuotaExceededError",
    "ValidationError",
    # Enums
    "Visibility",
    "ReportType",
    "RelativeDateRange",
    "Operation",
    "TimePeriodColumn",
    "TimeZoneSource",
    "DayOfWeek",
    "Frequency",
    "DeliveryCondition",
    "MetricValueType",
    "ComparisonType",
    "ReportState",
    # Date Range
    "Date",
    "FixedDateRange",
    "DateRange",
    # Filters
    "IntList",
    "StringList",
    "DoubleList",
    "Slice",
    "ReportValue",
    "Field_",
    "FieldFilter",
    "FilterList",
    "Filter",
    "DateRangeFilter",
    "DomainFilter",
    "AppFilter",
    "AdStrategyFilter",
    # Schedule
    "TimeOfDay",
    "WeeklySchedule",
    "MonthlySchedule",
    "Schedule",
    "ScheduleOptions",
    # Reports
    "Sort",
    "Flag",
    "ReportDefinition",
    "Report",
    "CreateReportRequest",
    "ReportResponse",
    "RunReportResponse",
    "ReportRow",
    "FetchRowsResponse",
    # Dimensions and Metrics
    "Dimension",
    "DimensionCategory",
    "DataFormat",
    "ReportType",
    "ALLOWED_DIMENSIONS",
    "Metric",
    "MetricCategory",
    "ALLOWED_METRICS",
    # Knowledge Base
    "Domain",
    "App",
    "AdStrategy",
    "ReportTemplate",
    "KNOWN_DOMAINS",
    "KNOWN_APPS",
    "AD_STRATEGIES",
    "REPORT_TEMPLATES",
    # Size
    "Size",
    "SizeType",
    "COMMON_SIZES",
]
