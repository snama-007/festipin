"""
LangGraph Orchestrator for Agentic Party Planning

This module implements the main orchestration logic using LangGraph
to coordinate multiple agents in a workflow-based approach.
"""

import asyncio
from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
import json

from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage

from app.core.logging import logger
from app.services.local_memory_store import (
    LocalMemoryStore, EventState, AgentResult, 
    create_event, get_event_state, update_agent_result, 
    set_final_plan, update_workflow_status
)
from app.services.agent_registry import (
    AgentRegistry, AgentType, AgentInput, AgentOutput,
    get_agent_registry
)


class OrchestrationState(TypedDict):
    """State for LangGraph orchestration"""
    event_id: str
    inputs: List[Dict[str, Any]]
    agent_results: Dict[str, Any]
    current_agent: str
    workflow_status: str
    user_feedback: Dict[str, Any]
    final_plan: Optional[Dict[str, Any]]
    execution_context: Dict[str, Any]


class LangGraphOrchestrator:
    """
    Main orchestrator using LangGraph for agent coordination
    
    Features:
    - Workflow-based agent execution
    - State management with local JSON storage
    - Error handling and recovery
    - Real-time progress tracking
    - User feedback integration
    """
    
    def __init__(self, memory_store: Optional[LocalMemoryStore] = None):
        self.memory_store = memory_store or LocalMemoryStore()
        self.agent_registry = get_agent_registry()
        self.graph = None
        self._build_workflow_graph()
        
        logger.info("LangGraph orchestrator initialized")
    
    def _build_workflow_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(OrchestrationState)
        
        # Add nodes for each agent
        workflow.add_node("input_classifier", self._input_classifier_node)
        workflow.add_node("theme_agent", self._theme_agent_node)
        workflow.add_node("cake_agent", self._cake_agent_node)
        workflow.add_node("venue_agent", self._venue_agent_node)
        workflow.add_node("catering_agent", self._catering_agent_node)
        workflow.add_node("budget_agent", self._budget_agent_node)
        workflow.add_node("vendor_agent", self._vendor_agent_node)
        workflow.add_node("planner_agent", self._planner_agent_node)
        
        # Define workflow edges
        workflow.set_entry_point("input_classifier")
        
        # From input classifier, route to appropriate agents
        workflow.add_conditional_edges(
            "input_classifier",
            self._route_after_classification,
            {
                "theme": "theme_agent",
                "cake": "cake_agent",
                "venue": "venue_agent",
                "catering": "catering_agent",
                "budget": "budget_agent",
                "vendor": "vendor_agent",
                "planner": "planner_agent"
            }
        )
        
        # From theme agent, continue to other agents
        workflow.add_conditional_edges(
            "theme_agent",
            self._route_after_theme,
            {
                "cake": "cake_agent",
                "venue": "venue_agent",
                "catering": "catering_agent",
                "budget": "budget_agent",
                "vendor": "vendor_agent",
                "planner": "planner_agent"
            }
        )
        
        # From cake agent, continue to other agents
        workflow.add_conditional_edges(
            "cake_agent",
            self._route_after_cake,
            {
                "venue": "venue_agent",
                "catering": "catering_agent",
                "budget": "budget_agent",
                "vendor": "vendor_agent",
                "planner": "planner_agent"
            }
        )
        
        # From venue agent, continue to other agents
        workflow.add_conditional_edges(
            "venue_agent",
            self._route_after_venue,
            {
                "catering": "catering_agent",
                "budget": "budget_agent",
                "vendor": "vendor_agent",
                "planner": "planner_agent"
            }
        )
        
        # From catering agent, continue to other agents
        workflow.add_conditional_edges(
            "catering_agent",
            self._route_after_catering,
            {
                "budget": "budget_agent",
                "vendor": "vendor_agent",
                "planner": "planner_agent"
            }
        )
        
        # From budget agent, continue to vendor and planner
        workflow.add_conditional_edges(
            "budget_agent",
            self._route_after_budget,
            {
                "vendor": "vendor_agent",
                "planner": "planner_agent"
            }
        )
        
        # From vendor agent, go to planner
        workflow.add_edge("vendor_agent", "planner_agent")
        
        # Planner agent is the final step
        workflow.add_edge("planner_agent", END)
        
        self.graph = workflow.compile()
        return self.graph
    
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
        """Execute the workflow asynchronously"""
        try:
            # Execute the graph
            final_state = await self.graph.ainvoke(initial_state)
            
            # Update final state
            await update_workflow_status(initial_state["event_id"], "completed")
            
            logger.info("Workflow completed", 
                       event_id=initial_state["event_id"],
                       final_plan_keys=list(final_state.get("final_plan", {}).keys()))
            
        except Exception as e:
            logger.error("Workflow execution failed", 
                        event_id=initial_state["event_id"], 
                        error=str(e))
            await update_workflow_status(initial_state["event_id"], "error")
    
    # Node implementations
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
            
            logger.info("Theme agent completed", 
                       event_id=state["event_id"],
                       theme=result.result.get("primary_theme"))
            
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
    
    # Routing functions
    def _route_after_classification(self, state: OrchestrationState) -> str:
        """Route after input classification"""
        classified_inputs = state["agent_results"].get("input_classifier", {}).get("classified_inputs", {})
        
        # Determine which agents to run based on classified inputs
        if "cake" in classified_inputs:
            return "cake"
        elif "theme" in classified_inputs:
            return "theme"
        else:
            return "theme"  # Default to theme
    
    def _route_after_theme(self, state: OrchestrationState) -> str:
        """Route after theme agent"""
        classified_inputs = state["agent_results"].get("input_classifier", {}).get("classified_inputs", {})
        
        if "cake" in classified_inputs and "cake_agent" not in state["agent_results"]:
            return "cake"
        elif "venue" in classified_inputs and "venue_agent" not in state["agent_results"]:
            return "venue"
        elif "catering" in classified_inputs and "catering_agent" not in state["agent_results"]:
            return "catering"
        else:
            return "budget"  # Move to budget calculation
    
    def _route_after_cake(self, state: OrchestrationState) -> str:
        """Route after cake agent"""
        classified_inputs = state["agent_results"].get("input_classifier", {}).get("classified_inputs", {})
        
        if "venue" in classified_inputs and "venue_agent" not in state["agent_results"]:
            return "venue"
        elif "catering" in classified_inputs and "catering_agent" not in state["agent_results"]:
            return "catering"
        else:
            return "budget"
    
    def _route_after_venue(self, state: OrchestrationState) -> str:
        """Route after venue agent"""
        classified_inputs = state["agent_results"].get("input_classifier", {}).get("classified_inputs", {})
        
        if "catering" in classified_inputs and "catering_agent" not in state["agent_results"]:
            return "catering"
        else:
            return "budget"
    
    def _route_after_catering(self, state: OrchestrationState) -> str:
        """Route after catering agent"""
        return "budget"
    
    def _route_after_budget(self, state: OrchestrationState) -> str:
        """Route after budget agent"""
        return "vendor"
    
    def _generate_recommendations(self, agent_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on agent results"""
        recommendations = []
        
        theme_result = agent_results.get("theme_agent", {})
        if theme_result:
            theme = theme_result.get("primary_theme", "general")
            recommendations.append(f"Focus on {theme} theme decorations")
        
        budget_result = agent_results.get("budget_agent", {})
        if budget_result:
            total_max = budget_result.get("total_budget", {}).get("max", 0)
            if total_max > 1500:
                recommendations.append("Consider booking vendors early for better rates")
            else:
                recommendations.append("Focus on DIY elements to stay within budget")
        
        return recommendations
    
    def _generate_next_steps(self, agent_results: Dict[str, Any]) -> List[str]:
        """Generate next steps for the user"""
        return [
            "Review and approve the generated plan",
            "Contact suggested vendors for quotes",
            "Book venue and key vendors",
            "Create detailed timeline",
            "Send invitations to guests"
        ]
    
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
        from app.services.local_memory_store import add_user_feedback
        await add_user_feedback(event_id, feedback)
        
        # Could trigger re-execution of specific agents based on feedback
        logger.info("User feedback added", event_id=event_id, feedback_keys=list(feedback.keys()))


# Global orchestrator instance
_orchestrator: Optional[LangGraphOrchestrator] = None


def get_orchestrator() -> LangGraphOrchestrator:
    """Get global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = LangGraphOrchestrator()
    return _orchestrator
