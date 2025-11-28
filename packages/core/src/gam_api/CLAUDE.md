# CLAUDE.md - GAM API Core Modules

This file provides guidance to Claude Code (claude.ai/code) when working with the core modules in this directory.

## Directory Overview

This directory contains the core business logic for the Google Ad Manager API integration. These modules are used by all interfaces (CLI, API, MCP, SDK) and provide the fundamental functionality.

## Architecture

### Core Modules

- **`auth.py`**: Authentication management
  - OAuth2 flow implementation
  - Token refresh logic
  - Credential validation
  - Session management

- **`client.py`**: GAM API client
  - SOAP API client wrapper
  - REST API v1 client
  - Connection pooling
  - Request/response handling

- **`config.py`**: Configuration management
  - Multi-format support (YAML, JSON, ENV)
  - Configuration validation
  - Default values
  - Environment variable handling

- **`exceptions.py`**: Custom exceptions
  - API-specific exceptions
  - Error categorization
  - Retry logic helpers
  - Error context preservation

- **`models.py`**: Data models
  - Report definitions
  - API response models
  - Dimension/metric enums
  - Date range models

- **`reports.py`**: Report generation
  - Report job creation
  - Status monitoring
  - Result downloading
  - Format conversion

## Key Classes and Functions

### AuthManager (auth.py)

```python
from src.core.auth import AuthManager

# Initialize auth manager
auth = AuthManager(config)

# Get credentials
credentials = auth.get_credentials()

# Refresh token if needed
auth.refresh_if_needed()

# Validate credentials
is_valid = auth.validate_credentials()
```

### GAMClient (client.py)

```python
from src.core.client import GAMClient

# Initialize client
client = GAMClient(config)

# SOAP API operations
soap_client = client.get_soap_client()
report_service = soap_client.GetService('ReportService')

# REST API operations
rest_session = client.get_rest_session()
response = rest_session.get(f"{BASE_URL}/networks/{network_code}/reports")
```

### Configuration (config.py)

```python
from src.core.config import Config, load_config

# Load configuration
config = load_config("path/to/config.yaml")

# Access values
network_code = config.gam.network_code
client_id = config.auth.oauth2.client_id

# Validate configuration
config.validate()
```

### Exceptions (exceptions.py)

```python
from src.core.exceptions import (
    GAMAPIError,
    AuthenticationError,
    ConfigurationError,
    ReportGenerationError,
    RateLimitError
)

try:
    result = api_operation()
except AuthenticationError as e:
    # Handle auth errors
    print(f"Authentication failed: {e.message}")
except RateLimitError as e:
    # Handle rate limits
    time.sleep(e.retry_after)
    retry()
```

### Models (models.py)

```python
from src.core.models import (
    ReportRequest,
    DateRange,
    Dimension,
    Metric,
    ReportResult
)

# Create report request
request = ReportRequest(
    name="Delivery Report",
    dimensions=[Dimension.DATE, Dimension.AD_UNIT_NAME],
    metrics=[Metric.IMPRESSIONS, Metric.CLICKS],
    date_range=DateRange(
        start_date="2024-01-01",
        end_date="2024-01-31"
    )
)

# Process result
result = ReportResult(data=response_data)
df = result.to_dataframe()
```

### ReportGenerator (reports.py)

```python
from src.core.reports import ReportGenerator

# Initialize generator
generator = ReportGenerator(client)

# Generate report
result = generator.generate_report(
    report_type="delivery",
    date_range={"start_date": "2024-01-01", "end_date": "2024-01-31"},
    output_format="csv"
)

# Custom report
result = generator.create_custom_report(
    dimensions=["DATE", "AD_UNIT_NAME"],
    metrics=["IMPRESSIONS", "CLICKS"],
    filters=[{"field": "AD_UNIT_NAME", "operator": "CONTAINS", "value": "Mobile"}]
)
```

## Configuration Formats

### Legacy Format (googleads.yaml)

```yaml
ad_manager:
  network_code: "123456789"
  application_name: "GAM-API-Client"
  client_id: "your-client-id.apps.googleusercontent.com"
  client_secret: "your-client-secret"
  refresh_token: "your-refresh-token"
```

### New Format (agent_config.yaml)

```yaml
gam:
  network_code: "123456789"
  api_version: "v202311"

auth:
  type: "oauth2"
  oauth2:
    client_id: "your-client-id"
    client_secret: "your-client-secret"
    refresh_token: "your-refresh-token"
```

### Environment Variables

```bash
export GAM_NETWORK_CODE="123456789"
export GAM_CLIENT_ID="your-client-id"
export GAM_CLIENT_SECRET="your-client-secret"
export GAM_REFRESH_TOKEN="your-refresh-token"
```

## Error Handling Patterns

### Retry Logic

```python
from src.core.exceptions import retry_on_error

@retry_on_error(max_retries=3, backoff_factor=2)
def api_call():
    # Operation that might fail
    pass
```

### Error Context

```python
try:
    result = generator.generate_report(request)
except ReportGenerationError as e:
    print(f"Report failed: {e.message}")
    print(f"Report ID: {e.report_id}")
    print(f"Status: {e.status}")
    print(f"Details: {e.details}")
```

## Best Practices

### 1. Configuration Loading

Always use the config module for configuration:

```python
# Good
from src.core.config import load_config
config = load_config()

# Bad
import yaml
with open("config.yaml") as f:
    config = yaml.safe_load(f)
```

### 2. Client Initialization

Reuse clients to benefit from connection pooling:

```python
# Good - reuse client
client = GAMClient(config)
for report in reports:
    client.generate_report(report)

# Bad - new client each time
for report in reports:
    client = GAMClient(config)
    client.generate_report(report)
```

### 3. Error Handling

Always catch specific exceptions:

```python
# Good
try:
    result = operation()
except AuthenticationError:
    # Handle auth error
except RateLimitError as e:
    # Handle rate limit
except GAMAPIError:
    # Handle other API errors

# Bad
try:
    result = operation()
except Exception:
    # Too generic
```

### 4. Date Handling

Use the DateRange model for consistency:

```python
# Good
from src.core.models import DateRange
date_range = DateRange.last_n_days(7)

# Also good
date_range = DateRange(
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Bad
date_range = {
    "start": "2024-01-01",
    "end": "2024-01-31"
}
```

## Performance Optimization

### Connection Pooling

The client automatically manages connection pools:

```python
# Client reuses connections
client = GAMClient(config)
# Multiple requests use the same connection pool
for i in range(100):
    client.make_request()
```

### Batch Operations

```python
# Process reports in batches
from src.core.reports import batch_generate_reports

reports = [report1, report2, report3]
results = batch_generate_reports(client, reports, batch_size=10)
```

### Caching

```python
from src.utils.cache import cached

@cached(ttl=3600)  # Cache for 1 hour
def get_dimensions():
    return client.get_available_dimensions()
```

## Testing Helpers

### Mock Client

```python
from src.core.client import MockGAMClient

# For testing
mock_client = MockGAMClient()
mock_client.set_response("reports", mock_data)
```

### Test Fixtures

```python
from src.core.models import create_test_report

# Create test report
test_report = create_test_report(
    report_type="delivery",
    rows=100
)
```

## Security Considerations

1. **Credential Storage**: Never store credentials in code
2. **Token Refresh**: Always check token expiry before requests
3. **Secure Transport**: All API calls use HTTPS
4. **Scope Limitation**: Request only necessary OAuth scopes
5. **Audit Logging**: Log all API operations for security audit

## Integration Guidelines

### For CLI Integration

```python
from src.core import GAMClient, load_config

config = load_config()
client = GAMClient(config)
# Use client for operations
```

### For API Integration

```python
from src.core import GAMClient
from src.core.exceptions import GAMAPIError
from fastapi import HTTPException

try:
    result = client.generate_report(request)
except GAMAPIError as e:
    raise HTTPException(status_code=500, detail=str(e))
```

### For MCP Integration

```python
from src.core import ReportGenerator

async def mcp_tool_handler(params):
    generator = ReportGenerator(client)
    return await generator.async_generate_report(params)
```

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Check refresh token validity
   - Verify OAuth2 credentials
   - Ensure correct scopes

2. **Network Code Errors**
   - Verify network code in config
   - Check user has access to network

3. **Rate Limits**
   - Implement exponential backoff
   - Use batch operations
   - Cache frequently accessed data

4. **Report Timeouts**
   - Increase polling interval
   - Check report complexity
   - Use async operations for large reports