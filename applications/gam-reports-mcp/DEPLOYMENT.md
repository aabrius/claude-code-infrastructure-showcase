# GAM Reports MCP Server - Deployment Guide

Complete guide for local Docker testing and Google Cloud Run deployment with **uv** package manager.

## Prerequisites

- Docker and Docker Compose installed
- Google Cloud SDK (`gcloud`) installed and configured
- GAM credentials file at `~/.googleads.yaml`
- Python 3.11+ for local development

## Quick Start - Local Docker Testing

### 1. Test Locally with Docker

```bash
# Run the test script (builds, starts, and tests server)
./test-local.sh

# Or manually:
docker-compose build
docker-compose up
```

The server will be available at:
- Health: http://localhost:8080/health
- MCP endpoint: http://localhost:8080/mcp
- Tools: http://localhost:8080/mcp/tools
- Resources: http://localhost:8080/mcp/resources

### 2. Test MCP Endpoints

```bash
# Health check
curl http://localhost:8080/health

# List available tools
curl http://localhost:8080/mcp/tools | jq '.tools[] | {name, description}'

# List resources
curl http://localhost:8080/mcp/resources | jq '.resources[] | {uri, name}'

# Test search tool
curl -X POST http://localhost:8080/mcp/tools/search \
  -H "Content-Type: application/json" \
  -d '{"query": "impressions"}' | jq '.'

# Test get_available_options tool
curl -X POST http://localhost:8080/mcp/tools/get_available_options \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.dimensions | keys | .[0:5]'
```

### 3. Stop and Clean Up

```bash
docker-compose down
```

## Cloud Run Deployment

### Prerequisites for Cloud Run

1. **Create Google Cloud Secret for GAM Credentials**

```bash
# Set your project ID
export PROJECT_ID="aa-lab-project"

# Create secret from your googleads.yaml
gcloud secrets create google-ads-yaml \
  --data-file=$HOME/.googleads.yaml \
  --project=$PROJECT_ID

# Grant Cloud Run service account access to the secret
gcloud secrets add-iam-policy-binding google-ads-yaml \
  --member="serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=$PROJECT_ID
```

2. **Enable Required APIs**

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  --project=$PROJECT_ID
```

### Deploy to Cloud Run

```bash
# Deploy with default settings
./deploy.sh

# Or with custom settings
PROJECT_ID=my-project REGION=us-central1 MAX_INSTANCES=10 ./deploy.sh
```

The deployment script will:
1. ✓ Check if the google-ads-yaml secret exists
2. ✓ Build Docker image with Cloud Build
3. ✓ Deploy to Cloud Run with authentication required
4. ✓ Test health endpoint
5. ✓ Display service URL and authentication instructions

### Post-Deployment

After deployment, you'll get:

```
Service URL:  https://gam-reports-mcp-xxx.run.app
MCP Endpoint: https://gam-reports-mcp-xxx.run.app/mcp
Health Check: https://gam-reports-mcp-xxx.run.app/health
```

## Authentication

### Cloud Run IAM Authentication

The service requires Cloud Run authentication (`--no-allow-unauthenticated`).

**Generate Identity Token:**

```bash
gcloud auth print-identity-token
```

**Test with Authentication:**

```bash
TOKEN=$(gcloud auth print-identity-token)

# Test health check (unauthenticated)
curl https://gam-reports-mcp-xxx.run.app/health

# Test MCP tools (authenticated)
curl -H "Authorization: Bearer $TOKEN" \
  https://gam-reports-mcp-xxx.run.app/mcp/tools
```

### Claude Desktop Configuration

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "gam-reports": {
      "url": "https://gam-reports-mcp-xxx.run.app/mcp",
      "transport": "http",
      "headers": {
        "Authorization": "Bearer <your-identity-token>"
      }
    }
  }
}
```

**Note:** Identity tokens expire after 1 hour. For production, use a service account with proper IAM roles.

## Architecture

### Container Architecture (uv + FastMCP)

```
┌─────────────────────────────────────────┐
│  Official uv Docker Image               │
│  ghcr.io/astral-sh/uv:python3.11-slim  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Dependencies Layer (cached)            │
│  - uv sync --frozen --no-dev           │
│  - Virtual environment in .venv/       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Application Layer                      │
│  - config/, core/, endpoints/          │
│  - models/, server.py, search.py       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Runtime                                │
│  - CMD: uv run --no-dev server.py      │
│  - HTTP transport on 0.0.0.0:8080      │
│  - Health check: /health               │
│  - MCP endpoint: /mcp                  │
└─────────────────────────────────────────┘
```

### Key Features

- **Fast Builds**: uv provides 10-100x faster dependency resolution
- **Layer Caching**: Dependencies cached separately from code
- **Security**: `--no-allow-unauthenticated` requires IAM authentication
- **Health Checks**: `/health` endpoint for load balancers
- **Logging**: `PYTHONUNBUFFERED=1` for immediate log output
- **Secrets**: GAM credentials mounted from Secret Manager
- **Auto-scaling**: 0-5 instances (configurable)

## Monitoring & Debugging

### View Logs

```bash
# Real-time logs
gcloud run services logs tail gam-reports-mcp \
  --project=aa-lab-project \
  --region=us-central1

# Recent logs
gcloud run services logs read gam-reports-mcp \
  --project=aa-lab-project \
  --region=us-central1 \
  --limit=100
```

### View Metrics

```bash
# Open Cloud Console metrics
open "https://console.cloud.google.com/run/detail/us-central1/gam-reports-mcp/metrics?project=aa-lab-project"
```

### Debug Locally

```bash
# Run with debug logging
LOG_LEVEL=DEBUG docker-compose up

# Check container logs
docker-compose logs -f gam-reports-mcp

# Execute commands in running container
docker-compose exec gam-reports-mcp bash
```

## Best Practices (2025)

Based on [official Google Cloud documentation](https://cloud.google.com/run/docs/tutorials/deploy-remote-mcp-server) and [FastMCP deployment guide](https://codelabs.developers.google.com/codelabs/cloud-run/how-to-deploy-a-secure-mcp-server-on-cloud-run):

1. ✅ **Use `uv` for package management** - 10-100x faster than pip
2. ✅ **Require authentication** - `--no-allow-unauthenticated` for security
3. ✅ **Use HTTP transport** - Required for Cloud Run, more scalable than SSE
4. ✅ **Implement health checks** - `/health` endpoint for load balancers
5. ✅ **Set `PYTHONUNBUFFERED=1`** - Immediate log output
6. ✅ **Use Secret Manager** - Never commit credentials
7. ✅ **Enable auto-scaling** - Start at 0, scale based on demand
8. ✅ **Use gen2 execution environment** - Better performance
9. ✅ **Separate dependency and code layers** - Faster rebuilds
10. ✅ **Test locally with Docker** - Catch issues before deployment

## Troubleshooting

### "Secret not found" Error

```bash
# Create the secret
gcloud secrets create google-ads-yaml \
  --data-file=$HOME/.googleads.yaml \
  --project=aa-lab-project
```

### "Health check failed" Error

The health endpoint (`/health`) is unauthenticated and should work without a token. If it fails in Cloud Run, check:

```bash
# Check service status
gcloud run services describe gam-reports-mcp \
  --project=aa-lab-project \
  --region=us-central1

# Check recent logs
gcloud run services logs read gam-reports-mcp \
  --project=aa-lab-project \
  --region=us-central1 \
  --limit=50
```

### "Permission denied" Accessing MCP Tools

MCP tools require authentication. Get a fresh identity token:

```bash
TOKEN=$(gcloud auth print-identity-token)
curl -H "Authorization: Bearer $TOKEN" \
  https://gam-reports-mcp-xxx.run.app/mcp/tools
```

### Local Docker "Can't connect to googleads.yaml"

Ensure your credentials file exists:

```bash
ls -la ~/.googleads.yaml
```

If missing, create it from your GAM credentials.

## Sources & References

This deployment setup follows 2025 best practices from:

- [Build and deploy a remote MCP server on Cloud Run](https://cloud.google.com/run/docs/tutorials/deploy-remote-mcp-server)
- [How to deploy a secure MCP server on Cloud Run](https://codelabs.developers.google.com/codelabs/cloud-run/how-to-deploy-a-secure-mcp-server-on-cloud-run)
- [Build and Deploy a Remote MCP Server to Google Cloud Run in Under 10 Minutes](https://cloud.google.com/blog/topics/developers-practitioners/build-and-deploy-a-remote-mcp-server-to-google-cloud-run-in-under-10-minutes)
- [Setting up uv with Google Cloud Run Functions](https://withlogic.co/var/log/2025/01/20/setting-up-uv-with-google-cloud-run-functions)
- [Host MCP servers on Cloud Run](https://cloud.google.com/run/docs/host-mcp-servers)

## Support

For issues:
1. Check logs: `gcloud run services logs read gam-reports-mcp`
2. Verify credentials secret is accessible
3. Test locally with Docker first
4. Check authentication token is valid
5. Review Cloud Run service configuration
