"""
Event-Driven Agent System API Routes

RESTful API endpoints for the event-driven party planning system.
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.services.event_driven_orchestrator import get_orchestrator
from app.core.logging import logger


router = APIRouter(prefix="/event-driven", tags=["Event-Driven Agents"])


# ===== Request/Response Models =====

class CreatePartyRequest(BaseModel):
    """Request to create a new party"""
    party_id: Optional[str] = Field(None, description="Optional custom party ID")
    initial_inputs: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Optional initial inputs"
    )
    user_id: Optional[str] = Field(None, description="User ID")

    class Config:
        json_schema_extra = {
            "example": {
                "initial_inputs": [
                    {
                        "content": "jungle theme party for 75 guests",
                        "source_type": "text",
                        "tags": ["theme", "venue"]
                    }
                ]
            }
        }


class CreatePartyResponse(BaseModel):
    """Response after creating a party"""
    success: bool
    party_id: str
    message: str
    websocket_url: str


class AddInputRequest(BaseModel):
    """Request to add input to party"""
    content: str = Field(..., description="Input content")
    source_type: str = Field(default="text", description="text, image, url, upload")
    tags: List[str] = Field(default_factory=list, description="Optional tags")
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "content": "I want a chocolate cake with unicorn decorations",
                "source_type": "text",
                "tags": ["cake"]
            }
        }


class AddInputResponse(BaseModel):
    """Response after adding input"""
    success: bool
    input_id: str
    message: str


class PartyStatusResponse(BaseModel):
    """Party status response"""
    success: bool
    party: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class SystemStatusResponse(BaseModel):
    """System status response"""
    success: bool
    status: Dict[str, Any]


# ===== API Endpoints =====

@router.post("/party", response_model=CreatePartyResponse)
async def create_party(request: CreatePartyRequest):
    """
    Create a new party planning session.

    This endpoint:
    1. Creates a new party state
    2. Processes initial inputs (if provided)
    3. Triggers InputAnalyzer to classify inputs
    4. Returns party ID and WebSocket URL for real-time updates

    Example:
    ```
    POST /api/v1/event-driven/party
    {
        "initial_inputs": [
            {
                "content": "jungle theme party for 75 guests",
                "source_type": "text",
                "tags": ["theme"]
            }
        ]
    }
    ```
    """
    try:
        orchestrator = await get_orchestrator()

        party_id = await orchestrator.create_party(
            party_id=request.party_id,
            initial_inputs=request.initial_inputs,
            user_id=request.user_id
        )

        return CreatePartyResponse(
            success=True,
            party_id=party_id,
            message="Party created successfully",
            websocket_url=f"ws://localhost:9000/api/v1/event-driven/ws/{party_id}"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to create party", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create party: {str(e)}")


@router.post("/party/{party_id}/input", response_model=AddInputResponse)
async def add_input(party_id: str, request: AddInputRequest):
    """
    Add input to existing party.

    This triggers:
    1. InputAnalyzer classifies the input
    2. Appropriate agents are triggered
    3. Real-time updates sent via WebSocket

    Example:
    ```
    POST /api/v1/event-driven/party/fp2025A12345/input
    {
        "content": "chocolate cake with rainbow frosting",
        "source_type": "text",
        "tags": ["cake"]
    }
    ```
    """
    try:
        orchestrator = await get_orchestrator()

        input_id = await orchestrator.add_input(
            party_id=party_id,
            content=request.content,
            source_type=request.source_type,
            tags=request.tags,
            metadata=request.metadata
        )

        return AddInputResponse(
            success=True,
            input_id=input_id,
            message="Input added successfully"
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Failed to add input", party_id=party_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to add input: {str(e)}")


@router.delete("/party/{party_id}/input/{input_id}")
async def remove_input(party_id: str, input_id: str):
    """
    Remove input from party.

    This triggers:
    1. Input is removed from state
    2. InputAnalyzer checks if agents still need to run
    3. Agents may be removed or re-run
    4. Budget and plan are recalculated

    Example:
    ```
    DELETE /api/v1/event-driven/party/fp2025A12345/input/inp_abc123
    ```
    """
    try:
        orchestrator = await get_orchestrator()

        removed = await orchestrator.remove_input(party_id, input_id)

        if not removed:
            raise HTTPException(status_code=404, detail="Input not found")

        return {
            "success": True,
            "message": "Input removed successfully"
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to remove input", party_id=party_id, input_id=input_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to remove input: {str(e)}")


@router.get("/party/{party_id}/status", response_model=PartyStatusResponse)
async def get_party_status(party_id: str):
    """
    Get current status of party planning session.

    Returns:
    - All inputs
    - Agent statuses and results
    - Current budget
    - Final plan
    - Timestamps and metadata

    Example:
    ```
    GET /api/v1/event-driven/party/fp2025A12345/status
    ```
    """
    try:
        orchestrator = await get_orchestrator()

        status = await orchestrator.get_party_status(party_id)

        if not status:
            raise HTTPException(status_code=404, detail=f"Party {party_id} not found")

        return PartyStatusResponse(
            success=True,
            party=status
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get party status", party_id=party_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/system/status", response_model=SystemStatusResponse)
async def get_system_status():
    """
    Get overall system status.

    Returns:
    - Orchestrator status
    - Event bus metrics
    - State store statistics
    - Agent statuses

    Example:
    ```
    GET /api/v1/event-driven/system/status
    ```
    """
    try:
        orchestrator = await get_orchestrator()

        status = await orchestrator.get_system_status()

        return SystemStatusResponse(
            success=True,
            status=status
        )

    except Exception as e:
        logger.error("Failed to get system status", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/system/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
    - Service status
    - Timestamp
    """
    try:
        orchestrator = await get_orchestrator()

        return {
            "status": "healthy",
            "service": "event-driven-orchestrator",
            "running": orchestrator._running,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.websocket("/ws/{party_id}")
async def websocket_endpoint(websocket: WebSocket, party_id: str):
    """
    WebSocket endpoint for real-time party planning updates.

    Connect to: ws://localhost:9000/api/v1/event-driven/ws/{party_id}

    Receives messages:
    - agent_started: Agent begins execution
    - agent_completed: Agent finishes with results
    - agent_failed: Agent encounters error
    - budget_updated: Budget recalculated
    - plan_updated: Plan updated

    Example usage in JavaScript:
    ```javascript
    const ws = new WebSocket('ws://localhost:9000/api/v1/event-driven/ws/fp2025A12345');

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Update:', data);
    };
    ```
    """
    from app.api.routes.websocket import manager

    # Use existing WebSocket manager
    await manager.connect(party_id, websocket)

    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()

            # Echo back (for heartbeat/ping)
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        await manager.disconnect(party_id, websocket)
        logger.info("WebSocket client disconnected", party_id=party_id)
    except Exception as e:
        logger.error("WebSocket error", party_id=party_id, error=str(e))
        await manager.disconnect(party_id, websocket)


# Export router
__all__ = ["router"]
