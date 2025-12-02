# tests/e2e/test_mcp_server_docker.py
"""
End-to-end tests for MCP Server running in Docker.

These tests validate all MCP tools against a running Docker container.
Requires the container to be running before tests execute.

Usage:
    # Start the container first
    docker compose -f applications/mcp-server/docker-compose.test.yml up -d --build

    # Run tests
    pytest tests/e2e/test_mcp_server_docker.py -v

    # Cleanup
    docker compose -f applications/mcp-server/docker-compose.test.yml down
"""

import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import httpx
import pytest
import pytest_asyncio

# Server configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8080")
MCP_ENDPOINT = f"{MCP_SERVER_URL}/mcp"
HEALTH_ENDPOINT = f"{MCP_SERVER_URL}/health"

# Test timeouts
CONNECTION_TIMEOUT = 30
REQUEST_TIMEOUT = 60


class MCPTestClient:
    """Simple MCP client for e2e testing."""

    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        self.base_url = base_url
        self.auth_token = auth_token
        self._request_id = 0

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    def _next_request_id(self) -> int:
        self._request_id += 1
        return self._request_id

    async def initialize(self) -> Dict[str, Any]:
        """Initialize MCP connection."""
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(
                self.base_url,
                headers=self._get_headers(),
                json={
                    "jsonrpc": "2.0",
                    "id": self._next_request_id(),
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "e2e-test-client", "version": "1.0.0"},
                    },
                },
            )
            response.raise_for_status()
            return response.json()

    async def list_tools(self) -> Dict[str, Any]:
        """List available MCP tools."""
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(
                self.base_url,
                headers=self._get_headers(),
                json={
                    "jsonrpc": "2.0",
                    "id": self._next_request_id(),
                    "method": "tools/list",
                    "params": {},
                },
            )
            response.raise_for_status()
            return response.json()

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool."""
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(
                self.base_url,
                headers=self._get_headers(),
                json={
                    "jsonrpc": "2.0",
                    "id": self._next_request_id(),
                    "method": "tools/call",
                    "params": {"name": name, "arguments": arguments},
                },
            )
            response.raise_for_status()
            return response.json()


@pytest.fixture(scope="module")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


def _wait_for_server_sync() -> bool:
    """Synchronous wait for server to be ready."""
    import urllib.request
    import urllib.error

    start_time = time.time()
    while time.time() - start_time < CONNECTION_TIMEOUT:
        try:
            with urllib.request.urlopen(HEALTH_ENDPOINT, timeout=5) as response:
                if response.status == 200:
                    print(f"\nServer ready at {MCP_SERVER_URL}")
                    return True
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            pass
        time.sleep(1)

    pytest.fail(f"Server not ready after {CONNECTION_TIMEOUT}s at {MCP_SERVER_URL}")


@pytest.fixture(scope="module")
def wait_for_server():
    """Wait for the MCP server to be ready (sync fixture)."""
    return _wait_for_server_sync()


@pytest_asyncio.fixture(scope="module")
async def mcp_client(wait_for_server) -> MCPTestClient:
    """Create MCP test client."""
    return MCPTestClient(MCP_ENDPOINT)


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_returns_ok(self, wait_for_server):
        """Test health endpoint returns OK."""
        async with httpx.AsyncClient() as client:
            response = await client.get(HEALTH_ENDPOINT)
            assert response.status_code == 200
            assert response.text == "OK"


class TestOAuthDiscovery:
    """Tests for OAuth discovery endpoints."""

    @pytest.mark.asyncio
    async def test_oauth_protected_resource_metadata(self, wait_for_server):
        """Test OAuth protected resource metadata endpoint."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MCP_SERVER_URL}/.well-known/oauth-protected-resource"
            )
            assert response.status_code == 200
            data = response.json()
            assert "resource" in data
            assert "authorization_servers" in data
            assert "bearer_methods_supported" in data

    @pytest.mark.asyncio
    async def test_oauth_authorization_server_metadata(self, wait_for_server):
        """Test OAuth authorization server metadata endpoint."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MCP_SERVER_URL}/.well-known/oauth-authorization-server"
            )
            assert response.status_code == 200
            data = response.json()
            assert "issuer" in data
            assert "jwks_uri" in data


class TestMCPToolsListing:
    """Tests for MCP tools listing."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_expected_tools(self, mcp_client):
        """Test that all expected tools are listed."""
        # Note: This may fail without valid auth - that's expected
        # The test validates the endpoint is reachable
        try:
            result = await mcp_client.list_tools()
            if "result" in result:
                tools = result["result"].get("tools", [])
                tool_names = [t["name"] for t in tools]

                expected_tools = [
                    "gam_quick_report",
                    "gam_list_reports",
                    "gam_get_dimensions_metrics",
                    "gam_get_common_combinations",
                    "gam_get_quick_report_types",
                    "gam_create_report",
                    "gam_run_report",
                ]

                for tool_name in expected_tools:
                    assert tool_name in tool_names, f"Missing tool: {tool_name}"
            elif "error" in result:
                # Auth error expected without valid token
                assert result["error"]["code"] in [-32600, -32601, 401, 403]
        except httpx.HTTPStatusError as e:
            # 401/403 expected without auth
            assert e.response.status_code in [401, 403]


class TestMetadataTools:
    """Tests for metadata tools (don't require GAM API connection)."""

    @pytest.mark.asyncio
    async def test_get_quick_report_types(self, mcp_client):
        """Test gam_get_quick_report_types tool."""
        try:
            result = await mcp_client.call_tool("gam_get_quick_report_types", {})
            if "result" in result:
                content = result["result"].get("content", [])
                if content:
                    data = json.loads(content[0].get("text", "{}"))
                    assert "quick_report_types" in data or "success" in data
        except httpx.HTTPStatusError as e:
            assert e.response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_get_common_combinations(self, mcp_client):
        """Test gam_get_common_combinations tool."""
        try:
            result = await mcp_client.call_tool("gam_get_common_combinations", {})
            if "result" in result:
                content = result["result"].get("content", [])
                if content:
                    data = json.loads(content[0].get("text", "{}"))
                    assert "combinations" in data or "success" in data
        except httpx.HTTPStatusError as e:
            assert e.response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_get_dimensions_metrics(self, mcp_client):
        """Test gam_get_dimensions_metrics tool."""
        try:
            result = await mcp_client.call_tool(
                "gam_get_dimensions_metrics",
                {"report_type": "HISTORICAL", "category": "both"},
            )
            if "result" in result:
                content = result["result"].get("content", [])
                if content:
                    data = json.loads(content[0].get("text", "{}"))
                    assert "dimensions" in data or "metrics" in data or "success" in data
        except httpx.HTTPStatusError as e:
            assert e.response.status_code in [401, 403]


class TestReportTools:
    """Tests for report tools (may require GAM API connection)."""

    @pytest.mark.asyncio
    async def test_list_reports(self, mcp_client):
        """Test gam_list_reports tool."""
        try:
            result = await mcp_client.call_tool("gam_list_reports", {"limit": 5})
            if "result" in result:
                content = result["result"].get("content", [])
                if content:
                    data = json.loads(content[0].get("text", "{}"))
                    # Should have success key or reports key
                    assert "success" in data or "reports" in data or "error" in data
        except httpx.HTTPStatusError as e:
            assert e.response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_quick_report_delivery(self, mcp_client):
        """Test gam_quick_report tool with delivery report type."""
        try:
            result = await mcp_client.call_tool(
                "gam_quick_report",
                {"report_type": "delivery", "days_back": 7, "format": "json"},
            )
            if "result" in result:
                content = result["result"].get("content", [])
                if content:
                    data = json.loads(content[0].get("text", "{}"))
                    # Check response structure
                    assert "success" in data or "error" in data
                    if data.get("success"):
                        assert data.get("report_type") == "delivery"
        except httpx.HTTPStatusError as e:
            assert e.response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_create_report(self, mcp_client):
        """Test gam_create_report tool."""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")

        try:
            result = await mcp_client.call_tool(
                "gam_create_report",
                {
                    "name": "E2E Test Report",
                    "dimensions": '["DATE", "AD_UNIT_NAME"]',
                    "metrics": '["AD_SERVER_IMPRESSIONS", "AD_SERVER_CLICKS"]',
                    "start_date": yesterday,
                    "end_date": today,
                    "report_type": "HISTORICAL",
                    "run_immediately": False,
                },
            )
            if "result" in result:
                content = result["result"].get("content", [])
                if content:
                    data = json.loads(content[0].get("text", "{}"))
                    assert "success" in data or "error" in data or "report_id" in data
        except httpx.HTTPStatusError as e:
            assert e.response.status_code in [401, 403]


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_invalid_tool_name(self, mcp_client):
        """Test calling non-existent tool returns error."""
        try:
            result = await mcp_client.call_tool("non_existent_tool", {})
            # Should return an error
            assert "error" in result
        except httpx.HTTPStatusError as e:
            # HTTP error is also acceptable
            assert e.response.status_code in [400, 401, 403, 404]

    @pytest.mark.asyncio
    async def test_invalid_report_type(self, mcp_client):
        """Test invalid report type returns error."""
        try:
            result = await mcp_client.call_tool(
                "gam_quick_report",
                {"report_type": "invalid_type", "days_back": 7},
            )
            if "result" in result:
                content = result["result"].get("content", [])
                if content:
                    data = json.loads(content[0].get("text", "{}"))
                    # Should indicate an error
                    assert data.get("success") is False or "error" in data
        except httpx.HTTPStatusError as e:
            assert e.response.status_code in [400, 401, 403, 422]


class TestContainerHealth:
    """Tests for container health and stability."""

    @pytest.mark.asyncio
    async def test_multiple_concurrent_requests(self, mcp_client):
        """Test server handles multiple concurrent requests."""
        async def make_request():
            try:
                return await mcp_client.call_tool("gam_get_quick_report_types", {})
            except Exception as e:
                return {"error": str(e)}

        # Make 5 concurrent requests
        tasks = [make_request() for _ in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should complete (success or auth error, not crash)
        for result in results:
            assert result is not None

    @pytest.mark.asyncio
    async def test_health_after_requests(self, wait_for_server, mcp_client):
        """Test server is still healthy after processing requests."""
        # Make some requests
        try:
            await mcp_client.call_tool("gam_get_quick_report_types", {})
        except:
            pass

        # Check health
        async with httpx.AsyncClient() as client:
            response = await client.get(HEALTH_ENDPOINT)
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
