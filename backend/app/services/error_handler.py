"""
Enhanced Error Handling for Agent Orchestration

This module provides comprehensive error handling, retry logic,
and graceful degradation for the agent orchestration system.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable, Type
from datetime import datetime, timedelta
from enum import Enum
import traceback

from app.core.logging import logger


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories"""
    NETWORK = "network"
    VALIDATION = "validation"
    PROCESSING = "processing"
    STORAGE = "storage"
    AGENT = "agent"
    SYSTEM = "system"


class OrchestrationError(Exception):
    """Base exception for orchestration errors"""
    
    def __init__(self, message: str, category: ErrorCategory, 
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.timestamp = datetime.utcnow()
        self.traceback = traceback.format_exc()


class AgentError(OrchestrationError):
    """Agent-specific errors"""
    
    def __init__(self, agent_name: str, message: str, 
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Agent {agent_name}: {message}",
            ErrorCategory.AGENT,
            severity,
            {"agent_name": agent_name, **details or {}}
        )


class StorageError(OrchestrationError):
    """Storage-related errors"""
    
    def __init__(self, message: str, operation: str,
                 severity: ErrorSeverity = ErrorSeverity.HIGH,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Storage {operation}: {message}",
            ErrorCategory.STORAGE,
            severity,
            {"operation": operation, **details or {}}
        )


class ValidationError(OrchestrationError):
    """Validation errors"""
    
    def __init__(self, message: str, field: Optional[str] = None,
                 severity: ErrorSeverity = ErrorSeverity.LOW,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Validation error: {message}",
            ErrorCategory.VALIDATION,
            severity,
            {"field": field, **details or {}}
        )


class RetryConfig:
    """Configuration for retry logic"""
    
    def __init__(self, max_attempts: int = 3, 
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_backoff: bool = True,
                 jitter: bool = True):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_backoff = exponential_backoff
        self.jitter = jitter


class ErrorHandler:
    """Centralized error handling for orchestration"""
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.circuit_breakers: Dict[str, bool] = {}
        self.last_errors: Dict[str, datetime] = {}
    
    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """
        Handle an error and determine if operation should continue
        
        Returns:
            bool: True if operation should continue, False if should stop
        """
        error_key = self._get_error_key(error, context)
        
        # Log error
        await self._log_error(error, context)
        
        # Update error tracking
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        self.last_errors[error_key] = datetime.utcnow()
        
        # Check circuit breaker
        if self._is_circuit_open(error_key):
            logger.warning(f"Circuit breaker open for {error_key}")
            return False
        
        # Determine if should continue based on error type
        if isinstance(error, OrchestrationError):
            return self._should_continue_orchestration_error(error)
        else:
            return self._should_continue_generic_error(error)
    
    def _get_error_key(self, error: Exception, context: Dict[str, Any]) -> str:
        """Generate unique key for error tracking"""
        if isinstance(error, OrchestrationError):
            return f"{error.category.value}_{context.get('agent_name', 'unknown')}"
        else:
            return f"generic_{type(error).__name__}"
    
    async def _log_error(self, error: Exception, context: Dict[str, Any]):
        """Log error with appropriate level"""
        error_data = {
            "error_type": type(error).__name__,
            "message": str(error),
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if isinstance(error, OrchestrationError):
            error_data.update({
                "category": error.category.value,
                "severity": error.severity.value,
                "details": error.details
            })
            
            # Log based on severity
            if error.severity == ErrorSeverity.CRITICAL:
                logger.error("Critical orchestration error", **error_data)
            elif error.severity == ErrorSeverity.HIGH:
                logger.error("High severity orchestration error", **error_data)
            elif error.severity == ErrorSeverity.MEDIUM:
                logger.warning("Medium severity orchestration error", **error_data)
            else:
                logger.info("Low severity orchestration error", **error_data)
        else:
            logger.error("Generic error in orchestration", **error_data)
    
    def _is_circuit_open(self, error_key: str) -> bool:
        """Check if circuit breaker is open for error type"""
        if error_key in self.circuit_breakers:
            return self.circuit_breakers[error_key]
        
        # Open circuit if too many errors in short time
        error_count = self.error_counts.get(error_key, 0)
        last_error = self.last_errors.get(error_key)
        
        if error_count >= 5 and last_error:
            time_since_last = datetime.utcnow() - last_error
            if time_since_last < timedelta(minutes=5):
                self.circuit_breakers[error_key] = True
                return True
        
        return False
    
    def _should_continue_orchestration_error(self, error: OrchestrationError) -> bool:
        """Determine if should continue after orchestration error"""
        if error.severity == ErrorSeverity.CRITICAL:
            return False
        elif error.severity == ErrorSeverity.HIGH:
            return error.category in [ErrorCategory.AGENT, ErrorCategory.PROCESSING]
        else:
            return True
    
    def _should_continue_generic_error(self, error: Exception) -> bool:
        """Determine if should continue after generic error"""
        # Continue for most generic errors, stop for critical ones
        critical_errors = [MemoryError, SystemExit, KeyboardInterrupt]
        return not any(isinstance(error, exc_type) for exc_type in critical_errors)
    
    def reset_circuit_breaker(self, error_key: str):
        """Reset circuit breaker for error type"""
        self.circuit_breakers[error_key] = False
        self.error_counts[error_key] = 0


async def retry_with_backoff(func: Callable, *args, 
                           retry_config: RetryConfig = None,
                           error_handler: ErrorHandler = None,
                           **kwargs) -> Any:
    """
    Execute function with retry logic and exponential backoff
    
    Args:
        func: Function to execute
        *args: Function arguments
        retry_config: Retry configuration
        error_handler: Error handler instance
        **kwargs: Function keyword arguments
    
    Returns:
        Function result or raises last exception
    """
    if retry_config is None:
        retry_config = RetryConfig()
    
    if error_handler is None:
        error_handler = ErrorHandler()
    
    last_exception = None
    
    for attempt in range(retry_config.max_attempts):
        try:
            result = await func(*args, **kwargs)
            
            # Reset error count on success
            error_key = f"{func.__name__}_success"
            error_handler.error_counts[error_key] = 0
            
            return result
            
        except Exception as e:
            last_exception = e
            
            # Check if should continue retrying
            context = {
                "function": func.__name__,
                "attempt": attempt + 1,
                "max_attempts": retry_config.max_attempts
            }
            
            should_continue = await error_handler.handle_error(e, context)
            
            if not should_continue or attempt == retry_config.max_attempts - 1:
                break
            
            # Calculate delay
            delay = retry_config.base_delay
            if retry_config.exponential_backoff:
                delay *= (2 ** attempt)
            
            delay = min(delay, retry_config.max_delay)
            
            if retry_config.jitter:
                import random
                delay *= (0.5 + random.random() * 0.5)
            
            logger.info(f"Retrying {func.__name__} in {delay:.2f}s (attempt {attempt + 1})")
            await asyncio.sleep(delay)
    
    # Re-raise last exception
    raise last_exception


class GracefulDegradation:
    """Handle graceful degradation when components fail"""
    
    def __init__(self):
        self.fallback_strategies: Dict[str, Callable] = {}
        self.component_status: Dict[str, bool] = {}
    
    def register_fallback(self, component: str, fallback_func: Callable):
        """Register fallback strategy for component"""
        self.fallback_strategies[component] = fallback_func
    
    async def execute_with_fallback(self, component: str, primary_func: Callable, 
                                  *args, **kwargs) -> Any:
        """Execute primary function with fallback if it fails"""
        try:
            result = await primary_func(*args, **kwargs)
            self.component_status[component] = True
            return result
            
        except Exception as e:
            logger.warning(f"Primary {component} failed, using fallback", error=str(e))
            self.component_status[component] = False
            
            if component in self.fallback_strategies:
                fallback_func = self.fallback_strategies[component]
                return await fallback_func(*args, **kwargs)
            else:
                raise e
    
    def is_component_healthy(self, component: str) -> bool:
        """Check if component is healthy"""
        return self.component_status.get(component, True)


# Global error handler instance
_error_handler = ErrorHandler()
_graceful_degradation = GracefulDegradation()


def get_error_handler() -> ErrorHandler:
    """Get global error handler"""
    return _error_handler


def get_graceful_degradation() -> GracefulDegradation:
    """Get global graceful degradation handler"""
    return _graceful_degradation


# Decorator for automatic error handling
def handle_errors(error_category: ErrorCategory = ErrorCategory.SYSTEM,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM):
    """Decorator for automatic error handling"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if not isinstance(e, OrchestrationError):
                    e = OrchestrationError(
                        str(e), error_category, severity,
                        {"function": func.__name__}
                    )
                
                context = {
                    "function": func.__name__,
                    "args": str(args)[:100],  # Truncate for logging
                    "kwargs": str(kwargs)[:100]
                }
                
                should_continue = await _error_handler.handle_error(e, context)
                
                if not should_continue:
                    raise e
                
                # Return default value based on error category
                return _get_default_return_value(error_category)
        
        return wrapper
    return decorator


def _get_default_return_value(category: ErrorCategory) -> Any:
    """Get default return value for error category"""
    defaults = {
        ErrorCategory.AGENT: {"error": "Agent execution failed"},
        ErrorCategory.STORAGE: None,
        ErrorCategory.VALIDATION: False,
        ErrorCategory.PROCESSING: {},
        ErrorCategory.NETWORK: None,
        ErrorCategory.SYSTEM: None
    }
    return defaults.get(category, None)
