"""Unit tests for ReportService."""

import pytest
from unittest.mock import Mock
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

    def test_init_validates_client_not_none(self):
        """Test that __init__ raises ValueError when client is None."""
        from applications.mcp_server.services import ReportService

        with pytest.raises(ValueError, match="Client cannot be None"):
            ReportService(client=None)

    def test_list_reports(self, mock_gam_client):
        """Test listing available reports."""
        from applications.mcp_server.services import ReportService

        # Mock client response
        mock_gam_client.list_reports = Mock(return_value=[
            {
                "reportId": "report-1",
                "displayName": "Test Report 1",
                "createTime": "2024-01-01T00:00:00Z",
                "updateTime": "2024-01-02T00:00:00Z",
            },
            {
                "reportId": "report-2",
                "displayName": "Test Report 2",
                "createTime": "2024-01-03T00:00:00Z",
                "updateTime": "2024-01-04T00:00:00Z",
            }
        ])

        service = ReportService(client=mock_gam_client)
        result = service.list_reports(limit=20)

        assert result["success"] is True
        assert result["total_reports"] == 2
        assert len(result["reports"]) == 2
        assert result["reports"][0]["id"] == "report-1"
        assert result["reports"][0]["name"] == "Test Report 1"
        mock_gam_client.list_reports.assert_called_once_with(limit=20)

    def test_get_dimensions_metrics_both(self, mock_gam_client):
        """Test getting both dimensions and metrics."""
        from applications.mcp_server.services import ReportService

        service = ReportService(client=mock_gam_client)
        result = service.get_dimensions_metrics(report_type="HISTORICAL", category="both")

        assert result["success"] is True
        assert result["report_type"] == "HISTORICAL"
        assert "dimensions" in result
        assert "metrics" in result
        assert isinstance(result["dimensions"], list)
        assert isinstance(result["metrics"], list)
        assert len(result["dimensions"]) > 0
        assert len(result["metrics"]) > 0

    def test_get_dimensions_metrics_dimensions_only(self, mock_gam_client):
        """Test getting dimensions only."""
        from applications.mcp_server.services import ReportService

        service = ReportService(client=mock_gam_client)
        result = service.get_dimensions_metrics(report_type="HISTORICAL", category="dimensions")

        assert result["success"] is True
        assert "dimensions" in result
        assert "metrics" not in result

    def test_get_dimensions_metrics_metrics_only(self, mock_gam_client):
        """Test getting metrics only."""
        from applications.mcp_server.services import ReportService

        service = ReportService(client=mock_gam_client)
        result = service.get_dimensions_metrics(report_type="HISTORICAL", category="metrics")

        assert result["success"] is True
        assert "metrics" in result
        assert "dimensions" not in result

    def test_get_dimensions_metrics_reach_report(self, mock_gam_client):
        """Test getting metrics for REACH report type includes reach-specific metrics."""
        from applications.mcp_server.services import ReportService

        service = ReportService(client=mock_gam_client)
        result = service.get_dimensions_metrics(report_type="REACH", category="metrics")

        assert result["success"] is True
        assert "metrics" in result
        # REACH reports should include reach-specific metrics
        assert isinstance(result["metrics"], list)

    def test_get_common_combinations(self, mock_gam_client):
        """Test getting common dimension-metric combinations."""
        from applications.mcp_server.services import ReportService

        service = ReportService(client=mock_gam_client)
        result = service.get_common_combinations()

        assert result["success"] is True
        assert "combinations" in result
        combinations = result["combinations"]

        # Verify expected combinations exist
        assert "delivery_analysis" in combinations
        assert "inventory_analysis" in combinations
        assert "revenue_analysis" in combinations

        # Verify structure of combinations
        for combo_name, combo_data in combinations.items():
            assert "description" in combo_data
            assert "dimensions" in combo_data
            assert "metrics" in combo_data
            assert isinstance(combo_data["dimensions"], list)
            assert isinstance(combo_data["metrics"], list)

    def test_get_quick_report_types(self, mock_gam_client):
        """Test getting available quick report types."""
        from applications.mcp_server.services import ReportService

        service = ReportService(client=mock_gam_client)
        result = service.get_quick_report_types()

        assert result["success"] is True
        assert "quick_report_types" in result
        types = result["quick_report_types"]

        # Verify all expected report types exist
        expected_types = {"delivery", "inventory", "sales", "reach", "programmatic"}
        assert set(types.keys()) == expected_types

        # Verify structure of each type
        for type_name, type_data in types.items():
            assert "name" in type_data
            assert "description" in type_data
            assert isinstance(type_data["name"], str)
            assert isinstance(type_data["description"], str)
