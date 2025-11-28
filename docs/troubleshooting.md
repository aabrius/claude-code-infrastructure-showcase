# Troubleshooting Guide

Common issues and solutions for GAM API integration project.

## 🔐 Authentication Issues

### OAuth Token Expired
**Problem:** Getting "InvalidCredentials" or "AuthenticationError"

**Solution:**
```bash
# Regenerate OAuth token
python generate_new_token.py

# Or use make command
make auth

# Verify token is working
python -c "from src.sdk import GAMClient; GAMClient().get_dimensions_metrics()"
```

### Missing or Invalid Credentials
**Problem:** "Configuration not found" or "Missing credentials"

**Solution:**
```bash
# Check if config file exists
ls -la googleads.yaml

# Copy from example if missing
cp googleads.yaml.example googleads.yaml

# Edit with your credentials
# Required fields: network_code, client_id, client_secret, refresh_token
```

### JWT Authentication Failed (MCP)
**Problem:** MCP client shows "Unauthorized" errors

**Solution:**
```bash
# Get new JWT token from service logs
gcloud logs read --service=gam-mcp-server --limit=20 | grep "Client token"

# Update MCP client configuration with new token
# Location: ~/.claude_desktop_config.json
```

## 🌐 API Connection Issues

### GAM API Connection Failed
**Problem:** "Failed to connect to GAM API" or timeout errors

**Solution:**
```bash
# Test internet connection
ping googleapis.com

# Check if GAM API is accessible
curl -I https://admanager.googleapis.com/v1

# Verify network code in config
grep network_code googleads.yaml
```

### Rate Limiting
**Problem:** "QuotaExceeded" or "RateLimitExceeded" errors

**Solution:**
```python
# Add delays between requests
import time
reports = []
for report_type in ['delivery', 'inventory']:
    report = client.quick_report(report_type).run()
    reports.append(report)
    time.sleep(2)  # Wait 2 seconds between requests
```

### Circuit Breaker Activated
**Problem:** "Circuit breaker is OPEN" errors

**Solution:**
```python
# Wait for circuit breaker to reset (usually 60 seconds)
time.sleep(60)

# Or reset manually
client.reset_circuit_breaker()
```

## 📊 Report Generation Issues

### Empty Report Results
**Problem:** Reports return 0 rows or empty data

**Solution:**
```python
# Check date range - might be too recent
report = client.quick_report('delivery', days_back=30).run()  # Try older data

# Verify ad units have traffic
dimensions = client.get_dimensions_metrics()
print("Available dimensions:", [d['id'] for d in dimensions['dimensions']])

# Check if network has data for the period
report = (client
    .report()
    .dimensions(['DATE'])
    .metrics(['TOTAL_IMPRESSIONS'])
    .date_range(days_back=90)  # Check longer period
    .run())
```

### Invalid Dimension/Metric Combinations
**Problem:** "Invalid dimension metric combination" errors

**Solution:**
```python
# Get valid combinations
combinations = client.get_common_combinations()
print("Valid combinations:", combinations)

# Use pre-validated quick reports
report = client.quick_report('delivery').run()  # These always work

# Test individual dimensions/metrics
try:
    report = client.report().dimensions(['DATE']).metrics(['TOTAL_IMPRESSIONS']).run()
except Exception as e:
    print(f"Error: {e}")
```

### Report Timeout
**Problem:** Reports taking too long or timing out

**Solution:**
```python
# Reduce date range
report = client.quick_report('delivery', days_back=7).run()  # Instead of 30 days

# Use fewer dimensions
report = (client
    .report()
    .dimensions(['DATE'])  # Fewer dimensions = faster
    .metrics(['TOTAL_IMPRESSIONS'])
    .date_range(days_back=14)
    .run())

# Enable caching for repeated queries
client = GAMClient(cache_enabled=True)
```

## 🚀 Cloud Run Deployment Issues

### Service Won't Start
**Problem:** Cloud Run service fails to start

**Solution:**
```bash
# Check build logs
gcloud builds list --limit=5
gcloud builds log [BUILD_ID]

# Check service logs
gcloud logs read --service=gam-mcp-server --limit=20

# Common issues and fixes:
# 1. Missing environment variables
gcloud run services describe gam-mcp-server --region=us-central1

# 2. Port configuration (should be 8080)
# 3. Memory limits (increase if needed)
gcloud run services update gam-mcp-server --memory=2Gi --region=us-central1
```

### Memory/CPU Issues
**Problem:** Service running out of memory or CPU

**Solution:**
```bash
# Increase resources
gcloud run services update gam-mcp-server \
  --memory=2Gi \
  --cpu=2 \
  --region=us-central1

# Enable minimum instances to reduce cold starts
gcloud run services update gam-mcp-server \
  --min-instances=1 \
  --region=us-central1
```

### Environment Variables Not Set
**Problem:** Missing or incorrect environment variables

**Solution:**
```bash
# List current environment variables
gcloud run services describe gam-mcp-server \
  --region=us-central1 \
  --format='value(spec.template.spec.template.spec.containers[0].env[].name,spec.template.spec.template.spec.containers[0].env[].value)'

# Set required variables
gcloud run services update gam-mcp-server \
  --region=us-central1 \
  --set-env-vars \
    MCP_TRANSPORT=http,\
    MCP_AUTH_ENABLED=true,\
    GAM_NETWORK_CODE=your_network_code
```

## 🐍 Python/Dependency Issues

### Import Errors
**Problem:** "ModuleNotFoundError" or import issues

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e ".[all]"

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Verify installation
python -c "from src.sdk import GAMClient; print('OK')"
```

### Package Version Conflicts
**Problem:** Conflicting package versions

**Solution:**
```bash
# Create fresh virtual environment
python -m venv fresh_env
source fresh_env/bin/activate  # On Windows: fresh_env\Scripts\activate

# Install specific versions
pip install -r requirements.txt

# Check for conflicts
pip check
```

### SSL Certificate Issues
**Problem:** SSL verification errors

**Solution:**
```bash
# Update certificates
pip install --upgrade certifi

# Or disable SSL verification temporarily (not recommended for production)
export PYTHONHTTPSVERIFY=0
```

## 📱 MCP Client Issues

### Claude Desktop Not Connecting
**Problem:** MCP server not appearing in Claude Desktop

**Solution:**
1. Check configuration file location:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Verify JSON format:
```json
{
  "mcpServers": {
    "gam-api": {
      "url": "https://gam-mcp-server-183972668403.us-central1.run.app/mcp",
      "transport": "http",
      "headers": {
        "Authorization": "Bearer YOUR_JWT_TOKEN"
      }
    }
  }
}
```

3. Restart Claude Desktop after configuration changes

### MCP Tools Not Working
**Problem:** MCP tools returning errors or not available

**Solution:**
```bash
# Test MCP server directly
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://gam-mcp-server-183972668403.us-central1.run.app/mcp

# Check service health
curl https://gam-mcp-server-183972668403.us-central1.run.app/health

# Get new JWT token
gcloud logs read --service=gam-mcp-server --limit=10 | grep "Client token"
```

## 🔧 Development Environment Issues

### Local API Server Issues
**Problem:** FastAPI server won't start locally

**Solution:**
```bash
# Check if port 8000 is in use
lsof -i :8000

# Use different port
uvicorn src.api.main:app --port 8001

# Or use the make command
make api
```

### Tests Failing
**Problem:** pytest tests fail

**Solution:**
```bash
# Run tests with verbose output
pytest -v

# Run specific test category
pytest -m unit

# Check test dependencies
pip install pytest pytest-cov pytest-mock

# Run with coverage
pytest --cov=src
```

## 📊 Performance Issues

### Slow Report Generation
**Problem:** Reports taking too long to generate

**Solution:**
```python
# Use pagination for large reports
report = (client
    .report()
    .dimensions(['DATE'])
    .metrics(['TOTAL_IMPRESSIONS'])
    .date_range(days_back=7)  # Smaller date range
    .limit(1000)  # Limit rows
    .run())

# Enable caching
client = GAMClient(cache_enabled=True, cache_ttl=3600)

# Use connection pooling
client = GAMClient(pool_connections=10, pool_maxsize=20)
```

### Memory Issues with Large Reports
**Problem:** Out of memory when processing large reports

**Solution:**
```python
# Process in chunks
def process_large_report(report_type, days_back=30, chunk_size=7):
    results = []
    for i in range(0, days_back, chunk_size):
        chunk_start = days_back - i
        chunk_end = max(days_back - i - chunk_size, 0)
        
        report = (client
            .quick_report(report_type)
            .date_range(days_back=chunk_start, end_days_back=chunk_end)
            .run())
        
        results.append(report)
    
    return results

# Use streaming for large datasets
report = client.quick_report('delivery').stream()
for batch in report:
    process_batch(batch)
```

## 🚨 Error Codes Reference

### Common Error Codes

| Error Code | Meaning | Solution |
|------------|---------|----------|
| `INVALID_CREDENTIALS` | OAuth token expired/invalid | Run `python generate_new_token.py` |
| `QUOTA_EXCEEDED` | API quota reached | Wait for quota reset or reduce requests |
| `INVALID_REPORT_TYPE` | Unknown report type | Use: delivery, inventory, sales, reach, programmatic |
| `INVALID_DATE_RANGE` | Invalid date range | Check date format (YYYY-MM-DD) |
| `NETWORK_NOT_FOUND` | Invalid network code | Verify network_code in googleads.yaml |
| `INSUFFICIENT_PERMISSIONS` | GAM API access denied | Check GAM account permissions |

### Debug Mode
Enable debug logging for detailed error information:

```bash
# Environment variable
export LOG_LEVEL=DEBUG

# Or in code
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🆘 Getting Help

### Diagnostic Commands
```bash
# System info
python --version
pip list | grep -E "(google|oauth|requests)"

# Service status
curl https://gam-mcp-server-183972668403.us-central1.run.app/health

# Test SDK
python -c "
from src.sdk import GAMClient
client = GAMClient()
print('Client initialized successfully')
try:
    dims = client.get_dimensions_metrics()
    print(f'Available dimensions: {len(dims.get(\"dimensions\", []))}')
except Exception as e:
    print(f'Error: {e}')
"
```

### Log Analysis
```bash
# Check recent logs
gcloud logs read --service=gam-mcp-server \
  --format="table(timestamp,severity,textPayload)" \
  --limit=50

# Filter for errors
gcloud logs read --service=gam-mcp-server \
  --filter="severity>=ERROR" \
  --limit=20
```

### Health Checks
```bash
# MCP server health
curl https://gam-mcp-server-183972668403.us-central1.run.app/health

# Detailed status
curl https://gam-mcp-server-183972668403.us-central1.run.app/status

# Test with authentication
curl -H "Authorization: Bearer $JWT_TOKEN" \
  https://gam-mcp-server-183972668403.us-central1.run.app/mcp
```

## 📞 Support Resources

1. **Google Ad Manager API Documentation**: https://developers.google.com/ad-manager/api/beta
2. **Google Cloud Run Documentation**: https://cloud.google.com/run/docs
3. **FastMCP Documentation**: Check MCP protocol specification
4. **Project Issues**: Report bugs and issues in the project repository

### Before Reporting Issues

Please include:
- Error messages and stack traces
- Configuration (sanitized, no secrets)
- Steps to reproduce
- Environment details (Python version, OS)
- Logs from `gcloud logs read --service=gam-mcp-server --limit=20`