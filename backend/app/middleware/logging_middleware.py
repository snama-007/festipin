"""
FastAPI logging middleware with request/response tracking and correlation IDs
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logger import logger, set_request_id, clear_request_id, log_metrics


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses with correlation IDs
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        set_request_id(request_id)

        # Start timer
        start_time = time.time()

        # Log incoming request
        logger.info(
            "Incoming request",
            method=request.method,
            url=str(request.url),
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_id=request_id,
        )

        # Process request and handle errors
        try:
            response = await call_next(request)

            # Calculate request duration
            duration = time.time() - start_time

            # Log response
            logger.info(
                "Request completed",
                method=request.method,
                url=str(request.url),
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
                request_id=request_id,
            )

            # Log metrics
            log_metrics(
                "http_request_duration_seconds",
                duration,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as exc:
            # Calculate request duration even on error
            duration = time.time() - start_time

            # Log error with full context
            logger.error(
                "Request failed",
                method=request.method,
                url=str(request.url),
                path=request.url.path,
                duration_ms=round(duration * 1000, 2),
                error=str(exc),
                error_type=type(exc).__name__,
                request_id=request_id,
                exc_info=True,
            )

            raise

        finally:
            # Clear request context
            clear_request_id()


class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging slow requests and performance metrics
    """

    def __init__(self, app: ASGIApp, slow_request_threshold: float = 1.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time

        # Log slow requests
        if duration > self.slow_request_threshold:
            logger.warning(
                "Slow request detected",
                method=request.method,
                path=request.url.path,
                duration_ms=round(duration * 1000, 2),
                threshold_ms=self.slow_request_threshold * 1000,
            )

        return response


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for enhanced error logging with context
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            # Extract request context
            request_context = {
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "headers": dict(request.headers),
                "client_ip": request.client.host if request.client else None,
            }

            # Log error with full context
            logger.exception(
                "Unhandled exception in request",
                error=str(exc),
                error_type=type(exc).__name__,
                request_context=request_context,
            )

            # Re-raise exception for FastAPI to handle
            raise
