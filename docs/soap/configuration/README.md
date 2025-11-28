# Google Ad Manager SOAP API v202511 - Configuration Services

**Last Updated:** 2025-11-28 (Expanded with complete field definitions)
**API Version:** v202511
**Namespace:** `https://www.google.com/apis/ads/publisher/v202511`

This document provides comprehensive reference documentation for the Configuration category of the Google Ad Manager SOAP API. These services handle network settings, CDN configuration, ads.txt management, and mobile application inventory.

---

## Table of Contents

1. [Overview](#overview)
2. [Initial Setup Guide](#initial-setup-guide)
3. [NetworkService](#networkservice)
   - [Network Object - Complete Field Reference](#network-object---complete-field-reference)
   - [ThirdPartyDataDeclaration Object](#thirdpartydatadeclaration-object)
   - [ChildPublisher Object](#childpublisher-object)
4. [CdnConfigurationService](#cdnconfigurationservice)
   - [CdnConfiguration Object - Complete Field Reference](#cdnconfiguration-object---complete-field-reference)
   - [SourceContentConfiguration Object](#sourcecontentconfiguration-object)
   - [MediaLocationSettings Object](#medialocationssettings-object)
   - [SecurityPolicySettings Object - Complete Field Reference](#securitypolicysettings-object---complete-field-reference)
5. [AdsTxtService](#adstxtservice)
   - [MCM Supply Chain Diagnostics](#mcm-supply-chain-diagnostics)
   - [Ads.txt Line Format](#adstxt-line-format)
6. [MobileApplicationService](#mobileapplicationservice)
   - [MobileApplication Object - Complete Field Reference](#mobileapplication-object---complete-field-reference)
   - [MobileApplicationStore Enum - Complete Reference](#mobileapplicationstore-enum---complete-reference)
   - [MobileApplicationPlatform Enum](#mobileapplicationplatform-enum)
   - [MobileApplication.ApprovalStatus Enum](#mobileapplicationapprovalstatus-enum)
7. [Data Models - Quick Reference](#data-models---quick-reference)
8. [Error Handling](#error-handling)
9. [Python Code Examples](#python-code-examples)
10. [Best Practices](#best-practices)

---

## Overview

The Configuration category contains four services that manage fundamental aspects of your Ad Manager network:

| Service | Purpose | Key Capabilities |
|---------|---------|------------------|
| **NetworkService** | Network configuration and access | Get network info, create test networks, update display names |
| **CdnConfigurationService** | CDN setup for DAI | Create/manage CDN configurations for Dynamic Ad Insertion |
| **AdsTxtService** | Ads.txt management | Read MCM supply chain diagnostics |
| **MobileApplicationService** | Mobile app inventory | Claim and manage mobile/CTV applications |

### Service Access Pattern

All configuration services follow the same access pattern:

```python
from googleads import ad_manager

# Initialize client
client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')

# Get service instance
network_service = client.GetService('NetworkService', version='v202511')
cdn_service = client.GetService('CdnConfigurationService', version='v202511')
ads_txt_service = client.GetService('AdsTxtService', version='v202511')
mobile_app_service = client.GetService('MobileApplicationService', version='v202511')
```

---

## Initial Setup Guide

### First-Time Configuration Steps

1. **Enable API Access**
   - Navigate to Admin > Global settings > Network settings in Ad Manager UI
   - Enable API access for your network

2. **Create Service Account**
   - Create a Google Cloud project
   - Enable the Google Ad Manager API
   - Create a service account with Ad Manager API access

3. **Configure Authentication**
   ```yaml
   # googleads.yaml
   ad_manager:
     application_name: YOUR_APPLICATION_NAME
     network_code: YOUR_NETWORK_CODE
     path_to_private_key_file: /path/to/service_account.json
   ```

4. **Verify Network Access**
   ```python
   # Test your configuration
   client = ad_manager.AdManagerClient.LoadFromStorage()
   network_service = client.GetService('NetworkService', version='v202511')
   network = network_service.getCurrentNetwork()
   print(f"Connected to: {network['displayName']} ({network['networkCode']})")
   ```

5. **Create Test Network (Optional)**
   - Use `makeTestNetwork()` for development without affecting production
   - Note: Test networks cannot serve ads or generate reports with data

---

## NetworkService

**WSDL:** `https://ads.google.com/apis/ads/publisher/v202511/NetworkService?wsdl`

Provides operations for retrieving and managing network configuration. Essential for multi-network access scenarios and initial API setup.

### Methods

#### getAllNetworks

Returns all Network objects accessible to the current login. Use this without a network code in the SOAP header when the login has access to multiple networks.

```
getAllNetworks() -> Network[]
```

**Parameters:** None

**Returns:** `Network[]` - Array of all accessible networks

**Use Case:** When a single set of credentials has access to multiple Ad Manager networks (e.g., agency accounts). Intended to be used without a network code in the SOAP header when the login may have more than one network.

---

#### getCurrentNetwork

Returns the network for which requests are being made based on the network code in the SOAP header.

```
getCurrentNetwork() -> Network
```

**Parameters:** None

**Returns:** `Network` - The current network object

**Use Case:** Retrieve full network details including timezone, currency, and effective root ad unit.

---

#### getDefaultThirdPartyDataDeclaration

Returns the default third-party data declaration for the network.

```
getDefaultThirdPartyDataDeclaration() -> ThirdPartyDataDeclaration
```

**Parameters:** None

**Returns:** `ThirdPartyDataDeclaration` - Default declaration settings (empty if never configured)

**Use Case:** Check network-level default settings for third-party data declarations on creatives.

---

#### makeTestNetwork

Creates a new blank test network for development purposes.

```
makeTestNetwork() -> Network
```

**Parameters:** None

**Returns:** `Network` - The newly created test network

**Limitations:**
- Only one test network per login (email address)
- Test networks cannot serve ads
- Reports will always return no data (no traffic history)
- Limited to 10,000 objects per entity type
- No data transfer from existing networks
- Forecasting produces simulated results only
- No Ad Manager 360 features by default

**Use Case:** Development and testing without affecting production data.

---

#### updateNetwork

Updates network settings. Currently limited to the display name.

```
updateNetwork(network: Network) -> Network
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `network` | `Network` | Yes | Network object with updated fields |

**Returns:** `Network` - The updated network

**Updatable Fields:**
- `displayName` - The network's display name
- `secondaryCurrencyCodes` - Alternate currencies (where supported)

**Note:** Currently only the display name can be modified through the API.

---

### Network Object - Complete Field Reference

The Network object represents an Ad Manager network with all its configuration and metadata.

| Field | Type | Read-Only | Description |
|-------|------|-----------|-------------|
| `id` | `xsd:long` | Yes | The unique ID of the Network. Assigned by Google. |
| `displayName` | `xsd:string` | No | The display name of the network. |
| `networkCode` | `xsd:string` | Yes | The network code. Required in SOAP headers if login has access to multiple networks. |
| `propertyCode` | `xsd:string` | Yes | The property code for the publisher. |
| `timeZone` | `xsd:string` | Yes | The time zone associated with delivery of orders and reporting (e.g., "America/New_York"). |
| `currencyCode` | `xsd:string` | Yes | The primary currency code (e.g., "USD"). |
| `secondaryCurrencyCodes` | `xsd:string[]` | No | Currencies usable as alternatives to primary currency for trafficking line items. |
| `effectiveRootAdUnitId` | `xsd:string` | Yes | The AdUnit.id of the top most ad unit to which descendant ad units can be added. |
| `isTest` | `xsd:boolean` | Yes | Whether this is a test network. |

### Network Settings Reference (Summary)

| Setting | Configurable | Description |
|---------|--------------|-------------|
| Display Name | Yes | Human-readable network name |
| Secondary Currencies | Yes | Additional currencies for line items |
| Network Code | No | Unique network identifier |
| Property Code | No | Publisher property identifier |
| Time Zone | No | Delivery and reporting timezone |
| Primary Currency | No | Default currency for transactions |
| Is Test | No | Whether this is a test network |

---

### ThirdPartyDataDeclaration Object

Represents a set of declarations about what (if any) third party companies are associated with a given creative. Can be configured at the network level as a default for all creatives or customized per individual creative.

| Field | Type | Description |
|-------|------|-------------|
| `declarationType` | `DeclarationType` | Type of declaration (see enum values below) |
| `thirdPartyCompanyIds` | `xsd:long[]` | Array of RichMediaAdsCompany IDs associated with the entity |

#### DeclarationType Enum

| Value | Description |
|-------|-------------|
| `NONE` | No companies are associated. Functions identically to `DECLARED` with an empty company list. |
| `DECLARED` | A specific set of RichMediaAdsCompany associations are declared. |
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |

---

### ChildPublisher Object

Represents a network being managed as part of Multiple Customer Management (MCM). Used in CompanyService for managing parent-child network relationships.

| Field | Type | Read-Only | Description |
|-------|------|-----------|-------------|
| `approvedDelegationType` | `DelegationType` | Yes | Type of delegation the parent has been approved to have over the child. Set to `proposedDelegationType` value upon approval by the child network. Null if parent not yet approved. |
| `proposedDelegationType` | `DelegationType` | No | Type of delegation the parent has proposed to have over the child, pending approval. |
| `invitationStatus` | `InvitationStatus` | Yes | Invitation status of the delegation relationship between parent and child. |
| `accountStatus` | `AccountStatus` | Yes | Status reflecting the child publisher's Ad Manager account based on their status and Google's policy verification. |
| `childNetworkCode` | `xsd:string` | No | Network code of the child network. |
| `sellerId` | `xsd:string` | No | Child publisher's seller ID from parent's sellers.json file. Only applicable for Manage Inventory delegations. |
| `proposedRevenueShareMillipercent` | `xsd:long` | Yes (for updates) | Proposed revenue share percentage in millipercentage (0-100000, where 100000 = 100%). |
| `onboardingTasks` | `OnboardingTask[]` | Yes | Pending onboarding tasks. Only populated when AccountStatus is `PENDING_GOOGLE_APPROVAL`. |

#### DelegationType Enum

| Value | Description |
|-------|-------------|
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |
| `MANAGE_ACCOUNT` | The parent network gets complete access to the child network's account. |
| `MANAGE_INVENTORY` | A subset of the ad requests from the child are delegated to the parent, determined by the tag on the child network's web pages. The parent network does not have access to the child network's account. |

#### InvitationStatus Enum

| Value | Description |
|-------|-------------|
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |
| `ACCEPTED` | The invitation has been accepted by the child publisher. |
| `EXPIRED` | The invitation has expired without a response. |
| `PENDING` | The invitation is pending a response from the child publisher. |
| `REJECTED` | The invitation was rejected by the child publisher. |
| `WITHDRAWN` | The invitation was withdrawn by the parent publisher. |
| `DEACTIVATED_BY_AD_MANAGER` | The relationship has been deactivated by Ad Manager. |

#### AccountStatus Enum

| Value | Description |
|-------|-------------|
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |
| `INVITED` | The child publisher has been invited. |
| `DECLINED` | The child publisher declined the invitation. |
| `PENDING_GOOGLE_APPROVAL` | The relationship is pending Google's approval. |
| `APPROVED` | The relationship has been approved and is active. |
| `CLOSED_POLICY_VIOLATION` | The account was closed due to policy violation. |
| `CLOSED_INVALID_ACTIVITY` | The account was closed due to invalid activity. |
| `CLOSED_BY_PUBLISHER` | The account was closed by the publisher. |
| `DISAPPROVED_INELIGIBLE` | The account was disapproved due to ineligibility. |
| `DISAPPROVED_DUPLICATE_ACCOUNT` | The account was disapproved as a duplicate. |
| `EXPIRED` | The invitation or relationship has expired. |
| `INACTIVE` | The relationship is inactive. |
| `DEACTIVATED_BY_AD_MANAGER` | The relationship was deactivated by Ad Manager. |

#### OnboardingTask Enum

| Value | Description |
|-------|-------------|
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |
| `BILLING_PROFILE_CREATION` | Billing profile needs to be created. |
| `PHONE_PIN_VERIFICATION` | Phone PIN verification is required. |
| `AD_MANAGER_ACCOUNT_SETUP` | Ad Manager account setup is required. |

---

## CdnConfigurationService

**WSDL:** `https://ads.google.com/apis/ads/publisher/v202511/CdnConfigurationService?wsdl`

Manages Content Delivery Network configurations for Dynamic Ad Insertion (DAI). CDN configurations define how content is ingested from origin servers and delivered to end users.

### Methods

#### createCdnConfigurations

Creates new CDN configurations.

```
createCdnConfigurations(cdnConfigurations: CdnConfiguration[]) -> CdnConfiguration[]
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cdnConfigurations` | `CdnConfiguration[]` | Yes | Array of configurations to create |

**Returns:** `CdnConfiguration[]` - The created configurations with assigned IDs

---

#### getCdnConfigurationsByStatement

Retrieves CDN configurations matching the specified criteria.

```
getCdnConfigurationsByStatement(statement: Statement) -> CdnConfigurationPage
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `statement` | `Statement` | Yes | PQL filter statement |

**Filterable Fields:**
| Field | PQL Type | Description |
|-------|----------|-------------|
| `id` | `Number` | Unique configuration ID |
| `name` | `String` | Configuration name |

**Returns:** `CdnConfigurationPage` - Paginated results

**Note:** Currently only returns configurations of type `LIVE_STREAM_SOURCE_CONTENT`.

---

#### updateCdnConfigurations

Updates existing CDN configurations.

```
updateCdnConfigurations(cdnConfigurations: CdnConfiguration[]) -> CdnConfiguration[]
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cdnConfigurations` | `CdnConfiguration[]` | Yes | Array of configurations to update |

**Returns:** `CdnConfiguration[]` - The updated configurations

---

#### performCdnConfigurationAction

Performs actions on CDN configurations matching a filter.

```
performCdnConfigurationAction(
    cdnConfigurationAction: CdnConfigurationAction,
    filterStatement: Statement
) -> UpdateResult
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cdnConfigurationAction` | `CdnConfigurationAction` | Yes | Action to perform |
| `filterStatement` | `Statement` | Yes | Filter for target configurations |

**Returns:** `UpdateResult` - Number of rows affected

**Available Actions:**

| Action | Description |
|--------|-------------|
| `ActivateCdnConfigurations` | Activates CDN configurations, making them available for use |
| `ArchiveCdnConfigurations` | Archives CDN configurations, removing them from active use |

**Archive Restrictions:**
- Cannot archive if used by active content sources
- Cannot archive if used by active live streams

---

### CDN Configuration Workflow

1. **Define Ingest Settings** - How DAI fetches content from your origin
2. **Define Delivery Settings** - How DAI serves content to users
3. **Configure Security** - Authentication for both ingest and delivery
4. **Activate Configuration** - Make available for live streams

---

### CdnConfiguration Object - Complete Field Reference

A CdnConfiguration encapsulates information about where and how to ingest and deliver content enabled for DAI (Dynamic Ad Insertion).

| Field | Type | Read-Only | Required | Description |
|-------|------|-----------|----------|-------------|
| `id` | `xsd:long` | Yes | No | The unique ID of the CdnConfiguration. Assigned by Google. |
| `name` | `xsd:string` | No | Yes | The name of the CdnConfiguration. Maximum length of 255 characters. |
| `cdnConfigurationType` | `CdnConfigurationType` | No | Yes | The type of CDN configuration represented by this CdnConfiguration. |
| `sourceContentConfiguration` | `SourceContentConfiguration` | No | Yes | Parameters for how this configuration sources content, enabling content retrieval and delivery as part of modified streams. |
| `cdnConfigurationStatus` | `CdnConfigurationStatus` | Yes | No | The status of the CDN configuration. |

#### CdnConfigurationType Enum

| Value | Description |
|-------|-------------|
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |
| `LIVE_STREAM_SOURCE_CONTENT` | A configuration that specifies where and how LiveStreamEvent content should be ingested and delivered. |

#### CdnConfigurationStatus Enum

| Value | Description |
|-------|-------------|
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |
| `ACTIVE` | The CDN configuration is in use and available for live streams. |
| `ARCHIVED` | The CDN configuration is no longer used. |

---

### SourceContentConfiguration Object

Defines how DAI handles content ingestion and delivery. Contains settings for both ingest (fetching from origin) and delivery (serving to users).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ingestSettings` | `MediaLocationSettings` | Yes | Configuration for how DAI should ingest media. At ingest time, the URL prefix of media in a stream's playlist is matched with an ingest location and the corresponding authentication credentials are used to download the media. |
| `defaultDeliverySettings` | `MediaLocationSettings` | Yes | Default configuration for how DAI should deliver the non-modified media segments. At delivery time, the ingest location's URL prefix is replaced with the delivery location's URL prefix, and the security policy from the delivery settings determines how DAI delivers the media. |

---

### MediaLocationSettings Object

Links a media location with security settings. Used to configure both ingest and delivery endpoints.

| Field | Type | Read-Only | Required | Description |
|-------|------|-----------|----------|-------------|
| `name` | `xsd:string` | Yes | No | The name of the media location. Assigned by Google. |
| `urlPrefix` | `xsd:string` | No | Yes | The URL prefix of the media location (e.g., "origin.example.com/content"). Should not include the scheme (http:// or https://). |
| `securityPolicy` | `SecurityPolicySettings` | No | Yes | The security policy and authentication credentials needed to access the content in this media location. |

---

### SecurityPolicySettings Object - Complete Field Reference

Security and authentication configuration for CDN access. The `securityPolicyType` determines which other fields should be populated.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `securityPolicyType` | `SecurityPolicyType` | Yes | Type of security policy. Determines which other fields should be populated. |
| `tokenAuthenticationKey` | `xsd:string` | No | Shared security key used to generate the Akamai HMAC token for authenticating requests. Only applicable when `securityPolicyType` is `AKAMAI`. |
| `disableServerSideUrlSigning` | `xsd:boolean` | No | Controls whether segment URLs are signed using the authentication key on the server. When true, disables server-side URL signing. |
| `originForwardingType` | `OriginForwardingType` | No | Specifies origin forwarding method for Akamai authentication on master playlists. |
| `originPathPrefix` | `xsd:string` | No | The origin path prefix provided by the publisher for the master playlist. Used when `originForwardingType` is `CONVENTIONAL`. |
| `mediaPlaylistOriginForwardingType` | `OriginForwardingType` | No | Origin forwarding type for media playlists in live stream configurations. |
| `mediaPlaylistOriginPathPrefix` | `xsd:string` | No | The origin path prefix provided by the publisher for the media playlists. Used when `mediaPlaylistOriginForwardingType` is `CONVENTIONAL`. |
| `keysetName` | `xsd:string` | No | The name of the EdgeCacheKeyset on the Media CDN configuration for validating signed requests. Only applicable when `securityPolicyType` is `CLOUD_MEDIA`. |
| `signedRequestExpirationTtlSeconds` | `xsd:long` | No | Duration in seconds for request validity when using short tokens. |

#### SecurityPolicyType Enum

| Value | Description |
|-------|-------------|
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |
| `NONE` | Indicates that no authentication is necessary. Use for open/public content. |
| `AKAMAI` | Security policy for accessing content on the Akamai CDN. Requires `tokenAuthenticationKey` and origin forwarding settings. |
| `CLOUD_MEDIA` | Security policy for accessing content on Google Cloud Media CDN. Requires `keysetName` configuration. |

#### OriginForwardingType Enum

| Value | Description |
|-------|-------------|
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |
| `ORIGIN_PATH` | Indicates that origin forwarding is set up by passing an originpath query string parameter (necessary for Akamai dynamic packaging to work). |
| `CONVENTIONAL` | Indicates that conventional origin forwarding is used. Requires setting `originPathPrefix` or `mediaPlaylistOriginPathPrefix`. |
| `NONE` | Indicates that origin forwarding is not being used. |

---

## AdsTxtService

**WSDL:** `https://ads.google.com/apis/ads/publisher/v202511/AdsTxtService?wsdl`

**Namespace:** `https://www.google.com/apis/ads/publisher/v202511`

Provides methods for retrieving AdsTxt objects and access to Multiple Customer Management (MCM) supply chain diagnostics for ads.txt compliance.

### Methods

#### getMcmSupplyChainDiagnosticsDownloadUrl

Returns a download URL String for the MCM Manage Inventory SupplyChain diagnostics report.

```
getMcmSupplyChainDiagnosticsDownloadUrl() -> String
```

**Parameters:** None (no input fields required)

**Returns:** `xsd:string` - URL to download the diagnostics report

**Report Details:**
- **Refresh Frequency:** Refreshed twice daily
- **Content:** Contains supply chain diagnostic information for MCM relationships
- **Format:** CSV file with diagnostic entries
- **Purpose:** Used for MCM inventory management compliance

**Possible Errors:**
| Error Type | Description |
|------------|-------------|
| `ApiVersionError` | API version mismatch |
| `AuthenticationError` | Invalid or missing credentials |
| `CommonError` | General API error |
| `FeatureError` | Feature not enabled for the network |
| `InternalApiError` | Internal server error |
| `PermissionError` | Insufficient permissions |
| `ServerError` | Server-side error |

**Use Case:** Programmatically access ads.txt/app-ads.txt diagnostic information for MCM relationships. Automate monitoring and alerting for supply chain issues.

---

### Understanding Ads.txt

**ads.txt** (Authorized Digital Sellers) helps prevent unauthorized inventory sales:

- **ads.txt** - For web inventory (placed at domain root, e.g., `example.com/ads.txt`)
- **app-ads.txt** - For mobile app inventory (linked in app store listing)

#### Ads.txt Line Format

Each line in an ads.txt file follows this format:
```
<exchange domain>, <publisher ID>, <account type>, [certification authority ID]
```

Example:
```
google.com, pub-1234567890123456, DIRECT, f08c47fec0942fa0
```

#### MCM Supply Chain Diagnostics

The MCM supply chain diagnostics report helps identify:
- Missing or incorrect ads.txt entries
- Supply chain authorization issues
- MCM relationship configuration problems
- Inventory authorization gaps
- Seller ID mismatches

#### Report Content Fields

The downloaded CSV report typically includes:
| Field | Description |
|-------|-------------|
| Domain/App | The domain or app identifier |
| Issue Type | Type of ads.txt issue detected |
| Expected Entry | The expected ads.txt line |
| Status | Current authorization status |
| Child Network | The child publisher network code |
| Recommendation | Suggested action to resolve |

---

## MobileApplicationService

**WSDL:** `https://ads.google.com/apis/ads/publisher/v202511/MobileApplicationService?wsdl`

**Namespace:** `https://www.google.com/apis/ads/publisher/v202511`

Manages mobile and Connected TV (CTV) applications for targeting purposes. A MobileApplication is a mobile application that has been added to or "claimed" by the network to be used for targeting purposes. These mobile apps can come from various app stores.

### Methods

#### createMobileApplications

Creates and claims mobile applications to be used for targeting in the network.

```
createMobileApplications(mobileApplications: MobileApplication[]) -> MobileApplication[]
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mobileApplications` | `MobileApplication[]` | Yes | Applications to create/claim |

**Required Fields for Creation:**
- `displayName` - Application display name (max 255 characters)
- `appStoreId` - The app store ID to claim (read-only after creation)
- `appStores` - Array of stores the app belongs to (mutable to allow for third party app store linking)

**Returns:** `MobileApplication[]` - The created applications with assigned IDs

---

#### getMobileApplicationsByStatement

Retrieves a MobileApplicationPage of mobile applications matching the specified criteria.

```
getMobileApplicationsByStatement(filterStatement: Statement) -> MobileApplicationPage
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filterStatement` | `Statement` | Yes | PQL filter statement |

**Filterable Fields:**
| Field | PQL Type | Description |
|-------|----------|-------------|
| `id` | `Number` | Unique application ID |
| `displayName` | `String` | Application display name |
| `appStore` | `String` | App store enum value |
| `mobileApplicationExternalId` | `String` | External app store ID (alternative to `appStoreId`) |
| `isArchived` | `Boolean` | Archival status |

**Returns:** `MobileApplicationPage` - Paginated results with matching applications

---

#### updateMobileApplications

Updates specified mobile application records.

```
updateMobileApplications(mobileApplications: MobileApplication[]) -> MobileApplication[]
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mobileApplications` | `MobileApplication[]` | Yes | Applications to update |

**Returns:** `MobileApplication[]` - The updated applications

---

#### performMobileApplicationAction

Executes state-change operations on mobile applications matching the specified filter.

```
performMobileApplicationAction(
    mobileApplicationAction: MobileApplicationAction,
    filterStatement: Statement
) -> UpdateResult
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mobileApplicationAction` | `MobileApplicationAction` | Yes | Action to perform |
| `filterStatement` | `Statement` | Yes | Filter for target applications |

**Returns:** `UpdateResult` - Number of rows affected

**Available Actions:**

| Action | Description |
|--------|-------------|
| `ArchiveMobileApplications` | Marks applications as archived, removing them from active targeting. |
| `UnarchiveMobileApplications` | Restores previously archived applications to active status. |

---

### MobileApplication Object - Complete Field Reference

A MobileApplication represents a mobile or CTV application that has been claimed by the network for targeting purposes.

| Field | Type | Read-Only | Required | Description |
|-------|------|-----------|----------|-------------|
| `id` | `xsd:long` | Yes | No | Uniquely identifies the mobile application. Assigned by Google when a mobile application is claimed. **Deprecated:** Use `applicationId` instead. |
| `applicationId` | `xsd:long` | Yes | No | Alternative identifier space replacing the deprecated `id` field. |
| `displayName` | `xsd:string` | No | Yes | The display name of the mobile application. Maximum length of 255 characters. |
| `appStoreId` | `xsd:string` | Yes (after creation) | Yes | The app store ID of the app to claim. Required for creation, then becomes read-only. |
| `appStores` | `MobileApplicationStore[]` | No | Yes | The app stores the mobile application belongs to. Required for creation and mutable to allow for third party app store linking. |
| `isArchived` | `xsd:boolean` | Yes | No | The archival status of the mobile application. |
| `appStoreName` | `xsd:string` | Yes | No | The name of the application as it appears in the app store. Populated automatically by Google. |
| `applicationCode` | `xsd:string` | Yes | No | The SDK identifier for the application. The UI refers to this as "App ID". |
| `developerName` | `xsd:string` | Yes | No | The name of the developer or publisher. Populated automatically by Google. |
| `platform` | `MobileApplicationPlatform` | Yes | No | The device platform the application runs on. Populated automatically by Google. |
| `isFree` | `xsd:boolean` | Yes | No | Whether the application is free on the app store. |
| `downloadUrl` | `xsd:string` | Yes | No | The app store download URL. Populated automatically by Google. |
| `approvalStatus` | `MobileApplication.ApprovalStatus` | Yes | No | The approval status indicating advertising eligibility. |

---

### MobileApplicationStore Enum - Complete Reference

Defines all supported app stores for mobile and CTV applications.

#### Mobile App Stores

| Enum Value | Platform | Description |
|------------|----------|-------------|
| `APPLE_ITUNES` | iOS | Apple App Store |
| `GOOGLE_PLAY` | Android | Google Play Store |
| `AMAZON_APP_STORE` | Android | Amazon Appstore |
| `OPPO_APP_STORE` | Android | OPPO App Market |
| `SAMSUNG_APP_STORE` | Android | Samsung Galaxy Store (also `SAMSUNG_GALAXY_STORE`) |
| `VIVO_APP_STORE` | Android | VIVO App Store |
| `XIAOMI_APP_STORE` | Android | Xiaomi GetApps (also `XIAOMI_MI_APP_STORE`) |

#### CTV App Stores

| Enum Value | Platform | Description |
|------------|----------|-------------|
| `ROKU` | CTV | Roku Channel Store |
| `AMAZON_FIRETV` | CTV | Amazon Fire TV |
| `PLAYSTATION` | CTV | PlayStation Store |
| `XBOX` | CTV | Xbox Store |
| `SAMSUNG_TV` | CTV | Samsung Smart TV |
| `LG_TV` | CTV | LG Content Store |

#### Special Values

| Enum Value | Description |
|------------|-------------|
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |

---

### MobileApplicationPlatform Enum

Defines the device platforms that mobile applications can run on.

| Value | Description |
|-------|-------------|
| `UNKNOWN` | The value returned if the actual value is not exposed by the requested API version. |
| `ANDROID` | Android mobile platform |
| `IOS` | iOS mobile platform |
| `ROKU` | Roku CTV platform |
| `AMAZON_FIRETV` | Amazon Fire TV platform |
| `PLAYSTATION` | PlayStation gaming platform |
| `XBOX` | Xbox gaming platform |
| `SAMSUNG_TV` | Samsung Smart TV platform |
| `LG_TV` | LG Smart TV platform |

---

### MobileApplication.ApprovalStatus Enum

Represents the approval status of a mobile application for advertising eligibility.

| Value | Description |
|-------|-------------|
| `UNKNOWN` | Unknown approval status. |
| `DRAFT` | The application is not yet ready for review. |
| `UNCHECKED` | The application has not yet been reviewed. |
| `APPROVED` | The application can serve ads. |
| `DISAPPROVED` | The application failed approval checks and cannot serve any ads. |
| `APPEALING` | The application is disapproved but has a pending review status, signaling an appeal. |

---

### ArchiveStatus Reference

For understanding the archival state of mobile applications:

| Status | Description |
|--------|-------------|
| Active (`isArchived = false`) | The application is available for targeting in line items and ad rules. |
| Archived (`isArchived = true`) | The application is archived and not available for new targeting. Existing references remain intact. |

---

## Data Models - Quick Reference

This section provides a quick reference summary of the main data models. For complete field documentation including all enum values and detailed descriptions, see the corresponding service sections above.

### Network (Quick Reference)

| Field | Type | Writable | Description |
|-------|------|----------|-------------|
| `id` | `xsd:long` | No | Unique network ID |
| `displayName` | `xsd:string` | Yes | Human-readable network name |
| `networkCode` | `xsd:string` | No | Unique identifier for SOAP headers |
| `propertyCode` | `xsd:string` | No | Publisher property identifier |
| `timeZone` | `xsd:string` | No | Timezone (e.g., "America/New_York") |
| `currencyCode` | `xsd:string` | No | Primary currency code (e.g., "USD") |
| `secondaryCurrencyCodes` | `xsd:string[]` | Yes | Alternate currencies |
| `effectiveRootAdUnitId` | `xsd:string` | No | Top-level ad unit ID |
| `isTest` | `xsd:boolean` | No | Whether this is a test network |

See [Network Object - Complete Field Reference](#network-object---complete-field-reference) for full documentation.

---

### CdnConfiguration (Quick Reference)

| Field | Type | Writable | Description |
|-------|------|----------|-------------|
| `id` | `xsd:long` | No | Unique configuration ID |
| `name` | `xsd:string` | Yes | Configuration name (max 255 chars) |
| `cdnConfigurationType` | `CdnConfigurationType` | Yes | Type: `LIVE_STREAM_SOURCE_CONTENT` |
| `sourceContentConfiguration` | `SourceContentConfiguration` | Yes | Ingest and delivery settings |
| `cdnConfigurationStatus` | `CdnConfigurationStatus` | No | Status: `ACTIVE` or `ARCHIVED` |

See [CdnConfiguration Object - Complete Field Reference](#cdnconfiguration-object---complete-field-reference) for full documentation including `SourceContentConfiguration`, `MediaLocationSettings`, and `SecurityPolicySettings`.

---

### MobileApplication (Quick Reference)

| Field | Type | Writable | Description |
|-------|------|----------|-------------|
| `id` | `xsd:long` | No | Unique ID (deprecated) |
| `applicationId` | `xsd:long` | No | New identifier space |
| `displayName` | `xsd:string` | Yes | Display name (max 255 chars) |
| `appStoreId` | `xsd:string` | No (after creation) | External app store ID |
| `appStores` | `MobileApplicationStore[]` | Yes | App stores the app belongs to |
| `isArchived` | `xsd:boolean` | No | Whether archived |
| `platform` | `MobileApplicationPlatform` | No | Platform (ANDROID, IOS, ROKU, etc.) |
| `approvalStatus` | `ApprovalStatus` | No | Ad serving approval status |

See [MobileApplication Object - Complete Field Reference](#mobileapplication-object---complete-field-reference) for full documentation including all enum values.

---

## Error Handling

### Common Errors Across Services

| Error Type | Description |
|------------|-------------|
| `AuthenticationError` | Invalid or expired credentials |
| `PermissionError` | Insufficient permissions for operation |
| `QuotaError` | API quota exceeded |
| `ServerError` | Internal server error |
| `InternalApiError` | Internal API processing error |
| `RequiredError` | Required field missing |
| `NotNullError` | Null value not allowed |
| `StringLengthError` | String exceeds maximum length |

### CdnConfigurationService Errors

| Reason | Description |
|--------|-------------|
| `URL_SHOULD_NOT_CONTAIN_SCHEME` | URL prefix should not include http:// or https:// |
| `INVALID_DELIVERY_LOCATION_NAMES` | Delivery location names are invalid |
| `CANNOT_ARCHIVE_IF_USED_BY_ACTIVE_CONTENT_SOURCES` | Configuration in use by content sources |
| `CANNOT_ARCHIVE_IF_USED_BY_ACTIVE_LIVE_STREAMS` | Configuration in use by live streams |
| `UNSUPPORTED_SECURITY_POLICY_TYPE` | Security policy type not supported |

### MobileApplicationService Errors

| Reason | Description |
|--------|-------------|
| `INVALID_APP_ID` | App store ID is invalid |
| `APP_STORE_CONFLICT` | App already claimed by another network |
| `INVALID_DISPLAY_NAME` | Display name doesn't meet requirements |
| `INVALID_STATUS_TRANSITION` | Action not valid for current status |

---

## Python Code Examples

### Getting Network Information

```python
from googleads import ad_manager


def get_network_info():
    """Retrieve and display current network information."""
    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    network_service = client.GetService('NetworkService', version='v202511')

    # Get current network
    network = network_service.getCurrentNetwork()

    print("Network Information:")
    print(f"  ID: {network['id']}")
    print(f"  Display Name: {network['displayName']}")
    print(f"  Network Code: {network['networkCode']}")
    print(f"  Property Code: {network['propertyCode']}")
    print(f"  Time Zone: {network['timeZone']}")
    print(f"  Currency: {network['currencyCode']}")
    print(f"  Is Test: {network['isTest']}")
    print(f"  Root Ad Unit: {network['effectiveRootAdUnitId']}")

    if 'secondaryCurrencyCodes' in network:
        print(f"  Secondary Currencies: {', '.join(network['secondaryCurrencyCodes'])}")

    return network


def get_all_accessible_networks():
    """List all networks accessible to the current login."""
    # Note: Remove network_code from googleads.yaml for this call
    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    network_service = client.GetService('NetworkService', version='v202511')

    networks = network_service.getAllNetworks()

    print(f"Found {len(networks)} accessible networks:")
    for net in networks:
        print(f"  - {net['displayName']} ({net['networkCode']})")

    return networks


if __name__ == '__main__':
    get_network_info()
```

---

### Creating a Test Network

```python
from googleads import ad_manager


def create_test_network():
    """Create a test network for development."""
    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    network_service = client.GetService('NetworkService', version='v202511')

    try:
        test_network = network_service.makeTestNetwork()

        print("Test network created successfully!")
        print(f"  Network Code: {test_network['networkCode']}")
        print(f"  Display Name: {test_network['displayName']}")
        print("")
        print("Important notes:")
        print("  - Only one test network per login")
        print("  - Test networks cannot serve ads")
        print("  - Reports will return no data")
        print("  - Limited to 10,000 objects per entity")

        return test_network

    except Exception as e:
        if 'TEST_NETWORK_ALREADY_EXISTS' in str(e):
            print("Error: A test network already exists for this login.")
        else:
            raise


def update_network_name(new_name):
    """Update the network's display name."""
    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    network_service = client.GetService('NetworkService', version='v202511')

    # Get current network
    network = network_service.getCurrentNetwork()

    # Update display name
    network['displayName'] = new_name

    # Apply update
    updated_network = network_service.updateNetwork(network)

    print(f"Network name updated to: {updated_network['displayName']}")
    return updated_network


if __name__ == '__main__':
    create_test_network()
```

---

### Setting Up CDN Configurations

```python
from googleads import ad_manager


def create_cdn_configuration(name, ingest_url_prefix, delivery_url_prefix):
    """Create a CDN configuration for DAI live streaming."""
    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    cdn_service = client.GetService('CdnConfigurationService', version='v202511')

    cdn_config = {
        'name': name,
        'cdnConfigurationType': 'LIVE_STREAM_SOURCE_CONTENT',
        'sourceContentConfiguration': {
            'ingestSettings': {
                'urlPrefix': ingest_url_prefix,
                'securityPolicy': {
                    'securityPolicyType': 'NONE'
                }
            },
            'defaultDeliverySettings': {
                'urlPrefix': delivery_url_prefix,
                'securityPolicy': {
                    'securityPolicyType': 'NONE'
                }
            }
        }
    }

    result = cdn_service.createCdnConfigurations([cdn_config])

    created = result[0]
    print(f"CDN Configuration created:")
    print(f"  ID: {created['id']}")
    print(f"  Name: {created['name']}")
    print(f"  Status: {created['cdnConfigurationStatus']}")

    return created


def create_cdn_with_akamai_auth(name, ingest_url_prefix, delivery_url_prefix,
                                 ingest_token_key, delivery_token_key):
    """Create a CDN configuration with Akamai authentication."""
    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    cdn_service = client.GetService('CdnConfigurationService', version='v202511')

    cdn_config = {
        'name': name,
        'cdnConfigurationType': 'LIVE_STREAM_SOURCE_CONTENT',
        'sourceContentConfiguration': {
            'ingestSettings': {
                'urlPrefix': ingest_url_prefix,
                'securityPolicy': {
                    'securityPolicyType': 'AKAMAI',
                    'tokenAuthenticationKey': ingest_token_key,
                    'disableServerSideUrlSigning': False
                }
            },
            'defaultDeliverySettings': {
                'urlPrefix': delivery_url_prefix,
                'securityPolicy': {
                    'securityPolicyType': 'AKAMAI',
                    'tokenAuthenticationKey': delivery_token_key,
                    'originForwardingType': 'CONVENTIONAL',
                    'originPathPrefix': '/origin'
                }
            }
        }
    }

    result = cdn_service.createCdnConfigurations([cdn_config])
    print(f"CDN Configuration with Akamai auth created: {result[0]['id']}")
    return result[0]


def get_cdn_configurations():
    """Retrieve all CDN configurations."""
    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    cdn_service = client.GetService('CdnConfigurationService', version='v202511')

    statement = ad_manager.StatementBuilder(version='v202511')

    cdn_configs = []
    while True:
        response = cdn_service.getCdnConfigurationsByStatement(
            statement.ToStatement()
        )

        if 'results' in response and len(response['results']) > 0:
            for config in response['results']:
                print(f"CDN Config: {config['name']} (ID: {config['id']}, Status: {config['cdnConfigurationStatus']})")
                cdn_configs.extend(response['results'])
            statement.offset += statement.limit
        else:
            break

    print(f"Total CDN configurations: {len(cdn_configs)}")
    return cdn_configs


def archive_cdn_configuration(cdn_config_id):
    """Archive a CDN configuration."""
    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    cdn_service = client.GetService('CdnConfigurationService', version='v202511')

    statement = (ad_manager.StatementBuilder(version='v202511')
                 .Where('id = :id')
                 .WithBindVariable('id', cdn_config_id))

    result = cdn_service.performCdnConfigurationAction(
        {'xsi_type': 'ArchiveCdnConfigurations'},
        statement.ToStatement()
    )

    print(f"Archived {result['numChanges']} CDN configuration(s)")
    return result


if __name__ == '__main__':
    # Create a simple CDN configuration
    create_cdn_configuration(
        name='My CDN Config',
        ingest_url_prefix='origin.example.com/content',
        delivery_url_prefix='cdn.example.com/content'
    )
```

---

### Reading Ads.txt Entries

```python
from googleads import ad_manager
import requests


def get_mcm_diagnostics_report():
    """Download and display MCM supply chain diagnostics."""
    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    ads_txt_service = client.GetService('AdsTxtService', version='v202511')

    # Get download URL
    download_url = ads_txt_service.getMcmSupplyChainDiagnosticsDownloadUrl()

    print(f"Diagnostics Report URL: {download_url}")
    print("Note: Report is refreshed twice daily")

    # Download the report
    response = requests.get(download_url)

    if response.status_code == 200:
        # Save report to file
        with open('mcm_diagnostics.csv', 'wb') as f:
            f.write(response.content)
        print("Report saved to mcm_diagnostics.csv")

        # Display first few lines
        lines = response.text.split('\n')[:10]
        print("\nReport preview:")
        for line in lines:
            print(f"  {line}")
    else:
        print(f"Error downloading report: {response.status_code}")

    return download_url


if __name__ == '__main__':
    get_mcm_diagnostics_report()
```

---

### Managing Mobile Applications

```python
from googleads import ad_manager


def claim_mobile_application(display_name, app_store_id, app_stores):
    """Claim a mobile application for the network."""
    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    mobile_service = client.GetService('MobileApplicationService', version='v202511')

    mobile_app = {
        'displayName': display_name,
        'appStoreId': app_store_id,
        'appStores': app_stores  # e.g., ['GOOGLE_PLAY'] or ['APPLE_ITUNES']
    }

    result = mobile_service.createMobileApplications([mobile_app])

    created = result[0]
    print(f"Mobile application claimed:")
    print(f"  ID: {created['id']}")
    print(f"  Display Name: {created['displayName']}")
    print(f"  App Store ID: {created['appStoreId']}")
    print(f"  Platform: {created.get('platform', 'N/A')}")
    print(f"  Application Code: {created.get('applicationCode', 'N/A')}")

    return created


def claim_android_app(display_name, package_name):
    """Claim an Android app from Google Play."""
    return claim_mobile_application(
        display_name=display_name,
        app_store_id=package_name,  # e.g., 'com.example.myapp'
        app_stores=['GOOGLE_PLAY']
    )


def claim_ios_app(display_name, apple_id):
    """Claim an iOS app from the App Store."""
    return claim_mobile_application(
        display_name=display_name,
        app_store_id=apple_id,  # e.g., '123456789'
        app_stores=['APPLE_ITUNES']
    )


def claim_roku_app(display_name, channel_id):
    """Claim a Roku channel."""
    return claim_mobile_application(
        display_name=display_name,
        app_store_id=channel_id,
        app_stores=['ROKU']
    )


def get_mobile_applications(page_size=100):
    """Retrieve all mobile applications."""
    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    mobile_service = client.GetService('MobileApplicationService', version='v202511')

    statement = (ad_manager.StatementBuilder(version='v202511')
                 .Limit(page_size))

    all_apps = []
    while True:
        response = mobile_service.getMobileApplicationsByStatement(
            statement.ToStatement()
        )

        if 'results' in response and len(response['results']) > 0:
            for app in response['results']:
                status = 'Archived' if app.get('isArchived', False) else 'Active'
                print(f"App: {app['displayName']} (ID: {app['id']}, Platform: {app.get('platform', 'N/A')}, Status: {status})")
            all_apps.extend(response['results'])
            statement.offset += statement.limit
        else:
            break

    print(f"\nTotal mobile applications: {len(all_apps)}")
    return all_apps


def get_apps_by_platform(platform):
    """Retrieve mobile applications filtered by platform."""
    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    mobile_service = client.GetService('MobileApplicationService', version='v202511')

    # Note: Filter by appStore, not platform
    statement = (ad_manager.StatementBuilder(version='v202511')
                 .Where('appStore = :appStore')
                 .WithBindVariable('appStore', platform))

    response = mobile_service.getMobileApplicationsByStatement(
        statement.ToStatement()
    )

    apps = response.get('results', [])
    print(f"Found {len(apps)} {platform} applications")
    return apps


def archive_mobile_application(app_id):
    """Archive a mobile application."""
    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    mobile_service = client.GetService('MobileApplicationService', version='v202511')

    statement = (ad_manager.StatementBuilder(version='v202511')
                 .Where('id = :id')
                 .WithBindVariable('id', app_id))

    result = mobile_service.performMobileApplicationAction(
        {'xsi_type': 'ArchiveMobileApplications'},
        statement.ToStatement()
    )

    print(f"Archived {result['numChanges']} application(s)")
    return result


def unarchive_mobile_application(app_id):
    """Restore an archived mobile application."""
    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    mobile_service = client.GetService('MobileApplicationService', version='v202511')

    statement = (ad_manager.StatementBuilder(version='v202511')
                 .Where('id = :id')
                 .WithBindVariable('id', app_id))

    result = mobile_service.performMobileApplicationAction(
        {'xsi_type': 'UnarchiveMobileApplications'},
        statement.ToStatement()
    )

    print(f"Unarchived {result['numChanges']} application(s)")
    return result


if __name__ == '__main__':
    # List all mobile applications
    get_mobile_applications()

    # Example: Claim an Android app
    # claim_android_app('My Android App', 'com.example.myapp')

    # Example: Claim an iOS app
    # claim_ios_app('My iOS App', '123456789')

    # Example: Get all Roku apps
    # get_apps_by_platform('ROKU')
```

---

### Third-Party Data Declaration

```python
from googleads import ad_manager


def get_default_third_party_declaration():
    """Retrieve the network's default third-party data declaration."""
    client = ad_manager.AdManagerClient.LoadFromStorage('googleads.yaml')
    network_service = client.GetService('NetworkService', version='v202511')

    declaration = network_service.getDefaultThirdPartyDataDeclaration()

    if declaration:
        print("Default Third-Party Data Declaration:")
        print(f"  Declaration Type: {declaration.get('declarationType', 'Not set')}")

        company_ids = declaration.get('thirdPartyCompanyIds', [])
        if company_ids:
            print(f"  Associated Companies: {company_ids}")
        else:
            print("  No companies declared")
    else:
        print("No default third-party data declaration configured")

    return declaration


if __name__ == '__main__':
    get_default_third_party_declaration()
```

---

## Best Practices

### Network Configuration

1. **Use Test Networks for Development**
   - Create test networks using `makeTestNetwork()` for safe experimentation
   - Remember that test networks cannot serve ads or generate meaningful reports

2. **Multi-Network Access**
   - When managing multiple networks, use `getAllNetworks()` to discover accessible networks
   - Always specify the correct `networkCode` in your SOAP headers

3. **Keep Display Names Meaningful**
   - Use descriptive names that help identify the network's purpose
   - Update names when network usage changes

### CDN Configuration

1. **Start with NONE Security**
   - Begin with `securityPolicyType: NONE` to verify connectivity
   - Add authentication after confirming basic functionality

2. **Use Separate Configurations**
   - Create separate CDN configurations for different content types
   - This allows independent lifecycle management

3. **Test Before Activation**
   - Verify ingest and delivery URLs are correct before activating
   - Test with non-production content first

### Mobile Applications

1. **Consistent Naming**
   - Use consistent `displayName` values across platforms
   - Include platform identifier in names when managing many apps

2. **Batch Operations**
   - Claim multiple applications in a single API call
   - Use batch updates to minimize API calls

3. **Regular Audits**
   - Periodically review claimed applications
   - Archive applications no longer in use

### Ads.txt Management

1. **Regular Monitoring**
   - Download the MCM diagnostics report regularly
   - Address any authorization issues promptly

2. **Automation**
   - Set up automated downloads of the diagnostics report
   - Create alerts for supply chain issues

---

## Additional Resources

- [Google Ad Manager API Getting Started](https://developers.google.com/ad-manager/api/start)
- [API Reference Documentation](https://developers.google.com/ad-manager/api/reference/v202511)
- [Python Client Library](https://github.com/googleads/googleads-python-lib)
- [Ad Manager Help Center](https://support.google.com/admanager)
- [Create CDN Configurations](https://support.google.com/admanager/answer/7294300)
- [Mobile Apps Overview](https://support.google.com/admanager/answer/6238688)
- [Link App to App Store](https://support.google.com/admanager/answer/12636955)

---

*This documentation is based on Google Ad Manager SOAP API v202511. For the most current information, please refer to the official Google documentation.*
