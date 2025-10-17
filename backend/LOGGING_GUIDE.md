# Logging System Guide

## Overview

Festipin backend uses **Loguru** for structured logging - a simple, powerful, and production-ready logging solution that provides:

- ✨ **Structured JSON logging** for easy parsing and analysis
- 🔍 **Request correlation IDs** for tracing requests across services
- 📊 **Automatic metrics collection** for performance monitoring
- 🔄 **Automatic log rotation** with compression
- ⚡ **Performance tracking** for slow request detection
- 🎨 **Beautiful console output** in development
- 📁 **Separate log files** for errors and metrics

## Features

### 1. Structured Logging
All logs are formatted as JSON in production with rich metadata:
```json
{
  "timestamp": "2025-01-15T10:30:45.123456+00:00",
  "level": "INFO",
  "message": "Image generation completed",
  "module": "service_manager",
  "function": "generate_image",
  "line": 198,
  "request_id": "abc123-def456",
  "extra": {
    "provider": "runware",
    "quality": "premium",
    "duration_ms": 1234.56
  }
}
```

### 2. Request Correlation
Every HTTP request gets a unique `request_id` that's:
- Automatically generated for each request
- Included in all logs during that request
- Added to response headers as `X-Request-ID`
- Used for tracing requests across the entire stack

### 3. Log Files

#### Main Application Log
- **Location:** `logs/festipin_YYYY-MM-DD.log`
- **Contains:** All application logs (INFO and above)
- **Rotation:** Daily at midnight
- **Retention:** 30 days
- **Compression:** ZIP after rotation

#### Error Log
- **Location:** `logs/festipin_errors_YYYY-MM-DD.log`
- **Contains:** Only ERROR and CRITICAL logs
- **Rotation:** When file reaches 100 MB
- **Retention:** 60 days
- **Features:** Full traceback with variable values

#### Metrics Log
- **Location:** `logs/festipin_metrics_YYYY-MM-DD.log`
- **Contains:** Performance metrics and measurements
- **Rotation:** When file reaches 500 MB
- **Retention:** 7 days
- **Format:** JSON with metric_name and metric_value fields

## Usage

### Basic Logging

```python
from app.core.logger import log_info, log_error, log_warning, log_debug

# Simple log message
log_info("User logged in")

# Log with structured data
log_info(
    "Image generated successfully",
    provider="runware",
    quality="premium",
    duration_ms=1234.56,
    user_id="user123"
)

# Error logging
log_error(
    "Failed to generate image",
    error=str(e),
    error_type=type(e).__name__,
    provider="runware",
    request_id=request.request_id
)

# Warning
log_warning(
    "Slow request detected",
    path="/api/generate",
    duration_ms=3000,
    threshold_ms=2000
)

# Debug (only in development)
log_debug(
    "Processing request",
    payload=request_data,
    headers=headers
)
```

### Metrics Logging

```python
from app.core.logger import log_metrics

# Log performance metrics
log_metrics(
    "image_generation_duration",
    processing_time,
    provider="runware",
    quality="premium",
    success=True
)

# Log business metrics
log_metrics(
    "api_requests_total",
    1,
    endpoint="/api/generate",
    method="POST",
    status_code=200
)
```

### Using the Logger Directly

```python
from app.core.logger import logger

# Loguru's powerful API
logger.info("Starting process")
logger.bind(user_id="123").info("User action")  # Add context
logger.success("Operation completed")  # Success level
logger.exception("Error occurred")  # Includes full traceback
```

### Request Context

The middleware automatically handles request correlation:

```python
from app.core.logger import set_request_id, get_request_id

# Get current request ID (set by middleware)
request_id = get_request_id()

# Manually set request ID (rarely needed)
set_request_id("custom-id-123")
```

## Middleware

### LoggingMiddleware
Automatically logs all HTTP requests and responses:
- Incoming request details (method, URL, client IP, user agent)
- Response status and processing time
- Request correlation ID
- Performance metrics

### PerformanceLoggingMiddleware
Detects and logs slow requests:
- Threshold: 2 seconds (configurable)
- Logs warning for requests exceeding threshold
- Includes full request context

### ErrorLoggingMiddleware
Enhanced error logging:
- Captures unhandled exceptions
- Logs full request context
- Includes query params, headers, client IP
- Provides detailed error information

## Configuration

### Environment Variables

```bash
# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Environment (affects log format)
ENVIRONMENT=production  # or development
```

### Log Levels

- **DEBUG:** Detailed diagnostic information (only in development)
- **INFO:** General informational messages
- **SUCCESS:** Successful operations (Loguru-specific)
- **WARNING:** Warning messages for unexpected situations
- **ERROR:** Error messages for failures
- **CRITICAL:** Critical failures requiring immediate attention

## Development vs Production

### Development Mode
- Pretty colored console output
- Human-readable format with emojis
- More verbose logging
- Easier to read during development

```
2025-01-15 10:30:45 | INFO     | service_manager:generate_image:198 | Image generated successfully
```

### Production Mode
- JSON structured output
- Machine-parseable format
- Optimized for log aggregators
- Essential information only

```json
{"timestamp":"2025-01-15T10:30:45.123456+00:00","level":"INFO","message":"Image generated successfully","module":"service_manager","function":"generate_image","line":198,"request_id":"abc123","extra":{"provider":"runware"}}
```

## Best Practices

### 1. Use Structured Logging
✅ **Good:**
```python
log_info(
    "Image generated",
    provider=provider_name,
    duration_ms=duration,
    quality=quality
)
```

❌ **Bad:**
```python
log_info(f"Image generated with {provider_name} in {duration}ms at {quality} quality")
```

### 2. Include Context
Always include relevant context in logs:
```python
log_error(
    "Database query failed",
    error=str(e),
    error_type=type(e).__name__,
    query=query,
    user_id=user_id,
    request_id=request_id
)
```

### 3. Use Appropriate Log Levels
- **DEBUG:** Detailed diagnostic info
- **INFO:** Normal application flow
- **WARNING:** Unexpected but handled situations
- **ERROR:** Errors that should be investigated
- **CRITICAL:** System failures

### 4. Don't Log Sensitive Data
Never log passwords, API keys, tokens, or PII:
```python
# ❌ Bad
log_info("User logged in", password=password, api_key=api_key)

# ✅ Good
log_info("User logged in", user_id=user_id, masked_email="u***@example.com")
```

### 5. Log Metrics for Monitoring
```python
# Track performance
log_metrics("image_generation_duration", duration, provider=provider)

# Track usage
log_metrics("api_calls_total", 1, endpoint=endpoint)

# Track errors
log_metrics("generation_errors_total", 1, provider=provider, error_type=error_type)
```

## Examples from Codebase

### Service Manager Logging
```python
# Initialization
log_info(
    "Service Manager initialized",
    providers=successful_providers,
    provider_count=len(successful_providers)
)

# Circuit breaker
log_warning(
    "Circuit breaker opened",
    provider=provider_name,
    failure_count=breaker['failure_count'],
    threshold=breaker['failure_threshold']
)

# Metrics
log_metrics(
    "image_generation_duration",
    processing_time,
    provider=provider_name,
    quality=request.quality.value,
    success=result.success
)
```

### Request Logging (Automatic)
```python
# Incoming request (logged by middleware)
logger.info(
    "Incoming request",
    method="POST",
    url="http://localhost:9000/api/generate",
    path="/api/generate",
    client_ip="127.0.0.1",
    user_agent="Mozilla/5.0...",
    request_id="abc123-def456"
)

# Request completed (logged by middleware)
logger.info(
    "Request completed",
    method="POST",
    path="/api/generate",
    status_code=200,
    duration_ms=1234.56,
    request_id="abc123-def456"
)
```

## Querying Logs

### View Today's Logs
```bash
cat logs/festipin_$(date +%Y-%m-%d).log
```

### View Errors Only
```bash
cat logs/festipin_errors_$(date +%Y-%m-%d).log
```

### Search for Request ID
```bash
grep "abc123-def456" logs/festipin_*.log
```

### Filter by Level (using jq)
```bash
cat logs/festipin_*.log | jq 'select(.level == "ERROR")'
```

### Track Specific Provider
```bash
cat logs/festipin_*.log | jq 'select(.extra.provider == "runware")'
```

### View Metrics Only
```bash
cat logs/festipin_metrics_$(date +%Y-%m-%d).log
```

### Calculate Average Duration
```bash
cat logs/festipin_metrics_*.log | \
  jq -s '[.[] | select(.metric_name == "image_generation_duration")] |
  add / length'
```

## Integration with External Tools

### Grafana Loki (Optional)
The JSON log format is ready for Loki ingestion via Promtail.

### ELK Stack (Optional)
Logs can be shipped to Elasticsearch using Filebeat.

### CloudWatch (Optional)
AWS CloudWatch agent can collect and index these logs.

### DataDog / New Relic
Both support JSON log ingestion out of the box.

## Troubleshooting

### Logs Not Appearing
1. Check log level: `LOG_LEVEL` in `.env`
2. Verify logs directory exists: `mkdir -p logs`
3. Check file permissions
4. Ensure logger is imported: `from app.core.logger import logger`

### Log Files Growing Too Large
1. Check rotation settings in `app/core/logger.py`
2. Reduce retention period
3. Lower log level in production
4. Enable compression (already enabled)

### Performance Impact
Loguru is highly optimized:
- Async logging with `enqueue=True`
- Minimal overhead (< 1ms per log)
- Automatic batching
- No blocking I/O

## Migration from Old Logging

If updating existing code:

```python
# Old
import logging
logger = logging.getLogger(__name__)
logger.info(f"User {user_id} logged in")

# New
from app.core.logger import log_info
log_info("User logged in", user_id=user_id)
```

## Summary

✅ **Structured JSON logging** for easy analysis
✅ **Automatic request correlation** via middleware
✅ **Separate logs** for errors, metrics, and general app logs
✅ **Automatic rotation** and compression
✅ **Performance tracking** and slow request detection
✅ **Production-ready** with minimal configuration
✅ **Beautiful output** in development mode

The logging system is now active and requires no additional setup! Just use the logging functions throughout your code and logs will be automatically captured, structured, and rotated.
