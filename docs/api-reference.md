# API Reference

Complete reference for REST API endpoints and MCP tools.

## 🌐 REST API Endpoints

**Base URL:** `http://localhost:8000/api/v1`

### Authentication
All endpoints require API key authentication:
```bash
-H "X-API-Key: your-api-key"
```

### Reports

#### Quick Report
Generate pre-configured reports with standard dimensions and metrics.

```http
POST /api/v1/reports/quick
Content-Type: application/json

{
  "report_type": "delivery",  // delivery, inventory, sales, reach, programmatic
  "days_back": 7,            // Optional, defaults to 7
  "date_range": {            // Optional alternative to days_back
    "start_date": "2024-01-01",
    "end_date": "2024-01-07"
  }
}
```

#### Custom Report
Create reports with custom dimensions and metrics.

```http
POST /api/v1/reports/custom
Content-Type: application/json

{
  "dimensions": ["DATE", "AD_UNIT_NAME"],
  "metrics": ["TOTAL_IMPRESSIONS", "TOTAL_CLICKS"],
  "date_range": {
    "start_date": "2024-01-01", 
    "end_date": "2024-01-07"
  },
  "filters": [                // Optional
    {
      "dimension": "AD_UNIT_NAME",
      "operator": "EQUALS",
      "values": ["Homepage Banner"]
    }
  ]
}
```

#### List Reports
Get paginated list of existing reports.

```http
GET /api/v1/reports?page=1&per_page=10
```

### Metadata

#### Dimensions and Metrics
Get available dimensions and metrics for report creation.

```http
GET /api/v1/metadata/dimensions-metrics
```

Response:
```json
{
  "dimensions": [
    {"id": "DATE", "name": "Date", "description": "Report date"},
    {"id": "AD_UNIT_NAME", "name": "Ad Unit", "description": "Ad unit name"}
  ],
  "metrics": [
    {"id": "TOTAL_IMPRESSIONS", "name": "Impressions", "description": "Total impressions"},
    {"id": "TOTAL_CLICKS", "name": "Clicks", "description": "Total clicks"}
  ]
}
```

#### Common Combinations
Get suggested dimension-metric combinations for reports.

```http
GET /api/v1/metadata/combinations
```

### System

#### Health Check
Basic service health status.

```http
GET /api/v1/health
```

#### Detailed Status
Comprehensive system status including database and external API connections.

```http
GET /api/v1/status
```

#### Version Info
API version and build information.

```http
GET /api/v1/version
```

## 🤖 MCP Tools

**Production Server:** `https://gam-mcp-server-183972668403.us-central1.run.app`  
**Authentication:** JWT Bearer tokens

### Available Tools

#### gam_quick_report
Generate pre-configured reports with standard metrics.

**Parameters:**
- `report_type` (string): Type of report - "delivery", "inventory", "sales", "reach", "programmatic"
- `days_back` (integer, optional): Number of days back from today (default: 7)

**Example:**
```json
{
  "report_type": "delivery",
  "days_back": 30
}
```

#### gam_create_report
Create custom reports with specific dimensions and metrics.

**Parameters:**
- `dimensions` (array): List of dimension IDs
- `metrics` (array): List of metric IDs  
- `start_date` (string): Start date (YYYY-MM-DD)
- `end_date` (string): End date (YYYY-MM-DD)
- `filters` (array, optional): Report filters

**Example:**
```json
{
  "dimensions": ["DATE", "AD_UNIT_NAME"],
  "metrics": ["TOTAL_IMPRESSIONS", "TOTAL_CLICKS"],
  "start_date": "2024-01-01",
  "end_date": "2024-01-07"
}
```

#### gam_list_reports
List available reports with pagination.

**Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `per_page` (integer, optional): Items per page (default: 10)

#### gam_get_dimensions_metrics
Get available dimensions and metrics for report creation.

**Parameters:** None

#### gam_get_common_combinations
Get suggested dimension-metric combinations.

**Parameters:** None

#### gam_get_quick_report_types
Get available quick report types and their descriptions.

**Parameters:** None

#### gam_run_report
Execute an existing report by ID.

**Parameters:**
- `report_id` (string): ID of the report to execute

## 📊 Report Types

### Delivery Report
Standard advertising delivery metrics.

**Dimensions:**
- DATE, AD_UNIT_NAME, ADVERTISER_NAME, ORDER_NAME, LINE_ITEM_NAME

**Metrics:**
- TOTAL_IMPRESSIONS, TOTAL_CLICKS, CTR, TOTAL_REVENUE, AVERAGE_ECPM

### Inventory Report
Ad inventory and fill rate metrics.

**Dimensions:**
- DATE, AD_UNIT_NAME, AD_UNIT_SIZE

**Metrics:**
- TOTAL_REQUESTS, MATCHED_REQUESTS, FILL_RATE, UNFILLED_IMPRESSIONS

### Sales Report
Revenue and monetization metrics.

**Dimensions:**
- DATE, ADVERTISER_NAME, ORDER_NAME, SALESPERSON_NAME

**Metrics:**
- TOTAL_REVENUE, AVERAGE_ECPM, TOTAL_IMPRESSIONS

### Reach Report
Audience reach and frequency metrics.

**Dimensions:**
- DATE, COUNTRY_NAME, DEVICE_CATEGORY_NAME

**Metrics:**
- UNIQUE_REACH, FREQUENCY, TOTAL_IMPRESSIONS

### Programmatic Report
Programmatic advertising performance.

**Dimensions:**
- DATE, DEMAND_CHANNEL_NAME, BUYER_NAME

**Metrics:**
- PROGRAMMATIC_REVENUE, PROGRAMMATIC_IMPRESSIONS, PROGRAMMATIC_CLICKS

## 🔧 Error Handling

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (missing/invalid API key or JWT)
- `404` - Not Found (endpoint or resource not found)
- `429` - Rate Limited (too many requests)
- `500` - Internal Server Error

### Error Response Format

```json
{
  "error": "Invalid report type",
  "code": "INVALID_REPORT_TYPE",
  "details": {
    "allowed_types": ["delivery", "inventory", "sales", "reach", "programmatic"]
  }
}
```

## 🚀 Rate Limits

- REST API: 100 requests per minute per API key
- MCP Tools: No explicit limits, but Google Ad Manager API limits apply
- Report generation: 10 concurrent reports per account

## 📝 Response Formats

All responses return JSON by default. Report data can be exported in multiple formats:

- **JSON**: Default structured data
- **CSV**: Comma-separated values for spreadsheet import  
- **DataFrame**: Python pandas DataFrame (SDK only)

### Sample Report Response

```json
{
  "report_id": "report_123456",
  "status": "completed",
  "generated_at": "2024-01-15T10:30:00Z",
  "data": [
    {
      "DATE": "2024-01-01",
      "AD_UNIT_NAME": "Homepage Banner",
      "TOTAL_IMPRESSIONS": 15000,
      "TOTAL_CLICKS": 450,
      "CTR": 3.0,
      "TOTAL_REVENUE": 75.00
    }
  ],
  "summary": {
    "total_rows": 1,
    "total_impressions": 15000,
    "total_clicks": 450,
    "total_revenue": 75.00
  }
}
```