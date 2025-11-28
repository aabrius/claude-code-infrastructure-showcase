# Deployment Guide

Complete guide for deploying the GAM API MCP server to Google Cloud Run.

## 🚀 Production Deployment

**Current Status:**
- ✅ **Service URL:** https://gam-mcp-server-183972668403.us-central1.run.app
- ✅ **Authentication:** JWT Bearer tokens
- ✅ **Auto-scaling:** 0-10 instances based on demand
- ✅ **Region:** us-central1

## 📋 Prerequisites

### Required Tools
```bash
# Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash
gcloud auth login
gcloud config set project etus-media-mgmt

# Install Docker
# Follow instructions at: https://docs.docker.com/get-docker/
```

### Required Files
- `googleads.yaml` - GAM API credentials
- `Dockerfile` - Container configuration
- `cloudbuild-simple.yaml` - Build configuration
- `deploy/quick-deploy.sh` - Deployment script

## 🔧 Environment Setup

### Google Cloud Project
```bash
# Set project and region
export PROJECT_ID="etus-media-mgmt"
export REGION="us-central1"
export SERVICE_NAME="gam-mcp-server"

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Environment Variables
```bash
# Required environment variables for Cloud Run
export MCP_TRANSPORT="http"
export MCP_AUTH_ENABLED="true"
export GAM_NETWORK_CODE="your_network_code"
export GAM_CLIENT_ID="your_client_id"
export GAM_CLIENT_SECRET="your_client_secret"
export GAM_REFRESH_TOKEN="your_refresh_token"
```

## 📦 Deployment Methods

### Method 1: Quick Deploy Script (Recommended)
```bash
# One-command deployment
./deploy/quick-deploy.sh

# Deploy with custom service name
./deploy/quick-deploy.sh my-custom-service
```

The script performs:
1. Builds Docker container using Cloud Build
2. Pushes to Container Registry
3. Deploys to Cloud Run with proper configuration
4. Sets up environment variables
5. Configures authentication

### Method 2: Manual Cloud Build
```bash
# Build and deploy using Cloud Build
gcloud builds submit --config=cloudbuild-simple.yaml

# Check build status
gcloud builds list --limit=5
```

### Method 3: Local Build and Deploy
```bash
# Build Docker image locally
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME .

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars MCP_TRANSPORT=http,MCP_AUTH_ENABLED=true
```

## 🔐 Authentication Setup

### JWT Token Generation
The service automatically generates JWT tokens on startup:

```bash
# Check service logs for JWT token
gcloud logs read --service=$SERVICE_NAME --limit=50 | grep "Client token"

# Example log output:
# Client token: eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...
```

### MCP Client Configuration
Configure your MCP client (Claude Desktop) with the JWT token:

```json
{
  "mcpServers": {
    "gam-api-cloud": {
      "url": "https://gam-mcp-server-183972668403.us-central1.run.app/mcp",
      "transport": "http",
      "headers": {
        "Authorization": "Bearer YOUR_JWT_TOKEN_HERE"
      }
    }
  }
}
```

## 🔧 Service Configuration

### Cloud Run Service Settings
```bash
# Update service configuration
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --concurrency 80 \
  --timeout 300s \
  --set-env-vars MCP_AUTH_ENABLED=true
```

### Environment Variables Management
```bash
# Set environment variables
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --set-env-vars \
    MCP_TRANSPORT=http,\
    MCP_AUTH_ENABLED=true,\
    GAM_NETWORK_CODE=$GAM_NETWORK_CODE,\
    GAM_CLIENT_ID=$GAM_CLIENT_ID,\
    GAM_CLIENT_SECRET=$GAM_CLIENT_SECRET,\
    GAM_REFRESH_TOKEN=$GAM_REFRESH_TOKEN

# Remove environment variable
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --remove-env-vars VAR_NAME
```

### Traffic Management
```bash
# Route all traffic to latest revision
gcloud run services update-traffic $SERVICE_NAME \
  --region $REGION \
  --to-latest

# Split traffic between revisions
gcloud run services update-traffic $SERVICE_NAME \
  --region $REGION \
  --to-revisions REVISION-1=50,REVISION-2=50
```

## 📊 Monitoring and Logging

### View Logs
```bash
# Real-time logs
gcloud logs tail --service=$SERVICE_NAME

# Recent logs
gcloud logs read --service=$SERVICE_NAME --limit=100

# Filter logs
gcloud logs read --service=$SERVICE_NAME \
  --filter="severity>=WARNING" \
  --limit=50
```

### Service Metrics
```bash
# Service status
gcloud run services describe $SERVICE_NAME --region=$REGION

# List revisions
gcloud run revisions list --service=$SERVICE_NAME --region=$REGION

# Service URL
gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --format='value(status.url)'
```

### Health Monitoring
```bash
# Check service health
curl https://your-service-url/health

# Detailed status
curl https://your-service-url/status

# MCP health check
curl -H "Authorization: Bearer $JWT_TOKEN" \
  https://your-service-url/mcp
```

## 🚨 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check build logs
gcloud builds list --limit=5
gcloud builds log BUILD_ID

# Check service logs
gcloud logs read --service=$SERVICE_NAME --limit=20
```

#### Authentication Errors
```bash
# Verify environment variables
gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --format='value(spec.template.spec.template.spec.containers[0].env[].name,spec.template.spec.template.spec.containers[0].env[].value)'

# Test OAuth credentials locally
python generate_new_token.py
```

#### Memory/CPU Issues
```bash
# Increase resources
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --memory 2Gi \
  --cpu 2
```

#### JWT Token Issues
```bash
# Generate new JWT token by restarting service
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --set-env-vars FORCE_RESTART=$(date +%s)

# Check logs for new token
gcloud logs read --service=$SERVICE_NAME --limit=10 | grep "Client token"
```

### Debug Mode
Enable debug logging for troubleshooting:

```bash
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --set-env-vars LOG_LEVEL=DEBUG,MCP_DEBUG=true
```

## 🔄 Updates and Rollbacks

### Deploy New Version
```bash
# Quick update
./deploy/quick-deploy.sh

# Or build and deploy manually
gcloud builds submit --config=cloudbuild-simple.yaml
```

### Rollback to Previous Version
```bash
# List revisions
gcloud run revisions list --service=$SERVICE_NAME --region=$REGION

# Route traffic to previous revision
gcloud run services update-traffic $SERVICE_NAME \
  --region $REGION \
  --to-revisions PREVIOUS_REVISION=100
```

### Canary Deployment
```bash
# Deploy new version
gcloud builds submit --config=cloudbuild-simple.yaml

# Split traffic 90/10
gcloud run services update-traffic $SERVICE_NAME \
  --region $REGION \
  --to-revisions OLD_REVISION=90,NEW_REVISION=10

# Monitor metrics, then route all traffic if successful
gcloud run services update-traffic $SERVICE_NAME \
  --region $REGION \
  --to-latest
```

## 📈 Performance Optimization

### Service Optimization
```bash
# Optimize for performance
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 1 \
  --max-instances 20 \
  --concurrency 100
```

### Cold Start Reduction
```bash
# Keep minimum instances warm
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --min-instances 2
```

### Connection Pooling
Environment variables for optimal performance:
```bash
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --set-env-vars \
    POOL_CONNECTIONS=10,\
    POOL_MAXSIZE=20,\
    MAX_RETRIES=3
```

## 🔒 Security

### IAM Permissions
```bash
# Grant necessary permissions to Cloud Run service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Secrets Management
```bash
# Store sensitive data in Secret Manager
echo -n "$GAM_CLIENT_SECRET" | gcloud secrets create gam-client-secret --data-file=-

# Use in Cloud Run
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --set-secrets GAM_CLIENT_SECRET=gam-client-secret:latest
```

### Network Security
```bash
# Restrict access to specific IPs (if needed)
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --ingress internal-and-cloud-load-balancing
```

## 📋 Maintenance

### Regular Tasks
```bash
# Weekly: Check service health
curl https://your-service-url/health

# Monthly: Review logs for errors
gcloud logs read --service=$SERVICE_NAME \
  --filter="severity>=ERROR" \
  --format="table(timestamp,severity,textPayload)"

# Quarterly: Update dependencies and redeploy
./deploy/quick-deploy.sh
```

### Backup Configuration
```bash
# Export service configuration
gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --format export > service-backup.yaml

# Store in version control or backup location
```

## 🎯 Production Checklist

Before deploying to production:

- [ ] Test OAuth credentials locally
- [ ] Verify environment variables are set correctly
- [ ] Test JWT authentication with MCP client
- [ ] Monitor initial deployment logs
- [ ] Verify all 7 MCP tools are working
- [ ] Set up monitoring and alerting
- [ ] Document JWT token for client configuration
- [ ] Test auto-scaling behavior
- [ ] Verify health endpoints respond correctly
- [ ] Check service costs and quotas

## 📞 Support

For deployment issues:
1. Check service logs: `gcloud logs read --service=$SERVICE_NAME`
2. Verify environment variables and authentication
3. Test OAuth credentials locally
4. Review troubleshooting section above
5. Check Google Cloud Console for service status