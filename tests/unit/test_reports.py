"""
Unit tests for the core reports module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date, timedelta

from gam_api.reports import (
    ReportGenerator,
    QUICK_REPORTS,
    generate_quick_report,
    list_quick_report_types
)
from gam_api.exceptions import (
    ReportError,
    ValidationError,
    ConfigurationError,
    APIError
)


class TestQuickReports:
    """Test cases for quick reports configuration."""

    def test_quick_reports_defined(self):
        """Test that QUICK_REPORTS contains expected report types."""
        assert "delivery" in QUICK_REPORTS
        assert "inventory" in QUICK_REPORTS
        assert "sales" in QUICK_REPORTS
        assert "reach" in QUICK_REPORTS
        assert "programmatic" in QUICK_REPORTS

    def test_quick_reports_structure(self):
        """Test QUICK_REPORTS entry structure."""
        for report_type, config in QUICK_REPORTS.items():
            assert "name" in config
            assert "description" in config

    def test_list_quick_report_types(self):
        """Test list_quick_report_types returns expected types."""
        types = list_quick_report_types()
        assert isinstance(types, list)
        assert "delivery" in types
        assert "inventory" in types
        assert "sales" in types
        assert "reach" in types
        assert "programmatic" in types


class TestReportGenerator:
    """Test cases for ReportGenerator class."""

    def test_init_without_client(self):
        """Test ReportGenerator initialization without client."""
        generator = ReportGenerator()
        assert generator.client is None

    def test_init_with_client(self):
        """Test ReportGenerator initialization with client."""
        mock_client = Mock()
        generator = ReportGenerator(client=mock_client)
        assert generator.client == mock_client

    def test_generate_quick_report_delivery(self):
        """Test generating a delivery quick report."""
        generator = ReportGenerator()
        result = generator.generate_quick_report('delivery')

        assert isinstance(result, dict)
        assert result['report_type'] == 'delivery'
        assert result['status'] == 'completed'

    def test_generate_quick_report_inventory(self):
        """Test generating an inventory quick report."""
        generator = ReportGenerator()
        result = generator.generate_quick_report('inventory')

        assert isinstance(result, dict)
        assert result['report_type'] == 'inventory'
        assert result['status'] == 'completed'

    def test_generate_quick_report_sales(self):
        """Test generating a sales quick report."""
        generator = ReportGenerator()
        result = generator.generate_quick_report('sales')

        assert isinstance(result, dict)
        assert result['report_type'] == 'sales'
        assert result['status'] == 'completed'

    def test_generate_quick_report_reach(self):
        """Test generating a reach quick report."""
        generator = ReportGenerator()
        result = generator.generate_quick_report('reach')

        assert isinstance(result, dict)
        assert result['report_type'] == 'reach'
        assert result['status'] == 'completed'

    def test_generate_quick_report_programmatic(self):
        """Test generating a programmatic quick report."""
        generator = ReportGenerator()
        result = generator.generate_quick_report('programmatic')

        assert isinstance(result, dict)
        assert result['report_type'] == 'programmatic'
        assert result['status'] == 'completed'

    def test_generate_quick_report_all_types(self):
        """Test all quick report types are handled."""
        generator = ReportGenerator()

        for report_type in QUICK_REPORTS.keys():
            result = generator.generate_quick_report(report_type)
            assert isinstance(result, dict)
            assert result['report_type'] == report_type

    def test_generate_quick_report_with_kwargs(self):
        """Test generate_quick_report accepts kwargs."""
        generator = ReportGenerator()
        result = generator.generate_quick_report('delivery', days_back=7, format='csv')

        assert isinstance(result, dict)
        assert result['report_type'] == 'delivery'


class TestGenerateQuickReportFunction:
    """Test the module-level generate_quick_report function."""

    def test_generate_quick_report_function(self):
        """Test generate_quick_report function works."""
        result = generate_quick_report('delivery')

        assert isinstance(result, dict)
        assert result['report_type'] == 'delivery'
        assert result['status'] == 'completed'

    def test_generate_quick_report_function_with_kwargs(self):
        """Test generate_quick_report function accepts kwargs."""
        result = generate_quick_report('inventory', days_back=30)

        assert isinstance(result, dict)
        assert result['report_type'] == 'inventory'
