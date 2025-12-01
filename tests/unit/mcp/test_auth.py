# tests/unit/mcp/test_auth.py
"""Unit tests for MCP authentication."""

import pytest
from unittest.mock import Mock, patch


class TestCreateAuthProvider:
    """Tests for auth provider creation."""

    def test_auth_disabled_returns_none(self):
        """Test auth disabled returns None provider."""
        from applications.mcp_server.auth import create_auth_provider
        from applications.mcp_server.settings import MCPSettings

        settings = MCPSettings(auth_enabled=False)
        provider = create_auth_provider(settings)

        assert provider is None

    def test_auth_enabled_creates_remote_provider(self):
        """Test auth enabled creates RemoteAuthProvider."""
        # Create mock modules before importing auth
        import sys
        from unittest.mock import MagicMock

        # Create mock fastmcp modules
        mock_jwt_verifier = MagicMock()
        mock_remote_auth = MagicMock()

        # Create the mock module structure
        fastmcp_mock = MagicMock()
        fastmcp_server_mock = MagicMock()
        fastmcp_auth_mock = MagicMock()
        fastmcp_providers_mock = MagicMock()
        fastmcp_jwt_mock = MagicMock()

        fastmcp_jwt_mock.JWTVerifier = mock_jwt_verifier
        fastmcp_providers_mock.jwt = fastmcp_jwt_mock
        fastmcp_auth_mock.RemoteAuthProvider = mock_remote_auth
        fastmcp_auth_mock.providers = fastmcp_providers_mock
        fastmcp_server_mock.auth = fastmcp_auth_mock
        fastmcp_mock.server = fastmcp_server_mock

        sys.modules['fastmcp'] = fastmcp_mock
        sys.modules['fastmcp.server'] = fastmcp_server_mock
        sys.modules['fastmcp.server.auth'] = fastmcp_auth_mock
        sys.modules['fastmcp.server.auth.providers'] = fastmcp_providers_mock
        sys.modules['fastmcp.server.auth.providers.jwt'] = fastmcp_jwt_mock

        try:
            from applications.mcp_server.auth import create_auth_provider
            from applications.mcp_server.settings import MCPSettings

            settings = MCPSettings(
                auth_enabled=True,
                mcp_resource_uri="https://my-server.run.app",
                oauth_gateway_url="https://ag.etus.io",
            )

            mock_jwt_instance = Mock()
            mock_jwt_verifier.return_value = mock_jwt_instance

            provider = create_auth_provider(settings)

            # Verify JWTVerifier was created with correct params
            mock_jwt_verifier.assert_called_once()
            call_kwargs = mock_jwt_verifier.call_args[1]
            assert "jwks_uri" in call_kwargs
            assert "ag.etus.io" in call_kwargs["jwks_uri"]

            # Verify RemoteAuthProvider was created
            mock_remote_auth.assert_called_once()
        finally:
            # Cleanup
            for key in list(sys.modules.keys()):
                if key.startswith('fastmcp'):
                    del sys.modules[key]

    def test_auth_enabled_requires_resource_uri(self):
        """Test auth enabled without resource URI raises error."""
        from applications.mcp_server.auth import create_auth_provider
        from applications.mcp_server.settings import MCPSettings

        settings = MCPSettings(
            auth_enabled=True,
            mcp_resource_uri=None,  # Missing required field
        )

        with pytest.raises(ValueError, match="MCP_RESOURCE_URI"):
            create_auth_provider(settings)
