# tests/unit/mcp/test_settings.py
"""Unit tests for MCP server settings."""

import pytest
import os
from unittest.mock import patch


class TestMCPSettings:
    """Tests for MCPSettings configuration."""

    def test_settings_loads_defaults(self):
        """Test settings loads with default values."""
        # Clear relevant env vars
        with patch.dict(os.environ, {}, clear=True):
            from applications.mcp_server.settings import MCPSettings

            settings = MCPSettings()

            assert settings.auth_enabled is False
            assert settings.port == 8080
            assert settings.log_level == "INFO"
            assert settings.oauth_gateway_url == "https://ag.etus.io"

    def test_settings_from_environment(self):
        """Test settings loads from environment variables."""
        env_vars = {
            "MCP_AUTH_ENABLED": "true",
            "MCP_PORT": "9000",
            "MCP_LOG_LEVEL": "DEBUG",
            "MCP_RESOURCE_URI": "https://my-server.run.app",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            from applications.mcp_server.settings import MCPSettings

            settings = MCPSettings()

            assert settings.auth_enabled is True
            assert settings.port == 9000
            assert settings.log_level == "DEBUG"
            assert settings.mcp_resource_uri == "https://my-server.run.app"

    def test_oauth_derived_settings(self):
        """Test OAuth settings are derived correctly."""
        env_vars = {
            "MCP_OAUTH_GATEWAY_URL": "https://custom-oauth.example.com",
            "MCP_RESOURCE_URI": "https://my-server.run.app",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            from applications.mcp_server.settings import MCPSettings

            settings = MCPSettings()

            assert settings.oauth_jwks_uri == "https://custom-oauth.example.com/.well-known/jwks.json"
            assert settings.oauth_issuer == "https://custom-oauth.example.com"
            assert settings.oauth_audience == "https://my-server.run.app"
