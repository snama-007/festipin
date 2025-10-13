"""
Enhanced Logging System for Agent Orchestration

This module provides comprehensive logging with structured output,
performance metrics, and debugging capabilities.
"""

import logging
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from contextlib import asynccontextmanager
from functools import wraps
import traceback
import sys

from app.core.logging import logger as base_logger


class StructuredLogger:
    """Enhanced structured logger for orchestration system"""
    
    def __init__(self, name: str = "orchestration"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create formatter
        self.formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "module": "%(name)s", "function": "%(funcName)s", "line": %(lineno)d}',
            datefmt='%Y-%m-%dT%H:%M:%S.%f'
        )
        
        # Add handler if not exists
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(self.formatter)
            self.logger.addHandler(handler)
    
    def _log(self, level: str, message: str, **kwargs):
        """Internal logging method with structured data"""
        log_data = {
            "message": message,
            **kwargs
        }
        
        # Add timestamp
        log_data["timestamp"] = datetime.utcnow().isoformat()
        
        # Log based on level
        if level == "info":
            self.logger.info(json.dumps(log_data))
        elif level == "warning":
            self.logger.warning(json.dumps(log_data))
        elif level == "error":
            self.logger.error(json.dumps(log_data))
        elif level == "debug":
            self.logger.debug(json.dumps(log_data))
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log("info", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log("warning", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log("error", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log("debug", message, **kwargs)


class PerformanceLogger:
    """Logger for performance metrics and timing"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.metrics: Dict[str, List[float]] = {}
    
    @asynccontextmanager
    async def time_operation(self, operation_name: str, **context):
        """Context manager for timing operations"""
        start_time = time.time()
        try:
            self.logger.info(f"Starting {operation_name}", operation=operation_name, **context)
            yield
        except Exception as e:
            self.logger.error(f"Error in {operation_name}", 
                            operation=operation_name, 
                            error=str(e), 
                            traceback=traceback.format_exc(),
                            **context)
            raise
        finally:
            duration = time.time() - start_time
            self._record_metric(operation_name, duration)
            self.logger.info(f"Completed {operation_name}", 
                           operation=operation_name, 
                           duration=duration,
                           **context)
    
    def _record_metric(self, operation_name: str, duration: float):
        """Record performance metric"""
        if operation_name not in self.metrics:
            self.metrics[operation_name] = []
        self.metrics[operation_name].append(duration)
    
    def get_metrics_summary(self) -> Dict[str, Dict[str, float]]:
        """Get summary of performance metrics"""
        summary = {}
        for operation, times in self.metrics.items():
            if times:
                summary[operation] = {
                    "count": len(times),
                    "avg": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                    "total": sum(times)
                }
        return summary
    
    def log_metrics_summary(self):
        """Log performance metrics summary"""
        summary = self.get_metrics_summary()
        self.logger.info("Performance metrics summary", metrics=summary)


class AgentLogger:
    """Specialized logger for agent operations"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.agent_stats: Dict[str, Dict[str, Any]] = {}
    
    def log_agent_start(self, agent_name: str, event_id: str, inputs_count: int):
        """Log agent start"""
        self.logger.info(f"Agent {agent_name} started", 
                        agent_name=agent_name,
                        event_id=event_id,
                        inputs_count=inputs_count,
                        status="started")
        
        # Initialize stats
        if agent_name not in self.agent_stats:
            self.agent_stats[agent_name] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "total_time": 0.0,
                "avg_time": 0.0
            }
    
    def log_agent_complete(self, agent_name: str, event_id: str, 
                          execution_time: float, result_size: int):
        """Log agent completion"""
        self.logger.info(f"Agent {agent_name} completed", 
                        agent_name=agent_name,
                        event_id=event_id,
                        execution_time=execution_time,
                        result_size=result_size,
                        status="completed")
        
        # Update stats
        stats = self.agent_stats[agent_name]
        stats["total_executions"] += 1
        stats["successful_executions"] += 1
        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["total_executions"]
    
    def log_agent_error(self, agent_name: str, event_id: str, 
                       error: str, execution_time: float):
        """Log agent error"""
        self.logger.error(f"Agent {agent_name} failed", 
                         agent_name=agent_name,
                         event_id=event_id,
                         error=error,
                         execution_time=execution_time,
                         status="failed")
        
        # Update stats
        stats = self.agent_stats[agent_name]
        stats["total_executions"] += 1
        stats["failed_executions"] += 1
        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["total_executions"]
    
    def get_agent_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get agent statistics"""
        return self.agent_stats.copy()
    
    def log_agent_stats_summary(self):
        """Log agent statistics summary"""
        self.logger.info("Agent statistics summary", agent_stats=self.agent_stats)


class WorkflowLogger:
    """Logger for workflow operations"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.workflow_stats: Dict[str, Dict[str, Any]] = {}
    
    def log_workflow_start(self, event_id: str, inputs_count: int, 
                          metadata: Dict[str, Any]):
        """Log workflow start"""
        self.logger.info(f"Workflow started", 
                        event_id=event_id,
                        inputs_count=inputs_count,
                        metadata=metadata,
                        status="started")
        
        # Initialize workflow stats
        self.workflow_stats[event_id] = {
            "start_time": time.time(),
            "inputs_count": inputs_count,
            "agents_completed": 0,
            "agents_failed": 0,
            "total_agents": 8  # Total number of agents
        }
    
    def log_workflow_progress(self, event_id: str, completed_agents: int, 
                            current_agent: str):
        """Log workflow progress"""
        progress = (completed_agents / 8) * 100  # Assuming 8 total agents
        
        self.logger.info(f"Workflow progress", 
                        event_id=event_id,
                        completed_agents=completed_agents,
                        current_agent=current_agent,
                        progress_percent=progress,
                        status="running")
    
    def log_workflow_complete(self, event_id: str, total_time: float, 
                            final_plan_size: int):
        """Log workflow completion"""
        self.logger.info(f"Workflow completed", 
                        event_id=event_id,
                        total_time=total_time,
                        final_plan_size=final_plan_size,
                        status="completed")
        
        # Update stats
        if event_id in self.workflow_stats:
            self.workflow_stats[event_id]["end_time"] = time.time()
            self.workflow_stats[event_id]["total_time"] = total_time
            self.workflow_stats[event_id]["final_plan_size"] = final_plan_size
    
    def log_workflow_error(self, event_id: str, error: str, 
                          failed_agent: Optional[str] = None):
        """Log workflow error"""
        self.logger.error(f"Workflow failed", 
                         event_id=event_id,
                         error=error,
                         failed_agent=failed_agent,
                         status="failed")
        
        # Update stats
        if event_id in self.workflow_stats:
            self.workflow_stats[event_id]["end_time"] = time.time()
            self.workflow_stats[event_id]["error"] = error
            if failed_agent:
                self.workflow_stats[event_id]["agents_failed"] += 1


class MemoryLogger:
    """Logger for memory store operations"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
    
    def log_memory_operation(self, operation: str, event_id: str, 
                           success: bool, duration: float, 
                           data_size: Optional[int] = None):
        """Log memory store operation"""
        level = "info" if success else "error"
        message = f"Memory {operation} {'succeeded' if success else 'failed'}"
        
        log_data = {
            "operation": operation,
            "event_id": event_id,
            "success": success,
            "duration": duration
        }
        
        if data_size is not None:
            log_data["data_size"] = data_size
        
        if level == "info":
            self.logger.info(message, **log_data)
        else:
            self.logger.error(message, **log_data)


# Global logger instances
_structured_logger = StructuredLogger("orchestration")
_performance_logger = PerformanceLogger(_structured_logger)
_agent_logger = AgentLogger(_structured_logger)
_workflow_logger = WorkflowLogger(_structured_logger)
_memory_logger = MemoryLogger(_structured_logger)


def get_structured_logger() -> StructuredLogger:
    """Get global structured logger"""
    return _structured_logger


def get_performance_logger() -> PerformanceLogger:
    """Get global performance logger"""
    return _performance_logger


def get_agent_logger() -> AgentLogger:
    """Get global agent logger"""
    return _agent_logger


def get_workflow_logger() -> WorkflowLogger:
    """Get global workflow logger"""
    return _workflow_logger


def get_memory_logger() -> MemoryLogger:
    """Get global memory logger"""
    return _memory_logger


# Decorator for automatic logging
def log_function_calls(logger: StructuredLogger = None):
    """Decorator to automatically log function calls"""
    if logger is None:
        logger = _structured_logger
    
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            logger.info(f"Calling {func.__name__}", 
                       function=func.__name__,
                       args_count=len(args),
                       kwargs_keys=list(kwargs.keys()))
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"Completed {func.__name__}", 
                           function=func.__name__,
                           duration=duration,
                           success=True)
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Failed {func.__name__}", 
                           function=func.__name__,
                           duration=duration,
                           error=str(e),
                           success=False)
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            logger.info(f"Calling {func.__name__}", 
                       function=func.__name__,
                       args_count=len(args),
                       kwargs_keys=list(kwargs.keys()))
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"Completed {func.__name__}", 
                           function=func.__name__,
                           duration=duration,
                           success=True)
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Failed {func.__name__}", 
                           function=func.__name__,
                           duration=duration,
                           error=str(e),
                           success=False)
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# Utility function to log system status
def log_system_status():
    """Log current system status"""
    logger = get_structured_logger()
    
    # Log performance metrics
    perf_logger = get_performance_logger()
    perf_logger.log_metrics_summary()
    
    # Log agent stats
    agent_logger = get_agent_logger()
    agent_logger.log_agent_stats_summary()
    
    # Log workflow stats
    workflow_logger = get_workflow_logger()
    logger.info("Workflow statistics", workflow_stats=workflow_logger.workflow_stats)


# Initialize logging
def initialize_logging():
    """Initialize the enhanced logging system"""
    logger = get_structured_logger()
    logger.info("Enhanced logging system initialized", 
               system="orchestration",
               version="1.0.0")
    
    return logger
