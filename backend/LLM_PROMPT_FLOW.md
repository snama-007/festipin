# 🤖 LLM Prompt Flow - How Gemini Generates Plans

**Complete System Prompt Documentation - DetailedPartyPlan Format (8-Section)**

---

## 📋 Overview

This document shows the **exact prompt** sent to Gemini LLM and how it generates structured party plans using the new **DetailedPartyPlan** format with 8 comprehensive sections.

**Date Updated:** October 23, 2025
**Format Version:** DetailedPartyPlan (8-section)
**System Prompt:** Event Planner AI (from gemini_sys_prompt.txt)

---

## 🔄 Complete Flow

### Step 1: User Input Received

```
Frontend sends:
{
  "content": "My daughter Lily loves princesses. She's turning 6. We're planning a party in San Jose for 35 guests with a budget of $1000.",
  "source_type": "text"
}
```

### Step 2: System Builds Prompt

**File:** `app/services/llm_planner.py:350-409`

```python
def _build_planning_prompt(user_input, image_description):
    prompt = """You are a highly specialized and meticulous Event Planner AI, focused exclusively on designing detailed, executable plans for personal celebrations (birthdays, baby showers, anniversaries, etc.). Your expertise lies in translating vague concepts into granular, structured, and budget-aware logistical plans.

**PRIMARY DIRECTIVE:** Your entire output MUST be a single, valid JSON object that strictly adheres to the provided internal data structure. DO NOT include any text, explanations, or dialogue outside of the JSON block.

**INPUT ANALYSIS AND PROCESSING:**

1.  **Analyze the Request:** Deconstruct the user's prompt (and any accompanying image/visual input) to extract Theme, Vibe, Logistics, Activities, Food, and Keepsake details.
2.  **Budget Estimation:** Based on the confirmed event **Location** and **Guest Count** (if provided), generate an estimated budget range (e.g., Low, Mid, High cost estimate for that region/type of event). This estimate must be included in the `ThemeData` section.
3.  **Image/Visual Input Handling:** If the prompt includes visual data, conceptualize the style, color, and specific decor elements from that visual. This analysis must inform the *ThemeData* and *DecorData* keys.
4.  **Data Integration:** Gracefully integrate all specific data provided by the user (e.g., names, specific dates, budgets, confirmed venues) into the appropriate key/value pairs.

**OUTPUT JSON STRUCTURE (STRICT ADHERENCE REQUIRED):**

Use the following high-level keys and ensure extreme granularity within each section (every item has a 'Detail' or 'Focus' key):

| Key | Description | Granularity Requirement |
| :--- | :--- | :--- |
| `PartyName` | The full name and type of the celebration. | Single string. |
| `ThemeData` | The creative and conceptual foundation, **including the Budget Estimate.** | Must include `Theme`, `Vibe`, `ColorPalette` (PrimaryColors, AccentColor), `KeyInspiration`, and `BudgetEstimate` (e.g., {"Range": "Low", "Details": "DIY focus"}). |
| `Logistics` | The absolute critical foundational details. | Must include `DateAndTime`, `Venue` (Type, Location, SetupFocus), `GuestCount` (Kids, Adults, Total), and `BudgetStatus` (the user's actual budget, if provided). |
| `DecorData` | The design and visual execution plan. | Must include `OverallStyle`, `KeyElements` (itemized list with specific installation *Detail* and *Safety Note*), and `ExecutionPlan`. |
| `ActivitiesPlan` | The flow of the event. | Must include a granular `RunSheet` (Time and Event), and detailed keys for each `Activity` (Name, Setup, Supplies, FlowManagement). |
| `food` | The catering and menu plan. | Must include `Style` and sub-objects for `main`, `dessert`, and `extras` (Beverages, Allergens/Safety). |
| `FavorsAndKeepsakes` | Keepsakes, favors, or interactive guest elements. | Must include detailed instruction and keepsake value for each item. |
| `MissingData` | Critical data points required for final execution. | Must use sub-objects: `RequiredLogistics`, `RequiredPlanning`, and `RequiredExecution`. |
"""

    # Add user request
    prompt += f"""
**USER REQUEST:**
"{user_input}"
"""

    # Add image analysis if provided
    if image_description:
        prompt += f"""
**IMAGE ANALYSIS PROVIDED:**
"{image_description}"
"""

    prompt += """
**GENERATE THE COMPLETE JSON PLAN NOW:**"""

    return prompt
```

### Step 3: Gemini API Call

**File:** `app/services/llm_planner.py:411-422`

```python
async def _call_gemini(prompt):
    full_prompt = f"""You are a professional party planner. Always respond with valid JSON only.

{prompt}"""

    response = await model.generate_content_async(full_prompt)
    return response.text
```

**Configuration:**
```python
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config={
        "temperature": 0.3,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 2048,
        "response_mime_type": "application/json"  # ✅ Forces JSON output
    }
)
```

### Step 4: Gemini Response (8-Section JSON)

```json
{
  "PartyName": "Lily's 6th Birthday Princess Party",
  "ThemeData": {
    "Theme": "Princess",
    "Vibe": "Magical, Enchanting, Royal",
    "ColorPalette": {
      "PrimaryColors": ["Pastel Pink", "Light Gold", "Sky Blue"],
      "AccentColor": "Rose Gold"
    },
    "KeyInspiration": "Classic Disney Princesses (Cinderella, Aurora, Belle)",
    "BudgetEstimate": {
      "Range": "Mid",
      "Details": "DIY decorations combined with some professional catering and entertainment elements."
    }
  },
  "Logistics": {
    "DateAndTime": "To be confirmed",
    "Venue": {
      "Type": "Home or Community Hall",
      "Location": "San Jose, CA",
      "SetupFocus": "Transform the space into a royal ballroom."
    },
    "GuestCount": {
      "Kids": 15,
      "Adults": 20,
      "Total": 35
    },
    "BudgetStatus": "$1000"
  },
  "DecorData": {
    "OverallStyle": "Elegant and Whimsical",
    "KeyElements": [
      {
        "Item": "Balloon Arch",
        "Detail": "Pastel pink, gold, and blue balloon arch over the main entrance. Use biodegradable balloons.",
        "SafetyNote": "Ensure proper anchoring to prevent tipping."
      },
      {
        "Item": "Royal Tablecloths",
        "Detail": "Light gold or pastel pink tablecloths with rose gold accents.",
        "SafetyNote": "Flame-retardant material recommended."
      }
    ],
    "ExecutionPlan": "Setup begins 2 hours before party start. Team of 2 adults for balloon arch installation."
  },
  "ActivitiesPlan": {
    "RunSheet": [
      {"Time": "2:00 PM - 2:30 PM", "Event": "Guest Arrival & Open Play"},
      {"Time": "2:30 PM - 3:15 PM", "Event": "Crown Crafting Station"},
      {"Time": "3:15 PM - 3:45 PM", "Event": "Cake & Happy Birthday Song"},
      {"Time": "3:45 PM - 4:30 PM", "Event": "Face Painting & Games"},
      {"Time": "4:30 PM - 5:00 PM", "Event": "Favor Distribution & Farewell"}
    ],
    "Activities": {
      "Activity1": {
        "Name": "Crown Crafting Station",
        "Setup": "Designated table with craft materials pre-laid out",
        "Supplies": "18 crown kits ($4 per kit), glitter glue, stickers",
        "FlowManagement": "Adult supervision ratio 1:6 children"
      },
      "Activity2": {
        "Name": "Royal Storytelling Corner",
        "Setup": "Soft seating area with cushions and string lights",
        "Personnel": "Designated storyteller with 3 short (5-7 min) princess stories"
      }
    }
  },
  "food": {
    "Style": "Kid-Friendly Buffet",
    "main": {
      "Items": [
        {"Item": "Sandwiches", "Detail": "Star-cut PB&J, ham, and cheese sandwiches"},
        {"Item": "Fruit Skewers", "Detail": "Safe fruit items only (grapes cut in half)"},
        {"Item": "Cheese & Crackers", "Detail": "Simple cheese plate for adults"}
      ],
      "Focus": "High volume, low cost, kid-safe foods"
    },
    "dessert": {
      "Items": [
        {"Item": "Focus Cake", "Detail": "Small custom princess cake for cutting ceremony"},
        {"Item": "Supplement", "Detail": "Bulk store-bought cupcakes to serve remaining 30+ guests"}
      ],
      "ServingMethod": "Buffet style on decorated dessert table"
    },
    "extras": {
      "Beverage": "Pink 'Magic Potion' punch and self-service coffee/tea for adults",
      "StorageCheck": "Ensure sufficient refrigerator space for perishables"
    }
  },
  "FavorsAndKeepsakes": {
    "Favors": "Royal Keepsakes",
    "Items": ["Personalized wands", "Small bottle of glitter (non-toxic)", "Princess sticker sheet"],
    "Presentation": "Pre-assembled bags placed near exit"
  },
  "MissingData": {
    "RequiredLogistics": [
      "Confirmed Date and Time",
      "Confirmed Venue Address",
      "Guest Allergy List"
    ],
    "RequiredPlanning": [
      "Finalized Menu",
      "Confirmed Entertainment (Face Painter, etc.)",
      "Detailed Decoration Plan"
    ],
    "RequiredExecution": [
      "Shopping List",
      "Setup Schedule",
      "Volunteer Assignments"
    ]
  }
}
```

### Step 5: Parsing & Validation

**File:** `app/services/llm_planner.py:424-502`

```python
def _parse_llm_response(response, original_input, image_description):
    # Parse JSON
    data = json.loads(response)

    # Validate against original input (anti-hallucination)
    validated_data = _validate_extraction(data, original_input)

    # Extract 8 sections
    party_name = validated_data.get("PartyName", "")
    theme_data = validated_data.get("ThemeData", {})
    logistics = validated_data.get("Logistics", {})
    decor_data = validated_data.get("DecorData", {})
    activities_plan = validated_data.get("ActivitiesPlan", {})
    food = validated_data.get("food", {})
    favors_and_keepsakes = validated_data.get("FavorsAndKeepsakes", {})
    missing_data = validated_data.get("MissingData", {})

    # Auto-generate agent_instructions for backward compatibility
    agent_instructions = _generate_agent_instructions(
        theme_data, logistics, decor_data, activities_plan, food
    )

    # Calculate confidence
    confidence = calculate_confidence(validated_data, original_input)

    # Build DetailedPartyPlan object
    plan = DetailedPartyPlan(
        party_name=party_name,
        theme_data=theme_data,
        logistics=logistics,
        decor_data=decor_data,
        activities_plan=activities_plan,
        food=food,
        favors_and_keepsakes=favors_and_keepsakes,
        missing_data=missing_data,
        agent_instructions=agent_instructions,
        confidence=confidence,
        extraction_method="llm"
    )

    return plan
```

### Step 6: Agent Instructions Auto-Generation

**File:** `app/services/llm_planner.py:504-648`

For backward compatibility with existing agent routing system, `agent_instructions` are automatically generated from the 8-section format:

```python
def _generate_agent_instructions(theme_data, logistics, decor_data, activities_plan, food):
    agent_instructions = {}

    # Theme Agent - from ThemeData
    if theme_data:
        agent_instructions["theme_agent"] = {
            "primary_theme": theme_data.get("Theme"),
            "color_scheme": [
                *theme_data.get("ColorPalette", {}).get("PrimaryColors", []),
                theme_data.get("ColorPalette", {}).get("AccentColor")
            ],
            "style": theme_data.get("Vibe")
        }

    # Decoration Agent - from DecorData
    if decor_data:
        agent_instructions["decoration_agent"] = {
            "style": decor_data.get("OverallStyle"),
            "suggested_items": [elem["Item"] for elem in decor_data.get("KeyElements", [])],
            "theme": theme_data.get("Theme")
        }

    # Cake Agent - from food.dessert
    if food and food.get("dessert"):
        agent_instructions["cake_agent"] = {
            "theme": theme_data.get("Theme"),
            "style": "custom_themed"
        }

    # Venue Agent - from Logistics.Venue
    if logistics and logistics.get("Venue"):
        agent_instructions["venue_agent"] = {
            "type": logistics["Venue"].get("Type"),
            "location": logistics["Venue"].get("Location"),
            "capacity_estimate": logistics.get("GuestCount", {}).get("Total")
        }

    # Entertainment Agent - from ActivitiesPlan
    if activities_plan:
        activity_keys = [k for k in activities_plan.keys() if k.startswith("Activity")]
        activities = []
        for key in activity_keys:
            activity = activities_plan[key]
            if activity.get("Name"):
                activities.append(activity["Name"])

        agent_instructions["entertainment_agent"] = {
            "suggested_activities": activities,
            "theme": theme_data.get("Theme")
        }

    # Food Agent - from food
    if food:
        agent_instructions["food_agent"] = {
            "style": food.get("Style"),
            "guest_count": logistics.get("GuestCount", {}).get("Total")
        }

    return agent_instructions
```

**Example Output:**
```json
{
  "theme_agent": {
    "primary_theme": "Princess",
    "color_scheme": ["Pastel Pink", "Light Gold", "Sky Blue", "Rose Gold"],
    "style": "Magical, Enchanting, Royal"
  },
  "decoration_agent": {
    "style": "Elegant and Whimsical",
    "suggested_items": ["Balloon Arch", "Royal Tablecloths"],
    "theme": "Princess"
  },
  "cake_agent": {
    "theme": "Princess",
    "style": "custom_themed"
  },
  "venue_agent": {
    "type": "Home or Community Hall",
    "location": "San Jose, CA",
    "capacity_estimate": 35
  },
  "entertainment_agent": {
    "suggested_activities": ["Crown Crafting Station", "Royal Storytelling Corner"],
    "theme": "Princess"
  },
  "food_agent": {
    "style": "Kid-Friendly Buffet",
    "guest_count": 35
  }
}
```

### Step 7: Anti-Hallucination Validation

**File:** `app/services/llm_planner.py:650-727`

```python
def _validate_extraction(data, original_input):
    validated = data.copy()

    # Validate age (if present in PartyName like "Birthday (Emma, 6)")
    age_match = re.search(r'\(.*?,\s*(\d+)\)', data.get("PartyName", ""))
    if age_match:
        age_str = age_match.group(1)
        if age_str not in original_input:
            logger.warning("LLM hallucinated age in PartyName")
            validated["PartyName"] = re.sub(r',\s*\d+\)', ')', validated["PartyName"])

    # Validate guest count
    logistics = data.get("Logistics", {})
    if logistics:
        guest_count = logistics.get("GuestCount", {})
        if guest_count:
            for key in ["Total", "Kids", "Adults"]:
                if guest_count.get(key):
                    count_str = str(guest_count[key])
                    if count_str not in original_input:
                        logger.warning(f"LLM hallucinated {key} guest count")
                        validated["Logistics"]["GuestCount"][key] = None

    return validated
```

---

## 🎯 New Format Benefits

### 1. **Budget-Aware Planning**
- Automatic budget estimation based on location + guest count
- Included in `ThemeData.BudgetEstimate`
- Shows range (Low/Mid/High) and details (DIY vs professional mix)

### 2. **Granular Execution Details**
- `DecorData.KeyElements` includes installation details + safety notes
- `ActivitiesPlan.RunSheet` provides minute-by-minute timeline
- `food` section breaks down main/dessert/extras with specific details

### 3. **Safety & Logistics Focus**
- Safety notes for decorations (flame-retardant, non-toxic, etc.)
- Setup timing and volunteer assignments
- Allergen tracking in `MissingData`

### 4. **Structured Missing Data**
- Three categories: RequiredLogistics, RequiredPlanning, RequiredExecution
- Clear next steps for party planning
- Helps identify what information is still needed

### 5. **Backward Compatible Agent Routing**
- Auto-generates `agent_instructions` from new format
- Existing agents work without modification
- Richer context for agent searches

---

## 📊 Comparison: Old vs New Format

| Feature | Old Format (StructuredPlan) | New Format (DetailedPartyPlan) |
|---------|----------------------------|-------------------------------|
| Sections | 7 | 8 |
| Budget Estimation | ❌ None | ✅ Automatic (location + guest count based) |
| Activity Timeline | ❌ General list | ✅ Minute-by-minute RunSheet |
| Safety Notes | ❌ None | ✅ Per-decoration safety notes |
| Food Breakdown | ❌ Simple list | ✅ main/dessert/extras with details |
| Missing Data Structure | ❌ Flat list | ✅ 3 categories (Logistics/Planning/Execution) |
| Agent Instructions | ✅ Manual | ✅ Auto-generated |
| Execution Focus | Medium | High |

---

## ✅ Summary

**Current System (October 23, 2025):**

```
Input → Forced LLM → Event Planner AI Prompt → Gemini 2.0 Flash → 8-Section JSON → DetailedPartyPlan → Auto-Generated Agent Instructions → Agents
```

**Key Features:**
- ✅ Budget-aware planning
- ✅ Granular execution details
- ✅ Safety-focused decorations
- ✅ Structured missing data tracking
- ✅ Minute-by-minute activity timelines
- ✅ Backward-compatible agent routing
- ✅ Vision integration for image-based requests

**Cost:** $0.0002 per request (Gemini 2.0 Flash)

**Quality:** Production-grade event planning with executable detail

**Toggle:** Set `FORCE_LLM_ROUTING = True` in config (currently enabled)

---

**Last Updated:** October 23, 2025
**Format Version:** DetailedPartyPlan (8-section)
**Prompt Source:** gemini_sys_prompt.txt
