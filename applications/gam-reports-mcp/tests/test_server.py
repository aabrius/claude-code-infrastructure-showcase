"""Tests for the MCP server."""

import json
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


# =============================================================================
# Resource Tests
# =============================================================================


def test_server_has_four_resources():
    """Test that server has exactly 4 resources for session context."""
    from server import mcp

    resource_count = len(mcp._resource_manager._resources)
    assert resource_count == 4, f"Expected 4 resources, found {resource_count}"


def test_server_has_required_resources():
    """Test that server has all required context resources."""
    from server import mcp

    resource_uris = list(mcp._resource_manager._resources.keys())

    assert "gam://context" in resource_uris
    assert "gam://dimensions" in resource_uris
    assert "gam://metrics" in resource_uris
    assert "gam://templates" in resource_uris


def test_context_resource_returns_valid_json():
    """Test that context resource returns valid JSON."""
    from server import mcp

    # Get the resource's underlying function
    resource = mcp._resource_manager._resources["gam://context"]
    result = resource.fn()
    data = json.loads(result)

    assert "network" in data
    assert "domains" in data
    assert "apps" in data
    assert "ad_strategies" in data


def test_dimensions_resource_returns_valid_json():
    """Test that dimensions resource returns valid JSON with categories."""
    from server import mcp

    resource = mcp._resource_manager._resources["gam://dimensions"]
    result = resource.fn()
    data = json.loads(result)

    # Should have at least one category
    assert len(data) > 0
    # Each category should have dimensions with required fields
    for category, dimensions in data.items():
        assert isinstance(dimensions, list)
        if dimensions:
            assert "name" in dimensions[0]
            assert "description" in dimensions[0]


def test_metrics_resource_returns_valid_json():
    """Test that metrics resource returns valid JSON with categories."""
    from server import mcp

    resource = mcp._resource_manager._resources["gam://metrics"]
    result = resource.fn()
    data = json.loads(result)

    # Should have at least one category
    assert len(data) > 0
    # Each category should have metrics with required fields
    for category, metrics in data.items():
        assert isinstance(metrics, list)
        if metrics:
            assert "name" in metrics[0]
            assert "description" in metrics[0]
            assert "data_format" in metrics[0]
            assert "report_types" in metrics[0]


def test_templates_resource_returns_valid_json():
    """Test that templates resource returns valid JSON array."""
    from server import mcp

    resource = mcp._resource_manager._resources["gam://templates"]
    result = resource.fn()
    data = json.loads(result)

    assert isinstance(data, list)
    if data:
        assert "name" in data[0]
        assert "dimensions" in data[0]
        assert "metrics" in data[0]


def test_server_has_instructions():
    """Test that server has instructions for session initialization."""
    from server import mcp, SERVER_INSTRUCTIONS

    # Instructions should contain key guidance
    assert "READ the context resource" in SERVER_INSTRUCTIONS
    assert "gam://context" in SERVER_INSTRUCTIONS
    assert "gam://dimensions" in SERVER_INSTRUCTIONS
    assert "gam://metrics" in SERVER_INSTRUCTIONS
