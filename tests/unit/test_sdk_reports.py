"""
Unit tests for the GAM SDK reports module.

Tests the ReportBuilder and ReportResult classes including fluent API,
data manipulation, export functionality, and error handling.
"""

import pytest
import pandas as pd
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import date, timedelta
from pathlib import Path

from gam_sdk.reports import ReportBuilder, ReportResult
from gam_sdk.exceptions import ReportError, ValidationError
from gam_api.models import ReportDefinition, DateRange, DateRangeType, ReportType
from gam_api.reports import QUICK_REPORTS


class TestReportResult:
    """Test ReportResult class functionality."""
    
    @pytest.fixture
    def sample_report_data(self):
        """Sample report data for testing."""
        rows = [
            {
                'dimensionValues': ['2024-01-01', 'Ad Unit 1'],
                'metricValueGroups': [{'primaryValues': ['1000', '50']}]
            },
            {
                'dimensionValues': ['2024-01-02', 'Ad Unit 2'],
                'metricValueGroups': [{'primaryValues': ['2000', '100']}]
            }
        ]
        dimension_headers = ['DATE', 'AD_UNIT_NAME']
        metric_headers = ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS']
        metadata = {'generated_at': '2024-01-01T00:00:00'}
        
        return ReportResult(rows, dimension_headers, metric_headers, metadata)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_report_result_initialization(self, sample_report_data):
        """Test ReportResult initialization."""
        assert len(sample_report_data.rows) == 2
        assert sample_report_data.dimension_headers == ['DATE', 'AD_UNIT_NAME']
        assert sample_report_data.metric_headers == ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS']
        assert sample_report_data.metadata['generated_at'] == '2024-01-01T00:00:00'
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_headers_property(self, sample_report_data):
        """Test headers property combines dimensions and metrics."""
        expected_headers = ['DATE', 'AD_UNIT_NAME', 'TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS']
        assert sample_report_data.headers == expected_headers
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_row_count_property(self, sample_report_data):
        """Test row_count property."""
        assert sample_report_data.row_count == 2
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_column_count_property(self, sample_report_data):
        """Test column_count property."""
        assert sample_report_data.column_count == 4
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_to_dict_method(self, sample_report_data):
        """Test to_dict method."""
        result_dict = sample_report_data.to_dict()
        
        assert 'headers' in result_dict
        assert 'dimension_headers' in result_dict
        assert 'metric_headers' in result_dict
        assert 'rows' in result_dict
        assert 'metadata' in result_dict
        assert 'summary' in result_dict
        
        assert result_dict['summary']['row_count'] == 2
        assert result_dict['summary']['column_count'] == 4
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_to_dataframe_method(self, sample_report_data):
        """Test to_dataframe method."""
        df = sample_report_data.to_dataframe()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == sample_report_data.headers
        
        # Check data conversion
        assert df.iloc[0]['DATE'] == '2024-01-01'
        assert df.iloc[0]['AD_UNIT_NAME'] == 'Ad Unit 1'
        assert df.iloc[0]['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS'] == 1000
        assert df.iloc[0]['TOTAL_LINE_ITEM_LEVEL_CLICKS'] == 50
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_to_dataframe_caching(self, sample_report_data):
        """Test that to_dataframe caches the result."""
        df1 = sample_report_data.to_dataframe()
        df2 = sample_report_data.to_dataframe()
        
        # Should return the same object (cached)
        assert df1 is df2
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_to_csv_export(self, sample_report_data, temp_report_file):
        """Test CSV export functionality."""
        csv_path = temp_report_file.replace('.csv', '_test.csv')
        
        result = sample_report_data.to_csv(csv_path)
        
        # Should return self for chaining
        assert result is sample_report_data
        
        # Check file was created
        assert os.path.exists(csv_path)
        
        # Verify content
        df = pd.read_csv(csv_path)
        assert len(df) == 2
        assert list(df.columns) == sample_report_data.headers
        
        # Cleanup
        os.unlink(csv_path)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_to_json_export_records(self, sample_report_data, temp_report_file):
        """Test JSON export with records format."""
        json_path = temp_report_file.replace('.csv', '.json')
        
        result = sample_report_data.to_json(json_path, format='records')
        
        # Should return self for chaining
        assert result is sample_report_data
        
        # Check file was created
        assert os.path.exists(json_path)
        
        # Verify content
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]['DATE'] == '2024-01-01'
        
        # Cleanup
        os.unlink(json_path)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_to_json_export_table(self, sample_report_data, temp_report_file):
        """Test JSON export with table format."""
        json_path = temp_report_file.replace('.csv', '_table.json')
        
        result = sample_report_data.to_json(json_path, format='table')
        
        # Should return self for chaining
        assert result is sample_report_data
        
        # Check file was created
        assert os.path.exists(json_path)
        
        # Verify content
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        assert 'headers' in data
        assert 'rows' in data
        assert 'metadata' in data
        
        # Cleanup
        os.unlink(json_path)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_to_excel_export(self, sample_report_data, temp_report_file):
        """Test Excel export functionality."""
        excel_path = temp_report_file.replace('.csv', '.xlsx')
        
        result = sample_report_data.to_excel(excel_path, sheet_name='Test Sheet')
        
        # Should return self for chaining
        assert result is sample_report_data
        
        # Check file was created
        assert os.path.exists(excel_path)
        
        # Verify content
        df = pd.read_excel(excel_path, sheet_name='Test Sheet')
        assert len(df) == 2
        assert list(df.columns) == sample_report_data.headers
        
        # Cleanup
        os.unlink(excel_path)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_filter_method(self, sample_report_data):
        """Test filter method."""
        # Filter for impressions > 1500
        filtered = sample_report_data.filter(
            lambda row: row.get('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 0) > 1500
        )
        
        assert isinstance(filtered, ReportResult)
        assert len(filtered) == 1
        assert filtered.dimension_headers == sample_report_data.dimension_headers
        assert filtered.metric_headers == sample_report_data.metric_headers
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_sort_method(self, sample_report_data):
        """Test sort method."""
        # Sort by impressions descending
        sorted_result = sample_report_data.sort('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', ascending=False)
        
        assert isinstance(sorted_result, ReportResult)
        assert len(sorted_result) == 2
        
        # Check that order is correct (2000 before 1000)
        df = sorted_result.to_dataframe()
        assert df.iloc[0]['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS'] == 2000
        assert df.iloc[1]['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS'] == 1000
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_head_method(self, sample_report_data):
        """Test head method."""
        head_result = sample_report_data.head(1)
        
        assert isinstance(head_result, ReportResult)
        assert len(head_result) == 1
        assert head_result.dimension_headers == sample_report_data.dimension_headers
        assert head_result.metric_headers == sample_report_data.metric_headers
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_tail_method(self, sample_report_data):
        """Test tail method."""
        tail_result = sample_report_data.tail(1)
        
        assert isinstance(tail_result, ReportResult)
        assert len(tail_result) == 1
        assert tail_result.dimension_headers == sample_report_data.dimension_headers
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_summary_method(self, sample_report_data):
        """Test summary method."""
        summary = sample_report_data.summary()
        
        assert 'row_count' in summary
        assert 'column_count' in summary
        assert 'numeric_columns' in summary
        assert 'statistics' in summary
        
        assert summary['row_count'] == 2
        assert summary['column_count'] == 4
        assert 'TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS' in summary['numeric_columns']
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_len_method(self, sample_report_data):
        """Test __len__ method."""
        assert len(sample_report_data) == 2
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_iter_method(self, sample_report_data):
        """Test __iter__ method."""
        rows = list(sample_report_data)
        assert len(rows) == 2
        assert rows[0]['dimensionValues'] == ['2024-01-01', 'Ad Unit 1']
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_repr_method(self, sample_report_data):
        """Test __repr__ method."""
        repr_str = repr(sample_report_data)
        assert "ReportResult" in repr_str
        assert "rows=2" in repr_str
        assert "cols=4" in repr_str


class TestReportBuilder:
    """Test ReportBuilder class functionality."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        return Mock()
    
    @pytest.fixture
    def mock_auth_manager(self):
        """Mock authentication manager."""
        return Mock()
    
    @pytest.fixture
    def report_builder(self, mock_config, mock_auth_manager):
        """Create a ReportBuilder instance with mocked generator."""
        builder = ReportBuilder(mock_config, mock_auth_manager)
        # Mock the generator after creation for tests that need it
        builder._generator = Mock()
        return builder

    @pytest.mark.unit
    @pytest.mark.sdk
    def test_report_builder_initialization(self, mock_config, mock_auth_manager):
        """Test ReportBuilder initialization."""
        builder = ReportBuilder(mock_config, mock_auth_manager)

        assert builder._config == mock_config
        assert builder._auth_manager == mock_auth_manager
        assert builder._report_type == ReportType.DELIVERY  # Default report type
        assert builder._dimensions == []
        assert builder._metrics == []
        assert builder._date_range is None
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_quick_report_valid_type(self, report_builder):
        """Test quick report with valid report type."""
        result = report_builder.quick('delivery')
        
        assert result is report_builder
        assert report_builder._quick_report_type == 'delivery'
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_quick_report_invalid_type(self, report_builder):
        """Test quick report with invalid report type."""
        with pytest.raises(ValidationError) as exc_info:
            report_builder.quick('invalid_type')
        
        assert "Invalid quick report type" in str(exc_info.value)
        assert exc_info.value.field_name == 'report_type'
        assert exc_info.value.field_value == 'invalid_type'
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_delivery_method(self, report_builder):
        """Test delivery quick report method."""
        result = report_builder.delivery()
        
        assert result is report_builder
        assert report_builder._quick_report_type == 'delivery'
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_inventory_method(self, report_builder):
        """Test inventory quick report method."""
        result = report_builder.inventory()
        
        assert result is report_builder
        assert report_builder._quick_report_type == 'inventory'
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_sales_method(self, report_builder):
        """Test sales quick report method."""
        result = report_builder.sales()
        
        assert result is report_builder
        assert report_builder._quick_report_type == 'sales'
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_reach_method(self, report_builder):
        """Test reach quick report method."""
        result = report_builder.reach()
        
        assert result is report_builder
        assert report_builder._quick_report_type == 'reach'
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_programmatic_method(self, report_builder):
        """Test programmatic quick report method."""
        result = report_builder.programmatic()
        
        assert result is report_builder
        assert report_builder._quick_report_type == 'programmatic'
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_dimensions_method(self, report_builder):
        """Test dimensions method."""
        result = report_builder.dimensions('DATE', 'AD_UNIT_NAME', 'LINE_ITEM_NAME')
        
        assert result is report_builder
        assert report_builder._dimensions == ['DATE', 'AD_UNIT_NAME', 'LINE_ITEM_NAME']
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_metrics_method(self, report_builder):
        """Test metrics method."""
        result = report_builder.metrics('IMPRESSIONS', 'CLICKS')
        
        assert result is report_builder
        assert report_builder._metrics == ['IMPRESSIONS', 'CLICKS']
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_date_range_method(self, report_builder):
        """Test date_range method."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        result = report_builder.date_range(start_date, end_date)
        
        assert result is report_builder
        assert report_builder._date_range.date_range_type == DateRangeType.CUSTOM
        assert report_builder._date_range.start_date == start_date
        assert report_builder._date_range.end_date == end_date
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_days_back_method(self, report_builder):
        """Test days_back method."""
        result = report_builder.days_back(7)
        
        assert result is report_builder
        assert report_builder._date_range is not None
        
        # Check that end date is today and start date is 7 days ago
        expected_end = date.today()
        expected_start = expected_end - timedelta(days=7)
        
        assert report_builder._date_range.end_date == expected_end
        assert report_builder._date_range.start_date == expected_start
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_last_7_days_method(self, report_builder):
        """Test last_7_days method."""
        result = report_builder.last_7_days()
        
        assert result is report_builder
        assert report_builder._date_range is not None
        
        expected_end = date.today()
        expected_start = expected_end - timedelta(days=7)
        
        assert report_builder._date_range.end_date == expected_end
        assert report_builder._date_range.start_date == expected_start
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_last_30_days_method(self, report_builder):
        """Test last_30_days method."""
        result = report_builder.last_30_days()
        
        assert result is report_builder
        assert report_builder._date_range is not None
        
        expected_end = date.today()
        expected_start = expected_end - timedelta(days=30)
        
        assert report_builder._date_range.end_date == expected_end
        assert report_builder._date_range.start_date == expected_start
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_this_month_method(self, report_builder):
        """Test this_month method."""
        result = report_builder.this_month()
        
        assert result is report_builder
        assert report_builder._date_range is not None
        
        today = date.today()
        expected_start = today.replace(day=1)
        expected_end = today
        
        assert report_builder._date_range.start_date == expected_start
        assert report_builder._date_range.end_date == expected_end
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_last_month_method(self, report_builder):
        """Test last_month method."""
        result = report_builder.last_month()
        
        assert result is report_builder
        assert report_builder._date_range is not None
        
        today = date.today()
        first_this_month = today.replace(day=1)
        last_month_end = first_this_month - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        
        assert report_builder._date_range.start_date == last_month_start
        assert report_builder._date_range.end_date == last_month_end
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_name_method(self, report_builder):
        """Test name method."""
        result = report_builder.name("Test Report")
        
        assert result is report_builder
        assert report_builder._report_name == "Test Report"
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_filter_method(self, report_builder):
        """Test filter method."""
        result = report_builder.filter('AD_UNIT_NAME', 'CONTAINS', ['mobile'])
        
        assert result is report_builder
        assert len(report_builder._filters) == 1
        assert report_builder._filters[0]['dimension'] == 'AD_UNIT_NAME'
        assert report_builder._filters[0]['operator'] == 'CONTAINS'
        assert report_builder._filters[0]['values'] == ['mobile']
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_execute_quick_report(self, report_builder, mock_report_result):
        """Test execute method with quick report."""
        report_builder._quick_report_type = 'delivery'
        
        with patch('gam_sdk.reports.generate_quick_report') as mock_generate:
            mock_generate.return_value = mock_report_result
            
            result = report_builder.execute()
            
            assert isinstance(result, ReportResult)
            mock_generate.assert_called_once_with('delivery', 30)  # Default days_back
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_execute_custom_report(self, report_builder, mock_report_result):
        """Test execute method with custom report."""
        report_builder._dimensions = ['DATE', 'AD_UNIT_NAME']
        report_builder._metrics = ['IMPRESSIONS']
        
        # Mock the generator methods
        mock_report = Mock()
        mock_report.id = 'test-report-id'
        
        report_builder._generator.create_report.return_value = mock_report
        report_builder._generator.run_report.return_value = mock_report
        report_builder._generator.fetch_results.return_value = mock_report_result
        
        result = report_builder.execute()
        
        assert isinstance(result, ReportResult)
        report_builder._generator.create_report.assert_called_once()
        report_builder._generator.run_report.assert_called_once_with(mock_report)
        report_builder._generator.fetch_results.assert_called_once_with(mock_report)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_execute_validation_error_no_dimensions(self, report_builder):
        """Test execute method validation error - no dimensions."""
        report_builder._metrics = ['IMPRESSIONS']
        # No dimensions set
        
        with pytest.raises(ValidationError) as exc_info:
            report_builder.execute()
        
        assert "At least one dimension is required" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_execute_validation_error_no_metrics(self, report_builder):
        """Test execute method validation error - no metrics."""
        report_builder._dimensions = ['DATE']
        # No metrics set
        
        with pytest.raises(ValidationError) as exc_info:
            report_builder.execute()
        
        assert "At least one metric is required" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_execute_default_date_range(self, report_builder, mock_report_result):
        """Test execute method uses default date range when none specified."""
        report_builder._dimensions = ['DATE']
        report_builder._metrics = ['IMPRESSIONS']
        # No date range set
        
        mock_report = Mock()
        report_builder._generator.create_report.return_value = mock_report
        report_builder._generator.run_report.return_value = mock_report
        report_builder._generator.fetch_results.return_value = mock_report_result
        
        result = report_builder.execute()
        
        # Should have set default date range (last 30 days)
        assert report_builder._date_range is not None
        expected_end = date.today()
        expected_start = expected_end - timedelta(days=30)
        assert report_builder._date_range.start_date == expected_start
        assert report_builder._date_range.end_date == expected_end
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_execute_auto_generated_name(self, report_builder, mock_report_result):
        """Test execute method auto-generates report name."""
        report_builder._dimensions = ['DATE']
        report_builder._metrics = ['IMPRESSIONS']
        # No name set
        
        mock_report = Mock()
        report_builder._generator.create_report.return_value = mock_report
        report_builder._generator.run_report.return_value = mock_report
        report_builder._generator.fetch_results.return_value = mock_report_result
        
        result = report_builder.execute()
        
        # Should have auto-generated name
        assert report_builder._report_name is not None
        assert "Custom Report" in report_builder._report_name
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_preview_method(self, report_builder, mock_report_result):
        """Test preview method."""
        report_builder._quick_report_type = 'delivery'
        
        with patch('gam_sdk.reports.generate_quick_report') as mock_generate:
            mock_generate.return_value = mock_report_result
            
            result = report_builder.preview(limit=3)
            
            assert isinstance(result, ReportResult)
            assert len(result) <= 3  # Should be limited
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_repr_method(self, report_builder):
        """Test __repr__ method."""
        # Empty builder
        repr_str = repr(report_builder)
        assert "ReportBuilder(empty)" in repr_str
        
        # Builder with configuration
        report_builder._quick_report_type = 'delivery'
        report_builder._dimensions = ['DATE', 'AD_UNIT_NAME']
        report_builder._metrics = ['IMPRESSIONS']
        report_builder.last_7_days()
        
        repr_str = repr(report_builder)
        assert "ReportBuilder" in repr_str
        assert "quick=delivery" in repr_str
        assert "dims=2" in repr_str
        assert "metrics=1" in repr_str
        assert "days=7" in repr_str


class TestReportBuilderErrorHandling:
    """Test error handling in ReportBuilder."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        return Mock()

    @pytest.fixture
    def mock_auth_manager(self):
        """Mock authentication manager."""
        return Mock()

    @pytest.fixture
    def report_builder(self, mock_config, mock_auth_manager):
        """Create a ReportBuilder instance with mocked generator."""
        builder = ReportBuilder(mock_config, mock_auth_manager)
        builder._generator = Mock()
        return builder
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_execute_report_generation_error(self, report_builder):
        """Test execute method handles ReportGenerationError."""
        from gam_api.exceptions import ReportGenerationError
        
        report_builder._dimensions = ['DATE']
        report_builder._metrics = ['IMPRESSIONS']
        
        report_builder._generator.create_report.side_effect = ReportGenerationError("Generation failed")
        
        with pytest.raises(ReportError) as exc_info:
            report_builder.execute()
        
        assert "Report generation failed" in str(exc_info.value)
    
    @pytest.mark.unit
    @pytest.mark.sdk
    def test_execute_unexpected_error(self, report_builder):
        """Test execute method handles unexpected errors."""
        report_builder._dimensions = ['DATE']
        report_builder._metrics = ['IMPRESSIONS']
        
        report_builder._generator.create_report.side_effect = Exception("Unexpected error")
        
        with pytest.raises(ReportError) as exc_info:
            report_builder.execute()
        
        assert "Unexpected error during report execution" in str(exc_info.value)