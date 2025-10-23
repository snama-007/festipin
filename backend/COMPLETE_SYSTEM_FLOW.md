# 🎯 Complete System Flow - From Input to Agent Routing

**End-to-End Documentation**

---

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Current Configuration](#current-configuration)
3. [Complete Flow](#complete-flow)
4. [LLM Prompt Engineering](#llm-prompt-engineering)
5. [Agent Routing](#agent-routing)
6. [Examples](#examples)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│         (Sends text + optional image to backend)                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EVENT-DRIVEN API                              │
│              POST /party/{id}/input                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              UNIFIED INPUT PROCESSOR                             │
│         (Processes text + optional image)                        │
│                                                                   │
│  If image → Vision API → Image Description                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│               SMART INPUT ROUTER                                 │
│                                                                   │
│  🔄 Current Mode: FORCED LLM                                     │
│  ✅ Skip complexity assessment                                   │
│  ✅ Route ALL inputs to Gemini LLM                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  LLM PLANNER (Gemini 2.0 Flash)                 │
│                                                                   │
│  1. Build system prompt                                          │
│  2. Send to Gemini API                                           │
│  3. Receive structured JSON                                      │
│  4. Validate (anti-hallucination)                                │
│  5. Calculate confidence                                         │
│  6. Create StructuredPlan object                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  INPUT ANALYZER AGENT                            │
│       (Receives plan, classifies inputs)                         │
│                                                                   │
│  Uses plan.to_natural_language() for classification             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT ROUTING                                 │
│        (Based on plan.agent_instructions)                        │
│                                                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐               │
│  │ Theme      │  │   Cake     │  │   Venue    │               │
│  │ Agent      │  │   Agent    │  │   Agent    │  ...          │
│  └────────────┘  └────────────┘  └────────────┘               │
└───────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PARTY LOGGING                                  │
│          logs/party_fp-{id}.log                                  │
│                                                                   │
│  All decisions and routing logged to party-specific file        │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Current Configuration

**File:** `app/core/config.py`

```python
# AI Services
GEMINI_API_KEY: str = "AIzaSy..."
GEMINI_MODEL: str = "gemini-2.0-flash"

# Routing Strategy
FORCE_LLM_ROUTING: bool = True  # ✅ ACTIVE
```

**What This Means:**
- ✅ Complexity assessment is SKIPPED
- ✅ ALL inputs route to Gemini LLM
- ✅ Vision integration still active when images provided
- ✅ 100% of requests use LLM (vs 30% in hybrid mode)

---

## 🔄 Complete Flow

### Step 1: Frontend Input

```javascript
// Frontend sends
POST /api/v1/event-driven/party/fp-test-party/input
{
  "content": "My daughter Emma loves unicorns. She is turning 6.",
  "source_type": "text",
  "image_url": null  // Optional
}
```

### Step 2: Unified Input Processor

```python
# app/services/unified_input_processor.py

processor = get_unified_processor()

processed = await processor.process(
    content="My daughter Emma loves unicorns. She is turning 6.",
    source_type="text",
    image_url=None,
    tags=[]
)

# Output:
# {
#   "natural_language": "My daughter Emma loves unicorns. She is turning 6.",
#   "processor_chain": ["text"],
#   "confidence": 100,
#   "vision_data": None
# }
```

### Step 3: Smart Router (Forced LLM Mode)

```python
# app/services/smart_input_router.py

router = get_smart_router()

# Check configuration
if settings.FORCE_LLM_ROUTING:  # ✅ True
    # Log decision
    log_party_event("Forced LLM routing enabled - skipping complexity assessment")

    # Route to LLM (skip complexity assessment)
    result = await router._process_with_llm(
        user_input="My daughter Emma loves unicorns. She is turning 6.",
        image_description=None,
        vision_confidence=None
    )
```

### Step 4: LLM Planner Builds Prompt

```python
# app/services/llm_planner.py

planner = get_llm_planner()

# Build prompt
prompt = """You are a professional party planner. Always respond with valid JSON only.

You are a professional party planner. Analyze this party planning request and create a detailed structured plan.

User Request: "My daughter Emma loves unicorns. She is turning 6."

Create a comprehensive JSON plan with:

1. **event_details**: Event type, theme, sub-themes
2. **honoree_info**: Name, age, relation, age group
3. **guest_info**: Guest count, guest type (children/adults/mixed)
4. **explicit_requirements**: What the user explicitly stated
5. **inferred_requirements**: What you can deduce from context
6. **missing_information**: Critical info needed (location, date, budget, etc.)
7. **agent_instructions**: Specific search criteria for each agent

Be specific and actionable. Extract ALL implicit needs.

Example for "My daughter loves rainbows and unicorns, turning 5":
{
  "event_type": "birthday",
  "theme": "rainbow unicorn",
  "sub_themes": ["rainbow", "magical", "fantasy"],
  "honoree_age": 5,
  "honoree_relation": "daughter",
  ...
}

Return ONLY valid JSON, no markdown or extra text."""
```

### Step 5: Gemini API Call

```python
# Send to Gemini
response = await model.generate_content_async(prompt)

# Response received in ~3-6 seconds
```

### Step 6: Gemini Response (JSON)

```json
{
  "event_details": {
    "event_type": "birthday",
    "theme": "unicorn",
    "sub_themes": ["magic", "fantasy", "rainbows", "sparkles"]
  },
  "honoree_info": {
    "name": "Emma",
    "age": 6,
    "relation": "daughter",
    "age_group": "early_childhood"
  },
  "guest_info": {
    "guest_count": null,
    "guest_type": "children"
  },
  "explicit_requirements": {
    "theme": "unicorns"
  },
  "inferred_requirements": {
    "decorations": {
      "suggested_items": ["unicorn balloons", "rainbow streamers", "glitter tablecloth"],
      "color_scheme": ["pastel", "rainbow", "white", "gold", "pink"]
    },
    "cake": {
      "theme": "unicorn",
      "features": ["rainbow layers", "unicorn horn", "edible glitter"]
    },
    "activities": {
      "age_appropriate": ["face painting", "craft station", "unicorn themed games"]
    }
  },
  "missing_information": ["location", "date", "time", "budget", "guest_count"],
  "agent_instructions": {
    "theme_agent": {
      "primary_theme": "unicorn",
      "color_scheme": ["pastel", "rainbow", "white", "gold"],
      "style": "magical_whimsical"
    },
    "cake_agent": {
      "theme": "unicorn",
      "style": "custom_themed",
      "features": ["rainbow_layers", "unicorn_horn_topper"]
    },
    "venue_agent": {
      "type": "indoor_or_outdoor",
      "child_friendly": true,
      "capacity_estimate": 25
    },
    "entertainment_agent": {
      "type": "children's entertainer",
      "specialty": "unicorn-themed",
      "age_appropriateness": "6-year-olds"
    },
    "decoration_agent": {
      "theme": "unicorn",
      "style": "whimsical, magical",
      "color_palette": ["pastel", "rainbow", "gold"]
    }
  }
}
```

### Step 7: Validation & Parsing

```python
# Validate (prevent hallucinations)
validated_data = planner._validate_extraction(data, original_input)

# Check: Age "6" appears in input ✅
# Check: Guest count not in input → remains null ✅

# Parse into StructuredPlan
plan = StructuredPlan(
    event_type="birthday",
    theme="unicorn",
    sub_themes=["magic", "fantasy", "rainbows", "sparkles"],
    honoree_name="Emma",
    honoree_age=6,
    honoree_relation="daughter",
    age_group="early_childhood",
    guest_count=None,
    guest_type="children",
    explicit_requirements={"theme": "unicorns"},
    inferred_requirements={...},
    missing_information=["location", "date", "time", "budget", "guest_count"],
    agent_instructions={...},
    confidence=50.0,
    extraction_method="llm"
)
```

### Step 8: Natural Language Conversion

```python
# Convert to natural language for InputAnalyzer
nl = plan.to_natural_language()

# Output:
"birthday. with unicorn theme. for 6 year old. celebrating Emma.
featuring unicorn balloons, rainbow streamers, glitter tablecloth"
```

### Step 9: Input Analyzer Classification

```python
# app/services/agents/input_analyzer_agent.py

analyzer = InputAnalyzerAgent()

classification = analyzer.analyze_input(
    natural_language="birthday. with unicorn theme. for 6 year old...",
    metadata={
        "extracted_data": plan.to_dict(),
        "agent_instructions": plan.agent_instructions
    }
)

# Classifies input into categories:
# - theme (unicorn)
# - cake (unicorn cake)
# - venue (child-friendly)
# - entertainment (kids entertainer)
# - decorations (unicorn themed)
```

### Step 10: Agent Routing

```python
# Orchestrator routes to agents based on agent_instructions

# Theme Agent receives:
{
  "primary_theme": "unicorn",
  "color_scheme": ["pastel", "rainbow", "white", "gold"],
  "style": "magical_whimsical"
}
# Searches Pinterest for "unicorn party theme pastel rainbow"

# Cake Agent receives:
{
  "theme": "unicorn",
  "style": "custom_themed",
  "features": ["rainbow_layers", "unicorn_horn_topper"]
}
# Searches for "unicorn birthday cake rainbow layers custom"

# Venue Agent receives:
{
  "type": "indoor_or_outdoor",
  "child_friendly": true,
  "capacity_estimate": 25
}
# Searches for "child friendly party venue capacity 25"

# ... and so on for all agents
```

### Step 11: Party Logging

```json
// logs/party_fp-test-party.log

{"timestamp": "2025-10-23T...", "level": "INFO", "party_id": "fp-test-party", "message": "Forced LLM routing enabled - skipping complexity assessment", "input_preview": "My daughter Emma loves unicorns..."}
{"timestamp": "2025-10-23T...", "level": "INFO", "party_id": "fp-test-party", "message": "Processing with LLM planner", "vision_confidence": null}
{"timestamp": "2025-10-23T...", "level": "INFO", "party_id": "fp-test-party", "message": "LLM plan generated", "event_type": "birthday", "theme": "unicorn", "confidence": 50.0}
```

---

## 🤖 LLM Prompt Engineering

### Key Elements

**1. Role Definition**
```
"You are a professional party planner."
```

**2. Clear Task**
```
"Analyze this party planning request and create a detailed structured plan."
```

**3. Structured Output (7 sections)**
- event_details
- honoree_info
- guest_info
- explicit_requirements
- inferred_requirements
- missing_information
- agent_instructions

**4. Few-Shot Example**
Complete example showing desired JSON format

**5. Specific Instructions**
- "Be specific and actionable"
- "Extract ALL implicit needs"
- "Return ONLY valid JSON"

**6. JSON Mode Enforcement**
```python
generation_config={
    "response_mime_type": "application/json"
}
```

---

## 🎯 Agent Routing

### How Agents Use agent_instructions

Each agent receives specific search criteria from the LLM plan:

**Theme Agent:**
```python
instructions = plan.agent_instructions["theme_agent"]
# {
#   "primary_theme": "unicorn",
#   "color_scheme": ["pastel", "rainbow"],
#   "style": "magical_whimsical"
# }

# Executes:
search_pinterest("unicorn party theme", filters={
    "colors": ["pastel", "rainbow"],
    "style": "magical"
})
```

**Cake Agent:**
```python
instructions = plan.agent_instructions["cake_agent"]
# {
#   "theme": "unicorn",
#   "features": ["rainbow_layers", "unicorn_horn"]
# }

# Executes:
search_cakes("unicorn birthday cake", filters={
    "features": ["rainbow layers", "horn topper"],
    "custom": true
})
```

**Venue Agent:**
```python
instructions = plan.agent_instructions["venue_agent"]
# {
#   "type": "indoor_or_outdoor",
#   "child_friendly": true,
#   "capacity_estimate": 25
# }

# Executes:
search_venues(filters={
    "child_friendly": true,
    "capacity": 20-30,
    "type": ["indoor", "outdoor"]
})
```

---

## 📝 Examples

### Example 1: Simple Text Input

**Input:**
```
"Birthday party for 30 kids, superhero theme"
```

**Flow:**
1. ✅ Forced LLM mode → Skip complexity
2. ✅ Send to Gemini with prompt
3. ✅ Gemini extracts: birthday, superhero, 30 guests
4. ✅ Creates agent_instructions for theme, cake, venue
5. ✅ Agents search with specific criteria

**Result:**
- Theme Agent: Searches "superhero party theme"
- Cake Agent: Searches "superhero birthday cake 30 servings"
- Venue Agent: Searches "venue 30 kids capacity"

---

### Example 2: Complex Narrative

**Input:**
```
"My grandmother loves her rose garden and afternoon tea.
She's turning 85 next month."
```

**Flow:**
1. ✅ Forced LLM mode → Skip complexity
2. ✅ Send to Gemini with context
3. ✅ Gemini infers: birthday, garden tea party, senior, elegant
4. ✅ Creates rich inferred_requirements
5. ✅ Agent instructions tailored for seniors

**Result:**
- Theme Agent: Searches "vintage garden tea party elegant"
- Cake Agent: Searches "garden floral cake elegant"
- Venue Agent: Searches "senior-friendly outdoor garden venue"

---

### Example 3: With Image

**Input:**
```
Text: "I want exactly this for the party"
Image: "Enchanted forest setup with fairy lights, mushrooms, moss"
```

**Flow:**
1. ✅ Vision API analyzes image
2. ✅ Image description passed to LLM
3. ✅ Gemini combines text + vision context
4. ✅ Extracts: enchanted forest theme
5. ✅ Agent instructions include specific visual elements

**Result:**
- Theme Agent: Searches "enchanted forest party fairy lights mushrooms"
- Decoration Agent: Searches "moss table runner woodland creatures"
- Venue Agent: Searches "outdoor venue suitable for enchanted theme"

---

## ✅ Summary

**Current System:**

```
Input → Forced LLM → Gemini → Structured Plan → Agent Instructions → Agents
```

**Key Features:**
- ✅ All inputs processed by Gemini LLM (maximum quality)
- ✅ Rich semantic understanding and inference
- ✅ Detailed agent instructions for precise searches
- ✅ Vision integration when images provided
- ✅ Anti-hallucination validation
- ✅ Complete logging to party-specific files

**Cost:** $0.0002 per request (~3x hybrid mode, 50-150x cheaper than OpenAI)

**Quality:** Highest quality extraction for all inputs

**Toggle:** Set `FORCE_LLM_ROUTING = False` to restore hybrid mode
