"""
Local JSON-based Memory Store for Agent Orchestration

This module provides a file-based memory system for storing agent states,
event data, and orchestration context. Designed for immediate implementation
with easy migration path to Firebase later.
"""

import json
import os
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import uuid
import shutil
from dataclasses import dataclass, asdict
import threading

from app.core.logging import logger


@dataclass
class AgentResult:
    """Individual agent execution result"""
    agent_name: str
    status: str  # 'pending', 'running', 'completed', 'error'
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow().isoformat()


@dataclass
class EventState:
    """Complete event orchestration state"""
    event_id: str
    inputs: List[Dict[str, Any]]
    agent_results: Dict[str, AgentResult]
    workflow_status: str  # 'initializing', 'running', 'completed', 'error'
    user_feedback: Dict[str, Any]
    final_plan: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow().isoformat()
        if self.metadata is None:
            self.metadata = {}


class LocalMemoryStore:
    """
    Local JSON-based memory store for agent orchestration
    
    Features:
    - File-based storage with JSON serialization
    - Thread-safe operations
    - Automatic cleanup of old data
    - Easy migration to Firebase
    - Backup and restore capabilities
    """
    
    def __init__(self, base_path: str = "memory_store", max_age_days: int = 7):
        self.base_path = Path(base_path)
        self.max_age_days = max_age_days
        self.lock = threading.RLock()
        
        # Create directory structure
        self.events_dir = self.base_path / "events"
        self.backups_dir = self.base_path / "backups"
        self.temp_dir = self.base_path / "temp"
        
        self._ensure_directories()
        self._cleanup_old_data()
        
        logger.info("Local memory store initialized", base_path=str(self.base_path))
    
    def _ensure_directories(self):
        """Create necessary directories"""
        for directory in [self.events_dir, self.backups_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _cleanup_old_data(self):
        """Remove events older than max_age_days"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.max_age_days)
        
        for event_file in self.events_dir.glob("*.json"):
            try:
                file_time = datetime.fromtimestamp(event_file.stat().st_mtime)
                if file_time < cutoff_date:
                    event_file.unlink()
                    logger.info("Cleaned up old event file", file=str(event_file))
            except Exception as e:
                logger.warning("Failed to clean up old file", file=str(event_file), error=str(e))
    
    def generate_event_id(self) -> str:
        """Generate unique event ID"""
        return f"evt_{uuid.uuid4().hex[:12]}"
    
    async def create_event(self, inputs: List[Dict[str, Any]], metadata: Dict[str, Any] = None) -> str:
        """Create new event and return event_id"""
        event_id = self.generate_event_id()
        
        event_state = EventState(
            event_id=event_id,
            inputs=inputs,
            agent_results={},
            workflow_status="initializing",
            user_feedback={},
            metadata=metadata or {}
        )
        
        await self.store_event_state(event_state)
        
        logger.info("Created new event", event_id=event_id, input_count=len(inputs))
        return event_id
    
    async def store_event_state(self, event_state: EventState):
        """Store complete event state"""
        with self.lock:
            event_state.updated_at = datetime.utcnow().isoformat()
            
            # Write to temporary file first, then atomic move
            temp_file = self.temp_dir / f"{event_state.event_id}.json.tmp"
            final_file = self.events_dir / f"{event_state.event_id}.json"
            
            try:
                with open(temp_file, 'w') as f:
                    json.dump(asdict(event_state), f, indent=2, default=str)
                
                # Atomic move
                shutil.move(str(temp_file), str(final_file))
                
            except Exception as e:
                # Clean up temp file on error
                if temp_file.exists():
                    temp_file.unlink()
                raise e
    
    async def get_event_state(self, event_id: str) -> Optional[EventState]:
        """Retrieve event state"""
        event_file = self.events_dir / f"{event_id}.json"
        
        if not event_file.exists():
            return None
        
        try:
            with open(event_file, 'r') as f:
                data = json.load(f)
            
            # Convert agent_results back to AgentResult objects
            agent_results = {}
            for agent_name, result_data in data.get('agent_results', {}).items():
                agent_results[agent_name] = AgentResult(**result_data)
            
            # Create EventState object
            event_state = EventState(
                event_id=data['event_id'],
                inputs=data['inputs'],
                agent_results=agent_results,
                workflow_status=data['workflow_status'],
                user_feedback=data['user_feedback'],
                final_plan=data.get('final_plan'),
                metadata=data.get('metadata', {}),
                created_at=data['created_at'],
                updated_at=data['updated_at']
            )
            
            return event_state
            
        except Exception as e:
            logger.error("Failed to load event state", event_id=event_id, error=str(e))
            return None
    
    async def update_agent_result(self, event_id: str, agent_name: str, result: Dict[str, Any], 
                                status: str = "completed", error: str = None, execution_time: float = None):
        """Update specific agent result"""
        event_state = await self.get_event_state(event_id)
        if not event_state:
            raise ValueError(f"Event {event_id} not found")
        
        agent_result = AgentResult(
            agent_name=agent_name,
            status=status,
            result=result,
            error=error,
            execution_time=execution_time
        )
        
        event_state.agent_results[agent_name] = agent_result
        await self.store_event_state(event_state)
        
        logger.info("Updated agent result", 
                   event_id=event_id, 
                   agent_name=agent_name, 
                   status=status)
    
    async def update_workflow_status(self, event_id: str, status: str):
        """Update workflow status"""
        event_state = await self.get_event_state(event_id)
        if not event_state:
            raise ValueError(f"Event {event_id} not found")
        
        event_state.workflow_status = status
        await self.store_event_state(event_state)
        
        logger.info("Updated workflow status", event_id=event_id, status=status)
    
    async def add_user_feedback(self, event_id: str, feedback: Dict[str, Any]):
        """Add user feedback to event"""
        event_state = await self.get_event_state(event_id)
        if not event_state:
            raise ValueError(f"Event {event_id} not found")
        
        event_state.user_feedback.update(feedback)
        await self.store_event_state(event_state)
        
        logger.info("Added user feedback", event_id=event_id, feedback_keys=list(feedback.keys()))
    
    async def set_final_plan(self, event_id: str, plan: Dict[str, Any]):
        """Set final plan for event"""
        event_state = await self.get_event_state(event_id)
        if not event_state:
            raise ValueError(f"Event {event_id} not found")
        
        event_state.final_plan = plan
        event_state.workflow_status = "completed"
        await self.store_event_state(event_state)
        
        logger.info("Set final plan", event_id=event_id, plan_keys=list(plan.keys()))
    
    async def list_active_events(self) -> List[str]:
        """List all active event IDs"""
        event_files = list(self.events_dir.glob("*.json"))
        return [f.stem for f in event_files]
    
    async def get_event_summary(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get lightweight event summary"""
        event_state = await self.get_event_state(event_id)
        if not event_state:
            return None
        
        return {
            "event_id": event_state.event_id,
            "workflow_status": event_state.workflow_status,
            "input_count": len(event_state.inputs),
            "completed_agents": len([r for r in event_state.agent_results.values() 
                                   if r.status == "completed"]),
            "total_agents": len(event_state.agent_results),
            "has_final_plan": event_state.final_plan is not None,
            "created_at": event_state.created_at,
            "updated_at": event_state.updated_at
        }
    
    async def backup_event(self, event_id: str) -> str:
        """Create backup of event data"""
        event_state = await self.get_event_state(event_id)
        if not event_state:
            raise ValueError(f"Event {event_id} not found")
        
        backup_id = f"{event_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        backup_file = self.backups_dir / f"{backup_id}.json"
        
        with open(backup_file, 'w') as f:
            json.dump(asdict(event_state), f, indent=2, default=str)
        
        logger.info("Created event backup", event_id=event_id, backup_file=str(backup_file))
        return str(backup_file)
    
    async def restore_event(self, backup_file: str) -> str:
        """Restore event from backup"""
        with open(backup_file, 'r') as f:
            data = json.load(f)
        
        # Generate new event ID to avoid conflicts
        new_event_id = self.generate_event_id()
        data['event_id'] = new_event_id
        data['created_at'] = datetime.utcnow().isoformat()
        data['updated_at'] = datetime.utcnow().isoformat()
        
        # Convert agent_results back to AgentResult objects
        agent_results = {}
        for agent_name, result_data in data.get('agent_results', {}).items():
            agent_results[agent_name] = AgentResult(**result_data)
        
        event_state = EventState(
            event_id=new_event_id,
            inputs=data['inputs'],
            agent_results=agent_results,
            workflow_status=data['workflow_status'],
            user_feedback=data['user_feedback'],
            final_plan=data.get('final_plan'),
            metadata=data.get('metadata', {}),
            created_at=data['created_at'],
            updated_at=data['updated_at']
        )
        
        await self.store_event_state(event_state)
        
        logger.info("Restored event from backup", 
                   backup_file=backup_file, 
                   new_event_id=new_event_id)
        return new_event_id
    
    async def delete_event(self, event_id: str):
        """Delete event data"""
        event_file = self.events_dir / f"{event_id}.json"
        if event_file.exists():
            event_file.unlink()
            logger.info("Deleted event", event_id=event_id)
        else:
            logger.warning("Event file not found for deletion", event_id=event_id)
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory store statistics"""
        event_files = list(self.events_dir.glob("*.json"))
        backup_files = list(self.backups_dir.glob("*.json"))
        
        total_size = sum(f.stat().st_size for f in event_files)
        
        return {
            "active_events": len(event_files),
            "backups": len(backup_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "base_path": str(self.base_path),
            "max_age_days": self.max_age_days
        }


# Global instance
_memory_store: Optional[LocalMemoryStore] = None


def get_memory_store() -> LocalMemoryStore:
    """Get global memory store instance"""
    global _memory_store
    if _memory_store is None:
        _memory_store = LocalMemoryStore()
    return _memory_store


# Convenience functions for easy migration to Firebase later
async def create_event(inputs: List[Dict[str, Any]], metadata: Dict[str, Any] = None) -> str:
    """Create new event - interface compatible with Firebase version"""
    return await get_memory_store().create_event(inputs, metadata)


async def get_event_state(event_id: str) -> Optional[EventState]:
    """Get event state - interface compatible with Firebase version"""
    return await get_memory_store().get_event_state(event_id)


async def update_agent_result(event_id: str, agent_name: str, result: Dict[str, Any], 
                            status: str = "completed", error: str = None, execution_time: float = None):
    """Update agent result - interface compatible with Firebase version"""
    return await get_memory_store().update_agent_result(
        event_id, agent_name, result, status, error, execution_time
    )


async def set_final_plan(event_id: str, plan: Dict[str, Any]):
    """Set final plan - interface compatible with Firebase version"""
    return await get_memory_store().set_final_plan(event_id, plan)


async def update_workflow_status(event_id: str, status: str):
    """Update workflow status - interface compatible with Firebase version"""
    return await get_memory_store().update_workflow_status(event_id, status)


async def add_user_feedback(event_id: str, feedback: Dict[str, Any]):
    """Add user feedback - interface compatible with Firebase version"""
    return await get_memory_store().add_user_feedback(event_id, feedback)
