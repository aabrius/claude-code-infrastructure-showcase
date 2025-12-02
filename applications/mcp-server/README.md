# GAM MCP Server

Google Ad Manager MCP (Model Context Protocol) Server for AI assistants.

## Overview

This MCP server provides 6 tools for AI assistants to interact with Google Ad Manager via the REST API v1:

1. `gam_quick_report` - Generate pre-configured reports (delivery, inventory, sales, reach, programmatic)
2. `gam_create_report` - Create custom reports with specific dimensions and metrics
3. `gam_list_reports` - List existing reports
4. `gam_get_dimensions_metrics` - Get available dimensions and metrics
5. `gam_get_common_combinations` - Get common dimension-metric combinations
6. `gam_get_quick_report_types` - Get available quick report types

## Production Deployment

**Live Service**: https://gam.etus.io

- **Platform**: Google Cloud Run
- **Authentication**: JWT Bearer tokens
- **Transport**: HTTP-based
- **Scaling**: 0-10 instances based on demand

## Local Development

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- Google Ad Manager credentials (`googleads.yaml`)

### Setup

```bash
cd applications/mcp-server

# Install dependencies with uv
uv sync

# Ensure googleads.yaml is accessible (symlink or copy)
ln -sf ../../googleads.yaml ./googleads.yaml

# Run server (HTTP transport with OAuth - matches production)
MCP_RESOURCE_URI=http://localhost:8080 uv run python main.py
```

### Testing with MCP Inspector

```bash
# Test via MCP Inspector (requires valid JWT token)
npx @modelcontextprotocol/inspector \
  -e MCP_RESOURCE_URI=http://localhost:8080 \
  -- uv run python main.py
```

### Running Tests

```bash
# Run unit tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=.
```

## Authentication

**Auth is ALWAYS enabled** - there is no toggle. This matches the mcp-clickhouse pattern.

### How It Works
- **Type**: JWT Bearer tokens via RemoteAuthProvider + JWTVerifier
- **Header**: `Authorization: Bearer <jwt-token>`
- **Transport**: HTTP only (OAuth requires headers)
- **Validation**: Signature (JWKS), issuer, audience, expiration

## Tools Documentation

### gam_quick_report

Generate pre-configured reports with minimal parameters.

**Parameters**:
- `report_type`: string - One of: delivery, inventory, sales, reach, programmatic
- `days_back`: int (optional) - Number of days to look back (default: 30)
- `format`: string (optional) - Output format: json, csv, summary (default: json)

**Example**:
```json
{
    "report_type": "delivery",
    "days_back": 7,
    "format": "json"
}
```

### gam_create_report

Create custom reports with specific dimensions and metrics.

> **Important**: This tool uses **REST API v1 metric names**, which differ from SOAP API names.
> For example, use `AD_SERVER_IMPRESSIONS` instead of `TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS`.

**Parameters**:
- `name`: string - Report name
- `dimensions`: array - List of dimension names (e.g., DATE, AD_UNIT_NAME)
- `metrics`: array - List of metric names (REST API v1 format)
- `start_date`: string - Start date in YYYY-MM-DD format
- `end_date`: string - End date in YYYY-MM-DD format
- `report_type`: string (optional) - HISTORICAL, REACH, or AD_SPEED (default: HISTORICAL)
- `run_immediately`: bool (optional) - Whether to execute immediately (default: true)

**Example**:
```json
{
    "name": "My Custom Report",
    "dimensions": ["DATE", "AD_UNIT_NAME"],
    "metrics": ["AD_EXCHANGE_IMPRESSIONS", "AD_EXCHANGE_REVENUE", "AD_EXCHANGE_AVERAGE_ECPM"],
    "start_date": "2025-11-01",
    "end_date": "2025-11-30",
    "report_type": "HISTORICAL"
}
```

**Common REST API v1 Metrics**:
| Category | Metrics |
|----------|---------|
| Ad Server | `AD_SERVER_IMPRESSIONS`, `AD_SERVER_CLICKS`, `AD_SERVER_CTR` |
| Ad Exchange | `AD_EXCHANGE_IMPRESSIONS`, `AD_EXCHANGE_REVENUE`, `AD_EXCHANGE_AVERAGE_ECPM` |
| Programmatic | `PROGRAMMATIC_IMPRESSIONS`, `PROGRAMMATIC_REVENUE` |

### gam_list_reports

List available reports in the Ad Manager network.

**Parameters**:
- `limit`: int (optional) - Maximum reports to return (default: 20)

### gam_get_dimensions_metrics

Get available dimensions and metrics for reports.

**Parameters**:
- `report_type`: string (optional) - HISTORICAL, REACH, or AD_SPEED (default: HISTORICAL)
- `category`: string (optional) - dimensions, metrics, or both (default: both)

### gam_get_common_combinations

Get common dimension-metric combinations for different use cases.

**Parameters**: None

**Returns**: Pre-defined combinations for delivery analysis, inventory analysis, and revenue analysis.

### gam_get_quick_report_types

Get available quick report types with descriptions.

**Parameters**: None

## Architecture

```
mcp-server/
├── main.py            # Entry point (HTTP transport only)
├── server.py          # FastMCP server with OAuth + tool definitions
├── dependencies.py    # Lifespan dependency injection
├── services/
│   └── report_service.py  # Business logic for reports
├── models/
│   └── responses.py   # Pydantic response models
├── pyproject.toml     # Package configuration
├── Dockerfile         # Cloud Run deployment
└── README.md
```

### Key Components

- **FastMCP**: Framework for building MCP servers with decorator-based tool registration
- **ReportService**: Business logic layer, independent of MCP for testability
- **Lifespan DI**: GAMClient and cache initialized via FastMCP lifespan
- **Unified Client**: Uses REST API v1 with async support

## Deployment

### Cloud Run (Production)

```bash
# Build and deploy
gcloud builds submit --config=cloudbuild.yaml

# Update service
gcloud run services update gam-mcp-server \
    --region=us-central1 \
    --set-env-vars MCP_RESOURCE_URI=https://gam.etus.io
```

### Docker (Local)

```bash
# Build image
docker build -t gam-mcp-server .

# Run container
docker run -p 8080:8080 \
    -e MCP_RESOURCE_URI=http://localhost:8080 \
    -v $(pwd)/googleads.yaml:/app/googleads.yaml \
    gam-mcp-server
```

## Client Configuration

### Claude Desktop (Production)

```json
{
    "mcpServers": {
        "gam-api": {
            "url": "https://gam.etus.io/mcp",
            "transport": "http",
            "headers": {
                "Authorization": "Bearer <jwt-token>"
            }
        }
    }
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OAUTH_GATEWAY_URL` | OAuth authorization server | `https://ag.etus.io` |
| `MCP_RESOURCE_URI` | Your server's base URL | **Required** |
| `MCP_SERVER_HOST` | Server bind host | `0.0.0.0` |
| `MCP_SERVER_PORT` | Server bind port | `8080` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Troubleshooting

### Common Issues

1. **"GAM client not available" / Mock Mode**
   - Ensure `googleads.yaml` is accessible from the mcp-server directory
   - Check OAuth credentials are valid
   - Verify network code is correct

2. **Invalid Metric Names**
   - REST API v1 uses different metric names than SOAP API
   - Use `AD_SERVER_IMPRESSIONS` instead of `TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS`
   - Use `AD_EXCHANGE_IMPRESSIONS` instead of `AD_EXCHANGE_LINE_ITEM_LEVEL_IMPRESSIONS`

3. **asyncio.run() Error**
   - The server runs in an async context
   - Ensure all report methods use async/await

4. **Authentication Errors**
   - Check JWT token validity
   - Verify `MCP_RESOURCE_URI` matches token audience
   - Ensure OAuth gateway is reachable

### Debug Mode

```bash
# Enable debug logging
LOG_LEVEL=DEBUG MCP_RESOURCE_URI=http://localhost:8080 uv run python main.py
```

## Related Documentation

- [GAM API v1 Reference](../../docs/api/GAM_API_V1_COMPLETE_REFERENCE.md)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://gofastmcp.com)
- [Google Ad Manager API](https://developers.google.com/ad-manager)
