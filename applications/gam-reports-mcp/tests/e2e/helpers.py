"""Helper functions for e2e tests."""

from typing import Any, Dict
import httpx


def json_rpc_request(
    client: httpx.Client,
    mcp_endpoint: str,
    method: str,
    params: Dict[str, Any] | None = None,
    request_id: int = 1,
    session_id: str | None = None,
) -> httpx.Response:
    """Make a JSON-RPC 2.0 request to the MCP endpoint.

    Note: session_id is kept for compatibility but FastMCP handles
    sessions automatically via HTTP transport.
    """
    payload = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
    }
    if params is not None:
        payload["params"] = params

    # MCP Streamable HTTP requires these Accept headers
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
    }

    # Include session ID only if explicitly provided
    # (FastMCP manages sessions automatically)
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    return client.post(mcp_endpoint, json=payload, headers=headers)


def call_tool(
    client: httpx.Client,
    mcp_endpoint: str,
    tool_name: str,
    params: Dict[str, Any] | None = None,
    session_id: str | None = None,
) -> httpx.Response:
    """Call an MCP tool using JSON-RPC."""
    tool_params = {"name": tool_name}
    if params:
        tool_params["arguments"] = params

    return json_rpc_request(client, mcp_endpoint, "tools/call", tool_params, session_id=session_id)


def get_tools(client: httpx.Client, mcp_endpoint: str, session_id: str | None = None) -> httpx.Response:
    """Get list of available MCP tools using JSON-RPC."""
    return json_rpc_request(client, mcp_endpoint, "tools/list", session_id=session_id)


def get_resources(client: httpx.Client, mcp_endpoint: str, session_id: str | None = None) -> httpx.Response:
    """Get list of available MCP resources using JSON-RPC."""
    return json_rpc_request(client, mcp_endpoint, "resources/list", session_id=session_id)


def read_resource(
    client: httpx.Client, mcp_endpoint: str, resource_uri: str, session_id: str | None = None
) -> httpx.Response:
    """Read an MCP resource by URI using JSON-RPC."""
    return json_rpc_request(
        client, mcp_endpoint, "resources/read", {"uri": resource_uri}, session_id=session_id
    )


def assert_json_rpc_success(response: httpx.Response, method: str) -> Dict[str, Any]:
    """Assert JSON-RPC response is successful and return the result."""
    assert response.status_code == 200, (
        f"JSON-RPC '{method}' failed with status {response.status_code}: {response.text}"
    )

    # Handle Server-Sent Events (SSE) format
    # Response format: "event: message\ndata: {...}\n\n"
    text = response.text
    if text.startswith("event:"):
        # Parse SSE format - extract JSON from "data:" lines
        import json
        for line in text.split("\n"):
            if line.startswith("data: "):
                data = json.loads(line[6:])  # Skip "data: " prefix
                break
        else:
            raise AssertionError(f"No data line found in SSE response: {text[:200]}")
    else:
        # Plain JSON response
        data = response.json()

    # Check for JSON-RPC error
    if "error" in data:
        error = data["error"]
        error_msg = error.get("message", "Unknown error")
        raise AssertionError(
            f"JSON-RPC '{method}' returned error {error.get('code', 'N/A')}: {error_msg}"
        )

    # Return the result
    assert "result" in data, f"JSON-RPC response missing 'result' field: {data}"
    return data["result"]


def assert_tool_response_success(
    response: httpx.Response, tool_name: str
) -> Dict[str, Any]:
    """Assert tool response is successful and return the result."""
    result = assert_json_rpc_success(response, f"tools/call:{tool_name}")

    # MCP tools/call returns result with 'content' array
    # Extract the actual tool response from content[0]
    if isinstance(result, dict) and "content" in result:
        content = result["content"]
        if isinstance(content, list) and len(content) > 0:
            first_content = content[0]
            if "text" in first_content:
                # Try to parse as JSON if it looks like JSON
                import json

                try:
                    return json.loads(first_content["text"])
                except json.JSONDecodeError:
                    return {"text": first_content["text"]}
            return first_content
        return result
    return result


def assert_resource_response_success(
    response: httpx.Response, resource_uri: str
) -> Dict[str, Any]:
    """Assert resource response is successful and return the result."""
    result = assert_json_rpc_success(response, f"resources/read:{resource_uri}")

    # MCP resources/read returns result with 'contents' array
    # Extract the actual resource data from contents[0]
    if isinstance(result, dict) and "contents" in result:
        contents = result["contents"]
        if isinstance(contents, list) and len(contents) > 0:
            first_content = contents[0]
            if "text" in first_content:
                # Try to parse as JSON if it looks like JSON
                import json

                try:
                    return json.loads(first_content["text"])
                except json.JSONDecodeError:
                    return {"text": first_content["text"]}
            return first_content
        return result
    return result
