"""
SDK-specific exceptions for the Google Ad Manager API SDK.

Provides clean, specific exceptions for different SDK operations
with helpful error messages and optional error codes.
"""

from typing import Optional, Any, Dict


class SDKError(Exception):
    """Base exception for all SDK operations."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        Initialize SDK error.
        
        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self) -> str:
        """Return formatted error message."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ReportError(SDKError):
    """Exception for report generation and management operations."""
    
    def __init__(self, message: str, report_id: Optional[str] = None, **kwargs):
        """
        Initialize report error.
        
        Args:
            message: Error message
            report_id: Optional report ID for context
            **kwargs: Additional arguments passed to SDKError
        """
        super().__init__(message, **kwargs)
        self.report_id = report_id


class ConfigError(SDKError):
    """Exception for configuration management operations."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            config_key: Optional configuration key for context
            **kwargs: Additional arguments passed to SDKError
        """
        super().__init__(message, **kwargs)
        self.config_key = config_key


class AuthError(SDKError):
    """Exception for authentication operations."""
    
    def __init__(self, message: str, auth_step: Optional[str] = None, **kwargs):
        """
        Initialize authentication error.
        
        Args:
            message: Error message
            auth_step: Optional authentication step for context
            **kwargs: Additional arguments passed to SDKError
        """
        super().__init__(message, **kwargs)
        self.auth_step = auth_step


class ValidationError(SDKError):
    """Exception for input validation errors."""
    
    def __init__(self, message: str, field_name: Optional[str] = None, field_value: Optional[Any] = None, **kwargs):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            field_name: Optional field name that failed validation
            field_value: Optional field value that failed validation
            **kwargs: Additional arguments passed to SDKError
        """
        super().__init__(message, **kwargs)
        self.field_name = field_name
        self.field_value = field_value


class NetworkError(SDKError):
    """Exception for network and API communication errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[str] = None, **kwargs):
        """
        Initialize network error.
        
        Args:
            message: Error message
            status_code: Optional HTTP status code
            response_body: Optional response body for debugging
            **kwargs: Additional arguments passed to SDKError
        """
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.response_body = response_body


class TimeoutError(SDKError):
    """Exception for operation timeout errors."""
    
    def __init__(self, message: str, timeout_seconds: Optional[float] = None, operation: Optional[str] = None, **kwargs):
        """
        Initialize timeout error.
        
        Args:
            message: Error message
            timeout_seconds: Optional timeout duration
            operation: Optional operation that timed out
            **kwargs: Additional arguments passed to SDKError
        """
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds
        self.operation = operation


class RateLimitError(SDKError):
    """Exception for API rate limit errors."""
    
    def __init__(self, message: str, retry_after: Optional[float] = None, **kwargs):
        """
        Initialize rate limit error.
        
        Args:
            message: Error message
            retry_after: Optional seconds to wait before retrying
            **kwargs: Additional arguments passed to SDKError
        """
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class QuotaExceededError(SDKError):
    """Exception for API quota exceeded errors."""
    
    def __init__(self, message: str, quota_type: Optional[str] = None, reset_time: Optional[str] = None, **kwargs):
        """
        Initialize quota exceeded error.
        
        Args:
            message: Error message
            quota_type: Optional type of quota exceeded
            reset_time: Optional quota reset time
            **kwargs: Additional arguments passed to SDKError
        """
        super().__init__(message, **kwargs)
        self.quota_type = quota_type
        self.reset_time = reset_time


class PermissionError(SDKError):
    """Exception for insufficient permissions errors."""
    
    def __init__(self, message: str, required_permission: Optional[str] = None, **kwargs):
        """
        Initialize permission error.
        
        Args:
            message: Error message
            required_permission: Optional required permission
            **kwargs: Additional arguments passed to SDKError
        """
        super().__init__(message, **kwargs)
        self.required_permission = required_permission


# Error mapping for common scenarios
ERROR_CODE_MAP = {
    'INVALID_CREDENTIALS': AuthError,
    'TOKEN_EXPIRED': AuthError,
    'NETWORK_CODE_INVALID': ConfigError,
    'REPORT_NOT_FOUND': ReportError,
    'REPORT_GENERATION_FAILED': ReportError,
    'INVALID_DIMENSIONS': ValidationError,
    'INVALID_METRICS': ValidationError,
    'RATE_LIMIT_EXCEEDED': RateLimitError,
    'QUOTA_EXCEEDED': QuotaExceededError,
    'INSUFFICIENT_PERMISSIONS': PermissionError,
    'REQUEST_TIMEOUT': TimeoutError,
    'NETWORK_ERROR': NetworkError,
}


def create_error_from_code(error_code: str, message: str, **kwargs) -> SDKError:
    """
    Create appropriate exception instance based on error code.
    
    Args:
        error_code: Error code to map
        message: Error message
        **kwargs: Additional arguments for the exception
        
    Returns:
        Appropriate exception instance
    """
    error_class = ERROR_CODE_MAP.get(error_code, SDKError)
    return error_class(message, error_code=error_code, **kwargs)


def handle_api_error(response_data: Dict[str, Any]) -> SDKError:
    """
    Handle API error response and create appropriate exception.
    
    Args:
        response_data: API error response data
        
    Returns:
        Appropriate exception instance
    """
    error_code = response_data.get('code', 'UNKNOWN_ERROR')
    message = response_data.get('message', 'Unknown API error occurred')
    details = response_data.get('details', {})
    
    return create_error_from_code(error_code, message, details=details)