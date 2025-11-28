# GAM MCP Server - Authentication Setup

## Overview

Authentication has been implemented for the GAM MCP Server deployed on Google Cloud Run. The server uses Bearer token authentication to protect the MCP endpoints.

## Authentication Details

### Token Information
- **Token**: `a2965203870061b4371c3b86fd8664539773ca818ae69714572a60f4d8016ae7`
- **Type**: Bearer token
- **Header**: `Authorization: Bearer <token>`

### How It Works

1. **Environment Variable**: The server checks for `MCP_AUTH_TOKEN` environment variable
2. **Request Validation**: All requests must include the Authorization header
3. **Token Comparison**: The provided token is compared with the environment variable
4. **Access Control**: Invalid or missing tokens receive a 401 Unauthorized response

### Implementation

The authentication is implemented in `src/mcp/fastmcp_server.py`:

```python
auth_token = os.environ.get("MCP_AUTH_TOKEN")
if auth_token:
    async def authenticate(request):
        """Simple bearer token authentication."""
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer ") and auth_header[7:] == auth_token:
            return {"authenticated": True}
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    mcp.authenticate = authenticate
```

## Using the Authenticated Server

### With Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "gam-api-cloud": {
      "url": "https://gam-mcp-server-183972668403.us-central1.run.app/mcp",
      "transport": "http",
      "headers": {
        "Authorization": "Bearer a2965203870061b4371c3b86fd8664539773ca818ae69714572a60f4d8016ae7"
      }
    }
  }
}
```

### With Python MCP Client

```python
from mcp import Client
import httpx

# Create authenticated HTTP client
http_client = httpx.Client(
    headers={
        "Authorization": "Bearer a2965203870061b4371c3b86fd8664539773ca818ae69714572a60f4d8016ae7"
    }
)

# Initialize MCP client
client = Client(
    url="https://gam-mcp-server-183972668403.us-central1.run.app/mcp",
    transport="http",
    http_client=http_client
)
```

### With cURL

```bash
# Example: Initialize session
curl -X POST https://gam-mcp-server-183972668403.us-central1.run.app/mcp/v1/initialize \
  -H "Content-Type: application/json" \
  -H "Accept: application/json,text/event-stream" \
  -H "Authorization: Bearer a2965203870061b4371c3b86fd8664539773ca818ae69714572a60f4d8016ae7" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {}
    },
    "id": 1
  }'
```

## Security Best Practices

### 1. Token Rotation

To rotate the authentication token:

```bash
# Generate new token
NEW_TOKEN=$(openssl rand -hex 32)

# Update Cloud Run service
gcloud run services update gam-mcp-server \
  --set-env-vars MCP_AUTH_TOKEN=$NEW_TOKEN \
  --project etus-media-mgmt \
  --region us-central1

# Update all clients with new token
```

### 2. Token Storage

- **Never commit tokens to version control**
- Store tokens in secure password managers
- Use environment variables or secret management systems
- Rotate tokens regularly

### 3. HTTPS Only

The Cloud Run service automatically provides HTTPS encryption, ensuring tokens are transmitted securely.

### 4. Additional Security Layers

Consider adding:
- IP allowlisting (Cloud Run supports VPC connector)
- Rate limiting
- Request logging and monitoring
- OAuth2 for user-specific access

## Testing Authentication

### Test Script

```python
#!/usr/bin/env python3
import requests

SERVICE_URL = "https://gam-mcp-server-183972668403.us-central1.run.app"
AUTH_TOKEN = "a2965203870061b4371c3b86fd8664539773ca818ae69714572a60f4d8016ae7"

# Test with authentication
response = requests.post(
    f"{SERVICE_URL}/mcp/v1/initialize",
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json,text/event-stream",
        "Authorization": f"Bearer {AUTH_TOKEN}"
    },
    json={
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {}},
        "id": 1
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
```

## Monitoring

### Check Authentication Logs

```bash
# View authentication-related logs
gcloud run services logs read gam-mcp-server \
  --project etus-media-mgmt \
  --region us-central1 \
  --limit 50 | grep -i auth
```

### Monitor Failed Attempts

Set up alerts for 401 responses to detect unauthorized access attempts:

```bash
# Create log-based metric for failed auth
gcloud logging metrics create failed_auth_attempts \
  --description="Failed authentication attempts on GAM MCP Server" \
  --log-filter='resource.type="cloud_run_revision"
    resource.labels.service_name="gam-mcp-server"
    httpRequest.status=401'
```

## Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Check token is correct
   - Ensure "Bearer " prefix is included
   - Verify token hasn't been rotated

2. **Authentication Not Working**
   - Check MCP_AUTH_TOKEN is set in Cloud Run
   - Verify FastMCP version supports authentication
   - Check server logs for authentication messages

3. **Token Exposed**
   - Immediately rotate the token
   - Update all client configurations
   - Review access logs for unauthorized use

## Future Enhancements

Consider implementing:
- **OAuth2**: For user-specific authentication
- **API Keys**: For service-to-service communication
- **JWT Tokens**: For stateless authentication with expiry
- **mTLS**: For mutual TLS authentication