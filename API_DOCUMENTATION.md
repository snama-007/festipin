"""
API Documentation for Agent Orchestration System

This document provides comprehensive documentation for all API endpoints
in the agent orchestration system.
"""

# Agent Orchestration API Documentation

## Base URL
```
http://localhost:9000/api/v1
```

## Authentication
Currently no authentication required. Future versions will support JWT tokens.

## Content Type
All requests and responses use `application/json` unless specified otherwise.

---

## Endpoints

### 1. Health Check

#### GET `/health`
Check if the API is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0"
}
```

#### GET `/api/v1/orchestration/health`
Check orchestration system health.

**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "orchestrator": "available",
  "memory_store": "available",
  "active_events": 0,
  "timestamp": "2025-01-07T00:00:00Z"
}
```

---

### 2. Orchestration Management

#### POST `/api/v1/orchestration/start`
Start a new agent orchestration workflow.

**Request Body:**
```json
{
  "inputs": [
    {
      "source_type": "text|image|url",
      "content": "string",
      "tags": ["string"],
      "metadata": {
        "key": "value"
      }
    }
  ],
  "metadata": {
    "event_type": "party",
    "source": "url",
    "timestamp": "2025-01-07T00:00:00Z"
  }
}
```

**Response:**
```json
{
  "success": true,
  "event_id": "evt_abc123",
  "message": "Orchestration started with event ID: evt_abc123"
}
```

**Example:**
```bash
curl -X POST http://localhost:9000/api/v1/orchestration/start \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "source_type": "text",
        "content": "jungle themed birthday party for 5 year old",
        "tags": ["jungle", "birthday", "kids"],
        "metadata": {"age": 5, "theme": "jungle"}
      }
    ],
    "metadata": {
      "event_type": "party",
      "source": "text"
    }
  }'
```

#### GET `/api/v1/orchestration/status/{event_id}`
Get current status of an orchestration workflow.

**Path Parameters:**
- `event_id` (string): The event ID returned from start endpoint

**Response:**
```json
{
  "success": true,
  "event_id": "evt_abc123",
  "workflow_status": "running|completed|error",
  "agent_results": {
    "input_classifier": {
      "status": "completed",
      "result": {
        "classified_inputs": {
          "theme": [...],
          "cake": [...]
        }
      },
      "execution_time": 0.5
    },
    "theme_agent": {
      "status": "running",
      "result": null,
      "execution_time": null
    }
  },
  "final_plan": {
    "event_summary": {
      "theme": "jungle",
      "total_budget": {"min": 500, "max": 1200}
    },
    "recommendations": ["Focus on jungle theme decorations"],
    "next_steps": ["Review and approve the generated plan"]
  },
  "created_at": "2025-01-07T00:00:00Z",
  "updated_at": "2025-01-07T00:01:30Z"
}
```

**Example:**
```bash
curl http://localhost:9000/api/v1/orchestration/status/evt_abc123
```

#### POST `/api/v1/orchestration/feedback/{event_id}`
Add user feedback to a workflow.

**Path Parameters:**
- `event_id` (string): The event ID

**Request Body:**
```json
{
  "feedback": {
    "rating": 5,
    "comment": "Great results!",
    "improvements": ["More vendor suggestions"],
    "user_id": "user123"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Feedback added successfully"
}
```

**Example:**
```bash
curl -X POST http://localhost:9000/api/v1/orchestration/feedback/evt_abc123 \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": {
      "rating": 5,
      "comment": "Excellent party plan!",
      "improvements": ["More budget options"]
    }
  }'
```

---

### 3. Event Management

#### GET `/api/v1/orchestration/events`
List all active events.

**Response:**
```json
{
  "success": true,
  "events": [
    {
      "event_id": "evt_abc123",
      "workflow_status": "completed",
      "input_count": 1,
      "completed_agents": 8,
      "total_agents": 8,
      "has_final_plan": true,
      "created_at": "2025-01-07T00:00:00Z",
      "updated_at": "2025-01-07T00:01:30Z"
    }
  ],
  "count": 1
}
```

#### GET `/api/v1/orchestration/stats`
Get memory store statistics.

**Response:**
```json
{
  "success": true,
  "stats": {
    "active_events": 5,
    "backups": 2,
    "total_size_bytes": 1024000,
    "total_size_mb": 1.02,
    "base_path": "memory_store",
    "max_age_days": 7
  }
}
```

#### POST `/api/v1/orchestration/backup/{event_id}`
Create backup of event data.

**Path Parameters:**
- `event_id` (string): The event ID to backup

**Response:**
```json
{
  "success": true,
  "backup_path": "memory_store/backups/evt_abc123_20250107_000000.json",
  "message": "Backup created for event evt_abc123"
}
```

#### DELETE `/api/v1/orchestration/event/{event_id}`
Delete event data.

**Path Parameters:**
- `event_id` (string): The event ID to delete

**Response:**
```json
{
  "success": true,
  "message": "Event evt_abc123 deleted successfully"
}
```

---

## Data Models

### OrchestrationInput
```json
{
  "source_type": "text|image|url",
  "content": "string",
  "tags": ["string"],
  "metadata": {
    "key": "value"
  }
}
```

### AgentStatus
```json
{
  "agent_name": "string",
  "status": "pending|running|completed|error",
  "progress": 0.0,
  "result": {},
  "error": "string",
  "execution_time": 0.0
}
```

### WorkflowStatus
```json
{
  "event_id": "string",
  "workflow_status": "initializing|running|completed|error",
  "agent_results": {
    "agent_name": AgentStatus
  },
  "final_plan": {},
  "created_at": "string",
  "updated_at": "string"
}
```

---

## Agent Types

The system includes the following agents:

1. **input_classifier** - Analyzes and routes inputs to appropriate agents
2. **theme_agent** - Detects and defines party themes
3. **cake_agent** - Plans cake details and decorations
4. **venue_agent** - Suggests venues and layouts
5. **catering_agent** - Plans food and menu options
6. **budget_agent** - Estimates costs and budget breakdown
7. **vendor_agent** - Matches with real vendors
8. **planner_agent** - Assembles final comprehensive plan

---

## Error Handling

### Error Response Format
```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-01-07T00:00:00Z"
}
```

### Common Error Codes
- `VALIDATION_ERROR` - Invalid request data
- `AGENT_ERROR` - Agent execution failed
- `STORAGE_ERROR` - Memory store operation failed
- `NOT_FOUND` - Event or resource not found
- `TIMEOUT` - Operation timed out

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (validation error)
- `404` - Not Found
- `500` - Internal Server Error

---

## Rate Limiting

Currently no rate limiting implemented. Future versions will include:
- 100 requests per minute per IP
- 10 concurrent orchestrations per user

---

## WebSocket Support (Future)

Real-time updates will be available via WebSocket:
```
ws://localhost:9000/ws/orchestration/{event_id}
```

Events:
- `agent_started` - Agent begins execution
- `agent_completed` - Agent finishes successfully
- `agent_failed` - Agent encounters error
- `workflow_completed` - Entire workflow finished

---

## Examples

### Complete Workflow Example

1. **Start Orchestration:**
```bash
curl -X POST http://localhost:9000/api/v1/orchestration/start \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [
      {
        "source_type": "text",
        "content": "princess themed tea party for 7 year old",
        "tags": ["princess", "tea", "party", "girls"],
        "metadata": {"age": 7, "theme": "princess"}
      }
    ]
  }'
```

2. **Monitor Progress:**
```bash
# Poll every 2 seconds until completed
while true; do
  curl http://localhost:9000/api/v1/orchestration/status/evt_abc123
  sleep 2
done
```

3. **Add Feedback:**
```bash
curl -X POST http://localhost:9000/api/v1/orchestration/feedback/evt_abc123 \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": {
      "rating": 5,
      "comment": "Perfect princess party plan!"
    }
  }'
```

---

## Testing

### Health Check
```bash
curl http://localhost:9000/health
```

### System Stats
```bash
curl http://localhost:9000/api/v1/orchestration/stats
```

### Run Demo
```bash
cd backend
python3 demo_orchestration.py
```

---

## Support

For issues or questions:
1. Check the logs: `tail -f backend.log`
2. Run health checks: `curl http://localhost:9000/health`
3. Check system stats: `curl http://localhost:9000/api/v1/orchestration/stats`
4. Review error handling documentation
