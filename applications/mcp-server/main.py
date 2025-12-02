"""
Main entry point for MCP server.

Usage:
    MCP_RESOURCE_URI=https://gam.etus.io python main.py

Note: This server uses HTTP transport with OAuth authentication (matches mcp-clickhouse).
"""

import os
import sys
import logging

from server import (
    mcp,
    MCP_RESOURCE_URI,
    MCP_SERVER_HOST,
    MCP_SERVER_PORT,
    OAUTH_GATEWAY_URL,
)

# Configure logging based on environment
log_level = os.environ.get("LOG_LEVEL", os.environ.get("MCP_LOG_LEVEL", "INFO"))
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Run the MCP server."""
    # Log configuration
    logger.info(f"OAuth Gateway: {OAUTH_GATEWAY_URL}")
    logger.info(f"Resource URI: {MCP_RESOURCE_URI}")
    logger.info(f"Host: {MCP_SERVER_HOST}")
    logger.info(f"Port: {MCP_SERVER_PORT}")

    # HTTP transport only (matches mcp-clickhouse)
    mcp.run(
        transport="http",
        host=MCP_SERVER_HOST,
        port=MCP_SERVER_PORT,
        path="/mcp",
    )


if __name__ == "__main__":
    main()
