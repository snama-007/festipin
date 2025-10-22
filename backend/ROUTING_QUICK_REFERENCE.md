# 🎯 Routing Approach - Quick Reference

## Which Approach is Used?

### 🤖 HYBRID APPROACH (Automatic Decision)

The system **automatically chooses** between:

| Approach | Usage | Cost | Speed | When Used |
|----------|-------|------|-------|-----------|
| **Regex** | 70% | Free ✅ | Instant ⚡ | Simple/Medium inputs with explicit data |
| **LLM** | 30% | Paid 💰 | 2-5s 🐢 | Complex narratives requiring inference |

---

## Decision Algorithm

```
INPUT → Complexity Score (0-100)

Score ≥ 50  → REGEX (Free, Fast)
Score 20-49 → REGEX (Free, Fast)
Score < 20  → LLM (Paid, Smart)
```

### Scoring Factors

**Positive (Use Regex):**
- ✅ Has explicit theme: `"unicorn theme"` → +10
- ✅ Has event type: `"birthday party"` → +10
- ✅ Has guest count: `"30 guests"` → +10
- ✅ Short input (≤15 words) → +15
- ✅ Comma-separated → +10

**Negative (Use LLM):**
- ❌ Narrative language: `"loves", "favorite"` → -5 each
- ❌ Long text (>50 words) → -20
- ❌ Has image → -10

---

## What Gets Logged?

### Every Input Logs:

**1. Complexity Assessment**
```json
{
  "complexity_level": "simple|medium|complex",
  "use_llm": true|false,
  "reasons": ["explicit_theme", "concise_input"],
  "has_vision": false
}
```

**2. Processing Method**
```json
// REGEX:
{"message": "Processing with regex extraction"}

// LLM:
{"message": "Processing with LLM planner"}
{"message": "LLM plan generated", "theme": "Garden Tea Party"}
```

**3. Confidence Score**
```json
{
  "overall": 85.5,
  "completeness": 70.0,
  "critical_present": true
}
```

---

## LLM Output Format

When LLM is used, you get:

```json
{
  "extracted_data": {
    "event_type": "Birthday",
    "theme": "Garden Tea Party",
    "sub_themes": ["Elegant", "Vintage"],
    "honoree_age": 80,
    
    "explicit_requirements": {
      "style": "elegant but not too formal"
    },
    
    "inferred_requirements": {
      "venue_type": "garden or outdoor",
      "atmosphere": "sophisticated"
    },
    
    "missing_information": ["guest_count", "budget"],
    
    "agent_instructions": {
      "theme_agent": {...},
      "venue_agent": {...}
    }
  },
  
  "natural_language": "Birthday with Garden Tea Party theme for 80 year old",
  
  "processor": "llm",
  "confidence": 85.0
}
```

---

## InputAnalyzer Format

When using Event-Driven endpoints, InputAnalyzer receives:

```python
{
    "input_id": "input-abc123",
    "type": "text",
    "content": "Original input text...",
    
    # From hybrid processing:
    "processed": {
        "natural_language": "Simplified description",
        "extracted_data": {...},  # Full extraction
        "processor_used": "llm"|"regex",
        "confidence": 85.0,
        "agent_instructions": {...}  # Only if LLM used
    }
}
```

InputAnalyzer uses `natural_language` for keyword matching to route to agents.

---

## Examples

### Simple → Regex
```
Input: "Birthday party for 30 kids, superhero theme"
Score: 60 (explicit theme + event + count + concise)
Route: REGEX ✅
Time: 0.5s
Cost: $0
```

### Medium → Regex
```
Input: "I need to plan my daughter's birthday. She loves unicorns."
Score: 35 (event + moderate length - complex language)
Route: REGEX ✅
Time: 0.6s
Cost: $0
```

### Complex → LLM
```
Input: "My grandmother loves gardening. We want elegant but informal."
Score: 10 (long narrative + complex language)
Route: LLM 🤖
Time: 3s
Cost: $0.01
```

---

## View Logs

```bash
# Start server
./start_server.sh

# Logs show:
✅ Input complexity assessed → Shows which route
✅ Processing with regex/LLM → Confirms decision
✅ Confidence calculated → Quality metrics
```

---

## Documentation Files

- `ROUTING_AND_LOGGING_GUIDE.md` - Complete technical details
- `LOG_EXAMPLES.md` - Real log examples
- `FRONTEND_INTEGRATION.md` - API usage guide

---

**Key Insight:** The system is ALREADY HYBRID. You don't choose - it automatically picks the best approach for each input!
