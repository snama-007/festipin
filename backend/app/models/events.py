"""
Event Schema Models for Event-Driven Agent System

Pydantic models defining all event types that flow through the event bus.
These schemas ensure type safety and validation across the entire system.
"""

from typing import Dict, Any, List, Optional, Literal, Union
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


# ===== Base Event =====

class BaseEvent(BaseModel):
    """
    Base event structure for all events in the system.
    All events inherit from this base class.
    """
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    party_id: str = Field(..., description="Party session ID")
    event_type: str = Field(..., description="Type of event")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    correlation_id: str = Field(default_factory=lambda: f"corr_{uuid.uuid4().hex[:12]}")
    payload: Dict[str, Any] = Field(..., description="Event-specific data")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "evt_abc123",
                "party_id": "fp2025A12345",
                "event_type": "party.input.added",
                "timestamp": "2025-10-21T10:30:00Z",
                "correlation_id": "corr_xyz",
                "payload": {},
                "metadata": {}
            }
        }


# ===== Input Events =====

class InputAddedPayload(BaseModel):
    """Payload for input.added event"""
    input_id: str
    content: str
    source_type: Literal["text", "image", "url", "upload"]
    tags: List[str] = Field(default_factory=list)
    added_by: str
    metadata: Optional[Dict[str, Any]] = None


class InputAddedEvent(BaseEvent):
    """Event emitted when user adds a new input"""
    event_type: Literal["party.input.added"] = "party.input.added"
    payload: InputAddedPayload  # type: ignore


class InputRemovedPayload(BaseModel):
    """Payload for input.removed event"""
    input_id: str
    removed_by: str
    reason: Literal["user_action", "duplicate", "invalid"] = "user_action"


class InputRemovedEvent(BaseEvent):
    """Event emitted when user removes an input"""
    event_type: Literal["party.input.removed"] = "party.input.removed"
    payload: InputRemovedPayload  # type: ignore


# ===== Agent Execution Events =====

class AgentShouldExecutePayload(BaseModel):
    """Payload for agent.should_execute event"""
    agent_name: str
    execution_type: Literal["start", "rerun", "recalculate"]
    input_ids: List[str] = Field(default_factory=list)
    priority: int = Field(default=3, ge=1, le=5, description="1=highest, 5=lowest")
    reason: Optional[str] = None


class AgentShouldExecuteEvent(BaseEvent):
    """Event emitted when InputAnalyzer determines an agent should execute"""
    event_type: Literal["party.agent.should_execute"] = "party.agent.should_execute"
    payload: AgentShouldExecutePayload  # type: ignore


class AgentStartedPayload(BaseModel):
    """Payload for agent.started event"""
    agent_name: str
    execution_id: str
    input_count: int = 0
    message: Optional[str] = None


class AgentStartedEvent(BaseEvent):
    """Event emitted when an agent starts execution"""
    event_type: Literal["party.agent.started"] = "party.agent.started"
    payload: AgentStartedPayload  # type: ignore


class AgentCompletedPayload(BaseModel):
    """Payload for agent.completed event"""
    agent_name: str
    execution_id: str
    result: Dict[str, Any]
    confidence: float = Field(ge=0.0, le=1.0)
    execution_time_ms: float


class AgentCompletedEvent(BaseEvent):
    """Event emitted when an agent completes successfully"""
    event_type: Literal["party.agent.completed"] = "party.agent.completed"
    payload: AgentCompletedPayload  # type: ignore


class AgentFailedPayload(BaseModel):
    """Payload for agent.failed event"""
    agent_name: str
    execution_id: str
    error: str
    error_type: Literal["timeout", "validation", "external_api", "internal"] = "internal"
    retry_count: int = 0


class AgentFailedEvent(BaseEvent):
    """Event emitted when an agent fails"""
    event_type: Literal["party.agent.failed"] = "party.agent.failed"
    payload: AgentFailedPayload  # type: ignore


class AgentDataRemovedPayload(BaseModel):
    """Payload for agent.data_removed event"""
    agent_name: str
    reason: str
    removed_input_id: Optional[str] = None


class AgentDataRemovedEvent(BaseEvent):
    """Event emitted when an agent's data is removed (e.g., all theme inputs removed)"""
    event_type: Literal["party.agent.data_removed"] = "party.agent.data_removed"
    payload: AgentDataRemovedPayload  # type: ignore


# ===== Budget Events =====

class BudgetRange(BaseModel):
    """Budget range with min/max"""
    min: int
    max: int
    note: Optional[str] = None


class BudgetUpdatedPayload(BaseModel):
    """Payload for budget.updated event"""
    total_budget: BudgetRange
    previous_total: Optional[BudgetRange] = None
    delta: Optional[BudgetRange] = None
    breakdown: Dict[str, BudgetRange]
    based_on_agents: List[str] = Field(default_factory=list)


class BudgetUpdatedEvent(BaseEvent):
    """Event emitted when budget is recalculated"""
    event_type: Literal["party.budget.updated"] = "party.budget.updated"
    payload: BudgetUpdatedPayload  # type: ignore


# ===== Plan Events =====

class PlanRecommendation(BaseModel):
    """Single recommendation in the plan"""
    category: str
    priority: Literal["low", "medium", "high", "critical"]
    description: str


class PlanUpdatedPayload(BaseModel):
    """Payload for plan.updated event"""
    completion_percent: int = Field(ge=0, le=100)
    recommendations: List[PlanRecommendation] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    missing_agents: List[str] = Field(default_factory=list)
    active_agents: List[str] = Field(default_factory=list)
    checklist_summary: Optional[Dict[str, int]] = None


class PlanUpdatedEvent(BaseEvent):
    """Event emitted when FinalPlanner updates the plan"""
    event_type: Literal["party.plan.updated"] = "party.plan.updated"
    payload: PlanUpdatedPayload  # type: ignore


# ===== WebSocket Events (Frontend-facing) =====

class WebSocketMessage(BaseModel):
    """
    Messages sent to frontend via WebSocket.
    Simplified version of internal events.
    """
    type: str = Field(..., description="Message type")
    agent: Optional[str] = None
    status: Optional[Literal["running", "completed", "failed"]] = None
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Optional[Dict[str, Any]] = None


# ===== Event Type Union =====

# Union type for all event types (useful for type checking)
Event = Union[
    InputAddedEvent,
    InputRemovedEvent,
    AgentShouldExecuteEvent,
    AgentStartedEvent,
    AgentCompletedEvent,
    AgentFailedEvent,
    AgentDataRemovedEvent,
    BudgetUpdatedEvent,
    PlanUpdatedEvent
]


# ===== Helper Functions =====

def create_input_added_event(
    party_id: str,
    input_id: str,
    content: str,
    source_type: str,
    tags: List[str],
    added_by: str
) -> InputAddedEvent:
    """Helper to create InputAddedEvent"""
    return InputAddedEvent(
        party_id=party_id,
        payload=InputAddedPayload(
            input_id=input_id,
            content=content,
            source_type=source_type,  # type: ignore
            tags=tags,
            added_by=added_by
        )
    )


def create_agent_should_execute_event(
    party_id: str,
    agent_name: str,
    execution_type: str,
    input_ids: List[str],
    priority: int = 3,
    correlation_id: Optional[str] = None
) -> AgentShouldExecuteEvent:
    """Helper to create AgentShouldExecuteEvent"""
    event = AgentShouldExecuteEvent(
        party_id=party_id,
        payload=AgentShouldExecutePayload(
            agent_name=agent_name,
            execution_type=execution_type,  # type: ignore
            input_ids=input_ids,
            priority=priority
        )
    )
    if correlation_id:
        event.correlation_id = correlation_id
    return event


def create_agent_started_event(
    party_id: str,
    agent_name: str,
    execution_id: str,
    message: Optional[str] = None,
    correlation_id: Optional[str] = None
) -> AgentStartedEvent:
    """Helper to create AgentStartedEvent"""
    event = AgentStartedEvent(
        party_id=party_id,
        payload=AgentStartedPayload(
            agent_name=agent_name,
            execution_id=execution_id,
            message=message or f"Starting {agent_name}..."
        )
    )
    if correlation_id:
        event.correlation_id = correlation_id
    return event


def create_agent_completed_event(
    party_id: str,
    agent_name: str,
    execution_id: str,
    result: Dict[str, Any],
    confidence: float,
    execution_time_ms: float,
    correlation_id: Optional[str] = None
) -> AgentCompletedEvent:
    """Helper to create AgentCompletedEvent"""
    event = AgentCompletedEvent(
        party_id=party_id,
        payload=AgentCompletedPayload(
            agent_name=agent_name,
            execution_id=execution_id,
            result=result,
            confidence=confidence,
            execution_time_ms=execution_time_ms
        )
    )
    if correlation_id:
        event.correlation_id = correlation_id
    return event


def create_agent_failed_event(
    party_id: str,
    agent_name: str,
    execution_id: str,
    error: str,
    error_type: str = "internal",
    correlation_id: Optional[str] = None
) -> AgentFailedEvent:
    """Helper to create AgentFailedEvent"""
    event = AgentFailedEvent(
        party_id=party_id,
        payload=AgentFailedPayload(
            agent_name=agent_name,
            execution_id=execution_id,
            error=error,
            error_type=error_type  # type: ignore
        )
    )
    if correlation_id:
        event.correlation_id = correlation_id
    return event


def create_budget_updated_event(
    party_id: str,
    total_budget: Dict[str, int],
    breakdown: Dict[str, Dict[str, int]],
    based_on_agents: List[str],
    correlation_id: Optional[str] = None
) -> BudgetUpdatedEvent:
    """Helper to create BudgetUpdatedEvent"""
    event = BudgetUpdatedEvent(
        party_id=party_id,
        payload=BudgetUpdatedPayload(
            total_budget=BudgetRange(**total_budget),
            breakdown={k: BudgetRange(**v) for k, v in breakdown.items()},
            based_on_agents=based_on_agents
        )
    )
    if correlation_id:
        event.correlation_id = correlation_id
    return event


def create_input_removed_event(
    party_id: str,
    input_id: str,
    removed_by: str,
    reason: str = "user_action"
) -> InputRemovedEvent:
    """Helper to create InputRemovedEvent"""
    return InputRemovedEvent(
        party_id=party_id,
        payload=InputRemovedPayload(
            input_id=input_id,
            removed_by=removed_by,
            reason=reason  # type: ignore
        )
    )


def create_plan_updated_event(
    party_id: str,
    completion_percent: int,
    recommendations: List[Dict[str, str]],
    next_steps: List[str],
    active_agents: List[str],
    missing_agents: List[str],
    correlation_id: Optional[str] = None
) -> PlanUpdatedEvent:
    """Helper to create PlanUpdatedEvent"""
    event = PlanUpdatedEvent(
        party_id=party_id,
        payload=PlanUpdatedPayload(
            completion_percent=completion_percent,
            recommendations=[PlanRecommendation(**r) for r in recommendations],
            next_steps=next_steps,
            active_agents=active_agents,
            missing_agents=missing_agents
        )
    )
    if correlation_id:
        event.correlation_id = correlation_id
    return event


# Export all event types and helpers
__all__ = [
    # Base
    "BaseEvent",
    # Input events
    "InputAddedEvent",
    "InputRemovedEvent",
    # Agent events
    "AgentShouldExecuteEvent",
    "AgentStartedEvent",
    "AgentCompletedEvent",
    "AgentFailedEvent",
    "AgentDataRemovedEvent",
    # Budget & Plan events
    "BudgetUpdatedEvent",
    "PlanUpdatedEvent",
    # WebSocket
    "WebSocketMessage",
    # Union type
    "Event",
    # Helpers
    "create_input_added_event",
    "create_input_removed_event",
    "create_agent_should_execute_event",
    "create_agent_started_event",
    "create_agent_completed_event",
    "create_agent_failed_event",
    "create_budget_updated_event",
    "create_plan_updated_event",
]
