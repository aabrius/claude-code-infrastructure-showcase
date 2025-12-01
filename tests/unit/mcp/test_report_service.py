"""Unit tests for ReportService."""

import pytest
from unittest.mock import Mock, AsyncMock
import json


class TestReportService:
    """Tests for ReportService business logic."""

    @pytest.fixture
    def mock_gam_client(self):
        """Create mock GAM client."""
        client = Mock()
        client.delivery_report = Mock(return_value=Mock(
            total_rows=100,
            dimension_headers=["DATE", "AD_UNIT_NAME"],
            metric_headers=["IMPRESSIONS", "CLICKS"],
            rows=[{"date": "2024-01-01", "impressions": 1000}]
        ))
        client.inventory_report = Mock(return_value=Mock(
            total_rows=50,
            dimension_headers=["DATE"],
            metric_headers=["TOTAL_AD_REQUESTS"],
            rows=[]
        ))
        return client

    @pytest.fixture
    def mock_cache(self):
        """Create mock cache manager."""
        cache = Mock()
        cache.get = Mock(return_value=None)
        cache.set = Mock()
        return cache

    def test_quick_report_delivery(self, mock_gam_client, mock_cache):
        """Test generating delivery quick report."""
        from applications.mcp_server.services import ReportService

        service = ReportService(client=mock_gam_client, cache=mock_cache)
        result = service.quick_report("delivery", days_back=7)

        assert result["success"] is True
        assert result["report_type"] == "delivery"
        assert result["total_rows"] == 100
        mock_gam_client.delivery_report.assert_called_once()

    def test_quick_report_inventory(self, mock_gam_client, mock_cache):
        """Test generating inventory quick report."""
        from applications.mcp_server.services import ReportService

        service = ReportService(client=mock_gam_client, cache=mock_cache)
        result = service.quick_report("inventory", days_back=30)

        assert result["success"] is True
        assert result["report_type"] == "inventory"
        mock_gam_client.inventory_report.assert_called_once()

    def test_quick_report_invalid_type(self, mock_gam_client, mock_cache):
        """Test quick report with invalid type raises error."""
        from applications.mcp_server.services import ReportService

        service = ReportService(client=mock_gam_client, cache=mock_cache)

        with pytest.raises(ValueError, match="Unknown report type"):
            service.quick_report("invalid_type", days_back=7)

    def test_quick_report_uses_cache(self, mock_gam_client, mock_cache):
        """Test that quick report checks cache first."""
        from applications.mcp_server.services import ReportService

        # Cache returns a hit
        cached_result = {"success": True, "report_type": "delivery", "from_cache": True}
        mock_cache.get = Mock(return_value=cached_result)

        service = ReportService(client=mock_gam_client, cache=mock_cache)
        result = service.quick_report("delivery", days_back=7)

        assert result["from_cache"] is True
        mock_gam_client.delivery_report.assert_not_called()
