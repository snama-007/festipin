# 🎉 Festipin Backend - End-to-End CLI Test

A comprehensive CLI tool for testing the complete party planning backend system with real-time agent execution monitoring.

## 📋 Overview

This tool demonstrates the full party planning workflow:
1. **Input Processing** - User provides party requirements (theme, guests, preferences)
2. **Agent Orchestration** - Multiple AI agents work in parallel
3. **Real-time Event Monitoring** - Watch agents execute in real-time
4. **Results Aggregation** - Theme, venues, cakes, budget, and final plan
5. **System Metrics** - Event bus and state store statistics

## 🚀 Quick Start

### Run Default Scenario (Jungle Theme)
```bash
python test_e2e_cli.py
```

### Run Specific Scenario
```bash
# Scenario 1: Jungle Theme Party (75 guests)
python test_e2e_cli.py --scenario 1

# Scenario 2: Princess Theme Party (30 kids)
python test_e2e_cli.py --scenario 2

# Scenario 3: Space Theme Party (50 people)
python test_e2e_cli.py --scenario 3
```

### Interactive Mode (Custom Party)
```bash
python test_e2e_cli.py --interactive
```

You'll be prompted to enter:
- Party theme and guest count
- Cake preferences
- Venue preferences

### Run All Scenarios
```bash
python test_e2e_cli.py --all
```

## 🎨 Features

### ✅ Real-Time Event Monitoring
Watch agents execute in real-time with colored output:
- 🟡 Agent Starting
- 🟢 Agent Completed (with execution time)
- 🔵 Plan Updated (with completion %)
- 💰 Budget Updated (with range)

### ✅ Comprehensive Output

**Step 1: Orchestrator Initialization**
- Starts 6 agents: InputAnalyzer, FinalPlanner, BudgetAgent, ThemeAgent, VenueAgent, CakeAgent
- Initializes WebSocket bridge
- Sets up event bus with 9 topics

**Step 2: Party Creation**
- Generates unique party ID
- Processes initial inputs
- Triggers InputAnalyzer

**Step 3: Agent Processing**
- InputAnalyzer classifies inputs
- Triggers appropriate agents based on keywords
- Agents execute in parallel

**Step 4: Party Status**
- Shows all inputs provided
- Lists tags for each input

**Step 5: Agent Results**
- **ThemeAgent**: Detected theme, colors, decorations
- **VenueAgent**: Recommended venues with capacity and price
- **CakeAgent**: Bakery options and estimated costs

**Step 6: Budget Calculation**
- Total budget range (min-max)
- Breakdown by category (venue, cake, catering, etc.)
- Cost-saving recommendations

**Step 7: Final Plan**
- Completion percentage
- Top recommendations by priority (Critical, High, Medium)
- Next steps (5 actionable items)
- Active and missing agents

**Step 8: System Metrics**
- Event bus: Published, delivered, failed events
- State store: Total parties, inputs, agent results

**Step 9: Cleanup**
- Graceful shutdown of all agents
- Event bus shutdown with final metrics

## 📊 Demo Scenarios

### Scenario 1: Jungle Theme Birthday Party 🦁
**Inputs:**
- "jungle theme party for 75 guests"
- "need a chocolate cake with animal decorations"
- "outdoor venue preferred, budget around $2000"

**Expected Results:**
- Theme: Jungle (green, brown, yellow colors)
- 3 venue options (outdoor parks prioritized)
- 3 bakery options with custom designs
- Budget: $2,000-$2,500
- 100% plan completion

### Scenario 2: Princess Theme Party 👑
**Inputs:**
- "princess castle theme party for 30 kids"
- "pink vanilla cake with crown topper"

**Expected Results:**
- Theme: Princess (pink, purple, gold colors)
- 3 bakery options for princess cakes
- Budget: $80-$200
- 50% plan completion (missing venue info)

### Scenario 3: Space Theme Party 🚀
**Inputs:**
- "space and astronaut theme party for 50 people"
- "galaxy-themed cake with planet decorations"

**Expected Results:**
- Theme: Space (blue, purple, silver colors)
- 3 venue options
- 3 bakery options for space cakes
- Budget calculated based on agents
- Plan with space-themed recommendations

## 🎯 Command-Line Options

```
usage: test_e2e_cli.py [-h] [--scenario {1,2,3}] [--interactive] [--all] [--no-realtime]

options:
  -h, --help            Show this help message
  --scenario {1,2,3}    Run specific demo scenario
  --interactive         Interactive mode - provide your own inputs
  --all                 Run all demo scenarios sequentially
  --no-realtime         Disable real-time event monitoring
```

## 🔧 Technical Details

### Agent Workflow

```
┌─────────────────┐
│   User Input    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ InputAnalyzer   │ ← Classifies inputs (theme, cake, venue, etc.)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Agent Trigger  │ ← Emits party.agent.should_execute events
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┐
    ▼         ▼        ▼        ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Theme  │ │ Venue  │ │  Cake  │  ... (Dynamic Agents)
│ Agent  │ │ Agent  │ │ Agent  │
└────┬───┘ └───┬────┘ └───┬────┘
     │         │          │
     └─────────┼──────────┘
               ▼
      ┌────────────────┐
      │  BudgetAgent   │ ← Recalculates on completion
      └────────┬───────┘
               ▼
      ┌────────────────┐
      │ FinalPlanner   │ ← Aggregates all results
      └────────────────┘
```

### Event Flow

1. **party.input.added** → InputAnalyzer processes
2. **party.agent.should_execute** → Triggers specific agents
3. **party.agent.started** → Agent begins execution
4. **party.agent.completed** → Agent finishes with results
5. **party.budget.updated** → BudgetAgent recalculates
6. **party.plan.updated** → FinalPlanner updates plan

### State Management

- **Party State Store**: In-memory store (Redis-ready for production)
- **Event Bus**: AsyncIO queue-based (Kafka-ready for production)
- **Agent Results**: Stored with confidence scores and metadata

## 📈 Performance Metrics

### Typical Execution Times

- **Orchestrator Startup**: ~500ms
- **Party Creation**: ~50ms
- **Agent Execution**: ~1-2ms per agent
- **Total Workflow**: ~3-5 seconds

### Event Bus Throughput

- **Events Published**: 12-30 per workflow
- **Events Delivered**: 21-76 per workflow (fan-out)
- **Failed Deliveries**: 0 (100% reliability)

## 🐛 Troubleshooting

### Issue: ModuleNotFoundError
```bash
# Make sure you're in the backend directory
cd /path/to/festipin/backend

# Activate virtual environment
source venv-3.12/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Issue: Port Already in Use
The system doesn't bind to ports in CLI mode, so this shouldn't happen. If you see WebSocket warnings, they're normal (no actual WebSocket clients in CLI mode).

### Issue: Agents Not Executing
Check logs for errors. Common causes:
- Missing dependencies (run `pip install -r requirements.txt`)
- Database connection issues (not applicable for CLI - uses mock data)
- Python version (requires 3.10+)

## 🧪 Testing with Different Inputs

### Test Theme Detection
```python
# Jungle themes
"safari adventure party"
"wild animal party"
"tropical jungle theme"

# Princess themes
"royal princess party"
"castle birthday party"
"fairy tale princess theme"

# Space themes
"astronaut party"
"galaxy space party"
"rocket ship theme"
```

### Test Guest Count Extraction
```
"party for 50 people"
"inviting 75 guests"
"30 kids attending"
```

### Test Budget Parsing
```
"budget around $2000"
"spending up to $1500"
"$500 maximum budget"
```

## 📚 Integration with Full Backend

This CLI test uses the **same codebase** as the full backend API. You can:

1. **Run API Server:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Use WebSocket Client:**
   ```javascript
   const ws = new WebSocket('ws://localhost:9000/api/v1/event-driven/ws/PARTY_ID');
   ws.onmessage = (event) => console.log(JSON.parse(event.data));
   ```

3. **Call REST API:**
   ```bash
   # Create party
   curl -X POST http://localhost:9000/api/v1/event-driven/party \
     -H "Content-Type: application/json" \
     -d '{"initial_inputs": [{"content": "jungle theme party", "tags": ["theme"]}]}'

   # Add input
   curl -X POST http://localhost:9000/api/v1/event-driven/party/PARTY_ID/input \
     -H "Content-Type: application/json" \
     -d '{"content": "chocolate cake", "tags": ["cake"]}'

   # Get status
   curl http://localhost:9000/api/v1/event-driven/party/PARTY_ID/status
   ```

## 🎓 Learning Resources

- **Architecture**: See `PRODUCTION_ARCHITECTURE.md`
- **Event Schemas**: See `EVENT_SCHEMAS_AND_FRONTEND_INTEGRATION.md`
- **Implementation Status**: See `IMPLEMENTATION_STATUS.md`
- **API Documentation**: Visit `http://localhost:9000/docs` when API is running

## 📝 Output Legend

### Colors
- 🟢 **Green**: Success, completed actions
- 🔵 **Blue**: Info, general messages
- 🟡 **Yellow**: Warnings, in-progress actions
- 🔴 **Red**: Errors, critical issues
- 🟣 **Purple**: Headers, section titles

### Symbols
- ✓ Success
- ⟳ Loading/Processing
- • Bullet point
- ▶ Section header
- 💰 Budget
- 📋 Plan

## 🚀 Next Steps

1. **Try Interactive Mode**: Create your own custom party
2. **Modify Scenarios**: Edit `demo_scenario_X()` functions
3. **Add New Agents**: Implement catering_agent, vendor_agent
4. **Integrate Vision**: Add image processing for Pinterest refs
5. **Deploy to Production**: Switch to Redis + Kafka

---

**Built with:** Python 3.12, FastAPI, AsyncIO, Pydantic

**License:** MIT

**Support:** Open an issue on GitHub
