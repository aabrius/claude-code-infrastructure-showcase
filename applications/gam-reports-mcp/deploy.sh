#!/bin/bash
# Deploy GAM Reports MCP Server to Google Cloud Run
# Best practices for 2025: uv, authentication, health checks, monitoring

set -e

# Configuration
PROJECT_ID="${PROJECT_ID:-aa-lab-project}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="gam-reports-mcp"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
MIN_INSTANCES="${MIN_INSTANCES:-0}"
MAX_INSTANCES="${MAX_INSTANCES:-5}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  GAM Reports MCP Server Deployment${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "Project:       ${PROJECT_ID}"
echo -e "Region:        ${REGION}"
echo -e "Service:       ${SERVICE_NAME}"
echo -e "Min instances: ${MIN_INSTANCES}"
echo -e "Max instances: ${MAX_INSTANCES}"
echo ""

# Check if googleads.yaml secret exists
echo -e "${BLUE}Checking secrets...${NC}"
if ! gcloud secrets describe google-ads-yaml --project="${PROJECT_ID}" &>/dev/null; then
    echo -e "${YELLOW}⚠️  Secret 'google-ads-yaml' not found${NC}"
    echo -e "${YELLOW}   Create it with: gcloud secrets create google-ads-yaml --data-file=\$HOME/.googleads.yaml --project=${PROJECT_ID}${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Secret 'google-ads-yaml' found${NC}"

# Build and push the image
echo -e "\n${BLUE}Building Docker image with Cloud Build...${NC}"
gcloud builds submit \
  --tag "${IMAGE_NAME}" \
  --project "${PROJECT_ID}" \
  --timeout=10m

echo -e "${GREEN}✓ Image built and pushed${NC}"

# Get service URL if exists (for updating MCP_RESOURCE_URI)
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --platform managed \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --format 'value(status.url)' 2>/dev/null || echo "")

# Deploy to Cloud Run with best practices
echo -e "\n${BLUE}Deploying to Cloud Run...${NC}"
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE_NAME}" \
  --platform managed \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --memory 512Mi \
  --cpu 1 \
  --max-instances "${MAX_INSTANCES}" \
  --min-instances "${MIN_INSTANCES}" \
  --timeout 300 \
  --concurrency 80 \
  --port 8080 \
  --set-env-vars "MCP_TRANSPORT=http,MCP_PORT=8080,LOG_LEVEL=INFO,PYTHONUNBUFFERED=1" \
  --set-secrets "/app/.googleads.yaml=google-ads-yaml:latest" \
  --no-allow-unauthenticated \
  --execution-environment gen2 \
  --service-account "${SERVICE_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" || {
    echo -e "${YELLOW}Note: Service account ${SERVICE_NAME}@${PROJECT_ID}.iam.gserviceaccount.com not found${NC}"
    echo -e "${YELLOW}      Deploying with default service account${NC}"
    gcloud run deploy "${SERVICE_NAME}" \
      --image "${IMAGE_NAME}" \
      --platform managed \
      --region "${REGION}" \
      --project "${PROJECT_ID}" \
      --memory 512Mi \
      --cpu 1 \
      --max-instances "${MAX_INSTANCES}" \
      --min-instances "${MIN_INSTANCES}" \
      --timeout 300 \
      --concurrency 80 \
      --port 8080 \
      --set-env-vars "MCP_TRANSPORT=http,MCP_PORT=8080,LOG_LEVEL=INFO,PYTHONUNBUFFERED=1" \
      --set-secrets "/app/.googleads.yaml=google-ads-yaml:latest" \
      --no-allow-unauthenticated \
      --execution-environment gen2
  }

# Get the deployed service URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --platform managed \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --format 'value(status.url)')

echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Deployment Complete! ✓${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "\nService URL:  ${SERVICE_URL}"
echo -e "MCP Endpoint: ${SERVICE_URL}/mcp"
echo -e "Health Check: ${SERVICE_URL}/health"
echo ""
echo -e "${BLUE}Testing endpoints...${NC}"

# Test health check
if curl -sf "${SERVICE_URL}/health" > /dev/null; then
    echo -e "${GREEN}✓ Health check OK${NC}"
else
    echo -e "${YELLOW}⚠️  Health check failed (may require authentication)${NC}"
fi

echo -e "\n${BLUE}Authentication:${NC}"
echo -e "This service requires authentication. To access:"
echo -e "\n1. Generate identity token:"
echo -e "   ${GREEN}gcloud auth print-identity-token${NC}"
echo -e "\n2. Use token in requests:"
echo -e "   ${GREEN}curl -H \"Authorization: Bearer \$(gcloud auth print-identity-token)\" ${SERVICE_URL}/mcp/tools${NC}"
echo -e "\n3. Configure in Claude Desktop:"
echo -e '   {
     "mcpServers": {
       "gam-reports": {
         "url": "'${SERVICE_URL}'/mcp",
         "transport": "http",
         "headers": {
           "Authorization": "Bearer <identity-token>"
         }
       }
     }
   }'
echo ""
echo -e "${BLUE}Monitoring:${NC}"
echo -e "View logs: ${GREEN}gcloud run services logs read ${SERVICE_NAME} --project=${PROJECT_ID} --region=${REGION}${NC}"
echo -e "View metrics: ${GREEN}https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}/metrics?project=${PROJECT_ID}${NC}"
