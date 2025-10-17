"""
Enhanced structured logging with Loguru
Simple, powerful, and production-ready logging for FastAPI
"""

import sys
import json
from pathlib import Path
from typing import Any, Dict, Optional
from contextvars import ContextVar
from loguru import logger

from app.core.config import settings


# Context variable for request correlation ID
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def serialize_record(record: Dict[str, Any]) -> str:
    """
    Serialize log record to JSON format for structured logging
    """
    import traceback as tb

    subset = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
    }

    # Add request ID if available
    request_id = request_id_ctx.get()
    if request_id:
        subset["request_id"] = request_id

    # Add extra fields
    if record.get("extra"):
        subset["extra"] = record["extra"]

    # Add exception info if present
    if record.get("exception"):
        exc_type, exc_value, exc_traceback = record["exception"]
        subset["exception"] = {
            "type": exc_type.__name__ if exc_type else None,
            "value": str(exc_value) if exc_value else None,
            "traceback": "".join(tb.format_tb(exc_traceback)) if exc_traceback else None,
        }

    return json.dumps(subset)


def setup_logging():
    """
    Configure Loguru logger with structured JSON output and file rotation
    """
    # Remove default handler
    logger.remove()

    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Console handler - Pretty format for development
    if settings.ENVIRONMENT == "development":
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
            level=settings.LOG_LEVEL,
            colorize=True,
        )
    else:
        # JSON format for production (easier to parse with log aggregators)
        logger.add(
            sys.stdout,
            format="{message}",
            level=settings.LOG_LEVEL,
        )

    # File handler - JSON format with rotation
    logger.add(
        log_dir / "festipin_{time:YYYY-MM-DD}.log",
        format="{message}",
        level=settings.LOG_LEVEL,
        rotation="00:00",  # Rotate at midnight
        retention="30 days",  # Keep logs for 30 days
        compression="zip",  # Compress rotated logs
        enqueue=True,  # Thread-safe logging
        serialize=True,  # Serialize as JSON
    )

    # Error file handler - Only errors and above
    logger.add(
        log_dir / "festipin_errors_{time:YYYY-MM-DD}.log",
        format="{message}",
        level="ERROR",
        rotation="100 MB",  # Rotate when file reaches 100MB
        retention="60 days",  # Keep error logs longer
        compression="zip",
        enqueue=True,
        serialize=True,  # Serialize as JSON
        backtrace=True,  # Include full traceback
        diagnose=True,  # Include variable values in traceback
    )

    # Performance/metrics file handler
    logger.add(
        log_dir / "festipin_metrics_{time:YYYY-MM-DD}.log",
        format="{message}",
        level="INFO",
        filter=lambda record: "metrics" in record["extra"],
        rotation="500 MB",
        retention="7 days",
        compression="zip",
        enqueue=True,
        serialize=True,  # Serialize as JSON
    )

    logger.info(
        "Logging initialized",
        environment=settings.ENVIRONMENT,
        log_level=settings.LOG_LEVEL,
    )


# Initialize logging on module import
setup_logging()


# Convenience functions for structured logging
def log_info(message: str, **kwargs):
    """Log info message with structured data"""
    logger.bind(**kwargs).info(message)


def log_error(message: str, **kwargs):
    """Log error message with structured data"""
    logger.bind(**kwargs).error(message)


def log_warning(message: str, **kwargs):
    """Log warning message with structured data"""
    logger.bind(**kwargs).warning(message)


def log_debug(message: str, **kwargs):
    """Log debug message with structured data"""
    logger.bind(**kwargs).debug(message)


def log_success(message: str, **kwargs):
    """Log success message with structured data"""
    logger.bind(**kwargs).success(message)


def log_critical(message: str, **kwargs):
    """Log critical message with structured data"""
    logger.bind(**kwargs).critical(message)


def log_metrics(metric_name: str, value: Any, **kwargs):
    """Log metrics data for monitoring"""
    logger.bind(metrics=True, metric_name=metric_name, metric_value=value, **kwargs).info(
        f"Metric: {metric_name} = {value}"
    )


def set_request_id(request_id: str):
    """Set request ID for correlation"""
    request_id_ctx.set(request_id)


def get_request_id() -> Optional[str]:
    """Get current request ID"""
    return request_id_ctx.get()


def clear_request_id():
    """Clear request ID"""
    request_id_ctx.set(None)


# Export logger instance
__all__ = [
    "logger",
    "log_info",
    "log_error",
    "log_warning",
    "log_debug",
    "log_success",
    "log_critical",
    "log_metrics",
    "set_request_id",
    "get_request_id",
    "clear_request_id",
]
