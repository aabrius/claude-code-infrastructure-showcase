#!/bin/bash
set -e

# =============================================================================
# GAM Reports MCP Server - Production Deployment to Cloud Run
# =============================================================================
# Project: brius-appscripts
# Service: gam-reports-mcp
# Region: us-central1
# =============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="brius-appscripts"
REGION="us-central1"
SERVICE_NAME="gam-reports-mcp"
REPOSITORY="gam-reports"
IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_NAME}"
SECRET_NAME="googleads-yaml"
CREDENTIALS_FILE="../../googleads.yaml"
OAUTH_GATEWAY_URL="https://ag.etus.io"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  GAM Reports MCP - Production Deployment${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}Project:${NC} ${PROJECT_ID}"
echo -e "${GREEN}Region:${NC} ${REGION}"
echo -e "${GREEN}Service:${NC} ${SERVICE_NAME}"
echo ""

# Check if credentials file exists
if [ ! -f "${CREDENTIALS_FILE}" ]; then
    echo -e "${RED}❌ Error: GAM credentials not found at ${CREDENTIALS_FILE}${NC}"
    echo -e "${YELLOW}Please ensure googleads.yaml exists in the repository root${NC}"
    exit 1
fi

echo -e "${GREEN}✓ GAM credentials found${NC}"
echo ""

# Step 1: Set GCP project
echo -e "${BLUE}[1/6] Setting GCP project...${NC}"
gcloud config set project ${PROJECT_ID}
echo -e "${GREEN}✓ Project set to ${PROJECT_ID}${NC}"
echo ""

# Step 2: Enable required APIs
echo -e "${BLUE}[2/6] Enabling required Google Cloud APIs...${NC}"
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    --project=${PROJECT_ID} \
    --quiet

echo -e "${GREEN}✓ APIs enabled${NC}"
echo ""

# Step 3: Create Artifact Registry repository (if not exists)
echo -e "${BLUE}[3/6] Creating Artifact Registry repository...${NC}"
if gcloud artifacts repositories describe ${REPOSITORY} \
    --location=${REGION} \
    --project=${PROJECT_ID} >/dev/null 2>&1; then
    echo -e "${YELLOW}→ Repository already exists, skipping creation${NC}"
else
    gcloud artifacts repositories create ${REPOSITORY} \
        --repository-format=docker \
        --location=${REGION} \
        --description="GAM Reports MCP Server images" \
        --project=${PROJECT_ID}
    echo -e "${GREEN}✓ Repository created${NC}"
fi
echo ""

# Step 4: Create or update Secret Manager secret
echo -e "${BLUE}[4/6] Creating/updating Secret Manager secret for GAM credentials...${NC}"
if gcloud secrets describe ${SECRET_NAME} --project=${PROJECT_ID} >/dev/null 2>&1; then
    echo -e "${YELLOW}→ Secret exists, creating new version${NC}"
    gcloud secrets versions add ${SECRET_NAME} \
        --data-file="${CREDENTIALS_FILE}" \
        --project=${PROJECT_ID}
else
    echo -e "${YELLOW}→ Creating new secret${NC}"
    gcloud secrets create ${SECRET_NAME} \
        --data-file="${CREDENTIALS_FILE}" \
        --replication-policy="automatic" \
        --project=${PROJECT_ID}
fi
echo -e "${GREEN}✓ Secret configured${NC}"
echo ""

# Step 5: Build and push Docker image
echo -e "${BLUE}[5/6] Building and pushing Docker image...${NC}"
echo -e "${YELLOW}→ Building image: ${IMAGE_NAME}:latest${NC}"

gcloud builds submit \
    --tag="${IMAGE_NAME}:latest" \
    --project=${PROJECT_ID} \
    --region=${REGION} \
    --timeout=15m

echo -e "${GREEN}✓ Image built and pushed${NC}"
echo ""

# Step 6: Deploy to Cloud Run
echo -e "${BLUE}[6/6] Deploying to Cloud Run...${NC}"

# Get the service URL after deployment (we'll use it for MCP_RESOURCE_URI)
# First deploy without MCP_RESOURCE_URI, then update it
echo -e "${YELLOW}→ Initial deployment...${NC}"

gcloud run deploy ${SERVICE_NAME} \
    --image="${IMAGE_NAME}:latest" \
    --platform=managed \
    --region=${REGION} \
    --project=${PROJECT_ID} \
    --allow-unauthenticated \
    --memory=1Gi \
    --cpu=1 \
    --timeout=300 \
    --concurrency=80 \
    --min-instances=0 \
    --max-instances=10 \
    --set-env-vars="MCP_TRANSPORT=http,LOG_LEVEL=INFO,MCP_TEST_MODE=false,OAUTH_GATEWAY_URL=${OAUTH_GATEWAY_URL}" \
    --set-secrets="GOOGLE_ADS_YAML=${SECRET_NAME}:latest" \
    --quiet

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --platform=managed \
    --region=${REGION} \
    --project=${PROJECT_ID} \
    --format='value(status.url)')

echo -e "${GREEN}✓ Service deployed at: ${SERVICE_URL}${NC}"
echo ""

# Update with MCP_RESOURCE_URI
echo -e "${YELLOW}→ Updating with MCP_RESOURCE_URI...${NC}"

gcloud run services update ${SERVICE_NAME} \
    --region=${REGION} \
    --project=${PROJECT_ID} \
    --set-env-vars="MCP_RESOURCE_URI=${SERVICE_URL}" \
    --quiet

echo -e "${GREEN}✓ Service updated with resource URI${NC}"
echo ""

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✓ Deployment Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}Service URL:${NC} ${SERVICE_URL}"
echo -e "${GREEN}Health Check:${NC} ${SERVICE_URL}/health"
echo -e "${GREEN}MCP Endpoint:${NC} ${SERVICE_URL}/mcp"
echo -e "${GREEN}OAuth Discovery:${NC} ${SERVICE_URL}/.well-known/oauth-protected-resource"
echo ""
echo -e "${BLUE}OAuth Configuration:${NC}"
echo -e "  Gateway: ${OAUTH_GATEWAY_URL}"
echo -e "  Resource URI: ${SERVICE_URL}"
echo ""
echo -e "${YELLOW}Testing the deployment:${NC}"
echo -e "  curl ${SERVICE_URL}/health"
echo -e "  curl ${SERVICE_URL}/.well-known/oauth-protected-resource"
echo ""
echo -e "${YELLOW}MCP Client Configuration:${NC}"
echo '  {'
echo '    "mcpServers": {'
echo '      "gam-reports": {'
echo "        \"url\": \"${SERVICE_URL}/mcp\","
echo '        "transport": "http",'
echo '        "headers": {'
echo '          "Authorization": "Bearer <your-jwt-token>"'
echo '        }'
echo '      }'
echo '    }'
echo '  }'
echo ""
echo -e "${GREEN}✓ GAM Reports MCP Server is now running in production!${NC}"
echo ""
