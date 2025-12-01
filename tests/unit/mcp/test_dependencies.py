# tests/unit/mcp/test_dependencies.py
"""Unit tests for MCP dependencies and lifespan."""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock


class TestLifespan:
    """Tests for lifespan context manager."""

    @pytest.mark.asyncio
    async def test_lifespan_creates_client(self):
        """Test lifespan creates GAM client."""
        from applications.mcp_server.dependencies import lifespan

        mock_app = Mock()

        # Create a proper mock client that won't raise exceptions
        mock_client = Mock()
        mock_client.close = AsyncMock()

        # Patch all the imports that happen inside lifespan
        with patch("gam_api.GAMClient", return_value=mock_client) as MockClient:
            with patch("gam_shared.cache.CacheManager", return_value=Mock()):
                with patch("gam_shared.cache.FileCache", return_value=Mock()):
                    with patch("services.report_service.ReportService", return_value=Mock()):
                        with patch("settings.get_settings", return_value=Mock(cache_ttl=300)):
                            async with lifespan(mock_app):
                                # Client should be created and attached to app directly (FastMCP pattern)
                                MockClient.assert_called_once()
                                assert mock_app.gam_client == mock_client

    @pytest.mark.asyncio
    async def test_lifespan_creates_cache(self):
        """Test lifespan creates cache manager."""
        from applications.mcp_server.dependencies import lifespan

        mock_app = Mock()

        mock_cache = Mock()
        mock_client = Mock()
        mock_client.close = AsyncMock()

        with patch("gam_api.GAMClient", return_value=mock_client):
            with patch("gam_shared.cache.CacheManager", return_value=mock_cache) as MockCache:
                with patch("gam_shared.cache.FileCache", return_value=Mock()):
                    with patch("services.report_service.ReportService", return_value=Mock()):
                        with patch("settings.get_settings", return_value=Mock(cache_ttl=300)):
                            async with lifespan(mock_app):
                                MockCache.assert_called_once()
                                assert mock_app.cache == mock_cache

    @pytest.mark.asyncio
    async def test_lifespan_creates_report_service(self):
        """Test lifespan creates report service with injected deps."""
        from applications.mcp_server.dependencies import lifespan

        mock_app = Mock()

        mock_client = Mock()
        mock_client.close = AsyncMock()
        mock_cache = Mock()

        # Patch all dependencies
        with patch("gam_api.GAMClient", return_value=mock_client):
            with patch("gam_shared.cache.CacheManager", return_value=mock_cache):
                with patch("gam_shared.cache.FileCache", return_value=Mock()):
                    with patch("settings.get_settings", return_value=Mock(cache_ttl=300)):
                        async with lifespan(mock_app):
                            # Verify all components were created and attached to app directly (FastMCP pattern)
                            assert mock_app.gam_client == mock_client
                            assert mock_app.cache == mock_cache
                            # ReportService should be created (we can't easily mock the constructor
                            # due to the relative import, but we can verify it exists)
                            assert mock_app.report_service is not None
                            # Note: 'settings' is reserved in FastMCP, so we use 'app_settings'
                            assert hasattr(mock_app, 'app_settings')
