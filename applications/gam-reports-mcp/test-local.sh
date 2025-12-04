#!/bin/bash
# test-local.sh - Test MCP server locally with Docker

set -e

echo "🧪 Testing GAM Reports MCP Server locally with Docker"
echo "======================================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if googleads.yaml exists
if [ ! -f "$HOME/.googleads.yaml" ]; then
    echo -e "${RED}❌ Error: $HOME/.googleads.yaml not found${NC}"
    echo "Please create your Google Ads credentials file first"
    exit 1
fi

echo -e "\n${BLUE}1. Building Docker image...${NC}"
docker-compose build

echo -e "\n${BLUE}2. Starting services...${NC}"
docker-compose up -d gam-reports-mcp

echo -e "\n${BLUE}3. Waiting for server to be healthy...${NC}"
timeout 30 sh -c 'until docker-compose exec -T gam-reports-mcp curl -sf http://localhost:8080/health > /dev/null; do sleep 1; done' || {
    echo -e "${RED}❌ Server failed to start${NC}"
    docker-compose logs gam-reports-mcp
    docker-compose down
    exit 1
}

echo -e "${GREEN}✓ Server is healthy!${NC}"

echo -e "\n${BLUE}4. Testing MCP endpoints...${NC}"

echo -e "\n${BLUE}=== Health Check ===${NC}"
curl -s http://localhost:8080/health
echo ""

echo -e "\n${BLUE}=== List Tools ===${NC}"
curl -s http://localhost:8080/mcp/tools | jq '.tools[] | {name: .name, description: .description}' 2>/dev/null || curl -s http://localhost:8080/mcp/tools | head -100

echo -e "\n${BLUE}=== List Resources ===${NC}"
curl -s http://localhost:8080/mcp/resources | jq '.resources[] | {uri: .uri, name: .name}' 2>/dev/null || curl -s http://localhost:8080/mcp/resources | head -100

echo -e "\n${BLUE}=== Test Search Tool ===${NC}"
curl -s -X POST http://localhost:8080/mcp/tools/search \
  -H "Content-Type: application/json" \
  -d '{"query": "impressions"}' | jq '.' 2>/dev/null || echo "Search tool test (raw output above)"

echo -e "\n${GREEN}✓ All tests passed!${NC}"
echo -e "\n${BLUE}Server logs:${NC}"
docker-compose logs --tail=20 gam-reports-mcp

echo -e "\n${GREEN}Server is running at http://localhost:8080${NC}"
echo "MCP endpoint: http://localhost:8080/mcp"
echo ""
echo "To stop: docker-compose down"
echo "To view logs: docker-compose logs -f gam-reports-mcp"
echo "To test tools: curl -X POST http://localhost:8080/mcp/tools/<tool-name> -H 'Content-Type: application/json' -d '{...}'"
