# GAM API Selection Strategies

Guide to understanding how the Unified Client intelligently selects between SOAP and REST APIs.

## Overview

The GAM API integration supports two APIs:
- **REST API v1** (Beta) - Modern, async-first, optimized for reports
- **SOAP API** (Legacy) - Mature, full-featured, stable

The **Unified Client** automatically selects the optimal API based on operation type, performance metrics, and context.

## API Selection Decision Tree

```
┌─────────────────────────────────────┐
│  Operation Requested                │
└──────────┬──────────────────────────┘
           │
           ▼
    ┌──────────────┐
    │ SOAP-only    │──YES──▶ Use SOAP
    │ operation?   │
    └──────┬───────┘
           │ NO
           ▼
    ┌──────────────┐
    │ User API     │──YES──▶ Use Specified API
    │ preference?  │
    └──────┬───────┘
           │ NO
           ▼
    ┌──────────────┐
    │ Performance  │──LOW──▶ Try Fallback
    │ threshold?   │
    └──────┬───────┘
           │ OK
           ▼
    ┌──────────────┐
    │ Circuit      │──OPEN─▶ Use Fallback/Cache
    │ breaker?     │
    └──────┬───────┘
           │ CLOSED
           ▼
    Use REST (Default)
```

## Operation Type Mapping

### REST-Preferred Operations

**Report Operations** (PRIMARY: REST, FALLBACK: SOAP)
```python
CREATE_REPORT       # Better async support, streaming
GET_REPORT          # Faster metadata retrieval
DOWNLOAD_REPORT     # Efficient streaming for large files
LIST_REPORTS        # Pagination support
```

**Metadata Operations** (PRIMARY: REST, FALLBACK: SOAP)
```python
GET_DIMENSIONS      # Cached, fast retrieval
GET_METRICS         # Cached, fast retrieval
GET_NETWORK_INFO    # Quick network details
```

### SOAP-Only Operations

**Inventory Management** (SOAP ONLY)
```python
GET_LINE_ITEMS      # SOAP-exclusive
CREATE_LINE_ITEM    # SOAP-exclusive
UPDATE_LINE_ITEM    # SOAP-exclusive
GET_AD_UNITS        # SOAP-exclusive
```

**Advanced Filtering** (SOAP PREFERRED)
```python
COMPLEX_QUERIES     # StatementBuilder support
BULK_OPERATIONS     # Batch processing
CUSTOM_TARGETING    # Advanced targeting options
```

## Performance-Based Selection

### Success Rate Monitoring

```python
# Track API performance in real-time
{
    'rest': {
        'success_rate': 0.98,  # 98% success
        'avg_response_time': 1.2,  # 1.2 seconds
        'total_requests': 1000
    },
    'soap': {
        'success_rate': 0.95,  # 95% success
        'avg_response_time': 2.3,  # 2.3 seconds
        'total_requests': 500
    }
}
```

### Decision Rules

1. **If success_rate < threshold (default: 0.8)**
   - Switch to alternative API
   - Enable circuit breaker

2. **If avg_response_time > 5 seconds**
   - Consider alternative API
   - Log slow operation warning

3. **If 5 consecutive failures**
   - Open circuit breaker
   - Use fallback API or cached results

## Circuit Breaker Pattern

### States

**CLOSED** (Normal Operation)
```
- All requests go to primary API
- Failures counted
- Success resets failure count
```

**OPEN** (Failing)
```
- Requests bypass primary API
- Use fallback or cached results
- Timeout: 60 seconds before HALF_OPEN
```

**HALF_OPEN** (Testing Recovery)
```
- Limited requests to primary API
- Success → CLOSED
- Failure → OPEN again
```

### Configuration

```yaml
unified:
  circuit_breaker_threshold: 5  # Failures before opening
  circuit_breaker_timeout: 60.0  # Recovery timeout (seconds)
```

## Fallback Strategies

### Automatic Fallback

```python
async def operation_with_fallback():
    """Automatic fallback on failure"""
    try:
        # Try primary API (REST)
        result = await rest_adapter.create_report(params)
        return result
    except Exception as primary_error:
        logger.warning(f"Primary API failed: {primary_error}")

        # Automatic fallback to SOAP
        try:
            result = await soap_adapter.create_report(params)
            logger.info("Fallback to SOAP succeeded")
            return result
        except Exception as fallback_error:
            # Both failed - raise with context
            raise OperationError(
                primary=primary_error,
                fallback=fallback_error
            )
```

### Cached Fallback

```python
async def operation_with_cache():
    """Use cache when both APIs fail"""
    try:
        return await primary_operation()
    except Exception:
        # Try cache before fallback
        cached = get_from_cache(cache_key)
        if cached:
            return {
                **cached,
                'degraded_mode': True,
                'degraded_reason': 'Using cached results - API unavailable'
            }

        # Try fallback API
        return await fallback_operation()
```

## Configuration Examples

### Development (Auto-Selection)

```yaml
unified:
  api_preference: null  # Let system choose
  enable_fallback: true
  enable_performance_tracking: true

  circuit_breaker:
    failure_threshold: 3  # More sensitive for dev
    timeout: 30

  retry:
    max_attempts: 2  # Faster feedback
```

### Production (REST-Preferred)

```yaml
unified:
  api_preference: "rest"  # Prefer REST but allow fallback
  enable_fallback: true
  enable_performance_tracking: true

  circuit_breaker:
    failure_threshold: 5  # More tolerance
    timeout: 60

  retry:
    max_attempts: 3
    backoff_multiplier: 2.0
```

### Testing (Force Specific API)

```python
# Force REST only (no fallback)
config = {
    "unified": {
        "api_preference": "rest",
        "enable_fallback": False
    }
}

# Force SOAP only
config = {
    "unified": {
        "api_preference": "soap",
        "enable_fallback": False
    }
}
```

## Monitoring and Optimization

### Get Performance Metrics

```python
from gam_api.unified import GAMUnifiedClient

async with GAMUnifiedClient() as client:
    # Generate some reports
    await client.create_report(params)

    # Check performance
    stats = client.get_performance_summary()

    print(f"Total operations: {stats['client_metrics']['total_operations']}")
    print(f"REST success rate: {stats['strategy_performance']['rest']['success_rate']:.2%}")
    print(f"SOAP success rate: {stats['strategy_performance']['soap']['success_rate']:.2%}")
```

### Optimization Tips

1. **Monitor success rates**
   - Target: >95% for primary API
   - Alert if <90%

2. **Track response times**
   - Target: <2 seconds average
   - Alert if >5 seconds p95

3. **Adjust thresholds**
   - Increase circuit_breaker_threshold if too sensitive
   - Decrease for faster failover

4. **Cache effectively**
   - Use cache for metadata (dimensions, metrics)
   - TTL: 1 hour for metadata, 30 minutes for reports

## Common Scenarios

### Scenario 1: Rate Limiting

```
Problem: Too many requests to REST API
Solution: Circuit breaker opens → SOAP fallback
Result: Requests continue via SOAP
Recovery: After 60 seconds, try REST again
```

### Scenario 2: REST API Outage

```
Problem: REST API returns 503
Solution: Immediate fallback to SOAP
Result: No user impact
Monitoring: Log warns about degraded mode
```

### Scenario 3: Both APIs Unavailable

```
Problem: Both REST and SOAP fail
Solution: Return cached results if available
Result: Users see cached data with "degraded_mode" flag
Retry: Automatic retry with exponential backoff
```

### Scenario 4: Slow Performance

```
Problem: REST responses >5 seconds
Solution:
  1. Log slow operation warning
  2. Consider SOAP for next request
  3. If pattern continues, prefer SOAP temporarily
Result: Optimized for current conditions
```

## Best Practices

1. **Let the System Choose**
   - Don't override `api_preference` unless testing
   - Trust the performance-based selection

2. **Enable Fallback in Production**
   - Always set `enable_fallback: true`
   - Provides resilience against outages

3. **Monitor Metrics**
   - Check `get_performance_summary()` regularly
   - Set up alerting for low success rates

4. **Handle Degraded Mode**
   - Check for `degraded_mode` in responses
   - Inform users when using cache/fallback

5. **Test Both Paths**
   - Force REST and SOAP in tests
   - Verify fallback works correctly

6. **Configure Appropriately**
   - Dev: Lower thresholds for faster feedback
   - Prod: Higher thresholds for stability
   - Testing: Disable fallback to test specific API

---

**Note**: All examples assume async/await patterns. Synchronous versions available with `_sync` suffix.
