# 📝 Real Log Examples - Input Processing

**Quick Reference:** What you'll see in logs for different approaches

---

## 🟢 Example 1: SIMPLE Input → REGEX Processing

**Input:**
```json
{
  "text": "Birthday party for 30 kids, superhero theme, outdoor venue"
}
```

**Console Logs:**
```log
[2025-10-22 15:33:43] | INFO | Input complexity assessed
{
  "timestamp": "2025-10-22T22:33:43.812368+00:00",
  "level": "INFO",
  "message": "Input complexity assessed",
  "complexity_level": "simple",
  "use_llm": false,
  "reasons": ["explicit_theme", "explicit_event_type", "explicit_guest_count", "concise_input"],
  "has_vision": false
}

[2025-10-22 15:33:43] | INFO | Processing with regex extraction
{
  "timestamp": "2025-10-22T22:33:43.856098+00:00",
  "level": "INFO",
  "message": "Processing with regex extraction",
  "vision_confidence": null
}

[2025-10-22 15:33:43] | INFO | Starting LangGraph data extraction workflow
[2025-10-22 15:33:43] | INFO | Validating input for data extraction
[2025-10-22 15:33:43] | INFO | Input validation passed
[2025-10-22 15:33:43] | INFO | Extracting basic event information
[2025-10-22 15:33:43] | INFO | Extracted basic info: {"eventType": "Birthday", "theme": "Superhero"}
[2025-10-22 15:33:43] | INFO | Extracting event details
[2025-10-22 15:33:43] | INFO | Found 3 venues of type 'outdoor' for 30 guests
[2025-10-22 15:33:43] | INFO | Extracted event details

[2025-10-22 15:33:43] | INFO | Confidence calculated
{
  "timestamp": "2025-10-22T22:33:43.862240+00:00",
  "level": "INFO",
  "message": "Confidence calculated",
  "overall": 85.5,
  "completeness": 70.0,
  "quality": 80.0,
  "consistency": 100.0,
  "critical_present": true
}
```

**Response:**
```json
{
  "extracted_data": {
    "eventType": "Birthday",
    "theme": "Superhero",
    "guestCount": {"adults": 18, "kids": 12},
    "location": {
      "type": "Outdoor",
      "name": "Sunset Park",
      "venue_data": {...}
    }
  },
  "confidence": {
    "overall_score": 85.5
  },
  "processor": "regex",
  "routing": {
    "complexity": {"level": "simple", "use_llm": false},
    "processor": "regex"
  }
}
```

---

## 🟡 Example 2: MEDIUM Input → REGEX Processing (but closer to complex)

**Input:**
```json
{
  "text": "I need to plan something for my daughter's birthday. She really loves unicorns and rainbows."
}
```

**Console Logs:**
```log
[2025-10-22 15:35:12] | INFO | Input complexity assessed
{
  "complexity_level": "medium",
  "use_llm": false,
  "reasons": [
    "explicit_event_type",
    "moderate_length",
    "complex_language_x2"  // "loves", "really"
  ],
  "has_vision": false
}

[2025-10-22 15:35:12] | INFO | Processing with regex extraction
{
  "message": "Processing with regex extraction",
  "vision_confidence": null
}

[2025-10-22 15:35:12] | INFO | Confidence calculated
{
  "overall": 62.4,
  "completeness": 38.0,
  "quality": 34.0,
  "consistency": 100.0,
  "critical_present": false  // Missing guest count, budget
}
```

**Response:**
```json
{
  "extracted_data": {
    "eventType": "Birthday",
    "theme": "Unicorn",
    "honoreeName": "daughter"
  },
  "processor": "regex",
  "routing": {
    "complexity": {"level": "medium", "use_llm": false},
    "processor": "regex"
  }
}
```

---

## 🔴 Example 3: COMPLEX Input → LLM Processing

**Input:**
```json
{
  "text": "My grandmother is turning 80 and she loves gardening and tea parties. We want something elegant but not too formal, with her favorite flowers. She's very active for her age."
}
```

**Console Logs:**
```log
[2025-10-22 15:37:45] | INFO | Input complexity assessed
{
  "complexity_level": "complex",
  "use_llm": true,
  "reasons": [
    "moderate_length",
    "complex_language_x5",  // "loves", "favorite", "elegant", "active", "very"
    "long_narrative"
  ],
  "has_vision": false
}

[2025-10-22 15:37:45] | INFO | Processing with LLM planner
{
  "message": "Processing with LLM planner",
  "vision_confidence": null
}

[2025-10-22 15:37:45] | INFO | Generating LLM plan
{
  "input_length": 158,
  "has_image": false
}

[2025-10-22 15:37:48] | INFO | LLM plan generated
{
  "event_type": "Birthday",
  "theme": "Garden Tea Party",
  "confidence": 85.0,
  "agents_count": 4
}
```

**Response:**
```json
{
  "extracted_data": {
    "event_type": "Birthday",
    "theme": "Garden Tea Party",
    "sub_themes": ["Elegant", "Vintage", "Floral"],
    "honoree_name": "Grandmother",
    "honoree_age": 80,
    "honoree_relation": "grandmother",
    "age_group": "senior",
    "explicit_requirements": {
      "style": "elegant but not too formal",
      "interests": ["gardening", "tea parties"],
      "decorations": "favorite flowers"
    },
    "inferred_requirements": {
      "venue_type": "garden or outdoor",
      "food_type": "tea party menu",
      "atmosphere": "sophisticated yet comfortable",
      "accessibility": "senior-friendly"
    },
    "missing_information": ["guest_count", "budget", "date"],
    "agent_instructions": {
      "theme_agent": {
        "primary_theme": "Garden Tea Party",
        "style_keywords": ["elegant", "vintage", "floral"]
      },
      "venue_agent": {
        "preferred_types": ["garden", "outdoor", "banquet_hall"],
        "requirements": ["accessible", "elegant"]
      }
    }
  },
  "natural_language": "Birthday with Garden Tea Party theme for 80 year old celebrating Grandmother",
  "confidence": 85.0,
  "processor": "llm",
  "needs_user_input": true,
  "missing_fields": ["guest_count", "budget", "date"],
  "routing": {
    "complexity": {"level": "complex", "use_llm": true},
    "processor": "llm"
  }
}
```

---

## 🎨 Example 4: Image + Text → REGEX Processing

**Input:**
```json
{
  "text": "Birthday party for 50 guests",
  "image_url": "https://pinterest.com/pin/unicorn-party.jpg"
}
```

**Console Logs:**
```log
[2025-10-22 15:40:23] | INFO | Vision processing started
{
  "image_url": "https://pinterest.com/pin/unicorn-party.jpg"
}

[2025-10-22 15:40:25] | INFO | Vision analysis complete
{
  "detected_objects": 5,
  "primary_theme": "Unicorn",
  "confidence": 92.5
}

[2025-10-22 15:40:25] | INFO | Input complexity assessed
{
  "complexity_level": "medium",
  "use_llm": false,
  "reasons": [
    "explicit_event_type",
    "explicit_guest_count",
    "concise_input",
    "has_image_description"  // Image adds complexity but not enough to need LLM
  ],
  "has_vision": true
}

[2025-10-22 15:40:25] | INFO | Processing with regex extraction
{
  "vision_confidence": 92.5
}

[2025-10-22 15:40:25] | INFO | Confidence calculated
{
  "overall": 89.3,  // Boosted by high vision confidence
  "completeness": 75.0,
  "quality": 85.0,
  "vision_boost": 7.5
}
```

**Response:**
```json
{
  "extracted_data": {
    "eventType": "Birthday",
    "theme": "Unicorn",
    "guestCount": {"total": 50},
    "visual_elements": {
      "colors": ["pink", "purple", "rainbow"],
      "objects": ["balloons", "cake", "decorations"]
    }
  },
  "vision_data": {
    "detected_objects": [...],
    "confidence": 92.5
  },
  "processor": "regex",
  "routing": {
    "complexity": {"level": "medium", "use_llm": false},
    "processor": "regex",
    "vision_confidence": 92.5
  }
}
```

---

## 🎭 Example 5: Event-Driven Flow with LLM Input

**Request:**
```http
POST /api/v1/event-driven/party
{
  "party_id": "party-123",
  "initial_inputs": [
    {
      "type": "text",
      "content": "My daughter loves unicorns and rainbows. She's turning 5."
    }
  ]
}
```

**Console Logs:**
```log
[2025-10-22 15:42:10] | INFO | Party session created
{
  "party_id": "party-123"
}

[2025-10-22 15:42:10] | INFO | Input complexity assessed
{
  "complexity_level": "medium",
  "use_llm": false,
  "reasons": ["explicit_age", "moderate_length", "complex_language_x1"]
}

[2025-10-22 15:42:10] | INFO | Processing with regex extraction

[2025-10-22 15:42:10] | INFO | Input added to party
{
  "party_id": "party-123",
  "input_id": "input-abc123",
  "input_type": "text"
}

[2025-10-22 15:42:10] | INFO | InputAnalyzer processing input
{
  "input_id": "input-abc123",
  "processor_used": "regex"
}

[2025-10-22 15:42:10] | INFO | Input classified
{
  "input_id": "input-abc123",
  "agents_matched": ["theme_agent", "budget_agent"],
  "keywords_found": ["unicorn", "rainbow", "turning 5"]
}

[2025-10-22 15:42:10] | INFO | Agent should execute event published
{
  "event_type": "party.agent.should_execute",
  "agent_id": "theme_agent",
  "party_id": "party-123"
}

[2025-10-22 15:42:10] | INFO | Agent should execute event published
{
  "event_type": "party.agent.should_execute",
  "agent_id": "budget_agent",
  "party_id": "party-123"
}

[2025-10-22 15:42:11] | INFO | theme_agent started
{
  "party_id": "party-123",
  "input_count": 1
}

[2025-10-22 15:42:12] | INFO | theme_agent completed
{
  "party_id": "party-123",
  "theme_suggestions": ["Unicorn", "Rainbow", "Fantasy"],
  "execution_time": "1.2s"
}
```

---

## 📊 Log Summary by Route

### REGEX Route Logs (70% of inputs)
```
✅ Input complexity assessed (level: simple/medium)
✅ Processing with regex extraction
✅ LangGraph workflow steps (5-8 logs)
✅ Confidence calculated
```

### LLM Route Logs (30% of inputs)
```
✅ Input complexity assessed (level: complex)
✅ Processing with LLM planner
✅ Generating LLM plan
✅ LLM plan generated (with details)
```

### Event-Driven Additional Logs
```
✅ Party session created
✅ Input added to party
✅ InputAnalyzer processing input
✅ Input classified
✅ Agent should execute events (per matched agent)
✅ Agent started/completed events
```

---

## 🔍 How to Filter Logs

### View Only Routing Decisions
```bash
grep "Input complexity assessed" logs.txt
```

### View Only LLM Usage
```bash
grep "Processing with LLM" logs.txt
```

### View Only Agent Activity
```bash
grep "agent.*completed" logs.txt
```

### View Confidence Scores
```bash
grep "Confidence calculated" logs.txt
```

---

**Status:** All routing approaches are comprehensively logged in structured JSON format
