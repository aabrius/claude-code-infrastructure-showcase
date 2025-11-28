#!/bin/bash
# Interactive credential setup for GAM MCP Server

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to update YAML files
update_yaml_value() {
    local file=$1
    local key=$2
    local value=$3
    
    # Use sed to update the value
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|${key}|${value}|g" "$file"
    else
        # Linux
        sed -i "s|${key}|${value}|g" "$file"
    fi
}

print_status "Google Ad Manager MCP Server Credential Setup"
echo ""

# Check for existing credentials
if grep -q "INSERT_CLIENT_ID_HERE" googleads.yaml 2>/dev/null; then
    print_warning "No credentials found in googleads.yaml"
    echo ""
    
    # Prompt for credentials
    read -p "Enter your Google OAuth2 CLIENT_ID: " CLIENT_ID
    read -p "Enter your Google OAuth2 CLIENT_SECRET: " CLIENT_SECRET
    read -p "Enter your Google Ad Manager NETWORK_CODE: " NETWORK_CODE
    
    # Update googleads.yaml
    print_status "Updating googleads.yaml..."
    update_yaml_value "googleads.yaml" "INSERT_CLIENT_ID_HERE" "$CLIENT_ID"
    update_yaml_value "googleads.yaml" "INSERT_CLIENT_SECRET_HERE" "$CLIENT_SECRET"
    update_yaml_value "googleads.yaml" "INSERT_NETWORK_CODE_HERE" "$NETWORK_CODE"
    
    # Update agent_config.yaml
    print_status "Updating config/agent_config.yaml..."
    update_yaml_value "config/agent_config.yaml" "YOUR_NETWORK_CODE" "$NETWORK_CODE"
    update_yaml_value "config/agent_config.yaml" "YOUR_CLIENT_ID" "$CLIENT_ID"
    update_yaml_value "config/agent_config.yaml" "YOUR_CLIENT_SECRET" "$CLIENT_SECRET"
    
    print_status "Credentials updated in configuration files"
    echo ""
    
    # Generate refresh token
    print_warning "Now we need to generate a refresh token..."
    echo "This will open a browser window for authentication."
    read -p "Press Enter to continue..."
    
    python generate_new_token.py
    
else
    print_status "Credentials already configured in googleads.yaml"
fi

# Set up environment variables for deployment
print_status "Setting up deployment environment..."
export GCP_PROJECT_ID="etus-media-mgmt"
export GCP_REGION="us-central1"
export SERVICE_NAME="gam-mcp-server"

echo ""
print_status "Configuration complete!"
print_status "Project: $GCP_PROJECT_ID"
print_status "Region: $GCP_REGION"
print_status "Service: $SERVICE_NAME"
echo ""
print_status "Ready to deploy. Run: ./deploy/cloud-run-deploy.sh"