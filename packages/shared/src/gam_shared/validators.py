"""
Validators for Google Ad Manager API inputs.
"""

import re
from typing import List, Optional, Set
from datetime import date, datetime

# Define local ValidationError for shared package
class ValidationError(Exception):
    """Validation error for shared utilities."""
    def __init__(self, message: str, field: str = None, value=None):
        super().__init__(message)
        self.message = message
        self.field = field
        self.value = value

# Local classes for validators
class ReportType:
    HISTORICAL = "HISTORICAL"
    REACH = "REACH"
    AD_SPEED = "AD_SPEED"

class DateRangeType:
    CUSTOM = "CUSTOM"
    LAST_7_DAYS = "LAST_7_DAYS"
    LAST_30_DAYS = "LAST_30_DAYS"


# Common dimensions and metrics (subset for validation)
VALID_DIMENSIONS = {
    # Time dimensions
    "DATE", "WEEK", "MONTH", "YEAR",
    
    # Inventory dimensions
    "AD_UNIT_ID", "AD_UNIT_NAME", "AD_UNIT_CODE",
    
    # Order/Line item dimensions
    "ORDER_ID", "ORDER_NAME", "LINE_ITEM_ID", "LINE_ITEM_NAME",
    
    # Advertiser dimensions
    "ADVERTISER_ID", "ADVERTISER_NAME", "ADVERTISER_LABELS",
    
    # Geographic dimensions
    "COUNTRY_CODE", "COUNTRY_NAME", "REGION_CODE", "REGION_NAME",
    "CITY_NAME", "METRO_CODE", "METRO_NAME", "POSTAL_CODE",
    
    # Device dimensions
    "DEVICE_CATEGORY_NAME", "DEVICE_NAME", "BROWSER_NAME",
    "BROWSER_VERSION", "OPERATING_SYSTEM_NAME", "OPERATING_SYSTEM_VERSION",
    
    # Creative dimensions
    "CREATIVE_ID", "CREATIVE_NAME", "CREATIVE_SIZE", "CREATIVE_TYPE",
    
    # Programmatic dimensions
    "PROGRAMMATIC_CHANNEL_NAME", "PROGRAMMATIC_BUYER_NAME",
    
    # Other dimensions
    "CUSTOM_TARGETING_VALUE_ID", "PLACEMENT_NAME", "CONTENT_NAME",
    "REQUEST_TYPE", "AD_EXCHANGE_NAME"
}

VALID_METRICS = {
    # Impression metrics
    "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS",
    "TOTAL_LINE_ITEM_LEVEL_TARGETED_IMPRESSIONS",
    "TOTAL_IMPRESSIONS",
    
    # Click metrics
    "TOTAL_LINE_ITEM_LEVEL_CLICKS",
    "TOTAL_LINE_ITEM_LEVEL_TARGETED_CLICKS",
    "TOTAL_CLICKS",
    
    # CTR metrics
    "TOTAL_LINE_ITEM_LEVEL_CTR",
    "TOTAL_CTR",
    
    # Revenue metrics
    "TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE",
    "TOTAL_LINE_ITEM_LEVEL_ALL_REVENUE",
    "TOTAL_AD_EXCHANGE_LINE_ITEM_LEVEL_REVENUE",
    
    # CPM/eCPM metrics
    "TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM",
    "TOTAL_LINE_ITEM_LEVEL_WITH_CPD_AVERAGE_ECPM",
    
    # Request and fill metrics
    "TOTAL_AD_REQUESTS",
    "TOTAL_CODE_SERVED_COUNT",
    "TOTAL_FILL_RATE",
    "TOTAL_MATCH_RATE",
    
    # Programmatic metrics
    "PROGRAMMATIC_MATCH_RATE",
    "PROGRAMMATIC_AVAILABLE_IMPRESSIONS",
    "PROGRAMMATIC_REVENUE",
    
    # Reach metrics (for REACH reports)
    "UNIQUE_REACH_IMPRESSIONS",
    "UNIQUE_REACH_FREQUENCY",
    "UNIQUE_REACH"
}

# Dimension/metric compatibility rules
REACH_ONLY_METRICS = {
    "UNIQUE_REACH_IMPRESSIONS",
    "UNIQUE_REACH_FREQUENCY", 
    "UNIQUE_REACH"
}

TIME_DIMENSIONS = {"DATE", "WEEK", "MONTH", "YEAR"}


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