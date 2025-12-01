# tests/unit/mcp/test_dependencies.py
"""Unit tests for MCP dependencies and lifespan."""

import pytest
from unittest.mock import Mock, patch, AsyncMock


class TestLifespan:
    """Tests for lifespan context manager."""

    @pytest.mark.asyncio
    async def test_lifespan_creates_client(self):
        """Test lifespan creates GAM client."""
        from applications.mcp_server.dependencies import lifespan

        mock_app = Mock()
        mock_app.state = Mock()

        with patch("applications.mcp_server.dependencies.GAMClient") as MockClient:
            mock_client = Mock()
            MockClient.return_value = mock_client

            async with lifespan(mock_app):
                # Client should be created and attached to app state
                MockClient.assert_called_once()
                assert mock_app.state.gam_client == mock_client

    @pytest.mark.asyncio
    async def test_lifespan_creates_cache(self):
        """Test lifespan creates cache manager."""
        from applications.mcp_server.dependencies import lifespan

        mock_app = Mock()
        mock_app.state = Mock()

        with patch("applications.mcp_server.dependencies.GAMClient"):
            with patch("applications.mcp_server.dependencies.CacheManager") as MockCache:
                mock_cache = Mock()
                MockCache.return_value = mock_cache

                async with lifespan(mock_app):
                    MockCache.assert_called_once()
                    assert mock_app.state.cache == mock_cache

    @pytest.mark.asyncio
    async def test_lifespan_creates_report_service(self):
        """Test lifespan creates report service with injected deps."""
        from applications.mcp_server.dependencies import lifespan

        mock_app = Mock()
        mock_app.state = Mock()

        with patch("applications.mcp_server.dependencies.GAMClient") as MockClient:
            with patch("applications.mcp_server.dependencies.CacheManager") as MockCache:
                with patch("applications.mcp_server.dependencies.ReportService") as MockService:
                    mock_client = Mock()
                    mock_cache = Mock()
                    MockClient.return_value = mock_client
                    MockCache.return_value = mock_cache

                    async with lifespan(mock_app):
                        # ReportService should be created with client and cache
                        MockService.assert_called_once_with(
                            client=mock_client,
                            cache=mock_cache
                        )
