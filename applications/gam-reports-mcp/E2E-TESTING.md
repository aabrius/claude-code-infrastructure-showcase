# E2E Testing Guide

Quick reference for running end-to-end tests with local Docker setup.

## Quick Start

```bash
# Run all E2E tests (automated)
./run-e2e-tests.sh
```

## What Gets Tested

### ✅ Server Health & Discovery (6 tests)
- Health endpoint responds
- Lists all 7 tools
- Lists all 4 resources
- Validates tool and resource schemas

### ✅ MCP Resources (12 tests)
- `gam://context` - Network config, 27 domains, 2 apps, 3 strategies
- `gam://dimensions` - All dimensions organized by category
- `gam://metrics` - All metrics with Ad Exchange support
- `gam://templates` - 6+ report templates

### ✅ MCP Tools (14 tests)
- `search` - Find dimensions, metrics, templates by query
- `get_available_options` - Get all available options
- `create_report` - Validate report parameters
- `list_saved_reports` - List functionality
- `update_report` - Update validation
- `delete_report` - Delete validation
- `run_and_fetch_report` - Execution validation

### ✅ User Workflows (5 tests)
- Report discovery journey
- Media arbitrage analysis journey
- App mediation revenue journey
- Domain performance journey
- Report creation with validation

**Total: 37 E2E tests**

## Test Commands

```bash
# Run all tests
./run-e2e-tests.sh

# Run specific test file
./run-e2e-tests.sh tests/e2e/test_01_server_health.py

# Run specific test class
./run-e2e-tests.sh -k TestSearchTool

# Run specific test
./run-e2e-tests.sh -k test_search_for_impressions

# Run with verbose output
./run-e2e-tests.sh -vv

# Run with live logs
./run-e2e-tests.sh -s

# Run against remote server
MCP_SERVER_URL=https://gam-reports-mcp-xxx.run.app ./run-e2e-tests.sh
```

## Test Against Existing Server

```bash
# If server already running, tests will use it
curl http://localhost:8080/health  # Verify server is up
./run-e2e-tests.sh                 # Will skip server startup
```

## Expected Results

### ✅ Without GAM Credentials (30+ tests pass)
- All server health tests pass
- All resource read tests pass
- All tool validation tests pass
- All workflow discovery tests pass
- Report creation fails with auth errors (expected)

### ✅ With GAM Credentials (37 tests pass)
- All tests above pass
- Report creation may succeed (depending on API limits)
- GAM API integration fully tested

## Test Structure

```
tests/e2e/
├── conftest.py              # Fixtures (http_client, endpoints)
├── helpers.py               # API call helpers
├── test_01_server_health.py # 6 tests - Health & discovery
├── test_02_resources.py     # 12 tests - All 4 resources
├── test_03_tools.py         # 14 tests - All 7 tools
└── test_04_workflows.py     # 5 tests - User journeys
```

## Docker Setup

E2E tests use `docker-compose.e2e.yml`:
- Builds from Dockerfile
- Mounts `~/.googleads.yaml` for GAM auth
- Exposes port 8080
- Health checks enabled
- Auto-restart on failure

## Troubleshooting

### Server won't start
```bash
# Check logs
docker-compose -f docker-compose.e2e.yml logs gam-reports-mcp

# Rebuild
docker-compose -f docker-compose.e2e.yml build --no-cache
docker-compose -f docker-compose.e2e.yml up
```

### Port 8080 in use
```bash
# Find process
lsof -i :8080

# Stop existing server
docker-compose down
```

### Tests timeout
```bash
# Increase wait time
MAX_WAIT_TIME=120 ./run-e2e-tests.sh
```

### Missing dependencies
```bash
# Install dev dependencies with httpx
uv sync --group dev
# or
pip install -e ".[dev]"
```

## Manual Testing

### Test endpoints manually
```bash
# Start server
docker-compose -f docker-compose.e2e.yml up -d

# Health check
curl http://localhost:8080/health

# List tools
curl http://localhost:8080/mcp/tools | jq '.tools[] | {name, description}'

# List resources
curl http://localhost:8080/mcp/resources | jq '.resources[] | {uri, name}'

# Call search tool
curl -X POST http://localhost:8080/mcp/tools/search \
  -H "Content-Type: application/json" \
  -d '{"query": "impressions"}' | jq '.'

# Read context resource
curl -X POST http://localhost:8080/mcp/resources/read \
  -H "Content-Type: application/json" \
  -d '{"uri": "gam://context"}' | jq '.'
```

## CI/CD Integration

### Local Pre-commit Hook
```bash
# Add to .git/hooks/pre-push
#!/bin/bash
cd applications/gam-reports-mcp
./run-e2e-tests.sh || exit 1
```

### GitHub Actions
```yaml
- name: Run E2E Tests
  run: |
    cd applications/gam-reports-mcp
    ./run-e2e-tests.sh
```

## Performance

- **Test suite runtime**: ~5-10 seconds (server running)
- **With server startup**: ~15-20 seconds
- **Average test time**: <1 second
- **Health check timeout**: 60 seconds max

## Coverage Summary

| Component | Tests | Coverage |
|-----------|-------|----------|
| Health & Discovery | 6 | 100% |
| Resources (4) | 12 | 100% |
| Tools (7) | 14 | 100% |
| Workflows | 5 | 100% |
| **Total** | **37** | **100%** |

## Next Steps

After E2E tests pass:
1. ✅ Local Docker setup verified
2. ✅ All MCP endpoints working
3. ✅ Ready for Cloud Run deployment
4. ✅ Run `./deploy.sh` to deploy to GCP

## Documentation

- Full E2E test documentation: `tests/e2e/README.md`
- Deployment guide: `DEPLOYMENT.md`
- Local testing: `test-local.sh`
- This guide: `E2E-TESTING.md`
