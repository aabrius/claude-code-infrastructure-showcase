#!/bin/bash
# Cloud Run deployment script for GAM MCP Server

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-gam-mcp-server}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Check if required variables are set
if [ -z "$PROJECT_ID" ]; then
    print_error "GCP_PROJECT_ID environment variable is not set"
    exit 1
fi

# Check if using FastMCP or standard MCP
USE_FASTMCP=${USE_FASTMCP:-true}

if [ "$USE_FASTMCP" = "true" ]; then
    DOCKERFILE="applications/mcp-server/Dockerfile"
    print_status "Using FastMCP implementation (recommended for Cloud Run)"
else
    DOCKERFILE="applications/mcp-server/Dockerfile.legacy"
    print_status "Using standard MCP implementation with HTTP wrapper"
fi

# Authenticate with Google Cloud
print_status "Authenticating with Google Cloud..."
gcloud auth configure-docker

# Set the project
gcloud config set project ${PROJECT_ID}

# Build the Docker image
print_status "Building Docker image..."
docker build -f ${DOCKERFILE} -t ${IMAGE_NAME} .

# Push the image to Google Container Registry
print_status "Pushing image to Container Registry..."
docker push ${IMAGE_NAME}

# Deploy to Cloud Run
print_status "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0 \
    --port 8080 \
    --set-env-vars "MCP_TRANSPORT=http" \
    --set-env-vars "LOG_LEVEL=INFO" \
    --set-secrets "GAM_CONFIG=/app/config/agent_config.yaml:gam-config:latest" \
    --set-secrets "GOOGLE_ADS_YAML=/app/googleads.yaml:google-ads-yaml:latest"

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format 'value(status.url)')

print_status "Deployment complete!"
print_status "Service URL: ${SERVICE_URL}"
print_status ""
print_status "MCP endpoints:"
print_status "  - Health: ${SERVICE_URL}/health"
print_status "  - Tools: ${SERVICE_URL}/tools"
print_status "  - Execute: ${SERVICE_URL}/tool/{tool_name}"
if [ "$USE_FASTMCP" = "true" ]; then
    print_status "  - MCP Protocol: ${SERVICE_URL}/mcp"
fi

# Test the deployment
print_status "Testing deployment..."
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" ${SERVICE_URL}/health)

if [ "$HEALTH_STATUS" = "200" ]; then
    print_status "Health check passed! Service is running."
else
    print_error "Health check failed with status: ${HEALTH_STATUS}"
    exit 1
fi