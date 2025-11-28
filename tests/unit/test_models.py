"""
Unit tests for the core models module.
"""

import pytest
from datetime import datetime, timedelta
from typing import List, Dict

from gam_api.models import (
    ReportType,
    DateRangeType,
    DateRange,
    ReportDefinition,
    ReportStatus,
    Report,
    ReportResult,
    ExportFormat,
    Dimension,
    Metric,
    QuickReportConfig
)


class TestReportType:
    """Test cases for ReportType enum."""
    
    def test_report_types(self):
        """Test all report type values."""
        assert ReportType.DELIVERY == "delivery"
        assert ReportType.INVENTORY == "inventory"
        assert ReportType.SALES == "sales"
        assert ReportType.REACH == "reach"
        assert ReportType.PROGRAMMATIC == "programmatic"
    
    def test_report_type_is_string(self):
        """Test that report types are strings."""
        assert isinstance(ReportType.DELIVERY.value, str)
        assert ReportType.DELIVERY.value == "delivery"
        assert ReportType.DELIVERY == "delivery"  # Test that enum equals its string value
    
    def test_report_type_comparison(self):
        """Test report type comparisons."""
        assert ReportType.DELIVERY == ReportType.DELIVERY
        assert ReportType.DELIVERY != ReportType.INVENTORY
        assert ReportType.DELIVERY == "delivery"


class TestDateRangeType:
    """Test cases for DateRangeType enum."""
    
    def test_date_range_types(self):
        """Test all date range type values."""
        assert DateRangeType.LAST_WEEK == "LAST_WEEK"
        assert DateRangeType.LAST_MONTH == "LAST_MONTH"
        assert DateRangeType.CUSTOM == "CUSTOM"
        assert DateRangeType.LAST_N_DAYS == "LAST_N_DAYS"
    
    def test_date_range_type_is_string(self):
        """Test that date range types are strings."""
        assert isinstance(DateRangeType.CUSTOM.value, str)


class TestDateRange:
    """Test cases for DateRange class."""
    
    def test_init_with_dates(self):
        """Test DateRange initialization with start and end dates."""
        date_range = DateRange(
            start_date="2024-01-01",
            end_date="2024-01-31",
            date_range_type=DateRangeType.CUSTOM
        )
        
        assert date_range.start_date == "2024-01-01"
        assert date_range.end_date == "2024-01-31"
        assert date_range.date_range_type == DateRangeType.CUSTOM
    
    def test_init_with_defaults(self):
        """Test DateRange initialization with defaults."""
        date_range = DateRange()
        
        assert date_range.start_date is None
        assert date_range.end_date is None
        assert date_range.date_range_type is None
    
    def test_last_n_days(self):
        """Test creating date range for last N days."""
        # Mock datetime to have consistent test
        from unittest.mock import patch
        with patch('src.core.models.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 31, 12, 0, 0)
            mock_datetime.strftime = datetime.strftime
            
            date_range = DateRange.last_n_days(7)
            
            assert date_range.start_date == "2024-01-24"
            assert date_range.end_date == "2024-01-31"
            assert date_range.date_range_type == DateRangeType.LAST_N_DAYS
    
    def test_last_n_days_various_values(self):
        """Test last_n_days with various day values."""
        from unittest.mock import patch
        with patch('src.core.models.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 2, 15, 0, 0, 0)
            mock_datetime.strftime = datetime.strftime
            
            # Test 1 day
            date_range = DateRange.last_n_days(1)
            assert date_range.start_date == "2024-02-14"
            assert date_range.end_date == "2024-02-15"
            
            # Test 30 days
            date_range = DateRange.last_n_days(30)
            assert date_range.start_date == "2024-01-16"
            assert date_range.end_date == "2024-02-15"


class TestReportDefinition:
    """Test cases for ReportDefinition class."""
    
    def test_init_with_all_params(self):
        """Test ReportDefinition initialization with all parameters."""
        date_range = DateRange(start_date="2024-01-01", end_date="2024-01-31")
        
        report_def = ReportDefinition(
            name="Test Report",
            dimensions=["DATE", "AD_UNIT_NAME"],
            metrics=["IMPRESSIONS", "CLICKS"],
            date_range=date_range,
            filters=[{"field": "AD_UNIT_NAME", "operator": "CONTAINS", "value": "Mobile"}]
        )
        
        assert report_def.name == "Test Report"
        assert report_def.dimensions == ["DATE", "AD_UNIT_NAME"]
        assert report_def.metrics == ["IMPRESSIONS", "CLICKS"]
        assert report_def.date_range == date_range
        assert len(report_def.filters) == 1
        assert report_def.filters[0]["field"] == "AD_UNIT_NAME"
    
    def test_init_with_defaults(self):
        """Test ReportDefinition initialization with defaults."""
        report_def = ReportDefinition(name="Minimal Report")
        
        assert report_def.name == "Minimal Report"
        assert report_def.dimensions == []
        assert report_def.metrics == []
        assert report_def.date_range is None
        assert report_def.filters == []
    
    def test_init_with_kwargs(self):
        """Test ReportDefinition with additional kwargs."""
        report_def = ReportDefinition(
            name="Report with Extra",
            custom_field="custom_value",
            filters=[{"field": "COUNTRY", "value": "US"}]
        )
        
        assert report_def.name == "Report with Extra"
        assert report_def.filters == [{"field": "COUNTRY", "value": "US"}]


class TestReportStatus:
    """Test cases for ReportStatus enum."""
    
    def test_report_statuses(self):
        """Test all report status values."""
        assert ReportStatus.PENDING == "PENDING"
        assert ReportStatus.IN_PROGRESS == "IN_PROGRESS"
        assert ReportStatus.COMPLETED == "COMPLETED"
        assert ReportStatus.FAILED == "FAILED"
    
    def test_status_transitions(self):
        """Test typical status transitions."""
        status = ReportStatus.PENDING
        assert status == "PENDING"
        
        # Transition to in progress
        status = ReportStatus.IN_PROGRESS
        assert status == "IN_PROGRESS"
        
        # Transition to completed
        status = ReportStatus.COMPLETED
        assert status == "COMPLETED"


class TestReport:
    """Test cases for Report class."""
    
    def test_init_basic(self):
        """Test Report initialization with basic parameters."""
        report = Report(
            id="report-123",
            name="Test Report",
            status=ReportStatus.PENDING
        )
        
        assert report.id == "report-123"
        assert report.name == "Test Report"
        assert report.status == ReportStatus.PENDING
        assert report.data == []
        assert report.created_at is None
        assert report.completed_at is None
    
    def test_init_with_kwargs(self):
        """Test Report initialization with kwargs."""
        created_at = datetime.now()
        completed_at = created_at + timedelta(minutes=5)
        
        report = Report(
            id="report-456",
            name="Complete Report",
            status=ReportStatus.COMPLETED,
            data=[["2024-01-01", "1000"], ["2024-01-02", "2000"]],
            created_at=created_at,
            completed_at=completed_at
        )
        
        assert report.id == "report-456"
        assert report.status == ReportStatus.COMPLETED
        assert len(report.data) == 2
        assert report.created_at == created_at
        assert report.completed_at == completed_at
    
    def test_status_update(self):
        """Test updating report status."""
        report = Report(id="report-789", name="Status Test", status=ReportStatus.PENDING)
        
        assert report.status == ReportStatus.PENDING
        
        # Update status
        report.status = ReportStatus.IN_PROGRESS
        assert report.status == ReportStatus.IN_PROGRESS
        
        # Complete report
        report.status = ReportStatus.COMPLETED
        report.completed_at = datetime.now()
        assert report.status == ReportStatus.COMPLETED
        assert report.completed_at is not None


class TestReportResult:
    """Test cases for ReportResult class."""
    
    def test_init_with_data(self):
        """Test ReportResult initialization with data."""
        data = [
            {"date": "2024-01-01", "impressions": 1000},
            {"date": "2024-01-02", "impressions": 2000}
        ]
        
        result = ReportResult(data=data, headers=["date", "impressions"])
        
        assert result.data == data
        assert result.total_rows == 2
        assert result.headers == ["date", "impressions"]
    
    def test_init_empty(self):
        """Test ReportResult initialization with no data."""
        result = ReportResult()
        
        assert result.data == []
        assert result.total_rows == 0
        assert result.headers == []
    
    def test_init_with_total_rows_override(self):
        """Test ReportResult with custom total_rows."""
        data = [{"id": 1}, {"id": 2}]
        
        # Override total_rows (useful for paginated results)
        result = ReportResult(data=data, total_rows=100)
        
        assert len(result.data) == 2
        assert result.total_rows == 100  # Not len(data)
    
    def test_data_manipulation(self):
        """Test manipulating result data."""
        result = ReportResult()
        
        # Add data
        result.data.append({"metric": "value1"})
        result.data.append({"metric": "value2"})
        
        assert len(result.data) == 2
        assert result.data[0]["metric"] == "value1"


class TestExportFormat:
    """Test cases for ExportFormat enum."""
    
    def test_export_formats(self):
        """Test all export format values."""
        assert ExportFormat.JSON == "json"
        assert ExportFormat.CSV == "csv"
        assert ExportFormat.XLSX == "xlsx"
    
    def test_format_usage(self):
        """Test using export format in context."""
        format = ExportFormat.CSV
        assert format == "csv"
        assert format.value == "csv"
        
        # Can be used in string operations
        filename = f"report.{format.value}"
        assert filename == "report.csv"


class TestDimension:
    """Test cases for Dimension class."""
    
    def test_dimension_constants(self):
        """Test dimension constant values."""
        assert Dimension.DATE == "DATE"
        assert Dimension.AD_UNIT_NAME == "AD_UNIT_NAME"
        assert Dimension.ADVERTISER_NAME == "ADVERTISER_NAME"
    
    def test_dimension_usage(self):
        """Test using dimensions in collections."""
        dimensions = [Dimension.DATE, Dimension.AD_UNIT_NAME]
        
        assert len(dimensions) == 2
        assert Dimension.DATE in dimensions
        assert "DATE" in dimensions  # String comparison works


class TestMetric:
    """Test cases for Metric class."""
    
    def test_metric_constants(self):
        """Test metric constant values."""
        assert Metric.IMPRESSIONS == "IMPRESSIONS"
        assert Metric.CLICKS == "CLICKS"
        assert Metric.CTR == "CTR"
    
    def test_metric_usage(self):
        """Test using metrics in report definition."""
        metrics = [Metric.IMPRESSIONS, Metric.CLICKS, Metric.CTR]
        
        assert len(metrics) == 3
        assert all(isinstance(m, str) for m in metrics)


class TestQuickReportConfig:
    """Test cases for QuickReportConfig class."""
    
    def test_init_basic(self):
        """Test QuickReportConfig basic initialization."""
        config = QuickReportConfig(
            report_type="delivery",
            dimensions=["DATE", "AD_UNIT_NAME"],
            metrics=["IMPRESSIONS", "CLICKS"]
        )
        
        assert config.report_type == "delivery"
        assert config.dimensions == ["DATE", "AD_UNIT_NAME"]
        assert config.metrics == ["IMPRESSIONS", "CLICKS"]
        assert config.description == ""
    
    def test_init_with_description(self):
        """Test QuickReportConfig with description."""
        config = QuickReportConfig(
            report_type="inventory",
            description="Inventory performance report"
        )
        
        assert config.report_type == "inventory"
        assert config.dimensions == []
        assert config.metrics == []
        assert config.description == "Inventory performance report"
    
    def test_init_with_kwargs(self):
        """Test QuickReportConfig with additional kwargs."""
        config = QuickReportConfig(
            report_type="sales",
            dimensions=["DATE", "ADVERTISER_NAME"],
            metrics=["REVENUE", "ECPM"],
            description="Sales performance metrics",
            custom_field="custom_value"
        )
        
        assert config.report_type == "sales"
        assert len(config.dimensions) == 2
        assert len(config.metrics) == 2
        assert config.description == "Sales performance metrics"
    
    def test_modification(self):
        """Test modifying config after creation."""
        config = QuickReportConfig(report_type="reach")
        
        # Add dimensions and metrics
        config.dimensions.append("DATE")
        config.dimensions.append("COUNTRY_NAME")
        config.metrics.append("UNIQUE_REACH")
        
        assert len(config.dimensions) == 2
        assert len(config.metrics) == 1
        assert "COUNTRY_NAME" in config.dimensions