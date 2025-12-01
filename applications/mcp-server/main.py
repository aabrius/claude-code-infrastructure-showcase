"""
Main entry point for MCP server.

Usage:
    # Local development (stdio)
    python -m applications.mcp_server.main

    # HTTP transport (Cloud Run)
    MCP_TRANSPORT=http MCP_PORT=8080 python -m applications.mcp_server.main

    # With authentication
    MCP_AUTH_ENABLED=true MCP_RESOURCE_URI=https://my-server.run.app python -m applications.mcp_server.main
"""

import os
import logging

from settings import get_settings
from server import get_server

# Configure logging based on environment
log_level = os.environ.get("LOG_LEVEL", os.environ.get("MCP_LOG_LEVEL", "INFO"))
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Run the MCP server."""
    settings = get_settings()
    server = get_server()

    logger.info(
        "Starting MCP server",
        extra={
            "transport": settings.transport,
            "port": settings.port,
            "auth_enabled": settings.auth_enabled,
        }
    )

    if settings.transport == "http":
        # HTTP transport for Cloud Run
        server.run(
            transport="http",
            host="0.0.0.0",
            port=settings.port,
            path="/mcp",
        )
    else:
        # stdio transport for local development
        server.run(transport="stdio")


if __name__ == "__main__":
    main()
