"""Run report endpoint."""

from core.client import GAMClient


async def run_report(
    client: GAMClient,
    network_code: str,
    report_id: str,
) -> str:
    """
    POST /networks/{network}/reports/{id}:run

    Triggers report execution and returns the operation name for tracking.
    """
    response = await client.post(
        f"/networks/{network_code}/reports/{report_id}:run",
        json=None,
    )
    return response.get("name", "")
