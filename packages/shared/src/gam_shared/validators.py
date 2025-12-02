"""
Validators for Google Ad Manager API inputs.

This module provides validation utilities for GAM API parameters.
Dimension and metric definitions are imported from the dimensions_metrics module.
"""

import re
from typing import List, Optional, Set
from datetime import date, datetime

# Import dimension/metric constants from the centralized module
from .dimensions_metrics import (
    ALL_DIMENSIONS,
    ALL_METRICS,
    REACH_METRICS,
    TIME_DIMENSIONS,
    ReportType as DimensionsReportType,
    # Category-based sets for advanced validation
    ADVERTISER_DIMENSIONS,
    AD_UNIT_DIMENSIONS,
    LINE_ITEM_DIMENSIONS,
    ORDER_DIMENSIONS,
    GEOGRAPHIC_DIMENSIONS,
    DEVICE_DIMENSIONS,
    PROGRAMMATIC_DIMENSIONS,
)


# Define local ValidationError for shared package
class ValidationError(Exception):
    """Validation error for shared utilities."""
    def __init__(self, message: str, field: str = None, value=None):
        super().__init__(message)
        self.message = message
        self.field = field
        self.value = value


# Local classes for validators (backwards compatibility)
class ReportType:
    HISTORICAL = "HISTORICAL"
    REACH = "REACH"
    AD_SPEED = "AD_SPEED"


class DateRangeType:
    CUSTOM = "CUSTOM"
    LAST_7_DAYS = "LAST_7_DAYS"
    LAST_30_DAYS = "LAST_30_DAYS"


# Export dimension/metric sets for backwards compatibility
# These now come from dimensions_metrics.py (200+ dimensions, 150+ metrics)
VALID_DIMENSIONS = ALL_DIMENSIONS
VALID_METRICS = ALL_METRICS
REACH_ONLY_METRICS = REACH_METRICS


def validate_dimension(dimension: str) -> bool:
    """
    Validate a single dimension name.
    
    Args:
        dimension: Dimension name to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If dimension is invalid
    """
    if not dimension:
        raise ValidationError("Dimension cannot be empty")
    
    dimension = dimension.upper()
    if dimension not in VALID_DIMENSIONS:
        raise ValidationError(
            f"Invalid dimension: {dimension}",
            field="dimension",
            value=dimension
        )
    
    return True


def validate_metric(metric: str) -> bool:
    """
    Validate a single metric name.
    
    Args:
        metric: Metric name to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If metric is invalid
    """
    if not metric:
        raise ValidationError("Metric cannot be empty")
    
    metric = metric.upper()
    if metric not in VALID_METRICS:
        raise ValidationError(
            f"Invalid metric: {metric}",
            field="metric",
            value=metric
        )
    
    return True


def validate_dimensions_list(dimensions: List[str]) -> List[str]:
    """
    Validate a list of dimensions.
    
    Args:
        dimensions: List of dimension names
        
    Returns:
        Normalized list of dimensions
        
    Raises:
        ValidationError: If any dimension is invalid
    """
    if not dimensions:
        raise ValidationError("At least one dimension is required")
    
    normalized = []
    seen = set()
    
    for dim in dimensions:
        dim_upper = dim.upper()
        
        # Validate dimension
        validate_dimension(dim_upper)
        
        # Check for duplicates
        if dim_upper in seen:
            raise ValidationError(
                f"Duplicate dimension: {dim}",
                field="dimensions",
                value=dim
            )
        
        seen.add(dim_upper)
        normalized.append(dim_upper)
    
    return normalized


def validate_metrics_list(metrics: List[str]) -> List[str]:
    """
    Validate a list of metrics.
    
    Args:
        metrics: List of metric names
        
    Returns:
        Normalized list of metrics
        
    Raises:
        ValidationError: If any metric is invalid
    """
    if not metrics:
        raise ValidationError("At least one metric is required")
    
    normalized = []
    seen = set()
    
    for metric in metrics:
        metric_upper = metric.upper()
        
        # Validate metric
        validate_metric(metric_upper)
        
        # Check for duplicates
        if metric_upper in seen:
            raise ValidationError(
                f"Duplicate metric: {metric}",
                field="metrics",
                value=metric
            )
        
        seen.add(metric_upper)
        normalized.append(metric_upper)
    
    return normalized


def validate_report_type_compatibility(report_type: ReportType, metrics: List[str]) -> bool:
    """
    Validate that metrics are compatible with report type.
    
    Args:
        report_type: Type of report
        metrics: List of metrics
        
    Returns:
        True if compatible
        
    Raises:
        ValidationError: If incompatible
    """
    metrics_set = set(m.upper() for m in metrics)
    
    # Check REACH report compatibility
    if report_type == ReportType.REACH:
        non_reach_metrics = metrics_set - REACH_ONLY_METRICS - VALID_METRICS
        if non_reach_metrics:
            raise ValidationError(
                f"Metrics {non_reach_metrics} are not compatible with REACH reports"
            )
    else:
        # Check that REACH-only metrics aren't used in other reports
        reach_metrics_used = metrics_set & REACH_ONLY_METRICS
        if reach_metrics_used:
            raise ValidationError(
                f"Metrics {reach_metrics_used} can only be used in REACH reports"
            )
    
    return True


def validate_date_range(start_date: Optional[date], end_date: Optional[date]) -> bool:
    """
    Validate date range.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If invalid
    """
    if start_date and end_date:
        if start_date > end_date:
            raise ValidationError(
                "Start date cannot be after end date",
                field="date_range"
            )
        
        # Check not too far in future
        today = date.today()
        if end_date > today:
            raise ValidationError(
                "End date cannot be in the future",
                field="end_date",
                value=end_date
            )
    
    return True


def validate_network_code(network_code: str) -> bool:
    """
    Validate network code format.
    
    Args:
        network_code: Network code to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If invalid
    """
    if not network_code:
        raise ValidationError("Network code cannot be empty")
    
    # Network codes are typically numeric
    if not re.match(r'^\d+$', network_code):
        raise ValidationError(
            f"Invalid network code format: {network_code}",
            field="network_code",
            value=network_code
        )
    
    return True


def validate_currency_code(currency_code: str) -> bool:
    """
    Validate currency code format.
    
    Args:
        currency_code: ISO 4217 currency code
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If invalid
    """
    if not currency_code:
        raise ValidationError("Currency code cannot be empty")
    
    # Should be 3 uppercase letters
    if not re.match(r'^[A-Z]{3}$', currency_code.upper()):
        raise ValidationError(
            f"Invalid currency code format: {currency_code}",
            field="currency_code",
            value=currency_code
        )
    
    return True


def validate_timezone(timezone: str) -> bool:
    """
    Validate timezone format.
    
    Args:
        timezone: IANA timezone name
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If invalid
    """
    if not timezone:
        raise ValidationError("Timezone cannot be empty")
    
    # Basic validation - should contain /
    if '/' not in timezone:
        raise ValidationError(
            f"Invalid timezone format: {timezone}",
            field="timezone",
            value=timezone
        )
    
    return True


# Compatibility functions for fastmcp_server
def validate_dimensions(dimensions):
    """Validate dimensions for compatibility."""
    try:
        validated = validate_dimensions_list(dimensions)
        return type('Result', (), {'is_valid': True, 'errors': []})()
    except ValidationError as e:
        return type('Result', (), {'is_valid': False, 'errors': [str(e)]})()

def validate_metrics(metrics):
    """Validate metrics for compatibility.""" 
    try:
        validated = validate_metrics_list(metrics)
        return type('Result', (), {'is_valid': True, 'errors': []})()
    except ValidationError as e:
        return type('Result', (), {'is_valid': False, 'errors': [str(e)]})()

def validate_report_name(name: str) -> str:
    """
    Validate and sanitize report name.
    
    Args:
        name: Report name
        
    Returns:
        Sanitized name
        
    Raises:
        ValidationError: If invalid
    """
    if not name:
        raise ValidationError("Report name cannot be empty")
    
    # Remove invalid characters
    sanitized = re.sub(r'[^\w\s\-_.]', '', name)
    sanitized = sanitized.strip()
    
    if not sanitized:
        raise ValidationError(
            "Report name contains only invalid characters",
            field="name",
            value=name
        )
    
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    
    return sanitized