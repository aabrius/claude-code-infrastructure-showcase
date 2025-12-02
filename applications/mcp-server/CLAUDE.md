# CLAUDE.md - GAM API MCP Server

This file provides guidance to Claude Code when working with the MCP server in this directory.

## Directory Overview

This directory contains the MCP server implementation that enables AI assistants to interact with Google Ad Manager through the REST API v1.

## Architecture

```
mcp-server/
├── main.py              # Entry point (HTTP transport only)
├── server.py            # FastMCP server with OAuth + 7 tool definitions
├── dependencies.py      # Lifespan dependency injection
├── services/
│   └── report_service.py   # Business logic (async)
├── models/
│   └── responses.py     # Pydantic response models
├── pyproject.toml       # Package config with local deps
├── googleads.yaml       # Symlink to root credentials
└── .venv/               # Isolated virtual environment
```

**Note**: Auth is ALWAYS enabled (no toggle). Uses RemoteAuthProvider + JWTVerifier matching mcp-clickhouse pattern.

## MCP Tools (6 Available)

1. **gam_quick_report** - Pre-configured reports (delivery, inventory, sales, reach, programmatic)
2. **gam_create_report** - Custom reports with dimensions/metrics
3. **gam_list_reports** - List available reports
4. **gam_get_dimensions_metrics** - Available fields for reports
5. **gam_get_common_combinations** - Common dimension-metric pairs
6. **gam_get_quick_report_types** - Quick report type descriptions

## Key Technical Details

### REST API v1 Metric Names

The server uses **REST API v1**, which has different metric names than SOAP:

| REST API v1 | SOAP API (deprecated) |
|------------|----------------------|
| `AD_SERVER_IMPRESSIONS` | `TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS` |
| `AD_SERVER_CLICKS` | `TOTAL_LINE_ITEM_LEVEL_CLICKS` |
| `AD_EXCHANGE_IMPRESSIONS` | `AD_EXCHANGE_LINE_ITEM_LEVEL_IMPRESSIONS` |
| `AD_EXCHANGE_REVENUE` | `AD_EXCHANGE_LINE_ITEM_LEVEL_REVENUE` |

### Date Range Format

REST API v1 requires the `fixed` wrapper for date ranges:

```python
"dateRange": {
    "fixed": {
        "startDate": {"year": 2025, "month": 11, "day": 30},
        "endDate": {"year": 2025, "month": 11, "day": 30}
    }
}
```

### Async Operations

All tool implementations are async. The `create_report` method in ReportService is async and uses:
```python
result = await self.client._unified_client.create_report(report_definition)
```

### Dependency Injection

Resources are initialized in `dependencies.py` via FastMCP lifespan:
- `GAMClient` - REST API client
- `CacheManager` - Result caching
- `ReportService` - Business logic

Access in tools via `ctx.fastmcp.report_service`.

## Running Locally

```bash
# Install dependencies
uv sync

# Run server (HTTP transport with OAuth - matches production)
MCP_RESOURCE_URI=http://localhost:8080 uv run python main.py

# Test with MCP Inspector (requires valid JWT)
npx @modelcontextprotocol/inspector \
  -e MCP_RESOURCE_URI=http://localhost:8080 \
  -- uv run python main.py
```

## Common Issues

1. **Mock Mode**: If `googleads.yaml` not found, server runs in mock mode. Create symlink:
   ```bash
   ln -sf ../../googleads.yaml ./googleads.yaml
   ```

2. **Invalid Metrics**: Use REST API v1 names, not SOAP names

3. **Circular Import**: Fixed by importing from `.unified.client` instead of `.unified`

4. **asyncio.run() Error**: Use `await client._unified_client.create_report()` not sync methods

## Production Deployment

- **URL**: https://gam.etus.io
- **Auth**: JWT Bearer tokens (always enabled)
- **Transport**: HTTP only

## Package Dependencies

Defined in `pyproject.toml` with local workspace packages:
```toml
[tool.uv.sources]
gam-api-core = { path = "../../packages/core" }
gam-api-shared = { path = "../../packages/shared" }
```

After modifying core/shared packages, reinstall:
```bash
uv sync --reinstall-package gam-api-core --reinstall-package gam-api-shared
```
