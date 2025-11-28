---
name: gam-api-reports
description: Google Ad Manager report generation module for Python. Covers 5 report types (delivery, inventory, sales, reach, programmatic), report dimensions and metrics, report creation and execution, filtering and date ranges, report data manipulation, and MCP report tools (gam_quick_report, gam_create_report, gam_run_report, gam_list_reports).
---

# GAM API Report Module

## Purpose

Focused guidance for the Google Ad Manager **report generation module** - creating, executing, and manipulating GAM reports.

## When to Use This Skill

Use this skill when:
- **Generating GAM reports** (delivery, inventory, sales, reach, programmatic)
- **Working with report dimensions and metrics** for custom reports
- **Creating custom reports** with filters and date ranges
- **Using MCP report tools** (gam_quick_report, gam_create_report, etc.)
- **Manipulating report data** (filtering, sorting, exporting)
- **Understanding report types** and their standard configurations
- **Debugging report generation issues** or timeouts

**NOT for**: Authentication setup, MCP server deployment, line items/ad units, general API configuration

## 🎯 Quick Reference

### Report Types (5 Available)

1. **Delivery** - Impressions, clicks, CTR, CPM, revenue by ad unit/advertiser
2. **Inventory** - Ad requests, fill rate, matched requests by ad unit
3. **Sales** - Revenue, eCPM by advertiser/order/salesperson
4. **Reach** - Unique reach, frequency by country/device
5. **Programmatic** - Programmatic revenue, impressions by demand channel

See [report-types.md](resources/report-types.md) for dimensions, metrics, and examples.

### MCP Report Tools (4 Available)

1. `gam_quick_report` - Generate pre-configured reports (delivery, inventory, etc.)
2. `gam_create_report` - Create custom reports with specific dimensions/metrics
3. `gam_run_report` - Execute existing saved reports
4. `gam_list_reports` - List available saved reports

See [mcp-tools.md](resources/mcp-tools.md) for parameters and examples.

## 📦 Report Module Architecture

```
gam-api/packages/core/src/gam_api/
├── reports.py              # ReportGenerator class - main entry point
├── models.py               # ReportDefinition, DateRange, ReportType
├── adapters/
│   ├── rest/
│   │   └── analytics.py    # REST API report operations
│   └── soap/
│       └── soap_adapter.py # SOAP API report operations

applications/mcp-server/tools/
└── reports.py              # MCP report tools implementation
```

## 🚀 Common Report Patterns

```python
# Pattern 1: Quick Report (Predefined)
from gam_api import GAMClient
client = GAMClient()
report = client.quick_report('delivery', days_back=7)
print(f"Generated {len(report)} rows")
report.to_csv('delivery_report.csv')

# Pattern 2: Custom Report (Specific Dimensions/Metrics)
from gam_api.reports import ReportGenerator
from gam_api.models import DateRange

generator = ReportGenerator(client)
report = generator.create_custom_report(
    dimensions=['DATE', 'AD_UNIT_NAME', 'ADVERTISER_NAME'],
    metrics=['IMPRESSIONS', 'CLICKS', 'CTR', 'REVENUE'],
    date_range=DateRange.last_n_days(30),
    filters=[{'field': 'DEVICE_CATEGORY_NAME', 'operator': 'EQUALS', 'value': 'Mobile'}]
)

# Pattern 3: MCP Quick Report Tool
# Via Claude or MCP client
mcp_client.call_tool("gam_quick_report", {
    "report_type": "delivery",
    "days_back": 7
})

# Pattern 4: Report Data Manipulation
report = client.quick_report('delivery', days_back=30)
top_10 = (report
    .filter(lambda row: row.get('IMPRESSIONS', 0) > 10000)
    .sort('REVENUE', ascending=False)
    .head(10))
```

See [examples.md](resources/examples.md) for more report patterns.

## 🔧 Report Configuration

### Date Ranges

```python
from gam_api.models import DateRange

# Relative date ranges
DateRange.last_n_days(7)
DateRange.last_n_days(30)
DateRange.this_month()
DateRange.last_month()

# Absolute date range
DateRange(start_date='2024-01-01', end_date='2024-01-31')
```

### Report Filters

```python
# Filter by dimension value
filters = [{
    'field': 'DEVICE_CATEGORY_NAME',
    'operator': 'EQUALS',  # or CONTAINS, STARTS_WITH, IN
    'value': 'Mobile'
}]

# Multiple filters (AND logic)
filters = [
    {'field': 'COUNTRY_NAME', 'operator': 'IN', 'values': ['US', 'CA', 'GB']},
    {'field': 'IMPRESSIONS', 'operator': 'GREATER_THAN', 'value': 1000}
]
```

## 📊 Report Dimensions & Metrics

### Common Report Dimensions

**Time**: `DATE`, `MONTH_AND_YEAR`, `WEEK`
**Inventory**: `AD_UNIT_NAME`, `AD_UNIT_ID`, `AD_UNIT_SIZE`
**Campaign**: `LINE_ITEM_NAME`, `ORDER_NAME`, `ADVERTISER_NAME`, `CREATIVE_NAME`
**Geography**: `COUNTRY_NAME`, `REGION_NAME`, `CITY_NAME`
**Device**: `DEVICE_CATEGORY_NAME` (Desktop, Mobile, Tablet)

### Common Report Metrics

**Impressions**: `IMPRESSIONS`, `AD_SERVER_IMPRESSIONS`
**Clicks**: `CLICKS`, `AD_SERVER_CLICKS`
**Rates**: `CTR`, `FILL_RATE`, `AD_SERVER_CTR`
**Revenue**: `REVENUE`, `TOTAL_REVENUE`, `AD_SERVER_REVENUE`
**Performance**: `ECPM`, `CPM`, `AVERAGE_ECPM`
**Inventory**: `AD_REQUESTS`, `MATCHED_REQUESTS`, `UNFILLED_IMPRESSIONS`
**Reach**: `UNIQUE_REACH`, `FREQUENCY` (REACH report type only)

Get complete lists: see [dimensions-metrics.md](resources/dimensions-metrics.md) or use MCP tool `gam_get_dimensions_metrics`.

## 🐛 Report Troubleshooting

**Empty Report**: Check date range and filters - may be too restrictive
**Report Timeout**: Large reports take time - increase timeout or reduce date range
**Invalid Dimension/Metric**: Not all dimensions work with all metrics - check compatibility
**REACH metrics not showing**: Must use `report_type='REACH'` for unique reach/frequency
**Slow Report Generation**: Reduce date range, limit dimensions/metrics, or use quick reports

### Common Report Issues

```python
# Issue: Empty report despite data existing
# Solution: Check date range is correct
report = client.quick_report('delivery', days_back=7)  # vs days_back=365

# Issue: Report timeout
# Solution: Increase timeout for large reports
await client.wait_for_report(report_id, timeout=1800)  # 30 minutes

# Issue: Invalid dimension combination
# Solution: Use get_common_combinations() to find valid pairs
combinations = client.get_common_combinations()
```

## 📚 Resource Files

### Report-Specific Documentation

- **[report-types.md](resources/report-types.md)** - Complete details on all 5 report types with standard dimensions/metrics
- **[mcp-tools.md](resources/mcp-tools.md)** - MCP report tool reference (gam_quick_report, gam_create_report, etc.)
- **[examples.md](resources/examples.md)** - Practical report generation code examples
- **[dimensions-metrics.md](resources/dimensions-metrics.md)** - Complete lists of available dimensions and metrics for reports

## 🔑 Key Report Concepts

### Report Types and Use Cases

- **Delivery**: Campaign performance tracking (impressions, clicks, revenue)
- **Inventory**: Ad inventory utilization (fill rates, requests)
- **Sales**: Revenue analysis by advertiser/order
- **Reach**: Unique audience reach and frequency
- **Programmatic**: Programmatic channel performance

### Report Execution Flow

```
1. Define report (dimensions, metrics, date range, filters)
2. Create report job (returns report_id)
3. Wait for completion (poll status)
4. Download results (CSV, JSON, or DataFrame)
5. Process data (filter, sort, aggregate, export)
```

### Report Data Structure

```python
# ReportResult object
report.total_rows          # Number of rows
report.dimension_headers   # List of dimension names
report.metric_headers      # List of metric names
report.rows                # Raw report data
report.summary             # Aggregated statistics

# Data manipulation methods
report.filter(lambda row: row['IMPRESSIONS'] > 1000)
report.sort('REVENUE', ascending=False)
report.head(10)           # Top 10 rows
report.to_csv()           # Export to CSV
report.to_dataframe()     # Convert to pandas DataFrame
```

## 💡 Best Practices

1. **Use Unified Client** - Let it choose the optimal API
2. **Enable Fallback** - Always have backup strategy
3. **Monitor Performance** - Check metrics regularly
4. **Cache Results** - Use built-in caching for metadata
5. **Handle Errors Gracefully** - Use specific exception types
6. **Test with Real Data** - Journey tests with actual API
7. **Use Async Operations** - Better performance for large reports
8. **Validate Dimensions/Metrics** - Check compatibility before creating reports

## 🎓 Learning Path

### Beginner: Basic Reports

1. Setup authentication (`generate_new_token.py`)
2. Generate quick reports (delivery, inventory)
3. Export to CSV/Excel
4. Understand report types and dimensions

### Intermediate: Custom Reports

1. Create custom reports with specific dimensions/metrics
2. Use filters and date ranges
3. Work with SDK fluent API
4. Test with pytest

### Advanced: Production Deployment

1. Implement unified client with fallback
2. Deploy MCP server to Cloud Run
3. Monitor performance and optimize
4. Handle errors and edge cases
5. Use circuit breaker patterns

## 📞 Support

For issues and questions:
1. Check troubleshooting section above
2. Review resource files in `resources/`
3. Check service logs: `gcloud logs read --service=gam-mcp-server`
4. Verify configuration and authentication
5. Test with `python test_credentials.py`

---

**Status**: Production-ready ✅
**MCP Server**: https://gam-mcp-server-183972668403.us-central1.run.app
**Coverage**: 70%+ (unit + integration tests)
**Last Updated**: 2025-10-31
