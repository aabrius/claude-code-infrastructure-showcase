# GAM API Report Types

Complete reference for all 5 Google Ad Manager report types.

## Table of Contents

- [1. Delivery Report](#1-delivery-report)
- [2. Inventory Report](#2-inventory-report)
- [3. Sales Report](#3-sales-report)
- [4. Reach Report](#4-reach-report)
- [5. Programmatic Report](#5-programmatic-report)

---

## 1. Delivery Report

Track advertising delivery performance including impressions, clicks, and revenue.

### Use Cases
- Monitor campaign performance
- Track CTR and engagement metrics
- Analyze revenue by ad unit
- Optimize ad placements

### Standard Dimensions
```python
dimensions = [
    'DATE',                    # Report date
    'AD_UNIT_NAME',           # Ad unit name
    'ADVERTISER_NAME',        # Advertiser name
    'ORDER_NAME',             # Order name
    'LINE_ITEM_NAME',         # Line item name
]
```

### Standard Metrics
```python
metrics = [
    'IMPRESSIONS',            # Total impressions (REST API name)
    'CLICKS',                 # Total clicks
    'CTR',                    # Click-through rate
    'CPM',                    # Cost per thousand
    'REVENUE',                # Total revenue
]
```

### Quick Start Example
```python
from gam_api import GAMClient

client = GAMClient()
report = client.quick_report('delivery', days_back=7)

print(f"Total Impressions: {report.summary['total_impressions']}")
print(f"Total Clicks: {report.summary['total_clicks']}")
print(f"Average CTR: {report.summary['average_ctr']:.2%}")
```

### Custom Delivery Report
```python
report = (client
    .reports()
    .delivery()
    .last_30_days()
    .dimensions('DATE', 'AD_UNIT_NAME', 'ADVERTISER_NAME')
    .metrics('IMPRESSIONS', 'CLICKS', 'CTR', 'REVENUE')
    .execute())
```

---

## 2. Inventory Report

Monitor ad inventory, fill rates, and ad request performance.

### Use Cases
- Track inventory utilization
- Monitor fill rates
- Identify unfilled inventory
- Optimize ad unit performance

### Standard Dimensions
```python
dimensions = [
    'DATE',                    # Report date
    'AD_UNIT_NAME',           # Ad unit name
    'AD_UNIT_SIZE',           # Ad unit size (e.g., 300x250)
]
```

### Standard Metrics
```python
metrics = [
    'AD_REQUESTS',            # Total ad requests
    'MATCHED_REQUESTS',       # Matched ad requests
    'FILL_RATE',              # Fill rate percentage
    'UNFILLED_IMPRESSIONS',   # Unfilled impressions
]
```

### Quick Start Example
```python
client = GAMClient()
report = client.quick_report('inventory', days_back=7)

print(f"Fill Rate: {report.summary['average_fill_rate']:.2%}")
print(f"Total Ad Requests: {report.summary['total_ad_requests']}")
```

### Custom Inventory Report
```python
async with GAMUnifiedClient() as client:
    report_id = await client.create_report({
        'reportDefinition': {
            'reportType': 'HISTORICAL',
            'dimensions': ['DATE', 'AD_UNIT_NAME', 'AD_UNIT_SIZE'],
            'metrics': ['AD_REQUESTS', 'MATCHED_REQUESTS', 'FILL_RATE'],
            'dateRange': {'days_back': 30}
        }
    })
```

---

## 3. Sales Report

Analyze revenue metrics by advertiser, order, and sales team.

### Use Cases
- Track revenue by advertiser
- Monitor sales performance
- Analyze eCPM trends
- Report to sales teams

### Standard Dimensions
```python
dimensions = [
    'DATE',                    # Report date
    'ADVERTISER_NAME',        # Advertiser name
    'ORDER_NAME',             # Order name
    'SALESPERSON_NAME',       # Salesperson name (if available)
]
```

### Standard Metrics
```python
metrics = [
    'REVENUE',                # Total revenue
    'ECPM',                   # Effective CPM
    'IMPRESSIONS',            # Total impressions
]
```

### Quick Start Example
```python
client = GAMClient()
report = client.quick_report('sales', days_back=30)

# Top advertisers by revenue
top_advertisers = (report
    .group_by('ADVERTISER_NAME')
    .sum('REVENUE')
    .sort('REVENUE', ascending=False)
    .head(10))
```

### Custom Sales Report
```python
report = (client
    .reports()
    .sales()
    .last_90_days()
    .dimensions('DATE', 'ADVERTISER_NAME', 'ORDER_NAME')
    .metrics('REVENUE', 'ECPM', 'IMPRESSIONS')
    .execute())
```

---

## 4. Reach Report

Measure audience reach and frequency across different segments.

### Use Cases
- Measure unique reach
- Track frequency caps
- Analyze reach by geography
- Optimize reach campaigns

### Standard Dimensions
```python
dimensions = [
    'DATE',                    # Report date
    'COUNTRY_NAME',           # Country name
    'DEVICE_CATEGORY_NAME',   # Device category (Desktop, Mobile, Tablet)
]
```

### Standard Metrics
```python
metrics = [
    'UNIQUE_REACH',           # Unique users reached
    'FREQUENCY',              # Average frequency
    'IMPRESSIONS',            # Total impressions
]
```

### Quick Start Example
```python
client = GAMClient()
report = client.quick_report('reach', days_back=30)

print(f"Total Unique Reach: {report.summary['total_unique_reach']}")
print(f"Average Frequency: {report.summary['average_frequency']:.2f}")
```

### Custom Reach Report
```python
async with GAMUnifiedClient() as client:
    report_id = await client.create_report({
        'reportDefinition': {
            'reportType': 'REACH',  # Important: Use REACH report type
            'dimensions': ['DATE', 'COUNTRY_NAME', 'DEVICE_CATEGORY_NAME'],
            'metrics': ['UNIQUE_REACH', 'FREQUENCY', 'IMPRESSIONS'],
            'dateRange': {
                'startDate': '2024-01-01',
                'endDate': '2024-01-31'
            }
        }
    })
```

---

## 5. Programmatic Report

Track programmatic advertising performance and revenue.

### Use Cases
- Monitor programmatic revenue
- Track demand channel performance
- Analyze programmatic vs direct
- Optimize programmatic setup

### Standard Dimensions
```python
dimensions = [
    'DATE',                    # Report date
    'DEMAND_CHANNEL_NAME',    # Demand channel (Ad Exchange, Open Bidding)
    'BUYER_NAME',             # Buyer name (programmatic buyer)
]
```

### Standard Metrics
```python
metrics = [
    'PROGRAMMATIC_REVENUE',   # Programmatic revenue
    'PROGRAMMATIC_IMPRESSIONS',  # Programmatic impressions
    'PROGRAMMATIC_CLICKS',    # Programmatic clicks
]
```

### Quick Start Example
```python
client = GAMClient()
report = client.quick_report('programmatic', days_back=14)

# Revenue by demand channel
by_channel = (report
    .group_by('DEMAND_CHANNEL_NAME')
    .sum('PROGRAMMATIC_REVENUE')
    .to_dataframe())
```

### Custom Programmatic Report
```python
report = (client
    .reports()
    .programmatic()
    .last_30_days()
    .dimensions('DATE', 'DEMAND_CHANNEL_NAME', 'BUYER_NAME')
    .metrics('PROGRAMMATIC_REVENUE', 'PROGRAMMATIC_IMPRESSIONS')
    .execute())
```

---

## Report Type Comparison

| Report Type | Primary Focus | Key Metrics | Best For |
|-------------|---------------|-------------|----------|
| **Delivery** | Ad performance | Impressions, Clicks, CTR | Campaign monitoring |
| **Inventory** | Ad inventory | Fill Rate, Ad Requests | Inventory optimization |
| **Sales** | Revenue analysis | Revenue, eCPM | Sales reporting |
| **Reach** | Audience reach | Unique Reach, Frequency | Reach campaigns |
| **Programmatic** | Programmatic | Programmatic Revenue | Programmatic analysis |

## Common Patterns

### Multi-Report Generation
```python
# Generate multiple reports efficiently
async def generate_all_reports():
    async with GAMUnifiedClient() as client:
        reports = []

        for report_type in ['delivery', 'inventory', 'sales']:
            report_id = await client.create_report({
                'reportDefinition': {
                    'report_type': report_type,
                    'dateRange': {'days_back': 7}
                }
            })
            reports.append(report_id)

        return reports
```

### Comparative Analysis
```python
# Compare current vs previous period
current = client.quick_report('delivery', days_back=7)
previous = client.quick_report('delivery', days_back=14).filter_last_7_days()

comparison = {
    'impressions_change': (current.total_impressions - previous.total_impressions) / previous.total_impressions,
    'clicks_change': (current.total_clicks - previous.total_clicks) / previous.total_clicks
}
```

### Export Options
```python
# Multiple export formats
report = client.quick_report('sales', days_back=30)

# CSV for spreadsheets
report.to_csv('sales_report.csv')

# Excel for formatted reports
report.to_excel('sales_report.xlsx', sheet_name='Monthly Sales')

# JSON for APIs
report.to_json('sales_report.json', format='records')

# Pandas DataFrame for analysis
df = report.to_dataframe()
```

---

## Best Practices by Report Type

### Delivery Reports
- Use DATE dimension for trend analysis
- Include AD_UNIT_NAME for placement performance
- Monitor CTR to identify high-performing creatives
- Filter by ADVERTISER_NAME for client reporting

### Inventory Reports
- Track FILL_RATE daily to identify issues
- Use AD_UNIT_SIZE to optimize inventory mix
- Monitor UNFILLED_IMPRESSIONS for lost revenue
- Compare MATCHED_REQUESTS vs AD_REQUESTS

### Sales Reports
- Group by ADVERTISER_NAME for account performance
- Use monthly date ranges for sales cycles
- Calculate ECPM for yield optimization
- Include ORDER_NAME for campaign-level analysis

### Reach Reports
- Use REACH report type (not HISTORICAL)
- Include DEVICE_CATEGORY_NAME for device insights
- Monitor FREQUENCY for cap optimization
- Analyze COUNTRY_NAME for geographic reach

### Programmatic Reports
- Track DEMAND_CHANNEL_NAME for channel mix
- Monitor PROGRAMMATIC_REVENUE daily
- Compare programmatic vs direct revenue
- Use BUYER_NAME for buyer analysis

---

**Note**: All examples use REST API dimension/metric names (e.g., `IMPRESSIONS` instead of `TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS`). The unified client handles conversion automatically.
