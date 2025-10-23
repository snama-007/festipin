"""
LLM Planning Service

Uses Google Gemini to understand complex party planning inputs and generate
structured plans with deep semantic understanding.
"""

import json
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from app.core.config import settings
from app.core.logging import logger
from app.services.confidence_scorer import get_confidence_scorer

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI library not available - LLM planning will be disabled")


@dataclass
class DetailedPartyPlan:
    """Detailed party plan output from LLM (New format)"""

    # Party identification
    party_name: str = ""

    # Theme and creative direction
    theme_data: Dict[str, Any] = None  # {Theme, Vibe, ColorPalette, KeyInspiration, BudgetEstimate}

    # Logistics and fundamentals
    logistics: Dict[str, Any] = None  # {DateAndTime, Venue, GuestCount, BudgetStatus}

    # Decoration plan
    decor_data: Dict[str, Any] = None  # {OverallStyle, KeyElements, ExecutionPlan}

    # Activities and flow
    activities_plan: Dict[str, Any] = None  # {RunSheet, Activity1, Activity2, ...}

    # Food and catering
    food: Dict[str, Any] = None  # {Style, main, dessert, extras}

    # Favors and keepsakes
    favors_and_keepsakes: Dict[str, Any] = None  # {Favors, Items, Presentation}

    # Missing information
    missing_data: Dict[str, Any] = None  # {RequiredLogistics, RequiredPlanning, RequiredExecution}

    # Auto-generated agent instructions (for backward compatibility)
    agent_instructions: Dict[str, Dict[str, Any]] = None

    # Metadata
    confidence: float = 0.0
    extraction_method: str = "llm"

    def __post_init__(self):
        if self.theme_data is None:
            self.theme_data = {}
        if self.logistics is None:
            self.logistics = {}
        if self.decor_data is None:
            self.decor_data = {}
        if self.activities_plan is None:
            self.activities_plan = {}
        if self.food is None:
            self.food = {}
        if self.favors_and_keepsakes is None:
            self.favors_and_keepsakes = {}
        if self.missing_data is None:
            self.missing_data = {}
        if self.agent_instructions is None:
            self.agent_instructions = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def to_natural_language(self) -> str:
        """
        Convert detailed plan to natural language description
        for agent classification
        """
        parts = []

        # Party name
        if self.party_name:
            parts.append(self.party_name)

        # Theme
        if self.theme_data:
            theme = self.theme_data.get("Theme", "")
            vibe = self.theme_data.get("Vibe", "")
            if theme:
                parts.append(f"with {theme}")
            if vibe:
                parts.append(f"vibe: {vibe}")

        # Logistics - guest count
        if self.logistics:
            guest_count = self.logistics.get("GuestCount", {})
            if isinstance(guest_count, dict):
                total = guest_count.get("Total", 0)
                if total:
                    parts.append(f"for {total} guests")

        # Food style
        if self.food:
            food_style = self.food.get("Style", "")
            if food_style:
                parts.append(f"food style: {food_style}")

        # Decor style
        if self.decor_data:
            decor_style = self.decor_data.get("OverallStyle", "")
            if decor_style:
                parts.append(f"decor: {decor_style}")

        # Activities
        if self.activities_plan:
            run_sheet = self.activities_plan.get("RunSheet", [])
            if run_sheet:
                parts.append(f"with {len(run_sheet)} scheduled activities")

        return ". ".join(parts)

    def get_theme(self) -> str:
        """Extract theme for agent routing"""
        if self.theme_data:
            return self.theme_data.get("Theme", "")
        return ""

    def get_guest_count(self) -> Optional[int]:
        """Extract total guest count"""
        if self.logistics:
            guest_count = self.logistics.get("GuestCount", {})
            if isinstance(guest_count, dict):
                return guest_count.get("Total")
        return None

    def get_budget_range(self) -> str:
        """Extract budget range"""
        if self.theme_data:
            budget_est = self.theme_data.get("BudgetEstimate", {})
            if isinstance(budget_est, dict):
                return budget_est.get("Range", "")
        return ""


@dataclass
class StructuredPlan:
    """Structured party plan output from LLM (Legacy format - deprecated)"""

    # Event Details
    event_type: Optional[str] = None
    theme: Optional[str] = None
    sub_themes: List[str] = None

    # Honoree Information
    honoree_name: Optional[str] = None
    honoree_age: Optional[int] = None
    honoree_relation: Optional[str] = None
    age_group: Optional[str] = None

    # Guest Information
    guest_count: Optional[int] = None
    guest_type: Optional[str] = None

    # Explicit Requirements (user stated)
    explicit_requirements: Dict[str, Any] = None

    # Inferred Requirements (LLM deduced)
    inferred_requirements: Dict[str, Any] = None

    # Missing Information
    missing_information: List[str] = None

    # Agent Instructions
    agent_instructions: Dict[str, Dict[str, Any]] = None

    # Metadata
    confidence: float = 0.0
    extraction_method: str = "llm"

    def __post_init__(self):
        if self.sub_themes is None:
            self.sub_themes = []
        if self.explicit_requirements is None:
            self.explicit_requirements = {}
        if self.inferred_requirements is None:
            self.inferred_requirements = {}
        if self.missing_information is None:
            self.missing_information = []
        if self.agent_instructions is None:
            self.agent_instructions = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def to_natural_language(self) -> str:
        """
        Convert structured plan to natural language description
        for agent classification
        """
        parts = []

        # Event type and theme
        if self.event_type:
            parts.append(f"{self.event_type}")

        if self.theme:
            parts.append(f"with {self.theme} theme")

        # Honoree
        if self.honoree_age:
            parts.append(f"for {self.honoree_age} year old")

        if self.honoree_name:
            parts.append(f"celebrating {self.honoree_name}")

        # Guests
        if self.guest_count:
            parts.append(f"for {self.guest_count} guests")

        # Explicit requirements
        for category, details in self.explicit_requirements.items():
            if isinstance(details, dict):
                for key, value in details.items():
                    if value is True:
                        parts.append(f"needs {key.replace('_', ' ')}")
                    elif isinstance(value, str):
                        parts.append(f"{key}: {value}")

        # Inferred requirements
        for category, details in self.inferred_requirements.items():
            if isinstance(details, dict) and details.get('suggested_items'):
                items = details['suggested_items']
                if isinstance(items, list):
                    parts.append(f"featuring {', '.join(items[:3])}")

        return ". ".join(parts)


class LLMPlanner:
    """
    LLM-based planning service for complex input understanding

    Uses Google Gemini to:
    - Understand natural language party requests
    - Extract explicit and implicit requirements
    - Infer missing details from context
    - Generate structured plans for agents
    """

    def __init__(self):
        # Initialize confidence scorer
        self.confidence_scorer = get_confidence_scorer()

        if not GEMINI_AVAILABLE:
            logger.warning("LLM Planner initialized without Gemini - will use fallback")
            self.enabled = False
            return

        self.enabled = bool(settings.GEMINI_API_KEY)

        if self.enabled:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                generation_config={
                    "temperature": 0.3,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                    "response_mime_type": "application/json",
                }
            )
            logger.info("LLM Planner initialized", model=settings.GEMINI_MODEL)
        else:
            logger.warning("LLM Planner disabled - no Gemini API key configured")

    async def generate_plan(
        self,
        user_input: str,
        image_description: Optional[str] = None,
        timeout: float = 30.0
    ) -> DetailedPartyPlan:
        """
        Generate detailed party plan from user input

        Args:
            user_input: User's text input
            image_description: Optional image analysis description
            timeout: Request timeout in seconds

        Returns:
            DetailedPartyPlan with 8-section detailed structure
        """
        if not self.enabled:
            logger.warning("LLM planning not available - returning empty plan")
            return DetailedPartyPlan(extraction_method="disabled")

        logger.info(
            "Generating LLM plan",
            input_length=len(user_input),
            has_image=bool(image_description)
        )

        try:
            # Build prompt
            prompt = self._build_planning_prompt(user_input, image_description)

            # Call Gemini with timeout
            response = await asyncio.wait_for(
                self._call_gemini(prompt),
                timeout=timeout
            )

            # Parse response
            plan = self._parse_llm_response(response, user_input, image_description)

            logger.info(
                "LLM plan generated",
                party_name=plan.party_name,
                theme=plan.get_theme(),
                confidence=plan.confidence,
                agents_count=len(plan.agent_instructions)
            )

            return plan

        except asyncio.TimeoutError:
            logger.error("LLM planning timeout", timeout=timeout)
            return DetailedPartyPlan(
                extraction_method="llm_timeout",
                confidence=0.0
            )

        except Exception as e:
            logger.error("LLM planning failed", error=str(e), error_type=type(e).__name__)
            return DetailedPartyPlan(
                extraction_method="llm_error",
                confidence=0.0
            )

    def _build_planning_prompt(
        self,
        user_input: str,
        image_description: Optional[str]
    ) -> str:
        """Build the planning prompt for Gemini using specialized Event Planner AI prompt"""

        # Base system prompt from gemini_sys_prompt.txt
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

**CONDITIONAL INSTRUCTION (Flow Management):**

*   **Initial Request:** If the user provides the initial prompt, generate the complete JSON plan, performing the **Budget Estimation** and placing necessary placeholders in the `MissingData` section.
*   **Subsequent Update:** If the user provides data to fill a placeholder in a subsequent turn (e.g., provides the Allergy List or Date/Time), you MUST generate a **new, fully updated JSON** where that data is integrated into the correct section, and the placeholder is removed or marked as "Confirmed" in the `MissingData` section.

**EXECUTION MANDATE:** Be meticulous. Every detail must be accounted for. The generated JSON must be syntactically perfect and follow the structure explicitly. If a data point is vague, make a sensible, budget-appropriate assumption (and note the assumption).

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

    async def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API"""

        # Gemini expects a single prompt string
        full_prompt = f"""You are a professional party planner. Always respond with valid JSON only.

{prompt}"""

        # Generate content asynchronously
        response = await self.model.generate_content_async(full_prompt)

        return response.text

    def _parse_llm_response(
        self,
        response: str,
        original_input: str,
        image_description: Optional[str] = None
    ) -> DetailedPartyPlan:
        """Parse LLM JSON response into DetailedPartyPlan (new 8-section format)"""

        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse LLM JSON", error=str(e), response=response[:200])
            return DetailedPartyPlan(extraction_method="llm_parse_error")

        # Validate against original input to prevent hallucinations
        validation_passed = True
        try:
            validated_data = self._validate_extraction(data, original_input)
        except Exception as e:
            logger.warning("Validation error", error=str(e))
            validated_data = data
            validation_passed = False

        # Calculate enhanced confidence score
        source_text = original_input
        if image_description:
            source_text = f"{original_input}. Image shows: {image_description}"

        confidence_metrics = self.confidence_scorer.calculate_confidence(
            extracted_data=validated_data,
            source_input=source_text,
            extraction_method="llm",
            image_confidence=None,  # LLM doesn't have direct vision confidence
            validation_passed=validation_passed
        )

        logger.debug(
            "Enhanced confidence calculated",
            overall=confidence_metrics.overall_score,
            completeness=confidence_metrics.field_completeness,
            quality=confidence_metrics.field_quality,
            critical_present=confidence_metrics.critical_fields_present
        )

        # Extract 8 sections from new format
        party_name = validated_data.get("PartyName", "")
        theme_data = validated_data.get("ThemeData", {})
        logistics = validated_data.get("Logistics", {})
        decor_data = validated_data.get("DecorData", {})
        activities_plan = validated_data.get("ActivitiesPlan", {})
        food = validated_data.get("food", {})
        favors_and_keepsakes = validated_data.get("FavorsAndKeepsakes", {})
        missing_data = validated_data.get("MissingData", {})

        # Auto-generate agent_instructions for backward compatibility
        agent_instructions = self._generate_agent_instructions(
            theme_data=theme_data,
            logistics=logistics,
            decor_data=decor_data,
            activities_plan=activities_plan,
            food=food
        )

        # Build DetailedPartyPlan
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
            confidence=confidence_metrics.overall_score,
            extraction_method="llm"
        )

        return plan

    def _generate_agent_instructions(
        self,
        theme_data: Dict[str, Any],
        logistics: Dict[str, Any],
        decor_data: Dict[str, Any],
        activities_plan: Dict[str, Any],
        food: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Auto-generate agent_instructions from new 8-section format
        for backward compatibility with existing agent routing system
        """
        agent_instructions = {}

        # Theme Agent - from ThemeData
        if theme_data:
            theme_agent_data = {}
            if theme_data.get("Theme"):
                theme_agent_data["primary_theme"] = theme_data["Theme"]

            if theme_data.get("ColorPalette"):
                color_palette = theme_data["ColorPalette"]
                if isinstance(color_palette, dict):
                    primary_colors = color_palette.get("PrimaryColors", [])
                    accent_color = color_palette.get("AccentColor")
                    colors = primary_colors.copy() if isinstance(primary_colors, list) else []
                    if accent_color:
                        colors.append(accent_color)
                    theme_agent_data["color_scheme"] = colors

            if theme_data.get("Vibe"):
                theme_agent_data["style"] = theme_data["Vibe"]

            if theme_agent_data:
                agent_instructions["theme_agent"] = theme_agent_data

        # Decoration Agent - from DecorData
        if decor_data:
            decor_agent_data = {}
            if decor_data.get("OverallStyle"):
                decor_agent_data["style"] = decor_data["OverallStyle"]

            if decor_data.get("KeyElements"):
                key_elements = decor_data["KeyElements"]
                if isinstance(key_elements, list):
                    items = [elem.get("Item", "") for elem in key_elements if isinstance(elem, dict)]
                    if items:
                        decor_agent_data["suggested_items"] = items

            # Use theme from ThemeData
            if theme_data and theme_data.get("Theme"):
                decor_agent_data["theme"] = theme_data["Theme"]

            if decor_agent_data:
                agent_instructions["decoration_agent"] = decor_agent_data

        # Cake Agent - from food.dessert
        if food and food.get("dessert"):
            dessert = food["dessert"]
            cake_agent_data = {}

            # Extract cake details from dessert items
            if isinstance(dessert, dict):
                items = dessert.get("Items", [])
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            item_name = item.get("Item", "")
                            if "cake" in item_name.lower():
                                cake_agent_data["style"] = "custom_themed"
                                detail = item.get("Detail", "")
                                if detail:
                                    cake_agent_data["description"] = detail
                                break

            # Use theme from ThemeData
            if theme_data and theme_data.get("Theme"):
                cake_agent_data["theme"] = theme_data["Theme"]

            if cake_agent_data:
                agent_instructions["cake_agent"] = cake_agent_data

        # Venue Agent - from Logistics.Venue
        if logistics and logistics.get("Venue"):
            venue = logistics["Venue"]
            venue_agent_data = {}

            if isinstance(venue, dict):
                if venue.get("Type"):
                    venue_agent_data["type"] = venue["Type"]
                if venue.get("Location"):
                    venue_agent_data["location"] = venue["Location"]

            # Guest count for capacity
            guest_count = logistics.get("GuestCount", {})
            if isinstance(guest_count, dict):
                total = guest_count.get("Total")
                if total:
                    venue_agent_data["capacity_estimate"] = total

            if venue_agent_data:
                agent_instructions["venue_agent"] = venue_agent_data

        # Entertainment Agent - from ActivitiesPlan
        if activities_plan:
            entertainment_agent_data = {}

            # Look for activities
            activity_keys = [k for k in activities_plan.keys() if k.startswith("Activity")]
            if activity_keys:
                activities = []
                for key in activity_keys:
                    activity = activities_plan[key]
                    if isinstance(activity, dict) and activity.get("Name"):
                        activities.append(activity["Name"])

                if activities:
                    entertainment_agent_data["suggested_activities"] = activities

            # Use theme from ThemeData
            if theme_data and theme_data.get("Theme"):
                entertainment_agent_data["theme"] = theme_data["Theme"]

            if entertainment_agent_data:
                agent_instructions["entertainment_agent"] = entertainment_agent_data

        # Food/Catering Agent - from food
        if food:
            food_agent_data = {}

            if food.get("Style"):
                food_agent_data["style"] = food["Style"]

            # Guest count
            if logistics:
                guest_count = logistics.get("GuestCount", {})
                if isinstance(guest_count, dict):
                    total = guest_count.get("Total")
                    if total:
                        food_agent_data["guest_count"] = total

            if food_agent_data:
                agent_instructions["food_agent"] = food_agent_data

        return agent_instructions

    def _validate_extraction(self, data: Dict[str, Any], original_input: str) -> Dict[str, Any]:
        """
        Validate LLM extraction against original input to prevent hallucinations

        Rules:
        - Age must appear in original text (check PartyName)
        - Guest count must appear in original text (check Logistics.GuestCount)
        - Theme can be inferred
        - Budget estimates can be inferred
        """
        validated = data.copy()
        original_lower = original_input.lower()

        # Extract from new 8-section format
        logistics = data.get("Logistics", {})
        party_name = data.get("PartyName", "")

        # Validate age (if present in PartyName like "Birthday (Emma, 6)")
        import re
        age_match = re.search(r'\(.*?,\s*(\d+)\)', party_name)
        if age_match:
            age_str = age_match.group(1)
            if age_str not in original_input and f"{age_str} year" not in original_lower:
                logger.warning(
                    "LLM hallucinated age in PartyName",
                    claimed_age=age_str,
                    input=original_input[:100]
                )
                # Remove age from PartyName
                validated["PartyName"] = re.sub(r',\s*\d+\)', ')', party_name)

        # Validate guest count
        if logistics and isinstance(logistics, dict):
            guest_count = logistics.get("GuestCount", {})
            if isinstance(guest_count, dict):
                total = guest_count.get("Total")
                kids = guest_count.get("Kids")
                adults = guest_count.get("Adults")

                # Check if Total is hallucinated
                if total:
                    count_str = str(total)
                    if count_str not in original_input:
                        logger.warning(
                            "LLM hallucinated total guest count",
                            claimed_count=total,
                            input=original_input[:100]
                        )
                        if "Logistics" in validated and "GuestCount" in validated["Logistics"]:
                            validated["Logistics"]["GuestCount"]["Total"] = None

                # Check if Kids count is hallucinated
                if kids:
                    kids_str = str(kids)
                    if kids_str not in original_input:
                        logger.warning(
                            "LLM hallucinated kids count",
                            claimed_count=kids,
                            input=original_input[:100]
                        )
                        if "Logistics" in validated and "GuestCount" in validated["Logistics"]:
                            validated["Logistics"]["GuestCount"]["Kids"] = None

                # Check if Adults count is hallucinated
                if adults:
                    adults_str = str(adults)
                    if adults_str not in original_input:
                        logger.warning(
                            "LLM hallucinated adults count",
                            claimed_count=adults,
                            input=original_input[:100]
                        )
                        if "Logistics" in validated and "GuestCount" in validated["Logistics"]:
                            validated["Logistics"]["GuestCount"]["Adults"] = None

        # Theme, budget estimates, and inferred details can be inferred, so keep them

        return validated

    def _calculate_llm_confidence(self, data: Dict[str, Any]) -> float:
        """Calculate confidence score for LLM extraction"""

        score = 0.0
        max_score = 100.0

        # Event type (20 points)
        if data.get("event_type"):
            score += 20

        # Theme (20 points)
        if data.get("theme"):
            score += 20

        # Honoree info (15 points)
        if data.get("honoree_age"):
            score += 10
        if data.get("honoree_relation"):
            score += 5

        # Guest info (15 points)
        if data.get("guest_count"):
            score += 10
        if data.get("guest_type"):
            score += 5

        # Requirements (15 points)
        if data.get("explicit_requirements"):
            score += 7
        if data.get("inferred_requirements"):
            score += 8

        # Agent instructions (15 points)
        if data.get("agent_instructions"):
            score += 15

        return round((score / max_score) * 100, 2)


# Singleton instance
_llm_planner: Optional[LLMPlanner] = None


def get_llm_planner() -> LLMPlanner:
    """Get global LLM planner instance"""
    global _llm_planner
    if _llm_planner is None:
        _llm_planner = LLMPlanner()
    return _llm_planner


# Export
__all__ = ["LLMPlanner", "StructuredPlan", "DetailedPartyPlan", "get_llm_planner"]
