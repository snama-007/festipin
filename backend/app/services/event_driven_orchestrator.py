"""
Event-Driven Orchestrator

Coordinates the entire event-driven agent system.
Manages agent lifecycle and workflow execution.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from app.services.event_bus import get_event_bus
from app.services.party_state_store import get_state_store
from app.services.agents.input_analyzer_agent import InputAnalyzerAgent
from app.services.agents.final_planner_agent import FinalPlannerAgent
from app.services.agents.budget_agent import BudgetAgent
from app.services.agents.theme_agent import ThemeAgent
from app.services.agents.venue_agent import VenueAgent
from app.services.agents.cake_agent import CakeAgent
from app.services.websocket_bridge import get_websocket_bridge
from app.models.events import (
    create_input_added_event,
    create_input_removed_event,
)
from app.core.logging import logger


class EventDrivenOrchestrator:
    """
    Central orchestrator for event-driven agent system.

    Responsibilities:
    - Start/stop all agents
    - Create and manage party sessions
    - Handle input additions/removals
    - Coordinate event flow
    - Provide system status and metrics
    """

    def __init__(self):
        self.event_bus = get_event_bus()
        self.state_store = get_state_store()

        # Always-running agents
        self.input_analyzer = InputAnalyzerAgent()
        self.final_planner = FinalPlannerAgent()
        self.budget_agent = BudgetAgent()

        # Dynamic agents (listen for execution requests)
        self.theme_agent = ThemeAgent()
        self.venue_agent = VenueAgent()
        self.cake_agent = CakeAgent()

        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
        self._running = False

        logger.info("Event-driven orchestrator initialized")

    async def start(self):
        """
        Start the orchestrator and all agents.

        Starts:
        - InputAnalyzerAgent (always-running)
        - FinalPlannerAgent (always-running)
        - BudgetAgent (always-reactive)
        - ThemeAgent (dynamic listener)
        - VenueAgent (dynamic listener)
        - CakeAgent (dynamic listener)
        - WebSocketBridge (event → WebSocket forwarder)
        """
        if self._running:
            logger.warning("Orchestrator already running")
            return

        self._running = True
        logger.info("Starting event-driven orchestrator...")

        # Start WebSocket bridge
        await get_websocket_bridge()

        # Start all agents as background tasks
        self._background_tasks = [
            asyncio.create_task(self.input_analyzer.start(), name="InputAnalyzer"),
            asyncio.create_task(self.final_planner.start(), name="FinalPlanner"),
            asyncio.create_task(self.budget_agent.start(), name="BudgetAgent"),
            asyncio.create_task(self.theme_agent.start(), name="ThemeAgent"),
            asyncio.create_task(self.venue_agent.start(), name="VenueAgent"),
            asyncio.create_task(self.cake_agent.start(), name="CakeAgent"),
        ]

        logger.info(
            "Orchestrator started",
            background_tasks=len(self._background_tasks),
            agents=[
                "InputAnalyzer",
                "FinalPlanner",
                "BudgetAgent",
                "ThemeAgent",
                "VenueAgent",
                "CakeAgent",
                "WebSocketBridge"
            ]
        )

        # Wait a moment for agents to initialize
        await asyncio.sleep(0.5)

    async def stop(self):
        """Stop the orchestrator and all agents"""
        if not self._running:
            return

        logger.info("Stopping event-driven orchestrator...")

        self._running = False

        # Stop WebSocket bridge
        from app.services.websocket_bridge import shutdown_websocket_bridge
        await shutdown_websocket_bridge()

        # Stop all agents
        await self.input_analyzer.stop()
        await self.final_planner.stop()
        await self.budget_agent.stop()
        await self.theme_agent.stop()
        await self.venue_agent.stop()
        await self.cake_agent.stop()

        # Cancel background tasks
        for task in self._background_tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)

        # Shutdown event bus
        await self.event_bus.shutdown()

        logger.info("Orchestrator stopped")

    async def create_party(
        self,
        party_id: Optional[str] = None,
        initial_inputs: Optional[List[Dict[str, Any]]] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Create a new party planning session.

        Args:
            party_id: Optional party ID (auto-generated if not provided)
            initial_inputs: Optional list of initial inputs
            user_id: Optional user ID

        Returns:
            Party ID

        Raises:
            ValueError: If party_id already exists
        """
        # Generate party ID if not provided
        if not party_id:
            party_id = f"fp{datetime.now().year}{uuid.uuid4().hex[:8].upper()}"

        logger.info(
            "Creating party",
            party_id=party_id,
            initial_inputs=len(initial_inputs) if initial_inputs else 0,
            user_id=user_id
        )

        # Create party state
        await self.state_store.create_party(party_id, initial_inputs)

        # Emit input.added events for initial inputs
        if initial_inputs:
            for inp in initial_inputs:
                event = create_input_added_event(
                    party_id=party_id,
                    input_id=inp.get('input_id', f"inp_{uuid.uuid4().hex[:8]}"),
                    content=inp.get('content', ''),
                    source_type=inp.get('source_type', 'text'),
                    tags=inp.get('tags', []),
                    added_by=user_id or 'user'
                )

                await self.event_bus.publish("party.input.added", event)

        logger.info("Party created", party_id=party_id)

        return party_id

    async def add_input(
        self,
        party_id: str,
        content: str,
        source_type: str = "text",
        tags: Optional[List[str]] = None,
        added_by: str = "user",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add input to party.

        Args:
            party_id: Party identifier
            content: Input content
            source_type: Type of input (text, image, url, upload)
            tags: Optional tags
            added_by: User who added input
            metadata: Optional metadata

        Returns:
            Input ID

        Raises:
            ValueError: If party doesn't exist
        """
        # Verify party exists
        party_state = await self.state_store.get_party(party_id)
        if not party_state:
            raise ValueError(f"Party {party_id} not found")

        # Generate input ID
        input_id = f"inp_{uuid.uuid4().hex[:8]}"

        logger.info(
            "Adding input",
            party_id=party_id,
            input_id=input_id,
            content_preview=content[:50]
        )

        # Add to state
        await self.state_store.add_input(
            party_id=party_id,
            input_data={
                "input_id": input_id,
                "content": content,
                "source_type": source_type,
                "tags": tags or [],
                "added_by": added_by,
                "metadata": metadata or {}
            }
        )

        # Emit event
        event = create_input_added_event(
            party_id=party_id,
            input_id=input_id,
            content=content,
            source_type=source_type,
            tags=tags or [],
            added_by=added_by
        )

        await self.event_bus.publish("party.input.added", event)

        logger.info("Input added", party_id=party_id, input_id=input_id)

        return input_id

    async def remove_input(
        self,
        party_id: str,
        input_id: str,
        removed_by: str = "user"
    ) -> bool:
        """
        Remove input from party.

        Args:
            party_id: Party identifier
            input_id: Input identifier
            removed_by: User who removed input

        Returns:
            True if removed, False if not found

        Raises:
            ValueError: If party doesn't exist
        """
        # Verify party exists
        party_state = await self.state_store.get_party(party_id)
        if not party_state:
            raise ValueError(f"Party {party_id} not found")

        logger.info(
            "Removing input",
            party_id=party_id,
            input_id=input_id
        )

        # Remove from state
        removed = await self.state_store.remove_input(party_id, input_id)

        if removed:
            # Emit event
            event = create_input_removed_event(
                party_id=party_id,
                input_id=input_id,
                removed_by=removed_by
            )

            await self.event_bus.publish("party.input.removed", event)

            logger.info("Input removed", party_id=party_id, input_id=input_id)

        return removed

    async def get_party_status(self, party_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of party planning session.

        Args:
            party_id: Party identifier

        Returns:
            Party status dictionary or None if not found
        """
        party_state = await self.state_store.get_party(party_id)
        if not party_state:
            return None

        return {
            "party_id": party_id,
            "status": party_state.status,
            "inputs": [
                {
                    "input_id": inp.input_id,
                    "content": inp.content,
                    "source_type": inp.source_type,
                    "tags": inp.tags,
                    "added_at": inp.added_at
                }
                for inp in party_state.inputs
            ],
            "agents": {
                agent_name: {
                    "status": result.status,
                    "confidence": result.confidence,
                    "execution_time_ms": result.execution_time_ms,
                    "result_summary": self._summarize_result(agent_name, result.result)
                }
                for agent_name, result in party_state.active_agents.items()
            },
            "budget": party_state.budget,
            "final_plan": party_state.final_plan,
            "created_at": party_state.created_at,
            "updated_at": party_state.updated_at,
            "version": party_state.version
        }

    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "orchestrator": {
                "running": self._running,
                "background_tasks": len(self._background_tasks),
                "active_tasks": sum(1 for t in self._background_tasks if not t.done())
            },
            "event_bus": self.event_bus.get_metrics(),
            "state_store": self.state_store.get_stats(),
            "agents": {
                "input_analyzer": self.input_analyzer._running,
                "final_planner": self.final_planner._running,
                "budget_agent": self.budget_agent._running,
                "theme_agent": self.theme_agent._running,
                "venue_agent": self.venue_agent._running,
                "cake_agent": self.cake_agent._running,
            }
        }

    def _summarize_result(self, agent_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Create brief summary of agent result for status endpoint"""
        if agent_name == "theme_agent":
            return {
                "theme": result.get("primary_theme"),
                "confidence": result.get("confidence"),
                "colors": result.get("colors", [])[:3]
            }
        elif agent_name == "venue_agent":
            venues = result.get("recommended_venues", [])
            return {
                "venue_count": len(venues),
                "top_venue": venues[0].get("name") if venues else None
            }
        elif agent_name == "cake_agent":
            bakeries = result.get("recommended_bakeries", [])
            return {
                "bakery_count": len(bakeries),
                "estimated_cost": result.get("estimated_cost")
            }
        else:
            return {"has_result": True}


# Global orchestrator instance
_orchestrator: Optional[EventDrivenOrchestrator] = None


async def get_orchestrator() -> EventDrivenOrchestrator:
    """
    Get global orchestrator instance (singleton pattern).
    Automatically starts orchestrator if not running.

    Returns:
        Global EventDrivenOrchestrator instance
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = EventDrivenOrchestrator()
        await _orchestrator.start()
    elif not _orchestrator._running:
        await _orchestrator.start()

    return _orchestrator


async def shutdown_orchestrator():
    """Shutdown global orchestrator"""
    global _orchestrator
    if _orchestrator:
        await _orchestrator.stop()
        _orchestrator = None


# Export
__all__ = [
    "EventDrivenOrchestrator",
    "get_orchestrator",
    "shutdown_orchestrator",
]
