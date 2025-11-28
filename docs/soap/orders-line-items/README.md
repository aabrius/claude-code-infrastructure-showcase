# Google Ad Manager SOAP API v202511 - Orders & Line Items

> **API Version:** v202511
> **Last Updated:** 2025-11-28
> **Category:** Campaign Trafficking

This documentation covers the services for managing advertising campaigns in Google Ad Manager, including orders, line items, creative associations, and templates.

---

## Table of Contents

1. [Overview](#overview)
2. [Service Relationships](#service-relationships)
3. [OrderService](#orderservice)
4. [LineItemService](#lineitemservice)
5. [LineItemCreativeAssociationService](#lineitemcreativeassociationservice)
6. [LineItemTemplateService](#lineitemtemplateservice)
7. [Data Models](#data-models)
8. [Actions Reference](#actions-reference)
9. [PQL Filtering](#pql-filtering)
10. [Python Code Examples](#python-code-examples)
11. [Common Patterns & Best Practices](#common-patterns--best-practices)
12. [Error Handling](#error-handling)

---

## Overview

The Orders & Line Items category provides services for trafficking advertising campaigns in Google Ad Manager. These services form the core of campaign management:

### Use Cases

- **Campaign Setup**: Create orders for advertisers with associated line items
- **Creative Management**: Associate creatives with line items for ad serving
- **Campaign Optimization**: Update delivery settings, targeting, and pacing
- **Bulk Operations**: Perform actions (approve, pause, archive) on multiple items
- **Reporting Integration**: Track delivery statistics and performance metrics
- **Template Management**: Standardize line item configurations across campaigns

### Workflow Overview

```
Advertiser Campaign Setup Flow:

    [Order]
       |
       +---> [LineItem 1] --+---> [Creative A] (LICA)
       |          |        |
       |          |        +---> [Creative B] (LICA)
       |          |
       |          +---> Targeting (Geo, Inventory, Custom)
       |
       +---> [LineItem 2] --+---> [Creative C] (LICA)
                           |
                           +---> [Creative Set] (LICA)
```

---

## Service Relationships

Understanding how the four services relate to each other is essential for effective campaign management:

```
+-------------------+     contains      +------------------+
|   OrderService    | ----------------> |  LineItemService |
|   (Orders)        |    1:N           |  (LineItems)     |
+-------------------+                   +------------------+
                                               |
                                               | 1:N
                                               v
                              +--------------------------------+
                              | LineItemCreativeAssociation    |
                              | Service (LICAs)                |
                              +--------------------------------+
                                               |
                                               | references
                                               v
                              +--------------------------------+
                              | CreativeService                |
                              | (Creatives - separate service) |
                              +--------------------------------+

+------------------------+
| LineItemTemplateService|  (Templates for creating LineItems)
+------------------------+
```

### Key Relationships

| Parent | Child | Relationship |
|--------|-------|--------------|
| Order | LineItem | One-to-Many (orderId) |
| LineItem | LineItemCreativeAssociation | One-to-Many (lineItemId) |
| Creative | LineItemCreativeAssociation | One-to-Many (creativeId) |
| LineItemTemplate | LineItem | Template-to-Instance |

---

## OrderService

The OrderService provides methods for creating, updating, and managing orders - the top-level containers for advertising campaigns.

### WSDL Endpoint

```
https://ads.google.com/apis/ads/publisher/v202511/OrderService?wsdl
```

### Methods

#### createOrders

Creates new Order objects in the system.

| Aspect | Details |
|--------|---------|
| **Parameters** | `orders` (Order[]) - Array of Order objects to create |
| **Returns** | Order[] - The created orders with assigned IDs |
| **Required Fields** | name, advertiserId, traffickerId |

#### getOrdersByStatement

Retrieves orders matching a PQL query.

| Aspect | Details |
|--------|---------|
| **Parameters** | `filterStatement` (Statement) - PQL query statement |
| **Returns** | OrderPage - Paginated results containing Order objects |
| **Supported Filters** | id, name, advertiserId, salespersonId, traffickerId, status, startDateTime, endDateTime, lastModifiedDateTime |

#### updateOrders

Updates existing Order objects.

| Aspect | Details |
|--------|---------|
| **Parameters** | `orders` (Order[]) - Array of Order objects to update |
| **Returns** | Order[] - The updated orders |
| **Note** | Only mutable fields can be updated |

#### performOrderAction

Performs bulk actions on orders matching a filter.

| Aspect | Details |
|--------|---------|
| **Parameters** | `orderAction` (OrderAction) - Action to perform, `filterStatement` (Statement) - Filter for target orders |
| **Returns** | UpdateResult - Number of objects affected |
| **Actions** | See [Order Actions](#order-actions) |

---

## LineItemService

The LineItemService manages line items - the actual advertising commitments within orders that define delivery goals, targeting, and pricing.

### WSDL Endpoint

```
https://ads.google.com/apis/ads/publisher/v202511/LineItemService?wsdl
```

### Methods

#### createLineItems

Creates new LineItem objects.

| Aspect | Details |
|--------|---------|
| **Parameters** | `lineItems` (LineItem[]) - Array of LineItem objects to create |
| **Returns** | LineItem[] - The created line items with assigned IDs |
| **Required Fields** | orderId, name, lineItemType, startDateTime, costType, costPerUnit, creativePlaceholders, targeting |

#### getLineItemsByStatement

Retrieves line items matching a PQL query.

| Aspect | Details |
|--------|---------|
| **Parameters** | `filterStatement` (Statement) - PQL query statement |
| **Returns** | LineItemPage - Paginated results containing LineItem objects |
| **Supported Filters** | id, name, orderId, status, lineItemType, costType, deliveryRateType, startDateTime, endDateTime, creationDateTime, lastModifiedDateTime, externalId, isMissingCreatives |

#### updateLineItems

Updates existing LineItem objects.

| Aspect | Details |
|--------|---------|
| **Parameters** | `lineItems` (LineItem[]) - Array of LineItem objects to update |
| **Returns** | LineItem[] - The updated line items |
| **Note** | Some fields become immutable after delivery starts |

#### performLineItemAction

Performs bulk actions on line items matching a filter.

| Aspect | Details |
|--------|---------|
| **Parameters** | `lineItemAction` (LineItemAction) - Action to perform, `filterStatement` (Statement) - Filter for target line items |
| **Returns** | UpdateResult - Number of objects affected |
| **Actions** | See [LineItem Actions](#lineitem-actions) |

---

## LineItemCreativeAssociationService

The LineItemCreativeAssociationService (LICA Service) manages the associations between line items and creatives, controlling which ads serve for each campaign.

### WSDL Endpoint

```
https://ads.google.com/apis/ads/publisher/v202511/LineItemCreativeAssociationService?wsdl
```

### Methods

#### createLineItemCreativeAssociations

Creates new associations between line items and creatives.

| Aspect | Details |
|--------|---------|
| **Parameters** | `lineItemCreativeAssociations` (LineItemCreativeAssociation[]) |
| **Returns** | LineItemCreativeAssociation[] - The created associations |
| **Required Fields** | lineItemId, creativeId (or creativeSetId) |
| **Prerequisite** | Creative size must match a creative placeholder in the line item |

#### getLineItemCreativeAssociationsByStatement

Retrieves associations matching a PQL query.

| Aspect | Details |
|--------|---------|
| **Parameters** | `filterStatement` (Statement) - PQL query statement |
| **Returns** | LineItemCreativeAssociationPage - Paginated results |
| **Supported Filters** | lineItemId, creativeId, status, manualCreativeRotationWeight, destinationUrl, lastModifiedDateTime |

#### updateLineItemCreativeAssociations

Updates existing associations.

| Aspect | Details |
|--------|---------|
| **Parameters** | `lineItemCreativeAssociations` (LineItemCreativeAssociation[]) |
| **Returns** | LineItemCreativeAssociation[] - The updated associations |

#### performLineItemCreativeAssociationAction

Performs bulk actions on associations.

| Aspect | Details |
|--------|---------|
| **Parameters** | `lineItemCreativeAssociationAction` (LineItemCreativeAssociationAction), `filterStatement` (Statement) |
| **Returns** | UpdateResult |
| **Actions** | See [LICA Actions](#lica-actions) |

#### getPreviewUrl

Returns an in-site preview URL for a specific creative on a line item.

| Aspect | Details |
|--------|---------|
| **Parameters** | `lineItemId` (long), `creativeId` (long), `siteUrl` (string) |
| **Returns** | string - The preview URL |
| **Use Case** | Client review before campaign launch |

#### getPreviewUrlsForNativeStyles

Returns preview URLs for all native style variations.

| Aspect | Details |
|--------|---------|
| **Parameters** | `lineItemId` (long), `creativeId` (long), `siteUrl` (string) |
| **Returns** | CreativeNativeStylePreview[] - Preview URLs for each native style |

---

## LineItemTemplateService

The LineItemTemplateService manages templates that define default values for creating new line items, enabling standardization across campaigns.

### WSDL Endpoint

```
https://ads.google.com/apis/ads/publisher/v202511/LineItemTemplateService?wsdl
```

### Methods

#### getLineItemTemplatesByStatement

Retrieves line item templates matching a PQL query.

| Aspect | Details |
|--------|---------|
| **Parameters** | `filterStatement` (Statement) - PQL query statement |
| **Returns** | LineItemTemplatePage - Paginated results |
| **Supported Filters** | id |

**Note:** LineItemTemplateService is primarily read-only via the API. Templates are typically created and managed through the Ad Manager UI.

---

## Data Models

### Order

The Order object represents an advertiser's campaign container. An Order groups individual LineItem objects which fulfill ad requests from a particular advertiser.

#### Order Object Fields (Complete Reference)

| Field | Type | Description | Required | Read-Only |
|-------|------|-------------|----------|-----------|
| `id` | xsd:long | Unique ID of the Order. Assigned by Google when an order is created. | No | Yes |
| `name` | xsd:string | The name of the Order. Must be unique within the network and has a maximum length of 255 characters. | **Yes** | No |
| `startDateTime` | DateTime | The date and time at which the Order and its associated line items are enabled to begin serving. Computed from line items. | No | Yes |
| `endDateTime` | DateTime | The date and time at which the Order and its associated line items stop serving. Computed from line items. | No | Yes |
| `unlimitedEndDateTime` | xsd:boolean | Specifies whether or not the Order has an unlimited end date. | No | Yes |
| `status` | OrderStatus | The status of the Order. | No | Yes |
| `isArchived` | xsd:boolean | The archival status of the Order. | No | Yes |
| `notes` | xsd:string | Provides any additional notes that may annotate the Order. Maximum length of 65,535 characters. | No | No |
| `externalOrderId` | xsd:int | An arbitrary ID to associate with the Order for external system tracking. | No | No |
| `poNumber` | xsd:string | The purchase order number for the Order. Maximum length of 63 characters. | No | No |
| `currencyCode` | xsd:string | The ISO currency code for the Order. Defaults to the network's currency code. | No | Yes |
| `advertiserId` | xsd:long | The unique ID of the Company representing the advertiser. | **Yes** | No |
| `advertiserContactIds` | xsd:long[] | List of IDs for advertiser contacts associated with the Order. | No | No |
| `agencyId` | xsd:long | The unique ID of the Company representing the agency. | No | No |
| `agencyContactIds` | xsd:long[] | List of IDs for agency contacts associated with the Order. | No | No |
| `creatorId` | xsd:long | The unique ID of the User who created the Order. | No | Yes |
| `traffickerId` | xsd:long | The unique ID of the User responsible for trafficking the Order. | **Yes** | No |
| `secondaryTraffickerIds` | xsd:long[] | The IDs of secondary traffickers associated with the Order. | No | No |
| `salespersonId` | xsd:long | The unique ID of the User responsible for selling the Order. | No | No |
| `secondarySalespersonIds` | xsd:long[] | The IDs of secondary salespeople associated with the Order. | No | No |
| `totalImpressionsDelivered` | xsd:long | Total impressions delivered for all line items in the Order. | No | Yes |
| `totalClicksDelivered` | xsd:long | Total clicks delivered for all line items in the Order. | No | Yes |
| `totalViewableImpressionsDelivered` | xsd:long | Total viewable impressions delivered for all line items in the Order. | No | Yes |
| `totalBudget` | Money | Total budget for all line items in the Order. Calculated from LineItem values. | No | Yes |
| `appliedLabels` | AppliedLabel[] | The set of labels applied directly to the Order. | No | No |
| `effectiveAppliedLabels` | AppliedLabel[] | Labels applied directly to this Order plus those inherited from the advertiser company. | No | Yes |
| `lastModifiedByApp` | xsd:string | The name of the application that last modified the Order. | No | Yes |
| `isProgrammatic` | xsd:boolean | Whether or not this Order is programmatic. Defaults to false. | No | No |
| `appliedTeamIds` | xsd:long[] | The IDs of teams directly applied to this Order. | No | No |
| `lastModifiedDateTime` | DateTime | The date and time the Order was last modified. | No | No |
| `customFieldValues` | BaseCustomFieldValue[] | The values of custom fields associated with the Order. | No | No |

#### OrderStatus Enum

Describes the status of an Order.

| Value | Description |
|-------|-------------|
| `DRAFT` | Order has just been created but no approval has been requested yet. Order is not deliverable. |
| `PENDING_APPROVAL` | A request for approval for the Order has been made. Order is not deliverable. |
| `APPROVED` | Order has been approved and is ready to serve. Line items are eligible to serve. |
| `DISAPPROVED` | Order has been disapproved and is not eligible to serve. |
| `PAUSED` | Legacy state. Paused status should be checked on LineItems within the order. |
| `CANCELED` | Order has been canceled and cannot serve. |
| `DELETED` | Order has been deleted by DSM. |
| `UNKNOWN` | Value returned if the actual value is not exposed by the requested API version. |

---

### LineItem

The LineItem object represents an advertiser's commitment to purchase a specific number of ad impressions, clicks, or time. A LineItem belongs to an Order and defines delivery goals, targeting criteria, and pricing information.

#### LineItem Object Fields (Complete Reference)

##### Core Identification Fields

| Field | Type | Description | Required | Read-Only |
|-------|------|-------------|----------|-----------|
| `id` | xsd:long | Uniquely identifies the LineItem. Assigned by Google. | No | Yes |
| `orderId` | xsd:long | The ID of the Order to which the LineItem belongs. | **Yes** | No |
| `name` | xsd:string | The name of the line item. Maximum length of 255 characters. | **Yes** | No |
| `externalId` | xsd:string | An identifier for the LineItem meaningful to the publisher. Maximum length of 255 characters. | No | No |
| `orderName` | xsd:string | The name of the Order to which the LineItem belongs. | No | Yes |

##### Scheduling Fields

| Field | Type | Description | Required | Read-Only |
|-------|------|-------------|----------|-----------|
| `startDateTime` | DateTime | The date and time on which the LineItem is enabled to begin serving. | **Yes** | No |
| `startDateTimeType` | StartDateTimeType | Specifies whether to start serving right away (IMMEDIATELY), in an hour (ONE_HOUR_FROM_NOW), or at a specific time (USE_START_DATE_TIME). | No | No |
| `endDateTime` | DateTime | The date and time on which the LineItem will stop serving. | No | No |
| `autoExtensionDays` | xsd:int | The number of days to allow delivery past endDateTime to reach goals. Maximum 7 days. Ad Manager 360 only. | No | No |
| `unlimitedEndDateTime` | xsd:boolean | Whether the LineItem has an end time. Defaults to false. Only certain LineItemTypes can be set to true. | No | No |

##### Delivery Configuration

| Field | Type | Description | Required | Read-Only |
|-------|------|-------------|----------|-----------|
| `lineItemType` | LineItemType | Indicates the type of line item (SPONSORSHIP, STANDARD, etc.). Determines default priority. | **Yes** | No |
| `priority` | xsd:int | The priority for the line item. Valid range is 1 to 16. Defaults vary by LineItemType. | No | No |
| `deliveryRateType` | DeliveryRateType | The strategy used for delivering ads over the line item's duration (EVENLY, FRONTLOADED, AS_FAST_AS_POSSIBLE). | No | No |
| `deliveryForecastSource` | DeliveryForecastSource | The strategy used for choosing forecasted traffic shapes to pace items (HISTORICAL, FORECASTING, CUSTOM_PACING_CURVE). | No | No |
| `customPacingCurve` | CustomPacingCurve | Custom pacing curve used to pace the line item's delivery. | No | No |
| `roadblockingType` | RoadblockingType | The strategy for serving roadblocked creatives (ONLY_ONE, ONE_OR_MORE, AS_MANY_AS_POSSIBLE, ALL_ROADBLOCK, CREATIVE_SET). | No | No |

##### Creative Configuration

| Field | Type | Description | Required | Read-Only |
|-------|------|-------------|----------|-----------|
| `creativePlaceholders` | CreativePlaceholder[] | Details about the creatives expected to serve through this line item. | **Yes** | No |
| `creativeRotationType` | CreativeRotationType | The strategy used for displaying multiple creatives (EVEN, OPTIMIZED, MANUAL, SEQUENTIAL). | **Yes** | No |
| `creativeTargetings` | CreativeTargeting[] | Creative-level targeting specifications. | No | No |
| `isMissingCreatives` | xsd:boolean | Indicates if the LineItem is missing any creatives for the placeholder. | No | Yes |

##### Pricing Fields

| Field | Type | Description | Required | Read-Only |
|-------|------|-------------|----------|-----------|
| `costType` | CostType | The method used for billing this LineItem (CPA, CPC, CPD, CPM, VCPM, CPM_IN_TARGET, CPCV). | **Yes** | No |
| `costPerUnit` | Money | The amount of money to spend per impression or click. | **Yes** | No |
| `valueCostPerUnit` | Money | An amount to help the adserver rank inventory based on value, separate from costPerUnit for billing. | No | No |
| `discountType` | LineItemDiscountType | The type of discount being applied (PERCENTAGE or ABSOLUTE_VALUE). | No | No |
| `discount` | xsd:double | The discount percentage or absolute value depending on discountType. | No | No |
| `contractedUnitsBought` | xsd:long | The contracted quantity or minimum quantity for reporting reference. | No | No |
| `budget` | Money | The amount of money allocated to the LineItem. | No | Yes |

##### Goal Configuration

| Field | Type | Description | Required | Read-Only |
|-------|------|-------------|----------|-----------|
| `primaryGoal` | Goal | The primary goal that this LineItem is associated with for pacing and budgeting. | No | No |
| `secondaryGoals` | Goal[] | Secondary goals associated with the LineItem. | No | No |
| `frequencyCaps` | FrequencyCap[] | The set of frequency capping units for this LineItem. | No | No |

##### Targeting

| Field | Type | Description | Required | Read-Only |
|-------|------|-------------|----------|-----------|
| `targeting` | Targeting | Contains all targeting criteria for the ad campaign. | **Yes** | No |
| `environmentType` | EnvironmentType | The environment that the LineItem is targeting (BROWSER or VIDEO_PLAYER). | No | No |
| `allowedFormats` | AllowedFormats[] | The set of allowedFormats that this programmatic line item can have (AUDIO or unspecified for all). | No | No |

##### Status Fields

| Field | Type | Description | Required | Read-Only |
|-------|------|-------------|----------|-----------|
| `status` | ComputedStatus | The status of the LineItem. | No | Yes |
| `reservationStatus` | ReservationStatus | Indicates whether inventory has been reserved (RESERVED or UNRESERVED). | No | Yes |
| `isArchived` | xsd:boolean | The archival status of the LineItem. | No | Yes |
| `stats` | Stats | Trafficking statistics for the line item. | No | Yes |
| `deliveryIndicator` | DeliveryIndicator | Indicates the line item's performance level. | No | Yes |
| `deliveryData` | DeliveryData | Clicks or impressions delivered in the last 7 days. | No | Yes |

##### Video & Rich Media Fields

| Field | Type | Description | Required | Read-Only |
|-------|------|-------------|----------|-----------|
| `videoMaxDuration` | xsd:long | The max duration of a video creative in milliseconds. | No | No |
| `skippableAdType` | SkippableAdType | The nature of the line item's creatives' skippability (DISABLED, ENABLED, INSTREAM_SELECT, ANY). | No | No |
| `companionDeliveryOption` | CompanionDeliveryOption | Indicates how companion creatives should be delivered (OPTIONAL, AT_LEAST_ONE, ALL). | No | No |
| `customVastExtension` | xsd:string | Custom XML rendered in the VAST response. | No | No |

##### Additional Fields

| Field | Type | Description | Required | Read-Only |
|-------|------|-------------|----------|-----------|
| `activityAssociations` | LineItemActivityAssociation[] | Activity associations; applicable when costType is CPA. | No | No |
| `allowOverbook` | xsd:boolean | Whether overbooking is allowed for reservations. | No | No |
| `skipInventoryCheck` | xsd:boolean | Whether inventory check is skipped when updating. | No | No |
| `skipCrossSellingRuleWarningChecks` | xsd:boolean | Whether to skip checks for cross-selling rule warnings. | No | No |
| `reserveAtCreation` | xsd:boolean | Whether inventory is reserved when creating line item. | No | No |
| `webPropertyCode` | xsd:string | The web property code for dynamic allocation items. | No | No |
| `appliedLabels` | AppliedLabel[] | The set of labels applied directly to the line item. | No | No |
| `effectiveAppliedLabels` | AppliedLabel[] | Labels inherited from order and advertiser. | No | Yes |
| `disableSameAdvertiserCompetitiveExclusion` | xsd:boolean | Allow same advertiser serving despite exclusions. | No | No |
| `lastModifiedByApp` | xsd:string | The application that last modified this item. | No | Yes |
| `notes` | xsd:string | Additional notes. Maximum length of 65,535 characters. | No | No |
| `competitiveConstraintScope` | CompetitiveConstraintScope | The scope for competitive exclusion labels. | No | No |
| `lastModifiedDateTime` | DateTime | The date and time line item was last modified. | No | No |
| `creationDateTime` | DateTime | The date and time line item was created. | No | No |
| `customFieldValues` | BaseCustomFieldValue[] | The values of custom fields associated with the item. | No | No |
| `programmaticCreativeSource` | ProgrammaticCreativeSource | Indicates the programmatic creative source. | No | Yes |
| `thirdPartyMeasurementSettings` | ThirdPartyMeasurementSettings | Settings for third-party measurement. | No | No |
| `youtubeKidsRestricted` | xsd:boolean | Designates item as intended for YouTube Kids app. | No | No |
| `grpSettings` | GrpSettings | Information for line item with GRP demographic. | No | No |
| `dealInfo` | LineItemDealInfoDto | Deal information if programmatic. | No | No |
| `viewabilityProviderCompanyIds` | xsd:long[] | IDs of Companies providing ad verification. | No | No |
| `childContentEligibility` | ChildContentEligibility | Child content eligibility designation. | No | No |
| `repeatedCreativeServingEnabled` | xsd:boolean | Whether repeated creative serving is enabled. | No | No |

---

#### LineItemType Enum (Complete Reference)

Indicates the type of LineItem and determines the default priority for delivery.

| Value | Description | Default Priority |
|-------|-------------|------------------|
| `SPONSORSHIP` | A percentage of all the impressions that are being sold are reserved. Used for exclusive or share-of-voice campaigns. | 4 |
| `STANDARD` | A fixed quantity of impressions or clicks are reserved. Guaranteed delivery campaigns. | 8 |
| `NETWORK` | Fills unsold inventory. Users specify a daily percentage of unsold impressions or clicks. | 12 |
| `BULK` | Fixed impression/click delivery at lower priority than STANDARD type. Non-guaranteed bulk delivery. | 12 |
| `PRICE_PRIORITY` | Fills unsold inventory. Users specify a fixed quantity of unsold impressions or clicks. Competes on price. | 12 |
| `HOUSE` | Ads that promote products and services chosen by the publisher. Has lowest delivery priority. No revenue. | 16 |
| `LEGACY_DFP` | Migrated from DFP system. Cannot be created, activated, or resumed. | N/A |
| `CLICK_TRACKING` | Tracks ads served outside of Ad Manager, such as email newsletters. | N/A |
| `ADSENSE` | Uses dynamic allocation backed by AdSense. | 12 |
| `AD_EXCHANGE` | Uses dynamic allocation backed by the Google Ad Exchange. | 12 |
| `BUMPER` | Non-monetizable video line item targeting bumper positions (short house messages). | 16 |
| `ADMOB` | Uses dynamic allocation backed by AdMob. | 12 |
| `PREFERRED_DEAL` | No impressions reserved. Serves at second-price bid through ProposalLineItem. Programmatic. | N/A |

---

#### CostType Enum (Complete Reference)

Describes the billable actions for LineItem.

| Value | Description | Compatible LineItemTypes |
|-------|-------------|-------------------------|
| `CPA` | Cost per action. **Note:** Read-only since February 22, 2024 due to Spotlight deprecation. | SPONSORSHIP, STANDARD, BULK, NETWORK |
| `CPC` | Cost per click. | SPONSORSHIP, STANDARD, BULK, NETWORK, PRICE_PRIORITY, HOUSE |
| `CPD` | Cost per day. | SPONSORSHIP, NETWORK |
| `CPM` | Cost per mille (cost per thousand impressions). Most common cost type. | SPONSORSHIP, STANDARD, BULK, NETWORK, PRICE_PRIORITY, HOUSE |
| `VCPM` | Cost per thousand Active View viewable impressions. | STANDARD only |
| `CPM_IN_TARGET` | Cost per thousand in-target impressions. | STANDARD only |
| `CPCV` | Cost per completed view. For standard reservation video line items. | STANDARD only |
| `UNKNOWN` | Value returned when the actual value is not exposed by the requested API version. | N/A |

---

#### CreativeRotationType Enum (Complete Reference)

Describes the strategy for displaying multiple creatives associated with a LineItem.

| Value | Description |
|-------|-------------|
| `EVEN` | Creatives are displayed roughly the same number of times over the duration of the line item. |
| `OPTIMIZED` | Creatives are served roughly proportionally to their performance. Automatically optimizes serving. |
| `MANUAL` | Creatives are served roughly proportionally to their weights set on the LineItemCreativeAssociation. |
| `SEQUENTIAL` | Creatives are served exactly in sequential order (aka Storyboarding). Set on the LineItemCreativeAssociation. |

---

#### DeliveryRateType Enum (Complete Reference)

Describes the strategy for delivering ads over the duration of a line item.

| Value | Description |
|-------|-------------|
| `EVENLY` | Line items are served as evenly as possible across the number of days specified in a line item's duration. Recommended for most campaigns. |
| `FRONTLOADED` | Line items are served more aggressively in the beginning of the flight date. Useful for testing or when early delivery is important. |
| `AS_FAST_AS_POSSIBLE` | The booked impressions for a line item may be delivered well before the endDateTime. Other lower-priority or lower-value line items will be stopped from delivering until this line item meets the number of impressions or clicks it is booked for. |

---

#### RoadblockingType Enum (Complete Reference)

Describes the strategy for serving roadblocked creatives (multiple creatives on same page).

| Value | Description |
|-------|-------------|
| `ONLY_ONE` | Only one creative from a line item can serve at a time on a given page. |
| `ONE_OR_MORE` | Any number of creatives from a line item can serve together at a time. |
| `AS_MANY_AS_POSSIBLE` | As many creatives from a line item as can fit on a page will serve. This could mean anywhere from one to all of a line item's creatives given the size constraints of ad slots on a page. |
| `ALL_ROADBLOCK` | All or none of the creatives from a line item will serve. This option will only work if served to a GPT tag using SRA (single request architecture mode). |
| `CREATIVE_SET` | A master/companion CreativeSet roadblocking type. A LineItem.creativePlaceholders must be set accordingly. |

---

#### SkippableAdType Enum (Complete Reference)

Describes the skippability settings for video ads.

| Value | Description |
|-------|-------------|
| `DISABLED` | Skippable ad type is disabled. Ads cannot be skipped. |
| `ENABLED` | Skippable ad type is enabled. Ads can be skipped after the skip offset. |
| `INSTREAM_SELECT` | Skippable in-stream ad type. Uses TrueView in-stream select behavior. |
| `ANY` | Any skippable or not skippable. This is only for programmatic cases when the creative skippability is decided by the buyside. |
| `UNKNOWN` | Value returned if the actual value is not exposed by the requested API version. |

---

#### ComputedStatus Enum (Complete Reference)

Describes the computed status of a LineItem.

| Value | Description |
|-------|-------------|
| `DRAFT` | The LineItem is still being drafted. Not ready for delivery. |
| `PENDING_APPROVAL` | The LineItem has been submitted for approval. |
| `READY` | The LineItem has been activated and is ready to serve. |
| `DELIVERING` | The LineItem has begun serving impressions. |
| `DELIVERY_EXTENDED` | The LineItem has past its endDateTime with an auto extension, but hasn't met its goal. |
| `PAUSED` | The LineItem has been paused from serving manually. |
| `INACTIVE` | The LineItem is inactive. Either caused by missing creatives or the network disabling auto-activation. |
| `PAUSED_INVENTORY_RELEASED` | The LineItem has been paused and its reserved inventory has been released. The LineItem will not serve. |
| `COMPLETED` | The LineItem has completed its run and delivered its full goal. |
| `DISAPPROVED` | The LineItem has been disapproved and is not eligible to serve. |
| `CANCELED` | The LineItem has been canceled and is no longer eligible to serve. Legacy status imported from Google Ad Manager orders. |

---

### LineItemCreativeAssociation

A LineItemCreativeAssociation (LICA) associates a Creative or CreativeSet with a LineItem so that the creative can be served in ad units targeted by the line item. When a line item is selected to serve, the LICAs specify which creatives can appear for the ad units that are targeted by the line item.

#### LineItemCreativeAssociation Object Fields (Complete Reference)

| Field | Type | Description | Required | Read-Only |
|-------|------|-------------|----------|-----------|
| `lineItemId` | xsd:long | The ID of the LineItem to which the Creative should be associated. | **Yes** | No |
| `creativeId` | xsd:long | The ID of the Creative being associated. Required for single creative associations, ignored for creative set associations. | **Yes*** | No |
| `creativeSetId` | xsd:long | The ID of the CreativeSet being associated with a LineItem. Use this instead of creativeId when associating a creative set. | **Yes*** | No |
| `manualCreativeRotationWeight` | xsd:double | The weight value used only when the line item's creative rotation type is set to MANUAL. Defaults to 10. Higher values mean more frequent serving relative to other creatives. | No | No |
| `sequentialCreativeRotationIndex` | xsd:int | The sequential rotation index of the Creative. Used only for SEQUENTIAL rotation type. Defaults to 1. Lower index values serve first. | No | No |
| `startDateTime` | DateTime | Overrides the value set for LineItem.startDateTime. This is optional and only available for Ad Manager 360 networks. | No | No |
| `startDateTimeType` | StartDateTimeType | Governs the start time behavior: IMMEDIATELY (start right away), ONE_HOUR_FROM_NOW, or USE_START_DATE_TIME (use startDateTime field). Defaults to USE_START_DATE_TIME. | No | No |
| `endDateTime` | DateTime | Overrides LineItem.endDateTime. This is optional and only available for Ad Manager 360 networks. | No | No |
| `destinationUrl` | xsd:string | Overrides the value set for HasDestinationUrlCreative.destinationUrl. Allows different landing pages per LICA. Only available for Ad Manager 360 networks. | No | No |
| `sizes` | Size[] | Overrides the value set for Creative.size. Allows the creative to serve to incompatible ad unit sizes. | No | No |
| `status` | LineItemCreativeAssociation.Status | The status of the association (ACTIVE, INACTIVE, or UNKNOWN). | No | Yes |
| `stats` | LineItemCreativeAssociationStats | Contains trafficking statistics for the association including impressions and clicks delivered. | No | Yes |
| `lastModifiedDateTime` | DateTime | The date and time this association was last modified. | No | No |
| `targetingName` | xsd:string | Specifies the CreativeTargeting for this association. Should match the corresponding CreativePlaceholder targetingName on the line item. | No | No |

**Note:** *Either `creativeId` OR `creativeSetId` is required, depending on whether you're associating a single creative or a creative set.

#### LineItemCreativeAssociation.Status Enum

| Value | Description |
|-------|-------------|
| `ACTIVE` | The creative association is active and can serve. |
| `INACTIVE` | The creative association has been deactivated and will not serve. |
| `UNKNOWN` | Value returned if the actual value is not exposed by the requested API version. |

---

### LineItemTemplate

A LineItemTemplate provides default values for creating new line items. Templates can standardize line item configurations across campaigns and reduce setup time.

#### LineItemTemplate Object Fields (Complete Reference)

| Field | Type | Description | Required | Read-Only |
|-------|------|-------------|----------|-----------|
| `id` | xsd:long | Uniquely identifies the LineItemTemplate. Assigned by Google when a template is created. | No | Yes |
| `name` | xsd:string | The name of the LineItemTemplate. Must be unique within the network. | **Yes** | No |
| `isDefault` | xsd:boolean | Whether the LineItemTemplate represents the default choices for creating a LineItem. Only one default LineItemTemplate is allowed per Network. | No | Yes |
| `lineItemName` | xsd:string | The default name to be assigned to new line items created from this template. Maximum 127 characters. | No | No |
| `enabledForSameAdvertiserException` | xsd:boolean | The default value for the LineItem.enabledForSameAdvertiserException field of a new LineItem. Allows same-advertiser competitive exclusion override. | **Yes** | No |
| `notes` | xsd:string | Default notes to be assigned to new line items. Maximum 65,535 characters. | No | No |
| `lineItemType` | LineItemType | The default type of a new LineItem (SPONSORSHIP, STANDARD, NETWORK, etc.). | **Yes** | No |
| `deliveryRateType` | DeliveryRateType | The default delivery strategy for a new LineItem (EVENLY, FRONTLOADED, AS_FAST_AS_POSSIBLE). | **Yes** | No |
| `roadblockingType` | RoadblockingType | The default roadblocking strategy for a new LineItem (ONLY_ONE, ONE_OR_MORE, AS_MANY_AS_POSSIBLE, ALL_ROADBLOCK, CREATIVE_SET). | **Yes** | No |
| `creativeRotationType` | CreativeRotationType | The default creative rotation strategy for a new LineItem (EVEN, OPTIMIZED, MANUAL, SEQUENTIAL). | **Yes** | No |

**Note:** LineItemTemplates are primarily read-only via the API. Templates are typically created and managed through the Ad Manager UI.

---

### Targeting

The Targeting object contains all targeting criteria for a LineItem. It is a required field on LineItem and must specify at least inventory targeting.

#### Targeting Object Fields (Complete Reference)

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `inventoryTargeting` | InventoryTargeting | Specifies inventory targeted by the LineItem. **Must target at least one ad unit or placement.** | **Yes** |
| `geoTargeting` | GeoTargeting | Specifies geographical locations being targeted or excluded by the LineItem. | No |
| `dayPartTargeting` | DayPartTargeting | Specifies the days of the week and times that are targeted by the LineItem. | No |
| `dateTimeRangeTargeting` | DateTimeRangeTargeting | Specifies specific date ranges targeted by the LineItem. | No |
| `technologyTargeting` | TechnologyTargeting | Specifies browsing technologies (browsers, operating systems, device categories, etc.) targeted by the LineItem. | No |
| `customTargeting` | CustomCriteriaSet | Specifies custom key-value targeting criteria. Supports up to three levels of nested criteria with OR at the top level and AND at the second level. | No |
| `userDomainTargeting` | UserDomainTargeting | Specifies domains/subdomains targeted or excluded based on user IP associations. | No |
| `contentTargeting` | ContentTargeting | Specifies video categories and individual videos targeted by the LineItem. | No |
| `videoPositionTargeting` | VideoPositionTargeting | Targets specific positions within video streams (pre-roll, mid-roll, post-roll). | No |
| `mobileApplicationTargeting` | MobileApplicationTargeting | Targets specific mobile applications. | No |
| `buyerUserListTargeting` | BuyerUserListTargeting | Read-only field for programmatic LineItems regarding buyer user lists. | No (Read-only) |
| `inventoryUrlTargeting` | InventoryUrlTargeting | Specifies specific URLs targeted. Currently supported by YieldGroup only. | No |
| `verticalTargeting` | VerticalTargeting | Specifies IAB content verticals/categories targeted. IDs correspond to AD_CATEGORY table entries. | No |
| `contentLabelTargeting` | ContentLabelTargeting | Specifies content labels to exclude. IDs correspond to CONTENT_LABEL table entries. | No |
| `requestPlatformTargeting` | RequestPlatformTargeting | Specifies request platforms targeted. **Required for video line items and proposal line items.** | Conditional |
| `inventorySizeTargeting` | InventorySizeTargeting | Specifies creative sizes targeted. Supported on YieldGroup and TrafficDataRequest. | No |
| `publisherProvidedSignalsTargeting` | PublisherProvidedSignalsTargeting | Additional publisher-provided signals for targeting. | No |

---

#### InventoryTargeting Object

Specifies which ad units and placements are targeted or excluded.

| Field | Type | Description |
|-------|------|-------------|
| `targetedAdUnits` | AdUnitTargeting[] | A list of targeted ad units. Each AdUnitTargeting specifies adUnitId and includeDescendants. |
| `excludedAdUnits` | AdUnitTargeting[] | A list of excluded ad units. |
| `targetedPlacementIds` | xsd:long[] | A list of targeted Placement IDs. |

##### AdUnitTargeting Object

| Field | Type | Description |
|-------|------|-------------|
| `adUnitId` | xsd:string | The ID of the ad unit to target. |
| `includeDescendants` | xsd:boolean | Whether to include all child ad units. Defaults to true. |

---

#### GeoTargeting Object

Specifies geographical locations being targeted or excluded.

| Field | Type | Description |
|-------|------|-------------|
| `targetedLocations` | Location[] | The geographical locations being targeted by the LineItem. |
| `excludedLocations` | Location[] | The geographical locations being excluded by the LineItem. |

**Constraints:**
- Cannot simultaneously target and exclude identical locations
- Cannot target a child location if its parent is excluded
- Must not target a location while also targeting its parent
- Cannot explicitly define inclusions or exclusions already implicit in other selections

---

#### CustomCriteriaSet Object

Contains custom key-value targeting criteria with logical operators.

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `logicalOperator` | LogicalOperator | The logical operator to be applied to children (AND or OR). | **Yes** |
| `children` | CustomCriteriaNode[] | The custom criteria. Can contain CustomCriteriaSet, CustomCriteria, CmsMetadataCriteria, or AudienceSegmentCriteria. | **Yes** |

##### CustomCriteria Object

| Field | Type | Description |
|-------|------|-------------|
| `keyId` | xsd:long | The ID of the custom targeting key. |
| `valueIds` | xsd:long[] | The IDs of custom targeting values. Values are OR'd together. |
| `operator` | CustomCriteriaComparisonOperator | The comparison operator (IS, IS_NOT). |

---

#### FrequencyCap Object

Restricts impressions for individual viewers during designated time periods.

| Field | Type | Description |
|-------|------|-------------|
| `maxImpressions` | xsd:int | The maximum number of impressions that can be served to a user within the specified time period. |
| `numTimeUnits` | xsd:int | The number of time units to represent the total time period. |
| `timeUnit` | TimeUnit | The unit of time for the frequency cap (MINUTE, HOUR, DAY, WEEK, MONTH, LIFETIME, POD, STREAM). |

##### TimeUnit Enum

| Value | Description |
|-------|-------------|
| `MINUTE` | Per minute time unit. |
| `HOUR` | Per hour time unit. |
| `DAY` | Per day time unit. |
| `WEEK` | Per week time unit. |
| `MONTH` | Per month time unit. |
| `LIFETIME` | Per lifetime (total duration) of the line item. |
| `POD` | Per pod of ads in a video stream. Only for video player environments. |
| `STREAM` | Per video stream. Only for video player environments. |
| `UNKNOWN` | Value returned when the actual value is not exposed by the API version. |

---

#### Goal Object

Defines the delivery goal criteria a LineItem needs to satisfy.

| Field | Type | Description |
|-------|------|-------------|
| `goalType` | GoalType | The type of the goal (NONE, LIFETIME, DAILY). Defines the period over which the goal should be reached. |
| `unitType` | UnitType | The type of the goal unit (IMPRESSIONS, CLICKS, VIEWABLE_IMPRESSIONS, etc.). |
| `units` | xsd:long | For primary goals: the number or percentage reserved. For secondary goals: the threshold at which serving stops. |

##### GoalType Enum

| Value | Description | Compatible LineItemTypes |
|-------|-------------|-------------------------|
| `NONE` | No delivery goal specified. | PRICE_PRIORITY, AD_EXCHANGE, CLICK_TRACKING |
| `LIFETIME` | Delivery goal applies across entire line item duration. | STANDARD, BULK, PRICE_PRIORITY, ADSENSE, AD_EXCHANGE, ADMOB, CLICK_TRACKING |
| `DAILY` | Daily delivery goal. | SPONSORSHIP, NETWORK, PRICE_PRIORITY, HOUSE, ADSENSE, AD_EXCHANGE, ADMOB, BUMPER |
| `UNKNOWN` | Value returned when actual value isn't exposed by API version. | N/A |

##### UnitType Enum

| Value | Description |
|-------|-------------|
| `IMPRESSIONS` | Goal is measured in impressions. |
| `CLICKS` | Goal is measured in clicks. |
| `CLICK_THROUGH_CPA_CONVERSIONS` | Goal is click-through CPA conversions (deprecated). |
| `VIEW_THROUGH_CPA_CONVERSIONS` | Goal is view-through CPA conversions (deprecated). |
| `TOTAL_CPA_CONVERSIONS` | Goal is total CPA conversions (deprecated). |
| `VIEWABLE_IMPRESSIONS` | Goal is measured in viewable impressions. |
| `IN_TARGET_IMPRESSIONS` | Goal is measured in in-target impressions. |
| `COMPLETED_VIEWS` | Goal is measured in completed video views. |
| `UNKNOWN` | Value returned when actual value isn't exposed by API version. |

---

#### CreativePlaceholder Object

Describes the expected creative dimensions and settings for a line item.

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `size` | Size | The dimensions that the creative is expected to have. | **Yes** |
| `creativeTemplateId` | xsd:long | Native creative template ID. Required only when creativeSizeType is NATIVE. | Conditional |
| `companions` | CreativePlaceholder[] | The companion creatives expected. Only valid for VIDEO_PLAYER environment or CREATIVE_SET roadblocking. | No |
| `appliedLabels` | AppliedLabel[] | The set of label frequency caps applied directly to this placeholder. | No |
| `effectiveAppliedLabels` | AppliedLabel[] | Labels applied directly plus those inherited from creative template. | No (Read-only) |
| `expectedCreativeCount` | xsd:int | Expected number of creatives for this placeholder. Used to improve forecasting accuracy. | No |
| `creativeSizeType` | CreativeSizeType | Describes the size type (PIXEL, ASPECT_RATIO, INTERSTITIAL, NATIVE, etc.). Defaults to PIXEL. | No |
| `targetingName` | xsd:string | The name of the CreativeTargeting for creatives this placeholder represents. | No |
| `isAmpOnly` | xsd:boolean | Indicates whether the expected creative has an AMP-only variant. For forecasting only. | No |

---

## Actions Reference

Actions are used with the `performOrderAction`, `performLineItemAction`, and `performLineItemCreativeAssociationAction` methods to execute bulk operations on objects matching a filter statement.

### Order Actions (Complete Reference)

All Order actions are executed via `performOrderAction(orderAction, filterStatement)`.

| Action | Description | Use Case | Requirements |
|--------|-------------|----------|--------------|
| `ApproveOrders` | Approves orders for delivery. All line items become eligible to serve. | Campaign launch | Order must be in PENDING_APPROVAL or DRAFT status |
| `ApproveAndOverbookOrders` | Approves orders and allows inventory overbooking for its line items. | High-priority campaigns that must serve even if inventory is overcommitted | Order must be in PENDING_APPROVAL or DRAFT status |
| `ApproveOrdersWithoutReservationChanges` | Approves orders without modifying inventory reservations. | Workflow approval only (no inventory impact) | Order must be in PENDING_APPROVAL or DRAFT status |
| `ArchiveOrders` | Archives completed or canceled orders. Archived orders are hidden from default views. | Cleanup and organization | Order must not be actively delivering |
| `DeleteOrders` | Permanently deletes orders. **This action cannot be undone.** | Remove draft orders that will never be used | Order must be in DRAFT status |
| `DisapproveOrders` | Rejects orders in the approval workflow. Order becomes ineligible to serve. | Approval workflow rejection | Order must be in PENDING_APPROVAL status |
| `DisapproveOrdersWithoutReservationChanges` | Rejects orders without releasing inventory reservations. | Workflow rejection (preserve inventory) | Order must be in PENDING_APPROVAL status |
| `PauseOrders` | Pauses all line items in the order. Delivery stops immediately. | Temporary delivery stop | Order must be APPROVED |
| `ResumeOrders` | Resumes delivery for paused orders. Line items become eligible to serve again. | Resume delivery after pause | Order must be PAUSED |
| `ResumeAndOverbookOrders` | Resumes orders with overbooking allowed for line items. | Priority resume with guaranteed delivery | Order must be PAUSED |
| `RetractOrders` | Retracts an order from the approval workflow. Returns to DRAFT status. | Cancel approval request | Order must be in PENDING_APPROVAL status |
| `RetractOrdersWithoutReservationChanges` | Retracts orders without modifying inventory reservations. | Workflow retraction (preserve inventory) | Order must be in PENDING_APPROVAL status |
| `SubmitOrdersForApproval` | Submits draft orders for approval. Order enters PENDING_APPROVAL status. | Initiate approval workflow | Order must be in DRAFT status |
| `SubmitOrdersForApprovalAndOverbook` | Submits orders for approval with overbooking flag. | High-priority approval request | Order must be in DRAFT status |
| `SubmitOrdersForApprovalWithoutReservationChanges` | Submits orders without reserving inventory. | Workflow submission only | Order must be in DRAFT status |
| `UnarchiveOrders` | Restores archived orders to active state. | Recover campaigns for viewing or reporting | Order must be archived |

### LineItem Actions (Complete Reference)

All LineItem actions are executed via `performLineItemAction(lineItemAction, filterStatement)`.

| Action | Description | Use Case | Requirements |
|--------|-------------|----------|--------------|
| `ActivateLineItems` | Activates line items for delivery. Changes status to READY or DELIVERING. | Start campaign delivery | Line item must have creatives and valid targeting |
| `ArchiveLineItems` | Archives completed or canceled line items. Archived items are hidden from default views. | Cleanup and organization | Line item must not be actively delivering |
| `DeleteLineItems` | Permanently deletes line items. **This action cannot be undone.** | Remove draft line items | Line item must be in DRAFT status |
| `PauseLineItems` | Pauses line item delivery. Status changes to PAUSED. | Temporary delivery stop | Line item must be DELIVERING or READY |
| `ReleaseLineItems` | Releases reserved inventory for line items. Status changes to PAUSED_INVENTORY_RELEASED. | Free inventory for other campaigns | Line item must have reserved inventory |
| `ReserveLineItems` | Reserves inventory for line items. Guarantees delivery capacity. | Ensure delivery guarantee | Line item must be eligible for reservation |
| `ReserveAndOverbookLineItems` | Reserves inventory with overbooking allowed. Reserves even if insufficient inventory. | High-priority guaranteed delivery | Line item must be eligible for reservation |
| `ResumeLineItems` | Resumes paused line items. Status returns to READY/DELIVERING. | Resume delivery after pause | Line item must be PAUSED |
| `ResumeAndOverbookLineItems` | Resumes line items with overbooking allowed. | Priority resume with guaranteed delivery | Line item must be PAUSED |
| `UnarchiveLineItems` | Restores archived line items to active state. | Recover line items for viewing or reuse | Line item must be archived |

### LICA Actions (Complete Reference)

All LICA actions are executed via `performLineItemCreativeAssociationAction(lineItemCreativeAssociationAction, filterStatement)`.

| Action | Description | Use Case | Requirements |
|--------|-------------|----------|--------------|
| `ActivateLineItemCreativeAssociations` | Activates creative associations. Creatives become eligible to serve for the line item. | Enable specific creatives | Association must be INACTIVE |
| `DeactivateLineItemCreativeAssociations` | Deactivates creative associations. Creatives stop serving but association is preserved. | Temporarily disable creatives | Association must be ACTIVE |
| `DeleteLineItemCreativeAssociations` | Permanently removes creative associations. **This action cannot be undone.** | Remove creative-line item links | None |

### Action Response

All `performAction` methods return an `UpdateResult` object:

| Field | Type | Description |
|-------|------|-------------|
| `numChanges` | xsd:int | The number of objects that were affected by the action. |

---

## PQL Filtering

Publisher Query Language (PQL) enables filtering when retrieving objects.

### Statement Structure

```python
statement = {
    'query': 'WHERE field = :value ORDER BY field LIMIT 500 OFFSET 0',
    'values': [
        {'key': 'value', 'value': {'xsi_type': 'TextValue', 'value': 'search_term'}}
    ]
}
```

### Order Filter Fields

| Field | Type | Example |
|-------|------|---------|
| `id` | long | `WHERE id = :orderId` |
| `name` | string | `WHERE name LIKE '%campaign%'` |
| `advertiserId` | long | `WHERE advertiserId = :advertiserId` |
| `salespersonId` | long | `WHERE salespersonId = :userId` |
| `traffickerId` | long | `WHERE traffickerId = :userId` |
| `status` | string | `WHERE status = 'APPROVED'` |
| `startDateTime` | DateTime | `WHERE startDateTime >= :date` |
| `endDateTime` | DateTime | `WHERE endDateTime <= :date` |
| `lastModifiedDateTime` | DateTime | `WHERE lastModifiedDateTime > :date` |

### LineItem Filter Fields

| Field | Type | Example |
|-------|------|---------|
| `id` | long | `WHERE id = :lineItemId` |
| `name` | string | `WHERE name LIKE '%video%'` |
| `orderId` | long | `WHERE orderId = :orderId` |
| `status` | string | `WHERE status = 'DELIVERING'` |
| `lineItemType` | string | `WHERE lineItemType = 'STANDARD'` |
| `costType` | string | `WHERE costType = 'CPM'` |
| `deliveryRateType` | string | `WHERE deliveryRateType = 'EVENLY'` |
| `startDateTime` | DateTime | `WHERE startDateTime >= :date` |
| `endDateTime` | DateTime | `WHERE endDateTime <= :date` |
| `creationDateTime` | DateTime | `WHERE creationDateTime > :date` |
| `lastModifiedDateTime` | DateTime | `WHERE lastModifiedDateTime > :date` |
| `externalId` | string | `WHERE externalId = :externalId` |
| `isMissingCreatives` | boolean | `WHERE isMissingCreatives = true` |

### LICA Filter Fields

| Field | Type | Example |
|-------|------|---------|
| `lineItemId` | long | `WHERE lineItemId = :lineItemId` |
| `creativeId` | long | `WHERE creativeId = :creativeId` |
| `status` | string | `WHERE status = 'ACTIVE'` |
| `manualCreativeRotationWeight` | double | `WHERE manualCreativeRotationWeight > 0` |
| `destinationUrl` | string | `WHERE destinationUrl LIKE '%example%'` |
| `lastModifiedDateTime` | DateTime | `WHERE lastModifiedDateTime > :date` |

### LineItemTemplate Filter Fields

| Field | Type | Example |
|-------|------|---------|
| `id` | long | `WHERE id = :templateId` |

---

## Python Code Examples

### Setup and Authentication

```python
from googleads import ad_manager
from googleads import errors
import datetime

# Initialize the client from googleads.yaml
client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')

# Get service instances
order_service = client.GetService('OrderService', version='v202511')
line_item_service = client.GetService('LineItemService', version='v202511')
lica_service = client.GetService('LineItemCreativeAssociationService', version='v202511')
template_service = client.GetService('LineItemTemplateService', version='v202511')
```

### Creating an Order

```python
def create_order(client, advertiser_id, trafficker_id, name, notes=None):
    """Create a new order for an advertiser.

    Args:
        client: The Ad Manager client
        advertiser_id: The advertiser company ID
        trafficker_id: The trafficking user ID
        name: Order name
        notes: Optional order notes

    Returns:
        The created Order object
    """
    order_service = client.GetService('OrderService', version='v202511')

    order = {
        'name': name,
        'advertiserId': advertiser_id,
        'traffickerId': trafficker_id,
    }

    if notes:
        order['notes'] = notes

    # Create the order
    orders = order_service.createOrders([order])

    if orders:
        created_order = orders[0]
        print(f"Created order '{created_order['name']}' with ID {created_order['id']}")
        return created_order
    return None


# Example usage
order = create_order(
    client,
    advertiser_id=123456789,
    trafficker_id=987654321,
    name='Q4 2025 Display Campaign',
    notes='Holiday promotion campaign'
)
```

### Creating a Line Item with Targeting

```python
def create_line_item(
    client,
    order_id,
    name,
    ad_unit_ids,
    start_datetime,
    end_datetime,
    goal_units,
    cost_per_unit_micro_amount,
    sizes,
    line_item_type='STANDARD',
    cost_type='CPM',
    geo_target_ids=None,
    custom_targeting=None
):
    """Create a line item with targeting.

    Args:
        client: The Ad Manager client
        order_id: Parent order ID
        name: Line item name
        ad_unit_ids: List of ad unit IDs to target
        start_datetime: Start date as datetime object
        end_datetime: End date as datetime object
        goal_units: Number of impressions/clicks to deliver
        cost_per_unit_micro_amount: Cost in micro amounts (1,000,000 = $1.00)
        sizes: List of creative sizes as dicts {'width': X, 'height': Y}
        line_item_type: Type of line item (STANDARD, SPONSORSHIP, etc.)
        cost_type: Pricing model (CPM, CPC, etc.)
        geo_target_ids: Optional list of geographic location IDs
        custom_targeting: Optional custom targeting criteria

    Returns:
        The created LineItem object
    """
    line_item_service = client.GetService('LineItemService', version='v202511')

    # Build inventory targeting
    inventory_targeting = {
        'targetedAdUnits': [
            {'adUnitId': ad_unit_id, 'includeDescendants': True}
            for ad_unit_id in ad_unit_ids
        ]
    }

    # Build targeting object
    targeting = {
        'inventoryTargeting': inventory_targeting
    }

    # Add geo targeting if specified
    if geo_target_ids:
        targeting['geoTargeting'] = {
            'targetedLocations': [
                {'id': geo_id} for geo_id in geo_target_ids
            ]
        }

    # Add custom targeting if specified
    if custom_targeting:
        targeting['customTargeting'] = custom_targeting

    # Build creative placeholders
    creative_placeholders = [
        {
            'size': size,
            'creativeSizeType': 'PIXEL'
        }
        for size in sizes
    ]

    # Determine goal type based on cost type
    goal_type = 'IMPRESSIONS' if cost_type == 'CPM' else 'CLICKS'

    line_item = {
        'orderId': order_id,
        'name': name,
        'lineItemType': line_item_type,
        'targeting': targeting,
        'creativePlaceholders': creative_placeholders,
        'startDateTime': {
            'date': {
                'year': start_datetime.year,
                'month': start_datetime.month,
                'day': start_datetime.day
            },
            'hour': start_datetime.hour,
            'minute': start_datetime.minute,
            'second': 0,
            'timeZoneId': 'America/New_York'
        },
        'endDateTime': {
            'date': {
                'year': end_datetime.year,
                'month': end_datetime.month,
                'day': end_datetime.day
            },
            'hour': end_datetime.hour,
            'minute': end_datetime.minute,
            'second': 0,
            'timeZoneId': 'America/New_York'
        },
        'costType': cost_type,
        'costPerUnit': {
            'currencyCode': 'USD',
            'microAmount': cost_per_unit_micro_amount
        },
        'primaryGoal': {
            'goalType': 'LIFETIME',
            'unitType': goal_type,
            'units': goal_units
        },
        'creativeRotationType': 'OPTIMIZED',
        'deliveryRateType': 'EVENLY',
    }

    # Create the line item
    line_items = line_item_service.createLineItems([line_item])

    if line_items:
        created = line_items[0]
        print(f"Created line item '{created['name']}' with ID {created['id']}")
        return created
    return None


# Example usage
from datetime import datetime, timedelta

line_item = create_line_item(
    client,
    order_id=order['id'],
    name='Homepage Banner - 300x250',
    ad_unit_ids=[12345, 67890],  # Target specific ad units
    start_datetime=datetime.now() + timedelta(days=1),
    end_datetime=datetime.now() + timedelta(days=31),
    goal_units=1000000,  # 1 million impressions
    cost_per_unit_micro_amount=2000000,  # $2.00 CPM
    sizes=[{'width': 300, 'height': 250}],
    geo_target_ids=[2840],  # United States
)
```

### Creating a Line Item with Custom Targeting

```python
def create_line_item_with_custom_targeting(
    client,
    order_id,
    name,
    ad_unit_ids,
    custom_key_id,
    custom_value_ids,
    **kwargs
):
    """Create a line item with custom key-value targeting.

    Args:
        client: The Ad Manager client
        order_id: Parent order ID
        name: Line item name
        ad_unit_ids: List of ad unit IDs to target
        custom_key_id: Custom targeting key ID
        custom_value_ids: List of custom targeting value IDs (OR relationship)
        **kwargs: Additional line item parameters

    Returns:
        The created LineItem object
    """
    line_item_service = client.GetService('LineItemService', version='v202511')

    # Build custom targeting (values are OR'd together)
    custom_targeting = {
        'xsi_type': 'CustomCriteriaSet',
        'logicalOperator': 'AND',
        'children': [
            {
                'xsi_type': 'CustomCriteria',
                'keyId': custom_key_id,
                'valueIds': custom_value_ids,
                'operator': 'IS'
            }
        ]
    }

    # Build the targeting object
    targeting = {
        'inventoryTargeting': {
            'targetedAdUnits': [
                {'adUnitId': ad_unit_id, 'includeDescendants': True}
                for ad_unit_id in ad_unit_ids
            ]
        },
        'customTargeting': custom_targeting
    }

    line_item = {
        'orderId': order_id,
        'name': name,
        'lineItemType': kwargs.get('line_item_type', 'STANDARD'),
        'targeting': targeting,
        'creativePlaceholders': [
            {'size': {'width': 300, 'height': 250}, 'creativeSizeType': 'PIXEL'}
        ],
        'startDateTimeType': 'IMMEDIATELY',
        'unlimitedEndDateTime': True,
        'costType': 'CPM',
        'costPerUnit': {'currencyCode': 'USD', 'microAmount': 1000000},
        'primaryGoal': {
            'goalType': 'LIFETIME',
            'unitType': 'IMPRESSIONS',
            'units': 500000
        },
        'creativeRotationType': 'OPTIMIZED',
        'deliveryRateType': 'EVENLY',
    }

    line_items = line_item_service.createLineItems([line_item])

    if line_items:
        created = line_items[0]
        print(f"Created line item with custom targeting: {created['id']}")
        return created
    return None


# Example: Target users with specific interests
line_item = create_line_item_with_custom_targeting(
    client,
    order_id=order['id'],
    name='Sports Interest Targeting',
    ad_unit_ids=[12345],
    custom_key_id=111222,  # "interest" key
    custom_value_ids=[333444, 555666]  # "sports", "fitness" values
)
```

### Associating Creatives with Line Items

```python
def associate_creative_with_line_item(client, line_item_id, creative_id, weight=10):
    """Associate a creative with a line item.

    Args:
        client: The Ad Manager client
        line_item_id: The line item ID
        creative_id: The creative ID
        weight: Manual rotation weight (default 10)

    Returns:
        The created LineItemCreativeAssociation object
    """
    lica_service = client.GetService(
        'LineItemCreativeAssociationService',
        version='v202511'
    )

    lica = {
        'lineItemId': line_item_id,
        'creativeId': creative_id,
        'manualCreativeRotationWeight': weight
    }

    licas = lica_service.createLineItemCreativeAssociations([lica])

    if licas:
        created = licas[0]
        print(f"Associated creative {creative_id} with line item {line_item_id}")
        return created
    return None


def associate_multiple_creatives(client, line_item_id, creative_ids, weights=None):
    """Associate multiple creatives with a line item.

    Args:
        client: The Ad Manager client
        line_item_id: The line item ID
        creative_ids: List of creative IDs
        weights: Optional list of weights (same length as creative_ids)

    Returns:
        List of created LineItemCreativeAssociation objects
    """
    lica_service = client.GetService(
        'LineItemCreativeAssociationService',
        version='v202511'
    )

    if weights is None:
        weights = [10] * len(creative_ids)

    licas = [
        {
            'lineItemId': line_item_id,
            'creativeId': creative_id,
            'manualCreativeRotationWeight': weight
        }
        for creative_id, weight in zip(creative_ids, weights)
    ]

    created_licas = lica_service.createLineItemCreativeAssociations(licas)

    print(f"Associated {len(created_licas)} creatives with line item {line_item_id}")
    return created_licas


# Example usage
# Single creative
lica = associate_creative_with_line_item(
    client,
    line_item_id=line_item['id'],
    creative_id=999888777
)

# Multiple creatives with weights
licas = associate_multiple_creatives(
    client,
    line_item_id=line_item['id'],
    creative_ids=[111222333, 444555666, 777888999],
    weights=[50, 30, 20]  # 50%, 30%, 20% rotation
)
```

### Querying Orders and Line Items

```python
def get_orders_by_advertiser(client, advertiser_id, limit=500):
    """Get all orders for a specific advertiser.

    Args:
        client: The Ad Manager client
        advertiser_id: The advertiser company ID
        limit: Maximum number of orders to return

    Returns:
        List of Order objects
    """
    order_service = client.GetService('OrderService', version='v202511')

    statement = {
        'query': f'WHERE advertiserId = :advertiserId ORDER BY id LIMIT {limit}',
        'values': [
            {
                'key': 'advertiserId',
                'value': {
                    'xsi_type': 'NumberValue',
                    'value': advertiser_id
                }
            }
        ]
    }

    response = order_service.getOrdersByStatement(statement)

    if 'results' in response:
        orders = response['results']
        print(f"Found {len(orders)} orders for advertiser {advertiser_id}")
        return orders
    return []


def get_line_items_by_order(client, order_id, status=None, limit=500):
    """Get all line items for a specific order.

    Args:
        client: The Ad Manager client
        order_id: The order ID
        status: Optional status filter (e.g., 'DELIVERING')
        limit: Maximum number of line items to return

    Returns:
        List of LineItem objects
    """
    line_item_service = client.GetService('LineItemService', version='v202511')

    query = f'WHERE orderId = :orderId'
    values = [
        {
            'key': 'orderId',
            'value': {
                'xsi_type': 'NumberValue',
                'value': order_id
            }
        }
    ]

    if status:
        query += ' AND status = :status'
        values.append({
            'key': 'status',
            'value': {
                'xsi_type': 'TextValue',
                'value': status
            }
        })

    query += f' ORDER BY id LIMIT {limit}'

    statement = {
        'query': query,
        'values': values
    }

    response = line_item_service.getLineItemsByStatement(statement)

    if 'results' in response:
        line_items = response['results']
        print(f"Found {len(line_items)} line items for order {order_id}")
        return line_items
    return []


def get_line_items_missing_creatives(client, order_id=None, limit=500):
    """Get line items that are missing creatives.

    Args:
        client: The Ad Manager client
        order_id: Optional order ID to filter by
        limit: Maximum number of line items to return

    Returns:
        List of LineItem objects missing creatives
    """
    line_item_service = client.GetService('LineItemService', version='v202511')

    query = 'WHERE isMissingCreatives = true'
    values = []

    if order_id:
        query += ' AND orderId = :orderId'
        values.append({
            'key': 'orderId',
            'value': {
                'xsi_type': 'NumberValue',
                'value': order_id
            }
        })

    query += f' ORDER BY id LIMIT {limit}'

    statement = {
        'query': query,
        'values': values
    }

    response = line_item_service.getLineItemsByStatement(statement)

    if 'results' in response:
        line_items = response['results']
        print(f"Found {len(line_items)} line items missing creatives")
        return line_items
    return []


# Example usage
orders = get_orders_by_advertiser(client, advertiser_id=123456789)
line_items = get_line_items_by_order(client, order_id=orders[0]['id'], status='DELIVERING')
missing_creative_items = get_line_items_missing_creatives(client)
```

### Paginated Queries

```python
def get_all_line_items_paginated(client, order_id, page_size=500):
    """Get all line items for an order using pagination.

    Args:
        client: The Ad Manager client
        order_id: The order ID
        page_size: Number of items per page

    Yields:
        LineItem objects
    """
    line_item_service = client.GetService('LineItemService', version='v202511')

    offset = 0
    total_results = None

    while True:
        statement = {
            'query': f'WHERE orderId = :orderId ORDER BY id LIMIT {page_size} OFFSET {offset}',
            'values': [
                {
                    'key': 'orderId',
                    'value': {
                        'xsi_type': 'NumberValue',
                        'value': order_id
                    }
                }
            ]
        }

        response = line_item_service.getLineItemsByStatement(statement)

        if total_results is None:
            total_results = response.get('totalResultSetSize', 0)
            print(f"Total line items: {total_results}")

        if 'results' not in response or not response['results']:
            break

        for line_item in response['results']:
            yield line_item

        offset += page_size

        if offset >= total_results:
            break


# Example usage
for line_item in get_all_line_items_paginated(client, order_id=12345):
    print(f"Line item: {line_item['name']} (ID: {line_item['id']})")
```

### Performing Bulk Actions

```python
def approve_order(client, order_id):
    """Approve an order for delivery.

    Args:
        client: The Ad Manager client
        order_id: The order ID to approve

    Returns:
        UpdateResult with count of affected orders
    """
    order_service = client.GetService('OrderService', version='v202511')

    action = {'xsi_type': 'ApproveOrders'}

    statement = {
        'query': 'WHERE id = :orderId',
        'values': [
            {
                'key': 'orderId',
                'value': {
                    'xsi_type': 'NumberValue',
                    'value': order_id
                }
            }
        ]
    }

    result = order_service.performOrderAction(action, statement)

    if result and result['numChanges'] > 0:
        print(f"Approved order {order_id}")
    else:
        print(f"Failed to approve order {order_id}")

    return result


def pause_line_items_by_order(client, order_id):
    """Pause all line items in an order.

    Args:
        client: The Ad Manager client
        order_id: The order ID

    Returns:
        UpdateResult with count of affected line items
    """
    line_item_service = client.GetService('LineItemService', version='v202511')

    action = {'xsi_type': 'PauseLineItems'}

    statement = {
        'query': 'WHERE orderId = :orderId AND status = :status',
        'values': [
            {
                'key': 'orderId',
                'value': {
                    'xsi_type': 'NumberValue',
                    'value': order_id
                }
            },
            {
                'key': 'status',
                'value': {
                    'xsi_type': 'TextValue',
                    'value': 'DELIVERING'
                }
            }
        ]
    }

    result = line_item_service.performLineItemAction(action, statement)

    print(f"Paused {result['numChanges']} line items in order {order_id}")
    return result


def activate_line_item_creatives(client, line_item_id):
    """Activate all creative associations for a line item.

    Args:
        client: The Ad Manager client
        line_item_id: The line item ID

    Returns:
        UpdateResult with count of affected associations
    """
    lica_service = client.GetService(
        'LineItemCreativeAssociationService',
        version='v202511'
    )

    action = {'xsi_type': 'ActivateLineItemCreativeAssociations'}

    statement = {
        'query': 'WHERE lineItemId = :lineItemId AND status = :status',
        'values': [
            {
                'key': 'lineItemId',
                'value': {
                    'xsi_type': 'NumberValue',
                    'value': line_item_id
                }
            },
            {
                'key': 'status',
                'value': {
                    'xsi_type': 'TextValue',
                    'value': 'INACTIVE'
                }
            }
        ]
    }

    result = lica_service.performLineItemCreativeAssociationAction(action, statement)

    print(f"Activated {result['numChanges']} creative associations")
    return result


def archive_completed_orders(client, days_completed=30, limit=100):
    """Archive orders that completed more than X days ago.

    Args:
        client: The Ad Manager client
        days_completed: Number of days since completion
        limit: Maximum orders to archive

    Returns:
        UpdateResult with count of archived orders
    """
    order_service = client.GetService('OrderService', version='v202511')

    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_completed)

    action = {'xsi_type': 'ArchiveOrders'}

    # Note: This filters orders whose end date has passed
    statement = {
        'query': f'''
            WHERE status IN ('APPROVED', 'COMPLETED')
            AND endDateTime < :cutoffDate
            AND isArchived = false
            LIMIT {limit}
        ''',
        'values': [
            {
                'key': 'cutoffDate',
                'value': {
                    'xsi_type': 'DateTimeValue',
                    'value': {
                        'date': {
                            'year': cutoff_date.year,
                            'month': cutoff_date.month,
                            'day': cutoff_date.day
                        },
                        'hour': 0,
                        'minute': 0,
                        'second': 0,
                        'timeZoneId': 'UTC'
                    }
                }
            }
        ]
    }

    result = order_service.performOrderAction(action, statement)

    print(f"Archived {result['numChanges']} orders")
    return result


# Example usage
approve_order(client, order_id=12345)
pause_line_items_by_order(client, order_id=12345)
activate_line_item_creatives(client, line_item_id=67890)
archive_completed_orders(client, days_completed=60)
```

### Updating Line Items

```python
def update_line_item_end_date(client, line_item_id, new_end_date):
    """Update a line item's end date.

    Args:
        client: The Ad Manager client
        line_item_id: The line item ID
        new_end_date: New end date as datetime object

    Returns:
        The updated LineItem object
    """
    line_item_service = client.GetService('LineItemService', version='v202511')

    # First, retrieve the current line item
    statement = {
        'query': 'WHERE id = :lineItemId LIMIT 1',
        'values': [
            {
                'key': 'lineItemId',
                'value': {
                    'xsi_type': 'NumberValue',
                    'value': line_item_id
                }
            }
        ]
    }

    response = line_item_service.getLineItemsByStatement(statement)

    if 'results' not in response or not response['results']:
        raise ValueError(f"Line item {line_item_id} not found")

    line_item = response['results'][0]

    # Update the end date
    line_item['endDateTime'] = {
        'date': {
            'year': new_end_date.year,
            'month': new_end_date.month,
            'day': new_end_date.day
        },
        'hour': new_end_date.hour,
        'minute': new_end_date.minute,
        'second': 0,
        'timeZoneId': 'America/New_York'
    }

    # Update the line item
    updated = line_item_service.updateLineItems([line_item])

    if updated:
        print(f"Updated line item {line_item_id} end date to {new_end_date}")
        return updated[0]
    return None


def update_line_item_goal(client, line_item_id, new_units):
    """Update a line item's delivery goal.

    Args:
        client: The Ad Manager client
        line_item_id: The line item ID
        new_units: New goal units (impressions/clicks)

    Returns:
        The updated LineItem object
    """
    line_item_service = client.GetService('LineItemService', version='v202511')

    # Retrieve current line item
    statement = {
        'query': 'WHERE id = :lineItemId LIMIT 1',
        'values': [
            {
                'key': 'lineItemId',
                'value': {
                    'xsi_type': 'NumberValue',
                    'value': line_item_id
                }
            }
        ]
    }

    response = line_item_service.getLineItemsByStatement(statement)
    line_item = response['results'][0]

    # Update the primary goal
    line_item['primaryGoal']['units'] = new_units

    updated = line_item_service.updateLineItems([line_item])

    if updated:
        print(f"Updated line item {line_item_id} goal to {new_units} units")
        return updated[0]
    return None


# Example usage
from datetime import datetime, timedelta

# Extend campaign by 2 weeks
update_line_item_end_date(
    client,
    line_item_id=67890,
    new_end_date=datetime.now() + timedelta(days=14)
)

# Increase impression goal
update_line_item_goal(
    client,
    line_item_id=67890,
    new_units=2000000  # 2 million impressions
)
```

### Getting Line Item Templates

```python
def get_all_line_item_templates(client):
    """Get all line item templates in the network.

    Args:
        client: The Ad Manager client

    Returns:
        List of LineItemTemplate objects
    """
    template_service = client.GetService('LineItemTemplateService', version='v202511')

    statement = {'query': 'ORDER BY id LIMIT 500'}

    response = template_service.getLineItemTemplatesByStatement(statement)

    if 'results' in response:
        templates = response['results']
        print(f"Found {len(templates)} line item templates")

        for template in templates:
            print(f"  - {template['name']} (ID: {template['id']}, "
                  f"Type: {template['lineItemType']}, "
                  f"Default: {template.get('isDefault', False)})")

        return templates
    return []


def get_default_template(client):
    """Get the default line item template.

    Args:
        client: The Ad Manager client

    Returns:
        The default LineItemTemplate or None
    """
    templates = get_all_line_item_templates(client)

    for template in templates:
        if template.get('isDefault', False):
            return template

    return None


# Example usage
templates = get_all_line_item_templates(client)
default_template = get_default_template(client)
```

### Getting Creative Preview URLs

```python
def get_creative_preview_url(client, line_item_id, creative_id, site_url):
    """Get an in-site preview URL for a creative.

    Args:
        client: The Ad Manager client
        line_item_id: The line item ID
        creative_id: The creative ID
        site_url: The site URL to preview on

    Returns:
        The preview URL string
    """
    lica_service = client.GetService(
        'LineItemCreativeAssociationService',
        version='v202511'
    )

    preview_url = lica_service.getPreviewUrl(
        lineItemId=line_item_id,
        creativeId=creative_id,
        siteUrl=site_url
    )

    print(f"Preview URL: {preview_url}")
    return preview_url


# Example usage
preview = get_creative_preview_url(
    client,
    line_item_id=12345,
    creative_id=67890,
    site_url='https://www.example.com/article'
)
```

---

## Common Patterns & Best Practices

### Campaign Creation Workflow

```python
def create_complete_campaign(
    client,
    advertiser_id,
    trafficker_id,
    campaign_name,
    line_item_configs,
    creative_ids_map
):
    """Create a complete campaign with order, line items, and creative associations.

    Args:
        client: The Ad Manager client
        advertiser_id: Advertiser company ID
        trafficker_id: Trafficking user ID
        campaign_name: Campaign/order name
        line_item_configs: List of line item configuration dicts
        creative_ids_map: Dict mapping line item names to creative ID lists

    Returns:
        Tuple of (order, line_items, licas)
    """
    # Step 1: Create the order
    order = create_order(
        client,
        advertiser_id=advertiser_id,
        trafficker_id=trafficker_id,
        name=campaign_name
    )

    if not order:
        raise Exception("Failed to create order")

    # Step 2: Create line items
    line_item_service = client.GetService('LineItemService', version='v202511')

    line_items_to_create = []
    for config in line_item_configs:
        config['orderId'] = order['id']
        line_items_to_create.append(config)

    line_items = line_item_service.createLineItems(line_items_to_create)

    # Step 3: Create creative associations
    lica_service = client.GetService(
        'LineItemCreativeAssociationService',
        version='v202511'
    )

    licas_to_create = []
    for line_item in line_items:
        creative_ids = creative_ids_map.get(line_item['name'], [])
        for creative_id in creative_ids:
            licas_to_create.append({
                'lineItemId': line_item['id'],
                'creativeId': creative_id
            })

    licas = []
    if licas_to_create:
        licas = lica_service.createLineItemCreativeAssociations(licas_to_create)

    # Step 4: Approve the order
    approve_order(client, order['id'])

    return order, line_items, licas
```

### Error Handling Pattern

```python
from googleads import errors

def safe_create_order(client, order_data):
    """Create an order with comprehensive error handling.

    Args:
        client: The Ad Manager client
        order_data: Order configuration dict

    Returns:
        Created Order or None
    """
    order_service = client.GetService('OrderService', version='v202511')

    try:
        orders = order_service.createOrders([order_data])
        return orders[0] if orders else None

    except errors.GoogleAdsServerFault as e:
        # Handle API-specific errors
        for error in e.errors:
            error_type = error['ApiError.Type']

            if error_type == 'OrderError':
                reason = error.get('reason', 'UNKNOWN')
                if reason == 'INVALID_ORDER_NAME':
                    print(f"Invalid order name: {order_data.get('name')}")
                elif reason == 'ADVERTISER_NOT_FOUND':
                    print(f"Advertiser not found: {order_data.get('advertiserId')}")

            elif error_type == 'PermissionError':
                print("Permission denied - check user access")

            elif error_type == 'QuotaError':
                print("API quota exceeded - try again later")

            else:
                print(f"Error: {error_type} - {error}")

        return None

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def safe_perform_action(client, service_name, action_type, statement):
    """Perform an action with error handling and retry logic.

    Args:
        client: The Ad Manager client
        service_name: Name of the service (OrderService, LineItemService, etc.)
        action_type: Action xsi_type string
        statement: PQL statement dict

    Returns:
        UpdateResult or None
    """
    import time

    service = client.GetService(service_name, version='v202511')
    action = {'xsi_type': action_type}

    max_retries = 3
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            if service_name == 'OrderService':
                result = service.performOrderAction(action, statement)
            elif service_name == 'LineItemService':
                result = service.performLineItemAction(action, statement)
            elif service_name == 'LineItemCreativeAssociationService':
                result = service.performLineItemCreativeAssociationAction(action, statement)
            else:
                raise ValueError(f"Unknown service: {service_name}")

            return result

        except errors.GoogleAdsServerFault as e:
            # Check for retryable errors
            retryable = False
            for error in e.errors:
                if error.get('ApiError.Type') in ['ServerError', 'InternalApiError']:
                    retryable = True
                    break

            if retryable and attempt < max_retries - 1:
                print(f"Retryable error, waiting {retry_delay}s (attempt {attempt + 1})")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                raise

    return None
```

### Batch Operations

```python
def batch_update_line_items(client, updates, batch_size=200):
    """Update line items in batches to avoid API limits.

    Args:
        client: The Ad Manager client
        updates: List of (line_item_id, update_dict) tuples
        batch_size: Number of items per batch

    Returns:
        List of all updated LineItem objects
    """
    line_item_service = client.GetService('LineItemService', version='v202511')
    all_updated = []

    # Group updates by line item ID
    line_item_ids = [u[0] for u in updates]

    # Fetch all line items first
    for i in range(0, len(line_item_ids), batch_size):
        batch_ids = line_item_ids[i:i + batch_size]

        id_list = ', '.join(str(id) for id in batch_ids)
        statement = {
            'query': f'WHERE id IN ({id_list})',
            'values': []
        }

        response = line_item_service.getLineItemsByStatement(statement)

        if 'results' not in response:
            continue

        # Apply updates
        line_items_to_update = []
        for line_item in response['results']:
            for lid, update_dict in updates:
                if line_item['id'] == lid:
                    line_item.update(update_dict)
                    line_items_to_update.append(line_item)
                    break

        # Update batch
        if line_items_to_update:
            updated = line_item_service.updateLineItems(line_items_to_update)
            all_updated.extend(updated)
            print(f"Updated batch of {len(updated)} line items")

    return all_updated
```

### Validation Before Creation

```python
def validate_line_item_config(config):
    """Validate line item configuration before creation.

    Args:
        config: Line item configuration dict

    Raises:
        ValueError: If configuration is invalid
    """
    required_fields = ['orderId', 'name', 'lineItemType', 'costType',
                       'costPerUnit', 'creativePlaceholders', 'targeting']

    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field: {field}")

    # Validate name length
    if len(config['name']) > 255:
        raise ValueError("Line item name exceeds 255 characters")

    # Validate line item type
    valid_types = ['SPONSORSHIP', 'STANDARD', 'NETWORK', 'BULK',
                   'PRICE_PRIORITY', 'HOUSE', 'PREFERRED_DEAL']
    if config['lineItemType'] not in valid_types:
        raise ValueError(f"Invalid lineItemType: {config['lineItemType']}")

    # Validate cost type
    valid_cost_types = ['CPA', 'CPC', 'CPD', 'CPM', 'VCPM', 'CPM_IN_TARGET', 'CPCV']
    if config['costType'] not in valid_cost_types:
        raise ValueError(f"Invalid costType: {config['costType']}")

    # Validate creative placeholders
    if not config['creativePlaceholders']:
        raise ValueError("At least one creative placeholder is required")

    # Validate targeting
    if 'inventoryTargeting' not in config['targeting']:
        raise ValueError("inventoryTargeting is required in targeting")

    print("Line item configuration is valid")
```

---

## Error Handling

### Common Errors and Solutions

| Error Type | Common Reason | Solution |
|------------|---------------|----------|
| `OrderError` | INVALID_ORDER_NAME | Ensure name is unique and <= 255 chars |
| `OrderError` | ADVERTISER_NOT_FOUND | Verify advertiser company ID exists |
| `LineItemError` | INVALID_LINE_ITEM_TYPE | Use valid LineItemType enum value |
| `LineItemError` | START_DATE_TIME_IS_IN_PAST | Set startDateTime to future or use IMMEDIATELY |
| `LineItemCreativeAssociationError` | CREATIVE_NOT_ELIGIBLE | Creative size must match placeholder |
| `InventoryTargetingError` | INVALID_AD_UNIT_ID | Verify ad unit exists and is active |
| `CustomTargetingError` | KEY_NOT_FOUND | Verify custom targeting key ID |
| `PermissionError` | ACCESS_DENIED | Check user permissions |
| `QuotaError` | EXCEEDED_QUOTA | Implement rate limiting/backoff |
| `AuthenticationError` | NETWORK_API_ACCESS_DISABLED | Enable API access in network settings |

### Error Response Structure

```python
# Example error response structure
{
    'errors': [
        {
            'ApiError.Type': 'LineItemError',
            'fieldPath': 'lineItems[0].startDateTime',
            'trigger': '2024-01-01',
            'reason': 'START_DATE_TIME_IS_IN_PAST',
            'message': 'Start date time cannot be in the past.'
        }
    ]
}
```

---

## API Reference Links

Official Google Ad Manager API v202511 documentation:

| Resource | URL |
|----------|-----|
| **API Overview** | [developers.google.com/ad-manager/api/reference/v202511](https://developers.google.com/ad-manager/api/reference/v202511) |
| **OrderService** | [OrderService Reference](https://developers.google.com/ad-manager/api/reference/v202511/OrderService) |
| **Order Type** | [Order Object Reference](https://developers.google.com/ad-manager/api/reference/v202511/OrderService.Order) |
| **LineItemService** | [LineItemService Reference](https://developers.google.com/ad-manager/api/reference/v202511/LineItemService) |
| **LineItem Type** | [LineItem Object Reference](https://developers.google.com/ad-manager/api/reference/v202511/LineItemService.LineItem) |
| **LICA Service** | [LineItemCreativeAssociationService Reference](https://developers.google.com/ad-manager/api/reference/v202511/LineItemCreativeAssociationService) |
| **Template Service** | [LineItemTemplateService Reference](https://developers.google.com/ad-manager/api/reference/v202511/LineItemTemplateService) |
| **PQL Syntax** | [PublisherQueryLanguageService Reference](https://developers.google.com/ad-manager/api/reference/v202511/PublisherQueryLanguageService) |
| **Python Library** | [googleads-python-lib GitHub](https://github.com/googleads/googleads-python-lib) |

---

*Documentation generated for GAM API integration project. Last updated: 2025-11-28. Expanded with complete field definitions from official Google Ad Manager API v202511 reference.*
