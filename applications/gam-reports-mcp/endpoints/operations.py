"""Operations endpoint for async status tracking."""

import asyncio
from typing import Any
from core.client import GAMClient


async def get_operation(
    client: GAMClient,
    operation_name: str,
) -> dict[str, Any]:
    """GET /networks/{network}/operations/{id}"""
    # operation_name is full path: networks/123/operations/reports/runs/456
    return await client.get(f"/{operation_name}")


async def wait_for_operation(
    client: GAMClient,
    operation_name: str,
    timeout: int = 300,
    poll_interval: int = 5,
) -> dict[str, Any]:
    """Poll operation until complete or timeout."""
    elapsed = 0
    while elapsed < timeout:
        result = await get_operation(client, operation_name)
        if result.get("done", False):
            return result
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval
    raise TimeoutError(f"Operation {operation_name} timed out after {timeout}s")
