#!/bin/bash
# Set up Google Cloud secrets for GAM MCP Server

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID}"
REGION="${GCP_REGION:-us-central1}"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

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

# Set the project
gcloud config set project ${PROJECT_ID}

# Enable required APIs
print_status "Enabling required Google Cloud APIs..."
gcloud services enable secretmanager.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Function to create or update a secret
create_or_update_secret() {
    local SECRET_NAME=$1
    local SECRET_FILE=$2
    
    # Check if secret exists
    if gcloud secrets describe ${SECRET_NAME} >/dev/null 2>&1; then
        print_status "Updating existing secret: ${SECRET_NAME}"
        gcloud secrets versions add ${SECRET_NAME} --data-file=${SECRET_FILE}
    else
        print_status "Creating new secret: ${SECRET_NAME}"
        gcloud secrets create ${SECRET_NAME} --data-file=${SECRET_FILE}
    fi
}

# Check for config files
print_status "Checking for configuration files..."

# Google Ads YAML configuration
if [ -f "googleads.yaml" ]; then
    print_status "Found googleads.yaml"
    create_or_update_secret "google-ads-yaml" "googleads.yaml"
else
    print_warning "googleads.yaml not found. You'll need to create this file."
    print_warning "See: https://github.com/googleads/googleads-python-lib"
fi

# Agent configuration
if [ -f "config/agent_config.yaml" ]; then
    print_status "Found config/agent_config.yaml"
    create_or_update_secret "gam-config" "config/agent_config.yaml"
else
    print_warning "config/agent_config.yaml not found."
    
    # Create a template if it doesn't exist
    if [ ! -f "config/agent_config.yaml.template" ]; then
        print_status "Creating configuration template..."
        mkdir -p config
        cat > config/agent_config.yaml.template << 'EOF'
# Google Ad Manager MCP Server Configuration

# MCP Server settings
mcp:
  enabled: true
  server_name: "gam-mcp-server"
  description: "Google Ad Manager API MCP Server"

# Google Ad Manager settings
gam:
  network_code: "YOUR_NETWORK_CODE"
  api_version: "v1"  # REST API version
  
# Authentication
auth:
  type: "oauth2"
  oauth2:
    client_id: "${GOOGLE_CLIENT_ID}"
    client_secret: "${GOOGLE_CLIENT_SECRET}"
    refresh_token: "${GOOGLE_REFRESH_TOKEN}"

# Logging
logging:
  level: "INFO"
  format: "json"

# Cache settings
cache:
  enabled: true
  ttl: 3600  # 1 hour
  directory: "/app/cache"
EOF
        print_status "Created config/agent_config.yaml.template"
        print_warning "Please copy this template to config/agent_config.yaml and fill in your values"
    fi
fi

# Create service account for Cloud Run
print_status "Setting up service account..."
SERVICE_ACCOUNT_NAME="gam-mcp-server"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Create service account if it doesn't exist
if ! gcloud iam service-accounts describe ${SERVICE_ACCOUNT_EMAIL} >/dev/null 2>&1; then
    print_status "Creating service account: ${SERVICE_ACCOUNT_NAME}"
    gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
        --display-name="GAM MCP Server Service Account"
fi

# Grant necessary permissions
print_status "Granting permissions to service account..."

# Secret Manager access
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/secretmanager.secretAccessor"

# Cloud Run invoker (if you want to restrict access)
# gcloud projects add-iam-policy-binding ${PROJECT_ID} \
#     --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
#     --role="roles/run.invoker"

print_status "Secret setup complete!"
print_status ""
print_status "Next steps:"
print_status "1. Ensure googleads.yaml exists with your OAuth2 credentials"
print_status "2. Ensure config/agent_config.yaml exists with your configuration"
print_status "3. Run ./deploy/cloud-run-deploy.sh to deploy the service"
print_status ""
print_status "To generate OAuth2 refresh token:"
print_status "  python generate_new_token.py"