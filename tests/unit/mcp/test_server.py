"""Unit tests for refactored MCP server."""

import pytest
import sys
from unittest.mock import Mock, patch, AsyncMock, MagicMock


# Mock FastMCP before importing server module
@pytest.fixture(autouse=True)
def mock_fastmcp():
    """Mock FastMCP module for all tests."""
    mock_mcp = MagicMock()
    mock_context = MagicMock()

    # Create mock FastMCP class
    class MockFastMCP:
        def __init__(self, name, auth=None, lifespan=None):
            self.name = name
            self.auth = auth
            self.lifespan = lifespan
            self._tools = {}
            self._tool_counter = 0

        def tool(self, func):
            """Decorator to register tools."""
            tool_mock = Mock()
            tool_mock.name = func.__name__
            self._tools[self._tool_counter] = tool_mock
            self._tool_counter += 1
            return func

    mock_mcp.FastMCP = MockFastMCP
    mock_mcp.Context = mock_context

    # Mock the fastmcp module
    sys.modules['fastmcp'] = mock_mcp

    yield mock_mcp

    # Cleanup
    if 'fastmcp' in sys.modules:
        del sys.modules['fastmcp']


class TestMCPServerCreation:
    """Tests for MCP server creation."""

    def test_create_server_without_auth(self, mock_fastmcp):
        """Test creating server without authentication."""
        with patch("server.get_settings") as mock_settings:
            with patch("server.create_auth_provider") as mock_auth:
                mock_settings.return_value = Mock(auth_enabled=False, transport="stdio")
                mock_auth.return_value = None

                from applications.mcp_server.server import create_mcp_server

                server = create_mcp_server()

                assert server is not None
                assert server.name == "Google Ad Manager API"

    def test_server_has_required_tools(self, mock_fastmcp):
        """Test server registers all required tools."""
        with patch("server.get_settings") as mock_settings:
            with patch("server.create_auth_provider") as mock_auth:
                mock_settings.return_value = Mock(auth_enabled=False, transport="stdio")
                mock_auth.return_value = None

                from applications.mcp_server.server import create_mcp_server

                server = create_mcp_server()

                # Check tool names
                tool_names = [t.name for t in server._tools.values()]

                assert "gam_quick_report" in tool_names
                assert "gam_list_reports" in tool_names
                assert "gam_get_dimensions_metrics" in tool_names
                assert "gam_get_common_combinations" in tool_names
                assert "gam_get_quick_report_types" in tool_names


class TestQuickReportTool:
    """Tests for gam_quick_report tool."""

    @pytest.mark.asyncio
    async def test_quick_report_delegates_to_service(self, mock_fastmcp):
        """Test quick report tool delegates to ReportService."""
        mock_service = Mock()
        mock_service.quick_report = Mock(return_value={
            "success": True,
            "report_type": "delivery",
            "total_rows": 100,
        })

        mock_ctx = Mock()
        mock_ctx.app.state.report_service = mock_service

        from applications.mcp_server.server import _gam_quick_report

        result = await _gam_quick_report(
            report_type="delivery",
            days_back=7,
            format="json",
            ctx=mock_ctx
        )

        mock_service.quick_report.assert_called_once_with(
            "delivery", days_back=7, format="json"
        )
        assert '"success": true' in result
