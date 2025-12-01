"""
MCP Server configuration using Pydantic Settings.

All configuration is loaded from environment variables with MCP_ prefix.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, computed_field
from typing import Optional


class MCPSettings(BaseSettings):
    """Configuration for MCP server."""

    model_config = SettingsConfigDict(
        env_prefix="MCP_",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True
    )

    # Server settings
    auth_enabled: bool = Field(default=False, description="Enable JWT authentication")
    port: int = Field(default=8080, description="Server port")
    log_level: str = Field(default="INFO", description="Logging level")
    transport: str = Field(default="stdio", description="Transport: stdio or http")

    # OAuth settings
    oauth_gateway_url: str = Field(
        default="https://ag.etus.io",
        description="OAuth gateway URL for authentication"
    )
    resource_uri: Optional[str] = Field(
        default=None,
        description="MCP resource URI (required for auth)",
        alias="mcp_resource_uri"
    )

    # Cache settings
    cache_ttl: int = Field(default=3600, description="Default cache TTL in seconds")
    cache_max_size: int = Field(default=1000, description="Maximum cache entries")

    # Circuit breaker settings
    circuit_failure_threshold: int = Field(default=5, description="Failures before circuit opens")
    circuit_recovery_timeout: int = Field(default=60, description="Seconds before retry")

    @computed_field
    @property
    def oauth_jwks_uri(self) -> str:
        """JWKS URI derived from OAuth gateway."""
        return f"{self.oauth_gateway_url}/.well-known/jwks.json"

    @computed_field
    @property
    def oauth_issuer(self) -> str:
        """OAuth issuer derived from gateway URL."""
        return self.oauth_gateway_url

    @computed_field
    @property
    def oauth_audience(self) -> str:
        """OAuth audience - defaults to resource URI."""
        return self.resource_uri or ""

    # Backwards compatibility property
    @property
    def mcp_resource_uri(self) -> Optional[str]:
        """Backwards compatibility for mcp_resource_uri."""
        return self.resource_uri


# Singleton instance
_settings: Optional[MCPSettings] = None


def get_settings(force_reload: bool = False) -> MCPSettings:
    """
    Get or create settings singleton.

    Args:
        force_reload: If True, reload settings from environment (useful for testing)

    Returns:
        MCPSettings instance
    """
    global _settings
    if _settings is None or force_reload:
        _settings = MCPSettings()
    return _settings


def reset_settings() -> None:
    """Reset settings singleton (useful for testing)."""
    global _settings
    _settings = None
