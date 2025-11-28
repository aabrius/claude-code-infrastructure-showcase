# Google Ad Manager SOAP API v202511 - Inventory Category

> Comprehensive documentation for managing ad inventory through the Google Ad Manager SOAP API.

**API Version:** v202511
**Namespace:** `https://www.google.com/apis/ads/publisher/v202511`
**Last Updated:** 2025-11-28

---

## Table of Contents

1. [Overview](#overview)
2. [Services Reference](#services-reference)
   - [InventoryService](#inventoryservice)
   - [PlacementService](#placementservice)
   - [SiteService](#siteservice)
   - [SuggestedAdUnitService](#suggestedadunitservice)
3. [Data Models](#data-models)
   - [AdUnit](#adunit)
   - [AdUnitSize](#adunitsize)
   - [Size](#size)
   - [AdUnitParent](#adunitparent)
   - [Placement](#placement)
   - [Site](#site)
   - [SuggestedAdUnit](#suggestedadunit)
4. [Supporting Types and Enumerations](#supporting-types-and-enumerations)
   - [EnvironmentType](#environmenttype-enum)
   - [InventoryStatus](#inventorystatus-enum)
   - [AdUnit.TargetWindow](#adunittargetwindow-enum)
   - [SmartSizeMode](#smartsizemode-enum)
   - [ValueSourceType](#valuesourcetype-enum)
   - [AdSenseSettings](#adsensesettings)
   - [LabelFrequencyCap](#labelfrequencycap)
   - [FrequencyCap](#frequencycap)
   - [AppliedLabel](#appliedlabel)
5. [Ad Unit Hierarchy](#ad-unit-hierarchy)
6. [Actions Reference](#actions-reference)
7. [PQL Filtering](#pql-filtering)
8. [Python Code Examples](#python-code-examples)
9. [Common Patterns](#common-patterns)
10. [Error Handling](#error-handling)

---

## Overview

The Inventory category provides services for managing the fundamental building blocks of ad serving in Google Ad Manager. It encompasses:

- **Ad Units** - Chunks of identified inventory where ads can be served
- **Placements** - Logical groupings of ad units for targeting
- **Sites** - Websites or apps associated with your network
- **Suggested Ad Units** - Auto-detected ad units from undefined inventory

### Use Cases

| Scenario | Services Used |
|----------|---------------|
| Create ad unit structure for a new website | InventoryService |
| Group sports-related ad units for easy targeting | PlacementService |
| Register new sites for MCM child networks | SiteService |
| Review and approve auto-detected inventory | SuggestedAdUnitService |
| Bulk archive outdated inventory | InventoryService, PlacementService |

### Key Concepts

1. **Hierarchical Structure** - Ad units form a tree structure with parent-child relationships
2. **Inheritance** - Child ad units inherit settings from parents (labels, teams, AdSense settings)
3. **Status Management** - All inventory objects have lifecycle states (Active, Inactive, Archived)
4. **Targeting** - Ad units and placements are targetable in line items

---

## Services Reference

### InventoryService

Provides methods for creating, updating, and retrieving AdUnit objects. An AdUnit represents a chunk of identified inventory that can serve ads.

**WSDL:** `https://ads.google.com/apis/ads/publisher/v202511/InventoryService?wsdl`

#### Methods

##### createAdUnits

Creates new AdUnit objects.

```
AdUnit[] createAdUnits(AdUnit[] adUnits)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `adUnits` | `AdUnit[]` | Array of AdUnit objects to create |

**Returns:** `AdUnit[]` - The created AdUnit objects with populated IDs

**Validation Rules:**
- `name` is required and must be unique within the parent (case-insensitive). Maximum 255 characters.
- `parentId` is required for all non-root ad units. Use the network's effective root ad unit ID for top-level units.
- `adUnitCode` is optional. If not provided, Google assigns one based on the ad unit ID. Once set, it cannot be changed.
- `description` is optional. Maximum 65,535 characters.
- `adUnitSizes` is optional but recommended for ad serving.
- `targetWindow` defaults to `TOP` if not specified.
- `status` defaults to `ACTIVE` if not specified.

**Input Parameters for AdUnit Creation:**

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Max 255 chars, unique within parent |
| `parentId` | Yes* | Required except for effective root |
| `adUnitCode` | No | Auto-assigned if omitted, immutable |
| `description` | No | Max 65,535 chars |
| `targetWindow` | No | Defaults to TOP |
| `adUnitSizes` | No | Array of AdUnitSize objects |
| `isInterstitial` | No | Boolean |
| `isNative` | No | Boolean |
| `isFluid` | No | Boolean |
| `explicitlyTargeted` | No | Ad Manager 360 only |
| `adSenseSettings` | No | Inherited from parent if not set |
| `appliedLabelFrequencyCaps` | No | Max 10 per ad unit |
| `appliedLabels` | No | Array of AppliedLabel |
| `appliedTeamIds` | No | Array of team IDs |
| `smartSizeMode` | No | Defaults to NONE |
| `refreshRate` | No | 30-120 seconds, mobile apps only |
| `applicationId` | No | For CTV applications |

---

##### getAdUnitsByStatement

Retrieves AdUnit objects matching a PQL query.

```
AdUnitPage getAdUnitsByStatement(Statement filterStatement)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `filterStatement` | `Statement` | PQL query with filtering, ordering, and pagination |

**Returns:** `AdUnitPage` - Page of matching AdUnit objects

**AdUnitPage Structure:**
| Field | Type | Description |
|-------|------|-------------|
| `totalResultSetSize` | `xsd:int` | Total number of results matching the query |
| `startIndex` | `xsd:int` | Starting index of this page |
| `results` | `AdUnit[]` | Array of AdUnit objects for this page |

**Filterable Fields:**

| Field | Type | Supported Operators | Description |
|-------|------|---------------------|-------------|
| `id` | `xsd:string` | `=`, `!=`, `IN`, `NOT IN` | AdUnit ID |
| `name` | `xsd:string` | `=`, `!=`, `LIKE` | AdUnit name (case-insensitive) |
| `adUnitCode` | `xsd:string` | `=`, `!=`, `LIKE`, `IN` | Unique ad unit code |
| `parentId` | `xsd:string` | `=`, `IS NULL` | Parent AdUnit ID. Use `IS NULL` for root units. |
| `status` | `InventoryStatus` | `=`, `!=`, `IN`, `NOT IN` | ACTIVE, INACTIVE, or ARCHIVED |
| `lastModifiedDateTime` | `DateTime` | `=`, `!=`, `<`, `>`, `<=`, `>=` | Last modification timestamp |

---

##### getAdUnitSizesByStatement

Returns all relevant AdUnitSize objects. This method retrieves the sizes that are valid for ad units.

```
AdUnitSize[] getAdUnitSizesByStatement(Statement filterStatement)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `filterStatement` | `Statement` | PQL query for filtering sizes |

**Returns:** `AdUnitSize[]` - Array of matching AdUnitSize objects

**Note:** This method is typically used to discover available sizes before creating or updating ad units.

---

##### updateAdUnits

Updates existing AdUnit objects.

```
AdUnit[] updateAdUnits(AdUnit[] adUnits)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `adUnits` | `AdUnit[]` | Array of AdUnit objects with updated values |

**Returns:** `AdUnit[]` - The updated AdUnit objects

**Notes:**
- `id` is required for identifying which unit to update
- `parentId` cannot be changed after creation
- `adUnitCode` cannot be changed after creation

---

##### performAdUnitAction

Performs bulk actions on AdUnit objects matching a query.

```
UpdateResult performAdUnitAction(AdUnitAction adUnitAction, Statement filterStatement)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `adUnitAction` | `AdUnitAction` | Action to perform (see [Actions Reference](#actions-reference)) |
| `filterStatement` | `Statement` | PQL query to select target ad units |

**Returns:** `UpdateResult` - Result containing count of affected objects

---

### PlacementService

Provides methods for managing Placement objects. Placements group ad units together for easier targeting.

**WSDL:** `https://ads.google.com/apis/ads/publisher/v202511/PlacementService?wsdl`

#### Methods

##### createPlacements

Creates new Placement objects.

```
Placement[] createPlacements(Placement[] placements)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `placements` | `Placement[]` | Array of Placement objects to create |

**Returns:** `Placement[]` - The created Placement objects with populated IDs

---

##### getPlacementsByStatement

Retrieves Placement objects matching a PQL query.

```
PlacementPage getPlacementsByStatement(Statement filterStatement)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `filterStatement` | `Statement` | PQL query with filtering, ordering, and pagination |

**Returns:** `PlacementPage` - Page of matching Placement objects

**Filterable Fields:**
- `id` - Placement ID
- `name` - Placement name
- `description` - Placement description
- `placementCode` - Unique placement code
- `status` - InventoryStatus (ACTIVE, INACTIVE, ARCHIVED)
- `lastModifiedDateTime` - Last modification timestamp

---

##### updatePlacements

Updates existing Placement objects.

```
Placement[] updatePlacements(Placement[] placements)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `placements` | `Placement[]` | Array of Placement objects with updated values |

**Returns:** `Placement[]` - The updated Placement objects

---

##### performPlacementAction

Performs bulk actions on Placement objects matching a query.

```
UpdateResult performPlacementAction(PlacementAction placementAction, Statement filterStatement)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `placementAction` | `PlacementAction` | Action to perform |
| `filterStatement` | `Statement` | PQL query to select target placements |

**Returns:** `UpdateResult` - Result containing count of affected objects

---

### SiteService

Provides methods for managing Site objects. Sites represent websites or apps within your network or MCM child networks.

**WSDL:** `https://ads.google.com/apis/ads/publisher/v202511/SiteService?wsdl`

#### Methods

##### createSites

Creates new Site objects.

```
Site[] createSites(Site[] sites)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `sites` | `Site[]` | Array of Site objects to create |

**Returns:** `Site[]` - The created Site objects with populated IDs

---

##### getSitesByStatement

Retrieves Site objects matching a PQL query.

```
SitePage getSitesByStatement(Statement filterStatement)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `filterStatement` | `Statement` | PQL query with filtering, ordering, and pagination |

**Returns:** `SitePage` - Page of matching Site objects

**Filterable Fields:**
- `id` - Site ID
- `url` - Site URL
- `childNetworkCode` - MCM child network code
- `approvalStatus` - Approval status (DRAFT, UNCHECKED, APPROVED, DISAPPROVED, REQUIRES_REVIEW)
- `lastModifiedApprovalStatusDateTime` - Last approval status change

---

##### updateSites

Updates existing Site objects.

```
Site[] updateSites(Site[] sites)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `sites` | `Site[]` | Array of Site objects with updated values |

**Returns:** `Site[]` - The updated Site objects

**Notes:**
- `childNetworkCode` can be updated to move sites between O&O and represented

---

##### performSiteAction

Performs bulk actions on Site objects matching a query.

```
UpdateResult performSiteAction(SiteAction siteAction, Statement filterStatement)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `siteAction` | `SiteAction` | Action to perform |
| `filterStatement` | `Statement` | PQL query to select target sites |

**Returns:** `UpdateResult` - Result containing count of affected objects

---

### SuggestedAdUnitService

Provides methods for retrieving and approving SuggestedAdUnit objects. These are undefined ad units that have received significant traffic (10+ requests in the past week).

**WSDL:** `https://ads.google.com/apis/ads/publisher/v202511/SuggestedAdUnitService?wsdl`

**Note:** This service is available only to Premium publishers.

#### Methods

##### getSuggestedAdUnitsByStatement

Retrieves SuggestedAdUnit objects matching a PQL query.

```
SuggestedAdUnitPage getSuggestedAdUnitsByStatement(Statement filterStatement)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `filterStatement` | `Statement` | PQL query with filtering, ordering, and pagination |

**Returns:** `SuggestedAdUnitPage` - Page of matching SuggestedAdUnit objects

**Filterable Fields:**
- `id` - SuggestedAdUnit ID
- `numRequests` - Number of serving requests in the past week

---

##### performSuggestedAdUnitAction

Approves SuggestedAdUnit objects, creating actual AdUnit objects.

```
SuggestedAdUnitUpdateResult performSuggestedAdUnitAction(
    SuggestedAdUnitAction suggestedAdUnitAction,
    Statement filterStatement
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `suggestedAdUnitAction` | `SuggestedAdUnitAction` | Action to perform (ApproveSuggestedAdUnits) |
| `filterStatement` | `Statement` | PQL query to select target suggested ad units |

**Returns:** `SuggestedAdUnitUpdateResult` - Result containing IDs of created ad units

---

## Data Models

### AdUnit

Represents a chunk of identified inventory for serving ads. An AdUnit contains all settings needed to serve ads to identified inventory and can be the parent of other ad units in the hierarchy.

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | `xsd:string` | Update only | Yes | Uniquely identifies the AdUnit. Assigned by Google when created. Required for updates. |
| `parentId` | `xsd:string` | Yes* | After creation | ID of parent ad unit. Required for creation (* except for root units). Cannot be changed after creation. |
| `hasChildren` | `xsd:boolean` | No | Yes | Indicates whether this ad unit has child ad units. |
| `parentPath` | `AdUnitParent[]` | No | Yes | Path to this ad unit in the hierarchy represented as a list from the root to this ad unit's parent. For root ad units, this list is empty. |
| `name` | `xsd:string` | Yes | No | Display name of the ad unit. Maximum 255 characters. Must be unique within the parent (case-insensitive). |
| `description` | `xsd:string` | No | No | Optional description. Maximum 65,535 characters. |
| `targetWindow` | `AdUnit.TargetWindow` | No | No | The value to use for the HTML link's target attribute. Defaults to TOP. |
| `status` | `InventoryStatus` | No | Indirect | Status of the ad unit. Defaults to ACTIVE. Can only be changed via performAdUnitAction, not direct update. |
| `adUnitCode` | `xsd:string` | No | After creation | A string used to uniquely identify the ad unit for serving. If not provided during creation, assigned by Google based on the ad unit ID. Immutable after creation. |
| `adUnitSizes` | `AdUnitSize[]` | No | No | The permissible creative sizes that can be served inside this ad unit. |
| `isInterstitial` | `xsd:boolean` | No | No | Whether this is an interstitial ad unit. |
| `isNative` | `xsd:boolean` | No | No | Whether this is a native ad unit. |
| `isFluid` | `xsd:boolean` | No | No | Whether this is a fluid ad unit. |
| `explicitlyTargeted` | `xsd:boolean` | No | No | If true, only line items explicitly targeting this ad unit can serve. Prevents serving from parent targeting. Ad Manager 360 only. |
| `adSenseSettings` | `AdSenseSettings` | No | No | AdSense-specific configuration for this ad unit. |
| `adSenseSettingsSource` | `ValueSourceType` | No | No | Indicates where the adSenseSettings value came from (PARENT or DIRECTLY_SPECIFIED). |
| `appliedLabelFrequencyCaps` | `LabelFrequencyCap[]` | No | No | Label-based frequency caps directly applied to this ad unit. Maximum 10 per ad unit. |
| `effectiveLabelFrequencyCaps` | `LabelFrequencyCap[]` | No | Yes | All frequency caps including those inherited from parent ad units. |
| `appliedLabels` | `AppliedLabel[]` | No | No | Labels directly applied to this ad unit. |
| `effectiveAppliedLabels` | `AppliedLabel[]` | No | Yes | All labels including those inherited from parent ad units. |
| `effectiveTeamIds` | `xsd:long[]` | No | Yes | Team IDs including those inherited from parent ad units. |
| `appliedTeamIds` | `xsd:long[]` | No | No | Team IDs directly assigned to this ad unit. |
| `lastModifiedDateTime` | `DateTime` | No | Yes | Timestamp of the last modification to this ad unit. |
| `smartSizeMode` | `SmartSizeMode` | No | No | The smart size mode for this ad unit. Determines how ad sizes are handled. Defaults to NONE. |
| `refreshRate` | `xsd:int` | No | No | The duration in seconds after which the ad unit will automatically refresh. Valid range: 30-120 seconds. Only applicable to mobile app ad units. |
| `externalSetTopBoxChannelId` | `xsd:string` | No | Yes | The external set-top box channel ID for this ad unit. |
| `isSetTopBoxEnabled` | `xsd:boolean` | No | Yes | Whether this ad unit is enabled for set-top box serving. |
| `applicationId` | `xsd:long` | No | No | The ID of the CTV application associated with this ad unit. |

---

### AdUnitSize

Defines permissible creative dimensions for an ad unit. Specifies what size creatives can be served.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `size` | `Size` | Yes | The permissible creative size that can be served inside this ad unit. |
| `environmentType` | `EnvironmentType` | No | The environment type of the ad unit size. Defaults to `BROWSER`. |
| `companions` | `AdUnitSize[]` | No | Companion sizes for video ad units. Only valid when `environmentType` is `VIDEO_PLAYER`. Invalid for `BROWSER` environments. |
| `fullDisplayString` | `xsd:string` | No | The full display string of the size including companion sizes. Examples: "300x250" or "300x250v (180x150)". Read-only, auto-generated. |
| `isAudio` | `xsd:boolean` | No | Whether this is an audio ad size. If true, `size` will be set to 1x1 and `environmentType` will be set to `VIDEO_PLAYER` regardless of user input. |

**Note:** For interstitial, native, ignored, and fluid sizes, the Size must be 1x1.

---

### Size

Represents dimensions for ad units, line items, or creatives.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `width` | `xsd:int` | Yes | The width of the AdUnit, LineItem, or Creative in pixels. |
| `height` | `xsd:int` | Yes | The height of the AdUnit, LineItem, or Creative in pixels. |
| `isAspectRatio` | `xsd:boolean` | No | Whether this size represents an aspect ratio rather than fixed dimensions. |

---

### AdUnitParent

Summary of a parent AdUnit in the hierarchy path. All fields are read-only and populated by Google.

| Field | Type | Read-Only | Description |
|-------|------|-----------|-------------|
| `id` | `xsd:string` | Yes | The ID of the parent AdUnit. |
| `name` | `xsd:string` | Yes | The name of the parent AdUnit. |
| `adUnitCode` | `xsd:string` | Yes | A string used to uniquely identify the ad unit for serving. Assigned by Google when an ad unit is created. |

---

### Placement

Groups ad units together for targeting purposes. Placements allow you to target multiple ad units with a single targeting criterion.

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | `xsd:long` | No | Yes | Uniquely identifies the Placement. Assigned by Google when created. |
| `name` | `xsd:string` | Yes | No | The name of the placement. Maximum 255 characters. |
| `description` | `xsd:string` | No | No | A description of the placement. Maximum 65,535 characters. |
| `placementCode` | `xsd:string` | No | Yes | A string used to uniquely identify the Placement for serving. Assigned by Google when created. |
| `status` | `InventoryStatus` | No | Yes | The status of the placement. Modified via performPlacementAction only. |
| `targetedAdUnitIds` | `xsd:string[]` | No | No | The collection of AdUnit IDs that constitute this placement. |
| `lastModifiedDateTime` | `DateTime` | No | No | Timestamp of the most recent update to this placement. |

**Inherited From:** SiteTargetingInfo

---

### Site

Represents a website or app in your network. Used for Multiple Customer Management (MCM) scenarios.

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | `xsd:long` | No | Yes | Uniquely identifies the Site. Assigned by Google when created. |
| `url` | `xsd:string` | Yes | No | The URL of the Site (domain address). |
| `childNetworkCode` | `xsd:string` | No | No | The network code for a child network in MCM scenarios. Null if owned by the current network (O&O). Can be updated to move sites between O&O and represented. |
| `approvalStatus` | `ApprovalStatus` | No | Yes | Status of the review performed on the Site by Google. |
| `approvalStatusUpdateTime` | `DateTime` | No | No | The latest site approval status change time. |
| `disapprovalReasons` | `DisapprovalReason[]` | No | Yes | Provides reasons for disapproving the site. Null when the Site is not disapproved. |

#### ApprovalStatus Enum

| Value | Description |
|-------|-------------|
| `DRAFT` | Site has not yet been submitted for approval. |
| `UNCHECKED` | Site has been submitted but not yet reviewed by Google. |
| `APPROVED` | Site has been approved by Google. |
| `DISAPPROVED` | Site has been rejected by Google. Check `disapprovalReasons` for details. |
| `REQUIRES_REVIEW` | Site requires additional review by Google. |
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |

#### DisapprovalReason.Type Enum

| Value | Description |
|-------|-------------|
| `CONTENT` | The site has content that violates policy. |
| `OWNERSHIP` | The parent must be an authorized seller of the child network's inventory. |
| `OTHER` | Generic error type for other disapproval reasons. |
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |

---

### SuggestedAdUnit

Represents an undefined ad unit detected from traffic. A suggested ad unit is created when an ad tag receives at least 10 serving requests in the past week without a corresponding defined ad unit. All fields are read-only and auto-populated by Google.

| Field | Type | Read-Only | Description |
|-------|------|-----------|-------------|
| `id` | `xsd:string` | Yes | Unique identifier. Numerical after API version 201311. |
| `numRequests` | `xsd:long` | Yes | Count of ad tag serves from the previous week. Suggested ad units are only created when they have been served at least 10 times in that period. |
| `path` | `xsd:string[]` | Yes | Hierarchical path elements representing ad unit codes from the last existing unit forward. Each path element is a separate ad unit code in the returned list. |
| `parentPath` | `AdUnitParent[]` | Yes | Existing hierarchy leading to the parent of the first suggested unit. Combined with `path`, these form the complete path after approval. Note: Parent ad unit codes are not provided. |
| `targetWindow` | `AdUnit.TargetWindow` | Yes | Link target behavior from the underlying ad tag (TOP or BLANK). |
| `targetPlatform` | `TargetPlatform` | Yes | Browser platform for the clicked ad tag. |
| `suggestedAdUnitSizes` | `AdUnitSize[]` | Yes | Associated ad sizes detected from ad requests. |

#### TargetPlatform Enum

| Value | Description |
|-------|-------------|
| `WEB` | Desktop web browsers. |
| `MOBILE` | Mobile devices. |
| `ANY` | Any platform (universal). |

---

## Supporting Types and Enumerations

This section documents all supporting types, nested objects, and enumerations used by the main data models.

### EnvironmentType Enum

Specifies where ads can be displayed.

| Value | Description |
|-------|-------------|
| `BROWSER` | A regular web browser. This is the default value. |
| `VIDEO_PLAYER` | Video players. |

---

### InventoryStatus Enum

Represents the status of inventory objects (ad units and placements).

| Value | Description |
|-------|-------------|
| `ACTIVE` | The object is active and eligible for ad serving. |
| `INACTIVE` | The object is no longer active. It is visible but not serving ads. |
| `ARCHIVED` | The object has been archived. It is hidden and not serving ads. |

---

### AdUnit.TargetWindow Enum

Corresponds to the HTML link's target attribute.

| Value | Description |
|-------|-------------|
| `TOP` | Specifies that the link should open in the full body of the page. |
| `BLANK` | Specifies that the link should open in a new window. |

---

### SmartSizeMode Enum

Determines how ad sizes are handled for an ad unit.

| Value | Description |
|-------|-------------|
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |
| `NONE` | Fixed size mode. This is the default value. |
| `SMART_BANNER` | The height is fixed for the request, the width is a range. Used for smart banners that adapt to screen width. |
| `DYNAMIC_SIZE` | Height and width are both ranges. Allows flexible sizing. |

---

### ValueSourceType Enum

Identifies the source of a field's value within inherited settings.

| Value | Description |
|-------|-------------|
| `PARENT` | The field's value is inherited from the parent object. |
| `DIRECTLY_SPECIFIED` | The field's value is user specified and not inherited. |
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |

---

### AdSenseSettings

Contains all AdSense-specific configuration for an ad unit. All fields support inheritance from parent ad units.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `adSenseEnabled` | `xsd:boolean` | `true` | Controls whether an AdUnit serves ads from AdSense content network. Defaults to the ad unit's parent or ancestor's setting if one has been set. |
| `borderColor` | `xsd:string` | `FFFFFF` | Hexadecimal border color (000000 to FFFFFF). |
| `titleColor` | `xsd:string` | `0000FF` | Hexadecimal ad title color (000000 to FFFFFF). |
| `backgroundColor` | `xsd:string` | `FFFFFF` | Hexadecimal ad background color (000000 to FFFFFF). |
| `textColor` | `xsd:string` | `000000` | Hexadecimal ad text color (000000 to FFFFFF). |
| `urlColor` | `xsd:string` | `008000` | Hexadecimal ad URL color (000000 to FFFFFF). |
| `adType` | `AdSenseSettings.AdType` | `TEXT_AND_IMAGE` | Controls which ad formats can be served. |
| `borderStyle` | `AdSenseSettings.BorderStyle` | `DEFAULT` | Controls the border style of ad elements. |
| `fontFamily` | `AdSenseSettings.FontFamily` | `DEFAULT` | The font family for ad text. |
| `fontSize` | `AdSenseSettings.FontSize` | `DEFAULT` | The font size for ad text. |

#### AdSenseSettings.AdType Enum

| Value | Description |
|-------|-------------|
| `TEXT` | Allows text-only ads. |
| `IMAGE` | Allows image-only ads. |
| `TEXT_AND_IMAGE` | Allows both text and image ads. This is the default. |

#### AdSenseSettings.BorderStyle Enum

| Value | Description |
|-------|-------------|
| `DEFAULT` | Uses the default border-style of the browser. |
| `NOT_ROUNDED` | Uses a cornered (square) border-style. |
| `SLIGHTLY_ROUNDED` | Uses a slightly rounded border-style. |
| `VERY_ROUNDED` | Uses a rounded border-style. |

#### AdSenseSettings.FontFamily Enum

| Value | Description |
|-------|-------------|
| `DEFAULT` | Uses the default font family. |
| `ARIAL` | Uses Arial font family. |
| `TAHOMA` | Uses Tahoma font family. |
| `GEORGIA` | Uses Georgia font family. |
| `TIMES` | Uses Times font family. |
| `VERDANA` | Uses Verdana font family. |

#### AdSenseSettings.FontSize Enum

| Value | Description |
|-------|-------------|
| `DEFAULT` | Uses the default font size. |
| `SMALL` | Uses a small font size. |
| `MEDIUM` | Uses a medium font size. |
| `LARGE` | Uses a large font size. |

---

### LabelFrequencyCap

Limits the cumulative number of impressions of any ad units with a specific label that may be shown to a particular user over a time unit.

| Field | Type | Description |
|-------|------|-------------|
| `frequencyCap` | `FrequencyCap` | The frequency cap to be applied with this label. |
| `labelId` | `xsd:long` | ID of the label being capped on the AdUnit. |

---

### FrequencyCap

Represents a limit on the number of times a single viewer can be exposed to the same content in a specified time period.

| Field | Type | Description |
|-------|------|-------------|
| `maxImpressions` | `xsd:int` | The maximum number of impressions that can be served to a user within the specified time period. |
| `numTimeUnits` | `xsd:int` | The number of time units that represent the total time period. |
| `timeUnit` | `TimeUnit` | The unit of time for specifying the time period. |

#### TimeUnit Enum

| Value | Description |
|-------|-------------|
| `MINUTE` | Time period measured in minutes. |
| `HOUR` | Time period measured in hours. |
| `DAY` | Time period measured in days. |
| `WEEK` | Time period measured in weeks. |
| `MONTH` | Time period measured in months. |
| `LIFETIME` | Total lifetime of the campaign. |
| `POD` | A single ad pod (video). |
| `STREAM` | A single video stream. |
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |

---

### AppliedLabel

Represents a Label that can be applied to entities.

| Field | Type | Description |
|-------|------|-------------|
| `labelId` | `xsd:long` | The ID of a created Label. |
| `isNegated` | `xsd:boolean` | Used to negate label effects. Set to true to negate the effects of labelId and override inherited labels. |

---

## Ad Unit Hierarchy

### Structure Overview

Ad units form a tree structure:

```
Effective Root Ad Unit
├── Section: News
│   ├── Subsection: Politics
│   │   ├── Article Header (300x250, 728x90)
│   │   └── Article Sidebar (300x600)
│   └── Subsection: Sports
│       ├── Article Header (300x250, 728x90)
│       └── Article Sidebar (300x600)
├── Section: Entertainment
│   └── ...
└── Section: Technology
    └── ...
```

### Retrieving the Effective Root

The effective root is the topmost ad unit you can modify. Retrieve it via NetworkService:

```python
from googleads import ad_manager

client = ad_manager.AdManagerClient.LoadFromStorage()
network_service = client.GetService('NetworkService', version='v202511')

network = network_service.getCurrentNetwork()
effective_root_id = network['effectiveRootAdUnitId']
print(f"Effective root ad unit ID: {effective_root_id}")
```

### Inheritance Behavior

Child ad units inherit properties from parents:

| Property | Inheritance |
|----------|-------------|
| Labels | Inherited + directly applied |
| Team access | Inherited + directly assigned |
| Frequency caps | Inherited + directly applied |
| AdSense settings | Inherited unless directly specified |
| Targeting | Implicit (unless `explicitlyTargeted` is true) |

### Hierarchy Limits

| Account Type | Max Depth | Notes |
|--------------|-----------|-------|
| Small Business | 2 levels | Limited hierarchy |
| Premium | 6+ levels | Deep hierarchy support |

---

## Actions Reference

Actions are performed via the `performXxxAction` methods on each service. They allow bulk status changes to objects matching a PQL filter statement.

### AdUnit Actions (AdUnitAction)

Used with `InventoryService.performAdUnitAction()`.

| Action Class | Description | Effect on Status |
|--------------|-------------|------------------|
| `ActivateAdUnits` | Enables ad units for ad serving. Makes them available in targeting pickers for line items, rules, and other features. | `INACTIVE` -> `ACTIVE` |
| `DeactivateAdUnits` | Makes ad units ineligible for ad serving. Removes them from targeting pickers but they remain visible in the ad unit table. | `ACTIVE` -> `INACTIVE` |
| `ArchiveAdUnits` | Archives ad units, making them ineligible for serving. Removes them from targeting pickers and hides them from the default ad unit table view. Must filter to view archived units. | `ACTIVE` or `INACTIVE` -> `ARCHIVED` |

**Important Notes:**
- Changes are saved and applied immediately
- It can take up to 180 minutes before the change affects ad serving
- Archived ad units can be reactivated if needed
- Deactivating a parent ad unit does not automatically deactivate children

### Placement Actions (PlacementAction)

Used with `PlacementService.performPlacementAction()`.

| Action Class | Description | Effect on Status |
|--------------|-------------|------------------|
| `ActivatePlacements` | Enables placements for targeting. | `INACTIVE` -> `ACTIVE` |
| `DeactivatePlacements` | Disables placements. They remain visible but cannot be used for new targeting. | `ACTIVE` -> `INACTIVE` |
| `ArchivePlacements` | Archives placements. They are hidden and cannot be targeted. | `ACTIVE` or `INACTIVE` -> `ARCHIVED` |

### Site Actions (SiteAction)

Used with `SiteService.performSiteAction()`.

| Action Class | Description | Use Case |
|--------------|-------------|----------|
| `DeactivateSite` | Deactivates the site, preventing ad serving. | When you no longer want to serve ads on a site. |
| `SubmitSiteForApproval` | Submits the site for Google review. Changes approval status from DRAFT to UNCHECKED. | Required for MCM child networks before ads can serve. |

**Approval Workflow:**
1. Create site (status: `DRAFT`)
2. Perform `SubmitSiteForApproval` action (status: `UNCHECKED`)
3. Google reviews the site
4. Status changes to `APPROVED`, `DISAPPROVED`, or `REQUIRES_REVIEW`

### SuggestedAdUnit Actions (SuggestedAdUnitAction)

Used with `SuggestedAdUnitService.performSuggestedAdUnitAction()`.

| Action Class | Description | Result |
|--------------|-------------|--------|
| `ApproveSuggestedAdUnits` | Approves suggested ad units, creating actual AdUnit objects in your inventory. | Returns `SuggestedAdUnitUpdateResult` containing the IDs of newly created ad units. |

**Notes:**
- Approved suggested ad units become real ad units that can be targeted
- The suggested ad unit is removed after approval
- Unapproved suggested ad units automatically disappear if they receive fewer than 10 requests in a 7-day period

---

## PQL Filtering

### Syntax Overview

Publisher Query Language (PQL) provides SQL-like filtering:

```sql
WHERE field operator value [AND|OR condition]
ORDER BY field [ASC|DESC]
LIMIT count OFFSET offset
```

### Supported Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equals | `WHERE status = 'ACTIVE'` |
| `!=` | Not equals | `WHERE status != 'ARCHIVED'` |
| `IN` | In list | `WHERE id IN (123, 456, 789)` |
| `NOT IN` | Not in list | `WHERE status NOT IN ('ARCHIVED')` |
| `LIKE` | Wildcard match | `WHERE name LIKE 'Sports%'` |
| `IS NULL` | Null check | `WHERE parentId IS NULL` |

### Service-Specific Filterable Fields

#### InventoryService (AdUnits)

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | AdUnit ID |
| `name` | string | AdUnit name |
| `adUnitCode` | string | Unique code |
| `parentId` | string | Parent ID (NULL for root) |
| `status` | enum | ACTIVE, INACTIVE, ARCHIVED |
| `lastModifiedDateTime` | datetime | Last modification |

#### PlacementService

| Field | Type | Description |
|-------|------|-------------|
| `id` | long | Placement ID |
| `name` | string | Placement name |
| `description` | string | Description |
| `placementCode` | string | Unique code |
| `status` | enum | ACTIVE, INACTIVE, ARCHIVED |
| `lastModifiedDateTime` | datetime | Last modification |

#### SiteService

| Field | Type | Description |
|-------|------|-------------|
| `id` | long | Site ID |
| `url` | string | Site URL |
| `childNetworkCode` | string | Child network code |
| `approvalStatus` | enum | Approval status |
| `lastModifiedApprovalStatusDateTime` | datetime | Status change time |

#### SuggestedAdUnitService

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | SuggestedAdUnit ID |
| `numRequests` | long | Request count |

### Query Examples

```python
# Find root ad unit
"WHERE parentId IS NULL"

# Active ad units modified recently
"WHERE status = 'ACTIVE' AND lastModifiedDateTime > '2024-01-01T00:00:00'"

# Ad units by name pattern
"WHERE name LIKE 'Sports%' ORDER BY name ASC"

# Specific ad units by ID
"WHERE id IN ('12345', '67890')"

# Paginated results
"WHERE status = 'ACTIVE' ORDER BY id ASC LIMIT 100 OFFSET 0"
```

---

## Python Code Examples

### Setup and Configuration

```python
"""
Google Ad Manager Inventory Management Examples

Requires:
    pip install googleads

Configuration file (~/googleads.yaml):
    ad_manager:
      application_name: My Inventory Manager
      network_code: 'YOUR_NETWORK_CODE'
      client_id: 'YOUR_CLIENT_ID'
      client_secret: 'YOUR_CLIENT_SECRET'
      refresh_token: 'YOUR_REFRESH_TOKEN'
"""

from googleads import ad_manager

# Initialize client
client = ad_manager.AdManagerClient.LoadFromStorage()
```

### Creating Ad Unit Hierarchies

```python
def create_ad_unit_hierarchy(client):
    """Creates a complete ad unit hierarchy for a website section."""

    # Get services
    inventory_service = client.GetService('InventoryService', version='v202511')
    network_service = client.GetService('NetworkService', version='v202511')

    # Get effective root ad unit ID
    network = network_service.getCurrentNetwork()
    effective_root_id = network['effectiveRootAdUnitId']

    # Create parent section
    section_ad_unit = {
        'name': 'Sports Section',
        'description': 'All sports-related content',
        'parentId': effective_root_id,
        'targetWindow': 'TOP',
        'adUnitSizes': [
            {
                'size': {'width': 728, 'height': 90},
                'environmentType': 'BROWSER'
            },
            {
                'size': {'width': 300, 'height': 250},
                'environmentType': 'BROWSER'
            }
        ]
    }

    created_sections = inventory_service.createAdUnits([section_ad_unit])
    section_id = created_sections[0]['id']
    print(f"Created section: {created_sections[0]['name']} (ID: {section_id})")

    # Create child ad units
    child_ad_units = [
        {
            'name': 'Sports - Header',
            'parentId': section_id,
            'adUnitCode': 'sports_header',
            'adUnitSizes': [
                {'size': {'width': 728, 'height': 90}, 'environmentType': 'BROWSER'},
                {'size': {'width': 970, 'height': 250}, 'environmentType': 'BROWSER'}
            ]
        },
        {
            'name': 'Sports - Sidebar',
            'parentId': section_id,
            'adUnitCode': 'sports_sidebar',
            'adUnitSizes': [
                {'size': {'width': 300, 'height': 250}, 'environmentType': 'BROWSER'},
                {'size': {'width': 300, 'height': 600}, 'environmentType': 'BROWSER'}
            ]
        },
        {
            'name': 'Sports - Article Bottom',
            'parentId': section_id,
            'adUnitCode': 'sports_article_bottom',
            'adUnitSizes': [
                {'size': {'width': 728, 'height': 90}, 'environmentType': 'BROWSER'}
            ]
        }
    ]

    created_children = inventory_service.createAdUnits(child_ad_units)

    for ad_unit in created_children:
        print(f"  Created: {ad_unit['name']} (ID: {ad_unit['id']})")

    return section_id, [au['id'] for au in created_children]


if __name__ == '__main__':
    client = ad_manager.AdManagerClient.LoadFromStorage()
    create_ad_unit_hierarchy(client)
```

### Creating Placements from Ad Units

```python
def create_placement_from_ad_units(client, ad_unit_ids, placement_name):
    """Creates a placement containing specified ad units."""

    placement_service = client.GetService('PlacementService', version='v202511')

    placement = {
        'name': placement_name,
        'description': f'Placement grouping {len(ad_unit_ids)} ad units',
        'targetedAdUnitIds': ad_unit_ids
    }

    created_placements = placement_service.createPlacements([placement])
    placement = created_placements[0]

    print(f"Created placement: {placement['name']}")
    print(f"  ID: {placement['id']}")
    print(f"  Code: {placement['placementCode']}")
    print(f"  Status: {placement['status']}")
    print(f"  Ad Units: {len(placement['targetedAdUnitIds'])} units")

    return placement


def create_sports_placements(client):
    """Creates multiple themed placements."""

    inventory_service = client.GetService('InventoryService', version='v202511')
    placement_service = client.GetService('PlacementService', version='v202511')

    # Query for sports ad units
    statement = ad_manager.StatementBuilder(version='v202511')
    statement.Where("name LIKE 'Sports%' AND status = 'ACTIVE'")

    response = inventory_service.getAdUnitsByStatement(
        statement.ToStatement()
    )

    if 'results' in response:
        ad_unit_ids = [au['id'] for au in response['results']]

        # Create the placement
        placement = {
            'name': 'Sports Section - All Units',
            'description': 'All active sports section ad units for easy targeting',
            'targetedAdUnitIds': ad_unit_ids
        }

        created = placement_service.createPlacements([placement])
        print(f"Created placement with {len(ad_unit_ids)} ad units")
        return created[0]

    return None


if __name__ == '__main__':
    client = ad_manager.AdManagerClient.LoadFromStorage()
    create_sports_placements(client)
```

### Managing Sites

```python
def create_sites_for_network(client, urls, child_network_code=None):
    """Creates sites, optionally for an MCM child network."""

    site_service = client.GetService('SiteService', version='v202511')

    sites = []
    for url in urls:
        site = {
            'url': url
        }
        if child_network_code:
            site['childNetworkCode'] = child_network_code
        sites.append(site)

    created_sites = site_service.createSites(sites)

    for site in created_sites:
        print(f"Created site: {site['url']}")
        print(f"  ID: {site['id']}")
        print(f"  Status: {site['approvalStatus']}")
        if site.get('childNetworkCode'):
            print(f"  Child Network: {site['childNetworkCode']}")

    return created_sites


def submit_sites_for_approval(client, site_ids):
    """Submits sites for Google approval."""

    site_service = client.GetService('SiteService', version='v202511')

    statement = ad_manager.StatementBuilder(version='v202511')
    statement.Where(f"id IN ({','.join(map(str, site_ids))})")

    action = {'xsi_type': 'SubmitSiteForApproval'}

    result = site_service.performSiteAction(
        action,
        statement.ToStatement()
    )

    print(f"Submitted {result['numChanges']} sites for approval")
    return result


def get_disapproved_sites(client):
    """Retrieves all disapproved sites with reasons."""

    site_service = client.GetService('SiteService', version='v202511')

    statement = ad_manager.StatementBuilder(version='v202511')
    statement.Where("approvalStatus = 'DISAPPROVED'")

    response = site_service.getSitesByStatement(statement.ToStatement())

    if 'results' in response:
        for site in response['results']:
            print(f"Disapproved: {site['url']}")
            if site.get('disapprovalReasons'):
                for reason in site['disapprovalReasons']:
                    print(f"  Reason: {reason}")

    return response.get('results', [])


if __name__ == '__main__':
    client = ad_manager.AdManagerClient.LoadFromStorage()

    # Create O&O sites
    urls = ['https://example.com', 'https://blog.example.com']
    create_sites_for_network(client, urls)
```

### Querying Inventory

```python
def get_all_active_ad_units(client):
    """Retrieves all active ad units with pagination."""

    inventory_service = client.GetService('InventoryService', version='v202511')

    statement = ad_manager.StatementBuilder(version='v202511')
    statement.Where("status = 'ACTIVE'")
    statement.OrderBy('name', ascending=True)
    statement.Limit(500)

    all_ad_units = []

    while True:
        response = inventory_service.getAdUnitsByStatement(
            statement.ToStatement()
        )

        if 'results' in response:
            all_ad_units.extend(response['results'])
            print(f"Retrieved {len(all_ad_units)} ad units...")

            statement.IncreaseOffsetBy(500)

            if len(response['results']) < 500:
                break
        else:
            break

    return all_ad_units


def get_ad_unit_hierarchy(client, parent_id=None):
    """Retrieves ad unit hierarchy tree."""

    inventory_service = client.GetService('InventoryService', version='v202511')

    if parent_id:
        where_clause = f"parentId = '{parent_id}'"
    else:
        where_clause = "parentId IS NULL"

    statement = ad_manager.StatementBuilder(version='v202511')
    statement.Where(where_clause)
    statement.OrderBy('name', ascending=True)

    response = inventory_service.getAdUnitsByStatement(statement.ToStatement())

    hierarchy = []
    if 'results' in response:
        for ad_unit in response['results']:
            node = {
                'id': ad_unit['id'],
                'name': ad_unit['name'],
                'code': ad_unit.get('adUnitCode'),
                'status': ad_unit['status'],
                'children': []
            }

            if ad_unit.get('hasChildren'):
                node['children'] = get_ad_unit_hierarchy(client, ad_unit['id'])

            hierarchy.append(node)

    return hierarchy


def print_hierarchy(hierarchy, indent=0):
    """Prints ad unit hierarchy as tree."""
    for node in hierarchy:
        prefix = "  " * indent
        status_icon = "[+]" if node['status'] == 'ACTIVE' else "[-]"
        print(f"{prefix}{status_icon} {node['name']} ({node['code'] or 'no code'})")
        if node['children']:
            print_hierarchy(node['children'], indent + 1)


if __name__ == '__main__':
    client = ad_manager.AdManagerClient.LoadFromStorage()

    hierarchy = get_ad_unit_hierarchy(client)
    print_hierarchy(hierarchy)
```

### Bulk Operations

```python
def archive_inactive_ad_units(client, days_inactive=90):
    """Archives ad units that have been inactive for specified days."""

    from datetime import datetime, timedelta

    inventory_service = client.GetService('InventoryService', version='v202511')

    cutoff_date = datetime.now() - timedelta(days=days_inactive)
    cutoff_str = cutoff_date.strftime('%Y-%m-%dT%H:%M:%S')

    statement = ad_manager.StatementBuilder(version='v202511')
    statement.Where(
        f"status = 'INACTIVE' AND lastModifiedDateTime < '{cutoff_str}'"
    )

    action = {'xsi_type': 'ArchiveAdUnits'}

    result = inventory_service.performAdUnitAction(
        action,
        statement.ToStatement()
    )

    print(f"Archived {result['numChanges']} inactive ad units")
    return result


def activate_ad_units_by_pattern(client, name_pattern):
    """Activates all ad units matching a name pattern."""

    inventory_service = client.GetService('InventoryService', version='v202511')

    statement = ad_manager.StatementBuilder(version='v202511')
    statement.Where(f"name LIKE '{name_pattern}' AND status = 'INACTIVE'")

    action = {'xsi_type': 'ActivateAdUnits'}

    result = inventory_service.performAdUnitAction(
        action,
        statement.ToStatement()
    )

    print(f"Activated {result['numChanges']} ad units matching '{name_pattern}'")
    return result


def bulk_update_ad_unit_sizes(client, ad_unit_ids, new_sizes):
    """Updates sizes for multiple ad units."""

    inventory_service = client.GetService('InventoryService', version='v202511')

    # First, fetch the ad units
    id_list = ','.join([f"'{id}'" for id in ad_unit_ids])
    statement = ad_manager.StatementBuilder(version='v202511')
    statement.Where(f"id IN ({id_list})")

    response = inventory_service.getAdUnitsByStatement(statement.ToStatement())

    if 'results' in response:
        ad_units = response['results']

        # Update sizes
        for ad_unit in ad_units:
            ad_unit['adUnitSizes'] = new_sizes

        updated = inventory_service.updateAdUnits(ad_units)
        print(f"Updated sizes for {len(updated)} ad units")
        return updated

    return []


if __name__ == '__main__':
    client = ad_manager.AdManagerClient.LoadFromStorage()

    # Archive old inactive units
    archive_inactive_ad_units(client, days_inactive=90)

    # Activate sports units
    activate_ad_units_by_pattern(client, 'Sports%')
```

### Working with Suggested Ad Units

```python
def get_high_traffic_suggested_units(client, min_requests=100):
    """Retrieves suggested ad units with high traffic."""

    suggested_service = client.GetService(
        'SuggestedAdUnitService',
        version='v202511'
    )

    statement = ad_manager.StatementBuilder(version='v202511')
    statement.Where(f"numRequests >= {min_requests}")
    statement.OrderBy('numRequests', ascending=False)

    response = suggested_service.getSuggestedAdUnitsByStatement(
        statement.ToStatement()
    )

    if 'results' in response:
        print(f"Found {len(response['results'])} high-traffic suggested units:")
        for unit in response['results']:
            print(f"  Path: {'/'.join(unit['path'])}")
            print(f"    Requests: {unit['numRequests']}")
            print(f"    Sizes: {[s['fullDisplayString'] for s in unit.get('suggestedAdUnitSizes', [])]}")
        return response['results']

    return []


def approve_suggested_ad_units(client, suggested_ids):
    """Approves suggested ad units, creating real ad units."""

    suggested_service = client.GetService(
        'SuggestedAdUnitService',
        version='v202511'
    )

    id_list = ','.join([f"'{id}'" for id in suggested_ids])
    statement = ad_manager.StatementBuilder(version='v202511')
    statement.Where(f"id IN ({id_list})")

    action = {'xsi_type': 'ApproveSuggestedAdUnits'}

    result = suggested_service.performSuggestedAdUnitAction(
        action,
        statement.ToStatement()
    )

    if result.get('newAdUnitIds'):
        print(f"Created {len(result['newAdUnitIds'])} new ad units:")
        for ad_unit_id in result['newAdUnitIds']:
            print(f"  - {ad_unit_id}")

    return result


def auto_approve_high_traffic(client, min_requests=1000):
    """Automatically approves suggested units with very high traffic."""

    suggested_service = client.GetService(
        'SuggestedAdUnitService',
        version='v202511'
    )

    statement = ad_manager.StatementBuilder(version='v202511')
    statement.Where(f"numRequests >= {min_requests}")

    action = {'xsi_type': 'ApproveSuggestedAdUnits'}

    result = suggested_service.performSuggestedAdUnitAction(
        action,
        statement.ToStatement()
    )

    print(f"Auto-approved suggested units with {min_requests}+ requests")
    print(f"Created {len(result.get('newAdUnitIds', []))} new ad units")

    return result


if __name__ == '__main__':
    client = ad_manager.AdManagerClient.LoadFromStorage()

    # Review high-traffic suggestions
    suggestions = get_high_traffic_suggested_units(client, min_requests=100)
```

---

## Common Patterns

### 1. Inventory Structure by Content Type

```
Root
├── Desktop
│   ├── Above the Fold
│   │   ├── Leaderboard (728x90)
│   │   └── Billboard (970x250)
│   └── Below the Fold
│       ├── Medium Rectangle (300x250)
│       └── Skyscraper (300x600)
├── Mobile
│   ├── Mobile Leaderboard (320x50)
│   └── Mobile Banner (320x100)
└── Video
    ├── Pre-roll
    └── Mid-roll
```

### 2. Inventory Structure by Site Section

```
Root
├── Homepage
│   ├── Hero Unit
│   └── Sidebar
├── News
│   ├── Article Page
│   │   ├── Header
│   │   ├── In-content
│   │   └── Footer
│   └── Category Page
└── Sports
    └── ...
```

### 3. Placement Strategies

| Strategy | Description | Example |
|----------|-------------|---------|
| By Format | Group same-size units | "All 300x250 units" |
| By Section | Group by content area | "Sports Section" |
| By Value | Group by CPM tier | "Premium Inventory" |
| By Device | Group by platform | "Mobile Web Units" |
| Run of Site | All units | "ROS Placement" |

### 4. Naming Conventions

```
# Ad Unit naming pattern
{Section}_{Page}_{Position}_{Size}

Examples:
- Sports_Article_Header_728x90
- News_Homepage_Sidebar_300x600
- Mobile_App_Interstitial

# Placement naming pattern
{Type}_{Section/Format}_{Qualifier}

Examples:
- ROS_AllUnits_Premium
- Section_Sports_Desktop
- Format_Video_Preroll
```

### 5. Status Management Workflow

```
1. Creation
   └── Status: INACTIVE (default)

2. Testing
   └── Status: INACTIVE (verify tags work)

3. Launch
   └── Action: Activate → Status: ACTIVE

4. Pause
   └── Action: Deactivate → Status: INACTIVE

5. Retirement
   └── Action: Archive → Status: ARCHIVED
```

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `EntityLimitReachedError` | Too many ad units/placements | Archive unused inventory |
| `EntityChildrenLimitReachedError` | Too many children for parent | Restructure hierarchy |
| `UniqueError` | Duplicate name or code | Use unique identifiers |
| `RequiredError` | Missing required field | Provide `name` and `parentId` |
| `NotNullError` | Null value for required field | Check field values |
| `RangeError` | Value out of bounds | Check size/refresh rate limits |
| `PlacementError` | Invalid placement configuration | Verify ad unit IDs exist |

### Error Handling Pattern

```python
from googleads import ad_manager
from googleads.errors import GoogleAdsServerFault

def safe_create_ad_unit(client, ad_unit):
    """Creates an ad unit with comprehensive error handling."""

    inventory_service = client.GetService('InventoryService', version='v202511')

    try:
        result = inventory_service.createAdUnits([ad_unit])
        return result[0]

    except GoogleAdsServerFault as e:
        for error in e.errors:
            error_type = error['errorType']

            if error_type == 'UniqueError':
                print(f"Ad unit name/code already exists: {ad_unit['name']}")
            elif error_type == 'RequiredError':
                print(f"Missing required field: {error.get('fieldPath')}")
            elif error_type == 'EntityLimitReachedError':
                print("Ad unit limit reached. Archive unused units.")
            elif error_type == 'AuthenticationError':
                print("Authentication failed. Check credentials.")
            else:
                print(f"Error: {error_type} - {error.get('errorString')}")

        return None
```

---

## References

### Official Documentation

- [InventoryService v202511](https://developers.google.com/ad-manager/api/reference/v202511/InventoryService)
- [PlacementService v202511](https://developers.google.com/ad-manager/api/reference/v202511/PlacementService)
- [SiteService v202511](https://developers.google.com/ad-manager/api/reference/v202511/SiteService)
- [SuggestedAdUnitService v202511](https://developers.google.com/ad-manager/api/reference/v202511/SuggestedAdUnitService)
- [PQL Reference Guide](https://developers.google.com/ad-manager/api/pqlreference)
- [Ad Unit Hierarchy (Help Center)](https://support.google.com/admanager/answer/177203)

### Python Client Library

- [googleads-python-lib GitHub](https://github.com/googleads/googleads-python-lib)
- [PyPI Package](https://pypi.org/project/googleads/)

### Related Documentation in This Repository

- [SOAP API Overview](../README.md)
- [Reporting Category](../reporting/README.md)
- [Targeting Category](../targeting/README.md)

---

*This documentation was generated for Google Ad Manager SOAP API v202511. For the latest API updates, always refer to the official Google documentation.*
