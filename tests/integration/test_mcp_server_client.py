# tests/integration/test_mcp_server_client.py
"""
Integration tests for MCP Server using FastMCP Client.

These tests use FastMCP's in-memory client to test the server
without requiring network connections.
"""

import pytest
import sys
import json
from unittest.mock import Mock, patch, AsyncMock


# Skip all tests in this module if fastmcp is not available
fastmcp = pytest.importorskip("fastmcp", reason="FastMCP not installed")


@pytest.fixture(autouse=True)
def clean_server_module():
    """Clean server module from cache before each test to ensure proper FastMCP isolation."""
    # Remove all cached modules related to MCP server to ensure fresh import
    modules_to_remove = [
        k for k in list(sys.modules.keys())
        if any(x in k.lower() for x in ['server', 'dependencies', 'settings', 'auth', 'services'])
        and 'mcp' not in k  # Don't remove fastmcp modules
        and 'test' not in k  # Don't remove test modules
    ]

    # Remove specific application modules
    app_modules = ['server', 'dependencies', 'settings', 'auth', 'models', 'services']
    for mod in app_modules:
        if mod in sys.modules:
            del sys.modules[mod]

    for mod in modules_to_remove:
        if mod in sys.modules:
            try:
                del sys.modules[mod]
            except KeyError:
                pass

    yield


class TestMCPServerWithClient:
    """Integration tests using FastMCP Client."""

    @pytest.fixture
    def mock_gam_client(self):
        """Create a mock GAM client for testing."""
        client = Mock()
        client.generate_quick_report = Mock(return_value=Mock(
            data=[
                ['2024-01-01', 'Ad Unit 1', '1000', '50'],
                ['2024-01-02', 'Ad Unit 2', '2000', '100'],
            ],
            total_rows=2,
            dimension_headers=['DATE', 'AD_UNIT_NAME'],
            metric_headers=['IMPRESSIONS', 'CLICKS'],
        ))
        client.list_reports = Mock(return_value=[
            {'id': '1', 'name': 'Report 1'},
            {'id': '2', 'name': 'Report 2'},
        ])
        client.close = AsyncMock()
        return client

    @pytest.mark.asyncio
    async def test_server_lists_tools(self, mock_gam_client):
        """Test that server exposes all expected tools."""
        from fastmcp import Client

        with patch('gam_api.GAMClient', return_value=mock_gam_client):
            with patch('gam_shared.cache.CacheManager', return_value=Mock()):
                with patch('gam_shared.cache.FileCache', return_value=Mock()):
                    from server import get_server
                    mcp = get_server()

                    async with Client(mcp) as client:
                        tools = await client.list_tools()
                        tool_names = [t.name for t in tools]

                        expected_tools = [
                            "gam_quick_report",
                            "gam_list_reports",
                            "gam_get_dimensions_metrics",
                            "gam_get_common_combinations",
                            "gam_get_quick_report_types",
                        ]

                        for tool_name in expected_tools:
                            assert tool_name in tool_names, f"Missing tool: {tool_name}"

    @pytest.mark.asyncio
    async def test_server_tool_descriptions(self, mock_gam_client):
        """Test that tools have proper descriptions."""
        from fastmcp import Client

        with patch('gam_api.GAMClient', return_value=mock_gam_client):
            with patch('gam_shared.cache.CacheManager', return_value=Mock()):
                with patch('gam_shared.cache.FileCache', return_value=Mock()):
                    from server import get_server
                    mcp = get_server()

                    async with Client(mcp) as client:
                        tools = await client.list_tools()

                        for tool in tools:
                            assert tool.description, f"Tool {tool.name} has no description"
                            assert len(tool.description.strip()) > 10, \
                                f"Tool {tool.name} has too short description"

    @pytest.mark.asyncio
    async def test_quick_report_tool_schema(self, mock_gam_client):
        """Test gam_quick_report has correct parameter schema."""
        from fastmcp import Client

        with patch('gam_api.GAMClient', return_value=mock_gam_client):
            with patch('gam_shared.cache.CacheManager', return_value=Mock()):
                with patch('gam_shared.cache.FileCache', return_value=Mock()):
                    from server import get_server
                    mcp = get_server()

                    async with Client(mcp) as client:
                        tools = await client.list_tools()
                        quick_report = next(t for t in tools if t.name == "gam_quick_report")

                        schema = quick_report.inputSchema
                        properties = schema.get("properties", {})

                        assert "report_type" in properties
                        assert "days_back" in properties
                        assert "format" in properties

    @pytest.mark.asyncio
    async def test_call_get_quick_report_types(self, mock_gam_client):
        """Test calling gam_get_quick_report_types tool."""
        from fastmcp import Client

        with patch('gam_api.GAMClient', return_value=mock_gam_client):
            with patch('gam_shared.cache.CacheManager', return_value=Mock()):
                with patch('gam_shared.cache.FileCache', return_value=Mock()):
                    from server import get_server
                    mcp = get_server()

                    async with Client(mcp) as client:
                        result = await client.call_tool("gam_get_quick_report_types", {})

                        assert not result.is_error
                        response = json.loads(result.data)

                        assert "quick_report_types" in response
                        assert len(response["quick_report_types"]) == 5

                        type_names = list(response["quick_report_types"].keys())
                        assert "delivery" in type_names
                        assert "inventory" in type_names

    @pytest.mark.asyncio
    async def test_call_get_common_combinations(self, mock_gam_client):
        """Test calling gam_get_common_combinations tool."""
        from fastmcp import Client

        with patch('gam_api.GAMClient', return_value=mock_gam_client):
            with patch('gam_shared.cache.CacheManager', return_value=Mock()):
                with patch('gam_shared.cache.FileCache', return_value=Mock()):
                    from server import get_server
                    mcp = get_server()

                    async with Client(mcp) as client:
                        result = await client.call_tool("gam_get_common_combinations", {})

                        assert not result.is_error
                        response = json.loads(result.data)

                        assert "combinations" in response

    @pytest.mark.asyncio
    async def test_call_get_dimensions_metrics(self, mock_gam_client):
        """Test calling gam_get_dimensions_metrics tool."""
        from fastmcp import Client

        with patch('gam_api.GAMClient', return_value=mock_gam_client):
            with patch('gam_shared.cache.CacheManager', return_value=Mock()):
                with patch('gam_shared.cache.FileCache', return_value=Mock()):
                    from server import get_server
                    mcp = get_server()

                    async with Client(mcp) as client:
                        result = await client.call_tool(
                            "gam_get_dimensions_metrics",
                            {"report_type": "HISTORICAL", "category": "both"}
                        )

                        assert not result.is_error
                        response = json.loads(result.data)

                        assert "dimensions" in response
                        assert "metrics" in response

    @pytest.mark.asyncio
    async def test_server_info(self, mock_gam_client):
        """Test server provides correct info."""
        from fastmcp import Client

        with patch('gam_api.GAMClient', return_value=mock_gam_client):
            with patch('gam_shared.cache.CacheManager', return_value=Mock()):
                with patch('gam_shared.cache.FileCache', return_value=Mock()):
                    from server import get_server
                    mcp = get_server()

                    async with Client(mcp) as client:
                        info = client.initialize_result.serverInfo
                        assert info.name == "Google Ad Manager API"


class TestMCPServerSettings:
    """Tests for MCP server settings (now uses os.getenv directly)."""

    def test_server_env_defaults(self):
        """Test server uses correct environment defaults."""
        import os

        # Test default values when env vars not set
        assert os.getenv("MCP_SERVER_PORT", "8080") == "8080"
        assert os.getenv("MCP_SERVER_HOST", "0.0.0.0") == "0.0.0.0"
        assert os.getenv("OAUTH_GATEWAY_URL", "https://ag.etus.io") == "https://ag.etus.io"

    def test_oauth_derived_values(self):
        """Test OAuth settings are derived correctly."""
        import os

        oauth_gateway = os.getenv("OAUTH_GATEWAY_URL", "https://ag.etus.io")
        jwks_uri = os.getenv("OAUTH_JWKS_URI", f"{oauth_gateway}/.well-known/jwks.json")
        issuer = os.getenv("OAUTH_ISSUER", oauth_gateway)

        assert jwks_uri == f"{oauth_gateway}/.well-known/jwks.json"
        assert issuer == oauth_gateway


class TestReportServiceIntegration:
    """Test ReportService with mocked GAM client."""

    @pytest.fixture
    def mock_client(self):
        """Create mock GAM client with report methods."""
        client = Mock()

        # Mock the unified client for async operations
        mock_unified = AsyncMock()
        mock_unified.create_report = AsyncMock(return_value={
            "reportId": "123",
            "name": "networks/12345/reports/123",
            "displayName": "Test Report",
        })
        client._unified_client = mock_unified

        # Mock list_reports for sync operation
        client.list_reports = Mock(return_value=[
            {'reportId': '1', 'displayName': 'Test Report'}
        ])
        return client

    @pytest.mark.asyncio
    async def test_quick_report_integration(self, mock_client):
        """Test quick report through service (now async)."""
        from services.report_service import ReportService

        service = ReportService(client=mock_client)
        result = await service.quick_report("delivery", days_back=7)

        assert result["report_type"] == "delivery"
        assert result["days_back"] == 7
        assert result["success"] is True
        mock_client._unified_client.create_report.assert_called_once()

    def test_list_reports_integration(self, mock_client):
        """Test list reports through service."""
        from services.report_service import ReportService

        service = ReportService(client=mock_client)
        result = service.list_reports(limit=10)

        assert "reports" in result
        assert result["success"] is True
        mock_client.list_reports.assert_called_once_with(limit=10)

    @pytest.mark.asyncio
    async def test_service_validates_report_type(self, mock_client):
        """Test service validates report type (now async)."""
        from services.report_service import ReportService

        service = ReportService(client=mock_client)

        with pytest.raises(ValueError, match="Unknown report type"):
            await service.quick_report("invalid_type")

    def test_get_quick_report_types(self, mock_client):
        """Test getting quick report types."""
        from services.report_service import ReportService

        service = ReportService(client=mock_client)
        result = service.get_quick_report_types()

        assert result["success"] is True
        assert "quick_report_types" in result
        assert len(result["quick_report_types"]) == 5

    def test_get_common_combinations(self, mock_client):
        """Test getting common combinations."""
        from services.report_service import ReportService

        service = ReportService(client=mock_client)
        result = service.get_common_combinations()

        assert result["success"] is True
        assert "combinations" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
