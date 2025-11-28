---
name: python-fastapi-guidelines
description: Comprehensive backend development guide for Python/FastAPI with Pydantic validation. Use when creating routes, API endpoints, working with FastAPI routers, Pydantic models, async/await patterns, dependency injection, middleware, error handling, and API authentication. Covers clean architecture (routes → business logic → data access), consistent error handling, performance optimization, and testing strategies for Python microservices.
---

# Python FastAPI Development Guidelines

## Purpose

Establish consistency and best practices for Python/FastAPI backend services (GAM API, MCP Server) using modern async patterns, Pydantic validation, and clean architecture principles.

## When to Use This Skill

Automatically activates when working on:
- Creating or modifying API routes and endpoints
- Building FastAPI routers and path operations
- Implementing Pydantic models for validation
- Async/await patterns and coroutines
- Dependency injection with FastAPI Depends
- Middleware (CORS, authentication, logging)
- Error handling and exception handlers
- API authentication (API keys, OAuth2, JWT)
- Configuration management
- Backend testing and refactoring

---

## Quick Start

### New API Endpoint Checklist

- [ ] **Route**: Clean path operation in router file
- [ ] **Pydantic Models**: Request and response models
- [ ] **Validation**: Use Pydantic validators
- [ ] **Error Handling**: Try-except with proper HTTP exceptions
- [ ] **Dependencies**: Use FastAPI Depends for auth/config
- [ ] **Async/Await**: Use async def for I/O operations
- [ ] **Logging**: Structured logging with context
- [ ] **Tests**: Unit and integration tests
- [ ] **Documentation**: Docstrings and OpenAPI examples

### New FastAPI Service Checklist

- [ ] Directory structure (routes/, models/, auth/, config/)
- [ ] Main FastAPI app with middleware stack
- [ ] Pydantic BaseSettings for configuration
- [ ] Exception handlers for common errors
- [ ] Authentication dependencies
- [ ] CORS middleware configuration
- [ ] Structured logging setup
- [ ] Testing framework (pytest + httpx)

---

## Architecture Overview

### Clean Architecture

```
HTTP Request
    ↓
Routes (path operations only)
    ↓
Business Logic (services/functions)
    ↓
Data Access (clients/adapters)
    ↓
External APIs / Database
```

**Key Principle:** Each layer has ONE responsibility.

See [architecture-overview.md](resources/architecture-overview.md) for complete details.

---

## Directory Structure

```
applications/api-server/
├── main.py                  # FastAPI app creation
├── auth.py                  # Authentication
├── models.py                # Pydantic models
├── routes/
│   ├── __init__.py
│   ├── health.py           # Health endpoints
│   ├── reports.py          # Report endpoints
│   └── metadata.py         # Metadata endpoints
└── tests/
    └── test_routes.py

packages/core/src/gam_api/
├── auth.py                  # OAuth2 authentication
├── client.py                # GAM API client
├── models.py                # Data models
├── exceptions.py            # Custom exceptions
└── adapters/                # API adapters

packages/shared/src/gam_shared/
├── logger.py                # Structured logging
├── validators.py            # Validation utilities
└── formatters.py            # Data formatters
```

**Naming Conventions:**
- Modules: `snake_case` - `report_service.py`
- Classes: `PascalCase` - `ReportService`, `GAMClient`
- Functions: `snake_case` - `generate_report()`, `get_api_key()`
- Pydantic Models: `PascalCase` - `ReportRequest`, `ReportResponse`

---

## Core Principles (7 Key Rules)

### 1. Routes Only Route, Logic Stays Separate

```python
# ❌ NEVER: Business logic in routes
@router.post("/submit")
async def submit(request: dict):
    # 200 lines of logic
    pass

# ✅ ALWAYS: Delegate to business logic
@router.post("/submit")
async def submit(request: SubmitRequest):
    return await process_submission(request)
```

### 2. Use Pydantic for All Validation

```python
from pydantic import BaseModel, Field, validator

class ReportRequest(BaseModel):
    report_type: str = Field(..., description="Report type")
    days_back: int = Field(7, ge=1, le=365)

    @validator('report_type')
    def validate_type(cls, v):
        if v not in VALID_TYPES:
            raise ValueError(f"Invalid type: {v}")
        return v
```

### 3. All Errors Should Be Logged

```python
from gam_shared.logger import get_structured_logger

logger = get_structured_logger('api_reports')

try:
    result = await operation()
except Exception as e:
    logger.logger.error(f"Operation failed: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Operation failed")
```

### 4. Use Configuration, NEVER Hardcode

```python
# ❌ NEVER
API_KEY = "hardcoded-key"

# ✅ ALWAYS
from gam_api.config import get_config
config = get_config()
api_keys = config.api.api_keys
```

### 5. Async/Await for I/O Operations

```python
# ✅ Use async def for I/O operations
@router.get("/data")
async def get_data():
    data = await fetch_from_api()  # async I/O
    return data

# ✅ Sync functions for CPU-bound work
def process_data(data: List[dict]) -> List[dict]:
    return [transform(item) for item in data]
```

### 6. Use Dependency Injection

```python
from fastapi import Depends

async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key not in VALID_KEYS:
        raise HTTPException(401, "Invalid API key")
    return api_key

@router.get("/protected")
async def protected(api_key: str = Depends(get_api_key)):
    return {"message": "Access granted"}
```

### 7. Comprehensive Testing Required

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_report():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/reports", json={...})
        assert response.status_code == 200
```

---

## Common Imports

```python
# FastAPI
from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Pydantic
from pydantic import BaseModel, Field, validator

# Typing
from typing import List, Dict, Optional, Union, Any

# Async
import asyncio
import httpx

# Logging
from gam_shared.logger import get_structured_logger

# Project modules
from gam_api import GAMClient, DateRange
from gam_api.exceptions import GAMError, ValidationError
```

---

## Quick Reference

### HTTP Status Codes

| Code | Use Case |
|------|----------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Server Error |

### Service Templates

**applications/api-server** (✅ Reference) - FastAPI REST API patterns
**applications/mcp-server** (✅ Reference) - FastMCP server patterns

---

## Anti-Patterns to Avoid

❌ Business logic in route handlers
❌ Manual request validation (use Pydantic)
❌ Missing error handling
❌ Hardcoded configuration values
❌ Sync operations for I/O tasks
❌ print() instead of logger

---

## Navigation Guide

| Need to... | Read this |
|------------|-----------|
| Understand architecture | [architecture-overview.md](resources/architecture-overview.md) |
| Create routes | [routing-and-path-operations.md](resources/routing-and-path-operations.md) |
| Use Pydantic models | [pydantic-models.md](resources/pydantic-models.md) |
| Add authentication | [authentication-patterns.md](resources/authentication-patterns.md) |
| Handle async/errors | [async-and-errors.md](resources/async-and-errors.md) |
| Create middleware | [middleware-guide.md](resources/middleware-guide.md) |
| Manage config | [configuration.md](resources/configuration.md) |
| Write tests | [testing-guide.md](resources/testing-guide.md) |
| See examples | [complete-examples.md](resources/complete-examples.md) |

---

## Resource Files

### [architecture-overview.md](resources/architecture-overview.md)
Clean architecture, request lifecycle, separation of concerns for Python/FastAPI

### [routing-and-path-operations.md](resources/routing-and-path-operations.md)
FastAPI routing, path operations, dependencies, examples

### [pydantic-models.md](resources/pydantic-models.md)
Request/response models, validation, Field configuration

### [authentication-patterns.md](resources/authentication-patterns.md)
API key auth, OAuth2, JWT, dependency injection for auth

### [async-and-errors.md](resources/async-and-errors.md)
Async/await patterns, error handling, custom exceptions

### [middleware-guide.md](resources/middleware-guide.md)
CORS, authentication, logging middleware

### [dependency-injection.md](resources/dependency-injection.md)
FastAPI Depends system, reusable dependencies

### [configuration.md](resources/configuration.md)
Pydantic BaseSettings, environment variables, config management

### [testing-guide.md](resources/testing-guide.md)
pytest, httpx AsyncClient, testing patterns

### [performance-optimization.md](resources/performance-optimization.md)
Async optimization, caching, performance best practices

### [complete-examples.md](resources/complete-examples.md)
Full endpoint implementations, real-world examples

---

## Related Skills

- **error-tracking** - Sentry integration for Python
- **route-tester** - Testing authenticated API routes
- **skill-developer** - Meta-skill for creating and managing skills

---

**Skill Status**: ADAPTED FOR PYTHON/FASTAPI ✅
**Tech Stack**: Python 3.8+, FastAPI, Pydantic, async/await ✅
**Progressive Disclosure**: 11 resource files ✅
