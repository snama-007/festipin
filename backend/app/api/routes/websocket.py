"""
WebSocket Routes for Real-Time Agent Updates

Provides WebSocket connections for streaming agent orchestration progress
to the frontend in real-time.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import asyncio
import json
from datetime import datetime

from app.core.logging import logger


router = APIRouter()


class ConnectionManager:
    """
    Manages WebSocket connections for agent orchestration events.
    Multiple clients can subscribe to the same event_id.
    """

    def __init__(self):
        # event_id -> list of WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, event_id: str, websocket: WebSocket):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()

        if event_id not in self.active_connections:
            self.active_connections[event_id] = []

        self.active_connections[event_id].append(websocket)

        logger.info("WebSocket connected",
                   event_id=event_id,
                   total_connections=len(self.active_connections[event_id]))

        # Send initial connection message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "event_id": event_id,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def disconnect(self, event_id: str, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if event_id in self.active_connections:
            if websocket in self.active_connections[event_id]:
                self.active_connections[event_id].remove(websocket)

            # Clean up empty lists
            if not self.active_connections[event_id]:
                del self.active_connections[event_id]

            logger.info("WebSocket disconnected",
                       event_id=event_id,
                       remaining_connections=len(self.active_connections.get(event_id, [])))

    async def send_agent_update(self, event_id: str, data: dict):
        """
        Send update to all clients subscribed to this event.
        Used by orchestrator to broadcast agent progress.
        """
        if event_id not in self.active_connections:
            logger.warning("No WebSocket connections for event",
                          event_id=event_id)
            return

        # Add timestamp to all messages
        data["timestamp"] = datetime.utcnow().isoformat()

        # Send to all connected clients
        disconnected = []
        for connection in self.active_connections[event_id]:
            try:
                await connection.send_json(data)
            except Exception as e:
                logger.error("Failed to send WebSocket message",
                            event_id=event_id,
                            error=str(e))
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            await self.disconnect(event_id, connection)

    async def broadcast_message(self, event_id: str, message: str):
        """Broadcast a text message to all clients"""
        await self.send_agent_update(event_id, {
            "type": "message",
            "message": message
        })

    def get_connection_count(self, event_id: str) -> int:
        """Get number of active connections for an event"""
        return len(self.active_connections.get(event_id, []))


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/ws/orchestration/{event_id}")
async def websocket_orchestration_endpoint(websocket: WebSocket, event_id: str):
    """
    WebSocket endpoint for real-time orchestration updates.

    Frontend connects to: ws://localhost:9000/ws/orchestration/{event_id}

    Receives messages like:
    {
        "type": "agent_update",
        "agent": "theme_agent",
        "status": "running" | "completed" | "error",
        "result": {...},
        "message": "Analyzing party theme...",
        "timestamp": "2025-10-17T..."
    }
    """
    await manager.connect(event_id, websocket)

    try:
        # Keep connection alive and handle any incoming messages
        while True:
            # Receive messages from client (e.g., heartbeat, commands)
            data = await websocket.receive_text()

            # Handle client commands
            try:
                command = json.loads(data)

                if command.get("type") == "ping":
                    # Respond to heartbeat
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })

                elif command.get("type") == "status":
                    # Client requesting status update
                    from app.services.simple_orchestrator import get_orchestrator

                    orchestrator = get_orchestrator()
                    status = await orchestrator.get_workflow_status(event_id)

                    if status:
                        await websocket.send_json({
                            "type": "status_response",
                            "status": status,
                            "timestamp": datetime.utcnow().isoformat()
                        })

            except json.JSONDecodeError:
                logger.warning("Received non-JSON message from WebSocket",
                              event_id=event_id,
                              message=data)

    except WebSocketDisconnect:
        await manager.disconnect(event_id, websocket)
        logger.info("WebSocket client disconnected normally", event_id=event_id)

    except Exception as e:
        logger.error("WebSocket error",
                    event_id=event_id,
                    error=str(e))
        await manager.disconnect(event_id, websocket)


@router.get("/ws/orchestration/health")
async def websocket_health():
    """Health check for WebSocket service"""
    return {
        "status": "healthy",
        "service": "websocket",
        "active_events": len(manager.active_connections),
        "total_connections": sum(len(conns) for conns in manager.active_connections.values()),
        "timestamp": datetime.utcnow().isoformat()
    }


# Export manager for use by orchestrator
__all__ = ["router", "manager"]
