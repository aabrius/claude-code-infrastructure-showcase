#!/bin/bash
# Quick deployment script for GAM MCP Server to Cloud Run

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-etus-media-mgmt}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-gam-mcp-server}"
IMAGE_NAME="us-docker.pkg.dev/${PROJECT_ID}/gcr-io/${SERVICE_NAME}:latest"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if image exists
print_status "Checking if Docker image exists..."
if gcloud artifacts docker images list us-docker.pkg.dev/${PROJECT_ID}/gcr-io --filter="IMAGE:${SERVICE_NAME}" --format="value(IMAGE)" | grep -q "${SERVICE_NAME}"; then
    print_status "Docker image found: ${IMAGE_NAME}"
else
    print_error "Docker image not found. Please run Cloud Build first."
    exit 1
fi

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
    --project ${PROJECT_ID}

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --platform managed \
    --region ${REGION} \
    --project ${PROJECT_ID} \
    --format 'value(status.url)')

print_status "Deployment complete!"
print_status "Service URL: ${SERVICE_URL}"
print_status ""
print_status "Testing endpoints:"
print_status "  curl ${SERVICE_URL}/health"
print_status "  curl ${SERVICE_URL}/tools"
print_status ""
print_status "Example tool usage:"
print_status "  curl -X POST ${SERVICE_URL}/tool/gam_quick_report \\"
print_status "    -H 'Content-Type: application/json' \\"
print_status "    -d '{\"report_type\": \"delivery\", \"days_back\": 7}'"
print_status ""
print_status "For authenticated access, set MCP_AUTH_TOKEN environment variable"
print_status "and include 'Authorization: Bearer <token>' header in requests"