"""Async REST client for GAM API using aiohttp."""

import asyncio
import logging
from typing import Any

import aiohttp

from core.auth import GAMAuth
from models.errors import APIError, AuthenticationError, QuotaExceededError

logger = logging.getLogger(__name__)

API_BASE_URL = "https://admanager.googleapis.com/v1"


class GAMClient:
    """Async GAM REST client with connection pooling and retry logic."""

    def __init__(self, auth: GAMAuth):
        self.auth = auth
        self._session: aiohttp.ClientSession | None = None
        self._connector: aiohttp.TCPConnector | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create async session with connection pooling."""
        if self._session is None or self._session.closed:
            if self._connector is None or self._connector.closed:
                self._connector = aiohttp.TCPConnector(
                    limit=100,
                    limit_per_host=10,
                    keepalive_timeout=30,
                )

            credentials = self.auth.get_credentials()
            self._session = aiohttp.ClientSession(
                connector=self._connector,
                headers={
                    "Authorization": f"Bearer {credentials.token}",
                    "Content-Type": "application/json",
                },
                timeout=aiohttp.ClientTimeout(total=300, connect=30),
            )
        return self._session

    async def _request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        retries: int = 3,
    ) -> dict[str, Any]:
        """Make request with retry and error handling."""
        session = await self._get_session()
        url = f"{API_BASE_URL}{path}"

        for attempt in range(retries):
            try:
                async with session.request(method, url, json=json) as response:
                    if response.status == 401 and attempt < retries - 1:
                        # Refresh token and update session
                        credentials = self.auth.get_credentials()
                        session.headers["Authorization"] = f"Bearer {credentials.token}"
                        continue

                    if response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        if attempt < retries - 1:
                            await asyncio.sleep(retry_after)
                            continue
                        raise QuotaExceededError("Rate limited", retry_after=retry_after)

                    if response.status == 401:
                        raise AuthenticationError("Authentication failed")

                    if response.status >= 400:
                        error_data = await response.json()
                        error_msg = error_data.get("error", {}).get("message", "Unknown error")
                        raise APIError(error_msg, status_code=response.status)

                    if response.status == 204:
                        return {}
                    return await response.json()

            except aiohttp.ClientError as e:
                if attempt == retries - 1:
                    raise APIError(f"HTTP client error: {e}")
                await asyncio.sleep(2**attempt)

        raise APIError("Max retries exceeded")

    async def post(self, path: str, json: dict[str, Any] | None = None) -> dict[str, Any]:
        """POST request."""
        return await self._request("POST", path, json)

    async def get(self, path: str) -> dict[str, Any]:
        """GET request."""
        return await self._request("GET", path)

    async def patch(self, path: str, json: dict[str, Any]) -> dict[str, Any]:
        """PATCH request."""
        return await self._request("PATCH", path, json)

    async def delete(self, path: str) -> None:
        """DELETE request."""
        await self._request("DELETE", path)

    async def close(self) -> None:
        """Close session and connector."""
        if self._session and not self._session.closed:
            await self._session.close()
        if self._connector and not self._connector.closed:
            await self._connector.close()

    async def __aenter__(self) -> "GAMClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
