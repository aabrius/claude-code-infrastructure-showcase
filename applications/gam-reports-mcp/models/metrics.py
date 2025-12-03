"""GAM Report metrics - curated list for GAM REST API v1.

Metrics documented from:
https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks.reports#metric
"""

from enum import Enum
from pydantic import BaseModel, Field


class MetricCategory(str, Enum):
    """Categories for GAM metrics."""

    CORE = "core"  # Core delivery metrics (impressions, CTR)
    REVENUE = "revenue"  # Revenue and eCPM metrics
    INVENTORY = "inventory"  # Ad requests, fill rate
    AD_EXCHANGE = "ad_exchange"  # Ad Exchange metrics
    ACTIVE_VIEW = "active_view"  # Viewability metrics
    PROGRAMMATIC = "programmatic"  # Programmatic/yield metrics
    AD_SPEED = "ad_speed"  # Creative load time metrics
    UNVIEWED = "unviewed"  # Unviewed reason metrics


class DataFormat(str, Enum):
    """Data format types for metrics."""

    INTEGER = "INTEGER"  # Count values (impressions, clicks, requests)
    PERCENTAGE = "PERCENTAGE"  # Rate values (CTR, fill rate, viewability rate)
    CURRENCY = "CURRENCY"  # Money values (revenue, eCPM)
    RATIO = "RATIO"  # Ratio values (match rate)
    SECONDS = "SECONDS"  # Time values in seconds


class ReportType(str, Enum):
    """Report types that metrics are compatible with."""

    HISTORICAL = "HISTORICAL"  # Standard historical reports
    AD_SPEED = "AD_SPEED"  # Ad speed reports only
    REACH = "REACH"  # Reach reports only


class Metric(BaseModel):
    """A GAM metric with domain context and API metadata."""

    name: str = Field(description="GAM API metric name")
    category: MetricCategory
    data_format: DataFormat = Field(description="Data format type")
    description: str = Field(description="Official GAM API description")
    report_types: list[ReportType] = Field(
        default_factory=lambda: [ReportType.HISTORICAL],
        description="Compatible report types",
    )


# =============================================================================
# CURATED GAM METRICS - REST API v1
# =============================================================================

ALLOWED_METRICS: dict[str, Metric] = {
    # =========================================================================
    # Core Metrics
    # =========================================================================
    "IMPRESSIONS": Metric(
        name="IMPRESSIONS",
        category=MetricCategory.CORE,
        data_format=DataFormat.INTEGER,
        description="The number of impressions delivered by the ad server.",
        report_types=[ReportType.HISTORICAL],
    ),
    "CTR": Metric(
        name="CTR",
        category=MetricCategory.CORE,
        data_format=DataFormat.PERCENTAGE,
        description="The CTR for an ad delivered by the ad server.",
        report_types=[ReportType.HISTORICAL],
    ),
    # =========================================================================
    # Revenue Metrics
    # =========================================================================
    "AVERAGE_ECPM": Metric(
        name="AVERAGE_ECPM",
        category=MetricCategory.REVENUE,
        data_format=DataFormat.CURRENCY,
        description="The average estimated cost-per-thousand-impressions earned from the CPM and CPC ads delivered by the ad server.",
        report_types=[ReportType.HISTORICAL],
    ),
    "REVENUE": Metric(
        name="REVENUE",
        category=MetricCategory.REVENUE,
        data_format=DataFormat.CURRENCY,
        description="The CPM and CPC revenue earned, calculated in publisher currency, for the ads delivered by the ad server.",
        report_types=[ReportType.HISTORICAL],
    ),
    # =========================================================================
    # Inventory Metrics
    # =========================================================================
    "AD_REQUESTS": Metric(
        name="AD_REQUESTS",
        category=MetricCategory.INVENTORY,
        data_format=DataFormat.INTEGER,
        description="The total number of times that an ad request is sent to the ad server including dynamic allocation.",
        report_types=[ReportType.HISTORICAL],
    ),
    "FILL_RATE": Metric(
        name="FILL_RATE",
        category=MetricCategory.INVENTORY,
        data_format=DataFormat.PERCENTAGE,
        description="The fill rate indicating how often an ad request is filled by the ad server including dynamic allocation.",
        report_types=[ReportType.HISTORICAL],
    ),
    "CODE_SERVED_COUNT": Metric(
        name="CODE_SERVED_COUNT",
        category=MetricCategory.INVENTORY,
        data_format=DataFormat.INTEGER,
        description="The total number of times that the code for an ad is served by the ad server including inventory-level dynamic allocation.",
        report_types=[ReportType.HISTORICAL],
    ),
    "RESPONSES_SERVED": Metric(
        name="RESPONSES_SERVED",
        category=MetricCategory.INVENTORY,
        data_format=DataFormat.INTEGER,
        description="The total number of times that an ad is served by the ad server including dynamic allocation.",
        report_types=[ReportType.HISTORICAL],
    ),
    "REWARDS_GRANTED": Metric(
        name="REWARDS_GRANTED",
        category=MetricCategory.INVENTORY,
        data_format=DataFormat.INTEGER,
        description="The number of rewards granted for rewarded video ads.",
        report_types=[ReportType.HISTORICAL],
    ),
    "UNFILLED_IMPRESSIONS": Metric(
        name="UNFILLED_IMPRESSIONS",
        category=MetricCategory.INVENTORY,
        data_format=DataFormat.INTEGER,
        description="The total number of missed impressions due to the ad servers' inability to find ads to serve, including inventory-level dynamic allocation.",
        report_types=[ReportType.HISTORICAL],
    ),
    "UNMATCHED_AD_REQUESTS": Metric(
        name="UNMATCHED_AD_REQUESTS",
        category=MetricCategory.INVENTORY,
        data_format=DataFormat.INTEGER,
        description="The total number of times that an ad is not returned by the ad server.",
        report_types=[ReportType.HISTORICAL],
    ),
    "DROPOFF_RATE": Metric(
        name="DROPOFF_RATE",
        category=MetricCategory.INVENTORY,
        data_format=DataFormat.PERCENTAGE,
        description="The drop-off rate measuring the percentage of ad requests that did not result in an impression.",
        report_types=[ReportType.HISTORICAL],
    ),
    # =========================================================================
    # Ad Exchange Metrics
    # =========================================================================
    "AD_EXCHANGE_IMPRESSIONS": Metric(
        name="AD_EXCHANGE_IMPRESSIONS",
        category=MetricCategory.AD_EXCHANGE,
        data_format=DataFormat.INTEGER,
        description="The number of impressions an Ad Exchange ad delivered for line item-level dynamic allocation.",
        report_types=[ReportType.HISTORICAL],
    ),
    "AD_EXCHANGE_CLICKS": Metric(
        name="AD_EXCHANGE_CLICKS",
        category=MetricCategory.AD_EXCHANGE,
        data_format=DataFormat.INTEGER,
        description="The number of clicks an Ad Exchange ad delivered for line item-level dynamic allocation.",
        report_types=[ReportType.HISTORICAL],
    ),
    "AD_EXCHANGE_CTR": Metric(
        name="AD_EXCHANGE_CTR",
        category=MetricCategory.AD_EXCHANGE,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of clicks an Ad Exchange ad delivered to the number of impressions it delivered for line item-level dynamic allocation.",
        report_types=[ReportType.HISTORICAL],
    ),
    "AD_EXCHANGE_REVENUE": Metric(
        name="AD_EXCHANGE_REVENUE",
        category=MetricCategory.AD_EXCHANGE,
        data_format=DataFormat.CURRENCY,
        description="Revenue generated from Ad Exchange ads delivered for line item-level dynamic allocation. Represented in publisher currency and time zone.",
        report_types=[ReportType.HISTORICAL],
    ),
    "AD_EXCHANGE_AVERAGE_ECPM": Metric(
        name="AD_EXCHANGE_AVERAGE_ECPM",
        category=MetricCategory.AD_EXCHANGE,
        data_format=DataFormat.CURRENCY,
        description="The average estimated cost-per-thousand-impressions earned from the delivery of Ad Exchange ads for line item-level dynamic allocation.",
        report_types=[ReportType.HISTORICAL],
    ),
    "AD_EXCHANGE_MATCH_RATE": Metric(
        name="AD_EXCHANGE_MATCH_RATE",
        category=MetricCategory.AD_EXCHANGE,
        data_format=DataFormat.PERCENTAGE,
        description="The fraction of Ad Exchange queries that result in a matched query. Also known as 'Coverage'.",
        report_types=[ReportType.HISTORICAL],
    ),
    # =========================================================================
    # Ad Exchange Active View Metrics
    # =========================================================================
    "AD_EXCHANGE_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS": Metric(
        name="AD_EXCHANGE_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS",
        category=MetricCategory.ACTIVE_VIEW,
        data_format=DataFormat.INTEGER,
        description="The number of impressions delivered by Ad Exchange viewed on the user's screen.",
        report_types=[ReportType.HISTORICAL],
    ),
    "AD_EXCHANGE_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS": Metric(
        name="AD_EXCHANGE_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS",
        category=MetricCategory.ACTIVE_VIEW,
        data_format=DataFormat.INTEGER,
        description="The number of impressions delivered by Ad Exchange that were measurable by Active View.",
        report_types=[ReportType.HISTORICAL],
    ),
    "AD_EXCHANGE_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS_RATE": Metric(
        name="AD_EXCHANGE_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS_RATE",
        category=MetricCategory.ACTIVE_VIEW,
        data_format=DataFormat.PERCENTAGE,
        description="The percentage of impressions delivered by Ad Exchange viewed on the user's screen (out of Ad Exchange impressions measurable by Active View).",
        report_types=[ReportType.HISTORICAL],
    ),
    "AD_EXCHANGE_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS_RATE": Metric(
        name="AD_EXCHANGE_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS_RATE",
        category=MetricCategory.ACTIVE_VIEW,
        data_format=DataFormat.PERCENTAGE,
        description="The percentage of impressions delivered by Ad Exchange that were measurable by Active View (out of all Ad Exchange impressions sampled for Active View).",
        report_types=[ReportType.HISTORICAL],
    ),
    "AD_EXCHANGE_ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS": Metric(
        name="AD_EXCHANGE_ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS",
        category=MetricCategory.ACTIVE_VIEW,
        data_format=DataFormat.INTEGER,
        description="The number of Ad Exchange impressions eligible for Active View measurement.",
        report_types=[ReportType.HISTORICAL],
    ),
    "AD_EXCHANGE_ACTIVE_VIEW_AVERAGE_VIEWABLE_TIME": Metric(
        name="AD_EXCHANGE_ACTIVE_VIEW_AVERAGE_VIEWABLE_TIME",
        category=MetricCategory.ACTIVE_VIEW,
        data_format=DataFormat.SECONDS,
        description="The average time in seconds that Ad Exchange ads were viewable on screen.",
        report_types=[ReportType.HISTORICAL],
    ),
    # =========================================================================
    # Programmatic / Yield Metrics
    # =========================================================================
    "PROGRAMMATIC_RESPONSES_SERVED": Metric(
        name="PROGRAMMATIC_RESPONSES_SERVED",
        category=MetricCategory.PROGRAMMATIC,
        data_format=DataFormat.INTEGER,
        description="Total number of ad responses served from programmatic demand sources. Includes Ad Exchange, Open Bidding, and Preferred Deals.",
        report_types=[ReportType.HISTORICAL],
    ),
    "PROGRAMMATIC_MATCH_RATE": Metric(
        name="PROGRAMMATIC_MATCH_RATE",
        category=MetricCategory.PROGRAMMATIC,
        data_format=DataFormat.PERCENTAGE,
        description="The number of programmatic responses served divided by the number of requests eligible for programmatic. Includes Ad Exchange, Open Bidding, and Preferred Deals.",
        report_types=[ReportType.HISTORICAL],
    ),
    "YIELD_GROUP_MEDIATION_FILL_RATE": Metric(
        name="YIELD_GROUP_MEDIATION_FILL_RATE",
        category=MetricCategory.PROGRAMMATIC,
        data_format=DataFormat.PERCENTAGE,
        description="Yield group mediation fill rate indicating how often a network fills an ad request.",
        report_types=[ReportType.HISTORICAL],
    ),
    "YIELD_GROUP_IMPRESSIONS": Metric(
        name="YIELD_GROUP_IMPRESSIONS",
        category=MetricCategory.PROGRAMMATIC,
        data_format=DataFormat.INTEGER,
        description="The number of impressions delivered by a yield group.",
        report_types=[ReportType.HISTORICAL],
    ),
    "YIELD_GROUP_ESTIMATED_REVENUE": Metric(
        name="YIELD_GROUP_ESTIMATED_REVENUE",
        category=MetricCategory.PROGRAMMATIC,
        data_format=DataFormat.CURRENCY,
        description="Total net revenue earned by a yield group. This revenue already excludes Google revenue share.",
        report_types=[ReportType.HISTORICAL],
    ),
    "YIELD_GROUP_MEDIATION_THIRD_PARTY_ECPM": Metric(
        name="YIELD_GROUP_MEDIATION_THIRD_PARTY_ECPM",
        category=MetricCategory.PROGRAMMATIC,
        data_format=DataFormat.CURRENCY,
        description="The eCPM reported by the third-party mediation network.",
        report_types=[ReportType.HISTORICAL],
    ),
    # =========================================================================
    # Ad Speed - Creative Load Time Metrics
    # =========================================================================
    "CREATIVE_LOAD_TIME_0_500_MS_PERCENT": Metric(
        name="CREATIVE_LOAD_TIME_0_500_MS_PERCENT",
        category=MetricCategory.AD_SPEED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions where creative load time is 0-500ms to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    "CREATIVE_LOAD_TIME_500_1000_MS_PERCENT": Metric(
        name="CREATIVE_LOAD_TIME_500_1000_MS_PERCENT",
        category=MetricCategory.AD_SPEED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions where creative load time is 500ms-1s to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    "CREATIVE_LOAD_TIME_1_2_S_PERCENT": Metric(
        name="CREATIVE_LOAD_TIME_1_2_S_PERCENT",
        category=MetricCategory.AD_SPEED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions where creative load time is 1-2 seconds to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    "CREATIVE_LOAD_TIME_2_4_S_PERCENT": Metric(
        name="CREATIVE_LOAD_TIME_2_4_S_PERCENT",
        category=MetricCategory.AD_SPEED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions where creative load time is 2-4 seconds to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    "CREATIVE_LOAD_TIME_4_8_S_PERCENT": Metric(
        name="CREATIVE_LOAD_TIME_4_8_S_PERCENT",
        category=MetricCategory.AD_SPEED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions where creative load time is 4-8 seconds to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    "CREATIVE_LOAD_TIME_GREATER_THAN_8_S_PERCENT": Metric(
        name="CREATIVE_LOAD_TIME_GREATER_THAN_8_S_PERCENT",
        category=MetricCategory.AD_SPEED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions where creative load time exceeds 8 seconds to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    # =========================================================================
    # Ad Speed - Page Navigation to Tag Loaded
    # =========================================================================
    "PAGE_NAVIGATION_TO_TAG_LOADED_TIME_0_500_MS_PERCENT": Metric(
        name="PAGE_NAVIGATION_TO_TAG_LOADED_TIME_0_500_MS_PERCENT",
        category=MetricCategory.AD_SPEED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions where page navigation to tag loaded time is 0-500ms to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    "PAGE_NAVIGATION_TO_TAG_LOADED_TIME_500_1000_MS_PERCENT": Metric(
        name="PAGE_NAVIGATION_TO_TAG_LOADED_TIME_500_1000_MS_PERCENT",
        category=MetricCategory.AD_SPEED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions where page navigation to tag loaded time is 500ms-1s to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    "PAGE_NAVIGATION_TO_TAG_LOADED_TIME_1_2_S_PERCENT": Metric(
        name="PAGE_NAVIGATION_TO_TAG_LOADED_TIME_1_2_S_PERCENT",
        category=MetricCategory.AD_SPEED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions where page navigation to tag loaded time is 1-2 seconds to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    "PAGE_NAVIGATION_TO_TAG_LOADED_TIME_2_4_S_PERCENT": Metric(
        name="PAGE_NAVIGATION_TO_TAG_LOADED_TIME_2_4_S_PERCENT",
        category=MetricCategory.AD_SPEED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions where page navigation to tag loaded time is 2-4 seconds to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    "PAGE_NAVIGATION_TO_TAG_LOADED_TIME_4_8_S_PERCENT": Metric(
        name="PAGE_NAVIGATION_TO_TAG_LOADED_TIME_4_8_S_PERCENT",
        category=MetricCategory.AD_SPEED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions where page navigation to tag loaded time is 4-8 seconds to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    "PAGE_NAVIGATION_TO_TAG_LOADED_TIME_GREATER_THAN_8_S_PERCENT": Metric(
        name="PAGE_NAVIGATION_TO_TAG_LOADED_TIME_GREATER_THAN_8_S_PERCENT",
        category=MetricCategory.AD_SPEED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions where page navigation to tag loaded time exceeds 8 seconds to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    # =========================================================================
    # Ad Speed - Tag Loaded to First Ad Request
    # =========================================================================
    "TAG_LOADED_TO_FIRST_AD_REQUEST_TIME_0_500_MS_PERCENT": Metric(
        name="TAG_LOADED_TO_FIRST_AD_REQUEST_TIME_0_500_MS_PERCENT",
        category=MetricCategory.AD_SPEED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions where tag loaded to first ad request time is 0-500ms to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    "TAG_LOADED_TO_FIRST_AD_REQUEST_TIME_500_1000_MS_PERCENT": Metric(
        name="TAG_LOADED_TO_FIRST_AD_REQUEST_TIME_500_1000_MS_PERCENT",
        category=MetricCategory.AD_SPEED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions where tag loaded to first ad request time is 500ms-1s to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    "TAG_LOADED_TO_FIRST_AD_REQUEST_TIME_1_2_S_PERCENT": Metric(
        name="TAG_LOADED_TO_FIRST_AD_REQUEST_TIME_1_2_S_PERCENT",
        category=MetricCategory.AD_SPEED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions where tag loaded to first ad request time is 1-2 seconds to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    "TAG_LOADED_TO_FIRST_AD_REQUEST_TIME_2_4_S_PERCENT": Metric(
        name="TAG_LOADED_TO_FIRST_AD_REQUEST_TIME_2_4_S_PERCENT",
        category=MetricCategory.AD_SPEED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions where tag loaded to first ad request time is 2-4 seconds to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    "TAG_LOADED_TO_FIRST_AD_REQUEST_TIME_4_8_S_PERCENT": Metric(
        name="TAG_LOADED_TO_FIRST_AD_REQUEST_TIME_4_8_S_PERCENT",
        category=MetricCategory.AD_SPEED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions where tag loaded to first ad request time is 4-8 seconds to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    "TAG_LOADED_TO_FIRST_AD_REQUEST_TIME_GREATER_THAN_8_S_PERCENT": Metric(
        name="TAG_LOADED_TO_FIRST_AD_REQUEST_TIME_GREATER_THAN_8_S_PERCENT",
        category=MetricCategory.AD_SPEED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions where tag loaded to first ad request time exceeds 8 seconds to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    # =========================================================================
    # Unviewed Reason Metrics
    # =========================================================================
    "UNVIEWED_REASON_SLOT_NEVER_ENTERED_VIEWPORT_PERCENT": Metric(
        name="UNVIEWED_REASON_SLOT_NEVER_ENTERED_VIEWPORT_PERCENT",
        category=MetricCategory.UNVIEWED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions unviewed because the ad slot never entered the viewport to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    "UNVIEWED_REASON_USER_SCROLLED_BEFORE_AD_FILLED_PERCENT": Metric(
        name="UNVIEWED_REASON_USER_SCROLLED_BEFORE_AD_FILLED_PERCENT",
        category=MetricCategory.UNVIEWED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions unviewed because user scrolled before the ad filled to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    "UNVIEWED_REASON_USER_SCROLLED_BEFORE_AD_LOADED_PERCENT": Metric(
        name="UNVIEWED_REASON_USER_SCROLLED_BEFORE_AD_LOADED_PERCENT",
        category=MetricCategory.UNVIEWED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions unviewed because user scrolled or navigated before the ad loaded to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    "UNVIEWED_REASON_USER_SCROLLED_BEFORE_1_S_PERCENT": Metric(
        name="UNVIEWED_REASON_USER_SCROLLED_BEFORE_1_S_PERCENT",
        category=MetricCategory.UNVIEWED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions unviewed because user scrolled or navigated before one second to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
    "UNVIEWED_REASON_OTHER_PERCENT": Metric(
        name="UNVIEWED_REASON_OTHER_PERCENT",
        category=MetricCategory.UNVIEWED,
        data_format=DataFormat.PERCENTAGE,
        description="The ratio of impressions unviewed because of another non-viewable-impression reason to total impressions with ad latency data, as percentage.",
        report_types=[ReportType.AD_SPEED],
    ),
}
