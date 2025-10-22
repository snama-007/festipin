# 🎨 Frontend Integration Guide - Festipin Backend

**Last Updated:** October 22, 2025
**Backend Version:** 1.0.0
**Frontend Port:** 9010 (configured in CORS)

---

## ✅ Backend Status

**Status:** ✅ **READY FOR FRONTEND INTEGRATION**

- ✅ Server starts successfully
- ✅ CORS configured for `http://localhost:9010`
- ✅ Event-driven architecture initialized
- ✅ WebSocket support enabled
- ✅ All API endpoints tested
- ✅ 80+ tests passing

---

## 🚀 Quick Start

### 1. Start Backend Server

```bash
cd backend
source venv-3.12/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

Server will be available at: **http://localhost:9000**

### 2. Verify Backend Health

```bash
curl http://localhost:9000/health
# Response: {"status":"healthy","environment":"development","version":"1.0.0"}
```

### 3. Access API Documentation

- **Swagger UI:** http://localhost:9000/docs
- **ReDoc:** http://localhost:9000/redoc

---

## 🔌 API Endpoints

### Core Endpoints

#### 1. **Hybrid Input Processing** (Recommended)
```http
POST /api/v1/input/process-hybrid
Content-Type: application/json

{
  "text": "Birthday party for 50 guests, unicorn theme, outdoor venue",
  "image_url": "https://example.com/image.jpg"  // Optional
}
```

**Response:**
```json
{
  "extracted_data": {
    "eventType": "Birthday",
    "theme": "Unicorn",
    "guestCount": 50,
    "location": { "type": "Outdoor" }
  },
  "routing": {
    "complexity": "simple",
    "processor": "regex"
  },
  "confidence": {
    "overall_score": 85.5
  }
}
```

#### 2. **Event-Driven Party Planning** (New!)
```http
POST /api/v1/event-driven/party
Content-Type: application/json

{
  "party_id": "unique-party-id",
  "initial_inputs": [
    { "type": "text", "content": "Birthday party for 30 kids" },
    { "type": "text", "content": "Superhero theme" }
  ]
}
```

**Features:**
- ✅ Real-time agent execution via WebSocket
- ✅ Progressive party planning
- ✅ Add inputs anytime
- ✅ Remove inputs to trigger re-planning
- ✅ Automatic agent orchestration

#### 3. **Vision Processing**
```http
POST /api/v1/vision/analyze
Content-Type: multipart/form-data

image: [file upload]
```

**Response:**
```json
{
  "description": "Birthday party setup with unicorn decorations",
  "detected_objects": [
    { "type": "balloon", "color": "rainbow" },
    { "type": "cake", "theme": "unicorn" }
  ],
  "theme_suggestions": ["Unicorn", "Rainbow", "Fantasy"]
}
```

#### 4. **Plan Generation**
```http
POST /api/v1/plan/generate
Content-Type: application/json

{
  "event_type": "birthday",
  "theme": "unicorn",
  "guest_count": 30,
  "budget": 500
}
```

---

## 🔄 WebSocket Integration (Real-Time Updates)

### Connect to WebSocket

```javascript
const ws = new WebSocket('ws://localhost:9000/ws/party/YOUR_PARTY_ID');

ws.onopen = () => {
  console.log('Connected to party planning stream');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data);

  // Handle different event types
  switch(data.event_type) {
    case 'agent.started':
      console.log(`Agent ${data.agent_id} started`);
      break;
    case 'agent.completed':
      console.log(`Agent ${data.agent_id} completed with data:`, data.data);
      break;
    case 'budget.updated':
      console.log('Budget updated:', data.budget_data);
      break;
    case 'plan.updated':
      console.log('Plan updated:', data.plan_data);
      break;
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket closed');
};
```

### WebSocket Events You'll Receive

| Event Type | Description | Data |
|------------|-------------|------|
| `agent.started` | Agent begins execution | `agent_id`, `timestamp` |
| `agent.completed` | Agent finishes with data | `agent_id`, `data`, `timestamp` |
| `agent.failed` | Agent encountered error | `agent_id`, `error`, `timestamp` |
| `budget.updated` | Budget calculation complete | `budget_data`, `breakdown` |
| `plan.updated` | Full plan regenerated | `plan_data` |

---

## 📡 Event-Driven API Endpoints

### Party Management

```http
# Create/Initialize Party
POST /api/v1/event-driven/party
{
  "party_id": "party-123",
  "initial_inputs": [...]
}

# Get Party State
GET /api/v1/event-driven/party/{party_id}

# Get All Agent Data
GET /api/v1/event-driven/party/{party_id}/agents

# Get Specific Agent Data
GET /api/v1/event-driven/party/{party_id}/agents/{agent_id}

# Clear Party State
DELETE /api/v1/event-driven/party/{party_id}
```

### Input Management (Dynamic Planning)

```http
# Add Input (triggers re-analysis)
POST /api/v1/event-driven/party/{party_id}/input
{
  "type": "text",
  "content": "Budget is $500"
}

# Remove Input (triggers re-planning)
DELETE /api/v1/event-driven/party/{party_id}/input/{input_id}

# List All Inputs
GET /api/v1/event-driven/party/{party_id}/inputs
```

---

## 🎯 Frontend Integration Patterns

### Pattern 1: Simple Form Submission

```javascript
async function submitPartyDetails(formData) {
  const response = await fetch('http://localhost:9000/api/v1/input/process-hybrid', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: formData.description,
      image_url: formData.imageUrl
    })
  });

  const result = await response.json();
  return result;
}
```

### Pattern 2: Real-Time Event-Driven Planning

```javascript
class PartyPlanningSession {
  constructor(partyId) {
    this.partyId = partyId;
    this.ws = null;
    this.baseUrl = 'http://localhost:9000/api/v1/event-driven';
  }

  async initialize(initialInputs) {
    // Create party session
    await fetch(`${this.baseUrl}/party`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        party_id: this.partyId,
        initial_inputs: initialInputs
      })
    });

    // Connect WebSocket for real-time updates
    this.connectWebSocket();
  }

  connectWebSocket() {
    this.ws = new WebSocket(`ws://localhost:9000/ws/party/${this.partyId}`);

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleEvent(data);
    };
  }

  async addInput(type, content) {
    const response = await fetch(`${this.baseUrl}/party/${this.partyId}/input`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type, content })
    });
    return response.json();
  }

  async removeInput(inputId) {
    await fetch(`${this.baseUrl}/party/${this.partyId}/input/${inputId}`, {
      method: 'DELETE'
    });
  }

  async getAgentData(agentId) {
    const response = await fetch(
      `${this.baseUrl}/party/${this.partyId}/agents/${agentId}`
    );
    return response.json();
  }

  handleEvent(event) {
    // Update UI based on event type
    console.log('Event received:', event);
  }
}

// Usage
const session = new PartyPlanningSession('party-123');
await session.initialize([
  { type: 'text', content: 'Birthday party for 30 kids' }
]);

// Later, add more inputs dynamically
await session.addInput('text', 'Budget is $500');
await session.addInput('text', 'Superhero theme');
```

### Pattern 3: Image Upload with Vision

```javascript
async function uploadAndAnalyzeImage(file) {
  const formData = new FormData();
  formData.append('image', file);

  const response = await fetch('http://localhost:9000/api/v1/vision/analyze', {
    method: 'POST',
    body: formData
  });

  return response.json();
}
```

---

## 🔐 CORS Configuration

**Allowed Origins:** `http://localhost:9010`

If your frontend runs on a different port, update `.env`:

```bash
API_CORS_ORIGINS=http://localhost:9010,http://localhost:3000
```

Then restart the backend.

---

## 📦 Data Models

### Input Object
```typescript
interface Input {
  type: 'text' | 'image' | 'url';
  content: string;
  metadata?: {
    timestamp?: string;
    source?: string;
  };
}
```

### Extracted Party Data
```typescript
interface PartyData {
  eventType?: string;
  theme?: string;
  honoreeName?: string;
  honoreeAge?: number;
  guestCount?: {
    adults?: number;
    kids?: number;
  };
  budget?: {
    min?: number;
    max?: number;
  };
  date?: string;
  time?: string;
  duration?: string;
  location?: {
    type?: string;
    name?: string;
    address?: string;
  };
  foodPreferences?: string[];
  activities?: string[];
}
```

### Agent Event
```typescript
interface AgentEvent {
  event_type: 'agent.started' | 'agent.completed' | 'agent.failed';
  agent_id: string;
  party_id: string;
  timestamp: string;
  data?: any;
  error?: string;
}
```

---

## 🎨 Example React Integration

```jsx
import React, { useState, useEffect } from 'react';

function PartyPlanner() {
  const [partyId] = useState(() => `party-${Date.now()}`);
  const [inputs, setInputs] = useState([]);
  const [agentData, setAgentData] = useState({});
  const [ws, setWs] = useState(null);

  useEffect(() => {
    // Initialize party
    fetch('http://localhost:9000/api/v1/event-driven/party', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        party_id: partyId,
        initial_inputs: []
      })
    });

    // Connect WebSocket
    const websocket = new WebSocket(`ws://localhost:9000/ws/party/${partyId}`);

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.event_type === 'agent.completed') {
        setAgentData(prev => ({
          ...prev,
          [data.agent_id]: data.data
        }));
      }
    };

    setWs(websocket);

    return () => websocket.close();
  }, [partyId]);

  const addInput = async (text) => {
    await fetch(`http://localhost:9000/api/v1/event-driven/party/${partyId}/input`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type: 'text',
        content: text
      })
    });
  };

  return (
    <div>
      <h1>Party Planner</h1>

      {/* Input form */}
      <input
        type="text"
        placeholder="Describe your party..."
        onKeyPress={(e) => {
          if (e.key === 'Enter') {
            addInput(e.target.value);
            e.target.value = '';
          }
        }}
      />

      {/* Display agent results */}
      <div>
        <h2>Budget:</h2>
        <pre>{JSON.stringify(agentData.budget_agent, null, 2)}</pre>

        <h2>Theme:</h2>
        <pre>{JSON.stringify(agentData.theme_agent, null, 2)}</pre>

        <h2>Venue:</h2>
        <pre>{JSON.stringify(agentData.venue_agent, null, 2)}</pre>
      </div>
    </div>
  );
}
```

---

## 🧪 Testing with curl

```bash
# Test hybrid input
curl -X POST http://localhost:9000/api/v1/input/process-hybrid \
  -H "Content-Type: application/json" \
  -d '{"text": "Birthday party for 30 kids, superhero theme"}'

# Create event-driven party
curl -X POST http://localhost:9000/api/v1/event-driven/party \
  -H "Content-Type: application/json" \
  -d '{
    "party_id": "test-123",
    "initial_inputs": [
      {"type": "text", "content": "Birthday party for 30 kids"}
    ]
  }'

# Add input
curl -X POST http://localhost:9000/api/v1/event-driven/party/test-123/input \
  -H "Content-Type: application/json" \
  -d '{"type": "text", "content": "Budget is $500"}'

# Get party state
curl http://localhost:9000/api/v1/event-driven/party/test-123

# Get agent data
curl http://localhost:9000/api/v1/event-driven/party/test-123/agents/budget_agent
```

---

## 📊 Available Agents

When using event-driven endpoints, these agents run automatically:

| Agent ID | Purpose | Triggers On |
|----------|---------|-------------|
| `input_analyzer` | Classifies inputs | Any input added |
| `theme_agent` | Theme suggestions | Theme keywords detected |
| `venue_agent` | Venue recommendations | Location/venue keywords |
| `budget_agent` | Budget calculation | Budget/guest count detected |
| `cake_agent` | Cake suggestions | Cake keywords detected |
| `final_planner` | Complete plan | All required data present |

---

## 🚨 Error Handling

All endpoints return standard error responses:

```json
{
  "error": "Error type",
  "detail": "Detailed error message",
  "status_code": 400
}
```

Common status codes:
- `200` - Success
- `400` - Bad request (invalid input)
- `404` - Resource not found
- `500` - Internal server error

---

## 🔥 Hot Reload

Backend has hot reload enabled in development mode. Changes to code will automatically restart the server.

---

## 📝 Next Steps

1. **Start Backend:** `uvicorn app.main:app --reload`
2. **Test Endpoints:** Use Swagger UI at http://localhost:9000/docs
3. **Build Frontend:** Connect to API endpoints
4. **Use WebSockets:** For real-time updates
5. **Test Event-Driven:** Try the progressive planning flow

---

## 🆘 Support

- **API Docs:** http://localhost:9000/docs
- **Health Check:** http://localhost:9000/health
- **Backend Tests:** `pytest tests/ -v`

**Status:** ✅ **READY FOR FRONTEND INTEGRATION**
