"""
Party-Specific Logging System

Each party session gets its own log file: logs/party_fp-{id}.log
Active party context is tracked to route logs appropriately.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from contextvars import ContextVar

from app.core.config import settings

# Context variable to track active party
_active_party_id: ContextVar[Optional[str]] = ContextVar('active_party_id', default=None)


class PartyLogger:
    """Logger that writes to party-specific log files"""

    def __init__(self):
        # Ensure logs directory exists
        self.logs_dir = Path(__file__).parent.parent.parent / "logs"
        self.logs_dir.mkdir(exist_ok=True)

        # Cache of file handlers for active parties
        self._handlers: Dict[str, logging.FileHandler] = {}

        # Main logger for general logs
        self.general_logger = logging.getLogger("festipin.general")

    def set_active_party(self, party_id: str):
        """Set the active party context"""
        if not party_id.startswith("fp-"):
            party_id = f"fp-{party_id}"
        _active_party_id.set(party_id)

    def clear_active_party(self):
        """Clear active party context"""
        _active_party_id.set(None)

    def get_active_party(self) -> Optional[str]:
        """Get current active party ID"""
        return _active_party_id.get()

    def _get_log_file_path(self, party_id: str) -> Path:
        """Get log file path for party"""
        # Ensure party_id starts with fp-
        if not party_id.startswith("fp-"):
            party_id = f"fp-{party_id}"
        return self.logs_dir / f"party_{party_id}.log"

    def _get_handler(self, party_id: str) -> logging.FileHandler:
        """Get or create file handler for party"""
        if party_id not in self._handlers:
            log_file = self._get_log_file_path(party_id)
            handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            handler.setLevel(logging.INFO)

            # JSON formatter
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)

            self._handlers[party_id] = handler

        return self._handlers[party_id]

    def _format_log_entry(
        self,
        level: str,
        message: str,
        party_id: str,
        **kwargs
    ) -> str:
        """Format log entry as JSON"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "party_id": party_id,
            "message": message,
            **kwargs
        }
        return json.dumps(log_entry, ensure_ascii=False)

    def log(
        self,
        level: str,
        message: str,
        party_id: Optional[str] = None,
        **kwargs
    ):
        """
        Log a message to party-specific log file

        Args:
            level: Log level (INFO, DEBUG, WARNING, ERROR)
            message: Log message
            party_id: Party ID (uses active party if not provided)
            **kwargs: Additional fields to include in log
        """
        # Get party_id from context if not provided
        if party_id is None:
            party_id = self.get_active_party()

        # If no party context, skip party logging
        if party_id is None:
            return

        # Ensure party_id starts with fp-
        if not party_id.startswith("fp-"):
            party_id = f"fp-{party_id}"

        # Get handler for this party
        handler = self._get_handler(party_id)

        # Format log entry
        log_entry = self._format_log_entry(level, message, party_id, **kwargs)

        # Create log record
        record = logging.LogRecord(
            name=f"party.{party_id}",
            level=getattr(logging, level),
            pathname="",
            lineno=0,
            msg=log_entry,
            args=(),
            exc_info=None
        )

        # Write to party log file
        handler.emit(record)
        handler.flush()

    def info(self, message: str, party_id: Optional[str] = None, **kwargs):
        """Log INFO level message"""
        self.log("INFO", message, party_id, **kwargs)

    def debug(self, message: str, party_id: Optional[str] = None, **kwargs):
        """Log DEBUG level message"""
        self.log("DEBUG", message, party_id, **kwargs)

    def warning(self, message: str, party_id: Optional[str] = None, **kwargs):
        """Log WARNING level message"""
        self.log("WARNING", message, party_id, **kwargs)

    def error(self, message: str, party_id: Optional[str] = None, **kwargs):
        """Log ERROR level message"""
        self.log("ERROR", message, party_id, **kwargs)

    def get_party_logs(self, party_id: str) -> list:
        """
        Read all logs for a specific party

        Returns:
            List of log entries (parsed JSON)
        """
        if not party_id.startswith("fp-"):
            party_id = f"fp-{party_id}"

        log_file = self._get_log_file_path(party_id)

        if not log_file.exists():
            return []

        logs = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        logs.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        return logs

    def clear_party_logs(self, party_id: str):
        """Clear logs for a specific party"""
        if not party_id.startswith("fp-"):
            party_id = f"fp-{party_id}"

        log_file = self._get_log_file_path(party_id)

        if log_file.exists():
            log_file.unlink()

        # Remove handler from cache
        if party_id in self._handlers:
            handler = self._handlers[party_id]
            handler.close()
            del self._handlers[party_id]

    def close_party_logger(self, party_id: str):
        """Close logger for a specific party (cleanup)"""
        if not party_id.startswith("fp-"):
            party_id = f"fp-{party_id}"

        if party_id in self._handlers:
            handler = self._handlers[party_id]
            handler.close()
            del self._handlers[party_id]

    def __del__(self):
        """Cleanup all handlers on shutdown"""
        for handler in self._handlers.values():
            try:
                handler.close()
            except:
                pass


# Global party logger instance
_party_logger: Optional[PartyLogger] = None


def get_party_logger() -> PartyLogger:
    """Get global party logger instance"""
    global _party_logger
    if _party_logger is None:
        _party_logger = PartyLogger()
    return _party_logger


def set_active_party(party_id: str):
    """Set active party context for logging"""
    logger = get_party_logger()
    logger.set_active_party(party_id)


def clear_active_party():
    """Clear active party context"""
    logger = get_party_logger()
    logger.clear_active_party()


def log_party_event(
    message: str,
    level: str = "INFO",
    party_id: Optional[str] = None,
    **kwargs
):
    """
    Convenience function to log party events

    Usage:
        log_party_event("Input complexity assessed",
                       complexity_level="simple",
                       use_llm=False)
    """
    logger = get_party_logger()
    logger.log(level, message, party_id, **kwargs)
