"""GAM Reports MCP Server - 7 tools + 4 resources for report management."""

import json
import logging
from contextlib import asynccontextmanager
from typing import Any

from fastmcp import FastMCP

from config.settings import settings
from core.auth import GAMAuth
from core.client import GAMClient
from models.dimensions import ALLOWED_DIMENSIONS
from models.metrics import ALLOWED_METRICS
from models.knowledge import (
    REPORT_TEMPLATES,
    KNOWN_DOMAINS,
    KNOWN_APPS,
    AD_STRATEGIES,
)
from models.reports import CreateReportRequest
from endpoints import (
    create_report as create_report_endpoint,
    run_report as run_report_endpoint,
    list_reports as list_reports_endpoint,
    update_report as update_report_endpoint,
    delete_report as delete_report_endpoint,
    fetch_rows,
    wait_for_operation,
)
from search import search as search_knowledge

logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Server instructions tell the LLM what to do at session start
SERVER_INSTRUCTIONS = """
You are a Google Ad Manager reporting assistant. At the START of each session:

1. READ the context resource (gam://context) to understand:
   - Network configuration
   - Known domains and apps
   - Ad monetization strategies

2. REVIEW available options (gam://dimensions, gam://metrics, gam://templates) to know:
   - Which dimensions are available for reports
   - Which metrics can be measured
   - Pre-built report templates for common use cases

3. When the user asks for a report:
   - Use the `search` tool to find relevant dimensions/metrics
   - Suggest a template if it matches their need
   - Use `create_report` with validated dimension/metric names
   - Use `run_and_fetch_report` to get the data

IMPORTANT: Always validate dimension/metric names against the allowlist before creating reports.
"""


@asynccontextmanager
async def lifespan(app: FastMCP):
    """Initialize GAM client on startup."""
    auth = GAMAuth(settings.credentials_path)
    async with GAMClient(auth) as client:
        app.client = client
        app.network_code = auth.network_code
        if auth.network_code:
            logger.info(f"GAM Reports MCP started for network {auth.network_code}")
        else:
            logger.warning(
                "GAM Reports MCP started without credentials - "
                "operations requiring GAM API will fail"
            )
        yield


mcp = FastMCP("gam-reports", lifespan=lifespan, instructions=SERVER_INSTRUCTIONS)


# =============================================================================
# MCP RESOURCES - Read-only context for session initialization
# =============================================================================


@mcp.resource("gam://context")
def get_context() -> str:
    """
    Company context: network config, domains, apps, and ad strategies.
    Read this first to understand the GAM network setup.
    """
    context = {
        "network": {
            "description": "Google Ad Manager network configuration",
            "note": "Network code is loaded from credentials at runtime",
        },
        "domains": [d.model_dump() for d in KNOWN_DOMAINS],
        "apps": [a.model_dump() for a in KNOWN_APPS],
        "ad_strategies": [s.model_dump() for s in AD_STRATEGIES],
    }
    return json.dumps(context, indent=2)


@mcp.resource("gam://dimensions")
def get_dimensions_resource() -> str:
    """
    All available dimensions for reports, organized by category.
    Use these exact names when creating reports.
    """
    by_category: dict[str, list[dict]] = {}
    for name, dim in ALLOWED_DIMENSIONS.items():
        category = dim.category.value
        if category not in by_category:
            by_category[category] = []
        by_category[category].append({
            "name": name,
            "description": dim.description,
            "use_case": dim.use_case,
        })
    return json.dumps(by_category, indent=2)


@mcp.resource("gam://metrics")
def get_metrics_resource() -> str:
    """
    All available metrics for reports, organized by category.
    Includes data format (INTEGER, PERCENTAGE, CURRENCY, etc.) and report type compatibility.
    """
    by_category: dict[str, list[dict]] = {}
    for name, metric in ALLOWED_METRICS.items():
        category = metric.category.value
        if category not in by_category:
            by_category[category] = []
        by_category[category].append({
            "name": name,
            "description": metric.description,
            "data_format": metric.data_format.value,
            "report_types": [rt.value for rt in metric.report_types],
        })
    return json.dumps(by_category, indent=2)


@mcp.resource("gam://templates")
def get_templates_resource() -> str:
    """
    Pre-built report templates for common use cases.
    Use these as starting points for reports.
    """
    templates = []
    for t in REPORT_TEMPLATES:
        templates.append({
            "name": t.name,
            "description": t.description,
            "dimensions": t.dimensions,
            "metrics": t.metrics,
            "default_date_range_days": t.default_date_range_days,
        })
    return json.dumps(templates, indent=2)


@mcp.tool()
async def search(
    query: str,
    search_in: list[str] | None = None,
) -> dict[str, Any]:
    """
    Search across dimensions, metrics, templates, and domain knowledge.

    Use this to find relevant options when you're not sure what's available.
    Searches names, descriptions, use cases, and compatibility info.

    Args:
        query: Search term (e.g., "revenue", "fill rate", "mobile app")
        search_in: Limit search to specific categories.
                   Options: dimensions, metrics, templates, domains, apps, strategies
                   Default: search all
    """
    return search_knowledge(query, search_in)


@mcp.tool()
async def create_report(
    dimensions: list[str],
    metrics: list[str],
    start_date: str,
    end_date: str,
    filters: dict[str, Any] | None = None,
    report_name: str | None = None,
) -> dict[str, Any]:
    """
    Create a new GAM report with specified dimensions and metrics.

    Use this when you need to build a custom report. Dimensions and metrics
    are validated against the curated allowlist for this network.

    Args:
        dimensions: List of dimension names (e.g., ["DATE", "AD_UNIT_NAME"])
        metrics: List of metric names (e.g., ["TOTAL_IMPRESSIONS", "TOTAL_CLICKS"])
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        filters: Optional filters to apply
        report_name: Optional display name for the report
    """
    request = CreateReportRequest(
        display_name=report_name,
        dimensions=dimensions,
        metrics=metrics,
        start_date=start_date,
        end_date=end_date,
        filters=filters,
    )
    result = await create_report_endpoint(
        mcp.client,
        mcp.network_code,
        request,
    )
    return result.model_dump()


@mcp.tool()
async def run_and_fetch_report(
    report_id: str,
    max_rows: int = 1000,
) -> dict[str, Any]:
    """
    Execute a report and return the data rows.

    Use this when you have a report ID and want to get the actual data.
    Handles the run → poll → fetch workflow automatically.

    Args:
        report_id: The report ID to execute
        max_rows: Maximum number of rows to return (default 1000)
    """
    # Run the report
    operation_name = await run_report_endpoint(
        mcp.client,
        mcp.network_code,
        report_id,
    )

    # Wait for completion
    await wait_for_operation(mcp.client, operation_name)

    # Fetch results
    rows_response = await fetch_rows(
        mcp.client,
        mcp.network_code,
        report_id,
        page_size=max_rows,
    )
    return rows_response.model_dump()


@mcp.tool()
async def get_available_options() -> dict[str, Any]:
    """
    Get all available dimensions, metrics, and report templates.

    Use this first to understand what options are available for building reports.
    """
    return {
        "dimensions": {k: v.model_dump() for k, v in ALLOWED_DIMENSIONS.items()},
        "metrics": {k: v.model_dump() for k, v in ALLOWED_METRICS.items()},
        "templates": [t.model_dump() for t in REPORT_TEMPLATES],
    }


@mcp.tool()
async def list_saved_reports(
    filter_by_tag: str | None = None,
    page_size: int = 100,
) -> dict[str, Any]:
    """
    List all saved reports, optionally filtered by tag.

    Use this to see what reports already exist before creating new ones.

    Args:
        filter_by_tag: Optional tag to filter by
        page_size: Number of reports to return (default 100)
    """
    result = await list_reports_endpoint(
        mcp.client,
        mcp.network_code,
        page_size=page_size,
    )
    # TODO: Add tag filtering when GAM API supports it
    return result


@mcp.tool()
async def update_report(
    report_id: str,
    updates: dict[str, Any],
) -> dict[str, Any]:
    """
    Update an existing report configuration.

    Use this to modify dimensions, metrics, filters, or name of a saved report.

    Args:
        report_id: The report ID to update
        updates: Dictionary of fields to update
    """
    result = await update_report_endpoint(
        mcp.client,
        mcp.network_code,
        report_id,
        updates,
    )
    return result.model_dump()


@mcp.tool()
async def delete_report(report_id: str) -> dict[str, Any]:
    """
    Delete a saved report.

    Use this to remove reports that are no longer needed.

    Args:
        report_id: The report ID to delete
    """
    await delete_report_endpoint(
        mcp.client,
        mcp.network_code,
        report_id,
    )
    return {"status": "deleted", "report_id": report_id}


# =============================================================================
# HEALTH CHECK ENDPOINT - Unauthenticated for load balancers
# =============================================================================


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint for Cloud Run load balancers."""
    from starlette.responses import PlainTextResponse

    return PlainTextResponse("OK")


if __name__ == "__main__":
    import asyncio

    if settings.mcp_transport == "http":
        logger.info(f"Starting HTTP server on 0.0.0.0:{settings.mcp_port}")
        mcp.run(
            transport="http",
            host="0.0.0.0",  # Cloud Run requires binding to 0.0.0.0
            port=settings.mcp_port,
            path="/mcp",  # MCP endpoint path
        )
    else:
        logger.info("Starting STDIO server for local development")
        mcp.run(transport="stdio")
