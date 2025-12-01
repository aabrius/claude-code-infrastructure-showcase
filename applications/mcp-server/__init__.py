"""
Google Ad Manager MCP Server.

A FastMCP server providing AI assistants with tools to interact with
Google Ad Manager for report generation and metadata access.
"""

from server import create_mcp_server, get_server
from settings import MCPSettings, get_settings

__all__ = [
    "create_mcp_server",
    "get_server",
    "MCPSettings",
    "get_settings",
]

__version__ = "2.0.0"