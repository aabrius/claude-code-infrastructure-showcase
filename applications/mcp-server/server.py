"""
Refactored MCP Server for Google Ad Manager API.

This module creates the FastMCP server with:
- Proper authentication (RemoteAuthProvider + JWTVerifier)
- Dependency injection via lifespan
- Thin tool definitions that delegate to ReportService
- Pydantic response models
"""

import json
import logging
from typing import Literal, Optional

from fastmcp import FastMCP, Context

from settings import get_settings
from auth import create_auth_provider
from dependencies import lifespan
from models.responses import ErrorResponse

logger = logging.getLogger(__name__)


def create_mcp_server() -> FastMCP:
    """
    Create and configure the MCP server.

    Returns:
        Configured FastMCP server instance
    """
    settings = get_settings()

    # Create auth provider based on settings
    auth_provider = create_auth_provider(settings)

    # Create FastMCP server with lifespan
    mcp = FastMCP(
        "Google Ad Manager API",
        auth=auth_provider,
        lifespan=lifespan,
    )

    # Register tools
    _register_tools(mcp)

    logger.info(
        "MCP server created",
        extra={
            "auth_enabled": settings.auth_enabled,
            "transport": settings.transport,
        }
    )

    return mcp


def _register_tools(mcp: FastMCP) -> None:
    """Register all MCP tools."""

    @mcp.tool
    async def gam_quick_report(
        report_type: Literal["delivery", "inventory", "sales", "reach", "programmatic"],
        days_back: int = 30,
        format: Literal["json", "csv", "summary"] = "json",
        ctx: Context = None,
    ) -> str:
        """Generate quick reports with predefined configurations.

        Args:
            report_type: Type of report (delivery, inventory, sales, reach, programmatic)
            days_back: Number of days to look back (default: 30)
            format: Output format (default: json)

        Returns:
            JSON response with report data
        """
        return await _gam_quick_report(report_type, days_back, format, ctx)

    @mcp.tool
    async def gam_list_reports(
        limit: int = 20,
        ctx: Context = None,
    ) -> str:
        """List available reports in the Ad Manager network.

        Args:
            limit: Maximum reports to return (default: 20)

        Returns:
            JSON response with report list
        """
        return await _gam_list_reports(limit, ctx)

    @mcp.tool
    async def gam_get_dimensions_metrics(
        report_type: Literal["HISTORICAL", "REACH", "AD_SPEED"] = "HISTORICAL",
        category: Literal["dimensions", "metrics", "both"] = "both",
        ctx: Context = None,
    ) -> str:
        """Get available dimensions and metrics for reports.

        Args:
            report_type: Report type to get fields for
            category: Return dimensions, metrics, or both

        Returns:
            JSON response with available fields
        """
        return await _gam_get_dimensions_metrics(report_type, category, ctx)

    @mcp.tool
    async def gam_get_common_combinations(ctx: Context = None) -> str:
        """Get common dimension-metric combinations.

        Returns:
            JSON response with common combinations
        """
        return await _gam_get_common_combinations(ctx)

    @mcp.tool
    async def gam_get_quick_report_types(ctx: Context = None) -> str:
        """Get available quick report types.

        Returns:
            JSON response with report types
        """
        return await _gam_get_quick_report_types(ctx)


# Tool implementations (thin adapters to ReportService)

async def _gam_quick_report(
    report_type: str,
    days_back: int,
    format: str,
    ctx: Context,
) -> str:
    """Implementation for gam_quick_report tool."""
    try:
        service = ctx.app.state.report_service
        result = service.quick_report(report_type, days_back=days_back, format=format)
        return json.dumps(result, indent=2, default=str)
    except ValueError as e:
        return ErrorResponse.create(
            error_type="ValidationError",
            message=str(e),
            error_code="VAL_001",
            suggestions=["Use valid report types: delivery, inventory, sales, reach, programmatic"],
        ).model_dump_json(indent=2)
    except Exception as e:
        logger.exception("Quick report failed")
        return ErrorResponse.create(
            error_type="InternalError",
            message="Failed to generate report",
            error_code="INT_001",
            details={"error": str(e)},
        ).model_dump_json(indent=2)


async def _gam_list_reports(limit: int, ctx: Context) -> str:
    """Implementation for gam_list_reports tool."""
    try:
        service = ctx.app.state.report_service
        result = service.list_reports(limit=limit)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.exception("List reports failed")
        return ErrorResponse.create(
            error_type="InternalError",
            message="Failed to list reports",
            error_code="INT_002",
        ).model_dump_json(indent=2)


async def _gam_get_dimensions_metrics(
    report_type: str,
    category: str,
    ctx: Context,
) -> str:
    """Implementation for gam_get_dimensions_metrics tool."""
    try:
        service = ctx.app.state.report_service
        result = service.get_dimensions_metrics(report_type, category)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.exception("Get dimensions/metrics failed")
        return ErrorResponse.create(
            error_type="InternalError",
            message="Failed to get dimensions/metrics",
            error_code="INT_003",
        ).model_dump_json(indent=2)


async def _gam_get_common_combinations(ctx: Context) -> str:
    """Implementation for gam_get_common_combinations tool."""
    try:
        service = ctx.app.state.report_service
        result = service.get_common_combinations()
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.exception("Get combinations failed")
        return ErrorResponse.create(
            error_type="InternalError",
            message="Failed to get combinations",
            error_code="INT_004",
        ).model_dump_json(indent=2)


async def _gam_get_quick_report_types(ctx: Context) -> str:
    """Implementation for gam_get_quick_report_types tool."""
    try:
        service = ctx.app.state.report_service
        result = service.get_quick_report_types()
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.exception("Get report types failed")
        return ErrorResponse.create(
            error_type="InternalError",
            message="Failed to get report types",
            error_code="INT_005",
        ).model_dump_json(indent=2)


# Server singleton
_server: Optional[FastMCP] = None


def get_server() -> FastMCP:
    """Get or create server singleton."""
    global _server
    if _server is None:
        _server = create_mcp_server()
    return _server
