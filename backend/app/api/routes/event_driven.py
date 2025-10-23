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
from app.core.party_logger import set_active_party, clear_active_party, log_party_event, get_party_logger


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

    # NEW: Support for image URLs (Pinterest, uploads, or direct URLs)
    image_url: Optional[str] = Field(None, description="Image URL for vision analysis")

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

        # Set active party context for logging
        set_active_party(party_id)

        # Log party creation to party-specific log file
        log_party_event(
            "Party session created",
            user_id=request.user_id,
            initial_inputs_count=len(request.initial_inputs) if request.initial_inputs else 0
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
    Add input to existing party - supports text, image, or BOTH.

    This triggers:
    1. UnifiedInputProcessor processes text and/or image
    2. Vision AI analyzes images (if provided)
    3. Smart Router chooses optimal extraction (regex or LLM)
    4. InputAnalyzer classifies the combined input
    5. Appropriate agents are triggered
    6. Real-time updates sent via WebSocket

    Example (Text only):
    ```
    POST /api/v1/event-driven/party/fp2025A12345/input
    {
        "content": "chocolate cake with rainbow frosting",
        "source_type": "text",
        "tags": ["cake"]
    }
    ```

    Example (Image only):
    ```
    POST /api/v1/event-driven/party/fp2025A12345/input
    {
        "content": "pinterest_pin_123",
        "source_type": "image",
        "image_url": "https://pinterest.com/pin/123..."
    }
    ```

    Example (Text + Image):
    ```
    POST /api/v1/event-driven/party/fp2025A12345/input
    {
        "content": "I want something like this for a 5-year-old",
        "source_type": "text",
        "image_url": "https://pinterest.com/pin/123...",
        "tags": ["inspiration"]
    }
    ```
    """
    try:
        # Set active party context for logging
        set_active_party(party_id)

        from app.services.unified_input_processor import get_unified_processor

        # Step 1: Process input with UnifiedInputProcessor
        processor = get_unified_processor()

        processed = await processor.process(
            content=request.content,
            source_type=request.source_type,
            image_url=request.image_url,
            tags=request.tags
        )

        logger.info(
            "Input processed",
            party_id=party_id,
            processor_chain=processed.get("processor_chain"),
            confidence=processed.get("confidence"),
            has_vision=bool(processed.get("vision_data"))
        )

        # Step 2: Add to orchestrator with enriched data
        orchestrator = await get_orchestrator()

        # Prepare enhanced metadata
        enhanced_metadata = {
            **(request.metadata or {}),
            "image_url": request.image_url,
            "vision_analysis": processed.get("vision_data").to_dict() if processed.get("vision_data") else None,
            "processor_chain": processed.get("processor_chain"),
            "extraction_confidence": processed.get("confidence"),
            "agent_context": processed.get("agent_context")
        }

        input_id = await orchestrator.add_input(
            party_id=party_id,
            content=processed.get("natural_language", request.content),
            source_type=request.source_type,
            tags=processed.get("tags", request.tags),
            metadata=enhanced_metadata
        )

        # Prepare response message
        message_parts = ["Input added successfully"]
        if processed.get("vision_data"):
            theme = processed["vision_data"].theme
            message_parts.append(f"with vision analysis (detected: {theme} theme)")

        processor_info = " + ".join(processed.get("processor_chain", []))
        if processor_info:
            message_parts.append(f"[{processor_info}]")

        return AddInputResponse(
            success=True,
            input_id=input_id,
            message=". ".join(message_parts)
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


@router.get("/party/{party_id}/logs")
async def get_party_logs(party_id: str):
    """
    Get all logs for a specific party session.

    Returns all party-specific logs from the log file.
    Logs include:
    - Party creation
    - Input processing decisions (regex vs LLM)
    - Agent executions
    - Plan updates
    - Budget calculations

    Example:
    ```
    GET /api/v1/event-driven/party/fp-2025A12345/logs
    ```

    Response:
    ```json
    {
        "party_id": "fp-2025A12345",
        "log_file": "logs/party_fp-2025A12345.log",
        "total_logs": 45,
        "logs": [
            {
                "timestamp": "2025-10-22T...",
                "level": "INFO",
                "party_id": "fp-2025A12345",
                "message": "Party session created",
                "user_id": "user123"
            },
            ...
        ]
    }
    ```
    """
    try:
        party_logger = get_party_logger()

        # Ensure party_id starts with fp-
        if not party_id.startswith("fp-"):
            party_id = f"fp-{party_id}"

        # Get logs for this party
        logs = party_logger.get_party_logs(party_id)

        # Get log file path
        log_file = party_logger._get_log_file_path(party_id)

        return {
            "success": True,
            "party_id": party_id,
            "log_file": str(log_file),
            "total_logs": len(logs),
            "logs": logs
        }

    except Exception as e:
        logger.error("Failed to get party logs", party_id=party_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve logs: {str(e)}")


@router.delete("/party/{party_id}/logs")
async def clear_party_logs(party_id: str):
    """
    Clear all logs for a specific party session.

    Example:
    ```
    DELETE /api/v1/event-driven/party/fp-2025A12345/logs
    ```
    """
    try:
        party_logger = get_party_logger()

        # Ensure party_id starts with fp-
        if not party_id.startswith("fp-"):
            party_id = f"fp-{party_id}"

        # Clear logs
        party_logger.clear_party_logs(party_id)

        return {
            "success": True,
            "message": f"Logs cleared for party {party_id}"
        }

    except Exception as e:
        logger.error("Failed to clear party logs", party_id=party_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to clear logs: {str(e)}")


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
