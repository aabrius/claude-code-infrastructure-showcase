# E2E Test Suite for GAM Reports MCP Server

Comprehensive end-to-end tests for the GAM Reports MCP Server running in Docker.

## Overview

The E2E test suite validates the complete MCP server functionality:
- **Server health and availability**
- **MCP discovery** (tools and resources)
- **4 MCP resources** (context, dimensions, metrics, templates)
- **7 MCP tools** (search, create_report, etc.)
- **Complete workflows** (user journeys)

## Test Structure

```
tests/e2e/
├── README.md                    # This file
├── conftest.py                  # Pytest fixtures and setup
├── helpers.py                   # Helper functions for API calls
├── test_01_server_health.py     # Health checks and discovery
├── test_02_resources.py         # MCP resource tests
├── test_03_tools.py             # MCP tool tests
└── test_04_workflows.py         # Complete user journey tests
```

## Running E2E Tests

### Quick Start

```bash
# From project root
./run-e2e-tests.sh
```

This script will:
1. Start the MCP server in Docker
2. Wait for server to be healthy
3. Run all E2E tests
4. Show results and logs
5. Clean up containers

### Manual Execution

```bash
# Start server
docker-compose -f docker-compose.e2e.yml up -d

# Wait for health check
curl http://localhost:8080/health

# Run tests
uv run pytest tests/e2e/ -v

# Stop server
docker-compose -f docker-compose.e2e.yml down
```

### Run Specific Test Classes

```bash
# Server health tests only
./run-e2e-tests.sh -k TestServerHealth

# Resource tests only
./run-e2e-tests.sh -k TestContextResource

# Tool tests only
./run-e2e-tests.sh -k TestSearchTool

# Workflow tests only
./run-e2e-tests.sh -k TestReportDiscoveryWorkflow
```

### Run with Different Server

```bash
# Test against custom URL
MCP_SERVER_URL=http://custom-host:8080 ./run-e2e-tests.sh

# Test against Cloud Run deployment
MCP_SERVER_URL=https://gam-reports-mcp-xxx.run.app ./run-e2e-tests.sh
```

## Test Coverage

### Test 01: Server Health (6 tests)
- ✓ Health endpoint returns 200 OK
- ✓ Health check responds quickly (<500ms)
- ✓ Lists all 7 MCP tools
- ✓ Lists all 4 MCP resources
- ✓ Each tool has required fields
- ✓ Each resource has required fields

### Test 02: Resources (12 tests)
- **Context Resource (gam://context)**
  - ✓ Returns network, domains, apps, strategies
  - ✓ Has 27 domains
  - ✓ Has 2 apps (Android + iOS)
  - ✓ Has 3 ad strategies

- **Dimensions Resource (gam://dimensions)**
  - ✓ Returns all dimensions
  - ✓ Organized by category
  - ✓ Includes MOBILE_APP_ID dimension

- **Metrics Resource (gam://metrics)**
  - ✓ Returns all metrics
  - ✓ Organized by category
  - ✓ Includes Ad Exchange metrics

- **Templates Resource (gam://templates)**
  - ✓ Returns report templates
  - ✓ Includes media_arbitrage_daily
  - ✓ Includes app_mediation

### Test 03: Tools (14 tests)
- **search** - Find dimensions, metrics, templates
  - ✓ Search for impressions
  - ✓ Search for date dimension
  - ✓ Search with category filter
  - ✓ Search for templates

- **get_available_options** - Get all options
  - ✓ Returns dimensions, metrics, templates

- **create_report** - Validate report creation
  - ✓ Rejects invalid dimensions
  - ✓ Rejects invalid metrics
  - ✓ Accepts valid parameters

- **list_saved_reports** - List reports
  - ✓ Attempts to list (may fail without GAM auth)

- **update_report** - Update report
  - ✓ Requires report_id

- **delete_report** - Delete report
  - ✓ Requires report_id

- **run_and_fetch_report** - Execute report
  - ✓ Requires report_id

### Test 04: Workflows (5 tests)
- **Report Discovery Workflow**
  - ✓ User can discover what to report on

- **Media Arbitrage Workflow**
  - ✓ User can analyze arbitrage performance

- **App Mediation Workflow**
  - ✓ User can view mediation revenue

- **Domain Performance Workflow**
  - ✓ User can analyze domain performance

- **Report Creation Workflow**
  - ✓ User can create validated reports

## Test Requirements

### Dependencies
- Docker and Docker Compose
- pytest >= 8.0.0
- httpx >= 0.25.0
- GAM credentials file (optional, for full testing)

### Environment Variables
- `MCP_SERVER_URL` - Server base URL (default: http://localhost:8080)
- `COMPOSE_FILE` - Docker Compose file (default: docker-compose.e2e.yml)

## Expected Results

### With GAM Credentials
All tests should pass (37/37), including:
- Server health checks ✓
- Resource reads ✓
- Tool validations ✓
- Workflow tests ✓
- Report creation attempts (may succeed or fail depending on API limits)

### Without GAM Credentials
Most tests should pass (30+/37):
- Server health checks ✓
- Resource reads ✓
- Tool validations ✓ (validation only)
- Workflow tests ✓ (discovery and validation)
- Report creation will fail with authentication errors (expected)

## Troubleshooting

### Server Won't Start
```bash
# Check if port 8080 is in use
lsof -i :8080

# View server logs
docker-compose -f docker-compose.e2e.yml logs gam-reports-mcp

# Rebuild image
docker-compose -f docker-compose.e2e.yml build --no-cache
```

### Tests Timeout
```bash
# Increase max wait time
MAX_WAIT_TIME=120 ./run-e2e-tests.sh
```

### Connection Refused
```bash
# Verify server is running
curl http://localhost:8080/health

# Check Docker network
docker network ls
docker network inspect e2e-network
```

### GAM API Errors
```bash
# Verify credentials file exists
ls -la ~/.googleads.yaml

# Check if credentials are mounted
docker-compose -f docker-compose.e2e.yml exec gam-reports-mcp ls -la /app/.googleads.yaml
```

## CI/CD Integration

### GitHub Actions

```yaml
name: E2E Tests
on: [push, pull_request]
jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run E2E Tests
        run: |
          cd applications/gam-reports-mcp
          ./run-e2e-tests.sh
```

### GitLab CI

```yaml
e2e-tests:
  stage: test
  script:
    - cd applications/gam-reports-mcp
    - ./run-e2e-tests.sh
  services:
    - docker:dind
```

## Development

### Adding New Tests

1. Create test file in `tests/e2e/test_XX_name.py`
2. Use fixtures from `conftest.py`
3. Use helpers from `helpers.py`
4. Follow existing patterns (Arrange-Act-Assert)

Example:
```python
from .helpers import call_tool, assert_tool_response_success

def test_my_new_feature(http_client, mcp_endpoint):
    # Arrange
    params = {"param": "value"}

    # Act
    response = call_tool(http_client, mcp_endpoint, "tool_name", params)

    # Assert
    data = assert_tool_response_success(response, "tool_name")
    assert "expected_field" in data
```

### Debugging Tests

```bash
# Run with verbose output
./run-e2e-tests.sh -vv

# Run with pdb debugger
./run-e2e-tests.sh --pdb

# Run specific test
./run-e2e-tests.sh -k test_search_for_impressions

# Show print statements
./run-e2e-tests.sh -s
```

## Performance

E2E test suite completion time:
- **With healthy server**: ~5-10 seconds
- **With server startup**: ~15-20 seconds
- **Individual test**: <1 second average

## Coverage

E2E tests provide integration coverage for:
- ✅ All MCP endpoints
- ✅ All MCP tools (7/7)
- ✅ All MCP resources (4/4)
- ✅ Server health and discovery
- ✅ User workflows and journeys
- ✅ Validation logic
- ⚠️  GAM API integration (requires credentials)

For unit test coverage, see `tests/test_*.py`
