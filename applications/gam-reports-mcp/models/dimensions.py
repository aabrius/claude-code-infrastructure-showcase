"""Curated dimension definitions for GAM Reports."""

from enum import Enum
from pydantic import BaseModel, Field


class DimensionCategory(str, Enum):
    """Categories for dimensions."""

    TIME = "time"
    INVENTORY = "inventory"
    ADVERTISER = "advertiser"
    GEOGRAPHY = "geography"
    DEVICE = "device"


class Dimension(BaseModel):
    """A curated dimension with domain context."""

    name: str = Field(description="GAM API dimension name")
    category: DimensionCategory
    description: str = Field(description="What this dimension represents")
    use_case: str = Field(description="When to use this dimension")
    compatible_with: list[str] = Field(
        default_factory=list, description="Metrics that work well with this"
    )


# Curated allowlist - add your dimensions here
ALLOWED_DIMENSIONS: dict[str, Dimension] = {
    "DATE": Dimension(
        name="DATE",
        category=DimensionCategory.TIME,
        description="Daily granularity",
        use_case="Daily performance trends",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR"],
    ),
    "WEEK": Dimension(
        name="WEEK",
        category=DimensionCategory.TIME,
        description="Weekly aggregation",
        use_case="Weekly reporting",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS"],
    ),
    "MONTH": Dimension(
        name="MONTH",
        category=DimensionCategory.TIME,
        description="Monthly aggregation",
        use_case="Monthly reporting",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_REVENUE"],
    ),
    "AD_UNIT_NAME": Dimension(
        name="AD_UNIT_NAME",
        category=DimensionCategory.INVENTORY,
        description="Ad placement names",
        use_case="Performance by placement",
        compatible_with=["AD_REQUESTS", "MATCHED_REQUESTS", "FILL_RATE"],
    ),
    "AD_UNIT_CODE": Dimension(
        name="AD_UNIT_CODE",
        category=DimensionCategory.INVENTORY,
        description="Ad unit codes",
        use_case="Technical integration analysis",
        compatible_with=["AD_REQUESTS", "MATCHED_REQUESTS"],
    ),
    "ADVERTISER_NAME": Dimension(
        name="ADVERTISER_NAME",
        category=DimensionCategory.ADVERTISER,
        description="Advertiser display names",
        use_case="Revenue by advertiser",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "ORDER_NAME": Dimension(
        name="ORDER_NAME",
        category=DimensionCategory.ADVERTISER,
        description="Order/campaign names",
        use_case="Campaign performance",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS"],
    ),
    "COUNTRY_NAME": Dimension(
        name="COUNTRY_NAME",
        category=DimensionCategory.GEOGRAPHY,
        description="Country name",
        use_case="Geographic performance",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS"],
    ),
    "DEVICE_CATEGORY_NAME": Dimension(
        name="DEVICE_CATEGORY_NAME",
        category=DimensionCategory.DEVICE,
        description="Device type (Desktop, Mobile, Tablet)",
        use_case="Device performance analysis",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR"],
    ),
}
