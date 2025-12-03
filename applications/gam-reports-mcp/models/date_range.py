"""Date range models for GAM Reports."""

from datetime import date as date_type
from typing import Union
from pydantic import BaseModel, Field, model_validator

from .enums import RelativeDateRange


class Date(BaseModel):
    """Calendar date representation matching GAM API format."""

    year: int = Field(ge=1900, le=2100, description="Year (1900-2100)")
    month: int = Field(ge=1, le=12, description="Month (1-12)")
    day: int = Field(ge=1, le=31, description="Day (1-31)")

    @classmethod
    def from_date(cls, d: date_type) -> "Date":
        """Create from Python date object."""
        return cls(year=d.year, month=d.month, day=d.day)

    @classmethod
    def from_string(cls, s: str) -> "Date":
        """Create from ISO format string (YYYY-MM-DD)."""
        parts = s.split("-")
        return cls(year=int(parts[0]), month=int(parts[1]), day=int(parts[2]))

    def to_date(self) -> date_type:
        """Convert to Python date object."""
        return date_type(self.year, self.month, self.day)

    def to_iso(self) -> str:
        """Convert to ISO format string."""
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

    def to_gam_format(self) -> dict:
        """Convert to GAM API format."""
        return {"year": self.year, "month": self.month, "day": self.day}


class FixedDateRange(BaseModel):
    """Explicit date range with start and end dates."""

    start_date: Date = Field(alias="startDate", description="Start date of the range")
    end_date: Date = Field(alias="endDate", description="End date of the range")

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def validate_dates(self) -> "FixedDateRange":
        """Ensure end_date is not before start_date."""
        if self.end_date.to_date() < self.start_date.to_date():
            raise ValueError("end_date must not be before start_date")
        return self

    @classmethod
    def from_dates(cls, start: date_type, end: date_type) -> "FixedDateRange":
        """Create from Python date objects."""
        return cls(start_date=Date.from_date(start), end_date=Date.from_date(end))

    @classmethod
    def from_strings(cls, start: str, end: str) -> "FixedDateRange":
        """Create from ISO format strings."""
        return cls(start_date=Date.from_string(start), end_date=Date.from_string(end))

    def to_gam_format(self) -> dict:
        """Convert to GAM API format."""
        return {
            "fixedDateRange": {
                "startDate": self.start_date.to_gam_format(),
                "endDate": self.end_date.to_gam_format(),
            }
        }


class DateRange(BaseModel):
    """
    Date range that can be either fixed or relative.

    Use fixed_date_range for explicit start/end dates.
    Use relative_date_range for dynamic periods like TODAY, LAST_7_DAYS, etc.
    """

    fixed_date_range: FixedDateRange | None = Field(
        default=None, alias="fixedDateRange", description="Explicit date range"
    )
    relative_date_range: RelativeDateRange | None = Field(
        default=None, alias="relativeDateRange", description="Dynamic date range"
    )

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def validate_one_of(self) -> "DateRange":
        """Ensure exactly one of fixed or relative is set."""
        has_fixed = self.fixed_date_range is not None
        has_relative = self.relative_date_range is not None
        if not has_fixed and not has_relative:
            raise ValueError("Either fixed_date_range or relative_date_range must be set")
        if has_fixed and has_relative:
            raise ValueError("Cannot set both fixed_date_range and relative_date_range")
        return self

    @classmethod
    def fixed(cls, start: date_type | str, end: date_type | str) -> "DateRange":
        """Create a fixed date range."""
        if isinstance(start, str):
            fixed = FixedDateRange.from_strings(start, end)
        else:
            fixed = FixedDateRange.from_dates(start, end)
        return cls(fixed_date_range=fixed)

    @classmethod
    def relative(cls, period: RelativeDateRange | str) -> "DateRange":
        """Create a relative date range."""
        if isinstance(period, str):
            period = RelativeDateRange(period)
        return cls(relative_date_range=period)

    @classmethod
    def today(cls) -> "DateRange":
        """Create TODAY relative date range."""
        return cls.relative(RelativeDateRange.TODAY)

    @classmethod
    def yesterday(cls) -> "DateRange":
        """Create YESTERDAY relative date range."""
        return cls.relative(RelativeDateRange.YESTERDAY)

    @classmethod
    def last_7_days(cls) -> "DateRange":
        """Create LAST_7_DAYS relative date range."""
        return cls.relative(RelativeDateRange.LAST_7_DAYS)

    @classmethod
    def last_30_days(cls) -> "DateRange":
        """Create LAST_30_DAYS relative date range."""
        return cls.relative(RelativeDateRange.LAST_30_DAYS)

    @classmethod
    def this_month(cls) -> "DateRange":
        """Create THIS_MONTH relative date range."""
        return cls.relative(RelativeDateRange.THIS_MONTH)

    @classmethod
    def previous_month(cls) -> "DateRange":
        """Create PREVIOUS_MONTH relative date range."""
        return cls.relative(RelativeDateRange.PREVIOUS_MONTH)

    def to_gam_format(self) -> dict:
        """Convert to GAM API format."""
        if self.fixed_date_range:
            return self.fixed_date_range.to_gam_format()
        else:
            return {"relativeDateRange": self.relative_date_range.value}

    def is_fixed(self) -> bool:
        """Check if this is a fixed date range."""
        return self.fixed_date_range is not None

    def is_relative(self) -> bool:
        """Check if this is a relative date range."""
        return self.relative_date_range is not None
