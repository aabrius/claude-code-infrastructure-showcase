"""
GAM API Core Package - Google Ad Manager API Integration

This package provides the core functionality for integrating with Google Ad Manager
through both SOAP and REST APIs. It includes authentication, client management,
configuration handling, and report generation capabilities.
"""

__version__ = "1.0.0"

# Core imports
from .auth import AuthManager, get_auth_manager
from .client import GAMClient, get_gam_client  
from .config import Config, load_config, get_config
from .exceptions import (
    GAMError, APIError, AuthenticationError, ConfigurationError,
    InvalidRequestError, ReportGenerationError, ValidationError,
    QuotaExceededError, NetworkError, ReportTimeoutError, NotFoundError
)
from .models import (
    DateRange, DateRangeType, ReportDefinition, ReportType, ReportResult,
    Dimension, Metric, ReportStatus, ExportFormat, QuickReportConfig
)
from .reports import ReportGenerator, list_quick_report_types

# Compatibility aliases for existing code
GAMClient = GAMClient
DateRange = DateRange

# Simple helper classes for backward compatibility
class ReportBuilder:
    """Simple report builder for custom reports."""
    
    def __init__(self):
        self.dimensions = []
        self.metrics = []
        self.filters = []
        self.date_range = None
    
    def add_dimension(self, dimension: str):
        """Add a dimension to the report."""
        self.dimensions.append(dimension)
        return self
    
    def add_metric(self, metric: str):
        """Add a metric to the report."""
        self.metrics.append(metric)
        return self
    
    def set_date_range(self, date_range):
        """Set the date range for the report."""
        self.date_range = date_range
        return self
    
    def build(self):
        """Build the report definition."""
        return {
            "dimensions": self.dimensions,
            "metrics": self.metrics,
            "date_range": self.date_range
        }

__all__ = [
    # Core classes
    "GAMClient", "AuthManager", "Config", "ReportGenerator",
    
    # Helper classes  
    "DateRange", "ReportBuilder",
    
    # Models
    "ReportDefinition", "ReportResult", "DateRangeType", "ReportType",
    "Dimension", "Metric", "ReportStatus", "ExportFormat", "QuickReportConfig",
    
    # Exceptions
    "GAMError", "APIError", "AuthenticationError", "ConfigurationError",
    "InvalidRequestError", "ReportGenerationError", "ValidationError",
    "QuotaExceededError", "NetworkError", "ReportTimeoutError", "NotFoundError",
    
    # Functions
    "get_auth_manager", "get_gam_client", "get_config", "load_config",
    "list_quick_report_types",
]