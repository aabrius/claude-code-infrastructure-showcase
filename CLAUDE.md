# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Google Ad Manager API integration with **modular monorepo architecture** providing MCP Server, REST API, and Python SDK for automated report generation. Uses Python 3.8+ with OAuth 2.0 and deployed to Google Cloud Run with JWT authentication.

## Current Architecture (Post AA-487 Restructuring)

### Complete Monorepo Structure
```
gam-api/
├── packages/                    # Reusable components
│   ├── core/                   # GAM API functionality (gam_api package)
│   │   └── src/gam_api/        
│   │       ├── adapters/       # API adapter implementations
│   │       │   ├── rest/       # REST API v1 adapter (async_adapter.py, analytics.py)
│   │       │   └── soap/       # Legacy SOAP adapter
│   │       └── unified/        # Unified client with fallback strategy
│   ├── sdk/                    # Python SDK (gam_sdk package)
│   │   └── src/gam_sdk/        
│   │       └── builders/       # Fluent API builders pattern
│   └── shared/                 # Utilities (gam_shared package)
│       └── src/gam_shared/     # cache.py, formatters.py, logger.py, validators.py
├── applications/               # Deployable services
│   ├── api-server/            # FastAPI REST API
│   │   └── routes/            # health.py, metadata.py, reports.py endpoints
│   ├── mcp-server/            # FastMCP server with 7 tools
│   │   ├── tools/             # metadata.py, reports.py MCP tools
│   │   └── packages/          # Symlinks to core/shared packages
│   ├── legacy-scripts/        # (Empty - reserved for legacy)
│   └── report-builder/        # (Empty - future UI builder)
├── config/                     # Configuration files
│   └── examples/              # mcp_server.yaml example
├── scripts/                    # run_coverage_report.py, run_journey_validation.sh
├── infrastructure/            # Deployment scripts and configuration
├── docs/                      # Comprehensive documentation
├── tests/                     # Unit, integration, journeys, performance
└── legacy/                    # 87-line compatibility layer
```

### Production Interfaces
- **MCP Server**: https://gam.etus.io (7 tools, JWT auth)
- **REST API**: FastAPI with 17 endpoints at http://localhost:8000/api/v1
- **Python SDK**: Fluent API for programmatic access with builders pattern

## Configuration & Setup

### Configuration Files
- **`googleads.yaml`** - OAuth2 credentials, network code (legacy SOAP format)
- **`config/agent_config.yaml`** - Enhanced multi-interface configuration
- **`pyproject.toml`** - Monorepo workspace configuration

### Quick Setup
```bash
./scripts/setup_env.sh         # Complete environment setup
pip install -e ".[all]"        # Install all features
python generate_new_token.py   # Generate OAuth token
```

### Running Services
```bash
# Development
make api        # REST API (port 8000)
make mcp        # MCP server locally  
make test       # Run test suite

# Applications (new structure)
cd applications/api-server && python main.py     # REST API
cd applications/mcp-server && python main.py  # MCP server

# Production: https://gam.etus.io
```

## API Interfaces & Features

### REST API (applications/api-server/)
Base URL: `http://localhost:8000/api/v1`
- **Reports**: `/reports/quick`, `/reports/custom`, `/reports` (list)
- **Metadata**: `/metadata/dimensions-metrics`, `/metadata/combinations`
- **Health**: `/health`, `/status`, `/version`
- **Auth**: API key via `X-API-Key` header

### MCP Tools (applications/mcp-server/)
7 tools for AI assistants with JWT authentication:
1. `gam_quick_report` - Pre-configured reports
2. `gam_create_report` - Custom reports
3. `gam_list_reports` - List available reports
4. `gam_get_dimensions_metrics` - Available dimensions/metrics
5. `gam_get_common_combinations` - Common combinations
6. `gam_get_quick_report_types` - Quick report types
7. `gam_run_report` - Execute reports

### Report Types (All Interfaces)
1. **Delivery** - Impressions, clicks, CTR, CPM, revenue
2. **Inventory** - Ad requests, fill rate, matched requests  
3. **Sales** - Revenue, eCPM by advertiser/order
4. **Reach** - Unique reach, frequency by country/device
5. **Programmatic** - Programmatic channel performance

## Package Architecture

### Core Components (packages/)
- **`gam_api`** (packages/core/) - Auth, client, models, reports, adapters (SOAP/REST)
- **`gam_sdk`** (packages/sdk/) - Fluent API with builders pattern for programmatic access
- **`gam_shared`** (packages/shared/) - Cache, formatters, logger, validators

### Key Modules & Files
- **`packages/core/src/gam_api/`**:
  - `auth.py` - OAuth2 with automatic token refresh
  - `client.py` - Unified GAM client supporting SOAP/REST with fallback
  - `adapters/rest/` - async_adapter.py, analytics.py, rest_adapter.py
  - `adapters/soap/` - soap_adapter.py for legacy SOAP API
  - `unified/` - client.py, compatibility.py, fallback.py, strategy.py
- **`packages/shared/src/gam_shared/`**: cache.py, formatters.py, logger.py, validators.py
- **`applications/api-server/routes/`**: health.py, metadata.py, reports.py
- **`applications/mcp-server/tools/`**: metadata.py, reports.py

### Production Features
- **Multi-API Support**: SOAP (legacy) + REST API v1 (beta) with fallback
- **Authentication**: OAuth2 + JWT for production MCP server
- **Caching**: Multi-level (memory + file) with TTL
- **Error Handling**: Circuit breaker pattern, comprehensive exceptions
- **Testing**: Unit, integration, journeys, performance tests

## Testing & Development

### Test Structure
```bash
pytest                    # All tests
pytest -m unit           # Unit tests  
pytest -m integration    # Integration tests
pytest -m journeys       # Journey-based user scenarios
pytest --cov=packages    # Coverage for packages
```

### Important Notes
- **Token Management**: OAuth tokens expire - use `python generate_new_token.py`
- **API Compatibility**: SOAP (stable) + REST v1 (beta) with automatic fallback
- **Async Operations**: Report generation polls for completion
- **Module Installation**: Selective dependencies via `pip install -e ".[api]"` or `".[mcp]"`

## Production Deployment

### MCP Server (Cloud Run)
- **URL**: https://gam.etus.io
- **Auth**: JWT Bearer tokens (`MCP_AUTH_ENABLED=true`)
- **Transport**: Native HTTP (FastMCP implementation)
- **Scaling**: 0-10 instances, auto-scaling
- **Deploy**: `./infrastructure/deploy/quick-deploy.sh`

### Client Configuration
```json
{
  "mcpServers": {
    "gam-api-cloud": {
      "url": "https://gam.etus.io/mcp",
      "transport": "http",
      "headers": {"Authorization": "Bearer <jwt-token-from-logs>"}
    }
  }
}
```

## File Locations (Key Development Files)

### Core Development
- **Configuration**: `googleads.yaml`, `config/agent_config.yaml`, `config/mcp_server.yaml`
- **Setup**: `./scripts/setup_env.sh`, `python generate_new_token.py`
- **Core Package**: `packages/core/src/gam_api/` (auth, client, models, adapters/)
- **Applications**: `applications/api-server/` (routes/), `applications/mcp-server/` (tools/)
- **Scripts**: `scripts/run_coverage_report.py`, `scripts/run_journey_validation.sh`

### Development Workflow
```bash
# Setup environment
./scripts/setup_env.sh && pip install -e ".[all]"

# Generate OAuth token  
python generate_new_token.py

# Run services (choose one)
make api                    # REST API
make mcp                    # MCP server
cd applications/api-server && python main.py     # Direct API
cd applications/mcp-server && python fastmcp_server.py  # Direct MCP

# Test everything
make test                   # All tests
pytest -m journeys          # User journey tests
```

### Legacy Compatibility
Preserved in `legacy/src/` (87 lines) - original `main.py` and `main_rest.py` scripts still functional via import compatibility layer.