# GAM Reports MCP Server Design

**Date:** 2025-12-02
**Status:** Design Complete

## Overview

Standalone MCP Server for Google Ad Manager Report management using REST API only. Fully independent from existing packages in the monorepo.

## Goals

1. **Minimal Tools**: Goal-oriented MCP tools (7 total) to preserve LLM context
2. **Knowledge Base**: Pydantic models encoding curated dimensions/metrics and company domain knowledge
3. **Independence**: No imports from existing `gam_api`, `gam_sdk`, or `gam_shared` packages
4. **REST Only**: Uses GAM REST API v1 exclusively (no SOAP)
5. **Cloud Deployment**: Cloud Run with JWT authentication

## Architecture Decisions

### Tool Design Principles

Following Anthropic's "Writing Tools for Agents" guidance:
- **Strategic tools**: High-impact workflows, not raw endpoint exposure
- **Token efficiency**: Search over list, consolidated operations
- **Goal-oriented naming**: Tools describe what user wants to achieve

### Knowledge Base via Pydantic

- **Layer-based organization**: `dimensions.py`, `metrics.py`, `filters.py`
- **Curated allowlist**: Only dimensions/metrics relevant to our use cases
- **Domain context**: Domains, apps, ad strategies encoded as typed models
- **Search capability**: Query across all knowledge categories

## Project Structure

```
applications/gam-reports-mcp/
├── pyproject.toml                    # Standalone package
├── Dockerfile
├── deploy.sh
├── server.py                         # FastMCP entry point (7 tools)
│
├── config/
│   ├── settings.py                   # Pydantic Settings
│   ├── dimensions_metrics.yaml       # Curated allowlist + domain knowledge
│   └── templates/
│       ├── delivery.yaml
│       ├── inventory.yaml
│       ├── sales.yaml
│       └── programmatic.yaml
│
├── models/                           # Pydantic knowledge base (layer-based)
│   ├── __init__.py
│   ├── dimensions.py                 # Dimension definitions + ALLOWED_DIMENSIONS
│   ├── metrics.py                    # Metric definitions + ALLOWED_METRICS
│   ├── filters.py                    # DateRange, Domain, App, Strategy filters
│   ├── tags.py                       # Report tagging
│   ├── reports.py                    # CreateReportRequest, ReportResponse
│   ├── knowledge.py                  # Domains, Apps, Strategies (your context)
│   └── errors.py                     # APIError, AuthenticationError, etc.
│
├── endpoints/                        # One file per GAM REST endpoint
│   ├── __init__.py
│   ├── create.py                     # POST /networks/{network}/reports
│   ├── get.py                        # GET /networks/{network}/reports/{id}
│   ├── list.py                       # GET /networks/{network}/reports
│   ├── update.py                     # PATCH /networks/{network}/reports/{id}
│   ├── delete.py                     # DELETE /networks/{network}/reports/{id}
│   ├── run.py                        # POST /networks/{network}/reports/{id}:run
│   ├── fetch.py                      # POST /networks/{network}/reports/{id}/results:fetchRows
│   └── operations.py                 # GET /networks/{network}/operations/{id}
│
└── core/
    ├── __init__.py
    ├── auth.py                       # GAMAuth (standalone OAuth2)
    └── client.py                     # GAMClient (aiohttp async)
```

## MCP Tools (7 Total)

| Tool | Purpose | Parameters |
|------|---------|------------|
| `search` | Query knowledge base (dims, metrics, templates, domains, apps, strategies) | `query`, `search_in[]` |
| `create_report` | Build custom reports with validation | `dimensions[]`, `metrics[]`, `start_date`, `end_date`, `filters`, `report_name` |
| `run_and_fetch_report` | Execute and get data (handles full workflow) | `report_id`, `max_rows` |
| `get_available_options` | Full list of all options | `category` (optional) |
| `list_saved_reports` | Browse existing reports | `filter_by_tag` |
| `update_report` | Modify saved reports | `report_id`, `updates` |
| `delete_report` | Remove reports | `report_id` |

## Pydantic Knowledge Base Models

### Dimensions (`models/dimensions.py`)

```python
from enum import Enum
from pydantic import BaseModel, Field

class DimensionCategory(str, Enum):
    TIME = "time"
    INVENTORY = "inventory"
    ADVERTISER = "advertiser"
    GEOGRAPHY = "geography"
    DEVICE = "device"

class Dimension(BaseModel):
    name: str = Field(description="GAM API dimension name")
    category: DimensionCategory
    description: str = Field(description="What this dimension represents")
    use_case: str = Field(description="When to use this dimension")
    compatible_with: list[str] = Field(description="Metrics that work well with this")

ALLOWED_DIMENSIONS: dict[str, Dimension] = {
    "DATE": Dimension(
        name="DATE",
        category=DimensionCategory.TIME,
        description="Daily granularity",
        use_case="Daily performance trends",
        compatible_with=["TOTAL_IMPRESSIONS", "TOTAL_CLICKS", "TOTAL_CTR"]
    ),
    # ... curated list
}
```

### Filters (`models/filters.py`)

```python
from pydantic import BaseModel, Field
from datetime import date
from typing import Literal

class DateRangeFilter(BaseModel):
    start_date: date
    end_date: date

class DomainFilter(BaseModel):
    domains: list[str] = Field(description="Filter by your domains")

class AppFilter(BaseModel):
    app_ids: list[str] = Field(description="Your app bundle IDs")

class AdStrategyFilter(BaseModel):
    strategy: Literal["direct_sold", "programmatic", "house"]
```

### Knowledge (`models/knowledge.py`)

```python
from pydantic import BaseModel

class Domain(BaseModel):
    name: str
    ad_units: list[str]

class App(BaseModel):
    name: str
    bundle_id: str
    ad_units: list[str]

class AdStrategy(BaseModel):
    name: str
    description: str
    typical_dimensions: list[str]
    typical_metrics: list[str]

# Populated from config/dimensions_metrics.yaml
KNOWN_DOMAINS: list[Domain] = []
KNOWN_APPS: list[App] = []
AD_STRATEGIES: list[AdStrategy] = []
```

## Core Layer

### Auth (`core/auth.py`)

Standalone OAuth2 authentication aligned with existing `AuthManager` pattern:

```python
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from pathlib import Path
from pydantic import BaseModel
import yaml

class AuthConfig(BaseModel):
    client_id: str
    client_secret: str
    refresh_token: str
    network_code: str

class GAMAuth:
    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path or Path.home() / ".googleads.yaml"
        self._credentials: Credentials | None = None
        self._config: AuthConfig | None = None

    @property
    def config(self) -> AuthConfig:
        if self._config is None:
            data = yaml.safe_load(self.config_path.read_text())
            ad_manager = data.get("ad_manager", {})
            self._config = AuthConfig(**ad_manager)
        return self._config

    @property
    def network_code(self) -> str:
        return self.config.network_code

    def get_credentials(self) -> Credentials:
        if self._credentials is None or self._credentials.expired:
            self._credentials = Credentials(
                None,
                refresh_token=self.config.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.config.client_id,
                client_secret=self.config.client_secret
            )
            self._credentials.refresh(Request())
        return self._credentials
```

### Client (`core/client.py`)

Async REST client using aiohttp with connection pooling:

```python
import aiohttp
import asyncio
from typing import Any

API_BASE_URL = "https://admanager.googleapis.com/v1"

class GAMClient:
    def __init__(self, auth: GAMAuth):
        self.auth = auth
        self._session: aiohttp.ClientSession | None = None
        self._connector: aiohttp.TCPConnector | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=10,
                keepalive_timeout=30
            )
            credentials = self.auth.get_credentials()
            self._session = aiohttp.ClientSession(
                connector=self._connector,
                headers={
                    "Authorization": f"Bearer {credentials.token}",
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=300, connect=30)
            )
        return self._session

    async def _request(self, method: str, path: str, json: dict | None = None) -> dict:
        session = await self._get_session()
        url = f"{API_BASE_URL}{path}"
        async with session.request(method, url, json=json) as response:
            if response.status == 401:
                # Refresh token and retry
                credentials = self.auth.get_credentials()
                session.headers["Authorization"] = f"Bearer {credentials.token}"
                async with session.request(method, url, json=json) as retry_response:
                    retry_response.raise_for_status()
                    return await retry_response.json()
            response.raise_for_status()
            return await response.json()

    async def post(self, path: str, json: dict | None = None) -> dict:
        return await self._request("POST", path, json)

    async def get(self, path: str) -> dict:
        return await self._request("GET", path)

    async def patch(self, path: str, json: dict) -> dict:
        return await self._request("PATCH", path, json)

    async def delete(self, path: str) -> None:
        await self._request("DELETE", path)

    async def close(self):
        if self._session:
            await self._session.close()
        if self._connector:
            await self._connector.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
```

## Endpoints Layer

Each file handles one GAM REST endpoint with Pydantic validation:

### Example: `endpoints/create.py`

```python
from core.client import GAMClient
from models.reports import CreateReportRequest, ReportResponse
from models.dimensions import ALLOWED_DIMENSIONS
from models.metrics import ALLOWED_METRICS

async def create_report(
    client: GAMClient,
    network_code: str,
    request: CreateReportRequest
) -> ReportResponse:
    """POST /networks/{network}/reports"""

    # Validate against curated allowlist
    for dim in request.dimensions:
        if dim not in ALLOWED_DIMENSIONS:
            raise ValueError(f"Dimension '{dim}' not in curated allowlist")

    for metric in request.metrics:
        if metric not in ALLOWED_METRICS:
            raise ValueError(f"Metric '{metric}' not in curated allowlist")

    response = await client.post(
        f"/networks/{network_code}/reports",
        json=request.to_gam_format()
    )
    return ReportResponse.model_validate(response)
```

## MCP Server Entry Point

```python
# server.py
from fastmcp import FastMCP
from contextlib import asynccontextmanager
from core.client import GAMClient
from core.auth import GAMAuth
from config.settings import settings

@asynccontextmanager
async def lifespan(app: FastMCP):
    auth = GAMAuth(settings.credentials_path)
    async with GAMClient(auth) as client:
        app.state.client = client
        app.state.network_code = auth.network_code
        yield

mcp = FastMCP("gam-reports", lifespan=lifespan)

@mcp.tool()
async def search(query: str, search_in: list[str] | None = None) -> dict:
    """Search across dimensions, metrics, templates, and domain knowledge."""
    # Implementation searches ALLOWED_DIMENSIONS, ALLOWED_METRICS,
    # REPORT_TEMPLATES, KNOWN_DOMAINS, KNOWN_APPS, AD_STRATEGIES
    ...

@mcp.tool()
async def create_report(
    dimensions: list[str],
    metrics: list[str],
    start_date: str,
    end_date: str,
    filters: dict | None = None,
    report_name: str | None = None
) -> dict:
    """Create a new GAM report with specified dimensions and metrics."""
    ...

@mcp.tool()
async def run_and_fetch_report(report_id: str, max_rows: int = 1000) -> dict:
    """Execute a report and return the data rows."""
    ...

@mcp.tool()
async def get_available_options() -> dict:
    """Get all available dimensions, metrics, and report templates."""
    ...

@mcp.tool()
async def list_saved_reports(filter_by_tag: str | None = None) -> dict:
    """List all saved reports, optionally filtered by tag."""
    ...

@mcp.tool()
async def update_report(report_id: str, updates: dict) -> dict:
    """Update an existing report configuration."""
    ...

@mcp.tool()
async def delete_report(report_id: str) -> dict:
    """Delete a saved report."""
    ...
```

## Configuration

### Settings (`config/settings.py`)

```python
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path

class Settings(BaseSettings):
    network_code: str = Field(default="", env="GAM_NETWORK_CODE")
    credentials_path: Path = Field(
        default=Path.home() / ".googleads.yaml",
        env="GOOGLE_ADS_YAML"
    )
    mcp_transport: str = Field(default="stdio", env="MCP_TRANSPORT")
    mcp_port: int = Field(default=8080, env="MCP_PORT")
    auth_enabled: bool = Field(default=False, env="MCP_AUTH_ENABLED")
    jwt_secret: str = Field(default="", env="JWT_SECRET")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
```

## Deployment

### Dockerfile

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY config/ ./config/
COPY core/ ./core/
COPY endpoints/ ./endpoints/
COPY models/ ./models/
COPY server.py ./

RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT []
CMD ["python", "server.py"]
```

### Cloud Run Deployment

```bash
gcloud run deploy gam-reports-mcp \
  --source . \
  --region us-central1 \
  --memory 512Mi \
  --max-instances 5 \
  --set-secrets "/home/nonroot/.googleads.yaml=google-ads-yaml:latest" \
  --set-env-vars "MCP_TRANSPORT=http,MCP_AUTH_ENABLED=true"
```

## Dependencies

```toml
[project]
name = "gam-reports-mcp"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "fastmcp>=2.0.0",
    "aiohttp>=3.9.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "google-auth>=2.0.0",
    "pyyaml>=6.0.0",
]
```

## Next Steps

1. Populate `config/dimensions_metrics.yaml` with curated allowlist
2. Implement endpoint files
3. Implement MCP tools
4. Add unit tests
5. Deploy to Cloud Run
