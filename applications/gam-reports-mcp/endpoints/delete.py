"""Delete report endpoint."""

from core.client import GAMClient


async def delete_report(
    client: GAMClient,
    network_code: str,
    report_id: str,
) -> None:
    """DELETE /networks/{network}/reports/{id}"""
    await client.delete(f"/networks/{network_code}/reports/{report_id}")
