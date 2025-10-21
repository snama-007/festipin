"""
FinalPlanner Agent - Always-Running (Reactive)

Listens to agent completion events and generates/updates the final party plan.
Runs whenever any agent completes or budget updates.

This agent runs 24/7 as a background task.
"""

import asyncio
from typing import Dict, List, Any, Optional

from app.services.event_bus import get_event_bus
from app.services.party_state_store import get_state_store
from app.models.events import (
    AgentCompletedEvent,
    BudgetUpdatedEvent,
    AgentDataRemovedEvent,
    create_plan_updated_event,
)
from app.core.logging import logger


class FinalPlannerAgent:
    """
    Always-reactive agent that updates the final plan.

    Responsibilities:
    - Aggregate results from all completed agents
    - Generate comprehensive recommendations
    - Calculate completion percentage
    - Identify missing agents
    - Create prioritized next steps
    - Emit plan_updated events
    """

    def __init__(self):
        self.event_bus = get_event_bus()
        self.state_store = get_state_store()
        self._running = False

        # Required agents for a complete plan
        self.required_agents = ['theme_agent', 'venue_agent']

        # Optional agents (improve plan but not required)
        self.optional_agents = ['cake_agent', 'catering_agent', 'vendor_agent']

    async def start(self):
        """
        Start the always-reactive agent.
        Subscribes to agent completion and budget events.
        """
        if self._running:
            logger.warning("FinalPlanner already running")
            return

        self._running = True
        logger.info("FinalPlanner agent starting...")

        # Listen to multiple event types
        tasks = [
            asyncio.create_task(self._listen_agent_completed()),
            asyncio.create_task(self._listen_budget_updated()),
            asyncio.create_task(self._listen_agent_data_removed()),
        ]

        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error("FinalPlanner agent error", error=str(e))
            self._running = False
            raise

    async def stop(self):
        """Stop the agent"""
        self._running = False
        logger.info("FinalPlanner agent stopped")

    async def _listen_agent_completed(self):
        """Listen to party.agent.completed events"""
        logger.info("FinalPlanner: Listening to party.agent.completed")

        async for event in self.event_bus.subscribe("party.agent.completed"):
            if not self._running:
                break

            try:
                await self._update_plan(event.party_id, event.correlation_id, "agent_completed")
            except Exception as e:
                logger.error(
                    "Error handling agent_completed event",
                    event_id=event.event_id,
                    error=str(e)
                )

    async def _listen_budget_updated(self):
        """Listen to party.budget.updated events"""
        logger.info("FinalPlanner: Listening to party.budget.updated")

        async for event in self.event_bus.subscribe("party.budget.updated"):
            if not self._running:
                break

            try:
                await self._update_plan(event.party_id, event.correlation_id, "budget_updated")
            except Exception as e:
                logger.error(
                    "Error handling budget_updated event",
                    event_id=event.event_id,
                    error=str(e)
                )

    async def _listen_agent_data_removed(self):
        """Listen to party.agent.data_removed events"""
        logger.info("FinalPlanner: Listening to party.agent.data_removed")

        async for event in self.event_bus.subscribe("party.agent.data_removed"):
            if not self._running:
                break

            try:
                await self._update_plan(event.party_id, event.correlation_id, "agent_data_removed")
            except Exception as e:
                logger.error(
                    "Error handling agent_data_removed event",
                    event_id=event.event_id,
                    error=str(e)
                )

    async def _update_plan(self, party_id: str, correlation_id: str, trigger: str):
        """
        Recompute and update the final plan.

        Args:
            party_id: Party identifier
            correlation_id: Correlation ID for event tracing
            trigger: What triggered this update
        """
        logger.info(
            "FinalPlanner: Updating plan",
            party_id=party_id,
            trigger=trigger
        )

        # Get party state
        party_state = await self.state_store.get_party(party_id)
        if not party_state:
            logger.error("Party not found", party_id=party_id)
            return

        # Gather all completed agent results
        agent_results = {}
        for agent_name, agent_result in party_state.active_agents.items():
            if agent_result.status == "completed":
                agent_results[agent_name] = agent_result.result

        # Get budget
        budget = party_state.budget

        # Generate comprehensive plan
        final_plan = self._generate_plan(
            party_id=party_id,
            agent_results=agent_results,
            budget=budget,
            party_state=party_state
        )

        # Store in state
        await self.state_store.set_final_plan(party_id, final_plan)

        # Emit plan_updated event
        plan_event = create_plan_updated_event(
            party_id=party_id,
            completion_percent=final_plan["completion_percent"],
            recommendations=final_plan["recommendations"],
            next_steps=final_plan["next_steps"],
            active_agents=final_plan["active_agents"],
            missing_agents=final_plan["missing_agents"],
            correlation_id=correlation_id
        )

        await self.event_bus.publish("party.plan.updated", plan_event)

        logger.info(
            "FinalPlanner: Plan updated",
            party_id=party_id,
            completion_percent=final_plan["completion_percent"],
            active_agents=len(final_plan["active_agents"]),
            missing_agents=len(final_plan["missing_agents"])
        )

    def _generate_plan(
        self,
        party_id: str,
        agent_results: Dict[str, Dict],
        budget: Optional[Dict],
        party_state: Any
    ) -> Dict[str, Any]:
        """
        Generate comprehensive party plan from agent results.

        Args:
            party_id: Party identifier
            agent_results: Results from completed agents
            budget: Budget information
            party_state: Current party state

        Returns:
            Complete plan dictionary
        """
        # Calculate completion percentage
        completed_required = sum(
            1 for agent in self.required_agents
            if agent in agent_results
        )
        total_required = len(self.required_agents)
        completion_percent = int((completed_required / total_required) * 100) if total_required > 0 else 0

        # Get active and missing agents
        active_agents = list(agent_results.keys())
        all_agents = self.required_agents + self.optional_agents
        missing_agents = [
            agent for agent in all_agents
            if agent not in agent_results
        ]

        # Generate recommendations
        recommendations = self._generate_recommendations(agent_results, budget)

        # Generate next steps
        next_steps = self._generate_next_steps(agent_results, missing_agents)

        # Generate checklist summary
        checklist_summary = self._generate_checklist_summary(agent_results)

        # Build final plan
        plan = {
            "completion_percent": completion_percent,
            "recommendations": recommendations,
            "next_steps": next_steps,
            "active_agents": active_agents,
            "missing_agents": missing_agents,
            "checklist_summary": checklist_summary,
            "budget_summary": budget,
            "agent_details": self._summarize_agent_results(agent_results),
        }

        return plan

    def _generate_recommendations(
        self,
        agent_results: Dict[str, Dict],
        budget: Optional[Dict]
    ) -> List[Dict[str, str]]:
        """Generate prioritized recommendations"""
        recommendations = []

        # Theme recommendations
        if 'theme_agent' in agent_results:
            theme_data = agent_results['theme_agent']
            recommendations.append({
                "category": "Theme",
                "priority": "high",
                "description": f"Primary theme: {theme_data.get('primary_theme', 'N/A')}. "
                              f"Colors: {', '.join(theme_data.get('colors', [])[:3])}"
            })

        # Venue recommendations
        if 'venue_agent' in agent_results:
            venue_data = agent_results['venue_agent']
            venue_count = len(venue_data.get('recommended_venues', []))
            if venue_count > 0:
                top_venue = venue_data['recommended_venues'][0]
                recommendations.append({
                    "category": "Venue",
                    "priority": "critical",
                    "description": f"Top recommendation: {top_venue.get('name')} "
                                  f"(capacity: {top_venue.get('capacity')}, "
                                  f"price: ${top_venue.get('daily_price', 0)})"
                })

        # Cake recommendations
        if 'cake_agent' in agent_results:
            cake_data = agent_results['cake_agent']
            bakery_count = len(cake_data.get('recommended_bakeries', []))
            if bakery_count > 0:
                recommendations.append({
                    "category": "Cake",
                    "priority": "medium",
                    "description": f"Found {bakery_count} bakery options. "
                                  f"Estimated cost: ${cake_data.get('estimated_cost', {}).get('min', 0)}-"
                                  f"${cake_data.get('estimated_cost', {}).get('max', 0)}"
                })

        # Budget recommendations
        if budget:
            total_budget = budget.get('total_budget', {})
            if total_budget:
                recommendations.append({
                    "category": "Budget",
                    "priority": "high",
                    "description": f"Estimated total: ${total_budget.get('min', 0)}-${total_budget.get('max', 0)}"
                })

        # Add default recommendation if none exist
        if not recommendations:
            recommendations.append({
                "category": "General",
                "priority": "medium",
                "description": "Add more details to get personalized recommendations"
            })

        return recommendations

    def _generate_next_steps(
        self,
        agent_results: Dict[str, Dict],
        missing_agents: List[str]
    ) -> List[str]:
        """Generate prioritized next steps"""
        next_steps = []

        # Missing critical agents
        if 'theme_agent' in missing_agents:
            next_steps.append("Add theme information (e.g., 'jungle theme', 'princess party')")

        if 'venue_agent' in missing_agents:
            next_steps.append("Specify guest count and preferred location")

        # Missing optional agents
        if 'cake_agent' in missing_agents:
            next_steps.append("Add cake preferences (flavor, size, design)")

        if 'catering_agent' in missing_agents:
            next_steps.append("Specify food preferences and dietary requirements")

        if 'vendor_agent' in missing_agents:
            next_steps.append("Add vendor needs (decorations, entertainment, photography)")

        # Refinement steps
        if 'theme_agent' in agent_results:
            next_steps.append("Review theme colors and decorations")

        if 'venue_agent' in agent_results:
            next_steps.append("Compare venue options and book preferred location")

        if 'cake_agent' in agent_results:
            next_steps.append("Contact bakery to discuss custom design")

        # Default step
        if not next_steps:
            next_steps.append("Add more party details to get started")

        return next_steps[:5]  # Limit to top 5

    def _generate_checklist_summary(
        self,
        agent_results: Dict[str, Dict]
    ) -> Dict[str, int]:
        """Generate checklist summary statistics"""
        # In a full implementation, this would aggregate actual checklist items
        # For now, estimate based on completed agents
        estimated_tasks_per_agent = 3
        total_tasks = len(agent_results) * estimated_tasks_per_agent
        completed_tasks = 0  # Would come from actual checklist tracking

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": total_tasks - completed_tasks
        }

    def _summarize_agent_results(
        self,
        agent_results: Dict[str, Dict]
    ) -> Dict[str, Dict[str, Any]]:
        """Create summary of each agent's key findings"""
        summaries = {}

        for agent_name, result in agent_results.items():
            if agent_name == 'theme_agent':
                summaries[agent_name] = {
                    "theme": result.get("primary_theme"),
                    "confidence": result.get("confidence"),
                    "colors": result.get("colors", [])[:3]
                }
            elif agent_name == 'venue_agent':
                venues = result.get("recommended_venues", [])
                summaries[agent_name] = {
                    "venue_count": len(venues),
                    "top_venue": venues[0].get("name") if venues else None
                }
            elif agent_name == 'cake_agent':
                bakeries = result.get("recommended_bakeries", [])
                summaries[agent_name] = {
                    "bakery_count": len(bakeries),
                    "estimated_cost": result.get("estimated_cost")
                }

        return summaries


# Export
__all__ = ["FinalPlannerAgent"]
