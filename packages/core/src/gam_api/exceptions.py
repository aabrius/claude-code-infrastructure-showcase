"""
Custom exceptions for Google Ad Manager API integration.

This module now serves as a backward compatibility layer,
importing from the new gam_core package.
"""

# Try to import from new package location, with fallback definitions
try:
    from gam_core.exceptions import (
        GAMError,
        AuthenticationError,
        ConfigurationError,
        APIError,
        QuotaExceededError,
        InvalidRequestError,
        ReportError,
        ReportGenerationError,
        ReportTimeoutError,
        ValidationError,
    )
except ImportError:
    # Define exceptions locally if gam_core is not available
    
    class GAMError(Exception):
        """Base exception for all GAM-related errors."""
        pass
    
    
    class AuthenticationError(GAMError):
        """Authentication failure."""
        pass
    
    
    class ConfigurationError(GAMError):
        """Configuration error."""
        pass
    
    
    class APIError(GAMError):
        """General API error."""
        def __init__(self, message, status_code=None, error_code=None):
            super().__init__(message)
            self.status_code = status_code
            self.error_code = error_code
    
    
    class QuotaExceededError(APIError):
        """API quota exceeded."""
        pass
    
    
    class InvalidRequestError(APIError):
        """Invalid API request."""
        pass
    
    
    class ReportError(GAMError):
        """Report-related error."""
        pass
    
    
    class ReportGenerationError(ReportError):
        """Report generation failed."""
        pass
    
    
    class ReportTimeoutError(ReportError):
        """Report generation timed out."""
        pass
    
    
    class ValidationError(GAMError):
        """Validation error."""
        pass


# Additional exceptions for unified client
class NetworkError(APIError):
    """Network connectivity error."""
    pass


class NotFoundError(APIError):
    """Resource not found error."""
    pass


class ReportNotReadyError(ReportError):
    """Report is not ready for download."""
    pass


# Re-export for backward compatibility
__all__ = [
    "GAMError",
    "AuthenticationError",
    "ConfigurationError",
    "APIError",
    "QuotaExceededError",
    "InvalidRequestError",
    "ReportError",
    "ReportGenerationError",
    "ReportTimeoutError",
    "ValidationError",
    "NetworkError",
    "NotFoundError",
    "ReportNotReadyError",
]