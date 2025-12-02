"""Domain knowledge models for company context."""

from pydantic import BaseModel, Field


class Domain(BaseModel):
    """A known domain in your network."""

    name: str
    ad_units: list[str] = Field(default_factory=list)


class App(BaseModel):
    """A known mobile app in your network."""

    name: str
    bundle_id: str
    ad_units: list[str] = Field(default_factory=list)


class AdStrategy(BaseModel):
    """An ad monetization strategy."""

    name: str
    description: str
    typical_dimensions: list[str] = Field(default_factory=list)
    typical_metrics: list[str] = Field(default_factory=list)


class ReportTemplate(BaseModel):
    """A predefined report template."""

    name: str
    description: str
    dimensions: list[str]
    metrics: list[str]
    default_date_range_days: int = 7


# Default knowledge - customize for your network
KNOWN_DOMAINS: list[Domain] = []
KNOWN_APPS: list[App] = []
AD_STRATEGIES: list[AdStrategy] = [
    AdStrategy(
        name="direct_sold",
        description="Guaranteed campaigns sold directly to advertisers",
        typical_dimensions=["ADVERTISER_NAME", "ORDER_NAME", "DATE"],
        typical_metrics=["TOTAL_IMPRESSIONS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    AdStrategy(
        name="programmatic",
        description="Programmatic demand via exchanges",
        typical_dimensions=["DATE", "AD_UNIT_NAME"],
        typical_metrics=["TOTAL_IMPRESSIONS", "TOTAL_ECPM", "FILL_RATE"],
    ),
    AdStrategy(
        name="house",
        description="House ads for unsold inventory",
        typical_dimensions=["DATE", "AD_UNIT_NAME"],
        typical_metrics=["TOTAL_IMPRESSIONS"],
    ),
]
REPORT_TEMPLATES: list[ReportTemplate] = [
    ReportTemplate(
        name="delivery",
        description="Standard delivery report with impressions and clicks",
        dimensions=["DATE", "AD_UNIT_NAME"],
        metrics=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR"],
    ),
    ReportTemplate(
        name="inventory",
        description="Inventory health and fill rate analysis",
        dimensions=["DATE", "AD_UNIT_NAME"],
        metrics=["AD_REQUESTS", "MATCHED_REQUESTS", "FILL_RATE"],
    ),
    ReportTemplate(
        name="revenue",
        description="Revenue analysis by advertiser",
        dimensions=["DATE", "ADVERTISER_NAME"],
        metrics=["TOTAL_IMPRESSIONS", "TOTAL_CPM_AND_CPC_REVENUE", "TOTAL_ECPM"],
    ),
]
