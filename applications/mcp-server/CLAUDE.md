# CLAUDE.md - GAM API MCP Server

This file provides guidance to Claude Code (claude.ai/code) when working with the Model Context Protocol (MCP) server implementation in this directory.

## Directory Overview

This directory contains the MCP server implementation that enables AI assistants (like Claude) to interact with Google Ad Manager through standardized tools. MCP provides a protocol for AI models to use external tools safely and effectively.

## Recent Optimizations (✅ COMPLETED)

### Performance Enhancements
- **Cache Statistics Tracking**: Added hit/miss rate monitoring with `CacheStats` class
- **Response Time Monitoring**: Performance metrics with p50/p95/p99 percentiles
- **Cache Size Limits**: FileCache (100MB max) and MemoryCache (1000 items max)
- **LRU Eviction**: Automatic cleanup of least recently used items

### Error Handling Improvements
- **Enhanced Error Messages**: Contextual errors with suggestions and error codes
- **Structured Logging**: Request tracking with unique IDs and JSON formatting
- **Graceful Degradation**: Circuit breaker protection with cached fallbacks
- **Slow Operation Detection**: Automatic warnings for operations >5 seconds

### Documentation Updates
- **Comprehensive Tool Descriptions**: Added features, args, and return details
- **Usage Examples**: Practical examples for all MCP tools
- **Performance Monitoring Tool**: New `gam_get_performance_stats` tool

## Architecture

### Core Files

- **`fastmcp_server.py`**: FastMCP implementation (HTTP transport) - **✅ PRODUCTION DEPLOYED**
  - Native HTTP transport support
  - Decorator-based tool registration  
  - Type hint validation
  - Cloud-ready deployment
  - JWT authentication with RSA key pairs
  - **8 tools available** (includes performance stats tool)
  - Circuit breaker protection with graceful degradation
  - Comprehensive performance monitoring
  - **Service URL**: https://gam-mcp-server-183972668403.us-central1.run.app

### Tools Directory

- **`tools/reports.py`**: Report generation tools
  - `gam_quick_report`: Pre-configured reports
  - `gam_create_report`: Custom report creation
  - `gam_run_report`: Execute existing reports
  - `gam_list_reports`: List available reports

- **`tools/metadata.py`**: Metadata tools
  - `gam_get_dimensions`: List available dimensions
  - `gam_get_metrics`: List available metrics

## MCP Tools (7 Available)

The production deployment includes 7 MCP tools for comprehensive Google Ad Manager functionality:

### 1. gam_quick_report

Generate pre-configured reports with minimal parameters.

```json
{
  "name": "gam_quick_report",
  "arguments": {
    "report_type": "delivery",
    "days_back": 7
  }
}
```

**Parameters:**
- `report_type`: One of: delivery, inventory, sales, reach, programmatic
- `days_back`: Number of days to look back (optional)
- `start_date`: Start date in YYYY-MM-DD format (optional)
- `end_date`: End date in YYYY-MM-DD format (optional)

### 2. gam_create_report

Create custom reports with specific dimensions and metrics.

```json
{
  "name": "gam_create_report",
  "arguments": {
    "name": "Mobile Performance Report",
    "dimensions": ["DATE", "AD_UNIT_NAME", "DEVICE_CATEGORY_NAME"],
    "metrics": ["IMPRESSIONS", "CLICKS", "CTR"],
    "date_range": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31"
    },
    "filters": [
      {
        "field": "DEVICE_CATEGORY_NAME",
        "operator": "equals",
        "value": "Mobile"
      }
    ]
  }
}
```

**Parameters:**
- `name`: Report name
- `dimensions`: Array of dimension names
- `metrics`: Array of metric names
- `date_range`: Object with start_date and end_date
- `filters`: Array of filter objects (optional)
- `save`: Whether to save report definition (optional)

### 3. gam_run_report

Run an existing report by ID.

```json
{
  "name": "gam_run_report",
  "arguments": {
    "report_id": "12345",
    "date_override": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31"
    }
  }
}
```

**Parameters:**
- `report_id`: ID of existing report
- `date_override`: Optional date range override

### 4. gam_list_reports

List available reports with filtering options.

```json
{
  "name": "gam_list_reports",
  "arguments": {
    "limit": 10,
    "report_type": "delivery",
    "search": "mobile"
  }
}
```

**Parameters:**
- `limit`: Maximum number of reports (optional)
- `report_type`: Filter by type (optional)
- `search`: Search in report names (optional)

### 5. gam_get_dimensions

Get available dimensions with descriptions.

```json
{
  "name": "gam_get_dimensions",
  "arguments": {
    "category": "time",
    "search": "date"
  }
}
```

**Parameters:**
- `category`: Filter by category (optional)
- `search`: Search in dimension names (optional)

### 6. gam_get_dimensions_metrics

Get available dimensions and metrics with descriptions.

```json
{
  "name": "gam_get_dimensions_metrics",
  "arguments": {
    "report_type": "HISTORICAL",
    "category": "both"
  }
}
```

**Parameters:**
- `report_type`: One of: HISTORICAL, REACH, AD_SPEED (optional)
- `category`: One of: dimensions, metrics, both (optional)

### 7. gam_get_common_combinations

Get common dimension-metric combinations for different use cases.

```json
{
  "name": "gam_get_common_combinations",
  "arguments": {}
}
```

**Parameters:** None

### 8. gam_get_quick_report_types

Get available quick report types and their descriptions.

```json
{
  "name": "gam_get_quick_report_types", 
  "arguments": {}
}
```

**Parameters:** None

## Running the MCP Server

### Production Deployment (Recommended)

The FastMCP server is deployed to Google Cloud Run with JWT authentication:

```bash
# Service is running at:
https://gam-mcp-server-183972668403.us-central1.run.app

# Authentication is enabled via MCP_AUTH_ENABLED=true
# JWT tokens are issued using RSA key pairs
```

### Local Development

```bash
# Run FastMCP server locally (stdio)
python -m src.mcp.fastmcp_server

# Run with HTTP transport for testing
MCP_TRANSPORT=http PORT=8080 python -m src.mcp.fastmcp_server

# Enable authentication locally
MCP_AUTH_ENABLED=true python -m src.mcp.fastmcp_server

# Run original stdio server (legacy)
python -m src.mcp.server
```

### With MCP CLI

```bash
mcp install gam-api
mcp run gam-api
```

### Configuration

#### Production Configuration

The deployed service uses environment variables for configuration:

```bash
# Authentication
MCP_AUTH_ENABLED=true           # Enable JWT authentication
MCP_TRANSPORT=http              # Use HTTP transport
PORT=8080                       # Cloud Run port

# Google Ad Manager credentials (from Secret Manager)
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_CLIENT_SECRET=...
GOOGLE_OAUTH_REFRESH_TOKEN=...
GAM_NETWORK_CODE=...
```

#### Local Configuration

For local development, use configuration files:

```yaml
# config/agent_config.yaml
mcp:
  enabled: true
  server_name: "gam-api"
  description: "Google Ad Manager API MCP Server"
  
gam:
  network_code: "123456789"
  
auth:
  type: "oauth2"
  oauth2:
    client_id: "your-client-id"
    client_secret: "your-client-secret"
    refresh_token: "your-refresh-token"
```

## Implementation Details

### Server Structure

```python
from mcp.server import MCPServer
from mcp.types import Tool, ToolResult

class GAMServer(MCPServer):
    def __init__(self, config):
        super().__init__("gam-api")
        self.config = config
        self.client = GAMClient(config)
        self.register_tools()
    
    def register_tools(self):
        self.add_tool(self.quick_report_tool())
        self.add_tool(self.create_report_tool())
        # ... more tools
```

### Tool Implementation

```python
def quick_report_tool(self):
    return Tool(
        name="gam_quick_report",
        description="Generate a quick GAM report",
        parameters={
            "type": "object",
            "properties": {
                "report_type": {
                    "type": "string",
                    "enum": ["delivery", "inventory", "sales"]
                }
            },
            "required": ["report_type"]
        },
        handler=self.handle_quick_report
    )

async def handle_quick_report(self, params):
    try:
        result = await self.client.generate_quick_report(
            report_type=params["report_type"]
        )
        return ToolResult(success=True, data=result)
    except Exception as e:
        return ToolResult(success=False, error=str(e))
```

### Error Handling

```python
from src.core.exceptions import GAMAPIError
from mcp.types import ToolError

async def safe_handler(self, params):
    try:
        # Tool logic
        return ToolResult(success=True, data=data)
    except AuthenticationError:
        return ToolError(
            code="AUTH_FAILED",
            message="Authentication failed. Check credentials."
        )
    except RateLimitError as e:
        return ToolError(
            code="RATE_LIMIT",
            message=f"Rate limit exceeded. Retry after {e.retry_after}s"
        )
    except GAMAPIError as e:
        return ToolError(
            code="API_ERROR",
            message=str(e)
        )
```

## Tool Response Formats

### Success Response

```json
{
  "success": true,
  "data": {
    "report_id": "12345",
    "status": "completed",
    "rows": 1000,
    "file_path": "/reports/delivery_2024-01-31.csv",
    "summary": {
      "total_impressions": 1500000,
      "total_clicks": 7500,
      "average_ctr": 0.5
    }
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "INVALID_DIMENSION",
    "message": "Dimension 'INVALID_DIM' is not recognized",
    "details": {
      "available_dimensions": ["DATE", "AD_UNIT_NAME", ...]
    }
  }
}
```

## Best Practices

### 1. Async Operations

Always use async/await for long-running operations:

```python
async def handle_report(self, params):
    # Good - async operation
    result = await self.client.async_generate_report(params)
    
    # Monitor progress
    while not result.is_complete():
        await asyncio.sleep(5)
        status = await result.check_status()
        yield ToolProgress(percent=status.progress)
```

### 2. Parameter Validation

Validate parameters before processing:

```python
from src.utils.validators import validate_dimensions

def validate_params(self, params):
    # Validate dimensions
    if "dimensions" in params:
        valid, errors = validate_dimensions(params["dimensions"])
        if not valid:
            raise ValueError(f"Invalid dimensions: {errors}")
```

### 3. Progress Reporting

Report progress for long operations:

```python
async def handle_large_report(self, params):
    yield ToolProgress(0, "Initializing report...")
    
    report_id = await self.create_report(params)
    yield ToolProgress(25, f"Report created: {report_id}")
    
    await self.wait_for_completion(report_id)
    yield ToolProgress(75, "Report completed, downloading...")
    
    result = await self.download_report(report_id)
    yield ToolProgress(100, "Done!")
    
    return ToolResult(success=True, data=result)
```

### 4. Resource Management

Clean up resources properly:

```python
async def handle_with_cleanup(self, params):
    temp_file = None
    try:
        temp_file = await self.create_temp_file()
        result = await self.process_with_file(temp_file)
        return ToolResult(success=True, data=result)
    finally:
        if temp_file:
            await self.cleanup_temp_file(temp_file)
```

## Testing MCP Tools

### Using MCP Test Client

```python
from mcp.test import TestClient

async def test_quick_report():
    client = TestClient("gam-api")
    result = await client.call_tool(
        "gam_quick_report",
        {"report_type": "delivery", "days_back": 7}
    )
    assert result.success
    assert "report_id" in result.data
```

### Manual Testing

```bash
# Test server directly
echo '{"tool": "gam_quick_report", "params": {"report_type": "delivery"}}' | \
  python -m src.mcp.server

# Test with MCP CLI
mcp test gam-api gam_quick_report '{"report_type": "delivery"}'
```

## Integration with AI Assistants

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "gam-api": {
      "command": "python",
      "args": ["-m", "src.mcp.server"],
      "env": {
        "GAM_CONFIG_PATH": "/path/to/config.yaml"
      }
    }
  }
}
```

### Usage in Conversations

```
User: Can you generate a delivery report for the last week?
```

## Cloud Run Deployment

### FastMCP Deployment (Recommended)

FastMCP natively supports HTTP transport, making it ideal for Cloud Run:

```bash
# Deploy with FastMCP
export GCP_PROJECT_ID="your-project-id"
./deploy/setup-secrets.sh
./deploy/cloud-run-deploy.sh
```

The deployed service provides:
- `GET /health` - Health check endpoint
- `GET /tools` - List available MCP tools
- `POST /tool/{tool_name}` - Execute specific tool
- `POST /mcp` - Direct MCP protocol endpoint

### HTTP Endpoints

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe gam-mcp-server \
  --platform managed --region us-central1 \
  --format 'value(status.url)')

# List tools
curl ${SERVICE_URL}/tools

# Execute tool
curl -X POST ${SERVICE_URL}/tool/gam_quick_report \
  -H "Content-Type: application/json" \
  -d '{"report_type": "delivery", "days_back": 7}'
```

### Claude Desktop with Cloud Run

Configure Claude Desktop to connect to the deployed service:

```json
{
  "mcpServers": {
    "gam-api-cloud": {
      "url": "https://gam-mcp-server-183972668403.us-central1.run.app/mcp",
      "transport": "http",
      "headers": {
        "Authorization": "Bearer <JWT_TOKEN>"
      }
    }
  }
}
```

**Authentication Notes:**
- JWT tokens are automatically generated when `MCP_AUTH_ENABLED=true`
- Token is saved to `/tmp/gam-mcp-jwt-token.txt` in the container
- For production, implement proper token distribution

## Usage Examples

### Basic Report Generation

```python
# Quick delivery report for last 7 days
result = await mcp.call_tool("gam_quick_report", {
    "report_type": "delivery",
    "days_back": 7,
    "format": "json"
})

# Custom report with specific dimensions/metrics
result = await mcp.call_tool("gam_create_report", {
    "name": "Mobile CTR Analysis",
    "dimensions": ["DATE", "DEVICE_CATEGORY_NAME", "AD_UNIT_NAME"],
    "metrics": ["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "CTR"],
    "report_type": "HISTORICAL",
    "days_back": 30,
    "run_immediately": True
})
```

### Performance Monitoring

```python
# Get server performance statistics
stats = await mcp.call_tool("gam_get_performance_stats", {})

# Example response:
{
    "success": true,
    "server_stats": {
        "uptime_seconds": 3600,
        "uptime_human": "1.0 hours"
    },
    "operation_performance": {
        "gam_quick_report": {
            "count": 150,
            "errors": 2,
            "avg_time_ms": 1250.5,
            "p50_ms": 1100,
            "p95_ms": 2500,
            "p99_ms": 4500
        }
    },
    "cache_stats": {
        "hits": 120,
        "misses": 30,
        "hit_rate": 80.0
    }
}
```

### Error Handling Examples

```python
# Invalid report type - enhanced error response
result = await mcp.call_tool("gam_quick_report", {
    "report_type": "invalid_type"
})

# Response:
{
    "success": false,
    "error": {
        "type": "ValidationError",
        "message": "Invalid value for field 'report_type'",
        "code": "VAL_001",
        "details": {
            "field": "report_type",
            "provided_value": "invalid_type",
            "allowed_values": ["delivery", "inventory", "sales", "reach", "programmatic"]
        },
        "suggestions": [
            "Check the allowed values for 'report_type'",
            "Use gam_get_dimensions_metrics to see valid dimensions/metrics",
            "Refer to the API documentation for valid parameters"
        ]
    }
}
```

### Graceful Degradation

When GAM API is unavailable, the server will automatically:

1. **Use cached results** if available
2. **Indicate degraded mode** in responses
3. **Provide helpful error messages**

```python
# Response during degradation
{
    "success": true,
    "report_type": "delivery",
    "data": [...],
    "degraded_mode": true,
    "degraded_reason": "GAM API temporarily unavailable",
    "cached_at": "2024-01-15T10:30:00Z"
}
```

### Advanced Features

#### Circuit Breaker Status

The circuit breaker protects against cascading failures:

```python
# Circuit states:
# - CLOSED: Normal operation
# - OPEN: Failing, using cache/fallback
# - HALF_OPEN: Testing recovery

# After 5 consecutive failures:
# - Circuit opens for 60 seconds
# - Cached results used if available
# - Graceful error responses
```

#### Structured Logging

All operations include structured logs with:
- Unique request IDs
- Performance metrics
- Error context
- Cache hit/miss tracking

```json
{
    "timestamp": "2024-01-15T10:30:00Z",
    "level": "INFO",
    "message": "MCP tool completed",
    "request_id": "a1b2c3d4",
    "operation": "gam_quick_report",
    "duration_ms": 1250,
    "cache_hit": true,
    "success": true
}
```

## Best Practices

### 1. Use Cached Results

The server automatically caches successful results:
- Quick reports: 30 minutes
- Metadata: 1 hour
- Custom reports: Based on uniqueness

### 2. Handle Degraded Mode

Always check for `degraded_mode` in responses:

```python
if result.get("degraded_mode"):
    print(f"Using cached data: {result.get('degraded_reason')}")
```

### 3. Monitor Performance

Regularly check performance stats:

```python
# Check cache effectiveness
stats = await mcp.call_tool("gam_get_performance_stats", {})
cache_hit_rate = stats["cache_stats"]["hit_rate"]
if cache_hit_rate < 50:
    print("Consider adjusting cache TTL")

# Monitor slow operations
for op, metrics in stats["operation_performance"].items():
    if metrics["p95_ms"] > 5000:
        print(f"Operation {op} is slow: p95={metrics['p95_ms']}ms")
```

### 4. Use Common Combinations

Get pre-validated dimension/metric combinations:

```python
combinations = await mcp.call_tool("gam_get_common_combinations", {})

# Use a combination
ad_perf = combinations["combinations"]["ad_performance"]
report = await mcp.call_tool("gam_create_report", {
    "name": "Ad Performance Report",
    "dimensions": ad_perf["dimensions"],
    "metrics": ad_perf["metrics"]
})
```

## Troubleshooting

### Authentication Issues

```bash
# Check JWT token generation
gcloud logs read --service=gam-mcp-server --limit=10 | grep "Client token"

# Verify environment variables
gcloud run services describe gam-mcp-server --region=us-central1 \
  --format='value(spec.template.spec.containers[0].env[].name)'
```

### Performance Issues

```python
# Enable debug logging
export LOG_LEVEL=DEBUG
export MCP_LOG_FORMAT=json

# Check circuit breaker state
stats = await mcp.call_tool("gam_get_performance_stats", {})
print(f"Circuit state: {stats.get('circuit_breaker_state', 'unknown')}")
```

### Cache Issues

```python
# Monitor cache performance
stats = await mcp.call_tool("gam_get_performance_stats", {})
cache = stats["cache_stats"]
print(f"Hit rate: {cache['hit_rate']}%")
print(f"Total requests: {cache['hits'] + cache['misses']}")
```
