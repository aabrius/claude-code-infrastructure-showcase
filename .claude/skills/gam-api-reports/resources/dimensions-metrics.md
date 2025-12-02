# GAM Report Dimensions and Metrics

Complete reference for all available Google Ad Manager report dimensions and metrics (API v202511).

## API Naming Conventions

GAM has two APIs with different naming conventions:

| API | Status | Naming Style | Example Metric |
|-----|--------|--------------|----------------|
| **REST API v1** | Beta (newer) | Simplified | `IMPRESSIONS` |
| **SOAP API** | Stable (legacy) | Verbose | `TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS` |

**This document uses REST API names.** The Unified Client automatically handles conversion between APIs.

### Common Name Mappings

| REST API (simplified) | SOAP API (verbose) |
|-----------------------|---------------------|
| `IMPRESSIONS` | `TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS` |
| `CLICKS` | `TOTAL_LINE_ITEM_LEVEL_CLICKS` |
| `CTR` | `TOTAL_LINE_ITEM_LEVEL_CTR` |
| `REVENUE` | `TOTAL_LINE_ITEM_LEVEL_ALL_REVENUE` |
| `ECPM` | `TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM` |

**Dimensions** are generally the same across both APIs.

---

## Table of Contents

- [Dimensions](#dimensions)
  - [Time Dimensions](#time-dimensions)
  - [Advertiser Dimensions](#advertiser-dimensions)
  - [Ad Unit Dimensions](#ad-unit-dimensions)
  - [Line Item Dimensions](#line-item-dimensions)
  - [Order Dimensions](#order-dimensions)
  - [Creative Dimensions](#creative-dimensions)
  - [Geographic Dimensions](#geographic-dimensions)
  - [Device Dimensions](#device-dimensions)
  - [Programmatic Dimensions](#programmatic-dimensions)
  - [Custom Targeting Dimensions](#custom-targeting-dimensions)
- [Metrics](#metrics)
  - [Core Ad Server Metrics](#core-ad-server-metrics)
  - [Revenue Metrics](#revenue-metrics)
  - [Inventory Metrics](#inventory-metrics)
  - [Active View Metrics](#active-view-metrics)
  - [Video Metrics](#video-metrics)
  - [Programmatic Metrics](#programmatic-metrics)
  - [Reach Metrics](#reach-metrics)
- [Dimension-Metric Compatibility](#dimension-metric-compatibility)
- [Common Combinations by Report Type](#common-combinations-by-report-type)

---

## Dimensions

### Time Dimensions

| Dimension | Description |
|-----------|-------------|
| `DATE` | Report date (YYYY-MM-DD) |
| `HOUR` | Hour of day (0-23) |
| `DAY_OF_WEEK` | Day of the week |
| `WEEK` | Week number |
| `MONTH` | Month (YYYY-MM) |
| `YEAR` | Year (YYYY) |

### Advertiser Dimensions

| Dimension | Description |
|-----------|-------------|
| `ADVERTISER_ID` | Advertiser unique ID |
| `ADVERTISER_NAME` | Advertiser name |
| `ADVERTISER_DOMAIN_NAME` | Advertiser domain |
| `ADVERTISER_EXTERNAL_ID` | External advertiser ID |
| `ADVERTISER_LABELS` | Advertiser labels |
| `ADVERTISER_LABEL_IDS` | Advertiser label IDs |
| `ADVERTISER_PRIMARY_CONTACT` | Primary contact |
| `ADVERTISER_STATUS` | Status code |
| `ADVERTISER_STATUS_NAME` | Status name |
| `ADVERTISER_TYPE` | Type code |
| `ADVERTISER_TYPE_NAME` | Type name |
| `ADVERTISER_VERTICAL` | Industry vertical |
| `ADVERTISER_CREDIT_STATUS` | Credit status code |
| `ADVERTISER_CREDIT_STATUS_NAME` | Credit status name |

### Ad Unit Dimensions

| Dimension | Description |
|-----------|-------------|
| `AD_UNIT_ID` | Ad unit unique ID |
| `AD_UNIT_NAME` | Ad unit name |
| `AD_UNIT_CODE` | Ad unit code |
| `AD_UNIT_ID_ALL_LEVEL` | All level IDs |
| `AD_UNIT_NAME_ALL_LEVEL` | All level names |
| `AD_UNIT_ID_TOP_LEVEL` | Top level ID |
| `AD_UNIT_NAME_TOP_LEVEL` | Top level name |
| `AD_UNIT_STATUS` | Status code |
| `AD_UNIT_STATUS_NAME` | Status name |
| `AD_UNIT_REWARD_AMOUNT` | Reward amount (rewarded ads) |
| `AD_UNIT_REWARD_TYPE` | Reward type (rewarded ads) |

**Hierarchy Levels (1-16):**
- `AD_UNIT_ID_LEVEL_1` through `AD_UNIT_ID_LEVEL_5`
- `AD_UNIT_NAME_LEVEL_1` through `AD_UNIT_NAME_LEVEL_5`
- `AD_UNIT_CODE_LEVEL_1` through `AD_UNIT_CODE_LEVEL_5`

### Line Item Dimensions

| Dimension | Description |
|-----------|-------------|
| `LINE_ITEM_ID` | Line item unique ID |
| `LINE_ITEM_NAME` | Line item name |
| `LINE_ITEM_EXTERNAL_ID` | External line item ID |
| `LINE_ITEM_AGENCY` | Agency name |
| `LINE_ITEM_ARCHIVED` | Archived status |
| `LINE_ITEM_LABELS` | Line item labels |
| `LINE_ITEM_LABEL_IDS` | Label IDs |
| `LINE_ITEM_COST_TYPE` | Cost type code |
| `LINE_ITEM_COST_TYPE_NAME` | Cost type (CPM, CPC, CPD) |
| `LINE_ITEM_COST_PER_UNIT` | Cost per unit |
| `LINE_ITEM_CURRENCY_CODE` | Currency code |
| `LINE_ITEM_START_DATE` | Start date |
| `LINE_ITEM_END_DATE` | End date |
| `LINE_ITEM_END_DATE_TIME` | End date/time |
| `LINE_ITEM_DELIVERY_RATE_TYPE` | Delivery rate type code |
| `LINE_ITEM_DELIVERY_RATE_TYPE_NAME` | Delivery rate type |
| `LINE_ITEM_DELIVERY_INDICATOR` | Delivery indicator |
| `LINE_ITEM_COMPUTED_STATUS` | Computed status code |
| `LINE_ITEM_COMPUTED_STATUS_NAME` | Computed status |
| `LINE_ITEM_OPTIMIZABLE` | Optimizable flag |
| `LINE_ITEM_PRIORITY` | Priority level |
| `LINE_ITEM_CONTRACTED_QUANTITY` | Contracted quantity |
| `LINE_ITEM_LIFETIME_IMPRESSIONS` | Lifetime impressions |
| `LINE_ITEM_LIFETIME_CLICKS` | Lifetime clicks |
| `LINE_ITEM_LIFETIME_VIEWABLE_IMPRESSIONS` | Lifetime viewable impressions |
| `LINE_ITEM_FREQUENCY_CAP` | Frequency cap |
| `LINE_ITEM_EXTERNAL_DEAL_ID` | External deal ID |
| `LINE_ITEM_MAKEGOOD` | Makegood flag |
| `LINE_ITEM_PO_NUMBER` | PO number |
| `LINE_ITEM_PRIMARY_GOAL_TYPE` | Goal type code |
| `LINE_ITEM_PRIMARY_GOAL_TYPE_NAME` | Goal type name |
| `LINE_ITEM_PRIMARY_GOAL_UNIT_TYPE` | Goal unit type code |
| `LINE_ITEM_PRIMARY_GOAL_UNIT_TYPE_NAME` | Goal unit type name |
| `LINE_ITEM_RESERVATION_STATUS` | Reservation status code |
| `LINE_ITEM_RESERVATION_STATUS_NAME` | Reservation status |
| `LINE_ITEM_CREATIVE_ROTATION_TYPE` | Creative rotation type code |
| `LINE_ITEM_CREATIVE_ROTATION_TYPE_NAME` | Creative rotation type |
| `LINE_ITEM_ENVIRONMENT_TYPE` | Environment type code |
| `LINE_ITEM_ENVIRONMENT_TYPE_NAME` | Environment type |
| `LINE_ITEM_COMPANION_DELIVERY_OPTION` | Companion delivery code |
| `LINE_ITEM_COMPANION_DELIVERY_OPTION_NAME` | Companion delivery option |
| `LINE_ITEM_LAST_MODIFIED_BY_APP` | Last modified by app |
| `LINE_ITEM_NON_CPD_BOOKED_REVENUE` | Non-CPD booked revenue |
| `LINE_ITEM_DISCOUNT_ABSOLUTE` | Absolute discount |
| `LINE_ITEM_DISCOUNT_PERCENTAGE` | Discount percentage |

### Order Dimensions

| Dimension | Description |
|-----------|-------------|
| `ORDER_ID` | Order unique ID |
| `ORDER_NAME` | Order name |
| `ORDER_DELIVERY_STATUS` | Delivery status |
| `ORDER_START_DATE_TIME` | Start date/time |
| `ORDER_END_DATE_TIME` | End date/time |
| `ORDER_EXTERNAL_ID` | External order ID |
| `ORDER_PO_NUMBER` | PO number |
| `ORDER_IS_PROGRAMMATIC` | Programmatic flag |
| `ORDER_AGENCY` | Agency name |
| `ORDER_AGENCY_ID` | Agency ID |
| `ORDER_LABELS` | Order labels |
| `ORDER_LABEL_IDS` | Label IDs |
| `ORDER_TRAFFICKER` | Trafficker name |
| `ORDER_TRAFFICKER_ID` | Trafficker ID |
| `ORDER_SECONDARY_TRAFFICKERS` | Secondary traffickers |
| `ORDER_SALESPERSON` | Salesperson name |
| `ORDER_SECONDARY_SALESPEOPLE` | Secondary salespeople |
| `ORDER_LIFETIME_IMPRESSIONS` | Lifetime impressions |
| `ORDER_LIFETIME_CLICKS` | Lifetime clicks |

### Creative Dimensions

| Dimension | Description |
|-----------|-------------|
| `CREATIVE_ID` | Creative unique ID |
| `CREATIVE_NAME` | Creative name |
| `CREATIVE_TYPE` | Type code |
| `CREATIVE_TYPE_NAME` | Type name |
| `CREATIVE_BILLING_TYPE` | Billing type code |
| `CREATIVE_BILLING_TYPE_NAME` | Billing type |
| `CREATIVE_CLICK_THROUGH_URL` | Click-through URL |
| `CREATIVE_THIRD_PARTY_VENDOR` | Third-party vendor |
| `CREATIVE_TECHNOLOGY` | Technology code |
| `CREATIVE_TECHNOLOGY_NAME` | Technology name |
| `CREATIVE_SIZE` | Creative size |
| `CREATIVE_POLICIES_FILTERING` | Policy filtering code |
| `CREATIVE_POLICIES_FILTERING_NAME` | Policy filtering |
| `CREATIVE_SET_ROLE_TYPE` | Set role type |
| `CREATIVE_SET_ROLE_TYPE_NAME` | Set role type name |
| `CREATIVE_VIDEO_REDIRECT_THIRD_PARTY` | Video redirect |

### Geographic Dimensions

| Dimension | Description |
|-----------|-------------|
| `COUNTRY_ID` | Country ID |
| `COUNTRY_NAME` | Country name |
| `COUNTRY_CODE` | Country code (ISO) |
| `CONTINENT` | Continent code |
| `CONTINENT_NAME` | Continent name |
| `CITY_ID` | City ID |
| `CITY_NAME` | City name |
| `REGION_CODE` | Region code |
| `REGION_NAME` | Region name |
| `METRO_CODE` | Metro area code |
| `METRO_NAME` | Metro area name |

### Device Dimensions

| Dimension | Description |
|-----------|-------------|
| `DEVICE` | Device code |
| `DEVICE_NAME` | Device name |
| `DEVICE_CATEGORY` | Category code |
| `DEVICE_CATEGORY_NAME` | Category (Desktop, Mobile, Tablet) |
| `DEVICE_MANUFACTURER_ID` | Manufacturer ID |
| `DEVICE_MANUFACTURER_NAME` | Manufacturer name |
| `DEVICE_MODEL_ID` | Model ID |
| `DEVICE_MODEL_NAME` | Model name |
| `BROWSER_ID` | Browser ID |
| `BROWSER_NAME` | Browser name |
| `BROWSER_CATEGORY` | Browser category code |
| `BROWSER_CATEGORY_NAME` | Browser category |
| `OS_ID` | Operating system ID |
| `OS_NAME` | Operating system name |
| `OS_VERSION` | OS version |
| `CARRIER_ID` | Carrier ID |
| `CARRIER_NAME` | Carrier name |

### Programmatic Dimensions

| Dimension | Description |
|-----------|-------------|
| `DEMAND_CHANNEL` | Demand channel code |
| `DEMAND_CHANNEL_NAME` | Demand channel name |
| `DEMAND_SOURCE` | Demand source code |
| `DEMAND_SOURCE_NAME` | Demand source name |
| `DEMAND_SUBCHANNEL` | Subchannel code |
| `DEMAND_SUBCHANNEL_NAME` | Subchannel name |
| `CHANNEL` | Channel |
| `DEAL_ID` | Deal ID |
| `DEAL_NAME` | Deal name |
| `DEAL_BUYER_ID` | Deal buyer ID |
| `DEAL_BUYER_NAME` | Deal buyer name |
| `BIDDER_ENCRYPTED_ID` | Bidder encrypted ID |
| `BIDDER_NAME` | Bidder name |
| `BID_RANGE` | Bid range |
| `BID_REJECTION_REASON` | Rejection reason code |
| `BID_REJECTION_REASON_NAME` | Rejection reason |
| `BUYER_NETWORK_ID` | Buyer network ID |
| `BUYER_NETWORK_NAME` | Buyer network name |
| `ADX_PRODUCT` | Ad Exchange product code |
| `ADX_PRODUCT_NAME` | Ad Exchange product |
| `BRANDING_TYPE` | Branding type code |
| `BRANDING_TYPE_NAME` | Branding type |
| `DYNAMIC_ALLOCATION_TYPE` | Dynamic allocation code |
| `DYNAMIC_ALLOCATION_TYPE_NAME` | Dynamic allocation type |
| `IS_ADX_DIRECT` | Ad Exchange Direct flag |
| `IS_FIRST_LOOK_DEAL` | First Look deal flag |
| `YIELD_GROUP_ID` | Yield group ID |
| `YIELD_GROUP_NAME` | Yield group name |
| `YIELD_PARTNER_ID` | Yield partner ID |
| `YIELD_PARTNER_NAME` | Yield partner name |

### Custom Targeting Dimensions

| Dimension | Description |
|-----------|-------------|
| `KEY_VALUES_ID` | Key-value ID |
| `KEY_VALUES_NAME` | Key-value name |
| `CUSTOM_SPOT_ID` | Custom spot ID |
| `CUSTOM_SPOT_NAME` | Custom spot name |
| `CUSTOM_CRITERIA` | Custom criteria |
| `CUSTOM_TARGETING_VALUE_ID` | Targeting value ID |
| `CUSTOM_TARGETING_VALUE_NAME` | Targeting value name |

### Audience Dimensions

| Dimension | Description |
|-----------|-------------|
| `AGE_BRACKET` | Age bracket code |
| `AGE_BRACKET_NAME` | Age bracket |
| `GENDER` | Gender code |
| `GENDER_NAME` | Gender |
| `INTEREST` | Interest segment |
| `AUDIENCE_SEGMENT_ID_TARGETED` | Targeted segment ID |
| `AUDIENCE_SEGMENT_TARGETED` | Targeted segment name |

### Content Dimensions

| Dimension | Description |
|-----------|-------------|
| `CONTENT_ID` | Content ID |
| `CONTENT_NAME` | Content name |
| `CONTENT_CMS_NAME` | CMS name |
| `CONTENT_CMS_VIDEO_ID` | CMS video ID |
| `CONTENT_MAPPING_PRESENCE` | Content mapping code |
| `CONTENT_MAPPING_PRESENCE_NAME` | Content mapping |

### Other Dimensions

| Dimension | Description |
|-----------|-------------|
| `PLACEMENT_ID` | Placement ID |
| `PLACEMENT_NAME` | Placement name |
| `INVENTORY_TYPE` | Inventory type code |
| `INVENTORY_TYPE_NAME` | Inventory type |
| `INVENTORY_FORMAT` | Inventory format code |
| `INVENTORY_FORMAT_NAME` | Inventory format |
| `AD_LOCATION` | Ad location code |
| `AD_LOCATION_NAME` | Ad location |
| `AD_TYPE` | Ad type code |
| `AD_TYPE_NAME` | Ad type name |
| `AD_EXPERIENCES_TYPE` | Ad experiences type code |
| `AD_EXPERIENCES_TYPE_NAME` | Ad experiences type |
| `APP_VERSION` | App version |
| `SALESPERSON_ID` | Salesperson ID |
| `SALESPERSON_NAME` | Salesperson name |
| `CHILD_NETWORK_CODE` | Child network code (MCM) |
| `CHILD_NETWORK_ID` | Child network ID |
| `CHILD_PARTNER_NAME` | Child partner name |

---

## Metrics

### Core Ad Server Metrics

| Metric | Description |
|--------|-------------|
| `AD_SERVER_IMPRESSIONS` | Ad server impressions |
| `AD_SERVER_BEGIN_TO_RENDER_IMPRESSIONS` | Begin-to-render impressions |
| `AD_SERVER_TARGETED_IMPRESSIONS` | Targeted impressions |
| `AD_SERVER_CLICKS` | Ad server clicks |
| `AD_SERVER_TARGETED_CLICKS` | Targeted clicks |
| `AD_SERVER_UNFILTERED_IMPRESSIONS` | Unfiltered impressions |
| `AD_SERVER_UNFILTERED_CLICKS` | Unfiltered clicks |
| `AD_SERVER_CTR` | Click-through rate |

### Revenue Metrics

| Metric | Description |
|--------|-------------|
| `AD_SERVER_CPM_AND_CPC_REVENUE` | CPM and CPC revenue |
| `AD_SERVER_CPM_AND_CPC_REVENUE_GROSS` | CPM and CPC revenue (gross) |
| `AD_SERVER_CPD_REVENUE` | CPD revenue |
| `AD_SERVER_ALL_REVENUE` | All revenue |
| `AD_SERVER_ALL_REVENUE_GROSS` | All revenue (gross) |
| `AD_SERVER_WITHOUT_CPD_AVERAGE_ECPM` | Average eCPM (without CPD) |
| `AD_SERVER_WITH_CPD_AVERAGE_ECPM` | Average eCPM (with CPD) |
| `REVENUE` | Total revenue (simplified) |
| `ECPM` | Effective CPM (simplified) |
| `CPC` | Cost per click (simplified) |

### Total/Aggregated Metrics

| Metric | Description |
|--------|-------------|
| `TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS` | Total line item impressions |
| `TOTAL_LINE_ITEM_LEVEL_TARGETED_IMPRESSIONS` | Total targeted impressions |
| `TOTAL_LINE_ITEM_LEVEL_CLICKS` | Total line item clicks |
| `TOTAL_LINE_ITEM_LEVEL_TARGETED_CLICKS` | Total targeted clicks |
| `TOTAL_LINE_ITEM_LEVEL_CTR` | Total CTR |
| `TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE` | Total CPM and CPC revenue |
| `TOTAL_LINE_ITEM_LEVEL_ALL_REVENUE` | Total all revenue |
| `TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM` | Total average eCPM (without CPD) |
| `TOTAL_LINE_ITEM_LEVEL_WITH_CPD_AVERAGE_ECPM` | Total average eCPM (with CPD) |
| `IMPRESSIONS` | Total impressions (simplified) |
| `CLICKS` | Total clicks (simplified) |
| `CTR` | Click-through rate (simplified) |

### Inventory Metrics

| Metric | Description |
|--------|-------------|
| `TOTAL_CODE_SERVED_COUNT` | Total code served |
| `TOTAL_AD_REQUESTS` | Total ad requests |
| `AD_REQUESTS` | Ad requests (simplified) |
| `TOTAL_RESPONSES_SERVED` | Total responses served |
| `TOTAL_UNMATCHED_AD_REQUESTS` | Unmatched ad requests |
| `TOTAL_FILL_RATE` | Total fill rate |
| `FILL_RATE` | Fill rate (simplified) |
| `TOTAL_INVENTORY_LEVEL_UNFILLED_IMPRESSIONS` | Unfilled impressions |
| `UNFILLED_IMPRESSIONS` | Unfilled impressions (simplified) |
| `MATCHED_REQUESTS` | Matched requests (simplified) |
| `INVENTORY_LEVEL_IMPRESSIONS` | Inventory level impressions |

### AdSense Metrics

| Metric | Description |
|--------|-------------|
| `ADSENSE_LINE_ITEM_LEVEL_IMPRESSIONS` | AdSense impressions |
| `ADSENSE_LINE_ITEM_LEVEL_CLICKS` | AdSense clicks |
| `ADSENSE_LINE_ITEM_LEVEL_CTR` | AdSense CTR |
| `ADSENSE_LINE_ITEM_LEVEL_REVENUE` | AdSense revenue |
| `ADSENSE_LINE_ITEM_LEVEL_AVERAGE_ECPM` | AdSense average eCPM |
| `ADSENSE_RESPONSES_SERVED` | AdSense responses served |

### Ad Exchange Metrics

| Metric | Description |
|--------|-------------|
| `AD_EXCHANGE_LINE_ITEM_LEVEL_IMPRESSIONS` | Ad Exchange impressions |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_CLICKS` | Ad Exchange clicks |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_CTR` | Ad Exchange CTR |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_REVENUE` | Ad Exchange revenue |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_AVERAGE_ECPM` | Ad Exchange average eCPM |
| `AD_EXCHANGE_TOTAL_REQUESTS` | Ad Exchange total requests |
| `AD_EXCHANGE_MATCH_RATE` | Ad Exchange match rate |
| `AD_EXCHANGE_COST_PER_CLICK` | Ad Exchange CPC |
| `AD_EXCHANGE_TOTAL_REQUEST_CTR` | Total request CTR |
| `AD_EXCHANGE_MATCHED_REQUEST_CTR` | Matched request CTR |
| `AD_EXCHANGE_TOTAL_REQUEST_ECPM` | Total request eCPM |
| `AD_EXCHANGE_MATCHED_REQUEST_ECPM` | Matched request eCPM |
| `AD_EXCHANGE_LIFT_EARNINGS` | Lift earnings |
| `AD_EXCHANGE_RESPONSES_SERVED` | Ad Exchange responses served |

### Active View Metrics

| Metric | Description |
|--------|-------------|
| `TOTAL_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS` | Viewable impressions |
| `TOTAL_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS` | Measurable impressions |
| `TOTAL_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS_RATE` | Viewable rate |
| `TOTAL_ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS` | Eligible impressions |
| `TOTAL_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS_RATE` | Measurable rate |
| `TOTAL_ACTIVE_VIEW_AVERAGE_VIEWABLE_TIME` | Average viewable time |
| `TOTAL_ACTIVE_VIEW_REVENUE` | Active View revenue |
| `ACTIVE_VIEW_PERCENT_AUDIBLE_START_IMPRESSIONS` | Audible start % |
| `ACTIVE_VIEW_PERCENT_EVER_AUDIBLE_IMPRESSIONS` | Ever audible % |
| `AD_SERVER_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS` | Ad server viewable impressions |
| `AD_SERVER_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS` | Ad server measurable impressions |
| `AD_SERVER_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS_RATE` | Ad server viewable rate |
| `AD_SERVER_ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS` | Ad server eligible impressions |
| `AD_SERVER_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS_RATE` | Ad server measurable rate |
| `AD_SERVER_ACTIVE_VIEW_REVENUE` | Ad server Active View revenue |
| `AD_SERVER_ACTIVE_VIEW_AVERAGE_VIEWABLE_TIME` | Ad server average viewable time |

### Video Viewership Metrics

| Metric | Description |
|--------|-------------|
| `VIDEO_VIEWERSHIP_START` | Video starts |
| `VIDEO_VIEWERSHIP_FIRST_QUARTILE` | First quartile views |
| `VIDEO_VIEWERSHIP_MIDPOINT` | Midpoint views |
| `VIDEO_VIEWERSHIP_THIRD_QUARTILE` | Third quartile views |
| `VIDEO_VIEWERSHIP_COMPLETE` | Complete views |
| `VIDEO_VIEWERSHIP_AVERAGE_VIEW_RATE` | Average view rate |
| `VIDEO_VIEWERSHIP_AVERAGE_VIEW_TIME` | Average view time |
| `VIDEO_VIEWERSHIP_COMPLETION_RATE` | Completion rate |
| `VIDEO_VIEWERSHIP_TOTAL_ERROR_COUNT` | Total errors |
| `VIDEO_VIEWERSHIP_VIDEO_LENGTH` | Video length |
| `VIDEO_VIEWERSHIP_SKIP_BUTTON_SHOWN` | Skip button shown |
| `VIDEO_VIEWERSHIP_ENGAGED_VIEW` | Engaged views |
| `VIDEO_VIEWERSHIP_VIEW_THROUGH_RATE` | View-through rate |
| `VIDEO_VIEWERSHIP_AUTO_PLAYS` | Auto-plays |
| `VIDEO_VIEWERSHIP_CLICK_TO_PLAYS` | Click-to-plays |
| `VIDEO_VIEWERSHIP_TOTAL_ERROR_RATE` | Error rate |

### Video Interaction Metrics

| Metric | Description |
|--------|-------------|
| `VIDEO_INTERACTION_PAUSE` | Video pauses |
| `VIDEO_INTERACTION_RESUME` | Video resumes |
| `VIDEO_INTERACTION_REWIND` | Video rewinds |
| `VIDEO_INTERACTION_MUTE` | Video mutes |
| `VIDEO_INTERACTION_UNMUTE` | Video unmutes |
| `VIDEO_INTERACTION_COLLAPSE` | Video collapses |
| `VIDEO_INTERACTION_EXPAND` | Video expands |
| `VIDEO_INTERACTION_FULL_SCREEN` | Full screen views |
| `VIDEO_INTERACTION_AVERAGE_INTERACTION_RATE` | Average interaction rate |
| `VIDEO_INTERACTION_VIDEO_SKIPS` | Video skips |

### Video Opportunity Metrics

| Metric | Description |
|--------|-------------|
| `TOTAL_VIDEO_OPPORTUNITIES` | Total video opportunities |
| `TOTAL_VIDEO_CAPPED_OPPORTUNITIES` | Capped opportunities |
| `TOTAL_VIDEO_MATCHED_OPPORTUNITIES` | Matched opportunities |
| `TOTAL_VIDEO_MATCHED_DURATION` | Matched duration |
| `TOTAL_VIDEO_DURATION` | Total video duration |
| `TOTAL_VIDEO_BREAK_START` | Break starts |
| `TOTAL_VIDEO_BREAK_END` | Break ends |

### Bidding & Yield Metrics

| Metric | Description |
|--------|-------------|
| `BID_COUNT` | Bid count |
| `BID_AVERAGE_CPM` | Average bid CPM |
| `YIELD_GROUP_CALLOUTS` | Yield group callouts |
| `YIELD_GROUP_SUCCESSFUL_RESPONSES` | Successful responses |
| `YIELD_GROUP_BIDS` | Yield group bids |
| `YIELD_GROUP_BIDS_IN_AUCTION` | Bids in auction |
| `YIELD_GROUP_AUCTIONS_WON` | Auctions won |
| `YIELD_GROUP_IMPRESSIONS` | Yield group impressions |
| `YIELD_GROUP_ESTIMATED_REVENUE` | Estimated revenue |
| `YIELD_GROUP_ESTIMATED_CPM` | Estimated CPM |
| `YIELD_GROUP_MEDIATION_FILL_RATE` | Mediation fill rate |
| `YIELD_GROUP_MEDIATION_PASSBACKS` | Mediation passbacks |
| `YIELD_GROUP_MEDIATION_THIRD_PARTY_ECPM` | Mediation third-party eCPM |
| `YIELD_GROUP_MEDIATION_CHAINS_SERVED` | Mediation chains served |
| `MEDIATION_THIRD_PARTY_ECPM` | Third-party eCPM |

### Programmatic Deals Metrics

| Metric | Description |
|--------|-------------|
| `DEALS_BID_REQUESTS` | Deal bid requests |
| `DEALS_BIDS` | Deal bids |
| `DEALS_BID_RATE` | Deal bid rate |
| `DEALS_WINNING_BIDS` | Winning bids |
| `DEALS_WIN_RATE` | Win rate |
| `PROGRAMMATIC_RESPONSES_SERVED` | Programmatic responses |
| `PROGRAMMATIC_MATCH_RATE` | Programmatic match rate |
| `TOTAL_PROGRAMMATIC_ELIGIBLE_AD_REQUESTS` | Programmatic eligible requests |

### Reach Metrics

**Note:** These metrics require `reportType: 'REACH'`

| Metric | Description |
|--------|-------------|
| `UNIQUE_REACH_FREQUENCY` | Average frequency |
| `UNIQUE_REACH_IMPRESSIONS` | Reach impressions |
| `UNIQUE_REACH` | Unique users reached |

### Rich Media Metrics

| Metric | Description |
|--------|-------------|
| `RICH_MEDIA_BACKUP_IMAGES` | Backup images served |
| `RICH_MEDIA_DISPLAY_TIME` | Display time |
| `RICH_MEDIA_AVERAGE_DISPLAY_TIME` | Average display time |
| `RICH_MEDIA_EXPANSIONS` | Expansions |
| `RICH_MEDIA_EXPANDING_TIME` | Expanding time |
| `RICH_MEDIA_INTERACTION_TIME` | Interaction time |
| `RICH_MEDIA_INTERACTION_COUNT` | Interaction count |
| `RICH_MEDIA_INTERACTION_RATE` | Interaction rate |
| `RICH_MEDIA_AVERAGE_INTERACTION_TIME` | Average interaction time |
| `RICH_MEDIA_INTERACTION_IMPRESSIONS` | Interaction impressions |
| `RICH_MEDIA_MANUAL_CLOSES` | Manual closes |
| `RICH_MEDIA_FULL_SCREEN_IMPRESSIONS` | Full-screen impressions |

### Forecasting Metrics

| Metric | Description |
|--------|-------------|
| `SELL_THROUGH_FORECASTED_IMPRESSIONS` | Forecasted impressions |
| `SELL_THROUGH_AVAILABLE_IMPRESSIONS` | Available impressions |
| `SELL_THROUGH_RESERVED_IMPRESSIONS` | Reserved impressions |
| `SELL_THROUGH_SELL_THROUGH_RATE` | Sell-through rate |

### Ad Speed Metrics

| Metric | Description |
|--------|-------------|
| `CREATIVE_LOAD_TIME_0_500_MS_PERCENT` | Load time 0-500ms % |
| `CREATIVE_LOAD_TIME_500_1000_MS_PERCENT` | Load time 500ms-1s % |
| `CREATIVE_LOAD_TIME_1_2_S_PERCENT` | Load time 1-2s % |
| `CREATIVE_LOAD_TIME_2_4_S_PERCENT` | Load time 2-4s % |
| `CREATIVE_LOAD_TIME_4_8_S_PERCENT` | Load time 4-8s % |
| `CREATIVE_LOAD_TIME_GREATER_THAN_8_S_PERCENT` | Load time >8s % |

---

## Dimension-Metric Compatibility

Not all dimensions work with all metrics. Here are common compatibility rules:

### REACH Metrics
- **Required**: `reportType: 'REACH'`
- **Compatible dimensions**: `DATE`, `COUNTRY_NAME`, `DEVICE_CATEGORY_NAME`, `AGE_BRACKET`

### Video Metrics
- **Required**: Video ad units/line items
- **Compatible dimensions**: All standard dimensions plus video-specific

### Ad Exchange Metrics
- **Required**: Ad Exchange enabled
- **Compatible dimensions**: Most programmatic dimensions

### Active View Metrics
- **Required**: Active View enabled for ad units
- **Compatible dimensions**: All standard dimensions

---

## Common Combinations by Report Type

### Delivery Report
```python
dimensions = ['DATE', 'AD_UNIT_NAME', 'ADVERTISER_NAME', 'ORDER_NAME']
metrics = ['IMPRESSIONS', 'CLICKS', 'CTR', 'REVENUE', 'ECPM']
```

### Inventory Report
```python
dimensions = ['DATE', 'AD_UNIT_NAME', 'DEVICE_CATEGORY_NAME']
metrics = ['AD_REQUESTS', 'MATCHED_REQUESTS', 'FILL_RATE', 'IMPRESSIONS']
```

### Sales Report
```python
dimensions = ['DATE', 'ADVERTISER_NAME', 'ORDER_NAME', 'SALESPERSON_NAME']
metrics = ['REVENUE', 'IMPRESSIONS', 'ECPM', 'CLICKS', 'CTR']
```

### Reach Report
```python
# Note: reportType must be 'REACH'
dimensions = ['DATE', 'COUNTRY_NAME', 'DEVICE_CATEGORY_NAME', 'AGE_BRACKET']
metrics = ['UNIQUE_REACH', 'UNIQUE_REACH_FREQUENCY', 'UNIQUE_REACH_IMPRESSIONS']
```

### Programmatic Report
```python
dimensions = ['DATE', 'DEMAND_CHANNEL_NAME', 'DEAL_NAME', 'BUYER_NETWORK_NAME']
metrics = ['AD_EXCHANGE_LINE_ITEM_LEVEL_IMPRESSIONS', 'AD_EXCHANGE_LINE_ITEM_LEVEL_REVENUE', 'AD_EXCHANGE_LINE_ITEM_LEVEL_AVERAGE_ECPM']
```

---

## Using Dimensions and Metrics

### Get Available Dimensions/Metrics

```python
# Via Python SDK
from gam_api import GAMClient
client = GAMClient()
dimensions = client.get_dimensions()
metrics = client.get_metrics()

# Via MCP Tool
mcp_client.call_tool("gam_get_dimensions_metrics")
```

### Validate Combinations

```python
# Check if dimensions and metrics are compatible
client.validate_dimensions_metrics(
    dimensions=['DATE', 'AD_UNIT_NAME'],
    metrics=['IMPRESSIONS', 'UNIQUE_REACH']  # Will fail - UNIQUE_REACH needs REACH report type
)
```

### Custom Report with Specific Dimensions/Metrics

```python
from gam_api.reports import ReportGenerator

generator = ReportGenerator(client)
report = generator.create_custom_report(
    dimensions=['DATE', 'AD_UNIT_NAME', 'COUNTRY_NAME'],
    metrics=['IMPRESSIONS', 'CLICKS', 'CTR', 'REVENUE'],
    date_range={'start_date': '2024-01-01', 'end_date': '2024-01-31'},
    filters=[
        {'field': 'COUNTRY_NAME', 'operator': 'IN', 'values': ['US', 'CA', 'GB']}
    ]
)
```

---

**Reference**: Based on Google Ad Manager API v202511
**Last Updated**: 2025-12-01
