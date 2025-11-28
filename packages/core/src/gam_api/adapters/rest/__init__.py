"""
REST adapter package for Google Ad Manager API.

This package provides REST API adapter implementation for GAM operations
with advanced features like streaming, caching, and resilience patterns.
"""

from .rest_adapter import (
    RESTAdapter,
    # Enums
    Visibility,
    Recurrence,
    Frequency,
    DayOfWeek,
    TimeZoneSource,
    ReportType,
    TimePeriodColumn,
    # Builders
    ScheduleOptionsBuilder,
    SortBuilder,
    ReportDefinitionBuilder,
    # Parsers
    MetricValueParser,
)
from .analytics import RESTAnalytics
from .async_adapter import AsyncRESTAdapter

__all__ = [
    # Adapters
    "RESTAdapter",
    "RESTAnalytics",
    "AsyncRESTAdapter",
    # Enums
    "Visibility",
    "Recurrence",
    "Frequency",
    "DayOfWeek",
    "TimeZoneSource",
    "ReportType",
    "TimePeriodColumn",
    # Builders
    "ScheduleOptionsBuilder",
    "SortBuilder",
    "ReportDefinitionBuilder",
    # Parsers
    "MetricValueParser",
]