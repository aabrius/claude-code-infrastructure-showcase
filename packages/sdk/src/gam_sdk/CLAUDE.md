# CLAUDE.md - GAM API Python SDK

This file provides guidance to Claude Code (claude.ai/code) when working with the Python SDK implementation in this directory.

## Directory Overview

This directory contains the Python SDK for the Google Ad Manager API integration. The SDK provides a high-level, Pythonic interface for developers to integrate GAM functionality into their applications.

## Architecture

### Core Files

- **`client.py`**: Main SDK client class
  - High-level API interface
  - Method chaining support
  - Automatic retry logic
  - Response parsing

- **`auth.py`**: SDK authentication
  - Multiple auth methods support
  - Token management
  - Credential helpers

- **`config.py`**: SDK configuration
  - Builder pattern for config
  - Environment variable support
  - Validation helpers

- **`exceptions.py`**: SDK-specific exceptions
  - Detailed error information
  - Exception hierarchy
  - Error recovery helpers

- **`reports.py`**: Report operations
  - Fluent report builder
  - Async report generation
  - Result streaming

### Builders Directory

- **`builders/__init__.py`**: Query builders
  - Report query builder
  - Filter builder
  - Date range builder

## SDK Usage

### Basic Usage

```python
from src.sdk import GAMClient

# Initialize client with config file
client = GAMClient(config_path="googleads.yaml")

# Or with agent config
client = GAMClient(config_path="config/agent_config.yaml")

# Generate a quick report using fluent interface
report = client.quick_report("delivery", days_back=7)
print(f"Report generated: {report.id}")

# Test connection
status = client.test_connection()
print(f"Connection status: {status['overall_status']}")
```

### Advanced Usage

```python
from src.sdk import GAMClient

# Initialize client
client = GAMClient()

# Use fluent report builder interface
report_builder = client.reports()

# Build and execute custom reports (implementation varies by report builder)
# See ReportBuilder class for specific method signatures

# Access core client features
network_info = client.test_connection()
print(f"Network: {network_info.get('network_info', {}).get('displayName', 'Unknown')}")
```

### Async Usage

```python
import asyncio
from gam_api import AsyncGAMClient

async def generate_reports():
    async with AsyncGAMClient(config) as client:
        # Generate multiple reports concurrently
        tasks = [
            client.reports.quick("delivery"),
            client.reports.quick("inventory"),
            client.reports.quick("sales")
        ]
        reports = await asyncio.gather(*tasks)
        return reports
```

## Configuration Methods

### 1. Direct Initialization

```python
client = GAMClient(
    network_code="123456789",
    client_id="your-client-id",
    client_secret="your-client-secret",
    refresh_token="your-refresh-token"
)
```

### 2. Configuration File

```python
# From googleads.yaml (legacy format)
client = GAMClient(config_path="googleads.yaml")

# From agent config (enhanced format)  
client = GAMClient(config_path="config/agent_config.yaml")
```

### 3. Environment Variables

```python
# Reads GAM_* environment variables
client = GAMClient.from_env()
```

### 4. Builder Pattern

```python
from gam_api import ClientBuilder

client = (
    ClientBuilder()
    .network_code("123456789")
    .oauth2_credentials(
        client_id="...",
        client_secret="...",
        refresh_token="..."
    )
    .timeout(60)
    .max_retries(3)
    .build()
)
```

## Report Operations

### Report Builder

```python
# Fluent interface for report building
report = (
    client.reports
    .create("Revenue Analysis")
    .description("Monthly revenue breakdown by advertiser")
    .dimensions(
        Dimension.DATE,
        Dimension.ADVERTISER_NAME,
        Dimension.ORDER_NAME
    )
    .metrics(
        Metric.IMPRESSIONS,
        Metric.REVENUE,
        Metric.ECPM
    )
    .date_range("2024-01-01", "2024-01-31")
    .sort_by(Metric.REVENUE, descending=True)
    .limit(100)
)

# Execute report
result = report.run()

# Or save for later
saved_report = report.save()
print(f"Report saved with ID: {saved_report.id}")
```

### Report Formats

```python
# Different output formats
report.download("report.csv", format="csv")
report.download("report.xlsx", format="excel")
report.download("report.json", format="json")

# Get as pandas DataFrame
df = report.to_dataframe()

# Get as dictionary
data = report.to_dict()

# Stream as generator
for row in report.rows():
    print(row)
```

### Report Management

```python
# List reports
reports = client.reports.list(
    limit=20,
    filter_type="delivery"
)

# Get report by ID
report = client.reports.get("12345")

# Update report
report.update(
    name="Updated Report Name",
    date_range=DateRange.this_month()
)

# Delete report
report.delete()

# Clone report
cloned = report.clone("Cloned Report")
```

## Metadata Operations

```python
# Get dimensions
dimensions = client.metadata.dimensions()
for dim in dimensions:
    print(f"{dim.name}: {dim.description}")

# Search dimensions
date_dims = client.metadata.dimensions(search="date")

# Get metrics
metrics = client.metadata.metrics(category="revenue")

# Get valid combinations
combos = client.metadata.valid_combinations()
```

## Error Handling

```python
from gam_api.exceptions import (
    GAMAuthError,
    GAMRateLimitError,
    GAMReportError,
    GAMValidationError
)

try:
    report = client.reports.quick("delivery")
except GAMAuthError as e:
    print(f"Authentication failed: {e}")
    # Refresh credentials
    client.auth.refresh()
except GAMRateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}")
    time.sleep(e.retry_after)
    # Retry
except GAMReportError as e:
    print(f"Report failed: {e}")
    print(f"Report ID: {e.report_id}")
    print(f"Status: {e.status}")
```

## Advanced Features

### Pagination

```python
# Automatic pagination
all_reports = []
for page in client.reports.list().pages():
    all_reports.extend(page.items)
    print(f"Fetched page {page.number} of {page.total}")

# Manual pagination
page1 = client.reports.list(page=1, per_page=50)
page2 = page1.next_page()
```

### Batch Operations

```python
# Batch report generation
reports = [
    {"type": "delivery", "date_range": "last_week"},
    {"type": "inventory", "date_range": "last_month"},
    {"type": "sales", "date_range": "year_to_date"}
]

results = client.reports.batch_generate(reports)
for result in results:
    if result.success:
        print(f"Generated: {result.report.id}")
    else:
        print(f"Failed: {result.error}")
```

### Caching

```python
# Enable caching
client = GAMClient(config, cache_enabled=True)

# Cache metadata for 1 hour
dimensions = client.metadata.dimensions(cache_ttl=3600)

# Clear cache
client.cache.clear()
```

### Webhooks

```python
# Set up webhook for report completion
report = (
    client.reports
    .create("Large Report")
    .webhook("https://example.com/webhook")
    .run_async()
)

# Check status
status = report.status()
print(f"Report status: {status.state}")
print(f"Progress: {status.percent_complete}%")
```

## SDK Patterns

### Context Manager

```python
# Automatic cleanup with context manager
with GAMClient(config) as client:
    report = client.reports.quick("delivery")
    # Client automatically closed
```

### Retry Logic

```python
# Configure retry behavior
client = GAMClient(
    config,
    retry_config={
        "max_attempts": 5,
        "backoff_factor": 2,
        "retry_on": [500, 502, 503, 504]
    }
)
```

### Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or use custom logger
logger = logging.getLogger("my_app")
client = GAMClient(config, logger=logger)
```

### Middleware

```python
# Add custom middleware
def log_requests(request, next):
    print(f"Making request: {request.method} {request.url}")
    response = next(request)
    print(f"Response: {response.status_code}")
    return response

client.add_middleware(log_requests)
```

## Testing

### Mocking

```python
from gam_api.testing import MockGAMClient

# Create mock client
mock_client = MockGAMClient()

# Set up responses
mock_client.reports.quick.returns({
    "id": "12345",
    "status": "completed",
    "rows": 100
})

# Use in tests
result = mock_client.reports.quick("delivery")
assert result["id"] == "12345"
```

### Test Utilities

```python
from gam_api.testing import (
    create_test_report,
    generate_test_data,
    validate_report_schema
)

# Generate test data
test_data = generate_test_data(
    dimensions=["DATE", "AD_UNIT_NAME"],
    metrics=["IMPRESSIONS", "CLICKS"],
    rows=100
)

# Validate response
is_valid = validate_report_schema(response)
```

## Integration Examples

### Flask Integration

```python
from flask import Flask, jsonify
from gam_api import GAMClient

app = Flask(__name__)
client = GAMClient.from_env()

@app.route("/reports/<report_type>")
def generate_report(report_type):
    try:
        report = client.reports.quick(report_type)
        return jsonify({
            "report_id": report.id,
            "status": "processing"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### Celery Integration

```python
from celery import Celery
from gam_api import GAMClient

app = Celery("tasks")
client = GAMClient.from_env()

@app.task
def generate_report_task(report_type, date_range):
    report = client.reports.quick(report_type, date_range=date_range)
    return {
        "report_id": report.id,
        "file_path": report.download()
    }
```

### Jupyter Notebook

```python
# Interactive report exploration
from gam_api import GAMClient
import pandas as pd

client = GAMClient.from_yaml("googleads.yaml")

# Quick analysis
df = client.reports.quick("delivery").to_dataframe()
df.head()

# Visualize
df.groupby("DATE")["IMPRESSIONS"].sum().plot()
```

## Performance Tips

1. **Connection Pooling**: SDK automatically manages connection pools
2. **Streaming**: Use `stream()` for large reports
3. **Async Operations**: Use `AsyncGAMClient` for concurrent operations
4. **Caching**: Enable caching for metadata and repeated queries
5. **Batch Operations**: Use batch methods for multiple reports

## SDK Development

### Adding New Features

```python
# Extend the SDK
from gam_api import GAMClient

class CustomGAMClient(GAMClient):
    def custom_report(self, **kwargs):
        # Custom implementation
        pass
```

### Plugin System

```python
# Register custom plugins
from gam_api.plugins import register_plugin

@register_plugin("custom_formatter")
def custom_formatter(data):
    # Custom formatting logic
    return formatted_data

# Use plugin
client.reports.quick("delivery").format("custom_formatter")
```