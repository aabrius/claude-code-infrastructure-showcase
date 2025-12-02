# models/__init__.py
from .errors import APIError, AuthenticationError, QuotaExceededError, ValidationError
from .dimensions import Dimension, DimensionCategory, ALLOWED_DIMENSIONS

__all__ = [
    "APIError",
    "AuthenticationError",
    "QuotaExceededError",
    "ValidationError",
    "Dimension",
    "DimensionCategory",
    "ALLOWED_DIMENSIONS",
]
