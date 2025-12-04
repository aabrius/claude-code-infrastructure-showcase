#!/bin/bash
# run-e2e-tests.sh - Run E2E tests against local Docker MCP server

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  GAM Reports MCP - E2E Test Suite${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Configuration
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.e2e.yml}"
SERVER_URL="${MCP_SERVER_URL:-http://localhost:8080}"
MAX_WAIT_TIME=60

# Check if googleads.yaml exists
if [ ! -f "$HOME/.googleads.yaml" ]; then
    echo -e "${YELLOW}⚠️  Warning: $HOME/.googleads.yaml not found${NC}"
    echo -e "${YELLOW}   Some tests may fail without GAM credentials${NC}"
    echo ""
fi

# Clean up function
cleanup() {
    echo -e "\n${BLUE}Cleaning up...${NC}"
    docker-compose -f "${COMPOSE_FILE}" down -v 2>/dev/null || true
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Check if server is already running
if curl -sf "${SERVER_URL}/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Server already running at ${SERVER_URL}${NC}"
    USE_EXISTING_SERVER=true
else
    echo -e "${BLUE}Starting MCP server with Docker Compose...${NC}"
    docker-compose -f "${COMPOSE_FILE}" up -d gam-reports-mcp
    USE_EXISTING_SERVER=false

    echo -e "${BLUE}Waiting for server to be ready...${NC}"
    WAITED=0
    while [ $WAITED -lt $MAX_WAIT_TIME ]; do
        if curl -sf "${SERVER_URL}/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Server is ready!${NC}"
            break
        fi
        sleep 1
        WAITED=$((WAITED + 1))
        echo -n "."
    done
    echo ""

    if [ $WAITED -ge $MAX_WAIT_TIME ]; then
        echo -e "${RED}❌ Server failed to start within ${MAX_WAIT_TIME}s${NC}"
        echo -e "${RED}Checking logs:${NC}"
        docker-compose -f "${COMPOSE_FILE}" logs gam-reports-mcp
        exit 1
    fi
fi

# Run E2E tests
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Running E2E Tests${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

export MCP_SERVER_URL="${SERVER_URL}"

# Run tests with pytest
if command -v uv &> /dev/null; then
    echo -e "${BLUE}Using uv to run tests...${NC}"
    uv run pytest tests/e2e/ -v --tb=short --color=yes "$@"
    TEST_EXIT_CODE=$?
else
    echo -e "${BLUE}Using pytest directly...${NC}"
    pytest tests/e2e/ -v --tb=short --color=yes "$@"
    TEST_EXIT_CODE=$?
fi

echo ""

# Show results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}  ✓ All E2E Tests Passed!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}  ✗ Some E2E Tests Failed${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if [ "$USE_EXISTING_SERVER" = false ]; then
        echo -e "\n${BLUE}Server logs:${NC}"
        docker-compose -f "${COMPOSE_FILE}" logs --tail=50 gam-reports-mcp
    fi
fi

# Show server info
echo ""
echo -e "${BLUE}Server Information:${NC}"
echo -e "  URL: ${SERVER_URL}"
echo -e "  Health: ${SERVER_URL}/health"
echo -e "  MCP: ${SERVER_URL}/mcp"
echo ""

if [ "$USE_EXISTING_SERVER" = false ]; then
    echo -e "${BLUE}To view server logs:${NC}"
    echo -e "  docker-compose -f ${COMPOSE_FILE} logs -f gam-reports-mcp"
    echo ""
    echo -e "${BLUE}To stop server:${NC}"
    echo -e "  docker-compose -f ${COMPOSE_FILE} down"
    echo ""
fi

exit $TEST_EXIT_CODE
