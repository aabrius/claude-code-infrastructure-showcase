# Deploying GAM MCP Server to Google Cloud Run

This guide covers deploying the Google Ad Manager MCP Server to Google Cloud Run.

## Overview

We provide two deployment options:

1. **FastMCP** (Recommended) - Uses native HTTP transport, simpler deployment
2. **Standard MCP** - Uses stdio transport with HTTP wrapper

## Prerequisites

- Google Cloud account with billing enabled
- `gcloud` CLI installed and authenticated
- Docker installed locally
- Google Ad Manager account with API access
- OAuth2 credentials configured

## Quick Start

```bash
# 1. Set up environment variables
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"  # Optional, defaults to us-central1

# 2. Set up secrets
./deploy/setup-secrets.sh

# 3. Deploy to Cloud Run
./deploy/cloud-run-deploy.sh
```

## Detailed Setup

### 1. Configure OAuth2 Authentication

First, generate your OAuth2 refresh token:

```bash
python generate_new_token.py
```

This creates/updates `googleads.yaml` with your credentials.

### 2. Configure the MCP Server

Create `config/agent_config.yaml`:

```yaml
# MCP Server settings
mcp:
  enabled: true
  server_name: "gam-mcp-server"
  description: "Google Ad Manager API MCP Server"

# Google Ad Manager settings
gam:
  network_code: "YOUR_NETWORK_CODE"
  api_version: "v1"
  
# Authentication
auth:
  type: "oauth2"
  oauth2:
    client_id: "YOUR_CLIENT_ID"
    client_secret: "YOUR_CLIENT_SECRET"
    refresh_token: "YOUR_REFRESH_TOKEN"

# Logging
logging:
  level: "INFO"
  format: "json"
```

### 3. Set Up Google Cloud Secrets

The setup script will:
- Enable required APIs
- Create secrets for your config files
- Set up service accounts

```bash
./deploy/setup-secrets.sh
```

### 4. Deploy to Cloud Run

```bash
# Deploy with FastMCP (recommended)
./deploy/cloud-run-deploy.sh

# Or deploy with standard MCP
USE_FASTMCP=false ./deploy/cloud-run-deploy.sh
```

## Using the Deployed Service

### FastMCP Endpoints

Once deployed, your service will have these endpoints:

- `GET /health` - Health check
- `GET /tools` - List available MCP tools
- `POST /tool/{tool_name}` - Execute a specific tool
- `POST /mcp` - Direct MCP protocol endpoint

### Example Usage

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe gam-mcp-server \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)')

# List available tools
curl ${SERVICE_URL}/tools

# Generate a quick report
curl -X POST ${SERVICE_URL}/tool/gam_quick_report \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "delivery",
    "days_back": 7,
    "format": "json"
  }'
```

### Using with Claude Desktop

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "gam-mcp": {
      "url": "https://gam-mcp-server-xxxxx-uc.a.run.app/mcp",
      "transport": "http"
    }
  }
}
```

## CI/CD with Cloud Build

For automated deployments, use Cloud Build:

```bash
# Set up Cloud Build trigger
gcloud builds submit --config cloudbuild.yaml

# Or connect to GitHub for automatic deployments
gcloud beta builds triggers create github \
  --repo-name="gam-api" \
  --repo-owner="your-github-username" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild.yaml"
```

## Architecture Comparison

### FastMCP Architecture
```
Client → HTTP Request → Cloud Run → FastMCP Server → GAM API
```

### Standard MCP Architecture
```
Client → HTTP Request → Cloud Run → HTTP Wrapper → stdio → MCP Server → GAM API
```

## Monitoring and Logging

View logs:
```bash
gcloud run services logs read gam-mcp-server \
  --platform managed \
  --region us-central1 \
  --limit 50
```

Monitor metrics:
```bash
gcloud monitoring dashboards create \
  --config-from-file=monitoring/dashboard.yaml
```

## Security Considerations

1. **Authentication**: By default, the service allows unauthenticated access. For production:
   ```bash
   gcloud run services update gam-mcp-server \
     --platform managed \
     --region us-central1 \
     --no-allow-unauthenticated
   ```

2. **API Keys**: Consider implementing API key authentication:
   ```python
   # In FastMCP server
   @mcp.middleware
   async def check_api_key(request):
       api_key = request.headers.get("X-API-Key")
       if not api_key or api_key != os.environ.get("API_KEY"):
           raise HTTPException(401, "Invalid API key")
   ```

3. **Secrets**: All sensitive data should be in Google Secret Manager

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify OAuth2 refresh token is valid
   - Check Secret Manager permissions
   - Regenerate token if expired

2. **Deployment Failures**
   - Check Cloud Build logs
   - Verify Docker image builds locally
   - Ensure all APIs are enabled

3. **Runtime Errors**
   - Check Cloud Run logs
   - Verify environment variables
   - Test locally with same config

### Local Testing

Test FastMCP locally:
```bash
# Run with HTTP transport
MCP_TRANSPORT=http PORT=8080 python -m src.mcp.fastmcp_server

# Test endpoints
curl http://localhost:8080/health
curl http://localhost:8080/tools
```

## Cost Optimization

1. **Set minimum instances to 0** for development
2. **Use Cloud Scheduler** for periodic reports
3. **Enable Cloud Run CPU allocation** only during requests
4. **Set appropriate memory limits** (1GB is usually sufficient)

## Next Steps

1. Set up monitoring dashboards
2. Configure alerts for errors
3. Implement caching for frequently accessed data
4. Add custom domain mapping
5. Set up Cloud Armor for DDoS protection

## Support

For issues:
1. Check Cloud Run logs
2. Review error messages in responses
3. Verify configuration in Secret Manager
4. Test with minimal examples first