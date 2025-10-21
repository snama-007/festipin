"""
BudgetAgent - Reactive Agent

Recalculates budget whenever any cost-affecting agent completes.
Always-reactive like FinalPlanner.

State Machine: LISTENING → CALCULATING → COMPLETED → LISTENING
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
import uuid

from app.services.event_bus import get_event_bus
from app.services.party_state_store import get_state_store
from app.models.events import (
    AgentCompletedEvent,
    AgentDataRemovedEvent,
    create_budget_updated_event,
)
from app.core.logging import logger


class BudgetAgent:
    """
    Always-reactive agent that recalculates budget.

    Triggers:
    - party.agent.completed (when cost-related agents finish)
    - party.agent.data_removed (when agents are removed)

    Output:
    - total_budget: {min, max}
    - breakdown: {category: {min, max, note}}
    - recommendations: cost-saving tips
    - based_on_agents: which agents contributed
    """

    def __init__(self):
        self.agent_name = "budget_agent"
        self.event_bus = get_event_bus()
        self.state_store = get_state_store()
        self._running = False

        # Cost-affecting agents
        self.cost_agents = ['venue_agent', 'cake_agent', 'catering_agent', 'vendor_agent']

        # Default cost estimates (fallback)
        self.default_estimates = {
            'venue': {'min': 200, 'max': 1000},
            'cake': {'min': 80, 'max': 300},
            'catering': {'min': 300, 'max': 800},
            'decorations': {'min': 100, 'max': 400},
            'entertainment': {'min': 200, 'max': 600},
            'photography': {'min': 150, 'max': 400},
        }

    async def start(self):
        """
        Start the always-reactive agent.
        Listens to agent completions and recalculates budget.
        """
        if self._running:
            logger.warning(f"{self.agent_name} already running")
            return

        self._running = True
        logger.info(f"{self.agent_name} started (listening)")

        # Listen to multiple event types
        tasks = [
            asyncio.create_task(self._listen_agent_completed()),
            asyncio.create_task(self._listen_agent_data_removed()),
        ]

        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"{self.agent_name} error", error=str(e))
            self._running = False
            raise

    async def stop(self):
        """Stop the agent"""
        self._running = False
        logger.info(f"{self.agent_name} stopped")

    async def _listen_agent_completed(self):
        """Listen to party.agent.completed events"""
        logger.info(f"{self.agent_name}: Listening to party.agent.completed")

        async for event in self.event_bus.subscribe("party.agent.completed"):
            if not self._running:
                break

            # Only process if completed agent affects cost
            agent_name = event.payload.agent_name
            if agent_name in self.cost_agents:
                try:
                    await self._recalculate_budget(
                        event.party_id,
                        event.correlation_id,
                        f"{agent_name}_completed"
                    )
                except Exception as e:
                    logger.error(
                        f"{self.agent_name} recalculation error",
                        party_id=event.party_id,
                        error=str(e)
                    )

    async def _listen_agent_data_removed(self):
        """Listen to party.agent.data_removed events"""
        logger.info(f"{self.agent_name}: Listening to party.agent.data_removed")

        async for event in self.event_bus.subscribe("party.agent.data_removed"):
            if not self._running:
                break

            # Recalculate budget when any agent data is removed
            agent_name = event.payload.agent_name
            if agent_name in self.cost_agents:
                try:
                    await self._recalculate_budget(
                        event.party_id,
                        event.correlation_id,
                        f"{agent_name}_removed"
                    )
                except Exception as e:
                    logger.error(
                        f"{self.agent_name} recalculation error",
                        party_id=event.party_id,
                        error=str(e)
                    )

    async def _recalculate_budget(
        self,
        party_id: str,
        correlation_id: str,
        trigger: str
    ):
        """
        Recalculate budget based on all active cost agents.

        Args:
            party_id: Party identifier
            correlation_id: Correlation ID for event tracing
            trigger: What triggered this recalculation
        """
        start_time = time.time()

        logger.info(
            f"{self.agent_name}: Recalculating budget",
            party_id=party_id,
            trigger=trigger
        )

        # Get party state
        party_state = await self.state_store.get_party(party_id)
        if not party_state:
            logger.error(f"Party {party_id} not found")
            return

        # Get previous budget for delta calculation
        previous_budget = party_state.budget

        # Fetch all cost-related agent results
        agent_results = {}
        for agent in self.cost_agents:
            result = party_state.get_agent_result(agent)
            if result and result.status == 'completed':
                agent_results[agent] = result.result

        # Calculate budget
        budget_data = self._calculate_budget(agent_results)

        # Add delta if previous budget exists
        if previous_budget:
            prev_total = previous_budget.get('total_budget', {})
            curr_total = budget_data['total_budget']

            budget_data['previous_total'] = prev_total
            budget_data['delta'] = {
                'min': curr_total['min'] - prev_total.get('min', 0),
                'max': curr_total['max'] - prev_total.get('max', 0)
            }

        # Store in state
        await self.state_store.set_budget(party_id, budget_data)

        # Emit budget updated event
        budget_event = create_budget_updated_event(
            party_id=party_id,
            total_budget=budget_data['total_budget'],
            breakdown=budget_data['breakdown'],
            based_on_agents=budget_data['based_on_agents'],
            correlation_id=correlation_id
        )

        await self.event_bus.publish("party.budget.updated", budget_event)

        execution_time_ms = (time.time() - start_time) * 1000

        logger.info(
            f"{self.agent_name}: Budget recalculated",
            party_id=party_id,
            total_min=budget_data['total_budget']['min'],
            total_max=budget_data['total_budget']['max'],
            based_on_agents=len(budget_data['based_on_agents']),
            execution_time_ms=execution_time_ms
        )

    def _calculate_budget(self, agent_results: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Calculate budget from agent results.

        Args:
            agent_results: Results from cost-affecting agents

        Returns:
            Budget breakdown with totals
        """
        breakdown = {}
        total_min = 0
        total_max = 0
        based_on_agents = []

        # Extract actual costs from agent results

        # Venue costs
        if 'venue_agent' in agent_results:
            venue_data = agent_results['venue_agent']
            venues = venue_data.get('recommended_venues', [])
            if venues:
                top_venue = venues[0]
                venue_price = top_venue.get('daily_price', 0)
                if venue_price > 0:
                    breakdown['venue'] = {'min': venue_price, 'max': venue_price}
                else:
                    breakdown['venue'] = {'min': 0, 'max': 0, 'note': 'Free (permit may be required)'}
                total_min += breakdown['venue']['min']
                total_max += breakdown['venue']['max']
                based_on_agents.append('venue_agent')

        # Cake costs
        if 'cake_agent' in agent_results:
            cake_data = agent_results['cake_agent']
            estimated_cost = cake_data.get('estimated_cost', {})
            if estimated_cost:
                breakdown['cake'] = {
                    'min': estimated_cost.get('min', 80),
                    'max': estimated_cost.get('max', 300)
                }
                total_min += breakdown['cake']['min']
                total_max += breakdown['cake']['max']
                based_on_agents.append('cake_agent')

        # Catering costs
        if 'catering_agent' in agent_results:
            catering_data = agent_results['catering_agent']
            catering_cost = catering_data.get('estimated_total_cost', {})
            if catering_cost:
                breakdown['catering'] = {
                    'min': catering_cost.get('min', 300),
                    'max': catering_cost.get('max', 800)
                }
                total_min += breakdown['catering']['min']
                total_max += breakdown['catering']['max']
                based_on_agents.append('catering_agent')

        # Vendor costs
        if 'vendor_agent' in agent_results:
            vendor_data = agent_results['vendor_agent']
            vendors_by_category = vendor_data.get('vendors_by_category', {})

            for category, vendors in vendors_by_category.items():
                if vendors and len(vendors) > 0:
                    # Use average price from first vendor
                    avg_price = vendors[0].get('avg_price', 0)
                    if avg_price > 0:
                        breakdown[category] = {
                            'min': int(avg_price * 0.8),  # -20%
                            'max': int(avg_price * 1.2)   # +20%
                        }
                        total_min += breakdown[category]['min']
                        total_max += breakdown[category]['max']

            if vendors_by_category:
                based_on_agents.append('vendor_agent')

        # If no agent results, use default estimates
        if not breakdown:
            breakdown = self.default_estimates.copy()
            for costs in breakdown.values():
                total_min += costs.get('min', 0)
                total_max += costs.get('max', 0)
            based_on_agents = ['default_estimates']

        # Generate recommendations
        recommendations = self._get_budget_recommendations(total_min, total_max)
        cost_saving_tips = self._get_cost_saving_tips()

        return {
            'total_budget': {'min': total_min, 'max': total_max},
            'breakdown': breakdown,
            'recommendations': recommendations,
            'cost_saving_tips': cost_saving_tips,
            'based_on_agents': based_on_agents,
            'data_source': 'actual_agent_results' if agent_results else 'default_estimates'
        }

    def _get_budget_recommendations(self, min_cost: int, max_cost: int) -> List[str]:
        """Generate budget recommendations based on total cost"""
        if max_cost > 2000:
            return [
                "Consider DIY decorations to reduce costs",
                "Look for venue/catering package deals",
                "Book vendors 2-3 months in advance for discounts"
            ]
        elif max_cost > 1000:
            return [
                "Compare quotes from multiple vendors",
                "Consider off-peak timing for better rates",
                "Limit guest count if budget is tight"
            ]
        else:
            return [
                "Focus on essential items first",
                "Consider home venue to save costs",
                "DIY entertainment and decorations",
                "Potluck-style catering option"
            ]

    def _get_cost_saving_tips(self) -> List[str]:
        """General cost-saving tips"""
        return [
            "Book vendors 2-3 months in advance for early-bird discounts",
            "Consider weekday parties for 20-30% lower rates",
            "DIY decorations add personal touch and save money",
            "Digital invitations are free and eco-friendly",
            "Buy bulk supplies from wholesale stores",
            "Reuse and repurpose decorations from previous parties"
        ]


# Export
__all__ = ["BudgetAgent"]
