"""Curated dimension definitions for GAM Reports."""

from enum import Enum
from pydantic import BaseModel, Field


class DimensionCategory(str, Enum):
    """Categories for dimensions."""

    TIME = "time"
    INVENTORY = "inventory"
    ADVERTISER = "advertiser"
    ORDER = "order"
    LINE_ITEM = "line_item"
    CREATIVE = "creative"
    GEOGRAPHY = "geography"
    DEVICE = "device"
    PROGRAMMATIC = "programmatic"
    REQUEST = "request"
    TARGETING = "targeting"
    PRIVACY = "privacy"


class DataFormat(str, Enum):
    """Data formats returned by GAM API dimensions."""

    STRING = "STRING"
    ENUM = "ENUM"
    IDENTIFIER = "IDENTIFIER"
    DATE = "DATE"
    INTEGER = "INTEGER"
    STRING_LIST = "STRING_LIST"
    IDENTIFIER_LIST = "IDENTIFIER_LIST"
    BOOLEAN = "BOOLEAN"
    MONEY = "MONEY"
    PERCENT = "PERCENT"
    WHOLE_PERCENT = "WHOLE_PERCENT"
    TIMESTAMP = "TIMESTAMP"
    BID_RANGE = "BID_RANGE"


class ReportType(str, Enum):
    """GAM report types that dimensions can be compatible with."""

    HISTORICAL = "HISTORICAL"
    REACH = "REACH"
    PRIVACY_AND_MESSAGING = "PRIVACY_AND_MESSAGING"
    AD_SPEED = "AD_SPEED"


class Dimension(BaseModel):
    """A curated dimension with domain context."""

    name: str = Field(description="GAM API dimension name")
    category: DimensionCategory
    description: str = Field(description="What this dimension represents")
    use_case: str = Field(description="When to use this dimension")
    data_format: DataFormat = Field(
        default=DataFormat.STRING, description="Data type returned by GAM API"
    )
    report_types: list[ReportType] = Field(
        default_factory=lambda: [ReportType.HISTORICAL],
        description="Compatible report types",
    )
    compatible_with: list[str] = Field(
        default_factory=list, description="Metrics that work well with this"
    )


# Curated allowlist - add your dimensions here
ALLOWED_DIMENSIONS: dict[str, Dimension] = {
    # =========================================================================
    # TIME DIMENSIONS
    # =========================================================================
    "DATE": Dimension(
        name="DATE",
        category=DimensionCategory.TIME,
        description="Daily granularity - breaks down data by calendar date",
        use_case="Daily performance trends, day-over-day comparisons, identifying daily patterns",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR", "TOTAL_AD_REQUESTS", "TOTAL_FILL_RATE"],
    ),
    "HOUR": Dimension(
        name="HOUR",
        category=DimensionCategory.TIME,
        description="Hourly granularity (0-23) - RARELY USED",
        use_case="Investigating intraday issues, debugging traffic spikes, analyzing hourly patterns. Use sparingly as it creates many rows.",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_AD_REQUESTS", "TOTAL_FILL_RATE"],
    ),
    # =========================================================================
    # AD UNIT / INVENTORY DIMENSIONS
    # =========================================================================
    "AD_UNIT_NAME": Dimension(
        name="AD_UNIT_NAME",
        category=DimensionCategory.INVENTORY,
        description="Human-readable ad unit name where the ad was requested",
        use_case="Performance by placement, identifying top/bottom performers",
        compatible_with=["TOTAL_AD_REQUESTS", "TOTAL_IMPRESSIONS", "TOTAL_FILL_RATE", "TOTAL_CTR"],
    ),
    "AD_UNIT_ID": Dimension(
        name="AD_UNIT_ID",
        category=DimensionCategory.INVENTORY,
        description="Unique identifier for the ad unit (numeric ID)",
        use_case="Programmatic lookups, joining with other systems, API operations",
        compatible_with=["TOTAL_AD_REQUESTS", "TOTAL_IMPRESSIONS", "TOTAL_FILL_RATE"],
    ),
    "AD_UNIT_CODE": Dimension(
        name="AD_UNIT_CODE",
        category=DimensionCategory.INVENTORY,
        description="Ad unit code used in DFP/GPT tags",
        use_case="Technical integration analysis, matching with ad tag implementations",
        compatible_with=["TOTAL_AD_REQUESTS", "TOTAL_IMPRESSIONS", "TOTAL_FILL_RATE"],
    ),
    "AD_UNIT_STATUS": Dimension(
        name="AD_UNIT_STATUS",
        category=DimensionCategory.INVENTORY,
        description="Active/Inactive/Archived status of the ad unit",
        use_case="Filtering by ad unit lifecycle state, inventory audits",
        compatible_with=["TOTAL_AD_REQUESTS", "TOTAL_IMPRESSIONS"],
    ),
    "AD_UNIT_NAME_ALL_LEVEL": Dimension(
        name="AD_UNIT_NAME_ALL_LEVEL",
        category=DimensionCategory.INVENTORY,
        description="Full hierarchy path of ad unit names (root to leaf, excluding root)",
        use_case="Viewing complete ad unit hierarchy, understanding nested structure",
        compatible_with=["TOTAL_AD_REQUESTS", "TOTAL_IMPRESSIONS", "TOTAL_FILL_RATE"],
    ),
    "AD_UNIT_ID_ALL_LEVEL": Dimension(
        name="AD_UNIT_ID_ALL_LEVEL",
        category=DimensionCategory.INVENTORY,
        description="Full hierarchy path of ad unit IDs (root to leaf, excluding root)",
        use_case="Programmatic hierarchy lookups, joining hierarchical data",
        compatible_with=["TOTAL_AD_REQUESTS", "TOTAL_IMPRESSIONS", "TOTAL_FILL_RATE"],
    ),
    "AD_UNIT_NAME_TOP_LEVEL": Dimension(
        name="AD_UNIT_NAME_TOP_LEVEL",
        category=DimensionCategory.INVENTORY,
        description="Top-level ad unit name (first level below root)",
        use_case="High-level inventory grouping, site section analysis at top level",
        compatible_with=["TOTAL_AD_REQUESTS", "TOTAL_IMPRESSIONS", "TOTAL_FILL_RATE", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "AD_UNIT_REWARD_AMOUNT": Dimension(
        name="AD_UNIT_REWARD_AMOUNT",
        category=DimensionCategory.INVENTORY,
        description="Reward amount for rewarded ad units - USE ONLY WITH REWARDED AD FORMATS",
        use_case="Analyzing rewarded video/interstitial performance by reward value",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "VIDEO_COMPLETIONS"],
    ),
    "AD_UNIT_REWARD_TYPE": Dimension(
        name="AD_UNIT_REWARD_TYPE",
        category=DimensionCategory.INVENTORY,
        description="Type of reward (coins, gems, lives, etc.) - USE ONLY WITH REWARDED AD FORMATS",
        use_case="Segmenting rewarded ad performance by reward type",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "VIDEO_COMPLETIONS"],
    ),
    "SITE_NAME": Dimension(
        name="SITE_NAME",
        category=DimensionCategory.INVENTORY,
        description="Site/domain name where the ad was served",
        use_case="Performance analysis by site/property, multi-site publisher reporting",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CPM_AND_CPC_REVENUE", "TOTAL_FILL_RATE"],
    ),
    "URL_NAME": Dimension(
        name="URL_NAME",
        category=DimensionCategory.INVENTORY,
        description="Page URL where the ad was served",
        use_case="Page-level performance analysis, identifying high/low performing pages",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "MOBILE_APP_NAME": Dimension(
        name="MOBILE_APP_NAME",
        category=DimensionCategory.INVENTORY,
        description="Mobile app name where the ad was served",
        use_case="App-level performance analysis for mobile inventory",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CPM_AND_CPC_REVENUE", "TOTAL_FILL_RATE"],
    ),
    "MOBILE_APP_OWNERSHIP_STATUS_NAME": Dimension(
        name="MOBILE_APP_OWNERSHIP_STATUS_NAME",
        category=DimensionCategory.INVENTORY,
        description="App ownership status (Owned, Claimed, Third-party)",
        use_case="Identifying ownership of mobile app inventory",
        data_format=DataFormat.STRING,
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_AD_REQUESTS", "TOTAL_FILL_RATE"],
    ),
    "CHANNEL": Dimension(
        name="CHANNEL",
        category=DimensionCategory.INVENTORY,
        description="Channel/property grouping for inventory",
        use_case="Performance analysis by channel/property grouping",
        data_format=DataFormat.STRING,
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_AD_REQUESTS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "CONTENT_MAPPING_PRESENCE_NAME": Dimension(
        name="CONTENT_MAPPING_PRESENCE_NAME",
        category=DimensionCategory.INVENTORY,
        description="Whether content mapping is present for the request",
        use_case="Analyzing content-mapped vs non-content-mapped inventory performance",
        data_format=DataFormat.STRING,
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_AD_REQUESTS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "URL_ID": Dimension(
        name="URL_ID",
        category=DimensionCategory.INVENTORY,
        description="Unique identifier for the page URL",
        use_case="Programmatic URL lookups, joining with external page data",
        data_format=DataFormat.IDENTIFIER,
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    # =========================================================================
    # ADVERTISER DIMENSIONS
    # =========================================================================
    "CLASSIFIED_ADVERTISER_NAME": Dimension(
        name="CLASSIFIED_ADVERTISER_NAME",
        category=DimensionCategory.ADVERTISER,
        description="Google-classified advertiser name (auto-detected from creative)",
        use_case="Brand analysis when advertiser not explicitly set, programmatic advertiser identification",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "CLASSIFIED_BRAND_NAME": Dimension(
        name="CLASSIFIED_BRAND_NAME",
        category=DimensionCategory.ADVERTISER,
        description="Google-classified brand name (auto-detected from creative content)",
        use_case="Brand-level analysis for programmatic demand, identifying specific brands in campaigns",
        data_format=DataFormat.STRING,
        report_types=[ReportType.HISTORICAL, ReportType.AD_SPEED],
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "ADVERTISER_VERTICAL": Dimension(
        name="ADVERTISER_VERTICAL",
        category=DimensionCategory.ADVERTISER,
        description="Industry category (Arts & Entertainment, Travel & Tourism, Finance, etc.)",
        use_case="Revenue breakdown by industry, vertical performance analysis",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "ADVERTISER_DOMAIN_NAME": Dimension(
        name="ADVERTISER_DOMAIN_NAME",
        category=DimensionCategory.ADVERTISER,
        description="Web domain associated with the advertiser",
        use_case="Brand safety analysis, identifying advertiser websites",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS"],
    ),
    "ADVERTISER_TYPE_NAME": Dimension(
        name="ADVERTISER_TYPE_NAME",
        category=DimensionCategory.ADVERTISER,
        description="Advertiser type (House Advertiser, Ad Network, etc.)",
        use_case="Segmenting performance by advertiser relationship type",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    # =========================================================================
    # ORDER DIMENSIONS
    # =========================================================================
    "ORDER_NAME": Dimension(
        name="ORDER_NAME",
        category=DimensionCategory.ORDER,
        description="Order/campaign name (parent of line items)",
        use_case="Campaign-level performance analysis, grouping line items by deal",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "ORDER_ID": Dimension(
        name="ORDER_ID",
        category=DimensionCategory.ORDER,
        description="Unique identifier for the order",
        use_case="Programmatic lookups, joining with trafficking data",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "ORDER_START_DATE_TIME": Dimension(
        name="ORDER_START_DATE_TIME",
        category=DimensionCategory.ORDER,
        description="Start date and time of the order",
        use_case="Filtering by campaign launch date, analyzing seasonal campaigns",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS"],
    ),
    # =========================================================================
    # LINE ITEM DIMENSIONS
    # =========================================================================
    "LINE_ITEM_NAME": Dimension(
        name="LINE_ITEM_NAME",
        category=DimensionCategory.LINE_ITEM,
        description="Name of the line item (campaign/deal)",
        use_case="Campaign performance analysis, delivery tracking by deal",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "LINE_ITEM_ID": Dimension(
        name="LINE_ITEM_ID",
        category=DimensionCategory.LINE_ITEM,
        description="Unique identifier for the line item",
        use_case="Programmatic lookups, joining with trafficking data, API operations",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "LINE_ITEM_COMPUTED_STATUS_NAME": Dimension(
        name="LINE_ITEM_COMPUTED_STATUS_NAME",
        category=DimensionCategory.LINE_ITEM,
        description="Current operational status (Delivering, Paused, Completed, etc.)",
        use_case="Filtering by delivery state, troubleshooting underdelivery",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS"],
    ),
    "LINE_ITEM_TYPE_NAME": Dimension(
        name="LINE_ITEM_TYPE_NAME",
        category=DimensionCategory.LINE_ITEM,
        description="Line item type (Sponsorship, Standard, Network, Bulk, Price Priority, House, etc.)",
        use_case="Segmenting by deal type, analyzing direct vs programmatic performance",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "LINE_ITEM_START_DATE": Dimension(
        name="LINE_ITEM_START_DATE",
        category=DimensionCategory.LINE_ITEM,
        description="Start date of the line item",
        use_case="Filtering by campaign launch date, analyzing new campaigns",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS"],
    ),
    "LINE_ITEM_ARCHIVED": Dimension(
        name="LINE_ITEM_ARCHIVED",
        category=DimensionCategory.LINE_ITEM,
        description="Whether the line item is archived (true/false)",
        use_case="Filtering archived vs active line items, historical analysis",
        data_format=DataFormat.BOOLEAN,
        report_types=[ReportType.HISTORICAL, ReportType.REACH],
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "OPTIMIZATION_TYPE_NAME": Dimension(
        name="OPTIMIZATION_TYPE_NAME",
        category=DimensionCategory.LINE_ITEM,
        description="Optimization type applied to line item (Maximize clicks, Maximize CTR, etc.)",
        use_case="Analyzing performance by optimization strategy",
        data_format=DataFormat.STRING,
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR"],
    ),
    # =========================================================================
    # CREATIVE DIMENSIONS
    # =========================================================================
    "CREATIVE_TYPE_NAME": Dimension(
        name="CREATIVE_TYPE_NAME",
        category=DimensionCategory.CREATIVE,
        description="Creative format type (Image, HTML5, Video, Third-party, etc.)",
        use_case="Analyzing performance by creative format, identifying best-performing ad types",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "CREATIVE_SIZE_NAME": Dimension(
        name="CREATIVE_SIZE_NAME",
        category=DimensionCategory.CREATIVE,
        description="Creative dimensions (300x250, 728x90, 320x50, etc.)",
        use_case="Size performance analysis, identifying best-performing ad sizes",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR", "TOTAL_FILL_RATE"],
    ),
    "CREATIVE_NAME": Dimension(
        name="CREATIVE_NAME",
        category=DimensionCategory.CREATIVE,
        description="Name of the creative asset",
        use_case="Creative-level performance analysis, A/B testing different creative assets",
        data_format=DataFormat.STRING,
        report_types=[ReportType.HISTORICAL, ReportType.AD_SPEED],
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR"],
    ),
    "CREATIVE_TECHNOLOGY_NAME": Dimension(
        name="CREATIVE_TECHNOLOGY_NAME",
        category=DimensionCategory.CREATIVE,
        description="Technology used for rendering creative (HTML5, Flash, Image, etc.)",
        use_case="Analyzing performance by creative technology/rendering method",
        data_format=DataFormat.STRING,
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR"],
    ),
    "RENDERED_CREATIVE_SIZE": Dimension(
        name="RENDERED_CREATIVE_SIZE",
        category=DimensionCategory.CREATIVE,
        description="Actual rendered size of the creative (may differ from requested size)",
        use_case="Identifying size rendering differences, debugging creative display issues",
        data_format=DataFormat.STRING,
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR"],
    ),
    # =========================================================================
    # PROGRAMMATIC DIMENSIONS
    # =========================================================================
    "YIELD_PARTNER_NAME": Dimension(
        name="YIELD_PARTNER_NAME",
        category=DimensionCategory.PROGRAMMATIC,
        description="Yield partner/header bidding partner name",
        use_case="Programmatic partner performance analysis, header bidding optimization",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CPM_AND_CPC_REVENUE", "TOTAL_FILL_RATE"],
    ),
    "DEMAND_CHANNEL_NAME": Dimension(
        name="DEMAND_CHANNEL_NAME",
        category=DimensionCategory.PROGRAMMATIC,
        description="Demand source type (Ad Exchange, Open Bidding, Direct, House, etc.)",
        use_case="Analyzing revenue and fill by demand channel, programmatic vs direct comparison",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CPM_AND_CPC_REVENUE", "TOTAL_FILL_RATE", "TOTAL_AD_REQUESTS"],
    ),
    "YIELD_GROUP_NAME": Dimension(
        name="YIELD_GROUP_NAME",
        category=DimensionCategory.PROGRAMMATIC,
        description="Yield group name for header bidding/Open Bidding configurations",
        use_case="Analyzing performance by yield group, optimizing header bidding setup",
        data_format=DataFormat.STRING,
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CPM_AND_CPC_REVENUE", "TOTAL_FILL_RATE"],
    ),
    # =========================================================================
    # REQUEST / AD FORMAT DIMENSIONS
    # =========================================================================
    "REQUEST_TYPE_NAME": Dimension(
        name="REQUEST_TYPE_NAME",
        category=DimensionCategory.REQUEST,
        description="Type of ad request (ADS, VIDEO, NATIVE, etc.)",
        use_case="Analyzing request mix, understanding demand by request type",
        data_format=DataFormat.STRING,
        compatible_with=["TOTAL_AD_REQUESTS", "TOTAL_IMPRESSIONS", "TOTAL_FILL_RATE"],
    ),
    "INVENTORY_TYPE_NAME": Dimension(
        name="INVENTORY_TYPE_NAME",
        category=DimensionCategory.REQUEST,
        description="Inventory type (WEB, MOBILE_APP, GAMES, etc.)",
        use_case="Segmenting performance by platform type, web vs app analysis",
        compatible_with=["TOTAL_AD_REQUESTS", "TOTAL_IMPRESSIONS", "TOTAL_FILL_RATE", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "AD_REQUEST_SIZE": Dimension(
        name="AD_REQUEST_SIZE",
        category=DimensionCategory.REQUEST,
        description="Requested ad size code (e.g., 300x250)",
        use_case="Size-level request analysis, identifying most requested sizes",
        compatible_with=["TOTAL_AD_REQUESTS", "TOTAL_IMPRESSIONS", "TOTAL_FILL_RATE"],
    ),
    "AD_REQUEST_SIZE_NAME": Dimension(
        name="AD_REQUEST_SIZE_NAME",
        category=DimensionCategory.REQUEST,
        description="Requested ad size as human-readable string",
        use_case="Size-level request analysis with readable format",
        compatible_with=["TOTAL_AD_REQUESTS", "TOTAL_IMPRESSIONS", "TOTAL_FILL_RATE"],
    ),
    "AD_REQUEST_AD_UNIT_SIZES": Dimension(
        name="AD_REQUEST_AD_UNIT_SIZES",
        category=DimensionCategory.REQUEST,
        description="All ad sizes included in the request (multi-size requests)",
        use_case="Analyzing multi-size request patterns, size flexibility analysis",
        compatible_with=["TOTAL_AD_REQUESTS", "TOTAL_IMPRESSIONS", "TOTAL_FILL_RATE"],
    ),
    "AD_REQUEST_AD_UNIT_SIZES_NAME": Dimension(
        name="AD_REQUEST_AD_UNIT_SIZES_NAME",
        category=DimensionCategory.REQUEST,
        description="All ad sizes in request as human-readable string",
        use_case="Multi-size request analysis with readable format",
        compatible_with=["TOTAL_AD_REQUESTS", "TOTAL_IMPRESSIONS", "TOTAL_FILL_RATE"],
    ),
    "AD_LOCATION_NAME": Dimension(
        name="AD_LOCATION_NAME",
        category=DimensionCategory.REQUEST,
        description="Ad position on page (Above the fold, Below the fold, etc.)",
        use_case="Viewability and position analysis, above-fold vs below-fold performance",
        data_format=DataFormat.STRING,
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "SERVING_RESTRICTION_NAME": Dimension(
        name="SERVING_RESTRICTION_NAME",
        category=DimensionCategory.REQUEST,
        description="Serving restriction applied to the request (e.g., non-personalized ads)",
        use_case="Analyzing impact of serving restrictions on fill rate and revenue",
        data_format=DataFormat.STRING,
        compatible_with=["TOTAL_AD_REQUESTS", "TOTAL_IMPRESSIONS", "TOTAL_FILL_RATE", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    # =========================================================================
    # TARGETING DIMENSIONS
    # =========================================================================
    "PLACEMENT_NAME": Dimension(
        name="PLACEMENT_NAME",
        category=DimensionCategory.TARGETING,
        description="Placement group name (logical grouping of ad units)",
        use_case="Performance by placement group, site section analysis",
        compatible_with=["TOTAL_AD_REQUESTS", "TOTAL_IMPRESSIONS", "TOTAL_FILL_RATE", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "PLACEMENT_STATUS": Dimension(
        name="PLACEMENT_STATUS",
        category=DimensionCategory.TARGETING,
        description="Placement status (Active, Inactive, Archived)",
        use_case="Filtering by placement lifecycle state, auditing active placements",
        compatible_with=["TOTAL_AD_REQUESTS", "TOTAL_IMPRESSIONS"],
    ),
    "CUSTOM_TARGETING_VALUE_ID": Dimension(
        name="CUSTOM_TARGETING_VALUE_ID",
        category=DimensionCategory.TARGETING,
        description="Key-Value targeting ID - YOUR CUSTOM VALUES sent to GAM via GPT tags",
        use_case="Analyze performance by your custom key-values (e.g., article_type=sports, user_tier=premium). This is the ONLY way to pass custom data to GAM for reporting.",
        compatible_with=["TOTAL_AD_REQUESTS", "TOTAL_IMPRESSIONS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "CUSTOM_CRITERIA": Dimension(
        name="CUSTOM_CRITERIA",
        category=DimensionCategory.TARGETING,
        description="Key-Value targeting criteria - YOUR CUSTOM KEY=VALUE pairs sent to GAM",
        use_case="Full key=value breakdown of your custom targeting. Use this to analyze custom segments like content_category, logged_in_status, etc. This is the ONLY mechanism for custom reporting dimensions in GAM.",
        compatible_with=["TOTAL_AD_REQUESTS", "TOTAL_IMPRESSIONS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "KEY_VALUES_NAME": Dimension(
        name="KEY_VALUES_NAME",
        category=DimensionCategory.TARGETING,
        description="Key-value pair names as human-readable strings",
        use_case="Analyzing key-value targeting performance with readable labels",
        data_format=DataFormat.STRING,
        compatible_with=["TOTAL_AD_REQUESTS", "TOTAL_IMPRESSIONS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "TARGETING_NAME": Dimension(
        name="TARGETING_NAME",
        category=DimensionCategory.TARGETING,
        description="Name of targeting criteria applied to the ad request",
        use_case="Understanding which specific targeting criteria are driving performance",
        data_format=DataFormat.STRING,
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "TARGETING_TYPE_NAME": Dimension(
        name="TARGETING_TYPE_NAME",
        category=DimensionCategory.TARGETING,
        description="Type of targeting applied (Geographic, Device, Custom, etc.)",
        use_case="Understanding which targeting criteria drive performance",
        data_format=DataFormat.STRING,
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS"],
    ),
    "UNIFIED_PRICING_RULE_NAME": Dimension(
        name="UNIFIED_PRICING_RULE_NAME",
        category=DimensionCategory.TARGETING,
        description="Unified pricing rule name applied to the request",
        use_case="Analyzing impact of pricing rules on fill rate and revenue",
        compatible_with=["TOTAL_AD_REQUESTS", "TOTAL_IMPRESSIONS", "TOTAL_CPM_AND_CPC_REVENUE", "TOTAL_FILL_RATE"],
    ),
    # =========================================================================
    # GEOGRAPHY DIMENSIONS
    # =========================================================================
    "COUNTRY_NAME": Dimension(
        name="COUNTRY_NAME",
        category=DimensionCategory.GEOGRAPHY,
        description="Country name (localized)",
        use_case="Geographic performance analysis, regional revenue breakdown",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "COUNTRY_CODE": Dimension(
        name="COUNTRY_CODE",
        category=DimensionCategory.GEOGRAPHY,
        description="ISO country code (US, CA, MX, etc.)",
        use_case="Programmatic lookups, joining with external geographic data",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "REGION_NAME": Dimension(
        name="REGION_NAME",
        category=DimensionCategory.GEOGRAPHY,
        description="State/Province/Region name (localized)",
        use_case="Sub-country geographic analysis, state-level performance",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "REGION_CODE": Dimension(
        name="REGION_CODE",
        category=DimensionCategory.GEOGRAPHY,
        description="Region/state code (CA, NY, TX, etc.)",
        use_case="Programmatic lookups, joining with external regional data",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    # =========================================================================
    # DEVICE & BROWSER DIMENSIONS
    # =========================================================================
    "DEVICE_CATEGORY_NAME": Dimension(
        name="DEVICE_CATEGORY_NAME",
        category=DimensionCategory.DEVICE,
        description="Device type (Desktop, Mobile, Tablet, Connected TV)",
        use_case="Device performance analysis, mobile vs desktop comparison",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR", "TOTAL_FILL_RATE"],
    ),
    "DEVICE_NAME": Dimension(
        name="DEVICE_NAME",
        category=DimensionCategory.DEVICE,
        description="Specific device model (iPhone 14, Samsung Galaxy S23, etc.)",
        use_case="Device-specific performance analysis, identifying problematic devices",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR"],
    ),
    "BROWSER_NAME": Dimension(
        name="BROWSER_NAME",
        category=DimensionCategory.DEVICE,
        description="Browser name (Chrome, Safari, Firefox, Edge, etc.)",
        use_case="Browser compatibility analysis, ad rendering issues by browser",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR", "TOTAL_FILL_RATE"],
    ),
    "OPERATING_SYSTEM_NAME": Dimension(
        name="OPERATING_SYSTEM_NAME",
        category=DimensionCategory.DEVICE,
        description="Operating system name (Windows, iOS, Android, macOS, etc.)",
        use_case="OS-level performance analysis, platform targeting insights",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR"],
    ),
    "MOBILE_DEVICE_NAME": Dimension(
        name="MOBILE_DEVICE_NAME",
        category=DimensionCategory.DEVICE,
        description="Mobile device model - USE ONLY FOR MOBILE TRAFFIC ANALYSIS",
        use_case="Mobile-specific device analysis, identifying top mobile devices",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR"],
    ),
    "DEVICE_MANUFACTURER_NAME": Dimension(
        name="DEVICE_MANUFACTURER_NAME",
        category=DimensionCategory.DEVICE,
        description="Device manufacturer (Apple, Samsung, Google, etc.)",
        use_case="Analyzing performance by device brand/manufacturer",
        data_format=DataFormat.STRING,
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR"],
    ),
    "DEVICE_MODEL_NAME": Dimension(
        name="DEVICE_MODEL_NAME",
        category=DimensionCategory.DEVICE,
        description="Specific device model name",
        use_case="Detailed device-level performance analysis",
        data_format=DataFormat.STRING,
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR"],
    ),
    "OPERATING_SYSTEM_CATEGORY_NAME": Dimension(
        name="OPERATING_SYSTEM_CATEGORY_NAME",
        category=DimensionCategory.DEVICE,
        description="OS category (Desktop OS, Mobile OS, etc.)",
        use_case="High-level OS type analysis",
        data_format=DataFormat.STRING,
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR"],
    ),
    "OPERATING_SYSTEM_VERSION_NAME": Dimension(
        name="OPERATING_SYSTEM_VERSION_NAME",
        category=DimensionCategory.DEVICE,
        description="Specific OS version (iOS 17.1, Android 14, Windows 11, etc.)",
        use_case="OS version-level performance analysis, identifying version-specific issues",
        data_format=DataFormat.STRING,
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR"],
    ),
    # =========================================================================
    # PRIVACY / CONSENT DIMENSIONS
    # =========================================================================
    "APP_TRACKING_TRANSPARENCY_CONSENT_STATUS": Dimension(
        name="APP_TRACKING_TRANSPARENCY_CONSENT_STATUS",
        category=DimensionCategory.PRIVACY,
        description="iOS App Tracking Transparency (ATT) consent status - iOS 14.5+ privacy setting",
        use_case="Privacy compliance analysis, understanding ATT opt-in/opt-out impact on iOS traffic",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CPM_AND_CPC_REVENUE", "TOTAL_FILL_RATE"],
    ),
    "DELIVERED_SECURE_SIGNAL_NAME": Dimension(
        name="DELIVERED_SECURE_SIGNAL_NAME",
        category=DimensionCategory.PRIVACY,
        description="Name of secure signal delivered with ad request (e.g., encrypted signals)",
        use_case="Analyzing which secure signals are being passed to buyers",
        data_format=DataFormat.STRING,
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_AD_REQUESTS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "ESP_DELIVERY_NAME": Dimension(
        name="ESP_DELIVERY_NAME",
        category=DimensionCategory.PRIVACY,
        description="Encrypted Signals for Publishers (ESP) delivery status",
        use_case="Analyzing ESP signal delivery effectiveness",
        data_format=DataFormat.STRING,
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_AD_REQUESTS", "TOTAL_CPM_AND_CPC_REVENUE"],
    ),
    "ESP_PRESENCE_NAME": Dimension(
        name="ESP_PRESENCE_NAME",
        category=DimensionCategory.PRIVACY,
        description="Whether ESP signals are present in the request",
        use_case="Understanding ESP signal coverage across inventory",
        data_format=DataFormat.STRING,
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_AD_REQUESTS", "TOTAL_FILL_RATE"],
    ),
    "PPID_STATUS_NAME": Dimension(
        name="PPID_STATUS_NAME",
        category=DimensionCategory.PRIVACY,
        description="Publisher Provided ID (PPID) status - whether PPID is present",
        use_case="Analyzing first-party ID coverage, understanding addressable inventory",
        data_format=DataFormat.STRING,
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_AD_REQUESTS", "TOTAL_CPM_AND_CPC_REVENUE", "TOTAL_FILL_RATE"],
    ),
}
