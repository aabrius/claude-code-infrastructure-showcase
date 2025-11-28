# GAM MCP Server

Google Ad Manager MCP (Model Context Protocol) Server for AI assistants.

## 🎯 Overview

This MCP server provides 7 tools for AI assistants to interact with Google Ad Manager:

1. `gam_quick_report` - Generate pre-configured reports
2. `gam_create_report` - Create custom reports  
3. `gam_list_reports` - List existing reports
4. `gam_get_dimensions_metrics` - Get available dimensions and metrics
5. `gam_get_common_combinations` - Get common dimension-metric combinations
6. `gam_get_quick_report_types` - Get available quick report types
7. `gam_run_report` - Execute existing reports

## 🚀 Production Deployment

**Live Service**: https://gam-mcp-server-183972668403.us-central1.run.app

- **Platform**: Google Cloud Run
- **Authentication**: JWT Bearer tokens
- **Transport**: HTTP-based
- **Scaling**: 0-10 instances based on demand

## 🔧 Local Development

### Setup

```bash
# Install dependencies
pip install -e .

# Set environment variables
export GAM_CONFIG_PATH="path/to/config.yaml"
export MCP_AUTH_ENABLED="false"  # Disable auth for local dev

# Run server
python fastmcp_server.py
```

### Configuration

The server uses the `gam_api` package for GAM integration:

```python
from gam_api import GAMClient, DateRange, ReportBuilder

# Server automatically initializes client
client = GAMClient()  # Loads config from GAM_CONFIG_PATH
```

### Testing

```bash
# Test MCP tools
python -m pytest tests/

# Test with MCP client
# Use the tools via any MCP-compatible client
```

## 🔐 Authentication

### Production (Cloud Run)
- **Type**: JWT Bearer tokens using FastMCP BearerAuthProvider
- **Header**: `Authorization: Bearer <jwt-token>`
- **Scopes**: Configurable via MCP_AUTH_SCOPES

### Development
- **Type**: None (set MCP_AUTH_ENABLED=false)
- **Access**: Direct HTTP calls

## 📊 Tools Documentation

### gam_quick_report
Generate pre-configured reports (delivery, inventory, sales, reach, programmatic).

**Parameters**:
- `report_type`: string - Type of report to generate
- `date_range`: object - Date range for the report
- `output_format`: string (optional) - Output format (default: "json")

**Example**:
```json
{
    "report_type": "delivery",
    "date_range": {"days_back": 7},
    "output_format": "json"
}
```

### gam_create_report  
Create custom reports with specific dimensions and metrics.

**Parameters**:
- `dimensions`: array - List of dimension names
- `metrics`: array - List of metric names  
- `date_range`: object - Date range for the report
- `filters`: array (optional) - Report filters

**Example**:
```json
{
    "dimensions": ["DATE", "AD_UNIT_NAME"],
    "metrics": ["IMPRESSIONS", "CLICKS"],
    "date_range": {"start_date": "2024-01-01", "end_date": "2024-01-31"},
    "filters": [{"field": "AD_UNIT_NAME", "operator": "CONTAINS", "value": "Mobile"}]
}
```

### gam_get_dimensions_metrics
Get lists of available dimensions and metrics.

**Parameters**: None

**Returns**:
```json
{
    "dimensions": ["DATE", "AD_UNIT_NAME", "COUNTRY_NAME", ...],
    "metrics": ["IMPRESSIONS", "CLICKS", "CTR", "REVENUE", ...]
}
```

## 🏗️ Architecture

```
MCP Server
├── fastmcp_server.py      # Main FastMCP server
├── tools/                 # MCP tool implementations
│   ├── reports.py         # Report generation tools
│   └── metadata.py        # Metadata tools
├── Dockerfile             # Cloud Run deployment
└── pyproject.toml         # Package configuration
```

### Integration with gam_api

The server uses the clean `gam_api` package:

```python
# Clean, simple integration
from gam_api import GAMClient, DateRange, ReportBuilder

async def gam_quick_report(report_type: str, date_range: dict):
    client = GAMClient()
    
    # Convert to DateRange object
    if "days_back" in date_range:
        dr = DateRange.last_n_days(date_range["days_back"])
    else:
        dr = DateRange(date_range["start_date"], date_range["end_date"])
    
    # Use the clean API
    if report_type == "delivery":
        return client.delivery_report(dr)
    elif report_type == "inventory":
        return client.inventory_report(dr)
    # ... etc
```

## 🚀 Deployment

### Cloud Run (Production)

```bash
# Build and deploy
gcloud builds submit --config=cloudbuild.yaml

# Update service
gcloud run services update gam-mcp-server \
    --region=us-central1 \
    --set-env-vars MCP_AUTH_ENABLED=true
```

### Docker (Local)

```bash
# Build image
docker build -t gam-mcp-server .

# Run container
docker run -p 8000:8000 \
    -e GAM_CONFIG_PATH=/config/config.yaml \
    -e MCP_AUTH_ENABLED=false \
    -v $(pwd)/config:/config \
    gam-mcp-server
```

## 📝 Client Configuration

### Claude Desktop

```json
{
    "mcpServers": {
        "gam-api": {
            "url": "https://gam-mcp-server-183972668403.us-central1.run.app/mcp",
            "transport": "http",
            "headers": {
                "Authorization": "Bearer <jwt-token>"
            }
        }
    }
}
```

### Local Development

```json
{
    "mcpServers": {
        "gam-api-local": {
            "url": "http://localhost:8000/mcp",
            "transport": "http"
        }
    }
}
```

## 🔍 Monitoring

The server includes:
- **Health checks**: Built-in FastMCP health endpoints
- **Logging**: Structured logging with performance tracking
- **Metrics**: Request/response metrics
- **Error handling**: Comprehensive error reporting

## 🆘 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Check JWT token validity
   - Verify MCP_AUTH_ENABLED setting

2. **GAM API Errors**  
   - Verify GAM configuration in config.yaml
   - Check OAuth token validity
   - Ensure network code is correct

3. **Connection Issues**
   - Verify server is running and accessible
   - Check firewall settings for HTTP traffic
   - Test with curl: `curl https://gam-mcp-server-183972668403.us-central1.run.app/health`

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python fastmcp_server.py
```

## 📚 Related Documentation

- [GAM API Package Documentation](../../docs/NEW_PACKAGE_GUIDE.md)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Google Ad Manager API Documentation](https://developers.google.com/ad-manager)