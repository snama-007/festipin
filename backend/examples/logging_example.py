"""
Example usage of the Loguru logging system
Run this file to see different logging examples
"""

import time
import asyncio
from app.core.logger import (
    log_info,
    log_error,
    log_warning,
    log_debug,
    log_success,
    log_critical,
    log_metrics,
    set_request_id,
    logger,
)


def basic_logging_examples():
    """Basic logging examples"""
    print("\n=== Basic Logging Examples ===\n")

    # Simple info log
    log_info("Application started")

    # Log with structured data
    log_info(
        "User action performed",
        user_id="user123",
        action="login",
        ip_address="192.168.1.1",
    )

    # Success log
    log_success("Database connection established")

    # Warning log
    log_warning(
        "API rate limit approaching",
        current_count=95,
        limit=100,
        time_window="1 minute",
    )

    # Error log
    log_error(
        "Failed to process payment",
        error="Insufficient funds",
        error_type="PaymentError",
        user_id="user123",
        amount=99.99,
    )

    # Debug log (only shown if LOG_LEVEL=DEBUG)
    log_debug(
        "Processing request",
        payload={"key": "value"},
        headers={"Authorization": "Bearer [REDACTED]"},
    )


def exception_logging_example():
    """Exception logging example"""
    print("\n=== Exception Logging Example ===\n")

    try:
        # Simulate an error
        result = 1 / 0
    except Exception as e:
        log_error(
            "Mathematical operation failed",
            error=str(e),
            error_type=type(e).__name__,
            operation="division",
        )

        # Using logger.exception for full traceback
        logger.exception("Full exception details with traceback")


def metrics_logging_examples():
    """Metrics logging examples"""
    print("\n=== Metrics Logging Examples ===\n")

    # Performance metric
    start_time = time.time()
    time.sleep(0.1)  # Simulate work
    duration = time.time() - start_time

    log_metrics(
        "image_generation_duration",
        duration,
        provider="runware",
        quality="premium",
        success=True,
    )

    # Counter metric
    log_metrics(
        "api_requests_total",
        1,
        endpoint="/api/generate",
        method="POST",
        status_code=200,
    )

    # Business metric
    log_metrics(
        "revenue_generated",
        29.99,
        currency="USD",
        subscription_type="premium",
    )


def request_correlation_example():
    """Request correlation example"""
    print("\n=== Request Correlation Example ===\n")

    # Simulate a request with correlation ID
    request_id = "req-123-abc-456"
    set_request_id(request_id)

    log_info("Processing request", endpoint="/api/generate", method="POST")

    # Simulate service calls
    log_info("Calling image generation service", provider="runware")
    time.sleep(0.05)
    log_info("Image generation completed", generation_id="img-789")

    # Simulate database call
    log_info("Saving to database", table="generations")
    time.sleep(0.02)
    log_success("Database save completed", record_id="db-456")

    log_info("Request completed", duration_ms=70, status="success")


def service_logging_example():
    """Service-specific logging example"""
    print("\n=== Service Logging Example ===\n")

    # Service initialization
    log_info(
        "Service Manager initialized",
        providers=["runware", "gemini"],
        provider_count=2,
        routing_strategy="primary_first",
    )

    # Circuit breaker
    log_warning(
        "Circuit breaker opened",
        provider="runware",
        failure_count=5,
        threshold=5,
    )

    # Provider selection
    log_info(
        "Provider selected",
        provider="gemini",
        reason="circuit_breaker_open",
        fallback=True,
    )

    # Generation completed
    log_success(
        "Image generation completed",
        provider="gemini",
        generation_id="gen-123",
        duration_ms=1234.56,
        quality="standard",
    )


async def async_logging_example():
    """Async logging example"""
    print("\n=== Async Logging Example ===\n")

    async def process_task(task_id: int):
        log_info("Task started", task_id=task_id)
        await asyncio.sleep(0.1)
        log_success("Task completed", task_id=task_id)

    # Run multiple async tasks
    tasks = [process_task(i) for i in range(3)]
    await asyncio.gather(*tasks)


def contextual_logging_example():
    """Contextual logging with bind"""
    print("\n=== Contextual Logging Example ===\n")

    # Create a logger with context
    user_logger = logger.bind(user_id="user789", session_id="sess123")

    user_logger.info("User logged in")
    user_logger.info("User viewed dashboard")
    user_logger.info("User generated image")
    user_logger.success("User session completed")


def performance_tracking_example():
    """Performance tracking example"""
    print("\n=== Performance Tracking Example ===\n")

    operations = [
        ("database_query", 0.05),
        ("api_call", 0.15),
        ("image_processing", 0.5),
        ("file_upload", 0.2),
    ]

    for operation, duration in operations:
        time.sleep(duration)
        log_metrics(
            f"{operation}_duration",
            duration,
            operation=operation,
            status="completed",
        )

        if duration > 0.3:
            log_warning(
                "Slow operation detected",
                operation=operation,
                duration_ms=duration * 1000,
                threshold_ms=300,
            )


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("Loguru Structured Logging Examples")
    print("=" * 60)

    basic_logging_examples()
    exception_logging_example()
    metrics_logging_examples()
    request_correlation_example()
    service_logging_example()
    contextual_logging_example()
    performance_tracking_example()

    # Run async example
    asyncio.run(async_logging_example())

    print("\n" + "=" * 60)
    print("Examples completed! Check logs/ directory for output.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
