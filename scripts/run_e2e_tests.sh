#!/bin/bash
# End-to-end test runner for MCP Server Docker container
#
# Usage:
#   ./scripts/run_e2e_tests.sh           # Run full e2e tests
#   ./scripts/run_e2e_tests.sh --quick   # Quick smoke test only
#   ./scripts/run_e2e_tests.sh --keep    # Keep container running after tests
#   ./scripts/run_e2e_tests.sh --no-build # Skip build, use existing image

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MCP_SERVER_DIR="$PROJECT_ROOT/applications/mcp-server"
COMPOSE_FILE="$MCP_SERVER_DIR/docker-compose.test.yml"
CONTAINER_NAME="mcp-server-mcp-server-1"
MCP_SERVER_URL="http://localhost:8080"
HEALTH_ENDPOINT="$MCP_SERVER_URL/health"

# Parse arguments
QUICK_TEST=false
KEEP_CONTAINER=false
SKIP_BUILD=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            QUICK_TEST=true
            shift
            ;;
        --keep)
            KEEP_CONTAINER=true
            shift
            ;;
        --no-build)
            SKIP_BUILD=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --quick      Run quick smoke test only"
            echo "  --keep       Keep container running after tests"
            echo "  --no-build   Skip Docker build, use existing image"
            echo "  -v, --verbose Enable verbose output"
            echo "  -h, --help   Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi

    if ! command -v uv &> /dev/null; then
        log_warning "uv not found, will try with pip"
    fi

    log_success "Prerequisites check passed"
}

# Cleanup function
cleanup() {
    if [ "$KEEP_CONTAINER" = false ]; then
        log_info "Cleaning up..."
        cd "$MCP_SERVER_DIR"
        docker compose -f docker-compose.test.yml down --remove-orphans 2>/dev/null || true
        log_success "Cleanup complete"
    else
        log_info "Container kept running (use 'docker compose -f $COMPOSE_FILE down' to stop)"
    fi
}

# Set trap for cleanup on exit
trap cleanup EXIT

# Build Docker image
build_image() {
    if [ "$SKIP_BUILD" = true ]; then
        log_info "Skipping build (--no-build flag)"
        return 0
    fi

    log_info "Building Docker image..."
    cd "$MCP_SERVER_DIR"

    if [ "$VERBOSE" = true ]; then
        docker compose -f docker-compose.test.yml build
    else
        docker compose -f docker-compose.test.yml build --quiet
    fi

    log_success "Docker image built successfully"
}

# Start container
start_container() {
    log_info "Starting MCP server container..."
    cd "$MCP_SERVER_DIR"

    # Stop any existing container
    docker compose -f docker-compose.test.yml down --remove-orphans 2>/dev/null || true

    # Start container
    docker compose -f docker-compose.test.yml up -d

    log_success "Container started"
}

# Wait for server to be ready
wait_for_server() {
    log_info "Waiting for server to be ready..."
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$HEALTH_ENDPOINT" > /dev/null 2>&1; then
            log_success "Server is ready!"
            return 0
        fi
        echo -n "."
        sleep 1
        ((attempt++))
    done

    echo ""
    log_error "Server failed to start within ${max_attempts}s"

    # Show container logs for debugging
    log_info "Container logs:"
    cd "$MCP_SERVER_DIR"
    docker compose -f docker-compose.test.yml logs --tail=50

    exit 1
}

# Run quick smoke test
run_smoke_test() {
    log_info "Running smoke test..."

    # Test health endpoint
    local health_response=$(curl -s "$HEALTH_ENDPOINT")
    if [ "$health_response" = "OK" ]; then
        log_success "Health check: OK"
    else
        log_error "Health check failed: $health_response"
        return 1
    fi

    # Test OAuth discovery endpoint
    local oauth_response=$(curl -s -w "%{http_code}" -o /dev/null "$MCP_SERVER_URL/.well-known/oauth-protected-resource")
    if [ "$oauth_response" = "200" ]; then
        log_success "OAuth discovery: OK"
    else
        log_warning "OAuth discovery returned: $oauth_response"
    fi

    log_success "Smoke test passed!"
}

# Run full e2e tests
run_e2e_tests() {
    log_info "Running full e2e tests..."

    cd "$PROJECT_ROOT"

    # Install test dependencies if needed
    if [ -f "$MCP_SERVER_DIR/.venv/bin/pytest" ]; then
        PYTEST="$MCP_SERVER_DIR/.venv/bin/pytest"
    elif command -v uv &> /dev/null; then
        # Use uv to run pytest from the mcp-server venv
        cd "$MCP_SERVER_DIR"
        PYTEST="uv run pytest"
    else
        log_error "pytest not found. Please install test dependencies."
        exit 1
    fi

    # Create e2e test directory if missing __init__.py
    mkdir -p "$PROJECT_ROOT/tests/e2e"
    touch "$PROJECT_ROOT/tests/e2e/__init__.py"

    # Run tests
    cd "$MCP_SERVER_DIR"
    export MCP_SERVER_URL="$MCP_SERVER_URL"

    if [ "$VERBOSE" = true ]; then
        $PYTEST "$PROJECT_ROOT/tests/e2e/test_mcp_server_docker.py" -v --tb=short
    else
        $PYTEST "$PROJECT_ROOT/tests/e2e/test_mcp_server_docker.py" -v --tb=line
    fi

    local test_result=$?

    if [ $test_result -eq 0 ]; then
        log_success "All e2e tests passed!"
    else
        log_error "Some e2e tests failed"
        return $test_result
    fi
}

# Show container logs
show_logs() {
    log_info "Container logs:"
    cd "$MCP_SERVER_DIR"
    docker compose -f docker-compose.test.yml logs --tail=20
}

# Main execution
main() {
    echo ""
    echo "========================================"
    echo "  MCP Server E2E Test Runner"
    echo "========================================"
    echo ""

    check_prerequisites
    build_image
    start_container
    wait_for_server

    if [ "$QUICK_TEST" = true ]; then
        run_smoke_test
    else
        run_smoke_test
        run_e2e_tests
    fi

    echo ""
    log_success "All tests completed successfully!"

    if [ "$KEEP_CONTAINER" = true ]; then
        echo ""
        log_info "Container is still running at $MCP_SERVER_URL"
        log_info "View logs: docker compose -f $COMPOSE_FILE logs -f"
        log_info "Stop: docker compose -f $COMPOSE_FILE down"
    fi
}

main "$@"
