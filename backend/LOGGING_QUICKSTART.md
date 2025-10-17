# Loguru Logging - Quick Reference

## Import

```python
from app.core.logger import (
    log_info, log_error, log_warning, log_debug,
    log_success, log_critical, log_metrics, logger
)
```

## Basic Usage

```python
# Simple message
log_info("User logged in")

# With context
log_info("Image generated", provider="runware", duration_ms=1234.56, user_id="user123")

# Error
log_error("Operation failed", error=str(e), error_type=type(e).__name__)

# Warning
log_warning("Rate limit approaching", count=95, limit=100)

# Success
log_success("Database migration completed")

# Debug (only in development)
log_debug("Processing data", payload=data)
```

## Metrics

```python
# Performance metric
log_metrics("api_request_duration", duration, endpoint="/api/generate", status=200)

# Business metric
log_metrics("images_generated", 1, provider="runware", quality="premium")
```

## Advanced

```python
# With context binding
user_logger = logger.bind(user_id="123", session_id="abc")
user_logger.info("Action performed")

# Exception with traceback
try:
    risky_operation()
except Exception as e:
    logger.exception("Operation failed")  # Includes full traceback
```

## Log Files

| File | Content | Rotation | Retention |
|------|---------|----------|-----------|
| `festipin_YYYY-MM-DD.log` | All logs (INFO+) | Daily | 30 days |
| `festipin_errors_YYYY-MM-DD.log` | Errors only | 100MB | 60 days |
| `festipin_metrics_YYYY-MM-DD.log` | Metrics only | 500MB | 7 days |

## Viewing Logs

```bash
# Today's logs
cat logs/festipin_$(date +%Y-%m-%d).log | jq .

# Errors only
cat logs/festipin_errors_*.log | jq '.record.message'

# Metrics
cat logs/festipin_metrics_*.log | jq '.record.extra'

# Search by request ID
grep "request-id-123" logs/*.log

# Filter by level
cat logs/*.log | jq 'select(.record.level.name == "ERROR")'
```

## Best Practices

✅ **DO**: Use structured logging with key-value pairs
```python
log_info("User action", user_id=user_id, action="login")
```

❌ **DON'T**: Use string formatting
```python
log_info(f"User {user_id} performed {action}")
```

✅ **DO**: Include context
```python
log_error("API call failed", provider=provider, endpoint=url, status_code=status)
```

❌ **DON'T**: Log sensitive data
```python
log_info("User login", password=password)  # Never!
```

## Configuration

```bash
# .env file
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
ENVIRONMENT=development  # or production
```

## HTTP Middleware (Automatic)

Every request automatically logs:
- Incoming request (method, URL, client IP, user agent)
- Request completion (status, duration)
- Errors with full context
- Performance warnings for slow requests (> 2s)
- Correlation ID (added to response header as `X-Request-ID`)

No configuration needed - it's already active!

## Need More?

- Full guide: `LOGGING_GUIDE.md`
- Examples: `python3 examples/logging_example.py`
- Setup details: `LOGGING_SETUP_COMPLETE.md`
