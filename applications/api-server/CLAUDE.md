# CLAUDE.md - GAM API REST Interface

This file provides guidance to Claude Code (claude.ai/code) when working with the FastAPI REST API implementation in this directory.

## Directory Overview

This directory contains the FastAPI REST API implementation for the Google Ad Manager API integration project. It provides a modern RESTful interface for generating reports and accessing GAM metadata.

## Architecture

### Core Files
- **`main.py`**: FastAPI application entry point
  - Application initialization and configuration
  - CORS middleware setup
  - Global exception handling
  - Router registration
  
- **`auth.py`**: API authentication implementation
  - API key validation
  - Security dependencies
  - Authentication middleware

- **`models.py`**: Pydantic models for request/response validation
  - Request models: `QuickReportRequest`, `CustomReportRequest`
  - Response models: `ReportResponse`, `ErrorResponse`
  - Metadata models: `DimensionMetric`, `CombinationExample`

### Routes Directory
- **`routes/health.py`**: Health check and status endpoints
  - `/health`: Basic health check
  - `/status`: Detailed system status

- **`routes/reports.py`**: Report generation endpoints
  - `/reports/quick`: Pre-configured report types
  - `/reports/custom`: Custom report creation
  - `/reports`: List existing reports

- **`routes/metadata.py`**: GAM metadata endpoints
  - `/metadata/dimensions-metrics`: Available dimensions and metrics
  - `/metadata/combinations`: Common dimension-metric combinations

## API Endpoints

### Report Generation
```
POST /api/v1/reports/quick
- Generate pre-configured reports (delivery, inventory, sales, reach, programmatic)
- Requires: report_type, date_range

POST /api/v1/reports/custom
- Create custom reports with specific dimensions/metrics
- Requires: dimensions[], metrics[], date_range

GET /api/v1/reports
- List all reports with pagination
- Query params: page, page_size
```

### Metadata
```
GET /api/v1/metadata/dimensions-metrics
- Returns all available dimensions and metrics

GET /api/v1/metadata/combinations
- Returns common dimension-metric combination examples
```

### Health & Status
```
GET /api/v1/health
- Basic health check endpoint

GET /api/v1/status
- Detailed status including GAM connection and system info
```

## Authentication

All endpoints (except health checks) require API key authentication:
```
Headers:
  X-API-Key: your-api-key-here
```

API keys are configured in `config/agent_config.yaml`:
```yaml
api:
  enabled: true
  api_keys:
    - key: "your-secure-api-key"
      name: "production"
```

## Running the API

### Development
```bash
# Direct execution
python -m src.api.main

# Or with uvicorn
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
# With gunicorn
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or with uvicorn directly
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Configuration

The API uses the main project configuration from `config/agent_config.yaml`:
```yaml
api:
  enabled: true
  host: "0.0.0.0"
  port: 8000
  cors_origins: ["*"]
  api_keys:
    - key: "secure-key-1"
      name: "production"
    - key: "dev-key-123"
      name: "development"
```

## Error Handling

The API uses consistent error responses:
```json
{
  "error": "Error type",
  "detail": "Detailed error message",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

HTTP Status Codes:
- 200: Success
- 400: Bad Request (invalid parameters)
- 401: Unauthorized (missing/invalid API key)
- 404: Not Found
- 500: Internal Server Error

## Development Guidelines

### Adding New Endpoints
1. Create route function in appropriate module (reports.py, metadata.py, etc.)
2. Define Pydantic models for request/response in models.py
3. Add authentication dependency if needed
4. Include proper error handling
5. Add endpoint documentation with docstrings

### Request Validation
Use Pydantic models for automatic validation:
```python
class MyRequest(BaseModel):
    field1: str
    field2: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "field1": "value",
                "field2": 123
            }
        }
```

### Response Format
Always return consistent response structures:
```python
# Success
return {
    "success": True,
    "data": {...},
    "message": "Operation completed"
}

# Error (handled by exception handlers)
raise HTTPException(
    status_code=400,
    detail="Invalid parameter"
)
```

## Testing

### Manual Testing
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Quick report (with API key)
curl -X POST http://localhost:8000/api/v1/reports/quick \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "delivery",
    "date_range": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31"
    }
  }'
```

### API Documentation
When running, access interactive API docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Common Issues

### CORS Errors
Check `cors_origins` in configuration. Use `["*"]` for development, specific origins for production.

### Authentication Failures
1. Verify API key is included in X-API-Key header
2. Check key exists in configuration
3. Ensure configuration file is loaded correctly

### Connection Errors
1. Verify GAM credentials in googleads.yaml
2. Check network connectivity
3. Ensure OAuth2 token is valid

## Security Considerations

1. **API Keys**: Store securely, never commit to version control
2. **CORS**: Configure specific origins for production
3. **Rate Limiting**: Consider implementing rate limiting for production
4. **HTTPS**: Always use HTTPS in production
5. **Input Validation**: Rely on Pydantic models for validation

## Performance Tips

1. **Async Operations**: Use async/await for I/O operations
2. **Connection Pooling**: GAM client reuses connections
3. **Caching**: Consider caching metadata endpoints
4. **Pagination**: Always paginate list endpoints
5. **Background Tasks**: Use FastAPI background tasks for long operations

## Integration with Other Components

- **Core Modules**: Uses src.core for GAM operations
- **Utils**: Uses src.utils for logging and formatting
- **Configuration**: Shares config with MCP and other interfaces
- **Authentication**: Can share auth tokens with other interfaces