"""
VenueAgent - Dynamic Agent

Searches for party venues based on guest count, budget, and theme.
Uses mock database for venue recommendations.

State Machine: IDLE → RUNNING → COMPLETED → IDLE
"""

import asyncio
import time
import re
from typing import Dict, List, Any, Optional
import uuid

from app.services.event_bus import get_event_bus
from app.services.party_state_store import get_state_store
from app.services.mock_database import get_mock_database
from app.models.events import (
    AgentShouldExecuteEvent,
    create_agent_started_event,
    create_agent_completed_event,
    create_agent_failed_event,
)
from app.core.logging import logger


class VenueAgent:
    """
    Dynamic agent that searches for party venues.

    Triggers:
    - party.agent.should_execute with agent_name="venue_agent"

    Dependencies:
    - Uses ThemeAgent result if available (for theme matching)

    Output:
    - recommended_venues: List of venue recommendations
    - total_matches: Total number of venues found
    - search_criteria: Criteria used for search
    """

    def __init__(self):
        self.agent_name = "venue_agent"
        self.event_bus = get_event_bus()
        self.state_store = get_state_store()
        self.mock_db = get_mock_database()
        self._running = False

    async def start(self):
        """
        Start listening for execution requests.
        """
        if self._running:
            logger.warning(f"{self.agent_name} already running")
            return

        self._running = True
        logger.info(f"{self.agent_name} started (listening)")

        # Listen for execution requests
        async for event in self.event_bus.subscribe("party.agent.should_execute"):
            if not self._running:
                break

            # Check if this event is for us
            if event.payload.agent_name != self.agent_name:
                continue

            try:
                await self._execute(event)
            except Exception as e:
                logger.error(
                    f"{self.agent_name} execution error",
                    event_id=event.event_id,
                    error=str(e)
                )

    async def stop(self):
        """Stop the agent"""
        self._running = False
        logger.info(f"{self.agent_name} stopped")

    async def _execute(self, event: AgentShouldExecuteEvent):
        """
        Execute venue search.

        Process:
        1. Get party state and inputs
        2. Extract guest count and location preferences
        3. Get theme from ThemeAgent if available
        4. Query mock database for venues
        5. Rank and filter results
        6. Emit completion event
        """
        party_id = event.party_id
        execution_id = f"exec_{uuid.uuid4().hex[:12]}"
        start_time = time.time()

        logger.info(
            f"{self.agent_name} executing",
            party_id=party_id,
            execution_id=execution_id
        )

        # Emit started event
        started_event = create_agent_started_event(
            party_id=party_id,
            agent_name=self.agent_name,
            execution_id=execution_id,
            message="Searching for venues...",
            correlation_id=event.correlation_id
        )
        await self.event_bus.publish("party.agent.started", started_event)

        # Mark agent as running
        await self.state_store.set_agent_started(party_id, self.agent_name)

        try:
            # Get party state
            party_state = await self.state_store.get_party(party_id)
            if not party_state:
                raise ValueError(f"Party {party_id} not found")

            # Extract search criteria
            guest_count = self._extract_guest_count(party_state.inputs)
            budget = self._extract_budget(party_state)
            theme = self._extract_theme(party_state)
            location_pref = self._extract_location(party_state.inputs)

            # Search venues
            result = await self._search_venues(
                guest_count=guest_count,
                budget=budget,
                theme=theme,
                location_pref=location_pref
            )

            # Calculate execution time
            execution_time_ms = (time.time() - start_time) * 1000

            # Store result
            await self.state_store.set_agent_result(
                party_id=party_id,
                agent_name=self.agent_name,
                result=result,
                confidence=0.85,
                execution_time_ms=execution_time_ms,
                status="completed"
            )

            # Emit completed event
            completed_event = create_agent_completed_event(
                party_id=party_id,
                agent_name=self.agent_name,
                execution_id=execution_id,
                result=result,
                confidence=0.85,
                execution_time_ms=execution_time_ms,
                correlation_id=event.correlation_id
            )
            await self.event_bus.publish("party.agent.completed", completed_event)

            logger.info(
                f"{self.agent_name} completed",
                party_id=party_id,
                venues_found=result['total_matches'],
                execution_time_ms=execution_time_ms
            )

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000

            await self.state_store.set_agent_failed(
                party_id=party_id,
                agent_name=self.agent_name,
                error=str(e)
            )

            failed_event = create_agent_failed_event(
                party_id=party_id,
                agent_name=self.agent_name,
                execution_id=execution_id,
                error=str(e),
                correlation_id=event.correlation_id
            )
            await self.event_bus.publish("party.agent.failed", failed_event)

            logger.error(f"{self.agent_name} failed", party_id=party_id, error=str(e))

    async def _search_venues(
        self,
        guest_count: int,
        budget: int,
        theme: Optional[str],
        location_pref: Optional[str]
    ) -> Dict[str, Any]:
        """
        Search for venues using mock database.

        Args:
            guest_count: Number of guests
            budget: Maximum budget
            theme: Party theme (if known)
            location_pref: Location preference

        Returns:
            Venue search results
        """
        # Query mock PostgreSQL
        db_venues = self.mock_db.query_venues(
            min_capacity=guest_count,
            max_price=budget,
            limit=5
        )

        # Query mock RAG (vector search) if theme is known
        rag_venues = []
        if theme:
            rag_venues = self.mock_db.semantic_search_venues(
                query=f"{theme} party venue for {guest_count} guests",
                k=3
            )

        # Combine and deduplicate results
        all_venues = {v['id']: v for v in db_venues}
        for v in rag_venues:
            if v['id'] not in all_venues:
                all_venues[v['id']] = v

        # Sort by rating and capacity match
        venues_list = list(all_venues.values())
        venues_list.sort(
            key=lambda v: (
                -v.get('rating', 0),  # Higher rating first
                -abs(v.get('capacity', 0) - guest_count)  # Closer capacity match
            )
        )

        # Take top 3
        recommendations = venues_list[:3]

        return {
            "recommended_venues": recommendations,
            "total_matches": len(all_venues),
            "search_criteria": {
                "guest_count": guest_count,
                "budget": budget,
                "theme": theme,
                "location": location_pref
            },
            "data_source": "mock_database"
        }

    def _extract_guest_count(self, inputs: List[Any]) -> int:
        """Extract guest count from inputs"""
        for inp in inputs:
            content = inp.content.lower()

            # Look for patterns like "75 guests", "50 people", etc.
            patterns = [
                r'(\d+)\s*(?:guests?|people|persons?|attendees?)',
                r'(?:for|inviting)\s*(\d+)',
            ]

            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    try:
                        count = int(match.group(1))
                        if 5 <= count <= 500:  # Reasonable range
                            logger.debug(f"Extracted guest count: {count}")
                            return count
                    except ValueError:
                        continue

        # Default guest count
        return 50

    def _extract_budget(self, party_state: Any) -> int:
        """Extract budget from budget agent or default"""
        if party_state.budget:
            total_budget = party_state.budget.get('total_budget', {})
            max_budget = total_budget.get('max', 1000)
            return max_budget

        # Default budget
        return 1000

    def _extract_theme(self, party_state: Any) -> Optional[str]:
        """Extract theme from ThemeAgent result"""
        theme_result = party_state.get_agent_result('theme_agent')
        if theme_result and theme_result.status == 'completed':
            return theme_result.result.get('primary_theme')
        return None

    def _extract_location(self, inputs: List[Any]) -> Optional[str]:
        """Extract location preference from inputs"""
        location_keywords = ['downtown', 'outdoor', 'indoor', 'park', 'hall', 'home']

        for inp in inputs:
            content = inp.content.lower()
            for keyword in location_keywords:
                if keyword in content:
                    return keyword

        return None


# Export
__all__ = ["VenueAgent"]
