---
name: route-tester
description: Testing API routes with FastAPI TestClient, pytest, and httpx. Use when testing endpoints, validating route functionality, debugging API responses, or setting up integration tests. Covers API key authentication, async testing, fixtures, and testing patterns for GAM API routes.
---

# FastAPI Route Testing Guide

## Purpose

Comprehensive guide for testing FastAPI routes in the GAM API project using pytest, TestClient, and httpx async client.

## When to Use This Skill

- Testing new API endpoints after creation
- Validating route functionality after modifications
- Debugging authentication issues
- Writing integration tests for report endpoints
- Testing metadata endpoints
- Verifying error handling and validation
- Setting up test fixtures and utilities

---

## Quick Start

### Basic Test Structure

```python
# tests/test_routes.py
import pytest
from fastapi.testclient import TestClient
from applications.api-server.main import create_app

@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)

@pytest.fixture
def api_headers():
    return {"X-API-Key": "test-api-key"}

def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_authenticated_endpoint(client, api_headers):
    response = client.get("/api/v1/metadata/dimensions-metrics", headers=api_headers)
    assert response.status_code == 200
    assert "dimensions" in response.json()
```

---

## Testing Methods

### Method 1: FastAPI TestClient (Sync)

**Best for:** Quick tests, simple route validation

```python
from fastapi.testclient import TestClient

def test_quick_report(client, api_headers):
    response = client.post(
        "/api/v1/reports/quick",
        headers=api_headers,
        json={
            "report_type": "delivery",
            "date_range": {"start_date": "2024-01-01", "end_date": "2024-01-31"}
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
```

### Method 2: httpx AsyncClient (Async)

**Best for:** Async routes, integration tests

```python
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_async_report(async_client, api_headers):
    response = await async_client.post(
        "/api/v1/reports/custom",
        headers=api_headers,
        json={
            "dimensions": ["AD_UNIT_NAME"],
            "metrics": ["TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS"],
            "date_range": {"start_date": "2024-01-01", "end_date": "2024-01-31"}
        }
    )
    assert response.status_code == 200
```

### Method 3: curl (Manual Testing)

```bash
# Health check (no auth)
curl http://localhost:8000/api/v1/health

# Authenticated request
curl -H "X-API-Key: your-key" \
     http://localhost:8000/api/v1/metadata/dimensions-metrics

# Quick report
curl -X POST http://localhost:8000/api/v1/reports/quick \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"report_type":"delivery","date_range":{"start_date":"2024-01-01","end_date":"2024-01-31"}}'
```

---

## Essential Fixtures

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

@pytest.fixture(scope="module")
def app():
    return create_app()

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
async def async_client(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def api_headers():
    return {"X-API-Key": "test-api-key"}

@pytest.fixture
def sample_report_request():
    return {
        "report_type": "delivery",
        "date_range": {"start_date": "2024-01-01", "end_date": "2024-01-31"}
    }
```

See [fixtures-guide.md](resources/fixtures-guide.md) for complete fixture patterns.

---

## Testing Your Routes

### Health Endpoints (No Auth)

```python
def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_status(client):
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    assert "gam_connection" in response.json()
```

### Report Endpoints (Auth Required)

```python
def test_quick_report(client, api_headers, sample_report_request):
    response = client.post("/api/v1/reports/quick", headers=api_headers, json=sample_report_request)
    assert response.status_code == 200
    assert "report_id" in response.json()["data"]

def test_custom_report(client, api_headers):
    response = client.post(
        "/api/v1/reports/custom",
        headers=api_headers,
        json={
            "dimensions": ["AD_UNIT_NAME"],
            "metrics": ["TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS"],
            "date_range": {"start_date": "2024-01-01", "end_date": "2024-01-31"}
        }
    )
    assert response.status_code == 200
```

### Metadata Endpoints (Auth Required)

```python
def test_dimensions_metrics(client, api_headers):
    response = client.get("/api/v1/metadata/dimensions-metrics", headers=api_headers)
    assert response.status_code == 200
    assert "dimensions" in response.json()
    assert "metrics" in response.json()
```

See [route-examples.md](resources/route-examples.md) for complete examples.

---

## Authentication Testing

```python
def test_valid_api_key(client, api_headers):
    response = client.get("/api/v1/metadata/dimensions-metrics", headers=api_headers)
    assert response.status_code == 200

def test_missing_api_key(client):
    response = client.get("/api/v1/metadata/dimensions-metrics")
    assert response.status_code == 401

def test_invalid_api_key(client):
    response = client.get(
        "/api/v1/metadata/dimensions-metrics",
        headers={"X-API-Key": "invalid-key"}
    )
    assert response.status_code == 401
```

See [authentication-tests.md](resources/authentication-tests.md) for auth patterns.

---

## Error Handling Tests

```python
def test_invalid_report_type(client, api_headers):
    response = client.post(
        "/api/v1/reports/quick",
        headers=api_headers,
        json={"report_type": "invalid", "date_range": {"start_date": "2024-01-01", "end_date": "2024-01-31"}}
    )
    assert response.status_code == 400

def test_missing_required_fields(client, api_headers):
    response = client.post("/api/v1/reports/quick", headers=api_headers, json={"report_type": "delivery"})
    assert response.status_code == 422
```

See [error-tests.md](resources/error-tests.md) for comprehensive error testing.

---

## Integration Testing

```python
@pytest.mark.integration
async def test_full_report_flow(async_client, api_headers):
    # Create report
    create_resp = await async_client.post(
        "/api/v1/reports/quick",
        headers=api_headers,
        json={"report_type": "delivery", "date_range": {"start_date": "2024-01-01", "end_date": "2024-01-31"}}
    )
    assert create_resp.status_code == 200
    report_id = create_resp.json()["data"]["report_id"]

    # Verify in list
    list_resp = await async_client.get("/api/v1/reports", headers=api_headers)
    assert any(r["id"] == report_id for r in list_resp.json()["reports"])
```

See [integration-tests.md](resources/integration-tests.md) for workflow testing.

---

## Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_reports.py

# With coverage
pytest --cov=applications/api-server --cov-report=html

# Integration only
pytest -m integration

# Verbose
pytest -v

# Stop on first failure
pytest -x
```

### Test Markers

```python
@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.external
@pytest.mark.skipif("CI" in os.environ, reason="Local only")
```

See [pytest-configuration.md](resources/pytest-configuration.md) for complete setup.

---

## Common Patterns

### Parametrized Tests

```python
@pytest.mark.parametrize("report_type", ["delivery", "inventory", "sales", "reach", "programmatic"])
def test_all_report_types(client, api_headers, report_type):
    response = client.post(
        "/api/v1/reports/quick",
        headers=api_headers,
        json={"report_type": report_type, "date_range": {"start_date": "2024-01-01", "end_date": "2024-01-31"}}
    )
    assert response.status_code == 200
```

### Mocking GAM Client

```python
from unittest.mock import patch

def test_with_mocked_gam(client, api_headers):
    with patch('gam_api.client.GAMClient') as mock_gam:
        mock_gam.return_value.create_report.return_value = {"report_id": "123", "rows": []}
        response = client.post("/api/v1/reports/quick", headers=api_headers, json={...})
        assert response.status_code == 200
```

See [testing-patterns.md](resources/testing-patterns.md) for more patterns.

---

## Testing Checklist

**Before testing:**
- [ ] Identify endpoint path
- [ ] Determine if auth required
- [ ] Prepare request data
- [ ] Create fixtures
- [ ] Write happy path test
- [ ] Write error tests

**After creating route:**
- [ ] Test valid data
- [ ] Test invalid data
- [ ] Test without auth
- [ ] Test with invalid auth
- [ ] Test edge cases
- [ ] Check error messages
- [ ] Verify OpenAPI docs

---

## Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── test_health.py           # Health endpoints
├── test_reports.py          # Report endpoints
├── test_metadata.py         # Metadata endpoints
├── test_authentication.py   # Auth tests
├── test_validation.py       # Validation tests
└── integration/
    ├── test_report_flow.py
    └── test_error_scenarios.py
```

---

## Key Differences from Node.js

**Authentication:**
- ❌ No cookie-based JWT / Keycloak
- ✅ API key in `X-API-Key` header

**Testing:**
- ❌ No Mocha/Jest / test-auth-route.js
- ✅ pytest + TestClient + httpx

**Project:**
- ❌ No blog-api, notifications
- ✅ GAM API with api-server, mcp-server

---

## Reference Files

### [fixtures-guide.md](resources/fixtures-guide.md)
Pytest fixtures: basic, advanced, scopes, async patterns

### [route-examples.md](resources/route-examples.md)
Complete examples: health, reports, metadata, pagination

### [authentication-tests.md](resources/authentication-tests.md)
Auth patterns: valid, missing, invalid API keys

### [error-tests.md](resources/error-tests.md)
Error testing: validation, invalid input, edge cases

### [integration-tests.md](resources/integration-tests.md)
Integration: workflows, multi-step, mocking, e2e

### [testing-patterns.md](resources/testing-patterns.md)
Patterns: parametrized, mocking, builders, assertions

### [pytest-configuration.md](resources/pytest-configuration.md)
Configuration: pytest.ini, env vars, coverage, CI/CD

---

## Resources

**Documentation:**
- https://fastapi.tiangolo.com/tutorial/testing/
- https://docs.pytest.org/
- https://www.python-httpx.org/

**Project Files:**
- `applications/api-server/main.py` - FastAPI app
- `applications/api-server/auth.py` - Authentication
- `applications/api-server/routes/` - All routes
- `tests/` - Test suite

---

**Status**: Following 500-line rule ✅
**Line Count**: 434 lines (under 500) ✅
**Reference Files**: 7 guides for details ✅
