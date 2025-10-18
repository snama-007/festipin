# 🏗️ **Production-Grade Party Planning System Architecture**
## *Scalable to 100K Concurrent Users with Dynamic Agent Orchestration*

**Document Version:** 1.0
**Last Updated:** October 18, 2025
**Status:** Architecture Design & Implementation Guide

---

## 📊 **Executive Summary**

### **Core Requirements**
1. ✅ **Always-Running Agents**: InputClassifier + PlannerFinal (continuous)
2. ✅ **Dynamic Agents**: Theme, Cake, Venue, Catering, Vendor (start/stop)
3. ✅ **Dynamic Inputs**: Add/Remove inputs → agents recalculate
4. ✅ **Budget Recalculation**: Auto-updates when any agent data changes
5. ✅ **Scale**: 100K concurrent party planning sessions
6. ✅ **Training Pipeline**: Capture all interactions for ML

### **Key Architectural Principles**
- **Event-Driven**: All state changes flow through Kafka event streams
- **CQRS Pattern**: Separate write (events) and read (cache) paths
- **Event Sourcing**: Complete audit trail of all party planning decisions
- **Reactive**: Agents respond to events, not scheduled polling
- **Horizontally Scalable**: Auto-scale from 10 to 500 pods based on load

---

## 🎯 **System Architecture Overview**

```
┌─────────────────────────────────────────────────────────────────────┐
│                     USER LAYER (Web/Mobile)                          │
│  100K concurrent users × avg 50 inputs/session = 5M inputs/hour     │
└────────────────────────┬────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────────┐
│                   API GATEWAY LAYER                                  │
│  • Rate Limiting (1000 req/sec/user)                                │
│  • Authentication (JWT)                                              │
│  • Load Balancing (Round Robin + Least Connections)                 │
│  • CDN (CloudFlare/CloudFront) for static assets                    │
└────────────────────────┬────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────────┐
│               EVENT-DRIVEN ORCHESTRATION LAYER                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Apache Kafka / AWS Kinesis (Event Stream)                   │  │
│  │  Partitions: 1000 (by party_id % 1000)                       │  │
│  │  Throughput: 100K events/sec                                 │  │
│  │                                                               │  │
│  │  Topics:                                                      │  │
│  │    • party.input.added                                       │  │
│  │    • party.input.removed                                     │  │
│  │    • party.agent.started                                     │  │
│  │    • party.agent.completed                                   │  │
│  │    • party.agent.failed                                      │  │
│  │    • party.budget.recalculated                               │  │
│  │    • party.plan.updated                                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────────┐
│                    AGENT EXECUTION LAYER                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │ ALWAYS-ON AGENTS │  │ DYNAMIC AGENTS   │  │  CONTROL PLANE   │ │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤ │
│  │ • InputAnalyzer  │  │ • ThemeAgent     │  │ • AgentRegistry  │ │
│  │   (streaming)    │  │ • CakeAgent      │  │ • StateManager   │ │
│  │                  │  │ • VenueAgent     │  │ • DependencyDAG  │ │
│  │ • PlannerFinal   │  │ • CateringAgent  │  │ • HealthChecker  │ │
│  │   (reactive)     │  │ • VendorAgent    │  │                  │ │
│  │                  │  │ • BudgetAgent    │  │                  │ │
│  │ • HealthMonitor  │  │   (reactive)     │  │                  │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
│                                                                      │
│  Deployment: Kubernetes Pods (Auto-scaling: 10-500 pods)            │
│  Resource Limits: 2 CPU, 4GB RAM per pod                            │
└────────────────────────┬────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────────┐
│                      DATA LAYER                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │   PostgreSQL     │  │   Redis Cache    │  │  Vector DB       │ │
│  │  (Party State)   │  │ (Session State)  │  │  (Embeddings)    │ │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤ │
│  │ • party_events   │  │ • active_parties │  │ • vendor_vectors │ │
│  │ • agent_results  │  │ • agent_cache    │  │ • venue_vectors  │ │
│  │ • input_history  │  │ • user_sessions  │  │ • theme_vectors  │ │
│  │ • budget_logs    │  │ TTL: 24 hours    │  │                  │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              S3 / Object Storage                              │  │
│  │  • training_data/events/{year}/{month}/{day}/{hour}/         │  │
│  │  • user_uploads/{party_id}/images/                           │  │
│  │  • backups/daily/{party_id}.json                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────────┐
│                ML TRAINING PIPELINE (Offline)                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Apache Spark / AWS EMR (Batch Processing)                   │  │
│  │  • Feature Engineering: User preferences, agent patterns     │  │
│  │  • Model Training: Input classification, budget prediction   │  │
│  │  • A/B Testing: Agent effectiveness metrics                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 **Agent Lifecycle State Machine**

### **1. Always-Running Agents**

#### **InputAnalyzer Agent (Always Active)**

```
┌─────────────────────────────────────────────────────────────┐
│              INPUT ANALYZER AGENT (Always Active)            │
├─────────────────────────────────────────────────────────────┤
│  State: RUNNING (24/7)                                       │
│  Trigger: Event stream (party.input.added / removed)        │
│  Output: Classification + Agent Execution Plan               │
│                                                              │
│  Flow:                                                       │
│    1. Listen to Kafka topic: party.input.*                  │
│    2. For each event:                                       │
│       a. Classify input (theme/cake/venue/catering/vendor)  │
│       b. Determine affected agents                          │
│       c. Emit events: party.agent.should_execute            │
│    3. Store classification in Redis (party:{id}:inputs)     │
└─────────────────────────────────────────────────────────────┘
```

**Responsibilities:**
- Continuous input analysis
- Real-time classification using keyword matching + ML models
- Routing logic to determine which agents need to start/stop/rerun
- Dependency graph calculation for cascade effects

**Deployment:**
- Kubernetes Deployment: 3-10 replicas
- Auto-scaling based on Kafka consumer lag
- Resource limits: 1 CPU, 2GB RAM per replica

#### **PlannerFinal Agent (Always Reactive)**

```
┌─────────────────────────────────────────────────────────────┐
│           PLANNER FINAL AGENT (Always Reactive)              │
├─────────────────────────────────────────────────────────────┤
│  State: LISTENING (reactive)                                 │
│  Trigger: Any agent completion event                         │
│  Output: Updated final checklist + recommendations           │
│                                                              │
│  Flow:                                                       │
│    1. Listen to: party.agent.completed                      │
│    2. Fetch all agent results from Redis                    │
│    3. Recompute final plan:                                 │
│       a. Aggregate all recommendations                      │
│       b. Generate prioritized checklist                     │
│       c. Calculate completion percentage                    │
│    4. Emit: party.plan.updated                              │
│    5. Store in PostgreSQL + Redis                           │
└─────────────────────────────────────────────────────────────┘
```

**Responsibilities:**
- Real-time plan assembly
- Intelligent recommendation generation based on all agent outputs
- Completion percentage calculation
- Next steps generation
- Missing agent detection

**Deployment:**
- Kubernetes Deployment: 5-20 replicas
- Auto-scaling based on event throughput
- Resource limits: 1 CPU, 2GB RAM per replica

---

### **2. Dynamic Agents (Start/Stop on Demand)**

#### **State Transitions**

```
IDLE → STARTING → RUNNING → COMPLETED → IDLE
  ↑                                        │
  └────────────── (removed) ───────────────┘
```

#### **Theme Agent**

```
┌─────────────────────────────────────────────────────────────┐
│                THEME AGENT (Dynamic)                         │
├─────────────────────────────────────────────────────────────┤
│  States: IDLE → STARTING → RUNNING → COMPLETED → IDLE       │
│                                                              │
│  Lifecycle:                                                  │
│    IDLE:                                                     │
│      • Waiting for trigger                                  │
│      • No resources allocated                               │
│                                                              │
│    STARTING:                                                 │
│      • Triggered by: party.agent.should_execute             │
│      • Allocate resources (K8s pod spawn)                   │
│      • Load context from Redis                              │
│                                                              │
│    RUNNING:                                                  │
│      • Execute theme detection                              │
│      • Query vector DB for theme matches                    │
│      • Generate colors, decorations, activities             │
│                                                              │
│    COMPLETED:                                                │
│      • Store results in PostgreSQL + Redis                  │
│      • Emit: party.agent.completed                          │
│      • Trigger dependent agents (cake, venue, vendors)      │
│                                                              │
│    REMOVED (when input removed):                             │
│      • Delete theme results from DB                         │
│      • Emit: party.agent.data_removed                       │
│      • Trigger cascade: budget recalculation                │
└─────────────────────────────────────────────────────────────┘
```

**Triggers:**
- `party.agent.should_execute` with `agent_name: "theme_agent"`
- Input contains theme keywords: theme, decor, decoration, style, aesthetic

**Dependencies:**
- **Affects**: CakeAgent, VenueAgent, VendorAgent
- **Priority**: 1 (highest - runs first)

#### **Budget Agent (Reactive)**

```
┌─────────────────────────────────────────────────────────────┐
│                BUDGET AGENT (Reactive)                       │
├─────────────────────────────────────────────────────────────┤
│  State: LISTENING → RECALCULATING → COMPLETED → LISTENING   │
│                                                              │
│  Triggers:                                                   │
│    • party.agent.completed (any cost-related agent)         │
│    • party.agent.data_removed (any agent)                   │
│                                                              │
│  Flow:                                                       │
│    1. Fetch active agent results:                           │
│       - venue_agent → venue cost                            │
│       - cake_agent → cake cost                              │
│       - catering_agent → catering cost                      │
│       - vendor_agent → vendor costs                         │
│    2. Aggregate costs:                                      │
│       total_min = sum(agent.cost.min for all active)        │
│       total_max = sum(agent.cost.max for all active)        │
│    3. Calculate breakdown by category                       │
│    4. Emit: party.budget.recalculated                       │
│    5. Store in PostgreSQL + Redis                           │
└─────────────────────────────────────────────────────────────┘
```

**Recalculation Logic:**
- Always runs after any cost-affecting agent completes
- Removes costs when agent data is deleted
- Maintains historical budget snapshots for comparison

**Priority**: 4 (runs after all cost agents)

---

## 💾 **Data Models (PostgreSQL)**

### **1. Party Events Table (Event Sourcing)**

```sql
CREATE TABLE party_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    party_id VARCHAR(20) NOT NULL,  -- fp2025A12345
    event_type VARCHAR(50) NOT NULL, -- 'input_added', 'agent_completed', etc.
    event_version INT NOT NULL DEFAULT 1,
    aggregate_version INT NOT NULL, -- Event sequence per party

    -- Event payload (JSONB for flexibility)
    payload JSONB NOT NULL,

    -- Metadata
    user_id UUID,
    correlation_id UUID, -- For tracing
    causation_id UUID,   -- Event that caused this

    -- Timestamps
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Indexing
    CONSTRAINT party_events_party_version UNIQUE (party_id, aggregate_version)
);

CREATE INDEX idx_party_events_party_id ON party_events(party_id);
CREATE INDEX idx_party_events_event_type ON party_events(event_type);
CREATE INDEX idx_party_events_occurred_at ON party_events(occurred_at DESC);

-- Example event:
INSERT INTO party_events (party_id, event_type, aggregate_version, payload) VALUES (
    'fp2025A12345',
    'input_added',
    1,
    '{
        "input_id": "inp_abc123",
        "content": "jungle theme party for 75 guests",
        "source_type": "text",
        "tags": ["theme", "venue"],
        "added_by": "user_xyz",
        "added_at": "2025-10-18T10:30:00Z"
    }'
);
```

**Key Characteristics:**
- **Immutable**: Events are never updated or deleted
- **Complete Audit Trail**: Every state change is recorded
- **Replay Capability**: Rebuild state from events for debugging
- **Versioning**: `aggregate_version` ensures event ordering

---

### **2. Party State Table (Current Snapshot)**

```sql
CREATE TABLE party_state (
    party_id VARCHAR(20) PRIMARY KEY,
    user_id UUID NOT NULL,

    -- Current state
    status VARCHAR(20) NOT NULL, -- 'planning', 'completed', 'cancelled'
    current_version INT NOT NULL DEFAULT 0,

    -- Active inputs (materialized from events)
    inputs JSONB NOT NULL DEFAULT '[]',

    -- Active agents (which are currently running/completed)
    active_agents JSONB NOT NULL DEFAULT '{}',
    -- Example: {"theme_agent": "completed", "cake_agent": "running"}

    -- Agent results (denormalized for fast reads)
    agent_results JSONB NOT NULL DEFAULT '{}',

    -- Current budget
    budget JSONB,

    -- Final plan
    final_plan JSONB,

    -- Metadata for ML
    metadata JSONB DEFAULT '{}',
    -- Example: {
    --   "total_inputs": 15,
    --   "total_removals": 3,
    --   "avg_response_time_ms": 250,
    --   "user_satisfaction": null,
    --   "conversion": false
    -- }

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    -- Soft delete
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_party_state_user_id ON party_state(user_id);
CREATE INDEX idx_party_state_status ON party_state(status);
CREATE INDEX idx_party_state_created_at ON party_state(created_at DESC);
```

**Read Optimization:**
- Denormalized agent results for fast queries
- JSONB indexes for nested queries
- Materialized view of current state (rebuilt from events)

---

### **3. Agent Execution Log (Performance & Training)**

```sql
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    party_id VARCHAR(20) NOT NULL,
    agent_type VARCHAR(50) NOT NULL,

    -- Execution details
    execution_id UUID NOT NULL, -- For re-runs
    trigger_event_id UUID REFERENCES party_events(id),

    -- Status
    status VARCHAR(20) NOT NULL, -- 'started', 'completed', 'failed'

    -- Performance
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    duration_ms INT,

    -- Input/Output
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,

    -- Context
    context JSONB, -- Other agent results available at execution time

    -- ML Features
    confidence FLOAT,
    model_version VARCHAR(20),

    -- Resource usage (for cost optimization)
    cpu_usage_percent FLOAT,
    memory_mb INT,
    api_calls INT,

    -- Indexing
    FOREIGN KEY (party_id) REFERENCES party_state(party_id)
);

CREATE INDEX idx_agent_executions_party_id ON agent_executions(party_id);
CREATE INDEX idx_agent_executions_agent_type ON agent_executions(agent_type);
CREATE INDEX idx_agent_executions_started_at ON agent_executions(started_at DESC);
```

**ML Training Use Cases:**
- Agent performance analysis
- Cost prediction per agent type
- Failure pattern detection
- Optimal agent sequencing

---

### **4. Input History (for Removals)**

```sql
CREATE TABLE input_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    party_id VARCHAR(20) NOT NULL,
    input_id VARCHAR(50) NOT NULL,

    -- Input data
    content TEXT NOT NULL,
    source_type VARCHAR(20),
    tags TEXT[],

    -- Classification
    classified_as TEXT[], -- ['theme', 'venue']

    -- Status
    status VARCHAR(20) NOT NULL, -- 'active', 'removed'

    -- Affected agents (which agents processed this input)
    affected_agents JSONB DEFAULT '[]',
    -- Example: ["theme_agent", "venue_agent"]

    -- Timestamps
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    removed_at TIMESTAMPTZ,

    FOREIGN KEY (party_id) REFERENCES party_state(party_id)
);

CREATE INDEX idx_input_history_party_id ON input_history(party_id);
CREATE INDEX idx_input_history_input_id ON input_history(party_id, input_id);
CREATE INDEX idx_input_history_status ON input_history(status) WHERE status = 'active';
```

**Removal Cascade Logic:**
1. Mark input as `removed`
2. Check if any agents still need this input
3. If no other inputs for agent → remove agent data
4. Trigger budget recalculation
5. Update final plan

---

## 🔧 **Redis Cache Schema**

### **Cache Keys & TTLs**

```python
# Active party session (TTL: 24 hours)
party:{party_id}:state = {
    "status": "planning",
    "active_inputs": [
        {"id": "inp_1", "content": "jungle theme", "tags": ["theme"]},
        {"id": "inp_2", "content": "75 guests", "tags": ["venue", "catering"]}
    ],
    "active_agents": {
        "theme_agent": {"status": "completed", "result": {...}},
        "venue_agent": {"status": "running", "started_at": "2025-10-18T10:35:00Z"}
    },
    "last_updated": "2025-10-18T10:35:15Z"
}

# Agent result cache (TTL: 24 hours)
party:{party_id}:agent:{agent_name} = {
    "status": "completed",
    "result": {
        "primary_theme": "jungle",
        "colors": ["green", "brown"],
        "confidence": 0.92
    },
    "execution_time_ms": 1250,
    "completed_at": "2025-10-18T10:35:10Z"
}

# Budget cache (TTL: 24 hours, invalidated on any agent completion)
party:{party_id}:budget = {
    "total_min": 950,
    "total_max": 2400,
    "breakdown": {
        "venue": {"min": 0, "max": 0, "note": "Free (permit required)"},
        "cake": {"min": 80, "max": 300},
        "catering": {"min": 450, "max": 900},
        "vendors": {"min": 420, "max": 1200}
    },
    "calculated_at": "2025-10-18T10:36:00Z",
    "based_on_agents": ["venue_agent", "cake_agent", "catering_agent", "vendor_agent"]
}

# Final plan cache (TTL: 24 hours, invalidated on any change)
party:{party_id}:final_plan = {
    "recommendations": [...],
    "next_steps": [...],
    "completion_percent": 85,
    "missing_agents": ["photography_vendor"],
    "last_updated": "2025-10-18T10:36:05Z"
}

# User session (TTL: 1 hour)
session:{session_id} = {
    "user_id": "usr_xyz",
    "party_id": "fp2025A12345",
    "websocket_connection_id": "ws_conn_789",
    "last_activity": "2025-10-18T10:36:10Z"
}
```

### **Cache Invalidation Strategy**

```python
# Invalidate on agent completion
async def on_agent_completed(party_id: str, agent_name: str):
    # Invalidate affected caches
    await redis.delete(f"party:{party_id}:agent:{agent_name}")
    await redis.delete(f"party:{party_id}:budget")
    await redis.delete(f"party:{party_id}:final_plan")

    # Update state cache
    await update_party_state_cache(party_id)

# Invalidate on input removal
async def on_input_removed(party_id: str, input_id: str):
    # Invalidate all dependent caches
    await redis.delete(f"party:{party_id}:budget")
    await redis.delete(f"party:{party_id}:final_plan")

    # Update state cache
    await update_party_state_cache(party_id)
```

---

## 📡 **Event-Driven Flow (Kafka Topics)**

### **Topic Configuration**

```yaml
# Kafka Topic Configuration
topics:
  - name: party.input.added
    partitions: 1000
    replication_factor: 3
    retention_ms: 604800000  # 7 days

  - name: party.input.removed
    partitions: 1000
    replication_factor: 3
    retention_ms: 604800000

  - name: party.agent.should_execute
    partitions: 1000
    replication_factor: 3
    retention_ms: 86400000  # 1 day

  - name: party.agent.completed
    partitions: 1000
    replication_factor: 3
    retention_ms: 604800000

  - name: party.agent.data_removed
    partitions: 1000
    replication_factor: 3
    retention_ms: 604800000

  - name: party.budget.recalculated
    partitions: 1000
    replication_factor: 3
    retention_ms: 604800000

  - name: party.plan.updated
    partitions: 1000
    replication_factor: 3
    retention_ms: 604800000
```

### **Event Schemas**

#### **party.input.added**
```json
{
  "event_id": "evt_abc123",
  "party_id": "fp2025A12345",
  "timestamp": "2025-10-18T10:30:00Z",
  "payload": {
    "input_id": "inp_1",
    "content": "I need a balloon artist",
    "source_type": "text",
    "tags": ["vendor"],
    "added_by": "user_xyz"
  },
  "correlation_id": "corr_xyz",
  "metadata": {
    "client_ip": "192.168.1.1",
    "user_agent": "Mozilla/5.0..."
  }
}
```

#### **party.input.removed**
```json
{
  "event_id": "evt_def456",
  "party_id": "fp2025A12345",
  "timestamp": "2025-10-18T10:40:00Z",
  "payload": {
    "input_id": "inp_1",
    "removed_by": "user_xyz",
    "reason": "user_changed_mind"
  },
  "correlation_id": "corr_xyz"
}
```

#### **party.agent.completed**
```json
{
  "event_id": "evt_ghi789",
  "party_id": "fp2025A12345",
  "timestamp": "2025-10-18T10:35:00Z",
  "payload": {
    "agent_name": "theme_agent",
    "execution_id": "exec_123",
    "result": {
      "primary_theme": "jungle",
      "colors": ["green", "brown", "yellow"],
      "confidence": 0.92
    },
    "execution_time_ms": 1250
  },
  "correlation_id": "corr_xyz"
}
```

#### **party.budget.recalculated**
```json
{
  "event_id": "evt_jkl012",
  "party_id": "fp2025A12345",
  "timestamp": "2025-10-18T10:36:00Z",
  "payload": {
    "total_budget": {"min": 950, "max": 2400},
    "previous_total": {"min": 800, "max": 2100},
    "delta": {"min": 150, "max": 300},
    "reason": "vendor_agent_completed",
    "breakdown": {...}
  },
  "correlation_id": "corr_xyz"
}
```

---

## 🚀 **Agent Implementation (Enhanced)**

### **1. InputAnalyzer Agent (Always Running)**

**File:** `app/services/agents/input_analyzer_agent.py`

```python
import asyncio
from typing import Dict, List, Set
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from app.core.logging import logger
from app.services.classification_engine import ClassificationEngine

class InputAnalyzerAgent:
    """
    Always-running agent that analyzes inputs in real-time
    Deployed as: Kubernetes Deployment (replicas: 3-10)
    Scales based on: Kafka consumer lag
    """

    def __init__(self):
        self.classification_engine = ClassificationEngine()
        self.agent_dependency_graph = {
            'theme': {
                'affects': ['cake', 'venue', 'vendor'],
                'priority': 1
            },
            'cake': {
                'affects': ['budget'],
                'priority': 2
            },
            'venue': {
                'affects': ['budget', 'catering'],
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
            'budget': {
                'affects': ['planner_final'],
                'priority': 4
            }
        }

    async def start(self):
        """
        Start consuming from Kafka
        """
        consumer = AIOKafkaConsumer(
            'party.input.added',
            'party.input.removed',
            bootstrap_servers='kafka:9092',
            group_id='input-analyzer-group',
            enable_auto_commit=False,  # Manual commit for exactly-once
            max_poll_records=100,      # Batch processing
        )

        producer = AIOKafkaProducer(
            bootstrap_servers='kafka:9092',
            compression_type='gzip'
        )

        await consumer.start()
        await producer.start()

        logger.info("InputAnalyzerAgent started",
                   topics=consumer.subscription())

        try:
            async for msg in consumer:
                try:
                    event = json.loads(msg.value)

                    if msg.topic == 'party.input.added':
                        await self.handle_input_added(event, producer)
                    elif msg.topic == 'party.input.removed':
                        await self.handle_input_removed(event, producer)

                    # Commit offset after successful processing
                    await consumer.commit()

                except Exception as e:
                    logger.error("Failed to process event",
                                event_id=event.get('event_id'),
                                error=str(e))
                    # Dead letter queue
                    await self.send_to_dlq(event, str(e))

        finally:
            await consumer.stop()
            await producer.stop()

    async def handle_input_added(self, event: Dict, producer):
        """
        Process new input and determine agent execution plan
        """
        party_id = event['party_id']
        new_input = event['payload']

        # 1. Classify input
        classification = await self.classification_engine.classify(new_input)

        # 2. Get current party state from Redis
        party_state = await redis.get(f"party:{party_id}:state")

        # 3. Determine agent execution plan
        execution_plan = await self.create_execution_plan(
            party_id,
            classification,
            party_state
        )

        # 4. Emit agent execution events (in priority order)
        for step in sorted(execution_plan, key=lambda x: x['priority']):
            await producer.send(
                'party.agent.should_execute',
                value=json.dumps({
                    'party_id': party_id,
                    'agent_name': step['agent'],
                    'execution_type': step['type'],  # 'start' or 'rerun'
                    'input_ids': step['input_ids'],
                    'priority': step['priority'],
                    'correlation_id': event['correlation_id']
                }).encode('utf-8')
            )

        logger.info("Input analyzed and execution plan created",
                   party_id=party_id,
                   classification=classification,
                   agents_to_execute=len(execution_plan))

    async def create_execution_plan(
        self,
        party_id: str,
        classification: Dict,
        party_state: Dict
    ) -> List[Dict]:
        """
        Create ordered execution plan based on dependencies
        """
        plan = []
        active_agents = set(party_state.get('active_agents', {}).keys())

        for category, inputs in classification['primary'].items():
            agent_name = f"{category}_agent"

            if agent_name in active_agents:
                # Agent already ran → schedule re-run
                plan.append({
                    'agent': agent_name,
                    'type': 'rerun',
                    'input_ids': [inp['input_id'] for inp in inputs],
                    'priority': self.agent_dependency_graph[category]['priority']
                })
            else:
                # New agent → schedule start
                plan.append({
                    'agent': agent_name,
                    'type': 'start',
                    'input_ids': [inp['input_id'] for inp in inputs],
                    'priority': self.agent_dependency_graph[category]['priority']
                })

            # Add cascade effects (dependent agents)
            for dependent in self.agent_dependency_graph[category]['affects']:
                dependent_agent = f"{dependent}_agent"
                if dependent_agent in active_agents:
                    plan.append({
                        'agent': dependent_agent,
                        'type': 'recalculate',
                        'input_ids': [],
                        'priority': self.agent_dependency_graph[dependent]['priority'],
                        'reason': f'dependency_on_{agent_name}'
                    })

        return plan

    async def handle_input_removed(self, event: Dict, producer):
        """
        Handle input removal and determine cleanup/recalculation
        """
        party_id = event['party_id']
        removed_input_id = event['payload']['input_id']

        # 1. Get affected agents from input history
        input_record = await db.get_input_by_id(party_id, removed_input_id)
        affected_agents = input_record['affected_agents']

        # 2. Get remaining active inputs
        remaining_inputs = await db.get_active_inputs(party_id)

        # 3. Determine cleanup actions
        for agent in affected_agents:
            agent_category = agent.replace('_agent', '')

            # Check if agent is still needed
            still_needed = any(
                agent_category in inp['classified_as']
                for inp in remaining_inputs
            )

            if not still_needed:
                # Emit data removal event
                await producer.send(
                    'party.agent.data_removed',
                    value=json.dumps({
                        'party_id': party_id,
                        'agent_name': agent,
                        'reason': 'no_relevant_inputs',
                        'removed_input_id': removed_input_id
                    }).encode('utf-8')
                )
            else:
                # Re-run agent with updated inputs
                await producer.send(
                    'party.agent.should_execute',
                    value=json.dumps({
                        'party_id': party_id,
                        'agent_name': agent,
                        'execution_type': 'rerun',
                        'reason': 'input_removed_revalidate'
                    }).encode('utf-8')
                )

        # 4. Always trigger budget recalculation
        await producer.send(
            'party.agent.should_execute',
            value=json.dumps({
                'party_id': party_id,
                'agent_name': 'budget_agent',
                'execution_type': 'recalculate',
                'reason': 'agent_data_changed'
            }).encode('utf-8')
        )
```

---

### **2. PlannerFinal Agent (Always Reactive)**

**File:** `app/services/agents/planner_final_agent.py`

```python
class PlannerFinalAgent:
    """
    Always-reactive agent that updates final plan on any change
    Deployed as: Kubernetes Deployment (replicas: 5-20)
    Triggers: Any agent completion or data removal
    """

    async def start(self):
        consumer = AIOKafkaConsumer(
            'party.agent.completed',
            'party.agent.data_removed',
            'party.budget.recalculated',
            bootstrap_servers='kafka:9092',
            group_id='planner-final-group'
        )

        await consumer.start()

        try:
            async for msg in consumer:
                event = json.loads(msg.value)
                await self.update_final_plan(event)
        finally:
            await consumer.stop()

    async def update_final_plan(self, event: Dict):
        """
        Recompute final plan based on all agent results
        """
        party_id = event['party_id']

        # 1. Fetch all active agent results from Redis
        agent_results = {}
        for agent_key in await redis.keys(f"party:{party_id}:agent:*"):
            agent_name = agent_key.split(':')[-1]
            result = await redis.get(agent_key)
            if result:
                agent_results[agent_name] = json.loads(result)

        # 2. Fetch current budget
        budget = await redis.get(f"party:{party_id}:budget")
        budget = json.loads(budget) if budget else None

        # 3. Generate comprehensive plan
        final_plan = await self.generate_final_plan(
            party_id,
            agent_results,
            budget
        )

        # 4. Store in Redis + PostgreSQL
        await redis.setex(
            f"party:{party_id}:final_plan",
            86400,  # 24 hours
            json.dumps(final_plan)
        )

        await db.update_party_state(
            party_id,
            {'final_plan': final_plan}
        )

        # 5. Emit update event (for WebSocket broadcast)
        await producer.send(
            'party.plan.updated',
            value=json.dumps({
                'party_id': party_id,
                'final_plan': final_plan,
                'updated_at': datetime.utcnow().isoformat()
            }).encode('utf-8')
        )

        logger.info("Final plan updated",
                   party_id=party_id,
                   completion_percent=final_plan['completion_percent'])

    async def generate_final_plan(
        self,
        party_id: str,
        agent_results: Dict,
        budget: Dict
    ) -> Dict:
        """
        Generate intelligent final plan with recommendations
        """
        # Calculate completion percentage
        required_agents = ['theme_agent', 'venue_agent', 'budget_agent']
        completed_required = sum(
            1 for agent in required_agents
            if agent in agent_results
        )
        completion_percent = int((completed_required / len(required_agents)) * 100)

        # Generate recommendations (implementation details in full code)
        recommendations = self._generate_recommendations(agent_results, budget)

        # Generate next steps
        next_steps = self._generate_next_steps(agent_results)

        return {
            "completion_percent": completion_percent,
            "recommendations": recommendations,
            "next_steps": next_steps,
            "active_agents": list(agent_results.keys()),
            "missing_agents": [
                agent for agent in required_agents
                if agent not in agent_results
            ],
            "budget_summary": budget,
            "last_updated": datetime.utcnow().isoformat()
        }
```

---

### **3. BudgetAgent (Reactive)**

**File:** `app/services/agents/budget_agent.py`

```python
class BudgetAgent:
    """
    Reactive budget calculator
    Triggers: Any cost-related agent completion or data removal
    """

    async def start(self):
        consumer = AIOKafkaConsumer(
            'party.agent.should_execute',
            bootstrap_servers='kafka:9092',
            group_id='budget-agent-group'
        )

        await consumer.start()

        try:
            async for msg in consumer:
                event = json.loads(msg.value)

                # Only process events for budget_agent
                if event['agent_name'] == 'budget_agent':
                    await self.recalculate_budget(event)
        finally:
            await consumer.stop()

    async def recalculate_budget(self, event: Dict):
        """
        Recalculate budget based on all active agent results
        """
        party_id = event['party_id']

        # 1. Fetch all cost-related agent results
        agent_results = {}
        cost_agents = ['venue_agent', 'cake_agent', 'catering_agent', 'vendor_agent']

        for agent in cost_agents:
            result = await redis.get(f"party:{party_id}:agent:{agent}")
            if result:
                agent_results[agent] = json.loads(result)['result']

        # 2. Calculate budget breakdown
        breakdown = {}
        total_min = 0
        total_max = 0

        # (Budget calculation logic - see full implementation)

        # 3. Create budget object
        budget = {
            'total_budget': {'min': total_min, 'max': total_max},
            'breakdown': breakdown,
            'recommendations': self._get_budget_recommendations(total_min, total_max),
            'calculated_at': datetime.utcnow().isoformat(),
            'based_on_agents': list(agent_results.keys())
        }

        # 4. Store in Redis + PostgreSQL
        await redis.setex(f"party:{party_id}:budget", 86400, json.dumps(budget))
        await db.update_party_state(party_id, {'budget': budget})

        # 5. Emit budget recalculated event
        await producer.send('party.budget.recalculated', ...)
```

---

## 📊 **Training Data Pipeline**

### **1. Event Collection (Real-time)**

**S3 Structure:**
```
training_data/
  events/
    year=2025/
      month=10/
        day=18/
          hour=10/
            part-00001.jsonl.gz  # 10:00-10:59 events
            part-00002.jsonl.gz
```

**Event Format (JSONL):**
```json
{
  "event_id": "evt_abc123",
  "event_type": "input_added",
  "party_id": "fp2025A12345",
  "user_id": "usr_xyz",
  "timestamp": "2025-10-18T10:30:00Z",
  "payload": {...},

  "features": {
    "input_length": 25,
    "input_type": "text",
    "classification": ["vendor", "balloon_artist"],
    "classification_confidence": 0.92,
    "session_age_minutes": 15,
    "total_inputs_so_far": 3
  },

  "context": {
    "active_agents": ["theme_agent", "venue_agent"],
    "budget_so_far": {"min": 500, "max": 1200},
    "user_timezone": "America/Los_Angeles"
  }
}
```

---

### **2. Feature Engineering (Batch - Daily)**

**Spark Job:** `jobs/feature_engineering.py`

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

def engineer_features(date: str):
    """
    Run daily feature engineering on previous day's events
    """
    spark = SparkSession.builder.appName("feature_engineering").getOrCreate()

    # Read events
    events_df = spark.read.json(
        f"s3://training-data/events/year={date[:4]}/month={date[5:7]}/day={date[8:10]}/"
    )

    # Aggregate by party_id
    party_features = events_df.groupBy("party_id").agg(
        count("event_id").alias("total_events"),
        countDistinct(when(col("event_type") == "input_added", 1)).alias("total_inputs"),
        countDistinct(when(col("event_type") == "input_removed", 1)).alias("total_removals"),
        avg(col("features.input_length")).alias("avg_input_length"),
        collect_set(col("features.classification")).alias("all_classifications"),
        (max("timestamp") - min("timestamp")).alias("session_duration_seconds"),
        max(when(col("event_type") == "party.completed", 1).otherwise(0)).alias("completed")
    )

    # Write to feature store
    party_features.write.mode("overwrite").parquet(
        f"s3://training-data/features/date={date}/party_features.parquet"
    )
```

---

### **3. Model Training (Weekly)**

**Models:**
1. **Input Classification Improvement**
   - Input: User text
   - Output: Categories + Confidence
   - Algorithm: BERT + Multi-label classification

2. **Budget Prediction**
   - Input: Theme, guest count, location, agent selections
   - Output: Predicted budget range
   - Algorithm: Gradient Boosting Regressor

3. **Agent Recommendation**
   - Input: Current inputs, active agents
   - Output: Suggested next agents
   - Algorithm: Sequential Neural Network

4. **Completion Prediction**
   - Input: Current party state
   - Output: Probability of completion
   - Algorithm: XGBoost Classifier

---

## 🔐 **Scalability & Performance**

### **1. Horizontal Scaling (Kubernetes)**

```yaml
# kubernetes/agent-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: input-analyzer-agent
spec:
  replicas: 5  # Start with 5, auto-scale to 50
  selector:
    matchLabels:
      app: input-analyzer
  template:
    metadata:
      labels:
        app: input-analyzer
    spec:
      containers:
      - name: input-analyzer
        image: festipin/input-analyzer:v1.0
        resources:
          requests:
            cpu: "1000m"
            memory: "2Gi"
          limits:
            cpu: "2000m"
            memory: "4Gi"

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: input-analyzer-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: input-analyzer-agent
  minReplicas: 5
  maxReplicas: 50
  metrics:
  - type: External
    external:
      metric:
        name: kafka_consumer_lag
      target:
        type: AverageValue
        averageValue: "1000"  # Scale up if lag > 1000
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

### **2. Database Sharding**

```sql
-- PostgreSQL: Hash-based partitioning

CREATE TABLE party_events_partitioned (
    LIKE party_events INCLUDING ALL
) PARTITION BY HASH (party_id);

-- Create 100 partitions
DO $$
BEGIN
    FOR i IN 0..99 LOOP
        EXECUTE format(
            'CREATE TABLE party_events_p%s PARTITION OF party_events_partitioned
             FOR VALUES WITH (MODULUS 100, REMAINDER %s)',
            i, i
        );
    END LOOP;
END $$;
```

**Result:** Each partition handles ~1000 parties at 100K scale

---

### **3. Multi-Level Caching**

```python
async def get_party_state(party_id: str) -> Dict:
    """
    L1 (App Memory) → L2 (Redis) → L3 (PostgreSQL)
    """
    # L1: In-memory cache (1000 hot parties, TTL: 5 min)
    if party_id in app_cache:
        return app_cache[party_id]

    # L2: Redis (all active parties, TTL: 24 hours)
    cached = await redis.get(f"party:{party_id}:state")
    if cached:
        party_state = json.loads(cached)
        app_cache[party_id] = party_state
        return party_state

    # L3: PostgreSQL (all parties)
    party_state = await db.query(
        "SELECT * FROM party_state WHERE party_id = $1",
        party_id
    )

    if party_state:
        await redis.setex(f"party:{party_id}:state", 86400, json.dumps(party_state))
        app_cache[party_id] = party_state

    return party_state
```

---

## 💰 **Cost Analysis (100K Concurrent Users)**

### **Monthly Infrastructure Costs (AWS)**

```
┌────────────────────────────────────────────────────────────┐
│ Component              │ Specification         │ Cost/Month│
├────────────────────────────────────────────────────────────┤
│ EKS Cluster (K8s)      │ 3 m5.2xlarge nodes    │   $1,152  │
│ Agent Pods (avg 30)    │ 30 pods × 2GB each    │     $720  │
│ PostgreSQL RDS         │ db.r5.2xlarge (HA)    │   $1,460  │
│ Redis Cluster          │ cache.r6g.xlarge × 3  │     $672  │
│ Kafka MSK              │ kafka.m5.large × 3    │     $630  │
│ S3 Storage             │ 500GB (events+backup) │      $12  │
│ CloudFront CDN         │ 1TB transfer          │      $85  │
│ Load Balancer (ALB)    │ 3 ALBs                │      $90  │
│ OpenAI API             │ 100K users × 50 calls │  $15,000  │
│ Pinecone Vector DB     │ Standard plan         │      $70  │
├────────────────────────────────────────────────────────────┤
│ TOTAL                  │                       │  $19,891  │
└────────────────────────────────────────────────────────────┘

Cost per user per month: $19,891 / 100,000 = $0.20
Revenue target: $5-10/user/month → 25-50x margin
```

---

## ✅ **Best Practices Summary**

### **1. Event Sourcing**
- ✅ All state changes stored as immutable events
- ✅ Complete audit trail for compliance
- ✅ Replay capability for debugging

### **2. CQRS Pattern**
- ✅ Write path: Kafka → PostgreSQL (events)
- ✅ Read path: Redis cache → Fast queries
- ✅ Materialized views for complex queries

### **3. Idempotency**
- ✅ Event IDs prevent duplicate processing
- ✅ Exactly-once delivery with Kafka transactions
- ✅ Idempotent API endpoints

### **4. Graceful Degradation**
- ✅ Agent failures don't block workflow
- ✅ Redis failure → fallback to PostgreSQL
- ✅ Kafka lag → auto-scale consumers

### **5. Observability**
- ✅ Distributed tracing (Jaeger)
- ✅ Metrics (Prometheus + Grafana)
- ✅ Structured logging (ELK stack)
- ✅ Real-time dashboards

---

## 🎯 **Implementation Roadmap**

### **Phase 1: Core Architecture (Weeks 1-4)**
- [ ] Event-driven infrastructure (Kafka setup)
- [ ] PostgreSQL schema + migrations
- [ ] Redis cluster configuration
- [ ] Always-on agents (InputAnalyzer, PlannerFinal)
- [ ] Basic API endpoints

### **Phase 2: Dynamic Agents (Weeks 5-8)**
- [ ] Implement all 6 dynamic agents
- [ ] Agent lifecycle management
- [ ] Dependency graph execution
- [ ] WebSocket real-time updates

### **Phase 3: Scale & Optimize (Weeks 9-12)**
- [ ] Load testing (10K → 100K users)
- [ ] Database sharding
- [ ] Multi-level caching
- [ ] Performance optimization
- [ ] Cost optimization

### **Phase 4: ML Pipeline (Weeks 13-16)**
- [ ] Training data collection
- [ ] Feature engineering (Spark jobs)
- [ ] Model training infrastructure
- [ ] Model deployment & A/B testing

---

## 📚 **References & Documentation**

### **External Dependencies**
- **Kafka:** https://kafka.apache.org/documentation/
- **PostgreSQL:** https://www.postgresql.org/docs/
- **Redis:** https://redis.io/documentation
- **Kubernetes:** https://kubernetes.io/docs/
- **LangChain:** https://python.langchain.com/docs/

### **Internal Documentation**
- `IMPLEMENTATION_COMPLETE.md` - Current MVP status
- `MOCK_DATABASE_MVP_GUIDE.md` - Mock database usage
- `LOGGING_GUIDE.md` - Logging best practices
- `TESTING_GUIDE.md` - Testing strategies

---

## 🔧 **Appendix: Configuration Examples**

### **Kafka Consumer Configuration**

```python
# config/kafka_config.py

KAFKA_CONFIG = {
    'bootstrap_servers': 'kafka:9092',
    'security_protocol': 'SASL_SSL',
    'sasl_mechanism': 'SCRAM-SHA-512',
    'sasl_username': os.getenv('KAFKA_USERNAME'),
    'sasl_password': os.getenv('KAFKA_PASSWORD'),

    # Consumer settings
    'group_id': 'input-analyzer-group',
    'enable_auto_commit': False,
    'auto_offset_reset': 'earliest',
    'max_poll_records': 100,
    'max_poll_interval_ms': 300000,  # 5 minutes

    # Performance tuning
    'fetch_min_bytes': 1024,
    'fetch_max_wait_ms': 500,
    'compression_type': 'gzip'
}
```

### **Redis Configuration**

```python
# config/redis_config.py

REDIS_CONFIG = {
    'host': 'redis-cluster',
    'port': 6379,
    'db': 0,
    'decode_responses': True,
    'max_connections': 50,

    # Connection pool
    'socket_timeout': 5,
    'socket_connect_timeout': 5,
    'socket_keepalive': True,

    # Retry settings
    'retry_on_timeout': True,
    'health_check_interval': 30
}
```

---

**END OF DOCUMENT**

**Document Status:** ✅ Complete and Ready for Implementation
**Next Steps:** Phase 1 - Core Architecture Development
**Contact:** Architecture Team - festipin-arch@team.com
