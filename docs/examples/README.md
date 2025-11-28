# GAM SDK Examples

This directory contains comprehensive examples demonstrating the Google Ad Manager SDK's fluent API design and advanced features.

## 📁 Example Files

### 🚀 [sdk_quick_start.py](sdk_quick_start.py)
**Basic SDK usage and fluent API patterns**

Demonstrates:
- Client initialization and configuration
- Quick report generation with predefined settings
- Fluent report building with method chaining
- Configuration management
- Authentication handling
- Data export to multiple formats
- Advanced date range configurations
- Complete data analysis workflows

**Key Examples:**
```python
# Quick report generation
report = client.quick_report('delivery', days_back=7)

# Fluent report building
report = (client
    .reports()
    .delivery()
    .last_30_days()
    .dimensions('DATE', 'AD_UNIT_NAME')
    .metrics('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS')
    .execute())

# Configuration management
config = (client
    .config()
    .set('gam.network_code', '12345678')
    .validate()
    .save())
```

### 🔧 [sdk_advanced_usage.py](sdk_advanced_usage.py)
**Advanced patterns and production-ready techniques**

Demonstrates:
- Context manager usage for resource management
- Comprehensive error handling strategies
- Custom configuration scenarios
- Complex report building patterns
- Performance optimization techniques
- Production-ready deployment patterns

**Key Examples:**
```python
# Context manager usage
with GAMClient() as client:
    report = client.reports().delivery().execute()

# Error handling with specific exception types
try:
    report = client.reports().invalid_type().execute()
except ValidationError as e:
    print(f"Validation failed: {e.field_name}")

# Performance optimization
preview = client.reports().delivery().preview(limit=5)
```

### 📊 [custom_report.py](custom_report.py)
**Template for creating custom reports** (existing file)

Shows how to create specialized report types with custom logic and formatting.

## 🎯 Quick Start Guide

### 1. Prerequisites
Before running the examples, ensure you have:

```bash
# Install dependencies
pip install -r requirements.txt

# Configure authentication
cp googleads.yaml.example googleads.yaml
# Edit googleads.yaml with your credentials

# Generate OAuth token
python generate_new_token.py
```

### 2. Run Basic Examples
```bash
# Basic SDK usage patterns
python examples/sdk_quick_start.py

# Advanced usage and production patterns
python examples/sdk_advanced_usage.py
```

### 3. Expected Output Structure
```
relatorios/
├── delivery_7days.csv
├── custom_report.csv
├── custom_report.json
├── custom_report.xlsx
├── analysis/
│   ├── full_report.xlsx
│   ├── top_performers.csv
│   └── summary.json
├── advanced_scenarios/
│   ├── current_month.csv
│   ├── previous_month.csv
│   ├── detailed_analysis.xlsx
│   └── analysis_summary.json
└── production/
    └── production_report_YYYYMMDD.csv
```

## 🔍 Key SDK Features Demonstrated

### Fluent API Design
- **Method Chaining**: Chain operations for readable, expressive code
- **Intelligent Defaults**: Sensible defaults with easy customization
- **Type Safety**: Full type hints for excellent IDE support

### Report Generation
- **Quick Reports**: Predefined report types (delivery, inventory, sales, reach, programmatic)
- **Custom Reports**: Build reports with custom dimensions, metrics, and filters
- **Date Ranges**: Flexible date range options (last N days, current/last month, custom ranges)
- **Data Export**: Export to CSV, JSON, Excel formats

### Configuration Management
- **Dot Notation**: Access config values with intuitive syntax (`config.get('gam.network_code')`)
- **Validation**: Built-in validation with detailed error reporting
- **File Operations**: Load/save configuration from YAML/JSON files
- **Change Tracking**: Track and manage pending configuration changes

### Authentication
- **Status Monitoring**: Check authentication status and credential health
- **Auto-Refresh**: Automatic token refresh when needed
- **Connection Testing**: Test both SOAP and REST API connectivity
- **Scope Validation**: Verify OAuth scopes are properly configured

### Error Handling
- **Specific Exceptions**: Detailed exception hierarchy for different error types
- **Error Context**: Rich error information with context and suggestions
- **Graceful Degradation**: Fallback strategies for robust operation

### Data Manipulation
- **DataFrame Integration**: Native pandas DataFrame support
- **Filtering**: Flexible data filtering with lambda functions
- **Sorting**: Multi-column sorting capabilities
- **Analysis**: Built-in summary statistics and data analysis

## 🏗️ Architecture Overview

```
SDK Architecture:
├── GAMClient (main entry point)
│   ├── reports() → ReportBuilder (fluent report building)
│   ├── config() → ConfigManager (configuration management)
│   └── auth() → AuthManager (authentication handling)
├── ReportResult (data container with manipulation methods)
└── Exception Hierarchy (specific error types)
```

### Core Classes

**GAMClient**: Main entry point providing access to all SDK functionality
- Thread-safe initialization
- Auto-authentication support
- Context manager interface
- Connection testing and health checks

**ReportBuilder**: Fluent interface for building reports
- Method chaining for readable code
- Predefined quick report types
- Custom dimension/metric selection
- Flexible date range options

**ReportResult**: Container for report data with rich manipulation
- Pandas DataFrame integration
- Export to multiple formats
- Data filtering and sorting
- Summary statistics

**ConfigManager**: Configuration management with validation
- Dot notation access
- File I/O operations
- Change tracking
- Validation with detailed results

**AuthManager**: Authentication and connection management
- Status monitoring
- Token refresh
- Connection testing
- Network information retrieval

## 🔒 Security Best Practices

The examples demonstrate security best practices:

### Credential Management
- Secrets are never logged or displayed
- Configuration hiding for sensitive fields
- Secure file permissions for exports
- OAuth token management

### Error Handling
- No sensitive data in error messages
- Graceful degradation without data exposure
- Proper exception propagation

### Data Export
- Restrictive file permissions
- Timestamped unique filenames
- Secure directory creation

## 🚀 Production Deployment

### Configuration
```python
# Production initialization
client = GAMClient(
    config_path='/secure/path/googleads.yaml',
    auto_authenticate=True
)

# Health check before operations
status = client.test_connection()
if status['overall_status'] != 'healthy':
    # Handle degraded service
    pass
```

### Error Handling
```python
# Robust error handling
try:
    report = client.reports().delivery().execute()
except ReportError as e:
    logger.error(f"Report generation failed: {e}")
    # Implement fallback or retry logic
except AuthError as e:
    logger.error(f"Authentication failed: {e}")
    # Trigger re-authentication flow
```

### Performance Optimization
```python
# Use previews for validation
preview = client.reports().delivery().preview(limit=5)

# Efficient date ranges
report = client.reports().delivery().last_7_days().execute()

# Selective dimensions/metrics
report = (client
    .reports()
    .dimensions('DATE', 'AD_UNIT_NAME')  # Only essential
    .metrics('TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS')  # Only essential
    .execute())
```

### Logging and Monitoring
```python
import logging

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('gam_production')

# Log key operations
logger.info(f"Report generated: {len(report)} rows")
logger.warning(f"Large dataset: {len(report)} rows")
```

## 📈 Performance Guidelines

### Report Size Management
- Use `preview()` for quick validation (5-10 rows)
- Limit date ranges to necessary periods
- Select only required dimensions and metrics
- Implement pagination for large datasets

### Memory Usage
- Process reports in chunks for very large datasets
- Use streaming export for minimal memory footprint
- Clear intermediate data when not needed

### API Rate Limits
- Implement exponential backoff for retries
- Monitor API quota usage
- Use connection pooling for multiple requests

## 🛠️ Troubleshooting

### Common Issues

**Authentication Failures**
```bash
# Regenerate OAuth token
python generate_new_token.py

# Verify configuration
python -c "from sdk import GAMClient; client = GAMClient(); print(client.test_connection())"
```

**Configuration Errors**
```bash
# Validate configuration
python -c "from sdk import GAMClient; client = GAMClient(); client.config().validate()"
```

**Network Connectivity**
```bash
# Test API endpoints
python -c "from sdk import GAMClient; client = GAMClient(); client.auth().test_connection()"
```

### Debug Mode
```python
import logging
logging.getLogger('sdk').setLevel(logging.DEBUG)

# Enable debug logging for detailed operation info
client = GAMClient()
```

## 📚 Additional Resources

- [GAM API v1 Documentation](https://developers.google.com/ad-manager/api/beta/getting-started)
- [SOAP API Documentation](https://developers.google.com/ad-manager/api/start)
- [OAuth 2.0 Setup Guide](https://developers.google.com/ad-manager/api/authentication)
- [Project CLAUDE.md](../CLAUDE.md) - Complete project documentation

## 🤝 Contributing

When adding new examples:

1. Follow the established pattern structure
2. Include comprehensive error handling
3. Add detailed comments and docstrings
4. Demonstrate both basic and advanced usage
5. Update this README with new examples

## 📝 License

These examples are part of the GAM SDK project and follow the same licensing terms.