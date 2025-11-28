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
    validate_currency_code, validate_timezone, validate_report_name
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
]