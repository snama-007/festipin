# 📋 Event Schemas & Frontend Integration Guide

**Version:** 1.0
**Date:** October 21, 2025
**Purpose:** Complete data schema reference for agent inputs, outputs, and frontend WebSocket integration

---

## 📊 Table of Contents

1. [Event Bus Topic Schemas](#event-bus-topic-schemas)
2. [Agent Input/Output Schemas](#agent-inputoutput-schemas)
3. [Frontend WebSocket Integration](#frontend-websocket-integration)
4. [Complete Data Flow Examples](#complete-data-flow-examples)
5. [TypeScript/React Integration](#typescriptreact-integration)

---

## 1. Event Bus Topic Schemas

### **Event Structure (Base)**

All events follow this base structure:

```typescript
interface BaseEvent {
  event_id: string;           // UUID v4
  party_id: string;           // Party session ID (fp2025A12345)
  event_type: string;         // Event type (see below)
  timestamp: string;          // ISO 8601 timestamp
  correlation_id: string;     // For tracing related events
  payload: object;            // Event-specific data
  metadata?: object;          // Optional metadata
}
```

---

### **Topic: `party.input.added`**

**When:** User adds a new input (text, image, URL)

```typescript
interface InputAddedEvent extends BaseEvent {
  event_type: "party.input.added";
  payload: {
    input_id: string;           // Unique input ID
    content: string;            // User input text
    source_type: "text" | "image" | "url" | "upload";
    tags: string[];             // Auto-detected tags
    added_by: string;           // User ID
    metadata?: {
      image_url?: string;
      pinterest_url?: string;
      file_size?: number;
    };
  };
}
```

**Example:**
```json
{
  "event_id": "evt_abc123",
  "party_id": "fp2025A12345",
  "event_type": "party.input.added",
  "timestamp": "2025-10-21T10:30:00Z",
  "correlation_id": "corr_xyz",
  "payload": {
    "input_id": "inp_1",
    "content": "I want a jungle theme party for my 5 year old",
    "source_type": "text",
    "tags": ["theme", "age"],
    "added_by": "user_xyz"
  }
}
```

---

### **Topic: `party.input.removed`**

**When:** User removes an input

```typescript
interface InputRemovedEvent extends BaseEvent {
  event_type: "party.input.removed";
  payload: {
    input_id: string;
    removed_by: string;
    reason: "user_action" | "duplicate" | "invalid";
  };
}
```

---

### **Topic: `party.agent.should_execute`**

**When:** InputAnalyzer determines an agent needs to run

```typescript
interface AgentShouldExecuteEvent extends BaseEvent {
  event_type: "party.agent.should_execute";
  payload: {
    agent_name: "theme_agent" | "venue_agent" | "cake_agent" | "budget_agent";
    execution_type: "start" | "rerun" | "recalculate";
    input_ids: string[];        // Relevant inputs for this agent
    priority: number;           // 1 (high) to 4 (low)
    reason?: string;            // Why agent is being triggered
  };
}
```

**Example:**
```json
{
  "event_id": "evt_def456",
  "party_id": "fp2025A12345",
  "event_type": "party.agent.should_execute",
  "timestamp": "2025-10-21T10:30:05Z",
  "correlation_id": "corr_xyz",
  "payload": {
    "agent_name": "theme_agent",
    "execution_type": "start",
    "input_ids": ["inp_1"],
    "priority": 1,
    "reason": "new_theme_input_detected"
  }
}
```

---

### **Topic: `party.agent.started`**

**When:** Agent begins execution

```typescript
interface AgentStartedEvent extends BaseEvent {
  event_type: "party.agent.started";
  payload: {
    agent_name: string;
    execution_id: string;       // UUID for this specific execution
    input_count: number;        // Number of inputs being processed
  };
}
```

---

### **Topic: `party.agent.completed`**

**When:** Agent finishes successfully

```typescript
interface AgentCompletedEvent extends BaseEvent {
  event_type: "party.agent.completed";
  payload: {
    agent_name: string;
    execution_id: string;
    result: object;             // Agent-specific result (see Agent Output Schemas)
    confidence: number;         // 0.0 - 1.0
    execution_time_ms: number;
  };
}
```

**Example:**
```json
{
  "event_id": "evt_ghi789",
  "party_id": "fp2025A12345",
  "event_type": "party.agent.completed",
  "timestamp": "2025-10-21T10:30:10Z",
  "correlation_id": "corr_xyz",
  "payload": {
    "agent_name": "theme_agent",
    "execution_id": "exec_123",
    "result": {
      "primary_theme": "jungle",
      "confidence": 0.92,
      "colors": ["green", "brown", "yellow"],
      "decorations": ["animal balloons", "leaf garlands"],
      "activities": ["animal charades", "safari hunt"]
    },
    "confidence": 0.92,
    "execution_time_ms": 1250
  }
}
```

---

### **Topic: `party.agent.failed`**

**When:** Agent execution fails

```typescript
interface AgentFailedEvent extends BaseEvent {
  event_type: "party.agent.failed";
  payload: {
    agent_name: string;
    execution_id: string;
    error: string;
    error_type: "timeout" | "validation" | "external_api" | "internal";
    retry_count: number;
  };
}
```

---

### **Topic: `party.budget.updated`**

**When:** Budget is recalculated (after any cost-related agent completes)

```typescript
interface BudgetUpdatedEvent extends BaseEvent {
  event_type: "party.budget.updated";
  payload: {
    total_budget: {
      min: number;
      max: number;
    };
    previous_total?: {
      min: number;
      max: number;
    };
    delta?: {
      min: number;
      max: number;
    };
    breakdown: {
      [category: string]: {
        min: number;
        max: number;
        note?: string;
      };
    };
    based_on_agents: string[];  // Which agents contributed to this budget
  };
}
```

**Example:**
```json
{
  "event_id": "evt_jkl012",
  "party_id": "fp2025A12345",
  "event_type": "party.budget.updated",
  "timestamp": "2025-10-21T10:35:00Z",
  "correlation_id": "corr_xyz",
  "payload": {
    "total_budget": {"min": 950, "max": 2400},
    "previous_total": {"min": 800, "max": 2100},
    "delta": {"min": 150, "max": 300},
    "breakdown": {
      "venue": {"min": 0, "max": 0, "note": "Free (permit required)"},
      "cake": {"min": 80, "max": 300},
      "catering": {"min": 450, "max": 900},
      "vendors": {"min": 420, "max": 1200}
    },
    "based_on_agents": ["venue_agent", "cake_agent", "catering_agent", "vendor_agent"]
  }
}
```

---

### **Topic: `party.plan.updated`**

**When:** FinalPlanner generates/updates the complete plan

```typescript
interface PlanUpdatedEvent extends BaseEvent {
  event_type: "party.plan.updated";
  payload: {
    completion_percent: number;
    recommendations: Array<{
      category: string;
      priority: "low" | "medium" | "high" | "critical";
      description: string;
    }>;
    next_steps: string[];
    missing_agents: string[];   // Agents that haven't run yet
    active_agents: string[];    // Agents that have completed
    checklist_summary: {
      total_tasks: number;
      completed_tasks: number;
      pending_tasks: number;
    };
  };
}
```

---

## 2. Agent Input/Output Schemas

### **Standard Agent Input**

All agents receive this standardized input:

```typescript
interface AgentInput {
  agent_type: string;           // e.g., "theme_agent"
  event_id: string;             // Workflow event ID
  inputs: Array<{
    input_id: string;
    content: string;
    source_type: string;
    tags: string[];
    metadata?: object;
  }>;
  context: {
    party_id: string;
    agent_results?: {           // Results from previously completed agents
      [agent_name: string]: object;
    };
    user_preferences?: object;
    existing_plan?: object;
  };
}
```

---

### **Standard Agent Output**

All agents return this standardized output:

```typescript
interface AgentOutput {
  agent_type: string;
  result: object;               // Agent-specific result (see below)
  confidence: number;           // 0.0 - 1.0
  execution_time: number;       // Seconds
  metadata: {
    [key: string]: any;
  };
}
```

---

### **Agent-Specific Result Schemas**

#### **1. InputAnalyzer (Always-Running)**

**Input:** Raw user inputs
**Output:**

```typescript
interface InputAnalyzerResult {
  classified_inputs: {
    theme?: Array<InputItem>;
    cake?: Array<InputItem>;
    venue?: Array<InputItem>;
    catering?: Array<InputItem>;
    vendor?: Array<InputItem>;
    budget?: Array<InputItem>;
  };
  routing_plan: Array<{
    agent_name: string;
    priority: number;
    input_ids: string[];
  }>;
}
```

---

#### **2. ThemeAgent (Dynamic)**

**Input:** Inputs tagged with "theme"
**Output:**

```typescript
interface ThemeAgentResult {
  primary_theme: string;        // e.g., "jungle", "unicorn", "space"
  theme_scores: {
    [theme: string]: number;    // Confidence scores for each theme
  };
  confidence: number;           // Overall confidence
  colors: string[];             // ["green", "brown", "yellow"]
  decorations: string[];        // ["animal balloons", "leaf garlands"]
  activities: string[];         // ["animal charades", "safari hunt"]
  style_tags?: string[];        // Additional style descriptors
}
```

**Example:**
```json
{
  "primary_theme": "jungle",
  "theme_scores": {
    "jungle": 8,
    "safari": 5,
    "animal": 3
  },
  "confidence": 0.92,
  "colors": ["green", "brown", "yellow", "orange"],
  "decorations": [
    "animal balloons",
    "leaf garlands",
    "safari props"
  ],
  "activities": [
    "animal charades",
    "safari hunt",
    "jungle obstacle course"
  ]
}
```

---

#### **3. VenueAgent (Dynamic)**

**Input:** Guest count, budget, theme
**Output:**

```typescript
interface VenueAgentResult {
  recommended_venues: Array<{
    id: string;
    name: string;
    type: "park" | "banquet_hall" | "restaurant" | "home" | "other";
    capacity: number;
    location: string;
    daily_price: number;        // 0 for free venues
    amenities: string[];
    rating: number;             // 1.0 - 5.0
    theme_fit_score: number;    // 0.0 - 1.0
    notes?: string;
  }>;
  total_matches: number;
  search_criteria: {
    guest_count: number;
    budget: number;
    theme: string;
  };
  data_source: "mock_database" | "real_database" | "api";
}
```

**Example:**
```json
{
  "recommended_venues": [
    {
      "id": "venue_1",
      "name": "Riverside Park",
      "type": "park",
      "capacity": 100,
      "location": "Downtown",
      "daily_price": 0,
      "amenities": ["picnic tables", "playground", "pavilion"],
      "rating": 4.5,
      "theme_fit_score": 0.9,
      "notes": "Permit required ($50). Great for outdoor jungle theme."
    }
  ],
  "total_matches": 5,
  "search_criteria": {
    "guest_count": 75,
    "budget": 1000,
    "theme": "jungle"
  },
  "data_source": "mock_database"
}
```

---

#### **4. CakeAgent (Dynamic)**

**Input:** Theme, age, guest count
**Output:**

```typescript
interface CakeAgentResult {
  recommended_bakeries: Array<{
    id: string;
    name: string;
    specialties: string[];
    custom_designs: boolean;
    dietary_options: string[];
    price_range: {
      small: number;
      medium: number;
      large: number;
    };
    rating: number;
    lead_time_days: number;
    theme_match_score: number;
  }>;
  cake_style: "traditional" | "modern" | "themed" | "custom";
  theme: string;
  decorations: string[];
  estimated_cost: {
    min: number;
    max: number;
  };
  size_recommendation: "small" | "medium" | "large";
}
```

**Example:**
```json
{
  "recommended_bakeries": [
    {
      "id": "bakery_1",
      "name": "Sweet Dreams Bakery",
      "specialties": ["Custom Designs", "Fondant Art"],
      "custom_designs": true,
      "dietary_options": ["Vegan", "Gluten-Free"],
      "price_range": {
        "small": 80,
        "medium": 150,
        "large": 300
      },
      "rating": 4.8,
      "lead_time_days": 7,
      "theme_match_score": 0.95
    }
  ],
  "cake_style": "themed",
  "theme": "jungle",
  "decorations": [
    "animal figurines",
    "leaf patterns",
    "safari colors"
  ],
  "estimated_cost": {
    "min": 80,
    "max": 300
  },
  "size_recommendation": "medium"
}
```

---

#### **5. BudgetAgent (Reactive - Always-Running)**

**Input:** All completed agent results
**Output:**

```typescript
interface BudgetAgentResult {
  total_budget: {
    min: number;
    max: number;
  };
  breakdown: {
    [category: string]: {
      min: number;
      max: number;
      note?: string;
    };
  };
  recommendations: string[];
  cost_saving_tips: string[];
  data_source: "actual_agent_results" | "estimates";
  completion_level: "partial" | "complete";
}
```

---

#### **6. FinalPlanner (Reactive - Always-Running)**

**Input:** All agent results + budget
**Output:**

```typescript
interface FinalPlannerResult {
  completion_percent: number;
  recommendations: Array<{
    category: string;
    priority: "low" | "medium" | "high" | "critical";
    description: string;
    estimated_cost?: {
      min: number;
      max: number;
    };
  }>;
  next_steps: Array<{
    step: string;
    deadline?: string;
    assigned_agent?: string;
  }>;
  active_agents: string[];
  missing_agents: string[];
  checklist: Array<{
    category: string;
    items: Array<{
      task: string;
      priority: string;
      status: string;
      estimated_cost?: {
        min: number;
        max: number;
      };
    }>;
  }>;
  budget_summary: {
    min: number;
    max: number;
    breakdown: object;
  };
  last_updated: string;
}
```

---

## 3. Frontend WebSocket Integration

### **Connection Setup**

**WebSocket URL:**
```
ws://localhost:9000/ws/orchestration/{party_id}
```

### **React Hook Example**

```typescript
import { useEffect, useState } from 'react';

interface AgentUpdate {
  type: string;
  agent?: string;
  status?: string;
  result?: any;
  message?: string;
  timestamp: string;
}

export function useAgentUpdates(partyId: string) {
  const [updates, setUpdates] = useState<AgentUpdate[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    // Connect to WebSocket
    const websocket = new WebSocket(
      `ws://localhost:9000/ws/orchestration/${partyId}`
    );

    websocket.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);

      // Send initial ping
      websocket.send(JSON.stringify({ type: 'ping' }));
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Agent update:', data);

      setUpdates(prev => [...prev, data]);

      // Handle different event types
      switch (data.type) {
        case 'connection':
          console.log('Connection established:', data);
          break;

        case 'agent_started':
          console.log(`Agent ${data.agent} started`);
          break;

        case 'agent_completed':
          console.log(`Agent ${data.agent} completed:`, data.result);
          break;

        case 'agent_failed':
          console.error(`Agent ${data.agent} failed:`, data.error);
          break;

        case 'budget_updated':
          console.log('Budget updated:', data.payload);
          break;

        case 'plan_updated':
          console.log('Plan updated:', data.payload);
          break;

        case 'pong':
          // Heartbeat response
          break;
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    websocket.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };

    setWs(websocket);

    // Cleanup
    return () => {
      websocket.close();
    };
  }, [partyId]);

  // Send heartbeat every 30 seconds
  useEffect(() => {
    if (!ws || !isConnected) return;

    const interval = setInterval(() => {
      ws.send(JSON.stringify({ type: 'ping' }));
    }, 30000);

    return () => clearInterval(interval);
  }, [ws, isConnected]);

  return { updates, isConnected, ws };
}
```

### **Usage in Component**

```typescript
function PartyPlanningDashboard({ partyId }: { partyId: string }) {
  const { updates, isConnected } = useAgentUpdates(partyId);

  // Track agent states
  const [agentStates, setAgentStates] = useState<{
    [agentName: string]: {
      status: 'idle' | 'running' | 'completed' | 'failed';
      result?: any;
      error?: string;
    };
  }>({});

  // Track budget
  const [budget, setBudget] = useState<any>(null);

  // Track final plan
  const [finalPlan, setFinalPlan] = useState<any>(null);

  useEffect(() => {
    // Process latest update
    const latestUpdate = updates[updates.length - 1];
    if (!latestUpdate) return;

    switch (latestUpdate.type) {
      case 'agent_started':
        setAgentStates(prev => ({
          ...prev,
          [latestUpdate.agent!]: {
            status: 'running',
          }
        }));
        break;

      case 'agent_completed':
        setAgentStates(prev => ({
          ...prev,
          [latestUpdate.agent!]: {
            status: 'completed',
            result: latestUpdate.result,
          }
        }));
        break;

      case 'agent_failed':
        setAgentStates(prev => ({
          ...prev,
          [latestUpdate.agent!]: {
            status: 'failed',
            error: latestUpdate.error,
          }
        }));
        break;

      case 'budget_updated':
        setBudget(latestUpdate.payload);
        break;

      case 'plan_updated':
        setFinalPlan(latestUpdate.payload);
        break;
    }
  }, [updates]);

  return (
    <div>
      <div>Connection: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}</div>

      <h2>Agent Progress</h2>
      {Object.entries(agentStates).map(([agentName, state]) => (
        <div key={agentName}>
          <span>{agentName}</span>
          <span>{state.status}</span>
          {state.status === 'completed' && <pre>{JSON.stringify(state.result, null, 2)}</pre>}
          {state.status === 'failed' && <span>Error: {state.error}</span>}
        </div>
      ))}

      <h2>Budget</h2>
      {budget && (
        <div>
          <div>Total: ${budget.total_budget.min} - ${budget.total_budget.max}</div>
          <pre>{JSON.stringify(budget.breakdown, null, 2)}</pre>
        </div>
      )}

      <h2>Final Plan</h2>
      {finalPlan && (
        <div>
          <div>Completion: {finalPlan.completion_percent}%</div>
          <div>Next Steps:</div>
          <ul>
            {finalPlan.next_steps.map((step: string, i: number) => (
              <li key={i}>{step}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

---

## 4. Complete Data Flow Examples

### **Example 1: User Adds Theme Input**

**Step 1: User submits input**
```
Frontend → POST /api/v1/orchestration/start
Body: {
  "inputs": [
    {
      "content": "I want a jungle theme party for 75 guests",
      "source_type": "text"
    }
  ]
}
```

**Step 2: Backend emits event**
```
Event Bus → party.input.added
{
  "event_id": "evt_1",
  "party_id": "fp2025A12345",
  "event_type": "party.input.added",
  "payload": {
    "input_id": "inp_1",
    "content": "I want a jungle theme party for 75 guests",
    "source_type": "text",
    "tags": ["theme", "venue"],
    "added_by": "user_xyz"
  }
}
```

**Step 3: InputAnalyzer processes event**
```
InputAnalyzer → Classifies input
Result: theme=["jungle"], venue=["75 guests"]

Emits: party.agent.should_execute
{
  "payload": {
    "agent_name": "theme_agent",
    "execution_type": "start",
    "priority": 1
  }
}
```

**Step 4: ThemeAgent executes**
```
Event Bus → party.agent.started
WebSocket → Frontend receives:
{
  "type": "agent_started",
  "agent": "theme_agent",
  "message": "Analyzing party theme..."
}

ThemeAgent runs...

Event Bus → party.agent.completed
WebSocket → Frontend receives:
{
  "type": "agent_completed",
  "agent": "theme_agent",
  "status": "completed",
  "result": {
    "primary_theme": "jungle",
    "confidence": 0.92,
    "colors": ["green", "brown", "yellow"],
    "decorations": ["animal balloons", "leaf garlands"],
    "activities": ["animal charades", "safari hunt"]
  }
}
```

**Step 5: VenueAgent triggers (depends on theme)**
```
Event Bus → party.agent.should_execute
{
  "payload": {
    "agent_name": "venue_agent",
    "execution_type": "start",
    "priority": 2,
    "reason": "dependency_on_theme_agent"
  }
}

VenueAgent executes...

WebSocket → Frontend receives:
{
  "type": "agent_completed",
  "agent": "venue_agent",
  "result": {
    "recommended_venues": [...]
  }
}
```

**Step 6: BudgetAgent recalculates**
```
Event Bus → party.budget.updated
WebSocket → Frontend receives:
{
  "type": "budget_updated",
  "payload": {
    "total_budget": {"min": 500, "max": 1500},
    "breakdown": {...}
  }
}
```

**Step 7: FinalPlanner updates**
```
Event Bus → party.plan.updated
WebSocket → Frontend receives:
{
  "type": "plan_updated",
  "payload": {
    "completion_percent": 60,
    "next_steps": ["Add cake preferences", "Specify catering needs"],
    "active_agents": ["theme_agent", "venue_agent"],
    "missing_agents": ["cake_agent", "catering_agent"]
  }
}
```

---

### **Example 2: User Removes Input**

**Step 1: User removes an input**
```
Frontend → DELETE /api/v1/orchestration/input/{input_id}
```

**Step 2: Backend emits event**
```
Event Bus → party.input.removed
```

**Step 3: InputAnalyzer checks if agents still needed**
```
If no other theme inputs exist:
  Emit: party.agent.data_removed
  {
    "payload": {
      "agent_name": "theme_agent",
      "reason": "no_relevant_inputs"
    }
  }
```

**Step 4: State cleanup**
```
StateStore → Removes theme_agent result
BudgetAgent → Recalculates budget
FinalPlanner → Updates plan

WebSocket → Frontend receives updates
```

---

## 5. TypeScript/React Integration

### **Complete Type Definitions**

```typescript
// event-types.ts

export interface BaseEvent {
  event_id: string;
  party_id: string;
  event_type: string;
  timestamp: string;
  correlation_id: string;
  payload: any;
  metadata?: Record<string, any>;
}

export interface AgentStartedEvent extends BaseEvent {
  type: 'agent_started';
  agent: string;
  message: string;
}

export interface AgentCompletedEvent extends BaseEvent {
  type: 'agent_completed';
  agent: string;
  status: 'completed';
  result: any;
  confidence: number;
  execution_time_ms: number;
}

export interface AgentFailedEvent extends BaseEvent {
  type: 'agent_failed';
  agent: string;
  status: 'failed';
  error: string;
}

export interface BudgetUpdatedEvent extends BaseEvent {
  type: 'budget_updated';
  payload: {
    total_budget: { min: number; max: number };
    breakdown: Record<string, { min: number; max: number; note?: string }>;
  };
}

export interface PlanUpdatedEvent extends BaseEvent {
  type: 'plan_updated';
  payload: {
    completion_percent: number;
    recommendations: Array<{
      category: string;
      priority: string;
      description: string;
    }>;
    next_steps: string[];
    active_agents: string[];
    missing_agents: string[];
  };
}

export type AgentEvent =
  | AgentStartedEvent
  | AgentCompletedEvent
  | AgentFailedEvent
  | BudgetUpdatedEvent
  | PlanUpdatedEvent;

// Agent result types
export interface ThemeResult {
  primary_theme: string;
  confidence: number;
  colors: string[];
  decorations: string[];
  activities: string[];
}

export interface VenueResult {
  recommended_venues: Array<{
    id: string;
    name: string;
    type: string;
    capacity: number;
    daily_price: number;
    rating: number;
  }>;
  search_criteria: {
    guest_count: number;
    budget: number;
    theme: string;
  };
}

export interface CakeResult {
  recommended_bakeries: Array<{
    id: string;
    name: string;
    rating: number;
    price_range: {
      small: number;
      medium: number;
      large: number;
    };
  }>;
  cake_style: string;
  estimated_cost: { min: number; max: number };
}
```

### **State Management (Zustand Example)**

```typescript
// store/partyPlanStore.ts
import create from 'zustand';

interface AgentState {
  status: 'idle' | 'running' | 'completed' | 'failed';
  result?: any;
  error?: string;
}

interface PartyPlanStore {
  partyId: string | null;
  agentStates: Record<string, AgentState>;
  budget: any | null;
  finalPlan: any | null;
  isConnected: boolean;

  setPartyId: (id: string) => void;
  updateAgentState: (agent: string, state: AgentState) => void;
  updateBudget: (budget: any) => void;
  updateFinalPlan: (plan: any) => void;
  setConnectionStatus: (connected: boolean) => void;
  reset: () => void;
}

export const usePartyPlanStore = create<PartyPlanStore>((set) => ({
  partyId: null,
  agentStates: {},
  budget: null,
  finalPlan: null,
  isConnected: false,

  setPartyId: (id) => set({ partyId: id }),

  updateAgentState: (agent, state) =>
    set((prev) => ({
      agentStates: {
        ...prev.agentStates,
        [agent]: state,
      },
    })),

  updateBudget: (budget) => set({ budget }),

  updateFinalPlan: (plan) => set({ finalPlan: plan }),

  setConnectionStatus: (connected) => set({ isConnected: connected }),

  reset: () =>
    set({
      agentStates: {},
      budget: null,
      finalPlan: null,
    }),
}));
```

---

## Summary

### **Key Takeaways**

1. **Event-Driven Architecture**: All state changes flow through the event bus
2. **Standardized Schemas**: All events and agent I/O follow consistent patterns
3. **Real-Time Updates**: Frontend receives instant updates via WebSocket
4. **Type Safety**: Complete TypeScript definitions for all events and results
5. **Scalable Design**: Patterns translate directly to Kafka/Redis in production

### **Frontend Integration Steps**

1. Connect to WebSocket: `ws://localhost:9000/ws/orchestration/{party_id}`
2. Listen for events: `agent_started`, `agent_completed`, `budget_updated`, `plan_updated`
3. Update UI state based on events
4. Display agent progress, results, budget, and final plan
5. Handle errors and disconnections gracefully

---

**Document Status:** ✅ Complete
**Next Steps:** Implement event bus and agent system
**Questions?** Refer to this document as the single source of truth for all data schemas
