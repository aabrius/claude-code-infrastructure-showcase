# applications/mcp-server/auth.py
"""
MCP Server authentication configuration.

Uses RemoteAuthProvider + JWTVerifier for OAuth integration with external
authorization servers like ag.etus.io.
"""

import logging
from typing import Optional

from pydantic import AnyHttpUrl

logger = logging.getLogger(__name__)


def create_auth_provider(settings):
    """
    Create authentication provider based on settings.

    Args:
        settings: MCPSettings instance

    Returns:
        RemoteAuthProvider if auth enabled, None otherwise

    Raises:
        ValueError: If auth enabled but required settings missing
    """
    if not settings.auth_enabled:
        logger.info("Authentication disabled")
        return None

    # Validate required settings for auth
    if not settings.mcp_resource_uri:
        raise ValueError(
            "MCP_RESOURCE_URI environment variable is required when auth is enabled. "
            "Set this to your server's public URL (e.g., https://my-server.run.app)"
        )

    try:
        from fastmcp.server.auth import RemoteAuthProvider
        from fastmcp.server.auth.providers.jwt import JWTVerifier
    except ImportError as e:
        logger.warning(f"FastMCP auth not available: {e}. Using fallback.")
        return _create_fallback_auth(settings)

    # Create JWT verifier for token validation
    token_verifier = JWTVerifier(
        jwks_uri=settings.oauth_jwks_uri,
        issuer=settings.oauth_issuer,
        audience=settings.oauth_audience,
    )

    # Create remote auth provider
    auth_provider = RemoteAuthProvider(
        token_verifier=token_verifier,
        authorization_servers=[AnyHttpUrl(settings.oauth_gateway_url)],
        base_url=settings.mcp_resource_uri,
    )

    logger.info(
        "Authentication enabled",
        extra={
            "oauth_gateway": settings.oauth_gateway_url,
            "resource_uri": settings.mcp_resource_uri,
        }
    )

    return auth_provider


def _create_fallback_auth(settings):
    """
    Create fallback authentication using BearerAuthProvider.

    This is used when RemoteAuthProvider is not available (older FastMCP versions).
    """
    try:
        from fastmcp.server.auth import BearerAuthProvider
        from fastmcp.server.auth.providers.bearer import RSAKeyPair

        key_pair = RSAKeyPair.generate()

        auth_provider = BearerAuthProvider(
            public_key=key_pair.public_key,
            issuer="gam-mcp-server",
            audience="gam-api",
        )

        # Generate client token for testing
        client_token = key_pair.create_token(
            subject="gam-api-client",
            issuer="gam-mcp-server",
            audience="gam-api",
            scopes=["read", "write", "admin"],
        )

        logger.warning(
            "Using fallback BearerAuthProvider (upgrade FastMCP for RemoteAuthProvider)",
            extra={"token_preview": f"{client_token[:50]}..."}
        )

        # Save token for client configuration
        try:
            with open("/tmp/gam-mcp-jwt-token.txt", "w") as f:
                f.write(client_token)
        except IOError:
            pass

        return auth_provider

    except ImportError:
        logger.error("No authentication provider available")
        return None
