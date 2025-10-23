# 📋 Party-Specific Logging Guide

**Feature:** Each party session gets its own dedicated log file

---

## 🎯 Overview

Every party planning session (starting with `fp-`) now has its own dedicated log file that tracks:
- Party creation
- Input processing decisions (regex vs LLM)
- Complexity assessments
- Agent executions
- All events specific to that party

**Log Files Location:** `logs/party_fp-{id}.log`

---

## 🔧 How It Works

### Automatic Context Tracking

When you create a party or add input, the system **automatically**:
1. Sets the active party context
2. Routes all logs to that party's file
3. Includes party_id in every log entry

### Party ID Format

All party IDs are automatically prefixed with `fp-`:
- Input: `"test-party"` → Stored as: `"fp-test-party"`
- Input: `"fp-2025A12345"` → Stored as: `"fp-2025A12345"` (no change)

---

## 📁 Log File Structure

### File Naming
```
logs/
├── party_fp-test-party.log
├── party_fp-2025A12345.log
└── party_fp-xyz789.log
```

### Log Entry Format

Each line is a JSON object:
```json
{
  "timestamp": "2025-10-22T22:33:43.812368+00:00",
  "level": "INFO",
  "party_id": "fp-2025A12345",
  "message": "Input complexity assessed",
  "complexity_level": "simple",
  "use_llm": false,
  "reasons": ["explicit_theme", "concise_input"],
  "input_preview": "Birthday party for 30 kids, superhero theme"
}
```

---

## 📊 What Gets Logged?

### 1. Party Creation
```json
{
  "timestamp": "2025-10-22T22:33:43.812368+00:00",
  "level": "INFO",
  "party_id": "fp-2025A12345",
  "message": "Party session created",
  "user_id": "user123",
  "initial_inputs_count": 1
}
```

### 2. Input Complexity Assessment
```json
{
  "timestamp": "2025-10-22T22:33:45.123456+00:00",
  "level": "INFO",
  "party_id": "fp-2025A12345",
  "message": "Input complexity assessed",
  "complexity_level": "simple",
  "use_llm": false,
  "reasons": ["explicit_theme", "explicit_event_type", "concise_input"],
  "has_vision": false,
  "input_preview": "Birthday party for 30 kids, superhero theme"
}
```

### 3. Processing Route Decision
```json
// REGEX Route
{
  "timestamp": "2025-10-22T22:33:45.234567+00:00",
  "level": "INFO",
  "party_id": "fp-2025A12345",
  "message": "Processing with regex extraction",
  "vision_confidence": null
}

// LLM Route
{
  "timestamp": "2025-10-22T22:33:45.345678+00:00",
  "level": "INFO",
  "party_id": "fp-2025A12345",
  "message": "Processing with LLM planner",
  "vision_confidence": null
}
```

### 4. LLM Plan Generated (if complex input)
```json
{
  "timestamp": "2025-10-22T22:33:48.456789+00:00",
  "level": "INFO",
  "party_id": "fp-2025A12345",
  "message": "LLM plan generated",
  "event_type": "Birthday",
  "theme": "Garden Tea Party",
  "confidence": 85.0,
  "agents_count": 4
}
```

---

## 🔌 API Endpoints

### Get Party Logs

```http
GET /api/v1/event-driven/party/{party_id}/logs
```

**Example Request:**
```bash
curl http://localhost:9000/api/v1/event-driven/party/fp-2025A12345/logs
```

**Response:**
```json
{
  "success": true,
  "party_id": "fp-2025A12345",
  "log_file": "logs/party_fp-2025A12345.log",
  "total_logs": 45,
  "logs": [
    {
      "timestamp": "2025-10-22T22:33:43.812368+00:00",
      "level": "INFO",
      "party_id": "fp-2025A12345",
      "message": "Party session created",
      "user_id": "user123",
      "initial_inputs_count": 1
    },
    {
      "timestamp": "2025-10-22T22:33:45.123456+00:00",
      "level": "INFO",
      "party_id": "fp-2025A12345",
      "message": "Input complexity assessed",
      "complexity_level": "simple",
      "use_llm": false
    },
    ...
  ]
}
```

### Clear Party Logs

```http
DELETE /api/v1/event-driven/party/{party_id}/logs
```

**Example Request:**
```bash
curl -X DELETE http://localhost:9000/api/v1/event-driven/party/fp-2025A12345/logs
```

**Response:**
```json
{
  "success": true,
  "message": "Logs cleared for party fp-2025A12345"
}
```

---

## 💻 Frontend Integration

### Fetch Party Logs

```javascript
async function getPartyLogs(partyId) {
  const response = await fetch(
    `http://localhost:9000/api/v1/event-driven/party/${partyId}/logs`
  );
  const data = await response.json();

  console.log(`Total logs: ${data.total_logs}`);
  console.log('Logs:', data.logs);

  return data.logs;
}

// Usage
const logs = await getPartyLogs('fp-2025A12345');
```

### Display Logs in UI

```javascript
function displayLogs(logs) {
  const logContainer = document.getElementById('party-logs');

  logs.forEach(log => {
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry log-${log.level.toLowerCase()}`;

    const time = new Date(log.timestamp).toLocaleTimeString();

    logEntry.innerHTML = `
      <span class="time">[${time}]</span>
      <span class="level">${log.level}</span>
      <span class="message">${log.message}</span>
      ${log.complexity_level ? `<span class="badge">${log.complexity_level}</span>` : ''}
      ${log.use_llm !== undefined ? `<span class="badge">${log.use_llm ? 'LLM' : 'REGEX'}</span>` : ''}
    `;

    logContainer.appendChild(logEntry);
  });
}
```

### React Component Example

```jsx
import React, { useState, useEffect } from 'react';

function PartyLogs({ partyId }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchLogs() {
      try {
        const response = await fetch(
          `http://localhost:9000/api/v1/event-driven/party/${partyId}/logs`
        );
        const data = await response.json();
        setLogs(data.logs);
      } catch (error) {
        console.error('Failed to fetch logs:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchLogs();

    // Refresh logs every 5 seconds
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, [partyId]);

  if (loading) return <div>Loading logs...</div>;

  return (
    <div className="party-logs">
      <h3>Party Logs ({logs.length})</h3>
      <div className="log-entries">
        {logs.map((log, idx) => (
          <div key={idx} className={`log-entry log-${log.level.toLowerCase()}`}>
            <span className="time">
              {new Date(log.timestamp).toLocaleTimeString()}
            </span>
            <span className="level">{log.level}</span>
            <span className="message">{log.message}</span>

            {/* Show routing decision */}
            {log.use_llm !== undefined && (
              <span className={`badge ${log.use_llm ? 'llm' : 'regex'}`}>
                {log.use_llm ? 'LLM' : 'REGEX'}
              </span>
            )}

            {/* Show complexity level */}
            {log.complexity_level && (
              <span className={`badge complexity-${log.complexity_level}`}>
                {log.complexity_level}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 🎨 CSS Styling Example

```css
.party-logs {
  max-height: 500px;
  overflow-y: auto;
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
}

.log-entry {
  padding: 8px 12px;
  margin: 5px 0;
  border-left: 3px solid #ccc;
  background: white;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.log-entry.log-info {
  border-left-color: #2196F3;
}

.log-entry.log-warning {
  border-left-color: #FF9800;
  background: #FFF3E0;
}

.log-entry.log-error {
  border-left-color: #F44336;
  background: #FFEBEE;
}

.time {
  color: #666;
  font-size: 0.9em;
  min-width: 80px;
}

.level {
  font-weight: bold;
  text-transform: uppercase;
  font-size: 0.8em;
  min-width: 50px;
}

.badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  font-weight: bold;
}

.badge.llm {
  background: #FF9800;
  color: white;
}

.badge.regex {
  background: #4CAF50;
  color: white;
}

.badge.complexity-simple {
  background: #4CAF50;
  color: white;
}

.badge.complexity-medium {
  background: #FF9800;
  color: white;
}

.badge.complexity-complex {
  background: #F44336;
  color: white;
}
```

---

## 📂 Programmatic Usage

### Using PartyLogger Directly

```python
from app.core.party_logger import (
    get_party_logger,
    set_active_party,
    log_party_event
)

# Set active party
set_active_party("fp-2025A12345")

# Log an event
log_party_event(
    "Custom event happened",
    event_type="custom",
    data={"foo": "bar"}
)

# Get party logger instance
logger = get_party_logger()

# Read logs
logs = logger.get_party_logs("fp-2025A12345")
print(f"Total logs: {len(logs)}")

# Clear logs
logger.clear_party_logs("fp-2025A12345")
```

---

## 📊 Complete Example Flow

### 1. Create Party
```http
POST /api/v1/event-driven/party
{
  "party_id": "test-party",
  "initial_inputs": []
}
```

**Log Created:**
```
logs/party_fp-test-party.log
```

**First Log Entry:**
```json
{
  "timestamp": "2025-10-22T22:33:43.812368+00:00",
  "level": "INFO",
  "party_id": "fp-test-party",
  "message": "Party session created",
  "user_id": null,
  "initial_inputs_count": 0
}
```

### 2. Add Input
```http
POST /api/v1/event-driven/party/fp-test-party/input
{
  "content": "Birthday party for 30 kids, superhero theme",
  "source_type": "text"
}
```

**New Log Entries Added:**
```json
{
  "message": "Input complexity assessed",
  "complexity_level": "simple",
  "use_llm": false
}

{
  "message": "Processing with regex extraction"
}
```

### 3. View Logs
```http
GET /api/v1/event-driven/party/fp-test-party/logs
```

**Response:**
```json
{
  "total_logs": 3,
  "logs": [
    { "message": "Party session created" },
    { "message": "Input complexity assessed" },
    { "message": "Processing with regex extraction" }
  ]
}
```

---

## 🔍 Benefits

✅ **Per-Party Isolation** - Each party has its own log file
✅ **Easy Debugging** - Track entire party planning flow
✅ **Audit Trail** - Complete history of decisions made
✅ **Cost Analysis** - See how often LLM vs Regex is used
✅ **Performance Tracking** - Monitor processing times
✅ **Frontend Integration** - Display logs in UI

---

## 🎯 Key Features

1. **Automatic Context** - Party context is automatically tracked
2. **Structured JSON** - All logs are valid JSON for easy parsing
3. **Timestamped** - Every entry has ISO 8601 timestamp
4. **Filterable** - Filter by level, message type, etc.
5. **API Access** - Fetch logs via REST API
6. **Real-time** - Logs written immediately as events happen

---

## ⚠️ Important Notes

- Log files are created in `backend/logs/` directory
- Logs persist until manually cleared
- Each party session maintains separate log file
- Logs are written synchronously (no loss of data)
- Log files are UTF-8 encoded JSON lines
- Party IDs are automatically prefixed with `fp-`

---

**Status:** ✅ **PARTY-SPECIFIC LOGGING ACTIVE**

All routing decisions and events are now logged per-party!
