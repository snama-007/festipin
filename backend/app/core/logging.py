"""
Structured logging configuration
"""

import logging
import sys
from typing import Any, Dict
import json
from datetime import datetime, timezone

from app.core.config import settings


class StructuredLogger:
    """Structured JSON logger"""
    
    def __init__(self, name: str = "parx-planner"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        # Console handler with structured format
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(handler)
    
    def _log(self, level: str, message: str, **kwargs: Any):
        """Internal log method with structured data"""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
            **kwargs
        }
        
        log_method = getattr(self.logger, level.lower())
        log_method(json.dumps(log_data))
    
    def info(self, message: str, **kwargs: Any):
        """Log info message"""
        self._log("INFO", message, **kwargs)
    
    def error(self, message: str, **kwargs: Any):
        """Log error message"""
        self._log("ERROR", message, **kwargs)
    
    def warning(self, message: str, **kwargs: Any):
        """Log warning message"""
        self._log("WARNING", message, **kwargs)
    
    def debug(self, message: str, **kwargs: Any):
        """Log debug message"""
        self._log("DEBUG", message, **kwargs)


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logs"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record"""
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            try:
                # If already JSON, return as-is
                json.loads(record.msg)
                return record.msg
            except json.JSONDecodeError:
                pass
        
        # Create structured log
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logging() -> StructuredLogger:
    """Setup application logging"""
    return StructuredLogger()


# Global logger instance
logger = setup_logging()

