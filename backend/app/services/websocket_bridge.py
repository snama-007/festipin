"""
WebSocket Bridge

Bridges the event bus to WebSocket connections.
Listens to events and broadcasts them to connected clients.
"""

import asyncio
from typing import Dict, Any

from app.services.event_bus import get_event_bus
from app.models.events import WebSocketMessage
from app.core.logging import logger


class WebSocketBridge:
    """
    Bridges event bus events to WebSocket connections.

    Listens to all relevant events and forwards them to WebSocket manager.
    """

    def __init__(self):
        self.event_bus = get_event_bus()
        self._running = False
        self._tasks = []

    async def start(self):
        """Start the WebSocket bridge"""
        if self._running:
            logger.warning("WebSocket bridge already running")
            return

        self._running = True
        logger.info("WebSocket bridge starting...")

        # Import here to avoid circular imports
        from app.api.routes.websocket import manager

        # Start listeners for each event type
        self._tasks = [
            asyncio.create_task(
                self._forward_events("party.agent.started", manager, "agent_started")
            ),
            asyncio.create_task(
                self._forward_events("party.agent.completed", manager, "agent_completed")
            ),
            asyncio.create_task(
                self._forward_events("party.agent.failed", manager, "agent_failed")
            ),
            asyncio.create_task(
                self._forward_events("party.budget.updated", manager, "budget_updated")
            ),
            asyncio.create_task(
                self._forward_events("party.plan.updated", manager, "plan_updated")
            ),
        ]

        logger.info("WebSocket bridge started", listeners=len(self._tasks))

    async def stop(self):
        """Stop the WebSocket bridge"""
        if not self._running:
            return

        logger.info("WebSocket bridge stopping...")

        self._running = False

        # Cancel all tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()

        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

        logger.info("WebSocket bridge stopped")

    async def _forward_events(self, topic: str, manager, message_type: str):
        """
        Forward events from event bus to WebSocket manager.

        Args:
            topic: Event bus topic to subscribe to
            manager: WebSocket connection manager
            message_type: Type of message for frontend
        """
        logger.info(f"WebSocket bridge listening to {topic}")

        try:
            async for event in self.event_bus.subscribe(topic):
                if not self._running:
                    break

                try:
                    # Convert event to WebSocket message
                    ws_message = self._convert_to_websocket_message(event, message_type)

                    # Send to all clients for this party
                    await manager.send_agent_update(event.party_id, ws_message.model_dump())

                    logger.debug(
                        "Event forwarded to WebSocket",
                        party_id=event.party_id,
                        type=message_type
                    )

                except Exception as e:
                    logger.error(
                        "Failed to forward event to WebSocket",
                        topic=topic,
                        event_id=event.event_id,
                        error=str(e)
                    )

        except Exception as e:
            logger.error(f"WebSocket bridge error for {topic}", error=str(e))

    def _convert_to_websocket_message(self, event: Any, message_type: str) -> WebSocketMessage:
        """
        Convert event bus event to WebSocket message.

        Args:
            event: Event from event bus
            message_type: Type of WebSocket message

        Returns:
            WebSocketMessage for frontend
        """
        payload = event.payload

        # Base message
        message = WebSocketMessage(
            type=message_type,
            timestamp=event.timestamp
        )

        # Add type-specific fields
        if message_type == "agent_started":
            message.agent = payload.agent_name
            message.status = "running"
            message.message = payload.message or f"{payload.agent_name} started"

        elif message_type == "agent_completed":
            message.agent = payload.agent_name
            message.status = "completed"
            message.result = payload.result
            message.message = f"{payload.agent_name} completed successfully"

        elif message_type == "agent_failed":
            message.agent = payload.agent_name
            message.status = "failed"
            message.error = payload.error
            message.message = f"{payload.agent_name} failed: {payload.error}"

        elif message_type == "budget_updated":
            message.payload = {
                "total_budget": payload.total_budget.model_dump(),
                "breakdown": {
                    k: v.model_dump() for k, v in payload.breakdown.items()
                },
                "based_on_agents": payload.based_on_agents
            }
            message.message = "Budget updated"

        elif message_type == "plan_updated":
            message.payload = {
                "completion_percent": payload.completion_percent,
                "recommendations": [r.model_dump() for r in payload.recommendations],
                "next_steps": payload.next_steps,
                "active_agents": payload.active_agents,
                "missing_agents": payload.missing_agents
            }
            message.message = f"Plan updated ({payload.completion_percent}% complete)"

        return message


# Global bridge instance
_bridge: WebSocketBridge = None


async def get_websocket_bridge() -> WebSocketBridge:
    """Get global WebSocket bridge instance"""
    global _bridge
    if _bridge is None:
        _bridge = WebSocketBridge()
        await _bridge.start()
    elif not _bridge._running:
        await _bridge.start()

    return _bridge


async def shutdown_websocket_bridge():
    """Shutdown WebSocket bridge"""
    global _bridge
    if _bridge:
        await _bridge.stop()
        _bridge = None


# Export
__all__ = [
    "WebSocketBridge",
    "get_websocket_bridge",
    "shutdown_websocket_bridge",
]
