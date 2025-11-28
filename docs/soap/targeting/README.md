# Google Ad Manager SOAP API v202511 - Targeting

This document provides comprehensive documentation for the **Targeting** category of the Google Ad Manager SOAP API v202511. It covers custom targeting, audience segments, segment population, and targeting presets.

**Last Updated:** 2025-11-28
**API Version:** v202511
**WSDL Namespace:** `https://www.google.com/apis/ads/publisher/v202511`

---

## Table of Contents

1. [Overview](#overview)
2. [Targeting Types](#targeting-types)
3. [Services Reference](#services-reference)
   - [CustomTargetingService](#customtargetingservice)
   - [AudienceSegmentService](#audiencesegmentservice)
   - [SegmentPopulationService](#segmentpopulationservice)
   - [TargetingPresetService](#targetingpresetservice)
4. [Data Models](#data-models)
   - [CustomTargetingKey](#customtargetingkey)
   - [CustomTargetingValue](#customtargetingvalue)
   - [CustomCriteria and CustomCriteriaSet](#customcriteria-and-customcriteriaset)
   - [AudienceSegment](#audiencesegment)
   - [SegmentPopulationRequest](#segmentpopulationrequest)
   - [TargetingPreset](#targetingpreset)
   - [Targeting Object](#targeting-object)
5. [Targeting Sub-Types](#targeting-sub-types)
   - [InventoryTargeting](#inventorytargeting)
   - [GeoTargeting](#geotargeting)
   - [DayPartTargeting](#dayparttargeting)
   - [TechnologyTargeting](#technologytargeting)
   - [VideoPositionTargeting](#videopositiontargeting)
   - [ContentTargeting](#contenttargeting)
   - [UserDomainTargeting](#userdomaintargeting)
   - [RequestPlatformTargeting](#requestplatformtargeting)
   - [InventoryUrlTargeting](#inventoryurltargeting)
   - [BuyerUserListTargeting](#buyeruserlisttargeting)
6. [Custom Targeting](#custom-targeting)
   - [Keys vs Values](#keys-vs-values)
   - [Match Types](#match-types)
   - [Hierarchies](#hierarchies)
7. [Targeting Expression Syntax](#targeting-expression-syntax)
8. [Actions Reference](#actions-reference)
9. [Python Code Examples](#python-code-examples)
10. [Error Handling](#error-handling)
11. [Best Practices](#best-practices)

---

## Overview

Targeting in Google Ad Manager determines **where** and **to whom** ads are displayed. The targeting system allows publishers to:

- Define custom key-value pairs for granular ad targeting
- Create and manage audience segments based on user behavior
- Build complex targeting expressions combining multiple criteria
- Save reusable targeting configurations as presets

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Custom Targeting** | Key-value pairs that can be passed via ad tags for targeting |
| **Audience Segments** | Groups of users based on behavior, demographics, or custom rules |
| **Targeting Presets** | Saved targeting configurations that can be reused across line items |
| **Targeting Expression** | Logical combination of targeting criteria (AND/OR operators) |

---

## Targeting Types

Google Ad Manager supports multiple targeting types that can be combined to create precise ad delivery rules:

### Inventory Targeting (`InventoryTargeting`)
Targets specific ad units and placements where ads can serve.

| Field | Type | Description |
|-------|------|-------------|
| `targetedAdUnits` | `AdUnitTargeting[]` | List of ad units to include |
| `excludedAdUnits` | `AdUnitTargeting[]` | List of ad units to exclude |
| `targetedPlacementIds` | `long[]` | List of placement IDs to include |

### Geographic Targeting (`GeoTargeting`)
Targets users based on their geographic location.

| Target Type | Description |
|-------------|-------------|
| Countries | Target entire countries |
| Regions | States, provinces, prefectures |
| Metro Areas | DMA (Designated Market Areas) |
| Cities | Individual cities |
| Postal Codes | ZIP/postal code targeting |

### Technology Targeting (`TechnologyTargeting`)
Targets based on user device and browser characteristics.

| Sub-type | Description |
|----------|-------------|
| `BrowserTargeting` | Target specific browsers (Chrome, Firefox, Safari, etc.) |
| `DeviceCategoryTargeting` | Desktop, mobile, tablet, connected TV |
| `DeviceCapabilityTargeting` | Device features (MRAID support, phone calls, etc.) |
| `OperatingSystemTargeting` | Target specific OS versions |
| `BandwidthGroupTargeting` | Connection speed targeting |

### Day-Part Targeting (`DayPartTargeting`)
Controls delivery based on specific days and times.

| Field | Description |
|-------|-------------|
| `dayParts` | Array of DayPart objects defining time windows |
| `timeZone` | PUBLISHER (network time zone) or BROWSER (user's time zone) |

**DayPart Structure:**
```python
{
    'dayOfWeek': 'MONDAY',  # MONDAY through SUNDAY
    'startTime': {'hour': 9, 'minute': 'ZERO'},  # Inclusive start
    'endTime': {'hour': 17, 'minute': 'ZERO'}    # Exclusive end
}
```

### Custom Targeting (`CustomCriteriaSet`)
Targets based on custom key-value pairs passed in ad requests.

| Component | Description |
|-----------|-------------|
| `CustomCriteriaSet` | Container with logical operator (AND/OR) |
| `CustomCriteria` | Individual key-value targeting condition |

### User Domain Targeting (`UserDomainTargeting`)
Targets or excludes users from specific domains or subdomains.

### Content Targeting (`ContentTargeting`)
Targets video categories and individual videos (for video ad rules).

### Video Position Targeting (`VideoPositionTargeting`)
Targets based on video ad position (pre-roll, mid-roll, post-roll).

### Mobile Application Targeting (`MobileApplicationTargeting`)
Targets specific mobile applications.

### Audience Segment Targeting
Targets users belonging to specific audience segments.

---

## Services Reference

### CustomTargetingService

**WSDL:** `https://ads.google.com/apis/ads/publisher/v202511/CustomTargetingService?wsdl`

Manages `CustomTargetingKey` and `CustomTargetingValue` objects for custom targeting.

#### Methods

##### createCustomTargetingKeys

Creates new custom targeting keys.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `keys` | `CustomTargetingKey[]` | Yes | Array of keys to create |

**Required Fields:**
- `CustomTargetingKey.name`
- `CustomTargetingKey.type`

**Returns:** `CustomTargetingKey[]` - The created keys with populated IDs

---

##### createCustomTargetingValues

Creates new custom targeting values for existing keys.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `values` | `CustomTargetingValue[]` | Yes | Array of values to create |

**Required Fields:**
- `CustomTargetingValue.customTargetingKeyId`
- `CustomTargetingValue.name`

**Returns:** `CustomTargetingValue[]` - The created values with populated IDs

---

##### getCustomTargetingKeysByStatement

Retrieves custom targeting keys matching a filter.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filterStatement` | `Statement` | Yes | PQL filter statement |

**Filterable Fields:**

| Field | PQL Name |
|-------|----------|
| ID | `id` |
| Name | `name` |
| Display Name | `displayName` |
| Type | `type` |

**Returns:** `CustomTargetingKeyPage` - Paginated results

---

##### getCustomTargetingValuesByStatement

Retrieves custom targeting values matching a filter.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filterStatement` | `Statement` | Yes | PQL filter statement |

**Filterable Fields:**

| Field | PQL Name |
|-------|----------|
| ID | `id` |
| Key ID | `customTargetingKeyId` |
| Name | `name` |
| Display Name | `displayName` |
| Match Type | `matchType` |

**Important:** The WHERE clause **must** always contain `customTargetingKeyId` as one of its columns AND'ed with the rest of the query.

**Returns:** `CustomTargetingValuePage` - Paginated results

---

##### updateCustomTargetingKeys

Updates existing custom targeting keys.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `keys` | `CustomTargetingKey[]` | Yes | Array of keys to update |

**Returns:** `CustomTargetingKey[]` - The updated keys

---

##### updateCustomTargetingValues

Updates existing custom targeting values.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `values` | `CustomTargetingValue[]` | Yes | Array of values to update |

**Returns:** `CustomTargetingValue[]` - The updated values

---

##### performCustomTargetingKeyAction

Performs actions on custom targeting keys matching a filter.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customTargetingKeyAction` | `CustomTargetingKeyAction` | Yes | Action to perform |
| `filterStatement` | `Statement` | Yes | PQL filter statement |

**Available Actions:**
- `ActivateCustomTargetingKeys` - Activate inactive keys
- `DeleteCustomTargetingKeys` - Delete keys

**Returns:** `UpdateResult` - Number of rows affected

---

##### performCustomTargetingValueAction

Performs actions on custom targeting values matching a filter.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customTargetingValueAction` | `CustomTargetingValueAction` | Yes | Action to perform |
| `filterStatement` | `Statement` | Yes | PQL filter statement |

**Available Actions:**
- `ActivateCustomTargetingValues` - Activate inactive values
- `DeleteCustomTargetingValues` - Delete values

**Returns:** `UpdateResult` - Number of rows affected

---

### AudienceSegmentService

**WSDL:** `https://ads.google.com/apis/ads/publisher/v202511/AudienceSegmentService?wsdl`

Manages audience segments for targeting users based on behavior and characteristics.

#### Methods

##### createAudienceSegments

Creates new first-party audience segments.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `segments` | `FirstPartyAudienceSegment[]` | Yes | Array of segments to create |

**Returns:** `FirstPartyAudienceSegment[]` - The created segments with populated IDs

---

##### getAudienceSegmentsByStatement

Retrieves audience segments matching a filter.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filterStatement` | `Statement` | Yes | PQL filter statement |

**Filterable Fields:**

| Field | PQL Name |
|-------|----------|
| ID | `id` |
| Name | `name` |
| Status | `status` |
| Type | `type` |
| Size | `size` |
| Data Provider Name | `dataProviderName` |
| Segment Type | `segmentType` |
| Approval Status | `approvalStatus` |
| Cost | `cost` |
| Start Date/Time | `startDateTime` |
| End Date/Time | `endDateTime` |

**Returns:** `AudienceSegmentPage` - Paginated results

---

##### updateAudienceSegments

Updates existing first-party audience segments.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `segments` | `FirstPartyAudienceSegment[]` | Yes | Array of segments to update |

**Returns:** `FirstPartyAudienceSegment[]` - The updated segments

---

##### performAudienceSegmentAction

Performs actions on audience segments matching a filter.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | `AudienceSegmentAction` | Yes | Action to perform |
| `filterStatement` | `Statement` | Yes | PQL filter statement |

**Available Actions:**
- `ActivateAudienceSegments` - Activate segments for targeting
- `DeactivateAudienceSegments` - Deactivate segments
- `ApproveAudienceSegments` - Approve shared segments
- `RejectAudienceSegments` - Reject shared segments
- `PopulateAudienceSegments` - Populate segments with identifiers

**Returns:** `UpdateResult` - Number of rows affected

---

### SegmentPopulationService

**WSDL:** `https://ads.google.com/apis/ads/publisher/v202511/SegmentPopulationService?wsdl`

Provides methods for populating audience segments with user identifiers.

#### Methods

##### updateSegmentMemberships

Updates identifiers within an audience segment.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `updateRequest` | `SegmentPopulationRequest` | Yes | Request containing segment and identifier data |

**Returns:** `SegmentPopulationResponse` - Contains `batchUploadId` for grouping requests

**Important:** The returned `batchUploadId` can be used to group multiple requests. Batches expire if `ProcessAction` is not invoked within **5 days**.

---

##### getSegmentPopulationResultsByIds

Retrieves results for batch upload operations.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `batchUploadIds` | `long[]` | Yes | Array of batch upload IDs |

**Returns:** `SegmentPopulationResults[]` - Results for each batch upload

---

##### performSegmentPopulationAction

Executes actions on batch uploads.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | `SegmentPopulationAction` | Yes | Action to perform |
| `batchUploadIds` | `long[]` | Yes | Array of batch upload IDs |

**Available Actions:**
- `ProcessAction` - Process the batch upload

**Returns:** `UpdateResult` - Number of rows affected

---

### TargetingPresetService

**WSDL:** `https://ads.google.com/apis/ads/publisher/v202511/TargetingPresetService?wsdl`

Manages saved targeting configurations that can be reused across line items.

#### Methods

##### createTargetingPresets

Creates new targeting presets.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `targetingPresets` | `TargetingPreset[]` | Yes | Array of presets to create |

**Returns:** `TargetingPreset[]` - The created presets with populated IDs

---

##### getTargetingPresetsByStatement

Retrieves targeting presets matching a filter.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filterStatement` | `Statement` | Yes | PQL filter statement |

**Filterable Fields:**

| Field | PQL Name |
|-------|----------|
| ID | `id` |
| Name | `name` |

**Returns:** `TargetingPresetPage` - Paginated results

---

##### updateTargetingPresets

Updates existing targeting presets.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `targetingPresets` | `TargetingPreset[]` | Yes | Array of presets to update |

**Returns:** `TargetingPreset[]` - The updated presets

---

##### performTargetingPresetAction

Performs actions on targeting presets matching a filter.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `targetingPresetAction` | `TargetingPresetAction` | Yes | Action to perform |
| `filterStatement` | `Statement` | Yes | PQL filter statement |

**Available Actions:**
- `DeleteTargetingPresetAction` - Delete targeting presets

**Returns:** `UpdateResult` - Number of rows affected

---

## Data Models

### CustomTargetingKey

Represents a key used for custom targeting (e.g., "color", "section", "sport").

| Field | Type | Read-Only | Required | Description |
|-------|------|-----------|----------|-------------|
| `id` | `xsd:long` | Yes | No | Unique identifier. Populated by Google. |
| `name` | `xsd:string` | No | Yes | Key name. Max 10 characters. Allowed: alphanumeric and symbols except `" ' = ! + # * ~ ; ^ ( ) < > [ ]` and whitespace. |
| `displayName` | `xsd:string` | No | No | Descriptive display name for the key. |
| `type` | `CustomTargetingKey.Type` | No | Yes | Key type classification. |
| `status` | `CustomTargetingKey.Status` | Yes | No | Current status. Managed via `performCustomTargetingKeyAction`. |
| `reportableType` | `ReportableType` | No | No | Reporting availability in Ad Manager query tool. |

#### CustomTargetingKey.Type Enum

| Value | Description |
|-------|-------------|
| `PREDEFINED` | Target audiences by criteria values that are defined in advance. Only pre-created values can be used for targeting. |
| `FREEFORM` | Target audiences by adding criteria values when creating line items. Values can be created on-the-fly during trafficking. |

#### CustomTargetingKey.Status Enum

| Value | Description |
|-------|-------------|
| `ACTIVE` | The object is active and available for targeting. |
| `INACTIVE` | The object is no longer active. |
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |

#### ReportableType Enum

| Value | Description |
|-------|-------------|
| `ON` | Available for reporting in the Ad Manager query tool. |
| `OFF` | Not available for reporting in the Ad Manager query tool. |
| `CUSTOM_DIMENSION` | Custom dimension available for reporting in the Ad Manager query tool. |
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |

---

### CustomTargetingValue

Represents a value associated with a custom targeting key.

| Field | Type | Read-Only | Required | Description |
|-------|------|-----------|----------|-------------|
| `customTargetingKeyId` | `xsd:long` | No | Yes | ID of the parent CustomTargetingKey. |
| `id` | `xsd:long` | Yes | No | Unique identifier. Populated by Google. |
| `name` | `xsd:string` | No | Yes | Value name. Max 40 characters. Allowed: alphanumeric and most symbols except `" ' = ! + # * ~ ; ^ ( ) < > [ ]`. |
| `displayName` | `xsd:string` | No | No | Descriptive display name for the value. |
| `matchType` | `CustomTargetingValue.MatchType` | No | No | How the value is matched against ad requests. |
| `status` | `CustomTargetingValue.Status` | Yes | No | Current status. Managed via `performCustomTargetingValueAction`. |

#### CustomTargetingValue.MatchType Enum

| Value | Description | Restrictions |
|-------|-------------|--------------|
| `EXACT` | Exact string match. Example: `car=honda` matches only `car=honda`. | Default for PREDEFINED keys. |
| `BROAD` | Lenient matching when at least one word in the ad request matches the targeted value. | Cannot be used within audience segment rules. |
| `PREFIX` | Matches values starting with the specified string. Example: `car=hond` matches `car=honda`. | Ad Manager 360 only. |
| `BROAD_PREFIX` | Combination of BROAD and PREFIX matching. Matches words that start with the targeted value characters. | Cannot be used in audience segment rules. Ad Manager 360 only. |
| `SUFFIX` | Matches values ending with the specified string. | Cannot be used within line item targeting. Ad Manager 360 only. |
| `CONTAINS` | Matches values containing the specified string anywhere. | Cannot be used within line item targeting. Ad Manager 360 only. |
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. | - |

**Note:** `PREFIX`, `BROAD_PREFIX`, `SUFFIX`, and `CONTAINS` match types are only available for Ad Manager 360 networks.

#### CustomTargetingValue.Status Enum

| Value | Description |
|-------|-------------|
| `ACTIVE` | The object is active and available for targeting. |
| `INACTIVE` | The object is no longer active. |
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |

---

### CustomCriteria and CustomCriteriaSet

These types are used to build complex targeting expressions.

#### CustomCriteriaSet

A container for combining targeting criteria with logical operators.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `logicalOperator` | `CustomCriteriaSet.LogicalOperator` | Yes | The logical operator to apply to children. |
| `children` | `CustomCriteriaNode[]` | Yes | Child nodes (can be CustomCriteriaSet, CustomCriteria, AudienceSegmentCriteria, or CmsMetadataCriteria). |

**LogicalOperator Enum:**

| Value | Description |
|-------|-------------|
| `AND` | All children must match. |
| `OR` | Any child must match. |

#### CustomCriteria

A leaf node representing a key-value targeting condition.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `keyId` | `xsd:long` | Yes | The ID of the CustomTargetingKey. |
| `valueIds` | `xsd:long[]` | Yes | Array of CustomTargetingValue IDs to match. |
| `operator` | `CustomCriteria.ComparisonOperator` | Yes | The comparison operator. |

**ComparisonOperator Enum:**

| Value | Description |
|-------|-------------|
| `IS` | Key equals one of the specified values. |
| `IS_NOT` | Key does not equal any of the specified values. |

#### AudienceSegmentCriteria

A leaf node for targeting audience segments.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `operator` | `AudienceSegmentCriteria.ComparisonOperator` | Yes | The comparison operator (`IS` or `IS_NOT`). |
| `audienceSegmentIds` | `xsd:long[]` | Yes | Array of AudienceSegment IDs to target. |

#### CmsMetadataCriteria

A leaf node for targeting CMS metadata.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `operator` | `CmsMetadataCriteria.ComparisonOperator` | Yes | The comparison operator (`EQUALS` or `NOT_EQUALS`). |
| `cmsMetadataValueIds` | `xsd:long[]` | Yes | Array of CmsMetadataValue IDs to target. |

#### Inheritance Hierarchy

```
CustomCriteriaNode (abstract base)
  |
  +-- CustomCriteriaSet (composite node with logical operator)
  |
  +-- CustomCriteriaLeaf (abstract leaf base)
        |
        +-- CustomCriteria (key-value targeting)
        +-- AudienceSegmentCriteria (audience segment targeting)
        +-- CmsMetadataCriteria (CMS metadata targeting)
```

---

### AudienceSegment

Base type representing an audience segment.

| Field | Type | Read-Only | Required | Description |
|-------|------|-----------|----------|-------------|
| `id` | `xsd:long` | Yes | No | Unique identifier. Populated by Google. |
| `name` | `xsd:string` | No | Yes | Segment name. Max 255 characters. |
| `categoryIds` | `xsd:long[]` | No | No | IDs of categories this segment belongs to. Optional, may be empty. |
| `description` | `xsd:string` | No | No | Segment description. Max 8192 characters. |
| `status` | `AudienceSegment.Status` | Yes* | No | Targeting availability. Defaults to ACTIVE on creation. *Settable during creation, read-only during updates. |
| `size` | `xsd:long` | Yes | No | Number of unique identifiers in the segment. |
| `mobileWebSize` | `xsd:long` | Yes | No | Number of unique mobile web identifiers. |
| `idfaSize` | `xsd:long` | Yes | No | Number of unique IDFA identifiers. |
| `adIdSize` | `xsd:long` | Yes | No | Number of unique AdID identifiers. |
| `ppidSize` | `xsd:long` | Yes | No | Number of unique publisher-provided identifiers (PPID). |
| `dataProvider` | `AudienceSegmentDataProvider` | Yes | No | Owner data provider of this segment. |
| `type` | `AudienceSegment.Type` | Yes | No | Segment type classification. Assigned by Google. |

#### AudienceSegment.Status Enum

| Value | Description |
|-------|-------------|
| `ACTIVE` | Segment is available for targeting. |
| `INACTIVE` | Segment is not available for targeting. |
| `UNUSED` | Segment was deactivated by Google due to inactivity. |
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |

#### AudienceSegment.Type Enum

| Value | Description |
|-------|-------------|
| `FIRST_PARTY` | First-party segments created and owned by the publisher. |
| `SHARED` | First-party segments shared by other clients. |
| `THIRD_PARTY` | Third-party segments licensed from data providers. Does not include Google-provided licensed segments. |
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |

#### FirstPartyAudienceSegment

An audience segment owned by the publisher network. Inherits all fields from `AudienceSegment` with no additional fields.

**Subtypes:**

##### RuleBasedFirstPartyAudienceSegment

Segment populated based on rules. Includes additional fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `pageViews` | `xsd:int` | Yes | Number of times a user's cookie must match the segment rule. Range: 1-12. |
| `recencyDays` | `xsd:int` | No | Number of days within which a user's cookie must match the segment rule. Range: 1-90. |
| `membershipExpirationDays` | `xsd:int` | No | Number of days after which a user's cookie will be removed due to inactivity. Range: 1-540. |
| `rule` | `FirstPartyAudienceSegmentRule` | Yes | The rule that determines user eligibility criteria. |

##### NonRuleBasedFirstPartyAudienceSegment

Segment populated via batch upload. Includes additional fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `membershipExpirationDays` | `xsd:int` | Yes | Number of days after which a user's cookie will be removed due to inactivity. Range: 1-540. |

#### ThirdPartyAudienceSegment

Third-party data provider segment. Inherits all fields from `AudienceSegment` plus:

| Field | Type | Read-Only | Description |
|-------|------|-----------|-------------|
| `approvalStatus` | `AudienceSegmentApprovalStatus` | No | Publisher's approval status for the segment. |
| `cost` | `Money` | Yes | CPM cost for the segment. Assigned by the data provider. |
| `licenseType` | `LicenseType` | Yes | License classification (`DIRECT_LICENSE` or `GLOBAL_LICENSE`). |
| `startDateTime` | `DateTime` | Yes | Date and time when the segment becomes available. Assigned by the data provider. |
| `endDateTime` | `DateTime` | Yes | Date and time when the segment ceases to be available. Assigned by the data provider. |

#### AudienceSegmentApprovalStatus Enum

| Value | Description |
|-------|-------------|
| `UNAPPROVED` | Segment is waiting to be approved or rejected. Cannot be targeted. |
| `APPROVED` | Segment is approved and can be targeted. |
| `REJECTED` | Segment is rejected and cannot be targeted. |
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |

#### SharedAudienceSegment

A segment shared with the publisher from another client. Inherits all fields from `AudienceSegment` with no additional fields.

---

### SegmentPopulationRequest

Request object for populating audience segments with user identifiers.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `batchUploadId` | `xsd:long` | No | The ID of the batch that will process identifiers. If not specified, provided by Google. |
| `segmentId` | `xsd:long` | Yes | The ID of the segment to populate. Segment must be active. |
| `isDeletion` | `xsd:boolean` | No | Indicates whether identifiers should be added (`false`) or removed (`true`) from the segment. |
| `identifierType` | `IdentifierType` | Yes | The type of identifier being operated upon. |
| `ids` | `xsd:string[]` | Yes | The identifiers to upload. Max 100,000 elements per request. |
| `consentType` | `ConsentType` | No | Consent type gathered for all identifiers in this request. |

#### IdentifierType Enum

| Value | Description |
|-------|-------------|
| `PUBLISHER_PROVIDED_IDENTIFIER` | Publisher-provided identifier (PPID). |
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |

#### ConsentType Enum

| Value | Description |
|-------|-------------|
| `UNSET` | Consent type not set. |
| `GRANTED` | User consent has been granted. |
| `DENIED` | User consent has been denied. |
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |

### SegmentPopulationResults

Results for a batch upload operation.

| Field | Type | Description |
|-------|------|-------------|
| `batchUploadId` | `xsd:long` | The batch ID for looking up results. |
| `segmentId` | `xsd:long` | The segment ID associated with the population job. |
| `status` | `SegmentPopulationStatus` | The current status of the upload request. |
| `numSuccessfulIdsProcessed` | `xsd:long` | Number of IDs that were processed successfully. |
| `errors` | `IdError[]` | Identifiers with errors. |

#### SegmentPopulationStatus Enum

| Value | Description |
|-------|-------------|
| `PREPARING` | Batch is being prepared for processing. |
| `PROCESSING` | Batch is currently being processed. |
| `SUCCESS` | Batch was processed successfully. |
| `FAILED` | Batch processing failed. |
| `EXPIRED` | Batch expired before processing (5-day TTL). |
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |

---

### TargetingPreset

A saved targeting configuration that can be reused across line items.

| Field | Type | Read-Only | Required | Description |
|-------|------|-----------|----------|-------------|
| `id` | `xsd:long` | Yes | No | Unique identifier. Assigned by Google. |
| `name` | `xsd:string` | No | Yes | Preset name. Max 255 characters. |
| `targeting` | `Targeting` | No | Yes | The targeting criteria for this preset. |

---

### Targeting Object

The main `Targeting` type contains all targeting criteria for a `LineItem` or `TargetingPreset`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `geoTargeting` | `GeoTargeting` | No | Geographic location targeting. |
| `inventoryTargeting` | `InventoryTargeting` | **Yes** | Ad unit and placement targeting. Must target at least one ad unit or placement. |
| `dayPartTargeting` | `DayPartTargeting` | No | Day and time targeting. |
| `dateTimeRangeTargeting` | `DateTimeRangeTargeting` | No | Specific date range targeting. |
| `technologyTargeting` | `TechnologyTargeting` | No | Browser, device, OS targeting. |
| `customTargeting` | `CustomCriteriaSet` | No | Custom key-value targeting with up to three hierarchical levels. |
| `userDomainTargeting` | `UserDomainTargeting` | No | Domain targeting. |
| `contentTargeting` | `ContentTargeting` | No | Video content and bundle targeting. |
| `videoPositionTargeting` | `VideoPositionTargeting` | No | Video ad position targeting (pre-roll, mid-roll, post-roll). |
| `mobileApplicationTargeting` | `MobileApplicationTargeting` | No | Mobile app targeting. |
| `buyerUserListTargeting` | `BuyerUserListTargeting` | Read-only | Programmatic buyer user lists. Populated by Google. |
| `inventoryUrlTargeting` | `InventoryUrlTargeting` | No | URL targeting for yield groups. |
| `verticalTargeting` | `VerticalTargeting` | No | Vertical/category targeting (AD_CATEGORY table entries). |
| `contentLabelTargeting` | `ContentLabelTargeting` | No | Content label exclusions (CONTENT_LABEL table). |
| `requestPlatformTargeting` | `RequestPlatformTargeting` | No* | Request platform targeting. *Required for video line items. |
| `inventorySizeTargeting` | `InventorySizeTargeting` | No | Ad size targeting for yield groups. |
| `publisherProvidedSignalsTargeting` | `PublisherProvidedSignalsTargeting` | No | Publisher-provided signals targeting. |

---

## Targeting Sub-Types

### InventoryTargeting

Specifies what inventory is targeted by a line item.

| Field | Type | Description |
|-------|------|-------------|
| `targetedAdUnits` | `AdUnitTargeting[]` | List of ad units to include. |
| `excludedAdUnits` | `AdUnitTargeting[]` | List of ad units to exclude. |
| `targetedPlacementIds` | `xsd:long[]` | List of placement IDs to include. |

#### AdUnitTargeting

| Field | Type | Description |
|-------|------|-------------|
| `adUnitId` | `xsd:string` | Included or excluded ad unit ID. |
| `includeDescendants` | `xsd:boolean` | Whether all descendants are included/excluded. Default: `true`. |

---

### GeoTargeting

Specifies geographic locations to target or exclude.

| Field | Type | Description |
|-------|------|-------------|
| `targetedLocations` | `Location[]` | Geographic locations being targeted. |
| `excludedLocations` | `Location[]` | Geographic locations being excluded. |

**Constraints:**
- Cannot simultaneously target and exclude identical locations.
- Cannot target a child location when its parent is excluded.
- Cannot target a parent when also targeting its child.

#### Location

| Field | Type | Description |
|-------|------|-------------|
| `id` | `xsd:long` | Unique identifier for the location. |
| `type` | `xsd:string` | Location type (e.g., "COUNTRY", "CITY", "STATE", "COUNTY"). |
| `canonicalParentId` | `xsd:int` | The nearest location parent's ID. |
| `displayName` | `xsd:string` | Localized name of the geographical entity. |

---

### DayPartTargeting

Modifies delivery times for particular days of the week.

| Field | Type | Description |
|-------|------|-------------|
| `dayParts` | `DayPart[]` | Days and times for delivery. Ignored when targeting all days/times. |
| `timeZone` | `DeliveryTimeZone` | Time zone for delivery. Default: `BROWSER`. |

#### DeliveryTimeZone Enum

| Value | Description |
|-------|-------------|
| `PUBLISHER` | Use the publisher's time zone. |
| `BROWSER` | Use the browser's (user's) time zone. |

#### DayPart

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `dayOfWeek` | `DayOfWeek` | Yes | Day of the week the target applies to. |
| `startTime` | `TimeOfDay` | Yes | Start time (inclusive). |
| `endTime` | `TimeOfDay` | Yes | End time (exclusive). |

#### DayOfWeek Enum

`MONDAY`, `TUESDAY`, `WEDNESDAY`, `THURSDAY`, `FRIDAY`, `SATURDAY`, `SUNDAY`

#### TimeOfDay

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `hour` | `xsd:int` | Yes | Hour in 24-hour time (0-24 inclusive). |
| `minute` | `MinuteOfHour` | Yes | Minutes past the hour. |

#### MinuteOfHour Enum

| Value | Description |
|-------|-------------|
| `ZERO` | Zero minutes past the hour (:00). |
| `FIFTEEN` | Fifteen minutes past the hour (:15). |
| `THIRTY` | Thirty minutes past the hour (:30). |
| `FORTY_FIVE` | Forty-five minutes past the hour (:45). |

---

### TechnologyTargeting

Specifies browser, device, and operating system targeting.

| Field | Type | Description |
|-------|------|-------------|
| `bandwidthGroupTargeting` | `BandwidthGroupTargeting` | Connection speed targeting. |
| `browserTargeting` | `BrowserTargeting` | Browser targeting (Chrome, Firefox, Safari, etc.). |
| `browserLanguageTargeting` | `BrowserLanguageTargeting` | Browser language targeting. |
| `deviceCapabilityTargeting` | `DeviceCapabilityTargeting` | Device capability targeting (MRAID support, etc.). |
| `deviceCategoryTargeting` | `DeviceCategoryTargeting` | Device category targeting (desktop, mobile, tablet, CTV). |
| `deviceManufacturerTargeting` | `DeviceManufacturerTargeting` | Device manufacturer targeting (Apple, Samsung, etc.). |
| `mobileCarrierTargeting` | `MobileCarrierTargeting` | Mobile carrier targeting. |
| `mobileDeviceTargeting` | `MobileDeviceTargeting` | Mobile device targeting. |
| `mobileDeviceSubmodelTargeting` | `MobileDeviceSubmodelTargeting` | Mobile device submodel targeting. |
| `operatingSystemTargeting` | `OperatingSystemTargeting` | Operating system targeting. |
| `operatingSystemVersionTargeting` | `OperatingSystemVersionTargeting` | OS version targeting. |

---

### VideoPositionTargeting

Specifies video ad positions to target.

| Field | Type | Description |
|-------|------|-------------|
| `targetedPositions` | `VideoPositionTarget[]` | Video positions being targeted. |

#### VideoPositionTarget

| Field | Type | Description |
|-------|------|-------------|
| `videoPosition` | `VideoPosition` | The video position to target (required). |
| `videoBumperType` | `VideoBumperType` | Bumper position type (BEFORE or AFTER the ad pod). |
| `videoPositionWithinPod` | `VideoPositionWithinPod` | Position within an ad pod. |
| `adSpotId` | `xsd:long` | Custom ad spot ID. Must be null if targeting position, bumper, or pod position. |

#### VideoPosition

| Field | Type | Description |
|-------|------|-------------|
| `positionType` | `VideoPosition.Type` | Type of video position. |
| `midrollIndex` | `xsd:int` | Index of mid-roll to target. Only valid for MIDROLL position type. |

#### VideoPosition.Type Enum

| Value | Description |
|-------|-------------|
| `PREROLL` | Position before the video starts playing. |
| `MIDROLL` | Position within the middle of the playing video. |
| `POSTROLL` | Position after the video is completed. |
| `ALL` | Targets all video positions. |
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |

#### VideoBumperType Enum

| Value | Description |
|-------|-------------|
| `BEFORE` | Bumper position before the ad pod. |
| `AFTER` | Bumper position after the ad pod. |

---

### ContentTargeting

Specifies video content and content bundles to target.

| Field | Type | Description |
|-------|------|-------------|
| `targetedContentIds` | `xsd:long[]` | IDs of content being targeted. |
| `excludedContentIds` | `xsd:long[]` | IDs of content being excluded. |
| `targetedVideoContentBundleIds` | `xsd:long[]` | ContentBundle IDs being targeted. |
| `excludedVideoContentBundleIds` | `xsd:long[]` | ContentBundle IDs being excluded. |

---

### UserDomainTargeting

Specifies domains to target or exclude.

| Field | Type | Description |
|-------|------|-------------|
| `domains` | `xsd:string[]` | Domains or subdomains to target/exclude. Max 67 characters per domain. Required. |
| `targeted` | `xsd:boolean` | Whether domains should be targeted (`true`) or excluded (`false`). Default: `true`. |

---

### RequestPlatformTargeting

Specifies request platforms to target.

| Field | Type | Description |
|-------|------|-------------|
| `targetedRequestPlatforms` | `RequestPlatform[]` | Request platforms to target. Empty means all platforms. |

#### RequestPlatform Enum

| Value | Description |
|-------|-------------|
| `BROWSER` | Request from a web browser (desktop and mobile web). |
| `MOBILE_APP` | Request from a mobile application (including interstitial and rewarded video). |
| `VIDEO_PLAYER` | Request from a video player playing publisher content (web, mobile app, and CTV). |
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |

**Note:** Required for ProposalLineItems and video line items. Read-only for non-video line items.

---

### InventoryUrlTargeting

Specifies URLs to target or exclude (for yield groups).

| Field | Type | Description |
|-------|------|-------------|
| `targetedUrls` | `InventoryUrl[]` | URLs to include. |
| `excludedUrls` | `InventoryUrl[]` | URLs to exclude. |

---

### BuyerUserListTargeting

Indicates buyer user list targeting for programmatic line items.

| Field | Type | Description |
|-------|------|-------------|
| `hasBuyerUserListTargeting` | `xsd:boolean` | Whether the programmatic line item has buyer user list targeting. |

**Note:** This field is read-only and populated by Google.

---

## Custom Targeting

### Keys vs Values

Custom targeting uses a **key-value** structure:

- **Keys** define the targeting category (e.g., "color", "section", "interest")
- **Values** define specific options within that category (e.g., "red", "sports", "technology")

```
Key: "section"  -->  Values: "news", "sports", "entertainment"
Key: "color"    -->  Values: "red", "blue", "green"
```

### Key Types

| Type | Description | Use Case |
|------|-------------|----------|
| **PREDEFINED** | Only pre-created values can be used | Controlled vocabulary (e.g., content categories) |
| **FREEFORM** | Values can be created on-the-fly | Dynamic values (e.g., article IDs, user IDs) |

### Match Types

Match types determine how targeting values are compared:

| Match Type | Description | Example | Restrictions |
|------------|-------------|---------|--------------|
| `EXACT` | Exact string match | "sports" matches only "sports" | Default for PREDEFINED |
| `BROAD` | Fuzzy/similar match | "sport" might match "sports" | Not for audience segments |
| `PREFIX` | Starts with | "tech*" matches "technology", "technical" | Ad Manager 360 only |
| `BROAD_PREFIX` | Fuzzy starts with | "tech*" with fuzzy matching | Ad Manager 360 only; not for audience segments |
| `SUFFIX` | Ends with | "*ball" matches "football", "basketball" | Ad Manager 360 only; not for line items |
| `CONTAINS` | Contains substring | "*port*" matches "sports", "report" | Ad Manager 360 only; not for line items |

### Hierarchies

Custom targeting supports hierarchical key-value structures for organizing targeting criteria:

```
Category (Key)
  --> Subcategory (Value with hierarchy)
    --> Specific Item (Child value)
```

Example:
```
"geo" (Key)
  --> "us" (Value)
    --> "us_ca" (Child: California)
    --> "us_ny" (Child: New York)
  --> "uk" (Value)
    --> "uk_london" (Child: London)
```

---

## Targeting Expression Syntax

Custom targeting uses `CustomCriteriaSet` to build complex logical expressions.

### Structure

The targeting tree has **three levels**:

1. **Level 1 (Root):** Top-level `CustomCriteriaSet` with OR operator
2. **Level 2:** Child `CustomCriteriaSet` objects with AND operator
3. **Level 3:** Leaf `CustomCriteria` objects (actual key-value conditions)

```
CustomCriteriaSet (OR)
  |
  +-- CustomCriteriaSet (AND)
  |     |-- CustomCriteria (key1 IS value1)
  |     |-- CustomCriteria (key2 IS value2)
  |
  +-- CustomCriteriaSet (AND)
        |-- CustomCriteria (key3 IS value3)
```

**Expression:** `(key1=value1 AND key2=value2) OR (key3=value3)`

### CustomCriteriaSet

| Field | Type | Description |
|-------|------|-------------|
| `logicalOperator` | `CustomCriteriaSet.LogicalOperator` | AND or OR |
| `children` | `CustomCriteriaNode[]` | Child nodes (sets or criteria) |

### CustomCriteria

| Field | Type | Description |
|-------|------|-------------|
| `keyId` | `long` | CustomTargetingKey ID |
| `valueIds` | `long[]` | Array of CustomTargetingValue IDs |
| `operator` | `CustomCriteria.ComparisonOperator` | IS or IS_NOT |

### Operators

**Logical Operators (CustomCriteriaSet):**
- `AND` - All children must match
- `OR` - Any child must match

**Comparison Operators (CustomCriteria):**
- `IS` - Key equals one of the values
- `IS_NOT` - Key does not equal any of the values

---

## Actions Reference

### CustomTargetingKeyAction

| Action | Description |
|--------|-------------|
| `ActivateCustomTargetingKeys` | Activates inactive custom targeting keys |
| `DeleteCustomTargetingKeys` | Deletes custom targeting keys (and their values) |

### CustomTargetingValueAction

| Action | Description |
|--------|-------------|
| `ActivateCustomTargetingValues` | Activates inactive custom targeting values |
| `DeleteCustomTargetingValues` | Deletes custom targeting values |

### AudienceSegmentAction

| Action | Description |
|--------|-------------|
| `ActivateAudienceSegments` | Activates segments for targeting |
| `DeactivateAudienceSegments` | Deactivates segments |
| `ApproveAudienceSegments` | Approves shared segments |
| `RejectAudienceSegments` | Rejects shared segments |
| `PopulateAudienceSegments` | Triggers segment population |

### SegmentPopulationAction

| Action | Description |
|--------|-------------|
| `ProcessAction` | Processes the batch upload |

### TargetingPresetAction

| Action | Description |
|--------|-------------|
| `DeleteTargetingPresetAction` | Deletes targeting presets |

---

## Python Code Examples

### Setup

```python
from googleads import ad_manager

# Load client from configuration file (googleads.yaml)
client = ad_manager.AdManagerClient.LoadFromStorage()

# API Version
API_VERSION = 'v202511'
```

### Creating Custom Targeting Keys and Values

```python
def create_custom_targeting_key(client, name, display_name, key_type='PREDEFINED'):
    """
    Create a custom targeting key.

    Args:
        client: AdManagerClient instance
        name: Key name (max 10 chars, alphanumeric)
        display_name: Human-readable display name
        key_type: 'PREDEFINED' or 'FREEFORM'

    Returns:
        Created CustomTargetingKey object
    """
    custom_targeting_service = client.GetService(
        'CustomTargetingService', version=API_VERSION
    )

    key = {
        'name': name,
        'displayName': display_name,
        'type': key_type
    }

    result = custom_targeting_service.createCustomTargetingKeys([key])
    created_key = result[0]

    print(f"Created key: {created_key['name']} (ID: {created_key['id']})")
    return created_key


def create_custom_targeting_values(client, key_id, values):
    """
    Create custom targeting values for a key.

    Args:
        client: AdManagerClient instance
        key_id: ID of the parent CustomTargetingKey
        values: List of dicts with 'name' and optional 'displayName', 'matchType'

    Returns:
        List of created CustomTargetingValue objects
    """
    custom_targeting_service = client.GetService(
        'CustomTargetingService', version=API_VERSION
    )

    values_to_create = []
    for value in values:
        value_obj = {
            'customTargetingKeyId': key_id,
            'name': value['name'],
            'displayName': value.get('displayName', value['name']),
            'matchType': value.get('matchType', 'EXACT')
        }
        values_to_create.append(value_obj)

    result = custom_targeting_service.createCustomTargetingValues(values_to_create)

    for created_value in result:
        print(f"Created value: {created_value['name']} (ID: {created_value['id']})")

    return result


# Example usage
if __name__ == '__main__':
    client = ad_manager.AdManagerClient.LoadFromStorage()

    # Create a "section" key
    section_key = create_custom_targeting_key(
        client,
        name='section',
        display_name='Content Section',
        key_type='PREDEFINED'
    )

    # Create values for the section key
    section_values = create_custom_targeting_values(
        client,
        key_id=section_key['id'],
        values=[
            {'name': 'news', 'displayName': 'News Section'},
            {'name': 'sports', 'displayName': 'Sports Section'},
            {'name': 'tech', 'displayName': 'Technology Section'}
        ]
    )
```

### Querying Custom Targeting Data

```python
def get_all_custom_targeting_keys(client):
    """
    Retrieve all custom targeting keys.

    Returns:
        List of CustomTargetingKey objects
    """
    custom_targeting_service = client.GetService(
        'CustomTargetingService', version=API_VERSION
    )

    statement = ad_manager.StatementBuilder(version=API_VERSION)
    all_keys = []

    while True:
        response = custom_targeting_service.getCustomTargetingKeysByStatement(
            statement.ToStatement()
        )

        if 'results' in response and len(response['results']) > 0:
            all_keys.extend(response['results'])
            statement.offset += statement.limit
        else:
            break

    return all_keys


def get_values_for_key(client, key_id):
    """
    Retrieve all values for a specific custom targeting key.

    Args:
        key_id: ID of the CustomTargetingKey

    Returns:
        List of CustomTargetingValue objects
    """
    custom_targeting_service = client.GetService(
        'CustomTargetingService', version=API_VERSION
    )

    # Note: customTargetingKeyId must be in the WHERE clause
    statement = (ad_manager.StatementBuilder(version=API_VERSION)
                 .Where('customTargetingKeyId = :keyId')
                 .WithBindVariable('keyId', key_id))

    all_values = []

    while True:
        response = custom_targeting_service.getCustomTargetingValuesByStatement(
            statement.ToStatement()
        )

        if 'results' in response and len(response['results']) > 0:
            all_values.extend(response['results'])
            statement.offset += statement.limit
        else:
            break

    return all_values


# Example usage
if __name__ == '__main__':
    client = ad_manager.AdManagerClient.LoadFromStorage()

    keys = get_all_custom_targeting_keys(client)
    print(f"Found {len(keys)} custom targeting keys:")

    for key in keys:
        print(f"\n{key['displayName']} ({key['name']}) - Type: {key['type']}")
        values = get_values_for_key(client, key['id'])
        for value in values:
            print(f"  - {value['displayName']} ({value['name']})")
```

### Building Complex Targeting Expressions

```python
def build_custom_targeting(key_values):
    """
    Build a CustomCriteriaSet for targeting.

    Args:
        key_values: List of tuples (key_id, [value_ids], operator)
            operator: 'IS' or 'IS_NOT'

    Returns:
        CustomCriteriaSet object

    Example:
        # Target (color=red OR color=blue) AND section=sports
        build_custom_targeting([
            (color_key_id, [red_value_id, blue_value_id], 'IS'),
            (section_key_id, [sports_value_id], 'IS')
        ])
    """
    criteria = []

    for key_id, value_ids, operator in key_values:
        criterion = {
            'xsi_type': 'CustomCriteria',
            'keyId': key_id,
            'valueIds': value_ids,
            'operator': operator
        }
        criteria.append(criterion)

    # If multiple criteria, wrap in AND set
    if len(criteria) > 1:
        and_set = {
            'xsi_type': 'CustomCriteriaSet',
            'logicalOperator': 'AND',
            'children': criteria
        }

        # Top level OR set
        return {
            'xsi_type': 'CustomCriteriaSet',
            'logicalOperator': 'OR',
            'children': [and_set]
        }
    else:
        return {
            'xsi_type': 'CustomCriteriaSet',
            'logicalOperator': 'OR',
            'children': criteria
        }


def build_or_targeting(expressions):
    """
    Build a targeting expression with OR at the top level.

    Args:
        expressions: List of lists, each inner list contains
            (key_id, [value_ids], operator) tuples that will be AND'ed together.
            The outer lists are OR'ed.

    Returns:
        CustomCriteriaSet object

    Example:
        # (section=sports AND color=red) OR (section=news AND premium=true)
        build_or_targeting([
            [(section_key_id, [sports_id], 'IS'), (color_key_id, [red_id], 'IS')],
            [(section_key_id, [news_id], 'IS'), (premium_key_id, [true_id], 'IS')]
        ])
    """
    and_sets = []

    for expression in expressions:
        criteria = []
        for key_id, value_ids, operator in expression:
            criterion = {
                'xsi_type': 'CustomCriteria',
                'keyId': key_id,
                'valueIds': value_ids,
                'operator': operator
            }
            criteria.append(criterion)

        and_set = {
            'xsi_type': 'CustomCriteriaSet',
            'logicalOperator': 'AND',
            'children': criteria
        }
        and_sets.append(and_set)

    return {
        'xsi_type': 'CustomCriteriaSet',
        'logicalOperator': 'OR',
        'children': and_sets
    }


# Example: Creating a line item with custom targeting
def create_line_item_with_targeting(client, order_id, ad_unit_ids, custom_targeting):
    """
    Create a line item with custom targeting.

    Args:
        client: AdManagerClient instance
        order_id: ID of the parent order
        ad_unit_ids: List of ad unit IDs to target
        custom_targeting: CustomCriteriaSet object
    """
    line_item_service = client.GetService('LineItemService', version=API_VERSION)

    # Build inventory targeting
    inventory_targeting = {
        'targetedAdUnits': [{'adUnitId': id} for id in ad_unit_ids]
    }

    # Build complete targeting
    targeting = {
        'inventoryTargeting': inventory_targeting,
        'customTargeting': custom_targeting
    }

    line_item = {
        'name': 'Line Item with Custom Targeting',
        'orderId': order_id,
        'targeting': targeting,
        'lineItemType': 'STANDARD',
        'costType': 'CPM',
        'costPerUnit': {'currencyCode': 'USD', 'microAmount': 2000000},  # $2.00 CPM
        'primaryGoal': {
            'goalType': 'LIFETIME',
            'unitType': 'IMPRESSIONS',
            'units': 100000
        },
        'startDateTimeType': 'IMMEDIATELY',
        'unlimitedEndDateTime': True,
        'creativeRotationType': 'EVEN'
    }

    result = line_item_service.createLineItems([line_item])
    return result[0]
```

### Creating Audience Segments

```python
def create_audience_segment(client, name, description=None):
    """
    Create a first-party audience segment.

    Args:
        client: AdManagerClient instance
        name: Segment name (max 255 chars)
        description: Optional description (max 8192 chars)

    Returns:
        Created FirstPartyAudienceSegment object
    """
    audience_segment_service = client.GetService(
        'AudienceSegmentService', version=API_VERSION
    )

    segment = {
        'name': name,
        'description': description or f'Audience segment: {name}',
        'status': 'ACTIVE',
        # NonRuleBasedFirstPartyAudienceSegment for manual population
        'xsi_type': 'NonRuleBasedFirstPartyAudienceSegment',
        'membershipExpirationDays': 30  # Required for NonRuleBased
    }

    result = audience_segment_service.createAudienceSegments([segment])
    created_segment = result[0]

    print(f"Created segment: {created_segment['name']} (ID: {created_segment['id']})")
    return created_segment


def create_rule_based_segment(client, name, rule, page_views=1, recency_days=30, expiration_days=90):
    """
    Create a rule-based first-party audience segment.

    Args:
        client: AdManagerClient instance
        name: Segment name (max 255 chars)
        rule: FirstPartyAudienceSegmentRule object
        page_views: Number of times rule must match (1-12)
        recency_days: Days within which rule must match (1-90)
        expiration_days: Days until membership expires (1-540)

    Returns:
        Created RuleBasedFirstPartyAudienceSegment object
    """
    audience_segment_service = client.GetService(
        'AudienceSegmentService', version=API_VERSION
    )

    segment = {
        'name': name,
        'status': 'ACTIVE',
        'xsi_type': 'RuleBasedFirstPartyAudienceSegment',
        'pageViews': page_views,
        'recencyDays': recency_days,
        'membershipExpirationDays': expiration_days,
        'rule': rule
    }

    result = audience_segment_service.createAudienceSegments([segment])
    return result[0]


def get_audience_segments(client, status=None):
    """
    Retrieve audience segments.

    Args:
        client: AdManagerClient instance
        status: Optional filter by status ('ACTIVE', 'INACTIVE', 'UNUSED')

    Returns:
        List of AudienceSegment objects
    """
    audience_segment_service = client.GetService(
        'AudienceSegmentService', version=API_VERSION
    )

    statement = ad_manager.StatementBuilder(version=API_VERSION)

    if status:
        statement = statement.Where('status = :status').WithBindVariable('status', status)

    all_segments = []

    while True:
        response = audience_segment_service.getAudienceSegmentsByStatement(
            statement.ToStatement()
        )

        if 'results' in response and len(response['results']) > 0:
            all_segments.extend(response['results'])
            statement.offset += statement.limit
        else:
            break

    return all_segments


def activate_audience_segments(client, segment_ids):
    """
    Activate audience segments.

    Args:
        client: AdManagerClient instance
        segment_ids: List of segment IDs to activate

    Returns:
        UpdateResult with number of affected rows
    """
    audience_segment_service = client.GetService(
        'AudienceSegmentService', version=API_VERSION
    )

    statement = (ad_manager.StatementBuilder(version=API_VERSION)
                 .Where('id IN (:ids)')
                 .WithBindVariable('ids', segment_ids))

    action = {'xsi_type': 'ActivateAudienceSegments'}

    result = audience_segment_service.performAudienceSegmentAction(
        action, statement.ToStatement()
    )

    print(f"Activated {result['numChanges']} segments")
    return result


# Example usage
if __name__ == '__main__':
    client = ad_manager.AdManagerClient.LoadFromStorage()

    # Create a segment
    segment = create_audience_segment(
        client,
        name='High-Value Users',
        description='Users who have made purchases in the last 30 days'
    )

    # List all active segments
    active_segments = get_audience_segments(client, status='ACTIVE')
    print(f"\nActive segments: {len(active_segments)}")
    for seg in active_segments:
        print(f"  - {seg['name']} (Size: {seg.get('size', 0)})")
```

### Populating Audience Segments

```python
def populate_segment_with_identifiers(client, segment_id, identifiers, is_deletion=False):
    """
    Populate an audience segment with user identifiers.

    Args:
        client: AdManagerClient instance
        segment_id: ID of the audience segment
        identifiers: List of identifier strings (max 100,000)
        is_deletion: True to remove identifiers, False to add

    Returns:
        Batch upload ID for tracking
    """
    segment_population_service = client.GetService(
        'SegmentPopulationService', version=API_VERSION
    )

    # Create the population request
    request = {
        'segmentId': segment_id,
        'identifierType': 'PUBLISHER_PROVIDED_IDENTIFIER',
        'ids': identifiers,
        'isDeletion': is_deletion,
        'consentType': 'GRANTED'
    }

    response = segment_population_service.updateSegmentMemberships(request)
    batch_upload_id = response['batchUploadId']

    print(f"Created batch upload: {batch_upload_id}")
    print(f"Identifiers submitted: {len(identifiers)}")

    return batch_upload_id


def process_segment_population(client, batch_upload_ids):
    """
    Process batch uploads to finalize segment population.

    Note: Must be called within 5 days of creating the batch.

    Args:
        client: AdManagerClient instance
        batch_upload_ids: List of batch upload IDs

    Returns:
        UpdateResult
    """
    segment_population_service = client.GetService(
        'SegmentPopulationService', version=API_VERSION
    )

    action = {'xsi_type': 'ProcessAction'}

    result = segment_population_service.performSegmentPopulationAction(
        action, batch_upload_ids
    )

    print(f"Processed {result['numChanges']} batch uploads")
    return result


def get_population_results(client, batch_upload_ids):
    """
    Get results for batch upload operations.

    Args:
        client: AdManagerClient instance
        batch_upload_ids: List of batch upload IDs

    Returns:
        List of SegmentPopulationResults
    """
    segment_population_service = client.GetService(
        'SegmentPopulationService', version=API_VERSION
    )

    results = segment_population_service.getSegmentPopulationResultsByIds(
        batch_upload_ids
    )

    for result in results:
        print(f"Batch {result['batchUploadId']}:")
        print(f"  Status: {result.get('status', 'UNKNOWN')}")
        print(f"  Processed: {result.get('numSuccessfulIdsProcessed', 0)}")

    return results


# Example: Full workflow
if __name__ == '__main__':
    client = ad_manager.AdManagerClient.LoadFromStorage()

    # Step 1: Create segment
    segment = create_audience_segment(client, 'Newsletter Subscribers')

    # Step 2: Add identifiers (PPIDs in this example)
    identifiers = [
        'user_12345',
        'user_67890',
        'user_11111',
        # ... more identifiers
    ]

    batch_id = populate_segment_with_identifiers(
        client,
        segment_id=segment['id'],
        identifiers=identifiers
    )

    # Step 3: Process the batch
    process_segment_population(client, [batch_id])

    # Step 4: Check results
    get_population_results(client, [batch_id])
```

### Applying Targeting to Line Items

```python
def apply_targeting_to_line_item(client, line_item_id, targeting_config):
    """
    Apply comprehensive targeting to an existing line item.

    Args:
        client: AdManagerClient instance
        line_item_id: ID of the line item to update
        targeting_config: Dict containing targeting configuration

    Returns:
        Updated line item
    """
    line_item_service = client.GetService('LineItemService', version=API_VERSION)

    # Get existing line item
    statement = (ad_manager.StatementBuilder(version=API_VERSION)
                 .Where('id = :id')
                 .WithBindVariable('id', line_item_id))

    response = line_item_service.getLineItemsByStatement(statement.ToStatement())

    if 'results' not in response or len(response['results']) == 0:
        raise ValueError(f"Line item {line_item_id} not found")

    line_item = response['results'][0]

    # Update targeting
    line_item['targeting'] = targeting_config

    result = line_item_service.updateLineItems([line_item])
    return result[0]


def build_comprehensive_targeting(
    ad_unit_ids,
    geo_targets=None,
    custom_targeting=None,
    day_parts=None,
    browsers=None,
    device_categories=None,
    request_platforms=None
):
    """
    Build a comprehensive targeting object.

    Args:
        ad_unit_ids: List of ad unit IDs (required)
        geo_targets: List of geo target IDs (countries, regions, cities)
        custom_targeting: CustomCriteriaSet object
        day_parts: List of DayPart objects
        browsers: List of browser technology IDs
        device_categories: List of device category IDs
        request_platforms: List of request platforms ('BROWSER', 'MOBILE_APP', 'VIDEO_PLAYER')

    Returns:
        Complete Targeting object
    """
    targeting = {
        'inventoryTargeting': {
            'targetedAdUnits': [{'adUnitId': id, 'includeDescendants': True} for id in ad_unit_ids]
        }
    }

    # Geographic targeting
    if geo_targets:
        targeting['geoTargeting'] = {
            'targetedLocations': [{'id': id} for id in geo_targets]
        }

    # Custom targeting
    if custom_targeting:
        targeting['customTargeting'] = custom_targeting

    # Day-part targeting
    if day_parts:
        targeting['dayPartTargeting'] = {
            'dayParts': day_parts,
            'timeZone': 'PUBLISHER'  # or 'BROWSER'
        }

    # Technology targeting
    if browsers or device_categories:
        tech_targeting = {}

        if browsers:
            tech_targeting['browserTargeting'] = {
                'isTargeted': True,
                'browsers': [{'id': id} for id in browsers]
            }

        if device_categories:
            tech_targeting['deviceCategoryTargeting'] = {
                'targetedDeviceCategories': [{'id': id} for id in device_categories]
            }

        targeting['technologyTargeting'] = tech_targeting

    # Request platform targeting
    if request_platforms:
        targeting['requestPlatformTargeting'] = {
            'targetedRequestPlatforms': request_platforms
        }

    return targeting


# Example: Complete targeting setup
if __name__ == '__main__':
    client = ad_manager.AdManagerClient.LoadFromStorage()

    # Build custom targeting
    # Assuming we have these IDs from previous operations
    SECTION_KEY_ID = 12345
    SPORTS_VALUE_ID = 67890
    NEWS_VALUE_ID = 67891

    custom_targeting = build_or_targeting([
        [(SECTION_KEY_ID, [SPORTS_VALUE_ID], 'IS')],
        [(SECTION_KEY_ID, [NEWS_VALUE_ID], 'IS')]
    ])

    # Day-part targeting: Weekdays 9 AM - 5 PM
    day_parts = []
    for day in ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']:
        day_parts.append({
            'dayOfWeek': day,
            'startTime': {'hour': 9, 'minute': 'ZERO'},
            'endTime': {'hour': 17, 'minute': 'ZERO'}
        })

    # Build comprehensive targeting
    targeting = build_comprehensive_targeting(
        ad_unit_ids=['111111', '222222'],  # Your ad unit IDs
        geo_targets=[2840],  # 2840 = United States
        custom_targeting=custom_targeting,
        day_parts=day_parts,
        device_categories=[30001, 30002],  # Desktop, Mobile
        request_platforms=['BROWSER', 'MOBILE_APP']
    )

    # Apply to line item
    LINE_ITEM_ID = 99999999
    updated_line_item = apply_targeting_to_line_item(
        client, LINE_ITEM_ID, targeting
    )

    print(f"Updated line item: {updated_line_item['name']}")
```

### Working with Targeting Presets

```python
def create_targeting_preset(client, name, targeting):
    """
    Create a targeting preset for reuse.

    Args:
        client: AdManagerClient instance
        name: Preset name (max 255 chars)
        targeting: Targeting object

    Returns:
        Created TargetingPreset object
    """
    targeting_preset_service = client.GetService(
        'TargetingPresetService', version=API_VERSION
    )

    preset = {
        'name': name,
        'targeting': targeting
    }

    result = targeting_preset_service.createTargetingPresets([preset])
    created_preset = result[0]

    print(f"Created preset: {created_preset['name']} (ID: {created_preset['id']})")
    return created_preset


def get_targeting_presets(client, name_filter=None):
    """
    Retrieve targeting presets.

    Args:
        client: AdManagerClient instance
        name_filter: Optional name pattern filter

    Returns:
        List of TargetingPreset objects
    """
    targeting_preset_service = client.GetService(
        'TargetingPresetService', version=API_VERSION
    )

    statement = ad_manager.StatementBuilder(version=API_VERSION)

    if name_filter:
        statement = (statement
                     .Where("name LIKE :name")
                     .WithBindVariable('name', f'%{name_filter}%'))

    all_presets = []

    while True:
        response = targeting_preset_service.getTargetingPresetsByStatement(
            statement.ToStatement()
        )

        if 'results' in response and len(response['results']) > 0:
            all_presets.extend(response['results'])
            statement.offset += statement.limit
        else:
            break

    return all_presets


def delete_targeting_presets(client, preset_ids):
    """
    Delete targeting presets.

    Args:
        client: AdManagerClient instance
        preset_ids: List of preset IDs to delete

    Returns:
        UpdateResult with number of deleted presets
    """
    targeting_preset_service = client.GetService(
        'TargetingPresetService', version=API_VERSION
    )

    statement = (ad_manager.StatementBuilder(version=API_VERSION)
                 .Where('id IN (:ids)')
                 .WithBindVariable('ids', preset_ids))

    action = {'xsi_type': 'DeleteTargetingPresetAction'}

    result = targeting_preset_service.performTargetingPresetAction(
        action, statement.ToStatement()
    )

    print(f"Deleted {result['numChanges']} presets")
    return result


# Example usage
if __name__ == '__main__':
    client = ad_manager.AdManagerClient.LoadFromStorage()

    # Create a reusable targeting preset
    targeting = build_comprehensive_targeting(
        ad_unit_ids=['111111'],
        geo_targets=[2840],  # United States
        device_categories=[30001]  # Desktop
    )

    preset = create_targeting_preset(
        client,
        name='US Desktop Users',
        targeting=targeting
    )

    # List all presets
    presets = get_targeting_presets(client)
    print(f"\nFound {len(presets)} targeting presets:")
    for p in presets:
        print(f"  - {p['name']} (ID: {p['id']})")
```

---

## Error Handling

### Common Errors

| Error Type | Description | Resolution |
|------------|-------------|------------|
| `CustomTargetingError` | Custom targeting validation failed | Check key/value names, types, and limits |
| `EntityLimitReachedError` | Maximum entities reached | Delete unused keys/values/segments |
| `EntityChildrenLimitReachedError` | Too many child entities | Reduce values per key |
| `CollectionSizeError` | Array too large for single request | Batch requests into smaller chunks |
| `QuotaError` | API quota exceeded | Implement exponential backoff |
| `SegmentPopulationError` | Segment population failed | Check identifier format and consent |

### SegmentPopulationError Reasons

| Reason | Description |
|--------|-------------|
| `TOO_MANY_IDENTIFIERS` | Batch contains too many identifiers (max 100,000) |
| `INVALID_SEGMENT` | Segment ID is invalid or not accessible |
| `JOB_ALREADY_STARTED` | Batch processing already in progress |
| `NO_IDENTIFIERS` | No identifiers provided |
| `NO_CONSENT` | Consent requirements not met |

### Error Handling Example

```python
from googleads import errors as googleads_errors

def safe_create_targeting_key(client, name, display_name, key_type):
    """
    Create a custom targeting key with error handling.
    """
    try:
        return create_custom_targeting_key(client, name, display_name, key_type)

    except googleads_errors.GoogleAdsServerFault as e:
        for error in e.errors:
            error_type = error['errorType']

            if error_type == 'CustomTargetingError':
                reason = error['reason']
                if reason == 'KEY_NAME_INVALID':
                    print(f"Invalid key name: {name}")
                elif reason == 'KEY_NAME_ALREADY_EXISTS':
                    print(f"Key already exists: {name}")
                    # Optionally retrieve existing key
                else:
                    print(f"Custom targeting error: {reason}")

            elif error_type == 'EntityLimitReachedError':
                print("Maximum custom targeting keys reached")

            elif error_type == 'QuotaError':
                print("API quota exceeded, retrying with backoff...")
                # Implement exponential backoff

            else:
                print(f"Unexpected error: {error_type}")

        raise
```

---

## Best Practices

### Custom Targeting

1. **Use descriptive names**: Choose clear, meaningful names for keys and values
2. **Prefer PREDEFINED keys**: Use predefined keys when possible for better control
3. **Limit key-value count**: Stay within entity limits to avoid quota issues
4. **Clean up unused targeting**: Regularly audit and delete unused keys/values
5. **Use appropriate match types**: EXACT for precise matching, broader types only when needed

### Audience Segments

1. **Start small**: Test segments with small populations before scaling
2. **Monitor segment size**: Track segment growth and performance
3. **Use meaningful names**: Include purpose and criteria in segment names
4. **Process batches promptly**: Complete batch processing within 5 days
5. **Set appropriate expiration**: Balance between membership retention and segment freshness

### Targeting Expressions

1. **Keep expressions simple**: Complex expressions are harder to debug
2. **Document targeting logic**: Maintain documentation of targeting rules
3. **Test before deploying**: Verify targeting with forecasting tools
4. **Use presets for reuse**: Save common targeting configurations as presets
5. **Follow the three-level structure**: Root OR, child AND, leaf criteria

### API Usage

1. **Implement pagination**: Always paginate large result sets
2. **Handle rate limits**: Use exponential backoff for quota errors
3. **Cache metadata**: Cache dimension/metric lists that change infrequently
4. **Batch operations**: Group multiple operations into batches when possible
5. **Include required WHERE clauses**: Always include `customTargetingKeyId` when querying values

---

## Resources

### Official Documentation

- [CustomTargetingService Reference](https://developers.google.com/ad-manager/api/reference/v202511/CustomTargetingService)
- [AudienceSegmentService Reference](https://developers.google.com/ad-manager/api/reference/v202511/AudienceSegmentService)
- [SegmentPopulationService Reference](https://developers.google.com/ad-manager/api/reference/v202511/SegmentPopulationService)
- [TargetingPresetService Reference](https://developers.google.com/ad-manager/api/reference/v202511/TargetingPresetService)
- [Targeting Types Help](https://support.google.com/admanager/answer/2884033)
- [Custom Targeting Help](https://support.google.com/admanager/answer/188092)

### Related Documentation

- [LineItemService Targeting](https://developers.google.com/ad-manager/api/reference/v202511/LineItemService.Targeting)
- [Geo Targets Reference](https://developers.google.com/ad-manager/api/geotargets)
- [SOAP API Getting Started](https://developers.google.com/ad-manager/api/start)

---

*This documentation is part of the gam-api project. For more information, see the [main documentation](/docs/README.md).*
