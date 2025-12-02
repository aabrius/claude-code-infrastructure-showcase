"""Curated metric definitions for GAM Reports."""

from enum import Enum
from pydantic import BaseModel, Field


class MetricCategory(str, Enum):
    """Categories for metrics."""

    DELIVERY = "delivery"
    REVENUE = "revenue"
    INVENTORY = "inventory"
    ENGAGEMENT = "engagement"


class Metric(BaseModel):
    """A curated metric with domain context."""

    name: str = Field(description="GAM API metric name")
    category: MetricCategory
    description: str = Field(description="What this metric represents")
    use_case: str = Field(description="When to use this metric")


# Curated allowlist - add your metrics here
ALLOWED_METRICS: dict[str, Metric] = {
    "TOTAL_IMPRESSIONS": Metric(
        name="TOTAL_IMPRESSIONS",
        category=MetricCategory.DELIVERY,
        description="Total ad impressions served",
        use_case="Volume analysis",
    ),
    "TOTAL_CLICKS": Metric(
        name="TOTAL_CLICKS",
        category=MetricCategory.DELIVERY,
        description="Total clicks on ads",
        use_case="Engagement analysis",
    ),
    "TOTAL_CTR": Metric(
        name="TOTAL_CTR",
        category=MetricCategory.ENGAGEMENT,
        description="Click-through rate",
        use_case="Ad effectiveness",
    ),
    "TOTAL_CPM_AND_CPC_REVENUE": Metric(
        name="TOTAL_CPM_AND_CPC_REVENUE",
        category=MetricCategory.REVENUE,
        description="Combined CPM and CPC revenue",
        use_case="Total revenue analysis",
    ),
    "TOTAL_ECPM": Metric(
        name="TOTAL_ECPM",
        category=MetricCategory.REVENUE,
        description="Effective CPM",
        use_case="Yield optimization",
    ),
    "AD_REQUESTS": Metric(
        name="AD_REQUESTS",
        category=MetricCategory.INVENTORY,
        description="Total ad requests",
        use_case="Demand analysis",
    ),
    "MATCHED_REQUESTS": Metric(
        name="MATCHED_REQUESTS",
        category=MetricCategory.INVENTORY,
        description="Requests matched with ads",
        use_case="Fill analysis",
    ),
    "FILL_RATE": Metric(
        name="FILL_RATE",
        category=MetricCategory.INVENTORY,
        description="Percentage of requests filled",
        use_case="Inventory efficiency",
    ),
}
