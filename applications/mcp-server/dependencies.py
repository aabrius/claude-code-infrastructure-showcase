# applications/mcp-server/dependencies.py
"""
MCP Server dependency injection and lifespan management.

Uses FastMCP lifespan for proper resource management.
Matches mcp-clickhouse pattern - no settings module, direct os.getenv().
"""

from contextlib import asynccontextmanager
import logging
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP

logger = logging.getLogger(__name__)

# Cache TTL from environment (matches mcp-clickhouse pattern)
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))


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
    from services.report_service import ReportService

    # Try to import and create GAM client (may fail without credentials)
    mock_mode = False
    gam_client = None

    try:
        from gam_api import GAMClient
        gam_client = GAMClient()
        logger.info("GAM client initialized")
    except ImportError as e:
        logger.warning(f"GAM API import failed: {e}. Running in mock mode.")
        mock_mode = True
    except Exception as e:
        logger.warning(f"GAM client initialization failed: {e}. Running in mock mode.")
        mock_mode = True

    # Create cache manager (optional, may fail)
    cache = None
    try:
        from gam_shared.cache import CacheManager, FileCache
        cache = CacheManager(FileCache())
        logger.info(f"Cache initialized with TTL={CACHE_TTL}s")
    except ImportError as e:
        logger.warning(f"Cache import failed: {e}. Running without cache.")
    except Exception as e:
        logger.warning(f"Cache initialization failed: {e}. Running without cache.")

    # Create report service with injected dependencies
    # Use mock_mode if client is unavailable (for testing metadata tools)
    report_service = ReportService(client=gam_client, cache=cache, mock_mode=mock_mode)
    if mock_mode:
        logger.warning("ReportService running in mock mode - only metadata tools available")

    # Attach directly to server for access in tools via ctx.fastmcp
    app.gam_client = gam_client
    app.cache = cache
    app.report_service = report_service

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
