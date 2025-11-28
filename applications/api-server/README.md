# GAM API Server

REST API for Google Ad Manager integration.

## 🎯 Overview

FastAPI-based REST API server providing 17 endpoints for Google Ad Manager operations:

### Report Endpoints
- `POST /api/v1/reports/quick` - Generate pre-configured reports
- `POST /api/v1/reports/custom` - Create custom reports
- `GET /api/v1/reports` - List existing reports
- `GET /api/v1/reports/{report_id}` - Get specific report
- `DELETE /api/v1/reports/{report_id}` - Delete report

### Metadata Endpoints
- `GET /api/v1/metadata/dimensions-metrics` - Available dimensions and metrics
- `GET /api/v1/metadata/combinations` - Common dimension-metric combinations
- `GET /api/v1/metadata/quick-report-types` - Available quick report types

### Health & Status Endpoints
- `GET /health` - Basic health check
- `GET /api/v1/status` - Detailed system status
- `GET /api/v1/version` - API version info

## 🚀 Running the Server

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GAM_CONFIG_PATH="path/to/config.yaml"
export API_KEY="your-api-key"

# Run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Base URL**: http://localhost:8000

### Docker

```bash
# Build image
docker build -t gam-api-server .

# Run container
docker run -p 8000:8000 \
    -e GAM_CONFIG_PATH=/config/config.yaml \
    -e API_KEY=your-api-key \
    -v $(pwd)/config:/config \
    gam-api-server
```

### Docker Compose

```yaml
version: '3.8'
services:
  api-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GAM_CONFIG_PATH=/config/config.yaml
      - API_KEY=your-api-key
    volumes:
      - ./config:/config
```

## 🔧 Configuration

The server uses the `gam_api` package for GAM integration:

```python
from gam_api import GAMClient, DateRange, ReportBuilder

# Server automatically initializes client
client = GAMClient()  # Loads config from GAM_CONFIG_PATH
```

### Environment Variables

- `GAM_CONFIG_PATH`: Path to GAM configuration file
- `API_KEY`: API key for authentication (X-API-Key header)
- `PORT`: Server port (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)

## 📊 API Documentation

### Authentication

All endpoints require API key authentication:

```bash
curl -H "X-API-Key: your-api-key" \
     http://localhost:8000/api/v1/reports
```

### Quick Reports

Generate pre-configured reports:

```bash
curl -X POST http://localhost:8000/api/v1/reports/quick \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "report_type": "delivery",
    "date_range": {"days_back": 7},
    "output_format": "json"
  }'
```

**Response**:
```json
{
  "success": true,
  "report_id": "rpt_123456",
  "report_type": "delivery",
  "status": "completed",
  "data": [...],
  "total_rows": 1000,
  "generated_at": "2024-01-15T10:30:00Z"
}
```

### Custom Reports

Create reports with specific dimensions and metrics:

```bash
curl -X POST http://localhost:8000/api/v1/reports/custom \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "name": "Mobile Performance Analysis",
    "dimensions": ["DATE", "AD_UNIT_NAME", "DEVICE_CATEGORY_NAME"],
    "metrics": ["IMPRESSIONS", "CLICKS", "CTR"],
    "date_range": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31"
    },
    "filters": [
      {
        "field": "DEVICE_CATEGORY_NAME",
        "operator": "EQUALS",
        "value": "Mobile"
      }
    ]
  }'
```

### List Reports

Get existing reports:

```bash
curl -H "X-API-Key: your-api-key" \
     "http://localhost:8000/api/v1/reports?limit=10&type=delivery"
```

### Get Metadata

Retrieve available dimensions and metrics:

```bash
curl -H "X-API-Key: your-api-key" \
     http://localhost:8000/api/v1/metadata/dimensions-metrics
```

**Response**:
```json
{
  "success": true,
  "dimensions": [
    "DATE", "AD_UNIT_NAME", "COUNTRY_NAME", "DEVICE_CATEGORY_NAME"
  ],
  "metrics": [
    "IMPRESSIONS", "CLICKS", "CTR", "REVENUE"
  ]
}
```

## 🏗️ Architecture

```
API Server
├── main.py              # FastAPI application
├── auth.py              # API key authentication
├── models.py            # Pydantic models
├── routes/              # API endpoints
│   ├── health.py        # Health check endpoints
│   ├── metadata.py      # Metadata endpoints
│   └── reports.py       # Report endpoints
├── Dockerfile           # Container image
└── requirements.txt     # Dependencies
```

### Integration with gam_api

The server uses the clean `gam_api` package:

```python
from gam_api import GAMClient, DateRange, ReportBuilder

class ReportService:
    def __init__(self):
        self.client = GAMClient()
    
    async def create_quick_report(self, report_type: str, date_range: dict):
        # Convert to DateRange object
        if "days_back" in date_range:
            dr = DateRange.last_n_days(date_range["days_back"])
        else:
            dr = DateRange(date_range["start_date"], date_range["end_date"])
        
        # Use the clean API
        if report_type == "delivery":
            return self.client.delivery_report(dr)
        elif report_type == "inventory":
            return self.client.inventory_report(dr)
        # ... etc
```

## 🔐 Security

### API Key Authentication

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != expected_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key
```

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 Monitoring

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/api/v1/status
```

### Logging

The server includes structured logging:

```python
import logging
from gam_api import APIError

logger = logging.getLogger(__name__)

@app.post("/api/v1/reports/quick")
async def create_quick_report(request: QuickReportRequest):
    try:
        logger.info(f"Creating quick report: {request.report_type}")
        result = await report_service.create_quick_report(request)
        logger.info(f"Report created successfully: {result.get('report_id')}")
        return result
    except Exception as e:
        logger.error(f"Report creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

## 🚀 Deployment

### Production Configuration

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  api-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GAM_CONFIG_PATH=/config/config.yaml
      - API_KEY=${API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./config:/config:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Cloud Deployment

```bash
# Build and push to registry
docker build -t gcr.io/project-id/gam-api-server .
docker push gcr.io/project-id/gam-api-server

# Deploy to Cloud Run
gcloud run deploy gam-api-server \
  --image gcr.io/project-id/gam-api-server \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GAM_CONFIG_PATH=/config/config.yaml
```

## 🧪 Testing

### Unit Tests

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_quick_report():
    response = client.post(
        "/api/v1/reports/quick",
        json={
            "report_type": "delivery",
            "date_range": {"days_back": 7}
        },
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
```

### Integration Tests

```bash
# Test with real API
export GAM_CONFIG_PATH="config/test_config.yaml"
export API_KEY="test-api-key"
python -m pytest tests/integration/
```

## 🆘 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Check API key in X-API-Key header
   - Verify GAM configuration file exists and is valid

2. **GAM API Errors**
   - Check OAuth token validity in config
   - Verify network code is correct
   - Check GAM API rate limits

3. **Connection Issues**
   - Test health endpoint: `curl http://localhost:8000/health`
   - Check server logs for startup errors
   - Verify port 8000 is available

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uvicorn main:app --reload --log-level debug
```

### Logs

```bash
# View application logs
docker logs gam-api-server

# Follow logs in real-time
docker logs -f gam-api-server
```

## 📚 Related Documentation

- [GAM API Package Documentation](../../docs/NEW_PACKAGE_GUIDE.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Ad Manager API Documentation](https://developers.google.com/ad-manager)