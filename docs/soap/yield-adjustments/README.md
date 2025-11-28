# Google Ad Manager SOAP API v202511 - Yield & Adjustments

**Last Updated:** 2025-11-28
**API Version:** v202511
**Category:** Yield Management & Forecasting

---

## Table of Contents

1. [Overview](#overview)
2. [Services Summary](#services-summary)
3. [YieldGroupService](#yieldgroupservice)
   - [Methods](#yieldgroupservice-methods)
   - [Data Models](#yield-group-data-models)
4. [AdjustmentService](#adjustmentservice)
   - [Methods](#adjustmentservice-methods)
   - [Data Models](#adjustment-data-models)
5. [Python Code Examples](#python-code-examples)
6. [Actions Reference](#actions-reference)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)

---

## Overview

The **Yield & Adjustments** category in Google Ad Manager's SOAP API provides programmatic control over two critical revenue optimization functions:

### Yield Management

Yield groups enable publishers to maximize revenue by:
- Configuring **Open Bidding** partners for server-to-server programmatic demand
- Setting up **header bidding** integrations for client-side demand
- Managing **mobile app mediation** for SDK-based monetization
- Controlling **Ad Exchange** participation at the inventory level

### Forecast Adjustments

Forecast adjustments allow publishers to:
- Modify traffic predictions for **seasonal events** (holidays, sales periods)
- Account for **external factors** affecting traffic (marketing campaigns, site redesigns)
- Create **traffic segments** to isolate portions of inventory for analysis
- Override system forecasts when publishers have better predictive information

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Yield Group** | A configuration that defines which inventory competes with which demand sources |
| **Yield Partner** | A third-party exchange or network participating in Open Bidding or mediation |
| **Ad Source** | A specific demand configuration within a yield group |
| **Traffic Forecast Segment** | A slice of inventory with specific targeting used for forecast adjustments |
| **Forecast Adjustment** | A modification to predicted traffic volume for a segment and date range |

---

## Services Summary

| Service | Purpose | WSDL Endpoint |
|---------|---------|---------------|
| **YieldGroupService** | Manage yield groups, partners, and ad sources | `https://ads.google.com/apis/ads/publisher/v202511/YieldGroupService?wsdl` |
| **AdjustmentService** | Manage forecast adjustments and traffic segments | `https://ads.google.com/apis/ads/publisher/v202511/AdjustmentService?wsdl` |

### Namespace

```
https://www.google.com/apis/ads/publisher/v202511
```

---

## YieldGroupService

The `YieldGroupService` manages yield groups for Open Bidding, header bidding, and mobile app mediation. Each yield group specifies inventory targeting and contains one or more ad sources from yield partners.

### YieldGroupService Methods

#### createYieldGroups

Creates multiple yield groups in bulk.

| Attribute | Value |
|-----------|-------|
| **Method** | `createYieldGroups` |
| **Parameter** | `yieldGroups` - Array of `YieldGroup` objects |
| **Returns** | Array of created `YieldGroup` objects with assigned IDs |

```python
# Method signature
yield_groups = yield_group_service.createYieldGroups(yieldGroups)
```

#### getYieldGroupsByStatement

Retrieves yield groups matching the specified PQL query criteria.

| Attribute | Value |
|-----------|-------|
| **Method** | `getYieldGroupsByStatement` |
| **Parameter** | `statement` - PQL `Statement` object with query and values |
| **Returns** | `YieldGroupPage` with results and pagination info |

```python
# Method signature
page = yield_group_service.getYieldGroupsByStatement(statement)
```

**Filterable Fields:**
- `id` - Yield group ID
- `name` - Yield group name
- `status` - Yield group status

#### updateYieldGroups

Updates existing yield groups.

| Attribute | Value |
|-----------|-------|
| **Method** | `updateYieldGroups` |
| **Parameter** | `yieldGroups` - Array of `YieldGroup` objects with modifications |
| **Returns** | Array of updated `YieldGroup` objects |

```python
# Method signature
yield_groups = yield_group_service.updateYieldGroups(yieldGroups)
```

#### getYieldPartners

Returns all available yield partners for the network.

| Attribute | Value |
|-----------|-------|
| **Method** | `getYieldPartners` |
| **Parameters** | None |
| **Returns** | Array of `YieldPartner` objects |

```python
# Method signature
partners = yield_group_service.getYieldPartners()
```

---

### Yield Group Data Models

#### YieldGroup

The primary entity representing a yield group configuration.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `yieldGroupId` | `xsd:long` | Read-only | The unique ID of the YieldGroup. This attribute is read-only and is assigned by Google when the yield group is created. |
| `yieldGroupName` | `xsd:string` | **Required** | The display name of the yield group. Must be unique within the network. |
| `exchangeStatus` | `YieldEntityStatus` | **Required** | Status of the Ad Exchange for this yield group. If any active ad sources exist in the group, this must be set to `ACTIVE`. |
| `format` | `YieldFormat` | **Required** | The ad format for the group. Determines which ad formats can compete in this yield group. |
| `environmentType` | `YieldEnvironmentType` | **Required** | The environment type of the group. Determines where ads from this yield group can serve. |
| `targeting` | `Targeting` | Optional | Yield group targeting configuration. Defines which inventory the yield group applies to. Supports inventory targeting, geo targeting, custom targeting, and other targeting types. |
| `adSources` | `YieldAdSource[]` | Optional | The ad sources (demand partners) belonging to this yield group. Each ad source represents a configured demand partner that will compete for impressions. |

---

#### YieldAdSource

Represents a demand source within a yield group.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `adSourceId` | `xsd:long` | Read-only | The unique ID of the ad source. This attribute is read-only and is assigned by Google when the ad source is created. |
| `companyId` | `xsd:long` | **Required** | The ID of the partner owning the ad source. This should be the ID of the Company representing the yield partner. Obtain valid company IDs from `getYieldPartners()`. |
| `displaySettings` | `AbstractDisplaySettings` | **Required** | Data that describes how to call an ad network. Must be one of the concrete subtypes: `OpenBiddingSetting` or `SdkMediationSettings`. |
| `status` | `YieldEntityStatus` | **Required** | User-assigned status controlling mediation behavior. Can be set to `DELETED` to remove the ad source from the YieldGroup. |
| `manualCpm` | `Money` | Optional | CPM manually assigned to this source. This will be used as a default CPM until automatic data collection is available for the ad source, or always if `overrideDynamicCpm` is set to true. |
| `overrideDynamicCpm` | `xsd:boolean` | Optional | When set to true, automatically collected CPM data is ignored in favor of manually configured values. Default is false. |

---

#### YieldPartner

Represents an available yield partner in the network.

| Field | Type | Description |
|-------|------|-------------|
| `companyId` | `xsd:long` | The company ID of the partner, uniquely identifying it in the publisher network. If this ID is null, then this represents a canonical third-party company ad network. |
| `settings` | `YieldPartnerSettings[]` | The settings of the partner, representing its capabilities. Contains information about supported formats, environments, and integration types. |

---

#### YieldPartnerSettings

Settings describing a yield partner's capabilities.

| Field | Type | Description |
|-------|------|-------------|
| `status` | `PartnerSettingStatus` | The status of this partner setting. Values: `UNKNOWN`, `PENDING`, `ACTIVE`, `DEPRECATED` |
| `environment` | `YieldEnvironmentType` | The environment type this setting applies to. |
| `format` | `YieldFormat` | The ad format this setting supports. |
| `integrationType` | `YieldIntegrationType` | The integration type for this setting. |
| `platform` | `YieldPlatform` | The mobile platform this setting applies to (for SDK mediation). |
| `parameters` | `YieldParameter[]` | Array of parameters required by this partner setting. |

---

#### YieldParameter

Describes a parameter field used by mobile adapters to communicate with ad networks.

| Field | Type | Description |
|-------|------|-------------|
| `name` | `xsd:string` | Identifier of the parameter (e.g., "publisherId", "appId"). |
| `isOptional` | `xsd:boolean` | Whether or not this parameter is optional when configuring the ad source. |

---

#### AbstractDisplaySettings

Base class for information necessary to call an ad network as part of mediation or Open Bidding. This is an abstract type and cannot be instantiated directly.

**Subtypes:**

| Subtype | Inheritance | Use Case |
|---------|-------------|----------|
| `OpenBiddingSetting` | Extends `AbstractDisplaySettings` | Server-to-server Open Bidding configuration |
| `SdkMediationSettings` | Extends `OpenBiddingSetting` | Mobile SDK-based mediation configuration |

---

#### OpenBiddingSetting

Configuration for Open Bidding (server-to-server) demand.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `yieldIntegrationType` | `YieldIntegrationType` | **Required** | Integration type of the demand syndication setting. Must be either `EXCHANGE_BIDDING` or `NETWORK_BIDDING` for Open Bidding configurations. |

---

#### SdkMediationSettings

Configuration for SDK-based mobile mediation. Extends `OpenBiddingSetting`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `parameters` | `YieldParameter_StringMapEntry[]` | Optional | A map of key-value pairs to be used by this mobile adapter. Keys are parameter names, values are the configured values. |
| `yieldIntegrationType` | `YieldIntegrationType` | **Required** | The integration type of the adapter. For SDK mediation, this may be `CUSTOM_EVENT` or `SDK`. |
| `platform` | `YieldPlatform` | **Required** | The mobile platform of the adapter (`ANDROID` or `IOS`). |

---

### YieldGroupService Enumerations

#### YieldEntityStatus

Status values for yield groups and ad sources.

| Value | Description |
|-------|-------------|
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |
| `EXPERIMENTING` | The yield group or ad source is in experiment mode, used for testing configurations. |
| `ACTIVE` | Currently active and competing for impressions in the unified auction. |
| `INACTIVE` | Not active; will not compete for impressions. |
| `DELETED` | Marked for deletion and will be removed from the system. |

---

#### YieldFormat

Ad format types supported by yield groups.

| Value | Description |
|-------|-------------|
| `UNKNOWN` | Default/unspecified format. The value returned if the actual value is not exposed. |
| `BANNER` | Standard banner ad format (320x50, 300x250, etc.). |
| `INTERSTITIAL` | Full-screen interstitial ad format. |
| `NATIVE` | Native ad format that matches the look and feel of the app/site. |
| `VIDEO_VAST` | Video ad format using the VAST (Video Ad Serving Template) protocol. |
| `REWARDED` | Rewarded video advertisement format where users receive in-app rewards. |
| `REWARDED_INTERSTITIAL` | Rewarded full-screen interstitial format combining both features. |
| `APP_OPEN` | App opening ad format displayed when an app is launched or brought to foreground. |

---

#### YieldEnvironmentType

Environment types where yield groups can serve.

| Value | Description |
|-------|-------------|
| `UNKNOWN` | Default/unspecified environment. The value returned if the actual value is not exposed. |
| `MOBILE` | Mobile app environment (iOS and Android applications). |
| `VIDEO_VAST` | Video player environment for in-stream video ads. |
| `WEB` | Web browser environment (desktop and mobile web). |

---

#### YieldIntegrationType

Integration types for demand sources.

| Value | Description |
|-------|-------------|
| `UNKNOWN` | Default/unspecified integration type. |
| `CUSTOM_EVENT` | Custom event integration for SDK mediation with custom adapter code. |
| `SDK` | Direct SDK integration with the demand partner's SDK. |
| `OPEN_BIDDING` | Server-to-server Open Bidding integration (formerly Exchange Bidding). |

---

#### YieldPlatform

Mobile platforms for SDK mediation.

| Value | Description |
|-------|-------------|
| `UNKNOWN` | Default/unspecified platform. |
| `ANDROID` | Android mobile platform. |
| `IOS` | iOS mobile platform (iPhone, iPad). |

---

#### PartnerSettingStatus

Status of yield partner settings.

| Value | Description |
|-------|-------------|
| `UNKNOWN` | Default/unspecified status. |
| `PENDING` | Partner setting is pending activation or approval. |
| `ACTIVE` | Partner setting is active and available for use. |
| `DEPRECATED` | Partner setting is deprecated and should not be used for new configurations. |

---

#### YieldGroupPage

Paginated results for yield group queries.

| Field | Type | Description |
|-------|------|-------------|
| `totalResultSetSize` | `xsd:int` | Total number of matching yield groups across all pages. |
| `startIndex` | `xsd:int` | Starting index of the results returned in this page. |
| `results` | `YieldGroup[]` | Array of yield group objects for this page. |

---

## AdjustmentService

The `AdjustmentService` manages forecast adjustments and traffic forecast segments. It enables publishers to modify forecasted traffic volumes to account for known events, seasonal patterns, or other factors the automated forecast may not capture.

### AdjustmentService Methods

#### createTrafficForecastSegments

Creates new traffic forecast segments.

| Attribute | Value |
|-----------|-------|
| **Method** | `createTrafficForecastSegments` |
| **Parameter** | `trafficForecastSegments` - Array of `TrafficForecastSegment` objects |
| **Returns** | Array of created `TrafficForecastSegment` objects with assigned IDs |

```python
# Method signature
segments = adjustment_service.createTrafficForecastSegments(trafficForecastSegments)
```

#### getTrafficForecastSegmentsByStatement

Retrieves traffic forecast segments matching the specified criteria.

| Attribute | Value |
|-----------|-------|
| **Method** | `getTrafficForecastSegmentsByStatement` |
| **Parameter** | `statement` - PQL `Statement` object |
| **Returns** | `TrafficForecastSegmentPage` with results |

```python
# Method signature
page = adjustment_service.getTrafficForecastSegmentsByStatement(statement)
```

#### updateTrafficForecastSegments

Updates existing traffic forecast segments.

| Attribute | Value |
|-----------|-------|
| **Method** | `updateTrafficForecastSegments` |
| **Parameter** | `trafficForecastSegments` - Array of `TrafficForecastSegment` objects |
| **Returns** | Array of updated `TrafficForecastSegment` objects |

```python
# Method signature
segments = adjustment_service.updateTrafficForecastSegments(trafficForecastSegments)
```

#### performTrafficForecastSegmentAction

Performs actions on traffic forecast segments.

| Attribute | Value |
|-----------|-------|
| **Method** | `performTrafficForecastSegmentAction` |
| **Parameter 1** | `action` - `TrafficForecastSegmentAction` object |
| **Parameter 2** | `filterStatement` - PQL `Statement` to select segments |
| **Returns** | `UpdateResult` with count of affected segments |

```python
# Method signature
result = adjustment_service.performTrafficForecastSegmentAction(action, filterStatement)
```

#### createForecastAdjustments

Creates new forecast adjustments.

| Attribute | Value |
|-----------|-------|
| **Method** | `createForecastAdjustments` |
| **Parameter** | `forecastAdjustments` - Array of `ForecastAdjustment` objects |
| **Returns** | Array of created `ForecastAdjustment` objects with assigned IDs |

```python
# Method signature
adjustments = adjustment_service.createForecastAdjustments(forecastAdjustments)
```

#### getForecastAdjustmentsByStatement

Retrieves forecast adjustments matching the specified criteria.

| Attribute | Value |
|-----------|-------|
| **Method** | `getForecastAdjustmentsByStatement` |
| **Parameter** | `statement` - PQL `Statement` object |
| **Returns** | `ForecastAdjustmentPage` with results |

```python
# Method signature
page = adjustment_service.getForecastAdjustmentsByStatement(statement)
```

#### updateForecastAdjustments

Updates existing forecast adjustments.

| Attribute | Value |
|-----------|-------|
| **Method** | `updateForecastAdjustments` |
| **Parameter** | `forecastAdjustments` - Array of `ForecastAdjustment` objects |
| **Returns** | Array of updated `ForecastAdjustment` objects |

```python
# Method signature
adjustments = adjustment_service.updateForecastAdjustments(forecastAdjustments)
```

#### performForecastAdjustmentAction

Performs actions on forecast adjustments (activate/deactivate).

| Attribute | Value |
|-----------|-------|
| **Method** | `performForecastAdjustmentAction` |
| **Parameter 1** | `action` - `ForecastAdjustmentAction` object |
| **Parameter 2** | `filterStatement` - PQL `Statement` to select adjustments |
| **Returns** | `UpdateResult` with count of affected adjustments |

```python
# Method signature
result = adjustment_service.performForecastAdjustmentAction(action, filterStatement)
```

#### calculateDailyAdOpportunityCounts

Takes a prospective forecast adjustment and calculates the daily ad opportunity counts corresponding to its provided volume settings. This is useful for previewing what the system will calculate before actually creating the adjustment.

| Attribute | Value |
|-----------|-------|
| **Method** | `calculateDailyAdOpportunityCounts` |
| **Parameter** | `forecastAdjustment` - A `ForecastAdjustment` object with volume settings configured |
| **Returns** | `ForecastAdjustment` - The same object with `calculatedDailyAdOpportunityCounts` field populated |

**Use Cases:**
- Preview daily breakdown before creating a `TOTAL_VOLUME` adjustment
- Validate historical basis calculations before saving
- Understand how volume will be distributed across the date range

**Example:**

```python
def preview_daily_breakdown(segment_id, start_date, end_date, total_impressions):
    """
    Preview how total impressions will be distributed across days.
    """
    adjustment_service = client.GetService('AdjustmentService', version=VERSION)

    # Create a prospective adjustment (not saved)
    prospective_adjustment = {
        'trafficForecastSegmentId': segment_id,
        'dateRange': {
            'startDate': {'year': start_date.year, 'month': start_date.month, 'day': start_date.day},
            'endDate': {'year': end_date.year, 'month': end_date.month, 'day': end_date.day}
        },
        'volumeType': 'TOTAL_VOLUME',
        'totalVolumeSettings': {
            'adOpportunityCount': total_impressions
        }
    }

    # Calculate without saving
    result = adjustment_service.calculateDailyAdOpportunityCounts(prospective_adjustment)

    # Access the calculated daily values
    daily_counts = result.get('calculatedDailyAdOpportunityCounts', [])
    print(f"Daily breakdown for {total_impressions:,} total impressions:")
    for i, count in enumerate(daily_counts):
        print(f"  Day {i + 1}: {count:,} impressions")

    return daily_counts
```

---

### Adjustment Data Models

#### TrafficForecastSegment

Defines a slice of inventory for forecast analysis and adjustment. A segment is defined by targeting criteria and can have multiple forecast adjustments applied to it over different date ranges.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `xsd:long` | Read-only | The unique ID of the TrafficForecastSegment. This field is read-only and set by Google when the segment is created. |
| `name` | `xsd:string` | **Required** | Name of the TrafficForecastSegment. This field must be unique among all segments for this network. Maximum length is 255 characters. |
| `targeting` | `Targeting` | **Required** | The targeting that defines a segment of traffic. **Important:** Targeting cannot be changed after segment creation. To modify targeting, create a new segment and migrate adjustments. |
| `activeForecastAdjustmentCount` | `xsd:int` | Read-only | The number of active forecast adjustments associated with the TrafficForecastSegment. This attribute is read-only and updated automatically. |
| `creationDateTime` | `DateTime` | Read-only | The date and time that the TrafficForecastSegment was created. This attribute is read-only. |

**Notes:**
- Segments are immutable after creation with respect to their targeting
- A segment can have multiple adjustments, but only one adjustment per date
- The `activeForecastAdjustmentCount` only counts `ACTIVE` adjustments, not `INACTIVE` ones

---

#### ForecastAdjustment

Provides information about the expected volume and composition of traffic over a date range for a traffic forecast segment. Allows publishers to override system-generated forecasts with their own predictions.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `xsd:long` | Read-only | The unique ID of the ForecastAdjustment. System-generated when the adjustment is created. |
| `trafficForecastSegmentId` | `xsd:long` | **Required**, Immutable | The ID of the parent TrafficForecastSegment. This value cannot be changed after the adjustment is created. |
| `name` | `xsd:string` | **Required** | Name identifying the forecast adjustment. Should be descriptive (e.g., "Black Friday 2025 Traffic Spike"). |
| `dateRange` | `DateRange` | **Required** | The start and end date range of the adjustment. Defines the temporal scope of when the adjustment applies. |
| `status` | `ForecastAdjustmentStatus` | Read-only | The status of the adjustment (`ACTIVE` or `INACTIVE`). Modified via `performForecastAdjustmentAction` only, not through updates. |
| `volumeType` | `ForecastAdjustmentVolumeType` | **Required** | The volume type of the adjustment. Determines which volume settings field is used: `DAILY_VOLUME`, `TOTAL_VOLUME`, or `HISTORICAL_BASIS_VOLUME`. |
| `allowAdjustingForecastAboveRecommendedLimit` | `xsd:boolean` | Optional | Whether to allow provided volume settings to increase the current forecast by more than 300%. This is a non-persistent flag used during creation/update to bypass validation. Default is false. |
| `dailyVolumeSettings` | `DailyVolumeSettings` | Conditional | Required when `volumeType` is `DAILY_VOLUME`; ignored otherwise. Specifies exact daily ad opportunity counts. |
| `totalVolumeSettings` | `TotalVolumeSettings` | Conditional | Required when `volumeType` is `TOTAL_VOLUME`; ignored otherwise. Specifies a single total count distributed across days. |
| `historicalBasisVolumeSettings` | `HistoricalBasisVolumeSettings` | Conditional | Required when `volumeType` is `HISTORICAL_BASIS_VOLUME`; ignored otherwise. Bases the adjustment on historical data with a multiplier. |
| `calculatedDailyAdOpportunityCounts` | `xsd:long[]` | Read-only | The daily number of ad opportunities calculated to satisfy the provided volume settings. Auto-populated after creation. Array length matches the number of days in `dateRange`. |

**Important Constraints:**
- Only one adjustment can be active for a given segment and date
- Adjustments cannot overlap with other active adjustments for the same segment
- Recommended to keep adjustments between 10% and 300% of the baseline forecast

---

#### Volume Settings Types

##### DailyVolumeSettings

Used when specifying ad opportunities on a day-by-day basis. Provides the most granular control over forecast adjustments.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `adOpportunityCounts` | `xsd:long[]` | **Required** | A list of ad opportunity counts where each value represents the expected number of ad opportunities on the corresponding day of the adjustment date range. **The number of values must exactly match the number of days in the adjustment date range.** |

**Example:** For a 7-day adjustment (Dec 22-28), provide exactly 7 values:
```python
'dailyVolumeSettings': {
    'adOpportunityCounts': [
        1000000,   # Dec 22
        1100000,   # Dec 23
        1200000,   # Dec 24
        800000,    # Dec 25 (holiday - lower traffic)
        600000,    # Dec 26
        700000,    # Dec 27
        900000     # Dec 28
    ]
}
```

---

##### TotalVolumeSettings

Used when specifying a total number of ad opportunities across the entire date range. The system automatically distributes this total across days based on historical patterns.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `adOpportunityCount` | `xsd:long` | **Required** | The total ad opportunity count over the entire forecast adjustment date range. This single value represents the cumulative ad opportunities expected across all days in the range. |

**Use Case:** When you know the total expected impressions but want the system to handle daily distribution:
```python
'totalVolumeSettings': {
    'adOpportunityCount': 5000000  # 5 million total impressions over the date range
}
```

---

##### HistoricalBasisVolumeSettings

Used when basing the adjustment on historical performance data. Allows applying a multiplier to historical traffic patterns.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `useParentTrafficForecastSegmentTargeting` | `xsd:boolean` | **Required** | Whether the parent traffic forecast segment targeting or the `targeting` field's historical volume data should be used. Set to `true` to use the segment's targeting. |
| `targeting` | `Targeting` | Conditional | The targeting criteria to use as the source of the historical volume data. **Required if `useParentTrafficForecastSegmentTargeting` is false; ignored otherwise.** Allows using different targeting than the segment for historical reference. |
| `historicalDateRange` | `DateRange` | **Required** | The date range to use for the historical ad opportunity volume. Typically the same period from the previous year. |
| `multiplierMilliPercent` | `xsd:long` | **Required** | The multiplier to apply to the historical traffic volume, expressed in thousandths of a percent. Example: Setting forecasted traffic to 130% of historical would use value `130000`. Value of `100000` equals 100% (no change). |

**Multiplier Examples:**
| Desired Percentage | multiplierMilliPercent Value |
|-------------------|------------------------------|
| 50% (half) | 50000 |
| 100% (same) | 100000 |
| 150% (1.5x) | 150000 |
| 200% (double) | 200000 |
| 300% (triple) | 300000 |

---

#### DateRange

Represents a range of dates with optional bounds.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `startDate` | `Date` | Conditional | The start date of this range. This field is optional, and if not set, there is no lower bound on the date range. **If this field is not set, then `endDate` must be specified.** |
| `endDate` | `Date` | Conditional | The end date of this range. This field is optional, and if not set, there is no upper bound on the date range. **If this field is not set, then `startDate` must be specified.** |

**Note:** For `ForecastAdjustment.dateRange`, both fields are typically required to define the exact adjustment period.

---

#### Date

Represents a calendar date.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `year` | `xsd:int` | **Required** | Year (e.g., 2025). Four-digit year value. |
| `month` | `xsd:int` | **Required** | Month (1..12). January is 1, December is 12. |
| `day` | `xsd:int` | **Required** | Day of the month (1..31). Must be valid for the given month and year. |

**Example:**
```python
'startDate': {
    'year': 2025,
    'month': 11,
    'day': 28
}
```

---

### AdjustmentService Enumerations

#### ForecastAdjustmentStatus

The status of a forecast adjustment. **Inactive adjustments are not applied during forecasting.**

| Value | Description |
|-------|-------------|
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |
| `ACTIVE` | Indicates the current adjustment is active and being applied to forecasts. |
| `INACTIVE` | Indicates the current adjustment is inactive and will not affect forecasts. |

**Note:** Status is modified using `performForecastAdjustmentAction`, not through `updateForecastAdjustments`.

---

#### ForecastAdjustmentVolumeType

Determines how volume settings for a ForecastAdjustment are specified.

| Value | Description |
|-------|-------------|
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |
| `DAILY_VOLUME` | Volume is defined by a series of daily ad opportunity counts. Use `dailyVolumeSettings`. |
| `TOTAL_VOLUME` | Volume is defined by a single total ad opportunity count. Use `totalVolumeSettings`. |
| `HISTORICAL_BASIS_VOLUME` | Volume is defined by historical volume data with a multiplier. Use `historicalBasisVolumeSettings`. |

---

#### Page Objects

##### TrafficForecastSegmentPage

Paginated results for traffic forecast segment queries.

| Field | Type | Description |
|-------|------|-------------|
| `totalResultSetSize` | `xsd:int` | Total number of matching segments across all pages. |
| `startIndex` | `xsd:int` | Starting index of the results returned in this page. |
| `results` | `TrafficForecastSegment[]` | Array of traffic forecast segment objects for this page. |

---

##### ForecastAdjustmentPage

Paginated results for forecast adjustment queries.

| Field | Type | Description |
|-------|------|-------------|
| `totalResultSetSize` | `xsd:int` | Total number of matching adjustments across all pages. |
| `startIndex` | `xsd:int` | Starting index of the results returned in this page. |
| `results` | `ForecastAdjustment[]` | Array of forecast adjustment objects for this page. |

---

## Python Code Examples

### Setup

```python
from googleads import ad_manager

# Initialize the Ad Manager client from configuration
# Requires ~/googleads.yaml with credentials
client = ad_manager.AdManagerClient.LoadFromStorage()

# API version
VERSION = 'v202511'
```

### Example 1: Get Available Yield Partners

```python
def get_yield_partners():
    """
    Retrieve all available yield partners for the network.

    Returns:
        list: Available yield partners that can be added to yield groups.
    """
    yield_group_service = client.GetService('YieldGroupService', version=VERSION)

    partners = yield_group_service.getYieldPartners()

    print(f"Found {len(partners)} yield partners:")
    for partner in partners:
        print(f"  - {partner['name']} (Company ID: {partner['companyId']})")

    return partners


if __name__ == '__main__':
    get_yield_partners()
```

### Example 2: Create a Yield Group for Open Bidding

```python
def create_open_bidding_yield_group(ad_unit_ids, partner_company_id, yield_group_name):
    """
    Create a yield group configured for Open Bidding.

    Args:
        ad_unit_ids: List of ad unit IDs to target.
        partner_company_id: Company ID of the yield partner.
        yield_group_name: Name for the new yield group.

    Returns:
        The created yield group object.
    """
    yield_group_service = client.GetService('YieldGroupService', version=VERSION)

    # Build inventory targeting
    inventory_targeting = {
        'targetedAdUnits': [{'adUnitId': id} for id in ad_unit_ids]
    }

    # Build the ad source with Open Bidding settings
    ad_source = {
        'companyId': partner_company_id,
        'status': 'ACTIVE',
        'displaySettings': {
            'xsi_type': 'OpenBiddingSetting'
            # Additional Open Bidding settings can be added here
        },
        # Optional: Set a manual CPM for initial bidding
        'manualCpm': {
            'currencyCode': 'USD',
            'microAmount': 500000  # $0.50 CPM
        },
        'overrideDynamicCpm': False  # Use automatic CPM when available
    }

    # Build the yield group
    yield_group = {
        'yieldGroupName': yield_group_name,
        'exchangeStatus': 'ACTIVE',  # Include Ad Exchange
        'format': 'BANNER',
        'environmentType': 'WEB',
        'targeting': {
            'inventoryTargeting': inventory_targeting
        },
        'adSources': [ad_source]
    }

    # Create the yield group
    result = yield_group_service.createYieldGroups([yield_group])

    created_group = result[0]
    print(f"Created yield group: {created_group['yieldGroupName']}")
    print(f"  ID: {created_group['yieldGroupId']}")

    return created_group


if __name__ == '__main__':
    AD_UNIT_IDS = ['12345678', '87654321']  # Replace with actual ad unit IDs
    PARTNER_COMPANY_ID = 11111111  # Replace with actual partner company ID
    YIELD_GROUP_NAME = 'Premium Inventory - Open Bidding'

    create_open_bidding_yield_group(AD_UNIT_IDS, PARTNER_COMPANY_ID, YIELD_GROUP_NAME)
```

### Example 3: Query Yield Groups by Status

```python
def get_active_yield_groups():
    """
    Retrieve all active yield groups.

    Returns:
        list: Active yield groups.
    """
    yield_group_service = client.GetService('YieldGroupService', version=VERSION)

    # Create a PQL statement to filter by status
    statement = ad_manager.StatementBuilder(version=VERSION)
    statement.Where('exchangeStatus = :status')
    statement.WithBindVariable('status', 'ACTIVE')
    statement.Limit(500)

    all_yield_groups = []

    while True:
        response = yield_group_service.getYieldGroupsByStatement(
            statement.ToStatement()
        )

        if 'results' in response and response['results']:
            all_yield_groups.extend(response['results'])
            statement.Offset(statement.offset + statement.limit)
        else:
            break

    print(f"Found {len(all_yield_groups)} active yield groups:")
    for yg in all_yield_groups:
        ad_source_count = len(yg.get('adSources', []))
        print(f"  - {yg['yieldGroupName']} ({ad_source_count} ad sources)")

    return all_yield_groups


if __name__ == '__main__':
    get_active_yield_groups()
```

### Example 4: Update Yield Group Ad Source CPM

```python
def update_ad_source_cpm(yield_group_id, ad_source_id, new_cpm_micro_amount):
    """
    Update the manual CPM for an ad source in a yield group.

    Args:
        yield_group_id: ID of the yield group.
        ad_source_id: ID of the ad source to update.
        new_cpm_micro_amount: New CPM in micro amounts (1000000 = $1.00).

    Returns:
        Updated yield group object.
    """
    yield_group_service = client.GetService('YieldGroupService', version=VERSION)

    # Fetch the existing yield group
    statement = ad_manager.StatementBuilder(version=VERSION)
    statement.Where('yieldGroupId = :id')
    statement.WithBindVariable('id', yield_group_id)

    response = yield_group_service.getYieldGroupsByStatement(statement.ToStatement())

    if not response.get('results'):
        raise ValueError(f"Yield group {yield_group_id} not found")

    yield_group = response['results'][0]

    # Find and update the ad source
    for ad_source in yield_group.get('adSources', []):
        if ad_source['adSourceId'] == ad_source_id:
            ad_source['manualCpm'] = {
                'currencyCode': 'USD',
                'microAmount': new_cpm_micro_amount
            }
            ad_source['overrideDynamicCpm'] = True
            break
    else:
        raise ValueError(f"Ad source {ad_source_id} not found in yield group")

    # Update the yield group
    result = yield_group_service.updateYieldGroups([yield_group])

    print(f"Updated CPM to ${new_cpm_micro_amount / 1000000:.2f}")
    return result[0]


if __name__ == '__main__':
    YIELD_GROUP_ID = 123456789
    AD_SOURCE_ID = 987654321
    NEW_CPM = 750000  # $0.75

    update_ad_source_cpm(YIELD_GROUP_ID, AD_SOURCE_ID, NEW_CPM)
```

### Example 5: Create a Traffic Forecast Segment

```python
def create_traffic_segment(segment_name, ad_unit_ids, geo_targeting=None):
    """
    Create a traffic forecast segment for a specific slice of inventory.

    Args:
        segment_name: Name for the segment.
        ad_unit_ids: List of ad unit IDs to include.
        geo_targeting: Optional geographic targeting dict.

    Returns:
        Created traffic forecast segment.
    """
    adjustment_service = client.GetService('AdjustmentService', version=VERSION)

    # Build targeting
    targeting = {
        'inventoryTargeting': {
            'targetedAdUnits': [{'adUnitId': id} for id in ad_unit_ids]
        }
    }

    # Add geo targeting if provided
    if geo_targeting:
        targeting['geoTargeting'] = geo_targeting

    segment = {
        'name': segment_name,
        'targeting': targeting
    }

    result = adjustment_service.createTrafficForecastSegments([segment])

    created_segment = result[0]
    print(f"Created traffic segment: {created_segment['name']}")
    print(f"  ID: {created_segment['id']}")

    return created_segment


if __name__ == '__main__':
    SEGMENT_NAME = 'US Homepage Traffic'
    AD_UNIT_IDS = ['12345678']

    # Target United States (geo ID: 2840)
    GEO_TARGETING = {
        'targetedLocations': [{'id': 2840}]  # United States
    }

    create_traffic_segment(SEGMENT_NAME, AD_UNIT_IDS, GEO_TARGETING)
```

### Example 6: Create a Forecast Adjustment for a Seasonal Event

```python
import datetime

def create_seasonal_adjustment(
    segment_id,
    adjustment_name,
    start_date,
    end_date,
    multiplier_percent
):
    """
    Create a forecast adjustment based on historical data with a multiplier.

    This is useful for seasonal events like Black Friday, holidays, etc.

    Args:
        segment_id: ID of the traffic forecast segment.
        adjustment_name: Name for the adjustment.
        start_date: Start date as datetime.date object.
        end_date: End date as datetime.date object.
        multiplier_percent: Multiplier as percentage (e.g., 150 for 150%).

    Returns:
        Created forecast adjustment.
    """
    adjustment_service = client.GetService('AdjustmentService', version=VERSION)

    # Calculate historical date range (same period last year)
    historical_start = datetime.date(
        start_date.year - 1,
        start_date.month,
        start_date.day
    )
    historical_end = datetime.date(
        end_date.year - 1,
        end_date.month,
        end_date.day
    )

    adjustment = {
        'name': adjustment_name,
        'trafficForecastSegmentId': segment_id,
        'dateRange': {
            'startDate': {
                'year': start_date.year,
                'month': start_date.month,
                'day': start_date.day
            },
            'endDate': {
                'year': end_date.year,
                'month': end_date.month,
                'day': end_date.day
            }
        },
        'volumeType': 'HISTORICAL_BASIS_VOLUME',
        'historicalBasisVolumeSettings': {
            'useParentTrafficForecastSegmentTargeting': True,
            'historicalDateRange': {
                'startDate': {
                    'year': historical_start.year,
                    'month': historical_start.month,
                    'day': historical_start.day
                },
                'endDate': {
                    'year': historical_end.year,
                    'month': historical_end.month,
                    'day': historical_end.day
                }
            },
            # Multiplier in milli-percent (100000 = 100%)
            'multiplierMilliPercent': multiplier_percent * 1000
        },
        'allowAdjustingForecastAboveRecommendedLimit': False
    }

    result = adjustment_service.createForecastAdjustments([adjustment])

    created_adjustment = result[0]
    print(f"Created forecast adjustment: {created_adjustment['name']}")
    print(f"  ID: {created_adjustment['id']}")
    print(f"  Status: {created_adjustment['status']}")

    return created_adjustment


if __name__ == '__main__':
    SEGMENT_ID = 123456789
    ADJUSTMENT_NAME = 'Black Friday 2025 - Expected 150% Traffic'

    # Black Friday 2025 dates
    START_DATE = datetime.date(2025, 11, 28)
    END_DATE = datetime.date(2025, 11, 30)

    # Expect 150% of last year's traffic
    MULTIPLIER = 150

    create_seasonal_adjustment(
        SEGMENT_ID,
        ADJUSTMENT_NAME,
        START_DATE,
        END_DATE,
        MULTIPLIER
    )
```

### Example 7: Create a Total Volume Forecast Adjustment

```python
import datetime

def create_total_volume_adjustment(
    segment_id,
    adjustment_name,
    start_date,
    end_date,
    total_impressions
):
    """
    Create a forecast adjustment with a specific total impression count.

    Useful when you know exactly how many impressions to expect
    (e.g., from a marketing campaign with known reach).

    Args:
        segment_id: ID of the traffic forecast segment.
        adjustment_name: Name for the adjustment.
        start_date: Start date as datetime.date object.
        end_date: End date as datetime.date object.
        total_impressions: Total expected impressions.

    Returns:
        Created forecast adjustment.
    """
    adjustment_service = client.GetService('AdjustmentService', version=VERSION)

    adjustment = {
        'name': adjustment_name,
        'trafficForecastSegmentId': segment_id,
        'dateRange': {
            'startDate': {
                'year': start_date.year,
                'month': start_date.month,
                'day': start_date.day
            },
            'endDate': {
                'year': end_date.year,
                'month': end_date.month,
                'day': end_date.day
            }
        },
        'volumeType': 'TOTAL_VOLUME',
        'totalVolumeSettings': {
            'adOpportunityCount': total_impressions
        }
    }

    result = adjustment_service.createForecastAdjustments([adjustment])

    created_adjustment = result[0]
    print(f"Created adjustment for {total_impressions:,} total impressions")

    return created_adjustment


if __name__ == '__main__':
    SEGMENT_ID = 123456789
    ADJUSTMENT_NAME = 'Product Launch Campaign'
    START_DATE = datetime.date(2025, 12, 1)
    END_DATE = datetime.date(2025, 12, 7)
    TOTAL_IMPRESSIONS = 5000000  # 5 million impressions expected

    create_total_volume_adjustment(
        SEGMENT_ID,
        ADJUSTMENT_NAME,
        START_DATE,
        END_DATE,
        TOTAL_IMPRESSIONS
    )
```

### Example 8: Create a Daily Volume Forecast Adjustment

```python
import datetime

def create_daily_volume_adjustment(
    segment_id,
    adjustment_name,
    start_date,
    daily_impressions
):
    """
    Create a forecast adjustment with specific daily impression counts.

    Useful when traffic varies day-by-day (e.g., weekday vs weekend).

    Args:
        segment_id: ID of the traffic forecast segment.
        adjustment_name: Name for the adjustment.
        start_date: Start date as datetime.date object.
        daily_impressions: List of daily impression counts.

    Returns:
        Created forecast adjustment.
    """
    adjustment_service = client.GetService('AdjustmentService', version=VERSION)

    # Calculate end date based on number of days
    num_days = len(daily_impressions)
    end_date = start_date + datetime.timedelta(days=num_days - 1)

    adjustment = {
        'name': adjustment_name,
        'trafficForecastSegmentId': segment_id,
        'dateRange': {
            'startDate': {
                'year': start_date.year,
                'month': start_date.month,
                'day': start_date.day
            },
            'endDate': {
                'year': end_date.year,
                'month': end_date.month,
                'day': end_date.day
            }
        },
        'volumeType': 'DAILY_VOLUME',
        'dailyVolumeSettings': {
            'adOpportunityCounts': daily_impressions
        }
    }

    result = adjustment_service.createForecastAdjustments([adjustment])

    created_adjustment = result[0]
    total = sum(daily_impressions)
    print(f"Created daily adjustment: {total:,} total impressions over {num_days} days")

    return created_adjustment


if __name__ == '__main__':
    SEGMENT_ID = 123456789
    ADJUSTMENT_NAME = 'Holiday Week Traffic'
    START_DATE = datetime.date(2025, 12, 22)

    # Mon, Tue, Wed (high), Thu-Sat (holiday - lower), Sun (recovery)
    DAILY_IMPRESSIONS = [
        1000000,  # Monday
        1000000,  # Tuesday
        1200000,  # Wednesday (pre-holiday spike)
        500000,   # Thursday (holiday)
        400000,   # Friday (holiday)
        600000,   # Saturday
        900000    # Sunday
    ]

    create_daily_volume_adjustment(
        SEGMENT_ID,
        ADJUSTMENT_NAME,
        START_DATE,
        DAILY_IMPRESSIONS
    )
```

### Example 9: Activate/Deactivate Forecast Adjustments

```python
def activate_forecast_adjustments(adjustment_ids):
    """
    Activate multiple forecast adjustments.

    Args:
        adjustment_ids: List of adjustment IDs to activate.

    Returns:
        Number of adjustments activated.
    """
    adjustment_service = client.GetService('AdjustmentService', version=VERSION)

    # Build statement to select adjustments
    statement = ad_manager.StatementBuilder(version=VERSION)
    statement.Where('id IN (:ids)')
    statement.WithBindVariable('ids', adjustment_ids)

    action = {'xsi_type': 'ActivateForecastAdjustments'}

    result = adjustment_service.performForecastAdjustmentAction(
        action,
        statement.ToStatement()
    )

    count = result.get('numChanges', 0)
    print(f"Activated {count} forecast adjustment(s)")

    return count


def deactivate_forecast_adjustments(adjustment_ids):
    """
    Deactivate multiple forecast adjustments.

    Args:
        adjustment_ids: List of adjustment IDs to deactivate.

    Returns:
        Number of adjustments deactivated.
    """
    adjustment_service = client.GetService('AdjustmentService', version=VERSION)

    statement = ad_manager.StatementBuilder(version=VERSION)
    statement.Where('id IN (:ids)')
    statement.WithBindVariable('ids', adjustment_ids)

    action = {'xsi_type': 'DeactivateForecastAdjustments'}

    result = adjustment_service.performForecastAdjustmentAction(
        action,
        statement.ToStatement()
    )

    count = result.get('numChanges', 0)
    print(f"Deactivated {count} forecast adjustment(s)")

    return count


if __name__ == '__main__':
    ADJUSTMENT_IDS = [111111, 222222, 333333]

    # Activate adjustments
    activate_forecast_adjustments(ADJUSTMENT_IDS)

    # Or deactivate
    # deactivate_forecast_adjustments(ADJUSTMENT_IDS)
```

### Example 10: Query All Forecast Adjustments for a Segment

```python
def get_adjustments_for_segment(segment_id):
    """
    Retrieve all forecast adjustments for a specific traffic segment.

    Args:
        segment_id: ID of the traffic forecast segment.

    Returns:
        list: Forecast adjustments for the segment.
    """
    adjustment_service = client.GetService('AdjustmentService', version=VERSION)

    statement = ad_manager.StatementBuilder(version=VERSION)
    statement.Where('trafficForecastSegmentId = :segmentId')
    statement.WithBindVariable('segmentId', segment_id)
    statement.OrderBy('dateRange.startDate', ascending=True)
    statement.Limit(500)

    all_adjustments = []

    while True:
        response = adjustment_service.getForecastAdjustmentsByStatement(
            statement.ToStatement()
        )

        if 'results' in response and response['results']:
            all_adjustments.extend(response['results'])
            statement.Offset(statement.offset + statement.limit)
        else:
            break

    print(f"Found {len(all_adjustments)} adjustments for segment {segment_id}:")
    for adj in all_adjustments:
        date_range = adj['dateRange']
        start = f"{date_range['startDate']['year']}-{date_range['startDate']['month']:02d}-{date_range['startDate']['day']:02d}"
        end = f"{date_range['endDate']['year']}-{date_range['endDate']['month']:02d}-{date_range['endDate']['day']:02d}"
        print(f"  - {adj['name']} ({start} to {end}) - {adj['status']}")

    return all_adjustments


if __name__ == '__main__':
    SEGMENT_ID = 123456789
    get_adjustments_for_segment(SEGMENT_ID)
```

---

## Actions Reference

Actions are used with the `performForecastAdjustmentAction` and `performTrafficForecastSegmentAction` methods to change the status of objects. Actions inherit from their respective base action types.

### Forecast Adjustment Actions

All forecast adjustment actions extend `ForecastAdjustmentAction`.

| Action Type | xsi_type | Description |
|-------------|----------|-------------|
| `ActivateForecastAdjustments` | `ActivateForecastAdjustments` | Activates selected forecast adjustments, making them affect forecasting. After activation, the adjustment's status becomes `ACTIVE`. |
| `DeactivateForecastAdjustments` | `DeactivateForecastAdjustments` | Deactivates selected forecast adjustments, removing them from forecasting calculations. After deactivation, the adjustment's status becomes `INACTIVE`. |

**Usage Example:**
```python
# Activate adjustments
action = {'xsi_type': 'ActivateForecastAdjustments'}
result = adjustment_service.performForecastAdjustmentAction(action, statement.ToStatement())

# Deactivate adjustments
action = {'xsi_type': 'DeactivateForecastAdjustments'}
result = adjustment_service.performForecastAdjustmentAction(action, statement.ToStatement())
```

### Traffic Forecast Segment Actions

All traffic forecast segment actions extend `TrafficForecastSegmentAction`.

| Action Type | xsi_type | Description |
|-------------|----------|-------------|
| `ActivateTrafficForecastSegments` | `ActivateTrafficForecastSegments` | Activates selected traffic forecast segments, making them available for adjustments. |
| `DeactivateTrafficForecastSegments` | `DeactivateTrafficForecastSegments` | Deactivates selected traffic forecast segments. Note: Segments with active adjustments cannot be deactivated. |

**Usage Example:**
```python
# Activate segments
action = {'xsi_type': 'ActivateTrafficForecastSegments'}
result = adjustment_service.performTrafficForecastSegmentAction(action, statement.ToStatement())

# Deactivate segments
action = {'xsi_type': 'DeactivateTrafficForecastSegments'}
result = adjustment_service.performTrafficForecastSegmentAction(action, statement.ToStatement())
```

### UpdateResult

Both action methods return an `UpdateResult` object:

| Field | Type | Description |
|-------|------|-------------|
| `numChanges` | `xsd:int` | The number of objects that were affected by the action. |

---

## Error Handling

### YieldGroupService Errors

| Error Type | Description |
|------------|-------------|
| `YieldError` | Generic yield-related errors |
| `EntityLimitReachedError` | Maximum number of yield groups reached |
| `EntityChildrenLimitReachedError` | Maximum ad sources in a yield group reached |
| `InventoryTargetingError` | Invalid inventory targeting configuration |
| `GeoTargetingError` | Invalid geographic targeting |
| `CustomTargetingError` | Invalid custom targeting criteria |

### AdjustmentService Errors

| Error Type | Description |
|------------|-------------|
| `ForecastAdjustmentError` | Forecast adjustment-specific errors |
| `TrafficForecastSegmentError` | Traffic segment-specific errors |
| `DateTimeRangeTargetingError` | Invalid date range |
| `FeatureError` | Feature not available (Ad Manager 360 required) |

### Common Error Reasons

**ForecastAdjustmentError.Reason**

| Reason | Description |
|--------|-------------|
| `ADJUSTMENT_OVERLAPS_EXISTING` | Date range overlaps with existing adjustment |
| `INVALID_DATE_RANGE` | Start date must be before end date |
| `SEGMENT_NOT_FOUND` | Traffic segment ID does not exist |
| `VOLUME_TYPE_REQUIRED` | Must specify a volume type |
| `UNKNOWN` | Unknown error occurred |

**TrafficForecastSegmentError.Reason**

| Reason | Description |
|--------|-------------|
| `SEGMENT_NAME_REQUIRED` | Segment must have a name |
| `TARGETING_REQUIRED` | Segment must have targeting criteria |
| `DUPLICATE_SEGMENT_NAME` | Segment name already exists |
| `UNKNOWN` | Unknown error occurred |

### Error Handling Example

```python
from googleads import errors

def safe_create_adjustment(adjustment_service, adjustment):
    """
    Create a forecast adjustment with error handling.
    """
    try:
        result = adjustment_service.createForecastAdjustments([adjustment])
        return result[0]

    except errors.GoogleAdsServerFault as e:
        for error in e.errors:
            error_type = error.get('errorType', 'Unknown')
            reason = error.get('reason', 'Unknown')

            if error_type == 'ForecastAdjustmentError':
                if reason == 'ADJUSTMENT_OVERLAPS_EXISTING':
                    print("Error: An adjustment already exists for this date range")
                elif reason == 'SEGMENT_NOT_FOUND':
                    print("Error: Traffic segment not found")
                else:
                    print(f"Forecast error: {reason}")

            elif error_type == 'FeatureError':
                print("Error: This feature requires Ad Manager 360")

            else:
                print(f"Error: {error_type} - {reason}")

        return None

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None
```

---

## Best Practices

### Yield Group Management

1. **Organize by Inventory, Not Partners**
   - Create yield groups based on inventory characteristics (format, environment, geography)
   - Add multiple yield partners to each group rather than creating partner-specific groups

2. **Start with Ad Exchange Enabled**
   - Always include Ad Exchange (`exchangeStatus: ACTIVE`) as baseline competition
   - Additional yield partners compete against Ad Exchange in the unified auction

3. **Use Manual CPM Wisely**
   - Set manual CPM as a floor for new partners
   - Disable `overrideDynamicCpm` once automatic data collection is established

4. **Limit Partners per Group**
   - Maximum 10 third-party yield partners per yield group
   - More partners can increase latency and reduce win rates

5. **Monitor Performance**
   - Use the Yield Group reporting to track partner performance
   - Regularly review and remove underperforming partners

### Forecast Adjustment Management

1. **Create Segments Before Adjustments**
   - Define traffic forecast segments for inventory slices you frequently adjust
   - Reuse segments across multiple adjustment periods

2. **Use Historical Basis for Recurring Events**
   - For annual events (holidays, seasonal sales), use `HISTORICAL_BASIS_VOLUME`
   - Reference the same period from the previous year

3. **Stay Within Recommended Limits**
   - Keep adjustments between 10% and 300% of daily forecast values
   - Adjustments outside this range may have unexpected effects

4. **Plan Ahead**
   - Create adjustments at least 1-2 weeks before the affected period
   - This gives the system time to incorporate changes into delivery planning

5. **Avoid Overlapping Adjustments**
   - Each traffic segment can have only one active adjustment per date
   - Deactivate old adjustments before creating new ones for the same period

### API Usage

1. **Use Pagination**
   - Always implement pagination when retrieving yield groups or adjustments
   - Default page size is 500; adjust based on your needs

2. **Batch Operations**
   - Create/update multiple objects in single API calls
   - Reduces API quota consumption and improves performance

3. **Cache Yield Partners**
   - Yield partner list changes infrequently
   - Cache the result of `getYieldPartners()` and refresh daily

4. **Handle Rate Limits**
   - Implement exponential backoff for API errors
   - Monitor quota usage in Google Cloud Console

---

## Resources

### Official Documentation

#### YieldGroupService (v202511)

- [YieldGroupService Reference](https://developers.google.com/ad-manager/api/reference/v202511/YieldGroupService) - Service overview and methods
- [YieldGroup Type](https://developers.google.com/ad-manager/api/reference/v202511/YieldGroupService.YieldGroup) - YieldGroup object definition
- [YieldAdSource Type](https://developers.google.com/ad-manager/api/reference/v202511/YieldGroupService.YieldAdSource) - Ad source configuration
- [YieldPartner Type](https://developers.google.com/ad-manager/api/reference/v202511/YieldGroupService.YieldPartner) - Partner information
- [YieldEntityStatus Enum](https://developers.google.com/ad-manager/api/reference/v202511/YieldGroupService.YieldEntityStatus) - Status values
- [YieldFormat Enum](https://developers.google.com/ad-manager/api/reference/v202511/YieldGroupService.YieldFormat) - Ad format values
- [YieldEnvironmentType Enum](https://developers.google.com/ad-manager/api/reference/v202511/YieldGroupService.YieldEnvironmentType) - Environment types
- [AbstractDisplaySettings Type](https://developers.google.com/ad-manager/api/reference/v202511/YieldGroupService.AbstractDisplaySettings) - Display settings base class
- [OpenBiddingSetting Type](https://developers.google.com/ad-manager/api/reference/v202511/YieldGroupService.OpenBiddingSetting) - Open Bidding configuration
- [SdkMediationSettings Type](https://developers.google.com/ad-manager/api/reference/v202511/YieldGroupService.SdkMediationSettings) - SDK mediation configuration

#### AdjustmentService (v202511)

- [AdjustmentService Reference](https://developers.google.com/ad-manager/api/reference/v202511/AdjustmentService) - Service overview and methods
- [ForecastAdjustment Type](https://developers.google.com/ad-manager/api/reference/v202511/AdjustmentService.ForecastAdjustment) - Forecast adjustment object
- [TrafficForecastSegment Type](https://developers.google.com/ad-manager/api/reference/v202511/AdjustmentService.TrafficForecastSegment) - Traffic segment object
- [DailyVolumeSettings Type](https://developers.google.com/ad-manager/api/reference/v202511/AdjustmentService.DailyVolumeSettings) - Daily volume configuration
- [TotalVolumeSettings Type](https://developers.google.com/ad-manager/api/reference/v202511/AdjustmentService.TotalVolumeSettings) - Total volume configuration
- [HistoricalBasisVolumeSettings Type](https://developers.google.com/ad-manager/api/reference/v202511/AdjustmentService.HistoricalBasisVolumeSettings) - Historical basis configuration
- [ForecastAdjustmentStatus Enum](https://developers.google.com/ad-manager/api/reference/v202511/AdjustmentService.ForecastAdjustmentStatus) - Adjustment status values
- [ForecastAdjustmentVolumeType Enum](https://developers.google.com/ad-manager/api/reference/v202511/AdjustmentService.ForecastAdjustmentVolumeType) - Volume type values
- [DateRange Type](https://developers.google.com/ad-manager/api/reference/v202511/AdjustmentService.DateRange) - Date range object
- [Date Type](https://developers.google.com/ad-manager/api/reference/v202511/AdjustmentService.Date) - Date object

#### Guides and Concepts

- [Forecasting Guide](https://developers.google.com/ad-manager/api/forecasting) - Overview of forecasting capabilities
- [Create and Manage Yield Groups](https://support.google.com/admanager/answer/7390828) - UI guide for yield groups
- [Add Forecast Adjustments](https://support.google.com/admanager/answer/9080424) - UI guide for adjustments
- [About Forecast Adjustments](https://support.google.com/admanager/answer/9144207) - Conceptual overview
- [Forecast Adjustment Limitations](https://support.google.com/admanager/answer/9144209) - Constraints and limits
- [Yield Group Reporting](https://support.google.com/admanager/table/7575094) - Available metrics

### Client Libraries

- [Python Client Library (googleads-python-lib)](https://github.com/googleads/googleads-python-lib) - Official Python library
- [Client Libraries & Example Code](https://developers.google.com/ad-manager/api/clients) - All supported languages
- [Best Practices](https://developers.google.com/ad-manager/api/bestpractices) - API usage guidelines

### Related Services

- [ForecastService (v202511)](https://developers.google.com/ad-manager/api/reference/v202511/ForecastService) - Traffic and availability forecasting
- [CompanyService (v202511)](https://developers.google.com/ad-manager/api/reference/v202511/CompanyService) - Managing yield partner companies
- [InventoryService (v202511)](https://developers.google.com/ad-manager/api/reference/v202511/InventoryService) - Ad unit management
- [NetworkService (v202511)](https://developers.google.com/ad-manager/api/reference/v202511/NetworkService) - Network configuration

### WSDL Endpoints

For direct SOAP integration:

```
YieldGroupService:
https://ads.google.com/apis/ads/publisher/v202511/YieldGroupService?wsdl

AdjustmentService:
https://ads.google.com/apis/ads/publisher/v202511/AdjustmentService?wsdl
```

---

*This documentation is based on Google Ad Manager SOAP API v202511 (released November 2025). Field definitions and descriptions are sourced directly from the official Google API reference documentation. For the most current information, always refer to the official Google documentation.*
