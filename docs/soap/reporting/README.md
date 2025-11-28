# Google Ad Manager SOAP API - Reporting Category (v202511)

## Table of Contents

1. [Overview](#overview)
2. [Report Types](#report-types)
3. [Report Workflow](#report-workflow)
4. [Services Reference](#services-reference)
   - [ReportService](#reportservice)
   - [PublisherQueryLanguageService](#publisherquerylanguageservice)
   - [ForecastService](#forecastservice)
5. [Data Models](#data-models)
6. [Dimensions Reference](#dimensions-reference)
7. [Metrics Reference](#metrics-reference)
8. [Dimension Attributes](#dimension-attributes)
9. [Date Ranges](#date-ranges)
10. [Publisher Query Language (PQL)](#publisher-query-language-pql)
11. [Forecasting](#forecasting)
12. [Python Code Examples](#python-code-examples)
13. [Common Report Patterns](#common-report-patterns)
14. [Best Practices](#best-practices)
15. [Troubleshooting](#troubleshooting)

---

## Overview

The Reporting category in the Google Ad Manager SOAP API provides comprehensive tools for extracting performance data, generating forecasts, and querying system data. This category includes three key services:

| Service | Purpose |
|---------|---------|
| **ReportService** | Execute reports on ad campaigns, networks, inventory, and sales |
| **PublisherQueryLanguageService** | Query system data using SQL-like syntax (PQL) |
| **ForecastService** | Predict inventory availability and delivery performance |

### Key Capabilities

- **Historical Reporting**: Analyze past performance with 600+ metrics
- **Real-time Reporting**: Access near-real-time delivery data
- **Reach Reporting**: Unique audience measurement with Nielsen integration
- **Forecasting**: Predict inventory availability and delivery outcomes
- **Custom Queries**: Extract entity data using Publisher Query Language
- **Saved Queries**: Reuse reports created in the Ad Manager UI

### API Endpoint

```
https://ads.google.com/apis/ads/publisher/v202511
```

### WSDL Locations

```
https://ads.google.com/apis/ads/publisher/v202511/ReportService?wsdl
https://ads.google.com/apis/ads/publisher/v202511/PublisherQueryLanguageService?wsdl
https://ads.google.com/apis/ads/publisher/v202511/ForecastService?wsdl
```

---

## Report Types

Google Ad Manager supports multiple report types, each designed for specific use cases:

### Historical Reports

Standard reports analyzing past performance data.

| Report Category | Description | Key Dimensions |
|-----------------|-------------|----------------|
| **Delivery** | Impressions, clicks, CTR, revenue | DATE, LINE_ITEM_ID, ORDER_ID |
| **Revenue** | CPM, CPC, and total revenue analysis | ADVERTISER_ID, SALESPERSON_ID |
| **Inventory** | Ad unit and placement performance | AD_UNIT_ID, PLACEMENT_ID |
| **Video** | Video ad performance and viewership | POSITION_OF_POD, VIDEO_AD_TYPE |
| **Programmatic** | Exchange and deals performance | PROGRAMMATIC_CHANNEL_ID, YIELD_GROUP_ID |

### Reach Reports

Measure unique audience reach (requires Nielsen integration for full metrics).

| Metric Type | Description |
|-------------|-------------|
| **Unique Reach** | Number of distinct users reached |
| **Frequency** | Average impressions per user |
| **GRP (Gross Rating Points)** | Audience volume measurement |

**Note**: Reach reports require `DateRangeType.REACH_LIFETIME` (last 93 days).

### Future Sell-Through Reports

Forecast future inventory availability.

| Metric | Description |
|--------|-------------|
| Future sell-through rate | Percentage of forecasted impressions already reserved |
| Available impressions | Projected available inventory |
| Reserved impressions | Already booked inventory |

### Real-Time Reports

Near-real-time delivery data with limited dimension support.

| Use Case | Typical Latency |
|----------|-----------------|
| Live event monitoring | 15-30 minutes |
| Troubleshooting delivery | Near real-time |

### Ad Speed Reports

Measure ad loading performance and page speed impact.

| Metric Category | Examples |
|-----------------|----------|
| Creative load time | 0-500ms, 500ms-1s, 1s-2s, etc. |
| Page navigation time | Time from page load to first ad request |

---

## Report Workflow

### Standard Workflow Diagram

```
+------------------+     +-------------------+     +------------------+
|  Create Report   | --> |   Poll Status     | --> | Download Report  |
|  (runReportJob)  |     | (getReportJob     |     | (getReportDown   |
|                  |     |     Status)       |     |    loadURL)      |
+------------------+     +-------------------+     +------------------+
         |                       |                         |
         v                       v                         v
    ReportJob ID           IN_PROGRESS /              Report URL
                           COMPLETED /                (gzip archive)
                           FAILED
```

### Step-by-Step Process

#### Step 1: Create Report Query

Build a `ReportQuery` object specifying dimensions, metrics, filters, and date range.

#### Step 2: Run Report Job

Submit the query using `runReportJob()`. Returns a `ReportJob` with a server-assigned ID.

#### Step 3: Poll for Completion

Repeatedly call `getReportJobStatus()` until status is `COMPLETED` or `FAILED`.

**Recommended polling interval**: Start at 5 seconds, increase exponentially up to 60 seconds.

#### Step 4: Download Results

Call `getReportDownloadURL()` or `getReportDownloadUrlWithOptions()` to get the download URL.

#### Step 5: Parse Report

Download and decompress the gzip archive. Parse based on selected export format.

### Report Job Status Values

| Status | Description |
|--------|-------------|
| `IN_PROGRESS` | Report is being generated |
| `COMPLETED` | Report is ready for download |
| `FAILED` | Report generation failed |

---

## Services Reference

### ReportService

The primary service for executing reports and retrieving performance data.

**WSDL**: `https://ads.google.com/apis/ads/publisher/v202511/ReportService?wsdl`

#### Methods

##### runReportJob

Initiates the execution of a report.

| Parameter | Type | Description |
|-----------|------|-------------|
| `reportJob` | `ReportJob` | Contains the `ReportQuery` with dimensions, columns, and filters |

| Returns | Description |
|---------|-------------|
| `ReportJob` | Same object with server-assigned `id` field populated |

**Notes**:
- The `reportQuery` field must be populated
- Report execution is asynchronous

---

##### getReportJobStatus

Returns the current status of a report job.

| Parameter | Type | Description |
|-----------|------|-------------|
| `reportJobId` | `xsd:long` | The ID returned from `runReportJob` |

| Returns | Description |
|---------|-------------|
| `ReportJobStatus` | One of: `IN_PROGRESS`, `COMPLETED`, `FAILED` |

---

##### getReportDownloadURL

Returns the URL to download the completed report.

| Parameter | Type | Description |
|-----------|------|-------------|
| `reportJobId` | `xsd:long` | The completed report job ID |
| `exportFormat` | `ExportFormat` | Output format (CSV_DUMP, TSV, XML, XLSX, TSV_EXCEL) |

| Returns | Description |
|---------|-------------|
| `xsd:string` | URL to download the report (gzip compressed by default) |

---

##### getReportDownloadUrlWithOptions

Returns the download URL with additional options.

| Parameter | Type | Description |
|-----------|------|-------------|
| `reportJobId` | `xsd:long` | The completed report job ID |
| `reportDownloadOptions` | `ReportDownloadOptions` | Configuration for download |

| Returns | Description |
|---------|-------------|
| `xsd:string` | URL to download the report |

**ReportDownloadOptions Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `exportFormat` | `ExportFormat` | Output format |
| `includeReportProperties` | `boolean` | Include metadata header |
| `includeTotalsRow` | `boolean` | Include summary totals |
| `useGzipCompression` | `boolean` | Enable/disable gzip compression |

---

##### getSavedQueriesByStatement

Retrieves saved queries created or shared with the current user.

| Parameter | Type | Description |
|-----------|------|-------------|
| `filterStatement` | `Statement` | PQL filter for selecting queries |

| Returns | Description |
|---------|-------------|
| `SavedQueryPage` | Page of matching saved queries |

**Notes**:
- Saved queries from the UI may not be API-compatible
- Check `isCompatibleWithApiVersion` before using
- Query ID is visible in the UI URL when viewing a saved report

---

### PublisherQueryLanguageService

Provides SQL-like querying for system entities.

**WSDL**: `https://ads.google.com/apis/ads/publisher/v202511/PublisherQueryLanguageService?wsdl`

#### Methods

##### select

Retrieves rows of data based on a PQL statement.

| Parameter | Type | Description |
|-----------|------|-------------|
| `selectStatement` | `Statement` | PQL SELECT query |

| Returns | Description |
|---------|-------------|
| `ResultSet` | Query results with column headers and typed values |

**Example Query**:
```sql
SELECT Id, Name, Status FROM Line_Item WHERE OrderId = 12345
```

---

### ForecastService

Provides inventory forecasting capabilities.

**WSDL**: `https://ads.google.com/apis/ads/publisher/v202511/ForecastService?wsdl`

#### Methods

##### getAvailabilityForecast

Gets availability forecast for a prospective line item.

| Parameter | Type | Description |
|-----------|------|-------------|
| `lineItem` | `ProspectiveLineItem` | Unsaved line item to forecast |
| `forecastOptions` | `AvailabilityForecastOptions` | Forecast configuration |

| Returns | Description |
|---------|-------------|
| `AvailabilityForecast` | Availability data including matched, available, and possible units |

---

##### getAvailabilityForecastById

Gets availability forecast for an existing line item.

| Parameter | Type | Description |
|-----------|------|-------------|
| `lineItemId` | `xsd:long` | ID of existing line item |
| `forecastOptions` | `AvailabilityForecastOptions` | Forecast configuration |

| Returns | Description |
|---------|-------------|
| `AvailabilityForecast` | Availability data for the line item |

**Supported Line Item Types**: `SPONSORSHIP`, `STANDARD`

---

##### getDeliveryForecast

Gets delivery forecast for multiple prospective line items.

| Parameter | Type | Description |
|-----------|------|-------------|
| `lineItems` | `ProspectiveLineItem[]` | Array of unsaved line items |
| `forecastOptions` | `DeliveryForecastOptions` | Forecast configuration |

| Returns | Description |
|---------|-------------|
| `DeliveryForecast` | Predicted delivery for all line items |

**Key Difference**: Simulates competition between line items for accurate delivery predictions.

---

##### getDeliveryForecastByIds

Gets delivery forecast for existing line items.

| Parameter | Type | Description |
|-----------|------|-------------|
| `lineItemIds` | `xsd:long[]` | Array of line item IDs |
| `forecastOptions` | `DeliveryForecastOptions` | Forecast configuration |

| Returns | Description |
|---------|-------------|
| `DeliveryForecast` | Predicted delivery for specified line items |

---

##### getTrafficData

Retrieves historical and forecasted traffic data.

| Parameter | Type | Description |
|-----------|------|-------------|
| `trafficDataRequest` | `TrafficDataRequest` | Traffic data specification |

| Returns | Description |
|---------|-------------|
| `TrafficDataResponse` | Historical and forecasted traffic metrics |

**Note**: Available only for Ad Manager 360 networks.

---

## Data Models

### ReportJob

Represents a report execution request. The `ReportJob` object is defined in the namespace `https://www.google.com/apis/ads/publisher/v202511` and is used by the ReportService's `runReportJob()` method.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `xsd:long` | Read-only | Server-assigned unique identifier. This value is read-only and is assigned by Google when the report is created. |
| `reportQuery` | `ReportQuery` | **Yes** | Holds the filtering criteria for the report. Must be populated before calling `runReportJob()`. |

---

### ReportJobStatus

The status of a report job execution.

| Value | Description |
|-------|-------------|
| `IN_PROGRESS` | Report job is currently executing on the server |
| `COMPLETED` | Report job finished successfully and is ready for download |
| `FAILED` | Report job failed to complete; cannot be downloaded |

---

### ReportQuery

Defines the complete report parameters. A `ReportQuery` object allows you to specify the selection criteria for generating a report. Only reports with at least one `Column` are supported.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `dimensions` | `Dimension[]` | **Yes** | The list of break-down types being requested in the report. Must include at least one dimension. |
| `dimensionAttributes` | `DimensionAttribute[]` | No | Additional metadata fields associated with dimensions (e.g., `LINE_ITEM_START_DATE_TIME`). |
| `columns` | `Column[]` | **Yes** | The list of trafficking statistics and revenue information (metrics) being requested. Must contain at least one column. |
| `dateRangeType` | `DateRangeType` | **Yes** | Predefined or custom date range for the report. |
| `startDate` | `Date` | Conditional | Custom start date. Required when `dateRangeType` is `CUSTOM_DATE`. |
| `endDate` | `Date` | Conditional | Custom end date. Required when `dateRangeType` is `CUSTOM_DATE`. |
| `statement` | `Statement` | No | PQL filter statement for filtering dimensions. |
| `adUnitView` | `AdUnitView` | No | Specifies how ad unit hierarchy is presented in results. Defaults to `TOP_LEVEL`. |
| `timeZoneType` | `TimeZoneType` | No | Timezone for date/time dimension breakdowns. Defaults to `PUBLISHER`. |
| `customFieldIds` | `xsd:long[]` | No | List of custom field IDs to include as dimensions. |
| `customDimensionKeyIds` | `xsd:long[]` | No | List of custom dimension key IDs for custom targeting dimensions. |
| `contentMetadataKeyHierarchyCustomTargetingKeyIds` | `xsd:long[]` | No | List of content metadata key hierarchy custom targeting key IDs. |
| `cmsMetadataKeyIds` | `xsd:long[]` | No | List of CMS metadata key IDs for content-based reporting. |
| `useSalesLocalTimeZone` | `xsd:boolean` | No | Whether to use the sales team's local timezone for date breakdowns. |
| `includeZeroSalesRows` | `xsd:boolean` | No | Whether to include rows with zero sales data. |
| `reportCurrency` | `xsd:string` | No | Three-letter currency code (e.g., `USD`, `EUR`) for revenue reporting. |

---

### Date

Represents a date for report date ranges.

| Field | Type | Description |
|-------|------|-------------|
| `year` | `xsd:int` | Year (e.g., 2024) |
| `month` | `xsd:int` | Month (1-12) |
| `day` | `xsd:int` | Day of month (1-31) |

---

### AdUnitView Enum

Specifies how ad unit hierarchy is presented in report results.

| Value | Description |
|-------|-------------|
| `TOP_LEVEL` | Only the top level ad units. Metrics include events for their descendants that are not filtered out. Best for summary reports. |
| `FLAT` | All the ad units. Metrics do not include events for the descendants. Each ad unit appears as a separate row. |
| `HIERARCHICAL` | Generates reports using the ad unit hierarchy structure. Replaces standard ad unit columns with numbered levels ("Ad unit 1", "Ad unit 2", etc.), displaying "N/A" when a level does not apply to a row. Like FLAT, metrics exclude descendant events. |

---

### TimeZoneType Enum

Specifies the timezone used for time-based dimension breakdowns.

| Value | Description | Compatible Dimensions |
|-------|-------------|----------------------|
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. | N/A |
| `PUBLISHER` | Use the publisher's network timezone. Compatible with all metrics in Ad Manager reports. | `DATE`, `WEEK`, `MONTH_AND_YEAR`, `DAY`, `HOUR` |
| `PACIFIC` | Use Pacific Time (PT) timezone. Only compatible with Ad Exchange metrics in Historical report type. | `DATE_PT`, `WEEK_PT`, `MONTH_YEAR_PT`, `DAY_OF_WEEK_PT` |

---

### DateRangeType Enum

Specifies the time period for report data. Use `CUSTOM_DATE` for specific date ranges.

#### Historical Date Ranges

| Value | Description |
|-------|-------------|
| `TODAY` | The current day. |
| `YESTERDAY` | The previous day. |
| `LAST_WEEK` | The last week, from Monday to Sunday. |
| `LAST_MONTH` | The previous calendar month. |
| `LAST_3_MONTHS` | The last 3 full months. For example, May 5, 2024 would span February 1 to April 30. |
| `REACH_LIFETIME` | The last 93 days. **Required** for reach-related columns (`UNIQUE_REACH_IMPRESSIONS`, `UNIQUE_REACH_FREQUENCY`, `UNIQUE_REACH`). |
| `CUSTOM_DATE` | Custom date range. Requires `startDate` and `endDate` to be specified in the `ReportQuery`. |

#### Future Date Ranges (for Forecasting Reports)

| Value | Description |
|-------|-------------|
| `NEXT_DAY` | The next day. |
| `NEXT_WEEK` | The next week, from Monday to Sunday. |
| `NEXT_MONTH` | The next calendar month. |
| `NEXT_QUARTER` | The next fiscal quarter. |
| `NEXT_90_DAYS` | The next ninety days. |
| `NEXT_3_MONTHS` | The next three months. |
| `NEXT_12_MONTHS` | The next twelve months. |
| `CURRENT_AND_NEXT_MONTH` | Beginning of the next day until the end of the next month. |

---

### ExportFormat Enum

The file formats available for downloading report results.

| Value | Description | Best For |
|-------|-------------|----------|
| `TSV` | Tab-separated values. | General purpose text processing |
| `TSV_EXCEL` | Tab-separated values formatted for Excel. | Opening directly in Excel |
| `CSV_DUMP` | Comma-separated output for automated processing. Uses qualified column headers, micros for currency values, and ISO 8601 for dates. No formatting. | Automated/programmatic processing |
| `XML` | XML format. | XML-based data processing |
| `XLSX` | Office Open XML spreadsheet designed for Excel 2007+. | Modern Excel with formatting |

---

### ReportDownloadOptions

Configuration options for downloading report results.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `exportFormat` | `ExportFormat` | - | The output format for the report file. |
| `includeReportProperties` | `xsd:boolean` | `false` | Whether to include report metadata header in the output. |
| `includeTotalsRow` | `xsd:boolean` | `false` | Whether to include a summary totals row at the end. |
| `useGzipCompression` | `xsd:boolean` | `true` | Whether to compress the report file using gzip. |

---

### SavedQuery

Represents a report query saved in the Ad Manager UI that can be retrieved and executed via API.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `xsd:long` | Unique identifier for the saved query. Visible in the UI URL when viewing a saved report. |
| `name` | `xsd:string` | Display name of the saved query. |
| `reportQuery` | `ReportQuery` | The query specification. Will be `null` if the query is not compatible with the current API version. |
| `isCompatibleWithApiVersion` | `xsd:boolean` | Whether the saved query can be used via the current API version. **Always check this before using the query.** |

**Important Notes**:
- Saved queries from the UI may use features not supported by the API
- The query ID is visible in the UI URL when viewing a saved report
- Always verify `isCompatibleWithApiVersion` before attempting to run a saved query

---

### Statement

Captures the WHERE, ORDER BY, and LIMIT clauses of a PQL query for filtering report data.

| Field | Type | Description |
|-------|------|-------------|
| `query` | `xsd:string` | The PQL query string (e.g., `WHERE Status = :status`). |
| `values` | `String_ValueMapEntry[]` | Array of bind variable name-value pairs for parameterized queries. |

**Statement Example**:
```python
statement = {
    'query': "WHERE LINE_ITEM_ID = :lineItemId AND ORDER_ID = :orderId",
    'values': [
        {'key': 'lineItemId', 'value': {'numberValue': 12345}},
        {'key': 'orderId', 'value': {'numberValue': 67890}}
    ]
}
```

---

### AvailabilityForecast

Reports the maximum number of available units with which a line item can be booked. This forecast is analogous to the "check inventory" feature in the Ad Manager UI.

| Field | Type | Description |
|-------|------|-------------|
| `lineItemId` | `xsd:long` | Uniquely identifies this availability forecast. Read-only, assigned by Google when forecast is created. Null for prospective line items. |
| `orderId` | `xsd:long` | Identifier for the associated Order. Null for prospective line items without an order ID set. |
| `unitType` | `UnitType` | The unit with which the goal or cap of the LineItem is defined. See UnitType enum below. |
| `availableUnits` | `xsd:long` | The number of units that can be booked without affecting the delivery of any reserved line items. |
| `deliveredUnits` | `xsd:long` | Units already served if the reservation is currently active. |
| `matchedUnits` | `xsd:long` | The number of units that match the specified targeting and delivery settings. |
| `possibleUnits` | `xsd:long` | The maximum number of units that could be booked by taking inventory away from lower priority items. |
| `reservedUnits` | `xsd:long` | The number of reserved units requested, as absolute or percentage value. |
| `breakdowns` | `ForecastBreakdown[]` | Breakdowns for each time window defined in `ForecastBreakdownOptions`. |
| `targetingCriteriaBreakdowns` | `TargetingCriteriaBreakdown[]` | Forecast results segmented by line item targeting. Only populated if `includeTargetingCriteriaBreakdown` is `true` in options. |
| `contendingLineItems` | `ContendingLineItem[]` | List of competing line items for this forecast. Only populated if `includeContendingLineItems` is `true` in options. |
| `alternativeUnitTypeForecasts` | `AlternativeUnitTypeForecast[]` | Alternative unit type views of this forecast (e.g., impressions vs. clicks). |
| `demographicBreakdowns` | `GrpDemographicBreakdown[]` | Demographic breakdowns for GRP-enabled forecasts. |

#### UnitType Enum

| Value | Description |
|-------|-------------|
| `IMPRESSIONS` | Impression-based goals |
| `CLICKS` | Click-based goals |
| `CLICK_THROUGH_CPA_CONVERSIONS` | Click-through CPA conversion goals |
| `VIEW_THROUGH_CPA_CONVERSIONS` | View-through CPA conversion goals |
| `TOTAL_CPA_CONVERSIONS` | Total CPA conversion goals |
| `VIEWABLE_IMPRESSIONS` | Viewable impression goals |
| `IN_TARGET_IMPRESSIONS` | In-target impression goals (GRP) |
| `COMPLETED_VIEWS` | Completed video view goals |
| `UNKNOWN` | Unknown unit type |

---

### DeliveryForecast

Results from a delivery forecast.

| Field | Type | Description |
|-------|------|-------------|
| `lineItemDeliveryForecasts` | `LineItemDeliveryForecast[]` | Per-line-item delivery predictions |

---

### LineItemDeliveryForecast

Delivery prediction for a single line item.

| Field | Type | Description |
|-------|------|-------------|
| `lineItemId` | `xsd:long` | Line item ID (null for prospective) |
| `orderId` | `xsd:long` | Order ID (null for prospective) |
| `unitType` | `UnitType` | Measurement unit |
| `predictedDeliveryUnits` | `xsd:long` | Units expected to be delivered |
| `deliveredUnits` | `xsd:long` | Units already served |
| `matchedUnits` | `xsd:long` | Units matching targeting |

---

## Dimensions Reference

Dimensions define how report data is grouped and broken down. The v202511 API provides 200+ dimensions organized into categories. Dimensions support specific report types: Historical, Future sell-through, Reach, Ad speed, Real-time video, YouTube consolidated, Partner finance, and Ad Connector.

### Time Dimensions

| Dimension | Description | Filterable | Format |
|-----------|-------------|------------|--------|
| `DATE` | Daily breakdown in network timezone | Yes (ISO 8601 `YYYY-MM-DD`) | YYYY-MM-DD |
| `WEEK` | Weekly breakdown | No | Week number |
| `MONTH_AND_YEAR` | Monthly grouping in network timezone | Yes (ISO 4601 `YYYY-MM`) | MMMM YYYY |
| `DAY` | Day of week grouping (1=Monday to 7=Sunday) | Yes (day index) | Day name |
| `HOUR` | Hourly breakdown (0-23) | Yes (hour number) | 0-23 |
| `DATE_PT` | Daily breakdown in Pacific Time | Yes | YYYY-MM-DD |
| `WEEK_PT` | Weekly breakdown in Pacific Time | No | Week number |
| `MONTH_YEAR_PT` | Monthly breakdown in Pacific Time | Yes | MMMM YYYY |
| `DAY_OF_WEEK_PT` | Day of week in Pacific Time | Yes | Day name |

### Line Item Dimensions

| Dimension | Description | Filterable | Notes |
|-----------|-------------|------------|-------|
| `LINE_ITEM_ID` | Line item numeric ID | Yes | Auto-includes `LINE_ITEM_NAME` |
| `LINE_ITEM_NAME` | Line item display name | Yes | Auto-includes `LINE_ITEM_ID` |
| `LINE_ITEM_TYPE` | Type classification (Standard, Sponsorship, etc.) | Yes | |

### Order Dimensions

| Dimension | Description | Filterable | Notes |
|-----------|-------------|------------|-------|
| `ORDER_ID` | Order numeric ID | Yes | Auto-includes `ORDER_NAME` |
| `ORDER_NAME` | Order display name | Yes | Auto-includes `ORDER_ID` |
| `ORDER_DELIVERY_STATUS` | Delivery progress status | Filter only | Values: `STARTED`, `NOT_STARTED`, `COMPLETED` |

### Advertiser & Company Dimensions

| Dimension | Description | Filterable |
|-----------|-------------|------------|
| `ADVERTISER_ID` | Advertiser company ID | Yes |
| `ADVERTISER_NAME` | Advertiser company name | Yes |
| `CLASSIFIED_ADVERTISER_ID` | Classified advertiser ID | Yes |
| `CLASSIFIED_ADVERTISER_NAME` | Classified advertiser name | Yes |
| `BUYING_AGENCY_NAME` | Agency identification | Yes |
| `ADVERTISER_VERTICAL_NAME` | Vertical categorization | Yes |
| `ADVERTISER_DOMAIN_NAME` | Advertiser domain grouping | Yes |

### Creative Dimensions

| Dimension | Description | Filterable | Notes |
|-----------|-------------|------------|-------|
| `CREATIVE_ID` | Creative numeric ID | Yes | |
| `CREATIVE_NAME` | Creative display name | Yes | |
| `CREATIVE_TYPE` | Creative type (Image, Video, etc.) | Yes | |
| `CREATIVE_BILLING_TYPE` | Billing methodology categorization | Yes | |
| `CREATIVE_SIZE` | Creative dimensions (WxH) | No | |
| `CREATIVE_SIZE_DELIVERED` | Actual delivered creative size | No | |
| `MASTER_COMPANION_CREATIVE_ID` | Creative set ID | Yes | |
| `MASTER_COMPANION_CREATIVE_NAME` | Creative set name | Yes | |

### Inventory Dimensions

| Dimension | Description | Filterable | Notes |
|-----------|-------------|------------|-------|
| `AD_UNIT_ID` | Ad unit numeric ID | Yes | Auto-includes `AD_UNIT_NAME` |
| `AD_UNIT_NAME` | Ad unit display name | Yes | |
| `AD_UNIT_STATUS` | Ad unit status | Filter only | Not reportable as dimension |
| `PARENT_AD_UNIT_ID` | Parent ad unit ID | Filter only | For descendant filtering |
| `PARENT_AD_UNIT_NAME` | Parent ad unit name | Filter only | For descendant filtering |
| `PLACEMENT_ID` | Placement numeric ID | Yes | |
| `PLACEMENT_NAME` | Placement display name | Yes | |
| `PLACEMENT_STATUS` | Placement status | Filter only | |
| `INVENTORY_FORMAT` | Format classification | Yes | |
| `INVENTORY_FORMAT_NAME` | Format display name | Yes | |
| `REQUESTED_AD_SIZES` | Requested size chain | No | |
| `AD_REQUEST_AD_UNIT_SIZES` | Requested size specifications | No | |

### Geographic Dimensions

| Dimension | Description | Filterable |
|-----------|-------------|------------|
| `COUNTRY_CRITERIA_ID` | Country targeting criteria ID | Yes |
| `COUNTRY_CODE` | ISO 2-letter country code | Yes |
| `COUNTRY_NAME` | Country display name | Yes |
| `REGION_CRITERIA_ID` | Region/state targeting ID | Yes |
| `REGION_NAME` | Region/state display name | Yes |
| `CITY_CRITERIA_ID` | City targeting criteria ID | Yes |
| `CITY_NAME` | City display name | Yes |
| `METRO_CRITERIA_ID` | Metro/DMA area ID | Yes |
| `METRO_NAME` | Metro/DMA area name | Yes |
| `POSTAL_CODE_CRITERIA_ID` | Postal code criteria ID | Yes |
| `POSTAL_CODE` | Postal code value | Yes |

### Device & Technology Dimensions

| Dimension | Description | Filterable |
|-----------|-------------|------------|
| `DEVICE_CATEGORY_ID` | Device category ID | Yes |
| `DEVICE_CATEGORY_NAME` | Device type (Desktop, Mobile, Tablet, Connected TV) | Yes |
| `BROWSER_NAME` | Browser name | Yes |
| `OPERATING_SYSTEM_VERSION_ID` | OS version ID | Yes |
| `OPERATING_SYSTEM_VERSION_NAME` | OS name and version | Yes |
| `MOBILE_DEVICE_NAME` | Mobile device model name | Yes |
| `MOBILE_INVENTORY_TYPE` | Mobile inventory classification | Yes |
| `MOBILE_APP_RESOLVED_ID` | Mobile app ID | Yes |
| `MOBILE_APP_RESOLVED_NAME` | Mobile app name | Yes |
| `BANDWIDTH_ID` | Connection speed ID | Yes |
| `BANDWIDTH_NAME` | Connection speed category | Yes |
| `CARRIER_ID` | Mobile carrier ID | Yes |
| `CARRIER_NAME` | Mobile carrier name | Yes |

### Targeting & Audience Dimensions

| Dimension | Description | Filterable | Notes |
|-----------|-------------|------------|-------|
| `CUSTOM_TARGETING_VALUE_ID` | Custom key-value pair IDs | Yes | |
| `CUSTOM_CRITERIA` | Custom targeting display | Yes | Supports EXACT, BROAD, PREFIX matching |
| `CUSTOM_DIMENSION` | Marked custom targeting keys | Yes | Requires key ID specification |
| `TARGETING` | Predefined targeting criteria (OS, browser, etc.) | No | |
| `TARGETING_TYPE_CODE` | Targeting methodology code | Yes | |
| `TARGETING_TYPE_NAME` | Targeting methodology name | Yes | |
| `AD_REQUEST_CUSTOM_CRITERIA` | Custom criteria from requests | No | |
| `AUDIENCE_SEGMENT_ID` | Billable audience segment ID | Yes | |
| `AUDIENCE_SEGMENT_NAME` | Audience segment name | Yes | |
| `AUDIENCE_SEGMENT_DATA_PROVIDER_NAME` | Data provider name | Yes | |

### Video Dimensions

| Dimension | Description | Filterable | Values |
|-----------|-------------|------------|--------|
| `VIDEO_FALLBACK_POSITION` | Fallback positioning | Yes | `NON_FALLBACK`, `FALLBACK_POSITION_1`, etc. |
| `POSITION_OF_POD` | Pod placement in content | Yes | `PREROLL`, `POSTROLL`, `MIDROLL` variants |
| `POSITION_IN_POD` | Position within pod | Yes | `UNKNOWN_POSITION`, `POSITION_1`, etc. |
| `VIDEO_VAST_VERSION` | VAST specification version | Yes | |
| `VIDEO_AD_REQUEST_DURATION_ID` | Request duration category ID | Yes | |
| `VIDEO_AD_REQUEST_DURATION` | Request duration value | Yes | |
| `VIDEO_PLCMT_ID` | IAB video placement type ID | Yes | |
| `VIDEO_PLCMT_NAME` | IAB video placement type name | Yes | |
| `VIDEO_AD_DURATION` | Ad duration categorization | Yes | |
| `VIDEO_AD_TYPE_ID` | Video ad type ID | Yes | |
| `VIDEO_AD_TYPE_NAME` | Video ad type name | Yes | |
| `VIDEO_BREAK_TYPE` | Break categorization code | Yes | |
| `VIDEO_BREAK_TYPE_NAME` | Break categorization name | Yes | |
| `VIDEO_REDIRECT_THIRD_PARTY` | Video redirect vendor | Yes | |

### Programmatic Dimensions

| Dimension | Description | Filterable |
|-----------|-------------|------------|
| `PROGRAMMATIC_BUYER_ID` | Programmatic buyer account ID | Yes |
| `PROGRAMMATIC_BUYER_NAME` | Programmatic buyer name | Yes |
| `PROGRAMMATIC_CHANNEL_ID` | Transaction type ID | Yes |
| `PROGRAMMATIC_CHANNEL_NAME` | Transaction type name (Open Auction, PMP, etc.) | Yes |
| `PROGRAMMATIC_DEAL_ID` | Deal ID | Yes |
| `PROGRAMMATIC_DEAL_NAME` | Deal name | Yes |
| `EXCHANGE_BIDDING_DEAL_ID` | Exchange bidding deal ID | Yes |
| `EXCHANGE_BIDDING_DEAL_TYPE` | Exchange bidding deal type | Yes |
| `IS_FIRST_LOOK_DEAL` | First Look traffic indicator (boolean) | Yes |
| `IS_ADX_DIRECT` | Ad Exchange Direct traffic indicator | Yes |
| `BUYER_NETWORK_ID` | Buyer network ID | Yes |
| `BUYER_NETWORK_NAME` | Buyer network name | Yes |
| `BIDDER_ID` | Bidder ID | Yes |
| `BIDDER_NAME` | Bidder name | Yes |

### Yield & Pricing Dimensions

| Dimension | Description | Filterable |
|-----------|-------------|------------|
| `YIELD_GROUP_ID` | Yield optimization group ID | Yes |
| `YIELD_GROUP_NAME` | Yield group name | Yes |
| `YIELD_PARTNER` | Yield partner identification | Yes |
| `YIELD_PARTNER_TAG` | Yield partner tag | Yes |
| `CLASSIFIED_YIELD_PARTNER_NAME` | Detected yield partner name | Yes |
| `UNIFIED_PRICING_RULE_ID` | Unified pricing rule ID | Yes |
| `UNIFIED_PRICING_RULE_NAME` | Unified pricing rule name | Yes |
| `FIRST_LOOK_PRICING_RULE_ID` | First-look pricing rule ID | Yes |
| `FIRST_LOOK_PRICING_RULE_NAME` | First-look pricing rule name | Yes |
| `BID_RANGE` | Bid range bucket ($0.10 increments) | Yes |
| `BID_REJECTION_REASON_ID` | Auction non-participation reason ID | Yes |
| `BID_REJECTION_REASON_NAME` | Auction non-participation reason | Yes |

### Sales & Operations Dimensions

| Dimension | Description | Filterable |
|-----------|-------------|------------|
| `SALESPERSON_ID` | Salesperson user ID | Yes |
| `SALESPERSON_NAME` | Salesperson name | Yes |
| `REQUEST_TYPE` | Ad request type categorization | Yes |
| `DOMAIN` | Top private domain grouping | Yes |
| `SITE_NAME` | Publisher site grouping | Yes |
| `CHANNEL_NAME` | Channel-based classification | Yes |
| `URL_ID` | URL ID | Yes |
| `URL_NAME` | URL name | Yes |
| `SERVING_RESTRICTION_ID` | Serving restriction ID | Yes |
| `SERVING_RESTRICTION_NAME` | Serving restriction name | Yes |

### Content Dimensions

| Dimension | Description | Filterable | Notes |
|-----------|-------------|------------|-------|
| `CONTENT_ID` | Content identifier | Yes | |
| `CONTENT_NAME` | Content name | Yes | |
| `CONTENT_BUNDLE_ID` | Content bundle/package ID | Yes | |
| `CONTENT_BUNDLE_NAME` | Content bundle name | Yes | |
| `CMS_METADATA` | CMS metadata key-values | Yes | Requires CMS metadata key specification |

### Ad Technology & Vendor Dimensions

| Dimension | Description | Filterable |
|-----------|-------------|------------|
| `AD_NETWORK_ID` | SDK mediation network ID | Yes |
| `AD_NETWORK_NAME` | SDK mediation network name | Yes |
| `MEDIATION_TYPE` | Web, mobile app, or video mediation | Yes |
| `AD_TECHNOLOGY_PROVIDER_ID` | Ad technology provider ID | Yes |
| `AD_TECHNOLOGY_PROVIDER_NAME` | Ad technology provider name | Yes |
| `AD_TECHNOLOGY_PROVIDER_DOMAIN` | Ad technology provider domain | Yes |
| `TCF_VENDOR_ID` | TCF Global Vendor List ID | Yes |
| `TCF_VENDOR_NAME` | TCF vendor name | Yes |

### Native & Template Dimensions

| Dimension | Description | Filterable |
|-----------|-------------|------------|
| `NATIVE_TEMPLATE_ID` | Native creative template ID | Yes |
| `NATIVE_TEMPLATE_NAME` | Native template name | Yes |
| `NATIVE_STYLE_ID` | Native ad style ID | Yes |
| `NATIVE_STYLE_NAME` | Native ad style name | Yes |

### Custom Events Dimensions

| Dimension | Description | Filterable | Notes |
|-----------|-------------|------------|-------|
| `CUSTOM_EVENT_ID` | Custom event tracking ID | Yes | |
| `CUSTOM_EVENT_NAME` | Custom event name | Yes | |
| `CUSTOM_EVENT_TYPE` | Custom event type | Yes | timer/exit/counter |
| `CUSTOM_SPOT_ID` | Ad rule spot ID | Yes | |
| `CUSTOM_SPOT_NAME` | Ad rule spot name | Yes | |

### Brand & Classification Dimensions

| Dimension | Description | Filterable |
|-----------|-------------|------------|
| `CLASSIFIED_BRAND_ID` | Brand classification ID | Yes |
| `CLASSIFIED_BRAND_NAME` | Brand classification name | Yes |
| `BRANDING_TYPE_CODE` | Brand safety classification code | Yes |
| `BRANDING_TYPE_NAME` | Brand safety classification name | Yes |

### Demographics Dimensions (GRP/Nielsen)

| Dimension | Description | Filterable |
|-----------|-------------|------------|
| `GRP_DEMOGRAPHICS` | Gender/age brackets | Yes |
| `NIELSEN_DEMOGRAPHICS` | Nielsen age/gender segments | Yes |

**GRP_DEMOGRAPHICS Values**: `MALE_13_TO_17`, `MALE_18_TO_24`, `MALE_25_TO_34`, `MALE_35_TO_44`, `MALE_45_TO_54`, `MALE_55_TO_64`, `MALE_65_PLUS`, `FEMALE_13_TO_17`, `FEMALE_18_TO_24`, `FEMALE_25_TO_34`, `FEMALE_35_TO_44`, `FEMALE_45_TO_54`, `FEMALE_55_TO_64`, `FEMALE_65_PLUS`

### Partner Management Dimensions

| Dimension | Description | Filterable |
|-----------|-------------|------------|
| `PARTNER_MANAGEMENT_PARTNER_ID` | Partner company ID | Yes |
| `PARTNER_MANAGEMENT_PARTNER_NAME` | Partner company name | Yes |
| `PARTNER_MANAGEMENT_PARTNER_LABEL_ID` | Partner label ID | Yes |
| `PARTNER_MANAGEMENT_PARTNER_LABEL_NAME` | Partner label name | Yes |
| `PARTNER_MANAGEMENT_ASSIGNMENT_ID` | Partner assignment ID | Yes |
| `PARTNER_MANAGEMENT_ASSIGNMENT_NAME` | Partner assignment name | Yes |
| `CHILD_NETWORK_CODE` | MCM child network code | Yes |
| `CHILD_PARTNER_NAME` | MCM child partner name | Yes |
| `WEB_PROPERTY_CODE` | Web property identification | Yes |

### Inventory Share Dimensions

| Dimension | Description | Filterable |
|-----------|-------------|------------|
| `INVENTORY_SHARE_ASSIGNMENT_ID` | Inventory sharing assignment ID | Yes |
| `INVENTORY_SHARE_ASSIGNMENT_NAME` | Inventory sharing assignment name | Yes |
| `INVENTORY_SHARE_OUTCOME` | Sharing result categorization | Yes |

### Ad Exchange Dimensions

| Dimension | Description | Filterable |
|-----------|-------------|------------|
| `AD_EXCHANGE_PRODUCT_CODE` | Ad Exchange product code | Yes |
| `AD_EXCHANGE_PRODUCT_NAME` | Ad Exchange product name | Yes |
| `AD_EXCHANGE_OPTIMIZATION_TYPE` | Optimization methodology | Yes |
| `DYNAMIC_ALLOCATION_ID` | Dynamic allocation rule ID | Yes |
| `DYNAMIC_ALLOCATION_NAME` | Dynamic allocation rule name | Yes |

### Ad Request Dimensions

| Dimension | Description | Filterable |
|-----------|-------------|------------|
| `AD_TYPE_ID` | Ad format classification ID | Yes |
| `AD_TYPE_NAME` | Ad format classification name | Yes |
| `AD_LOCATION_ID` | Ad placement location ID | Yes |
| `AD_LOCATION_NAME` | Ad placement location name | Yes |
| `DEMAND_CHANNEL_ID` | Demand channel ID | Yes |
| `DEMAND_CHANNEL_NAME` | Demand channel name | Yes |

### Ad Connector (DP) Dimensions

These dimensions support the "Ad Connector" report type with demand-side breakdowns:

| Dimension | Description | Filterable |
|-----------|-------------|------------|
| `DP_DATE` | Ad Connector date grouping | Yes |
| `DP_WEEK` | Ad Connector week grouping | Yes |
| `DP_MONTH_YEAR` | Ad Connector month grouping | Yes |
| `DP_COUNTRY_CRITERIA_ID` | Geographic demand data ID | Yes |
| `DP_COUNTRY_NAME` | Geographic demand country name | Yes |
| `DP_INVENTORY_TYPE` | Inventory categorization | Yes |
| `DP_CREATIVE_SIZE` | Delivered size specifications | No |
| `DP_BRAND_NAME` | Demand-side brand name | Yes |
| `DP_ADVERTISER_NAME` | Demand-side advertiser name | Yes |
| `DP_ADX_BUYER_NETWORK_NAME` | Ad Exchange network name | Yes |
| `DP_MOBILE_DEVICE_NAME` | Mobile device classification | Yes |
| `DP_DEVICE_CATEGORY_NAME` | Device category classification | Yes |
| `DP_TAG_ID` | Tag identifier | Yes |
| `DP_DEAL_ID` | Deal identifier | Yes |
| `DP_APP_ID` | App identifier | Yes |

---

## Metrics Reference

Metrics (columns) represent the data values returned in reports. The v202511 API provides 300+ metrics organized into categories. All monetary values are in publisher currency unless otherwise specified.

### Ad Server Metrics

Core delivery and revenue metrics from the Google Ad Manager ad server.

| Metric | Description |
|--------|-------------|
| `AD_SERVER_IMPRESSIONS` | Number of impressions delivered by the ad server |
| `AD_SERVER_BEGIN_TO_RENDER_IMPRESSIONS` | Begin-to-render impressions from ad server |
| `AD_SERVER_TARGETED_IMPRESSIONS` | Impressions delivered via explicit custom criteria targeting |
| `AD_SERVER_CLICKS` | Number of clicks delivered by ad server |
| `AD_SERVER_TARGETED_CLICKS` | Clicks from custom criteria targeting |
| `AD_SERVER_CTR` | Click-through rate (clicks / impressions) |
| `AD_SERVER_CPM_AND_CPC_REVENUE` | CPM and CPC revenue earned, calculated in publisher currency |
| `AD_SERVER_CPM_AND_CPC_REVENUE_GROSS` | Gross CPM/CPC revenue including pre-rev-share |
| `AD_SERVER_CPD_REVENUE` | Cost-per-day revenue from ad server |
| `AD_SERVER_ALL_REVENUE` | Total revenue from ad server (all cost types) |
| `AD_SERVER_ALL_REVENUE_GROSS` | Gross total revenue including programmatic pre-rev-share |
| `AD_SERVER_WITHOUT_CPD_AVERAGE_ECPM` | Average eCPM excluding CPD ads |
| `AD_SERVER_WITH_CPD_AVERAGE_ECPM` | Average eCPM including all ad types |
| `AD_SERVER_UNFILTERED_IMPRESSIONS` | Downloaded impressions including spam |
| `AD_SERVER_UNFILTERED_BEGIN_TO_RENDER_IMPRESSIONS` | Begin-to-render impressions with spam |
| `AD_SERVER_UNFILTERED_CLICKS` | Clicks including spam-recognized interactions |
| `AD_SERVER_RESPONSES_SERVED` | Total times ad was served by ad server |

### Ad Server Active View Metrics

| Metric | Description |
|--------|-------------|
| `AD_SERVER_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS` | Impressions delivered by ad server viewed on user's screen |
| `AD_SERVER_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS` | Ad server impressions measurable by Active View |
| `AD_SERVER_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS_RATE` | Viewability percentage for ad server |
| `AD_SERVER_ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS` | Ad server impressions eligible for viewability measurement |
| `AD_SERVER_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS_RATE` | Measurability percentage for ad server |
| `AD_SERVER_ACTIVE_VIEW_REVENUE` | Active View revenue from ad server |
| `AD_SERVER_ACTIVE_VIEW_AVERAGE_VIEWABLE_TIME` | Average time in seconds impressions are viewable |

### Line Item Level Metrics

| Metric | Description |
|--------|-------------|
| `AD_SERVER_LINE_ITEM_LEVEL_PERCENT_IMPRESSIONS` | Ratio of impressions for line item-level dynamic allocation |
| `AD_SERVER_LINE_ITEM_LEVEL_PERCENT_CLICKS` | Click ratio for line item-level allocation |
| `AD_SERVER_LINE_ITEM_LEVEL_WITHOUT_CPD_PERCENT_REVENUE` | Revenue ratio excluding CPD |
| `AD_SERVER_LINE_ITEM_LEVEL_WITH_CPD_PERCENT_REVENUE` | Revenue ratio including CPD |

### AdSense Metrics

| Metric | Description |
|--------|-------------|
| `ADSENSE_LINE_ITEM_LEVEL_IMPRESSIONS` | Impressions from AdSense ads (line item-level) |
| `ADSENSE_LINE_ITEM_LEVEL_TARGETED_IMPRESSIONS` | AdSense impressions via targeting (deprecated) |
| `ADSENSE_LINE_ITEM_LEVEL_CLICKS` | Clicks from AdSense ads |
| `ADSENSE_LINE_ITEM_LEVEL_TARGETED_CLICKS` | AdSense clicks via targeting (deprecated) |
| `ADSENSE_LINE_ITEM_LEVEL_CTR` | Click-through rate for AdSense |
| `ADSENSE_LINE_ITEM_LEVEL_REVENUE` | Revenue generated from AdSense |
| `ADSENSE_LINE_ITEM_LEVEL_AVERAGE_ECPM` | Average eCPM from AdSense |
| `ADSENSE_LINE_ITEM_LEVEL_PERCENT_IMPRESSIONS` | AdSense impression ratio |
| `ADSENSE_LINE_ITEM_LEVEL_PERCENT_CLICKS` | AdSense click ratio |
| `ADSENSE_LINE_ITEM_LEVEL_WITHOUT_CPD_PERCENT_REVENUE` | AdSense revenue ratio (CPM/CPC) |
| `ADSENSE_LINE_ITEM_LEVEL_WITH_CPD_PERCENT_REVENUE` | AdSense revenue ratio (all types) |
| `ADSENSE_RESPONSES_SERVED` | Times AdSense ad was delivered |
| `ADSENSE_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS` | AdSense impressions viewed on-screen |
| `ADSENSE_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS` | AdSense impressions measurable by Active View |
| `ADSENSE_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS_RATE` | AdSense viewability percentage |
| `ADSENSE_ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS` | AdSense eligible for viewability measurement |
| `ADSENSE_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS_RATE` | AdSense measurability percentage |
| `ADSENSE_ACTIVE_VIEW_AVERAGE_VIEWABLE_TIME` | AdSense average viewable duration |

### Ad Exchange Metrics

| Metric | Description |
|--------|-------------|
| `AD_EXCHANGE_LINE_ITEM_LEVEL_IMPRESSIONS` | Impressions from Ad Exchange (line item-level) |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_TARGETED_IMPRESSIONS` | Ad Exchange impressions via targeting (deprecated) |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_CLICKS` | Clicks from Ad Exchange |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_TARGETED_CLICKS` | Ad Exchange clicks via targeting (deprecated) |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_CTR` | Click-through rate for Ad Exchange |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_PERCENT_IMPRESSIONS` | Ad Exchange impression ratio |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_PERCENT_CLICKS` | Ad Exchange click ratio |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_REVENUE` | Revenue generated from Ad Exchange ads |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_WITHOUT_CPD_PERCENT_REVENUE` | Ad Exchange revenue ratio (CPM/CPC) |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_WITH_CPD_PERCENT_REVENUE` | Ad Exchange revenue ratio (all types) |
| `AD_EXCHANGE_LINE_ITEM_LEVEL_AVERAGE_ECPM` | Average eCPM from Ad Exchange |
| `AD_EXCHANGE_RESPONSES_SERVED` | Times Ad Exchange ad was delivered |
| `AD_EXCHANGE_TOTAL_REQUESTS` | Total queries sent to Ad Exchange |
| `AD_EXCHANGE_MATCH_RATE` | Fraction of Ad Exchange queries resulting in match |
| `AD_EXCHANGE_COST_PER_CLICK` | Amount earned per Ad Exchange click |
| `AD_EXCHANGE_TOTAL_REQUEST_CTR` | Fraction of Ad Exchange requests resulting in click |
| `AD_EXCHANGE_MATCHED_REQUEST_CTR` | Click ratio for matched Ad Exchange requests |
| `AD_EXCHANGE_TOTAL_REQUEST_ECPM` | Earnings per thousand Ad Exchange requests |
| `AD_EXCHANGE_MATCHED_REQUEST_ECPM` | Earnings per thousand matched Ad Exchange requests |
| `AD_EXCHANGE_LIFT_EARNINGS` | Increase in Ad Exchange revenue for won impressions |
| `AD_EXCHANGE_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS` | Ad Exchange impressions viewed on-screen |
| `AD_EXCHANGE_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS` | Ad Exchange impressions measurable by Active View |
| `AD_EXCHANGE_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS_RATE` | Ad Exchange viewability percentage |
| `AD_EXCHANGE_ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS` | Ad Exchange eligible for viewability measurement |
| `AD_EXCHANGE_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS_RATE` | Ad Exchange measurability percentage |
| `AD_EXCHANGE_ACTIVE_VIEW_AVERAGE_VIEWABLE_TIME` | Ad Exchange average viewable duration |

### Total (Combined) Metrics

| Metric | Description |
|--------|-------------|
| `TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS` | Total impressions including line item-level allocation |
| `TOTAL_LINE_ITEM_LEVEL_TARGETED_IMPRESSIONS` | Total targeted impressions |
| `TOTAL_LINE_ITEM_LEVEL_CLICKS` | Total clicks including line item-level allocation |
| `TOTAL_LINE_ITEM_LEVEL_TARGETED_CLICKS` | Total targeted clicks |
| `TOTAL_LINE_ITEM_LEVEL_CTR` | Overall click-through rate |
| `TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE` | Total CPM and CPC revenue |
| `TOTAL_LINE_ITEM_LEVEL_ALL_REVENUE` | Total CPM, CPC and CPD revenue |
| `TOTAL_LINE_ITEM_LEVEL_WITHOUT_CPD_AVERAGE_ECPM` | Overall eCPM excluding CPD |
| `TOTAL_LINE_ITEM_LEVEL_WITH_CPD_AVERAGE_ECPM` | Overall eCPM including all types |
| `TOTAL_CODE_SERVED_COUNT` | Total times code for ad is served |
| `TOTAL_AD_REQUESTS` | Total number of times ad request sent to server |
| `TOTAL_RESPONSES_SERVED` | Total number of times ad is served by server |
| `TOTAL_UNMATCHED_AD_REQUESTS` | Total number of times ad not returned |
| `TOTAL_FILL_RATE` | Fill rate indicating how often request is filled |
| `TOTAL_INVENTORY_LEVEL_UNFILLED_IMPRESSIONS` | Total missed impressions due to inability to find ads |

### Total Active View Metrics

| Metric | Description |
|--------|-------------|
| `TOTAL_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS` | Total impressions viewed on user's screen |
| `TOTAL_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS` | Total impressions sampled and measured by Active View |
| `TOTAL_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS_RATE` | Viewability percentage overall |
| `TOTAL_ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS` | Total impressions eligible for viewability measurement |
| `TOTAL_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS_RATE` | Measurability percentage overall |
| `TOTAL_ACTIVE_VIEW_AVERAGE_VIEWABLE_TIME` | Average time impressions reported as being viewable |
| `TOTAL_ACTIVE_VIEW_REVENUE` | Active View total revenue |
| `ACTIVE_VIEW_PERCENT_AUDIBLE_START_IMPRESSIONS` | Percentage of video creatives with audible playback at start |
| `ACTIVE_VIEW_PERCENT_EVER_AUDIBLE_IMPRESSIONS` | Percentage of video creatives where volume > 0 at any point |

### Dynamic Allocation Metrics

| Metric | Description |
|--------|-------------|
| `DYNAMIC_ALLOCATION_OPPORTUNITY_IMPRESSIONS_COMPETING_TOTAL` | Total dynamic allocation impressions |
| `DYNAMIC_ALLOCATION_OPPORTUNITY_UNFILLED_IMPRESSIONS_COMPETING` | Unfilled queries attempting dynamic allocation |
| `DYNAMIC_ALLOCATION_OPPORTUNITY_ELIGIBLE_IMPRESSIONS_TOTAL` | Ad Exchange/AdSense and Ad Manager impressions |
| `DYNAMIC_ALLOCATION_OPPORTUNITY_IMPRESSIONS_NOT_COMPETING_TOTAL` | Difference between eligible and competing |
| `DYNAMIC_ALLOCATION_OPPORTUNITY_IMPRESSIONS_NOT_COMPETING_PERCENT_TOTAL` | Percentage not competing |
| `DYNAMIC_ALLOCATION_OPPORTUNITY_SATURATION_RATE_TOTAL` | Percent eligible impressions in allocation |
| `DYNAMIC_ALLOCATION_OPPORTUNITY_MATCH_RATE_TOTAL` | Percent of dynamic allocation queries won |

### Bidding & Yield Metrics

| Metric | Description |
|--------|-------------|
| `BID_COUNT` | Number of bids associated with selected dimensions |
| `BID_AVERAGE_CPM` | Average CPM associated with bids |
| `YIELD_GROUP_CALLOUTS` | Times yield partner asked to return bid |
| `YIELD_GROUP_SUCCESSFUL_RESPONSES` | Times yield group buyer returned bid successfully |
| `YIELD_GROUP_BIDS` | Bids received from Open Bidding buyers |
| `YIELD_GROUP_BIDS_IN_AUCTION` | Bids from Open Bidding that competed in auction |
| `YIELD_GROUP_AUCTIONS_WON` | Winning bids from Open Bidding buyers |
| `YIELD_GROUP_IMPRESSIONS` | Matched yield group requests with ad delivery |
| `YIELD_GROUP_ESTIMATED_REVENUE` | Total net revenue earned by yield group |
| `YIELD_GROUP_ESTIMATED_CPM` | Estimated net rate for yield groups |
| `YIELD_GROUP_MEDIATION_FILL_RATE` | How often network fills ad request (mediation) |
| `YIELD_GROUP_MEDIATION_PASSBACKS` | Times ad network did not deliver impression |
| `YIELD_GROUP_MEDIATION_THIRD_PARTY_ECPM` | Revenue per thousand impressions from third-party data |
| `YIELD_GROUP_MEDIATION_CHAINS_SERVED` | Total requests where mediation chain was served |
| `MEDIATION_THIRD_PARTY_ECPM` | Mediation third-party average cost-per-thousand-impressions |

### Deals & Programmatic Metrics

| Metric | Description |
|--------|-------------|
| `DEALS_BID_REQUESTS` | Number of bid requests sent for each deal |
| `DEALS_BIDS` | Number of bids placed on each deal |
| `DEALS_BID_RATE` | Bid rate for each deal |
| `DEALS_WINNING_BIDS` | Number of winning bids for each deal |
| `DEALS_WIN_RATE` | Win rate for each deal |
| `PROGRAMMATIC_RESPONSES_SERVED` | Ad responses served from programmatic demand sources |
| `PROGRAMMATIC_MATCH_RATE` | Programmatic responses divided by eligible requests |
| `TOTAL_PROGRAMMATIC_ELIGIBLE_AD_REQUESTS` | Ad requests eligible for programmatic inventory |

### Video Viewership Metrics

| Metric | Description |
|--------|-------------|
| `VIDEO_VIEWERSHIP_START` | Impressions where video was played |
| `VIDEO_VIEWERSHIP_FIRST_QUARTILE` | Times video played to 25% of its length |
| `VIDEO_VIEWERSHIP_MIDPOINT` | Times video reached midpoint during play |
| `VIDEO_VIEWERSHIP_THIRD_QUARTILE` | Times video played to 75% of its length |
| `VIDEO_VIEWERSHIP_COMPLETE` | Times video played to completion |
| `VIDEO_VIEWERSHIP_AVERAGE_VIEW_RATE` | Average percentage of video watched by users |
| `VIDEO_VIEWERSHIP_AVERAGE_VIEW_TIME` | Average time (seconds) users watched video |
| `VIDEO_VIEWERSHIP_COMPLETION_RATE` | Percentage of times video played to end |
| `VIDEO_VIEWERSHIP_TOTAL_ERROR_COUNT` | Times error occurred (VAST, playback, invalid response) |
| `VIDEO_VIEWERSHIP_VIDEO_LENGTH` | Duration of video creative |
| `VIDEO_VIEWERSHIP_SKIP_BUTTON_SHOWN` | Times skip button shown in video |
| `VIDEO_VIEWERSHIP_ENGAGED_VIEW` | Engaged views (ad viewed to completion or for 30s) |
| `VIDEO_VIEWERSHIP_VIEW_THROUGH_RATE` | View-through rate represented as percentage |
| `VIDEO_VIEWERSHIP_AUTO_PLAYS` | Times publisher-specified video auto-played |
| `VIDEO_VIEWERSHIP_CLICK_TO_PLAYS` | Times publisher-specified video clicked to play |
| `VIDEO_VIEWERSHIP_TOTAL_ERROR_RATE` | Error rate percentage from error count + impressions |
| `DROPOFF_RATE` | The drop-off rate |

### Video TrueView Metrics

| Metric | Description |
|--------|-------------|
| `VIDEO_TRUEVIEW_VIEWS` | Views to completion or 30 seconds (whichever first) |
| `VIDEO_TRUEVIEW_SKIP_RATE` | Percentage of times user clicked Skip |
| `VIDEO_TRUEVIEW_VTR` | TrueView views divided by TrueView impressions |

### Video Interaction Metrics

| Metric | Description |
|--------|-------------|
| `VIDEO_INTERACTION_PAUSE` | Times user paused ad clip |
| `VIDEO_INTERACTION_RESUME` | Times user unpaused video |
| `VIDEO_INTERACTION_REWIND` | Times user rewinds video |
| `VIDEO_INTERACTION_MUTE` | Times video player in mute state during play |
| `VIDEO_INTERACTION_UNMUTE` | Times user unmutes video |
| `VIDEO_INTERACTION_COLLAPSE` | Times user collapses video |
| `VIDEO_INTERACTION_EXPAND` | Times user expands video |
| `VIDEO_INTERACTION_FULL_SCREEN` | Times ad clip played in full screen mode |
| `VIDEO_INTERACTION_AVERAGE_INTERACTION_RATE` | Average user interactions with video |
| `VIDEO_INTERACTION_VIDEO_SKIPS` | Times skippable video is skipped |

### Video Opportunities & Breaks Metrics

| Metric | Description |
|--------|-------------|
| `TOTAL_VIDEO_OPPORTUNITIES` | Total number of video opportunities |
| `TOTAL_VIDEO_CAPPED_OPPORTUNITIES` | Total video capped opportunities |
| `TOTAL_VIDEO_MATCHED_OPPORTUNITIES` | Total video matched opportunities |
| `TOTAL_VIDEO_MATCHED_DURATION` | Total filled duration in ad breaks (seconds) |
| `TOTAL_VIDEO_DURATION` | Total duration in ad breaks (seconds) |
| `TOTAL_VIDEO_BREAK_START` | Total number of break starts |
| `TOTAL_VIDEO_BREAK_END` | Total number of break ends |

### VAST Error Metrics

| Metric | Description |
|--------|-------------|
| `VIDEO_ERRORS_VAST_ERROR_100_COUNT` | VAST error 100: XML parsing error |
| `VIDEO_ERRORS_VAST_ERROR_101_COUNT` | VAST error 101: VAST schema validation error |
| `VIDEO_ERRORS_VAST_ERROR_102_COUNT` | VAST error 102: VAST version not supported |
| `VIDEO_ERRORS_VAST_ERROR_200_COUNT` | VAST error 200: Trafficking error |
| `VIDEO_ERRORS_VAST_ERROR_201_COUNT` | VAST error 201: Video player expecting different linearity |
| `VIDEO_ERRORS_VAST_ERROR_202_COUNT` | VAST error 202: Video player expecting different duration |
| `VIDEO_ERRORS_VAST_ERROR_203_COUNT` | VAST error 203: Video player expecting different size |
| `VIDEO_ERRORS_VAST_ERROR_300_COUNT` | VAST error 300: General wrapper error |
| `VIDEO_ERRORS_VAST_ERROR_301_COUNT` | VAST error 301: Timeout of VAST URI |
| `VIDEO_ERRORS_VAST_ERROR_302_COUNT` | VAST error 302: Wrapper limit reached |
| `VIDEO_ERRORS_VAST_ERROR_303_COUNT` | VAST error 303: No ads VAST response after wrapper |
| `VIDEO_ERRORS_VAST_ERROR_400_COUNT` | VAST error 400: General linear error |
| `VIDEO_ERRORS_VAST_ERROR_401_COUNT` | VAST error 401: File not found |
| `VIDEO_ERRORS_VAST_ERROR_402_COUNT` | VAST error 402: Timeout of media file URI |
| `VIDEO_ERRORS_VAST_ERROR_403_COUNT` | VAST error 403: Could not find supported media file |
| `VIDEO_ERRORS_VAST_ERROR_405_COUNT` | VAST error 405: Problem displaying media file |
| `VIDEO_ERRORS_VAST_ERROR_500_COUNT` | VAST error 500: General nonlinear error |
| `VIDEO_ERRORS_VAST_ERROR_501_COUNT` | VAST error 501: Creative dimension error |
| `VIDEO_ERRORS_VAST_ERROR_502_COUNT` | VAST error 502: Unable to fetch nonlinear resource |
| `VIDEO_ERRORS_VAST_ERROR_503_COUNT` | VAST error 503: Could not find supported nonlinear resource |
| `VIDEO_ERRORS_VAST_ERROR_600_COUNT` | VAST error 600: General companion error |
| `VIDEO_ERRORS_VAST_ERROR_601_COUNT` | VAST error 601: Companion dimension error |
| `VIDEO_ERRORS_VAST_ERROR_602_COUNT` | VAST error 602: Unable to display companion |
| `VIDEO_ERRORS_VAST_ERROR_603_COUNT` | VAST error 603: Unable to fetch companion resource |
| `VIDEO_ERRORS_VAST_ERROR_604_COUNT` | VAST error 604: Could not find supported companion resource |
| `VIDEO_ERRORS_VAST_ERROR_900_COUNT` | VAST error 900: Undefined error |
| `VIDEO_ERRORS_VAST_ERROR_901_COUNT` | VAST error 901: General VPAID error |

### Video Optimization Metrics

| Metric | Description |
|--------|-------------|
| `VIDEO_OPTIMIZATION_CONTROL_STARTS` | Number of control starts |
| `VIDEO_OPTIMIZATION_OPTIMIZED_STARTS` | Number of optimized starts |
| `VIDEO_OPTIMIZATION_CONTROL_COMPLETES` | Number of control completes |
| `VIDEO_OPTIMIZATION_OPTIMIZED_COMPLETES` | Number of optimized completes |
| `VIDEO_OPTIMIZATION_CONTROL_COMPLETION_RATE` | Rate of control completions |
| `VIDEO_OPTIMIZATION_OPTIMIZED_COMPLETION_RATE` | Rate of optimized completions |
| `VIDEO_OPTIMIZATION_COMPLETION_RATE_LIFT` | Percentage optimized exceeds unoptimized |
| `VIDEO_OPTIMIZATION_CONTROL_SKIP_BUTTON_SHOWN` | Number control skip buttons shown |
| `VIDEO_OPTIMIZATION_OPTIMIZED_SKIP_BUTTON_SHOWN` | Number optimized skip buttons shown |
| `VIDEO_OPTIMIZATION_CONTROL_ENGAGED_VIEW` | Number of control engaged views |
| `VIDEO_OPTIMIZATION_OPTIMIZED_ENGAGED_VIEW` | Number of optimized engaged views |
| `VIDEO_OPTIMIZATION_CONTROL_VIEW_THROUGH_RATE` | Control view-through rate |
| `VIDEO_OPTIMIZATION_OPTIMIZED_VIEW_THROUGH_RATE` | Optimized view-through rate |
| `VIDEO_OPTIMIZATION_VIEW_THROUGH_RATE_LIFT` | Percentage optimized VTR exceeds unoptimized |

### Rich Media Metrics

| Metric | Description |
|--------|-------------|
| `RICH_MEDIA_BACKUP_IMAGES` | Total times backup image served instead of rich media |
| `RICH_MEDIA_DISPLAY_TIME` | Time (seconds) rich media ad displayed to users |
| `RICH_MEDIA_AVERAGE_DISPLAY_TIME` | Average time (seconds) rich media displayed |
| `RICH_MEDIA_EXPANSIONS` | Number of times expanding ad was expanded |
| `RICH_MEDIA_EXPANDING_TIME` | Average time (seconds) expanding ad viewed in expanded state |
| `RICH_MEDIA_INTERACTION_TIME` | Average time (seconds) user interacts with rich media |
| `RICH_MEDIA_INTERACTION_COUNT` | Number of times user interacts with rich media |
| `RICH_MEDIA_INTERACTION_RATE` | Ratio of interactions to ad displays |
| `RICH_MEDIA_AVERAGE_INTERACTION_TIME` | Average time (seconds) user interacts with rich media |
| `RICH_MEDIA_INTERACTION_IMPRESSIONS` | Impressions where user interacted with rich media |
| `RICH_MEDIA_MANUAL_CLOSES` | Times user manually closed floating/expanding ad |
| `RICH_MEDIA_FULL_SCREEN_IMPRESSIONS` | Impression measured when user opens ad in full screen |
| `RICH_MEDIA_VIDEO_INTERACTIONS` | Times user clicked graphical controls of video player |
| `RICH_MEDIA_VIDEO_INTERACTION_RATE` | Ratio of video interactions to video plays |
| `RICH_MEDIA_VIDEO_MUTES` | Times rich media video was muted |
| `RICH_MEDIA_VIDEO_PAUSES` | Times rich media video was paused |
| `RICH_MEDIA_VIDEO_PLAYES` | Times rich media video was played |
| `RICH_MEDIA_VIDEO_MIDPOINTS` | Times rich media video played to midpoint |
| `RICH_MEDIA_VIDEO_COMPLETES` | Times rich media video fully played |
| `RICH_MEDIA_VIDEO_REPLAYS` | Times rich media video restarted |
| `RICH_MEDIA_VIDEO_STOPS` | Times rich media video was stopped |
| `RICH_MEDIA_VIDEO_UNMUTES` | Times rich media video unmuted |
| `RICH_MEDIA_VIDEO_VIEW_TIME` | Average time (seconds) rich media video viewed per view |
| `RICH_MEDIA_VIDEO_VIEW_RATE` | Percentage of video watched by user |
| `RICH_MEDIA_CUSTOM_EVENT_TIME` | Time (seconds) user interacts with rich media ad |
| `RICH_MEDIA_CUSTOM_EVENT_COUNT` | Times user views and interacts with specified part |

### Reach & Nielsen Metrics

| Metric | Description |
|--------|-------------|
| `UNIQUE_REACH_FREQUENCY` | Average impressions per unique visitor |
| `UNIQUE_REACH_IMPRESSIONS` | Total reach impressions |
| `UNIQUE_REACH` | Total unique visitors |
| `NIELSEN_IMPRESSIONS` | Total impressions tracked for Nielsen measurement |
| `NIELSEN_IN_TARGET_IMPRESSIONS` | Impressions for in-target demographic |
| `NIELSEN_POPULATION_BASE` | Population in the demographic |
| `NIELSEN_IN_TARGET_POPULATION_BASE` | Total population for in-target demographics |
| `NIELSEN_UNIQUE_AUDIENCE` | Different people within demographic who were reached |
| `NIELSEN_IN_TARGET_UNIQUE_AUDIENCE` | Different people within in-target demographics reached |
| `NIELSEN_PERCENT_AUDIENCE_REACH` | Unique audience as percentage of population base |
| `NIELSEN_IN_TARGET_PERCENT_AUDIENCE_REACH` | Unique audience percentage for in-target |
| `NIELSEN_AVERAGE_FREQUENCY` | Average times person sees advertisement |
| `NIELSEN_IN_TARGET_AVERAGE_FREQUENCY` | Average times person sees ad for in-target demographics |
| `NIELSEN_GROSS_RATING_POINTS` | Unit of audience volume (percentage x frequency) |
| `NIELSEN_IN_TARGET_GROSS_RATING_POINTS` | Audience volume for in-target demographics |
| `NIELSEN_PERCENT_IMPRESSIONS_SHARE` | Share of impressions reaching target demographic |
| `NIELSEN_IN_TARGET_PERCENT_IMPRESSIONS_SHARE` | Share of impressions reaching in-target |
| `NIELSEN_PERCENT_POPULATION_SHARE` | Share of total population in population base |
| `NIELSEN_IN_TARGET_PERCENT_POPULATION_SHARE` | Share of population for in-target demographics |
| `NIELSEN_PERCENT_AUDIENCE_SHARE` | Share of unique audience in demographic |
| `NIELSEN_IN_TARGET_PERCENT_AUDIENCE_SHARE` | Share of unique audience for in-target |
| `NIELSEN_AUDIENCE_INDEX` | Relative unique audience vs share of population |
| `NIELSEN_IN_TARGET_AUDIENCE_INDEX` | Relative unique audience for in-target vs population share |
| `NIELSEN_IMPRESSIONS_INDEX` | Relative impressions per person vs overall population |
| `NIELSEN_IN_TARGET_IMPRESSIONS_INDEX` | Impressions per person for in-target vs population |
| `NIELSEN_IN_TARGET_RATIO` | Adjusted in-target impression share for pacing and billing |

### Ad Speed Metrics

| Metric | Description |
|--------|-------------|
| `CREATIVE_LOAD_TIME_0_500_MS_PERCENT` | Creative load time 0-500ms percentage |
| `CREATIVE_LOAD_TIME_500_1000_MS_PERCENT` | Creative load time 500ms-1s percentage |
| `CREATIVE_LOAD_TIME_1_2_S_PERCENT` | Creative load time 1s-2s percentage |
| `CREATIVE_LOAD_TIME_2_4_S_PERCENT` | Creative load time 2s-4s percentage |
| `CREATIVE_LOAD_TIME_4_8_S_PERCENT` | Creative load time 4s-8s percentage |
| `CREATIVE_LOAD_TIME_GREATER_THAN_8_S_PERCENT` | Creative load time >8s percentage |
| `UNVIEWED_REASON_SLOT_NEVER_ENTERED_VIEWPORT_PERCENT` | Slot never entered viewport percentage |
| `UNVIEWED_REASON_USER_SCROLLED_BEFORE_AD_FILLED_PERCENT` | User scrolled before fill percentage |
| `UNVIEWED_REASON_USER_SCROLLED_BEFORE_AD_LOADED_PERCENT` | User scrolled before load percentage |
| `UNVIEWED_REASON_USER_SCROLLED_BEFORE_1_S_PERCENT` | User scrolled before 1s percentage |
| `UNVIEWED_REASON_OTHER_PERCENT` | Other non-viewable reasons percentage |
| `PAGE_NAVIGATION_TO_TAG_LOADED_TIME_0_500_MS_PERCENT` | DOM to tag load 0-500ms percentage |
| `PAGE_NAVIGATION_TO_TAG_LOADED_TIME_500_1000_MS_PERCENT` | DOM to tag load 500ms-1s percentage |
| `PAGE_NAVIGATION_TO_TAG_LOADED_TIME_1_2_S_PERCENT` | DOM to tag load 1s-2s percentage |
| `PAGE_NAVIGATION_TO_TAG_LOADED_TIME_2_4_S_PERCENT` | DOM to tag load 2s-4s percentage |
| `PAGE_NAVIGATION_TO_TAG_LOADED_TIME_4_8_S_PERCENT` | DOM to tag load 4s-8s percentage |
| `PAGE_NAVIGATION_TO_TAG_LOADED_TIME_GREATER_THAN_8_S_PERCENT` | DOM to tag load >8s percentage |
| `PAGE_NAVIGATION_TO_FIRST_AD_REQUEST_TIME_0_500_MS_PERCENT` | DOM to first request 0-500ms percentage |
| `PAGE_NAVIGATION_TO_FIRST_AD_REQUEST_TIME_500_1000_MS_PERCENT` | DOM to first request 500ms-1s percentage |
| `PAGE_NAVIGATION_TO_FIRST_AD_REQUEST_TIME_1_2_S_PERCENT` | DOM to first request 1s-2s percentage |
| `PAGE_NAVIGATION_TO_FIRST_AD_REQUEST_TIME_2_4_S_PERCENT` | DOM to first request 2s-4s percentage |
| `PAGE_NAVIGATION_TO_FIRST_AD_REQUEST_TIME_4_8_S_PERCENT` | DOM to first request 4s-8s percentage |
| `PAGE_NAVIGATION_TO_FIRST_AD_REQUEST_TIME_GREATER_THAN_8_S_PERCENT` | DOM to first request >8s percentage |
| `TAG_LOAD_TO_FIRST_AD_REQUEST_TIME_0_500_MS_PERCENT` | Tag load to request 0-500ms percentage |
| `TAG_LOAD_TO_FIRST_AD_REQUEST_TIME_500_1000_MS_PERCENT` | Tag load to request 500ms-1s percentage |
| `TAG_LOAD_TO_FIRST_AD_REQUEST_TIME_1_2_S_PERCENT` | Tag load to request 1s-2s percentage |
| `TAG_LOAD_TO_FIRST_AD_REQUEST_TIME_2_4_S_PERCENT` | Tag load to request 2s-4s percentage |
| `TAG_LOAD_TO_FIRST_AD_REQUEST_TIME_4_8_S_PERCENT` | Tag load to request 4s-8s percentage |
| `TAG_LOAD_TO_FIRST_AD_REQUEST_TIME_GREATER_THAN_8_S_PERCENT` | Tag load to request >8s percentage |

### Partner & YouTube Metrics

| Metric | Description |
|--------|-------------|
| `PARTNER_SALES_PARTNER_IMPRESSIONS` | Partner-sold impressions served to YouTube partner inventory |
| `PARTNER_SALES_PARTNER_CODE_SERVED` | Times ad server responded to partner inventory request |
| `PARTNER_SALES_GOOGLE_IMPRESSIONS` | Google-sold impressions to partner inventory |
| `PARTNER_SALES_GOOGLE_RESERVATION_IMPRESSIONS` | Google-sold reservation impressions |
| `PARTNER_SALES_GOOGLE_AUCTION_IMPRESSIONS` | Google-sold auction impressions |
| `PARTNER_SALES_QUERIES` | Total ad requests eligible to serve to partner inventory |
| `PARTNER_SALES_FILLED_QUERIES` | Ad requests filled with at least one ad |
| `PARTNER_SALES_SELL_THROUGH_RATE` | Fill rate percentage for partner inventory |
| `PARTNER_MANAGEMENT_HOST_IMPRESSIONS` | Host impressions in partner management |
| `PARTNER_MANAGEMENT_HOST_CLICKS` | Host clicks in partner management |
| `PARTNER_MANAGEMENT_HOST_CTR` | Host CTR in partner management |
| `PARTNER_MANAGEMENT_UNFILLED_IMPRESSIONS` | Unfilled impressions in partner management |
| `PARTNER_MANAGEMENT_PARTNER_IMPRESSIONS` | Partner impressions in partner management |
| `PARTNER_MANAGEMENT_PARTNER_CLICKS` | Partner clicks in partner management |
| `PARTNER_MANAGEMENT_PARTNER_CTR` | Partner CTR in partner management |
| `PARTNER_MANAGEMENT_GROSS_REVENUE` | Gross revenue in partner management |

### Partner Finance Metrics

| Metric | Description |
|--------|-------------|
| `PARTNER_FINANCE_HOST_IMPRESSIONS` | Monthly host impressions for partner finance |
| `PARTNER_FINANCE_HOST_REVENUE` | Monthly host revenue for partner finance |
| `PARTNER_FINANCE_HOST_ECPM` | Monthly host eCPM for partner finance |
| `PARTNER_FINANCE_PARTNER_REVENUE` | Monthly partner revenue for partner finance |
| `PARTNER_FINANCE_PARTNER_ECPM` | Monthly partner eCPM for partner finance |
| `PARTNER_FINANCE_GROSS_REVENUE` | Monthly gross revenue for partner finance |

### SDK Mediation Metrics

| Metric | Description |
|--------|-------------|
| `SDK_MEDIATION_CREATIVE_IMPRESSIONS` | Impressions for particular SDK mediation creative |
| `SDK_MEDIATION_CREATIVE_CLICKS` | Clicks for particular SDK mediation creative |

### Forecasting Metrics

| Metric | Description |
|--------|-------------|
| `SELL_THROUGH_FORECASTED_IMPRESSIONS` | Forecasted impressions for future sell-through reports |
| `SELL_THROUGH_AVAILABLE_IMPRESSIONS` | Available impressions for future reports |
| `SELL_THROUGH_RESERVED_IMPRESSIONS` | Reserved impressions for future reports |
| `SELL_THROUGH_SELL_THROUGH_RATE` | Sell-through rate for future impressions |

### Invoicing Metrics

| Metric | Description |
|--------|-------------|
| `INVOICED_IMPRESSIONS` | Number of invoiced impressions |
| `INVOICED_UNFILLED_IMPRESSIONS` | Number of invoiced unfilled impressions |

### Ad Connector (DP) Metrics

| Metric | Description |
|--------|-------------|
| `DP_IMPRESSIONS` | Impressions delivered (Ad Connector) |
| `DP_CLICKS` | Clicks delivered (Ad Connector) |
| `DP_QUERIES` | Number of requests (Ad Connector) |
| `DP_MATCHED_QUERIES` | Requests with matched buyer (Ad Connector) |
| `DP_COST` | Revenue earned for delivered ads (Ad Connector) |
| `DP_ECPM` | Average eCPM for delivered ads (Ad Connector) |
| `DP_ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS` | Eligible impressions for viewability (Ad Connector) |
| `DP_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS` | Impressions measurable by Active View (Ad Connector) |
| `DP_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS` | Impressions viewed on-screen (Ad Connector) |
| `DP_ACTIVE_VIEW_MEASURABLE_IMPRESSIONS_RATE` | Measurability percentage (Ad Connector) |
| `DP_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS_RATE` | Viewability percentage (Ad Connector) |

### Real-Time Video Metrics

| Metric | Description |
|--------|-------------|
| `VIDEO_IMPRESSIONS_REAL_TIME` | Total impressions from ad server, AdSense, Ad Exchange (real-time) |
| `VIDEO_MATCHED_QUERIES_REAL_TIME` | Total matched queries (real-time) |
| `VIDEO_UNMATCHED_QUERIES_REAL_TIME` | Total unmatched queries (real-time) |
| `VIDEO_TOTAL_QUERIES_REAL_TIME` | Total ad requests (real-time) |
| `VIDEO_CREATIVE_SERVE_REAL_TIME` | Total creatives served (real-time) |
| `VIDEO_VAST_TOTAL_ERROR_COUNT_REAL_TIME` | Total VAST video errors (real-time) |

---

## Dimension Attributes

Dimension attributes provide additional metadata for dimensions without creating separate groupings. They can only be selected with their corresponding dimension (e.g., `LINE_ITEM_LABELS` requires `LINE_ITEM_NAME` or `LINE_ITEM_ID` in dimensions).

### Line Item Attributes

| Attribute | Required Dimension | Description |
|-----------|-------------------|-------------|
| `LINE_ITEM_LABELS` | `LINE_ITEM_NAME` | Comma-separated list of applied Label.name values |
| `LINE_ITEM_LABEL_IDS` | `LINE_ITEM_NAME` | Comma-separated list of applied Label IDs |
| `LINE_ITEM_OPTIMIZABLE` | `LINE_ITEM_NAME` | Generated as `true` for line items eligible for optimization, `false` otherwise |
| `LINE_ITEM_DELIVERY_INDICATOR` | `LINE_ITEM_NAME` | Delivery progress indicator: exactly 100%, over 100%, under 100%, or N/A |
| `LINE_ITEM_DELIVERY_PACING` | `LINE_ITEM_NAME` | Delivery pacing type (EVEN, FRONTLOADED, etc.) |
| `LINE_ITEM_FREQUENCY_CAP` | `LINE_ITEM_NAME` | Comma-separated list of impression limits per time period |
| `LINE_ITEM_RECONCILIATION_STATUS` | `LINE_ITEM_NAME` | Monthly reconciliation status for the line item |
| `LINE_ITEM_LAST_RECONCILIATION_DATE_TIME` | `LINE_ITEM_NAME` | Most recent reconciliation timestamp |
| `LINE_ITEM_START_DATE_TIME` | `LINE_ITEM_NAME` | Start date in YYYY-MM-DD format |
| `LINE_ITEM_END_DATE_TIME` | `LINE_ITEM_NAME` | End date in YYYY-MM-DD format |
| `LINE_ITEM_EXTERNAL_ID` | `LINE_ITEM_NAME` | External system ID (LineItem.externalId) |
| `LINE_ITEM_COST_TYPE` | `LINE_ITEM_NAME` | Cost type (CPM, CPC, CPD, etc.) |
| `LINE_ITEM_COST_PER_UNIT` | `LINE_ITEM_NAME` | Unit pricing for line item inventory |
| `LINE_ITEM_CURRENCY_CODE` | `LINE_ITEM_NAME` | Three-letter currency code (e.g., USD, EUR) |
| `LINE_ITEM_GOAL_QUANTITY` | `LINE_ITEM_NAME` | Total reserved impressions, clicks, or days |
| `LINE_ITEM_AVERAGE_NUMBER_OF_VIEWERS` | `LINE_ITEM_NAME` | Nielsen audience measurement metric for reach |
| `LINE_ITEM_SPONSORSHIP_GOAL_PERCENTAGE` | `LINE_ITEM_NAME` | Ratio between goal quantity and sponsorship targets (0-100) |
| `LINE_ITEM_LIFETIME_IMPRESSIONS` | `LINE_ITEM_NAME` | Total impressions delivered over line item lifetime |
| `LINE_ITEM_LIFETIME_CLICKS` | `LINE_ITEM_NAME` | Total clicks accumulated over line item lifetime |
| `LINE_ITEM_PRIORITY` | `LINE_ITEM_NAME` | Priority level as value between 1 and 16 |
| `LINE_ITEM_COMPUTED_STATUS` | `LINE_ITEM_NAME` | Derived status reflecting current line item state |
| `LINE_ITEM_CONTRACTED_QUANTITY` | `LINE_ITEM_NAME` | LineItem.contractedUnitsBought quantity |
| `LINE_ITEM_DISCOUNT` | `LINE_ITEM_NAME` | Line item discount as percentage or absolute value |
| `LINE_ITEM_NON_CPD_BOOKED_REVENUE` | `LINE_ITEM_NAME` | Booking cost for non-CPD line items |

### Order Attributes

| Attribute | Required Dimension | Description |
|-----------|-------------------|-------------|
| `ORDER_START_DATE_TIME` | `ORDER_NAME` | Start date in YYYY-MM-DD format |
| `ORDER_END_DATE_TIME` | `ORDER_NAME` | End date in YYYY-MM-DD format |
| `ORDER_EXTERNAL_ID` | `ORDER_NAME` | Order.externalOrderId value |
| `ORDER_PO_NUMBER` | `ORDER_NAME` | Order.poNumber (purchase order) |
| `ORDER_IS_PROGRAMMATIC` | `ORDER_NAME` | Boolean indicating programmatic order status |
| `ORDER_AGENCY` | `ORDER_NAME` | Name of associated agency |
| `ORDER_AGENCY_ID` | `ORDER_NAME` | ID of associated agency |
| `ORDER_LABELS` | `ORDER_NAME` | Comma-separated list of applied Label.name values |
| `ORDER_LABEL_IDS` | `ORDER_NAME` | Comma-separated list of applied Label IDs |
| `ORDER_TRAFFICKER` | `ORDER_NAME` | Name and email in format "name(email)" |
| `ORDER_TRAFFICKER_ID` | `ORDER_NAME` | Order.traffickerId value |
| `ORDER_SECONDARY_TRAFFICKERS` | `ORDER_NAME` | Multiple trafficker contacts in "name(email)" format |
| `ORDER_SALESPERSON` | `ORDER_NAME` | Primary salesperson in "name(email)" format |
| `ORDER_SECONDARY_SALESPEOPLE` | `ORDER_NAME` | Multiple salespeople contacts, comma-separated |
| `ORDER_LIFETIME_IMPRESSIONS` | `ORDER_NAME` | Total impressions delivered over order lifetime |
| `ORDER_LIFETIME_CLICKS` | `ORDER_NAME` | Total clicks accumulated over order lifetime |
| `ORDER_BOOKED_CPM` | `ORDER_NAME` | Cost of booking all CPM ads for the order |
| `ORDER_BOOKED_CPC` | `ORDER_NAME` | Cost of booking all CPC ads for the order |

### Advertiser Attributes

| Attribute | Required Dimension | Description |
|-----------|-------------------|-------------|
| `ADVERTISER_EXTERNAL_ID` | `ADVERTISER_NAME` | Company.externalId value |
| `ADVERTISER_TYPE` | `ADVERTISER_NAME` | Company classification type |
| `ADVERTISER_CREDIT_STATUS` | `ADVERTISER_NAME` | Credit standing indicator |
| `ADVERTISER_PRIMARY_CONTACT` | `ADVERTISER_NAME` | Primary contact in "name(email)" format |
| `ADVERTISER_LABELS` | `ADVERTISER_NAME` | Comma-separated list of Company.appliedLabels Label.name values |
| `ADVERTISER_LABEL_IDS` | `ADVERTISER_NAME` | Comma-separated list of applied Label IDs |

### Creative Attributes

| Attribute | Required Dimension | Description |
|-----------|-------------------|-------------|
| `CREATIVE_OR_CREATIVE_SET` | `CREATIVE_NAME` | Indicates if creative is 'Creative' or 'Creative set' |
| `MASTER_COMPANION_TYPE` | `CREATIVE_NAME` | Type of creative in set: master or companion |
| `CREATIVE_CLICK_THROUGH_URL` | `CREATIVE_NAME` | Click-through destination URL |
| `CREATIVE_SSL_SCAN_RESULT` | `CREATIVE_NAME` | SSL compliance scan status |
| `CREATIVE_SSL_COMPLIANCE_OVERRIDE` | `CREATIVE_NAME` | Whether SSL status override was applied |
| `LINE_ITEM_CREATIVE_START_DATE` | `CREATIVE_NAME` | LineItemCreativeAssociation.startDateTime (date only) |
| `LINE_ITEM_CREATIVE_END_DATE` | `CREATIVE_NAME` | LineItemCreativeAssociation.endDateTime (date only) |

### Content Attributes

| Attribute | Required Dimension | Description |
|-----------|-------------------|-------------|
| `CONTENT_CMS_NAME` | `CONTENT_NAME` | CmsContent.displayName from first Content.cmsContent element |
| `CONTENT_CMS_VIDEO_ID` | `CONTENT_NAME` | CMS content identifier for video source materials |

### Partner Management Attributes

| Attribute | Required Dimension | Description |
|-----------|-------------------|-------------|
| `CHILD_PARTNER_NAME` | MCM dimension | Breaks down data by child partner name in MCM "Manage Inventory" |

### Ad Unit Attributes

| Attribute | Required Dimension | Description |
|-----------|-------------------|-------------|
| `AD_UNIT_CODE` | `AD_UNIT_NAME` | AdUnit.adUnitCode value |

---

## Publisher Query Language (PQL)

PQL is a SQL-like query language for retrieving entity data from Ad Manager. It is used via the `PublisherQueryLanguageService` to query match tables and supplement report data.

### PublisherQueryLanguageService

The service provides a single primary operation:

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `select` | `selectStatement` (Statement) | `ResultSet` | Retrieves rows of data that satisfy the given Statement.query from the system. |

### Statement Object

Captures the query string and bind variable values.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | `xsd:string` | Yes | The PQL query string including WHERE, ORDER BY, and LIMIT clauses. |
| `values` | `String_ValueMapEntry[]` | No | Array of bind variable name-value pairs for parameterized queries. |

### Value Types

PQL supports several value types for bind variables and result data:

| Type | Description | Example |
|------|-------------|---------|
| `TextValue` | Text/string value | `{'textValue': 'Campaign Name'}` |
| `NumberValue` | Numeric value (integer or decimal) | `{'numberValue': 12345}` |
| `DateValue` | Date value (year, month, day) | `{'dateValue': {'year': 2024, 'month': 1, 'day': 15}}` |
| `DateTimeValue` | Date and time value | `{'dateTimeValue': {'date': {...}, 'hour': 14, 'minute': 30, 'second': 0, 'timeZoneId': 'America/New_York'}}` |
| `BooleanValue` | Boolean value | `{'booleanValue': True}` |
| `SetValue` | Set of values | `{'setValues': [{'numberValue': 1}, {'numberValue': 2}]}` |

### ResultSet Object

The response container for PQL queries.

| Field | Type | Description |
|-------|------|-------------|
| `columnTypes` | `ColumnType[]` | Array of column type descriptors for each column in the result. |
| `rows` | `Row[]` | Array of result rows. |

### Row Object

A single row in the result set.

| Field | Type | Description |
|-------|------|-------------|
| `values` | `Value[]` | Array of values corresponding to each column in the query. |

### ColumnType Object

Describes a column in the result set.

| Field | Type | Description |
|-------|------|-------------|
| `labelName` | `xsd:string` | The column name/label. |

### Syntax Structure

```sql
[SELECT column1, column2, ... FROM table_name]
[WHERE <condition> {[AND | OR] <condition> ...}]
[ORDER BY <property> [ASC | DESC]]
[LIMIT {[<offset>,] <count>} | {<count> OFFSET <offset>}]
```

**Note**: The `SELECT ... FROM` portion is only used with the PublisherQueryLanguageService. For ReportService statements, only WHERE, ORDER BY, and LIMIT clauses are supported.

### Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equals | `Id = 12345` |
| `!=` | Not equals | `Status != 'PAUSED'` |
| `<` | Less than | `Priority < 12` |
| `<=` | Less than or equal | `Priority <= 12` |
| `>` | Greater than | `Priority > 6` |
| `>=` | Greater than or equal | `Priority >= 6` |
| `IN` | In list | `Id IN (1, 2, 3)` |
| `NOT IN` | Not in list | `Status NOT IN ('ARCHIVED')` |
| `LIKE` | Pattern match | `Name LIKE 'Campaign%'` |
| `IS NULL` | Null check | `EndDateTime IS NULL` |
| `AND` | Logical AND | `Status = 'ACTIVE' AND Priority = 12` |
| `OR` | Logical OR | `Type = 'STANDARD' OR Type = 'SPONSORSHIP'` |

### String Handling

- Use single quotes for strings: `'value'`
- Escape apostrophes by doubling: `'O''Brien'`
- Numbers can be quoted or unquoted
- Keywords (SELECT, FROM, WHERE, etc.) are case-insensitive

### Bind Variables

Use colon-prefixed variables for parameterized queries. This prevents SQL injection and improves query caching.

```python
statement = {
    'query': "WHERE Status = :status AND StartDateTime > :startTime",
    'values': [
        {'key': 'status', 'value': {'textValue': 'ACTIVE'}},
        {'key': 'startTime', 'value': {'dateTimeValue': {
            'date': {'year': 2024, 'month': 1, 'day': 1},
            'hour': 0, 'minute': 0, 'second': 0,
            'timeZoneId': 'America/New_York'
        }}}
    ]
}
```

### Available PQL Tables

#### Core Entity Tables

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `Line_Item` | Line item data | Id, Name, Status, LineItemType, OrderId, StartDateTime, EndDateTime |
| `Ad_Unit` | Ad unit inventory data | Id, Name, Status, ParentId, AdUnitCode |
| `Order` | Order/campaign data | Id, Name, Status, AdvertiserId, StartDateTime, EndDateTime |
| `User` | User account data | Id, Name, Email, RoleId |
| `Company` | Company (advertiser/agency) data | Id, Name, Type, CreditStatus, ExternalId |
| `Creative` | Creative asset data | Id, Name, AdvertiserId, Width, Height |
| `Placement` | Placement data | Id, Name, Status, TargetedAdUnitIds |

#### Targeting Tables

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `Geo_Target` | Geographic targeting criteria | Id, Name, CountryCode, Type, CanonicalParentId |
| `Browser` | Browser targeting data | Id, Name, MajorVersion, MinorVersion |
| `Operating_System` | Operating system data | Id, Name |
| `Operating_System_Version` | OS version data | Id, Name, OperatingSystemId |
| `Device_Category` | Device category targets | Id, Name |
| `Device_Manufacturer` | Device manufacturer data | Id, Name |
| `Mobile_Device` | Mobile device models | Id, Name, ManufacturerId |
| `Device_Capability` | Device capabilities | Id, Name |
| `Bandwidth_Group` | Connection speed groups | Id, Name |
| `Browser_Language` | Browser language targets | Id, Name, LanguageCode |

#### Content Tables

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `Content` | Video content data | Id, Name, Status |
| `Content_Bundle` | Content bundle groupings | Id, Name, Status |
| `Content_Metadata_Key_Hierarchy` | Content metadata hierarchies | Id, Name |

#### Audience Tables

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `Audience_Segment` | Audience segment definitions | Id, Name, Status, Type, Size |
| `Audience_Segment_Category` | Segment category hierarchy | Id, Name, ParentId |

#### Programmatic Tables

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `Programmatic_Buyer` | Programmatic buyer accounts | Id, Name, Status |
| `Bidder` | Exchange bidder information | Id, Name |
| `Yield_Partner` | Yield partner data | Id, Name |

#### System Tables

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `Change_History` | Audit log of changes | ChangeDateTime, EntityId, EntityType, Operation, UserId |
| `Time_Zone` | Timezone reference data | Id, StandardName |
| `Ad_Category` | Ad category taxonomy | Id, Name, ParentId |
| `Rich_Media_Ad_Company` | Rich media vendors | Id, Name |

#### MCM (Multiple Customer Management) Tables

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `MCM_Earnings` | MCM revenue data | Month, ChildNetworkCode, TotalEarnings |
| `Child_Publisher` | Child network data | Id, Name, NetworkCode |

#### Label Tables

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `Label` | Label definitions | Id, Name, Description, Type |

### PQL Examples

**Get all active line items for an order:**
```sql
SELECT Id, Name, Status, LineItemType, StartDateTime, EndDateTime
FROM Line_Item
WHERE OrderId = 12345 AND Status = 'DELIVERING'
ORDER BY Name ASC
```

**Get geographic targets by country:**
```sql
SELECT Id, Name, CanonicalParentId, Type
FROM Geo_Target
WHERE Type = 'CITY' AND CountryCode = 'US'
LIMIT 1000
```

**Get all companies of type advertiser:**
```sql
SELECT Id, Name, Type, CreditStatus, ExternalId
FROM Company
WHERE Type = 'ADVERTISER'
ORDER BY Name ASC
```

**Get change history for a line item:**
```sql
SELECT ChangeDateTime, EntityType, Operation, UserId
FROM Change_History
WHERE EntityId = 12345 AND EntityType = 'LINE_ITEM'
ORDER BY ChangeDateTime DESC
LIMIT 100
```

**Get audience segments with size data:**
```sql
SELECT Id, Name, Status, Type, Size
FROM Audience_Segment
WHERE Status = 'ACTIVE'
ORDER BY Size DESC
LIMIT 50
```

### Python PQL Example

```python
def query_line_items(client, order_id):
    """Query line items for an order using PQL."""

    pql_service = client.GetService('PublisherQueryLanguageService', version='v202511')

    # Create the statement
    statement = {
        'query': """
            SELECT Id, Name, Status, LineItemType, StartDateTime, EndDateTime
            FROM Line_Item
            WHERE OrderId = :orderId AND Status IN ('READY', 'DELIVERING')
            ORDER BY Name ASC
            LIMIT 500
        """,
        'values': [
            {'key': 'orderId', 'value': {'numberValue': order_id}}
        ]
    }

    # Execute the query
    result_set = pql_service.select(statement)

    # Process results
    rows = []
    if 'rows' in result_set:
        columns = [col['labelName'] for col in result_set['columnTypes']]
        for row in result_set['rows']:
            row_dict = {}
            for i, value in enumerate(row['values']):
                # Extract the actual value based on type
                if 'textValue' in value:
                    row_dict[columns[i]] = value['textValue']
                elif 'numberValue' in value:
                    row_dict[columns[i]] = value['numberValue']
                elif 'dateTimeValue' in value:
                    dt = value['dateTimeValue']
                    row_dict[columns[i]] = f"{dt['date']['year']}-{dt['date']['month']:02d}-{dt['date']['day']:02d}"
                else:
                    row_dict[columns[i]] = None
            rows.append(row_dict)

    return rows
```

---

## ForecastService

The ForecastService provides inventory forecasting capabilities to predict availability, delivery, and traffic data for line items. This is analogous to the "Check Inventory" feature in the Ad Manager UI.

### Service Methods

| Method | Description | Line Item Types |
|--------|-------------|-----------------|
| `getAvailabilityForecast` | Gets availability forecast for a ProspectiveLineItem | All types |
| `getAvailabilityForecastById` | Gets availability forecast for an existing LineItem | SPONSORSHIP, STANDARD only |
| `getDeliveryForecast` | Simulates delivery for multiple prospective line items | All types |
| `getDeliveryForecastByIds` | Simulates delivery for existing line items | All types |
| `getTrafficData` | Gets historical/forecasted traffic data | Ad Manager 360 only |

### ProspectiveLineItem Object

A prospective line item represents a line item that does not yet exist in the system, used for forecasting purposes.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `lineItem` | `LineItem` | Yes | The line item configuration to forecast. Does not require an ID. |
| `advertiserId` | `xsd:long` | No | Advertiser ID for the prospective line item. |
| `prospectiveLineItemId` | `xsd:long` | No | Optional ID for identifying this prospective item in multi-item forecasts. |

### AvailabilityForecast Object

Reports the maximum number of available units with which a line item can be booked.

| Field | Type | Description |
|-------|------|-------------|
| `lineItemId` | `xsd:long` | Uniquely identifies this forecast. Read-only, assigned by Google. Null for prospective items. |
| `orderId` | `xsd:long` | Associated Order ID. Null for prospective items without order. |
| `unitType` | `UnitType` | Unit type for goal/cap (IMPRESSIONS, CLICKS, VIEWABLE_IMPRESSIONS, etc.). |
| `availableUnits` | `xsd:long` | Units bookable without affecting reserved line items. |
| `deliveredUnits` | `xsd:long` | Units already served if reservation is active. |
| `matchedUnits` | `xsd:long` | Total units matching targeting and delivery settings. |
| `possibleUnits` | `xsd:long` | Maximum units if taking inventory from lower-priority items. |
| `reservedUnits` | `xsd:long` | Number of reserved units requested (absolute or percentage). |
| `breakdowns` | `ForecastBreakdown[]` | Time-window breakdowns per ForecastBreakdownOptions. |
| `targetingCriteriaBreakdowns` | `TargetingCriteriaBreakdown[]` | Breakdowns by line item targeting criteria. |
| `contendingLineItems` | `ContendingLineItem[]` | Competing line items for this forecast. |
| `alternativeUnitTypeForecasts` | `AlternativeUnitTypeForecast[]` | Forecast in alternative unit types. |
| `demographicBreakdowns` | `GrpDemographicBreakdown[]` | Demographic breakdowns for GRP-enabled forecasts. |

### AvailabilityForecastOptions Object

Configuration options for availability forecast requests.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `includeContendingLineItems` | `xsd:boolean` | `false` | Include list of competing line items in response. |
| `includeTargetingCriteriaBreakdown` | `xsd:boolean` | `false` | Include per-targeting-criteria breakdown. Cannot be set if `breakdown` is manually specified. |
| `breakdown` | `ForecastBreakdownOptions` | - | Manual breakdown configuration by time or targeting. |

### TargetingCriteriaBreakdown Object

Provides breakdown of forecast by targeting criteria.

| Field | Type | Description |
|-------|------|-------------|
| `targetingDimension` | `TargetingDimension` | The targeting dimension (AD_UNIT, PLACEMENT, COUNTRY, etc.). |
| `targetingCriteriaId` | `xsd:long` | ID of the targeting criteria. |
| `targetingCriteriaName` | `xsd:string` | Name of the targeting criteria. |
| `excluded` | `xsd:boolean` | Whether this criteria is excluded from targeting. |
| `availableUnits` | `xsd:long` | Available units for this targeting segment. |
| `matchedUnits` | `xsd:long` | Matched units for this targeting segment. |

### ContendingLineItem Object

Represents a line item competing for the same inventory.

| Field | Type | Description |
|-------|------|-------------|
| `lineItemId` | `xsd:long` | ID of the contending line item. |
| `contendingImpressions` | `xsd:long` | Number of impressions contending with the forecasted item. |

### DeliveryForecast Object

Results from a delivery simulation across multiple line items.

| Field | Type | Description |
|-------|------|-------------|
| `lineItemDeliveryForecasts` | `LineItemDeliveryForecast[]` | Per-line-item delivery predictions. |

### LineItemDeliveryForecast Object

Delivery prediction for a single line item in a simulation.

| Field | Type | Description |
|-------|------|-------------|
| `lineItemId` | `xsd:long` | Line item ID (null for prospective). |
| `orderId` | `xsd:long` | Order ID (null for prospective). |
| `unitType` | `UnitType` | Measurement unit (IMPRESSIONS, CLICKS, etc.). |
| `predictedDeliveryUnits` | `xsd:long` | Units expected to be delivered. |
| `deliveredUnits` | `xsd:long` | Units already served. |
| `matchedUnits` | `xsd:long` | Units matching targeting. |

### DeliveryForecastOptions Object

Configuration options for delivery forecast requests.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `ignoredLineItemIds` | `xsd:long[]` | - | Line item IDs to ignore in the simulation. |

### GrpDemographicBreakdown Object

Demographic breakdown for GRP (Gross Rating Point) enabled forecasts.

| Field | Type | Description |
|-------|------|-------------|
| `availableUnits` | `xsd:long` | Available units for this demographic. |
| `matchedUnits` | `xsd:long` | Matched units for this demographic. |
| `unitType` | `UnitType` | Unit type for this breakdown. |
| `gender` | `GrpGender` | Gender (MALE, FEMALE, UNKNOWN). |
| `age` | `GrpAge` | Age bracket. |

### TrafficDataRequest Object (Ad Manager 360 Only)

Request for historical and forecasted traffic data.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `targeting` | `Targeting` | Yes | Targeting specification for traffic query. |
| `requestedDateRange` | `DateRange` | Yes | Date range for traffic data. |

### TrafficDataResponse Object

Response containing traffic data.

| Field | Type | Description |
|-------|------|-------------|
| `historicalTimeSeries` | `TimeSeries` | Historical traffic data. |
| `forecastedTimeSeries` | `TimeSeries` | Forecasted traffic data. |
| `overallDateRange` | `DateRange` | Overall date range of data. |

### Use Cases

#### Availability Forecasts

- **Check inventory before creating line items**: Verify sufficient inventory exists before booking
- **Validate targeting**: Confirm targeting reaches expected audience size
- **Identify contention**: Understand which existing line items compete for inventory

#### Delivery Forecasts

- **Multi-line-item simulation**: Predict how multiple competing line items will deliver
- **Displacement analysis**: Understand how new bookings affect existing campaigns
- **Pacing planning**: Plan campaign pacing based on delivery predictions

#### Traffic Data (Ad Manager 360)

- **Historical analysis**: Review past traffic patterns
- **Future planning**: Forecast future inventory availability
- **Seasonal trends**: Identify patterns for planning

### Forecast Workflow Example

```python
def get_availability_forecast(client, line_item_config):
    """Get availability forecast for a prospective line item."""

    forecast_service = client.GetService('ForecastService', version='v202511')

    # Create prospective line item
    prospective_line_item = {
        'lineItem': line_item_config,
        'advertiserId': 12345  # Optional
    }

    # Configure options
    forecast_options = {
        'includeContendingLineItems': True,
        'includeTargetingCriteriaBreakdown': True
    }

    # Get forecast
    forecast = forecast_service.getAvailabilityForecast(
        prospectiveLineItem=prospective_line_item,
        forecastOptions=forecast_options
    )

    # Process results
    print(f"Matched units: {forecast['matchedUnits']}")
    print(f"Available units: {forecast['availableUnits']}")
    print(f"Possible units: {forecast['possibleUnits']}")

    # Check contending line items
    if 'contendingLineItems' in forecast:
        print(f"Contending line items: {len(forecast['contendingLineItems'])}")
        for cli in forecast['contendingLineItems']:
            print(f"  - Line Item {cli['lineItemId']}: {cli['contendingImpressions']} impressions")

    return forecast
```

### Test Network Behavior

Test networks return consistent, predictable forecast results based on `lineItemType` and `unitsBought` values. This allows for testing integration without live traffic data:

- **Specific Values**: Test networks return fixed `availableUnits`, `forecastUnits`, and `deliveredUnits` based on input parameters
- **Exceptions**: Certain configurations may return `NO_FORECAST_YET` or `SERVER_NOT_AVAILABLE` errors for testing error handling

---

## Python Code Examples

### Setup and Authentication

```python
from googleads import ad_manager
from googleads import errors
import tempfile
import gzip

# Initialize the Ad Manager client
client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')

# Get the network code
network_service = client.GetService('NetworkService', version='v202511')
current_network = network_service.getCurrentNetwork()
print(f'Network: {current_network["displayName"]} ({current_network["networkCode"]})')
```

### Creating and Running a Report Job

```python
def run_delivery_report(client, start_date, end_date):
    """Run a basic delivery report."""

    report_service = client.GetService('ReportService', version='v202511')

    # Define the report query
    report_query = {
        'dimensions': ['DATE', 'LINE_ITEM_ID', 'LINE_ITEM_NAME'],
        'dimensionAttributes': ['LINE_ITEM_START_DATE_TIME', 'LINE_ITEM_END_DATE_TIME'],
        'columns': [
            'AD_SERVER_IMPRESSIONS',
            'AD_SERVER_CLICKS',
            'AD_SERVER_CTR',
            'AD_SERVER_ALL_REVENUE'
        ],
        'dateRangeType': 'CUSTOM_DATE',
        'startDate': start_date,
        'endDate': end_date
    }

    # Create the report job
    report_job = {'reportQuery': report_query}

    # Run the report
    report_job = report_service.runReportJob(report_job)
    print(f'Report job ID: {report_job["id"]}')

    return report_job
```

### Polling for Report Completion

```python
import time

def wait_for_report(report_service, report_job_id, max_wait_seconds=600):
    """Poll until report is complete or failed."""

    start_time = time.time()
    poll_interval = 5  # Start with 5 seconds

    while time.time() - start_time < max_wait_seconds:
        status = report_service.getReportJobStatus(report_job_id)

        if status == 'COMPLETED':
            print('Report completed successfully.')
            return True
        elif status == 'FAILED':
            raise Exception('Report job failed.')
        else:
            print(f'Report status: {status}. Waiting {poll_interval} seconds...')
            time.sleep(poll_interval)
            # Exponential backoff, max 60 seconds
            poll_interval = min(poll_interval * 1.5, 60)

    raise Exception('Report timed out.')
```

### Downloading Reports

```python
def download_report(report_service, report_job_id, export_format='CSV_DUMP'):
    """Download a completed report."""

    # Get download URL
    report_download_url = report_service.getReportDownloadURL(
        report_job_id,
        export_format
    )

    # Download using report_downloader utility
    report_downloader = client.GetDataDownloader(version='v202511')

    with tempfile.NamedTemporaryFile(
        mode='wb',
        suffix='.csv.gz',
        delete=False
    ) as report_file:
        report_downloader.DownloadReportToFile(
            report_job_id,
            export_format,
            report_file
        )
        print(f'Report saved to: {report_file.name}')
        return report_file.name
```

### Downloading with Options

```python
def download_report_with_options(report_service, report_job_id):
    """Download report with custom options."""

    download_options = {
        'exportFormat': 'CSV_DUMP',
        'includeReportProperties': True,
        'includeTotalsRow': True,
        'useGzipCompression': True
    }

    report_url = report_service.getReportDownloadUrlWithOptions(
        report_job_id,
        download_options
    )

    return report_url
```

### Using Saved Queries

```python
def get_and_run_saved_query(client, query_name):
    """Retrieve a saved query and run it."""

    report_service = client.GetService('ReportService', version='v202511')

    # Create statement to filter by name
    statement = {
        'query': "WHERE name = :name",
        'values': [
            {'key': 'name', 'value': {'textValue': query_name}}
        ]
    }

    # Get saved queries
    page = report_service.getSavedQueriesByStatement(statement)

    if 'results' in page and len(page['results']) > 0:
        saved_query = page['results'][0]

        # Check compatibility
        if saved_query['isCompatibleWithApiVersion']:
            # Create report job from saved query
            report_job = {'reportQuery': saved_query['reportQuery']}

            # Optionally modify the query
            # report_job['reportQuery']['dateRangeType'] = 'YESTERDAY'

            # Run the report
            report_job = report_service.runReportJob(report_job)
            return report_job
        else:
            raise Exception(f'Saved query "{query_name}" is not compatible with API version.')
    else:
        raise Exception(f'Saved query "{query_name}" not found.')
```

### Running PQL Queries

```python
def run_pql_query(client, query):
    """Execute a PQL query and return results."""

    pql_service = client.GetService('PublisherQueryLanguageService', version='v202511')

    statement = {'query': query}
    response = pql_service.select(statement)

    # Process results
    if 'rows' in response:
        # Get column headers
        columns = [col['labelName'] for col in response['columnTypes']]
        print(f'Columns: {columns}')

        # Process rows
        results = []
        for row in response['rows']:
            row_data = {}
            for i, value in enumerate(row['values']):
                # Extract value based on type
                if 'textValue' in value:
                    row_data[columns[i]] = value['textValue']
                elif 'numberValue' in value:
                    row_data[columns[i]] = value['numberValue']
                elif 'booleanValue' in value:
                    row_data[columns[i]] = value['booleanValue']
                elif 'dateTimeValue' in value:
                    row_data[columns[i]] = value['dateTimeValue']
                else:
                    row_data[columns[i]] = None
            results.append(row_data)

        return results

    return []


# Example usage
line_items = run_pql_query(
    client,
    "SELECT Id, Name, Status FROM Line_Item WHERE OrderId = 12345"
)
```

### Getting Availability Forecast

```python
def get_availability_forecast(client, targeting, start_date, end_date):
    """Get availability forecast for a prospective line item."""

    forecast_service = client.GetService('ForecastService', version='v202511')

    # Create prospective line item
    line_item = {
        'targeting': targeting,
        'creativePlaceholders': [
            {
                'size': {'width': 300, 'height': 250},
                'expectedCreativeCount': 1
            }
        ],
        'lineItemType': 'STANDARD',
        'startDateTime': start_date,
        'endDateTime': end_date,
        'costType': 'CPM',
        'costPerUnit': {'currencyCode': 'USD', 'microAmount': 2000000},  # $2.00 CPM
        'primaryGoal': {
            'goalType': 'LIFETIME',
            'unitType': 'IMPRESSIONS',
            'units': 1000000
        }
    }

    prospective_line_item = {
        'lineItem': line_item
    }

    # Forecast options
    forecast_options = {
        'includeContendingLineItems': True,
        'includeTargetingCriteriaBreakdown': True
    }

    # Get forecast
    forecast = forecast_service.getAvailabilityForecast(
        prospective_line_item,
        forecast_options
    )

    print(f"Matched units: {forecast['matchedUnits']}")
    print(f"Available units: {forecast['availableUnits']}")
    print(f"Possible units: {forecast['possibleUnits']}")

    return forecast
```

### Getting Delivery Forecast

```python
def get_delivery_forecast(client, line_item_ids):
    """Get delivery forecast for existing line items."""

    forecast_service = client.GetService('ForecastService', version='v202511')

    # Forecast options
    forecast_options = {
        'ignoredLineItemIds': []  # Optional: exclude specific line items
    }

    # Get forecast
    forecast = forecast_service.getDeliveryForecastByIds(
        line_item_ids,
        forecast_options
    )

    # Process results
    for item_forecast in forecast['lineItemDeliveryForecasts']:
        print(f"Line Item ID: {item_forecast['lineItemId']}")
        print(f"  Predicted delivery: {item_forecast['predictedDeliveryUnits']}")
        print(f"  Already delivered: {item_forecast.get('deliveredUnits', 0)}")
        print(f"  Matched units: {item_forecast['matchedUnits']}")

    return forecast
```

### Complete Report Workflow Example

```python
def run_complete_report(client, dimensions, columns, start_date, end_date):
    """Complete workflow: create, poll, download, parse."""

    report_service = client.GetService('ReportService', version='v202511')

    # Step 1: Create report query
    report_query = {
        'dimensions': dimensions,
        'columns': columns,
        'dateRangeType': 'CUSTOM_DATE',
        'startDate': start_date,
        'endDate': end_date
    }

    # Step 2: Run report
    report_job = {'reportQuery': report_query}
    report_job = report_service.runReportJob(report_job)
    job_id = report_job['id']
    print(f'Started report job: {job_id}')

    # Step 3: Poll for completion
    wait_for_report(report_service, job_id)

    # Step 4: Download report
    report_file = download_report(report_service, job_id, 'CSV_DUMP')

    # Step 5: Parse results
    import csv

    results = []
    with gzip.open(report_file, 'rt') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)

    print(f'Retrieved {len(results)} rows')
    return results


# Usage example
results = run_complete_report(
    client,
    dimensions=['DATE', 'ORDER_NAME', 'LINE_ITEM_NAME'],
    columns=['AD_SERVER_IMPRESSIONS', 'AD_SERVER_CLICKS', 'AD_SERVER_ALL_REVENUE'],
    start_date={'year': 2024, 'month': 1, 'day': 1},
    end_date={'year': 2024, 'month': 1, 'day': 31}
)
```

---

## Common Report Patterns

### Delivery Report by Advertiser

```python
report_query = {
    'dimensions': ['DATE', 'ADVERTISER_NAME', 'ORDER_NAME', 'LINE_ITEM_NAME'],
    'dimensionAttributes': [
        'LINE_ITEM_START_DATE_TIME',
        'LINE_ITEM_END_DATE_TIME',
        'LINE_ITEM_DELIVERY_INDICATOR'
    ],
    'columns': [
        'AD_SERVER_IMPRESSIONS',
        'AD_SERVER_CLICKS',
        'AD_SERVER_CTR',
        'AD_SERVER_CPM_AND_CPC_REVENUE'
    ],
    'dateRangeType': 'LAST_MONTH'
}
```

### Revenue Report by Salesperson

```python
report_query = {
    'dimensions': ['MONTH_AND_YEAR', 'SALESPERSON_NAME', 'ADVERTISER_NAME'],
    'columns': [
        'AD_SERVER_ALL_REVENUE',
        'AD_SERVER_IMPRESSIONS',
        'AD_SERVER_AVERAGE_ECPM'
    ],
    'dateRangeType': 'LAST_3_MONTHS'
}
```

### Inventory Performance by Ad Unit

```python
report_query = {
    'dimensions': ['DATE', 'AD_UNIT_NAME'],
    'columns': [
        'TOTAL_IMPRESSIONS',
        'TOTAL_CLICKS',
        'TOTAL_CTR',
        'TOTAL_REVENUE',
        'TOTAL_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS',
        'AD_SERVER_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS_RATE'
    ],
    'adUnitView': 'HIERARCHICAL',
    'dateRangeType': 'LAST_WEEK'
}
```

### Video Performance Report

```python
report_query = {
    'dimensions': ['DATE', 'LINE_ITEM_NAME', 'CREATIVE_NAME'],
    'columns': [
        'AD_SERVER_IMPRESSIONS',
        'VIDEO_VIEWERSHIP_START',
        'VIDEO_VIEWERSHIP_FIRST_QUARTILE',
        'VIDEO_VIEWERSHIP_MIDPOINT',
        'VIDEO_VIEWERSHIP_THIRD_QUARTILE',
        'VIDEO_VIEWERSHIP_COMPLETE',
        'VIDEO_VIEWERSHIP_COMPLETION_RATE',
        'VIDEO_VIEWERSHIP_AVERAGE_VIEW_TIME'
    ],
    'dateRangeType': 'LAST_WEEK'
}
```

### Programmatic Performance Report

```python
report_query = {
    'dimensions': [
        'DATE',
        'PROGRAMMATIC_CHANNEL_NAME',
        'YIELD_GROUP_NAME',
        'PROGRAMMATIC_BUYER_NAME'
    ],
    'columns': [
        'AD_EXCHANGE_IMPRESSIONS',
        'AD_EXCHANGE_REVENUE',
        'AD_EXCHANGE_AVERAGE_ECPM',
        'DEALS_BID_REQUESTS',
        'DEALS_MATCHED_REQUESTS'
    ],
    'dateRangeType': 'LAST_WEEK'
}
```

### Geographic Performance Report

```python
report_query = {
    'dimensions': ['DATE', 'COUNTRY_NAME', 'REGION_NAME', 'CITY_NAME'],
    'columns': [
        'TOTAL_IMPRESSIONS',
        'TOTAL_CLICKS',
        'TOTAL_CTR',
        'TOTAL_REVENUE'
    ],
    'dateRangeType': 'LAST_MONTH',
    # Filter to specific country
    'statement': {
        'query': 'WHERE COUNTRY_CRITERIA_ID = :countryId',
        'values': [
            {'key': 'countryId', 'value': {'numberValue': 2840}}  # USA
        ]
    }
}
```

### Device Performance Report

```python
report_query = {
    'dimensions': [
        'DATE',
        'DEVICE_CATEGORY_NAME',
        'BROWSER_NAME',
        'OPERATING_SYSTEM_VERSION_NAME'
    ],
    'columns': [
        'TOTAL_IMPRESSIONS',
        'TOTAL_CLICKS',
        'TOTAL_CTR',
        'TOTAL_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS',
        'AD_SERVER_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS_RATE'
    ],
    'dateRangeType': 'LAST_WEEK'
}
```

### Future Sell-Through Report

```python
report_query = {
    'dimensions': ['DATE', 'AD_UNIT_NAME'],
    'columns': [
        'SELL_THROUGH_FORECASTED_IMPRESSIONS',
        'SELL_THROUGH_AVAILABLE_IMPRESSIONS',
        'SELL_THROUGH_RESERVED_IMPRESSIONS',
        'SELL_THROUGH_SELL_THROUGH_RATE'
    ],
    'dateRangeType': 'NEXT_MONTH'
}
```

---

## Best Practices

### Performance Optimization

1. **Minimize date ranges**: Shorter date ranges process faster
2. **Limit dimensions**: Fewer dimensions = smaller result sets
3. **Use filters**: Filter early to reduce data processing
4. **Choose appropriate granularity**: Daily vs hourly based on need

### Report Design

1. **Validate combinations**: Not all dimension/column combinations work
2. **Test in UI first**: Build complex reports in the UI, then retrieve via API
3. **Use saved queries**: Reuse validated report configurations
4. **Handle pagination**: Large PQL results require LIMIT/OFFSET

### Error Handling

1. **Implement retries**: Transient failures are common
2. **Handle timeouts**: Long reports may require extended polling
3. **Check compatibility**: Verify saved queries are API-compatible
4. **Validate permissions**: User roles affect available data

### Quota Management

1. **Batch requests**: Combine operations where possible
2. **Cache results**: Avoid re-running identical reports
3. **Monitor usage**: Track API quota consumption
4. **Use async patterns**: Don't block on report completion

---

## Troubleshooting

### Common Errors

#### "Column X is not compatible with dimension Y"

Not all metrics work with all dimensions. Check the compatibility matrix in the UI or use saved queries.

**Solution**: Remove the incompatible dimension or column.

#### "The saved query is not compatible with API version"

The saved query uses UI-only features.

**Solution**: Recreate the report with API-compatible options, especially date ranges.

#### "Report job failed"

Report generation encountered an error.

**Solution**:
- Reduce date range
- Remove complex dimensions
- Check for data availability in the date range

#### "NO_FORECAST_YET"

Insufficient historical data for forecasting.

**Solution**: Wait for more data to accumulate (typically 7+ days of traffic).

#### "Request timed out"

Report took too long to generate.

**Solution**:
- Reduce date range
- Remove dimensions
- Remove less essential columns
- Split into multiple smaller reports

### Debugging Tips

1. **Check the UI**: Verify data exists in the Ad Manager UI
2. **Use test networks carefully**: Test networks have no delivery data
3. **Validate targeting**: Ensure targeting criteria match existing inventory
4. **Check user permissions**: Some reports require specific roles

---

## External References

- [ReportService Reference (v202511)](https://developers.google.com/ad-manager/api/reference/v202511/ReportService)
- [Dimension Reference (v202511)](https://developers.google.com/ad-manager/api/reference/v202511/ReportService.Dimension)
- [Column Reference (v202511)](https://developers.google.com/ad-manager/api/reference/v202511/ReportService.Column)
- [Reporting Basics Guide](https://developers.google.com/ad-manager/api/reporting)
- [PQL Developer's Guide](https://developers.google.com/ad-manager/api/pqlreference)
- [ForecastService Reference (v202511)](https://developers.google.com/ad-manager/api/reference/v202511/ForecastService)
- [Forecasting Guide](https://developers.google.com/ad-manager/api/forecasting)
- [PublisherQueryLanguageService Reference (v202511)](https://developers.google.com/ad-manager/api/reference/v202511/PublisherQueryLanguageService)

---

*Last Updated: 2024-11-28*
*API Version: v202511*
