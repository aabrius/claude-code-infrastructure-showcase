"""Tests for the MCP server."""

import pytest


def test_server_has_required_tools():
    """Test that server has all 7 required tools."""
    from server import mcp

    tool_names = [tool.name for tool in mcp._tool_manager._tools.values()]

    assert "search" in tool_names
    assert "create_report" in tool_names
    assert "run_and_fetch_report" in tool_names
    assert "get_available_options" in tool_names
    assert "list_saved_reports" in tool_names
    assert "update_report" in tool_names
    assert "delete_report" in tool_names


def test_server_name():
    """Test that server has correct name."""
    from server import mcp

    assert mcp.name == "gam-reports"


def test_server_has_exactly_seven_tools():
    """Test that server has exactly 7 tools."""
    from server import mcp

    tool_count = len(mcp._tool_manager._tools)
    assert tool_count == 7, f"Expected 7 tools, found {tool_count}"
