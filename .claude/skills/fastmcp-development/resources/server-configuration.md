# FastMCP Server Configuration

## Table of Contents

1. [Server Initialization](#server-initialization)
2. [Constructor Parameters](#constructor-parameters)
3. [Component Management](#component-management)
4. [Validation & Security](#validation--security)
5. [Server Composition](#server-composition)
6. [Client Usage](#client-usage)

---

## Server Initialization

### Basic Setup

```python
from fastmcp import FastMCP

mcp = FastMCP(name="MyServer")
```

### Full Configuration

```python
import os
from fastmcp import FastMCP
from fastmcp.server.auth import RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier
from pydantic import AnyHttpUrl

# OAuth configuration
OAUTH_GATEWAY_URL = os.getenv("OAUTH_GATEWAY_URL", "https://ag.etus.io")
MCP_RESOURCE_URI = os.getenv("MCP_RESOURCE_URI")
OAUTH_JWKS_URI = os.getenv("OAUTH_JWKS_URI", f"{OAUTH_GATEWAY_URL}/.well-known/jwks.json")
OAUTH_ISSUER = os.getenv("OAUTH_ISSUER", OAUTH_GATEWAY_URL)
OAUTH_AUDIENCE = os.getenv("OAUTH_AUDIENCE", MCP_RESOURCE_URI)

# Create auth provider
token_verifier = JWTVerifier(
    jwks_uri=OAUTH_JWKS_URI,
    issuer=OAUTH_ISSUER,
    audience=OAUTH_AUDIENCE,
)
auth_provider = RemoteAuthProvider(
    token_verifier=token_verifier,
    authorization_servers=[AnyHttpUrl(OAUTH_GATEWAY_URL)],
    base_url=MCP_RESOURCE_URI,
)

mcp = FastMCP(
    # Basic identity
    name="ProductionServer",
    instructions="Server for data analysis tasks",
    version="1.0.0",
    website_url="https://example.com/docs",  # v2.14.0+

    # Pre-defined tools
    tools=[my_tool_function, another_tool],

    # Tag filtering
    include_tags={"production"},
    exclude_tags={"debug", "test"},

    # Duplicate handling
    on_duplicate_tools="error",
    on_duplicate_resources="warn",
    on_duplicate_prompts="replace",

    # Validation
    strict_input_validation=False,

    # Metadata
    include_fastmcp_meta=True,

    # Authentication
    auth=auth_provider,

    # Lifecycle management
    lifespan=app_lifespan,

    # Custom serialization
    tool_serializer=custom_serializer
)
```

---

## Constructor Parameters

### Identity & Description

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | "FastMCP" | Server identifier |
| `instructions` | str | None | How to use server |
| `version` | str | None | Version string |
| `website_url` | str | None | Documentation URL (v2.14.0+) |
| `icons` | list[Icon] | None | Visual icons (v2.14.0+) |

### Component Management

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tools` | list | None | Pre-defined tools |
| `include_tags` | set[str] | None | Only expose matching tags |
| `exclude_tags` | set[str] | None | Hide matching tags |

### Duplicate Handling

| Parameter | Type | Default | Options |
|-----------|------|---------|---------|
| `on_duplicate_tools` | str | "error" | error, warn, replace, ignore |
| `on_duplicate_resources` | str | "warn" | error, warn, replace, ignore |
| `on_duplicate_prompts` | str | "replace" | error, warn, replace, ignore |

### Validation & Security

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `strict_input_validation` | bool | False | Reject type mismatches |
| `mask_error_details` | bool | False | Hide internal errors |
| `include_fastmcp_meta` | bool | True | Include metadata (v2.11.0+) |

### Advanced

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `auth` | Provider | None | Authentication provider |
| `lifespan` | AsyncCM | None | Startup/shutdown logic |
| `tool_serializer` | callable | None | Custom JSON serialization |

---

## Component Management

### Tag-Based Filtering

```python
# Only expose production-ready tools
mcp = FastMCP(
    name="ProductionServer",
    include_tags={"production", "stable"}
)

@mcp.tool(tags={"production", "reports"})
async def generate_report(): pass  # Exposed

@mcp.tool(tags={"debug"})
async def debug_info(): pass  # Hidden
```

### Exclude Tags

```python
# Hide debug and test tools
mcp = FastMCP(
    name="Server",
    exclude_tags={"debug", "test", "internal"}
)
```

### Pre-registering Tools

```python
async def my_tool(param: str) -> str:
    """My tool description."""
    return f"Result: {param}"

mcp = FastMCP(
    name="Server",
    tools=[my_tool]  # Pre-register tools
)
```

---

## Validation & Security

### Strict Input Validation

```python
# Flexible (default): Coerces types
# "10" → 10, "true" → True
mcp = FastMCP("FlexibleServer")

# Strict: Rejects mismatches
# "10" → ValidationError
mcp = FastMCP("StrictServer", strict_input_validation=True)
```

### Error Masking

```python
# Hide internal error details
mcp = FastMCP("SecureServer", mask_error_details=True)

@mcp.tool
async def operation():
    raise ValueError("Internal")  # Client sees: "An error occurred"
    raise ToolError("Visible")    # Client sees: "Visible"
```

### Custom Serialization

```python
import yaml

def yaml_serializer(data):
    """Custom YAML serialization."""
    return yaml.dump(data)

mcp = FastMCP(
    name="Server",
    tool_serializer=yaml_serializer  # v2.2.7+
)
```

---

## Server Composition

### Importing (Static Copy)

```python
# Main server
main = FastMCP("MainServer")

# Sub-server
reports = FastMCP("ReportsServer")

@reports.tool
async def generate_report(): pass

# Import all components (one-time copy)
main.import_server(reports)

# With prefix
main.import_server(reports, prefix="reports")
# Tool available as: reports_generate_report
```

### Mounting (Live Delegation)

```python
# Mount for live updates
main.mount(reports)

# With prefix
main.mount(reports, prefix="reports")
```

### Import vs Mount

| Feature | Import | Mount |
|---------|--------|-------|
| Updates | Static copy | Live delegation |
| Performance | Fast | Delegation overhead |
| Changes | Not reflected | Immediately visible |
| Use case | Stable components | Dynamic servers |

### Proxying Remote Servers

```python
from fastmcp import FastMCP

# Create proxy to remote server
proxy = FastMCP.as_proxy("https://remote-server.com/mcp")

# Mount proxy
main.mount(proxy, prefix="remote")
```

---

## Client Usage

### Creating Clients

```python
from fastmcp import Client, FastMCP

# In-memory (testing)
server = FastMCP("TestServer")
client = Client(server)

# HTTP server
client = Client("https://example.com/mcp")

# Python script
client = Client("my_server.py")

# Node.js script
client = Client("server.js")
```

### Client Operations

```python
async with Client(mcp) as client:
    # List tools
    tools = await client.list_tools()

    # Call tool
    result = await client.call_tool("my_tool", {"param": "value"})

    # List resources
    resources = await client.list_resources()

    # Read resource
    content = await client.read_resource("config://settings")

    # List prompts
    prompts = await client.list_prompts()

    # Get prompt
    messages = await client.get_prompt("analyze", {"data": "..."})

    # Server info
    print(f"Server: {client.initialize_result.serverInfo.name}")
```

### Client Configuration

```python
client = Client(
    "server.py",
    log_handler=log_handler,
    progress_handler=progress_handler,
    sampling_handler=sampling_handler,
    timeout=30.0,
    auto_initialize=True  # Set False for manual init
)
```

---

## Running the Server

### Transport Options

```python
if __name__ == "__main__":
    # STDIO (default) - Claude Desktop, local dev
    mcp.run()

    # HTTP - Remote access, Cloud Run
    mcp.run(transport="http", host="0.0.0.0", port=8080)

    # SSE (legacy)
    mcp.run(transport="sse")
```

### Async Entry Point

```python
import asyncio

async def main():
    mcp = FastMCP("AsyncServer")
    await mcp.run_async(transport="http", port=8080)

if __name__ == "__main__":
    asyncio.run(main())
```

### ASGI Application

```python
def create_app():
    mcp = FastMCP("MyServer")

    @mcp.tool
    async def my_tool(param: str) -> str:
        return f"Result: {param}"

    return mcp.http_app()

# For uvicorn/gunicorn
app = create_app()
```

```bash
uvicorn server:app --host 0.0.0.0 --port 8080
```

### Custom HTTP Routes

```python
from fastmcp.server.http import custom_route

@custom_route("/health", methods=["GET"])
async def health_check():
    return {"status": "healthy"}

@custom_route("/metrics", methods=["GET"])
async def metrics():
    return {"requests": get_count()}
```

---

## Lifecycle Management

### Startup/Shutdown Logic

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def app_lifespan(server: FastMCP):
    # Startup
    print("Server starting...")
    await initialize_database()
    await warm_caches()

    yield  # Server runs here

    # Shutdown
    print("Server shutting down...")
    await close_connections()

mcp = FastMCP("Server", lifespan=app_lifespan)
```

---

## Environment Variables

OAuth configuration via environment variables:

```bash
# Logging
export FASTMCP_LOG_LEVEL=DEBUG

# OAuth Configuration
export OAUTH_GATEWAY_URL=https://ag.etus.io
export MCP_RESOURCE_URI=https://my-server.run.app  # Required
export OAUTH_JWKS_URI=https://ag.etus.io/.well-known/jwks.json
export OAUTH_ISSUER=https://ag.etus.io
export OAUTH_AUDIENCE=https://my-server.run.app/mcp
```
