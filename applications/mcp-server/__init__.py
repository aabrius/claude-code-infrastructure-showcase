"""
Google Ad Manager MCP Server.

A FastMCP server providing AI assistants with tools to interact with
Google Ad Manager for report generation and metadata access.
"""

# Lazy imports to avoid loading FastMCP at module import time
# This allows other modules (like dependencies) to be imported without FastMCP

__all__ = [
    "create_mcp_server",
    "get_server",
    "MCPSettings",
    "get_settings",
]

__version__ = "2.0.0"


def __getattr__(name):
    """Lazy import to avoid FastMCP dependency at module load time."""
    if name in ("create_mcp_server", "get_server"):
        from server import create_mcp_server, get_server
        return {"create_mcp_server": create_mcp_server, "get_server": get_server}[name]
    elif name in ("MCPSettings", "get_settings"):
        from settings import MCPSettings, get_settings
        return {"MCPSettings": MCPSettings, "get_settings": get_settings}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")