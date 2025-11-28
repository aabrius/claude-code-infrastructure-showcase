# GAM API - New Package Structure Guide

## 🎯 Overview

The GAM API project has been restructured to provide a clean, simple package interface that makes integration easier for other applications. This guide covers the new `gam_api` package and migration from the legacy structure.

## ✨ New Package Structure

```
gam_api/                    # Clean installable package
├── __init__.py            # Public API exports
├── client.py              # Main GAMClient class
├── pyproject.toml         # Package configuration
└── core/                  # Internal implementation

src/                       # Legacy applications (preserved)
├── api/                   # FastAPI REST API
├── mcp/                   # MCP server
├── core/                  # Core implementation (with deprecation warnings)
└── utils/                 # Utilities
```

## 🚀 Quick Start

### Installation

```bash
# Install the clean package
pip install -e .

# Or with specific features
pip install -e ".[all]"     # All features
pip install -e ".[mcp]"     # MCP server only
pip install -e ".[api]"     # REST API only
```

### Basic Usage

```python
# Clean, simple imports
from gam_api import GAMClient, DateRange, ReportBuilder

# Initialize client (automatically loads config)
client = GAMClient()

# Or with specific config
client = GAMClient(config_path="config.yaml")
# Or with dict config
client = GAMClient(config={"auth": {...}, "api": {...}})

# Quick reports
delivery_report = client.delivery_report(DateRange.last_week())
inventory_report = client.inventory_report(DateRange.last_n_days(30))

# Custom reports using builder pattern
custom_report = client.create_report(
    ReportBuilder()
    .add_dimension("DATE")
    .add_dimension("AD_UNIT_NAME")
    .add_metric("IMPRESSIONS")
    .add_metric("CLICKS")
    .set_date_range(DateRange.last_n_days(7))
    .add_filter("AD_UNIT_NAME", "CONTAINS", "Mobile")
    .build()
)

# Metadata
dimensions = client.get_available_dimensions()
metrics = client.get_available_metrics()
combinations = client.get_common_combinations()

# Utilities
is_connected = client.test_connection()
network_info = client.get_network_info()
```

## 📋 Available Methods

### Quick Report Methods

```python
# All quick report methods accept DateRange and optional parameters
client.delivery_report(date_range, **kwargs)      # Impressions, clicks, CTR, revenue
client.inventory_report(date_range, **kwargs)     # Ad requests, fill rate
client.sales_report(date_range, **kwargs)         # Revenue, eCPM by advertiser
client.reach_report(date_range, **kwargs)         # Unique reach, frequency
client.programmatic_report(date_range, **kwargs)  # Programmatic performance
```

### Custom Report Methods

```python
client.create_report(report_definition)    # Create custom report
client.list_reports(**filters)            # List existing reports
```

### Metadata Methods

```python
client.get_available_dimensions()          # List all dimensions
client.get_available_metrics()            # List all metrics  
client.get_common_combinations()           # Common dimension-metric pairs
```

### Utility Methods

```python
client.test_connection()                   # Test API connectivity
client.get_network_info()                 # GAM network information  
```

## 🛠 Helper Classes

### DateRange

```python
# Predefined ranges
DateRange.last_week()           # Last 7 days
DateRange.last_month()          # Last 30 days
DateRange.last_n_days(14)       # Last N days

# Custom range
DateRange("2024-01-01", "2024-01-31")
```

### ReportBuilder

```python
# Fluent API for building custom reports
report_def = (
    ReportBuilder()
    .add_dimension("DATE")
    .add_dimension("AD_UNIT_NAME")
    .add_metric("IMPRESSIONS") 
    .add_metric("CLICKS")
    .set_date_range(DateRange.last_week())
    .add_filter("AD_UNIT_NAME", "CONTAINS", "Mobile")
    .build()
)
```

## 🔄 Migration Guide

### From Legacy Imports

```python
# OLD (deprecated) ❌
from src.core.unified.client import GAMUnifiedClient
from src.core.unified import create_unified_client
from src.core.models import DateRange, ReportDefinition

unified_client = GAMUnifiedClient(config)
report = unified_client.generate_quick_report("delivery", {...})

# NEW (recommended) ✅
from gam_api import GAMClient, DateRange, ReportBuilder

client = GAMClient(config)
report = client.delivery_report(DateRange.last_week())
```

### Method Name Changes

| Legacy Method | New Method |
|---------------|------------|
| `generate_quick_report("delivery", ...)` | `delivery_report(DateRange(...))` |
| `generate_quick_report("inventory", ...)` | `inventory_report(DateRange(...))` |
| `create_custom_report(...)` | `create_report(ReportBuilder().build())` |
| `get_reports()` | `list_reports()` |
| `get_dimensions()` | `get_available_dimensions()` |
| `get_metrics()` | `get_available_metrics()` |

### Configuration Changes

```python
# OLD ❌
from src.core.config import load_config
from src.core.unified.client import GAMUnifiedClient

config = load_config("config.yaml")
client = GAMUnifiedClient(config=config)

# NEW ✅  
from gam_api import GAMClient

# Automatic config loading
client = GAMClient()

# Or explicit config path
client = GAMClient(config_path="config.yaml")

# Or dict config
client = GAMClient(config={
    "auth": {"client_id": "...", "client_secret": "...", ...},
    "api": {"network_code": "123456789"}
})
```

## ⚠️ Backward Compatibility

The legacy `src.*` imports will continue to work but will issue deprecation warnings:

```python
# This still works but shows deprecation warning
from src.core.unified.client import GAMUnifiedClient
```

**Timeline**: Legacy imports will be supported for at least 6 months to allow gradual migration.

## 🧪 Error Handling

```python
from gam_api import GAMClient, APIError, AuthenticationError, ReportGenerationError

client = GAMClient()

try:
    report = client.delivery_report(DateRange.last_week())
except AuthenticationError:
    print("Authentication failed - check credentials")
except ReportGenerationError as e:
    print(f"Report generation failed: {e}")
except APIError as e:
    print(f"API error: {e}")
```

## 📦 Package Features

### Optional Dependencies

```bash
# Core functionality only
pip install -e .

# With MCP server support
pip install -e ".[mcp]"

# With REST API support  
pip install -e ".[api]"

# With Excel export support
pip install -e ".[excel]"

# Everything
pip install -e ".[all]"
```

### Entry Points

```python
# Quick start function
from gam_api import quick_start
client = quick_start()  # Uses default config

# Factory function
from gam_api import create_client
client = create_client(config_path="config.yaml")

# Direct import (recommended)
from gam_api import GAMClient
client = GAMClient()
```

## 🎯 Benefits of New Structure

1. **Simple Imports**: Single `from gam_api import GAMClient`
2. **Clean API**: Intuitive method names and fluent builders
3. **Easy Integration**: Other applications can install and use in minutes
4. **Backward Compatible**: Existing code continues to work (with warnings)
5. **Modular**: Install only the features you need
6. **Type Safe**: Full type hints for better IDE support
7. **Self-Documenting**: Clear method names and docstrings

## 🔍 Examples

### Company Application Integration

```python
# requirements.txt
gam-api>=1.0.0

# application.py
from gam_api import GAMClient, DateRange

def get_weekly_delivery_metrics():
    client = GAMClient()  # Auto-loads config
    return client.delivery_report(DateRange.last_week())

def get_custom_metrics():
    client = GAMClient()
    return client.create_report(
        ReportBuilder()
        .add_dimension("DATE")
        .add_dimension("ADVERTISER_NAME")
        .add_metric("REVENUE")
        .add_metric("IMPRESSIONS")
        .set_date_range(DateRange.last_n_days(30))
        .build()
    )
```

### Data Analysis Script

```python
from gam_api import GAMClient, DateRange
import pandas as pd

# Initialize client
client = GAMClient()

# Get multiple report types
delivery = client.delivery_report(DateRange.last_month())
inventory = client.inventory_report(DateRange.last_month())
sales = client.sales_report(DateRange.last_month())

# Convert to DataFrames for analysis
delivery_df = pd.DataFrame(delivery['rows'])
inventory_df = pd.DataFrame(inventory['rows']) 
sales_df = pd.DataFrame(sales['rows'])

# Your analysis code here...
```

## 🆘 Troubleshooting

### Import Errors

```python
# If you see: ModuleNotFoundError: No module named 'gam_api'
# Run: pip install -e .

# If you see: ImportError: No module named 'src'
# Make sure you're running from the project root directory
```

### Configuration Issues

```python
# If client initialization fails, check your config
from gam_api import GAMClient

try:
    client = GAMClient()
except Exception as e:
    client = GAMClient(config_path="path/to/config.yaml")
    # Or check if config file exists and has correct format
```

### Legacy Code Warnings

```python
# If you see deprecation warnings, migrate to new imports:
# OLD: from src.core.unified.client import GAMUnifiedClient
# NEW: from gam_api import GAMClient
```

## 📞 Support

For questions about the new package structure:

1. Check this guide first
2. Look at the examples in `examples/` directory  
3. Review the API documentation
4. Check existing issues in the project

The new `gam_api` package is designed to be simple and intuitive. Most use cases should work with just `GAMClient`, `DateRange`, and `ReportBuilder`.