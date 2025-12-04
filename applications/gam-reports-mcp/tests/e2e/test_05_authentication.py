"""E2E tests for OAuth discovery endpoints and authentication."""

import pytest
import httpx


class TestOAuthDiscoveryEndpoints:
    """Test OAuth 2.0 discovery endpoints (RFC 9728, RFC 8414, OpenID Connect)."""

    def test_oauth_protected_resource_metadata(
        self, http_client: httpx.Client, server_url: str
    ):
        """Should return OAuth 2.0 Protected Resource metadata (RFC 9728).

        This endpoint advertises that the MCP server is an OAuth-protected resource
        and specifies which authorization servers can issue tokens for it.
        """
        response = http_client.get(f"{server_url}/.well-known/oauth-protected-resource")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()

        # RFC 9728 required fields
        assert "resource" in data, "Missing 'resource' field"
        assert "authorization_servers" in data, "Missing 'authorization_servers' field"

        # Verify authorization servers list
        auth_servers = data["authorization_servers"]
        assert isinstance(auth_servers, list), "authorization_servers should be a list"
        assert len(auth_servers) > 0, "Should have at least one authorization server"
        assert "https://ag.etus.io" in auth_servers, "Should include ag.etus.io gateway"

        # Optional but expected fields
        assert "bearer_methods_supported" in data, "Missing 'bearer_methods_supported'"
        assert "header" in data["bearer_methods_supported"], "Should support header bearer tokens"

        # Resource metadata
        if "resource_name" in data:
            assert "Google Ad Manager" in data["resource_name"]

    def test_oauth_authorization_server_metadata(
        self, http_client: httpx.Client, server_url: str
    ):
        """Should return OAuth 2.0 Authorization Server metadata (RFC 8414).

        This endpoint proxies the authorization server's metadata to clients.
        """
        response = http_client.get(f"{server_url}/.well-known/oauth-authorization-server")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()

        # RFC 8414 required fields
        assert "issuer" in data, "Missing 'issuer' field"

        # Common OAuth server metadata fields
        expected_fields = [
            "authorization_endpoint",
            "token_endpoint",
        ]

        for field in expected_fields:
            assert field in data, f"Missing '{field}' field in authorization server metadata"

        # Verify issuer is correct
        issuer = data["issuer"]
        assert "ag.etus.io" in issuer or "https://" in issuer, "Issuer should be a valid URL"

    def test_openid_configuration(
        self, http_client: httpx.Client, server_url: str
    ):
        """Should return OpenID Connect Discovery metadata.

        This endpoint provides OpenID Connect configuration for clients that need it.
        """
        response = http_client.get(f"{server_url}/.well-known/openid-configuration")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()

        # OpenID Connect Discovery required fields
        assert "issuer" in data, "Missing 'issuer' field"

        # Common OpenID fields
        expected_fields = [
            "authorization_endpoint",
            "token_endpoint",
        ]

        for field in expected_fields:
            assert field in data, f"Missing '{field}' field in OpenID configuration"

        # Verify issuer format
        issuer = data["issuer"]
        assert issuer.startswith("https://"), "Issuer must use HTTPS"

    def test_oauth_discovery_endpoints_support_cors(
        self, http_client: httpx.Client, server_url: str
    ):
        """OAuth discovery endpoints should support CORS preflight (OPTIONS).

        This is required for browser-based clients like MCP Inspector.
        """
        endpoints = [
            "/.well-known/oauth-protected-resource",
            "/.well-known/oauth-authorization-server",
            "/.well-known/openid-configuration",
        ]

        for endpoint in endpoints:
            response = http_client.options(f"{server_url}{endpoint}")

            # OPTIONS should return 204 No Content for CORS preflight
            assert response.status_code == 204, (
                f"OPTIONS {endpoint} returned {response.status_code}, expected 204"
            )

            # Check CORS headers
            headers = response.headers
            assert "access-control-allow-origin" in headers, f"Missing CORS headers on {endpoint}"
            assert "access-control-allow-methods" in headers, f"Missing allowed methods on {endpoint}"

    def test_oauth_endpoints_return_json_content_type(
        self, http_client: httpx.Client, server_url: str
    ):
        """OAuth discovery endpoints should return application/json content type."""
        endpoints = [
            "/.well-known/oauth-protected-resource",
            "/.well-known/oauth-authorization-server",
            "/.well-known/openid-configuration",
        ]

        for endpoint in endpoints:
            response = http_client.get(f"{server_url}{endpoint}")

            assert response.status_code == 200
            content_type = response.headers.get("content-type", "")
            assert "application/json" in content_type, (
                f"{endpoint} should return application/json, got {content_type}"
            )


class TestTestModeAuthentication:
    """Test authentication behavior in test mode (MCP_TEST_MODE=true)."""

    def test_mcp_endpoints_accessible_in_test_mode(
        self, http_client: httpx.Client, mcp_endpoint: str, mcp_session_id: str
    ):
        """In test mode, MCP endpoints should be accessible without authentication.

        This test verifies that MCP_TEST_MODE=true properly disables authentication.
        """
        # List tools should work without auth header in test mode
        from .helpers import get_tools, assert_json_rpc_success

        response = get_tools(http_client, mcp_endpoint, mcp_session_id)
        result = assert_json_rpc_success(response, "tools/list")

        assert "tools" in result
        assert len(result["tools"]) == 7, "Should have 7 tools available"

    def test_health_endpoint_always_unauthenticated(
        self, http_client: httpx.Client, health_endpoint: str
    ):
        """Health endpoint should always be accessible without authentication.

        This is required for load balancers and monitoring systems.
        """
        response = http_client.get(health_endpoint)

        assert response.status_code == 200
        assert response.text == "OK"


class TestAuthenticationWarnings:
    """Test authentication mode detection and warnings."""

    def test_server_logs_test_mode_warning(self):
        """Server should log a warning when running in test mode.

        This is a documentation test - the warning is logged at server startup.
        The warning message is: "⚠️  RUNNING IN TEST MODE - Authentication disabled!"

        To verify manually:
        1. Set MCP_TEST_MODE=true
        2. Start server
        3. Check logs for warning message
        """
        # This is a documentation test - actual log checking would require
        # capturing server startup logs, which is beyond E2E test scope
        pass
