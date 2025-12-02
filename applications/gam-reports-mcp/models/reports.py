"""Report request and response models."""

from datetime import date
from typing import Any
from pydantic import BaseModel, Field


class CreateReportRequest(BaseModel):
    """Request to create a new report."""

    display_name: str | None = None
    dimensions: list[str]
    metrics: list[str]
    start_date: date | str
    end_date: date | str
    filters: dict[str, Any] | None = None

    def to_gam_format(self) -> dict[str, Any]:
        """Convert to GAM REST API format."""
        start = (
            self.start_date
            if isinstance(self.start_date, str)
            else self.start_date.isoformat()
        )
        end = (
            self.end_date
            if isinstance(self.end_date, str)
            else self.end_date.isoformat()
        )

        report_def: dict[str, Any] = {
            "dimensions": self.dimensions,
            "metrics": self.metrics,
            "dateRange": {
                "startDate": {"year": int(start[:4]), "month": int(start[5:7]), "day": int(start[8:10])},
                "endDate": {"year": int(end[:4]), "month": int(end[5:7]), "day": int(end[8:10])},
            },
        }

        if self.filters:
            report_def["filters"] = self.filters

        result: dict[str, Any] = {"reportDefinition": report_def}

        if self.display_name:
            result["displayName"] = self.display_name

        return result


class ReportResponse(BaseModel):
    """Response from report operations."""

    name: str = Field(description="Resource name: networks/{network}/reports/{id}")
    report_id: str = Field(description="The report ID")
    display_name: str | None = None
    state: str = Field(default="UNKNOWN", description="Report state")

    @classmethod
    def from_gam_response(cls, data: dict[str, Any]) -> "ReportResponse":
        """Create from GAM API response."""
        name = data.get("name", "")
        # Extract report_id from name: networks/123/reports/456 -> 456
        report_id = name.split("/")[-1] if name else ""
        return cls(
            name=name,
            report_id=report_id,
            display_name=data.get("displayName"),
            state=data.get("state", "UNKNOWN"),
        )


class FetchRowsResponse(BaseModel):
    """Response from fetching report rows."""

    rows: list[dict[str, Any]] = Field(default_factory=list)
    next_page_token: str | None = None
    total_row_count: int = 0
