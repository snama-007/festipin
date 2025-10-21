"""
CakeAgent - Dynamic Agent

Searches for bakeries and provides cake recommendations based on theme and preferences.
Uses mock database for bakery search.

State Machine: IDLE → RUNNING → COMPLETED → IDLE
"""

import asyncio
import time
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


class CakeAgent:
    """
    Dynamic agent that searches for bakeries and recommends cakes.

    Triggers:
    - party.agent.should_execute with agent_name="cake_agent"

    Dependencies:
    - Uses ThemeAgent result if available (for themed cake designs)

    Output:
    - recommended_bakeries: List of bakery recommendations
    - cake_style: Recommended cake style
    - theme: Theme for cake design
    - decorations: Cake decoration suggestions
    - estimated_cost: Cost estimate
    """

    def __init__(self):
        self.agent_name = "cake_agent"
        self.event_bus = get_event_bus()
        self.state_store = get_state_store()
        self.mock_db = get_mock_database()
        self._running = False

        # Theme-specific cake decorations
        self.theme_decorations = {
            'jungle': ['animal figurines', 'leaf patterns', 'safari colors'],
            'space': ['planet toppers', 'star sprinkles', 'galaxy frosting'],
            'princess': ['crown topper', 'pink frosting', 'sparkles'],
            'superhero': ['superhero figurines', 'cityscape design', 'cape details'],
            'unicorn': ['unicorn horn', 'rainbow layers', 'magical sprinkles'],
            'dinosaur': ['dino topper', 'volcano design', 'prehistoric colors'],
            'ocean': ['mermaid topper', 'blue waves', 'seashell decorations'],
            'farm': ['barn cake', 'animal toppers', 'tractor design'],
        }

    async def start(self):
        """Start listening for execution requests"""
        if self._running:
            logger.warning(f"{self.agent_name} already running")
            return

        self._running = True
        logger.info(f"{self.agent_name} started (listening)")

        async for event in self.event_bus.subscribe("party.agent.should_execute"):
            if not self._running:
                break

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
        Execute bakery search and cake recommendations.

        Process:
        1. Get party state and inputs
        2. Extract theme from ThemeAgent
        3. Extract preferences (flavors, dietary restrictions)
        4. Query mock database for bakeries
        5. Generate cake decoration suggestions
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
            message="Searching for bakeries...",
            correlation_id=event.correlation_id
        )
        await self.event_bus.publish("party.agent.started", started_event)

        await self.state_store.set_agent_started(party_id, self.agent_name)

        try:
            # Get party state
            party_state = await self.state_store.get_party(party_id)
            if not party_state:
                raise ValueError(f"Party {party_id} not found")

            # Extract criteria
            theme = self._extract_theme(party_state)
            budget = self._extract_budget(party_state.inputs)
            preferences = self._extract_preferences(party_state.inputs)

            # Search bakeries and generate recommendations
            result = await self._search_bakeries(
                theme=theme,
                budget=budget,
                preferences=preferences
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
                bakeries_found=len(result.get('recommended_bakeries', [])),
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

    async def _search_bakeries(
        self,
        theme: Optional[str],
        budget: int,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Search for bakeries and generate cake recommendations.

        Args:
            theme: Party theme (from ThemeAgent)
            budget: Budget for cake
            preferences: User preferences (flavors, dietary)

        Returns:
            Bakery recommendations and cake details
        """
        # Query mock database for bakeries
        db_bakeries = self.mock_db.query_bakeries(
            max_budget=budget,
            custom_designs=True,
            limit=5
        )

        # RAG search with theme if available
        rag_bakeries = []
        if theme:
            rag_bakeries = self.mock_db.semantic_search_bakeries(
                query=f"{theme} birthday cake design custom bakery",
                k=3
            )

        # Combine and deduplicate
        all_bakeries = {b['id']: b for b in db_bakeries}
        for b in rag_bakeries:
            if b['id'] not in all_bakeries:
                all_bakeries[b['id']] = b

        # Sort by rating and custom design capability
        bakeries_list = list(all_bakeries.values())
        bakeries_list.sort(
            key=lambda b: (
                -b.get('rating', 0),
                -int(b.get('custom_designs', False))
            )
        )

        recommendations = bakeries_list[:3]

        # Get theme-specific decorations
        decorations = self.theme_decorations.get(
            theme if theme else 'general',
            ['basic decorations', 'colored frosting', 'birthday message']
        )

        # Determine cake style
        cake_style = "themed" if theme else "traditional"

        # Estimate size based on guest count (if available)
        size_recommendation = self._recommend_size(preferences.get('guest_count', 50))

        return {
            "recommended_bakeries": recommendations,
            "cake_style": cake_style,
            "theme": theme or "general",
            "decorations": decorations,
            "estimated_cost": {
                "min": 80,
                "max": min(budget, 300)
            },
            "size_recommendation": size_recommendation,
            "data_source": "mock_database"
        }

    def _extract_theme(self, party_state: Any) -> Optional[str]:
        """Extract theme from ThemeAgent result"""
        theme_result = party_state.get_agent_result('theme_agent')
        if theme_result and theme_result.status == 'completed':
            return theme_result.result.get('primary_theme')
        return None

    def _extract_budget(self, inputs: List[Any]) -> int:
        """Extract cake budget from inputs"""
        # Look for cake-specific budget mentions
        for inp in inputs:
            content = inp.content.lower()
            if 'cake' in content and '$' in content:
                # Try to extract dollar amount
                import re
                match = re.search(r'\$\s*(\d+)', content)
                if match:
                    try:
                        budget = int(match.group(1))
                        if 50 <= budget <= 1000:
                            return budget
                    except ValueError:
                        pass

        # Default cake budget
        return 200

    def _extract_preferences(self, inputs: List[Any]) -> Dict[str, Any]:
        """Extract cake preferences from inputs"""
        preferences = {
            'flavors': [],
            'dietary': [],
            'guest_count': 50
        }

        # Common flavor keywords
        flavor_keywords = ['chocolate', 'vanilla', 'strawberry', 'red velvet', 'lemon', 'carrot']
        dietary_keywords = ['vegan', 'gluten-free', 'dairy-free', 'nut-free']

        for inp in inputs:
            content = inp.content.lower()

            # Extract flavors
            for flavor in flavor_keywords:
                if flavor in content:
                    preferences['flavors'].append(flavor)

            # Extract dietary restrictions
            for dietary in dietary_keywords:
                if dietary in content or dietary.replace('-', ' ') in content:
                    preferences['dietary'].append(dietary)

            # Extract guest count
            import re
            match = re.search(r'(\d+)\s*(?:guests?|people)', content)
            if match:
                try:
                    preferences['guest_count'] = int(match.group(1))
                except ValueError:
                    pass

        return preferences

    def _recommend_size(self, guest_count: int) -> str:
        """Recommend cake size based on guest count"""
        if guest_count < 20:
            return "small"
        elif guest_count < 50:
            return "medium"
        else:
            return "large"


# Export
__all__ = ["CakeAgent"]
