# applications/mcp-server/dependencies.py
"""
MCP Server dependency injection and lifespan management.

Uses FastMCP lifespan for proper resource management.
"""

from contextlib import asynccontextmanager
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: "FastMCP"):
    """
    Lifespan context manager for FastMCP server.

    Creates and manages shared resources:
    - GAMClient: Shared API client with connection pooling
    - CacheManager: Result caching
    - ReportService: Business logic with injected dependencies

    Args:
        app: FastMCP application instance
    """
    logger.info("Starting MCP server lifespan")

    # Import here to avoid circular dependencies
    from gam_api import GAMClient
    from gam_shared.cache import CacheManager, FileCache
    from .services.report_service import ReportService
    from .settings import get_settings

    settings = get_settings()

    # Create shared GAM client
    try:
        gam_client = GAMClient()
        logger.info("GAM client initialized")
    except Exception as e:
        logger.warning(f"GAM client initialization failed: {e}. Using None.")
        gam_client = None

    # Create cache manager
    cache = CacheManager(FileCache())
    logger.info(f"Cache initialized with TTL={settings.cache_ttl}s")

    # Create report service with injected dependencies
    report_service = ReportService(client=gam_client, cache=cache)

    # Attach to app state for access in tools
    app.state.gam_client = gam_client
    app.state.cache = cache
    app.state.report_service = report_service
    app.state.settings = settings

    logger.info("MCP server resources initialized")

    try:
        yield
    finally:
        # Cleanup
        logger.info("Shutting down MCP server")

        # Close client connections if needed
        if hasattr(gam_client, 'close'):
            try:
                await gam_client.close()
            except Exception as e:
                logger.error(f"Error closing GAM client: {e}")

        logger.info("MCP server shutdown complete")


def get_report_service(ctx) -> "ReportService":
    """
    Get report service from context.

    Args:
        ctx: MCP context with app state

    Returns:
        ReportService instance
    """
    return ctx.app.state.report_service


def get_gam_client(ctx):
    """
    Get GAM client from context.

    Args:
        ctx: MCP context with app state

    Returns:
        GAMClient instance or None
    """
    return ctx.app.state.gam_client


def get_cache(ctx):
    """
    Get cache manager from context.

    Args:
        ctx: MCP context with app state

    Returns:
        CacheManager instance
    """
    return ctx.app.state.cache
