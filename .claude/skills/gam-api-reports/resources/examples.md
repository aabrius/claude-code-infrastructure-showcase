# GAM API Practical Examples

Comprehensive collection of practical code examples for common GAM API tasks.

## Table of Contents

- [Basic Report Generation](#basic-report-generation)
- [Custom Reports](#custom-reports)
- [MCP Server Usage](#mcp-server-usage)
- [SDK Fluent API](#sdk-fluent-api)
- [Data Manipulation](#data-manipulation)
- [Error Handling](#error-handling)
- [Production Patterns](#production-patterns)

---

## Basic Report Generation

### Quick Reports for Last 7 Days

```python
from gam_api import GAMClient

# Initialize client
client = GAMClient()

# Delivery report
delivery = client.quick_report('delivery', days_back=7)
print(f"Total Impressions: {delivery.summary['total_impressions']:,}")
print(f"Total Revenue: ${delivery.summary['total_revenue']:.2f}")

# Export to CSV
delivery.to_csv('delivery_last_7_days.csv')
```

### Multiple Reports in Batch

```python
# Generate multiple reports efficiently
report_types = ['delivery', 'inventory', 'sales']

for report_type in report_types:
    report = client.quick_report(report_type, days_back=30)
    filename = f"{report_type}_30days.csv"
    report.to_csv(filename)
    print(f"✅ {report_type}: {len(report)} rows → {filename}")
```

---

## Custom Reports

### Custom Delivery Report with Filters

```python
from gam_api.unified import GAMUnifiedClient
import asyncio

async def custom_mobile_report():
    """Mobile-only delivery report"""
    async with GAMUnifiedClient() as client:
        report_id = await client.create_report({
            'displayName': 'Mobile Performance - Last 30 Days',
            'reportDefinition': {
                'reportType': 'HISTORICAL',
                'dimensions': [
                    'DATE',
                    'AD_UNIT_NAME',
                    'DEVICE_CATEGORY_NAME',
                    'COUNTRY_NAME'
                ],
                'metrics': [
                    'IMPRESSIONS',
                    'CLICKS',
                    'CTR',
                    'REVENUE'
                ],
                'dateRange': {
                    'startDate': '2024-01-01',
                    'endDate': '2024-01-31'
                },
                'filters': [{
                    'field': 'DEVICE_CATEGORY_NAME',
                    'operator': 'EQUALS',
                    'values': {
                        'stringList': {
                            'values': ['Mobile']
                        }
                    }
                }]
            }
        })

        # Wait for completion
        status = await client.wait_for_report(report_id, timeout=600)

        if status == 'COMPLETED':
            data = await client.download_report(report_id, format='CSV')
            with open('mobile_report.csv', 'w') as f:
                f.write(data)
            print("✅ Mobile report generated")

# Run
asyncio.run(custom_mobile_report())
```

### Geographic Performance Report

```python
async def geographic_report():
    """Performance by country"""
    async with GAMUnifiedClient() as client:
        report_id = await client.create_report({
            'reportDefinition': {
                'dimensions': [
                    'COUNTRY_NAME',
                    'AD_UNIT_NAME'
                ],
                'metrics': [
                    'IMPRESSIONS',
                    'CLICKS',
                    'REVENUE'
                ],
                'dateRange': {'days_back': 30}
            }
        })

        await client.wait_for_report(report_id)
        data = await client.download_report(report_id)
        return data

# Run
data = asyncio.run(geographic_report())
```

---

## MCP Server Usage

### Via Python MCP Client

```python
import httpx

# Production MCP server
MCP_SERVER = "https://gam-mcp-server-183972668403.us-central1.run.app"
JWT_TOKEN = "your-jwt-token-here"

# Quick report via MCP
response = httpx.post(
    f"{MCP_SERVER}/tool/gam_quick_report",
    json={
        "report_type": "delivery",
        "days_back": 7
    },
    headers={"Authorization": f"Bearer {JWT_TOKEN}"}
)

result = response.json()
print(f"Report generated: {result['total_rows']} rows")
```

### Custom Report via MCP

```python
# Create custom report via MCP
response = httpx.post(
    f"{MCP_SERVER}/tool/gam_create_report",
    json={
        "name": "Mobile CTR Analysis",
        "dimensions": ["DATE", "AD_UNIT_NAME", "DEVICE_CATEGORY_NAME"],
        "metrics": ["IMPRESSIONS", "CLICKS", "CTR"],
        "days_back": 14,
        "filters": [{
            "field": "DEVICE_CATEGORY_NAME",
            "operator": "equals",
            "value": "Mobile"
        }]
    },
    headers={"Authorization": f"Bearer {JWT_TOKEN}"}
)

result = response.json()
if result['success']:
    print(f"✅ Report created: {result['report_id']}")
```

### Get Performance Stats

```python
# Monitor MCP server performance
response = httpx.post(
    f"{MCP_SERVER}/tool/gam_get_performance_stats",
    json={},
    headers={"Authorization": f"Bearer {JWT_TOKEN}"}
)

stats = response.json()
print(f"Cache hit rate: {stats['cache_stats']['hit_rate']:.1f}%")
print(f"Avg quick_report time: {stats['operation_performance']['gam_quick_report']['avg_time_ms']}ms")
```

---

## SDK Fluent API

### Fluent Report Building

```python
from gam_api import GAMClient

client = GAMClient()

# Readable, chainable API
report = (client
    .reports()
    .delivery()
    .last_30_days()
    .dimensions('DATE', 'AD_UNIT_NAME', 'ADVERTISER_NAME')
    .metrics('IMPRESSIONS', 'CLICKS', 'CTR', 'REVENUE')
    .execute())

print(f"Generated {len(report)} rows")
```

### Data Transformation Pipeline

```python
# Complete transformation pipeline
top_performers = (client
    .reports()
    .delivery()
    .last_30_days()
    .execute()
    .filter(lambda row: row.get('IMPRESSIONS', 0) > 10000)
    .sort('IMPRESSIONS', ascending=False)
    .head(20)
    .to_excel('top_20_performers.xlsx'))

print("✅ Top 20 performers exported to Excel")
```

---

## Data Manipulation

### Filtering and Sorting

```python
# Generate report
report = client.quick_report('delivery', days_back=30)

# Filter high-performing ads
high_ctr = report.filter(
    lambda row: row.get('CTR', 0) > 2.0  # CTR > 2%
)

# Sort by revenue
by_revenue = high_ctr.sort('REVENUE', ascending=False)

# Get top 10
top_10 = by_revenue.head(10)

# Export
top_10.to_csv('top_10_high_ctr.csv')
```

### Group By and Aggregate

```python
import pandas as pd

# Convert to DataFrame for advanced operations
report = client.quick_report('delivery', days_back=30)
df = report.to_dataframe()

# Group by advertiser, sum revenue
by_advertiser = df.groupby('ADVERTISER_NAME').agg({
    'IMPRESSIONS': 'sum',
    'CLICKS': 'sum',
    'REVENUE': 'sum'
}).reset_index()

# Calculate CTR
by_advertiser['CTR'] = (by_advertiser['CLICKS'] / by_advertiser['IMPRESSIONS'] * 100)

# Sort and save
by_advertiser.sort_values('REVENUE', ascending=False).to_csv('revenue_by_advertiser.csv')
```

### Date Range Comparisons

```python
# Current vs previous period
current = client.quick_report('delivery', days_back=7)
previous = client.quick_report('delivery', days_back=14)

# Filter previous to last 7 days only (days 8-14)
previous_7 = previous[7:14]

# Compare metrics
comparison = {
    'current_impressions': current.summary['total_impressions'],
    'previous_impressions': previous_7.summary['total_impressions'],
    'change_pct': (
        (current.summary['total_impressions'] - previous_7.summary['total_impressions']) /
        previous_7.summary['total_impressions'] * 100
    )
}

print(f"Impressions change: {comparison['change_pct']:+.1f}%")
```

---

## Error Handling

### Graceful Error Handling

```python
from gam_api.exceptions import (
    AuthenticationError,
    APIError,
    RateLimitError
)

def generate_report_safely(report_type, days_back=7):
    """Generate report with comprehensive error handling"""
    try:
        client = GAMClient()
        report = client.quick_report(report_type, days_back)
        return report

    except AuthenticationError:
        print("❌ Authentication failed - regenerate token:")
        print("   python generate_new_token.py")
        return None

    except RateLimitError as e:
        print(f"⏳ Rate limited - retry after {e.retry_after} seconds")
        import time
        time.sleep(e.retry_after)
        return generate_report_safely(report_type, days_back)

    except APIError as e:
        print(f"❌ API Error: {e}")
        return None

# Usage
report = generate_report_safely('delivery', 30)
if report:
    print(f"✅ Generated {len(report)} rows")
```

### Retry with Exponential Backoff

```python
import time
from gam_api.exceptions import NetworkError

def generate_with_retry(report_type, max_retries=3):
    """Retry with exponential backoff"""
    for attempt in range(max_retries):
        try:
            client = GAMClient()
            return client.quick_report(report_type, days_back=7)

        except NetworkError as e:
            if attempt == max_retries - 1:
                raise

            wait_time = 2 ** attempt  # 1s, 2s, 4s
            print(f"⏳ Retry {attempt + 1}/{max_retries} in {wait_time}s...")
            time.sleep(wait_time)

# Usage
report = generate_with_retry('delivery')
```

---

## Production Patterns

### Async Batch Processing

```python
import asyncio
from gam_api.unified import GAMUnifiedClient

async def generate_all_reports():
    """Generate multiple reports concurrently"""
    async with GAMUnifiedClient() as client:
        # Create all reports concurrently
        tasks = []
        for report_type in ['delivery', 'inventory', 'sales']:
            task = client.create_report({
                'reportDefinition': {
                    'report_type': report_type,
                    'dateRange': {'days_back': 7}
                }
            })
            tasks.append(task)

        # Wait for all to complete
        report_ids = await asyncio.gather(*tasks)

        # Download results
        results = {}
        for report_type, report_id in zip(['delivery', 'inventory', 'sales'], report_ids):
            await client.wait_for_report(report_id)
            data = await client.download_report(report_id)
            results[report_type] = data

        return results

# Run
results = asyncio.run(generate_all_reports())
```

### Monitored Report Generation

```python
import logging
from datetime import datetime

def monitored_report(report_type, days_back=7):
    """Generate report with monitoring"""
    logger = logging.getLogger('gam_reports')

    start_time = datetime.now()
    try:
        logger.info(f"Starting {report_type} report")

        client = GAMClient()
        report = client.quick_report(report_type, days_back)

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Report completed: {len(report)} rows in {duration:.2f}s"
        )

        # Performance warnings
        if duration > 60:
            logger.warning(f"Slow report generation: {duration:.2f}s")

        if len(report) == 0:
            logger.warning(f"Empty report generated for {report_type}")

        return report

    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"Report failed after {duration:.2f}s: {e}")
        raise

# Usage with logging
logging.basicConfig(level=logging.INFO)
report = monitored_report('delivery', 30)
```

### Health Check and Validation

```python
def validate_gam_setup():
    """Comprehensive validation of GAM setup"""
    checks = {
        'authentication': False,
        'network_access': False,
        'report_generation': False,
    }

    try:
        client = GAMClient()

        # Check authentication
        if client.test_connection():
            checks['authentication'] = True
            print("✅ Authentication successful")

        # Check network access
        network_info = client.get_network_info()
        checks['network_access'] = True
        print(f"✅ Network: {network_info['displayName']}")

        # Check report generation
        test_report = client.quick_report('delivery', days_back=1)
        checks['report_generation'] = True
        print(f"✅ Report generation: {len(test_report)} rows")

    except Exception as e:
        print(f"❌ Validation failed: {e}")

    # Summary
    all_passed = all(checks.values())
    print(f"\n{'✅ All checks passed' if all_passed else '❌ Some checks failed'}")
    return checks

# Run validation
validate_gam_setup()
```

---

**Note**: All async examples use `asyncio.run()` for top-level execution. In async contexts, use `await` directly.
