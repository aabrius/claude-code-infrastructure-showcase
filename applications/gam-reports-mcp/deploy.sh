#!/bin/bash
# Deploy GAM Reports MCP Server to Google Cloud Run

set -e

# Configuration
PROJECT_ID="${PROJECT_ID:-aa-lab-project}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="gam-reports-mcp"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "Deploying ${SERVICE_NAME} to Cloud Run..."
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"

# Build and push the image
echo "Building Docker image..."
gcloud builds submit --tag "${IMAGE_NAME}" --project "${PROJECT_ID}"

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE_NAME}" \
  --platform managed \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 5 \
  --min-instances 0 \
  --timeout 300 \
  --concurrency 80 \
  --port 8080 \
  --set-env-vars "MCP_TRANSPORT=http,MCP_AUTH_ENABLED=true,MCP_PORT=8080,LOG_LEVEL=INFO" \
  --set-secrets "/home/nonroot/.googleads.yaml=google-ads-yaml:latest" \
  --allow-unauthenticated

echo "Deployment complete!"
echo "Service URL:"
gcloud run services describe "${SERVICE_NAME}" \
  --platform managed \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --format 'value(status.url)'
