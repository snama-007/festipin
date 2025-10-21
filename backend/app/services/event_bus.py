"""
In-Memory Event Bus using asyncio.Queue

Production-ready pub/sub pattern that can be swapped with Kafka later.
Supports multiple subscribers per topic with fan-out delivery.
"""

import asyncio
from typing import Dict, List, Set, AsyncIterator, Optional, Callable
from collections import defaultdict
import json
from datetime import datetime

from app.models.events import BaseEvent
from app.core.logging import logger


class EventBus:
    """
    In-memory event bus using asyncio.Queue for pub/sub pattern.

    Features:
    - Multiple subscribers per topic (fan-out)
    - Type-safe event publishing and subscription
    - Non-blocking async operations
    - Event history for debugging
    - Graceful shutdown

    Production Migration Path:
    Replace asyncio.Queue with Kafka producer/consumer while keeping
    the same API surface.
    """

    # Supported event topics
    TOPICS = {
        "party.input.added",
        "party.input.removed",
        "party.agent.should_execute",
        "party.agent.started",
        "party.agent.completed",
        "party.agent.failed",
        "party.agent.data_removed",
        "party.budget.updated",
        "party.plan.updated",
    }

    def __init__(self, max_queue_size: int = 1000):
        """
        Initialize event bus.

        Args:
            max_queue_size: Maximum events per queue (prevents memory overflow)
        """
        self.max_queue_size = max_queue_size

        # Topic -> List of subscriber queues
        self._subscribers: Dict[str, List[asyncio.Queue]] = defaultdict(list)

        # Event history for debugging (last 1000 events)
        self._event_history: List[Dict] = []
        self._max_history = 1000

        # Shutdown flag
        self._shutdown = False

        # Metrics
        self._metrics = {
            "total_published": 0,
            "total_delivered": 0,
            "failed_deliveries": 0,
        }

        logger.info(
            "Event bus initialized",
            topics=list(self.TOPICS),
            max_queue_size=max_queue_size
        )

    async def publish(self, topic: str, event: BaseEvent) -> None:
        """
        Publish event to all subscribers of a topic.

        Args:
            topic: Event topic (must be in TOPICS set)
            event: Event to publish (must be BaseEvent subclass)

        Raises:
            ValueError: If topic is not supported
        """
        if self._shutdown:
            logger.warning("Event bus is shutdown, ignoring publish", topic=topic)
            return

        if topic not in self.TOPICS:
            raise ValueError(f"Unknown topic: {topic}. Supported topics: {self.TOPICS}")

        # Ensure event_type matches topic
        if event.event_type != topic:
            logger.warning(
                "Event type mismatch",
                event_type=event.event_type,
                topic=topic
            )

        # Record to history
        self._add_to_history(event)

        # Update metrics
        self._metrics["total_published"] += 1

        # Get subscribers for this topic
        subscribers = self._subscribers.get(topic, [])

        if not subscribers:
            logger.debug(
                "No subscribers for topic",
                topic=topic,
                event_id=event.event_id
            )
            return

        # Publish to all subscribers (fan-out)
        delivered_count = 0
        for queue in subscribers:
            try:
                # Non-blocking put with timeout
                await asyncio.wait_for(
                    queue.put(event),
                    timeout=1.0
                )
                delivered_count += 1
            except asyncio.TimeoutError:
                logger.error(
                    "Failed to deliver event (queue full)",
                    topic=topic,
                    event_id=event.event_id,
                    queue_size=queue.qsize()
                )
                self._metrics["failed_deliveries"] += 1
            except Exception as e:
                logger.error(
                    "Failed to deliver event",
                    topic=topic,
                    event_id=event.event_id,
                    error=str(e)
                )
                self._metrics["failed_deliveries"] += 1

        self._metrics["total_delivered"] += delivered_count

        logger.debug(
            "Event published",
            topic=topic,
            event_id=event.event_id,
            party_id=event.party_id,
            subscribers=delivered_count
        )

    async def subscribe(self, topic: str) -> AsyncIterator[BaseEvent]:
        """
        Subscribe to a topic and receive events as async iterator.

        Usage:
            async for event in event_bus.subscribe("party.input.added"):
                await handle_event(event)

        Args:
            topic: Topic to subscribe to

        Yields:
            Events published to this topic

        Raises:
            ValueError: If topic is not supported
        """
        if topic not in self.TOPICS:
            raise ValueError(f"Unknown topic: {topic}. Supported topics: {self.TOPICS}")

        # Create queue for this subscriber
        queue: asyncio.Queue = asyncio.Queue(maxsize=self.max_queue_size)

        # Register subscriber
        self._subscribers[topic].append(queue)

        logger.info(
            "Subscriber registered",
            topic=topic,
            total_subscribers=len(self._subscribers[topic])
        )

        try:
            # Yield events from queue
            while not self._shutdown:
                try:
                    # Wait for event with timeout (allows checking shutdown flag)
                    event = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield event
                except asyncio.TimeoutError:
                    # No event received, continue (allows shutdown check)
                    continue
                except Exception as e:
                    logger.error(
                        "Error receiving event from queue",
                        topic=topic,
                        error=str(e)
                    )
                    break
        finally:
            # Cleanup: Remove subscriber
            if queue in self._subscribers[topic]:
                self._subscribers[topic].remove(queue)

            logger.info(
                "Subscriber unregistered",
                topic=topic,
                remaining_subscribers=len(self._subscribers[topic])
            )

    def subscribe_callback(
        self,
        topic: str,
        callback: Callable[[BaseEvent], asyncio.Future]
    ) -> asyncio.Task:
        """
        Subscribe to topic with callback function.
        Returns task that can be cancelled.

        Usage:
            async def handle_event(event):
                print(f"Received: {event}")

            task = event_bus.subscribe_callback("party.input.added", handle_event)

        Args:
            topic: Topic to subscribe to
            callback: Async function to call for each event

        Returns:
            Task running the subscription
        """
        async def subscription_loop():
            async for event in self.subscribe(topic):
                try:
                    await callback(event)
                except Exception as e:
                    logger.error(
                        "Error in subscription callback",
                        topic=topic,
                        event_id=event.event_id,
                        error=str(e)
                    )

        task = asyncio.create_task(subscription_loop())
        logger.info("Callback subscription started", topic=topic)
        return task

    def get_subscriber_count(self, topic: str) -> int:
        """Get number of active subscribers for a topic"""
        return len(self._subscribers.get(topic, []))

    def get_all_subscriber_counts(self) -> Dict[str, int]:
        """Get subscriber counts for all topics"""
        return {
            topic: len(subscribers)
            for topic, subscribers in self._subscribers.items()
        }

    def get_metrics(self) -> Dict[str, int]:
        """Get event bus metrics"""
        return {
            **self._metrics,
            "active_topics": len([t for t, s in self._subscribers.items() if s]),
            "total_subscribers": sum(len(s) for s in self._subscribers.values()),
        }

    def get_event_history(self, limit: int = 100) -> List[Dict]:
        """
        Get recent event history for debugging.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of event dictionaries (most recent first)
        """
        return self._event_history[-limit:][::-1]

    def get_events_by_party(self, party_id: str, limit: int = 100) -> List[Dict]:
        """
        Get event history for specific party.

        Args:
            party_id: Party ID to filter by
            limit: Maximum number of events to return

        Returns:
            List of event dictionaries for this party
        """
        party_events = [
            e for e in self._event_history
            if e.get("party_id") == party_id
        ]
        return party_events[-limit:][::-1]

    async def shutdown(self):
        """Gracefully shutdown event bus"""
        logger.info("Shutting down event bus...")
        self._shutdown = True

        # Give time for in-flight events to complete
        await asyncio.sleep(0.5)

        # Clear all queues
        for topic_queues in self._subscribers.values():
            for queue in topic_queues:
                while not queue.empty():
                    try:
                        queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break

        logger.info(
            "Event bus shutdown complete",
            final_metrics=self.get_metrics()
        )

    def _add_to_history(self, event: BaseEvent):
        """Add event to history (for debugging)"""
        try:
            event_dict = event.model_dump()
            event_dict["_recorded_at"] = datetime.utcnow().isoformat()

            self._event_history.append(event_dict)

            # Trim history if too large
            if len(self._event_history) > self._max_history:
                self._event_history = self._event_history[-self._max_history:]
        except Exception as e:
            logger.error("Failed to add event to history", error=str(e))

    def clear_history(self):
        """Clear event history (useful for testing)"""
        self._event_history.clear()
        logger.info("Event history cleared")


# Global event bus instance
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """
    Get global event bus instance (singleton pattern).

    Returns:
        Global EventBus instance
    """
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def reset_event_bus():
    """
    Reset global event bus (useful for testing).
    Creates a fresh EventBus instance.
    """
    global _event_bus
    if _event_bus:
        # Note: In production, should call shutdown() first
        pass
    _event_bus = EventBus()
    logger.info("Event bus reset")


# Export public API
__all__ = [
    "EventBus",
    "get_event_bus",
    "reset_event_bus",
]
