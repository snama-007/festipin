"""
Quick Start Guide for Agent Orchestration System

This guide helps you get the agent orchestration system running quickly.
"""

# Quick Start Commands

## 1. Install Dependencies

### Backend
```bash
cd festipin/backend
pip install -r requirements.txt
```

### Frontend
```bash
cd festipin/frontend
npm install
```

## 2. Start Backend Server

```bash
cd festipin/backend
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

## 3. Start Frontend Server

```bash
cd festipin/frontend
npm run dev
```

## 4. Test the System

### Run E2E Test
```bash
cd festipin/backend
python test_orchestration_e2e.py
```

### Manual Testing
1. Open http://localhost:3000
2. Enter a Pinterest URL or upload an image
3. Click "Start Agent Orchestration"
4. Watch the agents work in real-time!

## 5. API Endpoints

### Start Orchestration
```bash
curl -X POST http://localhost:9000/api/v1/orchestration/start \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "source_type": "text",
        "content": "jungle themed birthday party",
        "tags": ["jungle", "birthday", "kids"]
      }
    ]
  }'
```

### Check Status
```bash
curl http://localhost:9000/api/v1/orchestration/status/{event_id}
```

### Health Check
```bash
curl http://localhost:9000/api/v1/orchestration/health
```

## 6. File Structure

```
festipin/
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── local_memory_store.py      # Local JSON storage
│   │   │   ├── agent_registry.py          # Agent management
│   │   │   └── langgraph_orchestrator.py  # Workflow orchestration
│   │   └── api/routes/
│   │       └── orchestration.py           # API endpoints
│   └── test_orchestration_e2e.py         # E2E tests
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── AgentOrchestration.tsx    # React components
│   │   ├── services/
│   │   │   └── api.ts                    # API client
│   │   └── app/
│   │       └── page.tsx                  # Main page
└── FIREBASE_MIGRATION_STRATEGY.md        # Migration guide
```

## 7. Agent Types

- **🔍 Input Classifier**: Analyzes and routes inputs
- **🎨 Theme Agent**: Detects party themes
- **🍰 Cake Agent**: Plans cake details
- **🏠 Venue Agent**: Suggests venues
- **🍽️ Catering Agent**: Plans food
- **💰 Budget Agent**: Estimates costs
- **📞 Vendor Agent**: Matches vendors
- **📋 Planner Agent**: Assembles final plan

## 8. Memory Storage

### Local JSON (Current)
- Files stored in `memory_store/` directory
- Automatic cleanup after 7 days
- Thread-safe operations
- Easy to debug and test

### Firebase (Future)
- Cloud-based storage
- Real-time updates
- Scalable architecture
- See `FIREBASE_MIGRATION_STRATEGY.md`

## 9. Troubleshooting

### Backend Issues
```bash
# Check logs
tail -f backend.log

# Restart server
pkill -f uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

### Frontend Issues
```bash
# Clear cache
rm -rf .next
npm run dev

# Check console for errors
```

### Memory Store Issues
```bash
# Check memory stats
curl http://localhost:9000/api/v1/orchestration/stats

# Clear old events
rm -rf memory_store/events/*.json
```

## 10. Development Tips

### Adding New Agents
1. Create agent class in `agent_registry.py`
2. Register in `AgentRegistry`
3. Add to workflow in `langgraph_orchestrator.py`
4. Update frontend display names

### Debugging
- Check `memory_store/` for event data
- Use API endpoints to inspect state
- Run E2E tests for validation

### Performance
- Agents run in parallel when possible
- Local storage is fast for development
- Consider Firebase for production scale

## 11. Next Steps

1. **Test the system** with different inputs
2. **Add more agents** for specific use cases
3. **Migrate to Firebase** when ready for scale
4. **Add real-time updates** with WebSockets
5. **Implement user authentication** for multi-user support

## 12. Support

- Check logs for error details
- Run E2E tests to validate functionality
- Review `FIREBASE_MIGRATION_STRATEGY.md` for scaling
- Use API documentation at `/docs` endpoint

Happy coding! 🚀
