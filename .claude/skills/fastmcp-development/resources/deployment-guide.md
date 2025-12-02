# FastMCP Deployment Guide

## Table of Contents

1. [Transport Options](#transport-options)
2. [Local Development](#local-development)
3. [HTTP Deployment](#http-deployment)
4. [Cloud Run Deployment](#cloud-run-deployment)
5. [Docker Patterns](#docker-patterns)
6. [Client Configuration](#client-configuration)

---

## Transport Options

| Transport | Use Case | Endpoint |
|-----------|----------|----------|
| STDIO | Local dev, Claude Desktop | stdin/stdout |
| HTTP | Remote access, Cloud Run | `http://host:port/mcp` |
| SSE | Legacy (deprecated) | Server-Sent Events |

---

## Local Development

### STDIO (Default)

```python
from fastmcp import FastMCP

mcp = FastMCP("DevServer")

@mcp.tool
async def hello(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()  # Default: stdio transport
```

### FastMCP CLI

```bash
# Run server
fastmcp run server.py

# With specific Python version
fastmcp run server.py --python 3.11

# With dependencies
fastmcp run server.py --with pandas --with httpx

# Pass arguments to server
fastmcp run server.py -- --config config.json
```

### Local HTTP for Testing

```python
if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000
    )
```

```bash
# Test with curl
curl http://localhost:8000/mcp/tools
curl -X POST http://localhost:8000/mcp/tools/hello \
  -H "Content-Type: application/json" \
  -d '{"name": "World"}'
```

---

## HTTP Deployment

### Basic HTTP Server

```python
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))

    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=port,
        path="/mcp"  # Endpoint path
    )
```

### Custom Routes

```python
from fastmcp import FastMCP
from fastmcp.server.http import custom_route

mcp = FastMCP("MyServer")

@custom_route("/health", methods=["GET"])
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@custom_route("/metrics", methods=["GET"])
async def metrics():
    return {
        "uptime": get_uptime(),
        "requests": get_request_count()
    }
```

### ASGI Application

```python
from fastmcp import FastMCP

def create_app():
    mcp = FastMCP("MyServer")

    @mcp.tool
    async def my_tool(param: str) -> str:
        return f"Result: {param}"

    return mcp.http_app()

# For ASGI servers (uvicorn, gunicorn)
app = create_app()
```

```bash
# Run with uvicorn
uvicorn server:app --host 0.0.0.0 --port 8080

# Run with gunicorn
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Async Entry Point

```python
import asyncio

async def main():
    mcp = FastMCP("AsyncServer")

    @mcp.tool
    async def async_tool(param: str) -> str:
        return f"Async result: {param}"

    await mcp.run_async(
        transport="http",
        host="0.0.0.0",
        port=8080
    )

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Cloud Run Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Environment variables
ENV PORT=8080
ENV MCP_TRANSPORT=http
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:${PORT}/health || exit 1

# Run server
CMD ["python", "server.py"]
```

### requirements.txt

```
fastmcp>=2.13.0
httpx>=0.25.0
pydantic>=2.0.0
```

### Server with Cloud Run Patterns

```python
import os
import logging
from fastmcp import FastMCP, Context
from fastmcp.server.auth import RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier
from pydantic import AnyHttpUrl
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse

# Configure logging
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# OAuth Configuration
OAUTH_GATEWAY_URL = os.environ.get("OAUTH_GATEWAY_URL", "https://ag.etus.io")
MCP_RESOURCE_URI = os.environ.get("MCP_RESOURCE_URI")
OAUTH_JWKS_URI = os.environ.get("OAUTH_JWKS_URI", f"{OAUTH_GATEWAY_URL}/.well-known/jwks.json")
OAUTH_ISSUER = os.environ.get("OAUTH_ISSUER", OAUTH_GATEWAY_URL)
OAUTH_AUDIENCE = os.environ.get("OAUTH_AUDIENCE", MCP_RESOURCE_URI)

# Setup authentication
def create_auth():
    if not MCP_RESOURCE_URI:
        logger.warning("MCP_RESOURCE_URI not set - authentication disabled")
        return None

    logger.info(f"Setting up OAuth authentication")
    logger.info(f"  Gateway: {OAUTH_GATEWAY_URL}")
    logger.info(f"  Resource URI: {MCP_RESOURCE_URI}")

    token_verifier = JWTVerifier(
        jwks_uri=OAUTH_JWKS_URI,
        issuer=OAUTH_ISSUER,
        audience=OAUTH_AUDIENCE,
    )

    return RemoteAuthProvider(
        token_verifier=token_verifier,
        authorization_servers=[AnyHttpUrl(OAUTH_GATEWAY_URL)],
        base_url=MCP_RESOURCE_URI,
    )

# Create server
mcp = FastMCP("CloudRunServer", auth=create_auth())

# Health check (unauthenticated for load balancers)
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")

# OAuth discovery (RFC 9728)
@mcp.custom_route("/.well-known/oauth-protected-resource", methods=["GET"])
async def oauth_metadata(request: Request):
    return JSONResponse({
        "resource": OAUTH_AUDIENCE,
        "authorization_servers": [OAUTH_GATEWAY_URL],
        "bearer_methods_supported": ["header"],
    })

@mcp.tool
async def my_tool(param: str, ctx: Context) -> dict:
    """Example tool."""
    await ctx.info(f"Processing: {param}")
    return {"result": param, "status": "success"}

if __name__ == "__main__":
    # OAuth requires HTTP transport
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting HTTP server on port {port}")
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=port,
        path="/mcp"
    )
```

### Deploy Script

```bash
#!/bin/bash
set -e

PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project)}"
SERVICE_NAME="my-mcp-server"
REGION="us-central1"

# Build and push
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy with OAuth configuration
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars "OAUTH_GATEWAY_URL=https://ag.etus.io,MCP_RESOURCE_URI=https://$SERVICE_NAME-xxx.run.app" \
  --min-instances 0 \
  --max-instances 10 \
  --memory 512Mi \
  --timeout 300

# Get URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --platform managed --region $REGION \
  --format 'value(status.url)')

echo "Deployed to: $SERVICE_URL"
echo "MCP endpoint: $SERVICE_URL/mcp"
```

### cloudbuild.yaml

```yaml
steps:
  # Build image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/my-mcp-server', '.']

  # Push image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/my-mcp-server']

  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'my-mcp-server'
      - '--image=gcr.io/$PROJECT_ID/my-mcp-server'
      - '--region=us-central1'
      - '--platform=managed'
      - '--allow-unauthenticated'
      - '--set-env-vars=OAUTH_GATEWAY_URL=https://ag.etus.io,MCP_RESOURCE_URI=https://my-mcp-server-xxx.run.app'

images:
  - 'gcr.io/$PROJECT_ID/my-mcp-server'
```

---

## Docker Patterns

### Development Docker Compose

```yaml
version: '3.8'

services:
  mcp-server:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
      - OAUTH_GATEWAY_URL=https://ag.etus.io
      - MCP_RESOURCE_URI=http://localhost:8080
      - LOG_LEVEL=DEBUG
    volumes:
      - ./:/app
    command: python server.py

  # Optional: Test client
  test-client:
    image: curlimages/curl:latest
    depends_on:
      - mcp-server
    entrypoint: >
      sh -c "sleep 5 && curl -v http://mcp-server:8080/health"
```

### Production Docker Compose

```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
      - OAUTH_GATEWAY_URL=https://ag.etus.io
      - MCP_RESOURCE_URI=https://my-server.example.com
      - OAUTH_ISSUER=https://ag.etus.io
      - OAUTH_AUDIENCE=https://my-server.example.com/mcp
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

---

## Client Configuration

### Claude Desktop

```json
{
  "mcpServers": {
    "my-server-local": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "LOG_LEVEL": "DEBUG"
      }
    },
    "my-server-remote": {
      "url": "https://my-server.run.app/mcp",
      "transport": "http",
      "headers": {
        "Authorization": "Bearer <jwt-token>"
      }
    }
  }
}
```

### Python Client

```python
from fastmcp import Client

# Local STDIO
async with Client("python server.py") as client:
    result = await client.call_tool("my_tool", {"param": "value"})

# Remote HTTP
async with Client(
    url="https://my-server.run.app/mcp",
    headers={"Authorization": f"Bearer {token}"}
) as client:
    tools = await client.list_tools()
    result = await client.call_tool("my_tool", {"param": "value"})
```

### Testing Deployed Server

```bash
# Get service URL
SERVICE_URL="https://my-server.run.app"

# Health check
curl $SERVICE_URL/health

# List tools
curl $SERVICE_URL/mcp/tools

# Call tool (with auth)
TOKEN="your-jwt-token"
curl -X POST $SERVICE_URL/mcp/tools/my_tool \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"param": "test"}'
```

---

## Monitoring & Observability

### Structured Logging

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name
        }
        if hasattr(record, "extra"):
            log_obj.update(record.extra)
        return json.dumps(log_obj)

# Configure
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.getLogger().addHandler(handler)
```

### Cloud Run Logging

```python
import google.cloud.logging

# Initialize Cloud Logging
client = google.cloud.logging.Client()
client.setup_logging()

# Logs automatically sent to Cloud Logging
logger.info("MCP server started", extra={
    "service": "mcp-server",
    "version": "1.0.0"
})
```
