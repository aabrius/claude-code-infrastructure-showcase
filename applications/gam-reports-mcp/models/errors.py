"""Custom exceptions for GAM Reports MCP."""


class APIError(Exception):
    """Base exception for API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(APIError):
    """Authentication failed."""

    pass


class QuotaExceededError(APIError):
    """Rate limit exceeded."""

    def __init__(self, message: str, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(message, status_code=429)


class ValidationError(APIError):
    """Validation error."""

    def __init__(self, message: str, field: str | None = None):
        self.field = field
        super().__init__(message, status_code=400)
