# Google Ad Manager SOAP API v202511 - Creatives

> **API Version:** v202511
> **Last Updated:** 2025-11-28
> **Category:** Creative Management

This documentation covers the services for managing creatives, creative sets, creative templates, and creative wrappers in Google Ad Manager.

---

## Table of Contents

1. [Overview](#overview)
2. [Service Relationships](#service-relationships)
3. [CreativeService](#creativeservice)
4. [Creative Types Hierarchy](#creative-types-hierarchy)
5. [Creative Data Models](#creative-data-models)
6. [CreativeSetService](#creativesetservice)
7. [CreativeTemplateService](#creativetemplateservice)
8. [CreativeWrapperService](#creativewrapperservice)
9. [Enumerations Reference](#enumerations-reference)
10. [Python Code Examples](#python-code-examples)
11. [Best Practices](#best-practices)
12. [Error Handling](#error-handling)
13. [Related Services](#related-services)

---

## Overview

The Creatives category provides services for managing advertising creatives - the actual ad content that gets served to users. These services enable:

### Use Cases

- **Creative Management**: Create, update, and manage various creative types (image, video, HTML5, third-party)
- **Creative Sets**: Group master and companion creatives for coordinated delivery
- **Template-Based Creatives**: Use predefined or custom templates for standardized creative creation
- **Creative Wrappers**: Add header/footer HTML snippets or video tracking URLs to creatives
- **Native Ads**: Create native-eligible creatives using templates (see also [NativeStyleService](./NativeStyleService.md))

### Workflow Overview

```
Creative Lifecycle:

    [CreativeTemplate]           [CreativeWrapper]
           |                            |
           v                            v
    [TemplateCreative]    [Applied to Ad Units via Labels]
           |
           v
    [Creative] <---> [CreativeSet] (master + companions)
           |
           v
    [LineItemCreativeAssociation] (LICA)
           |
           v
    [LineItem] --> [Ad Serving]
```

---

## Service Relationships

```
+------------------------+       +------------------------+
|  CreativeTemplateService|      |  CreativeWrapperService |
|  (Templates - read only)|      |  (Header/Footer HTML)   |
+------------------------+       +------------------------+
           |                              |
           | defines                      | wraps
           v                              v
+------------------------+       +------------------------+
|    CreativeService     |       |      Ad Units          |
|    (All Creative Types)|       |  (via Label targeting) |
+------------------------+       +------------------------+
           |
           | groups into
           v
+------------------------+
|   CreativeSetService   |
|   (Master + Companions)|
+------------------------+
           |
           | associated via
           v
+------------------------+
| LineItemCreativeAssoc  |
|      Service (LICA)    |
+------------------------+
```

### Key Relationships

| Parent | Child | Relationship |
|--------|-------|--------------|
| CreativeTemplate | TemplateCreative | Template defines structure |
| Creative | CreativeSet | Master creative + companions |
| Creative | LineItemCreativeAssociation | Required for ad serving |
| CreativeWrapper | Ad Unit | Applied via labels |

---

## CreativeService

The CreativeService provides methods for creating, updating, retrieving, and performing actions on Creative objects.

### WSDL Endpoint

```
https://ads.google.com/apis/ads/publisher/v202511/CreativeService?wsdl
```

### Namespace

```
https://www.google.com/apis/ads/publisher/v202511
```

### Methods

#### createCreatives

Creates new Creative objects.

| Aspect | Details |
|--------|---------|
| **Parameters** | `creatives` (Creative[]) - Array of Creative objects to create |
| **Returns** | Creative[] - The created creatives with assigned IDs |
| **Required Fields** | advertiserId, name, size (varies by creative type) |

#### getCreativesByStatement

Retrieves creatives matching a PQL query.

| Aspect | Details |
|--------|---------|
| **Parameters** | `filterStatement` (Statement) - PQL query statement |
| **Returns** | CreativePage - Paginated results containing Creative objects |

**Filterable Fields:**

| Field | Type | Operators |
|-------|------|-----------|
| `id` | xsd:long | `=`, `!=`, `IN`, `NOT IN` |
| `name` | xsd:string | `=`, `!=`, `LIKE` |
| `advertiserId` | xsd:long | `=`, `!=`, `IN`, `NOT IN` |
| `width` | xsd:int | `=`, `!=`, `<`, `>` |
| `height` | xsd:int | `=`, `!=`, `<`, `>` |
| `lastModifiedDateTime` | DateTime | `=`, `!=`, `<`, `>` |

#### updateCreatives

Updates existing Creative objects.

| Aspect | Details |
|--------|---------|
| **Parameters** | `creatives` (Creative[]) - Array of Creative objects to update |
| **Returns** | Creative[] - The updated creatives |
| **Note** | The `id` field is required for updates |

#### performCreativeAction

Performs bulk actions on creatives matching a filter.

| Aspect | Details |
|--------|---------|
| **Parameters** | `creativeAction` (CreativeAction) - Action to perform, `filterStatement` (Statement) - Filter for target creatives |
| **Returns** | UpdateResult - Number of objects affected |

**Available Actions:**

| Action | xsi:type | Description |
|--------|----------|-------------|
| **Activate** | `ActivateCreatives` | Activates creatives for serving |
| **Deactivate** | `DeactivateCreatives` | Deactivates creatives (stops serving) |

---

## Creative Types Hierarchy

Google Ad Manager supports numerous creative types organized in a class hierarchy:

### Base Classes

```
Creative (abstract base)
    |
    +-- HasDestinationUrlCreative (abstract)
    |       |
    |       +-- BaseImageCreative
    |       +-- BaseImageRedirectCreative
    |       +-- BaseVideoCreative
    |       +-- BaseAudioCreative
    |       +-- CustomCreative
    |       +-- Html5Creative
    |       +-- TemplateCreative
    |       +-- ThirdPartyCreative
    |
    +-- BaseDynamicAllocationCreative
    |       |
    |       +-- AdExchangeCreative
    |       +-- AdSenseCreative
    |
    +-- ProgrammaticCreative
    +-- InternalRedirectCreative
    +-- UnsupportedCreative
```

### Image Creatives

| Type | Description | Use Case |
|------|-------------|----------|
| `ImageCreative` | Standard image ad with primary asset | Display banners |
| `AspectRatioImageCreative` | Responsive image with multiple densities | Multi-device campaigns |
| `ImageRedirectCreative` | Image hosted externally | Third-party image hosting |
| `ImageOverlayCreative` | Non-linear video overlay | Video companion overlays |
| `ImageRedirectOverlayCreative` | Externally hosted overlay | Third-party overlay hosting |

### Video Creatives

| Type | Description | Use Case |
|------|-------------|----------|
| `VideoCreative` | Hosted video with transcoding | In-stream video ads |
| `VideoRedirectCreative` | Video assets hosted externally | Third-party video hosting |
| `VastRedirectCreative` | Points to external VAST XML | Programmatic video |
| `SetTopBoxCreative` | Cable/satellite video-on-demand | Set-top box delivery |

### Audio Creatives

| Type | Description | Use Case |
|------|-------------|----------|
| `AudioCreative` | Hosted audio with transcoding | Audio streaming ads |
| `AudioRedirectCreative` | Audio assets hosted externally | Third-party audio hosting |

### HTML/Code Creatives

| Type | Description | Use Case |
|------|-------------|----------|
| `CustomCreative` | Custom HTML snippet with assets | Interactive ads |
| `Html5Creative` | HTML5 bundle (zipped) | Rich media ads |
| `ThirdPartyCreative` | Third-party ad server code | External ad serving |
| `TemplateCreative` | Based on creative template | Standardized formats, native ads |

### Other Creatives

| Type | Description | Use Case |
|------|-------------|----------|
| `ProgrammaticCreative` | Programmatic-served creative | Programmatic deals |
| `AdExchangeCreative` | Google Ad Exchange | AdX integration |
| `AdSenseCreative` | Google AdSense | AdSense integration |
| `ClickTrackingCreative` | Click tracking only | Click measurement |
| `InternalRedirectCreative` | Redirect to another creative | Creative aliasing |

---

## Creative Data Models

### Creative (Base Object)

All creative types inherit from this base object.

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | xsd:long | Update | Yes | Unique identifier assigned by Google |
| `name` | xsd:string | Yes | No | Name of the creative (max 255 characters) |
| `advertiserId` | xsd:long | Yes | No | ID of the advertiser that owns the creative |
| `size` | Size | Yes | Yes* | Dimensions of the creative (*required for creation) |
| `previewUrl` | xsd:string | No | Yes | URL for previewing the creative |
| `policyLabels` | CreativePolicyViolation[] | No | Yes | Detected policy violations |
| `appliedLabels` | AppliedLabel[] | No | No | Labels applied to the creative |
| `lastModifiedDateTime` | DateTime | No | Yes | Last modification timestamp |
| `customFieldValues` | BaseCustomFieldValue[] | No | No | Custom field values |
| `thirdPartyDataDeclaration` | ThirdPartyDataDeclaration | No | No | Third-party companies associated |
| `thirdPartyDataDeclarationStatus` | enum | No | Yes | Declaration vs detection comparison |
| `adBadgingEnabled` | xsd:boolean | No | No | Whether ad badging is enabled |
| `selfDeclaredEuropeanUnionPoliticalContent` | xsd:boolean | No | No | EU political content flag (default: false) |

### HasDestinationUrlCreative Fields

Additional fields for creatives with click-through URLs.

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `destinationUrl` | xsd:string | Conditional | No | Click-through URL (max 1024 chars). Required unless type is NONE |
| `destinationUrlType` | DestinationUrlType | No | No | Type of destination (default: CLICK_TO_WEB) |

### ImageCreative

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `primaryImageAsset` | CreativeAsset | Yes | No | The primary image asset |
| `altText` | xsd:string | No | No | Alternative text for accessibility (max 500 chars) |
| `overrideSize` | xsd:boolean | No | No | Allow size to differ from asset size |
| `thirdPartyImpressionTrackingUrls` | xsd:string[] | No | No | Impression tracking URLs (max 1024 chars each) |
| `secondaryImageAssets` | CreativeAsset[] | No | No | Additional assets for different screen densities |

### AspectRatioImageCreative

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `imageAssets` | CreativeAsset[] | Yes | No | Multiple image assets for different devices |
| `altText` | xsd:string | No | No | Alternative text (max 500 chars) |
| `overrideSize` | xsd:boolean | No | No | Allow size variance from asset |
| `thirdPartyImpressionTrackingUrls` | xsd:string[] | No | No | Impression tracking URLs |

### ImageRedirectCreative

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `imageUrl` | xsd:string | Yes | No | URL where image is hosted (max 1024 chars) |
| `altText` | xsd:string | No | No | Alternative text (max 500 chars) |
| `thirdPartyImpressionTrackingUrls` | xsd:string[] | No | No | Impression tracking URLs |

### ImageOverlayCreative

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `primaryImageAsset` | CreativeAsset | Yes | No | The overlay image asset |
| `overrideSize` | xsd:boolean | No | No | Allow size variance |
| `companionCreativeIds` | xsd:long[] | No | No | Associated companion creatives |
| `trackingUrls` | ConversionEvent_TrackingUrlsMapEntry[] | No | No | Event-based tracking URLs |
| `lockedOrientation` | LockedOrientation | No | No | Display orientation constraint |
| `customParameters` | xsd:string | No | No | Key=value parameters for VAST |
| `duration` | xsd:int | No | No | Suggested duration in milliseconds |
| `vastPreviewUrl` | xsd:string | No | Yes | VAST XML preview URL |

### VideoCreative

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `videoSourceUrl` | xsd:string | Yes | No | URL of source video for transcoding |
| `duration` | xsd:int | No | No | Expected duration in milliseconds |
| `allowDurationOverride` | xsd:boolean | No | No | Allow duration variance |
| `trackingUrls` | ConversionEvent_TrackingUrlsMapEntry[] | No | No | Event tracking URLs |
| `companionCreativeIds` | xsd:long[] | No | No | Companion creative IDs |
| `customParameters` | xsd:string | No | No | VAST AdParameters (key=value format) |
| `adId` | xsd:string | No | No | Ad ID per registry type |
| `adIdType` | AdIdType | No | No | Registry type (default: NONE) |
| `skippableAdType` | SkippableAdType | No | No | Skippability setting |
| `vastPreviewUrl` | xsd:string | No | Yes | Preview ad tag URL |
| `sslScanResult` | SslScanResult | No | Yes | SSL compatibility status |
| `sslManualOverride` | SslManualOverride | No | No | Manual SSL override |

### VideoRedirectCreative

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `videoAssets` | VideoRedirectAsset[] | Yes | No | Video assets hosted externally |
| `mezzanineFile` | VideoRedirectAsset | No | No | High quality mezzanine video |
| *Inherits all BaseVideoCreative fields* |

### VastRedirectCreative

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `vastXmlUrl` | xsd:string | Yes | No | URL to third-party VAST XML |
| `vastRedirectType` | VastRedirectType | Yes | No | Type of VAST ads (LINEAR, NON_LINEAR, or both) |
| `duration` | xsd:int | Yes | No | Duration in milliseconds |
| `companionCreativeIds` | xsd:long[] | No | No | Companion creative IDs |
| `trackingUrls` | ConversionEvent_TrackingUrlsMapEntry[] | No | No | Event tracking URLs |
| `vastPreviewUrl` | xsd:string | No | Yes | Preview URL |
| `sslScanResult` | SslScanResult | No | Yes | SSL scan status |
| `sslManualOverride` | SslManualOverride | No | No | SSL override |
| `isAudio` | xsd:boolean | No | No | Whether VAST points to audio |

### SetTopBoxCreative

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `externalAssetId` | xsd:string | Yes | No | Cable system asset identifier |
| `providerId` | xsd:string | Yes | No | Cable system provider identifier |
| `availabilityRegionIds` | xsd:string[] | No | No | Regional availability identifiers |
| `licenseWindowStartDateTime` | DateTime | No | No | Start of serving window |
| `licenseWindowEndDateTime` | DateTime | No | No | End of serving window |
| *Inherits all BaseVideoCreative fields* |

### AudioCreative

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `audioSourceUrl` | xsd:string | Yes | No | URL of source audio for transcoding |
| `duration` | xsd:int | No | No | Expected duration in milliseconds |
| `allowDurationOverride` | xsd:boolean | No | No | Allow duration variance |
| `trackingUrls` | ConversionEvent_TrackingUrlsMapEntry[] | No | No | Event tracking URLs |
| `companionCreativeIds` | xsd:long[] | No | No | Companion creative IDs |
| `customParameters` | xsd:string | No | No | VAST AdParameters |
| `adId` | xsd:string | No | No | Ad ID per registry |
| `adIdType` | AdIdType | No | No | Registry type |
| `skippableAdType` | SkippableAdType | No | No | Skippability |
| `vastPreviewUrl` | xsd:string | No | Yes | Preview URL |
| `sslScanResult` | SslScanResult | No | Yes | SSL status |
| `sslManualOverride` | SslManualOverride | No | No | SSL override |

### AudioRedirectCreative

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `audioAssets` | VideoRedirectAsset[] | Yes | No | Audio assets hosted externally |
| `mezzanineFile` | VideoRedirectAsset | No | No | High quality mezzanine audio |
| *Inherits all BaseAudioCreative fields* |

### CustomCreative

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `htmlSnippet` | xsd:string | Yes | No | HTML code for the creative |
| `customCreativeAssets` | CustomCreativeAsset[] | No | No | Assets referenced by snippet |
| `isInterstitial` | xsd:boolean | No | No | Whether it's an interstitial |
| `lockedOrientation` | LockedOrientation | No | No | Display orientation |
| `sslScanResult` | SslScanResult | No | Yes | SSL compatibility |
| `sslManualOverride` | SslManualOverride | No | No | SSL override |
| `isSafeFrameCompatible` | xsd:boolean | No | No | SafeFrame compatibility (default: true) |
| `thirdPartyImpressionTrackingUrls` | xsd:string[] | No | No | Impression tracking URLs |

### Html5Creative

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `html5Asset` | CreativeAsset | Yes | No | Zipped HTML5 bundle (.zip extension required) |
| `overrideSize` | xsd:boolean | No | No | Allow size to differ from asset |
| `thirdPartyImpressionTrackingUrls` | xsd:string[] | No | No | Impression tracking URLs |
| `thirdPartyClickTrackingUrl` | xsd:string | No | No | Click tracking URL |
| `lockedOrientation` | LockedOrientation | No | No | Display orientation |
| `sslScanResult` | SslScanResult | No | Yes | SSL compatibility |
| `sslManualOverride` | SslManualOverride | No | No | SSL override |
| `isSafeFrameCompatible` | xsd:boolean | No | No | SafeFrame compatibility (default: true) |

### ThirdPartyCreative

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `snippet` | xsd:string | Yes | No | HTML/JavaScript code snippet |
| `expandedSnippet` | xsd:string | No | Yes | Macro-expanded snippet |
| `sslScanResult` | SslScanResult | No | Yes | SSL compatibility |
| `sslManualOverride` | SslManualOverride | No | No | SSL override |
| `lockedOrientation` | LockedOrientation | No | No | Display orientation |
| `isSafeFrameCompatible` | xsd:boolean | No | No | SafeFrame compatibility (default: true) |
| `thirdPartyImpressionTrackingUrls` | xsd:string[] | No | No | Impression tracking URLs |
| `ampRedirectUrl` | xsd:string | No | No | AMP creative URL |

### TemplateCreative

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `creativeTemplateId` | xsd:long | Yes | Yes* | Template ID (*required for creation, immutable after) |
| `creativeTemplateVariableValues` | CreativeTemplateVariableValue[] | No | No | Variable values for the template |
| `destinationUrl` | xsd:string | Conditional | No | Click-through URL (required if template uses click macros) |
| `isInterstitial` | xsd:boolean | No | Yes | Whether template produces interstitials |
| `isNativeEligible` | xsd:boolean | No | Yes | Whether eligible for native serving |
| `isSafeFrameCompatible` | xsd:boolean | No | Yes | SafeFrame compatibility |
| `sslScanResult` | SslScanResult | No | Yes | SSL compatibility |
| `sslManualOverride` | SslManualOverride | No | No | SSL override |
| `lockedOrientation` | LockedOrientation | No | No | Display orientation |

### ProgrammaticCreative

A creative served through programmatic channels. Contains only inherited Creative base fields - the actual creative content is determined programmatically.

### CreativeAsset

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `assetId` | xsd:long | No | Yes* | Asset ID (*auto-generated by Google) |
| `assetByteArray` | xsd:base64Binary | Conditional | No | File content (required when creating without assetId) |
| `fileName` | xsd:string | Conditional | No | File name (required when assetByteArray is provided) |
| `fileSize` | xsd:long | No | Yes | File size in bytes |
| `assetUrl` | xsd:string | No | Yes | Preview URL |
| `size` | Size | No | Yes | Asset dimensions |
| `clickTags` | ClickTag[] | No | Yes | Asset click tags |
| `imageDensity` | ImageDensity | No | No | Pixel density (default: ONE_TO_ONE) |

### Size

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `width` | xsd:int | Yes | Width in pixels (use 1 for fluid/interstitial) |
| `height` | xsd:int | Yes | Height in pixels (use 1 for fluid/interstitial) |
| `isAspectRatio` | xsd:boolean | No | Whether dimensions represent aspect ratio |

### VideoRedirectAsset

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `redirectUrl` | xsd:string | Yes | URL to the video asset |
| `size` | Size | No | Video dimensions |
| `mimeType` | xsd:string | No | MIME type of video |
| `assetDuration` | xsd:long | No | Duration in milliseconds |
| `metadata` | VideoMetadata | No | Additional video metadata |

---

## CreativeSetService

The CreativeSetService manages creative sets - groupings of a master creative with companion creatives for coordinated delivery.

### WSDL Endpoint

```
https://ads.google.com/apis/ads/publisher/v202511/CreativeSetService?wsdl
```

### Methods

#### createCreativeSet

Creates a new CreativeSet.

| Aspect | Details |
|--------|---------|
| **Parameters** | `creativeSet` (CreativeSet) - The creative set to create |
| **Returns** | CreativeSet - The created creative set with ID |
| **Required Fields** | name, masterCreativeId, companionCreativeIds |

#### getCreativeSetsByStatement

Retrieves creative sets matching a PQL query.

| Aspect | Details |
|--------|---------|
| **Parameters** | `filterStatement` (Statement) - PQL query statement |
| **Returns** | CreativeSetPage - Paginated results |

**Filterable Fields:**

| Field | Type |
|-------|------|
| `id` | xsd:long |
| `name` | xsd:string |
| `masterCreativeId` | xsd:long |
| `lastModifiedDateTime` | DateTime |

#### updateCreativeSet

Updates an existing CreativeSet.

| Aspect | Details |
|--------|---------|
| **Parameters** | `creativeSet` (CreativeSet) - The creative set to update |
| **Returns** | CreativeSet - The updated creative set |
| **Note** | Master creative cannot be changed after creation |

### CreativeSet Object

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | xsd:long | No | Yes | Unique identifier |
| `name` | xsd:string | Yes | No | Name (max 255 characters) |
| `masterCreativeId` | xsd:long | Yes | Yes* | Master creative ID (*immutable after creation) |
| `companionCreativeIds` | xsd:long[] | Yes | No | Companion creative IDs |
| `lastModifiedDateTime` | DateTime | No | Yes | Last modification timestamp |

### CreativeSet Constraints

- A master creative cannot be a companion in the same set
- A master creative can only belong to one creative set
- All creatives in a set must belong to the same advertiser
- Master creative cannot be updated after creation

---

## CreativeTemplateService

The CreativeTemplateService provides read-only access to creative templates. Templates define reusable structures for creating standardized creatives, including native ad formats.

### WSDL Endpoint

```
https://ads.google.com/apis/ads/publisher/v202511/CreativeTemplateService?wsdl
```

### Methods

#### getCreativeTemplatesByStatement

Retrieves creative templates matching a PQL query.

| Aspect | Details |
|--------|---------|
| **Parameters** | `filterStatement` (Statement) - PQL query statement |
| **Returns** | CreativeTemplatePage - Paginated results |

**Filterable Fields:**

| Field | Type |
|-------|------|
| `id` | xsd:long |
| `name` | xsd:string |
| `type` | CreativeTemplateType |
| `status` | CreativeTemplateStatus |

**Note:** This service is read-only. Templates are created and managed through the Ad Manager UI.

### CreativeTemplate Object

| Field | Type | Read-Only | Description |
|-------|------|-----------|-------------|
| `id` | xsd:long | Yes | Unique identifier |
| `name` | xsd:string | Yes | Template name (max 255 characters) |
| `description` | xsd:string | Yes | Template description |
| `variables` | CreativeTemplateVariable[] | Yes | List of template variables |
| `snippet` | xsd:string | Yes | HTML snippet with variable placeholders |
| `type` | CreativeTemplateType | Yes | SYSTEM_DEFINED or USER_DEFINED |
| `status` | CreativeTemplateStatus | Yes | ACTIVE, INACTIVE, or DELETED |
| `isInterstitial` | xsd:boolean | Yes | Whether template produces interstitials |
| `isNativeEligible` | xsd:boolean | Yes | Whether eligible for native ad serving |
| `isSafeFrameCompatible` | xsd:boolean | Yes | SafeFrame compatibility (default: true) |

### CreativeTemplateVariable Types

All variable types share these base fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `label` | xsd:string | Yes | User-facing label (max 127 characters) |
| `uniqueName` | xsd:string | No | Auto-generated identifier |
| `description` | xsd:string | Yes | Help text (max 255 characters) |
| `isRequired` | xsd:boolean | No | Whether value is required |

**Variable Subtypes:**

| Type | Description |
|------|-------------|
| `StringCreativeTemplateVariable` | Text input |
| `UrlCreativeTemplateVariable` | URL input with validation |
| `LongCreativeTemplateVariable` | Numeric input |
| `AssetCreativeTemplateVariable` | File upload (image, video, etc.) |
| `ListStringCreativeTemplateVariable` | Dropdown selection |

### System-Defined Native Templates

Common system template IDs for native ads:

| Template ID | Format Name | Description |
|-------------|-------------|-------------|
| `10004400` | App Install | Mobile app installation ads |
| `10004401` | Content | Content recommendation ads |
| `10004402` | Video App Install | Video-based app install |
| `10004403` | Video Content | Video content ads |

For native ad styling, see [NativeStyleService](./NativeStyleService.md).

---

## CreativeWrapperService

The CreativeWrapperService manages creative wrappers - HTML snippets or video tracking URLs served alongside creatives at the ad unit level.

### WSDL Endpoint

```
https://ads.google.com/apis/ads/publisher/v202511/CreativeWrapperService?wsdl
```

### Methods

#### createCreativeWrappers

Creates new CreativeWrapper objects.

| Aspect | Details |
|--------|---------|
| **Parameters** | `creativeWrappers` (CreativeWrapper[]) - Wrappers to create |
| **Returns** | CreativeWrapper[] - Created wrappers with IDs |
| **Required Fields** | labelId, ordering, and (header/footer OR videoTrackingUrls) |

#### getCreativeWrappersByStatement

Retrieves wrappers matching a PQL query.

| Aspect | Details |
|--------|---------|
| **Parameters** | `filterStatement` (Statement) - PQL query |
| **Returns** | CreativeWrapperPage - Paginated results |

**Filterable Fields:** id, labelId, status, ordering

#### updateCreativeWrappers

Updates existing CreativeWrapper objects.

| Aspect | Details |
|--------|---------|
| **Parameters** | `creativeWrappers` (CreativeWrapper[]) - Wrappers to update |
| **Returns** | CreativeWrapper[] - Updated wrappers |
| **Note** | labelId cannot be changed after creation |

#### performCreativeWrapperAction

Performs bulk actions on wrappers.

| Aspect | Details |
|--------|---------|
| **Parameters** | `action` (CreativeWrapperAction), `filterStatement` (Statement) |
| **Returns** | UpdateResult |

**Available Actions:**

| Action | xsi:type | Description |
|--------|----------|-------------|
| **Activate** | `ActivateCreativeWrappers` | Activates wrappers |
| **Deactivate** | `DeactivateCreativeWrappers` | Deactivates wrappers |

### CreativeWrapper Object

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | xsd:long | No | Yes | Unique identifier |
| `labelId` | xsd:long | Yes | Yes* | Associated label ID (*immutable after creation) |
| `creativeWrapperType` | CreativeWrapperType | Yes | No | HTML or VIDEO_TRACKING_URL |
| `htmlHeader` | xsd:string | Conditional | No | Header HTML snippet |
| `htmlFooter` | xsd:string | Conditional | No | Footer HTML snippet |
| `ampHead` | xsd:string | No | No | AMP header snippet |
| `ampBody` | xsd:string | No | No | AMP body snippet |
| `videoTrackingUrls` | ConversionEvent_TrackingUrl[] | Conditional | No | Required when type is VIDEO_TRACKING_URL |
| `thirdPartyDataDeclaration` | ThirdPartyDataDeclaration | No | No | Third-party company declaration |
| `ordering` | CreativeWrapperOrdering | Yes | No | Wrapper rendering order |
| `status` | CreativeWrapperStatus | No | Yes | ACTIVE or INACTIVE |

### Wrapper Constraints

- Must be associated with `LabelType.CREATIVE_WRAPPER` labels
- Applied to ad units via `AdUnit.appliedLabels`
- Cannot be applied to video-only ad units
- Cannot be applied to mobile ad units
- Must contain either HTML header/footer OR video tracking URLs

---

## Enumerations Reference

### DestinationUrlType

| Value | Description |
|-------|-------------|
| `CLICK_TO_WEB` | Navigate to a web page (default) |
| `CLICK_TO_APP` | Start an application |
| `CLICK_TO_CALL` | Make a phone call |
| `NONE` | No destination URL |
| `UNKNOWN` | Value not exposed by API version |

### SslScanResult

| Value | Description |
|-------|-------------|
| `UNSCANNED` | Not yet scanned |
| `SCANNED_SSL` | Scanned and SSL compatible |
| `SCANNED_NON_SSL` | Scanned and NOT SSL compatible |
| `UNKNOWN` | Value not exposed by API version |

### SslManualOverride

| Value | Description |
|-------|-------------|
| `NO_OVERRIDE` | Use scan result (default) |
| `SSL_COMPATIBLE` | Override as SSL compatible |
| `NOT_SSL_COMPATIBLE` | Override as not SSL compatible |
| `UNKNOWN` | Value not exposed by API version |

### LockedOrientation

| Value | Description |
|-------|-------------|
| `FREE_ORIENTATION` | No orientation restriction |
| `PORTRAIT_ONLY` | Portrait mode only |
| `LANDSCAPE_ONLY` | Landscape mode only |
| `UNKNOWN` | Value not exposed by API version |

### SkippableAdType

| Value | Description |
|-------|-------------|
| `DISABLED` | Not skippable |
| `ENABLED` | Skippable after delay |
| `INSTREAM_SELECT` | In-stream skippable format |
| `ANY` | Determined by buyer (programmatic) |
| `UNKNOWN` | Value not exposed by API version |

### AdIdType

| Value | Description |
|-------|-------------|
| `AD_ID` | Registered with ad-id.org |
| `CLEARCAST` | Registered with clearcast.co.uk |
| `ARPP` | Registered with ARPP Pub-ID |
| `CUSV` | Registered with Auditel Spot ID |
| `NONE` | No external ad ID (default) |
| `UNKNOWN` | Value not exposed by API version |

### VastRedirectType

| Value | Description |
|-------|-------------|
| `LINEAR` | VAST contains only linear ads |
| `NON_LINEAR` | VAST contains only non-linear ads |
| `LINEAR_AND_NON_LINEAR` | VAST contains both types |

### ImageDensity

| Value | Description |
|-------|-------------|
| `ONE_TO_ONE` | 1:1 ratio (default) |
| `THREE_TO_TWO` | 3:2 ratio (1.5x density) |
| `TWO_TO_ONE` | 2:1 ratio (2x density) |
| `UNKNOWN` | Value not exposed by API version |

### CreativeTemplateType

| Value | Description |
|-------|-------------|
| `SYSTEM_DEFINED` | Google-defined templates |
| `USER_DEFINED` | Custom templates (network-specific) |

### CreativeTemplateStatus

| Value | Description |
|-------|-------------|
| `ACTIVE` | Template is active and usable |
| `INACTIVE` | Existing creatives work, new ones cannot be created |
| `DELETED` | Template deleted, creatives cannot serve |

### CreativeWrapperType

| Value | Description |
|-------|-------------|
| `HTML` | HTML header/footer snippets |
| `VIDEO_TRACKING_URL` | Video tracking URLs |
| `UNKNOWN` | Value not exposed by API version |

### CreativeWrapperOrdering

| Value | Description |
|-------|-------------|
| `INNER` | Wraps closest to creative (first) |
| `NO_PREFERENCE` | Wraps after INNER, before OUTER |
| `OUTER` | Wraps furthest from creative (last) |

### CreativeWrapperStatus

| Value | Description |
|-------|-------------|
| `ACTIVE` | Wrapper is active and serving |
| `INACTIVE` | Wrapper is not serving |

### ConversionEvent (Video Tracking)

**Standard VAST Events:**

| Value | Description |
|-------|-------------|
| `CREATIVE_VIEW` | Creative view event |
| `START` | Video start |
| `FIRST_QUARTILE` | 25% complete |
| `MIDPOINT` | 50% complete |
| `THIRD_QUARTILE` | 75% complete |
| `COMPLETE` | 100% complete |
| `MUTE` | Video muted |
| `UNMUTE` | Video unmuted |
| `PAUSE` | Video paused |
| `RESUME` | Video resumed |
| `REWIND` | Video rewound |
| `FULLSCREEN` | Entered fullscreen |
| `EXPAND` | Creative expanded |
| `COLLAPSE` | Creative collapsed |
| `CLOSE` | Creative closed |

**Custom/Extension Events:**

| Value | Description |
|-------|-------------|
| `SKIP_SHOWN` | Skip button displayed |
| `SKIPPED` | Video was skipped |
| `ENGAGED_VIEW` | 30 seconds viewed or completion |
| `ACCEPT_INVITATION` | Invitation accepted |
| `CLICK_TRACKING` | Click tracked |
| `SURVEY` | Survey interaction |
| `CUSTOM_CLICK` | Custom click event |
| `MEASURABLE_IMPRESSION` | Measurable impression |
| `VIEWABLE_IMPRESSION` | Viewable impression |
| `VIDEO_ABANDON` | Video abandoned |
| `FULLY_VIEWABLE_AUDIBLE_HALF_DURATION_IMPRESSION` | Full viewability metric |

---

## Python Code Examples

### Setup

```python
from googleads import ad_manager

# Initialize client
client = ad_manager.AdManagerClient.LoadFromStorage()
creative_service = client.GetService('CreativeService', version='v202511')
creative_set_service = client.GetService('CreativeSetService', version='v202511')
creative_template_service = client.GetService('CreativeTemplateService', version='v202511')
creative_wrapper_service = client.GetService('CreativeWrapperService', version='v202511')
```

### Create an Image Creative

```python
def create_image_creative(advertiser_id, name, width, height, image_data, filename, destination_url):
    """Create an image creative with uploaded asset."""

    creative = {
        'xsi_type': 'ImageCreative',
        'name': name,
        'advertiserId': advertiser_id,
        'size': {
            'width': width,
            'height': height,
            'isAspectRatio': False
        },
        'destinationUrl': destination_url,
        'primaryImageAsset': {
            'assetByteArray': image_data,  # Base64 encoded
            'fileName': filename
        }
    }

    result = creative_service.createCreatives([creative])

    print(f"Created ImageCreative ID: {result[0]['id']}")
    return result[0]


# Example usage with file
import base64

with open('/path/to/banner.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

create_image_creative(
    advertiser_id=12345,
    name='Homepage Banner 300x250',
    width=300,
    height=250,
    image_data=image_data,
    filename='banner.jpg',
    destination_url='https://example.com/landing'
)
```

### Create a Third-Party Creative

```python
def create_third_party_creative(advertiser_id, name, width, height, snippet):
    """Create a third-party creative with HTML snippet."""

    creative = {
        'xsi_type': 'ThirdPartyCreative',
        'name': name,
        'advertiserId': advertiser_id,
        'size': {
            'width': width,
            'height': height,
            'isAspectRatio': False
        },
        'snippet': snippet,
        'isSafeFrameCompatible': True
    }

    result = creative_service.createCreatives([creative])

    print(f"Created ThirdPartyCreative ID: {result[0]['id']}")
    return result[0]


# Example with third-party ad tag
snippet = '''
<script type="text/javascript">
  var adTag = "https://adserver.example.com/ad?size=300x250&cb=%%CACHEBUSTER%%";
  document.write('<scr' + 'ipt src="' + adTag + '"></scr' + 'ipt>');
</script>
'''

create_third_party_creative(
    advertiser_id=12345,
    name='Third Party Display Ad',
    width=300,
    height=250,
    snippet=snippet
)
```

### Create a Video Creative

```python
def create_video_creative(advertiser_id, name, video_url, duration_ms, destination_url=None):
    """Create a video creative for transcoding."""

    creative = {
        'xsi_type': 'VideoCreative',
        'name': name,
        'advertiserId': advertiser_id,
        'size': {
            'width': 1,  # Use 1x1 for video
            'height': 1,
            'isAspectRatio': False
        },
        'videoSourceUrl': video_url,
        'duration': duration_ms,
        'allowDurationOverride': True,
        'skippableAdType': 'ENABLED'
    }

    if destination_url:
        creative['destinationUrl'] = destination_url
        creative['destinationUrlType'] = 'CLICK_TO_WEB'

    result = creative_service.createCreatives([creative])

    print(f"Created VideoCreative ID: {result[0]['id']}")
    print(f"VAST Preview URL: {result[0].get('vastPreviewUrl', 'Pending transcoding')}")
    return result[0]


create_video_creative(
    advertiser_id=12345,
    name='Pre-roll Video 30s',
    video_url='https://storage.example.com/video.mp4',
    duration_ms=30000,
    destination_url='https://example.com/landing'
)
```

### Create a VAST Redirect Creative

```python
def create_vast_redirect_creative(advertiser_id, name, vast_url, duration_ms, vast_type='LINEAR'):
    """Create a VAST redirect creative pointing to external VAST."""

    creative = {
        'xsi_type': 'VastRedirectCreative',
        'name': name,
        'advertiserId': advertiser_id,
        'size': {
            'width': 1,
            'height': 1,
            'isAspectRatio': False
        },
        'vastXmlUrl': vast_url,
        'vastRedirectType': vast_type,
        'duration': duration_ms
    }

    result = creative_service.createCreatives([creative])

    print(f"Created VastRedirectCreative ID: {result[0]['id']}")
    return result[0]


create_vast_redirect_creative(
    advertiser_id=12345,
    name='Programmatic Video VAST',
    vast_url='https://vast.example.com/vast.xml',
    duration_ms=15000,
    vast_type='LINEAR'
)
```

### Create a Template-Based Creative (Native)

```python
def create_template_creative(advertiser_id, name, template_id, variable_values):
    """Create a creative from a template (e.g., native ad)."""

    creative = {
        'xsi_type': 'TemplateCreative',
        'name': name,
        'advertiserId': advertiser_id,
        'size': {
            'width': 1,  # Native ads use 1x1
            'height': 1,
            'isAspectRatio': False
        },
        'creativeTemplateId': template_id,
        'creativeTemplateVariableValues': variable_values
    }

    result = creative_service.createCreatives([creative])

    print(f"Created TemplateCreative ID: {result[0]['id']}")
    print(f"Is Native Eligible: {result[0].get('isNativeEligible', False)}")
    return result[0]


# Example: App Install native ad
variable_values = [
    {
        'xsi_type': 'StringCreativeTemplateVariableValue',
        'uniqueName': 'Headline',
        'value': 'Download Our Amazing App'
    },
    {
        'xsi_type': 'StringCreativeTemplateVariableValue',
        'uniqueName': 'Body',
        'value': 'Experience the best mobile app for productivity.'
    },
    {
        'xsi_type': 'UrlCreativeTemplateVariableValue',
        'uniqueName': 'Image',
        'value': 'https://example.com/app-image.jpg'
    },
    {
        'xsi_type': 'StringCreativeTemplateVariableValue',
        'uniqueName': 'Calltoaction',
        'value': 'Install Now'
    }
]

create_template_creative(
    advertiser_id=12345,
    name='App Install Native Ad',
    template_id=10004400,  # System-defined App Install template
    variable_values=variable_values
)
```

### Create an HTML5 Creative

```python
def create_html5_creative(advertiser_id, name, width, height, zip_data, filename, destination_url):
    """Create an HTML5 creative from zipped bundle."""

    creative = {
        'xsi_type': 'Html5Creative',
        'name': name,
        'advertiserId': advertiser_id,
        'size': {
            'width': width,
            'height': height,
            'isAspectRatio': False
        },
        'destinationUrl': destination_url,
        'html5Asset': {
            'assetByteArray': zip_data,  # Base64 encoded .zip
            'fileName': filename
        },
        'isSafeFrameCompatible': True
    }

    result = creative_service.createCreatives([creative])

    print(f"Created Html5Creative ID: {result[0]['id']}")
    return result[0]


# Example with HTML5 zip file
import base64

with open('/path/to/html5-ad.zip', 'rb') as f:
    zip_data = base64.b64encode(f.read()).decode('utf-8')

create_html5_creative(
    advertiser_id=12345,
    name='Interactive HTML5 Banner',
    width=300,
    height=250,
    zip_data=zip_data,
    filename='html5-ad.zip',
    destination_url='https://example.com/landing'
)
```

### Query Creatives

```python
def get_creatives_by_advertiser(advertiser_id, limit=100):
    """Get all creatives for an advertiser."""

    statement = (ad_manager.StatementBuilder(version='v202511')
                 .Where('advertiserId = :advertiserId')
                 .WithBindVariable('advertiserId', advertiser_id)
                 .Limit(limit))

    all_creatives = []

    while True:
        result = creative_service.getCreativesByStatement(statement.ToStatement())

        if 'results' in result:
            all_creatives.extend(result['results'])
            statement.offset += statement.limit

            if statement.offset >= result['totalResultSetSize']:
                break
        else:
            break

    print(f"Found {len(all_creatives)} creatives for advertiser {advertiser_id}")

    for creative in all_creatives:
        print(f"  ID: {creative['id']}")
        print(f"  Name: {creative['name']}")
        print(f"  Type: {creative.get('Creative.Type', type(creative).__name__)}")
        print(f"  Size: {creative['size']['width']}x{creative['size']['height']}")
        print("---")

    return all_creatives


def get_creatives_by_size(width, height, limit=500):
    """Get creatives of a specific size."""

    statement = (ad_manager.StatementBuilder(version='v202511')
                 .Where('width = :width AND height = :height')
                 .WithBindVariable('width', width)
                 .WithBindVariable('height', height)
                 .Limit(limit))

    result = creative_service.getCreativesByStatement(statement.ToStatement())

    return result.get('results', [])
```

### Activate/Deactivate Creatives

```python
def activate_creatives(creative_ids):
    """Activate one or more creatives."""

    statement = (ad_manager.StatementBuilder(version='v202511')
                 .Where('id IN (:ids)')
                 .WithBindVariable('ids', creative_ids))

    action = {'xsi_type': 'ActivateCreatives'}

    result = creative_service.performCreativeAction(action, statement.ToStatement())

    print(f"Activated {result['numChanges']} creatives")
    return result


def deactivate_creatives(creative_ids):
    """Deactivate one or more creatives."""

    statement = (ad_manager.StatementBuilder(version='v202511')
                 .Where('id IN (:ids)')
                 .WithBindVariable('ids', creative_ids))

    action = {'xsi_type': 'DeactivateCreatives'}

    result = creative_service.performCreativeAction(action, statement.ToStatement())

    print(f"Deactivated {result['numChanges']} creatives")
    return result
```

### Create a Creative Set

```python
def create_creative_set(name, master_creative_id, companion_creative_ids):
    """Create a creative set with master and companions."""

    creative_set = {
        'name': name,
        'masterCreativeId': master_creative_id,
        'companionCreativeIds': companion_creative_ids
    }

    result = creative_set_service.createCreativeSet(creative_set)

    print(f"Created CreativeSet ID: {result['id']}")
    print(f"  Master: {result['masterCreativeId']}")
    print(f"  Companions: {result['companionCreativeIds']}")
    return result


# Example: Video with companion banners
create_creative_set(
    name='Video Campaign Creative Set',
    master_creative_id=12345,  # Video creative
    companion_creative_ids=[67890, 11111]  # Banner companions
)
```

### Query Creative Templates

```python
def get_native_eligible_templates():
    """Get all native-eligible creative templates."""

    statement = (ad_manager.StatementBuilder(version='v202511')
                 .Where("status = 'ACTIVE'")
                 .Limit(500))

    native_templates = []

    while True:
        result = creative_template_service.getCreativeTemplatesByStatement(statement.ToStatement())

        if 'results' in result:
            for template in result['results']:
                if template.get('isNativeEligible', False):
                    native_templates.append(template)

            statement.offset += statement.limit
            if statement.offset >= result['totalResultSetSize']:
                break
        else:
            break

    print(f"Found {len(native_templates)} native-eligible templates:")

    for template in native_templates:
        print(f"  ID: {template['id']}")
        print(f"  Name: {template['name']}")
        print(f"  Type: {template['type']}")
        print(f"  Variables: {len(template.get('variables', []))}")
        print("---")

    return native_templates


def get_template_by_id(template_id):
    """Get a specific creative template by ID."""

    statement = (ad_manager.StatementBuilder(version='v202511')
                 .Where('id = :id')
                 .WithBindVariable('id', template_id))

    result = creative_template_service.getCreativeTemplatesByStatement(statement.ToStatement())

    if result.get('results'):
        template = result['results'][0]
        print(f"Template: {template['name']}")
        print(f"Native Eligible: {template.get('isNativeEligible', False)}")
        print(f"Variables:")
        for var in template.get('variables', []):
            print(f"  - {var['label']} ({var.get('CreativeTemplateVariable.Type', 'unknown')})")
            print(f"    Required: {var.get('isRequired', False)}")
        return template

    return None
```

### Create a Creative Wrapper

```python
def create_html_creative_wrapper(label_id, header_html=None, footer_html=None, ordering='NO_PREFERENCE'):
    """Create an HTML creative wrapper."""

    wrapper = {
        'labelId': label_id,
        'creativeWrapperType': 'HTML',
        'ordering': ordering
    }

    if header_html:
        wrapper['htmlHeader'] = header_html
    if footer_html:
        wrapper['htmlFooter'] = footer_html

    result = creative_wrapper_service.createCreativeWrappers([wrapper])

    print(f"Created CreativeWrapper ID: {result[0]['id']}")
    return result[0]


# Example: Viewability tracking wrapper
header_html = '''
<script>
  (function() {
    var img = new Image();
    img.src = 'https://tracking.example.com/impression?cb=' + Date.now();
  })();
</script>
'''

create_html_creative_wrapper(
    label_id=12345,  # Must be CREATIVE_WRAPPER label type
    header_html=header_html,
    ordering='OUTER'
)


def create_video_tracking_wrapper(label_id, tracking_events):
    """Create a video tracking URL creative wrapper."""

    wrapper = {
        'labelId': label_id,
        'creativeWrapperType': 'VIDEO_TRACKING_URL',
        'ordering': 'NO_PREFERENCE',
        'videoTrackingUrls': [
            {'key': event, 'value': url}
            for event, url in tracking_events.items()
        ]
    }

    result = creative_wrapper_service.createCreativeWrappers([wrapper])

    print(f"Created Video Tracking Wrapper ID: {result[0]['id']}")
    return result[0]


# Example: Video event tracking
tracking_events = {
    'START': 'https://tracking.example.com/start?cb=%%CACHEBUSTER%%',
    'FIRST_QUARTILE': 'https://tracking.example.com/25?cb=%%CACHEBUSTER%%',
    'MIDPOINT': 'https://tracking.example.com/50?cb=%%CACHEBUSTER%%',
    'THIRD_QUARTILE': 'https://tracking.example.com/75?cb=%%CACHEBUSTER%%',
    'COMPLETE': 'https://tracking.example.com/complete?cb=%%CACHEBUSTER%%'
}

create_video_tracking_wrapper(
    label_id=67890,
    tracking_events=tracking_events
)
```

---

## Best Practices

### Creative Management

1. **Use descriptive names**: Include size, format, and campaign info in creative names for easy identification
2. **Set appropriate SSL compatibility**: Use SSL-compatible creatives for HTTPS sites
3. **Provide alt text**: Always include alternative text for accessibility compliance
4. **Use correct sizes**: Set 1x1 for video, audio, and native creatives

### Asset Management

1. **Optimize file sizes**: Compress images and videos to reduce load time
2. **Use appropriate formats**:
   - Images: JPG for photos, PNG for graphics with transparency
   - Video: MP4 with H.264 codec
   - HTML5: Zip with valid manifest
3. **Provide multiple densities**: Include 1x, 1.5x, and 2x assets for high-DPI displays

### Creative Sets

1. **Match advertiser**: All creatives in a set must belong to the same advertiser
2. **Plan master carefully**: Master creative cannot be changed after creation
3. **Size coordination**: Ensure companion sizes complement the master creative

### Templates

1. **Use system templates**: Prefer Google's system-defined templates for better support
2. **Validate variable values**: Ensure all required template variables are populated
3. **Test native rendering**: Verify native creatives render correctly with NativeStyles

### Wrappers

1. **Order carefully**: Use INNER for measurement, OUTER for viewability
2. **Keep snippets lightweight**: Large wrappers impact ad load time
3. **Test SSL compatibility**: Ensure wrapper content is SSL-compatible for HTTPS sites

---

## Error Handling

### CreativeError Reasons

| Reason | Description |
|--------|-------------|
| `FLASH_AND_FALLBACK_URL_ARE_SAME` | Flash URL and fallback URL cannot be identical |
| `DESTINATION_URL_NOT_EMPTY` | Destination URL must be empty when type is NONE |
| `DESTINATION_URL_TYPE_NOT_SUPPORTED` | URL type not compatible with creative type |
| `CANNOT_CREATE_OR_UPDATE_LEGACY_DFP_CREATIVE` | Legacy DFP creatives are read-only |
| `CANNOT_CREATE_OR_UPDATE_LEGACY_DFP_MOBILE_CREATIVE` | Legacy mobile creatives are read-only |
| `INVALID_COMPANY_TYPE` | Company must be Advertiser, House Advertiser, or Ad Network |
| `DUPLICATE_ASSET_IN_CREATIVE` | Assets must be unique within a creative |
| `CREATIVE_ASSET_CANNOT_HAVE_ID_AND_BYTE_ARRAY` | Cannot provide both assetId and byte array |
| `CANNOT_CREATE_OR_UPDATE_UNSUPPORTED_CREATIVE` | Unsupported creative types cannot be modified |
| `CANNOT_CREATE_PROGRAMMATIC_CREATIVES` | Programmatic creatives are auto-created |
| `INVALID_SIZE_FOR_THIRD_PARTY_IMPRESSION_TRACKER` | Size required for impression tracking |
| `CANNOT_DEACTIVATE_CREATIVES_IN_CREATIVE_SETS` | Cannot deactivate creatives in active sets |
| `HOSTED_VIDEO_CREATIVE_REQUIRES_VIDEO_ASSET` | Video creatives must have video content |
| `CANNOT_REMOVE_PLACEMENT_IDS` | Cannot remove placement IDs from direct supply creatives |

### CreativeSetError Reasons

| Reason | Description |
|--------|-------------|
| `MASTER_CREATIVE_CANNOT_BE_COMPANION` | Master cannot be companion in same set |
| `MASTER_BELONGS_TO_MULTIPLE_SETS` | Master can only belong to one set |
| `CREATIVES_MUST_BELONG_TO_SAME_ADVERTISER` | All creatives must share advertiser |
| `CANNOT_UPDATE_MASTER_CREATIVE` | Master creative is immutable |

### Example Error Handling

```python
from googleads import errors

def create_creative_safely(creative):
    """Create a creative with comprehensive error handling."""
    try:
        result = creative_service.createCreatives([creative])
        return result[0]

    except errors.GoogleAdsServerFault as e:
        for error in e.errors:
            error_type = error.get('ApiExceptionFault', {}).get('errors', [{}])[0].get('@xsi:type', '')
            reason = error.get('ApiExceptionFault', {}).get('errors', [{}])[0].get('reason', '')

            if 'CreativeError' in error_type:
                if reason == 'INVALID_COMPANY_TYPE':
                    print("Error: Advertiser company type is invalid")
                elif reason == 'DUPLICATE_ASSET_IN_CREATIVE':
                    print("Error: Duplicate assets detected in creative")
                elif reason == 'HOSTED_VIDEO_CREATIVE_REQUIRES_VIDEO_ASSET':
                    print("Error: Video creative requires a video asset")
                else:
                    print(f"CreativeError: {reason}")

            elif 'AssetError' in error_type:
                print(f"Asset Error: {reason}")

            elif 'ImageError' in error_type:
                print(f"Image Error: {reason}")

            else:
                print(f"API Error: {error_type} - {reason}")

        raise
```

---

## Related Services

| Service | Purpose |
|---------|---------|
| [NativeStyleService](./NativeStyleService.md) | Define HTML/CSS rendering for native creatives |
| `LineItemCreativeAssociationService` | Associate creatives with line items |
| `LineItemService` | Manage line items that serve creatives |
| `LabelService` | Manage labels for creative wrappers |
| `InventoryService` | Get ad unit info for wrapper targeting |
| `CompanyService` | Manage advertiser companies |

---

## Resources

- [CreativeService Reference (v202511)](https://developers.google.com/ad-manager/api/reference/v202511/CreativeService)
- [CreativeSetService Reference (v202511)](https://developers.google.com/ad-manager/api/reference/v202511/CreativeSetService)
- [CreativeTemplateService Reference (v202511)](https://developers.google.com/ad-manager/api/reference/v202511/CreativeTemplateService)
- [CreativeWrapperService Reference (v202511)](https://developers.google.com/ad-manager/api/reference/v202511/CreativeWrapperService)
- [Creative Types Overview](https://developers.google.com/ad-manager/api/creatives)
- [Native Ads Guide](https://developers.google.com/ad-manager/api/native)
- [Video Creatives Guide](https://developers.google.com/ad-manager/api/video-creatives)
- [HTML5 Creatives Guide](https://support.google.com/admanager/answer/7046799)
