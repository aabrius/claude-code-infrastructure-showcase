"""Filter models for GAM Reports - complete GAM API filter mapping."""

from datetime import date
from typing import Literal, Any, Union
from pydantic import BaseModel, Field, model_validator

from .enums import Operation


# =============================================================================
# GAM API Filter Value Types
# =============================================================================


class IntList(BaseModel):
    """List of integer values for filters."""

    values: list[int] = Field(default_factory=list)


class StringList(BaseModel):
    """List of string values for filters."""

    values: list[str] = Field(default_factory=list)


class DoubleList(BaseModel):
    """List of double/float values for filters."""

    values: list[float] = Field(default_factory=list)


class Slice(BaseModel):
    """Slice for range-based filtering."""

    start_index: int | None = Field(default=None, alias="startIndex")
    end_index: int | None = Field(default=None, alias="endIndex")

    model_config = {"populate_by_name": True}


class ReportValue(BaseModel):
    """
    Flexible value representation for filters.

    Only one field should be set at a time. Matches GAM REST API v1.
    """

    int_value: int | None = Field(default=None, alias="intValue")
    string_value: str | None = Field(default=None, alias="stringValue")
    double_value: float | None = Field(default=None, alias="doubleValue")
    bool_value: bool | None = Field(default=None, alias="boolValue")
    bytes_value: str | None = Field(default=None, alias="bytesValue")
    int_list: IntList | None = Field(default=None, alias="intList")
    string_list: StringList | None = Field(default=None, alias="stringList")
    double_list: DoubleList | None = Field(default=None, alias="doubleList")
    slice: Slice | None = None

    model_config = {"populate_by_name": True}

    @classmethod
    def from_int(cls, value: int) -> "ReportValue":
        """Create from integer value."""
        return cls(int_value=value)

    @classmethod
    def from_string(cls, value: str) -> "ReportValue":
        """Create from string value."""
        return cls(string_value=value)

    @classmethod
    def from_bool(cls, value: bool) -> "ReportValue":
        """Create from boolean value."""
        return cls(bool_value=value)

    @classmethod
    def from_strings(cls, values: list[str]) -> "ReportValue":
        """Create from list of strings."""
        return cls(string_list=StringList(values=values))

    @classmethod
    def from_ints(cls, values: list[int]) -> "ReportValue":
        """Create from list of integers."""
        return cls(int_list=IntList(values=values))

    def to_gam_format(self) -> dict:
        """Convert to GAM API format."""
        if self.int_value is not None:
            return {"intValue": str(self.int_value)}
        elif self.string_value is not None:
            return {"stringValue": self.string_value}
        elif self.double_value is not None:
            return {"doubleValue": self.double_value}
        elif self.bool_value is not None:
            return {"boolValue": self.bool_value}
        elif self.bytes_value is not None:
            return {"bytesValue": self.bytes_value}
        elif self.int_list is not None:
            return {"intList": {"values": [str(v) for v in self.int_list.values]}}
        elif self.string_list is not None:
            return {"stringList": {"values": self.string_list.values}}
        elif self.double_list is not None:
            return {"doubleList": {"values": self.double_list.values}}
        elif self.slice is not None:
            result = {}
            if self.slice.start_index is not None:
                result["startIndex"] = self.slice.start_index
            if self.slice.end_index is not None:
                result["endIndex"] = self.slice.end_index
            return {"slice": result}
        return {}


# =============================================================================
# GAM API Filter Structures
# =============================================================================


class Field_(BaseModel):
    """
    Identifies a dimension or metric field for filtering.

    Note: Named Field_ to avoid conflict with pydantic.Field
    """

    dimension: str | None = None
    metric: str | None = None

    @model_validator(mode="after")
    def validate_one_of(self) -> "Field_":
        """Ensure exactly one of dimension or metric is set."""
        has_dimension = self.dimension is not None
        has_metric = self.metric is not None
        if not has_dimension and not has_metric:
            raise ValueError("Either dimension or metric must be set")
        if has_dimension and has_metric:
            raise ValueError("Cannot set both dimension and metric")
        return self

    @classmethod
    def from_dimension(cls, name: str) -> "Field_":
        """Create field targeting a dimension."""
        return cls(dimension=name)

    @classmethod
    def from_metric(cls, name: str) -> "Field_":
        """Create field targeting a metric."""
        return cls(metric=name)

    def to_gam_format(self) -> dict:
        """Convert to GAM API format."""
        if self.dimension:
            return {"dimension": self.dimension}
        return {"metric": self.metric}


class FieldFilter(BaseModel):
    """Field-based filter with operation and value. Matches GAM REST API v1."""

    field: Field_ = Field(description="The field to filter on")
    operation: Operation = Field(description="Filter operation")
    values: list[ReportValue] = Field(default_factory=list, description="Filter values")
    not_: bool = Field(default=False, alias="not", description="Negate the filter")
    time_period_index: int | None = Field(
        default=None,
        alias="timePeriodIndex",
        description="For filtering on specific time period columns",
    )
    metric_value_type: str | None = Field(
        default=None,
        alias="metricValueType",
        description="Metric value type (defaults to PRIMARY)",
    )

    model_config = {"populate_by_name": True}

    @classmethod
    def equals(cls, dimension: str, value: str) -> "FieldFilter":
        """Create equality filter using IN with single value (API standard)."""
        return cls(
            field=Field_.from_dimension(dimension),
            operation=Operation.IN,
            values=[ReportValue.from_strings([value])],
        )

    @classmethod
    def in_values(cls, dimension: str, values: list[str]) -> "FieldFilter":
        """Create IN filter for a dimension with multiple values."""
        return cls(
            field=Field_.from_dimension(dimension),
            operation=Operation.IN,
            values=[ReportValue.from_strings(values)],
        )

    @classmethod
    def contains(cls, dimension: str, value: str) -> "FieldFilter":
        """Create CONTAINS filter for a dimension."""
        return cls(
            field=Field_.from_dimension(dimension),
            operation=Operation.CONTAINS,
            values=[ReportValue.from_string(value)],
        )

    @classmethod
    def greater_than(cls, metric: str, value: int | float) -> "FieldFilter":
        """Create GREATER_THAN filter for a metric."""
        return cls(
            field=Field_.from_metric(metric),
            operation=Operation.GREATER_THAN,
            values=[ReportValue.from_int(int(value))],
        )

    @classmethod
    def less_than(cls, metric: str, value: int | float) -> "FieldFilter":
        """Create LESS_THAN filter for a metric."""
        return cls(
            field=Field_.from_metric(metric),
            operation=Operation.LESS_THAN,
            values=[ReportValue.from_int(int(value))],
        )

    @classmethod
    def matches(cls, dimension: str, pattern: str) -> "FieldFilter":
        """Create MATCHES filter for regex pattern matching."""
        return cls(
            field=Field_.from_dimension(dimension),
            operation=Operation.MATCHES,
            values=[ReportValue.from_string(pattern)],
        )

    @classmethod
    def between(cls, metric: str, min_val: int, max_val: int) -> "FieldFilter":
        """Create BETWEEN filter for a range of values."""
        return cls(
            field=Field_.from_metric(metric),
            operation=Operation.BETWEEN,
            values=[ReportValue.from_int(min_val), ReportValue.from_int(max_val)],
        )

    def to_gam_format(self) -> dict:
        """Convert to GAM API format."""
        result = {
            "field": self.field.to_gam_format(),
            "operation": self.operation.value,
            "values": [v.to_gam_format() for v in self.values],
        }
        if self.not_:
            result["not"] = True
        if self.time_period_index is not None:
            result["timePeriodIndex"] = self.time_period_index
        if self.metric_value_type is not None:
            result["metricValueType"] = self.metric_value_type
        return {"fieldFilter": result}


class FilterList(BaseModel):
    """List of filters (used in andFilter/orFilter). Matches GAM REST API v1."""

    filters: list["Filter"] = Field(default_factory=list)

    def to_gam_format(self) -> list[dict]:
        """Convert to GAM API format (array of filters)."""
        return [f.to_gam_format() for f in self.filters]


class Filter(BaseModel):
    """
    GAM Report filter - supports 4 union types per API spec.

    Exactly ONE of these must be set:
    - field_filter: A filter on a single field
    - not_filter: Negates another filter
    - and_filter: Combines filters with AND logic
    - or_filter: Combines filters with OR logic

    Examples:
        # Simple equals filter (uses IN with single value)
        filter = Filter.field_equals("ADVERTISER_NAME", "Acme Corp")

        # IN filter for multiple values
        filter = Filter.field_in("COUNTRY_NAME", ["USA", "Canada", "Mexico"])

        # Combine filters with AND
        filter = Filter.and_([
            Filter.field_equals("ADVERTISER_NAME", "Acme Corp"),
            Filter.field_greater_than("TOTAL_IMPRESSIONS", 1000),
        ])

        # Negate a filter
        filter = Filter.not_(Filter.field_equals("COUNTRY_NAME", "Unknown"))
    """

    field_filter: FieldFilter | None = Field(default=None, alias="fieldFilter")
    not_filter: "Filter | None" = Field(default=None, alias="notFilter")
    and_filter: FilterList | None = Field(default=None, alias="andFilter")
    or_filter: FilterList | None = Field(default=None, alias="orFilter")

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def validate_one_of(self) -> "Filter":
        """Ensure exactly one filter type is set."""
        set_fields = sum([
            self.field_filter is not None,
            self.not_filter is not None,
            self.and_filter is not None,
            self.or_filter is not None,
        ])
        if set_fields == 0:
            raise ValueError("One of fieldFilter, notFilter, andFilter, or orFilter must be set")
        if set_fields > 1:
            raise ValueError("Only one of fieldFilter, notFilter, andFilter, or orFilter can be set")
        return self

    @classmethod
    def field_equals(cls, dimension: str, value: str) -> "Filter":
        """Create equality filter (uses IN with single value per API spec)."""
        return cls(field_filter=FieldFilter.equals(dimension, value))

    @classmethod
    def field_in(cls, dimension: str, values: list[str]) -> "Filter":
        """Create IN filter with multiple values."""
        return cls(field_filter=FieldFilter.in_values(dimension, values))

    @classmethod
    def field_contains(cls, dimension: str, value: str) -> "Filter":
        """Create CONTAINS filter."""
        return cls(field_filter=FieldFilter.contains(dimension, value))

    @classmethod
    def field_greater_than(cls, metric: str, value: int | float) -> "Filter":
        """Create GREATER_THAN filter for metric."""
        return cls(field_filter=FieldFilter.greater_than(metric, value))

    @classmethod
    def field_less_than(cls, metric: str, value: int | float) -> "Filter":
        """Create LESS_THAN filter for metric."""
        return cls(field_filter=FieldFilter.less_than(metric, value))

    @classmethod
    def field_matches(cls, dimension: str, pattern: str) -> "Filter":
        """Create MATCHES filter for regex pattern."""
        return cls(field_filter=FieldFilter.matches(dimension, pattern))

    @classmethod
    def field_between(cls, metric: str, min_val: int, max_val: int) -> "Filter":
        """Create BETWEEN filter for range."""
        return cls(field_filter=FieldFilter.between(metric, min_val, max_val))

    @classmethod
    def not_(cls, filter: "Filter") -> "Filter":
        """Negate a filter."""
        return cls(not_filter=filter)

    @classmethod
    def and_(cls, filters: list["Filter"]) -> "Filter":
        """Combine filters with AND logic."""
        return cls(and_filter=FilterList(filters=filters))

    @classmethod
    def or_(cls, filters: list["Filter"]) -> "Filter":
        """Combine filters with OR logic."""
        return cls(or_filter=FilterList(filters=filters))

    def to_gam_format(self) -> dict:
        """Convert to GAM API format."""
        if self.field_filter:
            return self.field_filter.to_gam_format()
        elif self.not_filter:
            return {"notFilter": self.not_filter.to_gam_format()}
        elif self.and_filter:
            return {"andFilter": {"filters": self.and_filter.to_gam_format()}}
        elif self.or_filter:
            return {"orFilter": {"filters": self.or_filter.to_gam_format()}}
        return {}


# =============================================================================
# Domain-Specific Convenience Filters (Your Knowledge Base)
# =============================================================================


class DateRangeFilter(BaseModel):
    """Date range filter for reports (convenience wrapper)."""

    start_date: date
    end_date: date


class DomainFilter(BaseModel):
    """Filter by domains."""

    domains: list[str] = Field(description="Filter by your domains")

    def to_filter(self) -> Filter:
        """Convert to GAM Filter."""
        return Filter.field_in("AD_UNIT_NAME", self.domains)


class AppFilter(BaseModel):
    """Filter by mobile apps."""

    app_ids: list[str] = Field(description="Your app bundle IDs")

    def to_filter(self) -> Filter:
        """Convert to GAM Filter."""
        return Filter.field_in("APP_ID", self.app_ids)


class AdStrategyFilter(BaseModel):
    """Filter by ad strategy."""

    strategy: Literal["direct_sold", "programmatic", "house"]

    def to_filter(self) -> Filter:
        """Convert to GAM Filter based on strategy."""
        # Map strategy to appropriate GAM filter
        strategy_map = {
            "direct_sold": ("LINE_ITEM_TYPE", ["STANDARD", "SPONSORSHIP"]),
            "programmatic": ("DEMAND_CHANNEL", ["AD_EXCHANGE", "OPEN_BIDDING"]),
            "house": ("LINE_ITEM_TYPE", ["HOUSE"]),
        }
        dimension, values = strategy_map[self.strategy]
        return Filter.field_in(dimension, values)


# Update forward references
FilterList.model_rebuild()
Filter.model_rebuild()
