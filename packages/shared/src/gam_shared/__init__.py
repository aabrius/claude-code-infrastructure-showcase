"""
Utility modules for Google Ad Manager API integration.
"""

__version__ = "1.0.0"

from .cache import CacheBackend, FileCache, MemoryCache, get_cache
from .formatters import (
    ReportFormatter, JSONFormatter, CSVFormatter, SummaryFormatter, ExcelFormatter,
    get_formatter
)
from .logger import (
    StructuredLogger, setup_logging, get_logger, get_structured_logger,
    log_function_call, log_performance
)
from .validators import (
    validate_dimension, validate_metric, validate_dimensions_list, validate_metrics_list,
    validate_report_type_compatibility, validate_date_range, validate_network_code,
    validate_currency_code, validate_timezone, validate_report_name,
    VALID_DIMENSIONS, VALID_METRICS, REACH_ONLY_METRICS,
)
from .dimensions_metrics import (
    # Constants
    ALL_DIMENSIONS, ALL_METRICS, REACH_METRICS,
    TIME_DIMENSIONS, ADVERTISER_DIMENSIONS, AD_UNIT_DIMENSIONS,
    LINE_ITEM_DIMENSIONS, ORDER_DIMENSIONS, CREATIVE_DIMENSIONS,
    GEOGRAPHIC_DIMENSIONS, DEVICE_DIMENSIONS, PROGRAMMATIC_DIMENSIONS,
    AD_SERVER_METRICS, REVENUE_METRICS, TOTAL_METRICS, INVENTORY_METRICS,
    AD_EXCHANGE_METRICS, ACTIVE_VIEW_METRICS, VIDEO_METRICS, YIELD_METRICS,
    # Enums
    ReportType, DimensionCategory, MetricCategory,
    # Pydantic Models
    DimensionInfo, MetricInfo, ReportDimensionsMetrics,
    DimensionsMetricsResponse, CommonCombination,
    # Helper functions
    get_dimensions_by_category, get_metrics_by_category,
    get_metrics_for_report_type, normalize_metric_name, get_common_combinations,
    # Mappings
    REST_TO_SOAP_METRICS, SOAP_TO_REST_METRICS,
)

__all__ = [
    # Cache
    "CacheBackend", "FileCache", "MemoryCache", "get_cache",

    # Formatters
    "ReportFormatter", "JSONFormatter", "CSVFormatter", "SummaryFormatter", "ExcelFormatter",
    "get_formatter",

    # Logger
    "StructuredLogger", "setup_logging", "get_logger", "get_structured_logger",
    "log_function_call", "log_performance",

    # Validators
    "validate_dimension", "validate_metric", "validate_dimensions_list", "validate_metrics_list",
    "validate_report_type_compatibility", "validate_date_range", "validate_network_code",
    "validate_currency_code", "validate_timezone", "validate_report_name",
    "VALID_DIMENSIONS", "VALID_METRICS", "REACH_ONLY_METRICS",

    # Dimensions/Metrics Constants
    "ALL_DIMENSIONS", "ALL_METRICS", "REACH_METRICS",
    "TIME_DIMENSIONS", "ADVERTISER_DIMENSIONS", "AD_UNIT_DIMENSIONS",
    "LINE_ITEM_DIMENSIONS", "ORDER_DIMENSIONS", "CREATIVE_DIMENSIONS",
    "GEOGRAPHIC_DIMENSIONS", "DEVICE_DIMENSIONS", "PROGRAMMATIC_DIMENSIONS",
    "AD_SERVER_METRICS", "REVENUE_METRICS", "TOTAL_METRICS", "INVENTORY_METRICS",
    "AD_EXCHANGE_METRICS", "ACTIVE_VIEW_METRICS", "VIDEO_METRICS", "YIELD_METRICS",

    # Enums
    "ReportType", "DimensionCategory", "MetricCategory",

    # Pydantic Models
    "DimensionInfo", "MetricInfo", "ReportDimensionsMetrics",
    "DimensionsMetricsResponse", "CommonCombination",

    # Helper functions
    "get_dimensions_by_category", "get_metrics_by_category",
    "get_metrics_for_report_type", "normalize_metric_name", "get_common_combinations",

    # Mappings
    "REST_TO_SOAP_METRICS", "SOAP_TO_REST_METRICS",
]