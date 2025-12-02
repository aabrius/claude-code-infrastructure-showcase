"""Fetch report rows endpoint."""

from typing import Any
from core.client import GAMClient
from models.reports import FetchRowsResponse


async def fetch_rows(
    client: GAMClient,
    network_code: str,
    report_id: str,
    page_size: int = 1000,
    page_token: str | None = None,
) -> FetchRowsResponse:
    """POST /networks/{network}/reports/{id}/results:fetchRows"""
    request_body: dict[str, Any] = {"pageSize": page_size}
    if page_token:
        request_body["pageToken"] = page_token

    response = await client.post(
        f"/networks/{network_code}/reports/{report_id}/results:fetchRows",
        json=request_body,
    )
    return FetchRowsResponse(
        rows=response.get("rows", []),
        next_page_token=response.get("nextPageToken"),
        total_row_count=response.get("totalRowCount", 0),
    )
