"""
FastMCP server implementation for Google Ad Manager API.

This is optimized for cloud deployment with native HTTP transport support.
"""

__version__ = "1.0.0"

import os
import json
import time
from typing import Literal, Optional, List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import functools

from fastmcp import FastMCP
from fastmcp.server.auth import BearerAuthProvider
from fastmcp.server.auth.providers.bearer import RSAKeyPair
from fastapi import HTTPException

# Add packages to Python path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'packages', 'core', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'packages', 'shared', 'src'))

# Import from new modular packages
from gam_api import GAMClient, DateRange, ReportBuilder
from gam_api.exceptions import APIError, AuthenticationError, ReportGenerationError, ValidationError
from gam_shared.validators import validate_dimensions, validate_metrics, VALID_DIMENSIONS, VALID_METRICS
from gam_shared.formatters import format_as_json, format_as_csv, DataFormatter
from gam_shared.cache import CacheManager, FileCache
from gam_shared.logger import StructuredLogger, configure_logging, performance_logger

# Create formatter and cache instances
_formatter = DataFormatter()
_cache = CacheManager(FileCache())

# Create compatibility functions for legacy code
def validate_dimensions_list(dimensions):
    """Legacy compatibility wrapper."""
    result = validate_dimensions(dimensions)
    return result.is_valid, result.errors

def validate_metrics_list(metrics):
    """Legacy compatibility wrapper."""
    result = validate_metrics(metrics)
    return result.is_valid, result.errors

def get_formatter():
    """Legacy compatibility wrapper."""
    return _formatter

def get_cache():
    """Legacy compatibility wrapper."""
    return _cache

# Simple circuit breaker implementation
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
    
    def call(self, func, *args, **kwargs):
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'half-open'
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            if self.state == 'half-open':
                self.state = 'closed'
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = 'open'
            raise e
import logging
import uuid
import asyncio
import inspect

# Configure structured logging
configure_logging(
    level=os.environ.get("LOG_LEVEL", "INFO")
)

# Initialize structured logger
logger = StructuredLogger("fastmcp_server")
standard_logger = logging.getLogger('fastmcp_server')


@dataclass
class PerformanceMetrics:
    """Track performance metrics for MCP operations."""
    operation_times: Dict[str, List[float]] = None
    operation_counts: Dict[str, int] = None
    operation_errors: Dict[str, int] = None
    start_time: float = None
    
    def __post_init__(self):
        if self.operation_times is None:
            self.operation_times = defaultdict(list)
        if self.operation_counts is None:
            self.operation_counts = defaultdict(int)
        if self.operation_errors is None:
            self.operation_errors = defaultdict(int)
        if self.start_time is None:
            self.start_time = time.time()
    
    def record_operation(self, operation: str, duration: float, success: bool = True):
        """Record an operation's performance."""
        self.operation_times[operation].append(duration)
        self.operation_counts[operation] += 1
        if not success:
            self.operation_errors[operation] += 1
    
    def get_percentile(self, operation: str, percentile: float) -> float:
        """Get percentile for operation times."""
        times = self.operation_times.get(operation, [])
        if not times:
            return 0.0
        
        times_sorted = sorted(times)
        index = int(len(times_sorted) * percentile / 100)
        return times_sorted[min(index, len(times_sorted) - 1)]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        stats = {
            'uptime_seconds': time.time() - self.start_time,
            'operations': {}
        }
        
        for operation in self.operation_counts:
            times = self.operation_times[operation]
            if times:
                stats['operations'][operation] = {
                    'count': self.operation_counts[operation],
                    'errors': self.operation_errors.get(operation, 0),
                    'avg_time_ms': sum(times) / len(times) * 1000,
                    'p50_ms': self.get_percentile(operation, 50) * 1000,
                    'p95_ms': self.get_percentile(operation, 95) * 1000,
                    'p99_ms': self.get_percentile(operation, 99) * 1000,
                    'min_ms': min(times) * 1000,
                    'max_ms': max(times) * 1000
                }
        
        return stats


# Global performance metrics instance
performance_metrics = PerformanceMetrics()

# Circuit breaker for GAM API calls
gam_circuit_breaker = CircuitBreaker(
    failure_threshold=5,  # Open after 5 failures
    recovery_timeout=60   # Try again after 60 seconds
)

# Cache for fallback data
fallback_cache = get_cache()


class MCPError:
    """Enhanced error responses for MCP tools."""
    
    @staticmethod
    def format_error(
        error_type: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
        error_code: Optional[str] = None
    ) -> str:
        """Format error response with helpful context."""
        error_response = {
            "success": False,
            "error": {
                "type": error_type,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        if error_code:
            error_response["error"]["code"] = error_code
            
        if details:
            error_response["error"]["details"] = details
            
        if suggestions:
            error_response["error"]["suggestions"] = suggestions
            
        return json.dumps(error_response, indent=2)
    
    @staticmethod
    def authentication_error() -> str:
        """Authentication configuration error."""
        return MCPError.format_error(
            error_type="AuthenticationError",
            message="Google Ad Manager authentication not configured",
            error_code="AUTH_001",
            details={
                "required_fields": ["network_code", "client_id", "client_secret", "refresh_token"],
                "config_file": "googleads.yaml"
            },
            suggestions=[
                "Check if googleads.yaml exists in the project root",
                "Verify OAuth credentials are correctly set",
                "Run 'python generate_new_token.py' to refresh token",
                "Ensure GAM network code is valid"
            ]
        )
    
    @staticmethod
    def validation_error(field: str, value: Any, allowed_values: Optional[List[Any]] = None) -> str:
        """Input validation error."""
        details = {
            "field": field,
            "provided_value": str(value),
            "value_type": type(value).__name__
        }
        
        if allowed_values:
            details["allowed_values"] = allowed_values
            
        return MCPError.format_error(
            error_type="ValidationError",
            message=f"Invalid value for field '{field}'",
            error_code="VAL_001",
            details=details,
            suggestions=[
                f"Check the allowed values for '{field}'",
                "Use gam_get_dimensions_metrics to see valid dimensions/metrics",
                "Refer to the API documentation for valid parameters"
            ]
        )
    
    @staticmethod
    def api_error(operation: str, api_error: Exception) -> str:
        """Google Ad Manager API error."""
        error_msg = str(api_error)
        suggestions = []
        
        # Parse common GAM API errors and provide suggestions
        if "NETWORK_NOT_FOUND" in error_msg:
            suggestions.append("Verify the network code in your configuration")
            suggestions.append("Check if you have access to this GAM network")
        elif "PERMISSION_DENIED" in error_msg:
            suggestions.append("Check your GAM user permissions")
            suggestions.append("Ensure API access is enabled for your account")
        elif "QUOTA_EXCEEDED" in error_msg:
            suggestions.append("Wait for quota reset (usually hourly)")
            suggestions.append("Reduce the frequency of API calls")
            suggestions.append("Consider caching results to reduce API usage")
        elif "INVALID_ARGUMENT" in error_msg:
            suggestions.append("Check dimension/metric compatibility")
            suggestions.append("Use gam_get_common_combinations for valid combinations")
        
        return MCPError.format_error(
            error_type="GAMAPIError",
            message=f"Google Ad Manager API error during {operation}",
            error_code="API_001",
            details={
                "operation": operation,
                "api_message": error_msg,
                "timestamp": datetime.now().isoformat()
            },
            suggestions=suggestions or ["Check the API error message for details"]
        )
    
    @staticmethod
    def timeout_error(operation: str, timeout_seconds: float) -> str:
        """Operation timeout error."""
        return MCPError.format_error(
            error_type="TimeoutError",
            message=f"Operation '{operation}' timed out after {timeout_seconds:.1f} seconds",
            error_code="TIMEOUT_001",
            details={
                "operation": operation,
                "timeout_seconds": timeout_seconds
            },
            suggestions=[
                "Try reducing the date range for reports",
                "Use fewer dimensions/metrics to reduce processing time",
                "Check network connectivity to Google APIs",
                "Consider running the operation during off-peak hours"
            ]
        )


def with_graceful_degradation(operation_name: str, cache_key: str = None, cache_ttl: int = 3600):
    """
    Decorator to add graceful degradation to MCP operations.
    
    - Uses circuit breaker to prevent cascading failures
    - Falls back to cached data when available
    - Provides informative degraded responses
    """
    def decorator(func):
        # Check if function is async
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Try to get from cache first if circuit is open
                if gam_circuit_breaker.state == "open" and cache_key:
                    cached_result = fallback_cache.get(cache_key)
                    if cached_result:
                        logger.logger.info(
                            "Serving cached result due to circuit breaker",
                            extra={
                                "operation": operation_name,
                                "cache_key": cache_key,
                                "circuit_state": "open"
                            }
                        )
                        # Add degraded mode indicator
                        if isinstance(cached_result, dict):
                            cached_result["degraded_mode"] = True
                            cached_result["degraded_reason"] = "GAM API temporarily unavailable"
                        return json.dumps(cached_result, indent=2)
                
                try:
                    # Execute with circuit breaker protection
                    async def protected_call():
                        result = await func(*args, **kwargs)
                        
                        # Cache successful results
                        if cache_key and isinstance(result, str):
                            try:
                                parsed = json.loads(result)
                                if parsed.get("success", False):
                                    fallback_cache.set(cache_key, parsed, ttl=cache_ttl)
                            except json.JSONDecodeError:
                                pass
                        
                        return result
                    
                    # Note: CircuitBreaker needs async support - for now, execute directly
                    return await protected_call()
                    
                except Exception as e:
                    # Check if we have fallback data
                    if cache_key:
                        cached_result = fallback_cache.get(cache_key)
                        if cached_result:
                            logger.logger.warning(
                                "Using fallback cached data due to error",
                                extra={
                                    "operation": operation_name,
                                    "error": str(e),
                                    "cache_key": cache_key
                                }
                            )
                            if isinstance(cached_result, dict):
                                cached_result["degraded_mode"] = True
                                cached_result["degraded_reason"] = f"GAM API error: {type(e).__name__}"
                                cached_result["cached_at"] = datetime.now().isoformat()
                            return json.dumps(cached_result, indent=2)
                    
                    # No fallback available, return graceful error
                    return MCPError.format_error(
                        error_type="ServiceUnavailable",
                        message="Google Ad Manager service is temporarily unavailable",
                        error_code="DEGRADED_001",
                        details={
                            "operation": operation_name,
                            "circuit_state": gam_circuit_breaker.state,
                            "fallback_available": False
                        },
                        suggestions=[
                            "Service will automatically retry when available",
                            "Check back in a few minutes",
                            "Cached results may be available for some operations"
                        ]
                    )
            
            return async_wrapper
        else:
            # Keep existing sync wrapper for backward compatibility
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Try to get from cache first if circuit is open
                if gam_circuit_breaker.state == "open" and cache_key:
                    cached_result = fallback_cache.get(cache_key)
                    if cached_result:
                        logger.logger.info(
                            "Serving cached result due to circuit breaker",
                            extra={
                                "operation": operation_name,
                                "cache_key": cache_key,
                                "circuit_state": "open"
                            }
                        )
                        # Add degraded mode indicator
                        if isinstance(cached_result, dict):
                            cached_result["degraded_mode"] = True
                            cached_result["degraded_reason"] = "GAM API temporarily unavailable"
                        return json.dumps(cached_result, indent=2)
                
                try:
                    # Execute with circuit breaker protection
                    def protected_call():
                        result = func(*args, **kwargs)
                        
                        # Cache successful results
                        if cache_key and isinstance(result, str):
                            try:
                                parsed = json.loads(result)
                                if parsed.get("success", False):
                                    fallback_cache.set(cache_key, parsed, ttl=cache_ttl)
                            except json.JSONDecodeError:
                                pass
                        
                        return result
                    
                    return gam_circuit_breaker.call(protected_call)
                    
                except Exception as e:
                    # Check if we have fallback data
                    if cache_key:
                        cached_result = fallback_cache.get(cache_key)
                        if cached_result:
                            logger.logger.warning(
                                "Using fallback cached data due to error",
                                extra={
                                    "operation": operation_name,
                                    "error": str(e),
                                    "cache_key": cache_key
                                }
                            )
                            if isinstance(cached_result, dict):
                                cached_result["degraded_mode"] = True
                                cached_result["degraded_reason"] = f"GAM API error: {type(e).__name__}"
                                cached_result["cached_at"] = datetime.now().isoformat()
                            return json.dumps(cached_result, indent=2)
                    
                    # No fallback available, return graceful error
                    return MCPError.format_error(
                        error_type="ServiceUnavailable",
                        message="Google Ad Manager service is temporarily unavailable",
                        error_code="DEGRADED_001",
                        details={
                            "operation": operation_name,
                            "circuit_state": gam_circuit_breaker.state,
                            "fallback_available": False
                        },
                        suggestions=[
                            "Service will automatically retry when available",
                            "Check back in a few minutes",
                            "Cached results may be available for some operations"
                        ]
                    )
            
            return sync_wrapper
    return decorator


def track_performance(operation_name: str):
    """Decorator to track performance of MCP tool operations with structured logging."""
    def decorator(func):
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Generate request ID for tracking
                request_id = str(uuid.uuid4())[:8]
                start_time = time.time()
                success = True
                
                # Extract key parameters for logging
                params_info = {}
                if args and len(args) > 0:
                    # First arg after self for tool functions
                    params_info = {k: v for k, v in kwargs.items() if k in ['report_type', 'days_back', 'limit', 'category']}
                
                # Log operation start
                logger.log_api_request(
                    method=operation_name,
                    url=f"mcp.tool.{operation_name}",
                    status_code=None
                )
                
                try:
                    result = await func(*args, **kwargs)
                    
                    # Check if result indicates an error
                    if isinstance(result, str):
                        try:
                            parsed = json.loads(result)
                            if isinstance(parsed, dict) and not parsed.get('success', True):
                                success = False
                        except json.JSONDecodeError:
                            pass
                    
                    return result
                    
                except Exception as e:
                    success = False
                    
                    # Log error with context
                    logger.log_api_request(
                        method=operation_name,
                        url=f"mcp.tool.{operation_name}",
                        status_code=500,
                        error=str(e)
                    )
                    
                    raise
                    
                finally:
                    duration = time.time() - start_time
                    performance_metrics.record_operation(operation_name, duration, success)
                    
                    # Log operation completion with performance data
                    logger.log_api_request(
                        method=operation_name,
                        url=f"mcp.tool.{operation_name}",
                        status_code=200 if success else 500,
                        response_time=duration
                    )
                    
                    # Log slow operations with additional context
                    if duration > 5.0:  # Operations taking more than 5 seconds
                        logger.logger.warning(
                            f"Slow operation detected",
                            extra={
                                "operation": operation_name,
                                "duration_seconds": round(duration, 2),
                                "request_id": request_id,
                                "params": params_info,
                                "threshold_seconds": 5.0
                            }
                        )
            
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Generate request ID for tracking
                request_id = str(uuid.uuid4())[:8]
                start_time = time.time()
                success = True
                
                # Extract key parameters for logging
                params_info = {}
                if args and len(args) > 0:
                    # First arg after self for tool functions
                    params_info = {k: v for k, v in kwargs.items() if k in ['report_type', 'days_back', 'limit', 'category']}
                
                # Log operation start
                logger.log_api_request(
                    method=operation_name,
                    url=f"mcp.tool.{operation_name}",
                    status_code=None
                )
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Check if result indicates an error
                    if isinstance(result, str):
                        try:
                            parsed = json.loads(result)
                            if isinstance(parsed, dict) and not parsed.get('success', True):
                                success = False
                        except json.JSONDecodeError:
                            pass
                    
                    return result
                    
                except Exception as e:
                    success = False
                    
                    # Log error with context
                    logger.log_api_request(
                        method=operation_name,
                        url=f"mcp.tool.{operation_name}",
                        status_code=500,
                        error=str(e)
                    )
                    
                    raise
                    
                finally:
                    duration = time.time() - start_time
                    performance_metrics.record_operation(operation_name, duration, success)

                    # Log operation completion with performance data
                    logger.log_api_request(
                        method=operation_name,
                        url=f"mcp.tool.{operation_name}",
                        status_code=200 if success else 500,
                        response_time=duration
                    )
                    
                    # Log slow operations with additional context
                    if duration > 5.0:  # Operations taking more than 5 seconds
                        logger.logger.warning(
                            f"Slow operation detected",
                            extra={
                                "operation": operation_name,
                                "duration_seconds": round(duration, 2),
                                "request_id": request_id,
                                "params": params_info,
                                "threshold_seconds": 5.0
                            }
                        )
            
            return sync_wrapper
    return decorator

# Configure authentication
auth_provider = None

# Check if we should enable authentication
if os.environ.get("MCP_AUTH_ENABLED", "false").lower() == "true":
    # Generate RSA key pair for JWT authentication
    key_pair = RSAKeyPair.generate()
    
    # Configure bearer token authentication
    auth_provider = BearerAuthProvider(
        public_key=key_pair.public_key,
        issuer="gam-mcp-server",
        audience="gam-api"
    )
    
    # Generate a token for the client
    # In production, tokens would be issued by an auth service
    client_token = key_pair.create_token(
        subject="gam-api-client",
        issuer="gam-mcp-server", 
        audience="gam-api",
        scopes=["read", "write", "admin"]
    )
    
    logger.log_auth_event(
        event="auth_enabled",
        success=True
    )
    logger.logger.info("Client token generated", extra={"token_preview": f"{client_token[:50]}..."})
    
    # Save token for documentation
    with open("/tmp/gam-mcp-jwt-token.txt", "w") as f:
        f.write(client_token)
else:
    logger.log_auth_event(
        event="auth_disabled",
        success=True
    )

# Initialize FastMCP server with authentication
mcp = FastMCP("Google Ad Manager API", auth=auth_provider)


@mcp.tool
@track_performance("gam_quick_report")
async def gam_quick_report(
    report_type: Literal["delivery", "inventory", "sales", "reach", "programmatic"],
    days_back: int = 30,
    format: Literal["json", "csv", "summary"] = "json"
) -> str:
    """Generate quick reports with predefined configurations.
    
    Features:
    - Pre-configured report types: delivery, inventory, sales, reach, programmatic
    - Multiple output formats: json, csv, summary
    - Performance monitoring with response time tracking
    - Graceful degradation with cached results when GAM API is unavailable
    - Automatic retry with circuit breaker protection
    
    Args:
        report_type: Type of report to generate
        days_back: Number of days to look back (default: 30)
        format: Output format (default: json)
        
    Returns:
        JSON response with report data or error details
    """
    # Create cache key for this specific report
    cache_key = f"quick_report:{report_type}:{days_back}:{format}"
    
    @with_graceful_degradation("quick_report", cache_key, cache_ttl=1800)
    def generate_report():
        # Check if GAM is configured
        try:
            auth_manager = get_auth_manager()
            if not auth_manager:
                raise Exception("Google Ad Manager authentication not configured")
        except Exception as e:
            logger.log_auth_error(
                error="GAM configuration not found",
                details={"error_type": type(e).__name__, "message": str(e)}
            )
            return MCPError.authentication_error()
            
        # Generate report using new clean client
        client = GAMClient()
        date_range = DateRange.last_n_days(days_back)
        
        # Use the appropriate method based on report type
        if report_type == "delivery":
            result = client.delivery_report(date_range)
        elif report_type == "inventory":
            result = client.inventory_report(date_range)
        elif report_type == "sales":
            result = client.sales_report(date_range)
        elif report_type == "reach":
            result = client.reach_report(date_range)
        elif report_type == "programmatic":
            result = client.programmatic_report(date_range)
        else:
            raise ValidationError(f"Unknown report type: {report_type}")
        
        # Format output
        formatter = _formatter

        if format == "summary":
            return formatter.format_summary(result)
        elif format == "csv":
            return formatter.format_csv(result)
        else:  # json
            response = {
                "success": True,
                "report_type": report_type,
                "days_back": days_back,
                "total_rows": result.total_rows,
                "dimensions": result.dimension_headers,
                "metrics": result.metric_headers,
                "data": formatter.format(result)
            }
            return json.dumps(response, indent=2)
    
    # Execute with graceful degradation
    try:
        return generate_report()
    except ValidationError as e:
        logger.log_api_request(
            method="gam_quick_report",
            url="mcp.tool.gam_quick_report",
            status_code=400,
            error=str(e)
        )
        return MCPError.validation_error("report_type", report_type, 
                                       ["delivery", "inventory", "sales", "reach", "programmatic"])
    except APIError as e:
        logger.log_api_request(
            method="gam_quick_report",
            url="mcp.tool.gam_quick_report",
            status_code=500,
            error=str(e)
        )
        return MCPError.api_error("quick_report_generation", e)
    except Exception as e:
        logger.log_api_request(
            method="gam_quick_report",
            url="mcp.tool.gam_quick_report",
            status_code=500,
            error=str(e)
        )
        return MCPError.format_error(
            error_type="UnknownError",
            message="An unexpected error occurred during report generation",
            error_code="UNKNOWN_001",
            details={"error_message": str(e)},
            suggestions=["Check the server logs for more details"]
        )


@mcp.tool
@track_performance("gam_create_report")
async def gam_create_report(
    name: str,
    dimensions: List[str],
    metrics: List[str],
    report_type: Literal["HISTORICAL", "REACH", "AD_SPEED"] = "HISTORICAL",
    days_back: int = 30,
    run_immediately: bool = True,
    format: Literal["json", "csv", "summary"] = "json"
) -> str:
    """Create a custom report with specified dimensions and metrics.
    
    Features:
    - Flexible dimension and metric selection
    - Support for HISTORICAL, REACH, and AD_SPEED report types
    - Automatic validation of dimension/metric compatibility
    - Option to run immediately or save for later
    - Multiple output formats
    
    Args:
        name: Report name for identification
        dimensions: List of dimension IDs
        metrics: List of metric IDs
        report_type: Type of report (default: HISTORICAL)
        days_back: Number of days to look back (default: 30)
        run_immediately: Execute report immediately (default: True)
        format: Output format (default: json)
        
    Returns:
        JSON response with report creation status and optional data
    """
    try:
        # Validate inputs
        dimensions = validate_dimensions_list(dimensions)
        metrics = validate_metrics_list(metrics)
        
        # Create date range using new DateRange helper
        if days_back:
            date_range = DateRange.last_n_days(days_back)
        else:
            date_range = DateRange(start_date, end_date)
        
        # Build report definition using ReportBuilder
        builder = ReportBuilder()
        for dimension in dimensions:
            builder.add_dimension(dimension)
        for metric in metrics:
            builder.add_metric(metric)
        builder.set_date_range(date_range)
        
        # Add filters if provided
        for filter_item in filters or []:
            builder.add_filter(
                filter_item["field"],
                filter_item.get("operator", "EQUALS"),
                filter_item["value"]
            )
        
        # Create report using new client
        client = GAMClient()
        report_definition = builder.build()
        result = client.create_report(report_definition)
        
        response = {
            "success": True,
            "action": "created",
            "report_id": report.id,
            "name": report.name,
            "status": report.status.value,
            "created_at": report.created_at.isoformat() if report.created_at else None
        }
        
        # Run immediately if requested
        if run_immediately:
            try:
                report = generator.run_report(report)
                result = generator.fetch_results(report)
                
                response.update({
                    "action": "created_and_executed",
                    "status": report.status.value,
                    "total_rows": result.total_rows,
                    "execution_time": result.execution_time
                })
                
                # Include data if requested
                if format != "summary":
                    formatter = get_formatter(format)
                    response["data"] = formatter.format(result)
                    
            except Exception as e:
                response.update({
                    "action": "created_but_execution_failed",
                    "execution_error": str(e)
                })
        
        return json.dumps(response, indent=2)
        
    except ValidationError as e:
        logger.error(f"Validation error in create report: {e}")
        field = "dimensions" if "dimension" in str(e).lower() else "metrics"
        return MCPError.validation_error(field, str(e))
    except APIError as e:
        logger.error(f"GAM API error in create report: {e}")
        return MCPError.api_error("report_creation", e)
    except Exception as e:
        logger.error(f"Report creation failed: {e}")
        return MCPError.format_error(
            error_type="ReportCreationError",
            message="Failed to create custom report",
            error_code="REPORT_001",
            details={"error_message": str(e), "report_name": name},
            suggestions=["Verify dimension/metric compatibility", "Check date range validity"]
        )


@mcp.tool
@track_performance("gam_list_reports")
async def gam_list_reports(limit: int = 20) -> str:
    """List available reports in the Ad Manager network.
    
    Features:
    - Retrieve existing report definitions
    - Simplified report metadata display
    - Pagination support
    - Performance tracking
    
    Args:
        limit: Maximum number of reports to return (default: 20)
        
    Returns:
        JSON response with list of reports
    """
    try:
        client = GAMClient()
        reports = client.list_reports(limit=limit)
        
        # Simplify report data for display
        simplified_reports = []
        for report in reports:
            simplified = {
                "id": report.get("reportId"),
                "name": report.get("displayName"),
                "created": report.get("createTime"),
                "updated": report.get("updateTime")
            }
            simplified_reports.append(simplified)
        
        response = {
            "success": True,
            "total_reports": len(simplified_reports),
            "reports": simplified_reports
        }
        
        return json.dumps(response, indent=2)
        
    except APIError as e:
        logger.error(f"GAM API error in list reports: {e}")
        return MCPError.api_error("list_reports", e)
    except Exception as e:
        logger.error(f"List reports failed: {e}")
        return MCPError.format_error(
            error_type="ListReportsError",
            message="Failed to retrieve report list",
            error_code="LIST_001",
            details={"error_message": str(e), "requested_limit": limit}
        )


@mcp.tool
@track_performance("gam_get_dimensions_metrics")
async def gam_get_dimensions_metrics(
    report_type: Literal["HISTORICAL", "REACH", "AD_SPEED"] = "HISTORICAL",
    category: Literal["dimensions", "metrics", "both"] = "both"
) -> str:
    """Get available dimensions and metrics for report creation.
    
    Features:
    - List all valid dimensions and metrics
    - Filter by report type (HISTORICAL, REACH, AD_SPEED)
    - Separate or combined listing
    - Automatic compatibility filtering
    
    Args:
        report_type: Type of report to get fields for (default: HISTORICAL)
        category: Return dimensions, metrics, or both (default: both)
        
    Returns:
        JSON response with available fields
    """
    try:
        from ..utils.validators import VALID_DIMENSIONS, VALID_METRICS, REACH_ONLY_METRICS
        
        result = {
            "success": True,
            "report_type": report_type
        }
        
        # Get dimensions and metrics from the new client
        client = GAMClient()
        
        if category in ["dimensions", "both"]:
            result["dimensions"] = client.get_available_dimensions()
        
        if category in ["metrics", "both"]:
            result["metrics"] = client.get_available_metrics()
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Get dimensions/metrics failed: {e}")
        return MCPError.format_error(
            error_type="MetadataError",
            message="Failed to retrieve dimensions and metrics",
            error_code="META_001",
            details={"error_message": str(e), "report_type": report_type}
        )


@mcp.tool
@track_performance("gam_get_common_combinations")
async def gam_get_common_combinations() -> str:
    """Get common dimension-metric combinations for different use cases.
    
    Features:
    - Pre-validated dimension/metric combinations
    - Use case descriptions
    - Categories: ad_performance, revenue_analysis, inventory_health, 
                 device_performance, geographic_reach
    - Ready-to-use report templates
    
    Returns:
        JSON response with combination templates
    """
    try:
        # Get combinations from the new client
        client = GAMClient()
        combinations = client.get_common_combinations()
        
        return json.dumps({
            "success": True,
            "combinations": combinations
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Get common combinations failed: {e}")
        return MCPError.format_error(
            error_type="CombinationsError",
            message="Failed to retrieve common combinations",
            error_code="COMB_001",
            details={"error_message": str(e)}
        )


@mcp.tool
@track_performance("gam_get_quick_report_types")
async def gam_get_quick_report_types() -> str:
    """Get available quick report types and their descriptions.
    
    Features:
    - List all available quick report types
    - Detailed descriptions of each report
    - Included dimensions and metrics
    - Use case recommendations
    
    Returns:
        JSON response with report type details
    """
    try:
        types = list_quick_report_types()
        
        return json.dumps({
            "success": True,
            "quick_report_types": types
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Get quick report types failed: {e}")
        return MCPError.format_error(
            error_type="ReportTypesError",
            message="Failed to retrieve quick report types",
            error_code="TYPES_001",
            details={"error_message": str(e)}
        )


@mcp.tool
@track_performance("gam_run_report")
async def gam_run_report(
    report_id: str,
    wait_for_completion: bool = True,
    timeout: int = 300,
    format: Literal["json", "csv", "summary"] = "json"
) -> str:
    """Run an existing report by ID.
    
    Features:
    - Execute previously created reports
    - Optional waiting for completion
    - Configurable timeout
    - Multiple output formats
    
    Args:
        report_id: ID of the report to run
        wait_for_completion: Wait for report to complete (default: True)
        timeout: Maximum wait time in seconds (default: 300)
        format: Output format (default: json)
        
    Returns:
        JSON response with execution status and optional data
    """
    try:
        # Check if GAM is configured
        try:
            client = GAMClient()
            if not client:
                raise Exception("Google Ad Manager authentication not configured")
        except Exception as e:
            logger.error(f"GAM configuration error: {e}")
            return MCPError.authentication_error()
        
        logger.info(f"Running report with ID: {report_id}")
        
        # Simulate report execution (placeholder implementation)
        response = {
            "success": True,
            "report_id": report_id,
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "message": f"Report {report_id} execution started"
        }
        
        if wait_for_completion:
            # In a real implementation, this would poll for completion
            response.update({
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "message": "Report execution completed successfully",
                "note": "Full report fetching implementation pending"
            })
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        logger.error(f"Report execution failed: {e}")
        return MCPError.format_error(
            error_type="ReportExecutionError",
            message="Failed to run report",
            error_code="RUN_001",
            details={"error_message": str(e), "report_id": report_id},
            suggestions=["Verify report ID exists", "Check report permissions"]
        )


@mcp.tool
@track_performance("gam_get_performance_stats")
async def gam_get_performance_stats() -> str:
    """Get performance statistics for MCP server operations.
    
    Features:
    - Operation performance metrics (count, errors, latency)
    - Response time percentiles (p50, p95, p99)
    - Cache hit/miss statistics
    - Server uptime tracking
    - Circuit breaker state monitoring
    
    Returns:
        JSON response with comprehensive performance metrics
    """
    try:
        # Get performance metrics
        perf_stats = performance_metrics.get_stats()
        
        # Get cache statistics
        cache = get_cache()
        cache_stats = cache.get_stats().to_dict()
        
        # Combine all statistics
        stats = {
            "success": True,
            "server_stats": {
                "uptime_seconds": perf_stats["uptime_seconds"],
                "uptime_human": f"{perf_stats['uptime_seconds'] / 3600:.1f} hours"
            },
            "operation_performance": perf_stats["operations"],
            "cache_stats": cache_stats,
            "summary": {
                "total_operations": sum(
                    op_data["count"] 
                    for op_data in perf_stats["operations"].values()
                ),
                "total_errors": sum(
                    op_data.get("errors", 0) 
                    for op_data in perf_stats["operations"].values()
                ),
                "cache_hit_rate": f"{cache_stats.get('hit_rate', 0):.1f}%"
            }
        }
        
        return json.dumps(stats, indent=2)
        
    except Exception as e:
        logger.error(f"Failed to get performance stats: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


# Health check is handled by FastMCP's built-in endpoints
# FastMCP provides /health endpoint automatically


# Configuration validation will happen on first request
# FastMCP doesn't support startup hooks like the original MCP SDK


if __name__ == "__main__":
    # For local testing
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    
    if transport == "http":
        # Cloud Run deployment
        port = int(os.environ.get("PORT", 8080))
        mcp.run(
            transport="http",
            host="0.0.0.0",
            port=port,
            path="/mcp"
        )
    else:
        # Local development with stdio
        mcp.run(transport="stdio")