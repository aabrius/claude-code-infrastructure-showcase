# FastMCP Complete Examples

## Table of Contents

1. [Minimal Server](#minimal-server)
2. [Production Server](#production-server)
3. [API Integration Server](#api-integration-server)
4. [Report Generation Server](#report-generation-server)

---

## Minimal Server

The simplest possible FastMCP server:

```python
from fastmcp import FastMCP

mcp = FastMCP("MinimalServer")

@mcp.tool
async def hello(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"

@mcp.tool
async def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

if __name__ == "__main__":
    mcp.run()
```

---

## Production Server

Full-featured server with auth, logging, and error handling:

```python
"""
Production MCP Server with all best practices.
"""
import os
import logging
import time
import json
import functools
from typing import List, Dict, Optional, Literal
from datetime import datetime
from collections import defaultdict

from fastmcp import FastMCP, Context
from fastmcp.server.auth import RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.exceptions import ToolError
from pydantic import Field, AnyHttpUrl
from typing_extensions import Annotated
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse

# =============================================================================
# CONFIGURATION
# =============================================================================

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
PORT = int(os.environ.get("PORT", 8080))

# OAuth Configuration
OAUTH_GATEWAY_URL = os.environ.get("OAUTH_GATEWAY_URL", "https://ag.etus.io")
MCP_RESOURCE_URI = os.environ.get("MCP_RESOURCE_URI")
OAUTH_JWKS_URI = os.environ.get("OAUTH_JWKS_URI", f"{OAUTH_GATEWAY_URL}/.well-known/jwks.json")
OAUTH_ISSUER = os.environ.get("OAUTH_ISSUER", OAUTH_GATEWAY_URL)
OAUTH_AUDIENCE = os.environ.get("OAUTH_AUDIENCE", MCP_RESOURCE_URI)

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp-server")

# =============================================================================
# PERFORMANCE TRACKING
# =============================================================================

class PerformanceMetrics:
    def __init__(self):
        self.times = defaultdict(list)
        self.counts = defaultdict(int)
        self.errors = defaultdict(int)
        self.start_time = time.time()

    def record(self, operation: str, duration: float, success: bool = True):
        self.times[operation].append(duration)
        self.counts[operation] += 1
        if not success:
            self.errors[operation] += 1

    def get_stats(self) -> dict:
        stats = {
            "uptime_seconds": time.time() - self.start_time,
            "operations": {}
        }
        for op in self.counts:
            times = self.times[op]
            stats["operations"][op] = {
                "count": self.counts[op],
                "errors": self.errors[op],
                "avg_ms": sum(times) / len(times) * 1000 if times else 0,
                "max_ms": max(times) * 1000 if times else 0
            }
        return stats

metrics = PerformanceMetrics()

def track_performance(name: str):
    """Decorator to track tool performance."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            success = True
            try:
                return await func(*args, **kwargs)
            except Exception:
                success = False
                raise
            finally:
                metrics.record(name, time.time() - start, success)
        return wrapper
    return decorator

# =============================================================================
# AUTHENTICATION
# =============================================================================

def create_auth_provider():
    """Create OAuth authentication provider with JWTVerifier."""
    if not MCP_RESOURCE_URI:
        logger.warning("MCP_RESOURCE_URI not set - authentication disabled")
        return None

    logger.info(f"Setting up OAuth authentication")
    logger.info(f"  Gateway: {OAUTH_GATEWAY_URL}")
    logger.info(f"  Resource URI: {MCP_RESOURCE_URI}")
    logger.info(f"  JWKS URI: {OAUTH_JWKS_URI}")

    # JWT Verifier validates tokens against JWKS
    token_verifier = JWTVerifier(
        jwks_uri=OAUTH_JWKS_URI,
        issuer=OAUTH_ISSUER,
        audience=OAUTH_AUDIENCE,
    )

    # Remote Auth Provider handles OAuth automatically
    return RemoteAuthProvider(
        token_verifier=token_verifier,
        authorization_servers=[AnyHttpUrl(OAUTH_GATEWAY_URL)],
        base_url=MCP_RESOURCE_URI,
    )

# =============================================================================
# ERROR HANDLING
# =============================================================================

def format_error(
    error_type: str,
    message: str,
    code: str = None,
    suggestions: List[str] = None
) -> str:
    """Format consistent error response."""
    return json.dumps({
        "success": False,
        "error": {
            "type": error_type,
            "message": message,
            "code": code,
            "timestamp": datetime.now().isoformat(),
            "suggestions": suggestions or []
        }
    }, indent=2)

def format_success(data: dict) -> str:
    """Format consistent success response."""
    return json.dumps({
        "success": True,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }, indent=2)

# =============================================================================
# SERVER SETUP
# =============================================================================

mcp = FastMCP("ProductionServer", auth=create_auth_provider())

# =============================================================================
# TOOLS
# =============================================================================

@mcp.tool
@track_performance("search")
async def search(
    query: Annotated[str, Field(min_length=1, description="Search query")],
    limit: Annotated[int, Field(ge=1, le=100, description="Max results")] = 10,
    category: Optional[str] = None,
    ctx: Context = None
) -> str:
    """Search for items with optional filtering.

    Args:
        query: The search query string
        limit: Maximum number of results (1-100)
        category: Optional category filter
    """
    if ctx:
        await ctx.info(f"Searching for: {query}")

    try:
        # Simulated search
        results = [
            {"id": i, "title": f"Result {i} for {query}", "score": 0.9 - i*0.1}
            for i in range(min(limit, 5))
        ]

        if category:
            results = [r for r in results if category in r.get("categories", [])]

        return format_success({
            "query": query,
            "count": len(results),
            "results": results
        })

    except Exception as e:
        logger.exception(f"Search failed: {e}")
        return format_error(
            "SearchError",
            str(e),
            "SEARCH_001",
            ["Check query syntax", "Try a simpler query"]
        )

@mcp.tool
@track_performance("create_item")
async def create_item(
    name: Annotated[str, Field(min_length=1, max_length=100)],
    description: str,
    tags: List[str] = None,
    ctx: Context = None
) -> str:
    """Create a new item.

    Args:
        name: Item name (1-100 characters)
        description: Item description
        tags: Optional list of tags
    """
    if ctx:
        await ctx.info(f"Creating item: {name}")

    try:
        item = {
            "id": f"item_{int(time.time())}",
            "name": name,
            "description": description,
            "tags": tags or [],
            "created_at": datetime.now().isoformat()
        }

        return format_success(item)

    except Exception as e:
        logger.exception(f"Create item failed: {e}")
        return format_error(
            "CreateError",
            str(e),
            "CREATE_001"
        )

@mcp.tool
@track_performance("batch_process")
async def batch_process(
    items: List[str],
    operation: Literal["validate", "transform", "analyze"],
    ctx: Context = None
) -> str:
    """Process multiple items with progress reporting.

    Args:
        items: List of items to process
        operation: Type of operation to perform
    """
    if not items:
        raise ToolError("Items list cannot be empty")

    results = []
    total = len(items)

    if ctx:
        await ctx.info(f"Starting batch {operation} of {total} items")

    for i, item in enumerate(items):
        if ctx:
            await ctx.report_progress(progress=i, total=total)

        # Simulated processing
        result = {"item": item, "status": "processed", "operation": operation}
        results.append(result)

    if ctx:
        await ctx.report_progress(progress=total, total=total)
        await ctx.info("Batch processing complete")

    return format_success({
        "operation": operation,
        "processed": len(results),
        "results": results
    })

@mcp.tool
@track_performance("get_stats")
async def get_performance_stats() -> str:
    """Get server performance statistics."""
    stats = metrics.get_stats()
    return format_success(stats)

# =============================================================================
# RESOURCES
# =============================================================================

# Health check (unauthenticated for load balancers)
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """Health check endpoint - intentionally unauthenticated."""
    return PlainTextResponse("OK")

# OAuth discovery endpoint (RFC 9728)
@mcp.custom_route("/.well-known/oauth-protected-resource", methods=["GET"])
async def oauth_metadata(request: Request):
    """OAuth 2.0 Protected Resource Metadata."""
    return JSONResponse({
        "resource": OAUTH_AUDIENCE,
        "authorization_servers": [OAUTH_GATEWAY_URL],
        "bearer_methods_supported": ["header"],
        "resource_name": "Production MCP Server",
    })

@mcp.resource("status://server")
def get_server_status() -> dict:
    """Current server status."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "uptime_seconds": time.time() - metrics.start_time,
        "auth_configured": MCP_RESOURCE_URI is not None
    }

@mcp.resource("config://app")
def get_app_config() -> dict:
    """Application configuration (non-sensitive)."""
    return {
        "log_level": LOG_LEVEL,
        "oauth_gateway": OAUTH_GATEWAY_URL,
        "port": PORT
    }

# =============================================================================
# PROMPTS
# =============================================================================

@mcp.prompt
def analysis_prompt(data: str, focus: str = "general") -> str:
    """Generate data analysis prompt."""
    return f"""Analyze the following data with a focus on {focus}:

{data}

Provide:
1. Key observations
2. Patterns or trends
3. Recommendations
"""

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    # OAuth requires HTTP transport
    logger.info(f"Starting HTTP server on port {PORT}")
    logger.info(f"OAuth Gateway: {OAUTH_GATEWAY_URL}")
    logger.info(f"Resource URI: {MCP_RESOURCE_URI}")

    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=PORT,
        path="/mcp"
    )
```

---

## API Integration Server

Server that integrates with external APIs:

```python
"""
API Integration MCP Server.
Demonstrates external API integration patterns.
"""
import os
import httpx
from typing import Optional, List
from datetime import datetime, timedelta

from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError

mcp = FastMCP("APIIntegrationServer")

# HTTP client with connection pooling
http_client = httpx.AsyncClient(
    timeout=30.0,
    limits=httpx.Limits(max_keepalive_connections=10)
)

# Simple cache
_cache = {}
_cache_ttl = timedelta(minutes=5)

async def cached_fetch(url: str, cache_key: str) -> dict:
    """Fetch with caching."""
    now = datetime.now()

    if cache_key in _cache:
        data, cached_at = _cache[cache_key]
        if now - cached_at < _cache_ttl:
            return {**data, "_cached": True}

    response = await http_client.get(url)
    response.raise_for_status()
    data = response.json()

    _cache[cache_key] = (data, now)
    return {**data, "_cached": False}

@mcp.tool
async def fetch_weather(
    city: str,
    units: str = "metric",
    ctx: Context = None
) -> dict:
    """Fetch weather data for a city.

    Args:
        city: City name
        units: Temperature units (metric/imperial)
    """
    api_key = os.environ.get("WEATHER_API_KEY")
    if not api_key:
        raise ToolError("WEATHER_API_KEY not configured")

    if ctx:
        await ctx.info(f"Fetching weather for {city}")

    try:
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "units": units, "appid": api_key}

        response = await http_client.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        return {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "conditions": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"]
        }

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise ToolError(f"City not found: {city}")
        raise ToolError(f"Weather API error: {e}")

@mcp.tool
async def fetch_github_repo(
    owner: str,
    repo: str,
    ctx: Context = None
) -> dict:
    """Fetch GitHub repository information.

    Args:
        owner: Repository owner
        repo: Repository name
    """
    if ctx:
        await ctx.info(f"Fetching repo: {owner}/{repo}")

    cache_key = f"github:{owner}/{repo}"

    try:
        data = await cached_fetch(
            f"https://api.github.com/repos/{owner}/{repo}",
            cache_key
        )

        return {
            "name": data["name"],
            "description": data.get("description"),
            "stars": data["stargazers_count"],
            "forks": data["forks_count"],
            "language": data.get("language"),
            "url": data["html_url"],
            "cached": data.get("_cached", False)
        }

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise ToolError(f"Repository not found: {owner}/{repo}")
        raise ToolError(f"GitHub API error: {e}")

@mcp.tool
async def search_npm_packages(
    query: str,
    limit: int = 10,
    ctx: Context = None
) -> List[dict]:
    """Search npm packages.

    Args:
        query: Search query
        limit: Maximum results
    """
    if ctx:
        await ctx.info(f"Searching npm for: {query}")

    try:
        url = "https://registry.npmjs.org/-/v1/search"
        params = {"text": query, "size": limit}

        response = await http_client.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        packages = []

        for obj in data.get("objects", []):
            pkg = obj["package"]
            packages.append({
                "name": pkg["name"],
                "version": pkg["version"],
                "description": pkg.get("description", ""),
                "downloads": obj.get("downloads", {}).get("weekly", 0)
            })

        return packages

    except Exception as e:
        raise ToolError(f"npm search failed: {e}")

if __name__ == "__main__":
    mcp.run()
```

---

## Report Generation Server

Server focused on generating reports:

```python
"""
Report Generation MCP Server.
Based on GAM API patterns.
"""
import json
from typing import List, Literal, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError
from pydantic import Field
from typing_extensions import Annotated

mcp = FastMCP("ReportServer")

# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class DateRange:
    start_date: datetime
    end_date: datetime

    @classmethod
    def last_n_days(cls, days: int) -> "DateRange":
        end = datetime.now()
        start = end - timedelta(days=days)
        return cls(start_date=start, end_date=end)

@dataclass
class ReportResult:
    report_type: str
    dimensions: List[str]
    metrics: List[str]
    rows: List[dict]
    generated_at: datetime

# =============================================================================
# REPORT CONFIGURATIONS
# =============================================================================

REPORT_TYPES = {
    "delivery": {
        "dimensions": ["DATE", "AD_UNIT_NAME"],
        "metrics": ["IMPRESSIONS", "CLICKS", "CTR"],
        "description": "Ad delivery performance"
    },
    "inventory": {
        "dimensions": ["DATE", "AD_UNIT_NAME"],
        "metrics": ["AD_REQUESTS", "MATCHED_REQUESTS", "FILL_RATE"],
        "description": "Inventory utilization"
    },
    "revenue": {
        "dimensions": ["DATE", "ADVERTISER_NAME"],
        "metrics": ["REVENUE", "ECPM", "IMPRESSIONS"],
        "description": "Revenue analysis"
    }
}

VALID_DIMENSIONS = [
    "DATE", "AD_UNIT_NAME", "ADVERTISER_NAME",
    "ORDER_NAME", "LINE_ITEM_NAME", "COUNTRY_NAME"
]

VALID_METRICS = [
    "IMPRESSIONS", "CLICKS", "CTR", "REVENUE",
    "ECPM", "AD_REQUESTS", "MATCHED_REQUESTS", "FILL_RATE"
]

# =============================================================================
# TOOLS
# =============================================================================

@mcp.tool
async def quick_report(
    report_type: Literal["delivery", "inventory", "revenue"],
    days_back: Annotated[int, Field(ge=1, le=365)] = 30,
    format: Literal["json", "csv", "summary"] = "json",
    ctx: Context = None
) -> str:
    """Generate a quick report with predefined configuration.

    Args:
        report_type: Type of report (delivery, inventory, revenue)
        days_back: Number of days to look back (1-365)
        format: Output format
    """
    if report_type not in REPORT_TYPES:
        raise ToolError(f"Invalid report type. Choose from: {list(REPORT_TYPES.keys())}")

    config = REPORT_TYPES[report_type]
    date_range = DateRange.last_n_days(days_back)

    if ctx:
        await ctx.info(f"Generating {report_type} report for last {days_back} days")
        await ctx.report_progress(progress=0, total=100)

    # Simulated report generation
    rows = []
    for i in range(min(days_back, 10)):
        row = {
            "date": (date_range.end_date - timedelta(days=i)).strftime("%Y-%m-%d"),
        }
        for metric in config["metrics"]:
            row[metric.lower()] = 1000 - i * 50  # Simulated data
        rows.append(row)

    if ctx:
        await ctx.report_progress(progress=100, total=100)

    result = ReportResult(
        report_type=report_type,
        dimensions=config["dimensions"],
        metrics=config["metrics"],
        rows=rows,
        generated_at=datetime.now()
    )

    # Format output
    if format == "summary":
        return f"""Report: {report_type}
Period: Last {days_back} days
Rows: {len(rows)}
Dimensions: {', '.join(result.dimensions)}
Metrics: {', '.join(result.metrics)}"""

    elif format == "csv":
        headers = ["date"] + [m.lower() for m in result.metrics]
        lines = [",".join(headers)]
        for row in rows:
            lines.append(",".join(str(row.get(h, "")) for h in headers))
        return "\n".join(lines)

    else:  # json
        return json.dumps({
            "success": True,
            "report_type": report_type,
            "days_back": days_back,
            "total_rows": len(rows),
            "dimensions": result.dimensions,
            "metrics": result.metrics,
            "data": rows
        }, indent=2, default=str)

@mcp.tool
async def create_custom_report(
    name: str,
    dimensions: List[str],
    metrics: List[str],
    days_back: int = 30,
    ctx: Context = None
) -> str:
    """Create a custom report with specified dimensions and metrics.

    Args:
        name: Report name
        dimensions: List of dimensions to include
        metrics: List of metrics to include
        days_back: Number of days to look back
    """
    # Validate dimensions
    invalid_dims = [d for d in dimensions if d not in VALID_DIMENSIONS]
    if invalid_dims:
        raise ToolError(
            f"Invalid dimensions: {invalid_dims}. "
            f"Valid options: {VALID_DIMENSIONS}"
        )

    # Validate metrics
    invalid_metrics = [m for m in metrics if m not in VALID_METRICS]
    if invalid_metrics:
        raise ToolError(
            f"Invalid metrics: {invalid_metrics}. "
            f"Valid options: {VALID_METRICS}"
        )

    if ctx:
        await ctx.info(f"Creating custom report: {name}")

    # Generate report
    date_range = DateRange.last_n_days(days_back)
    rows = []

    for i in range(min(days_back, 10)):
        row = {"date": (date_range.end_date - timedelta(days=i)).strftime("%Y-%m-%d")}
        for metric in metrics:
            row[metric.lower()] = 1000 - i * 50
        rows.append(row)

    return json.dumps({
        "success": True,
        "report": {
            "name": name,
            "dimensions": dimensions,
            "metrics": metrics,
            "row_count": len(rows),
            "data": rows
        }
    }, indent=2)

@mcp.tool
async def get_report_types() -> str:
    """Get available quick report types and their configurations."""
    return json.dumps({
        "success": True,
        "report_types": REPORT_TYPES
    }, indent=2)

@mcp.tool
async def get_dimensions_metrics() -> str:
    """Get available dimensions and metrics for custom reports."""
    return json.dumps({
        "success": True,
        "dimensions": VALID_DIMENSIONS,
        "metrics": VALID_METRICS
    }, indent=2)

# =============================================================================
# RESOURCES
# =============================================================================

@mcp.resource("reports://types")
def report_types_resource() -> dict:
    """Available report types."""
    return REPORT_TYPES

@mcp.resource("reports://schema")
def report_schema_resource() -> dict:
    """Report schema information."""
    return {
        "dimensions": VALID_DIMENSIONS,
        "metrics": VALID_METRICS
    }

# =============================================================================
# PROMPTS
# =============================================================================

@mcp.prompt
def report_analysis_prompt(report_data: str) -> str:
    """Prompt for analyzing report data."""
    return f"""Analyze this report data and provide insights:

{report_data}

Please provide:
1. Key trends and patterns
2. Notable anomalies
3. Recommendations for improvement
"""

if __name__ == "__main__":
    mcp.run()
```

---

## ClickHouse MCP Server (Production Reference)

Real-world production MCP server with OAuth authentication, tool annotations, and database integration.
This is the exact implementation pattern from mcp-clickhouse.

```python
"""
ClickHouse MCP Server - Production Reference Implementation.

Features:
- OAuth 2.1 authentication with RemoteAuthProvider + JWTVerifier
- Health check endpoint (unauthenticated for load balancers)
- OAuth discovery endpoints (RFC 9728 and RFC 8414)
- Tool registration with ToolAnnotations
- MCP Context for logging and progress reporting
- Custom logging handler for MCP notifications
- Read-only query enforcement
"""
import logging
import json
from typing import Optional, List, Any
import concurrent.futures
import atexit
import os

from dotenv import load_dotenv
from fastmcp import FastMCP, Context
from fastmcp.tools import Tool
from fastmcp.prompts import Prompt
from fastmcp.exceptions import ToolError
from mcp.types import ToolAnnotations
from dataclasses import dataclass, field, asdict, is_dataclass
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse
from fastmcp.server.auth import RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier
from pydantic import AnyHttpUrl

# =============================================================================
# CUSTOM MCP LOGGING HANDLER
# =============================================================================

class MCPLoggingHandler(logging.Handler):
    """Custom logging handler that sends Python log records as MCP notifications.

    This handler bridges Python's standard logging to MCP's notification system,
    allowing errors logged via Python's logging to be visible in MCP clients
    (like Claude Desktop) while still being captured in Cloud Run logs.

    The handler only sends notifications when there's an active MCP context
    (during tool execution). If no context is available, it silently skips
    the MCP notification.
    """

    def emit(self, record: logging.LogRecord):
        """Send a log record as an MCP notification."""
        try:
            from fastmcp import Context

            # Get current MCP context (only available during active requests)
            try:
                ctx = Context.current()
            except Exception:
                return

            if not ctx:
                return

            # Map Python log levels to MCP notification levels
            level_map = {
                logging.DEBUG: 'debug',
                logging.INFO: 'info',
                logging.WARNING: 'warning',
                logging.ERROR: 'error',
                logging.CRITICAL: 'critical',
            }

            mcp_level = level_map.get(record.levelno, 'info')
            message = self.format(record)

            data = {
                "logger": record.name,
                "function": record.funcName,
                "line": record.lineno,
            }

            if record.exc_info:
                data["exception"] = str(record.exc_info[1])

            # Send to MCP client based on level
            if mcp_level == 'debug':
                ctx.debug(message, data=data)
            elif mcp_level == 'info':
                ctx.info(message, data=data)
            elif mcp_level == 'warning':
                ctx.warning(message, data=data)
            elif mcp_level == 'error':
                ctx.error(message, data=data)
            elif mcp_level == 'critical':
                ctx.critical(message, data=data)

        except Exception:
            pass  # Silently fail - don't crash on logging failures

# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class Column:
    database: str
    table: str
    name: str
    column_type: str
    default_kind: Optional[str]
    default_expression: Optional[str]
    comment: Optional[str]


@dataclass
class Table:
    database: str
    name: str
    engine: str
    create_table_query: str
    total_rows: int
    total_bytes: int
    comment: Optional[str] = None
    columns: List[Column] = field(default_factory=list)

# =============================================================================
# CONFIGURATION
# =============================================================================

MCP_SERVER_NAME = "mcp-clickhouse"

load_dotenv()

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "text").lower()
MCP_LOG_LEVEL = os.getenv("MCP_LOG_LEVEL", "WARNING").upper()

if LOG_FORMAT == "json":
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format='{"timestamp":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
    )
else:
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s"
    )

logger = logging.getLogger(MCP_SERVER_NAME)

# Add MCP logging handler
mcp_handler = MCPLoggingHandler()
mcp_handler.setLevel(getattr(logging, MCP_LOG_LEVEL, logging.WARNING))
logger.addHandler(mcp_handler)

# =============================================================================
# LAYER 1: MCP SERVER AUTH (RemoteAuthProvider + JWTVerifier)
# This protects your MCP server endpoints from unauthorized clients.
# Clients must present a valid JWT token from the OAuth gateway.
# =============================================================================

OAUTH_GATEWAY_URL = os.getenv("OAUTH_GATEWAY_URL", "https://ag.etus.io")
MCP_RESOURCE_URI = os.getenv("MCP_RESOURCE_URI")  # Required
OAUTH_JWKS_URI = os.getenv("OAUTH_JWKS_URI", f"{OAUTH_GATEWAY_URL}/.well-known/jwks.json")
OAUTH_ISSUER = os.getenv("OAUTH_ISSUER", OAUTH_GATEWAY_URL)
OAUTH_AUDIENCE = os.getenv("OAUTH_AUDIENCE", MCP_RESOURCE_URI)

# JWT Verifier validates tokens against JWKS
token_verifier = JWTVerifier(
    jwks_uri=OAUTH_JWKS_URI,
    issuer=OAUTH_ISSUER,
    audience=OAUTH_AUDIENCE,
)

# Remote Auth Provider handles OAuth automatically
auth = RemoteAuthProvider(
    token_verifier=token_verifier,
    authorization_servers=[AnyHttpUrl(OAUTH_GATEWAY_URL)],
    base_url=MCP_RESOURCE_URI,
)

# Create FastMCP server with OAuth authentication
mcp = FastMCP(name=MCP_SERVER_NAME, auth=auth)

# =============================================================================
# HEALTH CHECK (UNAUTHENTICATED)
# =============================================================================

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """Health check endpoint for monitoring server status.

    Intentionally unauthenticated for load balancers and monitoring.
    """
    try:
        # Verify database connectivity
        client = create_database_client()
        version = client.server_version
        return PlainTextResponse(f"OK - Connected to database {version}")
    except Exception as e:
        return PlainTextResponse(f"ERROR - {str(e)}", status_code=503)

# =============================================================================
# OAUTH DISCOVERY ENDPOINTS
# =============================================================================

@mcp.custom_route("/.well-known/oauth-protected-resource", methods=["GET"])
async def oauth_metadata(request: Request):
    """OAuth 2.0 Protected Resource Metadata (RFC 9728).

    Advertises:
    - Which authorization servers can issue tokens for this resource
    - What bearer token methods are supported
    - Resource identification information
    """
    metadata = {
        "resource": OAUTH_AUDIENCE,
        "authorization_servers": [OAUTH_GATEWAY_URL],
        "bearer_methods_supported": ["header"],
        "resource_name": "ClickHouse MCP Server",
        "resource_documentation": f"{MCP_RESOURCE_URI}/docs" if MCP_RESOURCE_URI else None,
    }
    logger.info(f"Serving OAuth protected resource metadata")
    return JSONResponse(metadata)


@mcp.custom_route("/.well-known/oauth-authorization-server", methods=["GET"])
async def oauth_authorization_server(request: Request):
    """OAuth 2.0 Authorization Server Metadata proxy (RFC 8414).

    Proxies metadata from authorization server for client discovery.
    Falls back to minimal config if auth server is unreachable.
    """
    import httpx

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            auth_server_url = f"{OAUTH_GATEWAY_URL}/.well-known/oauth-authorization-server"
            response = await client.get(auth_server_url)
            response.raise_for_status()
            logger.info(f"Proxied auth server metadata from {auth_server_url}")
            return JSONResponse(response.json())
    except Exception as e:
        logger.warning(f"Failed to fetch auth server metadata: {e}")

        # Fallback metadata
        fallback = {
            "issuer": OAUTH_ISSUER,
            "jwks_uri": OAUTH_JWKS_URI,
            "authorization_endpoint": f"{OAUTH_GATEWAY_URL}/authorize",
            "token_endpoint": f"{OAUTH_GATEWAY_URL}/token",
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code"],
        }
        return JSONResponse(fallback)

# =============================================================================
# TOOL FUNCTIONS
# =============================================================================

async def list_databases(ctx: Context):
    """List available databases."""
    await ctx.info("Listing all databases")
    client = create_database_client()
    result = client.command("SHOW DATABASES")

    if isinstance(result, str):
        databases = [db.strip() for db in result.strip().split("\n")]
    else:
        databases = [result]

    await ctx.info(f"Found {len(databases)} databases")
    return json.dumps(databases)


async def list_tables(database: str, ctx: Context, like: Optional[str] = None):
    """List tables in a database with schema information."""
    await ctx.info(f"Listing tables in database '{database}'")
    client = create_database_client()

    query = f"SELECT database, name, engine, total_rows, total_bytes FROM system.tables WHERE database = '{database}'"
    if like:
        query += f" AND name LIKE '{like}'"

    result = client.query(query)
    tables = [dict(zip(result.column_names, row)) for row in result.result_rows]
    total_tables = len(tables)

    await ctx.info(f"Found {total_tables} tables")

    # Report progress while fetching details
    for idx, table in enumerate(tables):
        await ctx.report_progress(
            progress=idx + 1,
            total=total_tables,
            message=f"Processing table {table['name']}"
        )

    return tables


async def run_select_query(query: str, ctx: Context):
    """Run a SELECT query (read-only)."""
    import asyncio

    await ctx.info(f"Executing query: {query[:100]}...")

    try:
        timeout_secs = 30

        result = await asyncio.wait_for(
            execute_query(query, ctx),
            timeout=timeout_secs
        )

        if isinstance(result, dict) and "error" in result:
            await ctx.warning(f"Query failed: {result['error']}")
            return {"status": "error", "message": result['error']}

        await ctx.info("Query completed successfully")
        return result

    except asyncio.TimeoutError:
        await ctx.warning(f"Query timed out after {timeout_secs} seconds")
        raise ToolError(f"Query timed out after {timeout_secs} seconds")
    except ToolError:
        raise
    except Exception as e:
        await ctx.error(f"Unexpected error: {str(e)}")
        raise ToolError(f"Query failed: {str(e)}")


async def execute_query(query: str, ctx: Context):
    """Execute query with read-only enforcement."""
    client = create_database_client()
    try:
        await ctx.info("Executing query")
        # Enforce read-only mode
        res = client.query(query, settings={"readonly": "1"})
        await ctx.info(f"Query returned {len(res.result_rows)} rows")
        return {"columns": res.column_names, "rows": res.result_rows}
    except Exception as err:
        await ctx.error(f"Query execution failed: {err}")
        logger.error(f"Query execution failed: {err}", exc_info=True)
        raise ToolError(f"Query execution failed: {str(err)}")


# =============================================================================
# LAYER 2: BACKEND SERVICE AUTH (separate from MCP auth!)
# This is how your MCP server authenticates to backend services.
# NOT covered by FastMCP skill - uses service-specific client libraries.
# =============================================================================

def create_database_client():
    """Create database client connection.

    NOTE: This is LAYER 2 auth - how the MCP server connects to ClickHouse.
    Completely separate from LAYER 1 (MCP server OAuth auth above).
    """
    import clickhouse_connect
    return clickhouse_connect.get_client(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "8123")),
        username=os.getenv("DB_USER", "default"),
        password=os.getenv("DB_PASSWORD", ""),
    )

# =============================================================================
# TOOL REGISTRATION WITH ANNOTATIONS
# =============================================================================

# List databases - read-only, idempotent
mcp.add_tool(Tool.from_function(
    list_databases,
    annotations=ToolAnnotations(
        title="List Databases",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True  # Queries external database
    )
))

# List tables - read-only, idempotent
mcp.add_tool(Tool.from_function(
    list_tables,
    annotations=ToolAnnotations(
        title="List Tables in Database",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True
    )
))

# Run SELECT query - read-only, NOT idempotent (results may change)
mcp.add_tool(Tool.from_function(
    run_select_query,
    annotations=ToolAnnotations(
        title="Execute SELECT Query",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=False,  # Results may change over time
        openWorldHint=True
    )
))

logger.info("Tools registered with annotations")

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # OAuth requires HTTP transport
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting HTTP server on port {port}")
    logger.info(f"OAuth Gateway: {OAUTH_GATEWAY_URL}")
    logger.info(f"Resource URI: {MCP_RESOURCE_URI}")

    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=port,
        path="/mcp"
    )
```

### Environment Variables for ClickHouse Server

```bash
# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 1: MCP SERVER AUTH
# How clients (Claude, etc.) authenticate TO your MCP server
# Documented in authentication-patterns.md
# ═══════════════════════════════════════════════════════════════════════════════
OAUTH_GATEWAY_URL=https://ag.etus.io
MCP_RESOURCE_URI=https://my-server.run.app
OAUTH_JWKS_URI=https://ag.etus.io/.well-known/jwks.json
OAUTH_ISSUER=https://ag.etus.io
OAUTH_AUDIENCE=https://my-server.run.app/mcp

# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 2: BACKEND SERVICE AUTH
# How your MCP server authenticates to backend services (ClickHouse, APIs, etc.)
# NOT covered by FastMCP skill - uses service-specific client libraries
# ═══════════════════════════════════════════════════════════════════════════════
DB_HOST=your-clickhouse-host.cloud
DB_PORT=8443
DB_USER=your_user
DB_PASSWORD=your_password

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
MCP_LOG_LEVEL=WARNING

# Server
PORT=8080
```

### Key Patterns from This Example

1. **OAuth Authentication**: RemoteAuthProvider + JWTVerifier with external OAuth gateway
2. **Health Check**: Unauthenticated `/health` endpoint for load balancers
3. **OAuth Discovery**: RFC 9728 and RFC 8414 compliant endpoints
4. **Tool Annotations**: ToolAnnotations with readOnlyHint, destructiveHint, idempotentHint, openWorldHint
5. **MCP Logging Handler**: Bridge Python logging to MCP notifications
6. **Progress Reporting**: `ctx.report_progress()` for long operations
7. **Read-Only Enforcement**: Database queries with `readonly=1`
8. **Error Handling**: ToolError for user-facing errors, logging for debugging
