"""Pytest fixtures for e2e tests."""

import os
import time
import pytest
import httpx
from typing import Generator


@pytest.fixture(scope="session")
def server_url() -> str:
    """MCP server base URL for e2e tests."""
    return os.environ.get("MCP_SERVER_URL", "http://localhost:8080")


@pytest.fixture(scope="session")
def mcp_endpoint(server_url: str) -> str:
    """MCP endpoint URL."""
    return f"{server_url}/mcp"


@pytest.fixture(scope="session")
def health_endpoint(server_url: str) -> str:
    """Health check endpoint URL."""
    return f"{server_url}/health"


@pytest.fixture(scope="session")
def http_client() -> Generator[httpx.Client, None, None]:
    """HTTP client for making requests to MCP server."""
    client = httpx.Client(timeout=30.0)
    yield client
    client.close()


@pytest.fixture(scope="session")
def wait_for_server(health_endpoint: str, http_client: httpx.Client) -> None:
    """Wait for server to be ready before running tests."""
    max_retries = 30
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            response = http_client.get(health_endpoint)
            if response.status_code == 200:
                print(f"\n✓ Server is ready at {health_endpoint}")
                return
        except httpx.ConnectError:
            pass

        if attempt < max_retries - 1:
            time.sleep(retry_delay)

    pytest.fail(f"Server not ready after {max_retries} attempts")


@pytest.fixture(autouse=True, scope="session")
def setup_session(wait_for_server):
    """Auto-use fixture to wait for server before any tests run."""
    pass


@pytest.fixture(scope="session")
def mcp_session_id(
    http_client: httpx.Client, mcp_endpoint: str, wait_for_server
) -> str:
    """Initialize MCP session and return session ID.

    FastMCP HTTP transport requires session initialization via
    the 'initialize' JSON-RPC method. The session ID is returned
    in the 'mcp-session-id' response header.
    """
    # MCP initialize request per protocol spec
    initialize_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "e2e-test-client",
                "version": "1.0.0"
            }
        }
    }

    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
    }

    try:
        response = http_client.post(mcp_endpoint, json=initialize_payload, headers=headers)

        if response.status_code == 200:
            # Extract session ID from response header (MCP protocol spec)
            session_id = response.headers.get("mcp-session-id") or response.headers.get("Mcp-Session-Id")
            if session_id:
                print(f"\n✓ MCP session initialized: {session_id}")
                return session_id
            else:
                raise Exception("Server returned 200 but no mcp-session-id header found")

        raise Exception(f"Initialize failed with status {response.status_code}: {response.text}")
    except Exception as e:
        pytest.fail(f"MCP session initialization failed: {e}")
