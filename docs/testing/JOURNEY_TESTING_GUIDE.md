# GAM API Journey Testing Guide

This document maps all possible user journeys through the GAM API system to ensure comprehensive testing coverage before UI development.

## 🗺️ Journey Categories

### 1. 🔐 Authentication Journeys

#### 1.1 First-Time Setup Journey
```
User → Install Package → Generate OAuth Token → Configure googleads.yaml → Verify Connection
```
**Test Points:**
- [ ] Missing credentials error handling
- [ ] Invalid client_id/secret handling
- [ ] Network code validation
- [ ] Token generation success
- [ ] Config file creation

#### 1.2 Token Refresh Journey
```
User → Make API Call → Token Expired → Auto Refresh → Continue Operation
```
**Test Points:**
- [ ] Automatic token refresh
- [ ] Refresh token expiry handling
- [ ] Concurrent refresh attempts
- [ ] Refresh failure recovery

#### 1.3 Multi-Network Journey
```
User → Configure Network A → Switch to Network B → Maintain Separate Sessions
```
**Test Points:**
- [ ] Multiple config files
- [ ] Network switching
- [ ] Session isolation
- [ ] Credential management

### 2. 📊 Report Generation Journeys

#### 2.1 Quick Report Journey
```
User → Select Report Type → Provide Date Range → Generate → Download Results
```
**Report Types to Test:**
- [ ] Delivery Report (impressions, clicks, CTR, revenue)
- [ ] Inventory Report (ad requests, fill rate)
- [ ] Sales Report (revenue by advertiser/order)
- [ ] Reach Report (unique reach, frequency)
- [ ] Programmatic Report (channel performance)

**Test Variations:**
- [ ] Single day
- [ ] Date range (7 days, 30 days, 90 days, 365 days)
- [ ] Historical data (>1 year old)
- [ ] Future dates (error case)
- [ ] Invalid date formats

#### 2.2 Custom Report Journey
```
User → Select Dimensions → Select Metrics → Add Filters → Set Date Range → Generate → Poll Status → Download
```
**Test Cases:**
- [ ] Valid dimension-metric combinations
- [ ] Incompatible combinations (should fail)
- [ ] 1-10 dimensions
- [ ] 1-20 metrics
- [ ] Complex filters
- [ ] Large result sets
- [ ] Empty result sets

#### 2.3 Report Export Journey
```
User → Generate Report → Select Format → Export → Verify Output
```
**Formats to Test:**
- [ ] JSON (default)
- [ ] CSV
- [ ] Excel (XLSX)
- [ ] XML (if supported)

### 3. 🌐 REST API Journeys

#### 3.1 API Discovery Journey
```
Developer → Access /docs → Explore Endpoints → Test with API Key → Integrate
```
**Test Points:**
- [ ] OpenAPI documentation accuracy
- [ ] Interactive docs functionality
- [ ] Example requests/responses
- [ ] API versioning

#### 3.2 CRUD Operations Journey
```
Developer → POST /reports → GET /reports/{id} → GET /reports → DELETE /reports/{id}
```
**Test Cases:**
- [ ] Create report with all parameters
- [ ] Create with minimal parameters
- [ ] Read single report
- [ ] List reports with pagination
- [ ] Filter reports
- [ ] Update report (if supported)
- [ ] Delete report
- [ ] Non-existent report handling

#### 3.3 Bulk Operations Journey
```
Developer → Create Multiple Reports → Batch Status Check → Bulk Download
```
**Test Points:**
- [ ] Concurrent report creation
- [ ] Rate limiting behavior
- [ ] Batch status endpoints
- [ ] Partial failure handling

### 4. 🤖 MCP Server Journeys

#### 4.1 Tool Discovery Journey
```
AI Assistant → Connect to MCP → List Available Tools → Understand Capabilities
```
**Tools to Verify:**
- [ ] gam_quick_report
- [ ] gam_create_report
- [ ] gam_list_reports
- [ ] gam_get_dimensions_metrics
- [ ] gam_get_common_combinations
- [ ] gam_get_quick_report_types

#### 4.2 Report Creation via MCP Journey
```
AI Assistant → Call gam_quick_report → Receive Results → Format for User
```
**Test Scenarios:**
- [ ] Valid tool calls
- [ ] Missing parameters
- [ ] Invalid parameters
- [ ] Error responses
- [ ] Timeout handling
- [ ] Large response handling

#### 4.3 JWT Authentication Journey
```
Client → Request Token → Authenticate → Make Authenticated Calls → Token Expiry → Re-authenticate
```
**Test Points:**
- [ ] Token generation
- [ ] Token validation
- [ ] Invalid token rejection
- [ ] Token expiry
- [ ] Concurrent authentication

### 5. 🐍 Python SDK Journeys

#### 5.1 Basic SDK Usage Journey
```
Developer → pip install → from gam_api import GAMClient → client.delivery_report() → Process Results
```
**Test Cases:**
- [ ] Package installation
- [ ] Import verification
- [ ] Client initialization
- [ ] Method availability
- [ ] Type hints/autocomplete

#### 5.2 Advanced SDK Journey
```
Developer → ReportBuilder → Chain Methods → Add Filters → Execute → Handle Async
```
**Test Patterns:**
```python
# Test these patterns
report = (ReportBuilder()
    .add_dimension("DATE")
    .add_dimension("AD_UNIT_NAME")
    .add_metric("IMPRESSIONS")
    .add_metric("CLICKS")
    .set_date_range(DateRange.last_week())
    .add_filter("AD_UNIT_NAME", "contains", "Mobile")
    .build())
```

#### 5.3 Error Handling Journey
```
Developer → Make Call → Catch Specific Exception → Implement Retry → Log Error
```
**Exception Types:**
- [ ] AuthenticationError
- [ ] ValidationError
- [ ] ReportGenerationError
- [ ] RateLimitError
- [ ] NetworkError

### 6. 🔧 Integration Journeys

#### 6.1 CI/CD Integration Journey
```
DevOps → Install in Pipeline → Run Automated Reports → Store Results → Notify on Failure
```
**Test Points:**
- [ ] Headless operation
- [ ] Environment variable config
- [ ] Exit codes
- [ ] Output parsing
- [ ] Error reporting

#### 6.2 Data Pipeline Journey
```
Data Engineer → Schedule Reports → Stream to BigQuery → Transform → Visualize
```
**Integration Points:**
- [ ] Scheduling (cron, Airflow)
- [ ] Streaming large datasets
- [ ] Incremental updates
- [ ] Schema evolution
- [ ] Failure recovery

#### 6.3 Monitoring Journey
```
SRE → Deploy → Monitor Health → Alert on Errors → View Metrics → Debug Issues
```
**Observability:**
- [ ] Health endpoints
- [ ] Prometheus metrics
- [ ] Structured logging
- [ ] Distributed tracing
- [ ] Error aggregation

### 7. 🚨 Error Handling Journeys

#### 7.1 Network Failure Journey
```
User → Request → Network Timeout → Retry Logic → Exponential Backoff → Success/Failure
```
**Failure Modes:**
- [ ] Connection timeout
- [ ] Read timeout
- [ ] DNS failure
- [ ] SSL errors
- [ ] Proxy issues

#### 7.2 API Limit Journey
```
User → Exceed Quota → Receive 429 Error → Check Headers → Wait → Retry
```
**Quota Types:**
- [ ] Requests per second
- [ ] Daily quota
- [ ] Concurrent requests
- [ ] Result size limits

#### 7.3 Data Validation Journey
```
User → Invalid Input → Clear Error Message → Correct Input → Success
```
**Validation Scenarios:**
- [ ] Invalid dimensions
- [ ] Invalid metrics
- [ ] Incompatible combinations
- [ ] Invalid date ranges
- [ ] Malformed filters

### 8. 🚀 Performance Journeys

#### 8.1 High Volume Journey
```
User → Request Large Report → Progress Updates → Chunked Download → Complete
```
**Performance Tests:**
- [ ] 1GB+ report generation
- [ ] 1M+ rows
- [ ] 100+ concurrent users
- [ ] Memory usage under load
- [ ] CPU usage patterns

#### 8.2 Caching Journey
```
User → First Request (Slow) → Subsequent Request (Fast) → Cache Invalidation → Fresh Data
```
**Cache Scenarios:**
- [ ] Cache hit rate
- [ ] Cache size limits
- [ ] TTL expiration
- [ ] Manual invalidation
- [ ] Cross-user isolation

## 📋 Testing Framework Structure

### Journey Test Structure
```
tests/
├── journeys/
│   ├── __init__.py
│   ├── test_authentication_journeys.py
│   ├── test_report_generation_journeys.py
│   ├── test_api_journeys.py
│   ├── test_mcp_journeys.py
│   ├── test_sdk_journeys.py
│   ├── test_error_journeys.py
│   └── test_performance_journeys.py
├── fixtures/
│   ├── journey_data.py
│   └── journey_helpers.py
└── reports/
    └── journey_coverage.html
```

### Journey Test Template
```python
import pytest
from gam_api import GAMClient, DateRange
from tests.fixtures.journey_helpers import JourneyRecorder

class TestDeliveryReportJourney:
    """Test the complete journey of generating a delivery report."""
    
    @pytest.fixture
    def journey_recorder(self):
        return JourneyRecorder("delivery_report_journey")
    
    def test_happy_path_journey(self, journey_recorder):
        """Test successful delivery report generation journey."""
        # Step 1: Initialize client
        journey_recorder.record_step("initialize_client")
        client = GAMClient()
        
        # Step 2: Create report request
        journey_recorder.record_step("create_request")
        date_range = DateRange.last_week()
        
        # Step 3: Generate report
        journey_recorder.record_step("generate_report")
        report = client.delivery_report(date_range)
        
        # Step 4: Validate results
        journey_recorder.record_step("validate_results")
        assert report is not None
        assert 'data' in report
        assert len(report['data']) > 0
        
        # Step 5: Export results
        journey_recorder.record_step("export_results")
        # Test various export formats
        
        journey_recorder.complete()
    
    def test_error_recovery_journey(self, journey_recorder):
        """Test error handling and recovery in report generation."""
        # Test various failure scenarios
        pass
```

## 🎯 Journey Testing Priorities

### Phase 1: Core Journeys (Must Have)
1. Basic authentication setup
2. All 5 quick report types
3. Custom report creation
4. REST API CRUD operations
5. Basic error handling

### Phase 2: Integration Journeys (Should Have)
1. MCP server tools
2. SDK fluent API
3. Batch operations
4. Caching behavior
5. Performance under load

### Phase 3: Advanced Journeys (Nice to Have)
1. Multi-network switching
2. Complex filtering
3. Data pipeline integration
4. Monitoring integration
5. Advanced error recovery

## 📊 Success Metrics

- **Coverage**: 100% of documented journeys tested
- **Reliability**: <0.1% failure rate in happy path journeys
- **Performance**: 95th percentile < 5s for report generation
- **Error Handling**: 100% of errors return actionable messages
- **Documentation**: Every journey has example code

## 🚀 Next Steps

1. Create journey test framework
2. Implement journey recording/playback
3. Build automated journey test suite
4. Create journey documentation
5. Set up journey monitoring
6. Generate journey coverage reports