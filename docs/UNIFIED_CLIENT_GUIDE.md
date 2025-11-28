# Unified Client Guide

The GAM Unified Client provides intelligent API selection between SOAP and REST APIs, automatic fallback mechanisms, and comprehensive error handling for Google Ad Manager operations.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Configuration](#configuration)
- [Basic Usage](#basic-usage)
- [Advanced Features](#advanced-features)
- [Migration Guide](#migration-guide)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)

## Overview

The Unified Client automatically selects the optimal API (SOAP or REST) based on:

- **Operation type**: Different operations have different API capabilities
- **Performance metrics**: Real-time tracking of API performance
- **Context**: Operation complexity, bulk operations, metadata requests
- **Configuration**: User preferences and system settings

### Key Features

- 🧠 **Smart API Selection**: Automatic choice between SOAP and REST
- 🔄 **Automatic Fallback**: Seamless failover when primary API fails
- 📊 **Performance Tracking**: Real-time metrics and optimization
- 🛡️ **Circuit Breaker**: Protection against cascading failures
- ⚡ **Async/Sync Support**: Both programming models supported
- 🔧 **Zero Breaking Changes**: Full backward compatibility

## Installation

```bash
# Install the GAM API package
pip install -e ".[all]"

# Or install with specific features
pip install -e ".[unified]"
```

## Configuration

### Basic Configuration

Create a configuration file with your Google Ad Manager credentials:

```yaml
# config/agent_config.yaml
auth:
  network_code: "123456789"
  oauth2:
    client_id: "your-client-id.apps.googleusercontent.com"
    client_secret: "your-client-secret"
    refresh_token: "your-refresh-token"

# Optional: Unified client settings
unified:
  api_preference: null  # null (auto), "soap", or "rest"
  enable_fallback: true
  enable_performance_tracking: true
  max_retries: 3
  circuit_breaker_threshold: 5
```

### Environment Variables

You can also configure via environment variables:

```bash
export GAM_NETWORK_CODE="123456789"
export GAM_CLIENT_ID="your-client-id"
export GAM_CLIENT_SECRET="your-client-secret"
export GAM_REFRESH_TOKEN="your-refresh-token"

# Unified client settings
export GAM_UNIFIED_API_PREFERENCE="rest"
export GAM_UNIFIED_ENABLE_FALLBACK="true"
export GAM_UNIFIED_MAX_RETRIES="5"
```

### Advanced Configuration

```yaml
unified:
  # API selection preferences
  api_preference: "rest"  # Global preference
  performance_threshold: 0.8  # Switch APIs if success rate drops below
  complexity_threshold: 10  # High complexity operations use SOAP
  
  # Circuit breaker settings
  circuit_breaker_threshold: 5  # Failures before opening
  circuit_breaker_timeout: 60.0  # Recovery timeout in seconds
  
  # Retry configuration
  max_retries: 3
  base_delay: 1.0
  max_delay: 60.0
  backoff_multiplier: 2.0
  retry_strategy: "exponential"  # linear, exponential, fibonacci
  
  # Per-operation overrides
  operation_preferences:
    create_report: "rest"
    get_line_items: "soap"  # SOAP only operation
  
  operation_timeouts:
    create_report: 600  # 10 minutes
    download_report: 1800  # 30 minutes
```

## Basic Usage

### Creating a Client

```python
from src.core.unified import GAMUnifiedClient, create_unified_client

# Method 1: Using factory function
client = create_unified_client()

# Method 2: With custom configuration
client = GAMUnifiedClient(config={
    'auth': {
        'network_code': '123456789',
        'client_id': 'your-client-id',
        'client_secret': 'your-secret',
        'refresh_token': 'your-token'
    }
})

# Method 3: With configuration file
client = create_unified_client('config/my_config.yaml')
```

### Basic Operations

```python
# Test connection
if await client.test_connection():
    print("Connected successfully!")

# Create a report (async)
report = await client.create_report({
    'displayName': 'Revenue Report',
    'reportDefinition': {
        'dimensions': ['DATE', 'AD_UNIT_NAME'],
        'metrics': ['IMPRESSIONS', 'CLICKS', 'REVENUE'],
        'dateRange': {
            'startDate': '2024-01-01',
            'endDate': '2024-01-31'
        }
    }
})

# Create a report (sync)
report = client.create_report_sync({
    'displayName': 'Revenue Report',
    'reportDefinition': {...}
})

# List reports
reports = await client.list_reports(limit=10)

# Get line items (automatically uses SOAP)
line_items = await client.get_line_items(
    order_id='123456',
    limit=50
)
```

### Error Handling

```python
from src.core.exceptions import (
    APIError, AuthenticationError, QuotaExceededError,
    NetworkError, ConfigurationError
)

try:
    report = await client.create_report(definition)
except AuthenticationError:
    print("Authentication failed - check credentials")
except QuotaExceededError as e:
    print(f"API quota exceeded - retry after {e.retry_after}s")
except NetworkError:
    print("Network error - will automatically retry")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except APIError as e:
    print(f"API error: {e}")
```

## Advanced Features

### API Preference Control

```python
# Set global preference
client.configure_api_preference('rest')

# Per-operation preference
report = await client.create_report(
    definition,
    api_preference='soap'  # Override for this operation
)
```

### Performance Monitoring

```python
# Get performance summary
stats = client.get_performance_summary()

print(f"Total operations: {stats['client_metrics']['total_operations']}")
print(f"Success rate: {stats['client_metrics']['successful_operations'] / stats['client_metrics']['total_operations']:.2%}")
print(f"API usage: {stats['client_metrics']['api_usage']}")

# Check adapter-specific metrics
print(f"REST success rate: {stats['strategy_performance']['rest']['success_rate']:.2%}")
print(f"SOAP success rate: {stats['strategy_performance']['soap']['success_rate']:.2%}")

# Reset statistics
client.reset_performance_stats()
```

### Adapter Availability

```python
# Check which adapters are available
if client.has_soap:
    print("SOAP adapter available")
    
if client.has_rest:
    print("REST adapter available")

# Direct adapter access (advanced users)
if client.soap_adapter:
    # Use SOAP-specific features
    service = client.soap_adapter.get_service('LineItemService')
```

### Context Manager Support

```python
# Automatic cleanup with context manager
async with GAMUnifiedClient(config) as client:
    reports = await client.list_reports()
    # Client cleanup handled automatically
```

## Migration Guide

### From Legacy GAMClient

The unified client maintains full backward compatibility:

```python
# Old code - still works!
from src.core.client import GAMClient

client = GAMClient()
reports = client.list_reports_rest()

# New unified methods available on same client
reports = client.list_reports_unified()  # Uses smart selection
performance = client.get_performance_summary()
```

### From Direct Adapter Usage

If you were using adapters directly:

```python
# Old approach
from src.core.adapters.rest import RESTAdapter
from src.core.adapters.soap import SOAPAdapter

rest_adapter = RESTAdapter(config)
soap_adapter = SOAPAdapter(config)

# Manually choose adapter
if operation_needs_soap:
    result = soap_adapter.get_line_items()
else:
    result = rest_adapter.create_report()

# New approach - automatic selection
from src.core.unified import GAMUnifiedClient

client = GAMUnifiedClient(config)
result = await client.get_line_items()  # Automatically uses SOAP
result = await client.create_report()   # Automatically uses REST
```

### Configuration Migration

```yaml
# Old format (googleads.yaml)
ad_manager:
  network_code: "123456789"
  client_id: "your-client-id"
  client_secret: "your-secret"
  refresh_token: "your-token"

# New format (agent_config.yaml) - supports more options
auth:
  network_code: "123456789"
  oauth2:
    client_id: "your-client-id"
    client_secret: "your-secret"
    refresh_token: "your-token"

unified:
  api_preference: "rest"
  enable_fallback: true
  max_retries: 5
```

## API Reference

### GAMUnifiedClient

#### Constructor

```python
GAMUnifiedClient(
    config: Optional[Union[Dict, Config]] = None,
    unified_config: Optional[UnifiedClientConfig] = None
)
```

#### Methods

##### Report Operations

- `async create_report(report_definition: Dict) -> Dict`
- `async get_report(report_id: str) -> Dict`
- `async list_reports(**filters) -> List[Dict]`
- `async get_report_status(report_id: str) -> str`
- `async download_report(report_id: str, format: str = 'CSV') -> Union[str, bytes]`
- `async delete_report(report_id: str) -> bool`

##### Line Item Operations

- `async get_line_items(**filters) -> List[Dict]`
- `async create_line_item(line_item: Dict) -> Dict`
- `async update_line_item(line_item_id: str, updates: Dict) -> Dict`
- `async delete_line_item(line_item_id: str) -> bool`

##### Inventory Operations

- `async get_ad_units(**filters) -> List[Dict]`
- `async create_ad_unit(ad_unit: Dict) -> Dict`

##### Metadata Operations

- `async get_dimensions() -> List[str]`
- `async get_metrics() -> List[str]`
- `async get_dimension_values(dimension: str, **filters) -> List[str]`

##### Utility Methods

- `async test_connection() -> bool`
- `async get_network_info() -> Dict`
- `configure_api_preference(preference: Optional[str])`
- `get_performance_summary() -> Dict`
- `reset_performance_stats()`

All async methods have synchronous equivalents with `_sync` suffix.

### Operation Types

```python
from src.core.unified.strategy import OperationType

# Available operations
OperationType.CREATE_REPORT
OperationType.GET_LINE_ITEMS
OperationType.GET_AD_UNITS
# ... and more
```

### Configuration Classes

```python
from src.core.unified import UnifiedClientConfig

config = UnifiedClientConfig(
    api_preference='rest',
    max_retries=5,
    enable_fallback=True,
    performance_threshold=0.9
)
```

## Troubleshooting

### Common Issues

#### No Adapters Available

**Error**: `No API adapters available - check authentication configuration`

**Solution**: Ensure valid credentials are configured:
```python
# Check configuration
config = load_config()
print(f"Network code: {config.auth.network_code}")
print(f"Client ID: {config.auth.client_id[:10]}...")

# Test with minimal config
client = GAMUnifiedClient({
    'auth': {
        'network_code': '123456',
        'client_id': 'valid-client-id',
        'client_secret': 'valid-secret',
        'refresh_token': 'valid-token'
    }
})
```

#### Authentication Failures

**Error**: `Authentication failed - check credentials`

**Solution**: Regenerate refresh token:
```bash
python generate_new_token.py
```

#### Circuit Breaker Open

**Error**: `Circuit breaker is OPEN - too many failures`

**Solution**: Wait for recovery timeout or reset:
```python
# Check circuit breaker status
stats = client.get_performance_summary()

# Reset if needed
client.reset_performance_stats()
```

### Debug Logging

Enable detailed logging to troubleshoot issues:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or configure specific loggers
logging.getLogger('src.core.unified').setLevel(logging.DEBUG)
logging.getLogger('src.core.unified.strategy').setLevel(logging.DEBUG)
```

### Performance Tuning

```python
# Adjust thresholds for your use case
unified_config = UnifiedClientConfig(
    # Prefer SOAP for complex operations
    complexity_threshold=5,  # Lower threshold
    
    # More aggressive circuit breaker
    circuit_breaker_threshold=3,
    circuit_breaker_timeout=30.0,
    
    # Faster retries for time-sensitive operations
    max_retries=2,
    base_delay=0.5,
    max_delay=10.0
)

client = GAMUnifiedClient(config, unified_config)
```

## Best Practices

1. **Let the client choose**: Don't override API preference unless necessary
2. **Monitor performance**: Check metrics regularly in production
3. **Handle errors gracefully**: Use specific exception types
4. **Configure appropriately**: Adjust timeouts and retries for your use case
5. **Use async when possible**: Better performance for concurrent operations

## Examples

### Complete Example: Report Generation

```python
import asyncio
from src.core.unified import create_unified_client
from src.core.exceptions import APIError

async def generate_revenue_report():
    """Generate a revenue report with error handling"""
    
    # Create client
    client = create_unified_client()
    
    try:
        # Test connection first
        if not await client.test_connection():
            raise APIError("Failed to connect to GAM API")
        
        # Create report
        report = await client.create_report({
            'displayName': 'Monthly Revenue Report',
            'reportDefinition': {
                'dimensions': ['DATE', 'AD_UNIT_NAME', 'ADVERTISER_NAME'],
                'metrics': ['IMPRESSIONS', 'CLICKS', 'CTR', 'REVENUE'],
                'dateRange': {
                    'startDate': '2024-01-01',
                    'endDate': '2024-01-31'
                },
                'filters': [{
                    'field': 'AD_UNIT_NAME',
                    'operator': 'CONTAINS',
                    'value': 'Mobile'
                }]
            }
        })
        
        print(f"Created report: {report['reportId']}")
        
        # Wait for completion
        while True:
            status = await client.get_report_status(report['reportId'])
            if status == 'COMPLETED':
                break
            elif status == 'FAILED':
                raise APIError("Report generation failed")
            
            print(f"Report status: {status}")
            await asyncio.sleep(10)
        
        # Download results
        data = await client.download_report(report['reportId'])
        print(f"Downloaded {len(data)} bytes of report data")
        
        # Get performance stats
        stats = client.get_performance_summary()
        print(f"API calls made: {stats['client_metrics']['total_operations']}")
        
        return data
        
    except Exception as e:
        print(f"Error generating report: {e}")
        raise

# Run the example
if __name__ == "__main__":
    asyncio.run(generate_revenue_report())
```

### Example: Bulk Operations with Progress

```python
async def update_line_items_bulk(client, line_item_ids, updates):
    """Update multiple line items with progress tracking"""
    
    results = []
    total = len(line_item_ids)
    
    for i, item_id in enumerate(line_item_ids):
        try:
            # Update with progress
            print(f"Updating {i+1}/{total}: {item_id}")
            
            result = await client.update_line_item(item_id, updates)
            results.append({'id': item_id, 'status': 'success'})
            
        except Exception as e:
            print(f"Failed to update {item_id}: {e}")
            results.append({'id': item_id, 'status': 'failed', 'error': str(e)})
            
            # Check if we should continue
            stats = client.get_performance_summary()
            if stats['client_metrics']['failed_operations'] > 10:
                print("Too many failures - stopping bulk update")
                break
    
    # Summary
    successful = sum(1 for r in results if r['status'] == 'success')
    print(f"Updated {successful}/{total} line items successfully")
    
    return results
```