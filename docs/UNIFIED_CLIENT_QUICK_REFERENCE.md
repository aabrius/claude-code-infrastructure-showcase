# Unified Client Quick Reference

## 🚀 Quick Start

```python
from src.core.unified import create_unified_client

# Create client (auto-detects config)
client = create_unified_client()

# Basic operations
await client.test_connection()
reports = await client.list_reports()
line_items = await client.get_line_items()  # Auto-uses SOAP
```

## 🧠 Smart API Selection

| Operation | Primary API | Fallback | Notes |
|-----------|-------------|----------|-------|
| **Reports** | REST | SOAP | Better performance |
| **Line Items** | SOAP | None | SOAP exclusive |
| **Inventory** | SOAP | REST | More features in SOAP |
| **Metadata** | REST | SOAP | Cached in REST |
| **Network Info** | REST | SOAP | Simpler in REST |

## ⚙️ Configuration

### Minimal Config
```yaml
auth:
  network_code: "123456789"
  oauth2:
    client_id: "your-client-id"
    client_secret: "your-secret"
    refresh_token: "your-token"
```

### Advanced Options
```yaml
unified:
  api_preference: "rest"  # Force REST first
  enable_fallback: true   # Auto-failover
  max_retries: 5         # Retry attempts
  performance_threshold: 0.8  # Switch if <80% success
```

## 🔄 Sync/Async Operations

```python
# Async (preferred)
report = await client.create_report(definition)

# Sync equivalent
report = client.create_report_sync(definition)

# All async methods have _sync variants
```

## 🛡️ Error Handling

```python
from src.core.exceptions import *

try:
    result = await client.operation()
except AuthenticationError:
    # Check credentials
except QuotaExceededError:
    # Wait and retry
except NetworkError:
    # Automatic retry
except APIError as e:
    # General API error
    print(f"Status: {e.status_code}")
```

## 📊 Performance Monitoring

```python
# Get metrics
stats = client.get_performance_summary()

# Key metrics
total_ops = stats['client_metrics']['total_operations']
success_rate = stats['client_metrics']['successful_operations'] / total_ops
api_usage = stats['client_metrics']['api_usage']

# Reset stats
client.reset_performance_stats()
```

## 🎯 API Preference

```python
# Global preference
client.configure_api_preference('soap')

# Per-operation override
await client.create_report(
    definition,
    api_preference='rest'
)
```

## 🔍 Common Patterns

### Report Generation
```python
# Create and wait for report
report = await client.create_report({
    'displayName': 'My Report',
    'reportDefinition': {
        'dimensions': ['DATE'],
        'metrics': ['IMPRESSIONS'],
        'dateRange': {'startDate': '2024-01-01', 'endDate': '2024-01-31'}
    }
})

# Poll for completion
while True:
    status = await client.get_report_status(report['reportId'])
    if status == 'COMPLETED':
        break
    await asyncio.sleep(10)

# Download
data = await client.download_report(report['reportId'])
```

### Bulk Operations
```python
# Process multiple items
for item_id in item_ids:
    try:
        await client.update_line_item(item_id, updates)
    except APIError:
        continue  # Skip failed items
```

### Check Availability
```python
if client.has_soap and client.has_rest:
    print("Both APIs available")
elif client.has_rest:
    print("REST only mode")
elif client.has_soap:
    print("SOAP only mode")
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "No adapters available" | Check credentials in config |
| "Circuit breaker OPEN" | Too many failures - wait or reset stats |
| "Authentication failed" | Regenerate refresh token |
| Slow performance | Check `performance_threshold` setting |

## 📝 Environment Variables

```bash
# Credentials
export GAM_NETWORK_CODE="123456789"
export GAM_CLIENT_ID="your-client-id"
export GAM_CLIENT_SECRET="your-secret"
export GAM_REFRESH_TOKEN="your-token"

# Unified settings
export GAM_UNIFIED_API_PREFERENCE="rest"
export GAM_UNIFIED_MAX_RETRIES="5"
export GAM_UNIFIED_ENABLE_FALLBACK="true"
```

## 🔗 Useful Imports

```python
# Main client
from src.core.unified import GAMUnifiedClient, create_unified_client

# Configuration
from src.core.unified import UnifiedClientConfig
from src.core.config import load_config

# Exceptions
from src.core.exceptions import (
    APIError, AuthenticationError, ConfigurationError,
    QuotaExceededError, NetworkError, InvalidRequestError
)

# Operation types
from src.core.unified.strategy import OperationType, APIType
```

## 💡 Tips

1. **Let it choose**: Don't override API selection unless necessary
2. **Use async**: Better performance for concurrent operations
3. **Monitor metrics**: Check performance regularly in production
4. **Handle errors**: Use specific exception types
5. **Cache metadata**: REST caches dimensions/metrics automatically