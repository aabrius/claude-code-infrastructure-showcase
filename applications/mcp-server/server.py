"""
MCP Server for Google Ad Manager API.

Matches mcp-clickhouse pattern exactly:
- Direct os.getenv() for configuration
- Auth ALWAYS created (no conditional)
- No MCP_AUTH_ENABLED toggle
"""

import json
import logging
import os
from typing import Literal, Optional

from fastmcp import FastMCP, Context
from fastmcp.server.auth import RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier
from pydantic import AnyHttpUrl
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse, Response

from dependencies import lifespan

# CORS headers for browser-based clients (MCP Inspector)
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS, DELETE",
    "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept, Mcp-Session-Id",
    "Access-Control-Max-Age": "86400",
}

logger = logging.getLogger(__name__)

# =============================================================================
# OAuth Configuration (matches mcp-clickhouse exactly)
# =============================================================================
OAUTH_GATEWAY_URL = os.getenv("OAUTH_GATEWAY_URL", "https://ag.etus.io")
MCP_RESOURCE_URI = os.getenv("MCP_RESOURCE_URI")  # Your server's URI (required)
OAUTH_JWKS_URI = os.getenv("OAUTH_JWKS_URI", f"{OAUTH_GATEWAY_URL}/.well-known/jwks.json")
OAUTH_ISSUER = os.getenv("OAUTH_ISSUER", OAUTH_GATEWAY_URL)
OAUTH_AUDIENCE = os.getenv("OAUTH_AUDIENCE", MCP_RESOURCE_URI)
MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8080"))

# =============================================================================
# Authentication Setup (ALWAYS created, no conditional - matches mcp-clickhouse)
# =============================================================================
# Note: audience=None to allow any audience (for testing with MCP Inspector)
# The OAuth gateway may not be setting the correct audience in tokens
token_verifier = JWTVerifier(
    jwks_uri=OAUTH_JWKS_URI,
    issuer=OAUTH_ISSUER,
    audience=None,  # TODO: Re-enable once OAuth gateway is properly configured
)

# Create Remote Auth Provider
# This handles all OAuth validation automatically!
auth = RemoteAuthProvider(
    token_verifier=token_verifier,
    authorization_servers=[AnyHttpUrl(OAUTH_GATEWAY_URL)],
    base_url=MCP_RESOURCE_URI,
)

# =============================================================================
# MCP Server Instance
# =============================================================================
mcp = FastMCP("Google Ad Manager API", auth=auth, lifespan=lifespan)


# =============================================================================
# Health Check & OAuth Discovery Routes
# =============================================================================
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """Health check endpoint - intentionally unauthenticated."""
    return PlainTextResponse("OK")


@mcp.custom_route("/.well-known/oauth-protected-resource", methods=["GET", "OPTIONS"])
async def oauth_protected_resource(request: Request) -> Response:
    """OAuth 2.0 Protected Resource Metadata (RFC 9728)."""
    if request.method == "OPTIONS":
        return Response(status_code=204, headers=CORS_HEADERS)
    metadata = {
        "resource": OAUTH_AUDIENCE,
        "authorization_servers": [OAUTH_GATEWAY_URL],
        "bearer_methods_supported": ["header"],
        "resource_name": "Google Ad Manager MCP Server",
        "resource_documentation": f"{MCP_RESOURCE_URI}/docs" if MCP_RESOURCE_URI else None,
    }
    return JSONResponse(metadata, headers=CORS_HEADERS)


@mcp.custom_route("/.well-known/oauth-authorization-server", methods=["GET", "OPTIONS"])
async def oauth_authorization_server(request: Request) -> Response:
    """OAuth 2.0 Authorization Server Metadata (RFC 8414)."""
    if request.method == "OPTIONS":
        return Response(status_code=204, headers=CORS_HEADERS)
    import httpx

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            auth_server_url = f"{OAUTH_GATEWAY_URL}/.well-known/oauth-authorization-server"
            response = await client.get(auth_server_url)
            response.raise_for_status()
            return JSONResponse(response.json(), headers=CORS_HEADERS)
    except Exception as e:
        logger.warning(f"Failed to fetch auth server metadata: {e}")
        fallback = {
            "issuer": OAUTH_ISSUER,
            "jwks_uri": OAUTH_JWKS_URI,
            "authorization_endpoint": f"{OAUTH_GATEWAY_URL}/authorize",
            "token_endpoint": f"{OAUTH_GATEWAY_URL}/token",
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code"],
            "token_endpoint_auth_methods_supported": ["client_secret_basic"],
        }
        return JSONResponse(fallback, headers=CORS_HEADERS)


@mcp.custom_route("/.well-known/openid-configuration", methods=["GET", "OPTIONS"])
async def openid_configuration(request: Request) -> Response:
    """OpenID Connect Discovery (proxied from auth server)."""
    if request.method == "OPTIONS":
        return Response(status_code=204, headers=CORS_HEADERS)
    import httpx

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Try OpenID config first, fallback to OAuth metadata
            for endpoint in [
                f"{OAUTH_GATEWAY_URL}/.well-known/openid-configuration",
                f"{OAUTH_GATEWAY_URL}/.well-known/oauth-authorization-server",
            ]:
                try:
                    response = await client.get(endpoint)
                    if response.status_code == 200:
                        return JSONResponse(response.json(), headers=CORS_HEADERS)
                except Exception:
                    continue
        raise Exception("No valid discovery endpoint found")
    except Exception as e:
        logger.warning(f"Failed to fetch OpenID config: {e}")
        # Return minimal OpenID-compatible response
        fallback = {
            "issuer": OAUTH_ISSUER,
            "jwks_uri": OAUTH_JWKS_URI,
            "authorization_endpoint": f"{OAUTH_GATEWAY_URL}/authorize",
            "token_endpoint": f"{OAUTH_GATEWAY_URL}/token",
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code"],
            "subject_types_supported": ["public"],
            "id_token_signing_alg_values_supported": ["RS256"],
        }
        return JSONResponse(fallback, headers=CORS_HEADERS)


# =============================================================================
# TOOLS
# =============================================================================
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
    """
    try:
        service = ctx.fastmcp.report_service
        result = await service.quick_report(report_type, days_back=days_back, format=format)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.exception("Quick report failed")
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool
async def gam_list_reports(
    limit: int = 20,
    ctx: Context = None,
) -> str:
    """List available reports in the Ad Manager network.

    Args:
        limit: Maximum reports to return (default: 20)
    """
    try:
        service = ctx.fastmcp.report_service
        result = service.list_reports(limit=limit)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.exception("List reports failed")
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool
async def gam_get_dimensions_metrics(
    report_type: Literal["HISTORICAL", "REACH", "AD_SPEED"] = "HISTORICAL",
    category: Literal["dimensions", "metrics", "both"] = "both",
    ctx: Context = None,
) -> str:
    """Get available dimensions and metrics for reports.

    Args:
        report_type: Report type (HISTORICAL, REACH, AD_SPEED)
        category: What to return (dimensions, metrics, or both)
    """
    try:
        service = ctx.fastmcp.report_service
        result = service.get_dimensions_metrics(report_type, category)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.exception("Get dimensions/metrics failed")
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool
async def gam_get_common_combinations(ctx: Context = None) -> str:
    """Get common dimension-metric combinations for different use cases."""
    try:
        service = ctx.fastmcp.report_service
        result = service.get_common_combinations()
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.exception("Get combinations failed")
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool
async def gam_get_quick_report_types(ctx: Context = None) -> str:
    """Get available quick report types with descriptions."""
    try:
        service = ctx.fastmcp.report_service
        result = service.get_quick_report_types()
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.exception("Get report types failed")
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool
async def gam_create_report(
    name: str,
    dimensions: str,
    metrics: str,
    start_date: str,
    end_date: str,
    report_type: Literal["HISTORICAL", "REACH", "AD_SPEED"] = "HISTORICAL",
    run_immediately: bool = True,
    ctx: Context = None,
) -> str:
    """Create a custom report with specified dimensions and metrics.

    Args:
        name: Report name
        dimensions: JSON array of dimension names, e.g. '["DATE", "AD_UNIT_NAME"]'
        metrics: JSON array of metric names, e.g. '["AD_SERVER_IMPRESSIONS"]'
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        report_type: Report type (default: HISTORICAL)
        run_immediately: Execute report now (default: True)
    """
    try:
        dims = json.loads(dimensions) if isinstance(dimensions, str) else dimensions
        mets = json.loads(metrics) if isinstance(metrics, str) else metrics

        service = ctx.fastmcp.report_service
        result = await service.create_report(
            name=name,
            dimensions=dims,
            metrics=mets,
            start_date=start_date,
            end_date=end_date,
            report_type=report_type,
            run_immediately=run_immediately,
        )
        return json.dumps(result, indent=2, default=str)
    except json.JSONDecodeError as e:
        return json.dumps({"success": False, "error": f"Invalid JSON: {e}"})
    except Exception as e:
        logger.exception("Create report failed")
        return json.dumps({"success": False, "error": str(e)})


@mcp.tool
async def gam_run_report(
    report_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    ctx: Context = None,
) -> str:
    """Execute an existing saved report by ID.

    Args:
        report_id: ID of the saved report
        start_date: Optional date override (YYYY-MM-DD)
        end_date: Optional date override (YYYY-MM-DD)
    """
    try:
        service = ctx.fastmcp.report_service
        result = await service.run_report(report_id, start_date, end_date)
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.exception(f"Run report failed for {report_id}")
        return json.dumps({"success": False, "error": str(e)})


def get_server() -> FastMCP:
    """Get the MCP server instance."""
    return mcp
