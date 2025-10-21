"""
ThemeAgent - Dynamic Agent

Detects party theme from user inputs.
Starts/stops on demand based on input events.

State Machine: IDLE → RUNNING → COMPLETED → IDLE
"""

import asyncio
import time
from typing import Dict, List, Any
import uuid

from app.services.event_bus import get_event_bus
from app.services.party_state_store import get_state_store
from app.models.events import (
    AgentShouldExecuteEvent,
    create_agent_started_event,
    create_agent_completed_event,
    create_agent_failed_event,
)
from app.core.logging import logger


class ThemeAgent:
    """
    Dynamic agent that detects party themes.

    Triggers:
    - party.agent.should_execute with agent_name="theme_agent"

    Output:
    - primary_theme: Detected theme name
    - confidence: Confidence score (0.0-1.0)
    - colors: List of theme colors
    - decorations: List of decoration suggestions
    - activities: List of activity suggestions
    """

    def __init__(self):
        self.agent_name = "theme_agent"
        self.event_bus = get_event_bus()
        self.state_store = get_state_store()
        self._running = False

        # Theme detection rules
        self.theme_keywords = {
            'jungle': ['jungle', 'safari', 'animal', 'wild', 'nature', 'zoo'],
            'space': ['space', 'astronaut', 'galaxy', 'planet', 'rocket', 'star'],
            'princess': ['princess', 'castle', 'royal', 'crown', 'magic', 'fairy'],
            'superhero': ['superhero', 'batman', 'spiderman', 'superman', 'hero', 'marvel'],
            'unicorn': ['unicorn', 'rainbow', 'magical', 'sparkle', 'fairy', 'glitter'],
            'dinosaur': ['dinosaur', 'dino', 'prehistoric', 'fossil', 'jurassic', 't-rex'],
            'ocean': ['ocean', 'sea', 'mermaid', 'fish', 'underwater', 'beach'],
            'farm': ['farm', 'barn', 'tractor', 'cow', 'pig', 'farmer'],
        }

        # Theme attributes
        self.theme_colors = {
            'jungle': ['green', 'brown', 'yellow', 'orange'],
            'space': ['blue', 'purple', 'silver', 'black'],
            'princess': ['pink', 'purple', 'gold', 'white'],
            'superhero': ['red', 'blue', 'yellow', 'black'],
            'unicorn': ['pink', 'purple', 'rainbow', 'white'],
            'dinosaur': ['green', 'brown', 'orange', 'yellow'],
            'ocean': ['blue', 'teal', 'white', 'aqua'],
            'farm': ['red', 'yellow', 'green', 'brown'],
        }

        self.theme_decorations = {
            'jungle': ['animal balloons', 'leaf garlands', 'safari props', 'vine decorations'],
            'space': ['planet decorations', 'star lights', 'rocket props', 'galaxy backdrop'],
            'princess': ['crowns', 'castle backdrop', 'magic wands', 'tulle draping'],
            'superhero': ['capes', 'masks', 'cityscape backdrop', 'comic book decorations'],
            'unicorn': ['unicorn horns', 'rainbow streamers', 'sparkles', 'cloud decorations'],
            'dinosaur': ['dino balloons', 'fossil props', 'volcano backdrop', 'jungle plants'],
            'ocean': ['fish decorations', 'seaweed', 'treasure chest', 'bubble machines'],
            'farm': ['hay bales', 'barn decorations', 'animal cutouts', 'red checkered tablecloths'],
        }

        self.theme_activities = {
            'jungle': ['animal charades', 'safari hunt', 'jungle obstacle course'],
            'space': ['planet making', 'rocket building', 'space exploration game'],
            'princess': ['crown decorating', 'castle building', 'royal tea party'],
            'superhero': ['cape decorating', 'superhero training', 'city rescue game'],
            'unicorn': ['horn making', 'rainbow crafts', 'magical story time'],
            'dinosaur': ['fossil digging', 'dino dance', 'prehistoric crafts'],
            'ocean': ['fish craft', 'treasure hunt', 'underwater dance'],
            'farm': ['animal feeding game', 'tractor races', 'farm crafts'],
        }

    async def start(self):
        """
        Start listening for execution requests.
        This agent processes requests on-demand.
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
        Execute theme detection.

        Process:
        1. Get party state and inputs
        2. Analyze inputs for theme keywords
        3. Score each theme
        4. Select primary theme
        5. Generate theme details (colors, decorations, activities)
        6. Emit completion event
        """
        party_id = event.party_id
        execution_id = f"exec_{uuid.uuid4().hex[:12]}"
        start_time = time.time()

        logger.info(
            f"{self.agent_name} executing",
            party_id=party_id,
            execution_id=execution_id,
            execution_type=event.payload.execution_type
        )

        # Emit started event
        started_event = create_agent_started_event(
            party_id=party_id,
            agent_name=self.agent_name,
            execution_id=execution_id,
            message="Analyzing party theme...",
            correlation_id=event.correlation_id
        )
        await self.event_bus.publish("party.agent.started", started_event)

        # Mark agent as running in state
        await self.state_store.set_agent_started(party_id, self.agent_name)

        try:
            # Get party state
            party_state = await self.state_store.get_party(party_id)
            if not party_state:
                raise ValueError(f"Party {party_id} not found")

            # Get all inputs
            inputs = party_state.inputs

            # Analyze theme
            result = await self._analyze_theme(inputs)

            # Calculate execution time
            execution_time_ms = (time.time() - start_time) * 1000

            # Store result in state
            await self.state_store.set_agent_result(
                party_id=party_id,
                agent_name=self.agent_name,
                result=result,
                confidence=result['confidence'],
                execution_time_ms=execution_time_ms,
                status="completed"
            )

            # Emit completed event
            completed_event = create_agent_completed_event(
                party_id=party_id,
                agent_name=self.agent_name,
                execution_id=execution_id,
                result=result,
                confidence=result['confidence'],
                execution_time_ms=execution_time_ms,
                correlation_id=event.correlation_id
            )
            await self.event_bus.publish("party.agent.completed", completed_event)

            logger.info(
                f"{self.agent_name} completed",
                party_id=party_id,
                execution_id=execution_id,
                theme=result['primary_theme'],
                confidence=result['confidence'],
                execution_time_ms=execution_time_ms
            )

        except Exception as e:
            # Calculate execution time
            execution_time_ms = (time.time() - start_time) * 1000

            # Mark as failed in state
            await self.state_store.set_agent_failed(
                party_id=party_id,
                agent_name=self.agent_name,
                error=str(e)
            )

            # Emit failed event
            failed_event = create_agent_failed_event(
                party_id=party_id,
                agent_name=self.agent_name,
                execution_id=execution_id,
                error=str(e),
                error_type="internal",
                correlation_id=event.correlation_id
            )
            await self.event_bus.publish("party.agent.failed", failed_event)

            logger.error(
                f"{self.agent_name} failed",
                party_id=party_id,
                execution_id=execution_id,
                error=str(e)
            )

    async def _analyze_theme(self, inputs: List[Any]) -> Dict[str, Any]:
        """
        Analyze inputs to detect theme.

        Args:
            inputs: List of PartyInput objects

        Returns:
            Theme analysis result
        """
        theme_scores = {}

        # Score each theme based on input content
        for inp in inputs:
            content = inp.content.lower()
            tags = [tag.lower() for tag in inp.tags]

            for theme, keywords in self.theme_keywords.items():
                score = 0

                # Check content
                for keyword in keywords:
                    if keyword in content:
                        score += 2

                # Check tags
                for tag in tags:
                    for keyword in keywords:
                        if keyword in tag:
                            score += 3

                if score > 0:
                    theme_scores[theme] = theme_scores.get(theme, 0) + score

        # Determine primary theme
        if theme_scores:
            primary_theme = max(theme_scores, key=theme_scores.get)
            max_score = theme_scores[primary_theme]
            confidence = min(max_score / 10.0, 1.0)
        else:
            primary_theme = "general"
            confidence = 0.5
            theme_scores = {"general": 5}

        # Get theme attributes
        colors = self.theme_colors.get(primary_theme, ['blue', 'white', 'silver'])
        decorations = self.theme_decorations.get(primary_theme, ['balloons', 'streamers', 'banners'])
        activities = self.theme_activities.get(primary_theme, ['party games', 'crafts', 'dancing'])

        return {
            "primary_theme": primary_theme,
            "theme_scores": theme_scores,
            "confidence": confidence,
            "colors": colors,
            "decorations": decorations,
            "activities": activities,
        }


# Export
__all__ = ["ThemeAgent"]
