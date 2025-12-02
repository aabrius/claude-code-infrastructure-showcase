# FastMCP Context and Middleware

## Table of Contents

1. [MCP Context](#mcp-context)
2. [Context Methods Reference](#context-methods-reference)
3. [Dependency Functions](#dependency-functions)
4. [Middleware Architecture](#middleware-architecture)
5. [Built-in Middleware](#built-in-middleware)
6. [Creating Custom Middleware](#creating-custom-middleware)

---

## MCP Context

The `Context` object provides access to MCP capabilities within tools, resources, and prompts.

### Injecting Context

```python
from fastmcp import FastMCP, Context

mcp = FastMCP("MyServer")

@mcp.tool
async def process_data(data: str, ctx: Context) -> dict:
    """Tool with context access."""
    await ctx.info(f"Processing: {data}")
    return {"processed": data}
```

**Key points:**
- Parameter name doesn't matter - only the `Context` type hint
- Context is optional and can appear anywhere in signature
- Not exposed as an MCP parameter to clients
- Each request gets a new context object

### Context in Different Components

```python
# In tools
@mcp.tool
async def tool_with_context(param: str, ctx: Context) -> str:
    await ctx.info("Tool called")
    return param

# In resources
@mcp.resource("status://server")
async def resource_with_context(ctx: Context) -> dict:
    return {"request_id": ctx.request_id}

# In prompts
@mcp.prompt
def prompt_with_context(topic: str, ctx: Context) -> str:
    return f"Discuss {topic} (ID: {ctx.request_id})"
```

---

## Context Methods Reference

### Logging

Send messages to clients with severity levels:

```python
@mcp.tool
async def logged_operation(ctx: Context) -> str:
    await ctx.debug("Debug details")      # Lowest severity
    await ctx.info("Information")         # Normal messages
    await ctx.warning("Warning message")  # Potential issues
    await ctx.error("Error occurred")     # Errors
    return "Done"
```

### Progress Reporting

Track long-running operations:

```python
@mcp.tool
async def batch_process(items: List[str], ctx: Context) -> dict:
    """Process items with progress updates."""
    total = len(items)
    results = []

    for i, item in enumerate(items):
        await ctx.report_progress(progress=i, total=total)
        result = await process_item(item)
        results.append(result)

    await ctx.report_progress(progress=total, total=total)
    return {"processed": len(results)}
```

### Resource Access

```python
@mcp.tool
async def read_config(ctx: Context) -> dict:
    """Access server resources."""
    # List all resources
    resources = await ctx.list_resources()

    # Read specific resource
    config = await ctx.read_resource("config://settings")

    return {"resources": len(resources), "config": config}
```

### Prompt Access (v2.13.0+)

```python
@mcp.tool
async def use_prompt(ctx: Context) -> str:
    """Access server prompts."""
    # List all prompts
    prompts = await ctx.list_prompts()

    # Get prompt with arguments
    result = await ctx.get_prompt("analyze", {"data": "sample"})

    return result
```

### LLM Sampling (v2.0.0+)

Request completions from the client's LLM:

```python
@mcp.tool
async def ai_enhanced(data: str, ctx: Context) -> dict:
    """Use LLM sampling for processing."""
    summary = await ctx.sample(
        f"Summarize this data:\n{data}",
        temperature=0.7
    )
    return {"summary": summary.text}
```

### User Elicitation (v2.10.0+)

Request structured input from users:

```python
@mcp.tool
async def interactive_tool(ctx: Context) -> dict:
    """Request user input during execution."""
    # Simple text input
    name = await ctx.elicit("Enter your name:", response_type=str)

    # Structured input with schema
    config = await ctx.elicit(
        "Configure settings:",
        response_type=dict,
        schema={
            "type": "object",
            "properties": {
                "theme": {"type": "string", "enum": ["light", "dark"]},
                "notifications": {"type": "boolean"}
            }
        }
    )

    return {"name": name, "config": config}
```

### State Management (v2.11.0+)

Share data within a single request:

```python
@mcp.tool
async def stateful_operation(ctx: Context) -> dict:
    """Use request-scoped state."""
    # Set state
    ctx.set_state("started_at", datetime.now())
    ctx.set_state("items_processed", 0)

    # Process and update state
    for item in items:
        await process(item)
        ctx.set_state("items_processed", ctx.get_state("items_processed") + 1)

    # Get state
    started = ctx.get_state("started_at")
    count = ctx.get_state("items_processed")

    return {"started": started, "count": count}
```

### Request Metadata

Access request information:

```python
@mcp.tool
async def inspect_request(ctx: Context) -> dict:
    """Access request metadata."""
    return {
        "request_id": ctx.request_id,    # Unique request ID
        "client_id": ctx.client_id,      # Client identifier
        "session_id": ctx.session_id,    # Session ID (HTTP only)
        "server": ctx.fastmcp.name       # Server instance
    }
```

---

## Dependency Functions

Access context and HTTP info from nested/helper functions:

### get_context()

```python
from fastmcp.server.dependencies import get_context

async def helper_function():
    """Access context from any function."""
    ctx = get_context()
    await ctx.info("Helper called")
```

### HTTP Dependencies

```python
from fastmcp.server.dependencies import (
    get_http_request,
    get_http_headers,
    get_access_token
)

@mcp.tool
async def http_aware_tool(ctx: Context) -> dict:
    """Access HTTP request details."""
    # Get request object
    request = get_http_request()

    # Get headers
    headers = get_http_headers()

    # Get access token (v2.11.0+)
    token = get_access_token()
    if token:
        client_id = token.client_id
        claims = token.claims

    return {"method": request.method if request else None}
```

---

## Middleware Architecture

Middleware enables cross-cutting functionality across all MCP requests.

### Pipeline Model

```
Request → Middleware 1 → Middleware 2 → Handler → Middleware 2 → Middleware 1 → Response
```

Each middleware can:
- Inspect incoming requests
- Modify requests before passing forward
- Execute the next handler via `call_next()`
- Inspect and transform responses
- Handle errors

### Adding Middleware

```python
from fastmcp.server.middleware import Middleware

mcp = FastMCP("MyServer")
mcp.add_middleware(LoggingMiddleware())
mcp.add_middleware(TimingMiddleware())

# Execution order:
# Request:  LoggingMiddleware → TimingMiddleware → Handler
# Response: TimingMiddleware → LoggingMiddleware → Client
```

---

## Built-in Middleware

FastMCP provides production-ready middleware:

### TimingMiddleware

```python
from fastmcp.server.middleware import TimingMiddleware

mcp.add_middleware(TimingMiddleware())
# Adds execution duration to response metadata
```

### LoggingMiddleware

```python
from fastmcp.server.middleware import LoggingMiddleware, StructuredLoggingMiddleware

# Basic logging
mcp.add_middleware(LoggingMiddleware())

# JSON structured logging
mcp.add_middleware(StructuredLoggingMiddleware())
```

### ResponseCachingMiddleware

```python
from fastmcp.server.middleware import ResponseCachingMiddleware

mcp.add_middleware(ResponseCachingMiddleware(
    ttl=300,  # 5 minutes
    max_size=1000
))
```

### RateLimitingMiddleware

```python
from fastmcp.server.middleware import RateLimitingMiddleware

mcp.add_middleware(RateLimitingMiddleware(
    max_requests=100,
    window_seconds=60
))
```

### ErrorHandlingMiddleware

```python
from fastmcp.server.middleware import ErrorHandlingMiddleware, RetryMiddleware

# Centralized error handling
mcp.add_middleware(ErrorHandlingMiddleware())

# Automatic retries
mcp.add_middleware(RetryMiddleware(max_retries=3))
```

### Tool Injection Middleware

```python
from fastmcp.server.middleware import (
    ToolInjectionMiddleware,
    PromptToolMiddleware,
    ResourceToolMiddleware
)

# Dynamically inject tools
mcp.add_middleware(ToolInjectionMiddleware(tools=[...]))

# Compatibility for limited clients
mcp.add_middleware(PromptToolMiddleware())
mcp.add_middleware(ResourceToolMiddleware())
```

---

## Creating Custom Middleware

### Basic Middleware

```python
from fastmcp.server.middleware import Middleware, MiddlewareContext

class LoggingMiddleware(Middleware):
    async def on_message(self, context: MiddlewareContext, call_next):
        print(f"Request: {context.method}")
        result = await call_next(context)
        print(f"Response: {context.method}")
        return result
```

### Available Hooks

| Hook | Description | Use Case |
|------|-------------|----------|
| `on_message` | All MCP messages | General logging |
| `on_request` | Request messages | Request processing |
| `on_notification` | Notification messages | Event handling |
| `on_call_tool` | Tool calls | Tool-specific logic |
| `on_read_resource` | Resource reads | Resource access control |
| `on_get_prompt` | Prompt requests | Prompt customization |
| `on_list_tools` | Tool listing | Dynamic tool filtering |
| `on_list_resources` | Resource listing | Resource filtering |
| `on_list_prompts` | Prompt listing | Prompt filtering |
| `on_initialize` | Client connection | Setup logic |

### Request Modification

```python
class InputNormalizationMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        # Modify request before processing
        if "value" in context.message.arguments:
            context.message.arguments["value"] = abs(
                context.message.arguments["value"]
            )

        return await call_next(context)
```

### Response Modification

```python
class MetadataMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        result = await call_next(context)

        # Add metadata to response
        if hasattr(result, 'structured_content'):
            result.structured_content["processed_at"] = datetime.now().isoformat()

        return result
```

### Error Handling

```python
from fastmcp.exceptions import ToolError

class AuthorizationMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        # Check authorization
        if not self.is_authorized(context):
            raise ToolError("Access denied: insufficient privileges")

        return await call_next(context)

    def is_authorized(self, context: MiddlewareContext) -> bool:
        # Check permissions
        return True
```

### Performance Tracking

```python
import time
from collections import defaultdict

class PerformanceMiddleware(Middleware):
    def __init__(self):
        self.timings = defaultdict(list)

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        start = time.time()
        try:
            result = await call_next(context)
            return result
        finally:
            duration = time.time() - start
            tool_name = context.message.name
            self.timings[tool_name].append(duration)

    def get_stats(self) -> dict:
        return {
            tool: {
                "count": len(times),
                "avg_ms": sum(times) / len(times) * 1000,
                "max_ms": max(times) * 1000
            }
            for tool, times in self.timings.items()
        }
```

### Rate Limiting

```python
from datetime import datetime, timedelta

class RateLimitMiddleware(Middleware):
    def __init__(self, max_requests: int = 100, window: int = 60):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window)
        self.requests = defaultdict(list)

    async def on_message(self, context: MiddlewareContext, call_next):
        client_id = context.client_id or "anonymous"
        now = datetime.now()

        # Clean old requests
        self.requests[client_id] = [
            t for t in self.requests[client_id]
            if now - t < self.window
        ]

        # Check limit
        if len(self.requests[client_id]) >= self.max_requests:
            raise ToolError(
                f"Rate limit exceeded. Max {self.max_requests} requests per {self.window.seconds}s"
            )

        # Record request
        self.requests[client_id].append(now)

        return await call_next(context)
```

---

## Middleware with Composition

### Parent/Child Middleware

When mounting servers, middleware layers:

```python
main = FastMCP("Main")
main.add_middleware(AuthMiddleware())  # Runs for all requests

child = FastMCP("Child")
child.add_middleware(LoggingMiddleware())  # Only for child requests

main.mount(child, prefix="child")

# Request to child tool:
# AuthMiddleware → LoggingMiddleware → Handler → LoggingMiddleware → AuthMiddleware
```

### Tag Filtering Across Composition

```python
main = FastMCP(
    "Main",
    include_tags={"production"},
    exclude_tags={"debug"}
)

# Tag filters apply recursively to all mounted/imported servers
```
