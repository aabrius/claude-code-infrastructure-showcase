# endpoints/create.py
"""Create report endpoint."""

from core.client import GAMClient
from models.reports import CreateReportRequest, ReportResponse
from models.dimensions import ALLOWED_DIMENSIONS
from models.metrics import ALLOWED_METRICS


async def create_report(
    client: GAMClient,
    network_code: str,
    request: CreateReportRequest,
) -> ReportResponse:
    """
    POST /networks/{network}/reports

    Creates a new report, validating dimensions/metrics against curated allowlist.
    """
    # Validate dimensions
    for dim in request.dimensions:
        if dim not in ALLOWED_DIMENSIONS:
            raise ValueError(f"Dimension '{dim}' not in curated allowlist")

    # Validate metrics
    for metric in request.metrics:
        if metric not in ALLOWED_METRICS:
            raise ValueError(f"Metric '{metric}' not in curated allowlist")

    response = await client.post(
        f"/networks/{network_code}/reports",
        json=request.to_gam_format(),
    )
    return ReportResponse.from_gam_response(response)
