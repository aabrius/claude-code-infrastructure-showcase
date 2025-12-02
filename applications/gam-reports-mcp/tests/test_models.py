# tests/test_models.py
import pytest
from models.errors import APIError, AuthenticationError, QuotaExceededError, ValidationError
from models.dimensions import Dimension, DimensionCategory, ALLOWED_DIMENSIONS


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


def test_dimension_category_enum():
    assert DimensionCategory.TIME == "time"
    assert DimensionCategory.INVENTORY == "inventory"


def test_dimension_model():
    dim = Dimension(
        name="DATE",
        category=DimensionCategory.TIME,
        description="Daily granularity",
        use_case="Daily performance trends",
        compatible_with=["TOTAL_IMPRESSIONS"],
    )
    assert dim.name == "DATE"
    assert dim.category == DimensionCategory.TIME


def test_allowed_dimensions_contains_date():
    assert "DATE" in ALLOWED_DIMENSIONS
    assert ALLOWED_DIMENSIONS["DATE"].category == DimensionCategory.TIME


def test_allowed_dimensions_contains_ad_unit_name():
    assert "AD_UNIT_NAME" in ALLOWED_DIMENSIONS
    assert ALLOWED_DIMENSIONS["AD_UNIT_NAME"].category == DimensionCategory.INVENTORY
