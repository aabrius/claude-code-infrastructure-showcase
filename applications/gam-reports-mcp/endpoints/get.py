"""Get report endpoint."""

from core.client import GAMClient
from models.reports import ReportResponse


async def get_report(
    client: GAMClient,
    network_code: str,
    report_id: str,
) -> ReportResponse:
    """GET /networks/{network}/reports/{id}"""
    response = await client.get(f"/networks/{network_code}/reports/{report_id}")
    return ReportResponse.from_gam_response(response)
