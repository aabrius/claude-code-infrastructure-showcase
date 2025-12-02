"""
GAM Report Dimensions and Metrics - Pydantic Models and Constants.

Complete reference for all available Google Ad Manager report dimensions
and metrics (REST API v1 / v202511).

This module provides:
- Complete lists of valid dimensions and metrics
- Pydantic models with validation
- Category-based groupings for discovery
- Compatibility mappings between REST and SOAP APIs
"""

from enum import Enum
from typing import List, Literal, Optional, Set
from pydantic import BaseModel, Field, field_validator


# =============================================================================
# DIMENSION CONSTANTS (200+ dimensions from REST API v1)
# =============================================================================

# Time Dimensions
TIME_DIMENSIONS = {
    "DATE", "HOUR", "DAY_OF_WEEK", "WEEK", "MONTH", "YEAR",
}

# Advertiser Dimensions
ADVERTISER_DIMENSIONS = {
    "ADVERTISER_ID", "ADVERTISER_NAME", "ADVERTISER_DOMAIN_NAME",
    "ADVERTISER_EXTERNAL_ID", "ADVERTISER_LABELS", "ADVERTISER_LABEL_IDS",
    "ADVERTISER_PRIMARY_CONTACT", "ADVERTISER_STATUS", "ADVERTISER_STATUS_NAME",
    "ADVERTISER_TYPE", "ADVERTISER_TYPE_NAME", "ADVERTISER_VERTICAL",
    "ADVERTISER_CREDIT_STATUS", "ADVERTISER_CREDIT_STATUS_NAME",
}

# Ad Unit Dimensions (with hierarchy levels)
AD_UNIT_DIMENSIONS = {
    "AD_UNIT_ID", "AD_UNIT_NAME", "AD_UNIT_CODE",
    "AD_UNIT_ID_ALL_LEVEL", "AD_UNIT_NAME_ALL_LEVEL",
    "AD_UNIT_ID_TOP_LEVEL", "AD_UNIT_NAME_TOP_LEVEL",
    "AD_UNIT_STATUS", "AD_UNIT_STATUS_NAME",
    "AD_UNIT_REWARD_AMOUNT", "AD_UNIT_REWARD_TYPE",
    # Levels 1-5 (add more as needed)
    "AD_UNIT_ID_LEVEL_1", "AD_UNIT_NAME_LEVEL_1", "AD_UNIT_CODE_LEVEL_1",
    "AD_UNIT_ID_LEVEL_2", "AD_UNIT_NAME_LEVEL_2", "AD_UNIT_CODE_LEVEL_2",
    "AD_UNIT_ID_LEVEL_3", "AD_UNIT_NAME_LEVEL_3", "AD_UNIT_CODE_LEVEL_3",
    "AD_UNIT_ID_LEVEL_4", "AD_UNIT_NAME_LEVEL_4", "AD_UNIT_CODE_LEVEL_4",
    "AD_UNIT_ID_LEVEL_5", "AD_UNIT_NAME_LEVEL_5", "AD_UNIT_CODE_LEVEL_5",
}

# Line Item Dimensions
LINE_ITEM_DIMENSIONS = {
    "LINE_ITEM_ID", "LINE_ITEM_NAME", "LINE_ITEM_EXTERNAL_ID",
    "LINE_ITEM_AGENCY", "LINE_ITEM_ARCHIVED", "LINE_ITEM_LABELS",
    "LINE_ITEM_LABEL_IDS", "LINE_ITEM_COST_TYPE", "LINE_ITEM_COST_TYPE_NAME",
    "LINE_ITEM_COST_PER_UNIT", "LINE_ITEM_CURRENCY_CODE",
    "LINE_ITEM_START_DATE", "LINE_ITEM_END_DATE", "LINE_ITEM_END_DATE_TIME",
    "LINE_ITEM_DELIVERY_RATE_TYPE", "LINE_ITEM_DELIVERY_RATE_TYPE_NAME",
    "LINE_ITEM_DELIVERY_INDICATOR", "LINE_ITEM_COMPUTED_STATUS",
    "LINE_ITEM_COMPUTED_STATUS_NAME", "LINE_ITEM_OPTIMIZABLE",
    "LINE_ITEM_PRIORITY", "LINE_ITEM_CONTRACTED_QUANTITY",
    "LINE_ITEM_LIFETIME_IMPRESSIONS", "LINE_ITEM_LIFETIME_CLICKS",
    "LINE_ITEM_LIFETIME_VIEWABLE_IMPRESSIONS", "LINE_ITEM_FREQUENCY_CAP",
    "LINE_ITEM_EXTERNAL_DEAL_ID", "LINE_ITEM_MAKEGOOD", "LINE_ITEM_PO_NUMBER",
    "LINE_ITEM_PRIMARY_GOAL_TYPE", "LINE_ITEM_PRIMARY_GOAL_TYPE_NAME",
    "LINE_ITEM_PRIMARY_GOAL_UNIT_TYPE", "LINE_ITEM_PRIMARY_GOAL_UNIT_TYPE_NAME",
    "LINE_ITEM_RESERVATION_STATUS", "LINE_ITEM_RESERVATION_STATUS_NAME",
    "LINE_ITEM_CREATIVE_ROTATION_TYPE", "LINE_ITEM_CREATIVE_ROTATION_TYPE_NAME",
    "LINE_ITEM_ENVIRONMENT_TYPE", "LINE_ITEM_ENVIRONMENT_TYPE_NAME",
}

# Order Dimensions
ORDER_DIMENSIONS = {
    "ORDER_ID", "ORDER_NAME", "ORDER_DELIVERY_STATUS",
    "ORDER_START_DATE_TIME", "ORDER_END_DATE_TIME", "ORDER_EXTERNAL_ID",
    "ORDER_PO_NUMBER", "ORDER_IS_PROGRAMMATIC", "ORDER_AGENCY", "ORDER_AGENCY_ID",
    "ORDER_LABELS", "ORDER_LABEL_IDS", "ORDER_TRAFFICKER", "ORDER_TRAFFICKER_ID",
    "ORDER_SECONDARY_TRAFFICKERS", "ORDER_SALESPERSON", "ORDER_SECONDARY_SALESPEOPLE",
    "ORDER_LIFETIME_IMPRESSIONS", "ORDER_LIFETIME_CLICKS",
}

# Creative Dimensions
CREATIVE_DIMENSIONS = {
    "CREATIVE_ID", "CREATIVE_NAME", "CREATIVE_TYPE", "CREATIVE_TYPE_NAME",
    "CREATIVE_BILLING_TYPE", "CREATIVE_BILLING_TYPE_NAME",
    "CREATIVE_CLICK_THROUGH_URL", "CREATIVE_THIRD_PARTY_VENDOR",
    "CREATIVE_TECHNOLOGY", "CREATIVE_TECHNOLOGY_NAME",
    "CREATIVE_SIZE", "CREATIVE_POLICIES_FILTERING",
}

# Geographic Dimensions
GEOGRAPHIC_DIMENSIONS = {
    "COUNTRY_ID", "COUNTRY_NAME", "COUNTRY_CODE",
    "CONTINENT", "CONTINENT_NAME",
    "CITY_ID", "CITY_NAME",
    "REGION_CODE", "REGION_NAME", "METRO_CODE", "METRO_NAME",
    "POSTAL_CODE",
}

# Device Dimensions
DEVICE_DIMENSIONS = {
    "DEVICE", "DEVICE_NAME", "DEVICE_CATEGORY", "DEVICE_CATEGORY_NAME",
    "DEVICE_MANUFACTURER_ID", "DEVICE_MANUFACTURER_NAME",
    "DEVICE_MODEL_ID", "DEVICE_MODEL_NAME",
    "BROWSER_ID", "BROWSER_NAME", "BROWSER_CATEGORY", "BROWSER_CATEGORY_NAME",
    "BROWSER_VERSION",
    "OS_ID", "OS_NAME", "OS_VERSION", "OPERATING_SYSTEM_NAME", "OPERATING_SYSTEM_VERSION",
    "CARRIER_ID", "CARRIER_NAME",
}

# Programmatic Dimensions
PROGRAMMATIC_DIMENSIONS = {
    "DEMAND_CHANNEL", "DEMAND_CHANNEL_NAME",
    "DEMAND_SOURCE", "DEMAND_SOURCE_NAME",
    "DEMAND_SUBCHANNEL", "DEMAND_SUBCHANNEL_NAME", "CHANNEL",
    "DEAL_ID", "DEAL_NAME", "DEAL_BUYER_ID", "DEAL_BUYER_NAME",
    "BIDDER_ENCRYPTED_ID", "BIDDER_NAME", "BID_RANGE",
    "BID_REJECTION_REASON", "BID_REJECTION_REASON_NAME",
    "BUYER_NETWORK_ID", "BUYER_NETWORK_NAME",
    "ADX_PRODUCT", "ADX_PRODUCT_NAME", "BRANDING_TYPE", "BRANDING_TYPE_NAME",
    "DYNAMIC_ALLOCATION_TYPE", "DYNAMIC_ALLOCATION_TYPE_NAME",
    "IS_ADX_DIRECT", "IS_FIRST_LOOK_DEAL",
    "YIELD_GROUP_ID", "YIELD_GROUP_NAME",
    "YIELD_PARTNER_ID", "YIELD_PARTNER_NAME",
    "PROGRAMMATIC_CHANNEL_NAME", "PROGRAMMATIC_BUYER_NAME",
}

# Custom Targeting Dimensions
CUSTOM_TARGETING_DIMENSIONS = {
    "KEY_VALUES_ID", "KEY_VALUES_NAME", "CUSTOM_SPOT_ID", "CUSTOM_SPOT_NAME",
    "CUSTOM_CRITERIA", "CUSTOM_TARGETING_VALUE_ID", "CUSTOM_TARGETING_VALUE_NAME",
}

# Audience Dimensions
AUDIENCE_DIMENSIONS = {
    "AGE_BRACKET", "AGE_BRACKET_NAME", "GENDER", "GENDER_NAME",
    "INTEREST", "AUDIENCE_SEGMENT_ID_TARGETED", "AUDIENCE_SEGMENT_TARGETED",
}

# Content Dimensions
CONTENT_DIMENSIONS = {
    "CONTENT_ID", "CONTENT_NAME", "CONTENT_CMS_NAME", "CONTENT_CMS_VIDEO_ID",
}

# Other Dimensions
OTHER_DIMENSIONS = {
    "PLACEMENT_ID", "PLACEMENT_NAME",
    "INVENTORY_TYPE", "INVENTORY_TYPE_NAME",
    "INVENTORY_FORMAT", "INVENTORY_FORMAT_NAME",
    "AD_LOCATION", "AD_LOCATION_NAME",
    "AD_TYPE", "AD_TYPE_NAME",
    "AD_EXCHANGE_NAME", "REQUEST_TYPE",
    "SALESPERSON_ID", "SALESPERSON_NAME",
    "APP_VERSION", "VIDEO_POSITION",
}

# Complete set of all valid dimensions
ALL_DIMENSIONS: Set[str] = (
    TIME_DIMENSIONS |
    ADVERTISER_DIMENSIONS |
    AD_UNIT_DIMENSIONS |
    LINE_ITEM_DIMENSIONS |
    ORDER_DIMENSIONS |
    CREATIVE_DIMENSIONS |
    GEOGRAPHIC_DIMENSIONS |
    DEVICE_DIMENSIONS |
    PROGRAMMATIC_DIMENSIONS |
    CUSTOM_TARGETING_DIMENSIONS |
    AUDIENCE_DIMENSIONS |
    CONTENT_DIMENSIONS |
    OTHER_DIMENSIONS
)


# =============================================================================
# METRIC CONSTANTS (150+ metrics from REST API v1)
# =============================================================================

# Core Ad Server Metrics
AD_SERVER_METRICS = {
    "AD_SERVER_IMPRESSIONS", "AD_SERVER_BEGIN_TO_RENDER_IMPRESSIONS",
    "AD_SERVER_TARGETED_IMPRESSIONS", "AD_SERVER_CLICKS",
    "AD_SERVER_TARGETED_CLICKS", "AD_SERVER_UNFILTERED_IMPRESSIONS",
    "AD_SERVER_UNFILTERED_CLICKS", "AD_SERVER_CTR",
}

# Revenue Metrics
REVENUE_METRICS = {
    "AD_SERVER_CPM_AND_CPC_REVENUE", "AD_SERVER_CPM_AND_CPC_REVENUE_GROSS",
    "AD_SERVER_CPD_REVENUE", "AD_SERVER_ALL_REVENUE",
    "AD_SERVER_ALL_REVENUE_GROSS", "AD_SERVER_WITHOUT_CPD_AVERAGE_ECPM",
    "AD_SERVER_WITH_CPD_AVERAGE_ECPM",
    "REVENUE", "ECPM", "CPC",  # Simplified aliases
}

# Total/Aggregated Metrics
TOTAL_METRICS = {
    "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS", "TOTAL_LINE_ITEM_LEVEL_TARGETED_IMPRESSIONS",
    "TOTAL_LINE_ITEM_LEVEL_CLICKS", "TOTAL_LINE_ITEM_LEVEL_TARGETED_CLICKS",
    "TOTAL_LINE_ITEM_LEVEL_CTR", "TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE",
    "TOTAL_LINE_ITEM_LEVEL_ALL_REVENUE",
    "TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM",
    "TOTAL_LINE_ITEM_LEVEL_WITH_CPD_AVERAGE_ECPM",
    "TOTAL_CODE_SERVED_COUNT", "TOTAL_AD_REQUESTS",
    "TOTAL_RESPONSES_SERVED", "TOTAL_UNMATCHED_AD_REQUESTS",
    "TOTAL_FILL_RATE", "TOTAL_INVENTORY_LEVEL_UNFILLED_IMPRESSIONS",
    "TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR", "TOTAL_MATCH_RATE",
    # Simplified aliases
    "IMPRESSIONS", "CLICKS", "CTR",
}

# Inventory Metrics
INVENTORY_METRICS = {
    "AD_REQUESTS", "MATCHED_REQUESTS", "FILL_RATE",
    "UNFILLED_IMPRESSIONS", "INVENTORY_LEVEL_IMPRESSIONS",
}

# AdSense Metrics
ADSENSE_METRICS = {
    "ADSENSE_LINE_ITEM_LEVEL_IMPRESSIONS", "ADSENSE_LINE_ITEM_LEVEL_CLICKS",
    "ADSENSE_LINE_ITEM_LEVEL_CTR", "ADSENSE_LINE_ITEM_LEVEL_REVENUE",
    "ADSENSE_LINE_ITEM_LEVEL_AVERAGE_ECPM", "ADSENSE_RESPONSES_SERVED",
}

# Ad Exchange Metrics
AD_EXCHANGE_METRICS = {
    "AD_EXCHANGE_LINE_ITEM_LEVEL_IMPRESSIONS",
    "AD_EXCHANGE_LINE_ITEM_LEVEL_CLICKS",
    "AD_EXCHANGE_LINE_ITEM_LEVEL_CTR",
    "AD_EXCHANGE_LINE_ITEM_LEVEL_REVENUE",
    "AD_EXCHANGE_LINE_ITEM_LEVEL_AVERAGE_ECPM",
    "AD_EXCHANGE_TOTAL_REQUESTS", "AD_EXCHANGE_MATCH_RATE",
    "AD_EXCHANGE_COST_PER_CLICK",
    "AD_EXCHANGE_TOTAL_REQUEST_CTR", "AD_EXCHANGE_MATCHED_REQUEST_CTR",
    "AD_EXCHANGE_TOTAL_REQUEST_ECPM", "AD_EXCHANGE_MATCHED_REQUEST_ECPM",
    "AD_EXCHANGE_LIFT_EARNINGS", "AD_EXCHANGE_RESPONSES_SERVED",
}

# Active View Metrics
ACTIVE_VIEW_METRICS = {
    "TOTAL_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS",
    "TOTAL_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS",
    "TOTAL_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS_RATE",
    "TOTAL_ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS",
    "TOTAL_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS_RATE",
    "TOTAL_ACTIVE_VIEW_AVERAGE_VIEWABLE_TIME",
    "TOTAL_ACTIVE_VIEW_REVENUE",
    "AD_SERVER_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS",
    "AD_SERVER_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS",
    "AD_SERVER_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS_RATE",
}

# Video Metrics
VIDEO_METRICS = {
    "VIDEO_VIEWERSHIP_START", "VIDEO_VIEWERSHIP_FIRST_QUARTILE",
    "VIDEO_VIEWERSHIP_MIDPOINT", "VIDEO_VIEWERSHIP_THIRD_QUARTILE",
    "VIDEO_VIEWERSHIP_COMPLETE", "VIDEO_VIEWERSHIP_AVERAGE_VIEW_RATE",
    "VIDEO_VIEWERSHIP_AVERAGE_VIEW_TIME", "VIDEO_VIEWERSHIP_COMPLETION_RATE",
    "VIDEO_VIEWERSHIP_TOTAL_ERROR_COUNT", "VIDEO_VIEWERSHIP_VIDEO_LENGTH",
    "VIDEO_VIEWERSHIP_SKIP_BUTTON_SHOWN", "VIDEO_VIEWERSHIP_ENGAGED_VIEW",
    "VIDEO_INTERACTION_PAUSE", "VIDEO_INTERACTION_RESUME",
    "VIDEO_INTERACTION_MUTE", "VIDEO_INTERACTION_UNMUTE",
    "VIDEO_INTERACTION_FULL_SCREEN", "VIDEO_INTERACTION_VIDEO_SKIPS",
}

# Reach Metrics (REACH report type only)
REACH_METRICS = {
    "UNIQUE_REACH_FREQUENCY", "UNIQUE_REACH_IMPRESSIONS", "UNIQUE_REACH",
}

# Programmatic Metrics
PROGRAMMATIC_METRICS = {
    "DEALS_BID_REQUESTS", "DEALS_BIDS", "DEALS_BID_RATE",
    "DEALS_WINNING_BIDS", "DEALS_WIN_RATE",
    "PROGRAMMATIC_RESPONSES_SERVED", "PROGRAMMATIC_MATCH_RATE",
    "TOTAL_PROGRAMMATIC_ELIGIBLE_AD_REQUESTS",
    "PROGRAMMATIC_AVAILABLE_IMPRESSIONS", "PROGRAMMATIC_REVENUE",
}

# Yield/Bidding Metrics
YIELD_METRICS = {
    "BID_COUNT", "BID_AVERAGE_CPM",
    "YIELD_GROUP_CALLOUTS", "YIELD_GROUP_SUCCESSFUL_RESPONSES",
    "YIELD_GROUP_BIDS", "YIELD_GROUP_BIDS_IN_AUCTION",
    "YIELD_GROUP_AUCTIONS_WON", "YIELD_GROUP_IMPRESSIONS",
    "YIELD_GROUP_ESTIMATED_REVENUE", "YIELD_GROUP_ESTIMATED_CPM",
    "YIELD_GROUP_MEDIATION_FILL_RATE",
}

# Complete set of all valid metrics
ALL_METRICS: Set[str] = (
    AD_SERVER_METRICS |
    REVENUE_METRICS |
    TOTAL_METRICS |
    INVENTORY_METRICS |
    ADSENSE_METRICS |
    AD_EXCHANGE_METRICS |
    ACTIVE_VIEW_METRICS |
    VIDEO_METRICS |
    REACH_METRICS |
    PROGRAMMATIC_METRICS |
    YIELD_METRICS
)


# =============================================================================
# REST API ↔ SOAP API NAME MAPPINGS
# =============================================================================

REST_TO_SOAP_METRICS = {
    # Simplified REST names → Full SOAP names
    "IMPRESSIONS": "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS",
    "CLICKS": "TOTAL_LINE_ITEM_LEVEL_CLICKS",
    "CTR": "TOTAL_LINE_ITEM_LEVEL_CTR",
    "REVENUE": "TOTAL_LINE_ITEM_LEVEL_ALL_REVENUE",
    "ECPM": "TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM",
}

SOAP_TO_REST_METRICS = {v: k for k, v in REST_TO_SOAP_METRICS.items()}


# =============================================================================
# PYDANTIC ENUMS
# =============================================================================

class ReportType(str, Enum):
    """GAM Report types."""
    HISTORICAL = "HISTORICAL"
    REACH = "REACH"
    AD_SPEED = "AD_SPEED"


class DimensionCategory(str, Enum):
    """Dimension categories for organization."""
    TIME = "time"
    ADVERTISER = "advertiser"
    AD_UNIT = "ad_unit"
    LINE_ITEM = "line_item"
    ORDER = "order"
    CREATIVE = "creative"
    GEOGRAPHIC = "geographic"
    DEVICE = "device"
    PROGRAMMATIC = "programmatic"
    CUSTOM_TARGETING = "custom_targeting"
    AUDIENCE = "audience"
    CONTENT = "content"
    OTHER = "other"


class MetricCategory(str, Enum):
    """Metric categories for organization."""
    AD_SERVER = "ad_server"
    REVENUE = "revenue"
    TOTAL = "total"
    INVENTORY = "inventory"
    ADSENSE = "adsense"
    AD_EXCHANGE = "ad_exchange"
    ACTIVE_VIEW = "active_view"
    VIDEO = "video"
    REACH = "reach"
    PROGRAMMATIC = "programmatic"
    YIELD = "yield"


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class DimensionInfo(BaseModel):
    """Information about a single dimension."""
    name: str = Field(..., description="Dimension name (uppercase)")
    category: DimensionCategory = Field(..., description="Dimension category")
    description: Optional[str] = Field(None, description="Human-readable description")

    @field_validator("name")
    @classmethod
    def validate_dimension_name(cls, v: str) -> str:
        v = v.upper()
        if v not in ALL_DIMENSIONS:
            raise ValueError(f"Invalid dimension: {v}")
        return v


class MetricInfo(BaseModel):
    """Information about a single metric."""
    name: str = Field(..., description="Metric name (uppercase)")
    category: MetricCategory = Field(..., description="Metric category")
    description: Optional[str] = Field(None, description="Human-readable description")
    reach_only: bool = Field(False, description="True if only valid for REACH reports")

    @field_validator("name")
    @classmethod
    def validate_metric_name(cls, v: str) -> str:
        v = v.upper()
        if v not in ALL_METRICS:
            raise ValueError(f"Invalid metric: {v}")
        return v


class ReportDimensionsMetrics(BaseModel):
    """Request model for dimensions and metrics in a report."""
    dimensions: List[str] = Field(
        ...,
        min_length=1,
        description="List of dimension names"
    )
    metrics: List[str] = Field(
        ...,
        min_length=1,
        description="List of metric names"
    )
    report_type: ReportType = Field(
        ReportType.HISTORICAL,
        description="Report type (affects valid metrics)"
    )

    @field_validator("dimensions")
    @classmethod
    def validate_dimensions(cls, v: List[str]) -> List[str]:
        validated = []
        for dim in v:
            dim_upper = dim.upper()
            if dim_upper not in ALL_DIMENSIONS:
                raise ValueError(f"Invalid dimension: {dim}")
            validated.append(dim_upper)
        return validated

    @field_validator("metrics")
    @classmethod
    def validate_metrics(cls, v: List[str], info) -> List[str]:
        validated = []
        for metric in v:
            metric_upper = metric.upper()
            if metric_upper not in ALL_METRICS:
                raise ValueError(f"Invalid metric: {metric}")
            validated.append(metric_upper)
        return validated

    def check_reach_compatibility(self) -> None:
        """Validate REACH metric compatibility with report type."""
        reach_used = set(self.metrics) & REACH_METRICS
        if reach_used and self.report_type != ReportType.REACH:
            raise ValueError(
                f"Metrics {reach_used} can only be used with REACH report type"
            )
        if self.report_type == ReportType.REACH and not reach_used:
            # Allow non-reach metrics in REACH reports
            pass


class DimensionsMetricsResponse(BaseModel):
    """Response model for available dimensions and metrics."""
    success: bool = True
    report_type: str = Field(..., description="Report type filter applied")
    dimensions: Optional[List[str]] = Field(None, description="Available dimensions")
    metrics: Optional[List[str]] = Field(None, description="Available metrics")
    dimension_count: Optional[int] = Field(None, description="Number of dimensions")
    metric_count: Optional[int] = Field(None, description="Number of metrics")


class CommonCombination(BaseModel):
    """A common dimension-metric combination."""
    name: str = Field(..., description="Combination name")
    description: str = Field(..., description="What this combination is for")
    dimensions: List[str] = Field(..., description="Recommended dimensions")
    metrics: List[str] = Field(..., description="Recommended metrics")
    report_type: ReportType = Field(
        ReportType.HISTORICAL,
        description="Recommended report type"
    )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_dimensions_by_category(category: DimensionCategory) -> Set[str]:
    """Get dimensions for a specific category."""
    category_map = {
        DimensionCategory.TIME: TIME_DIMENSIONS,
        DimensionCategory.ADVERTISER: ADVERTISER_DIMENSIONS,
        DimensionCategory.AD_UNIT: AD_UNIT_DIMENSIONS,
        DimensionCategory.LINE_ITEM: LINE_ITEM_DIMENSIONS,
        DimensionCategory.ORDER: ORDER_DIMENSIONS,
        DimensionCategory.CREATIVE: CREATIVE_DIMENSIONS,
        DimensionCategory.GEOGRAPHIC: GEOGRAPHIC_DIMENSIONS,
        DimensionCategory.DEVICE: DEVICE_DIMENSIONS,
        DimensionCategory.PROGRAMMATIC: PROGRAMMATIC_DIMENSIONS,
        DimensionCategory.CUSTOM_TARGETING: CUSTOM_TARGETING_DIMENSIONS,
        DimensionCategory.AUDIENCE: AUDIENCE_DIMENSIONS,
        DimensionCategory.CONTENT: CONTENT_DIMENSIONS,
        DimensionCategory.OTHER: OTHER_DIMENSIONS,
    }
    return category_map.get(category, set())


def get_metrics_by_category(category: MetricCategory) -> Set[str]:
    """Get metrics for a specific category."""
    category_map = {
        MetricCategory.AD_SERVER: AD_SERVER_METRICS,
        MetricCategory.REVENUE: REVENUE_METRICS,
        MetricCategory.TOTAL: TOTAL_METRICS,
        MetricCategory.INVENTORY: INVENTORY_METRICS,
        MetricCategory.ADSENSE: ADSENSE_METRICS,
        MetricCategory.AD_EXCHANGE: AD_EXCHANGE_METRICS,
        MetricCategory.ACTIVE_VIEW: ACTIVE_VIEW_METRICS,
        MetricCategory.VIDEO: VIDEO_METRICS,
        MetricCategory.REACH: REACH_METRICS,
        MetricCategory.PROGRAMMATIC: PROGRAMMATIC_METRICS,
        MetricCategory.YIELD: YIELD_METRICS,
    }
    return category_map.get(category, set())


def get_metrics_for_report_type(report_type: ReportType) -> Set[str]:
    """Get valid metrics for a report type."""
    if report_type == ReportType.REACH:
        # REACH reports can use reach metrics plus some standard metrics
        return ALL_METRICS
    else:
        # Non-REACH reports cannot use reach-only metrics
        return ALL_METRICS - REACH_METRICS


def normalize_metric_name(metric: str, to_format: Literal["rest", "soap"] = "rest") -> str:
    """
    Normalize metric name between REST and SOAP formats.

    Args:
        metric: Metric name to normalize
        to_format: Target format ("rest" for simplified, "soap" for verbose)

    Returns:
        Normalized metric name
    """
    metric = metric.upper()

    if to_format == "soap":
        return REST_TO_SOAP_METRICS.get(metric, metric)
    else:  # rest
        return SOAP_TO_REST_METRICS.get(metric, metric)


def get_common_combinations() -> List[CommonCombination]:
    """Get predefined common dimension-metric combinations."""
    return [
        CommonCombination(
            name="delivery_analysis",
            description="Analyze delivery performance by ad unit and time",
            dimensions=["DATE", "AD_UNIT_NAME", "LINE_ITEM_NAME"],
            metrics=["TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS", "TOTAL_LINE_ITEM_LEVEL_CLICKS", "TOTAL_LINE_ITEM_LEVEL_CTR"],
            report_type=ReportType.HISTORICAL,
        ),
        CommonCombination(
            name="inventory_analysis",
            description="Analyze ad unit performance and fill rates",
            dimensions=["DATE", "AD_UNIT_NAME"],
            metrics=["TOTAL_AD_REQUESTS", "TOTAL_CODE_SERVED_COUNT", "TOTAL_FILL_RATE"],
            report_type=ReportType.HISTORICAL,
        ),
        CommonCombination(
            name="revenue_analysis",
            description="Analyze revenue by advertiser and order",
            dimensions=["DATE", "ADVERTISER_NAME", "ORDER_NAME"],
            metrics=["TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS", "TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE"],
            report_type=ReportType.HISTORICAL,
        ),
        CommonCombination(
            name="geographic_analysis",
            description="Analyze performance by country and region",
            dimensions=["DATE", "COUNTRY_NAME", "DEVICE_CATEGORY_NAME"],
            metrics=["TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS", "TOTAL_LINE_ITEM_LEVEL_CLICKS"],
            report_type=ReportType.HISTORICAL,
        ),
        CommonCombination(
            name="reach_analysis",
            description="Analyze unique reach and frequency",
            dimensions=["DATE", "COUNTRY_NAME", "DEVICE_CATEGORY_NAME"],
            metrics=["UNIQUE_REACH", "UNIQUE_REACH_FREQUENCY", "UNIQUE_REACH_IMPRESSIONS"],
            report_type=ReportType.REACH,
        ),
        CommonCombination(
            name="programmatic_analysis",
            description="Analyze programmatic performance by demand channel",
            dimensions=["DATE", "DEMAND_CHANNEL_NAME"],
            metrics=["AD_EXCHANGE_LINE_ITEM_LEVEL_IMPRESSIONS", "AD_EXCHANGE_LINE_ITEM_LEVEL_REVENUE"],
            report_type=ReportType.HISTORICAL,
        ),
    ]


# =============================================================================
# BACKWARDS COMPATIBILITY EXPORTS
# =============================================================================

# Export for use by validators.py
VALID_DIMENSIONS = ALL_DIMENSIONS
VALID_METRICS = ALL_METRICS
REACH_ONLY_METRICS = REACH_METRICS
