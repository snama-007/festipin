"""
API Routes for Agent Orchestration

This module provides REST API endpoints for the agentic party planning system
using LangGraph orchestration with local JSON memory storage.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.logging import logger
from app.services.simple_orchestrator import get_orchestrator
from app.services.local_memory_store import get_memory_store


router = APIRouter()


class OrchestrationRequest(BaseModel):
    """Request to start agent orchestration"""
    inputs: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None


class OrchestrationResponse(BaseModel):
    """Response from orchestration request"""
    success: bool
    event_id: str
    message: str


class WorkflowStatusResponse(BaseModel):
    """Response for workflow status"""
    success: bool
    event_id: str
    workflow_status: str
    agent_results: Dict[str, Any]
    final_plan: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str


class UserFeedbackRequest(BaseModel):
    """Request to add user feedback"""
    feedback: Dict[str, Any]


@router.post("/orchestration/start", response_model=OrchestrationResponse)
async def start_orchestration(request: OrchestrationRequest):
    """
    Start new agent orchestration workflow
    
    Args:
        request: OrchestrationRequest with inputs and metadata
    
    Returns:
        OrchestrationResponse with event_id
    """
    try:
        logger.info("Starting orchestration", input_count=len(request.inputs))
        
        # Validate inputs
        if not request.inputs:
            raise HTTPException(400, "At least one input is required")
        
        # Start orchestration
        orchestrator = get_orchestrator()
        event_id = await orchestrator.start_orchestration(
            request.inputs, 
            request.metadata
        )
        
        logger.info("Orchestration started successfully", event_id=event_id)
        
        return OrchestrationResponse(
            success=True,
            event_id=event_id,
            message=f"Orchestration started with event ID: {event_id}"
        )
        
    except Exception as e:
        logger.error("Failed to start orchestration", error=str(e))
        raise HTTPException(500, f"Failed to start orchestration: {str(e)}")


@router.get("/orchestration/status/{event_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(event_id: str):
    """
    Get current workflow status
    
    Args:
        event_id: Event ID to check status for
    
    Returns:
        WorkflowStatusResponse with current status
    """
    try:
        orchestrator = get_orchestrator()
        status = await orchestrator.get_workflow_status(event_id)
        
        if not status:
            raise HTTPException(404, f"Event {event_id} not found")
        
        return WorkflowStatusResponse(
            success=True,
            event_id=event_id,
            workflow_status=status["workflow_status"],
            agent_results=status["agent_results"],
            final_plan=status["final_plan"],
            created_at=status["created_at"],
            updated_at=status["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get workflow status", event_id=event_id, error=str(e))
        raise HTTPException(500, f"Failed to get workflow status: {str(e)}")


@router.post("/orchestration/feedback/{event_id}")
async def add_user_feedback(event_id: str, request: UserFeedbackRequest):
    """
    Add user feedback to workflow
    
    Args:
        event_id: Event ID to add feedback to
        request: UserFeedbackRequest with feedback data
    
    Returns:
        Success response
    """
    try:
        orchestrator = get_orchestrator()
        await orchestrator.add_user_feedback(event_id, request.feedback)
        
        logger.info("User feedback added", event_id=event_id, feedback_keys=list(request.feedback.keys()))
        
        return {"success": True, "message": "Feedback added successfully"}
        
    except Exception as e:
        logger.error("Failed to add user feedback", event_id=event_id, error=str(e))
        raise HTTPException(500, f"Failed to add feedback: {str(e)}")


@router.get("/orchestration/events")
async def list_active_events():
    """
    List all active events
    
    Returns:
        List of active event summaries
    """
    try:
        memory_store = get_memory_store()
        event_ids = await memory_store.list_active_events()
        
        summaries = []
        for event_id in event_ids:
            summary = await memory_store.get_event_summary(event_id)
            if summary:
                summaries.append(summary)
        
        return {
            "success": True,
            "events": summaries,
            "count": len(summaries)
        }
        
    except Exception as e:
        logger.error("Failed to list events", error=str(e))
        raise HTTPException(500, f"Failed to list events: {str(e)}")


@router.get("/orchestration/stats")
async def get_memory_stats():
    """
    Get memory store statistics
    
    Returns:
        Memory store statistics
    """
    try:
        memory_store = get_memory_store()
        stats = await memory_store.get_memory_stats()
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error("Failed to get memory stats", error=str(e))
        raise HTTPException(500, f"Failed to get memory stats: {str(e)}")


@router.post("/orchestration/backup/{event_id}")
async def backup_event(event_id: str):
    """
    Create backup of event data
    
    Args:
        event_id: Event ID to backup
    
    Returns:
        Backup file path
    """
    try:
        memory_store = get_memory_store()
        backup_path = await memory_store.backup_event(event_id)
        
        logger.info("Event backup created", event_id=event_id, backup_path=backup_path)
        
        return {
            "success": True,
            "backup_path": backup_path,
            "message": f"Backup created for event {event_id}"
        }
        
    except Exception as e:
        logger.error("Failed to backup event", event_id=event_id, error=str(e))
        raise HTTPException(500, f"Failed to backup event: {str(e)}")


@router.delete("/orchestration/event/{event_id}")
async def delete_event(event_id: str):
    """
    Delete event data
    
    Args:
        event_id: Event ID to delete
    
    Returns:
        Success response
    """
    try:
        memory_store = get_memory_store()
        await memory_store.delete_event(event_id)
        
        logger.info("Event deleted", event_id=event_id)
        
        return {
            "success": True,
            "message": f"Event {event_id} deleted successfully"
        }
        
    except Exception as e:
        logger.error("Failed to delete event", event_id=event_id, error=str(e))
        raise HTTPException(500, f"Failed to delete event: {str(e)}")


# Health check endpoint
@router.get("/orchestration/health")
async def health_check():
    """
    Health check for orchestration system
    
    Returns:
        System health status
    """
    try:
        # Check if orchestrator is available
        orchestrator = get_orchestrator()
        memory_store = get_memory_store()
        
        # Get basic stats
        stats = await memory_store.get_memory_stats()
        
        return {
            "success": True,
            "status": "healthy",
            "orchestrator": "available",
            "memory_store": "available",
            "active_events": stats["active_events"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
