"""
In-Memory Party State Store

Thread-safe state management for party planning sessions.
Stores current state of each party (inputs, agent results, budget, plan).

Production Migration Path:
Replace in-memory dict with Redis for distributed state.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field, asdict
import json

from app.core.logging import logger


@dataclass
class PartyInput:
    """Single user input"""
    input_id: str
    content: str
    source_type: str  # text, image, url, upload
    tags: List[str] = field(default_factory=list)
    added_by: str = ""
    added_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result from an agent execution"""
    agent_name: str
    status: str  # running, completed, failed
    result: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    execution_time_ms: float = 0.0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


@dataclass
class PartyState:
    """
    Complete state for a party planning session.

    This is the single source of truth for all party data.
    """
    party_id: str
    status: str = "initializing"  # initializing, planning, completed, error

    # User inputs
    inputs: List[PartyInput] = field(default_factory=list)

    # Agent states
    active_agents: Dict[str, AgentResult] = field(default_factory=dict)

    # Budget (computed by BudgetAgent)
    budget: Optional[Dict[str, Any]] = None

    # Final plan (computed by FinalPlanner)
    final_plan: Optional[Dict[str, Any]] = None

    # User feedback
    user_feedback: List[Dict[str, Any]] = field(default_factory=list)

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Version (for optimistic locking)
    version: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

    def get_input_by_id(self, input_id: str) -> Optional[PartyInput]:
        """Get input by ID"""
        for inp in self.inputs:
            if inp.input_id == input_id:
                return inp
        return None

    def get_agent_result(self, agent_name: str) -> Optional[AgentResult]:
        """Get agent result by name"""
        return self.active_agents.get(agent_name)

    def get_completed_agents(self) -> List[str]:
        """Get list of completed agent names"""
        return [
            name for name, result in self.active_agents.items()
            if result.status == "completed"
        ]

    def get_running_agents(self) -> List[str]:
        """Get list of running agent names"""
        return [
            name for name, result in self.active_agents.items()
            if result.status == "running"
        ]

    def get_failed_agents(self) -> List[str]:
        """Get list of failed agent names"""
        return [
            name for name, result in self.active_agents.items()
            if result.status == "failed"
        ]


class PartyStateStore:
    """
    In-memory state store for party planning sessions.

    Thread-safe with asyncio.Lock per party.
    Supports CRUD operations and atomic updates.

    Production equivalent: Redis with key pattern party:{party_id}:*
    """

    def __init__(self):
        """Initialize state store"""
        # party_id -> PartyState
        self._states: Dict[str, PartyState] = {}

        # party_id -> asyncio.Lock (for thread-safe updates)
        self._locks: Dict[str, asyncio.Lock] = {}

        logger.info("Party state store initialized")

    async def create_party(
        self,
        party_id: str,
        initial_inputs: Optional[List[Dict[str, Any]]] = None
    ) -> PartyState:
        """
        Create new party state.

        Args:
            party_id: Unique party identifier
            initial_inputs: Optional list of initial inputs

        Returns:
            Created PartyState

        Raises:
            ValueError: If party already exists
        """
        if party_id in self._states:
            raise ValueError(f"Party {party_id} already exists")

        # Create lock for this party
        self._locks[party_id] = asyncio.Lock()

        # Create state
        state = PartyState(party_id=party_id)

        # Add initial inputs
        if initial_inputs:
            for inp_data in initial_inputs:
                input_obj = PartyInput(
                    input_id=inp_data.get("input_id", f"inp_{len(state.inputs) + 1}"),
                    content=inp_data.get("content", ""),
                    source_type=inp_data.get("source_type", "text"),
                    tags=inp_data.get("tags", []),
                    added_by=inp_data.get("added_by", "user"),
                    metadata=inp_data.get("metadata", {})
                )
                state.inputs.append(input_obj)

        state.status = "planning"
        self._states[party_id] = state

        logger.info(
            "Party created",
            party_id=party_id,
            initial_inputs=len(state.inputs)
        )

        return state

    async def get_party(self, party_id: str) -> Optional[PartyState]:
        """
        Get party state by ID.

        Args:
            party_id: Party identifier

        Returns:
            PartyState if exists, None otherwise
        """
        return self._states.get(party_id)

    async def update_party(
        self,
        party_id: str,
        updates: Dict[str, Any]
    ) -> PartyState:
        """
        Update party state (atomic operation).

        Args:
            party_id: Party identifier
            updates: Dictionary of fields to update

        Returns:
            Updated PartyState

        Raises:
            ValueError: If party doesn't exist
        """
        state = self._states.get(party_id)
        if not state:
            raise ValueError(f"Party {party_id} not found")

        # Acquire lock for thread-safe update
        async with self._locks[party_id]:
            # Apply updates
            for key, value in updates.items():
                if hasattr(state, key):
                    setattr(state, key, value)

            # Update timestamp and version
            state.updated_at = datetime.utcnow().isoformat()
            state.version += 1

            logger.debug(
                "Party updated",
                party_id=party_id,
                updated_fields=list(updates.keys()),
                version=state.version
            )

        return state

    async def add_input(
        self,
        party_id: str,
        input_data: Dict[str, Any]
    ) -> PartyInput:
        """
        Add input to party.

        Args:
            party_id: Party identifier
            input_data: Input data dictionary

        Returns:
            Created PartyInput

        Raises:
            ValueError: If party doesn't exist
        """
        state = self._states.get(party_id)
        if not state:
            raise ValueError(f"Party {party_id} not found")

        async with self._locks[party_id]:
            input_obj = PartyInput(
                input_id=input_data.get("input_id", f"inp_{len(state.inputs) + 1}"),
                content=input_data["content"],
                source_type=input_data.get("source_type", "text"),
                tags=input_data.get("tags", []),
                added_by=input_data.get("added_by", "user"),
                metadata=input_data.get("metadata", {})
            )

            state.inputs.append(input_obj)
            state.updated_at = datetime.utcnow().isoformat()
            state.version += 1

            logger.info(
                "Input added",
                party_id=party_id,
                input_id=input_obj.input_id,
                total_inputs=len(state.inputs)
            )

        return input_obj

    async def remove_input(
        self,
        party_id: str,
        input_id: str
    ) -> bool:
        """
        Remove input from party.

        Args:
            party_id: Party identifier
            input_id: Input identifier

        Returns:
            True if removed, False if not found

        Raises:
            ValueError: If party doesn't exist
        """
        state = self._states.get(party_id)
        if not state:
            raise ValueError(f"Party {party_id} not found")

        async with self._locks[party_id]:
            original_count = len(state.inputs)
            state.inputs = [inp for inp in state.inputs if inp.input_id != input_id]

            removed = len(state.inputs) < original_count

            if removed:
                state.updated_at = datetime.utcnow().isoformat()
                state.version += 1

                logger.info(
                    "Input removed",
                    party_id=party_id,
                    input_id=input_id,
                    remaining_inputs=len(state.inputs)
                )

        return removed

    async def set_agent_result(
        self,
        party_id: str,
        agent_name: str,
        result: Dict[str, Any],
        confidence: float = 1.0,
        execution_time_ms: float = 0.0,
        status: str = "completed"
    ) -> AgentResult:
        """
        Set agent result.

        Args:
            party_id: Party identifier
            agent_name: Agent name
            result: Agent result data
            confidence: Confidence score (0.0-1.0)
            execution_time_ms: Execution time in milliseconds
            status: Agent status (running, completed, failed)

        Returns:
            Created/updated AgentResult

        Raises:
            ValueError: If party doesn't exist
        """
        state = self._states.get(party_id)
        if not state:
            raise ValueError(f"Party {party_id} not found")

        async with self._locks[party_id]:
            agent_result = AgentResult(
                agent_name=agent_name,
                status=status,
                result=result,
                confidence=confidence,
                execution_time_ms=execution_time_ms,
                completed_at=datetime.utcnow().isoformat() if status == "completed" else None
            )

            # Update or create agent result
            if agent_name in state.active_agents:
                # Preserve started_at if updating
                old_result = state.active_agents[agent_name]
                agent_result.started_at = old_result.started_at

            state.active_agents[agent_name] = agent_result
            state.updated_at = datetime.utcnow().isoformat()
            state.version += 1

            logger.info(
                "Agent result set",
                party_id=party_id,
                agent_name=agent_name,
                status=status,
                confidence=confidence
            )

        return agent_result

    async def set_agent_started(
        self,
        party_id: str,
        agent_name: str
    ) -> AgentResult:
        """Mark agent as started"""
        state = self._states.get(party_id)
        if not state:
            raise ValueError(f"Party {party_id} not found")

        async with self._locks[party_id]:
            agent_result = AgentResult(
                agent_name=agent_name,
                status="running",
                started_at=datetime.utcnow().isoformat()
            )

            state.active_agents[agent_name] = agent_result
            state.updated_at = datetime.utcnow().isoformat()

            logger.info(
                "Agent started",
                party_id=party_id,
                agent_name=agent_name
            )

        return agent_result

    async def set_agent_failed(
        self,
        party_id: str,
        agent_name: str,
        error: str
    ) -> AgentResult:
        """Mark agent as failed"""
        state = self._states.get(party_id)
        if not state:
            raise ValueError(f"Party {party_id} not found")

        async with self._locks[party_id]:
            # Get existing result to preserve started_at
            existing = state.active_agents.get(agent_name)

            agent_result = AgentResult(
                agent_name=agent_name,
                status="failed",
                error=error,
                started_at=existing.started_at if existing else None,
                completed_at=datetime.utcnow().isoformat()
            )

            state.active_agents[agent_name] = agent_result
            state.updated_at = datetime.utcnow().isoformat()

            logger.error(
                "Agent failed",
                party_id=party_id,
                agent_name=agent_name,
                error=error
            )

        return agent_result

    async def remove_agent_result(
        self,
        party_id: str,
        agent_name: str
    ) -> bool:
        """
        Remove agent result (e.g., when no longer needed).

        Args:
            party_id: Party identifier
            agent_name: Agent name

        Returns:
            True if removed, False if not found
        """
        state = self._states.get(party_id)
        if not state:
            raise ValueError(f"Party {party_id} not found")

        async with self._locks[party_id]:
            if agent_name in state.active_agents:
                del state.active_agents[agent_name]
                state.updated_at = datetime.utcnow().isoformat()
                state.version += 1

                logger.info(
                    "Agent result removed",
                    party_id=party_id,
                    agent_name=agent_name
                )
                return True

        return False

    async def set_budget(
        self,
        party_id: str,
        budget: Dict[str, Any]
    ):
        """Set budget for party"""
        await self.update_party(party_id, {"budget": budget})

    async def set_final_plan(
        self,
        party_id: str,
        final_plan: Dict[str, Any]
    ):
        """Set final plan for party"""
        await self.update_party(party_id, {"final_plan": final_plan})

    async def delete_party(self, party_id: str) -> bool:
        """
        Delete party state.

        Args:
            party_id: Party identifier

        Returns:
            True if deleted, False if not found
        """
        if party_id in self._states:
            async with self._locks[party_id]:
                del self._states[party_id]
                del self._locks[party_id]

                logger.info("Party deleted", party_id=party_id)
                return True

        return False

    def get_all_party_ids(self) -> List[str]:
        """Get list of all party IDs"""
        return list(self._states.keys())

    def get_stats(self) -> Dict[str, Any]:
        """Get state store statistics"""
        total_parties = len(self._states)
        total_inputs = sum(len(state.inputs) for state in self._states.values())
        total_agent_results = sum(
            len(state.active_agents) for state in self._states.values()
        )

        status_counts = {}
        for state in self._states.values():
            status_counts[state.status] = status_counts.get(state.status, 0) + 1

        return {
            "total_parties": total_parties,
            "total_inputs": total_inputs,
            "total_agent_results": total_agent_results,
            "status_counts": status_counts,
        }


# Global state store instance
_state_store: Optional[PartyStateStore] = None


def get_state_store() -> PartyStateStore:
    """
    Get global state store instance (singleton pattern).

    Returns:
        Global PartyStateStore instance
    """
    global _state_store
    if _state_store is None:
        _state_store = PartyStateStore()
    return _state_store


def reset_state_store():
    """Reset global state store (useful for testing)"""
    global _state_store
    _state_store = PartyStateStore()
    logger.info("State store reset")


# Export public API
__all__ = [
    "PartyInput",
    "AgentResult",
    "PartyState",
    "PartyStateStore",
    "get_state_store",
    "reset_state_store",
]
