"""
LLM Planning Service

Uses GPT-4/Claude to understand complex party planning inputs and generate
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
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available - LLM planning will be disabled")


@dataclass
class StructuredPlan:
    """Structured party plan output from LLM"""

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

    Uses GPT-4 to:
    - Understand natural language party requests
    - Extract explicit and implicit requirements
    - Infer missing details from context
    - Generate structured plans for agents
    """

    def __init__(self):
        # Initialize confidence scorer
        self.confidence_scorer = get_confidence_scorer()

        if not OPENAI_AVAILABLE:
            logger.warning("LLM Planner initialized without OpenAI - will use fallback")
            self.enabled = False
            return

        self.enabled = bool(settings.OPENAI_API_KEY)

        if self.enabled:
            openai.api_key = settings.OPENAI_API_KEY
            logger.info("LLM Planner initialized", model="gpt-4-turbo")
        else:
            logger.warning("LLM Planner disabled - no OpenAI API key configured")

    async def generate_plan(
        self,
        user_input: str,
        image_description: Optional[str] = None,
        timeout: float = 30.0
    ) -> StructuredPlan:
        """
        Generate structured plan from user input

        Args:
            user_input: User's text input
            image_description: Optional image analysis description
            timeout: Request timeout in seconds

        Returns:
            StructuredPlan with extracted and inferred information
        """
        if not self.enabled:
            logger.warning("LLM planning not available - returning empty plan")
            return StructuredPlan(extraction_method="disabled")

        logger.info(
            "Generating LLM plan",
            input_length=len(user_input),
            has_image=bool(image_description)
        )

        try:
            # Build prompt
            prompt = self._build_planning_prompt(user_input, image_description)

            # Call OpenAI with timeout
            response = await asyncio.wait_for(
                self._call_openai(prompt),
                timeout=timeout
            )

            # Parse response
            plan = self._parse_llm_response(response, user_input, image_description)

            logger.info(
                "LLM plan generated",
                event_type=plan.event_type,
                theme=plan.theme,
                confidence=plan.confidence,
                agents_count=len(plan.agent_instructions)
            )

            return plan

        except asyncio.TimeoutError:
            logger.error("LLM planning timeout", timeout=timeout)
            return StructuredPlan(
                extraction_method="llm_timeout",
                confidence=0.0
            )

        except Exception as e:
            logger.error("LLM planning failed", error=str(e), error_type=type(e).__name__)
            return StructuredPlan(
                extraction_method="llm_error",
                confidence=0.0
            )

    def _build_planning_prompt(
        self,
        user_input: str,
        image_description: Optional[str]
    ) -> str:
        """Build the planning prompt for GPT-4"""

        prompt = f"""You are a professional party planner. Analyze this party planning request and create a detailed structured plan.

User Request: "{user_input}"
"""

        if image_description:
            prompt += f"""
Image Analysis: "{image_description}"
"""

        prompt += """
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
  "age_group": "preschool",
  "guest_type": "children",
  "explicit_requirements": {},
  "inferred_requirements": {
    "decorations": {
      "suggested_items": ["unicorn horn headbands", "rainbow balloons", "glitter decorations"],
      "color_scheme": ["rainbow", "pastel", "white", "gold"]
    },
    "cake": {
      "theme": "unicorn",
      "features": ["rainbow mane", "unicorn horn", "edible glitter"]
    },
    "activities": {
      "age_appropriate": ["face painting", "craft station", "simple games"]
    }
  },
  "missing_information": ["location", "guest_count", "date", "budget"],
  "agent_instructions": {
    "theme_agent": {
      "primary_theme": "rainbow unicorn",
      "color_scheme": ["rainbow", "pastel", "white", "gold"],
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
      "capacity_estimate": 30
    }
  }
}

Return ONLY valid JSON, no markdown or extra text."""

        return prompt

    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""

        response = await openai.ChatCompletion.acreate(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional party planner. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3,  # Lower for consistency
            max_tokens=2000
        )

        return response.choices[0].message.content

    def _parse_llm_response(
        self,
        response: str,
        original_input: str,
        image_description: Optional[str] = None
    ) -> StructuredPlan:
        """Parse LLM JSON response into StructuredPlan"""

        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse LLM JSON", error=str(e), response=response[:200])
            return StructuredPlan(extraction_method="llm_parse_error")

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

        # Build StructuredPlan
        plan = StructuredPlan(
            event_type=validated_data.get("event_type"),
            theme=validated_data.get("theme"),
            sub_themes=validated_data.get("sub_themes", []),
            honoree_name=validated_data.get("honoree_name"),
            honoree_age=validated_data.get("honoree_age"),
            honoree_relation=validated_data.get("honoree_relation"),
            age_group=validated_data.get("age_group"),
            guest_count=validated_data.get("guest_count"),
            guest_type=validated_data.get("guest_type"),
            explicit_requirements=validated_data.get("explicit_requirements", {}),
            inferred_requirements=validated_data.get("inferred_requirements", {}),
            missing_information=validated_data.get("missing_information", []),
            agent_instructions=validated_data.get("agent_instructions", {}),
            confidence=confidence_metrics.overall_score,
            extraction_method="llm"
        )

        return plan

    def _validate_extraction(self, data: Dict[str, Any], original_input: str) -> Dict[str, Any]:
        """
        Validate LLM extraction against original input to prevent hallucinations

        Rules:
        - Age must appear in original text
        - Guest count must appear in original text
        - Theme can be inferred
        - Event type can be inferred
        """
        validated = data.copy()
        original_lower = original_input.lower()

        # Validate age
        if data.get("honoree_age"):
            age_str = str(data["honoree_age"])
            if age_str not in original_input and f"{age_str} year" not in original_lower:
                logger.warning(
                    "LLM hallucinated age",
                    claimed_age=data["honoree_age"],
                    input=original_input[:100]
                )
                validated["honoree_age"] = None

        # Validate guest count
        if data.get("guest_count"):
            count_str = str(data["guest_count"])
            if count_str not in original_input:
                logger.warning(
                    "LLM hallucinated guest count",
                    claimed_count=data["guest_count"],
                    input=original_input[:100]
                )
                validated["guest_count"] = None

        # Theme and event_type can be inferred, so keep them

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
__all__ = ["LLMPlanner", "StructuredPlan", "get_llm_planner"]
