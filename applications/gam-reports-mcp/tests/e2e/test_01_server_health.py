"""E2E tests for server health and basic endpoints."""

import pytest
import httpx
from .helpers import get_tools, get_resources, assert_json_rpc_success


class TestServerHealth:
    """Test server health and availability."""

    def test_health_endpoint_returns_ok(
        self, http_client: httpx.Client, health_endpoint: str
    ):
        """Health endpoint should return 200 OK."""
        response = http_client.get(health_endpoint)
        assert response.status_code == 200
        assert response.text == "OK"

    def test_health_endpoint_is_fast(
        self, http_client: httpx.Client, health_endpoint: str
    ):
        """Health check should respond quickly (< 500ms)."""
        response = http_client.get(health_endpoint)
        assert response.elapsed.total_seconds() < 0.5


class TestMCPDiscovery:
    """Test MCP server discovery endpoints."""

    def test_list_tools_endpoint(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """Should list all available MCP tools."""
        response = get_tools(http_client, mcp_endpoint, mcp_session_id)
        result = assert_json_rpc_success(response, "tools/list")

        assert "tools" in result
        tools = result["tools"]
        assert isinstance(tools, list)
        assert len(tools) == 7, f"Expected 7 tools, got {len(tools)}"

        # Check required tool names
        tool_names = {tool["name"] for tool in tools}
        expected_tools = {
            "search",
            "create_report",
            "run_and_fetch_report",
            "get_available_options",
            "list_saved_reports",
            "update_report",
            "delete_report",
        }
        assert tool_names == expected_tools

    def test_list_resources_endpoint(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """Should list all available MCP resources."""
        response = get_resources(http_client, mcp_endpoint, mcp_session_id)
        result = assert_json_rpc_success(response, "resources/list")

        assert "resources" in result
        resources = result["resources"]
        assert isinstance(resources, list)
        assert len(resources) == 4, f"Expected 4 resources, got {len(resources)}"

        # Check required resource URIs
        resource_uris = {resource["uri"] for resource in resources}
        expected_resources = {
            "gam://context",
            "gam://dimensions",
            "gam://metrics",
            "gam://templates",
        }
        assert resource_uris == expected_resources

    def test_each_tool_has_required_fields(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """Each tool should have name, description, and inputSchema."""
        response = get_tools(http_client, mcp_endpoint, mcp_session_id)
        result = assert_json_rpc_success(response, "tools/list")
        tools = result["tools"]

        for tool in tools:
            assert "name" in tool, f"Tool missing 'name': {tool}"
            assert "description" in tool, f"Tool missing 'description': {tool}"
            assert "inputSchema" in tool, f"Tool missing 'inputSchema': {tool}"

            # Verify inputSchema structure
            schema = tool["inputSchema"]
            assert "type" in schema
            assert schema["type"] == "object"

    def test_each_resource_has_required_fields(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """Each resource should have uri, name, and mimeType."""
        response = get_resources(http_client, mcp_endpoint, mcp_session_id)
        result = assert_json_rpc_success(response, "resources/list")
        resources = result["resources"]

        for resource in resources:
            assert "uri" in resource, f"Resource missing 'uri': {resource}"
            assert "name" in resource, f"Resource missing 'name': {resource}"
            # mimeType is optional but commonly included
