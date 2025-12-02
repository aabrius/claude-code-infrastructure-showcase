"""Filter models for GAM Reports."""

from datetime import date
from typing import Literal
from pydantic import BaseModel, Field


class DateRangeFilter(BaseModel):
    """Date range filter for reports."""

    start_date: date
    end_date: date


class DomainFilter(BaseModel):
    """Filter by domains."""

    domains: list[str] = Field(description="Filter by your domains")


class AppFilter(BaseModel):
    """Filter by mobile apps."""

    app_ids: list[str] = Field(description="Your app bundle IDs")


class AdStrategyFilter(BaseModel):
    """Filter by ad strategy."""

    strategy: Literal["direct_sold", "programmatic", "house"]
