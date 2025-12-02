"""Update report endpoint."""

from typing import Any
from core.client import GAMClient
from models.reports import ReportResponse


async def update_report(
    client: GAMClient,
    network_code: str,
    report_id: str,
    updates: dict[str, Any],
) -> ReportResponse:
    """PATCH /networks/{network}/reports/{id}"""
    response = await client.patch(
        f"/networks/{network_code}/reports/{report_id}",
        json=updates,
    )
    return ReportResponse.from_gam_response(response)
