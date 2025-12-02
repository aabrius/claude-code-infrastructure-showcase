#!/bin/bash
#
# MCP Inspector Test Script for GAM API MCP Server
#
# Usage:
#   ./scripts/test_with_inspector.sh              # Interactive UI mode (local stdio)
#   ./scripts/test_with_inspector.sh --cli        # CLI mode with all tests
#   ./scripts/test_with_inspector.sh --ui         # Open UI mode
#   ./scripts/test_with_inspector.sh --http       # Test HTTP transport
#   ./scripts/test_with_inspector.sh --cloud      # Test Cloud Run deployment
#
# Requirements:
#   - Node.js v22.7.5+
#   - Python environment with dependencies installed
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Configuration
INSPECTOR_CONFIG="mcp-inspector.json"
LOCAL_HTTP_URL="http://localhost:8080/mcp"
CLOUD_URL="https://gam-mcp-server-183972668403.us-central1.run.app/mcp"

# Functions
print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_requirements() {
    print_header "Checking Requirements"

    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is required but not installed"
        echo "  Install from: https://nodejs.org/"
        exit 1
    fi

    NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
    if [ "$NODE_VERSION" -lt 22 ]; then
        print_warning "Node.js v22.7.5+ recommended (current: $(node -v))"
    else
        print_success "Node.js $(node -v)"
    fi

    # Check npx
    if ! command -v npx &> /dev/null; then
        print_error "npx is required but not installed"
        exit 1
    fi
    print_success "npx available"

    # Check uv (Python package manager)
    if ! command -v uv &> /dev/null; then
        print_error "uv is required but not installed"
        echo "  Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    print_success "uv $(uv --version | head -1)"

    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 is required but not installed"
        exit 1
    fi
    print_success "Python $(python3 --version)"

    # Check config file
    if [ -f "$INSPECTOR_CONFIG" ]; then
        print_success "Configuration file found: $INSPECTOR_CONFIG"
    else
        print_warning "Configuration file not found, will use defaults"
    fi

    # Check MCP server pyproject.toml
    if [ -f "applications/mcp-server/pyproject.toml" ]; then
        print_success "MCP server project found"
    else
        print_error "MCP server pyproject.toml not found"
        exit 1
    fi
}

run_ui_mode() {
    print_header "Starting MCP Inspector UI Mode"

    echo "Opening inspector at http://localhost:6274"
    echo ""
    echo "The inspector will connect using the config file."
    echo "Server: gam-api-local-stdio (uses uv for dependency management)"
    echo ""
    echo "Manual connection (if needed):"
    echo "  1. Select Transport: STDIO"
    echo "  2. Command: uv"
    echo "  3. Arguments: run --directory applications/mcp-server python main.py"
    echo "  4. Add environment variable: MCP_AUTH_ENABLED=false"
    echo "  5. Click 'Connect'"
    echo ""

    npx @modelcontextprotocol/inspector \
        --config "$INSPECTOR_CONFIG" \
        --server gam-api-local-stdio
}

run_ui_mode_simple() {
    print_header "Starting MCP Inspector UI (Simple)"

    echo "Opening inspector at http://localhost:6274"
    echo "Configure your connection in the UI..."
    echo ""

    npx @modelcontextprotocol/inspector
}

run_cli_tests() {
    print_header "Running CLI Tests (STDIO Transport)"

    echo "Testing local server with STDIO transport..."
    echo "Using uv to manage dependencies..."
    echo ""

    # Test 1: List tools
    print_info "Test 1: Listing available tools..."
    RESULT=$(npx @modelcontextprotocol/inspector --cli \
        -e MCP_AUTH_ENABLED=false \
        -e MCP_TRANSPORT=stdio \
        -- uv run --directory applications/mcp-server python main.py \
        --method tools/list 2>&1) || true

    if echo "$RESULT" | grep -q "gam_quick_report"; then
        print_success "tools/list - Found gam_quick_report tool"
    else
        print_warning "tools/list - Could not verify tools (check output below)"
        echo "$RESULT" | head -20
    fi

    # Test 2: Get quick report types
    print_info "Test 2: Getting quick report types..."
    RESULT=$(npx @modelcontextprotocol/inspector --cli \
        -e MCP_AUTH_ENABLED=false \
        -e MCP_TRANSPORT=stdio \
        -- uv run --directory applications/mcp-server python main.py \
        --method tools/call \
        --tool-name gam_get_quick_report_types 2>&1) || true

    if echo "$RESULT" | grep -q -i "delivery\|inventory\|sales"; then
        print_success "gam_get_quick_report_types - Retrieved report types"
    else
        print_warning "gam_get_quick_report_types - Could not verify output"
        echo "$RESULT" | head -20
    fi

    # Test 3: Get common combinations
    print_info "Test 3: Getting common dimension-metric combinations..."
    RESULT=$(npx @modelcontextprotocol/inspector --cli \
        -e MCP_AUTH_ENABLED=false \
        -e MCP_TRANSPORT=stdio \
        -- uv run --directory applications/mcp-server python main.py \
        --method tools/call \
        --tool-name gam_get_common_combinations 2>&1) || true

    if echo "$RESULT" | grep -q -i "combination\|dimensions\|metrics"; then
        print_success "gam_get_common_combinations - Retrieved combinations"
    else
        print_warning "gam_get_common_combinations - Could not verify output"
        echo "$RESULT" | head -20
    fi

    # Test 4: Get dimensions and metrics
    print_info "Test 4: Getting dimensions and metrics..."
    RESULT=$(npx @modelcontextprotocol/inspector --cli \
        -e MCP_AUTH_ENABLED=false \
        -e MCP_TRANSPORT=stdio \
        -- uv run --directory applications/mcp-server python main.py \
        --method tools/call \
        --tool-name gam_get_dimensions_metrics \
        --tool-arg report_type=HISTORICAL \
        --tool-arg category=both 2>&1) || true

    if echo "$RESULT" | grep -q -i "DATE\|IMPRESSIONS\|dimensions\|metrics"; then
        print_success "gam_get_dimensions_metrics - Retrieved fields"
    else
        print_warning "gam_get_dimensions_metrics - Could not verify output"
        echo "$RESULT" | head -20
    fi

    echo ""
    print_header "CLI Tests Complete"
}

run_http_tests() {
    print_header "Running HTTP Transport Tests"

    echo "Testing server at: $LOCAL_HTTP_URL"
    echo ""
    print_warning "Make sure your server is running:"
    echo "  make mcp-http  OR"
    echo "  MCP_TRANSPORT=http python applications/mcp-server/main.py"
    echo ""

    # Check if server is running
    if ! curl -s --connect-timeout 2 "http://localhost:8080/health" > /dev/null 2>&1; then
        print_error "Server not reachable at localhost:8080"
        echo ""
        echo "Start the server first:"
        echo "  MCP_TRANSPORT=http MCP_AUTH_ENABLED=false python applications/mcp-server/main.py"
        exit 1
    fi

    print_success "Server is running"
    echo ""

    # Test 1: List tools via HTTP
    print_info "Test 1: Listing tools via HTTP..."
    RESULT=$(npx @modelcontextprotocol/inspector --cli \
        "$LOCAL_HTTP_URL" \
        --transport http \
        --method tools/list 2>&1) || true

    if echo "$RESULT" | grep -q "gam_quick_report"; then
        print_success "tools/list via HTTP - Found tools"
    else
        print_warning "tools/list via HTTP - Could not verify"
        echo "$RESULT" | head -20
    fi

    # Test 2: Call tool via HTTP
    print_info "Test 2: Calling gam_get_quick_report_types via HTTP..."
    RESULT=$(npx @modelcontextprotocol/inspector --cli \
        "$LOCAL_HTTP_URL" \
        --transport http \
        --method tools/call \
        --tool-name gam_get_quick_report_types 2>&1) || true

    if echo "$RESULT" | grep -q -i "delivery\|inventory"; then
        print_success "Tool call via HTTP - Success"
    else
        print_warning "Tool call via HTTP - Could not verify"
        echo "$RESULT" | head -20
    fi

    print_header "HTTP Tests Complete"
}

run_cloud_tests() {
    print_header "Running Cloud Run Tests"

    echo "Testing server at: $CLOUD_URL"
    echo ""

    # Check for JWT token
    if [ -z "$GAM_MCP_JWT_TOKEN" ]; then
        print_warning "GAM_MCP_JWT_TOKEN not set"
        echo ""
        echo "Set your JWT token:"
        echo "  export GAM_MCP_JWT_TOKEN='your-jwt-token'"
        echo ""
        echo "Running without authentication (may fail)..."
    fi

    # Test 1: List tools (may require auth)
    print_info "Test 1: Listing tools on Cloud Run..."

    if [ -n "$GAM_MCP_JWT_TOKEN" ]; then
        # With auth header
        RESULT=$(npx @modelcontextprotocol/inspector --cli \
            "$CLOUD_URL" \
            --transport http \
            --header "Authorization: Bearer $GAM_MCP_JWT_TOKEN" \
            --method tools/list 2>&1) || true
    else
        RESULT=$(npx @modelcontextprotocol/inspector --cli \
            "$CLOUD_URL" \
            --transport http \
            --method tools/list 2>&1) || true
    fi

    if echo "$RESULT" | grep -q "gam_quick_report"; then
        print_success "Cloud Run tools/list - Success"
    elif echo "$RESULT" | grep -q -i "unauthorized\|401"; then
        print_error "Cloud Run requires authentication"
        echo "  Set: export GAM_MCP_JWT_TOKEN='your-token'"
    else
        print_warning "Could not verify Cloud Run connection"
        echo "$RESULT" | head -20
    fi

    print_header "Cloud Tests Complete"
}

show_usage() {
    echo "MCP Inspector Test Script for GAM API"
    echo ""
    echo "Usage:"
    echo "  $0              # Interactive UI mode with config"
    echo "  $0 --ui         # Simple UI mode (configure manually)"
    echo "  $0 --cli        # Run CLI tests (STDIO transport)"
    echo "  $0 --http       # Run HTTP transport tests"
    echo "  $0 --cloud      # Test Cloud Run deployment"
    echo "  $0 --all        # Run all tests"
    echo "  $0 --help       # Show this help"
    echo ""
    echo "Environment Variables:"
    echo "  GAM_MCP_JWT_TOKEN   JWT token for Cloud Run authentication"
    echo ""
    echo "Examples:"
    echo "  # Start interactive inspector"
    echo "  $0"
    echo ""
    echo "  # Run automated CLI tests"
    echo "  $0 --cli"
    echo ""
    echo "  # Test local HTTP server"
    echo "  MCP_TRANSPORT=http python applications/mcp-server/main.py &"
    echo "  $0 --http"
    echo ""
    echo "  # Test Cloud Run with auth"
    echo "  export GAM_MCP_JWT_TOKEN='eyJ...'"
    echo "  $0 --cloud"
}

# Main
case "${1:-}" in
    --help|-h)
        show_usage
        ;;
    --cli)
        check_requirements
        run_cli_tests
        ;;
    --ui)
        check_requirements
        run_ui_mode_simple
        ;;
    --http)
        check_requirements
        run_http_tests
        ;;
    --cloud)
        check_requirements
        run_cloud_tests
        ;;
    --all)
        check_requirements
        run_cli_tests
        run_http_tests
        run_cloud_tests
        ;;
    *)
        check_requirements
        run_ui_mode
        ;;
esac
