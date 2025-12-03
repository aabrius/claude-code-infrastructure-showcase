"""Report models for GAM Reports - complete GAM API report mapping."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field

from .enums import (
    Visibility,
    ReportType,
    TimePeriodColumn,
    TimeZoneSource,
    ReportState,
    ComparisonType,
)
from .date_range import DateRange
from .filters import Filter
from .schedule import ScheduleOptions


# =============================================================================
# Sort and Flag Models
# =============================================================================


class Sort(BaseModel):
    """Default result ordering for reports."""

    field: str = Field(description="Field name to sort by (dimension or metric)")
    descending: bool = Field(default=True, description="Sort descending if True")

    @classmethod
    def by(cls, field: str, descending: bool = True) -> "Sort":
        """Create sort specification."""
        return cls(field=field, descending=descending)

    @classmethod
    def ascending(cls, field: str) -> "Sort":
        """Create ascending sort."""
        return cls(field=field, descending=False)

    @classmethod
    def descending(cls, field: str) -> "Sort":
        """Create descending sort."""
        return cls(field=field, descending=True)

    def to_gam_format(self) -> dict:
        """Convert to GAM API format."""
        return {
            "field": self.field,
            "descending": self.descending,
        }


class Flag(BaseModel):
    """
    Row-marking criteria for flagging specific rows in results.

    Per GAM API spec, filters is an array that combines with AND logic.
    All filters must match for the flag to trigger.
    """

    name: str = Field(description="Flag identifier/name")
    filters: list[Filter] = Field(
        default_factory=list,
        description="Conditions that must ALL match to trigger this flag (AND logic)",
    )

    @classmethod
    def when(cls, name: str, *filters: Filter) -> "Flag":
        """Create a flag with specified conditions (AND logic)."""
        return cls(name=name, filters=list(filters))

    @classmethod
    def with_filter(cls, name: str, filter: Filter) -> "Flag":
        """Create a flag with a single filter condition."""
        return cls(name=name, filters=[filter])

    @classmethod
    def high_impressions(cls, threshold: int = 100000) -> "Flag":
        """Flag rows with impressions above threshold."""
        return cls(
            name="HIGH_IMPRESSIONS",
            filters=[Filter.field_greater_than("TOTAL_IMPRESSIONS", threshold)],
        )

    @classmethod
    def low_ctr(cls, threshold: float = 0.01) -> "Flag":
        """Flag rows with CTR below threshold."""
        return cls(
            name="LOW_CTR",
            filters=[Filter.field_less_than("CTR", threshold)],
        )

    def to_gam_format(self) -> dict:
        """Convert to GAM API format."""
        return {
            "name": self.name,
            "filters": [f.to_gam_format() for f in self.filters],
        }


# =============================================================================
# Report Definition
# =============================================================================


class ReportDefinition(BaseModel):
    """
    Specifies how to execute a report - the core configuration.

    This maps to the GAM API ReportDefinition object which contains
    all the configuration needed to run a report.
    """

    dimensions: list[str] = Field(description="Breakdown fields for the report")
    metrics: list[str] = Field(description="Measurement fields for the report")
    date_range: DateRange = Field(alias="dateRange", description="Primary date range")
    report_type: ReportType = Field(
        default=ReportType.HISTORICAL,
        alias="reportType",
        description="Report classification",
    )
    filters: list[Filter] = Field(default_factory=list, description="Result filters")
    sorts: list[Sort] = Field(default_factory=list, description="Default sort order")
    flags: list[Flag] = Field(default_factory=list, description="Row flagging conditions")
    time_zone_source: TimeZoneSource = Field(
        default=TimeZoneSource.PUBLISHER,
        alias="timeZoneSource",
        description="Timezone source",
    )
    time_zone: str | None = Field(
        default=None,
        alias="timeZone",
        description="IANA timezone if timeZoneSource is PROVIDED",
    )
    currency_code: str | None = Field(
        default=None,
        alias="currencyCode",
        description="ISO 4217 currency code (e.g., USD, EUR)",
    )
    comparison_date_range: DateRange | None = Field(
        default=None,
        alias="comparisonDateRange",
        description="Optional comparison period",
    )
    time_period_column: TimePeriodColumn | None = Field(
        default=None,
        alias="timePeriodColumn",
        description="Time period grouping for comparison",
    )
    custom_dimension_key_ids: list[int] = Field(
        default_factory=list,
        alias="customDimensionKeyIds",
        description="Custom dimension mappings",
    )
    line_item_custom_field_ids: list[int] = Field(
        default_factory=list,
        alias="lineItemCustomFieldIds",
        description="Line item custom field IDs",
    )
    order_custom_field_ids: list[int] = Field(
        default_factory=list,
        alias="orderCustomFieldIds",
        description="Order custom field IDs",
    )
    creative_custom_field_ids: list[int] = Field(
        default_factory=list,
        alias="creativeCustomFieldIds",
        description="Creative custom field IDs",
    )

    model_config = {"populate_by_name": True}

    def to_gam_format(self) -> dict:
        """Convert to GAM API format."""
        result: dict[str, Any] = {
            "dimensions": self.dimensions,
            "metrics": self.metrics,
            "dateRange": self.date_range.to_gam_format(),
            "reportType": self.report_type.value,
        }

        if self.filters:
            result["filters"] = [f.to_gam_format() for f in self.filters]
        if self.sorts:
            result["sorts"] = [s.to_gam_format() for s in self.sorts]
        if self.flags:
            result["flags"] = [f.to_gam_format() for f in self.flags]
        if self.time_zone_source != TimeZoneSource.PUBLISHER:
            result["timeZoneSource"] = self.time_zone_source.value
        if self.time_zone:
            result["timeZone"] = self.time_zone
        if self.currency_code:
            result["currencyCode"] = self.currency_code
        if self.comparison_date_range:
            result["comparisonDateRange"] = self.comparison_date_range.to_gam_format()
        if self.time_period_column:
            result["timePeriodColumn"] = self.time_period_column.value
        if self.custom_dimension_key_ids:
            result["customDimensionKeyIds"] = [
                str(id) for id in self.custom_dimension_key_ids
            ]
        if self.line_item_custom_field_ids:
            result["lineItemCustomFieldIds"] = [
                str(id) for id in self.line_item_custom_field_ids
            ]
        if self.order_custom_field_ids:
            result["orderCustomFieldIds"] = [
                str(id) for id in self.order_custom_field_ids
            ]
        if self.creative_custom_field_ids:
            result["creativeCustomFieldIds"] = [
                str(id) for id in self.creative_custom_field_ids
            ]

        return result


# =============================================================================
# Report Model (Top-Level Entity)
# =============================================================================


class Report(BaseModel):
    """
    Complete Report resource - the top-level GAM Report entity.

    This is the main model representing a saved report in GAM.
    """

    name: str | None = Field(
        default=None, description="Resource name: networks/{network}/reports/{id}"
    )
    report_id: str | None = Field(
        default=None, alias="reportId", description="Report ID (output only)"
    )
    display_name: str | None = Field(
        default=None, alias="displayName", description="User-facing report name"
    )
    visibility: Visibility = Field(
        default=Visibility.DRAFT, description="Report visibility"
    )
    report_definition: ReportDefinition = Field(
        alias="reportDefinition", description="Report configuration"
    )
    schedule_options: ScheduleOptions | None = Field(
        default=None, alias="scheduleOptions", description="Scheduling configuration"
    )
    update_time: str | None = Field(
        default=None, alias="updateTime", description="Last modification timestamp"
    )
    create_time: str | None = Field(
        default=None, alias="createTime", description="Creation timestamp"
    )
    locale: str | None = Field(
        default=None, description="Locale from request time (output only)"
    )

    model_config = {"populate_by_name": True}

    @classmethod
    def from_gam_response(cls, data: dict[str, Any]) -> "Report":
        """Create Report from GAM API response."""
        # Extract report_id from name if present
        name = data.get("name", "")
        report_id = name.split("/")[-1] if name else None

        # Parse report definition
        report_def_data = data.get("reportDefinition", {})
        date_range_data = report_def_data.get("dateRange", {})

        # Build DateRange
        if "fixedDateRange" in date_range_data:
            fixed = date_range_data["fixedDateRange"]
            date_range = DateRange.fixed(
                f"{fixed['startDate']['year']}-{fixed['startDate']['month']:02d}-{fixed['startDate']['day']:02d}",
                f"{fixed['endDate']['year']}-{fixed['endDate']['month']:02d}-{fixed['endDate']['day']:02d}",
            )
        elif "relativeDateRange" in date_range_data:
            date_range = DateRange.relative(date_range_data["relativeDateRange"])
        else:
            # Default to last 7 days
            date_range = DateRange.last_7_days()

        report_definition = ReportDefinition(
            dimensions=report_def_data.get("dimensions", []),
            metrics=report_def_data.get("metrics", []),
            date_range=date_range,
            report_type=ReportType(
                report_def_data.get("reportType", "HISTORICAL")
            ),
        )

        return cls(
            name=name,
            report_id=report_id,
            display_name=data.get("displayName"),
            visibility=Visibility(data.get("visibility", "DRAFT")),
            report_definition=report_definition,
            update_time=data.get("updateTime"),
            create_time=data.get("createTime"),
            locale=data.get("locale"),
        )

    def to_gam_format(self) -> dict:
        """Convert to GAM API format for create/update."""
        result: dict[str, Any] = {
            "reportDefinition": self.report_definition.to_gam_format(),
            "visibility": self.visibility.value,
        }

        if self.display_name:
            result["displayName"] = self.display_name
        if self.schedule_options:
            result["scheduleOptions"] = self.schedule_options.to_gam_format()

        return result


# =============================================================================
# Request/Response Models for API Operations
# =============================================================================


class CreateReportRequest(BaseModel):
    """Request to create a new report (simplified interface)."""

    display_name: str | None = None
    dimensions: list[str]
    metrics: list[str]
    start_date: str  # ISO format YYYY-MM-DD
    end_date: str  # ISO format YYYY-MM-DD
    filters: list[Filter] | None = None
    report_type: ReportType = Field(default=ReportType.HISTORICAL)
    visibility: Visibility = Field(default=Visibility.DRAFT)

    def to_report(self) -> Report:
        """Convert to full Report model."""
        return Report(
            display_name=self.display_name,
            visibility=self.visibility,
            report_definition=ReportDefinition(
                dimensions=self.dimensions,
                metrics=self.metrics,
                date_range=DateRange.fixed(self.start_date, self.end_date),
                report_type=self.report_type,
                filters=self.filters or [],
            ),
        )

    def to_gam_format(self) -> dict[str, Any]:
        """Convert to GAM REST API format."""
        return self.to_report().to_gam_format()


class ReportResponse(BaseModel):
    """Response from report operations."""

    name: str = Field(description="Resource name: networks/{network}/reports/{id}")
    report_id: str = Field(description="The report ID")
    display_name: str | None = None
    visibility: Visibility = Field(default=Visibility.DRAFT)
    state: ReportState = Field(default=ReportState.STATE_UNSPECIFIED)

    @classmethod
    def from_gam_response(cls, data: dict[str, Any]) -> "ReportResponse":
        """Create from GAM API response."""
        name = data.get("name", "")
        report_id = name.split("/")[-1] if name else ""
        return cls(
            name=name,
            report_id=report_id,
            display_name=data.get("displayName"),
            visibility=Visibility(data.get("visibility", "DRAFT")),
            state=ReportState(data.get("state", "STATE_UNSPECIFIED")),
        )


class RunReportResponse(BaseModel):
    """Response from running a report (long-running operation)."""

    operation_name: str = Field(
        alias="name", description="Operation name for polling"
    )
    done: bool = Field(default=False, description="Whether operation is complete")
    result: dict[str, Any] | None = Field(
        default=None, description="Result when done=True"
    )
    error: dict[str, Any] | None = Field(
        default=None, description="Error if operation failed"
    )

    model_config = {"populate_by_name": True}

    @classmethod
    def from_gam_response(cls, data: dict[str, Any]) -> "RunReportResponse":
        """Create from GAM API response."""
        return cls(
            operation_name=data.get("name", ""),
            done=data.get("done", False),
            result=data.get("response"),
            error=data.get("error"),
        )


class ReportRow(BaseModel):
    """A single row of report data."""

    dimension_values: dict[str, str] = Field(
        default_factory=dict, alias="dimensionValues"
    )
    metric_values: dict[str, Any] = Field(default_factory=dict, alias="metricValues")

    model_config = {"populate_by_name": True}


class FetchRowsResponse(BaseModel):
    """Response from fetching report rows."""

    rows: list[ReportRow] = Field(default_factory=list)
    total_row_count: int = Field(default=0, alias="totalRowCount")
    next_page_token: str | None = Field(default=None, alias="nextPageToken")
    comparison_rows: list[ReportRow] = Field(
        default_factory=list, alias="comparisonRows"
    )

    model_config = {"populate_by_name": True}

    @classmethod
    def from_gam_response(cls, data: dict[str, Any]) -> "FetchRowsResponse":
        """Create from GAM API response."""
        rows = []
        for row_data in data.get("rows", []):
            rows.append(
                ReportRow(
                    dimension_values=row_data.get("dimensionValues", {}),
                    metric_values=row_data.get("metricValues", {}),
                )
            )

        comparison_rows = []
        for row_data in data.get("comparisonRows", []):
            comparison_rows.append(
                ReportRow(
                    dimension_values=row_data.get("dimensionValues", {}),
                    metric_values=row_data.get("metricValues", {}),
                )
            )

        return cls(
            rows=rows,
            total_row_count=data.get("totalRowCount", 0),
            next_page_token=data.get("nextPageToken"),
            comparison_rows=comparison_rows,
        )

    def to_dicts(self) -> list[dict[str, Any]]:
        """Convert rows to list of flat dictionaries."""
        result = []
        for row in self.rows:
            flat = {}
            flat.update(row.dimension_values)
            flat.update(row.metric_values)
            result.append(flat)
        return result
