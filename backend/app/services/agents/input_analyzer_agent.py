"""
InputAnalyzer Agent - Always-Running

Continuously listens to input events and classifies them.
Determines which agents should execute based on input content.

This agent runs 24/7 as a background task.
"""

import asyncio
from typing import Dict, List, Set, Optional, Any
import re

from app.services.event_bus import get_event_bus
from app.services.party_state_store import get_state_store
from app.services.keyword_expansions import get_expanded_routing_rules
from app.models.events import (
    InputAddedEvent,
    InputRemovedEvent,
    create_agent_should_execute_event,
    AgentDataRemovedEvent,
    AgentDataRemovedPayload,
)
from app.core.logging import logger


class InputAnalyzerAgent:
    """
    Always-running agent that analyzes inputs in real-time.

    Responsibilities:
    - Classify inputs (theme, cake, venue, etc.)
    - Determine which agents need to run
    - Emit agent execution events with priorities
    - Handle input removal and cascade effects
    """

    def __init__(self):
        self.event_bus = get_event_bus()
        self.state_store = get_state_store()

        # Routing rules: category -> keywords (expanded with theme variations and synonyms)
        self.routing_rules = get_expanded_routing_rules()

        logger.debug(
            "InputAnalyzer initialized with expanded keywords",
            theme_keywords_count=len(self.routing_rules.get('theme', [])),
            total_categories=len(self.routing_rules)
        )

        # Agent dependency graph (which agents depend on which)
        self.agent_dependencies = {
            'theme': {
                'affects': ['cake', 'venue', 'vendor'],  # These agents should rerun if theme changes
                'priority': 1  # Highest priority (runs first)
            },
            'venue': {
                'affects': ['catering', 'budget'],
                'priority': 2
            },
            'cake': {
                'affects': ['budget'],
                'priority': 2
            },
            'catering': {
                'affects': ['budget'],
                'priority': 3
            },
            'vendor': {
                'affects': ['budget'],
                'priority': 3
            },
        }

        self._running = False

    async def start(self):
        """
        Start the always-running agent.
        Subscribes to input events and processes them continuously.
        """
        if self._running:
            logger.warning("InputAnalyzer already running")
            return

        self._running = True
        logger.info("InputAnalyzer agent starting...")

        # Start two background tasks (one for each event type)
        tasks = [
            asyncio.create_task(self._listen_input_added()),
            asyncio.create_task(self._listen_input_removed()),
        ]

        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error("InputAnalyzer agent error", error=str(e))
            self._running = False
            raise

    async def stop(self):
        """Stop the agent"""
        self._running = False
        logger.info("InputAnalyzer agent stopped")

    async def _listen_input_added(self):
        """Listen to party.input.added events"""
        logger.info("InputAnalyzer: Listening to party.input.added")

        async for event in self.event_bus.subscribe("party.input.added"):
            if not self._running:
                break

            try:
                await self._handle_input_added(event)
            except Exception as e:
                logger.error(
                    "Error handling input_added event",
                    event_id=event.event_id,
                    error=str(e)
                )

    async def _listen_input_removed(self):
        """Listen to party.input.removed events"""
        logger.info("InputAnalyzer: Listening to party.input.removed")

        async for event in self.event_bus.subscribe("party.input.removed"):
            if not self._running:
                break

            try:
                await self._handle_input_removed(event)
            except Exception as e:
                logger.error(
                    "Error handling input_removed event",
                    event_id=event.event_id,
                    error=str(e)
                )

    async def _handle_input_added(self, event: InputAddedEvent):
        """
        Handle new input being added.

        Process:
        1. Classify input (determine categories)
        2. Get current party state
        3. Create execution plan (which agents to trigger)
        4. Emit agent execution events
        """
        party_id = event.party_id
        payload = event.payload

        logger.info(
            "InputAnalyzer: Processing new input",
            party_id=party_id,
            input_id=payload.input_id,
            content_preview=payload.content[:50]
        )

        # 1. Classify input (with metadata for vision/LLM context)
        classification = self._classify_input(
            payload.content,
            payload.tags,
            payload.metadata
        )

        logger.debug(
            "Input classified",
            party_id=party_id,
            input_id=payload.input_id,
            categories=list(classification.keys()),
            has_vision_context=bool(payload.metadata and payload.metadata.get("agent_context"))
        )

        # 2. Get party state
        party_state = await self.state_store.get_party(party_id)
        if not party_state:
            logger.error("Party not found", party_id=party_id)
            return

        # 3. Create execution plan
        execution_plan = self._create_execution_plan(
            classification,
            party_state.get_completed_agents(),
            party_state.get_running_agents()
        )

        logger.info(
            "Execution plan created",
            party_id=party_id,
            agents_to_execute=len(execution_plan)
        )

        # 4. Emit agent execution events (in priority order)
        for plan_item in sorted(execution_plan, key=lambda x: x['priority']):
            agent_event = create_agent_should_execute_event(
                party_id=party_id,
                agent_name=plan_item['agent'],
                execution_type=plan_item['type'],
                input_ids=[payload.input_id],
                priority=plan_item['priority'],
                correlation_id=event.correlation_id
            )

            await self.event_bus.publish("party.agent.should_execute", agent_event)

            logger.debug(
                "Agent execution triggered",
                party_id=party_id,
                agent=plan_item['agent'],
                type=plan_item['type'],
                priority=plan_item['priority']
            )

    async def _handle_input_removed(self, event: InputRemovedEvent):
        """
        Handle input being removed.

        Process:
        1. Check which agents were using this input
        2. Check if agents still have other inputs
        3. If no inputs remain for agent → emit data_removed event
        4. If inputs remain → trigger agent rerun
        """
        party_id = event.party_id
        payload = event.payload
        input_id = payload.input_id

        logger.info(
            "InputAnalyzer: Processing input removal",
            party_id=party_id,
            input_id=input_id
        )

        # Get party state
        party_state = await self.state_store.get_party(party_id)
        if not party_state:
            logger.error("Party not found", party_id=party_id)
            return

        # Get removed input to know its classification
        # Note: In production, we'd need to track input->agent mappings
        # For now, we'll re-classify all remaining inputs

        # Classify all remaining inputs
        all_classifications: Dict[str, List] = {}
        for inp in party_state.inputs:
            classification = self._classify_input(inp.content, inp.tags, inp.metadata)
            for category, score in classification.items():
                if category not in all_classifications:
                    all_classifications[category] = []
                all_classifications[category].append(inp.input_id)

        # Check each agent to see if it should be removed or re-run
        for agent_name in ['theme_agent', 'venue_agent', 'cake_agent']:
            category = agent_name.replace('_agent', '')

            # Check if agent still has inputs
            still_has_inputs = category in all_classifications and len(all_classifications[category]) > 0

            # Check if agent has results
            has_results = agent_name in party_state.active_agents

            if not still_has_inputs and has_results:
                # Remove agent data
                data_removed_event = AgentDataRemovedEvent(
                    party_id=party_id,
                    payload=AgentDataRemovedPayload(
                        agent_name=agent_name,
                        reason="no_relevant_inputs",
                        removed_input_id=input_id
                    )
                )

                await self.event_bus.publish("party.agent.data_removed", data_removed_event)

                logger.info(
                    "Agent data removal triggered",
                    party_id=party_id,
                    agent=agent_name,
                    reason="no_relevant_inputs"
                )

            elif still_has_inputs and has_results:
                # Re-run agent with remaining inputs
                rerun_event = create_agent_should_execute_event(
                    party_id=party_id,
                    agent_name=agent_name,
                    execution_type="rerun",
                    input_ids=all_classifications[category],
                    priority=self.agent_dependencies.get(category, {}).get('priority', 3),
                    correlation_id=event.correlation_id
                )

                await self.event_bus.publish("party.agent.should_execute", rerun_event)

                logger.info(
                    "Agent rerun triggered",
                    party_id=party_id,
                    agent=agent_name,
                    reason="input_removed_revalidate"
                )

    def _classify_input(
        self,
        content: str,
        tags: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """
        Classify input into categories based on keywords.
        Enhanced to utilize vision context and LLM agent instructions.

        Args:
            content: Input text content (may include vision description)
            tags: Pre-assigned tags (may include vision-derived tags)
            metadata: Optional metadata with agent_context from vision/LLM

        Returns:
            Dictionary of category -> score (higher = better match)
        """
        content_lower = content.lower()
        classification: Dict[str, float] = {}

        # Check content against routing rules
        for category, keywords in self.routing_rules.items():
            score = 0.0

            # Check content for keywords
            for keyword in keywords:
                if keyword in content_lower:
                    score += 2.0

            # Check tags for keywords
            for tag in tags:
                tag_lower = tag.lower()
                for keyword in keywords:
                    if keyword in tag_lower:
                        score += 3.0

            if score > 0:
                classification[category] = score

        # NEW: Boost scores based on vision analysis or LLM agent instructions
        if metadata:
            agent_context = metadata.get("agent_context", {})

            # If agent_context has specific agent instructions, boost those agents
            for agent_key in agent_context.keys():
                # Extract category from agent_key (e.g., "theme_agent" -> "theme")
                category = agent_key.replace("_agent", "")
                if category in classification:
                    classification[category] += 5.0  # Boost from vision/LLM
                    logger.debug(
                        "Boosted agent from vision/LLM context",
                        category=category,
                        new_score=classification[category]
                    )
                else:
                    classification[category] = 5.0  # Add if not already present
                    logger.debug(
                        "Added agent from vision/LLM context",
                        category=category
                    )

        # Always include theme if no classification
        if not classification:
            classification['theme'] = 1.0

        return classification

    def _create_execution_plan(
        self,
        classification: Dict[str, float],
        completed_agents: List[str],
        running_agents: List[str]
    ) -> List[Dict]:
        """
        Create execution plan based on classification and current agent states.

        Args:
            classification: Categories with scores
            completed_agents: List of agents that have already completed
            running_agents: List of agents currently running

        Returns:
            List of plan items with agent, type, and priority
        """
        plan = []

        for category, score in classification.items():
            agent_name = f"{category}_agent"

            # Skip if agent is already running
            if agent_name in running_agents:
                logger.debug(
                    "Agent already running, skipping",
                    agent=agent_name
                )
                continue

            # Determine execution type
            if agent_name in completed_agents:
                execution_type = "rerun"
            else:
                execution_type = "start"

            # Get priority from dependencies
            priority = self.agent_dependencies.get(category, {}).get('priority', 3)

            plan.append({
                'agent': agent_name,
                'type': execution_type,
                'priority': priority,
                'score': score
            })

            # Also trigger dependent agents if this is a rerun
            if execution_type == "rerun":
                affected_agents = self.agent_dependencies.get(category, {}).get('affects', [])
                for affected_category in affected_agents:
                    affected_agent = f"{affected_category}_agent"

                    if affected_agent in completed_agents and affected_agent not in running_agents:
                        plan.append({
                            'agent': affected_agent,
                            'type': 'recalculate',
                            'priority': self.agent_dependencies.get(affected_category, {}).get('priority', 4),
                            'score': 0.0
                        })

        return plan


# Export
__all__ = ["InputAnalyzerAgent"]
