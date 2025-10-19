# 📚 **Case Studies: Memory, Cost & Optimization**

---

## **CASE 1: Edit/Resume Party Planning from Previous State**

### **Problem Statement**
User creates a party plan, saves it, and comes back later to edit. Questions:
- How do agents remember previous inputs and results?
- How to avoid re-running all agents from scratch?
- How to only process the CHANGES (delta)?
- How to maintain consistency when editing?

---

### **Solution Architecture**

#### **1. Event Sourcing + State Snapshots**

```
┌─────────────────────────────────────────────────────────────┐
│              PARTY LIFECYCLE TIMELINE                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Day 1: Initial Planning                                    │
│  ─────────────────────                                      │
│  10:00 AM - Create party (fp2025A12345)                     │
│  10:01 AM - Add input: "jungle theme"                       │
│            → ThemeAgent executes                            │
│            → Result stored: snapshot_v1                     │
│  10:05 AM - Add input: "75 guests"                          │
│            → VenueAgent, CateringAgent execute              │
│            → Result stored: snapshot_v2                     │
│  10:10 AM - User saves & closes                             │
│            → State: "draft"                                 │
│            → Snapshot saved: snapshot_final_v2              │
│                                                              │
│  Day 2: Resume & Edit                                       │
│  ────────────────────                                       │
│  2:00 PM - User clicks "Edit Party"                         │
│           → Load snapshot_final_v2 from PostgreSQL          │
│           → Restore all inputs, agent results to Redis      │
│           → Status: "editing"                               │
│  2:05 PM - Add input: "Need balloon artist"                │
│           → InputAnalyzer detects: NEW input                │
│           → Only VendorAgent & BudgetAgent execute          │
│           → ThemeAgent, VenueAgent NOT re-run (use cache)   │
│  2:10 PM - Remove input: "jungle theme"                     │
│           → InputAnalyzer detects: REMOVED input            │
│           → ThemeAgent data deleted                         │
│           → Cascade: VenueAgent, CakeAgent re-run           │
│                      (theme context changed)                │
│  2:15 PM - User saves again                                 │
│           → New snapshot: snapshot_final_v3                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### **Implementation**

#### **A. State Snapshot Storage**

```sql
-- PostgreSQL: Party Snapshots Table
CREATE TABLE party_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    party_id VARCHAR(20) NOT NULL,
    snapshot_version INT NOT NULL,
    snapshot_type VARCHAR(20) NOT NULL, -- 'draft', 'auto', 'final'

    -- Complete state snapshot
    state JSONB NOT NULL,
    -- {
    --   "inputs": [...],
    --   "agent_results": {...},
    --   "budget": {...},
    --   "final_plan": {...},
    --   "metadata": {
    --     "total_events": 15,
    --     "last_agent_run": "vendor_agent",
    --     "completion_percent": 85
    --   }
    -- }

    -- Snapshot metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID,

    -- Event sourcing reference
    last_event_id UUID REFERENCES party_events(id),
    event_count INT NOT NULL, -- Number of events up to this snapshot

    CONSTRAINT unique_party_snapshot UNIQUE (party_id, snapshot_version)
);

CREATE INDEX idx_snapshots_party_id ON party_snapshots(party_id);
CREATE INDEX idx_snapshots_created_at ON party_snapshots(created_at DESC);
```

#### **B. Snapshot Creation Logic**

```python
# app/services/snapshot_manager.py

class SnapshotManager:
    """
    Manages state snapshots for party planning sessions
    """

    async def create_snapshot(
        self,
        party_id: str,
        snapshot_type: str = 'auto'
    ) -> Dict:
        """
        Create a snapshot of current party state

        Triggered by:
        - User clicking "Save" (type: draft)
        - Every 10 events (type: auto)
        - Final plan completion (type: final)
        """
        # 1. Get current state from Redis
        party_state = await redis.get(f"party:{party_id}:state")

        # 2. Get all agent results
        agent_results = {}
        for agent_key in await redis.keys(f"party:{party_id}:agent:*"):
            agent_name = agent_key.split(':')[-1]
            result = await redis.get(agent_key)
            if result:
                agent_results[agent_name] = json.loads(result)

        # 3. Get budget & final plan
        budget = await redis.get(f"party:{party_id}:budget")
        final_plan = await redis.get(f"party:{party_id}:final_plan")

        # 4. Get event count
        event_count = await db.query(
            "SELECT COUNT(*) FROM party_events WHERE party_id = $1",
            party_id
        )

        # 5. Get last event ID
        last_event = await db.query(
            """SELECT id FROM party_events
               WHERE party_id = $1
               ORDER BY occurred_at DESC
               LIMIT 1""",
            party_id
        )

        # 6. Create snapshot version
        latest_snapshot = await db.query(
            """SELECT MAX(snapshot_version)
               FROM party_snapshots
               WHERE party_id = $1""",
            party_id
        )
        new_version = (latest_snapshot or 0) + 1

        # 7. Build snapshot
        snapshot = {
            "inputs": json.loads(party_state)['active_inputs'],
            "agent_results": agent_results,
            "budget": json.loads(budget) if budget else None,
            "final_plan": json.loads(final_plan) if final_plan else None,
            "metadata": {
                "total_events": event_count,
                "last_agent_run": self._get_last_agent_run(agent_results),
                "completion_percent": self._calculate_completion(agent_results),
                "snapshot_created_at": datetime.utcnow().isoformat()
            }
        }

        # 8. Save to PostgreSQL
        snapshot_id = await db.execute(
            """INSERT INTO party_snapshots
               (party_id, snapshot_version, snapshot_type, state,
                last_event_id, event_count)
               VALUES ($1, $2, $3, $4, $5, $6)
               RETURNING id""",
            party_id,
            new_version,
            snapshot_type,
            json.dumps(snapshot),
            last_event['id'],
            event_count
        )

        logger.info("Snapshot created",
                   party_id=party_id,
                   version=new_version,
                   type=snapshot_type,
                   event_count=event_count)

        return {
            "snapshot_id": snapshot_id,
            "version": new_version,
            "party_id": party_id
        }

    async def restore_from_snapshot(
        self,
        party_id: str,
        snapshot_version: int = None
    ) -> Dict:
        """
        Restore party state from snapshot

        Used when:
        - User clicks "Edit Party"
        - System needs to replay from checkpoint
        """
        # 1. Get snapshot (latest if version not specified)
        if snapshot_version:
            snapshot_record = await db.query(
                """SELECT * FROM party_snapshots
                   WHERE party_id = $1 AND snapshot_version = $2""",
                party_id, snapshot_version
            )
        else:
            snapshot_record = await db.query(
                """SELECT * FROM party_snapshots
                   WHERE party_id = $1
                   ORDER BY snapshot_version DESC
                   LIMIT 1""",
                party_id
            )

        if not snapshot_record:
            raise ValueError(f"No snapshot found for party {party_id}")

        snapshot_state = snapshot_record['state']

        # 2. Restore to Redis (hot cache)

        # 2a. Restore party state
        party_state = {
            "status": "editing",
            "active_inputs": snapshot_state['inputs'],
            "active_agents": {
                agent: {"status": "completed"}
                for agent in snapshot_state['agent_results'].keys()
            },
            "last_updated": datetime.utcnow().isoformat(),
            "restored_from_snapshot": snapshot_record['snapshot_version']
        }
        await redis.setex(
            f"party:{party_id}:state",
            86400,  # 24 hours
            json.dumps(party_state)
        )

        # 2b. Restore agent results
        for agent_name, result in snapshot_state['agent_results'].items():
            await redis.setex(
                f"party:{party_id}:agent:{agent_name}",
                86400,
                json.dumps(result)
            )

        # 2c. Restore budget
        if snapshot_state['budget']:
            await redis.setex(
                f"party:{party_id}:budget",
                86400,
                json.dumps(snapshot_state['budget'])
            )

        # 2d. Restore final plan
        if snapshot_state['final_plan']:
            await redis.setex(
                f"party:{party_id}:final_plan",
                86400,
                json.dumps(snapshot_state['final_plan'])
            )

        # 3. Update party_state table (PostgreSQL)
        await db.execute(
            """UPDATE party_state
               SET status = 'editing',
                   inputs = $1,
                   agent_results = $2,
                   budget = $3,
                   final_plan = $4,
                   updated_at = NOW()
               WHERE party_id = $5""",
            json.dumps(snapshot_state['inputs']),
            json.dumps(snapshot_state['agent_results']),
            json.dumps(snapshot_state['budget']),
            json.dumps(snapshot_state['final_plan']),
            party_id
        )

        logger.info("State restored from snapshot",
                   party_id=party_id,
                   snapshot_version=snapshot_record['snapshot_version'],
                   agent_count=len(snapshot_state['agent_results']),
                   input_count=len(snapshot_state['inputs']))

        return {
            "party_id": party_id,
            "restored_version": snapshot_record['snapshot_version'],
            "state": snapshot_state,
            "metadata": snapshot_state['metadata']
        }
```

#### **C. Delta Detection & Incremental Processing**

```python
# app/services/delta_processor.py

class DeltaProcessor:
    """
    Detects changes between saved state and new edits
    Only executes agents affected by changes
    """

    async def process_edit(
        self,
        party_id: str,
        new_inputs: List[Dict],
        removed_input_ids: List[str]
    ) -> Dict:
        """
        Process edits to existing party

        Smart delta detection:
        1. Compare new inputs vs saved inputs
        2. Identify which agents are affected
        3. Only re-run affected agents
        4. Reuse cached results for unchanged agents
        """
        # 1. Get saved state (from Redis, restored from snapshot)
        saved_state = await redis.get(f"party:{party_id}:state")
        saved_state = json.loads(saved_state)

        saved_inputs = {inp['input_id']: inp for inp in saved_state['active_inputs']}

        # 2. Detect NEW inputs
        new_input_items = []
        for inp in new_inputs:
            if inp['input_id'] not in saved_inputs:
                new_input_items.append(inp)

        # 3. Detect REMOVED inputs
        removed_items = []
        for removed_id in removed_input_ids:
            if removed_id in saved_inputs:
                removed_items.append(saved_inputs[removed_id])

        # 4. Classify new inputs
        affected_agents = set()

        if new_input_items:
            classification = await self.classifier.classify_batch(new_input_items)
            for category in classification['primary'].keys():
                affected_agents.add(f"{category}_agent")

        # 5. For removed inputs, find affected agents from history
        for removed_input in removed_items:
            input_history = await db.query(
                """SELECT affected_agents FROM input_history
                   WHERE party_id = $1 AND input_id = $2""",
                party_id,
                removed_input['input_id']
            )
            if input_history:
                affected_agents.update(input_history['affected_agents'])

        # 6. Add cascade agents (dependencies)
        cascade_agents = self._calculate_cascade(affected_agents)
        all_agents_to_run = affected_agents.union(cascade_agents)

        # 7. Determine execution plan
        execution_plan = []

        for agent in all_agents_to_run:
            # Check if agent result already exists
            existing_result = await redis.get(f"party:{party_id}:agent:{agent}")

            if existing_result and agent not in affected_agents:
                # Agent not directly affected → reuse cached result
                execution_plan.append({
                    'agent': agent,
                    'action': 'reuse_cache',
                    'reason': 'no_changes_affecting_this_agent'
                })
            else:
                # Agent needs to re-run
                execution_plan.append({
                    'agent': agent,
                    'action': 'execute',
                    'reason': 'input_added' if new_input_items else 'input_removed'
                })

        logger.info("Delta processing completed",
                   party_id=party_id,
                   new_inputs=len(new_input_items),
                   removed_inputs=len(removed_items),
                   affected_agents=len(affected_agents),
                   total_agents_to_run=len(execution_plan))

        return {
            "new_inputs": new_input_items,
            "removed_inputs": removed_items,
            "affected_agents": list(affected_agents),
            "cascade_agents": list(cascade_agents),
            "execution_plan": execution_plan,
            "estimated_cost_savings": self._calculate_savings(execution_plan)
        }

    def _calculate_cascade(self, affected_agents: Set[str]) -> Set[str]:
        """
        Calculate dependent agents that need to re-run
        """
        cascade = set()

        dependency_map = {
            'theme_agent': ['cake_agent', 'venue_agent', 'vendor_agent'],
            'venue_agent': ['budget_agent'],
            'cake_agent': ['budget_agent'],
            'catering_agent': ['budget_agent'],
            'vendor_agent': ['budget_agent'],
            'budget_agent': ['planner_final']
        }

        for agent in affected_agents:
            if agent in dependency_map:
                cascade.update(dependency_map[agent])

        return cascade

    def _calculate_savings(self, execution_plan: List[Dict]) -> Dict:
        """
        Calculate cost savings from reusing cached results
        """
        reused_count = sum(1 for step in execution_plan if step['action'] == 'reuse_cache')
        executed_count = sum(1 for step in execution_plan if step['action'] == 'execute')

        # Estimated cost per agent execution (OpenAI API calls)
        cost_per_agent = 0.02  # $0.02 per agent execution

        saved_cost = reused_count * cost_per_agent
        actual_cost = executed_count * cost_per_agent

        return {
            "reused_agents": reused_count,
            "executed_agents": executed_count,
            "cost_saved": f"${saved_cost:.4f}",
            "actual_cost": f"${actual_cost:.4f}",
            "savings_percent": int((reused_count / len(execution_plan)) * 100) if execution_plan else 0
        }
```

#### **D. API Endpoint for Edit/Resume**

```python
# app/api/routes/party_edit.py

@router.post("/party/{party_id}/resume")
async def resume_party_editing(party_id: str):
    """
    Resume editing a saved party

    Flow:
    1. Load latest snapshot from PostgreSQL
    2. Restore state to Redis
    3. Return current state to frontend
    """
    snapshot_manager = SnapshotManager()

    # Restore from latest snapshot
    restored_state = await snapshot_manager.restore_from_snapshot(party_id)

    return {
        "success": True,
        "party_id": party_id,
        "restored_from_version": restored_state['restored_version'],
        "state": restored_state['state'],
        "metadata": restored_state['metadata'],
        "message": "Party restored successfully. You can now continue editing."
    }


@router.post("/party/{party_id}/edit")
async def edit_party_inputs(
    party_id: str,
    request: EditPartyRequest
):
    """
    Process edits to existing party

    Smart delta processing:
    - Only runs affected agents
    - Reuses cached results for unchanged agents
    """
    delta_processor = DeltaProcessor()

    # Process delta
    delta_result = await delta_processor.process_edit(
        party_id,
        request.new_inputs,
        request.removed_input_ids
    )

    # Execute affected agents
    orchestrator = get_orchestrator()

    for step in delta_result['execution_plan']:
        if step['action'] == 'execute':
            # Emit event to trigger agent
            await orchestrator.trigger_agent(
                party_id,
                step['agent'],
                reason=step['reason']
            )

    return {
        "success": True,
        "party_id": party_id,
        "delta": delta_result,
        "message": f"Processing {delta_result['affected_agents']} agents. "
                   f"Reusing {delta_result['execution_plan'].count('reuse_cache')} cached results."
    }


@router.post("/party/{party_id}/save")
async def save_party_draft(party_id: str):
    """
    Save current party state as draft snapshot
    """
    snapshot_manager = SnapshotManager()

    snapshot = await snapshot_manager.create_snapshot(
        party_id,
        snapshot_type='draft'
    )

    return {
        "success": True,
        "snapshot_id": snapshot['snapshot_id'],
        "version": snapshot['version'],
        "message": "Party saved successfully"
    }
```

---

### **Example: Edit Flow with Delta Processing**

```
Initial State (Saved):
  Inputs:
    - inp_1: "jungle theme"        → ThemeAgent (cached)
    - inp_2: "75 guests"            → VenueAgent, CateringAgent (cached)
    - inp_3: "chocolate cake"       → CakeAgent (cached)
  Agent Results:
    - theme_agent: {primary_theme: "jungle", ...}
    - venue_agent: {recommended_venues: [...]}
    - catering_agent: {caterers: [...]}
    - cake_agent: {bakeries: [...]}
    - budget_agent: {total: $1,200}

User Edits:
  + Add: inp_4: "Need balloon artist"
  - Remove: inp_3: "chocolate cake"

Delta Processing:
  New Inputs: [inp_4]
    → Classification: vendor_agent
    → Action: Execute vendor_agent

  Removed Inputs: [inp_3]
    → Affected: cake_agent
    → Action: Delete cake_agent data

  Cascade Effects:
    → vendor_agent affects budget_agent → Execute budget_agent
    → cake_agent removed affects budget_agent → Execute budget_agent
    → budget_agent affects planner_final → Execute planner_final

  Execution Plan:
    1. theme_agent: REUSE CACHE (no changes)
    2. venue_agent: REUSE CACHE (no changes)
    3. catering_agent: REUSE CACHE (no changes)
    4. cake_agent: DELETE DATA (input removed)
    5. vendor_agent: EXECUTE (new input)
    6. budget_agent: EXECUTE (cascade)
    7. planner_final: EXECUTE (cascade)

  Cost Savings:
    - Reused: 3 agents (theme, venue, catering)
    - Executed: 3 agents (vendor, budget, planner)
    - Deleted: 1 agent (cake)
    - Savings: 50% cost reduction
```

---

## **CASE 2: Total Cost to Run Agents on Single Party**

### **Cost Breakdown Analysis**

#### **Assumption: Average Party Planning Session**
- **5 agents** run: Theme, Venue, Cake, Catering, Budget
- Each agent makes **API calls** to OpenAI/Gemini
- Vector DB queries for semantic search
- Infrastructure costs (compute, storage, bandwidth)

---

### **Detailed Cost Calculation**

```python
# Cost Calculator for Single Party Execution

class PartyCostCalculator:
    """
    Calculate total cost to execute agents for one party
    """

    def __init__(self):
        # OpenAI API Pricing (GPT-4o-mini - cost effective)
        self.openai_input_cost = 0.000150 / 1000   # $0.15 per 1M tokens
        self.openai_output_cost = 0.000600 / 1000  # $0.60 per 1M tokens

        # Pinecone Vector DB Pricing
        self.pinecone_query_cost = 0.0001  # $0.0001 per query

        # Infrastructure (amortized per request)
        self.k8s_pod_cost_per_second = 0.0001  # ~$0.36/hour for 1 pod
        self.redis_cost_per_operation = 0.000001
        self.postgres_cost_per_query = 0.000005

    def calculate_agent_cost(self, agent_name: str) -> Dict:
        """
        Calculate cost for individual agent execution
        """
        costs = {
            'theme_agent': {
                'openai_calls': 1,
                'input_tokens': 500,
                'output_tokens': 300,
                'vector_queries': 2,
                'execution_time_seconds': 1.5,
                'redis_ops': 3,
                'postgres_queries': 2
            },
            'venue_agent': {
                'openai_calls': 2,  # Classification + recommendation
                'input_tokens': 800,
                'output_tokens': 500,
                'vector_queries': 3,  # RAG for venue matching
                'execution_time_seconds': 2.0,
                'redis_ops': 5,
                'postgres_queries': 3
            },
            'cake_agent': {
                'openai_calls': 1,
                'input_tokens': 600,
                'output_tokens': 400,
                'vector_queries': 2,
                'execution_time_seconds': 1.5,
                'redis_ops': 3,
                'postgres_queries': 2
            },
            'catering_agent': {
                'openai_calls': 2,
                'input_tokens': 700,
                'output_tokens': 450,
                'vector_queries': 2,
                'execution_time_seconds': 1.8,
                'redis_ops': 4,
                'postgres_queries': 2
            },
            'budget_agent': {
                'openai_calls': 0,  # No LLM needed, pure calculation
                'input_tokens': 0,
                'output_tokens': 0,
                'vector_queries': 0,
                'execution_time_seconds': 0.3,
                'redis_ops': 8,  # Fetch all agent results
                'postgres_queries': 1
            }
        }

        agent_config = costs.get(agent_name, {})

        # Calculate component costs
        openai_cost = (
            agent_config.get('input_tokens', 0) * self.openai_input_cost +
            agent_config.get('output_tokens', 0) * self.openai_output_cost
        )

        vector_cost = (
            agent_config.get('vector_queries', 0) * self.pinecone_query_cost
        )

        compute_cost = (
            agent_config.get('execution_time_seconds', 0) *
            self.k8s_pod_cost_per_second
        )

        redis_cost = (
            agent_config.get('redis_ops', 0) *
            self.redis_cost_per_operation
        )

        postgres_cost = (
            agent_config.get('postgres_queries', 0) *
            self.postgres_cost_per_query
        )

        total = openai_cost + vector_cost + compute_cost + redis_cost + postgres_cost

        return {
            'agent': agent_name,
            'breakdown': {
                'openai_llm': f"${openai_cost:.6f}",
                'vector_db': f"${vector_cost:.6f}",
                'compute': f"${compute_cost:.6f}",
                'redis': f"${redis_cost:.6f}",
                'postgresql': f"${postgres_cost:.6f}"
            },
            'total_cost': f"${total:.6f}",
            'total_cost_numeric': total
        }

    def calculate_party_cost(self, agents: List[str]) -> Dict:
        """
        Calculate total cost for party planning with multiple agents
        """
        agent_costs = []
        total = 0

        for agent in agents:
            cost_data = self.calculate_agent_cost(agent)
            agent_costs.append(cost_data)
            total += cost_data['total_cost_numeric']

        # Add orchestration overhead
        orchestration_cost = 0.0001  # InputAnalyzer + PlannerFinal
        total += orchestration_cost

        return {
            'party_id': 'example_party',
            'agents_executed': len(agents),
            'agent_costs': agent_costs,
            'orchestration_cost': f"${orchestration_cost:.6f}",
            'total_cost': f"${total:.6f}",
            'total_cost_numeric': total
        }


# Example Usage:
calculator = PartyCostCalculator()

# Scenario 1: Complete party planning (5 agents)
complete_party_cost = calculator.calculate_party_cost([
    'theme_agent',
    'venue_agent',
    'cake_agent',
    'catering_agent',
    'budget_agent'
])

print(json.dumps(complete_party_cost, indent=2))
```

---

### **Cost Results: Single Party Execution**

```json
{
  "party_id": "fp2025A12345",
  "agents_executed": 5,
  "agent_costs": [
    {
      "agent": "theme_agent",
      "breakdown": {
        "openai_llm": "$0.000255",
        "vector_db": "$0.000200",
        "compute": "$0.000150",
        "redis": "$0.000003",
        "postgresql": "$0.000010"
      },
      "total_cost": "$0.000618"
    },
    {
      "agent": "venue_agent",
      "breakdown": {
        "openai_llm": "$0.000420",
        "vector_db": "$0.000300",
        "compute": "$0.000200",
        "redis": "$0.000005",
        "postgresql": "$0.000015"
      },
      "total_cost": "$0.000940"
    },
    {
      "agent": "cake_agent",
      "breakdown": {
        "openai_llm": "$0.000330",
        "vector_db": "$0.000200",
        "compute": "$0.000150",
        "redis": "$0.000003",
        "postgresql": "$0.000010"
      },
      "total_cost": "$0.000693"
    },
    {
      "agent": "catering_agent",
      "breakdown": {
        "openai_llm": "$0.000375",
        "vector_db": "$0.000200",
        "compute": "$0.000180",
        "redis": "$0.000004",
        "postgresql": "$0.000010"
      },
      "total_cost": "$0.000769"
    },
    {
      "agent": "budget_agent",
      "breakdown": {
        "openai_llm": "$0.000000",
        "vector_db": "$0.000000",
        "compute": "$0.000030",
        "redis": "$0.000008",
        "postgresql": "$0.000005"
      },
      "total_cost": "$0.000043"
    }
  ],
  "orchestration_cost": "$0.000100",
  "total_cost": "$0.003163",
  "total_cost_numeric": 0.003163
}
```

### **Summary: Cost Per Party**

```
┌─────────────────────────────────────────────────────────────┐
│         COST BREAKDOWN: SINGLE PARTY (5 AGENTS)              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Component                   Cost        Percentage          │
│  ─────────────────────────────────────────────────────      │
│  OpenAI LLM Calls            $0.001380      43.6%           │
│  Vector DB Queries           $0.000900      28.4%           │
│  Compute (K8s pods)          $0.000710      22.4%           │
│  Redis Operations            $0.000023       0.7%           │
│  PostgreSQL Queries          $0.000050       1.6%           │
│  Orchestration Overhead      $0.000100       3.2%           │
│  ─────────────────────────────────────────────────────      │
│  TOTAL PER PARTY             $0.003163     100.0%           │
│                                                              │
│  At 100K parties/month:                                     │
│  Monthly Cost: 100,000 × $0.003163 = $316.30               │
│                                                              │
│  With re-runs & edits (avg 1.5x):                           │
│  Actual Monthly Cost: $316.30 × 1.5 = $474.45              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## **CASE 3: How to Save Money on Agent Infrastructure**

### **The Core Problem**
```
Current Architecture:
  - Every agent runs on separate pods
  - LLM calls for every execution
  - Vector DB queries for every search
  - No result caching across users

Cost Breakdown (per party):
  - LLM: $0.001380 (44%) ← BIGGEST COST
  - Vector DB: $0.000900 (28%)
  - Compute: $0.000710 (22%)
  - Data: $0.000173 (6%)

Goal: Reduce cost by 60-80% while maintaining quality
```

---

### **Money-Saving Strategies**

#### **Strategy 1: Aggressive Result Caching (Save 40-60%)**

```python
# app/services/intelligent_cache.py

class IntelligentCacheManager:
    """
    Cache agent results across users for similar inputs

    Example:
    - User A: "jungle theme party" → ThemeAgent executes
    - User B: "jungle themed birthday" → Reuse cached result
    - Savings: 1 LLM call saved = $0.000255
    """

    async def get_or_execute_agent(
        self,
        agent_name: str,
        inputs: Dict,
        party_id: str
    ) -> Dict:
        """
        Check cache before executing agent
        """
        # 1. Generate cache key (normalized input)
        cache_key = self._generate_cache_key(agent_name, inputs)

        # 2. Check Redis cache
        cached_result = await redis.get(f"agent_cache:{cache_key}")

        if cached_result:
            logger.info("Cache HIT - Reusing result",
                       agent=agent_name,
                       cache_key=cache_key,
                       cost_saved="$0.000255")

            return {
                "result": json.loads(cached_result),
                "cache_hit": True,
                "cost_saved": 0.000255
            }

        # 3. Cache MISS - Execute agent
        result = await self._execute_agent(agent_name, inputs, party_id)

        # 4. Store in cache (TTL: 7 days)
        await redis.setex(
            f"agent_cache:{cache_key}",
            604800,  # 7 days
            json.dumps(result)
        )

        logger.info("Cache MISS - Executed and cached",
                   agent=agent_name,
                   cache_key=cache_key)

        return {
            "result": result,
            "cache_hit": False,
            "cost_saved": 0
        }

    def _generate_cache_key(self, agent_name: str, inputs: Dict) -> str:
        """
        Generate normalized cache key

        Example normalization:
        - "jungle theme" → "jungle"
        - "JUNGLE PARTY" → "jungle"
        - "75 guests" → "75"
        - "chocolate cake" → "chocolate_cake"
        """
        if agent_name == 'theme_agent':
            # Extract theme keywords
            content = inputs.get('content', '').lower()
            theme_keywords = ['jungle', 'space', 'princess', 'dinosaur', 'unicorn']

            for keyword in theme_keywords:
                if keyword in content:
                    return f"theme:{keyword}"

            return f"theme:general"

        elif agent_name == 'venue_agent':
            # Extract guest count
            import re
            content = inputs.get('content', '')
            numbers = re.findall(r'\d+', content)
            guest_count = int(numbers[0]) if numbers else 50

            # Round to nearest 25 for cache efficiency
            rounded_guests = round(guest_count / 25) * 25

            return f"venue:guests_{rounded_guests}"

        elif agent_name == 'cake_agent':
            content = inputs.get('content', '').lower()
            flavors = ['chocolate', 'vanilla', 'strawberry', 'red_velvet']

            for flavor in flavors:
                if flavor in content:
                    return f"cake:{flavor}"

            return f"cake:custom"

        # Default: hash of content
        import hashlib
        content_hash = hashlib.md5(
            str(inputs).encode()
        ).hexdigest()[:12]

        return f"{agent_name}:{content_hash}"


# Savings Calculation:
# - Cache hit rate: 60% (based on similar user inputs)
# - LLM cost per call: $0.000255
# - With 100K parties/month:
#   - Without cache: 100K × $0.001380 = $138.00/month
#   - With cache (60% hit): 40K × $0.001380 = $55.20/month
#   - SAVINGS: $82.80/month (60%)
```

---

#### **Strategy 2: Model Downgrading (Save 30-50%)**

```python
# Use cheaper models for simple tasks

class ModelSelector:
    """
    Use appropriate model based on task complexity
    """

    def select_model(self, agent_name: str, complexity: str) -> str:
        """
        GPT-4o: $0.00255 per 1K tokens (complex reasoning)
        GPT-4o-mini: $0.00075 per 1K tokens (simple tasks) ← 70% cheaper
        GPT-3.5-turbo: $0.0005 per 1K tokens (very simple) ← 80% cheaper
        """

        model_map = {
            # Complex reasoning required
            'theme_agent_complex': 'gpt-4o-mini',  # Was: gpt-4o
            'venue_agent_complex': 'gpt-4o-mini',

            # Simple classification
            'input_classifier': 'gpt-3.5-turbo',  # 80% cheaper
            'budget_agent': None,  # No LLM needed (pure math)

            # Medium complexity
            'cake_agent': 'gpt-4o-mini',
            'catering_agent': 'gpt-4o-mini'
        }

        return model_map.get(agent_name, 'gpt-4o-mini')


# Savings Calculation:
# - Old: GPT-4o for all agents
# - New: GPT-4o-mini (70% cheaper) + GPT-3.5-turbo (80% cheaper)
# - Average savings: 50% on LLM costs
# - With 100K parties: $138/month → $69/month
# - SAVINGS: $69/month (50%)
```

---

#### **Strategy 3: Batch Processing (Save 20-30%)**

```python
# Process multiple parties in batches to reduce overhead

class BatchProcessor:
    """
    Batch process similar agent requests
    """

    async def batch_execute_agent(
        self,
        agent_name: str,
        requests: List[Dict]  # Multiple party requests
    ) -> List[Dict]:
        """
        Execute agent for multiple parties in one API call

        Example:
        - Party A: "jungle theme"
        - Party B: "space theme"
        - Party C: "princess theme"

        Instead of 3 API calls:
        → 1 batched API call with all 3

        Savings: Reduce API overhead by 30%
        """
        # OpenAI Batch API (50% cheaper)
        batch_request = {
            "model": "gpt-4o-mini",
            "messages": [
                self._create_prompt(req) for req in requests
            ]
        }

        # Single API call for all requests
        batch_response = await openai_client.batch_complete(batch_request)

        # Parse results
        results = []
        for i, req in enumerate(requests):
            results.append({
                "party_id": req['party_id'],
                "result": batch_response[i]
            })

        return results


# Savings Calculation:
# - Batch API: 50% cheaper than regular API
# - Reduces network overhead
# - With 100K parties: $138/month → $96.60/month
# - SAVINGS: $41.40/month (30%)
```

---

#### **Strategy 4: Local Model for Classification (Save 90%)**

```python
# Use local BERT model for input classification instead of GPT

class LocalClassifier:
    """
    Use local BERT model for input classification

    Cost Comparison:
    - GPT-4o-mini: $0.00075 per classification
    - Local BERT: $0.00008 per classification (compute only)
    - SAVINGS: 90%
    """

    def __init__(self):
        # Load pre-trained BERT model
        from transformers import AutoTokenizer, AutoModelForSequenceClassification

        self.tokenizer = AutoTokenizer.from_pretrained(
            "distilbert-base-uncased-finetuned-sst-2-english"
        )
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "custom-party-classifier"  # Fine-tuned on party planning data
        )

    async def classify_input(self, text: str) -> Dict:
        """
        Classify input locally (no API call)
        """
        inputs = self.tokenizer(text, return_tensors="pt")
        outputs = self.model(**inputs)

        # Get classification
        predictions = torch.softmax(outputs.logits, dim=1)

        return {
            "categories": ["theme", "venue", "cake"],
            "confidences": predictions.tolist()[0],
            "cost": 0.00008  # Compute only
        }


# Savings Calculation:
# - 100K parties × 3 classifications each = 300K classifications
# - Old: 300K × $0.00075 = $225/month
# - New: 300K × $0.00008 = $24/month
# - SAVINGS: $201/month (89%)
```

---

#### **Strategy 5: Vector DB Optimization (Save 40-60%)**

```python
# Reduce vector queries with smarter indexing

class VectorDBOptimizer:
    """
    Optimize vector database queries
    """

    async def search_venues(self, query: str, filters: Dict) -> List[Dict]:
        """
        Old approach:
        - Query all venues (1000+)
        - Filter in application
        - Cost: $0.0001 × 3 queries = $0.0003

        New approach:
        - Pre-filter by metadata (capacity, location)
        - Query only relevant subset (50)
        - Cost: $0.0001 × 1 query = $0.0001

        SAVINGS: 67%
        """
        # 1. Pre-filter using metadata (free)
        metadata_filter = {
            "capacity_min": filters.get('guest_count', 0),
            "capacity_max": filters.get('guest_count', 0) * 1.5,
            "city": filters.get('location', 'any')
        }

        # 2. Single optimized vector query
        results = await pinecone_index.query(
            vector=self._embed(query),
            top_k=5,
            include_metadata=True,
            filter=metadata_filter  # Reduces search space by 95%
        )

        return results


# Savings Calculation:
# - Old: 3 queries per party × $0.0001 = $0.0003
# - New: 1 query per party × $0.0001 = $0.0001
# - Per 100K parties: $30/month → $10/month
# - SAVINGS: $20/month (67%)
```

---

### **Combined Savings Strategy**

```
┌──────────────────────────────────────────────────────────────────┐
│              COST OPTIMIZATION: BEFORE vs AFTER                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Component          Before      After      Strategy    Savings   │
│  ────────────────────────────────────────────────────────────   │
│  LLM Calls          $138.00     $34.50     Cache 60%    75%      │
│                                            + Model       │        │
│                                              downgrade   │        │
│                                                                   │
│  Classification     $225.00     $24.00     Local BERT   89%      │
│                                                                   │
│  Vector DB          $90.00      $30.00     Smart        67%      │
│                                            indexing     │        │
│                                                                   │
│  Compute            $71.00      $50.00     Batch        30%      │
│                                            processing   │        │
│                                                                   │
│  Data Ops           $17.30      $17.30     -            0%       │
│                                                                   │
│  ────────────────────────────────────────────────────────────   │
│  TOTAL              $541.30     $155.80                 71%      │
│  Per 100K parties                                               │
│                                                                   │
│  Cost per party:    $0.00541    $0.00156              -$0.00385 │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘

TOTAL SAVINGS: $385.50/month (71% reduction)
Per party savings: $0.00385 → At 1M parties/year: $3,850 saved
```

---

### **Best Practices Summary**

#### **1. Cache Everything**
```python
- Agent results (by normalized input)
- Vector embeddings (by text)
- API responses (by parameters)
- Database query results (by filters)

Cache Hierarchy:
L1: In-memory (hot data, 5 min TTL)
L2: Redis (warm data, 7 day TTL)
L3: PostgreSQL (cold data, permanent)
```

#### **2. Use Cheapest Model That Works**
```python
Classification → Local BERT (90% cheaper)
Simple tasks → GPT-3.5-turbo (80% cheaper)
Medium tasks → GPT-4o-mini (70% cheaper)
Complex reasoning → GPT-4o (when necessary)
```

#### **3. Batch When Possible**
```python
- Use OpenAI Batch API (50% discount)
- Process multiple parties together
- Combine similar requests
```

#### **4. Optimize Vector DB**
```python
- Pre-filter with metadata
- Reduce query dimensions
- Use hybrid search (keyword + vector)
- Cache frequent queries
```

#### **5. Monitor & Optimize**
```python
# Track cost per agent
async def track_agent_cost(agent_name, cost):
    await redis.hincrby(
        f"costs:{datetime.now().strftime('%Y-%m')}",
        agent_name,
        int(cost * 1000000)  # Store as microdollars
    )

# Monthly cost report
async def generate_cost_report():
    costs = await redis.hgetall(f"costs:2025-10")

    # Identify expensive agents
    expensive = sorted(
        costs.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # Optimize top 3 expensive agents
    for agent, cost in expensive[:3]:
        logger.warning(f"Optimize {agent}: ${cost/1000000:.2f}")
```

---

**END OF CASE STUDIES**
