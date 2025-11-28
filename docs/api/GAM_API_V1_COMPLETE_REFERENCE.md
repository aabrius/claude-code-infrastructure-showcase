# Google Ad Manager API v1 - Complete Report Reference

Based on: https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks.reports

## Report Resource

### Resource Representation
```json
{
  "name": string,
  "reportId": string,
  "visibility": enum (Visibility),
  "displayName": string,
  "updateTime": string,
  "createTime": string,
  "locale": string,
  "scheduleOptions": {
    object (ScheduleOptions)
  },
  "reportDefinition": {
    object (ReportDefinition)
  }
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Identifier. The resource name of the report. Format: `networks/{network_code}/reports/{report_id}` |
| `reportId` | string (int64) | Output only. Report ID. |
| `visibility` | enum (Visibility) | The visibility of the report. |
| `displayName` | string | Required. The display name of the report. |
| `updateTime` | string (Timestamp) | Output only. The time the report was last updated. |
| `createTime` | string (Timestamp) | Output only. The time the report was created. |
| `locale` | string | The locale for this report. Locale is used to determine currency and number formatting. |
| `scheduleOptions` | object (ScheduleOptions) | Optional. The schedule options for the report. |
| `reportDefinition` | object (ReportDefinition) | Required. The report definition. |

## Visibility Enum

Controls who can see and access the report.

| Value | Description |
|-------|-------------|
| `VISIBILITY_UNSPECIFIED` | Not specified |
| `HIDDEN` | Report is hidden from the UI but still accessible via API |
| `DRAFT` | Report is a draft and not yet finalized |
| `SAVED` | Report is saved and visible in the UI |

## ReportDefinition Object

```json
{
  "dimensions": [
    enum (Dimension)
  ],
  "metrics": [
    enum (Metric)
  ],
  "filters": [
    {
      object (Filter)
    }
  ],
  "sorts": [
    {
      object (Sort)
    }
  ],
  "dateRange": {
    object (DateRange)
  },
  "compareDateRange": {
    object (DateRange)
  },
  "localizationSettings": {
    object (LocalizationSettings)
  },
  "timeZone": string,
  "timeZoneSource": enum (TimeZoneSource),
  "currencyCode": string,
  "reportType": enum (ReportType),
  "timePeriodColumn": enum (TimePeriodColumn),
  "customDimensionKeyIds": [
    string
  ],
  "lineItemCustomFieldIds": [
    string
  ],
  "orderCustomFieldIds": [
    string
  ],
  "creativeCustomFieldIds": [
    string
  ],
  "flags": [
    {
      object (Flag)
    }
  ]
}
```

### ReportDefinition Fields

| Field | Type | Description |
|-------|------|-------------|
| `dimensions` | enum (Dimension)[] | Required. The dimensions for the report. |
| `metrics` | enum (Metric)[] | Required. The metrics for the report. |
| `filters` | object (Filter)[] | Optional. Filters to apply to the report. |
| `sorts` | object (Sort)[] | Optional. Sort order for the report rows. |
| `dateRange` | object (DateRange) | Required. The date range for the report. |
| `compareDateRange` | object (DateRange) | Optional. Comparison date range for the report. |
| `localizationSettings` | object (LocalizationSettings) | Optional. Localization settings. |
| `timeZone` | string | The time zone the date range is defined in. Defaults to network's time zone. Uses IANA time zone identifiers. |
| `timeZoneSource` | enum (TimeZoneSource) | The source of the time zone. |
| `currencyCode` | string | Currency code for revenue metrics. Defaults to network's currency code. |
| `reportType` | enum (ReportType) | Required. The type of the report. |
| `timePeriodColumn` | enum (TimePeriodColumn) | Include a time period column to introduce comparison columns. |
| `customDimensionKeyIds` | string[] | Custom dimension key IDs for KEY_VALUES dimension. Format: `networks/{network_code}/customTargetingKeys/{key_id}` |
| `lineItemCustomFieldIds` | string[] | Custom field IDs for line items. Format: `networks/{network_code}/customFields/{field_id}` |
| `orderCustomFieldIds` | string[] | Custom field IDs for orders. Format: `networks/{network_code}/customFields/{field_id}` |
| `creativeCustomFieldIds` | string[] | Custom field IDs for creatives. Format: `networks/{network_code}/customFields/{field_id}` |
| `flags` | object (Flag)[] | Optional. Flags to control report behavior. |

## Sort Object

```json
{
  "field": {
    // Union field can be one of:
    "dimension": enum (Dimension),
    "metric": enum (Metric)
  },
  "descending": boolean
}
```

### Sort Fields

| Field | Type | Description |
|-------|------|-------------|
| `field` | union | The field to sort by. Can be either a dimension or metric. |
| `descending` | boolean | If true, sort in descending order. Default is ascending (false). |

## TimeZoneSource Enum

| Value | Description |
|-------|-------------|
| `TIME_ZONE_SOURCE_UNSPECIFIED` | Not specified |
| `NETWORK` | Use the network's default time zone |
| `CUSTOM` | Use a custom time zone specified in the `timeZone` field |

## DateRange Object

```json
{
  // Union field date_range_type can be only one of the following:
  "fixed": {
    object (FixedDateRange)
  },
  "relative": {
    object (RelativeDateRange)
  }
  // End of list of possible types for union field date_range_type.
}
```

### FixedDateRange
```json
{
  "startDate": {
    object (Date)
  },
  "endDate": {
    object (Date)
  }
}
```

### RelativeDateRange
```json
{
  "relativePreset": enum (Preset)
}
```

#### Preset Enum Values
- `PRESET_UNSPECIFIED`
- `TODAY`
- `YESTERDAY`
- `THIS_WEEK`
- `THIS_WEEK_TO_DATE`
- `THIS_MONTH`
- `THIS_MONTH_TO_DATE`
- `THIS_QUARTER`
- `THIS_QUARTER_TO_DATE`
- `THIS_YEAR`
- `THIS_YEAR_TO_DATE`
- `LAST_7_DAYS`
- `LAST_30_DAYS`
- `LAST_WEEK`
- `LAST_MONTH`
- `LAST_QUARTER`
- `LAST_YEAR`
- `LAST_7_DAYS_TO_DATE`
- `LAST_30_DAYS_TO_DATE`
- `ALL_TIME`

### Date Object
```json
{
  "year": integer,
  "month": integer,
  "day": integer
}
```

## Filter Object

```json
{
  // Union field value can be only one of the following:
  "stringValue": {
    object (StringValue)
  },
  "intValue": {
    object (IntValue)
  },
  "boolValue": {
    object (BoolValue)
  }
  // End of list of possible types for union field value.
}
```

### StringValue
```json
{
  "values": [
    string
  ],
  "matchType": enum (MatchType)
}
```

#### MatchType Enum Values
- `MATCH_TYPE_UNSPECIFIED`
- `EXACT`
- `BEGINS_WITH`
- `CONTAINS`
- `ENDS_WITH`

### IntValue
```json
{
  "values": [
    string
  ],
  "operation": enum (Operation)
}
```

#### Operation Enum Values
- `OPERATION_UNSPECIFIED`
- `EQUALS`
- `LESS_THAN`
- `LESS_THAN_OR_EQUALS`
- `GREATER_THAN`
- `GREATER_THAN_OR_EQUALS`
- `BETWEEN`

### BoolValue
```json
{
  "value": boolean
}
```

## LocalizationSettings Object

```json
{
  "locale": string,
  "languageCode": string,
  "timeZone": string
}
```

## ReportType Enum

| Value | Description |
|-------|-------------|
| `REPORT_TYPE_UNSPECIFIED` | Not specified |
| `HISTORICAL` | Historical data report |
| `REACH` | Reach report |
| `AD_SPEED` | Ad speed report |

## TimePeriodColumn Enum

| Value | Description |
|-------|-------------|
| `TIME_PERIOD_COLUMN_UNSPECIFIED` | Not specified |
| `TIME_PERIOD_COLUMN_DATE` | Date column |
| `TIME_PERIOD_COLUMN_WEEK` | Week column |
| `TIME_PERIOD_COLUMN_MONTH` | Month column |

---

## Dimension Enum (Complete List)

> **Note:** Dimensions ending in `_NAME` return localized strings. Dimensions ending in `_ID` return identifiers.

### Time Dimensions
| Dimension | Description |
|-----------|-------------|
| `DATE` | Breaks down reporting data by date |
| `HOUR` | Breaks down reporting data by hour in one day |
| `DAY_OF_WEEK` | Breaks down reporting data by day of the week |

### Advertiser Dimensions
| Dimension | Description |
|-----------|-------------|
| `ADVERTISER_ID` | The ID of an advertiser company assigned to an order |
| `ADVERTISER_NAME` | The name of an advertiser company assigned to an order |
| `ADVERTISER_DOMAIN_NAME` | The domain name of the advertiser |
| `ADVERTISER_EXTERNAL_ID` | The ID used in an external system for advertiser identification |
| `ADVERTISER_LABELS` | Labels for competitive or ad exclusion purposes |
| `ADVERTISER_LABEL_IDS` | Label identifiers for competitive or ad exclusion |
| `ADVERTISER_PRIMARY_CONTACT` | The name of the contact associated with an advertiser company |
| `ADVERTISER_STATUS` | Advertiser status code |
| `ADVERTISER_STATUS_NAME` | Advertiser status localized name |
| `ADVERTISER_TYPE` | Advertiser type code |
| `ADVERTISER_TYPE_NAME` | Advertiser type localized name |
| `ADVERTISER_VERTICAL` | The category of an advertiser (e.g., Arts & Entertainment, Travel) |
| `ADVERTISER_CREDIT_STATUS` | Advertiser credit status code |
| `ADVERTISER_CREDIT_STATUS_NAME` | Advertiser credit status localized name |

### Ad Unit Dimensions
| Dimension | Description |
|-----------|-------------|
| `AD_UNIT_ID` | The ID of the ad unit where the ad was requested |
| `AD_UNIT_NAME` | The name of the ad unit where the ad was requested |
| `AD_UNIT_CODE` | The code of the ad unit where the ad was requested |
| `AD_UNIT_ID_ALL_LEVEL` | The full hierarchy of ad unit IDs from root to leaf |
| `AD_UNIT_NAME_ALL_LEVEL` | The full hierarchy of ad unit names from root to leaf |
| `AD_UNIT_ID_TOP_LEVEL` | The top-level ad unit ID |
| `AD_UNIT_NAME_TOP_LEVEL` | The top-level ad unit name |
| `AD_UNIT_ID_LEVEL_1` through `AD_UNIT_ID_LEVEL_16` | Ad unit IDs at specific hierarchy levels |
| `AD_UNIT_NAME_LEVEL_1` through `AD_UNIT_NAME_LEVEL_16` | Ad unit names at specific hierarchy levels |
| `AD_UNIT_CODE_LEVEL_1` through `AD_UNIT_CODE_LEVEL_16` | Ad unit codes at specific hierarchy levels |
| `AD_UNIT_STATUS` | Ad unit status code |
| `AD_UNIT_STATUS_NAME` | Ad unit status localized name |
| `AD_UNIT_REWARD_AMOUNT` | The reward amount of the ad unit |
| `AD_UNIT_REWARD_TYPE` | The reward type of the ad unit |

### Line Item Dimensions
| Dimension | Description |
|-----------|-------------|
| `LINE_ITEM_ID` | Line item identifier |
| `LINE_ITEM_NAME` | Line item name |
| `LINE_ITEM_EXTERNAL_ID` | The external ID of the Line item |
| `LINE_ITEM_AGENCY` | The agency of the order associated with the line item |
| `LINE_ITEM_ARCHIVED` | Whether a Line item is archived |
| `LINE_ITEM_LABELS` | Line item labels |
| `LINE_ITEM_LABEL_IDS` | Line item label identifiers |
| `LINE_ITEM_COST_TYPE` | Line item cost type code |
| `LINE_ITEM_COST_TYPE_NAME` | Line item cost type localized name |
| `LINE_ITEM_COST_PER_UNIT` | The cost per unit of the Line item |
| `LINE_ITEM_CURRENCY_CODE` | The 3 letter currency code of the Line Item |
| `LINE_ITEM_START_DATE` | The start date of the Line item |
| `LINE_ITEM_END_DATE` | The end date of the Line item |
| `LINE_ITEM_END_DATE_TIME` | The end date and time of the Line item |
| `LINE_ITEM_DELIVERY_RATE_TYPE` | Line item delivery rate type code |
| `LINE_ITEM_DELIVERY_RATE_TYPE_NAME` | Line item delivery rate type localized name |
| `LINE_ITEM_DELIVERY_INDICATOR` | The progress made for the delivery of the Line item |
| `LINE_ITEM_COMPUTED_STATUS` | Line item computed status code |
| `LINE_ITEM_COMPUTED_STATUS_NAME` | Line item computed status localized name |
| `LINE_ITEM_OPTIMIZABLE` | Whether a Line item is eligible for optimization |
| `LINE_ITEM_PRIORITY` | The priority of this Line item (1-16) |
| `LINE_ITEM_CONTRACTED_QUANTITY` | The contracted units bought for the Line item |
| `LINE_ITEM_LIFETIME_IMPRESSIONS` | Total impressions delivered over the lifetime |
| `LINE_ITEM_LIFETIME_CLICKS` | Total clicks delivered over the lifetime |
| `LINE_ITEM_LIFETIME_VIEWABLE_IMPRESSIONS` | Total viewable impressions delivered over the lifetime |
| `LINE_ITEM_FREQUENCY_CAP` | The frequency cap of the Line item |
| `LINE_ITEM_EXTERNAL_DEAL_ID` | The deal ID for Programmatic Direct campaigns |
| `LINE_ITEM_MAKEGOOD` | Whether or not the Line item is Makegood |
| `LINE_ITEM_PO_NUMBER` | The PO number of the order associated with the line item |
| `LINE_ITEM_PRIMARY_GOAL_TYPE` | Line item primary goal type code |
| `LINE_ITEM_PRIMARY_GOAL_TYPE_NAME` | Line item primary goal type localized name |
| `LINE_ITEM_PRIMARY_GOAL_UNIT_TYPE` | Line item primary goal unit type code |
| `LINE_ITEM_PRIMARY_GOAL_UNIT_TYPE_NAME` | Line item primary goal unit type localized name |
| `LINE_ITEM_RESERVATION_STATUS` | Line item reservation status code |
| `LINE_ITEM_RESERVATION_STATUS_NAME` | Line item reservation status localized name |
| `LINE_ITEM_CREATIVE_ROTATION_TYPE` | Creative rotation type code |
| `LINE_ITEM_CREATIVE_ROTATION_TYPE_NAME` | Creative rotation type localized name |
| `LINE_ITEM_CREATIVE_START_DATE` | Start date of a creative associated with line item |
| `LINE_ITEM_CREATIVE_END_DATE` | End date of a creative associated with line item |
| `LINE_ITEM_ENVIRONMENT_TYPE` | Line item environment type code |
| `LINE_ITEM_ENVIRONMENT_TYPE_NAME` | Line item environment type localized name |
| `LINE_ITEM_COMPANION_DELIVERY_OPTION` | Line item companion delivery option code |
| `LINE_ITEM_COMPANION_DELIVERY_OPTION_NAME` | Line item companion delivery option localized name |
| `LINE_ITEM_LAST_MODIFIED_BY_APP` | The application that last modified the Line Item |
| `LINE_ITEM_NON_CPD_BOOKED_REVENUE` | The cost of booking for the Line item (non-CPD) |
| `LINE_ITEM_DISCOUNT_ABSOLUTE` | The discount of the LineItem in whole units |
| `LINE_ITEM_DISCOUNT_PERCENTAGE` | The discount of the LineItem in percentage |
| `LINE_ITEM_PRIMARY_GOAL_UNITS_ABSOLUTE` | Total impressions/clicks reserved for a line item |
| `LINE_ITEM_PRIMARY_GOAL_UNITS_PERCENTAGE` | Percentage of impressions/clicks reserved |

### Order Dimensions
| Dimension | Description |
|-----------|-------------|
| `ORDER_ID` | Order identifier |
| `ORDER_NAME` | Order name |
| `ORDER_DELIVERY_STATUS` | Order delivery status |
| `ORDER_START_DATE_TIME` | Order start date and time |
| `ORDER_END_DATE_TIME` | Order end date and time |
| `ORDER_EXTERNAL_ID` | Order external ID |
| `ORDER_PO_NUMBER` | Order PO number |
| `ORDER_IS_PROGRAMMATIC` | Whether the order is programmatic |
| `ORDER_AGENCY` | Order agency name |
| `ORDER_AGENCY_ID` | Order agency ID |
| `ORDER_LABELS` | Order labels |
| `ORDER_LABEL_IDS` | Order label IDs |
| `ORDER_TRAFFICKER` | Order trafficker name |
| `ORDER_TRAFFICKER_ID` | Order trafficker ID |
| `ORDER_SECONDARY_TRAFFICKERS` | Order secondary traffickers |
| `ORDER_SALESPERSON` | Order salesperson |
| `ORDER_SECONDARY_SALESPEOPLE` | Order secondary salespeople |
| `ORDER_LIFETIME_IMPRESSIONS` | Order lifetime impressions |
| `ORDER_LIFETIME_CLICKS` | Order lifetime clicks |

### Creative Dimensions
| Dimension | Description |
|-----------|-------------|
| `CREATIVE_ID` | The ID of a creative |
| `CREATIVE_NAME` | Creative name |
| `CREATIVE_TYPE` | Creative type code |
| `CREATIVE_TYPE_NAME` | Creative type localized name |
| `CREATIVE_BILLING_TYPE` | Creative billing type code |
| `CREATIVE_BILLING_TYPE_NAME` | Creative billing type localized name |
| `CREATIVE_CLICK_THROUGH_URL` | The click-through URL of a creative |
| `CREATIVE_THIRD_PARTY_VENDOR` | Third party vendor name of a creative |
| `CREATIVE_TECHNOLOGY` | Creative technology code |
| `CREATIVE_TECHNOLOGY_NAME` | Creative technology localized name |
| `CREATIVE_POLICIES_FILTERING` | Creative Policies filtering code |
| `CREATIVE_POLICIES_FILTERING_NAME` | Creative Policies filtering localized name |
| `CREATIVE_SET_ROLE_TYPE` | Whether the creative is part of a creative set |
| `CREATIVE_SET_ROLE_TYPE_NAME` | Localized name for creative set role |
| `CREATIVE_VIDEO_REDIRECT_THIRD_PARTY` | The third party where GAM was redirected |

### Geographic Dimensions
| Dimension | Description |
|-----------|-------------|
| `COUNTRY_ID` | The criteria ID of the country |
| `COUNTRY_NAME` | The name of the country |
| `COUNTRY_CODE` | The ISO code of the country |
| `CONTINENT` | The continent (derived from country) |
| `CONTINENT_NAME` | The name of the continent |
| `CITY_ID` | The criteria ID of the city |
| `CITY_NAME` | The name of the city |

### Device Dimensions
| Dimension | Description |
|-----------|-------------|
| `DEVICE` | The device on which an ad was served |
| `DEVICE_NAME` | The localized name of the device |
| `DEVICE_CATEGORY` | The device category (smartphone, tablet, desktop) |
| `DEVICE_CATEGORY_NAME` | The name of the device category |
| `DEVICE_MANUFACTURER_ID` | Device manufacturer identifier |
| `DEVICE_MANUFACTURER_NAME` | Device manufacturer localized name |
| `DEVICE_MODEL_ID` | Device model identifier |
| `DEVICE_MODEL_NAME` | Device model localized name |

### Browser Dimensions
| Dimension | Description |
|-----------|-------------|
| `BROWSER_ID` | The ID of the browser |
| `BROWSER_NAME` | The name of the browser |
| `BROWSER_CATEGORY` | Browser category code |
| `BROWSER_CATEGORY_NAME` | Browser category localized name |

### Carrier Dimensions
| Dimension | Description |
|-----------|-------------|
| `CARRIER_ID` | Mobile carrier identifier |
| `CARRIER_NAME` | Name of the mobile carrier |

### Audience & User Dimensions
| Dimension | Description |
|-----------|-------------|
| `AGE_BRACKET` | User age bracket code from Google Analytics |
| `AGE_BRACKET_NAME` | Localized user age bracket (e.g., '18-24', '25-34') |
| `GENDER` | User gender code from Google Analytics |
| `GENDER_NAME` | Localized user gender (e.g., 'male', 'female') |
| `INTEREST` | User interest from Google Analytics |
| `AUDIENCE_SEGMENT_ID_TARGETED` | ID of targeted audience segment |
| `AUDIENCE_SEGMENT_TARGETED` | Name of targeted audience segment |

### Deal Dimensions
| Dimension | Description |
|-----------|-------------|
| `DEAL_ID` | Deal identifier |
| `DEAL_NAME` | Deal name |
| `DEAL_BUYER_ID` | The ID of the buyer of a deal |
| `DEAL_BUYER_NAME` | The name of the buyer of a deal |
| `EXCHANGE_BIDDING_DEAL_ID` | Exchange bidding deal identifier |
| `EXCHANGE_BIDDING_DEAL_TYPE` | Exchange bidding deal type code |
| `EXCHANGE_BIDDING_DEAL_TYPE_NAME` | Exchange bidding deal type localized name |
| `AUCTION_PACKAGE_DEAL` | The name of Auction Package deal |
| `AUCTION_PACKAGE_DEAL_ID` | The ID of Auction Package deal |

### Demand & Channel Dimensions
| Dimension | Description |
|-----------|-------------|
| `DEMAND_CHANNEL` | Demand channel code |
| `DEMAND_CHANNEL_NAME` | Demand channel localized name |
| `DEMAND_SOURCE` | Demand source code |
| `DEMAND_SOURCE_NAME` | Demand source localized name |
| `DEMAND_SUBCHANNEL` | Demand subchannel code |
| `DEMAND_SUBCHANNEL_NAME` | Demand subchannel localized name |
| `CHANNEL` | Inventory segmentation by channel |

### Bidding Dimensions
| Dimension | Description |
|-----------|-------------|
| `BIDDER_ENCRYPTED_ID` | The encrypted version of BIDDER_ID |
| `BIDDER_NAME` | The name of the bidder |
| `BID_RANGE` | The CPM range within which a bid falls |
| `BID_REJECTION_REASON` | Bid rejection reason code |
| `BID_REJECTION_REASON_NAME` | Localized name of the reason a bid was rejected |
| `HEADER_BIDDER_INTEGRATION_TYPE` | Header Bidder integration type code |
| `HEADER_BIDDER_INTEGRATION_TYPE_NAME` | Header Bidder integration type localized name |
| `BUYER_NETWORK_ID` | The ID of the buyer network |
| `BUYER_NETWORK_NAME` | The name of the buyer network |

### Inventory Dimensions
| Dimension | Description |
|-----------|-------------|
| `INVENTORY_TYPE` | The kind of web page or device where the ad was requested |
| `INVENTORY_TYPE_NAME` | Inventory type localized name |
| `INVENTORY_FORMAT` | The format of the ad unit (e.g., banner) |
| `INVENTORY_FORMAT_NAME` | Inventory format localized name |
| `AD_LOCATION` | Whether inventory was above (ATF) or below the fold (BTF) |
| `AD_LOCATION_NAME` | Localized string for above/below fold |

### Content Dimensions
| Dimension | Description |
|-----------|-------------|
| `CONTENT_ID` | ID of the video content served |
| `CONTENT_NAME` | Name of the video content served |
| `CONTENT_CMS_NAME` | The display name of the CMS content |
| `CONTENT_CMS_VIDEO_ID` | The CMS content ID of the video content |
| `CONTENT_MAPPING_PRESENCE` | Content mapping presence code |
| `CONTENT_MAPPING_PRESENCE_NAME` | Content mapping presence localized name |

### Ad Type Dimensions
| Dimension | Description |
|-----------|-------------|
| `AD_TYPE` | Ad type segmentation code |
| `AD_TYPE_NAME` | Ad type localized name |
| `AD_EXPERIENCES_TYPE` | Ad experiences type code |
| `AD_EXPERIENCES_TYPE_NAME` | Ad experiences type localized name |

### Programmatic Dimensions
| Dimension | Description |
|-----------|-------------|
| `ADX_PRODUCT` | Classification of different Ad Exchange products |
| `ADX_PRODUCT_NAME` | Localized Ad Exchange product name |
| `BRANDING_TYPE` | Amount of information about Publisher's page sent to buyer |
| `BRANDING_TYPE_NAME` | Localized branding type |
| `DYNAMIC_ALLOCATION_TYPE` | Inventory sources based on AdX dynamic allocation backfill type |
| `DYNAMIC_ALLOCATION_TYPE_NAME` | Dynamic allocation type localized name |
| `IS_ADX_DIRECT` | Whether traffic is AdX Direct |
| `IS_FIRST_LOOK_DEAL` | Whether traffic is First Look |

### Yield & Exchange Dimensions
| Dimension | Description |
|-----------|-------------|
| `EXCHANGE_THIRD_PARTY_COMPANY_ID` | ID of the yield partner as classified by Google |
| `EXCHANGE_THIRD_PARTY_COMPANY_NAME` | Name of the yield partner |
| `HBT_YIELD_PARTNER_ID` | The ID of the header bidding trafficking yield partner |
| `HBT_YIELD_PARTNER_NAME` | The name of the header bidding trafficking yield partner |
| `CURATOR_ID` | The ID of a Curation partner |
| `CURATOR_NAME` | The name of a Curation partner |
| `IS_CURATION_TARGETED` | If curation was targeted by the buyer |

### Custom Targeting Dimensions
| Dimension | Description |
|-----------|-------------|
| `KEY_VALUES_ID` | The Custom Targeting Value ID |
| `KEY_VALUES_NAME` | Custom Targeting formatted as `{keyName}={valueName}` |
| `CUSTOM_SPOT_ID` | The ID of an ad spot |
| `CUSTOM_SPOT_NAME` | The name of an ad spot |

### Active View Dimensions
| Dimension | Description |
|-----------|-------------|
| `ACTIVE_VIEW_MEASUREMENT_SOURCE` | The measurement source of a video ad |
| `ACTIVE_VIEW_MEASUREMENT_SOURCE_NAME` | Active View measurement source localized name |

### Ad Technology Provider Dimensions
| Dimension | Description |
|-----------|-------------|
| `AD_TECHNOLOGY_PROVIDER_ID` | The ID of the ad technology provider |
| `AD_TECHNOLOGY_PROVIDER_NAME` | The name of the ad technology provider |
| `AD_TECHNOLOGY_PROVIDER_DOMAIN` | The domain of the ad technology provider |

### Child Network Dimensions (MCM)
| Dimension | Description |
|-----------|-------------|
| `CHILD_NETWORK_CODE` | Child Publisher Network Code |
| `CHILD_NETWORK_ID` | Child Publisher Network Identifier |
| `CHILD_PARTNER_NAME` | Child Partner Network Name |

### Privacy & Consent Dimensions
| Dimension | Description |
|-----------|-------------|
| `APP_TRACKING_TRANSPARENCY_CONSENT_STATUS` | ATT consent code |
| `APP_TRACKING_TRANSPARENCY_CONSENT_STATUS_NAME` | ATT consent localized name |
| `FIRST_PARTY_ID_STATUS` | Whether a first-party user ID was present |
| `FIRST_PARTY_ID_STATUS_NAME` | Localized first-party ID status |

### Agency Dimensions
| Dimension | Description |
|-----------|-------------|
| `AGENCY_LEVEL_1_ID` through `AGENCY_LEVEL_3_ID` | Agency IDs at hierarchy levels |
| `AGENCY_LEVEL_1_NAME` through `AGENCY_LEVEL_3_NAME` | Agency names at hierarchy levels |

### Classified Dimensions
| Dimension | Description |
|-----------|-------------|
| `CLASSIFIED_ADVERTISER_ID` | ID of an advertiser, classified by Google |
| `CLASSIFIED_ADVERTISER_NAME` | Name of an advertiser, classified by Google |
| `CLASSIFIED_BRAND_ID` | ID of the brand, as classified by Google |
| `CLASSIFIED_BRAND_NAME` | Name of the brand, as classified by Google |

### Miscellaneous Dimensions
| Dimension | Description |
|-----------|-------------|
| `APP_VERSION` | The app version |
| `AUTO_REFRESHED_TRAFFIC` | Auto refreshed traffic code |
| `AUTO_REFRESHED_TRAFFIC_NAME` | Indicates if traffic is from auto-refreshed requests |
| `DSP_SEAT_ID` | The ID of DSP Seat |
| `IMPRESSION_COUNTING_METHOD` | Impression Counting Method code |
| `IMPRESSION_COUNTING_METHOD_NAME` | Impression Counting Method localized name |
| `INTERACTION_TYPE` | Interaction type code |
| `INTERACTION_TYPE_NAME` | Interaction type localized name |
| `GOOGLE_ANALYTICS_STREAM_ID` | The ID of a Google Analytics stream |
| `GOOGLE_ANALYTICS_STREAM_NAME` | The name of a Google Analytics stream |
| `FIRST_LOOK_PRICING_RULE_ID` | The ID of the first look pricing rule |
| `FIRST_LOOK_PRICING_RULE_NAME` | The name of the first look pricing rule |

---

## Metric Enum (Complete List)

> **Note:** Metrics are organized by category. Some metrics may be deprecated - check Google's official documentation for current status.

### Core Ad Server Metrics
| Metric | Description |
|--------|-------------|
| `AD_SERVER_IMPRESSIONS` | The number of impressions delivered by the ad server |
| `AD_SERVER_BEGIN_TO_RENDER_IMPRESSIONS` | Begin-to-render impressions from the ad server |
| `AD_SERVER_TARGETED_IMPRESSIONS` | Impressions delivered via explicit custom criteria targeting |
| `AD_SERVER_CLICKS` | The number of clicks delivered by the ad server |
| `AD_SERVER_TARGETED_CLICKS` | Clicks from explicitly targeted custom criteria |
| `AD_SERVER_UNFILTERED_IMPRESSIONS` | Downloaded impressions including spam-recognized ones |
| `AD_SERVER_UNFILTERED_CLICKS` | Clicks including those recognized as spam |
| `AD_SERVER_CTR` | Click-through rate for ad server ads |

### Revenue Metrics
| Metric | Description |
|--------|-------------|
| `AD_SERVER_CPM_AND_CPC_REVENUE` | CPM/CPC revenue in publisher currency |
| `AD_SERVER_CPM_AND_CPC_REVENUE_GROSS` | Gross CPM/CPC including pre-rev-share programmatic revenue |
| `AD_SERVER_CPD_REVENUE` | CPD revenue earned |
| `AD_SERVER_ALL_REVENUE` | Total revenue from all ad server ads |
| `AD_SERVER_ALL_REVENUE_GROSS` | Gross total revenue including pre-rev-share programmatic |
| `AD_SERVER_WITHOUT_CPD_AVERAGE_ECPM` | Average eCPM from CPM/CPC ads |
| `AD_SERVER_WITH_CPD_AVERAGE_ECPM` | Average eCPM from all ads |

### Total/Aggregated Metrics
| Metric | Description |
|--------|-------------|
| `TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS` | Total impressions with dynamic allocation |
| `TOTAL_LINE_ITEM_LEVEL_TARGETED_IMPRESSIONS` | Total targeted impressions |
| `TOTAL_LINE_ITEM_LEVEL_CLICKS` | Total clicks with dynamic allocation |
| `TOTAL_LINE_ITEM_LEVEL_TARGETED_CLICKS` | Total targeted clicks |
| `TOTAL_LINE_ITEM_LEVEL_CTR` | Overall click-through rate |
| `TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE` | Total CPM/CPC revenue |
| `TOTAL_LINE_ITEM_LEVEL_ALL_REVENUE` | The total CPM, CPC and CPD revenue generated |
| `TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM` | eCPM for CPM/CPC ads |
| `TOTAL_LINE_ITEM_LEVEL_WITH_CPD_AVERAGE_ECPM` | eCPM for all revenue types |
| `TOTAL_CODE_SERVED_COUNT` | Total code served by ad server |
| `TOTAL_AD_REQUESTS` | The total number of times that an ad request is sent |
| `TOTAL_RESPONSES_SERVED` | The total number of times that an ad is served |
| `TOTAL_UNMATCHED_AD_REQUESTS` | The total number of times that an ad is not returned |
| `TOTAL_FILL_RATE` | The fill rate indicating how often an ad request is filled |
| `TOTAL_INVENTORY_LEVEL_UNFILLED_IMPRESSIONS` | Missed impressions due to no available ads |

### AdSense Metrics
| Metric | Description |
|--------|-------------|
| `ADSENSE_LINE_ITEM_LEVEL_IMPRESSIONS` | AdSense impressions for dynamic allocation |
| `ADSENSE_LINE_ITEM_LEVEL_CLICKS` | AdSense clicks for dynamic allocation |
| `ADSENSE_LINE_ITEM_LEVEL_CTR` | The ratio of clicks to impressions |
| `ADSENSE_LINE_ITEM_LEVEL_REVENUE` | Revenue from AdSense dynamic allocation |
| `ADSENSE_LINE_ITEM_LEVEL_AVERAGE_ECPM` | Average eCPM from AdSense ads |
| `ADSENSE_LINE_ITEM_LEVEL_PERCENT_IMPRESSIONS` | AdSense impression percentage |
| `ADSENSE_LINE_ITEM_LEVEL_PERCENT_CLICKS` | AdSense click percentage |
| `ADSENSE_LINE_ITEM_LEVEL_WITHOUT_CPD_PERCENT_REVENUE` | AdSense CPM/CPC revenue percentage |
| `ADSENSE_LINE_ITEM_LEVEL_WITH_CPD_PERCENT_REVENUE` | AdSense total revenue percentage |
| `ADSENSE_RESPONSES_SERVED` | AdSense ad delivery count |

### Ad Exchange Metrics
| Metric | Description |
|--------|-------------|
| `AD_EXCHANGE_LINE_ITEM_LEVEL_IMPRESSIONS` | Ad Exchange impressions |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_CLICKS` | Ad Exchange clicks |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_CTR` | Click-to-impression ratio for Ad Exchange |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_REVENUE` | Revenue from Ad Exchange |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_AVERAGE_ECPM` | Average eCPM from Ad Exchange |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_PERCENT_IMPRESSIONS` | Ad Exchange impression percentage |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_PERCENT_CLICKS` | Ad Exchange click percentage |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_WITHOUT_CPD_PERCENT_REVENUE` | Ad Exchange CPM/CPC revenue percentage |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_WITH_CPD_PERCENT_REVENUE` | Ad Exchange total revenue percentage |
| `AD_EXCHANGE_TOTAL_REQUESTS` | Total queries sent to Ad Exchange |
| `AD_EXCHANGE_MATCH_RATE` | Query match rate (coverage) |
| `AD_EXCHANGE_COST_PER_CLICK` | Amount earned per Ad Exchange click |
| `AD_EXCHANGE_TOTAL_REQUEST_CTR` | Ad Exchange request click-through fraction |
| `AD_EXCHANGE_MATCHED_REQUEST_CTR` | Matched request click-through fraction |
| `AD_EXCHANGE_TOTAL_REQUEST_ECPM` | Amount earned per thousand Ad Exchange requests |
| `AD_EXCHANGE_MATCHED_REQUEST_ECPM` | Amount per thousand matched Ad Exchange requests |
| `AD_EXCHANGE_LIFT_EARNINGS` | Incremental revenue from won impressions vs. minimum CPM |
| `AD_EXCHANGE_RESPONSES_SERVED` | Ad Exchange ad delivery count |

### Bidding & Yield Metrics
| Metric | Description |
|--------|-------------|
| `BID_COUNT` | The number of bids associated with the selected dimensions |
| `BID_AVERAGE_CPM` | Average CPM per bid |
| `YIELD_GROUP_CALLOUTS` | Yield partner requests for bids (Open Bidding) |
| `YIELD_GROUP_SUCCESSFUL_RESPONSES` | Successful bid responses from yield partners |
| `YIELD_GROUP_BIDS` | Number of bids received from Open Bidding buyers |
| `YIELD_GROUP_BIDS_IN_AUCTION` | Bids competing in auction |
| `YIELD_GROUP_AUCTIONS_WON` | Winning bids from Open Bidding buyers |
| `YIELD_GROUP_IMPRESSIONS` | Matched yield group requests served |
| `YIELD_GROUP_ESTIMATED_REVENUE` | Net revenue from yield groups |
| `YIELD_GROUP_ESTIMATED_CPM` | Net rate for yield group partners |
| `YIELD_GROUP_MEDIATION_FILL_RATE` | Network fill rate for mediation |
| `YIELD_GROUP_MEDIATION_PASSBACKS` | Count of ad network passbacks |
| `YIELD_GROUP_MEDIATION_THIRD_PARTY_ECPM` | Third-party eCPM from network reports |
| `YIELD_GROUP_MEDIATION_CHAINS_SERVED` | Mediation chains served count |
| `MEDIATION_THIRD_PARTY_ECPM` | Mediation average eCPM |

### Programmatic Deals Metrics
| Metric | Description |
|--------|-------------|
| `DEALS_BID_REQUESTS` | Bid requests per deal |
| `DEALS_BIDS` | Bids placed on each deal |
| `DEALS_BID_RATE` | Bid rate for each deal |
| `DEALS_WINNING_BIDS` | Winning bids per deal |
| `DEALS_WIN_RATE` | Win rate for each deal |
| `PROGRAMMATIC_RESPONSES_SERVED` | Programmatic demand responses (Ad Exchange, Open Bidding) |
| `PROGRAMMATIC_MATCH_RATE` | Programmatic response divided by eligible request rate |
| `TOTAL_PROGRAMMATIC_ELIGIBLE_AD_REQUESTS` | Ad requests eligible for programmatic |

### Active View Metrics
| Metric | Description |
|--------|-------------|
| `TOTAL_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS` | Impressions viewed on-screen |
| `TOTAL_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS` | Impressions measured by Active View |
| `TOTAL_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS_RATE` | Percentage of viewable impressions |
| `TOTAL_ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS` | Impressions eligible for measurement |
| `TOTAL_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS_RATE` | Percentage of measurable impressions |
| `TOTAL_ACTIVE_VIEW_AVERAGE_VIEWABLE_TIME` | Average viewable time in seconds |
| `TOTAL_ACTIVE_VIEW_REVENUE` | Active View total revenue |
| `ACTIVE_VIEW_PERCENT_AUDIBLE_START_IMPRESSIONS` | Audible video at start percentage |
| `ACTIVE_VIEW_PERCENT_EVER_AUDIBLE_IMPRESSIONS` | Ever audible percentage |
| `AD_SERVER_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS` | Ad server on-screen impressions |
| `AD_SERVER_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS` | Ad server measured impressions |
| `AD_SERVER_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS_RATE` | Ad server viewable percentage |
| `AD_SERVER_ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS` | Ad server eligible impressions |
| `AD_SERVER_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS_RATE` | Ad server measurable percentage |
| `AD_SERVER_ACTIVE_VIEW_REVENUE` | Ad server Active View revenue |
| `AD_SERVER_ACTIVE_VIEW_AVERAGE_VIEWABLE_TIME` | Ad server average viewable time |

### Video Viewership Metrics
| Metric | Description |
|--------|-------------|
| `VIDEO_VIEWERSHIP_START` | The number of impressions where the video was played |
| `VIDEO_VIEWERSHIP_FIRST_QUARTILE` | Video played to 25% length |
| `VIDEO_VIEWERSHIP_MIDPOINT` | Video reached midpoint during playback |
| `VIDEO_VIEWERSHIP_THIRD_QUARTILE` | Video played to 75% length |
| `VIDEO_VIEWERSHIP_COMPLETE` | The number of times the video played to completion |
| `VIDEO_VIEWERSHIP_AVERAGE_VIEW_RATE` | Average percentage of video watched |
| `VIDEO_VIEWERSHIP_AVERAGE_VIEW_TIME` | Average time users watched (seconds) |
| `VIDEO_VIEWERSHIP_COMPLETION_RATE` | Percentage of videos played to end |
| `VIDEO_VIEWERSHIP_TOTAL_ERROR_COUNT` | Error occurrences (VAST, playback, etc.) |
| `VIDEO_VIEWERSHIP_VIDEO_LENGTH` | Video creative duration |
| `VIDEO_VIEWERSHIP_SKIP_BUTTON_SHOWN` | Skip button display count |
| `VIDEO_VIEWERSHIP_ENGAGED_VIEW` | Views to completion or 30s (whichever first) |
| `VIDEO_VIEWERSHIP_VIEW_THROUGH_RATE` | View-through rate as a percentage |
| `VIDEO_VIEWERSHIP_AUTO_PLAYS` | Publisher-specified automatic plays |
| `VIDEO_VIEWERSHIP_CLICK_TO_PLAYS` | Publisher-specified click-to-play count |
| `VIDEO_VIEWERSHIP_TOTAL_ERROR_RATE` | Error rate percentage |

### Video Interaction Metrics
| Metric | Description |
|--------|-------------|
| `VIDEO_INTERACTION_PAUSE` | User pause count |
| `VIDEO_INTERACTION_RESUME` | User unpause count |
| `VIDEO_INTERACTION_REWIND` | User rewind count |
| `VIDEO_INTERACTION_MUTE` | Mute state during ad playback |
| `VIDEO_INTERACTION_UNMUTE` | User unmute count |
| `VIDEO_INTERACTION_COLLAPSE` | Video size reduction count |
| `VIDEO_INTERACTION_EXPAND` | Video expansion count |
| `VIDEO_INTERACTION_FULL_SCREEN` | Full screen playback count |
| `VIDEO_INTERACTION_AVERAGE_INTERACTION_RATE` | Average user interactions |
| `VIDEO_INTERACTION_VIDEO_SKIPS` | Skippable video skip count |

### Video Opportunity Metrics
| Metric | Description |
|--------|-------------|
| `TOTAL_VIDEO_OPPORTUNITIES` | The total number of video opportunities |
| `TOTAL_VIDEO_CAPPED_OPPORTUNITIES` | Capped video opportunities |
| `TOTAL_VIDEO_MATCHED_OPPORTUNITIES` | Matched video opportunities |
| `TOTAL_VIDEO_MATCHED_DURATION` | Filled duration in ad breaks (seconds) |
| `TOTAL_VIDEO_DURATION` | The total duration in ad breaks |
| `TOTAL_VIDEO_BREAK_START` | Total break starts |
| `TOTAL_VIDEO_BREAK_END` | Total break ends |

### Rich Media Metrics
| Metric | Description |
|--------|-------------|
| `RICH_MEDIA_BACKUP_IMAGES` | Backup images served instead of rich media |
| `RICH_MEDIA_DISPLAY_TIME` | Display time in seconds for rich media |
| `RICH_MEDIA_AVERAGE_DISPLAY_TIME` | Average display time in seconds |
| `RICH_MEDIA_EXPANSIONS` | The number of times an expanding ad was expanded |
| `RICH_MEDIA_EXPANDING_TIME` | Average time in expanded state (seconds) |
| `RICH_MEDIA_INTERACTION_TIME` | Average user interaction time (seconds) |
| `RICH_MEDIA_INTERACTION_COUNT` | The number of times that a user interacts |
| `RICH_MEDIA_INTERACTION_RATE` | User interaction percentage |
| `RICH_MEDIA_AVERAGE_INTERACTION_TIME` | Average interaction duration (seconds) |
| `RICH_MEDIA_INTERACTION_IMPRESSIONS` | Impressions with user interactions |
| `RICH_MEDIA_MANUAL_CLOSES` | Manual closes of rich media ads |
| `RICH_MEDIA_FULL_SCREEN_IMPRESSIONS` | Impression count for full-screen mode |
| `RICH_MEDIA_VIDEO_INTERACTIONS` | Clicks on video player controls |
| `RICH_MEDIA_VIDEO_INTERACTION_RATE` | Video interaction percentage |
| `RICH_MEDIA_VIDEO_MUTES` | Video mute count |
| `RICH_MEDIA_VIDEO_PAUSES` | Video pause count |
| `RICH_MEDIA_VIDEO_PLAYES` | Video play count |
| `RICH_MEDIA_VIDEO_MIDPOINTS` | Times video reached midpoint |
| `RICH_MEDIA_VIDEO_COMPLETES` | Full video plays |
| `RICH_MEDIA_VIDEO_REPLAYS` | Video restart count |
| `RICH_MEDIA_VIDEO_STOPS` | Video stop count |
| `RICH_MEDIA_VIDEO_UNMUTES` | Video unmute count |
| `RICH_MEDIA_VIDEO_VIEW_TIME` | Average video view time per view (seconds) |
| `RICH_MEDIA_VIDEO_VIEW_RATE` | Percentage of video watched |
| `RICH_MEDIA_CUSTOM_EVENT_TIME` | Time spent on custom event (seconds) |
| `RICH_MEDIA_CUSTOM_EVENT_COUNT` | Custom event interaction count |

### Unique Reach Metrics
| Metric | Description |
|--------|-------------|
| `UNIQUE_REACH_FREQUENCY` | Average impressions per unique visitor |
| `UNIQUE_REACH_IMPRESSIONS` | Total reach impressions |
| `UNIQUE_REACH` | Total unique visitors |

### SDK Mediation Metrics
| Metric | Description |
|--------|-------------|
| `SDK_MEDIATION_CREATIVE_IMPRESSIONS` | Impressions for SDK mediation creative |
| `SDK_MEDIATION_CREATIVE_CLICKS` | Clicks for SDK mediation creative |

### Forecasting Metrics
| Metric | Description |
|--------|-------------|
| `SELL_THROUGH_FORECASTED_IMPRESSIONS` | Forecasted impressions for future reports |
| `SELL_THROUGH_AVAILABLE_IMPRESSIONS` | Available impressions for future reports |
| `SELL_THROUGH_RESERVED_IMPRESSIONS` | Reserved impressions for future reports |
| `SELL_THROUGH_SELL_THROUGH_RATE` | Sell-through rate for future reports |

### Ad Speed Metrics
| Metric | Description |
|--------|-------------|
| `CREATIVE_LOAD_TIME_0_500_MS_PERCENT` | 0-500ms load time percentage |
| `CREATIVE_LOAD_TIME_500_1000_MS_PERCENT` | 500ms-1s load time percentage |
| `CREATIVE_LOAD_TIME_1_2_S_PERCENT` | 1-2 second load time percentage |
| `CREATIVE_LOAD_TIME_2_4_S_PERCENT` | 2-4 second load time percentage |
| `CREATIVE_LOAD_TIME_4_8_S_PERCENT` | 4-8 second load time percentage |
| `CREATIVE_LOAD_TIME_GREATER_THAN_8_S_PERCENT` | Over 8 second load time percentage |
| `UNVIEWED_REASON_SLOT_NEVER_ENTERED_VIEWPORT_PERCENT` | Unviewed due to no viewport entry |
| `UNVIEWED_REASON_USER_SCROLLED_BEFORE_AD_FILLED_PERCENT` | Unviewed due to scroll before fill |
| `UNVIEWED_REASON_USER_SCROLLED_BEFORE_AD_LOADED_PERCENT` | Unviewed due to scroll before load |
| `UNVIEWED_REASON_USER_SCROLLED_BEFORE_1_S_PERCENT` | Unviewed due to scroll before 1 second |
| `UNVIEWED_REASON_OTHER_PERCENT` | Unviewed due to other reasons |

### Invoicing Metrics
| Metric | Description |
|--------|-------------|
| `INVOICED_IMPRESSIONS` | The number of invoiced impressions |
| `INVOICED_UNFILLED_IMPRESSIONS` | Invoiced unfilled impression count |

### Partner Management Metrics
| Metric | Description |
|--------|-------------|
| `PARTNER_MANAGEMENT_HOST_IMPRESSIONS` | Host impressions in partner management |
| `PARTNER_MANAGEMENT_HOST_CLICKS` | Host clicks in partner management |
| `PARTNER_MANAGEMENT_HOST_CTR` | Host click-through rate |
| `PARTNER_MANAGEMENT_UNFILLED_IMPRESSIONS` | Unfilled impressions in management |
| `PARTNER_MANAGEMENT_PARTNER_IMPRESSIONS` | Partner impressions in management |
| `PARTNER_MANAGEMENT_PARTNER_CLICKS` | Partner clicks in management |
| `PARTNER_MANAGEMENT_PARTNER_CTR` | Partner click-through rate |
| `PARTNER_MANAGEMENT_GROSS_REVENUE` | Gross revenue in partner management |

### Ad Connector Metrics
| Metric | Description |
|--------|-------------|
| `DP_IMPRESSIONS` | Number of impressions delivered |
| `DP_CLICKS` | Number of clicks delivered |
| `DP_QUERIES` | Number of requests |
| `DP_MATCHED_QUERIES` | Number of requests where a buyer was matched |
| `DP_COST` | Revenue earned in publisher currency |
| `DP_ECPM` | Average estimated cost-per-thousand-impressions |
| `DP_ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS` | Ad Connector eligible impressions |
| `DP_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS` | Ad Connector measured impressions |
| `DP_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS` | Ad Connector on-screen impressions |
| `DP_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS_RATE` | Ad Connector measurable percentage |
| `DP_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS_RATE` | Ad Connector viewable percentage |

---

## Flag Object

```json
{
  "flagName": enum (FlagName)
}
```

### FlagName Enum Values
- `FLAG_NAME_UNSPECIFIED`
- `ENVIRONMENT_PARTNER_SOLD_WITHOUT_VENDOR_DATA`
- `ENVIRONMENT_PARTNER_SOLD_WITHOUT_THIRD_PARTY_DATA`

## ScheduleOptions Object

Configuration for scheduled/recurring report runs.

```json
{
  "recurrence": enum (Recurrence),
  "startTime": string,
  "frequency": enum (Frequency),
  "endTime": string,
  "dayOfWeek": enum (DayOfWeek),
  "dayOfMonth": integer
}
```

### ScheduleOptions Fields

| Field | Type | Description |
|-------|------|-------------|
| `recurrence` | enum (Recurrence) | Whether the report runs once or repeatedly. |
| `startTime` | string (Timestamp) | When the schedule begins. RFC3339 format. |
| `frequency` | enum (Frequency) | How often the report runs (for REPEATING recurrence). |
| `endTime` | string (Timestamp) | When the schedule ends. Optional. RFC3339 format. |
| `dayOfWeek` | enum (DayOfWeek) | For weekly frequency, which day to run. |
| `dayOfMonth` | integer | For monthly frequency, which day of month to run (1-31). |

### Recurrence Enum Values
| Value | Description |
|-------|-------------|
| `RECURRENCE_UNSPECIFIED` | Not specified |
| `ONE_TIME` | Report runs only once |
| `REPEATING` | Report runs on a recurring schedule |

### Frequency Enum Values
| Value | Description |
|-------|-------------|
| `FREQUENCY_UNSPECIFIED` | Not specified |
| `DAILY` | Report runs daily |
| `WEEKLY` | Report runs weekly on specified day |
| `MONTHLY` | Report runs monthly on specified day |

### DayOfWeek Enum Values
- `DAY_OF_WEEK_UNSPECIFIED`
- `MONDAY`
- `TUESDAY`
- `WEDNESDAY`
- `THURSDAY`
- `FRIDAY`
- `SATURDAY`
- `SUNDAY`

## Methods

### 1. create
`POST https://admanager.googleapis.com/v1/{parent=networks/*}/reports`

Creates a report.

### 2. get
`GET https://admanager.googleapis.com/v1/{name=networks/*/reports/*}`

Gets a report.

### 3. list
`GET https://admanager.googleapis.com/v1/{parent=networks/*}/reports`

Lists reports.

Query parameters:
- `pageSize` (integer): Maximum number of results to return
- `pageToken` (string): Page token from previous list call
- `filter` (string): Filter expression
- `orderBy` (string): Sort order

### 4. patch
`PATCH https://admanager.googleapis.com/v1/{report.name=networks/*/reports/*}`

Updates a report.

Query parameters:
- `updateMask` (string): Field mask indicating fields to update

### 5. run
`POST https://admanager.googleapis.com/v1/{name=networks/*/reports/*}:run`

Runs a report asynchronously. Returns an Operation object.

**Response:**
```json
{
  "name": "networks/{networkCode}/operations/reports/runs/{operationId}",
  "done": false
}
```

### 6. fetchRows (Report Results)
`GET https://admanager.googleapis.com/v1/{name=networks/*/reports/*/results}:fetchRows`

Retrieves completed report data rows.

**Query Parameters:**
- `pageSize` (integer): Maximum rows to return (default: 1000, max: 10000)
- `pageToken` (string): Page token from previous call

**Response:**
```json
{
  "rows": [
    {
      "dimensionValues": {
        "DATE": { "stringValue": "2025-01-15" },
        "AD_UNIT_NAME": { "stringValue": "Homepage Banner" }
      },
      "metricValueGroups": [
        {
          "primaryValues": {
            "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS": { "integerValue": "15000" },
            "TOTAL_LINE_ITEM_LEVEL_CLICKS": { "integerValue": "150" }
          },
          "comparisonValues": {
            "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS": { "integerValue": "12000" },
            "TOTAL_LINE_ITEM_LEVEL_CLICKS": { "integerValue": "120" }
          },
          "compareToBaselinePrimaryValues": {
            "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS": { "percentageChange": "25.0" },
            "TOTAL_LINE_ITEM_LEVEL_CLICKS": { "percentageChange": "25.0" }
          },
          "compareToBaselineComparisonValues": {
            "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS": { "absoluteChange": "3000" },
            "TOTAL_LINE_ITEM_LEVEL_CLICKS": { "absoluteChange": "30" }
          },
          "flagValues": {
            "FLAG_NAME": { "boolValue": true }
          }
        }
      ]
    }
  ],
  "nextPageToken": "...",
  "totalRowCount": 1500,
  "runTime": "2025-01-15T10:30:00Z",
  "dateRanges": [
    {
      "fixed": {
        "startDate": { "year": 2025, "month": 1, "day": 1 },
        "endDate": { "year": 2025, "month": 1, "day": 31 }
      }
    }
  ]
}
```

## MetricValueGroup Object

When a report includes comparison date ranges or time period columns, metric values are organized in groups.

```json
{
  "primaryValues": {
    "METRIC_NAME": { object (MetricValue) }
  },
  "comparisonValues": {
    "METRIC_NAME": { object (MetricValue) }
  },
  "compareToBaselinePrimaryValues": {
    "METRIC_NAME": { object (ComparisonValue) }
  },
  "compareToBaselineComparisonValues": {
    "METRIC_NAME": { object (ComparisonValue) }
  },
  "flagValues": {
    "FLAG_NAME": { object (FlagValue) }
  }
}
```

### MetricValueGroup Fields

| Field | Type | Description |
|-------|------|-------------|
| `primaryValues` | map<string, MetricValue> | Metric values for the primary date range. |
| `comparisonValues` | map<string, MetricValue> | Metric values for the comparison date range (if `compareDateRange` specified). |
| `compareToBaselinePrimaryValues` | map<string, ComparisonValue> | Comparison metrics showing change from baseline for primary values. |
| `compareToBaselineComparisonValues` | map<string, ComparisonValue> | Comparison metrics showing change from baseline for comparison values. |
| `flagValues` | map<string, FlagValue> | Flag metric values (boolean indicators). |

## MetricValue Object

```json
{
  // Union field - one of:
  "integerValue": string,      // For count metrics (impressions, clicks)
  "decimalValue": string,      // For rate/ratio metrics (CTR, fill rate)
  "micros": string            // For currency values (revenue in micros, divide by 1,000,000)
}
```

## ComparisonValue Object

Represents the change between two values (primary vs baseline or comparison vs baseline).

```json
{
  // Union field - one of:
  "percentageChange": string,   // Percentage change (e.g., "25.5" = 25.5% increase)
  "absoluteChange": string      // Absolute numeric change
}
```

## FlagValue Object

```json
{
  "boolValue": boolean
}
```

---

## Operations API (Report Execution)

### Get Operation Status
`GET https://admanager.googleapis.com/v1/{name=networks/*/operations/reports/runs/*}`

Poll this endpoint to check if a report run has completed.

**Response (In Progress):**
```json
{
  "name": "networks/21842055933/operations/reports/runs/abc123",
  "done": false
}
```

**Response (Completed):**
```json
{
  "name": "networks/21842055933/operations/reports/runs/abc123",
  "done": true,
  "response": {
    "@type": "type.googleapis.com/google.ads.admanager.v1.RunReportResponse",
    "reportResult": "networks/21842055933/reports/456789/results/xyz789"
  }
}
```

**Response (Failed):**
```json
{
  "name": "networks/21842055933/operations/reports/runs/abc123",
  "done": true,
  "error": {
    "code": 3,
    "message": "Report execution failed: Invalid dimension combination"
  }
}
```

### Cancel Operation
`POST https://admanager.googleapis.com/v1/{name}:cancel`

Cancels a long-running report operation.

### Delete Operation
`DELETE https://admanager.googleapis.com/v1/{name}`

Deletes a completed operation.

---

## Complete Report Workflow

```
1. CREATE REPORT
   POST /v1/networks/{networkCode}/reports
   → Returns: Report resource with name

2. RUN REPORT
   POST /v1/{reportName}:run
   → Returns: Operation with name

3. POLL OPERATION (until done=true)
   GET /v1/{operationName}
   → Returns: Operation with done status

4. FETCH RESULTS (when done=true)
   GET /v1/{reportResult}:fetchRows
   → Returns: Report data rows (paginated)
```

**Python Example:**
```python
import time
import requests

# 1. Create report
report = session.post(f"{BASE_URL}/networks/{NETWORK_CODE}/reports", json=report_definition)
report_name = report.json()["name"]

# 2. Run report
operation = session.post(f"{BASE_URL}/{report_name}:run")
operation_name = operation.json()["name"]

# 3. Poll until complete
while True:
    status = session.get(f"{BASE_URL}/{operation_name}").json()
    if status.get("done"):
        if "error" in status:
            raise Exception(status["error"]["message"])
        result_name = status["response"]["reportResult"]
        break
    time.sleep(5)  # Poll every 5 seconds

# 4. Fetch rows
rows = []
page_token = None
while True:
    params = {"pageSize": 10000}
    if page_token:
        params["pageToken"] = page_token
    response = session.get(f"{BASE_URL}/{result_name}:fetchRows", params=params).json()
    rows.extend(response.get("rows", []))
    page_token = response.get("nextPageToken")
    if not page_token:
        break
```

---

## Example: Complete Report Request

```json
{
  "displayName": "Q2 2025 Revenue Analysis",
  "locale": "en-US",
  "reportDefinition": {
    "reportType": "HISTORICAL",
    "dimensions": [
      "DATE",
      "AD_UNIT_NAME",
      "ADVERTISER_NAME",
      "ORDER_NAME"
    ],
    "metrics": [
      "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS",
      "TOTAL_LINE_ITEM_LEVEL_CLICKS",
      "TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE"
    ],
    "dateRange": {
      "fixed": {
        "startDate": {
          "year": 2025,
          "month": 4,
          "day": 1
        },
        "endDate": {
          "year": 2025,
          "month": 6,
          "day": 30
        }
      }
    },
    "compareDateRange": {
      "fixed": {
        "startDate": {
          "year": 2025,
          "month": 1,
          "day": 1
        },
        "endDate": {
          "year": 2025,
          "month": 3,
          "day": 31
        }
      }
    },
    "filters": [
      {
        "stringValue": {
          "values": ["Premium Advertiser", "Gold Advertiser"],
          "matchType": "EXACT"
        }
      }
    ],
    "timeZone": "America/New_York",
    "currencyCode": "USD",
    "timePeriodColumn": "TIME_PERIOD_COLUMN_WEEK",
    "localizationSettings": {
      "locale": "en-US",
      "languageCode": "en",
      "timeZone": "America/New_York"
    }
  },
  "scheduleOptions": {
    "recurrence": "REPEATING",
    "startTime": "2025-07-01T00:00:00Z"
  }
}
```

## Example: Using Relative Date Range

```json
{
  "displayName": "Last 30 Days Performance",
  "reportDefinition": {
    "reportType": "HISTORICAL",
    "dimensions": ["DATE", "AD_UNIT_NAME"],
    "metrics": ["TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS"],
    "dateRange": {
      "relative": {
        "relativePreset": "LAST_30_DAYS"
      }
    }
  }
}
```

## Example: Report with Filters

```json
{
  "displayName": "Mobile Traffic Report",
  "reportDefinition": {
    "reportType": "HISTORICAL",
    "dimensions": ["DATE", "DEVICE_CATEGORY_NAME"],
    "metrics": ["TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS", "TOTAL_LINE_ITEM_LEVEL_CLICKS"],
    "dateRange": {
      "relative": {
        "relativePreset": "THIS_MONTH"
      }
    },
    "filters": [
      {
        "stringValue": {
          "values": ["Mobile", "Tablet"],
          "matchType": "EXACT"
        }
      },
      {
        "intValue": {
          "values": ["1000"],
          "operation": "GREATER_THAN"
        }
      }
    ]
  }
}
```

## Response Format

### Success Response
```json
{
  "name": "networks/21842055933/reports/123456789",
  "reportId": "123456789",
  "displayName": "Q2 2025 Revenue Analysis",
  "updateTime": "2025-06-22T20:00:00Z",
  "createTime": "2025-06-22T20:00:00Z",
  "locale": "en-US",
  "reportDefinition": {
    // ... your report definition
  }
}
```

### Error Response
```json
{
  "error": {
    "code": 400,
    "message": "Invalid dimension: INVALID_DIMENSION",
    "status": "INVALID_ARGUMENT",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.BadRequest",
        "fieldViolations": [
          {
            "field": "report_definition.dimensions",
            "description": "Dimension 'INVALID_DIMENSION' is not valid"
          }
        ]
      }
    ]
  }
}
```

## Notes

1. The API is in Beta and subject to change
2. All timestamps are in RFC3339 format
3. Currency codes follow ISO 4217 standard
4. Time zones follow IANA Time Zone Database names
5. Pagination is supported for list operations
6. Filtering supports complex expressions using Google's AIP-160 standard

---

## CustomTargetingValues Resource

Separate REST resource for managing custom targeting key values, used with the `KEY_VALUES` dimension.

**Base URL:** `https://admanager.googleapis.com/v1/networks/{networkCode}/customTargetingKeys/{keyId}/customTargetingValues`

### Resource Representation

```json
{
  "name": string,
  "adTagName": string,
  "displayName": string,
  "matchType": enum (MatchType),
  "status": enum (Status)
}
```

### CustomTargetingValue Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Resource name. Format: `networks/{networkCode}/customTargetingKeys/{keyId}/customTargetingValues/{valueId}` |
| `adTagName` | string | Required. The ad tag name used in targeting. Must be unique within the key. |
| `displayName` | string | The display name of the custom targeting value. |
| `matchType` | enum (MatchType) | How this value matches requests (EXACT, BROAD, PREFIX, etc.) |
| `status` | enum (Status) | The status of the custom targeting value. |

### MatchType Enum (CustomTargeting)

| Value | Description |
|-------|-------------|
| `MATCH_TYPE_UNSPECIFIED` | Not specified |
| `EXACT` | Exact match required |
| `BROAD` | Broad match (includes variations) |
| `PREFIX` | Matches values starting with this prefix |
| `BROAD_PREFIX` | Combination of broad and prefix matching |
| `SUFFIX` | Matches values ending with this suffix |
| `CONTAINS` | Matches values containing this string |

### Status Enum (CustomTargeting)

| Value | Description |
|-------|-------------|
| `STATUS_UNSPECIFIED` | Not specified |
| `ACTIVE` | The custom targeting value is active and can be used |
| `INACTIVE` | The custom targeting value is inactive |

### Methods

#### list
`GET https://admanager.googleapis.com/v1/{parent=networks/*/customTargetingKeys/*}/customTargetingValues`

Lists custom targeting values.

**Query Parameters:**
- `pageSize` (integer): Maximum results to return (default: 50, max: 1000)
- `pageToken` (string): Page token from previous call
- `filter` (string): AIP-160 filter expression
- `orderBy` (string): Sort order

**Response:**
```json
{
  "customTargetingValues": [
    {
      "name": "networks/123/customTargetingKeys/456/customTargetingValues/789",
      "adTagName": "sports",
      "displayName": "Sports Section",
      "matchType": "EXACT",
      "status": "ACTIVE"
    }
  ],
  "nextPageToken": "...",
  "totalSize": 150
}
```

#### get
`GET https://admanager.googleapis.com/v1/{name=networks/*/customTargetingKeys/*/customTargetingValues/*}`

Gets a single custom targeting value.

---

## Supported Time Zones

The `timeZone` field in ReportDefinition accepts IANA Time Zone Database identifiers. Common values:

### North America
| Time Zone | Description |
|-----------|-------------|
| `America/New_York` | Eastern Time (US & Canada) |
| `America/Chicago` | Central Time (US & Canada) |
| `America/Denver` | Mountain Time (US & Canada) |
| `America/Los_Angeles` | Pacific Time (US & Canada) |
| `America/Anchorage` | Alaska Time |
| `America/Phoenix` | Arizona (no DST) |
| `America/Toronto` | Eastern Time (Canada) |
| `America/Vancouver` | Pacific Time (Canada) |
| `America/Mexico_City` | Central Time (Mexico) |

### Europe
| Time Zone | Description |
|-----------|-------------|
| `Europe/London` | UK Time (GMT/BST) |
| `Europe/Paris` | Central European Time |
| `Europe/Berlin` | Central European Time |
| `Europe/Madrid` | Central European Time |
| `Europe/Rome` | Central European Time |
| `Europe/Amsterdam` | Central European Time |
| `Europe/Brussels` | Central European Time |
| `Europe/Zurich` | Central European Time |
| `Europe/Vienna` | Central European Time |
| `Europe/Stockholm` | Central European Time |
| `Europe/Warsaw` | Central European Time |
| `Europe/Prague` | Central European Time |
| `Europe/Athens` | Eastern European Time |
| `Europe/Helsinki` | Eastern European Time |
| `Europe/Moscow` | Moscow Time |
| `Europe/Istanbul` | Turkey Time |

### Asia Pacific
| Time Zone | Description |
|-----------|-------------|
| `Asia/Tokyo` | Japan Standard Time |
| `Asia/Seoul` | Korea Standard Time |
| `Asia/Shanghai` | China Standard Time |
| `Asia/Hong_Kong` | Hong Kong Time |
| `Asia/Singapore` | Singapore Time |
| `Asia/Taipei` | Taiwan Time |
| `Asia/Manila` | Philippines Time |
| `Asia/Bangkok` | Indochina Time |
| `Asia/Jakarta` | Western Indonesia Time |
| `Asia/Kolkata` | India Standard Time |
| `Asia/Mumbai` | India Standard Time |
| `Asia/Dubai` | Gulf Standard Time |
| `Asia/Karachi` | Pakistan Standard Time |
| `Australia/Sydney` | Australian Eastern Time |
| `Australia/Melbourne` | Australian Eastern Time |
| `Australia/Brisbane` | Australian Eastern Time (no DST) |
| `Australia/Perth` | Australian Western Time |
| `Pacific/Auckland` | New Zealand Time |

### South America
| Time Zone | Description |
|-----------|-------------|
| `America/Sao_Paulo` | Brasilia Time |
| `America/Buenos_Aires` | Argentina Time |
| `America/Santiago` | Chile Time |
| `America/Lima` | Peru Time |
| `America/Bogota` | Colombia Time |

### Other
| Time Zone | Description |
|-----------|-------------|
| `UTC` | Coordinated Universal Time |
| `Africa/Johannesburg` | South Africa Standard Time |
| `Africa/Cairo` | Egypt Time |
| `Africa/Lagos` | West Africa Time |

> **Note:** For a complete list of IANA time zones, see [IANA Time Zone Database](https://www.iana.org/time-zones).

---

## Using Custom Targeting in Reports

To include custom targeting key-values in your report:

1. Add `KEY_VALUES_ID` or `KEY_VALUES_NAME` to your dimensions
2. Specify the custom targeting key IDs in `customDimensionKeyIds`

**Example:**
```json
{
  "displayName": "Custom Targeting Report",
  "reportDefinition": {
    "reportType": "HISTORICAL",
    "dimensions": ["DATE", "KEY_VALUES_NAME"],
    "metrics": ["TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS"],
    "customDimensionKeyIds": [
      "networks/123456/customTargetingKeys/789"
    ],
    "dateRange": {
      "relative": { "relativePreset": "LAST_7_DAYS" }
    }
  }
}
```

The response will include key-value pairs formatted as `{keyName}={valueName}` in the `KEY_VALUES_NAME` dimension.