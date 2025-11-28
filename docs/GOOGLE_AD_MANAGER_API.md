# Google Ad Manager API Documentation

## Overview

The Google Ad Manager API provides programmatic access to manage ad inventory, create orders, run reports, and interact with advertising data. Google offers **two API versions**:

1. **REST API (Beta)** - Modern JSON/REST interface (recommended for new projects)
2. **SOAP API (Legacy)** - XML/SOAP interface (stable but will be deprecated)

---

## API Comparison

| Feature | REST API (Beta) | SOAP API (Legacy) |
|---------|-----------------|-------------------|
| Protocol | REST/JSON | SOAP/XML |
| Base URL | `https://admanager.googleapis.com/v1` | `https://ads.google.com/apis/ads/publisher` |
| Status | Beta (launched Sept 2024) | Stable (deprecated eventually) |
| Performance | Faster | Slower |
| Coverage | Reports + core resources | Complete (all services) |
| Client Libraries | Python, Java, .NET, PHP, Ruby, Node.js | Python, Java, .NET, PHP, Ruby |

---

## REST API (Beta)

### Service Endpoint
```
https://admanager.googleapis.com/v1
```

### Available Resources & Endpoints

#### Networks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/{name}` | Retrieve a Network object |
| GET | `/v1/networks` | List all accessible networks |

#### Ad Units (`v1.networks.adUnits`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/{name}` | Retrieve an AdUnit |
| GET | `/v1/{parent}/adUnits` | List AdUnit objects |

#### Reports (`v1.networks.reports`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/{parent}/reports` | Create a Report |
| GET | `/v1/{name}` | Retrieve a Report |
| GET | `/v1/{parent}/reports` | List Reports |
| PATCH | `/v1/{report.name}` | Update a Report |
| POST | `/v1/{name}:run` | Execute a report asynchronously |

#### Report Results (`v1.networks.reports.results`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/{name}:fetchRows` | Retrieve completed report rows |

#### Placements (`v1.networks.placements`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/{parent}/placements` | Create a Placement |
| POST | `/v1/{parent}/placements:batchCreate` | Batch create Placements |
| POST | `/v1/{parent}/placements:batchActivate` | Activate Placements |
| POST | `/v1/{parent}/placements:batchArchive` | Archive Placements |
| POST | `/v1/{parent}/placements:batchDeactivate` | Deactivate Placements |
| POST | `/v1/{parent}/placements:batchUpdate` | Batch update Placements |
| GET | `/v1/{name}` | Retrieve a Placement |
| GET | `/v1/{parent}/placements` | List Placements |
| PATCH | `/v1/{placement.name}` | Update a Placement |

#### Custom Fields (`v1.networks.customFields`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/{parent}/customFields` | Create a CustomField |
| POST | `/v1/{parent}/customFields:batchCreate` | Batch create CustomFields |
| POST | `/v1/{parent}/customFields:batchActivate` | Activate CustomFields |
| POST | `/v1/{parent}/customFields:batchDeactivate` | Deactivate CustomFields |
| POST | `/v1/{parent}/customFields:batchUpdate` | Batch update CustomFields |
| GET | `/v1/{name}` | Retrieve a CustomField |
| GET | `/v1/{parent}/customFields` | List CustomFields |
| PATCH | `/v1/{customField.name}` | Update a CustomField |

#### Contacts (`v1.networks.contacts`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/{parent}/contacts` | Create a contact |
| POST | `/v1/{parent}/contacts:batchCreate` | Batch create contacts |
| POST | `/v1/{parent}/contacts:batchUpdate` | Batch update contacts |
| GET | `/v1/{name}` | Retrieve a contact |
| GET | `/v1/{parent}/contacts` | List contacts |
| PATCH | `/v1/{contact.name}` | Update a contact |

#### Teams (`v1.networks.teams`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/{parent}/teams` | Create a Team |
| POST | `/v1/{parent}/teams:batchCreate` | Batch create Teams |
| POST | `/v1/{parent}/teams:batchActivate` | Batch activate Teams |
| POST | `/v1/{parent}/teams:batchDeactivate` | Batch deactivate Teams |
| POST | `/v1/{parent}/teams:batchUpdate` | Batch update Teams |
| GET | `/v1/{name}` | Retrieve a Team |
| GET | `/v1/{parent}/teams` | List Teams |
| PATCH | `/v1/{team.name}` | Update a Team |

#### Sites (`v1.networks.sites`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/{parent}/sites` | Create a Site |
| POST | `/v1/{parent}/sites:batchCreate` | Batch create Sites |
| POST | `/v1/{parent}/sites:batchDeactivate` | Deactivate Sites |
| POST | `/v1/{parent}/sites:batchSubmitForApproval` | Submit Sites for approval |
| POST | `/v1/{parent}/sites:batchUpdate` | Batch update Sites |
| GET | `/v1/{name}` | Retrieve a Site |
| GET | `/v1/{parent}/sites` | List Sites |
| PATCH | `/v1/{site.name}` | Update a Site |

#### Operations (`v1.operations`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/{name}` | Get operation status |
| POST | `/v1/{name}:cancel` | Cancel long-running operation |
| DELETE | `/v1/{name}` | Delete an operation |

#### Read-Only Resources
The API also provides GET/LIST operations for:
- Applications
- Audience Segments
- Companies
- Content
- Creatives
- Line Items
- Orders
- Roles
- Taxonomy Categories
- Users

---

## Authentication

### OAuth2 with Application Default Credentials (ADC)

All API requests require OAuth2 authentication. The recommended approach uses Application Default Credentials (ADC).

#### ADC Credential Lookup Order:
1. `GOOGLE_APPLICATION_CREDENTIALS` environment variable
2. User credentials via `gcloud` CLI
3. Service account attached to Google Cloud resource

#### Setup with Service Account

**Linux/macOS:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

**Windows:**
```cmd
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\service-account-key.json
```

#### Setup with User Credentials
```bash
gcloud auth application-default login \
  --scopes="https://www.googleapis.com/auth/admanager"

gcloud auth application-default set-quota-project PROJECT_ID
```

### Required OAuth2 Scope
```
https://www.googleapis.com/auth/admanager
```

---

## Client Libraries Installation

### Python
```bash
pip install google-ads-admanager
```

### Java (Maven)
```xml
<dependency>
  <groupId>com.google.api-ads</groupId>
  <artifactId>ad-manager</artifactId>
  <version>0.1.0</version>
</dependency>
```

### .NET
```bash
dotnet add package Google.Ads.AdManager.V1 --version 1.0.0-beta01
```

### PHP
```bash
composer require googleads/ad-manager
```

### Ruby
```bash
gem install google-ads-ad_manager
```

### Node.js
```bash
npm install @google-ads/admanager
```

---

## Reports

### Report Structure

```json
{
  "displayName": "My Report",
  "visibility": "DRAFT",
  "reportDefinition": {
    "dimensions": ["DATE", "LINE_ITEM_NAME", "AD_UNIT_NAME"],
    "metrics": ["AD_SERVER_IMPRESSIONS", "AD_SERVER_CLICKS", "AD_SERVER_CTR"],
    "dateRange": {
      "relative": "YESTERDAY"
    },
    "reportType": "HISTORICAL",
    "timeZone": "America/New_York",
    "currencyCode": "USD"
  }
}
```

### Report Visibility Options
- `HIDDEN` - API-only access (default)
- `DRAFT` - Visible in Ad Manager UI as draft
- `SAVED` - Fully saved in Ad Manager UI

### Report Types
- `HISTORICAL` - Standard historical reporting
- `REACH` - Unique reach and frequency
- `PRIVACY_AND_MESSAGING` - Privacy and consent data

### Creating and Running Reports

#### 1. Create Report
```python
from google.ads import admanager_v1

client = admanager_v1.ReportServiceClient()

report = {
    "display_name": "Daily Delivery Report",
    "report_definition": {
        "dimensions": ["DATE", "LINE_ITEM_NAME"],
        "metrics": ["AD_SERVER_IMPRESSIONS", "AD_SERVER_CLICKS"],
        "date_range": {"relative": "LAST_7_DAYS"},
        "report_type": "HISTORICAL"
    }
}

request = admanager_v1.CreateReportRequest(
    parent="networks/NETWORK_CODE",
    report=report
)
response = client.create_report(request=request)
print(f"Created report: {response.name}")
```

#### 2. Run Report
```python
run_request = admanager_v1.RunReportRequest(name=response.name)
operation = client.run_report(run_request)
```

#### 3. Poll for Completion
```python
# Client libraries handle polling automatically
result = operation.result()
```

#### 4. Fetch Results
```python
fetch_request = admanager_v1.FetchReportResultRowsRequest(
    name=f"{response.name}/results"
)
rows = client.fetch_report_result_rows(fetch_request)

for row in rows:
    print(row.dimension_values, row.metric_value_groups)
```

---

## Dimensions Reference

### Time Dimensions
| Dimension | Description | Report Types |
|-----------|-------------|--------------|
| `DATE` | Daily breakdown | HISTORICAL, REACH |
| `WEEK` | Weekly breakdown | HISTORICAL, REACH, PRIVACY_AND_MESSAGING |
| `MONTH_AND_YEAR` | Monthly breakdown | HISTORICAL |
| `HOUR` | Hourly breakdown | HISTORICAL |

### Inventory Dimensions
| Dimension | Description |
|-----------|-------------|
| `AD_UNIT_ID` | Ad unit identifier |
| `AD_UNIT_NAME` | Ad unit name |
| `PLACEMENT_ID` | Placement identifier |
| `PLACEMENT_NAME` | Placement name |

### Order & Line Item Dimensions
| Dimension | Description |
|-----------|-------------|
| `ORDER_ID` | Order identifier |
| `ORDER_NAME` | Order name |
| `LINE_ITEM_ID` | Line item identifier |
| `LINE_ITEM_NAME` | Line item name |
| `LINE_ITEM_TYPE` | Type (sponsorship, standard, etc.) |

### Company Dimensions
| Dimension | Description |
|-----------|-------------|
| `ADVERTISER_ID` | Advertiser company ID |
| `ADVERTISER_NAME` | Advertiser company name |
| `SALESPERSON_ID` | Salesperson user ID |
| `SALESPERSON_NAME` | Salesperson name |

### Creative Dimensions
| Dimension | Description |
|-----------|-------------|
| `CREATIVE_ID` | Creative identifier |
| `CREATIVE_NAME` | Creative name |
| `CREATIVE_SIZE` | Creative dimensions |
| `CREATIVE_TYPE` | Creative type (image, video, etc.) |

### Geographic Dimensions
| Dimension | Description |
|-----------|-------------|
| `COUNTRY_NAME` | Country name |
| `REGION_NAME` | Region/state name |
| `CITY_NAME` | City name |
| `METRO_NAME` | Metro area name |

### Device Dimensions
| Dimension | Description |
|-----------|-------------|
| `DEVICE_CATEGORY` | Device type (desktop, mobile, tablet) |
| `BROWSER_NAME` | Browser name |
| `OPERATING_SYSTEM` | Operating system |

### Video Dimensions
| Dimension | Description |
|-----------|-------------|
| `VIDEO_AD_TYPE` | Video ad type value |
| `VIDEO_AD_TYPE_NAME` | Video ad type localized name |
| `VIDEO_AD_DURATION` | Video ad duration |
| `VIDEO_AD_BREAK_TYPE` | Break type (pre-roll, mid-roll, post-roll) |
| `VIDEO_POSITION_IN_POD` | Position in video pod |
| `VIDEO_POSITION_OF_POD` | Position of pod in stream |
| `VIDEO_PLCMT` | Video placement per ADCOM 1.0 |
| `VIDEO_SDK_VERSION` | Video SDK version |
| `VIDEO_MEASUREMENT_SOURCE` | Video measurement source |

### Programmatic Dimensions
| Dimension | Description |
|-----------|-------------|
| `DEAL_BUYER_ID` | Deal buyer ID (formerly PROGRAMMATIC_BUYER_ID) |
| `DEAL_BUYER_NAME` | Deal buyer name (formerly PROGRAMMATIC_BUYER_NAME) |
| `YIELD_GROUP_BUYER_NAME` | Yield partner name |
| `DSP_SEAT_ID` | DSP seat identifier |
| `DYNAMIC_ALLOCATION_TYPE` | Dynamic allocation type |

---

## Metrics Reference

### Ad Server Metrics
| Metric | Description |
|--------|-------------|
| `AD_SERVER_IMPRESSIONS` | Total impressions served |
| `AD_SERVER_CLICKS` | Total clicks |
| `AD_SERVER_CTR` | Click-through rate |
| `AD_SERVER_CPM` | Cost per thousand impressions |
| `AD_SERVER_CPC` | Cost per click |
| `AD_SERVER_REVENUE` | Total revenue |
| `AD_SERVER_UNFILTERED_DOWNLOADED_IMPRESSIONS` | Unfiltered impressions |

### Delivery Metrics
| Metric | Description |
|--------|-------------|
| `AD_REQUESTS` | Total ad requests |
| `MATCHED_AD_REQUESTS` | Requests with matched ads |
| `FILL_RATE` | Percentage of filled requests |
| `CODE_SERVED_COUNT` | Code served count |
| `COVERAGE` | Ad coverage percentage |

### Active View Metrics
| Metric | Description |
|--------|-------------|
| `ACTIVE_VIEW_VIEWABLE_IMPRESSIONS` | Viewable impressions |
| `ACTIVE_VIEW_MEASURABLE_IMPRESSIONS` | Measurable impressions |
| `ACTIVE_VIEW_VIEWABLE_RATE` | Viewability rate |
| `ACTIVE_VIEW_ELIGIBLE_IMPRESSIONS` | Eligible impressions |

### Revenue Metrics
| Metric | Description |
|--------|-------------|
| `TOTAL_REVENUE` | Total revenue (all sources) |
| `AD_EXCHANGE_REVENUE` | Ad Exchange revenue |
| `ADSENSE_REVENUE` | AdSense revenue |
| `PROGRAMMATIC_REVENUE` | Programmatic revenue |

### Video Metrics
| Metric | Description |
|--------|-------------|
| `VIDEO_VIEWERSHIP_START` | Video starts |
| `VIDEO_VIEWERSHIP_FIRST_QUARTILE` | 25% completion |
| `VIDEO_VIEWERSHIP_MIDPOINT` | 50% completion |
| `VIDEO_VIEWERSHIP_THIRD_QUARTILE` | 75% completion |
| `VIDEO_VIEWERSHIP_COMPLETE` | 100% completion |
| `VIDEO_COMPLETION_RATE` | Completion rate |
| `VIDEO_ERRORS` | Video errors |

### Reach Metrics (REACH report type only)
| Metric | Description |
|--------|-------------|
| `UNIQUE_REACH` | Unique users reached |
| `UNIQUE_REACH_FREQUENCY` | Average frequency |
| `AVERAGE_UNIQUE_REACH` | Average unique reach |

---

## SOAP API (Legacy)

### Base URL
```
https://ads.google.com/apis/ads/publisher/{version}
```

### Current Version
`v202411` (as of November 2024)

### Available Services

| Service | Description |
|---------|-------------|
| `NetworkService` | Network information and settings |
| `ReportService` | Report creation and execution |
| `InventoryService` | Ad units and inventory management |
| `LineItemService` | Line item management |
| `OrderService` | Order management |
| `CompanyService` | Advertiser/agency management |
| `CreativeService` | Creative management |
| `PlacementService` | Placement management |
| `UserService` | User management |
| `TeamService` | Team management |
| `CustomFieldService` | Custom field management |
| `CustomTargetingService` | Custom targeting management |

### Python Client Library (SOAP)

#### Installation
```bash
pip install googleads
```

#### Configuration (`googleads.yaml`)
```yaml
ad_manager:
  application_name: My Application
  network_code: 'YOUR_NETWORK_CODE'

  # OAuth2 credentials
  client_id: 'YOUR_CLIENT_ID'
  client_secret: 'YOUR_CLIENT_SECRET'
  refresh_token: 'YOUR_REFRESH_TOKEN'
```

#### Basic Usage
```python
from googleads import ad_manager

# Load client from configuration
client = ad_manager.AdManagerClient.LoadFromStorage()

# Get network information
network_service = client.GetService('NetworkService')
networks = network_service.getAllNetworks()

for network in networks:
    print(f"Network: {network['displayName']} ({network['networkCode']})")
```

#### Running Reports (SOAP)
```python
from googleads import ad_manager

client = ad_manager.AdManagerClient.LoadFromStorage()
report_downloader = client.GetReportDownloader(version='v202411')

# Define report
report_job = {
    'reportQuery': {
        'dimensions': ['DATE', 'LINE_ITEM_ID', 'LINE_ITEM_NAME'],
        'columns': ['AD_SERVER_IMPRESSIONS', 'AD_SERVER_CLICKS', 'AD_SERVER_CTR'],
        'dateRangeType': 'LAST_7_DAYS'
    }
}

# Run report
report_job_id = report_downloader.WaitForReport(report_job)

# Download results
with open('report.csv', 'wb') as file:
    report_downloader.DownloadReportToFile(
        report_job_id,
        'CSV_DUMP',
        file
    )
```

#### PQL Queries
```python
data_downloader = client.GetDataDownloader(version='v202411')

pql_query = """
    SELECT Id, Name, Status, Impressions, Clicks
    FROM Line_Item
    WHERE OrderId = :orderId
"""

values = {'orderId': 123456}
results = data_downloader.DownloadPqlResultToList(pql_query, values)

for row in results[1:]:  # Skip header row
    print(row)
```

---

## Migration Notes

### Upcoming Changes (2025)

#### Dimension/Metric Renames (by October 1, 2025)
| Old Name | New Name |
|----------|----------|
| `PROGRAMMATIC_BUYER_ID` | `DEAL_BUYER_ID` |
| `PROGRAMMATIC_BUYER_NAME` | `DEAL_BUYER_NAME` |
| `AD_SERVER_UNFILTERED_IMPRESSIONS` | `AD_SERVER_UNFILTERED_DOWNLOADED_IMPRESSIONS` |

Old values supported as aliases until October 1, 2025.

### REST API vs SOAP API Migration

For new projects, use the REST API. The REST API provides:
- Better performance (JSON vs XML)
- Modern authentication (ADC)
- Simpler client library usage
- Built-in pagination

The SOAP API remains available for complete feature coverage (line items, inventory management, etc.) until the REST API reaches feature parity.

---

## Rate Limits & Best Practices

### Rate Limits
- Requests are subject to quota limits per API Console project
- Report execution has separate quotas from data operations

### Best Practices
1. **Use client libraries** - Handle authentication, retries, and pagination automatically
2. **Reuse service accounts** - SOAP and REST APIs can share the same credentials
3. **Cache metadata** - Dimensions/metrics lists change infrequently
4. **Batch operations** - Use batch endpoints for bulk updates
5. **Poll efficiently** - Use exponential backoff when checking report status

---

## Resources

### Official Documentation
- [REST API Reference](https://developers.google.com/ad-manager/api/beta/reference/rest)
- [Getting Started Guide](https://developers.google.com/ad-manager/api/beta/getting-started)
- [Reports Guide](https://developers.google.com/ad-manager/api/beta/reports)
- [Release Notes](https://developers.google.com/ad-manager/api/beta/docs/release-notes)
- [SOAP API Reference](https://developers.google.com/ad-manager/api/start)

### Support
- [Ad Manager Help Center](https://support.google.com/admanager)
- [Core Dimensions & Metrics](https://support.google.com/admanager/answer/9182941)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/google-ad-manager)
