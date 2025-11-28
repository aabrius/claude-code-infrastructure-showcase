# Routing and Path Operations - FastAPI Best Practices

Complete guide to clean route definitions and path operation patterns in FastAPI.

## Table of Contents

- [Routes: Routing Only](#routes-routing-only)
- [Path Operations Best Practices](#path-operations-best-practices)
- [Good Examples](#good-examples)
- [Anti-Patterns](#anti-patterns)
- [Refactoring Guide](#refactoring-guide)
- [Error Handling](#error-handling)
- [HTTP Status Codes](#http-status-codes)

---

## Routes: Routing Only

### The Golden Rule

**Routes should ONLY:**
- ✅ Define path operations (@router.get, @router.post, etc.)
- ✅ Declare dependencies (auth, config)
- ✅ Call business logic functions
- ✅ Return response models

**Routes should NEVER:**
- ❌ Contain business logic
- ❌ Access databases/APIs directly
- ❌ Implement validation logic (use Pydantic)
- ❌ Format complex responses (use Pydantic models)
- ❌ Handle complex error scenarios (use exception handlers)

### Clean Route Pattern

```python
# routes/reports.py
from fastapi import APIRouter, HTTPException, Depends
from models import QuickReportRequest, QuickReportResponse
from auth import get_api_key
from gam_shared.logger import get_structured_logger

router = APIRouter()
logger = get_structured_logger('api_reports')

# ✅ CLEAN: Path operation definition only
@router.post("/quick", response_model=QuickReportResponse)
async def generate_quick_report(
    request: QuickReportRequest,
    api_key: str = Depends(get_api_key)
):
    """Generate a quick report with predefined configurations."""
    try:
        # Delegate to business logic
        result = await generate_report(request.report_type, request.days_back)
        return QuickReportResponse(
            report_type=request.report_type,
            total_rows=len(result),
            data=result
        )
    except ValidationError as e:
        logger.logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.logger.error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail="Report generation failed")

@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    api_key: str = Depends(get_api_key)
):
    """Retrieve a specific report by ID."""
    report = await fetch_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
```

**Key Points:**
- Each route: decorator, function, dependencies, response model
- No complex try-catch needed (global handlers catch unhandled errors)
- Clean, readable, maintainable
- Easy to see all endpoints at a glance

---

## Path Operations Best Practices

### 1. Use Response Models

Always specify `response_model` for type safety and automatic documentation:

```python
from pydantic import BaseModel

class ReportResponse(BaseModel):
    id: str
    total_rows: int
    data: List[dict]

# ✅ With response model
@router.get("/report/{id}", response_model=ReportResponse)
async def get_report(id: str):
    return await fetch_report(id)

# ❌ Without response model (less type safety)
@router.get("/report/{id}")
async def get_report(id: str):
    return await fetch_report(id)
```

### 2. Use Dependencies for Common Logic

```python
from fastapi import Depends
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def get_api_key(api_key: str = Depends(api_key_header)) -> str:
    """Validate API key."""
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

# Use the dependency
@router.get("/protected")
async def protected_endpoint(api_key: str = Depends(get_api_key)):
    return {"message": "Access granted"}
```

### 3. Path Parameters vs Query Parameters

```python
# Path parameter - required
@router.get("/reports/{report_id}")
async def get_report(report_id: str):
    ...

# Query parameter - optional with default
from typing import Optional

@router.get("/reports")
async def list_reports(
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = None
):
    ...
```

### 4. Request Body with Pydantic

```python
from pydantic import BaseModel, Field

class CreateReportRequest(BaseModel):
    report_type: str = Field(..., description="Type of report")
    days_back: int = Field(7, ge=1, le=365)

    class Config:
        json_schema_extra = {
            "example": {
                "report_type": "delivery",
                "days_back": 7
            }
        }

@router.post("/reports")
async def create_report(request: CreateReportRequest):
    # Request automatically validated
    return await generate_report(request)
```

---

## Good Examples

### Example 1: Simple GET Endpoint

```python
# routes/health.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    version: str

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint."""
    return HealthResponse(status="healthy", version="1.0.0")
```

### Example 2: POST with Authentication

```python
# routes/reports.py
from fastapi import APIRouter, Depends, HTTPException
from models import CustomReportRequest, CustomReportResponse
from auth import get_api_key

router = APIRouter()

@router.post("/custom", response_model=CustomReportResponse)
async def create_custom_report(
    request: CustomReportRequest,
    api_key: str = Depends(get_api_key)
):
    """Create a custom report with specified dimensions and metrics."""
    try:
        # Validate combinations
        if not validate_dimensions_metrics(request.dimensions, request.metrics):
            raise HTTPException(
                status_code=400,
                detail="Invalid dimension-metric combination"
            )

        # Generate report
        result = await generate_custom_report(
            dimensions=request.dimensions,
            metrics=request.metrics,
            date_range=request.date_range
        )

        return CustomReportResponse(
            report_id=result.id,
            total_rows=result.total_rows,
            data=result.data
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Example 3: GET with Pagination

```python
from typing import List
from fastapi import Query

class ReportListItem(BaseModel):
    id: str
    name: str
    created_at: str

class ReportListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    reports: List[ReportListItem]

@router.get("/reports", response_model=ReportListResponse)
async def list_reports(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    api_key: str = Depends(get_api_key)
):
    """List all reports with pagination."""
    reports, total = await fetch_reports_paginated(page, page_size)
    return ReportListResponse(
        total=total,
        page=page,
        page_size=page_size,
        reports=reports
    )
```

---

## Anti-Patterns

### ❌ Business Logic in Routes

```python
# BAD: Too much logic in route
@router.post("/report")
async def create_report(request: ReportRequest):
    # Don't do this
    client = GAMClient()
    await client.authenticate()

    # Validate dimensions
    if not request.dimensions:
        raise HTTPException(400, "Missing dimensions")

    # Build query
    query = build_query(request.dimensions, request.metrics)

    # Execute
    data = await client.execute_query(query)

    # Process results
    processed = []
    for row in data:
        processed.append({
            'date': row[0],
            'impressions': int(row[1]),
            'clicks': int(row[2])
        })

    # Format output
    return {
        'success': True,
        'total': len(processed),
        'data': processed
    }
```

### ✅ Delegate to Business Logic

```python
# GOOD: Route delegates to service
@router.post("/report", response_model=ReportResponse)
async def create_report(request: ReportRequest):
    result = await report_service.generate_report(request)
    return result
```

### ❌ Manual Validation

```python
# BAD: Manual validation
@router.post("/report")
async def create_report(data: dict):
    if "report_type" not in data:
        raise HTTPException(400, "Missing report_type")
    if not isinstance(data["days_back"], int):
        raise HTTPException(400, "days_back must be integer")
    if data["days_back"] < 1 or data["days_back"] > 365:
        raise HTTPException(400, "days_back must be 1-365")
    ...
```

### ✅ Pydantic Validation

```python
# GOOD: Pydantic handles validation
class ReportRequest(BaseModel):
    report_type: str
    days_back: int = Field(ge=1, le=365)

@router.post("/report")
async def create_report(request: ReportRequest):  # Validated automatically
    ...
```

### ❌ Inconsistent Error Handling

```python
# BAD: Inconsistent error responses
@router.get("/report/{id}")
async def get_report(id: str):
    try:
        report = await fetch_report(id)
    except NotFoundError:
        return {"error": "Not found"}  # Wrong format
    except Exception as e:
        return {"message": str(e)}  # Different format
```

### ✅ Consistent Error Handling

```python
# GOOD: Use HTTPException consistently
@router.get("/report/{id}", response_model=ReportResponse)
async def get_report(id: str):
    report = await fetch_report(id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
```

---

## Refactoring Guide

### Before: Legacy Pattern

```python
@router.post("/submit")
async def submit_report(data: dict):
    try:
        # Validation
        if not data.get("type"):
            return {"error": "Missing type"}, 400

        # Business logic
        client = GAMClient()
        result = await client.generate_report(data["type"])

        # Processing
        formatted = format_result(result)

        return {"success": True, "data": formatted}
    except Exception as e:
        return {"error": str(e)}, 500
```

### After: FastAPI Best Practices

```python
# models.py
class SubmitReportRequest(BaseModel):
    type: str = Field(..., description="Report type")

class SubmitReportResponse(BaseModel):
    success: bool
    data: List[dict]

# routes/reports.py
@router.post("/submit", response_model=SubmitReportResponse)
async def submit_report(
    request: SubmitReportRequest,
    api_key: str = Depends(get_api_key)
):
    """Submit a report for generation."""
    result = await report_service.generate_report(request.type)
    return SubmitReportResponse(success=True, data=result)
```

---

## Error Handling

### Global Exception Handlers

Define in main.py:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from gam_api.exceptions import ValidationError, GAMError

app = FastAPI()

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "validation_error",
            "message": str(exc),
            "details": exc.details if hasattr(exc, 'details') else None
        }
    )

@app.exception_handler(GAMError)
async def gam_exception_handler(request: Request, exc: GAMError):
    return JSONResponse(
        status_code=500,
        content={
            "error": "gam_error",
            "message": str(exc)
        }
    )
```

### Route-Level Error Handling

```python
@router.post("/report")
async def create_report(request: ReportRequest):
    try:
        result = await generate_report(request)
        return result
    except ValidationError as e:
        # Specific validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except AuthenticationError as e:
        # Auth errors
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
```

---

## HTTP Status Codes

Use consistent status codes:

| Code | Use Case | Example |
|------|----------|---------|
| 200 | Success (GET, PUT) | `return data` |
| 201 | Created (POST) | `return new_resource, 201` |
| 204 | No Content (DELETE) | `return Response(status_code=204)` |
| 400 | Bad Request | `raise HTTPException(400, "Invalid input")` |
| 401 | Unauthorized | `raise HTTPException(401, "Invalid API key")` |
| 403 | Forbidden | `raise HTTPException(403, "Access denied")` |
| 404 | Not Found | `raise HTTPException(404, "Resource not found")` |
| 500 | Server Error | `raise HTTPException(500, "Internal error")` |

---

## Real Project Example

From `applications/api-server/routes/reports.py`:

```python
from fastapi import APIRouter, HTTPException, Depends
from models import QuickReportRequest, QuickReportResponse
from auth import get_api_key
from gam_api import GAMClient
from gam_shared.logger import get_structured_logger

router = APIRouter()
logger = get_structured_logger('api_reports')

@router.post("/quick", response_model=QuickReportResponse)
async def generate_quick_report(
    request: QuickReportRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Generate a quick report with predefined configurations.

    Quick reports include:
    - delivery: Impressions, clicks, CTR metrics
    - inventory: Ad unit performance analysis
    - sales: Revenue and monetization metrics
    """
    try:
        logger.log_function_call("generate_quick_report", kwargs=request.dict())

        # Generate report (delegated to business logic)
        generator = ReportGenerator()
        result = generator.generate_quick_report(
            report_type=request.report_type.value,
            days_back=request.days_back
        )

        # Format output
        formatter = get_formatter(request.format.value)
        formatted_data = formatter.format(result)

        response = QuickReportResponse(
            report_type=request.report_type.value,
            days_back=request.days_back,
            total_rows=result.total_rows,
            data=formatted_data
        )

        logger.logger.info(f"Quick report generated: {request.report_type.value}")
        return response

    except ValidationError as e:
        logger.logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except GAMError as e:
        logger.logger.error(f"GAM error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Best Practices Summary

1. ✅ Keep routes thin - delegate to business logic
2. ✅ Always use Pydantic models for request/response
3. ✅ Use `response_model` parameter
4. ✅ Use Depends() for authentication and common logic
5. ✅ Raise HTTPException for errors
6. ✅ Log errors before raising
7. ✅ Use type hints everywhere
8. ✅ Add docstrings for OpenAPI documentation
9. ✅ Use consistent error response formats
10. ✅ Test routes with httpx AsyncClient

---

**Related Resources:**
- [pydantic-models.md](pydantic-models.md) - Request/response validation
- [async-and-errors.md](async-and-errors.md) - Error handling patterns
- [authentication-patterns.md](authentication-patterns.md) - Auth dependencies
