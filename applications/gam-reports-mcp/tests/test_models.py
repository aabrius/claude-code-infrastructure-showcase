# tests/test_models.py
import pytest
from models.errors import APIError, AuthenticationError, QuotaExceededError, ValidationError
from models.dimensions import Dimension, DimensionCategory, ALLOWED_DIMENSIONS
from models.metrics import Metric, MetricCategory, ALLOWED_METRICS


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


def test_metric_category_enum():
    assert MetricCategory.CORE == "core"
    assert MetricCategory.REVENUE == "revenue"
    assert MetricCategory.AD_EXCHANGE == "ad_exchange"
    assert MetricCategory.ACTIVE_VIEW == "active_view"


def test_metric_model():
    from models.metrics import DataFormat, ReportType
    metric = Metric(
        name="IMPRESSIONS",
        category=MetricCategory.CORE,
        data_format=DataFormat.INTEGER,
        description="Total impressions served",
        report_types=[ReportType.HISTORICAL],
    )
    assert metric.name == "IMPRESSIONS"
    assert metric.data_format == DataFormat.INTEGER


def test_allowed_metrics_contains_impressions():
    from models.metrics import DataFormat
    assert "IMPRESSIONS" in ALLOWED_METRICS
    assert ALLOWED_METRICS["IMPRESSIONS"].category == MetricCategory.CORE
    assert ALLOWED_METRICS["IMPRESSIONS"].data_format == DataFormat.INTEGER


def test_allowed_metrics_contains_revenue():
    from models.metrics import DataFormat
    assert "REVENUE" in ALLOWED_METRICS
    assert ALLOWED_METRICS["REVENUE"].category == MetricCategory.REVENUE
    assert ALLOWED_METRICS["REVENUE"].data_format == DataFormat.CURRENCY


# Filter model tests
from datetime import date
from models.filters import DateRangeFilter, DomainFilter, AdStrategyFilter


def test_date_range_filter():
    f = DateRangeFilter(start_date=date(2024, 1, 1), end_date=date(2024, 1, 31))
    assert f.start_date == date(2024, 1, 1)
    assert f.end_date == date(2024, 1, 31)


def test_date_range_from_strings():
    f = DateRangeFilter(start_date="2024-01-01", end_date="2024-01-31")
    assert f.start_date == date(2024, 1, 1)


def test_domain_filter():
    f = DomainFilter(domains=["example.com", "m.example.com"])
    assert len(f.domains) == 2


def test_ad_strategy_filter():
    f = AdStrategyFilter(strategy="direct_sold")
    assert f.strategy == "direct_sold"


# Knowledge model tests
from models.knowledge import Domain, App, AdStrategy, ReportTemplate


def test_domain_model():
    d = Domain(name="example.com", ad_units=["homepage_leaderboard", "sidebar_mpu"])
    assert d.name == "example.com"
    assert len(d.ad_units) == 2


def test_app_model():
    app = App(name="Example iOS", app_id="6443685698", platform="ios", ad_units=["app_banner"])
    assert app.app_id == "6443685698"
    assert app.platform == "ios"


def test_ad_strategy_model():
    s = AdStrategy(
        name="direct_sold",
        description="Guaranteed campaigns",
        typical_dimensions=["ADVERTISER_NAME", "ORDER_NAME"],
        typical_metrics=["TOTAL_IMPRESSIONS", "TOTAL_CPM_AND_CPC_REVENUE"],
    )
    assert s.name == "direct_sold"


def test_report_template():
    t = ReportTemplate(
        name="delivery",
        description="Standard delivery report",
        dimensions=["DATE", "AD_UNIT_NAME"],
        metrics=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS"],
    )
    assert t.name == "delivery"


# Report model tests
from models.reports import CreateReportRequest, ReportResponse


def test_create_report_request():
    req = CreateReportRequest(
        display_name="Test Report",
        dimensions=["DATE", "AD_UNIT_NAME"],
        metrics=["TOTAL_IMPRESSIONS"],
        start_date="2024-01-01",
        end_date="2024-01-31",
    )
    assert req.display_name == "Test Report"
    assert len(req.dimensions) == 2


def test_create_report_request_to_gam_format():
    req = CreateReportRequest(
        dimensions=["DATE"],
        metrics=["TOTAL_IMPRESSIONS"],
        start_date="2024-01-01",
        end_date="2024-01-31",
    )
    gam_format = req.to_gam_format()
    assert "reportDefinition" in gam_format
    assert gam_format["reportDefinition"]["dimensions"] == ["DATE"]


def test_report_response():
    resp = ReportResponse(
        name="networks/123/reports/456",
        report_id="456",
        display_name="Test Report",
        state="COMPLETED",
    )
    assert resp.report_id == "456"
    assert resp.state == "COMPLETED"
