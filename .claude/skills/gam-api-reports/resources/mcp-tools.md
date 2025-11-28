# GAM MCP Server Tools Reference

Complete reference for all 8 MCP tools available in the production GAM API server.

**Production Server**: https://gam-mcp-server-183972668403.us-central1.run.app
**Authentication**: JWT Bearer tokens

## Table of Contents

- [1. gam_quick_report](#1-gam_quick_report)
- [2. gam_create_report](#2-gam_create_report)
- [3. gam_run_report](#3-gam_run_report)
- [4. gam_list_reports](#4-gam_list_reports)
- [5. gam_get_dimensions_metrics](#5-gam_get_dimensions_metrics)
- [6. gam_get_common_combinations](#6-gam_get_common_combinations)
- [7. gam_get_quick_report_types](#7-gam_get_quick_report_types)
- [8. gam_get_performance_stats](#8-gam_get_performance_stats)

---

## 1. gam_quick_report

Generate pre-configured reports with standard dimensions and metrics.

### Purpose
Quickly generate reports for common use cases without specifying dimensions/metrics.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `report_type` | string | Yes | Type of report: `delivery`, `inventory`, `sales`, `reach`, `programmatic` |
| `days_back` | integer | No | Number of days to look back (default: 30) |
| `start_date` | string | No | Start date in YYYY-MM-DD format (alternative to days_back) |
| `end_date` | string | No | End date in YYYY-MM-DD format (requires start_date) |
| `format` | string | No | Output format: `json`, `csv`, `summary` (default: `json`) |

### Example Request

```json
{
  "tool": "gam_quick_report",
  "arguments": {
    "report_type": "delivery",
    "days_back": 7
  }
}
```

### Example Response

```json
{
  "success": true,
  "report_type": "delivery",
  "days_back": 7,
  "total_rows": 1543,
  "dimensions": ["DATE", "AD_UNIT_NAME", "ADVERTISER_NAME"],
  "metrics": ["IMPRESSIONS", "CLICKS", "CTR", "REVENUE"],
  "execution_time": 12.5,
  "data_preview": [
    {
      "DATE": "2024-01-15",
      "AD_UNIT_NAME": "Homepage Banner",
      "ADVERTISER_NAME": "Acme Corp",
      "IMPRESSIONS": 15000,
      "CLICKS": 450,
      "CTR": 3.0,
      "REVENUE": 75.00
    }
  ],
  "note": "Showing first 10 rows of 1543 total rows"
}
```

### Use Cases
- Quick campaign performance check
- Daily monitoring dashboards
- Weekly reporting to stakeholders
- Ad-hoc analysis

---

## 2. gam_create_report

Create custom reports with specific dimensions, metrics, and filters.

### Purpose
Full control over report creation with custom dimensions, metrics, and filtering.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Report name/display name |
| `dimensions` | array | Yes | List of dimension names |
| `metrics` | array | Yes | List of metric names |
| `report_type` | string | No | Report type: `HISTORICAL`, `REACH`, `AD_SPEED` (default: `HISTORICAL`) |
| `days_back` | integer | No | Number of days to look back (default: 30) |
| `start_date` | string | No | Start date in YYYY-MM-DD format |
| `end_date` | string | No | End date in YYYY-MM-DD format |
| `filters` | array | No | Array of filter objects |
| `run_immediately` | boolean | No | Whether to run report immediately (default: true) |
| `format` | string | No | Output format (default: `json`) |

### Filter Object Structure

```json
{
  "field": "DEVICE_CATEGORY_NAME",
  "operator": "equals",
  "value": "Mobile"
}
```

### Example Request

```json
{
  "tool": "gam_create_report",
  "arguments": {
    "name": "Mobile Performance Report",
    "dimensions": ["DATE", "AD_UNIT_NAME", "DEVICE_CATEGORY_NAME"],
    "metrics": ["IMPRESSIONS", "CLICKS", "CTR", "REVENUE"],
    "report_type": "HISTORICAL",
    "days_back": 30,
    "filters": [
      {
        "field": "DEVICE_CATEGORY_NAME",
        "operator": "equals",
        "value": "Mobile"
      }
    ],
    "run_immediately": true
  }
}
```

### Example Response

```json
{
  "success": true,
  "report_id": "12345678",
  "report_name": "Mobile Performance Report",
  "status": "COMPLETED",
  "total_rows": 892,
  "dimensions": ["DATE", "AD_UNIT_NAME", "DEVICE_CATEGORY_NAME"],
  "metrics": ["IMPRESSIONS", "CLICKS", "CTR", "REVENUE"],
  "execution_time": 18.3,
  "data_preview": [...]
}
```

### Use Cases
- Custom analysis with specific dimensions
- Filtered reports for specific segments
- Ad-hoc queries for troubleshooting
- Client-specific reporting

---

## 3. gam_run_report

Execute an existing saved report.

### Purpose
Run a report that was previously created and saved in Google Ad Manager.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `report_id` | string | Yes | ID of the saved report |
| `date_override` | object | No | Optional date range override |

### Example Request

```json
{
  "tool": "gam_run_report",
  "arguments": {
    "report_id": "12345678",
    "date_override": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31"
    }
  }
}
```

### Example Response

```json
{
  "success": true,
  "report_id": "12345678",
  "status": "COMPLETED",
  "total_rows": 2156,
  "execution_time": 15.2
}
```

### Use Cases
- Run scheduled reports on-demand
- Re-run reports with different date ranges
- Automated reporting workflows
- Historical data comparison

---

## 4. gam_list_reports

List available saved reports with filtering options.

### Purpose
Discover and filter saved reports in Google Ad Manager.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Maximum number of reports to return (default: 10) |
| `report_type` | string | No | Filter by report type |
| `search` | string | No | Search in report names |

### Example Request

```json
{
  "tool": "gam_list_reports",
  "arguments": {
    "limit": 20,
    "search": "mobile"
  }
}
```

### Example Response

```json
{
  "success": true,
  "total_reports": 45,
  "reports": [
    {
      "report_id": "12345678",
      "name": "Mobile Performance Daily",
      "report_type": "HISTORICAL",
      "created_date": "2024-01-15",
      "last_run": "2024-01-31"
    },
    {
      "report_id": "87654321",
      "name": "Mobile Revenue Report",
      "report_type": "HISTORICAL",
      "created_date": "2024-01-10",
      "last_run": "2024-01-30"
    }
  ]
}
```

### Use Cases
- Discover existing reports
- Find reports by name
- Report inventory management
- Documentation and auditing

---

## 5. gam_get_dimensions_metrics

Get lists of available dimensions and metrics for report creation.

### Purpose
Discover valid dimensions and metrics for creating custom reports.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `report_type` | string | No | Filter by report type: `HISTORICAL`, `REACH`, `AD_SPEED` |
| `category` | string | No | Return only: `dimensions`, `metrics`, or `both` (default: `both`) |

### Example Request

```json
{
  "tool": "gam_get_dimensions_metrics",
  "arguments": {
    "report_type": "HISTORICAL",
    "category": "both"
  }
}
```

### Example Response

```json
{
  "success": true,
  "dimensions": [
    {
      "id": "DATE",
      "name": "Date",
      "description": "Report date",
      "category": "time"
    },
    {
      "id": "AD_UNIT_NAME",
      "name": "Ad Unit",
      "description": "Ad unit name",
      "category": "inventory"
    }
  ],
  "metrics": [
    {
      "id": "IMPRESSIONS",
      "name": "Impressions",
      "description": "Total impressions",
      "type": "integer"
    },
    {
      "id": "CLICKS",
      "name": "Clicks",
      "description": "Total clicks",
      "type": "integer"
    }
  ]
}
```

### Use Cases
- Explore available dimensions/metrics
- Validate report configurations
- Build report creation UI
- Documentation and reference

---

## 6. gam_get_common_combinations

Get pre-validated dimension-metric combinations for common use cases.

### Purpose
Get recommended combinations that are known to work well together.

### Parameters

None required.

### Example Request

```json
{
  "tool": "gam_get_common_combinations",
  "arguments": {}
}
```

### Example Response

```json
{
  "success": true,
  "combinations": {
    "ad_performance": {
      "name": "Ad Performance",
      "description": "Standard ad performance metrics",
      "dimensions": ["DATE", "AD_UNIT_NAME", "ADVERTISER_NAME"],
      "metrics": ["IMPRESSIONS", "CLICKS", "CTR", "REVENUE"]
    },
    "inventory_analysis": {
      "name": "Inventory Analysis",
      "description": "Ad inventory and fill rates",
      "dimensions": ["DATE", "AD_UNIT_NAME", "AD_UNIT_SIZE"],
      "metrics": ["AD_REQUESTS", "MATCHED_REQUESTS", "FILL_RATE"]
    },
    "geographic_reach": {
      "name": "Geographic Reach",
      "description": "Reach by geography",
      "dimensions": ["DATE", "COUNTRY_NAME", "DEVICE_CATEGORY_NAME"],
      "metrics": ["UNIQUE_REACH", "FREQUENCY", "IMPRESSIONS"]
    }
  }
}
```

### Use Cases
- Get started quickly with proven combinations
- Avoid incompatible dimension/metric pairs
- Build report templates
- Training and onboarding

---

## 7. gam_get_quick_report_types

Get available quick report types and their descriptions.

### Purpose
List all available quick report types with their standard configurations.

### Parameters

None required.

### Example Request

```json
{
  "tool": "gam_get_quick_report_types",
  "arguments": {}
}
```

### Example Response

```json
{
  "success": true,
  "report_types": {
    "delivery": {
      "name": "Delivery Report",
      "description": "Track impressions, clicks, and revenue",
      "dimensions": ["DATE", "AD_UNIT_NAME", "ADVERTISER_NAME"],
      "metrics": ["IMPRESSIONS", "CLICKS", "CTR", "REVENUE"]
    },
    "inventory": {
      "name": "Inventory Report",
      "description": "Monitor inventory and fill rates",
      "dimensions": ["DATE", "AD_UNIT_NAME", "AD_UNIT_SIZE"],
      "metrics": ["AD_REQUESTS", "MATCHED_REQUESTS", "FILL_RATE"]
    },
    "sales": {
      "name": "Sales Report",
      "description": "Analyze revenue by advertiser",
      "dimensions": ["DATE", "ADVERTISER_NAME", "ORDER_NAME"],
      "metrics": ["REVENUE", "ECPM", "IMPRESSIONS"]
    }
  }
}
```

### Use Cases
- Discover available quick reports
- Understand quick report configurations
- Build UI for report selection
- Documentation

---

## 8. gam_get_performance_stats

Get server performance statistics and metrics.

### Purpose
Monitor MCP server performance, cache effectiveness, and operation metrics.

### Parameters

None required.

### Example Request

```json
{
  "tool": "gam_get_performance_stats",
  "arguments": {}
}
```

### Example Response

```json
{
  "success": true,
  "server_stats": {
    "uptime_seconds": 86400,
    "uptime_human": "1.0 days"
  },
  "operation_performance": {
    "gam_quick_report": {
      "count": 250,
      "errors": 5,
      "avg_time_ms": 1250.5,
      "p50_ms": 1100,
      "p95_ms": 2500,
      "p99_ms": 4500
    },
    "gam_create_report": {
      "count": 150,
      "errors": 3,
      "avg_time_ms": 1850.2,
      "p50_ms": 1600,
      "p95_ms": 3200,
      "p99_ms": 5100
    }
  },
  "cache_stats": {
    "hits": 450,
    "misses": 180,
    "hit_rate": 71.4,
    "total_size_mb": 45.2
  },
  "circuit_breaker_state": "CLOSED"
}
```

### Use Cases
- Monitor server health
- Optimize cache configuration
- Identify performance bottlenecks
- Track error rates
- Capacity planning

---

## Authentication

All tools require JWT Bearer token authentication in production.

### Getting JWT Token

```bash
# Check service logs for JWT token
gcloud logs read --service=gam-mcp-server --limit=50 | grep "Client token"
```

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "gam-api-cloud": {
      "url": "https://gam-mcp-server-183972668403.us-central1.run.app/mcp",
      "transport": "http",
      "headers": {
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
      }
    }
  }
}
```

### HTTP API Access

```bash
# Direct HTTP call
curl -X POST \
  https://gam-mcp-server-183972668403.us-central1.run.app/tool/gam_quick_report \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "report_type": "delivery",
    "days_back": 7
  }'
```

---

## Error Handling

All tools return structured errors:

```json
{
  "success": false,
  "error": {
    "type": "ValidationError",
    "message": "Invalid value for field 'report_type'",
    "code": "VAL_001",
    "details": {
      "field": "report_type",
      "provided_value": "invalid_type",
      "allowed_values": ["delivery", "inventory", "sales", "reach", "programmatic"]
    },
    "suggestions": [
      "Check the allowed values for 'report_type'",
      "Use gam_get_quick_report_types to see valid report types"
    ]
  }
}
```

## Best Practices

1. **Use Quick Reports First** - Start with `gam_quick_report` for common cases
2. **Validate Dimensions/Metrics** - Use `gam_get_dimensions_metrics` before custom reports
3. **Check Common Combinations** - Use `gam_get_common_combinations` for proven setups
4. **Monitor Performance** - Regularly check `gam_get_performance_stats`
5. **Handle Degraded Mode** - Check for `degraded_mode` in responses
6. **Cache Results** - Server automatically caches results for 30-60 minutes
7. **Use Appropriate Date Ranges** - Larger ranges take longer to process
8. **Specify Formats** - Use `csv` format for spreadsheet import

---

## Tool Selection Guide

**For Quick Analysis:**
- `gam_quick_report` - Predefined reports for common cases

**For Custom Reports:**
- `gam_create_report` - Full control over dimensions/metrics/filters

**For Saved Reports:**
- `gam_list_reports` - Find existing reports
- `gam_run_report` - Execute saved reports

**For Discovery:**
- `gam_get_dimensions_metrics` - Available fields
- `gam_get_common_combinations` - Proven combinations
- `gam_get_quick_report_types` - Quick report options

**For Monitoring:**
- `gam_get_performance_stats` - Server health and performance

---

**Production Status**: ✅ Deployed and Operational
**Health Check**: https://gam-mcp-server-183972668403.us-central1.run.app/health
**Region**: us-central1 (Google Cloud Run)
**Scaling**: 0-10 instances based on demand
