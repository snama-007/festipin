# 🔀 Routing & Logging Guide - Hybrid Input Processing

**Last Updated:** October 22, 2025

---

## ⚙️ Current Routing Mode

**🚀 FORCED LLM MODE: ACTIVE**

The system is currently configured to **skip complexity assessment** and route **ALL inputs to Gemini LLM** for maximum quality.

- Configuration: `FORCE_LLM_ROUTING = True` in `app/core/config.py`
- See `FORCED_LLM_MODE.md` for complete documentation
- To restore hybrid routing: Set `FORCE_LLM_ROUTING = False`

---

## 📊 Overview: How Input is Processed

When the frontend sends input (text/image), the backend can use two approaches:

### **Current Mode: Forced LLM (Active)**
- ✅ **ALL inputs** → Gemini LLM (100% of cases) - Paid, highest quality
- ⏭️ Complexity assessment **skipped**

### **Alternative Mode: Hybrid (Disabled)**
When hybrid mode is enabled (`FORCE_LLM_ROUTING = False`):
1. **Fast Regex Extraction** (70% of cases) - Free, instant
2. **LLM Planning** (30% of cases) - Paid, intelligent

The system **automatically logs** which approach is used and why.

---

## 🔄 Step-by-Step Flow

### Step 1: Input Received from Frontend

```http
POST /api/v1/input/process-hybrid
{
  "text": "Birthday party for 30 kids, superhero theme, outdoor venue",
  "image_url": "https://..."  // Optional
}
```

### Step 2: Complexity Assessment (Smart Routing Decision)

**File:** `app/services/smart_input_router.py:117-126`

The system analyzes the input and scores it (0-100):

**Scoring Algorithm:**
```
Score = 0

✅ Explicit Data (40 points max):
  - Has theme keyword (+10) → "superhero theme"
  - Has event type (+10) → "birthday party"
  - Has guest count (+10) → "30 kids"
  - Has age mention (+5) → "5 year old"
  - Has location (+5) → "outdoor venue"

✅ Simplicity Indicators (30 points max):
  - Very short (≤15 words) → +15 points
  - Short (≤30 words) → +10 points
  - Comma-separated format → +10 points
  - Structured/bulleted → +5 points

❌ Complexity Penalties (negative points):
  - Complex language (-5 per keyword):
    "loves", "favorite", "elegant", "special", etc.
  - Long narrative (>50 words) → -20 points
  - Has image → -10 points

RESULT:
  Score ≥ 50 → SIMPLE (use regex)
  Score 20-49 → MEDIUM (use regex)
  Score < 20 → COMPLEX (use LLM)
```

**🔍 LOGGED:**
```json
{
  "timestamp": "2025-10-22T...",
  "level": "INFO",
  "message": "Input complexity assessed",
  "complexity_level": "simple",  // "simple", "medium", or "complex"
  "use_llm": false,
  "reasons": [
    "explicit_theme",
    "explicit_event_type",
    "explicit_guest_count",
    "concise_input"
  ],
  "has_vision": false
}
```

### Step 3A: REGEX Processing (Simple/Medium Inputs)

**File:** `app/services/smart_input_router.py:272-320`

**🔍 LOGGED:**
```json
{
  "timestamp": "2025-10-22T...",
  "level": "INFO",
  "message": "Processing with regex extraction",
  "vision_confidence": null
}
```

**Process:**
1. Uses `DataExtractionAgent` (LangGraph workflow)
2. Regex pattern matching for keywords
3. Venue database lookup
4. Confidence scoring

**Output Format:**
```json
{
  "extracted_data": {
    "eventType": "Birthday",
    "theme": "Superhero",
    "guestCount": {
      "adults": 18,
      "kids": 12
    },
    "location": {
      "type": "Outdoor",
      "name": "Sunset Park",
      "venue_data": {...}
    }
  },
  "natural_language": "Birthday party for 30 kids, superhero theme, outdoor venue",
  "confidence": {
    "overall_score": 85.5,
    "field_completeness": 70.0,
    "field_quality": 80.0,
    "critical_fields_present": true
  },
  "processor": "regex",
  "routing": {
    "complexity": {
      "level": "simple",
      "reasons": ["explicit_theme", "explicit_event_type"],
      "use_llm": false,
      "confidence": 0.75
    },
    "processor": "regex"
  }
}
```

### Step 3B: LLM Processing (Complex Inputs)

**File:** `app/services/smart_input_router.py:246-270`

**Example Complex Input:**
```
"My grandmother is turning 80 and she loves gardening and tea parties.
We want something elegant but not too formal, with her favorite flowers."
```

**🔍 LOGGED:**
```json
{
  "timestamp": "2025-10-22T...",
  "level": "INFO",
  "message": "Processing with LLM planner",
  "vision_confidence": null
}
```

**LLM Planning Process:**

**File:** `app/services/llm_planner.py:148-210`

**🔍 LOGGED (Start):**
```json
{
  "timestamp": "2025-10-22T...",
  "level": "INFO",
  "message": "Generating LLM plan",
  "input_length": 147,
  "has_image": false
}
```

**LLM Prompt Sent:**
```
You are a professional party planner. Analyze this party planning request
and create a detailed structured plan.

User Request: "My grandmother is turning 80 and she loves gardening and
tea parties. We want something elegant but not too formal, with her
favorite flowers."

Return JSON with:
{
  "event_type": "string",
  "theme": "string",
  "honoree_age": number,
  "explicit_requirements": {...},
  "inferred_requirements": {...},
  "missing_information": [...],
  "agent_instructions": {...}
}
```

**🔍 LOGGED (Complete):**
```json
{
  "timestamp": "2025-10-22T...",
  "level": "INFO",
  "message": "LLM plan generated",
  "event_type": "Birthday",
  "theme": "Garden Tea Party",
  "confidence": 85.0,
  "agents_count": 4
}
```

**LLM Output Format:**

**Data Class:** `app/services/llm_planner.py:25-74`

```python
@dataclass
class StructuredPlan:
    # Event Details
    event_type: Optional[str]           # "Birthday"
    theme: Optional[str]                # "Garden Tea Party"
    sub_themes: List[str]               # ["Elegant", "Vintage", "Floral"]

    # Honoree
    honoree_name: Optional[str]         # "Grandmother"
    honoree_age: Optional[int]          # 80
    honoree_relation: Optional[str]     # "grandmother"
    age_group: Optional[str]            # "senior"

    # Guests
    guest_count: Optional[int]          # null (not mentioned)
    guest_type: Optional[str]           # "family"

    # Requirements
    explicit_requirements: Dict         # User stated directly
    inferred_requirements: Dict         # LLM deduced

    # Missing Data
    missing_information: List[str]      # ["guest_count", "budget", "date"]

    # Agent Instructions
    agent_instructions: Dict            # What each agent should do

    # Metadata
    confidence: float                   # 0.0 - 100.0
    extraction_method: str              # "llm"
```

**Full LLM Response Example:**
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
    "guest_count": null,
    "guest_type": "family",
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
    "missing_information": [
      "guest_count",
      "budget",
      "date",
      "specific_flower_preferences"
    ],
    "agent_instructions": {
      "theme_agent": {
        "primary_theme": "Garden Tea Party",
        "style_keywords": ["elegant", "vintage", "floral"],
        "age_appropriate": true
      },
      "venue_agent": {
        "preferred_types": ["garden", "outdoor", "banquet_hall"],
        "requirements": ["accessible", "elegant", "garden_setting"]
      },
      "budget_agent": {
        "estimate_based_on": "seniors_party",
        "special_considerations": ["quality_over_quantity"]
      }
    },
    "confidence": 85.0,
    "extraction_method": "llm"
  },
  "natural_language": "Birthday with Garden Tea Party theme for 80 year old celebrating Grandmother",
  "confidence": 85.0,
  "processor": "llm",
  "needs_user_input": true,
  "missing_fields": ["guest_count", "budget", "date", "specific_flower_preferences"],
  "agent_instructions": {...},
  "routing": {
    "complexity": {
      "level": "complex",
      "reasons": ["complex_language_x4", "long_narrative"],
      "use_llm": true,
      "confidence": 0.15
    },
    "processor": "llm"
  }
}
```

---

## 🎯 How LLM Output Flows to Event-Driven System

### InputAnalyzer Agent Integration

**File:** `app/services/agents/input_analyzer_agent.py`

When using the event-driven endpoint:

**Step 1: Create Party with LLM-Processed Input**
```http
POST /api/v1/event-driven/party
{
  "party_id": "party-123",
  "initial_inputs": [
    {
      "type": "text",
      "content": "My grandmother loves gardening..."
    }
  ]
}
```

**Step 2: Input is Processed**
1. Input goes through `process-hybrid` internally
2. Complexity assessed → COMPLEX
3. LLM planner generates StructuredPlan
4. Natural language description created

**Step 3: InputAnalyzer Receives Format**

**What InputAnalyzer Gets:**
```python
{
    "input_id": "input-abc123",
    "type": "text",
    "content": "My grandmother is turning 80...",

    # PROCESSED VERSION (from hybrid processing):
    "processed": {
        "natural_language": "Birthday with Garden Tea Party theme for 80 year old",
        "extracted_data": {
            "event_type": "Birthday",
            "theme": "Garden Tea Party",
            "honoree_age": 80,
            # ... full LLM extraction
        },
        "processor_used": "llm",
        "confidence": 85.0
    }
}
```

**Step 4: InputAnalyzer Classifies & Routes**

**File:** `app/services/agents/input_analyzer_agent.py:150-250`

```python
def _classify_input(self, input_obj: Dict) -> Set[str]:
    """Classify which agents should execute"""

    agents_to_execute = set()

    # Use natural language from LLM
    text = input_obj["processed"]["natural_language"].lower()
    extracted = input_obj["processed"]["extracted_data"]

    # Theme detection
    if "theme" in extracted or any(keyword in text for keyword in theme_keywords):
        agents_to_execute.add("theme_agent")

    # Budget detection
    if "budget" in extracted or any(keyword in text for keyword in budget_keywords):
        agents_to_execute.add("budget_agent")

    # Venue detection
    if "location" in extracted or any(keyword in text for keyword in venue_keywords):
        agents_to_execute.add("venue_agent")

    return agents_to_execute
```

**🔍 LOGGED:**
```json
{
  "timestamp": "2025-10-22T...",
  "level": "INFO",
  "message": "Input classified",
  "input_id": "input-abc123",
  "agents_matched": ["theme_agent", "budget_agent", "venue_agent"],
  "processor_used": "llm"
}
```

**Step 5: Agents Execute**

Each agent receives:
```python
{
    "party_id": "party-123",
    "all_inputs": [...],  // All party inputs
    "processed_data": {   // Aggregated from all inputs
        "event_type": "Birthday",
        "theme": "Garden Tea Party",
        "honoree_age": 80,
        # ... combined from all LLM/regex extractions
    },
    "llm_instructions": {  // From LLM plan
        "theme_agent": {
            "primary_theme": "Garden Tea Party",
            "style_keywords": ["elegant", "vintage"]
        }
    }
}
```

---

## 📋 Complete Logging Flow Summary

### 1. Frontend Sends Input
```
→ No log yet
```

### 2. Complexity Assessment
```json
✅ LOG: "Input complexity assessed"
{
  "complexity_level": "simple|medium|complex",
  "use_llm": true|false,
  "reasons": ["explicit_theme", ...],
  "has_vision": true|false
}
```

### 3A. If REGEX Route
```json
✅ LOG: "Processing with regex extraction"
✅ LOG: "Regex extraction confidence"
{
  "overall": 85.5,
  "completeness": 70.0,
  "critical_present": true
}
```

### 3B. If LLM Route
```json
✅ LOG: "Processing with LLM planner"
✅ LOG: "Generating LLM plan"
{
  "input_length": 147,
  "has_image": false
}
✅ LOG: "LLM plan generated"
{
  "event_type": "Birthday",
  "theme": "Garden Tea Party",
  "confidence": 85.0,
  "agents_count": 4
}
```

### 4. Event-Driven (if using /event-driven endpoints)
```json
✅ LOG: "Input added to party"
{
  "party_id": "party-123",
  "input_id": "input-abc123",
  "input_type": "text"
}

✅ LOG: "Input classified"
{
  "agents_matched": ["theme_agent", "budget_agent"],
  "processor_used": "llm"
}

✅ LOG: "Agent should execute event published"
{
  "agent_id": "theme_agent",
  "party_id": "party-123"
}
```

---

## 🔍 How to View Logs

### Development Mode
Logs are output to console with colors and structure:

```bash
# Start server
uvicorn app.main:app --reload

# Example log output:
[32m2025-10-22 15:33:43[0m | [1mINFO[0m | Input complexity assessed
{"complexity_level": "simple", "use_llm": false, "reasons": ["explicit_theme"]}

[32m2025-10-22 15:33:43[0m | [1mINFO[0m | Processing with regex extraction
```

### Access Logs via API
```http
GET /api/v1/event-driven/party/{party_id}/logs
```
(If implemented - currently logs go to stdout)

---

## 💡 Key Takeaways

### Cost Optimization
- ✅ **70% of inputs use FREE regex** (simple/medium)
- ✅ **30% use PAID LLM** (complex only)
- ✅ **Automatic decision** - no configuration needed

### Logging Detail
- ✅ **Every step is logged** with structured JSON
- ✅ **Clear processor identification** (regex vs llm)
- ✅ **Confidence scores** for quality tracking
- ✅ **Agent routing decisions** visible

### LLM Format
- ✅ **Structured JSON output** (StructuredPlan dataclass)
- ✅ **Natural language summary** for agent routing
- ✅ **Agent-specific instructions** included
- ✅ **Missing fields** clearly identified

---

## 📊 Decision Tree Diagram

```
Input Received
    ↓
Complexity Assessment
    ↓
    ├─ Score ≥ 50 (SIMPLE)
    │   ↓
    │   Regex Processing → Fast, Free
    │   ↓
    │   DataExtractionAgent (LangGraph)
    │   ↓
    │   Pattern Matching + Venue DB
    │
    ├─ Score 20-49 (MEDIUM)
    │   ↓
    │   Regex Processing → Fast, Free
    │   ↓
    │   (Same as simple)
    │
    └─ Score < 20 (COMPLEX)
        ↓
        LLM Processing → Slower, Paid
        ↓
        GPT-4 / Claude
        ↓
        StructuredPlan with Inferences
        ↓
        Natural Language Summary

    ↓
Return to Frontend / Event System
    ↓
InputAnalyzer (Event-Driven)
    ↓
Classify & Route to Agents
    ↓
theme_agent, budget_agent, etc.
```

---

**Status:** ✅ **All routing decisions and data flows logged comprehensively**
