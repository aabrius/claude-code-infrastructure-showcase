# tests/test_models.py
import pytest
from models.errors import APIError, AuthenticationError, QuotaExceededError, ValidationError


def test_api_error_has_message():
    error = APIError("Something went wrong")
    assert str(error) == "Something went wrong"
    assert error.message == "Something went wrong"


def test_authentication_error_inherits_api_error():
    error = AuthenticationError("Invalid token")
    assert isinstance(error, APIError)


def test_quota_exceeded_has_retry_after():
    error = QuotaExceededError("Rate limited", retry_after=60)
    assert error.retry_after == 60


def test_validation_error_has_field():
    error = ValidationError("Invalid dimension", field="dimensions")
    assert error.field == "dimensions"
