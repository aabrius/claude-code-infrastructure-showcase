"""Unit tests for refactored MCP server."""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock


class TestToolImplementations:
    """Tests for tool implementation functions."""

    @pytest.mark.asyncio
    async def test_quick_report_delegates_to_service(self):
        """Test quick report tool delegates to ReportService."""
        # Import the implementation function directly
        from applications.mcp_server.server import _gam_quick_report

        mock_service = Mock()
        mock_service.quick_report = Mock(return_value={
            "success": True,
            "report_type": "delivery",
            "total_rows": 100,
        })

        mock_ctx = Mock()
        mock_ctx.fastmcp.report_service = mock_service

        result = await _gam_quick_report(
            report_type="delivery",
            days_back=7,
            format="json",
            ctx=mock_ctx
        )

        mock_service.quick_report.assert_called_once_with(
            "delivery", days_back=7, format="json"
        )
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_quick_report_handles_validation_error(self):
        """Test quick report handles ValueError with error response."""
        from applications.mcp_server.server import _gam_quick_report

        mock_service = Mock()
        mock_service.quick_report = Mock(side_effect=ValueError("Unknown report type"))

        mock_ctx = Mock()
        mock_ctx.fastmcp.report_service = mock_service

        result = await _gam_quick_report(
            report_type="invalid",
            days_back=7,
            format="json",
            ctx=mock_ctx
        )

        parsed = json.loads(result)
        assert parsed["success"] is False
        assert "ValidationError" in parsed["error"]["type"]

    @pytest.mark.asyncio
    async def test_list_reports_delegates_to_service(self):
        """Test list reports tool delegates to ReportService."""
        from applications.mcp_server.server import _gam_list_reports

        mock_service = Mock()
        mock_service.list_reports = Mock(return_value={
            "success": True,
            "reports": [{"id": "1", "name": "Test"}],
        })

        mock_ctx = Mock()
        mock_ctx.fastmcp.report_service = mock_service

        result = await _gam_list_reports(limit=20, ctx=mock_ctx)

        mock_service.list_reports.assert_called_once_with(limit=20)
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_dimensions_metrics_delegates_to_service(self):
        """Test get_dimensions_metrics tool delegates to ReportService."""
        from applications.mcp_server.server import _gam_get_dimensions_metrics

        mock_service = Mock()
        mock_service.get_dimensions_metrics = Mock(return_value={
            "dimensions": ["DATE", "AD_UNIT_NAME"],
            "metrics": ["IMPRESSIONS", "CLICKS"],
        })

        mock_ctx = Mock()
        mock_ctx.fastmcp.report_service = mock_service

        result = await _gam_get_dimensions_metrics(
            report_type="HISTORICAL",
            category="both",
            ctx=mock_ctx
        )

        mock_service.get_dimensions_metrics.assert_called_once_with("HISTORICAL", "both")
        parsed = json.loads(result)
        assert "dimensions" in parsed
        assert "metrics" in parsed

    @pytest.mark.asyncio
    async def test_get_common_combinations_delegates_to_service(self):
        """Test get_common_combinations tool delegates to ReportService."""
        from applications.mcp_server.server import _gam_get_common_combinations

        mock_service = Mock()
        mock_service.get_common_combinations = Mock(return_value={
            "combinations": [{"name": "test", "dimensions": [], "metrics": []}],
        })

        mock_ctx = Mock()
        mock_ctx.fastmcp.report_service = mock_service

        result = await _gam_get_common_combinations(ctx=mock_ctx)

        mock_service.get_common_combinations.assert_called_once()
        parsed = json.loads(result)
        assert "combinations" in parsed

    @pytest.mark.asyncio
    async def test_get_quick_report_types_delegates_to_service(self):
        """Test get_quick_report_types tool delegates to ReportService."""
        from applications.mcp_server.server import _gam_get_quick_report_types

        mock_service = Mock()
        mock_service.get_quick_report_types = Mock(return_value={
            "quick_report_types": {
                "delivery": {"description": "Delivery report"},
                "inventory": {"description": "Inventory report"},
            },
        })

        mock_ctx = Mock()
        mock_ctx.fastmcp.report_service = mock_service

        result = await _gam_get_quick_report_types(ctx=mock_ctx)

        mock_service.get_quick_report_types.assert_called_once()
        parsed = json.loads(result)
        assert "quick_report_types" in parsed


class TestToolErrorHandling:
    """Tests for error handling in tool implementations."""

    @pytest.mark.asyncio
    async def test_list_reports_handles_exception(self):
        """Test list reports returns error response on exception."""
        from applications.mcp_server.server import _gam_list_reports

        mock_service = Mock()
        mock_service.list_reports = Mock(side_effect=Exception("API error"))

        mock_ctx = Mock()
        mock_ctx.fastmcp.report_service = mock_service

        result = await _gam_list_reports(limit=20, ctx=mock_ctx)

        parsed = json.loads(result)
        assert parsed["success"] is False
        assert "InternalError" in parsed["error"]["type"]

    @pytest.mark.asyncio
    async def test_get_dimensions_metrics_handles_exception(self):
        """Test get_dimensions_metrics returns error response on exception."""
        from applications.mcp_server.server import _gam_get_dimensions_metrics

        mock_service = Mock()
        mock_service.get_dimensions_metrics = Mock(side_effect=Exception("API error"))

        mock_ctx = Mock()
        mock_ctx.fastmcp.report_service = mock_service

        result = await _gam_get_dimensions_metrics(
            report_type="HISTORICAL",
            category="both",
            ctx=mock_ctx
        )

        parsed = json.loads(result)
        assert parsed["success"] is False

    @pytest.mark.asyncio
    async def test_get_common_combinations_handles_exception(self):
        """Test get_common_combinations returns error response on exception."""
        from applications.mcp_server.server import _gam_get_common_combinations

        mock_service = Mock()
        mock_service.get_common_combinations = Mock(side_effect=Exception("API error"))

        mock_ctx = Mock()
        mock_ctx.fastmcp.report_service = mock_service

        result = await _gam_get_common_combinations(ctx=mock_ctx)

        parsed = json.loads(result)
        assert parsed["success"] is False

    @pytest.mark.asyncio
    async def test_get_quick_report_types_handles_exception(self):
        """Test get_quick_report_types returns error response on exception."""
        from applications.mcp_server.server import _gam_get_quick_report_types

        mock_service = Mock()
        mock_service.get_quick_report_types = Mock(side_effect=Exception("API error"))

        mock_ctx = Mock()
        mock_ctx.fastmcp.report_service = mock_service

        result = await _gam_get_quick_report_types(ctx=mock_ctx)

        parsed = json.loads(result)
        assert parsed["success"] is False
