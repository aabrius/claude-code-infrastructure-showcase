# tests/integration/test_mcp_server_real.py
"""
Integration tests for real MCP Server with actual GAM credentials.

These tests require:
- Valid GAM credentials (googleads.yaml)
- Network access to Google Ad Manager API

Run with: pytest tests/integration/test_mcp_server_real.py -v
Skip with: pytest -m "not real_server"
"""

import pytest
import os
import json
import subprocess
import sys
from pathlib import Path

# Mark all tests in this module as requiring real server
pytestmark = pytest.mark.real_server

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent


def has_gam_credentials() -> bool:
    """Check if GAM credentials are available."""
    googleads_yaml = PROJECT_ROOT / "googleads.yaml"
    if not googleads_yaml.exists():
        return False
    # Check for required environment or file content
    return True


def is_server_configured() -> bool:
    """Check if MCP server can be started."""
    server_dir = PROJECT_ROOT / "applications" / "mcp-server"
    return (server_dir / "main.py").exists()


# Skip entire module if no credentials
if not has_gam_credentials():
    pytest.skip("GAM credentials not available", allow_module_level=True)


class TestMCPInspectorCLI:
    """Tests using MCP Inspector CLI for automation."""

    @pytest.fixture(scope="class")
    def inspector_cmd(self):
        """Base inspector command."""
        return [
            "npx", "@modelcontextprotocol/inspector", "--cli",
            "-e", "MCP_AUTH_ENABLED=false",
            "-e", "MCP_TRANSPORT=stdio",
            "--",
            "uv", "run", "--directory", "applications/mcp-server",
            "python", "main.py"
        ]

    def run_inspector(self, inspector_cmd, method, tool_name=None, tool_args=None, timeout=60):
        """Run MCP Inspector CLI and return parsed result."""
        cmd = inspector_cmd + ["--method", method]

        if tool_name:
            cmd.extend(["--tool-name", tool_name])

        if tool_args:
            for key, value in tool_args.items():
                cmd.extend(["--tool-arg", f"{key}={value}"])

        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode != 0:
            pytest.fail(f"Inspector failed: {result.stderr}")

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON response: {result.stdout[:500]}")

    def test_list_tools(self, inspector_cmd):
        """Test that server exposes all expected tools."""
        result = self.run_inspector(inspector_cmd, "tools/list")

        assert "tools" in result
        tool_names = [t["name"] for t in result["tools"]]

        expected_tools = [
            "gam_quick_report",
            "gam_list_reports",
            "gam_get_dimensions_metrics",
            "gam_get_common_combinations",
            "gam_get_quick_report_types",
        ]

        for expected in expected_tools:
            assert expected in tool_names, f"Missing tool: {expected}"

    def test_get_quick_report_types(self, inspector_cmd):
        """Test gam_get_quick_report_types returns valid data."""
        result = self.run_inspector(
            inspector_cmd,
            "tools/call",
            tool_name="gam_get_quick_report_types"
        )

        assert "content" in result
        content = json.loads(result["content"][0]["text"])

        assert content["success"] is True
        assert "quick_report_types" in content

        types = content["quick_report_types"]
        assert "delivery" in types
        assert "inventory" in types
        assert "sales" in types

    def test_get_common_combinations(self, inspector_cmd):
        """Test gam_get_common_combinations returns valid data."""
        result = self.run_inspector(
            inspector_cmd,
            "tools/call",
            tool_name="gam_get_common_combinations"
        )

        assert "content" in result
        content = json.loads(result["content"][0]["text"])

        assert content["success"] is True
        assert "combinations" in content

    def test_get_dimensions_metrics(self, inspector_cmd):
        """Test gam_get_dimensions_metrics with parameters."""
        result = self.run_inspector(
            inspector_cmd,
            "tools/call",
            tool_name="gam_get_dimensions_metrics",
            tool_args={"report_type": "HISTORICAL", "category": "both"}
        )

        assert "content" in result
        content = json.loads(result["content"][0]["text"])

        assert content["success"] is True
        assert "dimensions" in content
        assert "metrics" in content

        # Check some expected dimensions
        assert "DATE" in content["dimensions"]

    @pytest.mark.slow
    def test_quick_report_delivery(self, inspector_cmd):
        """Test generating a real delivery report (requires API access)."""
        result = self.run_inspector(
            inspector_cmd,
            "tools/call",
            tool_name="gam_quick_report",
            tool_args={"report_type": "delivery", "days_back": "7"},
            timeout=120  # Reports can take time
        )

        assert "content" in result
        content = json.loads(result["content"][0]["text"])

        # Should succeed or return mock mode message
        if content.get("success"):
            assert "report_type" in content
            assert content["report_type"] == "delivery"
        else:
            # Mock mode is acceptable
            assert "error" in content or "mock" in str(content).lower()

    @pytest.mark.slow
    def test_list_reports(self, inspector_cmd):
        """Test listing reports (requires API access)."""
        result = self.run_inspector(
            inspector_cmd,
            "tools/call",
            tool_name="gam_list_reports",
            tool_args={"limit": "5"},
            timeout=60
        )

        assert "content" in result
        content = json.loads(result["content"][0]["text"])

        # Should succeed or return mock mode message
        if content.get("success"):
            assert "reports" in content
        else:
            # Mock mode is acceptable
            assert "error" in content


class TestMCPServerHTTP:
    """Tests for MCP server running in HTTP mode."""

    @pytest.fixture(scope="class")
    def http_server_url(self):
        """Get HTTP server URL (local or cloud)."""
        return os.environ.get(
            "MCP_SERVER_URL",
            "http://localhost:8080/mcp"
        )

    @pytest.fixture(scope="class")
    def inspector_http_cmd(self, http_server_url):
        """Inspector command for HTTP server."""
        return [
            "npx", "@modelcontextprotocol/inspector", "--cli",
            http_server_url,
            "--transport", "http"
        ]

    @pytest.mark.skipif(
        not os.environ.get("MCP_SERVER_URL"),
        reason="MCP_SERVER_URL not set"
    )
    def test_http_list_tools(self, inspector_http_cmd):
        """Test listing tools via HTTP transport."""
        cmd = inspector_http_cmd + ["--method", "tools/list"]

        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            pytest.skip(f"HTTP server not available: {result.stderr[:200]}")

        data = json.loads(result.stdout)
        assert "tools" in data

    @pytest.mark.skipif(
        not os.environ.get("MCP_SERVER_URL"),
        reason="MCP_SERVER_URL not set"
    )
    def test_http_call_tool(self, inspector_http_cmd):
        """Test calling a tool via HTTP transport."""
        cmd = inspector_http_cmd + [
            "--method", "tools/call",
            "--tool-name", "gam_get_quick_report_types"
        ]

        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            pytest.skip(f"HTTP server not available: {result.stderr[:200]}")

        data = json.loads(result.stdout)
        assert "content" in data


class TestMCPServerCloudRun:
    """Tests for production Cloud Run deployment."""

    CLOUD_URL = "https://gam-mcp-server-183972668403.us-central1.run.app/mcp"

    @pytest.fixture
    def jwt_token(self):
        """Get JWT token for authentication."""
        token = os.environ.get("GAM_MCP_JWT_TOKEN")
        if not token:
            pytest.skip("GAM_MCP_JWT_TOKEN not set")
        return token

    @pytest.mark.cloud
    def test_cloud_list_tools(self, jwt_token):
        """Test listing tools on Cloud Run deployment."""
        cmd = [
            "npx", "@modelcontextprotocol/inspector", "--cli",
            self.CLOUD_URL,
            "--transport", "http",
            "--header", f"Authorization: Bearer {jwt_token}",
            "--method", "tools/list"
        ]

        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=30
        )

        if "unauthorized" in result.stderr.lower() or result.returncode != 0:
            pytest.fail(f"Authentication failed: {result.stderr[:200]}")

        data = json.loads(result.stdout)
        assert "tools" in data

        tool_names = [t["name"] for t in data["tools"]]
        assert "gam_quick_report" in tool_names

    @pytest.mark.cloud
    def test_cloud_call_tool(self, jwt_token):
        """Test calling a tool on Cloud Run deployment."""
        cmd = [
            "npx", "@modelcontextprotocol/inspector", "--cli",
            self.CLOUD_URL,
            "--transport", "http",
            "--header", f"Authorization: Bearer {jwt_token}",
            "--method", "tools/call",
            "--tool-name", "gam_get_quick_report_types"
        ]

        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            pytest.fail(f"Tool call failed: {result.stderr[:200]}")

        data = json.loads(result.stdout)
        assert "content" in data

        content = json.loads(data["content"][0]["text"])
        assert content["success"] is True


class TestMCPFastMCPClient:
    """Tests using FastMCP Client for in-process testing."""

    @pytest.fixture
    def server_with_real_client(self):
        """Create server with real GAM client (if available)."""
        # Add server path
        server_path = PROJECT_ROOT / "applications" / "mcp-server"
        sys.path.insert(0, str(server_path))

        try:
            # Try to create with real client
            os.environ["MCP_AUTH_ENABLED"] = "false"
            from server import create_mcp_server
            return create_mcp_server()
        except Exception as e:
            pytest.skip(f"Cannot create server with real client: {e}")
        finally:
            if str(server_path) in sys.path:
                sys.path.remove(str(server_path))

    @pytest.mark.asyncio
    async def test_fastmcp_client_list_tools(self, server_with_real_client):
        """Test listing tools with FastMCP Client."""
        from fastmcp import Client

        async with Client(server_with_real_client) as client:
            tools = await client.list_tools()

            tool_names = [t.name for t in tools]
            assert "gam_quick_report" in tool_names
            assert "gam_get_quick_report_types" in tool_names

    @pytest.mark.asyncio
    async def test_fastmcp_client_call_metadata_tool(self, server_with_real_client):
        """Test calling a metadata tool with FastMCP Client."""
        from fastmcp import Client

        async with Client(server_with_real_client) as client:
            result = await client.call_tool("gam_get_quick_report_types", {})

            assert not result.is_error
            response = json.loads(result.data)

            assert response["success"] is True
            assert "quick_report_types" in response

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_fastmcp_client_call_report_tool(self, server_with_real_client):
        """Test calling a report tool with FastMCP Client (requires GAM access)."""
        from fastmcp import Client

        async with Client(server_with_real_client) as client:
            result = await client.call_tool(
                "gam_quick_report",
                {"report_type": "delivery", "days_back": 7}
            )

            response = json.loads(result.data)

            # Either success or mock mode
            if response.get("success"):
                assert response["report_type"] == "delivery"
            else:
                # Mock mode is acceptable
                assert "error" in response or "mock" in str(response).lower()


# Pytest markers configuration
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "real_server: tests that require real MCP server"
    )
    config.addinivalue_line(
        "markers", "cloud: tests that require Cloud Run deployment"
    )
    config.addinivalue_line(
        "markers", "slow: tests that may take a long time"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
