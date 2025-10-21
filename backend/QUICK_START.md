# 🎉 Quick Start - Festipin Backend E2E Testing

## TL;DR - Run Complete System Test

```bash
cd /Users/snama/s.space/Parx-Agentic-Verse/festipin/backend
source venv-3.12/bin/activate
python test_e2e_cli.py
```

## Available Commands

### 1️⃣ Run Default Demo (Jungle Theme)
```bash
python test_e2e_cli.py
```
Output: Complete party planning for 75-guest jungle theme party

### 2️⃣ Try Different Scenarios
```bash
python test_e2e_cli.py --scenario 1  # Jungle (75 guests)
python test_e2e_cli.py --scenario 2  # Princess (30 kids)
python test_e2e_cli.py --scenario 3  # Space (50 people)
```

### 3️⃣ Interactive Mode (Your Own Party!)
```bash
python test_e2e_cli.py --interactive
```
Then enter:
- Party theme and guests: `superhero party for 40 kids`
- Cake preferences: `red and blue cake with batman design`
- Venue: `indoor venue with games`

### 4️⃣ Run All Scenarios
```bash
python test_e2e_cli.py --all
```

### 5️⃣ Disable Real-time Monitoring (Cleaner Output)
```bash
python test_e2e_cli.py --no-realtime
```

## What You'll See

✅ **9 Steps of Complete Workflow:**

1. **Orchestrator Init** - 6 agents start
2. **Party Creation** - Unique party ID generated
3. **Agent Processing** - AI agents work in parallel
4. **Party Status** - All inputs displayed
5. **Agent Results** - Theme, venues, cakes detected
6. **Budget Calculation** - Cost breakdown with recommendations
7. **Final Plan** - Completion %, next steps, recommendations
8. **System Metrics** - Event bus performance stats
9. **Cleanup** - Graceful shutdown

## Example Output

```
THEME_AGENT Results:
  Status: COMPLETED
  Confidence: 80%
  Theme: jungle
  Colors: green, brown, yellow

VENUE_AGENT Results:
  Status: COMPLETED
  Confidence: 85%
  Venue Count: 3
  Top Venue: Sunshine Garden Park

CAKE_AGENT Results:
  Status: COMPLETED
  Confidence: 85%
  Bakery Count: 3
  Estimated Cost: $80 - $200

Total Budget: $2,080 - $2,200

Plan Completion: 100%
Next Steps:
  1. Specify food preferences and dietary requirements
  2. Add vendor needs (decorations, entertainment, photography)
  3. Review theme colors and decorations
  ...
```

## Performance

- **Startup:** ~500ms
- **Agent Execution:** ~1-2ms per agent
- **Total Workflow:** 3-5 seconds
- **Event Bus:** 30 events published, 76 delivered, 0 failed

## What's Being Tested

✅ Event-driven architecture
✅ 6 AI agents working in parallel
✅ Real-time event processing
✅ State management
✅ Budget calculations
✅ Plan generation
✅ Agent coordination
✅ Error handling
✅ Graceful shutdown

## Files Created

- `test_e2e_cli.py` - Main CLI test script
- `E2E_CLI_README.md` - Detailed documentation
- `QUICK_START.md` - This file

## Integration Tests (Optional)

Run pytest test suite:
```bash
source venv-3.12/bin/activate
python -m pytest tests/ -v --ignore=tests/test_storage_service.py
```

Result: 49 tests passed ✅

## Start API Server

To run the full API server with WebSocket support:
```bash
source venv-3.12/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

Then visit: http://localhost:9000/docs

## API Endpoints

Once server is running:
- `POST /api/v1/event-driven/party` - Create party
- `POST /api/v1/event-driven/party/{id}/input` - Add input
- `GET /api/v1/event-driven/party/{id}/status` - Get status
- `GET /api/v1/event-driven/system/status` - System metrics
- `WS /api/v1/event-driven/ws/{id}` - WebSocket real-time updates

---

**Done!** You now have a complete end-to-end testing system for the Festipin backend! 🎊
