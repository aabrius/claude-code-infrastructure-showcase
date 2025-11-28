# Google Ad Manager SDK - Usage Guide

A comprehensive guide to using the GAM SDK with fluent API design for automated report generation and data extraction.

## 📚 Table of Contents

- [Quick Start](#-quick-start)
- [Core Concepts](#-core-concepts)
- [Client Initialization](#-client-initialization)
- [Report Generation](#-report-generation)
- [Configuration Management](#-configuration-management)
- [Authentication](#-authentication)
- [Data Export & Manipulation](#-data-export--manipulation)
- [Error Handling](#-error-handling)
- [Advanced Patterns](#-advanced-patterns)
- [Performance Tips](#-performance-tips)
- [Production Deployment](#-production-deployment)

## 🚀 Quick Start

### Installation & Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure authentication
cp googleads.yaml.example googleads.yaml
# Edit with your GAM credentials

# Generate OAuth token
python generate_new_token.py
```

### Basic Usage

```python
from sdk import GAMClient

# Initialize client
client = GAMClient()

# Generate a quick report
report = client.quick_report('delivery', days_back=7)

# Export results
report.to_csv('delivery_report.csv')
print(f"Generated report with {len(report)} rows")
```

### Fluent API Example

```python
# Chain operations for readable, expressive code
report = (client
    .reports()
    .delivery()
    .last_30_days()
    .dimensions('DATE', 'AD_UNIT_NAME', 'LINE_ITEM_NAME')
    .metrics('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS')
    .execute())

# Manipulate and export data
top_performers = (report
    .filter(lambda row: row.get('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 0) > 10000)
    .sort('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', ascending=False)
    .head(10))

top_performers.to_excel('top_performers.xlsx')
```

## 🏗️ Core Concepts

### Fluent Interface Design

The SDK follows a fluent interface pattern that allows method chaining for readable, expressive code:

```python
# Each method returns self or a new object for continued chaining
result = (client
    .reports()          # Returns ReportBuilder
    .delivery()         # Returns ReportBuilder (configured)
    .last_7_days()      # Returns ReportBuilder (with date range)
    .execute())         # Returns ReportResult
```

### Key Components

**GAMClient**: Main entry point for all SDK operations
- Manages authentication and configuration
- Provides access to report building, config, and auth management
- Supports context manager pattern for resource cleanup

**ReportBuilder**: Fluent interface for building reports
- Method chaining for readable report configuration
- Predefined quick report types
- Custom dimension/metric selection
- Flexible date range options

**ReportResult**: Container for report data
- Pandas DataFrame integration
- Data manipulation methods (filter, sort, head, tail)
- Export to multiple formats (CSV, JSON, Excel)
- Summary statistics and analysis

## 🔧 Client Initialization

### Basic Initialization

```python
from sdk import GAMClient

# Use default configuration
client = GAMClient()

# Specify custom config file
client = GAMClient(config_path='/path/to/googleads.yaml')

# Override network code
client = GAMClient(network_code='12345678')

# Disable auto-authentication
client = GAMClient(auto_authenticate=False)
```

### Context Manager Pattern

```python
# Automatic resource cleanup
with GAMClient() as client:
    report = client.reports().delivery().execute()
    report.to_csv('output.csv')
# Client resources cleaned up automatically
```

### Configuration Dictionary (Planned)

```python
# Initialize with config dict (future feature)
config = {
    'gam': {'network_code': '12345678'},
    'oauth2': {
        'client_id': 'your_client_id',
        'client_secret': 'your_client_secret',
        'refresh_token': 'your_refresh_token'
    }
}
client = GAMClient(config=config)
```

## 📊 Report Generation

### Quick Reports

Predefined report types with sensible defaults:

```python
# Available quick report types
quick_reports = ['delivery', 'inventory', 'sales', 'reach', 'programmatic']

# Generate quick reports
delivery = client.quick_report('delivery', days_back=30)
inventory = client.quick_report('inventory', days_back=7)
sales = client.quick_report('sales', days_back=90)
```

### Fluent Report Building

#### Basic Report Structure

```python
report = (client
    .reports()
    .dimensions('DATE', 'AD_UNIT_NAME')
    .metrics('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS')
    .last_30_days()
    .execute())
```

#### Quick Report Methods

```python
# Predefined report types
delivery_report = client.reports().delivery()
inventory_report = client.reports().inventory()
sales_report = client.reports().sales()
reach_report = client.reports().reach()
programmatic_report = client.reports().programmatic()
```

#### Date Range Options

```python
# Relative date ranges
report = client.reports().delivery().last_7_days()
report = client.reports().delivery().last_30_days()
report = client.reports().delivery().last_90_days()
report = client.reports().delivery().this_month()
report = client.reports().delivery().last_month()

# Days back from today
report = client.reports().delivery().days_back(14)

# Custom date range
from datetime import date, timedelta
start_date = date.today() - timedelta(days=30)
end_date = date.today()
report = client.reports().delivery().date_range(start_date, end_date)
```

#### Dimensions and Metrics

```python
# Add multiple dimensions
report = (client
    .reports()
    .dimensions('DATE', 'AD_UNIT_NAME', 'LINE_ITEM_NAME', 'ADVERTISER_NAME')
    .metrics('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 'TOTAL_LINE_ITEM_LEVEL_CLICKS')
    .execute())

# Common dimensions
dimensions = [
    'DATE',
    'AD_UNIT_NAME',
    'LINE_ITEM_NAME',
    'ADVERTISER_NAME',
    'ORDER_NAME',
    'CREATIVE_NAME',
    'COUNTRY_NAME',
    'DEVICE_CATEGORY_NAME'
]

# Common metrics
metrics = [
    'TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS',
    'TOTAL_LINE_ITEM_LEVEL_CLICKS',
    'TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE',
    'AD_SERVER_IMPRESSIONS',
    'AD_SERVER_CLICKS',
    'AD_SERVER_CTR'
]
```

#### Report Naming and Filtering

```python
# Set report name
report = (client
    .reports()
    .delivery()
    .name("Daily Performance Report")
    .execute())

# Add filters (planned feature)
report = (client
    .reports()
    .delivery()
    .filter('AD_UNIT_NAME', 'CONTAINS', ['mobile', 'app'])
    .execute())
```

#### Report Preview

```python
# Generate preview with limited rows for quick validation
preview = (client
    .reports()
    .delivery()
    .last_30_days()
    .preview(limit=5))

print(f"Preview: {len(preview)} rows")
print(f"Columns: {preview.headers}")
```

### Report Examples

#### Delivery Performance Report

```python
delivery_report = (client
    .reports()
    .delivery()
    .last_30_days()
    .dimensions('DATE', 'AD_UNIT_NAME', 'LINE_ITEM_NAME')
    .metrics(
        'TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS',
        'TOTAL_LINE_ITEM_LEVEL_CLICKS',
        'TOTAL_LINE_ITEM_LEVEL_CPM_AND_CPC_REVENUE'
    )
    .name("30-Day Delivery Performance")
    .execute())
```

#### Inventory Analysis Report

```python
inventory_report = (client
    .reports()
    .inventory()
    .this_month()
    .dimensions('DATE', 'AD_UNIT_NAME')
    .execute())
```

#### Multi-Timeframe Comparison

```python
# Current vs previous month comparison
current_month = client.reports().sales().this_month().execute()
previous_month = client.reports().sales().last_month().execute()

print(f"Current month: {len(current_month)} rows")
print(f"Previous month: {len(previous_month)} rows")
```

## ⚙️ Configuration Management

### Reading Configuration

```python
config = client.config()

# Get values with dot notation
network_code = config.get('gam.network_code')
client_id = config.get('gam.oauth2.client_id')
timeout = config.get('api.timeout', 30)  # with default

# Show current configuration (secrets hidden)
current_config = config.show(hide_secrets=True)
print(json.dumps(current_config, indent=2))
```

### Modifying Configuration

```python
# Set individual values
config = (client
    .config()
    .set('gam.network_code', '12345678')
    .set('api.timeout', 60)
    .set('logging.level', 'DEBUG'))

# Update multiple values
config.update({
    'gam.network_code': '12345678',
    'api.timeout': 60,
    'logging.level': 'DEBUG'
})

# Check for pending changes
if config.has_pending_changes():
    changes = config.get_pending_changes()
    print(f"Pending changes: {changes}")
```

### Configuration Validation

```python
# Validate configuration
try:
    config.validate()
    print("✅ Configuration is valid")
except ConfigError as e:
    print(f"❌ Configuration validation failed: {e}")

# Get detailed validation results
validation_results = config.get_validation_results()
for field, result in validation_results.items():
    print(f"{field}: {result}")
```

### File Operations

```python
# Load from file
config.load_from_file('/path/to/config.yaml')

# Save to file
config.save_to_file('/path/to/config.yaml', format='yaml')
config.save_to_file('/path/to/config.json', format='json')

# Save with current filename
config.save_to_file()  # Uses previously loaded file path
```

### Connection Testing

```python
# Test API connection with current config
try:
    config.test_connection()
    print("✅ API connection successful")
except ConfigError as e:
    print(f"❌ Connection test failed: {e}")
```

### Change Management

```python
# Make changes without immediate application
config.set('test.setting', 'value')

# Discard pending changes
config.discard_changes()

# Reset to defaults
config.reset()
```

## 🔐 Authentication

### Authentication Status

```python
auth = client.auth()

# Check current status
auth.check_status()
status = auth.get_status()

print(f"Authenticated: {status['authenticated']}")
print(f"Credentials present: {status['credentials_present']}")
print(f"Token expiry: {status['token_expiry']}")
print(f"Errors: {status['errors']}")

# Simple authentication check
if auth.is_authenticated():
    print("✅ Ready to make API calls")
else:
    print("❌ Authentication required")
```

### Credential Management

```python
# Refresh credentials if needed
auth.refresh_if_needed()

# Force refresh
auth.refresh_if_needed(force=True)

# Chain authentication operations
auth_status = (client
    .auth()
    .check_status()
    .refresh_if_needed()
    .test_connection())
```

### Connection Testing

```python
# Test API connections
try:
    auth.test_connection()
    print("✅ API connection successful")
except AuthError as e:
    print(f"❌ Authentication failed: {e}")
except NetworkError as e:
    print(f"❌ Network error: {e}")
```

### Network Information

```python
# Get GAM network details
network_info = auth.get_network_info()
print(f"Network: {network_info['displayName']}")
print(f"Code: {network_info['networkCode']}")
print(f"Timezone: {network_info['timeZone']}")
print(f"Currency: {network_info['currencyCode']}")
```

### OAuth Scope Validation

```python
# Validate OAuth scopes
auth.validate_scopes()

# Validate custom scopes
required_scopes = [
    'https://www.googleapis.com/auth/dfp',
    'https://www.googleapis.com/auth/admanager'
]
auth.validate_scopes(required_scopes)
```

### Login and Logout

```python
# OAuth login flow (opens browser)
try:
    auth.login(
        redirect_uri='http://localhost:8080',
        open_browser=True
    )
except AuthError as e:
    print(f"Login failed: {e}")

# Logout and clear credentials
auth.logout(revoke_token=True)
```

## 📈 Data Export & Manipulation

### Report Data Structure

```python
report = client.reports().delivery().execute()

# Basic properties
print(f"Rows: {len(report)}")
print(f"Columns: {report.column_count}")
print(f"Headers: {report.headers}")
print(f"Dimensions: {report.dimension_headers}")
print(f"Metrics: {report.metric_headers}")
```

### Data Export Formats

```python
# Export to CSV
report.to_csv('report.csv')

# Export to JSON (various formats)
report.to_json('report.json', format='records')
report.to_json('report_table.json', format='table')

# Export to Excel
report.to_excel('report.xlsx', sheet_name='GAM Data')

# Chain export operations
(report
    .to_csv('report.csv')
    .to_json('report.json')
    .to_excel('report.xlsx'))
```

### Data Manipulation

#### Filtering

```python
# Filter by conditions
high_impressions = report.filter(
    lambda row: row.get('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 0) > 10000
)

# Complex filtering
active_campaigns = report.filter(
    lambda row: (
        row.get('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 0) > 1000 and
        row.get('TOTAL_LINE_ITEM_LEVEL_CLICKS', 0) > 10
    )
)
```

#### Sorting

```python
# Sort by single column
sorted_report = report.sort('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', ascending=False)

# Sort by multiple columns
sorted_report = report.sort(['DATE', 'TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS'])
```

#### Data Slicing

```python
# Get first/last rows
top_10 = report.head(10)
bottom_5 = report.tail(5)

# Get specific row range
middle_section = report[10:20]  # Slice notation
```

#### Summary Statistics

```python
# Get summary statistics
summary = report.summary()
print(f"Total rows: {summary['row_count']}")
print(f"Numeric columns: {summary['numeric_columns']}")

# Detailed statistics for numeric columns
for column, stats in summary['statistics'].items():
    print(f"{column}:")
    print(f"  Mean: {stats['mean']:.2f}")
    print(f"  Max: {stats['max']:.2f}")
    print(f"  Min: {stats['min']:.2f}")
```

### Pandas Integration

```python
# Convert to pandas DataFrame
df = report.to_dataframe()

# Use pandas operations
print(df.info())
print(df.describe())

# Pandas analysis
impression_stats = df['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS'].describe()
top_advertisers = df.groupby('ADVERTISER_NAME')['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS'].sum().head(10)
```

### Data Transformation Pipeline

```python
# Complete transformation pipeline
processed_data = (client
    .reports()
    .delivery()
    .last_30_days()
    .execute()
    .filter(lambda row: row.get('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', 0) > 5000)
    .sort('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS', ascending=False)
    .head(50))

# Export processed data
processed_data.to_excel('top_50_performers.xlsx')
```

## 🚨 Error Handling

### Exception Hierarchy

```python
from sdk.exceptions import (
    SDKError,           # Base exception
    ReportError,        # Report generation issues
    ConfigError,        # Configuration problems
    AuthError,          # Authentication failures
    ValidationError,    # Input validation failures
    NetworkError,       # Network/API communication issues
    TimeoutError,       # Operation timeouts
    RateLimitError,     # API rate limiting
    QuotaExceededError, # API quota exceeded
    PermissionError     # Insufficient permissions
)
```

### Specific Error Handling

```python
try:
    report = client.reports().delivery().execute()
except ValidationError as e:
    print(f"Invalid input: {e}")
    print(f"Field: {e.field_name}, Value: {e.field_value}")
except ReportError as e:
    print(f"Report generation failed: {e}")
    print(f"Report ID: {e.report_id}")
except AuthError as e:
    print(f"Authentication error: {e}")
    print(f"Auth step: {e.auth_step}")
except NetworkError as e:
    print(f"Network error: {e}")
    print(f"Status code: {e.status_code}")
except SDKError as e:
    print(f"SDK error: {e}")
    print(f"Error code: {e.error_code}")
    print(f"Details: {e.details}")
```

### Graceful Error Handling

```python
def generate_report_with_fallback(client, report_type, days_back=30):
    \"\"\"Generate report with fallback to simpler options.\"\"\"
    try:
        # Try primary report
        return client.quick_report(report_type, days_back)
    except ReportError:
        # Fallback to shorter time range
        try:
            return client.quick_report(report_type, days_back=7)
        except ReportError:
            # Fallback to basic delivery report
            return client.quick_report('delivery', days_back=7)

# Usage
report = generate_report_with_fallback(client, 'sales', 30)
```

### Retry Logic

```python
import time
from sdk.exceptions import RateLimitError, NetworkError

def execute_with_retry(operation, max_retries=3):
    \"\"\"Execute operation with exponential backoff retry.\"\"\"
    for attempt in range(max_retries):
        try:
            return operation()
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = e.retry_after or (2 ** attempt)
            time.sleep(wait_time)
        except NetworkError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)

# Usage
report = execute_with_retry(
    lambda: client.reports().delivery().execute()
)
```

## 🔄 Advanced Patterns

### Batch Report Generation

```python
# Generate multiple reports efficiently
report_configs = [
    ('delivery', 30),
    ('inventory', 7),
    ('sales', 90),
    ('reach', 30)
]

reports = {}
for report_type, days_back in report_configs:
    try:
        reports[report_type] = client.quick_report(report_type, days_back)
        print(f"✅ {report_type}: {len(reports[report_type])} rows")
    except ReportError as e:
        print(f"❌ {report_type} failed: {e}")
        reports[report_type] = None
```

### Configuration Profiles

```python
def load_config_profile(client, profile_name):
    \"\"\"Load configuration profile for different environments.\"\"\"
    profiles = {
        'development': {
            'api.timeout': 60,
            'logging.level': 'DEBUG',
            'cache.enabled': True
        },
        'production': {
            'api.timeout': 30,
            'logging.level': 'INFO',
            'cache.enabled': False
        }
    }
    
    if profile_name in profiles:
        client.config().update(profiles[profile_name])
        return True
    return False

# Usage
load_config_profile(client, 'production')
```

### Dynamic Report Building

```python
def build_dynamic_report(client, config_dict):
    \"\"\"Build report dynamically from configuration.\"\"\"
    builder = client.reports()
    
    # Apply report type
    if 'type' in config_dict:
        builder = getattr(builder, config_dict['type'])()
    
    # Apply date range
    if 'days_back' in config_dict:
        builder = builder.days_back(config_dict['days_back'])
    elif 'date_range' in config_dict:
        start, end = config_dict['date_range']
        builder = builder.date_range(start, end)
    
    # Apply dimensions and metrics
    if 'dimensions' in config_dict:
        builder = builder.dimensions(*config_dict['dimensions'])
    if 'metrics' in config_dict:
        builder = builder.metrics(*config_dict['metrics'])
    
    return builder.execute()

# Usage
report_config = {
    'type': 'delivery',
    'days_back': 14,
    'dimensions': ['DATE', 'AD_UNIT_NAME'],
    'metrics': ['TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS']
}
report = build_dynamic_report(client, report_config)
```

### Async-Style Operations (Future)

```python
# Planned: Async-style operations for better performance
async def generate_multiple_reports(client):
    \"\"\"Generate multiple reports concurrently.\"\"\"
    tasks = [
        client.reports().delivery().async_execute(),
        client.reports().inventory().async_execute(),
        client.reports().sales().async_execute()
    ]
    
    results = await asyncio.gather(*tasks)
    return dict(zip(['delivery', 'inventory', 'sales'], results))
```

## ⚡ Performance Tips

### Report Optimization

```python
# 1. Use preview for validation
preview = client.reports().delivery().preview(limit=5)
if len(preview) > 0:
    # Full report generation
    report = client.reports().delivery().execute()

# 2. Limit date ranges
report = client.reports().delivery().last_7_days()  # vs last_90_days()

# 3. Select only needed dimensions/metrics
report = (client
    .reports()
    .dimensions('DATE', 'AD_UNIT_NAME')  # Only essential
    .metrics('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS')  # Only essential
    .execute())

# 4. Use efficient export formats
report.to_csv('report.csv')  # Fastest
# report.to_excel('report.xlsx')  # Slower but feature-rich
```

### Memory Management

```python
# Process large reports in chunks
def process_large_report(client, chunk_size=1000):
    \"\"\"Process large report in memory-efficient chunks.\"\"\"
    report = client.reports().delivery().last_90_days().execute()
    
    total_rows = len(report)
    for start in range(0, total_rows, chunk_size):
        end = min(start + chunk_size, total_rows)
        chunk = report[start:end]
        
        # Process chunk
        process_chunk(chunk)
        
        # Clear chunk reference
        del chunk

def process_chunk(chunk):
    \"\"\"Process individual chunk.\"\"\"
    # Your processing logic here
    pass
```

### Connection Pooling

```python
# Use single client instance for multiple operations
def batch_operations(client):
    \"\"\"Perform multiple operations efficiently.\"\"\"
    results = {}
    
    # Single authentication check
    if not client.is_authenticated:
        raise AuthError("Authentication required")
    
    # Multiple reports with same client
    results['delivery'] = client.quick_report('delivery', 7)
    results['inventory'] = client.quick_report('inventory', 7)
    results['sales'] = client.quick_report('sales', 30)
    
    return results
```

## 🚀 Production Deployment

### Environment Configuration

```yaml
# production.yaml
gam:
  network_code: "123456789"
  oauth2:
    client_id: "${GAM_CLIENT_ID}"
    client_secret: "${GAM_CLIENT_SECRET}"
    refresh_token: "${GAM_REFRESH_TOKEN}"

api:
  timeout: 30
  max_retries: 3

logging:
  level: "INFO"
  format: "structured"

cache:
  enabled: false
  ttl: 300
```

### Production Client Setup

```python
import os
import logging
from sdk import GAMClient
from sdk.exceptions import SDKError

def create_production_client():
    \"\"\"Create production-ready GAM client.\"\"\"
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Initialize with production config
        client = GAMClient(
            config_path=os.getenv('GAM_CONFIG_PATH', 'production.yaml'),
            auto_authenticate=True
        )
        
        # Verify health
        status = client.test_connection()
        if status['overall_status'] != 'healthy':
            raise Exception(f"Client health check failed: {status}")
        
        return client
        
    except Exception as e:
        logging.error(f"Failed to create production client: {e}")
        raise

# Usage
client = create_production_client()
```

### Error Monitoring

```python
import logging
from datetime import datetime

def monitored_report_generation(client, report_type, days_back=30):
    \"\"\"Generate report with comprehensive monitoring.\"\"\"
    logger = logging.getLogger('gam_production')
    
    start_time = datetime.now()
    try:
        logger.info(f"Starting {report_type} report generation")
        
        report = client.quick_report(report_type, days_back)
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Report generated successfully in {duration:.2f}s: {len(report)} rows")
        
        # Performance monitoring
        if duration > 60:
            logger.warning(f"Slow report generation: {duration:.2f}s")
        
        if len(report) == 0:
            logger.warning(f"Empty report generated for {report_type}")
        
        return report
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"Report generation failed after {duration:.2f}s: {e}")
        raise
```

### Health Checks

```python
def health_check(client):
    \"\"\"Perform comprehensive health check.\"\"\"
    checks = {
        'authentication': False,
        'configuration': False,
        'network_connectivity': False,
        'api_accessibility': False
    }
    
    try:
        # Authentication check
        auth_status = client.auth().check_status().get_status()
        checks['authentication'] = auth_status['authenticated']
        
        # Configuration check
        client.config().validate()
        checks['configuration'] = True
        
        # Network connectivity
        connection_status = client.test_connection()
        checks['network_connectivity'] = connection_status['overall_status'] == 'healthy'
        
        # API accessibility (simple report)
        preview = client.reports().delivery().preview(limit=1)
        checks['api_accessibility'] = len(preview) >= 0
        
    except Exception as e:
        logging.error(f"Health check component failed: {e}")
    
    overall_health = all(checks.values())
    return {
        'healthy': overall_health,
        'checks': checks,
        'timestamp': datetime.now().isoformat()
    }
```

### Deployment Checklist

- [ ] Configure environment variables for sensitive data
- [ ] Set up structured logging with appropriate levels
- [ ] Implement health checks and monitoring
- [ ] Configure retry logic and error handling
- [ ] Set up performance monitoring and alerting
- [ ] Test with production-like data volumes
- [ ] Verify secure file permissions for exports
- [ ] Document configuration and deployment procedures
- [ ] Set up backup and recovery procedures
- [ ] Configure monitoring dashboards

---

## 📚 Additional Resources

- [Quick Start Examples](../examples/sdk_quick_start.py)
- [Advanced Usage Examples](../examples/sdk_advanced_usage.py)
- [API Reference Documentation](../CLAUDE.md)
- [GAM API v1 Beta](https://developers.google.com/ad-manager/api/beta/getting-started)
- [SOAP API Documentation](https://developers.google.com/ad-manager/api/start)

## 🤝 Support

For issues and questions:
1. Check the examples directory for usage patterns
2. Review error messages and exception details
3. Verify configuration and authentication setup
4. Consult the troubleshooting section in CLAUDE.md