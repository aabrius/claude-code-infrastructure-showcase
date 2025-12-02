# FastMCP Authentication Patterns

## Table of Contents

1. [Overview](#overview)
2. [Two Auth Layers (Important!)](#two-auth-layers-important)
3. [Canonical Server Template](#canonical-server-template)
4. [OAuth Discovery Endpoints](#oauth-discovery-endpoints)
5. [Environment Configuration](#environment-configuration)
6. [Security Best Practices](#security-best-practices)
7. [Client Configuration](#client-configuration)
8. [Token Validation Details](#token-validation-details)
9. [Troubleshooting "Bearer token rejected"](#troubleshooting-bearer-token-rejected)
10. [Testing Authentication](#testing-authentication)
11. [CORS Support for Browser-Based Clients](#cors-support-for-browser-based-clients)
12. [Advanced Debugging](#advanced-debugging)

---

## Overview

FastMCP authentication applies to HTTP-based transports. This guide covers the **RemoteAuthProvider** pattern with external OAuth gateway authentication using JWT tokens verified via JWKS.

**Key Principle: Auth is ALWAYS enabled.** There is no toggle. HTTP transport with OAuth is the only supported mode for production servers.

---

## Two Auth Layers (Important!)

**This skill ONLY covers MCP Server authentication** - how clients authenticate to your MCP server. Backend service authentication (databases, external APIs) is a separate concern handled by their respective client libraries.

### Authentication Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        TWO SEPARATE AUTH LAYERS                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Client (Claude, etc.)                                                 │
│         │                                                               │
│         │ JWT Bearer Token (OAuth 2.1)                                  │
│         │ ← RemoteAuthProvider + JWTVerifier                            │
│         │ ← THIS IS WHAT THIS SKILL DOCUMENTS                           │
│         ▼                                                               │
│   ┌─────────────┐                                                       │
│   │ MCP Server  │                                                       │
│   └─────────────┘                                                       │
│         │                                                               │
│         │ Service-Specific Auth (NOT covered here)                      │
│         │ • Google APIs: OAuth2 service account / googleads.yaml        │
│         │ • ClickHouse: connection string (DB_HOST, DB_USER, etc.)      │
│         │ • Other APIs: API keys, tokens, etc.                          │
│         ▼                                                               │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │  Backend Services (Google Ad Manager, ClickHouse, etc.)         │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Environment Variables Separation

```bash
# ═══════════════════════════════════════════════════════════════════════
# LAYER 1: MCP SERVER AUTH (documented in this skill)
# How clients authenticate TO your MCP server
# ═══════════════════════════════════════════════════════════════════════
OAUTH_GATEWAY_URL=https://ag.etus.io
MCP_RESOURCE_URI=https://my-mcp-server.run.app/mcp   # ⚠️ MUST include /mcp path!
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8080

# ═══════════════════════════════════════════════════════════════════════
# LAYER 2: BACKEND SERVICE AUTH (NOT covered in this skill)
# How your MCP server authenticates to backend services
# ═══════════════════════════════════════════════════════════════════════

# Example: ClickHouse database
DB_HOST=your-clickhouse-host.cloud
DB_PORT=8443
DB_USER=your_user
DB_PASSWORD=your_password

# Example: Google Ad Manager (uses googleads.yaml, not env vars)
# See gam-api-reports skill for GAM authentication
```

### Key Points

| Aspect | MCP Server Auth | Backend Service Auth |
|--------|-----------------|---------------------|
| **Purpose** | Protect MCP endpoints | Access external services |
| **Direction** | Client → MCP Server | MCP Server → Backend |
| **Mechanism** | RemoteAuthProvider + JWTVerifier | Service-specific |
| **Env Vars** | `OAUTH_*`, `MCP_RESOURCE_URI` | `DB_*`, `*_API_KEY`, etc. |
| **Documented** | ✅ This skill | ❌ See service-specific docs |

---

## Canonical Server Template

**This is the exact pattern used by mcp-clickhouse and gam-api servers.**

Copy this template for any new MCP server:

```python
"""
MCP Server with OAuth Authentication.

Auth is ALWAYS enabled - no toggle. HTTP transport only.
"""

import os
import logging

from fastmcp import FastMCP, Context
from fastmcp.server.auth import RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier
from pydantic import AnyHttpUrl
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse

logger = logging.getLogger(__name__)

# =============================================================================
# OAuth Configuration (module-level, no conditionals)
# =============================================================================
OAUTH_GATEWAY_URL = os.getenv("OAUTH_GATEWAY_URL", "https://ag.etus.io")
MCP_RESOURCE_URI = os.getenv("MCP_RESOURCE_URI")  # Your server's URI (required)
OAUTH_JWKS_URI = os.getenv("OAUTH_JWKS_URI", f"{OAUTH_GATEWAY_URL}/.well-known/jwks.json")
OAUTH_ISSUER = os.getenv("OAUTH_ISSUER", OAUTH_GATEWAY_URL)
OAUTH_AUDIENCE = os.getenv("OAUTH_AUDIENCE", MCP_RESOURCE_URI)
MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8080"))

# =============================================================================
# Authentication Setup (ALWAYS created, no conditional)
# =============================================================================
token_verifier = JWTVerifier(
    jwks_uri=OAUTH_JWKS_URI,
    issuer=OAUTH_ISSUER,
    audience=OAUTH_AUDIENCE,
)

# Create Remote Auth Provider
# This handles all OAuth validation automatically!
auth = RemoteAuthProvider(
    token_verifier=token_verifier,
    authorization_servers=[AnyHttpUrl(OAUTH_GATEWAY_URL)],
    base_url=MCP_RESOURCE_URI,
)

# =============================================================================
# MCP Server Instance
# =============================================================================
mcp = FastMCP("My MCP Server", auth=auth)


# =============================================================================
# Health Check & OAuth Discovery Routes
# =============================================================================
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """Health check endpoint - intentionally unauthenticated."""
    return PlainTextResponse("OK")


@mcp.custom_route("/.well-known/oauth-protected-resource", methods=["GET"])
async def oauth_protected_resource(request: Request) -> JSONResponse:
    """OAuth 2.0 Protected Resource Metadata (RFC 9728)."""
    metadata = {
        "resource": OAUTH_AUDIENCE,
        "authorization_servers": [OAUTH_GATEWAY_URL],
        "bearer_methods_supported": ["header"],
        "resource_name": "My MCP Server",
        "resource_documentation": f"{MCP_RESOURCE_URI}/docs" if MCP_RESOURCE_URI else None,
    }
    return JSONResponse(metadata)


@mcp.custom_route("/.well-known/oauth-authorization-server", methods=["GET"])
async def oauth_authorization_server(request: Request) -> JSONResponse:
    """OAuth 2.0 Authorization Server Metadata (RFC 8414)."""
    import httpx

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            auth_server_url = f"{OAUTH_GATEWAY_URL}/.well-known/oauth-authorization-server"
            response = await client.get(auth_server_url)
            response.raise_for_status()
            return JSONResponse(response.json())
    except Exception as e:
        logger.warning(f"Failed to fetch auth server metadata: {e}")
        fallback = {
            "issuer": OAUTH_ISSUER,
            "jwks_uri": OAUTH_JWKS_URI,
            "authorization_endpoint": f"{OAUTH_GATEWAY_URL}/authorize",
            "token_endpoint": f"{OAUTH_GATEWAY_URL}/token",
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code"],
            "token_endpoint_auth_methods_supported": ["client_secret_basic"],
        }
        return JSONResponse(fallback)


# =============================================================================
# TOOLS (add your tools here)
# =============================================================================
@mcp.tool
async def my_tool(param: str, ctx: Context) -> str:
    """Example tool - protected by OAuth automatically."""
    return f"Result: {param}"


# =============================================================================
# Entry Point
# =============================================================================
if __name__ == "__main__":
    mcp.run(
        transport="http",
        host=MCP_SERVER_HOST,
        port=MCP_SERVER_PORT,
        path="/mcp",
    )
```

### Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `OAUTH_GATEWAY_URL` | `https://ag.etus.io` | No | Authorization server URL |
| `MCP_RESOURCE_URI` | None | **Yes** | Your server's full MCP endpoint URL **including `/mcp` path** |
| `OAUTH_JWKS_URI` | `{GATEWAY}/.well-known/jwks.json` | No | JWKS endpoint |
| `OAUTH_ISSUER` | `OAUTH_GATEWAY_URL` | No | Expected token issuer |
| `OAUTH_AUDIENCE` | `MCP_RESOURCE_URI` | No | Expected token audience (must match `aud` claim in tokens) |
| `MCP_SERVER_HOST` | `0.0.0.0` | No | Server bind host |
| `MCP_SERVER_PORT` | `8080` | No | Server bind port |

> **⚠️ CRITICAL: `MCP_RESOURCE_URI` must include the `/mcp` path!**
>
> The OAuth gateway registers resources with the full path (e.g., `https://gam.etus.io/mcp`).
> Tokens are issued with `aud: "https://gam.etus.io/mcp"`.
> If your server expects `aud: "https://gam.etus.io"` (without `/mcp`), authentication will fail with "Bearer token rejected".
>
> ✅ Correct: `MCP_RESOURCE_URI=https://my-server.run.app/mcp`
> ❌ Wrong: `MCP_RESOURCE_URI=https://my-server.run.app`

### What NOT To Do

```python
# ❌ WRONG - Missing /mcp path in resource URI (causes "Bearer token rejected")
MCP_RESOURCE_URI = "https://my-server.run.app"  # Missing /mcp!
# ✅ CORRECT
MCP_RESOURCE_URI = "https://my-server.run.app/mcp"

# ❌ WRONG - No auth toggle
MCP_AUTH_ENABLED = os.getenv("MCP_AUTH_ENABLED", "false")
if MCP_AUTH_ENABLED:
    auth = RemoteAuthProvider(...)
else:
    auth = None

# ❌ WRONG - No Pydantic Settings for auth
class Settings(BaseSettings):
    auth_enabled: bool = False

# ❌ WRONG - No fallback auth providers
def create_auth():
    try:
        return RemoteAuthProvider(...)
    except:
        return BearerAuthProvider(...)  # NO FALLBACKS

# ❌ WRONG - No stdio transport option
if transport == "stdio":
    mcp.run(transport="stdio")  # Auth doesn't work with stdio
```

---

## OAuth Discovery Endpoints

These three routes are **required** for OAuth-protected MCP servers:

### 1. Health Check (Unauthenticated)

```python
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """Health check - used by load balancers, must NOT require auth."""
    return PlainTextResponse("OK")
```

### 2. Protected Resource Metadata (RFC 9728)

```python
@mcp.custom_route("/.well-known/oauth-protected-resource", methods=["GET"])
async def oauth_protected_resource(request: Request) -> JSONResponse:
    """Tells clients which auth servers can issue tokens for this resource."""
    return JSONResponse({
        "resource": OAUTH_AUDIENCE,
        "authorization_servers": [OAUTH_GATEWAY_URL],
        "bearer_methods_supported": ["header"],
        "resource_name": "My Server",
    })
```

### 3. Authorization Server Metadata Proxy (RFC 8414)

```python
@mcp.custom_route("/.well-known/oauth-authorization-server", methods=["GET"])
async def oauth_authorization_server(request: Request) -> JSONResponse:
    """Proxies auth server metadata for client discovery."""
    # Fetch from actual auth server, with fallback
    ...
```

---

## Environment Configuration

### Production (Cloud Run)

```bash
# Required - MUST include /mcp path!
MCP_RESOURCE_URI=https://my-server.run.app/mcp

# Optional (have sensible defaults)
OAUTH_GATEWAY_URL=https://ag.etus.io
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8080
LOG_LEVEL=INFO
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV MCP_SERVER_HOST=0.0.0.0
ENV MCP_SERVER_PORT=8080
ENV OAUTH_GATEWAY_URL=https://ag.etus.io
# MCP_RESOURCE_URI must be set at deploy time

CMD ["python", "server.py"]
```

### Cloud Run Deploy

```bash
# Note: MCP_RESOURCE_URI MUST include /mcp path to match OAuth gateway registration
gcloud run deploy my-mcp-server \
    --image gcr.io/my-project/my-mcp-server \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars "MCP_RESOURCE_URI=https://my-mcp-server-xxx.run.app/mcp"
```

---

## Security Best Practices

### 1. Auth is Always On

There is no toggle. The server always requires valid JWT tokens.

### 2. HTTP Transport Only

OAuth requires HTTP headers. STDIO transport does not support authentication.

```python
# Always HTTP
mcp.run(transport="http", host="0.0.0.0", port=8080, path="/mcp")
```

### 3. Health Check is Unauthenticated

Load balancers need to check health without tokens:

```python
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")
```

### 4. No Secrets in Code

All OAuth config comes from environment variables:

```python
OAUTH_GATEWAY_URL = os.getenv("OAUTH_GATEWAY_URL", "https://ag.etus.io")
MCP_RESOURCE_URI = os.getenv("MCP_RESOURCE_URI")
```

---

## Client Configuration

### Claude Desktop

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

### cURL Testing

```bash
# Health check (no auth required)
curl https://my-server.run.app/health

# OAuth discovery
curl https://my-server.run.app/.well-known/oauth-protected-resource

# Tool call (auth required)
TOKEN="eyJhbGciOiJSUzI1NiIs..."
curl -X POST https://my-server.run.app/mcp \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"my_tool","arguments":{"param":"test"}},"id":1}'
```

---

## Token Validation Details

### What JWTVerifier Checks

1. **Signature** - Verified against public key from JWKS endpoint
2. **Issuer (iss)** - Must match `OAUTH_ISSUER`
3. **Audience (aud)** - Must match `OAUTH_AUDIENCE`
4. **Expiration (exp)** - Token must not be expired
5. **Not Before (nbf)** - Token must be valid (if claim present)

### Error Responses

| Error | HTTP Status | Cause |
|-------|-------------|-------|
| Missing token | 401 | No Authorization header |
| Invalid token | 401 | Malformed JWT |
| Signature invalid | 401 | Key not in JWKS |
| Issuer mismatch | 401 | Token `iss` != `OAUTH_ISSUER` |
| Audience mismatch | 401 | Token `aud` != `OAUTH_AUDIENCE` |
| Token expired | 401 | Token `exp` in past |

### Troubleshooting "Bearer token rejected"

If you see "Bearer token rejected" in logs, the most common cause is **audience mismatch**:

1. **Check OAuth gateway's protected_resources:**
   ```bash
   curl -s https://ag.etus.io/.well-known/oauth-authorization-server | grep -A10 protected_resources
   ```

2. **Check your server's expected audience:**
   ```bash
   curl -s https://your-server/.well-known/oauth-protected-resource | jq .resource
   ```

3. **They must match exactly!**
   - Gateway has: `https://my-server.run.app/mcp`
   - Server expects: `https://my-server.run.app/mcp` ✅
   - Server expects: `https://my-server.run.app` ❌ (missing `/mcp`)

### Authentication Flow

```
Client Request (with Bearer token)
  ↓
FastMCP Server receives request
  ↓
RemoteAuthProvider intercepts request
  ↓
JWTVerifier validates token:
  ├─ Fetches JWKS from jwks_uri
  ├─ Verifies JWT signature
  ├─ Checks issuer claim
  ├─ Checks audience claim
  ├─ Verifies token not expired
  └─ (401 Unauthorized if validation fails)
  ↓
Tool executes with authenticated context
```

---

## Testing Authentication

### Using FastMCP Client

FastMCP includes a client that handles OAuth automatically:

```python
from fastmcp import Client
import asyncio

async def test_auth():
    # auth="oauth" automatically handles the OAuth flow
    async with Client("https://my-server.run.app/mcp", auth="oauth") as client:
        # First-time: opens browser for OAuth login
        print("✓ Authenticated!")

        # Test connectivity
        assert await client.ping()

        # List available tools
        tools = await client.list_tools()
        print(f"Tools: {[t.name for t in tools]}")

        # Call a protected tool
        result = await client.call_tool("my_tool", {"param": "test"})
        print(result)

asyncio.run(test_auth())
```

### Check If Auth Is Required

```python
from fastmcp.client.auth import check_if_auth_required

needs_auth = check_if_auth_required("https://my-server.run.app/mcp")
print(f"Auth required: {needs_auth}")
```

### Manual cURL Testing

```bash
# 1. Health check (no auth)
curl https://my-server.run.app/health

# 2. Check OAuth metadata
curl https://my-server.run.app/.well-known/oauth-protected-resource

# 3. Tool call (requires valid JWT)
TOKEN="eyJhbGciOiJSUzI1NiIs..."
curl -X POST https://my-server.run.app/mcp \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

---

## CORS Support for Browser-Based Clients

**MCP Inspector and other browser-based tools require CORS headers** on discovery endpoints. Without proper CORS support, OPTIONS preflight requests fail with 405 Method Not Allowed.

### CORS Headers Configuration

```python
from starlette.responses import Response, JSONResponse

# CORS headers for browser-based clients (MCP Inspector)
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS, DELETE",
    "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept, Mcp-Session-Id",
    "Access-Control-Max-Age": "86400",
}
```

### Updated OAuth Discovery Endpoints with CORS

```python
@mcp.custom_route("/.well-known/oauth-protected-resource", methods=["GET", "OPTIONS"])
async def oauth_protected_resource(request: Request) -> Response:
    """OAuth 2.0 Protected Resource Metadata (RFC 9728)."""
    if request.method == "OPTIONS":
        return Response(status_code=204, headers=CORS_HEADERS)
    metadata = {
        "resource": OAUTH_AUDIENCE,
        "authorization_servers": [OAUTH_GATEWAY_URL],
        "bearer_methods_supported": ["header"],
        "resource_name": "My MCP Server",
    }
    return JSONResponse(metadata, headers=CORS_HEADERS)


@mcp.custom_route("/.well-known/oauth-authorization-server", methods=["GET", "OPTIONS"])
async def oauth_authorization_server(request: Request) -> Response:
    """OAuth 2.0 Authorization Server Metadata (RFC 8414)."""
    if request.method == "OPTIONS":
        return Response(status_code=204, headers=CORS_HEADERS)
    import httpx
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OAUTH_GATEWAY_URL}/.well-known/oauth-authorization-server")
            response.raise_for_status()
            return JSONResponse(response.json(), headers=CORS_HEADERS)
    except Exception as e:
        logger.warning(f"Failed to fetch auth server metadata: {e}")
        fallback = {
            "issuer": OAUTH_ISSUER,
            "jwks_uri": OAUTH_JWKS_URI,
            "authorization_endpoint": f"{OAUTH_GATEWAY_URL}/authorize",
            "token_endpoint": f"{OAUTH_GATEWAY_URL}/token",
        }
        return JSONResponse(fallback, headers=CORS_HEADERS)


@mcp.custom_route("/.well-known/openid-configuration", methods=["GET", "OPTIONS"])
async def openid_configuration(request: Request) -> Response:
    """OpenID Connect Discovery - some clients look for this endpoint."""
    if request.method == "OPTIONS":
        return Response(status_code=204, headers=CORS_HEADERS)
    import httpx
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Try OpenID config first, fallback to OAuth metadata
            for endpoint in [
                f"{OAUTH_GATEWAY_URL}/.well-known/openid-configuration",
                f"{OAUTH_GATEWAY_URL}/.well-known/oauth-authorization-server",
            ]:
                response = await client.get(endpoint)
                if response.status_code == 200:
                    return JSONResponse(response.json(), headers=CORS_HEADERS)
    except Exception:
        pass
    # Minimal fallback
    return JSONResponse({
        "issuer": OAUTH_ISSUER,
        "jwks_uri": OAUTH_JWKS_URI,
        "authorization_endpoint": f"{OAUTH_GATEWAY_URL}/authorize",
        "token_endpoint": f"{OAUTH_GATEWAY_URL}/token",
    }, headers=CORS_HEADERS)
```

### Why CORS Matters

| Client Type | Needs CORS | Discovery Endpoints Used |
|------------|------------|--------------------------|
| MCP Inspector (browser) | ✅ Yes | All three `.well-known` endpoints |
| Claude Desktop | ❌ No | `oauth-protected-resource` only |
| Python/CLI clients | ❌ No | `oauth-protected-resource` only |

---

## Advanced Debugging

### Temporarily Disable Audience Validation

If you're getting "Bearer token rejected" and suspect audience mismatch, you can temporarily disable audience validation for debugging:

```python
# For debugging ONLY - audience validation disabled
token_verifier = JWTVerifier(
    jwks_uri=OAUTH_JWKS_URI,
    issuer=OAUTH_ISSUER,
    audience=None,  # ⚠️ Accepts any audience - for testing only!
)
```

> **⚠️ Warning:** Never deploy with `audience=None` in production. This bypasses a critical security check.

### Checking Cloud Run Logs for Auth Errors

```bash
# Get recent auth-related logs
gcloud logging read "resource.type=cloud_run_revision \
  AND resource.labels.service_name=my-mcp-server \
  AND (textPayload=~\"token\" OR textPayload=~\"Auth\")" \
  --limit=30 \
  --format="table(timestamp,textPayload)"

# Common error patterns in logs:
# "Bearer token rejected for client XXX" - Audience or issuer mismatch
# "Auth error returned: invalid_token" - Token validation failed
# "HTTP Request: GET https://ag.etus.io/.well-known/jwks.json" - JWKS fetch (good sign)
```

### Decode JWT to Check Claims

When debugging auth issues, decode the JWT token to verify claims:

```bash
# Decode JWT (without verification) - use jwt.io or:
echo "$TOKEN" | cut -d. -f2 | base64 -d 2>/dev/null | jq .

# Expected claims:
# {
#   "iss": "https://ag.etus.io",           # Must match OAUTH_ISSUER
#   "aud": "https://my-server.run.app/mcp", # Must match OAUTH_AUDIENCE
#   "exp": 1733150000,                      # Must be in the future
#   "sub": "user-id",
#   "client_id": "cl_xxxxx"
# }
```

### Common Auth Issues Checklist

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| OPTIONS returns 405 | Missing CORS | Add OPTIONS handler with CORS headers |
| "invalid_token" error | Audience mismatch | Check `MCP_RESOURCE_URI` includes `/mcp` |
| "Failed to discover OAuth" | Missing openid-configuration | Add `/.well-known/openid-configuration` endpoint |
| JWKS fetch fails | Network/firewall | Check connectivity to OAuth gateway |
| Token expired | TTL exceeded | Refresh token or re-authenticate |
