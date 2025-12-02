# tests/test_core.py
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from core.auth import GAMAuth, AuthConfig
from core.client import GAMClient


def test_auth_config_model():
    config = AuthConfig(
        client_id="test-client-id",
        client_secret="test-secret",
        refresh_token="test-refresh",
        network_code="123456",
    )
    assert config.client_id == "test-client-id"
    assert config.network_code == "123456"


def test_gam_auth_loads_config(tmp_path):
    config_file = tmp_path / "googleads.yaml"
    config_file.write_text("""
ad_manager:
  client_id: test-client-id
  client_secret: test-secret
  refresh_token: test-refresh
  network_code: "123456"
""")

    auth = GAMAuth(config_path=config_file)
    assert auth.config.client_id == "test-client-id"
    assert auth.network_code == "123456"


def test_gam_auth_network_code_property(tmp_path):
    config_file = tmp_path / "googleads.yaml"
    config_file.write_text("""
ad_manager:
  client_id: test-client-id
  client_secret: test-secret
  refresh_token: test-refresh
  network_code: "789"
""")

    auth = GAMAuth(config_path=config_file)
    assert auth.network_code == "789"


# GAMClient tests
@pytest.fixture
def mock_auth():
    auth = MagicMock()
    auth.network_code = "123456"
    creds = MagicMock()
    creds.token = "test-token"
    creds.expired = False
    auth.get_credentials.return_value = creds
    return auth


@pytest.mark.asyncio
async def test_gam_client_context_manager(mock_auth):
    async with GAMClient(mock_auth) as client:
        assert client.auth == mock_auth
    # Session should be closed after context


@pytest.mark.asyncio
async def test_gam_client_get_builds_correct_url(mock_auth):
    with patch("core.client.aiohttp.ClientSession") as mock_session_class:
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": "test"})

        # Setup async context manager for response
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_context.__aexit__.return_value = None
        mock_session.request.return_value = mock_context

        mock_session.closed = False
        mock_session_class.return_value = mock_session

        client = GAMClient(mock_auth)
        client._session = mock_session

        result = await client.get("/networks/123/reports")

        assert result == {"data": "test"}


@pytest.mark.asyncio
async def test_gam_client_post_sends_json(mock_auth):
    with patch("core.client.aiohttp.ClientSession") as mock_session_class:
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"created": "report"})

        # Setup async context manager for response
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_context.__aexit__.return_value = None
        mock_session.request.return_value = mock_context

        mock_session.closed = False
        mock_session_class.return_value = mock_session

        client = GAMClient(mock_auth)
        client._session = mock_session

        result = await client.post("/networks/123/reports", json={"name": "test"})

        assert result == {"created": "report"}
        mock_session.request.assert_called_once()


@pytest.mark.asyncio
async def test_gam_client_handles_401_error(mock_auth):
    with patch("core.client.aiohttp.ClientSession") as mock_session_class:
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.json = AsyncMock(return_value={"error": {"message": "Unauthorized"}})

        # Setup async context manager for response
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_context.__aexit__.return_value = None
        mock_session.request.return_value = mock_context

        mock_session.closed = False
        mock_session_class.return_value = mock_session

        client = GAMClient(mock_auth)
        client._session = mock_session

        from models.errors import AuthenticationError
        with pytest.raises(AuthenticationError):
            await client.get("/networks/123/reports")


@pytest.mark.asyncio
async def test_gam_client_handles_429_error(mock_auth):
    with patch("core.client.aiohttp.ClientSession") as mock_session_class:
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.status = 429
        mock_response.headers = {"Retry-After": "60"}

        # Setup async context manager for response
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_context.__aexit__.return_value = None
        mock_session.request.return_value = mock_context

        mock_session.closed = False
        mock_session_class.return_value = mock_session

        client = GAMClient(mock_auth)
        client._session = mock_session

        from models.errors import QuotaExceededError
        with pytest.raises(QuotaExceededError) as exc_info:
            await client.get("/networks/123/reports")
        assert exc_info.value.retry_after == 60
