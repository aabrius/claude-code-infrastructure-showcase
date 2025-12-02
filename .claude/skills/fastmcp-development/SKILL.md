---
name: fastmcp-development
description: Comprehensive guide for building MCP servers with FastMCP 2.0. Use when creating MCP tools, resources, prompts, implementing authentication (JWT, OAuth, RemoteAuthProvider, JWTVerifier), deploying to Cloud Run, working with MCP context, server composition, or building AI assistant integrations. Covers @mcp.tool decorators, type annotations, async patterns, error handling, HTTP transport, and production deployment.
---

# FastMCP Development Guide

## Purpose

Build production-ready MCP (Model Context Protocol) servers using FastMCP 2.0 - the fast, Pythonic way to create AI assistant integrations. This skill covers tools, resources, authentication, deployment, and best practices.

## When to Use This Skill

Automatically activates when working on:
- Creating MCP servers with FastMCP
- Building `@mcp.tool` decorated functions
- Implementing MCP resources and prompts
- Setting up authentication (JWT, OAuth, RemoteAuthProvider)
- Deploying MCP servers to Cloud Run or HTTP
- Working with MCP context (logging, progress, sampling)
- Server composition and mounting
- Integrating with Claude Desktop or AI clients

---

## Quick Start

### New MCP Server Checklist

- [ ] **FastMCP instance**: Initialize with name and optional auth
- [ ] **Tools**: Create `@mcp.tool` decorated async functions
- [ ] **Type annotations**: All parameters and returns typed
- [ ] **Docstrings**: Clear descriptions for tool discovery
- [ ] **Error handling**: Use `ToolError` for user-facing errors
- [ ] **Authentication**: Configure if deploying remotely
- [ ] **Transport**: Choose stdio (local) or HTTP (remote)
- [ ] **Testing**: Test tools before deployment

### Minimal MCP Server

```python
from fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool
async def hello(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
```

---

## Core Components

### 1. Tools

Functions exposed to LLMs for execution. Most common component.

```python
from fastmcp import FastMCP

mcp = FastMCP("CalculatorServer")

@mcp.tool
async def calculate(
    operation: Literal["add", "subtract", "multiply"],
    a: float,
    b: float
) -> float:
    """Perform arithmetic operation on two numbers."""
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    return a * b
```

**Key Points:**
- Use `@mcp.tool` decorator
- Type annotations are **mandatory**
- Docstrings become tool descriptions
- Prefer `async def` for I/O operations

See [tools-complete-guide.md](resources/tools-complete-guide.md) for full documentation.

### 2. Resources

Read-only data access points for LLM context.

```python
@mcp.resource("config://app/settings")
def get_settings() -> dict:
    """Application configuration."""
    return {"version": "1.0", "env": "production"}

# Dynamic resource with URI template
@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> dict:
    """Get user profile by ID."""
    return fetch_user(user_id)
```

See [resources-and-prompts.md](resources/resources-and-prompts.md) for details.

### 3. Prompts

Reusable, parameterized templates for LLM interactions.

```python
@mcp.prompt
def code_review(code: str, language: str = "python") -> str:
    """Generate a code review prompt."""
    return f"Review this {language} code:\n\n```{language}\n{code}\n```"
```

---

## Tool Creation Patterns

### Basic Tool with Types

```python
from typing import List, Optional, Literal
from pydantic import Field
from typing_extensions import Annotated

@mcp.tool
async def search_documents(
    query: str,
    limit: int = 10,
    category: Optional[str] = None
) -> List[dict]:
    """Search documents with optional category filter.

    Args:
        query: Search query string
        limit: Maximum results to return
        category: Optional category filter
    """
    results = await perform_search(query, limit, category)
    return results
```

### Tool with Pydantic Validation

```python
from pydantic import Field

@mcp.tool
async def create_report(
    name: Annotated[str, Field(min_length=1, max_length=100)],
    days_back: Annotated[int, Field(ge=1, le=365, description="Days to look back")],
    format: Literal["json", "csv", "summary"] = "json"
) -> dict:
    """Create a report with validated parameters."""
    return {"name": name, "days": days_back, "format": format}
```

### Tool with Error Handling

```python
from fastmcp.exceptions import ToolError

@mcp.tool
async def divide(a: float, b: float) -> float:
    """Divide two numbers."""
    if b == 0:
        raise ToolError("Cannot divide by zero")
    return a / b
```

### Tool with MCP Context

```python
from fastmcp import Context

@mcp.tool
async def long_operation(data_uri: str, ctx: Context) -> dict:
    """Process data with progress reporting."""
    await ctx.info("Starting operation...")

    # Report progress
    await ctx.report_progress(progress=25, total=100)

    # Read resource
    resource_data = await ctx.read_resource(data_uri)

    await ctx.report_progress(progress=100, total=100)
    return {"status": "complete", "data": resource_data}
```

---

## Authentication

> **Important:** This section covers **MCP Server authentication** only - how clients authenticate TO your MCP server. Backend service authentication (databases, Google APIs, etc.) is a separate concern. See [authentication-patterns.md](resources/authentication-patterns.md) for the full "Two Auth Layers" explanation.

### RemoteAuthProvider with JWTVerifier (Production)

```python
import os
from fastmcp import FastMCP
from fastmcp.server.auth import RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier
from pydantic import AnyHttpUrl

# OAuth configuration from environment
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

mcp = FastMCP(name="SecureServer", auth=auth)
```

### Environment Variables

```bash
OAUTH_GATEWAY_URL=https://ag.etus.io
MCP_RESOURCE_URI=https://my-server.run.app  # Required
OAUTH_JWKS_URI=https://ag.etus.io/.well-known/jwks.json
OAUTH_ISSUER=https://ag.etus.io
OAUTH_AUDIENCE=https://my-server.run.app/mcp
```

### OAuth Discovery Endpoints

```python
@mcp.custom_route("/.well-known/oauth-protected-resource", methods=["GET"])
async def oauth_metadata(request: Request):
    """RFC 9728 - Protected Resource Metadata."""
    return JSONResponse({
        "resource": OAUTH_AUDIENCE,
        "authorization_servers": [OAUTH_GATEWAY_URL],
        "bearer_methods_supported": ["header"],
    })
```

See [authentication-patterns.md](resources/authentication-patterns.md) for complete OAuth setup.

---

## Deployment

### Transport Options

| Transport | Use Case | Command |
|-----------|----------|---------|
| STDIO | Local dev, Claude Desktop | `mcp.run()` |
| HTTP | Remote access, Cloud Run | `mcp.run(transport="http", port=8080)` |
| SSE | Legacy (deprecated) | `mcp.run(transport="sse")` |

### Local Development (STDIO)

```python
if __name__ == "__main__":
    mcp.run()  # Default: stdio transport
```

### HTTP Deployment

```python
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=port,
        path="/mcp"
    )
```

### Cloud Run Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PORT=8080
ENV OAUTH_GATEWAY_URL=https://ag.etus.io
# MCP_RESOURCE_URI must be set at deploy time

CMD ["python", "server.py"]
```

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "my-server": {
      "url": "https://my-server.run.app/mcp",
      "transport": "http",
      "headers": {
        "Authorization": "Bearer <jwt-token-from-oauth-gateway>"
      }
    }
  }
}
```

See [deployment-guide.md](resources/deployment-guide.md) for full deployment patterns.

---

## Common Patterns

### Performance Tracking Decorator

```python
import time
import functools

def track_performance(operation_name: str):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start
                logger.info(f"{operation_name} completed in {duration:.2f}s")
                return result
            except Exception as e:
                logger.error(f"{operation_name} failed: {e}")
                raise
        return wrapper
    return decorator

@mcp.tool
@track_performance("search")
async def search(query: str) -> List[dict]:
    """Search with performance tracking."""
    return await perform_search(query)
```

### Circuit Breaker Pattern

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'

    async def call(self, func, *args, **kwargs):
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'half-open'
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            self.state = 'closed'
            self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = 'open'
            raise
```

### Structured Error Response

```python
def format_error(error_type: str, message: str, suggestions: List[str] = None) -> str:
    return json.dumps({
        "success": False,
        "error": {
            "type": error_type,
            "message": message,
            "suggestions": suggestions or []
        }
    }, indent=2)

@mcp.tool
async def validated_operation(param: str) -> str:
    if not param:
        return format_error(
            "ValidationError",
            "Parameter cannot be empty",
            ["Provide a non-empty string"]
        )
    return json.dumps({"success": True, "result": param})
```

---

## Quick Reference

### Decorator Options

```python
@mcp.tool(
    name="custom_name",           # Override function name
    description="Custom desc",    # Override docstring
    tags={"category", "filter"},  # Filtering tags
    enabled=True,                 # Enable/disable tool
    annotations={                 # MCP annotations
        "readOnlyHint": True,
        "destructiveHint": False
    }
)
async def my_tool(): pass
```

### Return Types

| Return Type | MCP Content |
|-------------|-------------|
| `str` | TextContent |
| `dict` | Structured JSON |
| `bytes` | Base64 blob |
| `Image` | Image content |
| `ToolResult` | Full control |

### Context Methods

```python
ctx: Context

await ctx.info("Info message")           # Logging
await ctx.warning("Warning message")
await ctx.error("Error message")
await ctx.report_progress(50, 100)       # Progress
await ctx.read_resource("uri://path")    # Read resource
await ctx.sample("prompt")               # LLM sampling
```

---

## Anti-Patterns to Avoid

- Missing type annotations (schema generation fails)
- Using `*args` or `**kwargs` (not supported)
- Sync functions for I/O operations (blocks event loop)
- Hardcoded secrets (use environment variables)
- Missing error handling (raw exceptions leak details)
- No docstrings (poor tool discovery)
- Blocking operations without progress reporting

---

## Navigation Guide

| Need to... | Read this |
|------------|-----------|
| Create tools | [tools-complete-guide.md](resources/tools-complete-guide.md) |
| Add resources/prompts | [resources-and-prompts.md](resources/resources-and-prompts.md) |
| Configure server | [server-configuration.md](resources/server-configuration.md) |
| Set up authentication | [authentication-patterns.md](resources/authentication-patterns.md) |
| Deploy to production | [deployment-guide.md](resources/deployment-guide.md) |
| Use MCP context | [context-and-middleware.md](resources/context-and-middleware.md) |
| See full examples | [complete-examples.md](resources/complete-examples.md) |

---

## Resource Files

### [tools-complete-guide.md](resources/tools-complete-guide.md)
Complete tool creation: decorators, parameters, validation, returns, error handling

### [resources-and-prompts.md](resources/resources-and-prompts.md)
Resources, URI templates, prompts, dynamic content

### [server-configuration.md](resources/server-configuration.md)
Server initialization, constructor parameters, component management, validation, composition, client usage

### [authentication-patterns.md](resources/authentication-patterns.md)
JWT, OAuth, RemoteAuthProvider, JWTVerifier, environment config, security

### [deployment-guide.md](resources/deployment-guide.md)
STDIO, HTTP, Cloud Run, Docker, production patterns

### [context-and-middleware.md](resources/context-and-middleware.md)
MCP context, logging, progress, middleware, server composition

### [complete-examples.md](resources/complete-examples.md)
Full server implementations, real-world examples

---

## Related Skills

- **python-fastapi-guidelines** - FastAPI backend patterns
- **gam-api-reports** - GAM API report generation
- **error-tracking** - Sentry integration

---

## External Resources

- [FastMCP Documentation](https://gofastmcp.com/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [PyPI Package](https://pypi.org/project/fastmcp/)

---

**Skill Status**: COMPLETE
**FastMCP Version**: 2.x (2.13.1+)
**Progressive Disclosure**: 7 resource files
