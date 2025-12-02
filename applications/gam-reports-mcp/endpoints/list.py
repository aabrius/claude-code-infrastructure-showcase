"""List reports endpoint."""

from typing import Any
from core.client import GAMClient


async def list_reports(
    client: GAMClient,
    network_code: str,
    page_size: int = 100,
    page_token: str | None = None,
) -> dict[str, Any]:
    """GET /networks/{network}/reports"""
    path = f"/networks/{network_code}/reports?pageSize={page_size}"
    if page_token:
        path += f"&pageToken={page_token}"
    return await client.get(path)
