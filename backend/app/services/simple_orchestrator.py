"""
Simple Orchestrator for Agentic Party Planning

This module implements a simple workflow orchestrator without LangGraph
for immediate functionality while LangGraph is being set up.
"""

import asyncio
from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
import json

from app.core.logging import logger
from app.services.local_memory_store import (
    LocalMemoryStore, EventState, AgentResult, 
    create_event, get_event_state, update_agent_result, 
    set_final_plan, update_workflow_status, add_user_feedback
)
from app.services.agent_registry import (
    AgentRegistry, AgentType, AgentInput, AgentOutput,
    get_agent_registry
)


class OrchestrationState(TypedDict):
    """State for orchestration"""
    event_id: str
    inputs: List[Dict[str, Any]]
    agent_results: Dict[str, Any]
    current_agent: str
    workflow_status: str
    user_feedback: Dict[str, Any]
    final_plan: Optional[Dict[str, Any]]
    execution_context: Dict[str, Any]


class SimpleOrchestrator:
    """
    Simple orchestrator for agent coordination without LangGraph
    
    Features:
    - Sequential agent execution
    - State management with local JSON storage
    - Error handling and recovery
    - Real-time progress tracking
    - User feedback integration
    """
    
    def __init__(self, memory_store: Optional[LocalMemoryStore] = None):
        self.memory_store = memory_store or LocalMemoryStore()
        self.agent_registry = get_agent_registry()
        self.ws_manager = None  # Will be set on first use

        logger.info("Simple orchestrator initialized")

    async def _broadcast_agent_update(self, event_id: str, agent_name: str,
                                      status: str, result: Optional[Dict] = None,
                                      message: Optional[str] = None, error: Optional[str] = None):
        """Broadcast agent update via WebSocket"""
        try:
            # Import lazily to avoid circular dependency
            if self.ws_manager is None:
                from app.api.routes.websocket import manager
                self.ws_manager = manager

            update = {
                "type": "agent_update",
                "agent": agent_name,
                "status": status,  # "running", "completed", "error"
            }

            if message:
                update["message"] = message
            if result:
                update["result"] = result
            if error:
                update["error"] = error

            await self.ws_manager.send_agent_update(event_id, update)

        except Exception as e:
            # Don't fail workflow if WebSocket broadcast fails
            logger.warning("Failed to broadcast WebSocket update",
                          event_id=event_id,
                          agent=agent_name,
                          error=str(e))
    
    async def start_orchestration(self, inputs: List[Dict[str, Any]], 
                                metadata: Dict[str, Any] = None) -> str:
        """Start new orchestration workflow"""
        try:
            # Create new event
            event_id = await create_event(inputs, metadata)
            
            # Initialize workflow state
            initial_state = OrchestrationState(
                event_id=event_id,
                inputs=inputs,
                agent_results={},
                current_agent="input_classifier",
                workflow_status="running",
                user_feedback={},
                final_plan=None,
                execution_context={}
            )
            
            # Update workflow status
            await update_workflow_status(event_id, "running")
            
            # Start workflow execution
            asyncio.create_task(self._execute_workflow(initial_state))
            
            logger.info("Started orchestration workflow", event_id=event_id)
            return event_id
            
        except Exception as e:
            logger.error("Failed to start orchestration", error=str(e))
            raise
    
    async def _execute_workflow(self, initial_state: OrchestrationState):
        """Execute the workflow sequentially"""
        try:
            state = initial_state.copy()
            
            # Execute agents in sequence
            agents_to_run = [
                ("input_classifier", self._input_classifier_node),
                ("theme_agent", self._theme_agent_node),
                ("cake_agent", self._cake_agent_node),
                ("venue_agent", self._venue_agent_node),
                ("catering_agent", self._catering_agent_node),
                ("budget_agent", self._budget_agent_node),
                ("vendor_agent", self._vendor_agent_node),
                ("planner_agent", self._planner_agent_node)
            ]
            
            for agent_name, agent_func in agents_to_run:
                try:
                    # Check if agent should run
                    if self._should_run_agent(agent_name, state):
                        logger.info(f"Running agent: {agent_name}", event_id=state["event_id"])
                        state = await agent_func(state)
                        
                        # Small delay between agents for better UX
                        await asyncio.sleep(0.5)
                    else:
                        logger.info(f"Skipping agent: {agent_name}", event_id=state["event_id"])
                        
                except Exception as e:
                    logger.error(f"Agent {agent_name} failed", 
                                event_id=state["event_id"], error=str(e))
                    # Continue with next agent
                    continue
            
            # Update final state
            await update_workflow_status(state["event_id"], "completed")
            
            logger.info("Workflow completed", 
                       event_id=state["event_id"],
                       final_plan_keys=list(state.get("final_plan", {}).keys()))
            
        except Exception as e:
            logger.error("Workflow execution failed", 
                        event_id=initial_state["event_id"], 
                        error=str(e))
            await update_workflow_status(initial_state["event_id"], "error")
    
    def _should_run_agent(self, agent_name: str, state: OrchestrationState) -> bool:
        """Determine if agent should run based on current state"""
        if agent_name == "input_classifier":
            return True
        
        if agent_name == "theme_agent":
            return "input_classifier" in state["agent_results"]
        
        if agent_name == "cake_agent":
            classified_inputs = state["agent_results"].get("input_classifier", {}).get("classified_inputs", {})
            return "cake" in classified_inputs
        
        if agent_name == "venue_agent":
            classified_inputs = state["agent_results"].get("input_classifier", {}).get("classified_inputs", {})
            return "venue" in classified_inputs
        
        if agent_name == "catering_agent":
            classified_inputs = state["agent_results"].get("input_classifier", {}).get("classified_inputs", {})
            return "catering" in classified_inputs
        
        if agent_name == "budget_agent":
            # Run after theme agent completes
            return "theme_agent" in state["agent_results"]
        
        if agent_name == "vendor_agent":
            # Run after budget agent completes
            return "budget_agent" in state["agent_results"]
        
        if agent_name == "planner_agent":
            # Run after vendor agent completes
            return "vendor_agent" in state["agent_results"]
        
        return False
    
    # Node implementations (same as LangGraph version)
    async def _input_classifier_node(self, state: OrchestrationState) -> OrchestrationState:
        """Input classifier node"""
        try:
            agent_input = AgentInput(
                agent_type=AgentType.INPUT_CLASSIFIER,
                inputs=state["inputs"],
                context=state["execution_context"],
                event_id=state["event_id"]
            )
            
            # Execute classifier agent
            result = await self.agent_registry.execute_agent(
                AgentType.INPUT_CLASSIFIER, agent_input
            )
            
            # Update state
            state["agent_results"]["input_classifier"] = result.result
            state["current_agent"] = "input_classifier"
            
            # Update memory store
            await update_agent_result(
                state["event_id"], 
                "input_classifier", 
                result.result,
                "completed",
                None,
                result.execution_time
            )
            
            logger.info("Input classifier completed", 
                       event_id=state["event_id"],
                       classified_count=len(result.result.get("classified_inputs", {})))
            
        except Exception as e:
            logger.error("Input classifier failed", 
                        event_id=state["event_id"], 
                        error=str(e))
            await update_agent_result(
                state["event_id"], 
                "input_classifier", 
                {"error": str(e)},
                "error",
                str(e)
            )
        
        return state
    
    async def _theme_agent_node(self, state: OrchestrationState) -> OrchestrationState:
        """Theme agent node"""
        try:
            # ✅ Broadcast: Starting
            await self._broadcast_agent_update(
                state["event_id"],
                "theme_agent",
                "running",
                message="Analyzing party theme..."
            )

            # Get classified inputs
            classified_inputs = state["agent_results"].get("input_classifier", {}).get("classified_inputs", {})
            theme_inputs = classified_inputs.get("theme", state["inputs"])

            if not theme_inputs:
                logger.warning("No theme inputs found", event_id=state["event_id"])
                return state

            agent_input = AgentInput(
                agent_type=AgentType.THEME,
                inputs=theme_inputs,
                context=state["execution_context"],
                event_id=state["event_id"]
            )

            # Execute theme agent
            result = await self.agent_registry.execute_agent(
                AgentType.THEME, agent_input
            )

            # Update state
            state["agent_results"]["theme_agent"] = result.result
            state["current_agent"] = "theme_agent"
            state["execution_context"]["theme_result"] = result.result

            # Update memory store
            await update_agent_result(
                state["event_id"],
                "theme_agent",
                result.result,
                "completed",
                None,
                result.execution_time
            )

            # ✅ Broadcast: Completed
            theme = result.result.get("primary_theme", "general")
            await self._broadcast_agent_update(
                state["event_id"],
                "theme_agent",
                "completed",
                result=result.result,
                message=f"Detected {theme} theme!"
            )

            logger.info("Theme agent completed",
                       event_id=state["event_id"],
                       theme=theme)

        except Exception as e:
            logger.error("Theme agent failed",
                        event_id=state["event_id"],
                        error=str(e))
            await update_agent_result(
                state["event_id"],
                "theme_agent",
                {"error": str(e)},
                "error",
                str(e)
            )

            # ✅ Broadcast: Error
            await self._broadcast_agent_update(
                state["event_id"],
                "theme_agent",
                "error",
                error=str(e)
            )

        return state
    
    async def _cake_agent_node(self, state: OrchestrationState) -> OrchestrationState:
        """Cake agent node"""
        try:
            # Get classified inputs
            classified_inputs = state["agent_results"].get("input_classifier", {}).get("classified_inputs", {})
            cake_inputs = classified_inputs.get("cake", [])
            
            if not cake_inputs:
                logger.info("No cake inputs found, skipping cake agent", event_id=state["event_id"])
                return state
            
            agent_input = AgentInput(
                agent_type=AgentType.CAKE,
                inputs=cake_inputs,
                context=state["execution_context"],
                event_id=state["event_id"]
            )
            
            # Execute cake agent
            result = await self.agent_registry.execute_agent(
                AgentType.CAKE, agent_input
            )
            
            # Update state
            state["agent_results"]["cake_agent"] = result.result
            state["current_agent"] = "cake_agent"
            
            # Update memory store
            await update_agent_result(
                state["event_id"], 
                "cake_agent", 
                result.result,
                "completed",
                None,
                result.execution_time
            )
            
            logger.info("Cake agent completed", 
                       event_id=state["event_id"],
                       cake_type=result.result.get("cake_type"))
            
        except Exception as e:
            logger.error("Cake agent failed", 
                        event_id=state["event_id"], 
                        error=str(e))
            await update_agent_result(
                state["event_id"], 
                "cake_agent", 
                {"error": str(e)},
                "error",
                str(e)
            )
        
        return state
    
    async def _venue_agent_node(self, state: OrchestrationState) -> OrchestrationState:
        """Venue agent node (placeholder)"""
        # Placeholder implementation
        venue_result = {
            "venue_type": "indoor",
            "capacity": 50,
            "amenities": ["tables", "chairs", "sound_system"],
            "estimated_cost": {"min": 200, "max": 500}
        }
        
        state["agent_results"]["venue_agent"] = venue_result
        state["current_agent"] = "venue_agent"
        
        await update_agent_result(
            state["event_id"], 
            "venue_agent", 
            venue_result,
            "completed"
        )
        
        logger.info("Venue agent completed", event_id=state["event_id"])
        return state
    
    async def _catering_agent_node(self, state: OrchestrationState) -> OrchestrationState:
        """Catering agent node (placeholder)"""
        # Placeholder implementation
        catering_result = {
            "menu_type": "buffet",
            "cuisine": "mixed",
            "estimated_cost": {"min": 300, "max": 800},
            "special_dietary": ["vegetarian", "gluten_free"]
        }
        
        state["agent_results"]["catering_agent"] = catering_result
        state["current_agent"] = "catering_agent"
        
        await update_agent_result(
            state["event_id"], 
            "catering_agent", 
            catering_result,
            "completed"
        )
        
        logger.info("Catering agent completed", event_id=state["event_id"])
        return state
    
    async def _budget_agent_node(self, state: OrchestrationState) -> OrchestrationState:
        """Budget agent node"""
        try:
            agent_input = AgentInput(
                agent_type=AgentType.BUDGET,
                inputs=state["inputs"],
                context={
                    "agent_results": state["agent_results"],
                    **state["execution_context"]
                },
                event_id=state["event_id"]
            )
            
            # Execute budget agent
            result = await self.agent_registry.execute_agent(
                AgentType.BUDGET, agent_input
            )
            
            # Update state
            state["agent_results"]["budget_agent"] = result.result
            state["current_agent"] = "budget_agent"
            
            # Update memory store
            await update_agent_result(
                state["event_id"], 
                "budget_agent", 
                result.result,
                "completed",
                None,
                result.execution_time
            )
            
            logger.info("Budget agent completed", 
                       event_id=state["event_id"],
                       total_max=result.result.get("total_budget", {}).get("max"))
            
        except Exception as e:
            logger.error("Budget agent failed", 
                        event_id=state["event_id"], 
                        error=str(e))
            await update_agent_result(
                state["event_id"], 
                "budget_agent", 
                {"error": str(e)},
                "error",
                str(e)
            )
        
        return state
    
    async def _vendor_agent_node(self, state: OrchestrationState) -> OrchestrationState:
        """Vendor agent node (placeholder)"""
        # Placeholder implementation
        vendor_result = {
            "suggested_vendors": [
                {"name": "Party Supplies Co", "type": "decorations", "rating": 4.5},
                {"name": "Cake Masters", "type": "cake", "rating": 4.8},
                {"name": "Event Catering", "type": "catering", "rating": 4.3}
            ],
            "contact_info": ["phone", "email", "website"]
        }
        
        state["agent_results"]["vendor_agent"] = vendor_result
        state["current_agent"] = "vendor_agent"
        
        await update_agent_result(
            state["event_id"], 
            "vendor_agent", 
            vendor_result,
            "completed"
        )
        
        logger.info("Vendor agent completed", event_id=state["event_id"])
        return state
    
    async def _planner_agent_node(self, state: OrchestrationState) -> OrchestrationState:
        """Planner agent node - final assembly"""
        try:
            # Assemble final plan from all agent results
            final_plan = {
                "event_summary": {
                    "theme": state["agent_results"].get("theme_agent", {}).get("primary_theme", "general"),
                    "total_budget": state["agent_results"].get("budget_agent", {}).get("total_budget", {}),
                    "created_at": datetime.utcnow().isoformat()
                },
                "agent_results": state["agent_results"],
                "recommendations": self._generate_recommendations(state["agent_results"]),
                "next_steps": self._generate_next_steps(state["agent_results"])
            }
            
            state["final_plan"] = final_plan
            state["current_agent"] = "planner_agent"
            state["workflow_status"] = "completed"
            
            # Update memory store
            await set_final_plan(state["event_id"], final_plan)
            
            logger.info("Planner agent completed - final plan assembled", 
                       event_id=state["event_id"])
            
        except Exception as e:
            logger.error("Planner agent failed", 
                        event_id=state["event_id"], 
                        error=str(e))
            await update_agent_result(
                state["event_id"], 
                "planner_agent", 
                {"error": str(e)},
                "error",
                str(e)
            )
        
        return state
    
    def _generate_recommendations(self, agent_results: Dict[str, Any]) -> List[str]:
        """Generate intelligent recommendations based on all agent results"""
        recommendations = []

        # Theme-based recommendations
        theme_result = agent_results.get("theme_agent", {})
        if theme_result:
            theme = theme_result.get("primary_theme", "general")
            colors = theme_result.get("colors", [])
            activities = theme_result.get("activities", [])

            recommendations.append(f"🎨 Focus on {theme} theme with {', '.join(colors[:2])} color scheme")

            if activities:
                recommendations.append(f"🎯 Plan {activities[0]} as a main activity")

        # Venue-based recommendations
        venue_result = agent_results.get("venue_agent", {})
        if venue_result:
            recommended_venues = venue_result.get("recommended_venues", [])
            if recommended_venues:
                top_venue = recommended_venues[0]
                venue_name = top_venue.get("name", "venue")
                venue_price = top_venue.get("daily_price", 0)

                if venue_price == 0:
                    recommendations.append(f"📍 {venue_name} is free - just need a permit!")
                elif venue_price < 500:
                    recommendations.append(f"📍 {venue_name} is affordable at ${venue_price}/day")
                else:
                    recommendations.append(f"📍 Consider {venue_name} for a premium venue experience")

        # Cake-based recommendations
        cake_result = agent_results.get("cake_agent", {})
        if cake_result:
            recommended_bakeries = cake_result.get("recommended_bakeries", [])
            if recommended_bakeries:
                top_bakery = recommended_bakeries[0]
                bakery_name = top_bakery.get("name", "bakery")
                custom = top_bakery.get("custom_designs", False)

                if custom:
                    recommendations.append(f"🎂 {bakery_name} offers custom designs perfect for your theme")
                else:
                    recommendations.append(f"🎂 {bakery_name} has affordable cake options")

        # Catering-based recommendations
        catering_result = agent_results.get("catering_agent", {})
        if catering_result:
            recommended_caterers = catering_result.get("recommended_caterers", [])
            if recommended_caterers:
                dietary = catering_result.get("dietary_accommodations", [])
                if dietary:
                    recommendations.append(f"🍽️ Found caterers with {', '.join(dietary[:2])} options")

        # Budget-based recommendations
        budget_result = agent_results.get("budget_agent", {})
        if budget_result:
            total_budget = budget_result.get("total_budget", {})
            total_min = total_budget.get("min", 0)
            total_max = total_budget.get("max", 0)

            if total_max > 0:
                recommendations.append(f"💰 Estimated budget: ${total_min:,}-${total_max:,}")

                if total_max > 2000:
                    recommendations.append("💡 Book vendors 2-3 months in advance for better rates")
                elif total_max > 1000:
                    recommendations.append("💡 Compare quotes from multiple vendors to save money")
                else:
                    recommendations.append("💡 Focus on DIY elements and home venue to stay in budget")

        # Vendor-based recommendations
        vendor_result = agent_results.get("vendor_agent", {})
        if vendor_result:
            vendors_by_category = vendor_result.get("vendors_by_category", {})
            total_vendors = sum(len(v) for v in vendors_by_category.values())

            if total_vendors > 0:
                recommendations.append(f"🏪 Found {total_vendors} vendors across {len(vendors_by_category)} categories")

        # General recommendations
        if len(recommendations) < 5:
            recommendations.append("📋 Create a detailed timeline at least 1 month before the event")
            recommendations.append("📧 Send invitations 2-3 weeks in advance")

        return recommendations[:8]  # Limit to 8 recommendations
    
    def _generate_next_steps(self, agent_results: Dict[str, Any]) -> List[str]:
        """Generate intelligent next steps based on agent results"""
        next_steps = []

        # Step 1: Always review the plan
        next_steps.append("1️⃣ Review and approve this party plan")

        # Step 2: Venue booking
        venue_result = agent_results.get("venue_agent", {})
        if venue_result and venue_result.get("recommended_venues"):
            venue_count = len(venue_result.get("recommended_venues", []))
            next_steps.append(f"2️⃣ Contact {venue_count} recommended venues for availability and booking")
        else:
            next_steps.append("2️⃣ Search for and book a suitable venue")

        # Step 3: Vendor contacts
        vendor_result = agent_results.get("vendor_agent", {})
        if vendor_result:
            vendors_by_category = vendor_result.get("vendors_by_category", {})
            if vendors_by_category:
                categories = list(vendors_by_category.keys())
                next_steps.append(f"3️⃣ Request quotes from {', '.join(categories[:2])} vendors")
            else:
                next_steps.append("3️⃣ Contact recommended vendors for quotes")
        else:
            next_steps.append("3️⃣ Search for and contact party vendors")

        # Step 4: Cake order
        cake_result = agent_results.get("cake_agent", {})
        if cake_result and cake_result.get("recommended_bakeries"):
            bakery_name = cake_result.get("recommended_bakeries", [{}])[0].get("name", "bakery")
            next_steps.append(f"4️⃣ Order custom cake from {bakery_name} (at least 2 weeks ahead)")
        else:
            next_steps.append("4️⃣ Order or arrange for party cake")

        # Step 5: Catering
        catering_result = agent_results.get("catering_agent", {})
        if catering_result and catering_result.get("recommended_caterers"):
            dietary = catering_result.get("dietary_accommodations", [])
            if dietary:
                next_steps.append(f"5️⃣ Arrange catering with {', '.join(dietary)} options")
            else:
                next_steps.append("5️⃣ Finalize catering menu and confirm guest count")
        else:
            next_steps.append("5️⃣ Arrange food and catering for the party")

        # Step 6: Decorations and theme
        theme_result = agent_results.get("theme_agent", {})
        if theme_result:
            theme = theme_result.get("primary_theme", "party")
            next_steps.append(f"6️⃣ Purchase or arrange {theme}-themed decorations")
        else:
            next_steps.append("6️⃣ Purchase decorations and party supplies")

        # Step 7: Budget confirmation
        budget_result = agent_results.get("budget_agent", {})
        if budget_result:
            total_budget = budget_result.get("total_budget", {})
            total_max = total_budget.get("max", 0)
            if total_max > 0:
                next_steps.append(f"7️⃣ Confirm budget allocation (~${total_max:,} total)")
            else:
                next_steps.append("7️⃣ Review and finalize budget")
        else:
            next_steps.append("7️⃣ Finalize party budget")

        # Step 8: Invitations
        next_steps.append("8️⃣ Send invitations 2-3 weeks before the party")

        # Step 9: Timeline
        next_steps.append("9️⃣ Create day-of timeline and assign responsibilities")

        # Step 10: Final checks
        next_steps.append("🔟 Confirm all bookings 1 week before the event")

        return next_steps
    
    async def get_workflow_status(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get current workflow status"""
        event_state = await get_event_state(event_id)
        if not event_state:
            return None
        
        return {
            "event_id": event_id,
            "workflow_status": event_state.workflow_status,
            "agent_results": {
                name: {
                    "status": result.status,
                    "result": result.result,
                    "execution_time": result.execution_time
                }
                for name, result in event_state.agent_results.items()
            },
            "final_plan": event_state.final_plan,
            "created_at": event_state.created_at,
            "updated_at": event_state.updated_at
        }
    
    async def add_user_feedback(self, event_id: str, feedback: Dict[str, Any]):
        """Add user feedback to workflow"""
        await add_user_feedback(event_id, feedback)
        
        # Could trigger re-execution of specific agents based on feedback
        logger.info("User feedback added", event_id=event_id, feedback_keys=list(feedback.keys()))


# Global orchestrator instance
_orchestrator: Optional[SimpleOrchestrator] = None


def get_orchestrator() -> SimpleOrchestrator:
    """Get global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SimpleOrchestrator()
    return _orchestrator
