# Google Ad Manager SOAP API v202511 - Ad Rules & Video

This documentation covers the Ad Rules and Video services for managing video ad monetization, Dynamic Ad Insertion (DAI), live streaming, and video ad break configurations.

**API Version:** v202511
**Namespace:** `https://www.google.com/apis/ads/publisher/v202511`
**WSDL Base:** `https://ads.google.com/apis/ads/publisher/v202511/`

---

## Table of Contents

1. [Overview](#overview)
2. [Ad Rules Concepts](#ad-rules-concepts)
3. [Services Reference](#services-reference)
   - [AdRuleService](#adruleservice)
   - [LiveStreamEventService](#livestreameventservice)
   - [DaiEncodingProfileService](#daiencodingprofileservice)
   - [DaiAuthenticationKeyService](#daiauthenticationkeyservice)
   - [StreamActivityMonitorService](#streamactivitymonitorservice)
4. [Data Models](#data-models)
   - [AdRule](#adrule)
   - [BaseAdRuleSlot](#baseadruleslot)
   - [AdSpot](#adspot)
   - [BreakTemplate](#breaktemplate)
   - [LiveStreamEvent](#livestreamevent)
   - [DaiEncodingProfile](#daiencodingprofile)
   - [DaiAuthenticationKey](#daiauthenticationkey)
   - [SamSession](#samsession)
5. [Enumerations Reference](#enumerations-reference)
6. [Break Templates](#break-templates)
7. [DAI Configuration](#dai-configuration)
8. [Actions Reference](#actions-reference)
9. [Python Code Examples](#python-code-examples)
10. [Video Ad Patterns](#video-ad-patterns)
11. [Troubleshooting](#troubleshooting)

---

## Overview

### What Are Ad Rules?

Ad rules contain data that the ad server uses to generate a playlist of video ads. They define when, where, and how many ads appear within video content. Ad rules are essential for:

- Controlling ad placement within video streams
- Setting frequency caps to limit ad exposure
- Targeting specific content or audiences
- Configuring pre-roll, mid-roll, and post-roll ad breaks

### Video Monetization in Google Ad Manager

Video monetization involves serving ads within video content through:

1. **Linear Video Ads** - Play before, during, or after video content
2. **Non-linear Overlays** - Display over video content without interrupting playback
3. **Companion Ads** - Display alongside video player

### Dynamic Ad Insertion (DAI)

DAI enables server-side ad insertion for live streams and video-on-demand content. Benefits include:

- **Seamless Ad Experience** - No buffering between content and ads
- **Ad Blocker Resistance** - Ads are stitched into the stream server-side
- **Consistent Quality** - Ads are transcoded to match content quality
- **Real-time Decisioning** - Personalized ad selection per viewer

**Note:** DAI features require Google Ad Manager 360.

---

## Ad Rules Concepts

### Ad Break Types

| Type | Description | Typical Duration |
|------|-------------|------------------|
| **Pre-roll** | Plays before content starts | 15-30 seconds |
| **Mid-roll** | Plays during content | 30-90 seconds |
| **Post-roll** | Plays after content ends | 15-30 seconds |

### Ad Pods

An ad pod is a group of ads that play sequentially within a single ad break. Pods are defined by:

- **Maximum ads per pod** - Limits the number of ads
- **Maximum duration** - Total time allowed for all ads
- **Ad spot configuration** - Defines constraints for each position

### Frequency Capping

Controls how often ads appear to prevent viewer fatigue:

| Setting | Description |
|---------|-------------|
| `TURN_ON` | Enable frequency caps with specified limits |
| `TURN_OFF` | Disable frequency caps entirely |
| `DEFER` | Use line item frequency cap settings |

### Targeting

Ad rules can target specific:

- **Content categories** - By video genre or topic
- **Geography** - By country, region, or metro area
- **Device type** - Desktop, mobile, tablet, CTV
- **Time of day** - Schedule ad rules for specific hours
- **Custom criteria** - Any custom targeting keys/values

---

## Services Reference

### AdRuleService

Provides methods for creating, updating, and retrieving AdRule, AdSpot, and BreakTemplate objects.

**WSDL:** `https://ads.google.com/apis/ads/publisher/v202511/AdRuleService?wsdl`

#### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `createAdRules` | `adRules: AdRule[]` | `AdRule[]` | Creates new AdRule objects |
| `getAdRulesByStatement` | `statement: Statement` | `AdRulePage` | Retrieves AdRules matching filter criteria |
| `updateAdRules` | `adRules: AdRule[]` | `AdRule[]` | Updates existing AdRule objects |
| `performAdRuleAction` | `action: AdRuleAction, filterStatement: Statement` | `UpdateResult` | Performs actions on matching AdRules |
| `createAdSpots` | `adSpots: AdSpot[]` | `AdSpot[]` | Creates new AdSpot objects |
| `getAdSpotsByStatement` | `filterStatement: Statement` | `AdSpotPage` | Retrieves AdSpots matching filter criteria |
| `updateAdSpots` | `adSpots: AdSpot[]` | `AdSpot[]` | Updates existing AdSpot objects |
| `createBreakTemplates` | `breakTemplate: BreakTemplate[]` | `BreakTemplate[]` | Creates new BreakTemplate objects |
| `getBreakTemplatesByStatement` | `filterStatement: Statement` | `BreakTemplatePage` | Retrieves BreakTemplates matching filter criteria |
| `updateBreakTemplates` | `breakTemplate: BreakTemplate[]` | `BreakTemplate[]` | Updates existing BreakTemplate objects |

#### Filterable Fields

For `getAdRulesByStatement`:

| Field | Supported Operators |
|-------|---------------------|
| `id` | =, != |
| `name` | =, !=, LIKE |
| `priority` | =, !=, <, <=, >, >= |
| `status` | =, != |

---

### LiveStreamEventService

Manages LiveStreamEvent objects for enabling Dynamic Ad Insertion into live video streams.

**WSDL:** `https://ads.google.com/apis/ads/publisher/v202511/LiveStreamEventService?wsdl`

**Note:** This service is only available for Ad Manager 360 networks.

#### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `createLiveStreamEvents` | `liveStreamEvents: LiveStreamEvent[]` | `LiveStreamEvent[]` | Creates new LiveStreamEvent objects |
| `getLiveStreamEventsByStatement` | `statement: Statement` | `LiveStreamEventPage` | Retrieves LiveStreamEvents matching filter criteria |
| `updateLiveStreamEvents` | `liveStreamEvents: LiveStreamEvent[]` | `LiveStreamEvent[]` | Updates existing LiveStreamEvent objects |
| `performLiveStreamEventAction` | `action: LiveStreamEventAction, filterStatement: Statement` | `UpdateResult` | Performs actions on matching LiveStreamEvents |
| `createSlates` | `slates: Slate[]` | `Slate[]` | Creates new Slate objects |
| `getSlatesByStatement` | `statement: Statement` | `SlatePage` | Retrieves Slates matching filter criteria |
| `updateSlates` | `slates: Slate[]` | `Slate[]` | Updates existing Slate objects |
| `performSlateAction` | `action: SlateAction, filterStatement: Statement` | `UpdateResult` | Performs actions on matching Slates |

---

### DaiEncodingProfileService

Manages encoding profiles for Dynamic Ad Insertion. DAI uses profile information to select appropriate ad transcodes.

**WSDL:** `https://ads.google.com/apis/ads/publisher/v202511/DaiEncodingProfileService?wsdl`

#### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `createDaiEncodingProfiles` | `daiEncodingProfiles: DaiEncodingProfile[]` | `DaiEncodingProfile[]` | Creates new encoding profiles |
| `getDaiEncodingProfilesByStatement` | `statement: Statement` | `DaiEncodingProfilePage` | Retrieves profiles matching filter criteria |
| `updateDaiEncodingProfiles` | `daiEncodingProfiles: DaiEncodingProfile[]` | `DaiEncodingProfile[]` | Updates existing encoding profiles |
| `performDaiEncodingProfileAction` | `action: DaiEncodingProfileAction, filterStatement: Statement` | `UpdateResult` | Performs actions on matching profiles |

---

### DaiAuthenticationKeyService

Manages authentication keys for securing DAI stream requests.

**WSDL:** `https://ads.google.com/apis/ads/publisher/v202511/DaiAuthenticationKeyService?wsdl`

#### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `createDaiAuthenticationKeys` | `daiAuthenticationKeys: DaiAuthenticationKey[]` | `DaiAuthenticationKey[]` | Creates new authentication keys |
| `getDaiAuthenticationKeysByStatement` | `statement: Statement` | `DaiAuthenticationKeyPage` | Retrieves keys matching filter criteria |
| `performDaiAuthenticationKeyAction` | `action: DaiAuthenticationKeyAction, filterStatement: Statement` | `UpdateResult` | Performs actions on matching keys |

**Note:** Authentication keys cannot be updated after creation; use `performDaiAuthenticationKeyAction` to activate/deactivate.

---

### StreamActivityMonitorService

Provides monitoring and debugging information for DAI sessions.

**WSDL:** `https://ads.google.com/apis/ads/publisher/v202511/StreamActivityMonitorService?wsdl`

#### Methods

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `getSamSessionsByStatement` | `statement: Statement` | `SamSessionPage` | Returns logging information for DAI sessions |
| `registerSessionsForMonitoring` | `sessionIds: string[]` | `string[]` | Registers session IDs for monitoring |

**Important Notes:**
- Session IDs must be registered via `registerSessionsForMonitoring` before they can be queried
- There may be a delay before session data is available
- Maximum of 25 sessions can be requested at once
- Supports filtering by `sessionId` and `debugKey` properties

---

## Data Models

### AdRule

Contains data that the ad server uses to generate a playlist of video ads.

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | `xsd:long` | No | Yes | Unique ID assigned by Google |
| `name` | `xsd:string` | Yes | No | Unique name (max 255 characters) |
| `priority` | `xsd:int` | Yes | No | Priority from 1-1000 (1 = highest) |
| `targeting` | `Targeting` | Yes | No | Targeting criteria for the ad rule |
| `startDateTime` | `DateTime` | Yes | No | Start date/time (must be future for new rules) |
| `startDateTimeType` | `StartDateTimeType` | No | No | How start time is specified (default: `USE_START_DATE_TIME`) |
| `endDateTime` | `DateTime` | Conditional | No | End date/time (required unless `unlimitedEndDateTime` is true) |
| `unlimitedEndDateTime` | `xsd:boolean` | No | No | If true, rule has no end date (default: false) |
| `status` | `AdRuleStatus` | No | Yes | Current status (default: `INACTIVE`) |
| `frequencyCapBehavior` | `FrequencyCapBehavior` | No | No | Frequency cap handling (default: `DEFER`) |
| `maxImpressionsPerLineItemPerStream` | `xsd:int` | No | No | Max impressions per line item per stream (default: 0) |
| `maxImpressionsPerLineItemPerPod` | `xsd:int` | No | No | Max impressions per line item per pod (default: 0) |
| `preroll` | `BaseAdRuleSlot` | Yes | No | Pre-roll slot configuration |
| `midroll` | `BaseAdRuleSlot` | Yes | No | Mid-roll slot configuration |
| `postroll` | `BaseAdRuleSlot` | Yes | No | Post-roll slot configuration |

---

### BaseAdRuleSlot

Base configuration for ad rule slots (pre-roll, mid-roll, post-roll). Extended by `StandardPoddingAdRuleSlot` and `OptimizedPoddingAdRuleSlot`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `slotBehavior` | `AdRuleSlotBehavior` | No | Whether to show ads in this slot (default: `DEFER`) |
| `maxVideoAdDuration` | `xsd:long` | No | Maximum duration for individual video ads in milliseconds (default: 0) |
| `videoMidrollFrequencyType` | `MidrollFrequencyType` | Yes (mid-roll) | How mid-roll frequency is determined |
| `videoMidrollFrequency` | `xsd:string` | Yes (mid-roll) | Frequency value based on type (seconds, cue points, etc.) |
| `bumper` | `AdRuleSlotBumper` | No | Bumper ad placement (default: `NONE`) |
| `maxBumperDuration` | `xsd:long` | No | Maximum bumper duration in milliseconds (default: 0) |
| `maxPodDuration` | `xsd:long` | No | Maximum total pod duration in milliseconds (default: 0) |
| `maxAdsInPod` | `xsd:int` | No | Maximum number of ads in the pod (default: 0) |
| `breakTemplateId` | `xsd:long` | No | Break template ID (OptimizedPoddingAdRuleSlot only) |

---

### AdSpot

A targetable entity used in the creation of AdRule objects. Contains constraints on ads that can appear.

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | `xsd:long` | No | Yes | Unique ID assigned by Google |
| `name` | `xsd:string` | Yes (custom) | No | Case-insensitive identifier for ad tags |
| `displayName` | `xsd:string` | No | No | Descriptive name (optional for custom spots) |
| `customSpot` | `xsd:boolean` | No | No | Whether this is a custom spot (default: false) |
| `flexible` | `xsd:boolean` | No | No | Permits unlimited ad counts when true (default: false) |
| `maxDurationMillis` | `xsd:long` | No | No | Maximum total duration in milliseconds (default: 0) |
| `maxNumberOfAds` | `xsd:int` | No | No | Maximum ads allowed (0 = no limit for flexible spots) |
| `targetingType` | `AdSpotTargetingType` | Yes | No | How the spot can be targeted |
| `backfillBlocked` | `xsd:boolean` | No | No | Whether backfill is blocked (default: false) |
| `allowedLineItemTypes` | `LineItemType[]` | No | No | Allowed line item types (empty = all allowed) |
| `inventorySharingBlocked` | `xsd:boolean` | No | No | Whether inventory sharing is blocked (default: false) |

#### Name Restrictions

The `name` field cannot contain: `"`, `'`, `=`, `!`, `+`, `#`, `*`, `~`, `;`, `^`, `(`, `)`, `<`, `>`, `[`, `]`, or whitespace.

---

### BreakTemplate

Defines what kinds of ads show at which positions within a pod.

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | `xsd:long` | No | Yes | Unique ID assigned by Google |
| `customTemplate` | `xsd:boolean` | No | No | Whether this is a custom template created outside ad rule workflow |
| `name` | `xsd:string` | Yes | No | Template name (case-insensitive, referenceable in ad tags) |
| `displayName` | `xsd:string` | No | No | Display name for the template |
| `breakTemplateMembers` | `BreakTemplateMember[]` | Yes | No | List of ad spots in order of appearance |

**Note:** A break template must have exactly one ad spot with `flexible = true`.

#### BreakTemplateMember

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `adSpotId` | `xsd:long` | Yes | ID of the AdSpot for this position |
| `adSpotFillType` | `AdSpotFillType` | Yes | How the spot should be filled |

---

### LiveStreamEvent

Encapsulates all information necessary to enable DAI into a live video stream.

#### Core Fields

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | `xsd:long` | No | Yes | Unique ID assigned by Google |
| `name` | `xsd:string` | Yes | No | Event name (max 255 characters) |
| `status` | `LiveStreamEventStatus` | No | Yes | Current status (created in `PAUSED` state) |
| `creationDateTime` | `DateTime` | No | Yes | When the event was created |
| `lastModifiedDateTime` | `DateTime` | No | Yes | When the event was last modified |

#### Scheduling Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `startDateTime` | `DateTime` | Conditional | Required if `startDateTimeType` is `USE_START_DATE_TIME` |
| `startDateTimeType` | `StartDateTimeType` | No | Controls when the event starts |
| `endDateTime` | `DateTime` | Conditional | Required unless `unlimitedEndDateTime` is true |
| `unlimitedEndDateTime` | `xsd:boolean` | No | If true, event has no end date (default: false) |

#### Content & Ad Configuration

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contentUrls` | `xsd:string[]` | Yes | CDN URLs for the live stream content |
| `adTags` | `xsd:string[]` | Yes | Master ad tag URLs |
| `assetKey` | `xsd:string` | No | Generated by Google (read-only) |
| `customAssetKey` | `xsd:string` | No | Immutable; max 64 alphanumeric chars (pod serving only) |

#### Ad Break & Serving Configuration

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `adBreakFillType` | `AdBreakFillType` | No | Fill type: `SLATE`, `UNDERLYING_CONTENT`, `MINIMIZE_SLATE` |
| `underfillAdBreakFillType` | `AdBreakFillType` | No | Fill behavior for incomplete ad breaks |
| `adHolidayDuration` | `xsd:long` | No | Seconds to skip mid-roll decisioning |
| `enableMaxFillerDuration` | `xsd:boolean` | No | Controls max filler duration feature |
| `maxFillerDuration` | `xsd:long` | No | Max seconds for ad pod filling |
| `defaultAdBreakDuration` | `xsd:long` | No | Duration for durationless ad breaks |
| `enableDurationlessAdBreaks` | `xsd:boolean` | No | Enables durationless ad breaks |
| `adServingFormat` | `AdServingFormat` | No | `AD_MANAGER_DAI` or `DIRECT` |

#### Streaming & Format Settings

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `dynamicAdInsertionType` | `DynamicAdInsertionType` | No | DAI type: `LINEAR`, `POD_SERVING_REDIRECT`, `POD_SERVING_MANIFEST` |
| `streamingFormat` | `StreamingFormat` | No | `HLS` or `DASH` (immutable after creation) |
| `dvrWindowSeconds` | `xsd:int` | No | DVR window length (uses encoder default if unset) |
| `podServingSegmentDuration` | `xsd:long` | No | Duration for ad stitching in pod serving |
| `enableRelativePlaylistDelivery` | `xsd:boolean` | No | Allow relative URLs in playlists |

#### Encoding & Authentication

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `daiEncodingProfileIds` | `xsd:long[]` | No | Pod serving profiles (can add but not remove) |
| `enableDaiAuthenticationKeys` | `xsd:boolean` | No | Enable DAI auth via IMA SDK |
| `streamCreateDaiAuthenticationKeyIds` | `xsd:long[]` | No | Auth keys for stream creation |
| `segmentUrlAuthenticationKeyIds` | `xsd:long[]` | No | Auth keys for ad segment URLs |

#### Advanced Features

| Field | Type | Description |
|-------|------|-------------|
| `totalEstimatedConcurrentUsers` | `xsd:long` | Expected concurrent viewers (default: 0) |
| `slateCreativeId` | `xsd:long` | Slate ID (uses network default if unset) |
| `sourceContentConfigurationIds` | `xsd:long[]` | CDN configuration IDs |
| `prerollSettings` | `PrerollSettings` | Optional preroll configuration |
| `hlsSettings` | `HlsSettings` | HLS-specific settings |
| `prefetchEnabled` | `xsd:boolean` | Enable ad request prefetching |
| `prefetchSettings` | `PrefetchSettings` | Prefetch configuration details |
| `enableAllowlistedIps` | `xsd:boolean` | Restrict to allowlisted IPs |
| `enableForceCloseAdBreaks` | `xsd:boolean` | Force-close breaks without #EXT-CUE-IN |
| `enableShortSegmentDropping` | `xsd:boolean` | Drop <1 second segments at pod end |
| `liveStreamConditioning` | `LiveStreamConditioning` | Conditioning settings |

#### Ad Break Markup Configuration

| Field | Type | Description |
|-------|------|-------------|
| `adBreakMarkups` | `AdBreakMarkupType[]` | Recognized marker formats |
| `adBreakMarkupTypesEnabled` | `xsd:boolean` | Enable specific markup subset |

#### HlsSettings

| Field | Type | Description |
|-------|------|-------------|
| `playlistType` | `PlaylistType` | Playlist type: `EVENT`, `LIVE` (default), `UNKNOWN`. Immutable after creation. |
| `masterPlaylistSettings` | `MasterPlaylistSettings` | Master playlist behavior settings |

#### PrefetchSettings

| Field | Type | Description |
|-------|------|-------------|
| `initialAdRequestDurationSeconds` | `xsd:int` | Duration of the part of the break to be prefetched |

#### LiveStreamConditioning

| Field | Type | Description |
|-------|------|-------------|
| `dashBridge` | `DashBridge` | DASH Bridge single-period to multi-period MPD conditioning |

---

### DaiEncodingProfile

Contains data about a publisher's encoding profiles for DAI ad transcode selection.

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | `xsd:long` | No | Yes | Unique ID assigned by Google |
| `name` | `xsd:string` | Yes | No | Profile name (max 64 chars, alphanumeric) |
| `status` | `DaiEncodingProfileStatus` | No | No | `ACTIVE`, `ARCHIVED`, or `UNKNOWN` (modifiable only via action) |
| `variantType` | `VariantType` | Yes | No | Playlist type: `MEDIA`, `IFRAME`, `SUBTITLES` |
| `containerType` | `ContainerType` | Conditional | No | Container: `TS`, `FMP4`, `HLS_AUDIO` (required for MEDIA/IFRAME) |
| `videoSettings` | `VideoSettings` | Conditional | No | Video configuration (required when media contains video) |
| `audioSettings` | `AudioSettings` | Conditional | No | Audio configuration (required when media contains audio) |

#### Name Restrictions

Cannot contain: `"`, `'`, `=`, `!`, `+`, `#`, `*`, `~`, `;`, `^`, `(`, `)`, `<`, `>`, `[`, `]`, or whitespace.

#### VideoSettings

| Field | Type | Description |
|-------|------|-------------|
| `codec` | `xsd:string` | RFC6381 codec string (e.g., "avc1.64001f" for H.264) |
| `bitrate` | `xsd:long` | Bitrate in bits per second (32kbps - 250 Mbps) |
| `framesPerSecond` | `xsd:double` | Frames per second (truncated to 3 decimal places) |
| `resolution` | `Size` | Video resolution in pixels (width x height) |

#### AudioSettings

| Field | Type | Description |
|-------|------|-------------|
| `codec` | `xsd:string` | RFC6381 codec string (e.g., "mp4a.40.2" for AAC) |
| `bitrate` | `xsd:long` | Bitrate in bits per second (8kbps - 250 Mbps) |
| `channels` | `xsd:long` | Number of audio channels including low frequency (max 8) |
| `sampleRateHertz` | `xsd:long` | Sample rate in hertz (44kHz - 100kHz) |

---

### DaiAuthenticationKey

Used to authenticate stream requests to the IMA SDK API.

| Field | Type | Required | Read-Only | Description |
|-------|------|----------|-----------|-------------|
| `id` | `xsd:long` | No | Yes | Unique ID assigned by Google |
| `name` | `xsd:string` | Yes | No | Label for the authentication key |
| `key` | `xsd:string` | No | Yes | The secure key value (assigned by Google, shown only at creation) |
| `keyType` | `DaiAuthenticationKeyType` | Yes | No | `API` or `HMAC` |
| `status` | `DaiAuthenticationKeyStatus` | No | No | `ACTIVE`, `INACTIVE`, or `UNKNOWN` |
| `creationDateTime` | `DateTime` | No | Yes | When the key was created |

**Security Note:** HMAC keys are more secure than API keys because they use a signed token with limited duration.

---

### SamSession

Contains debugging information for a Stream Activity Monitor session.

| Field | Type | Description |
|-------|------|-------------|
| `sessionId` | `xsd:string` | UUID that uniquely identifies the session |
| `isVodSession` | `xsd:boolean` | Whether this is a VOD session |
| `streamCreateRequest` | `StreamCreateRequest` | Initial request from video player |
| `adBreaks` | `AdBreak[]` | Debugging info for each ad break |
| `startDateTime` | `DateTime` | When the session started |
| `sessionDurationMillis` | `xsd:long` | Total session duration |
| `contentDurationMillis` | `xsd:long` | Content duration (VOD only) |

#### AdBreak

Debugging information for an individual ad break within a session.

| Field | Type | Description |
|-------|------|-------------|
| `rootAdResponses` | `AdResponse[]` | Root ad responses including prefetch and follow-up requests |
| `adDecisionCreatives` | `AdDecisionCreative[]` | Information about served creatives |
| `podNum` | `xsd:int` | 1-based index of this pod within the stream |
| `linearAbsolutePodNum` | `xsd:int` | Pod number for Linear streams only |
| `adBreakDurationMillis` | `xsd:long` | Total duration from content stop to resume |
| `filledDurationMillis` | `xsd:long` | Sum of ad durations within the break |
| `servedDurationMillis` | `xsd:long` | Actual ad time users observe |
| `startDateTime` | `DateTime` | When the ad break started |
| `startTimeOffsetMillis` | `xsd:long` | Offset within content (VOD only) |
| `samError` | `SamError` | Any errors during ad break stitching |
| `midrollIndex` | `xsd:int` | 1-based mid-roll position index (VOD VMAP only) |
| `decisionedAds` | `xsd:boolean` | Whether ads were decisioned for this break |
| `trackingEvents` | `TrackingEvent[]` | Associated tracking events |

#### SamError

Error information for Stream Activity Monitor.

| Field | Type | Description |
|-------|------|-------------|
| `samErrorType` | `SamErrorType` | Type of error that occurred |
| `errorDetails` | `xsd:string` | Details about the error |

---

## Enumerations Reference

### AdRuleStatus

| Value | Description |
|-------|-------------|
| `ACTIVE` | Ad rule is actively serving |
| `INACTIVE` | Ad rule is not serving (paused) |
| `UNKNOWN` | Value returned if not exposed by API version |

### StartDateTimeType

| Value | Description |
|-------|-------------|
| `USE_START_DATE_TIME` | Use the specified startDateTime |
| `IMMEDIATELY` | Start immediately upon activation |
| `ONE_HOUR_FROM_NOW` | Start one hour from now |
| `UNKNOWN` | Value returned if not exposed by API version |

### FrequencyCapBehavior

| Value | Description |
|-------|-------------|
| `TURN_ON` | Enable frequency caps with at least one limit |
| `TURN_OFF` | Disable all frequency caps |
| `DEFER` | Defer to next ad rule in priority order |
| `UNKNOWN` | Value returned if not exposed by API version |

### AdRuleSlotBehavior

| Value | Description |
|-------|-------------|
| `ALWAYS_SHOW` | This ad rule always includes this slot's ads |
| `NEVER_SHOW` | This ad rule never includes this slot's ads |
| `DEFER` | Defer to lower priority rules |
| `UNKNOWN` | Value returned if not exposed by API version |

### MidrollFrequencyType

| Value | Description |
|-------|-------------|
| `NONE` | Slot is not a mid-roll |
| `EVERY_N_SECONDS` | Time interval in seconds |
| `FIXED_TIME` | Comma-delimited time points in seconds |
| `EVERY_N_CUEPOINTS` | Single integer cue point interval |
| `FIXED_CUE_POINTS` | Ordinal cue points list |
| `UNKNOWN` | Value returned if not exposed by API version |

### AdRuleSlotBumper

| Value | Description |
|-------|-------------|
| `NONE` | Do not show a bumper ad |
| `BEFORE` | Show a bumper ad before the slot's other ads |
| `AFTER` | Show a bumper ad after the slot's other ads |
| `BEFORE_AND_AFTER` | Show a bumper before and after the slot's other ads |
| `UNKNOWN` | Value returned if not exposed by API version |

### AdSpotTargetingType

| Value | Description |
|-------|-------------|
| `NOT_REQUIRED` | Non-targeted line items may serve |
| `EXPLICITLY_TARGETED` | Only explicitly targeted line items serve |
| `EXPLICITLY_TARGETED_EXCEPT_HOUSE` | House ads serve regardless; others require explicit targeting |
| `UNKNOWN` | Value returned if not exposed by API version |

### AdSpotFillType

| Value | Description |
|-------|-------------|
| `REQUIRED` | If this ad spot is empty, the overall pod is invalid |
| `OPTIONAL` | The ad spot is always 'satisfied', whether empty or nonempty |
| `UNKNOWN` | Value returned if not exposed by API version |

### LineItemType

| Value | Description |
|-------|-------------|
| `SPONSORSHIP` | Sponsorship line item |
| `STANDARD` | Standard line item |
| `NETWORK` | Network line item |
| `BULK` | Bulk line item |
| `PRICE_PRIORITY` | Price priority line item |
| `HOUSE` | House line item |
| `LEGACY_DFP` | Legacy DFP line item |
| `CLICK_TRACKING` | Click tracking line item |
| `ADSENSE` | AdSense line item |
| `AD_EXCHANGE` | Ad Exchange line item |
| `BUMPER` | Bumper line item |
| `ADMOB` | AdMob line item |
| `PREFERRED_DEAL` | Preferred deal line item |
| `UNKNOWN` | Value returned if not exposed by API version |

### LiveStreamEventStatus

| Value | Description |
|-------|-------------|
| `ACTIVE` | Event is eligible for streaming |
| `PAUSED` | Event is paused (can be reactivated) |
| `ARCHIVED` | Event is archived |
| `ADS_PAUSED` | Stream continues; ad insertion paused |
| `UNKNOWN` | Value returned if not exposed by API version |

### DynamicAdInsertionType

| Value | Description |
|-------|-------------|
| `LINEAR` | Google serves unified manifest with stitched content and ads |
| `POD_SERVING_REDIRECT` | Partner manifest with Google ad redirects |
| `POD_SERVING_MANIFEST` | Google serves ad manifest for player switching |
| `UNKNOWN` | Value returned if not exposed by API version |

### StreamingFormat

| Value | Description |
|-------|-------------|
| `HLS` | HTTP Live Streaming format |
| `DASH` | MPEG-DASH format |
| `UNKNOWN` | Value returned if not exposed by API version |

### AdBreakFillType

| Value | Description |
|-------|-------------|
| `SLATE` | Fill with slate content |
| `UNDERLYING_CONTENT` | Fill with underlying content |
| `MINIMIZE_SLATE` | Mostly content with slate transitions |
| `UNKNOWN` | Value returned if not exposed by API version |

### AdServingFormat

| Value | Description |
|-------|-------------|
| `AD_MANAGER_DAI` | Google Ad Manager DAI |
| `DIRECT` | Google Ad Manager Ad Serving |
| `UNKNOWN` | Value returned if not exposed by API version |

### AdBreakMarkupType

| Value | Description |
|-------|-------------|
| `AD_BREAK_MARKUP_HLS_EXT_CUE` | CUE-OUT/CUE-IN (HLS only) |
| `AD_BREAK_MARKUP_HLS_PRIMETIME_SPLICE` | Adobe/Azure Prime Time CUE (HLS) |
| `AD_BREAK_MARKUP_HLS_DATERANGE_SPLICE` | DATERANGE marker (HLS) |
| `AD_BREAK_MARKUP_SCTE35_XML_SPLICE_INSERT` | SCTE35 XML (DASH) |
| `AD_BREAK_MARKUP_SCTE35_BINARY_SPLICE_INSERT` | SCTE35 Binary (HLS/DASH) |
| `AD_BREAK_MARKUP_SCTE35_BINARY_PROVIDER_AD_START_END` | Time Signal variant |
| `AD_BREAK_MARKUP_SCTE35_BINARY_PROVIDER_PLACEMENT_OP_START_END` | Placement variant |
| `AD_BREAK_MARKUP_SCTE35_BINARY_BREAK_START_END` | Break Signal variant |
| `UNKNOWN` | Value returned if not exposed by API version |

### PlaylistType

| Value | Description |
|-------|-------------|
| `EVENT` | Event playlist type |
| `LIVE` | Live playlist type |
| `UNKNOWN` | Value returned if not exposed by API version |

### DaiEncodingProfileStatus

| Value | Description |
|-------|-------------|
| `ACTIVE` | Profile is eligible for streaming |
| `ARCHIVED` | Profile has been archived |
| `UNKNOWN` | Value returned if not exposed by API version |

### VariantType

| Value | Description |
|-------|-------------|
| `MEDIA` | Media variant playlist (audio only, video only, or audio+video) |
| `IFRAME` | iFrame variant playlist (must contain video) |
| `SUBTITLES` | Subtitles variant playlist |
| `UNKNOWN` | Value returned if not exposed by API version |

### ContainerType

| Value | Description |
|-------|-------------|
| `TS` | Transport Stream (MPEG-2) container |
| `FMP4` | Fragmented MP4 container |
| `HLS_AUDIO` | HLS packed audio container |
| `UNKNOWN` | Value returned if not exposed by API version |

### DaiAuthenticationKeyType

| Value | Description |
|-------|-------------|
| `API` | Standard API key (passed via `api-key` SDK parameter) |
| `HMAC` | HMAC key for signature generation (via `auth-token` SDK parameter) |
| `UNKNOWN` | Value returned if not exposed by API version |

### DaiAuthenticationKeyStatus

| Value | Description |
|-------|-------------|
| `ACTIVE` | Key is active and IMA SDK API accepts it as valid |
| `INACTIVE` | Key is inactive and IMA SDK API rejects it |
| `UNKNOWN` | Value returned if not exposed by API version |

### SamErrorType

Error types for Stream Activity Monitor debugging.

| Value | Description |
|-------|-------------|
| `INTERNAL_ERROR` | Internal server error |
| `AD_REQUEST_ERROR` | Error making ad request |
| `VAST_PARSE_ERROR` | Error parsing VAST response |
| `UNSUPPORTED_AD_SYSTEM` | Ad system not supported |
| `CANNOT_FIND_UNIQUE_TRANSCODE_ID` | Cannot find unique transcode ID |
| `CANNOT_FIND_MEDIA_FILE_PATH` | Cannot find media file path |
| `MISSING_INLINE_ELEMENTS` | Missing inline elements in VAST |
| `MAX_WRAPPER_DEPTH_REACHED` | Maximum VAST wrapper depth exceeded |
| `INVALID_AD_SEQUENCE_NUMBER` | Invalid ad sequence number |
| `FAILED_PING` | Tracking ping failed |
| `AD_TAG_PARSE_ERROR` | Error parsing ad tag |
| `VMAP_PARSE_ERROR` | Error parsing VMAP response |
| `INVALID_VMAP_RESPONSE` | Invalid VMAP response |
| `NO_AD_BREAKS_IN_VMAP` | No ad breaks found in VMAP |
| `CUSTOM_AD_SOURCE_IN_VMAP` | Custom ad source in VMAP (unsupported) |
| `AD_BREAK_TYPE_NOT_SUPPORTED` | Ad break type not supported |
| `NEITHER_AD_SOURCE_NOR_TRACKING` | Neither ad source nor tracking found |
| `UNKNOWN_ERROR` | Unknown error occurred |
| `AD_POD_DROPPED_TO_MANY_AD_PODS` | Ad pod dropped due to too many pods |
| `AD_POD_DROPPED_EMPTY_ADS` | Ad pod dropped due to empty ads |
| `AD_BREAK_WITHOUT_AD_POD` | Ad break found without ad pod |
| `TRANSCODING_IN_PROGRESS` | Transcoding still in progress |
| `UNSUPPORTED_VAST_VERSION` | VAST version not supported |
| `AD_POD_DROPPED_BUMPER_ERROR` | Ad pod dropped due to bumper error |
| `NO_VALID_MEDIAFILES_FOUND` | No valid media files found |
| `EXCEEDS_MAX_FILLER` | Exceeds maximum filler duration |
| `SKIPPABLE_AD_NOT_SUPPORTED` | Skippable ads not supported |
| `AD_REQUEST_TIMEOUT` | Ad request timed out |
| `AD_POD_DROPPED_UNSUPPORTED_TYPE` | Ad pod dropped due to unsupported type |
| `DUPLICATE_AD_TAG` | Duplicate ad tag found |
| `FOLLOW_REDIRECTS_IS_FALSE` | Follow redirects is false |
| `AD_POD_DROPPED_INCOMPATIBLE_TIMEOFFSET` | Ad pod dropped due to incompatible time offset |
| `UNKNOWN` | Value returned if not exposed by API version |

---

## Break Templates

### Configuring Ad Break Structure

Break templates define the structure of ad pods. Each template consists of multiple ad spots arranged in sequence.

### Template Design Principles

1. **One Flexible Spot Required** - Every template must have exactly one flexible spot
2. **Position Ordering** - Spots are served in the order defined in the template
3. **Duration Management** - Use `maxDurationMillis` to control break length

### Example: Standard Mid-roll Template

```
[ Bookend Spot (15s) ] [ Flexible Spot (unlimited) ] [ Bookend Spot (15s) ]
```

This template:
- Opens with a premium 15-second fixed spot
- Allows variable ads in the middle
- Closes with another premium 15-second spot

### Use Cases

| Template Type | Configuration | Best For |
|--------------|---------------|----------|
| **Bookend** | Fixed + Flexible + Fixed | Premium sponsorship positions |
| **Standard** | Single Flexible | Maximum fill opportunity |
| **Limited** | Flexible with max duration | Short-form content |
| **Premium** | Multiple Fixed spots | High-value inventory |

---

## DAI Configuration

### Setting Up Dynamic Ad Insertion

#### Prerequisites

1. **Ad Manager 360** - DAI is only available with 360 accounts
2. **Encoding Profiles** - Configure profiles matching your content quality
3. **Authentication Keys** - Create API or HMAC keys for security
4. **Live Stream Events** - Define events with content URLs and ad tags

### Authentication Methods

#### API Key Authentication

Simple but less secure. API keys are static strings passed with each request.

```python
# Stream request with API key
stream_url = f"{base_url}?api-key={api_key}"
```

#### HMAC Token Authentication (Recommended)

More secure. Uses a signed hash with expiration.

```python
import hashlib
import hmac
import time

def generate_hmac_token(secret_key, data, expiry_seconds=300):
    """Generate HMAC token for DAI authentication."""
    expiry = int(time.time()) + expiry_seconds
    message = f"{data},{expiry}"
    signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"{message},{signature}"
```

### Encoding Profile Configuration

Configure profiles to match each quality level in your content:

| Profile | Resolution | Bitrate | Container |
|---------|------------|---------|-----------|
| 1080p | 1920x1080 | 5000 kbps | FMP4 |
| 720p | 1280x720 | 2500 kbps | FMP4 |
| 480p | 854x480 | 1000 kbps | TS |
| 360p | 640x360 | 500 kbps | TS |

---

## Actions Reference

### AdRuleAction Types

| Action | Description |
|--------|-------------|
| `ActivateAdRules` | Activates inactive ad rules |
| `DeactivateAdRules` | Deactivates active ad rules |
| `DeleteAdRules` | Deletes ad rules permanently |

### LiveStreamEventAction Types

| Action | Description |
|--------|-------------|
| `ActivateLiveStreamEvents` | Activates live stream events |
| `ArchiveLiveStreamEvents` | Archives completed events |
| `PauseLiveStreamEvents` | Pauses active events |
| `PauseLiveStreamEventAds` | Pauses advertisements within live stream events |
| `RefreshLiveStreamEventMasterPlaylists` | Refreshes the master playlists for live stream events |

### DaiEncodingProfileAction Types

| Action | Description |
|--------|-------------|
| `ActivateDaiEncodingProfiles` | Activates archived profiles |
| `ArchiveDaiEncodingProfiles` | Archives active profiles |

### DaiAuthenticationKeyAction Types

| Action | Description |
|--------|-------------|
| `ActivateDaiAuthenticationKeys` | Activates inactive keys |
| `DeactivateDaiAuthenticationKeys` | Deactivates active keys |

**Note:** A DAI authentication key cannot be deactivated if it is used by active content sources or active live streams.

---

## Python Code Examples

### Prerequisites

```bash
pip install googleads
```

### Configuration File (googleads.yaml)

```yaml
ad_manager:
  application_name: Video Ad Rules Application
  network_code: 'YOUR_NETWORK_CODE'
  client_id: 'YOUR_CLIENT_ID'
  client_secret: 'YOUR_CLIENT_SECRET'
  refresh_token: 'YOUR_REFRESH_TOKEN'
```

### Creating Ad Rules for Video Content

```python
from googleads import ad_manager

def create_video_ad_rule():
    """Create an ad rule for video content with pre-roll, mid-roll, and post-roll."""

    # Initialize the client
    client = ad_manager.AdManagerClient.LoadFromStorage()
    ad_rule_service = client.GetService('AdRuleService', version='v202511')

    # Define targeting (target all video content)
    targeting = {
        'inventoryTargeting': {
            'targetedAdUnits': [
                {'adUnitId': 'VIDEO_AD_UNIT_ID', 'includeDescendants': True}
            ]
        }
    }

    # Define pre-roll slot (single 30-second ad)
    preroll = {
        'xsi_type': 'StandardPoddingAdRuleSlot',
        'slotBehavior': 'ALWAYS_SHOW',
        'maxVideoAdDuration': 30000,  # 30 seconds in milliseconds
        'videoMidrollFrequencyType': 'NONE',
        'maxPodDuration': 30000,
        'maxAdsInPod': 1
    }

    # Define mid-roll slot (up to 90 seconds, every 5 minutes)
    midroll = {
        'xsi_type': 'StandardPoddingAdRuleSlot',
        'slotBehavior': 'ALWAYS_SHOW',
        'maxVideoAdDuration': 30000,
        'videoMidrollFrequencyType': 'EVERY_N_SECONDS',
        'videoMidrollFrequency': 300,  # Every 5 minutes
        'maxPodDuration': 90000,  # 90 seconds max per pod
        'maxAdsInPod': 3
    }

    # Define post-roll slot (single 15-second ad)
    postroll = {
        'xsi_type': 'StandardPoddingAdRuleSlot',
        'slotBehavior': 'ALWAYS_SHOW',
        'maxVideoAdDuration': 15000,
        'videoMidrollFrequencyType': 'NONE',
        'maxPodDuration': 15000,
        'maxAdsInPod': 1
    }

    # Create the ad rule
    ad_rule = {
        'name': 'Standard Video Ad Rule',
        'priority': 100,
        'targeting': targeting,
        'startDateTimeType': 'IMMEDIATELY',
        'unlimitedEndDateTime': True,
        'frequencyCapBehavior': 'TURN_ON',
        'maxImpressionsPerLineItemPerStream': 3,
        'maxImpressionsPerLineItemPerPod': 1,
        'preroll': preroll,
        'midroll': midroll,
        'postroll': postroll
    }

    # Create the ad rule
    result = ad_rule_service.createAdRules([ad_rule])

    for rule in result:
        print(f"Created ad rule: {rule['name']} (ID: {rule['id']})")

    return result

if __name__ == '__main__':
    create_video_ad_rule()
```

### Setting Up Break Templates

```python
from googleads import ad_manager

def create_break_template():
    """Create a break template with bookend and flexible spots."""

    client = ad_manager.AdManagerClient.LoadFromStorage()
    ad_rule_service = client.GetService('AdRuleService', version='v202511')

    # First, create the ad spots
    spots = [
        {
            'name': 'premium_opening',
            'displayName': 'Premium Opening Spot',
            'customSpot': True,
            'flexible': False,
            'maxDurationMillis': 15000,  # 15 seconds
            'maxNumberOfAds': 1,
            'targetingType': 'EXPLICITLY_TARGETED',
            'backfillBlocked': True
        },
        {
            'name': 'flexible_middle',
            'displayName': 'Flexible Middle Spot',
            'customSpot': True,
            'flexible': True,
            'maxDurationMillis': 60000,  # 60 seconds max
            'maxNumberOfAds': 0,  # Unlimited (allowed because flexible=True)
            'targetingType': 'NOT_REQUIRED',
            'backfillBlocked': False
        },
        {
            'name': 'premium_closing',
            'displayName': 'Premium Closing Spot',
            'customSpot': True,
            'flexible': False,
            'maxDurationMillis': 15000,
            'maxNumberOfAds': 1,
            'targetingType': 'EXPLICITLY_TARGETED',
            'backfillBlocked': True
        }
    ]

    # Create the ad spots
    created_spots = ad_rule_service.createAdSpots(spots)
    print(f"Created {len(created_spots)} ad spots")

    # Create the break template using the spot IDs
    break_template = {
        'name': 'Premium Bookend Template',
        'displayName': 'Premium Bookend Break Template',
        'breakTemplateMembers': [
            {'adSpotId': created_spots[0]['id'], 'adSpotFillType': 'REQUIRED'},
            {'adSpotId': created_spots[1]['id'], 'adSpotFillType': 'OPTIONAL'},
            {'adSpotId': created_spots[2]['id'], 'adSpotFillType': 'REQUIRED'}
        ]
    }

    # Create the break template
    result = ad_rule_service.createBreakTemplates([break_template])

    for template in result:
        print(f"Created break template: {template['name']} (ID: {template['id']})")

    return result

if __name__ == '__main__':
    create_break_template()
```

### Managing Live Stream Events

```python
from googleads import ad_manager
from datetime import datetime, timedelta

def create_live_stream_event():
    """Create a live stream event for DAI."""

    client = ad_manager.AdManagerClient.LoadFromStorage()
    live_stream_service = client.GetService('LiveStreamEventService', version='v202511')

    # Calculate start and end times
    start_time = datetime.now() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=3)

    def to_ad_manager_datetime(dt):
        return {
            'date': {
                'year': dt.year,
                'month': dt.month,
                'day': dt.day
            },
            'hour': dt.hour,
            'minute': dt.minute,
            'second': dt.second,
            'timeZoneId': 'America/New_York'
        }

    live_stream_event = {
        'name': 'Live Sports Event - Championship Game',
        'startDateTime': to_ad_manager_datetime(start_time),
        'endDateTime': to_ad_manager_datetime(end_time),
        'dynamicAdInsertionType': 'POD_SERVING_REDIRECT',
        'enableDaiAuthenticationKeys': True,
        'contentUrls': [
            'https://example.com/live/stream.m3u8'
        ],
        'adTags': [
            'https://pubads.g.doubleclick.net/gampad/ads?iu=/12345/live_sports&...'
        ],
        'hlsSettings': {
            'playlistType': 'LIVE'
        }
    }

    result = live_stream_service.createLiveStreamEvents([live_stream_event])

    for event in result:
        print(f"Created live stream event: {event['name']} (ID: {event['id']})")

    return result

def get_live_stream_events():
    """Retrieve active live stream events."""

    client = ad_manager.AdManagerClient.LoadFromStorage()
    live_stream_service = client.GetService('LiveStreamEventService', version='v202511')

    # Create statement to filter for active events
    statement = ad_manager.StatementBuilder(version='v202511')
    statement.Where('status = :status')
    statement.WithBindVariable('status', 'ACTIVE')

    response = live_stream_service.getLiveStreamEventsByStatement(
        statement.ToStatement()
    )

    if 'results' in response:
        for event in response['results']:
            print(f"Event: {event['name']} - Status: {event['status']}")

    return response

if __name__ == '__main__':
    create_live_stream_event()
    get_live_stream_events()
```

### Configuring DAI Encoding Profiles

```python
from googleads import ad_manager

def create_dai_encoding_profiles():
    """Create DAI encoding profiles for different quality levels."""

    client = ad_manager.AdManagerClient.LoadFromStorage()
    dai_service = client.GetService('DaiEncodingProfileService', version='v202511')

    profiles = [
        {
            'name': 'profile_1080p',
            'variantType': 'MEDIA',
            'containerType': 'FMP4',
            'videoSettings': {
                'codec': 'avc1.64001f',  # H.264 High Profile
                'bitrate': 5000000,  # 5 Mbps
                'framesPerSecond': 30.0,
                'resolution': {'width': 1920, 'height': 1080}
            },
            'audioSettings': {
                'codec': 'mp4a.40.2',  # AAC-LC
                'bitrate': 128000,  # 128 kbps
                'channels': 2,
                'sampleRateHertz': 48000
            }
        },
        {
            'name': 'profile_720p',
            'variantType': 'MEDIA',
            'containerType': 'FMP4',
            'videoSettings': {
                'codec': 'avc1.64001f',
                'bitrate': 2500000,  # 2.5 Mbps
                'framesPerSecond': 30.0,
                'resolution': {'width': 1280, 'height': 720}
            },
            'audioSettings': {
                'codec': 'mp4a.40.2',
                'bitrate': 128000,
                'channels': 2,
                'sampleRateHertz': 48000
            }
        },
        {
            'name': 'profile_480p',
            'variantType': 'MEDIA',
            'containerType': 'TS',
            'videoSettings': {
                'codec': 'avc1.42001e',  # H.264 Baseline Profile
                'bitrate': 1000000,  # 1 Mbps
                'framesPerSecond': 30.0,
                'resolution': {'width': 854, 'height': 480}
            },
            'audioSettings': {
                'codec': 'mp4a.40.2',
                'bitrate': 96000,
                'channels': 2,
                'sampleRateHertz': 44100
            }
        }
    ]

    result = dai_service.createDaiEncodingProfiles(profiles)

    for profile in result:
        print(f"Created encoding profile: {profile['name']} (ID: {profile['id']})")

    return result

if __name__ == '__main__':
    create_dai_encoding_profiles()
```

### Creating DAI Authentication Keys

```python
from googleads import ad_manager

def create_dai_authentication_keys():
    """Create HMAC and API authentication keys for DAI."""

    client = ad_manager.AdManagerClient.LoadFromStorage()
    key_service = client.GetService('DaiAuthenticationKeyService', version='v202511')

    keys = [
        {
            'name': 'Production HMAC Key',
            'keyType': 'HMAC'
        },
        {
            'name': 'Development API Key',
            'keyType': 'API'
        }
    ]

    result = key_service.createDaiAuthenticationKeys(keys)

    for key in result:
        print(f"Created key: {key['name']}")
        print(f"  Type: {key['keyType']}")
        print(f"  ID: {key['id']}")
        # Note: The actual key value is only returned once at creation
        if 'key' in key:
            print(f"  Key: {key['key']} (SAVE THIS - cannot be retrieved later!)")

    return result

if __name__ == '__main__':
    create_dai_authentication_keys()
```

### Monitoring Stream Activity

```python
from googleads import ad_manager

def monitor_stream_sessions(session_ids):
    """Monitor DAI stream sessions for debugging."""

    client = ad_manager.AdManagerClient.LoadFromStorage()
    sam_service = client.GetService('StreamActivityMonitorService', version='v202511')

    # First, register sessions for monitoring
    # Sessions must be registered before they can be queried
    registered = sam_service.registerSessionsForMonitoring(session_ids)
    print(f"Registered {len(registered)} sessions for monitoring")

    # Build statement to query sessions
    # Note: There may be a delay before session data is available
    statement = ad_manager.StatementBuilder(version='v202511')
    statement.Where('sessionId IN (:sessionIds)')
    statement.WithBindVariable('sessionIds', session_ids)
    statement.Limit(25)  # Maximum 25 sessions per request

    response = sam_service.getSamSessionsByStatement(statement.ToStatement())

    if 'results' in response:
        for session in response['results']:
            print(f"\nSession: {session['sessionId']}")
            print(f"  VOD Session: {session.get('isVodSession', False)}")
            print(f"  Start Time: {session.get('startDateTime', 'N/A')}")
            print(f"  Duration: {session.get('sessionDurationMillis', 0)}ms")

            if 'adBreaks' in session:
                print(f"  Ad Breaks: {len(session['adBreaks'])}")
                for i, ad_break in enumerate(session['adBreaks']):
                    print(f"    Break {i + 1}:")
                    print(f"      Pod Num: {ad_break.get('podNum', 'N/A')}")
                    print(f"      Duration: {ad_break.get('adBreakDurationMillis', 0)}ms")
                    print(f"      Filled: {ad_break.get('filledDurationMillis', 0)}ms")
                    print(f"      Served: {ad_break.get('servedDurationMillis', 0)}ms")
                    if 'samError' in ad_break:
                        error = ad_break['samError']
                        print(f"      Error: {error.get('samErrorType', 'UNKNOWN')}")
                        print(f"      Details: {error.get('errorDetails', 'N/A')}")

    return response

def debug_live_stream(event_id):
    """Get debugging information for a live stream event."""

    client = ad_manager.AdManagerClient.LoadFromStorage()

    # Get the live stream event
    live_stream_service = client.GetService('LiveStreamEventService', version='v202511')
    statement = ad_manager.StatementBuilder(version='v202511')
    statement.Where('id = :id')
    statement.WithBindVariable('id', event_id)

    response = live_stream_service.getLiveStreamEventsByStatement(
        statement.ToStatement()
    )

    if 'results' in response and len(response['results']) > 0:
        event = response['results'][0]
        print(f"Live Stream Event: {event['name']}")
        print(f"  Status: {event['status']}")
        print(f"  DAI Type: {event.get('dynamicAdInsertionType', 'N/A')}")
        print(f"  Auth Enabled: {event.get('enableDaiAuthenticationKeys', False)}")

        # Get associated sessions (if any are being monitored)
        # In practice, you would get session IDs from your video player

    return response

if __name__ == '__main__':
    # Example usage with sample session IDs
    session_ids = ['session-uuid-1', 'session-uuid-2']
    monitor_stream_sessions(session_ids)
```

---

## Video Ad Patterns

### Best Practices for Video Monetization

#### Content Length Guidelines

| Content Duration | Recommended Ad Strategy |
|-----------------|------------------------|
| < 2 minutes | Pre-roll only |
| 2-10 minutes | Pre-roll + 1 mid-roll |
| 10-30 minutes | Pre-roll + 2-3 mid-rolls |
| 30+ minutes | Pre-roll + mid-rolls every 8-10 min + post-roll |

#### Frequency Capping Recommendations

| Scenario | Max Impressions/Stream | Max Impressions/Pod |
|----------|----------------------|---------------------|
| Brand safety focused | 2 | 1 |
| Balanced monetization | 3 | 1 |
| Maximum fill | 5 | 2 |

### Ad Rule Priority Strategy

```
Priority 1-100:   Premium sponsorship deals
Priority 101-500: Category-specific rules
Priority 501-900: General audience rules
Priority 901-999: Fallback/default rules
```

### Common Patterns

#### Pattern 1: Short-Form Content (Social/UGC)

```python
# Pre-roll only, no mid-rolls
ad_rule = {
    'name': 'Short Form Rule',
    'priority': 500,
    'preroll': {
        'slotBehavior': 'ALWAYS_SHOW',
        'maxVideoAdDuration': 6000,  # 6-second bumper
        'maxAdsInPod': 1
    },
    'midroll': {'slotBehavior': 'NEVER_SHOW'},
    'postroll': {'slotBehavior': 'NEVER_SHOW'}
}
```

#### Pattern 2: Premium Long-Form Content

```python
# Full monetization with bookend templates
ad_rule = {
    'name': 'Premium Long Form Rule',
    'priority': 100,
    'frequencyCapBehavior': 'TURN_ON',
    'maxImpressionsPerLineItemPerStream': 2,
    'preroll': {
        'slotBehavior': 'ALWAYS_SHOW',
        'maxVideoAdDuration': 30000,
        'maxPodDuration': 60000,
        'maxAdsInPod': 2
    },
    'midroll': {
        'slotBehavior': 'ALWAYS_SHOW',
        'videoMidrollFrequencyType': 'EVERY_N_SECONDS',
        'videoMidrollFrequency': 600,  # Every 10 minutes
        'maxVideoAdDuration': 30000,
        'maxPodDuration': 90000,
        'maxAdsInPod': 3
    },
    'postroll': {
        'slotBehavior': 'ALWAYS_SHOW',
        'maxVideoAdDuration': 30000,
        'maxAdsInPod': 1
    }
}
```

#### Pattern 3: Live Sports Events

```python
# Natural break points with extended pods
live_event = {
    'name': 'Live Sports Event',
    'dynamicAdInsertionType': 'POD_SERVING_REDIRECT',
    'enableDaiAuthenticationKeys': True
}

# Associated ad rule
ad_rule = {
    'name': 'Live Sports Ad Rule',
    'priority': 50,
    'midroll': {
        'slotBehavior': 'ALWAYS_SHOW',
        'videoMidrollFrequencyType': 'FIXED_CUE_POINTS',  # Triggered by SCTE markers
        'maxPodDuration': 180000,  # Up to 3 minutes during timeouts
        'maxAdsInPod': 6
    }
}
```

---

## Troubleshooting

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `AdRuleNotFound` | Invalid ad rule ID | Verify the ad rule exists and is not deleted |
| `InvalidTargeting` | Malformed targeting object | Check targeting structure matches API schema |
| `PriorityConflict` | Duplicate priority value | Use unique priorities for each ad rule |
| `AuthenticationError` | Invalid OAuth credentials | Refresh OAuth token or check configuration |
| `NotActivated` | Feature requires activation | Contact Google to enable DAI features |
| `SamSessionError` | Session not registered | Call `registerSessionsForMonitoring` first |
| `QuotaExceeded` | API rate limit reached | Implement exponential backoff |
| `MALFORMED_SESSION_ID` | Invalid session ID format | Ensure session ID is a valid UUID |
| `REQUEST_EXCEEDS_SESSION_LIMIT` | Too many sessions requested | Limit to 25 sessions per request |

### SAM Error Types Reference

When debugging with Stream Activity Monitor, these are common error types:

| Error Type | Description | Resolution |
|------------|-------------|------------|
| `AD_REQUEST_ERROR` | Error making ad request | Check ad tag URL and network connectivity |
| `AD_REQUEST_TIMEOUT` | Ad request timed out | Increase timeout or check server latency |
| `VAST_PARSE_ERROR` | Error parsing VAST response | Validate VAST XML response |
| `UNSUPPORTED_VAST_VERSION` | VAST version not supported | Use VAST 2.0, 3.0, or 4.x |
| `NO_VALID_MEDIAFILES_FOUND` | No valid media files found | Check transcoded creative availability |
| `TRANSCODING_IN_PROGRESS` | Transcoding still in progress | Wait for transcoding to complete |
| `MAX_WRAPPER_DEPTH_REACHED` | Too many VAST wrapper redirects | Reduce wrapper chain depth |
| `EXCEEDS_MAX_FILLER` | Exceeds maximum filler duration | Adjust `maxFillerDuration` setting |

### Debugging Tips

1. **Use Stream Activity Monitor** - Register sessions and query for debugging info
2. **Check Ad Manager UI** - Verify configurations in the web interface
3. **Enable Detailed Logging** - Use the googleads library's logging features

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('googleads').setLevel(logging.DEBUG)
```

4. **Validate Targeting** - Use the Targeting Picker in Ad Manager UI to test
5. **Test with Known Content** - Use test content URLs during development

### API Version Compatibility

When upgrading API versions, check the [Release Notes](https://developers.google.com/ad-manager/api/rel_notes) for:

- Deprecated fields
- Renamed enums
- New required fields
- Behavioral changes

---

## Resources

### Official Documentation

- [AdRuleService Reference (v202511)](https://developers.google.com/ad-manager/api/reference/v202511/AdRuleService)
- [AdRule Type Reference](https://developers.google.com/ad-manager/api/reference/v202511/AdRuleService.AdRule)
- [AdSpot Type Reference](https://developers.google.com/ad-manager/api/reference/v202511/AdRuleService.AdSpot)
- [LiveStreamEventService Reference](https://developers.google.com/ad-manager/api/reference/v202511/LiveStreamEventService)
- [LiveStreamEvent Type Reference](https://developers.google.com/ad-manager/api/reference/v202511/LiveStreamEventService.LiveStreamEvent)
- [DaiEncodingProfileService Reference](https://developers.google.com/ad-manager/api/reference/v202511/DaiEncodingProfileService)
- [DaiAuthenticationKeyService Reference](https://developers.google.com/ad-manager/api/reference/v202511/DaiAuthenticationKeyService)
- [StreamActivityMonitorService Reference](https://developers.google.com/ad-manager/api/reference/v202511/StreamActivityMonitorService)
- [DAI Pod Serving API](https://developers.google.com/ad-manager/dynamic-ad-insertion/api/pod-serving/live/get-started)
- [Video Ad Rules Help](https://support.google.com/admanager/answer/9170964)
- [Standard Video Ad Rules](https://support.google.com/admanager/answer/9204132)

### Related Services

- [ReportService](../reporting/) - Generate video performance reports
- [InventoryService](../inventory/) - Manage video ad units
- [LineItemService](../orders-line-items/) - Create video line items

---

*Last Updated: November 2024*
*API Version: v202511*
