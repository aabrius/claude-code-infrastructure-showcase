# CLAUDE.md - GAM API Utilities

This file provides guidance to Claude Code (claude.ai/code) when working with the utility modules in this directory.

## Directory Overview

This directory contains shared utility modules used across all interfaces (CLI, API, MCP, SDK). These utilities provide common functionality for validation, formatting, caching, and logging.

## Utility Modules

### cache.py - Caching Utilities

Provides caching functionality to improve performance and reduce API calls.

```python
from src.utils.cache import Cache, cached

# Initialize cache
cache = Cache(max_size=1000, ttl=3600)

# Cache individual values
cache.set("key", value, ttl=1800)
value = cache.get("key")

# Decorator for functions
@cached(ttl=3600)
def expensive_operation():
    return fetch_from_api()

# Clear cache
cache.clear()
cache.clear_expired()
```

**Cache Backends:**
- **Memory**: Default in-memory cache
- **Redis**: For distributed caching
- **File**: For persistent caching

```python
# Redis backend
from src.utils.cache import RedisCache
cache = RedisCache(host="localhost", port=6379)

# File backend
from src.utils.cache import FileCache
cache = FileCache(directory="/tmp/gam_cache")
```

### formatters.py - Data Formatting

Formats data for different output formats and displays.

```python
from src.utils.formatters import (
    format_table,
    format_json,
    format_csv,
    format_yaml,
    format_number,
    format_date,
    humanize_bytes
)

# Table formatting
data = [{"name": "Item", "value": 100}]
print(format_table(data, headers=["Name", "Value"]))

# JSON formatting
print(format_json(data, indent=2))

# CSV formatting
csv_output = format_csv(data)

# Number formatting
print(format_number(1500000))  # "1,500,000"
print(format_number(0.0045, decimal_places=2))  # "0.00"

# Date formatting
print(format_date("2024-01-01"))  # "January 1, 2024"
print(format_date("2024-01-01", format="%Y-%m-%d"))  # "2024-01-01"

# Human-readable bytes
print(humanize_bytes(1024))  # "1.0 KB"
print(humanize_bytes(1048576))  # "1.0 MB"
```

**Report Formatters:**

```python
from src.utils.formatters import ReportFormatter

formatter = ReportFormatter()

# Format report data
formatted = formatter.format_report(
    data=report_data,
    format="table",
    options={
        "show_totals": True,
        "highlight_threshold": 1000
    }
)

# Custom formatting
class CustomFormatter(ReportFormatter):
    def format_cell(self, value, column):
        if column == "CTR":
            return f"{value:.2%}"
        return super().format_cell(value, column)
```

### logger.py - Structured Logging

Provides consistent logging across all modules.

```python
from src.utils.logger import get_logger, StructuredLogger

# Get logger for module
logger = get_logger(__name__)

# Basic logging
logger.info("Operation started", extra={"operation": "report_generation"})
logger.warning("Rate limit approaching", extra={"limit": 100, "current": 95})
logger.error("Operation failed", extra={"error_code": "AUTH_001"})

# Structured logging
structured_logger = StructuredLogger("gam-api")
structured_logger.log_event(
    "report_generated",
    {
        "report_id": "12345",
        "duration": 45.2,
        "rows": 1000
    }
)

# Context logging
with logger.context(request_id="abc123"):
    logger.info("Processing request")
    # All logs in this context include request_id
```

**Log Configuration:**

```python
from src.utils.logger import configure_logging

# Configure logging
configure_logging(
    level="INFO",
    format="json",  # or "text"
    output="file",  # or "console"
    file_path="/var/log/gam-api.log",
    rotate_size="100MB",
    backup_count=5
)
```

**Performance Logging:**

```python
from src.utils.logger import log_performance

@log_performance
def slow_operation():
    # Function execution time automatically logged
    pass

# Manual timing
from src.utils.logger import Timer

with Timer() as timer:
    perform_operation()
logger.info(f"Operation took {timer.elapsed:.2f} seconds")
```

### validators.py - Input Validation

Validates user input and API parameters.

```python
from src.utils.validators import (
    validate_date,
    validate_date_range,
    validate_dimensions,
    validate_metrics,
    validate_network_code,
    validate_email,
    ValidationError
)

# Date validation
try:
    date = validate_date("2024-01-01")
    date_range = validate_date_range("2024-01-01", "2024-01-31")
except ValidationError as e:
    print(f"Invalid date: {e}")

# Dimension/metric validation
valid_dims = validate_dimensions(["DATE", "AD_UNIT_NAME"])
valid_metrics = validate_metrics(["IMPRESSIONS", "CLICKS"])

# Network code validation
network_code = validate_network_code("123456789")

# Email validation
email = validate_email("user@example.com")
```

**Custom Validators:**

```python
from src.utils.validators import Validator, Rule

# Create custom validator
validator = Validator()

# Add rules
validator.add_rule("age", Rule.min(18))
validator.add_rule("age", Rule.max(100))
validator.add_rule("email", Rule.email())
validator.add_rule("name", Rule.required())
validator.add_rule("name", Rule.min_length(2))

# Validate data
errors = validator.validate({
    "name": "John",
    "age": 25,
    "email": "john@example.com"
})

if errors:
    print(f"Validation errors: {errors}")
```

**Dimension/Metric Compatibility:**

```python
from src.utils.validators import check_compatibility

# Check if dimensions and metrics are compatible
is_compatible = check_compatibility(
    dimensions=["DATE", "DEVICE_CATEGORY_NAME"],
    metrics=["IMPRESSIONS", "CLICKS"]
)

# Get compatible metrics for dimensions
compatible_metrics = get_compatible_metrics(["DATE", "AD_UNIT_NAME"])

# Get required dimensions for metrics
required_dims = get_required_dimensions(["UNIQUE_REACH"])
```

## Common Patterns

### Error Handling with Validation

```python
from src.utils.validators import validate_input, ValidationError

def process_report_request(params):
    try:
        validated = validate_input(params, schema={
            "report_type": {"type": "string", "required": True},
            "date_range": {"type": "date_range", "required": True},
            "dimensions": {"type": "list", "items": "dimension"}
        })
        return generate_report(validated)
    except ValidationError as e:
        logger.error("Validation failed", extra={"errors": e.errors})
        raise
```

### Caching with TTL

```python
from src.utils.cache import cached

@cached(ttl=3600, key_func=lambda x: f"report_{x}")
def get_report_definition(report_id):
    # Expensive operation cached for 1 hour
    return fetch_from_api(report_id)

# Cache with conditions
@cached(ttl=3600, condition=lambda result: result is not None)
def get_metadata():
    return fetch_metadata()
```

### Formatted Logging

```python
from src.utils.logger import get_logger
from src.utils.formatters import format_number

logger = get_logger(__name__)

def log_report_summary(report):
    logger.info(
        "Report completed",
        extra={
            "report_id": report.id,
            "rows": format_number(report.row_count),
            "duration": f"{report.duration:.2f}s",
            "impressions": format_number(report.total_impressions)
        }
    )
```

### Progressive Validation

```python
from src.utils.validators import ProgressiveValidator

validator = ProgressiveValidator()

# Stage 1: Basic validation
validator.validate_basic({
    "report_type": "delivery",
    "date_range": "last_7_days"
})

# Stage 2: Detailed validation
validator.validate_detailed({
    "dimensions": ["DATE", "AD_UNIT_NAME"],
    "metrics": ["IMPRESSIONS", "CLICKS"]
})

# Stage 3: Compatibility validation
validator.validate_compatibility()
```

## Performance Utilities

### Batch Processing

```python
from src.utils.batch import batch_process

def process_item(item):
    # Process individual item
    pass

# Process in batches
results = batch_process(
    items=large_list,
    process_func=process_item,
    batch_size=100,
    max_workers=4
)
```

### Rate Limiting

```python
from src.utils.rate_limit import RateLimiter

# Create rate limiter
limiter = RateLimiter(
    rate=100,  # 100 requests
    per=60     # per 60 seconds
)

# Use rate limiter
for request in requests:
    limiter.acquire()  # Blocks if rate limit exceeded
    make_api_call(request)
```

### Memory Management

```python
from src.utils.memory import memory_usage, sizeof

# Monitor memory usage
print(f"Current memory: {memory_usage()} MB")

# Get object size
data = load_large_dataset()
print(f"Data size: {sizeof(data)} bytes")

# Memory-efficient iteration
from src.utils.memory import chunked_reader

for chunk in chunked_reader(large_file, chunk_size=1024*1024):
    process_chunk(chunk)
```

## Integration Helpers

### Configuration Validation

```python
from src.utils.validators import validate_config

# Validate configuration file
errors = validate_config("config/agent_config.yaml")
if errors:
    logger.error("Configuration invalid", extra={"errors": errors})
    sys.exit(1)
```

### Environment Setup

```python
from src.utils.environment import setup_environment

# Setup environment
env = setup_environment(
    required_vars=["GAM_NETWORK_CODE", "GAM_CLIENT_ID"],
    defaults={
        "GAM_LOG_LEVEL": "INFO",
        "GAM_CACHE_TTL": "3600"
    }
)
```

### Testing Utilities

```python
from src.utils.testing import (
    create_mock_report,
    generate_test_data,
    temporary_config
)

# Create mock data
mock_report = create_mock_report(
    dimensions=["DATE", "AD_UNIT_NAME"],
    metrics=["IMPRESSIONS", "CLICKS"],
    rows=100
)

# Temporary config for testing
with temporary_config({"network_code": "test123"}):
    # Run tests with temporary config
    pass
```

## Best Practices

### 1. Always Validate Input

```python
# Good
validated_date = validate_date(user_input)
report = generate_report(validated_date)

# Bad
report = generate_report(user_input)  # No validation
```

### 2. Use Structured Logging

```python
# Good
logger.info("Report generated", extra={
    "report_id": report.id,
    "duration": duration,
    "user": user_id
})

# Bad
logger.info(f"Report {report.id} generated in {duration}s")
```

### 3. Cache Expensive Operations

```python
# Good
@cached(ttl=3600)
def get_available_dimensions():
    return api.fetch_dimensions()

# Bad
def get_available_dimensions():
    return api.fetch_dimensions()  # Called every time
```

### 4. Format Output Appropriately

```python
# Good
print(format_table(data, headers=columns))

# Bad
print(data)  # Raw dictionary output
```

## Troubleshooting

### Cache Issues

```python
# Debug cache
from src.utils.cache import get_cache_stats

stats = get_cache_stats()
print(f"Cache hit rate: {stats.hit_rate:.2%}")
print(f"Cache size: {stats.size}/{stats.max_size}")

# Clear specific keys
cache.delete_pattern("report_*")
```

### Logging Issues

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check log configuration
from src.utils.logger import get_log_config
config = get_log_config()
print(f"Log level: {config['level']}")
print(f"Log file: {config['file_path']}")
```

### Validation Debugging

```python
# Verbose validation
from src.utils.validators import validate_with_details

result = validate_with_details(data, schema)
if not result.is_valid:
    for error in result.errors:
        print(f"Field: {error.field}")
        print(f"Value: {error.value}")
        print(f"Error: {error.message}")
        print(f"Rule: {error.rule}")
```