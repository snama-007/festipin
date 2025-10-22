"""
Smart Input Router

Intelligently routes inputs to either:
- Fast regex extraction (for simple, structured inputs)
- LLM planning (for complex, narrative inputs)

Optimizes for both cost and quality.
"""

import re
from typing import Dict, Any, Optional, Literal
from dataclasses import dataclass

from app.core.logging import logger
from app.services.llm_planner import get_llm_planner, StructuredPlan
from app.services.data_extraction_agent import DataExtractionAgent
from app.services.confidence_scorer import get_confidence_scorer
from app.services.keyword_expansions import get_all_theme_keywords, get_all_event_keywords


@dataclass
class InputComplexity:
    """Assessment of input complexity"""

    level: Literal["simple", "medium", "complex"]
    reasons: list[str]
    use_llm: bool
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "reasons": self.reasons,
            "use_llm": self.use_llm,
            "confidence": self.confidence
        }


class SmartInputRouter:
    """
    Intelligent router that chooses extraction strategy based on input complexity

    Strategy Selection:
    - Simple inputs → Fast regex extraction (free, instant)
    - Complex inputs → LLM planning ($0.01-0.03, 2-5s, better quality)

    Cost Optimization: Saves ~70% by avoiding LLM for simple inputs
    """

    def __init__(self):
        self.regex_agent = DataExtractionAgent()
        self.llm_planner = get_llm_planner()
        self.confidence_scorer = get_confidence_scorer()

        # Get expanded keywords
        theme_keywords = get_all_theme_keywords()
        event_keywords = get_all_event_keywords()

        # Build theme regex pattern from expanded keywords (limit to top common ones for performance)
        # Use the most distinctive theme keywords to avoid false positives
        core_theme_keywords = [
            'princess', 'superhero', 'unicorn', 'dinosaur', 'space', 'pirate', 'jungle', 'safari',
            'beach', 'mermaid', 'carnival', 'construction', 'farm', 'sports', 'frozen', 'mickey',
            'paw patrol', 'peppa pig', 'rainbow', 'vintage', 'elegant', 'garden', 'art', 'music'
        ]
        theme_pattern = '|'.join(core_theme_keywords)

        # Build event regex pattern from expanded keywords
        core_event_keywords = [
            'birthday', 'wedding', 'anniversary', 'baby shower', 'graduation', 'retirement',
            'baptism', 'engagement', 'bday', 'b-day'
        ]
        event_pattern = '|'.join(core_event_keywords)

        # Compile regex patterns for complexity assessment
        self._patterns = {
            'explicit_theme': re.compile(
                rf'\b({theme_pattern})\s*(party|theme|birthday|celebration)?\b',
                re.IGNORECASE
            ),
            'explicit_event': re.compile(
                rf'\b({event_pattern})\b',
                re.IGNORECASE
            ),
            'explicit_count': re.compile(r'\b(\d+)\s*(guests?|people|persons?|kids?|children)\b'),
            'explicit_age': re.compile(r'\b(?:turning|age|years? old)\s*(\d+)\b'),
            'explicit_location': re.compile(r'\b(at|in|near|zip|zipcode|city)\s+([A-Za-z\s]+|\d{5})\b'),
            'explicit_budget': re.compile(r'\$\s*(\d+)'),
        }

        logger.info(
            "Smart Input Router initialized",
            theme_keywords=len(theme_keywords),
            event_keywords=len(event_keywords),
            patterns_count=len(self._patterns)
        )

    async def process_input(
        self,
        user_input: str,
        image_description: Optional[str] = None,
        vision_confidence: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Process input with optimal strategy

        Args:
            user_input: User's text input
            image_description: Optional vision analysis description
            vision_confidence: Optional vision analysis confidence (0-1)

        Returns:
            Dict with extraction results and metadata
        """

        # Step 1: Assess complexity
        complexity = self._assess_complexity(user_input, image_description)

        logger.info(
            "Input complexity assessed",
            complexity_level=complexity.level,
            use_llm=complexity.use_llm,
            reasons=complexity.reasons,
            has_vision=vision_confidence is not None
        )

        # Step 2: Route to appropriate processor
        if complexity.use_llm:
            # Use LLM for complex inputs
            result = await self._process_with_llm(user_input, image_description, vision_confidence)
        else:
            # Use fast regex for simple inputs
            result = await self._process_with_regex(user_input, image_description, vision_confidence)

        # Step 3: Add routing metadata
        result["routing"] = {
            "complexity": complexity.to_dict(),
            "processor": "llm" if complexity.use_llm else "regex",
            "vision_confidence": vision_confidence
        }

        return result

    def _assess_complexity(
        self,
        user_input: str,
        image_description: Optional[str]
    ) -> InputComplexity:
        """
        Assess input complexity to determine processing strategy

        Simple: Has explicit theme, event type, guest count, location
        Complex: Narrative, implicit needs, requires inference
        """

        reasons = []
        score = 0
        max_score = 100

        text = user_input.lower()
        word_count = len(user_input.split())

        # Check for explicit structured data (40 points)
        if self._patterns['explicit_theme'].search(text):
            score += 10
            reasons.append("explicit_theme")

        if self._patterns['explicit_event'].search(text):
            score += 10
            reasons.append("explicit_event_type")

        if self._patterns['explicit_count'].search(text):
            score += 10
            reasons.append("explicit_guest_count")

        if self._patterns['explicit_age'].search(text):
            score += 5
            reasons.append("explicit_age")

        if self._patterns['explicit_location'].search(text):
            score += 5
            reasons.append("explicit_location")

        # Check for simplicity indicators (30 points)
        if word_count <= 15:
            score += 15
            reasons.append("concise_input")
        elif word_count <= 30:
            score += 10
            reasons.append("moderate_length")

        # Comma-separated or structured format (15 points)
        if text.count(',') >= 2:
            score += 10
            reasons.append("structured_format")

        if '\n' in user_input:
            score += 5
            reasons.append("multiline_structured")

        # Check for complexity indicators (negative score)
        complexity_keywords = [
            'loves', 'favorite', 'interested in',
            'elegant', 'casual', 'formal', 'sophisticated',
            'special', 'magical', 'memorable', 'unique',
            'grandmother', 'daughter', 'son',
            'we want', 'i need', 'looking for'
        ]

        complex_count = sum(1 for keyword in complexity_keywords if keyword in text)
        if complex_count > 0:
            score -= complex_count * 5
            reasons.append(f"complex_language_x{complex_count}")

        # Long narrative (negative score)
        if word_count > 50:
            score -= 20
            reasons.append("long_narrative")

        # Image input adds complexity (needs integration)
        if image_description:
            score -= 10
            reasons.append("has_image_description")

        # Calculate final assessment
        confidence = max(0, min(100, score)) / 100

        if score >= 50:
            level = "simple"
            use_llm = False
        elif score >= 20:
            level = "medium"
            use_llm = False  # Still try regex first
        else:
            level = "complex"
            use_llm = True

        return InputComplexity(
            level=level,
            reasons=reasons,
            use_llm=use_llm,
            confidence=confidence
        )

    async def _process_with_llm(
        self,
        user_input: str,
        image_description: Optional[str],
        vision_confidence: Optional[float] = None
    ) -> Dict[str, Any]:
        """Process input with LLM planning"""

        logger.info("Processing with LLM planner", vision_confidence=vision_confidence)

        # Generate structured plan
        plan = await self.llm_planner.generate_plan(user_input, image_description)

        # Convert to natural language for agent classification
        natural_language = plan.to_natural_language()

        return {
            "extracted_data": plan.to_dict(),
            "natural_language": natural_language,
            "confidence": plan.confidence,
            "processor": "llm",
            "needs_user_input": len(plan.missing_information) > 3,
            "missing_fields": plan.missing_information,
            "agent_instructions": plan.agent_instructions
        }

    async def _process_with_regex(
        self,
        user_input: str,
        image_description: Optional[str],
        vision_confidence: Optional[float] = None
    ) -> Dict[str, Any]:
        """Process input with fast regex extraction"""

        logger.info("Processing with regex extraction", vision_confidence=vision_confidence)

        # Use existing DataExtractionAgent
        result = await self.regex_agent.extract_data(user_input, image_description)

        # Extract natural language description from result
        natural_language = user_input
        if image_description:
            natural_language = f"{user_input}. Image shows: {image_description}"

        # Calculate enhanced confidence
        extracted_data = result.get("extracted_data", {})
        confidence_metrics = self.confidence_scorer.calculate_confidence(
            extracted_data=extracted_data,
            source_input=natural_language,
            extraction_method="regex",
            image_confidence=vision_confidence,
            validation_passed=True
        )

        logger.debug(
            "Regex extraction confidence",
            overall=confidence_metrics.overall_score,
            completeness=confidence_metrics.field_completeness,
            quality=confidence_metrics.field_quality,
            critical_present=confidence_metrics.critical_fields_present
        )

        return {
            "extracted_data": extracted_data,
            "natural_language": natural_language,
            "confidence": confidence_metrics.overall_score,
            "processor": "regex",
            "needs_user_input": not confidence_metrics.critical_fields_present or confidence_metrics.overall_score < 60,
            "missing_fields": confidence_metrics.missing_critical_fields,
            "suggestions": result.get("suggestions", []),
            "friendly_message": result.get("friendly_message", ""),
            "confidence_metrics": confidence_metrics  # Include detailed metrics
        }

    def is_simple_structured(self, text: str) -> bool:
        """
        Quick check if input is simple and structured

        Returns True if input has:
        - Explicit theme
        - Event type
        - Guest count or age
        - Concise (< 30 words)
        """

        if len(text.split()) > 30:
            return False

        text_lower = text.lower()

        has_theme = bool(self._patterns['explicit_theme'].search(text_lower))
        has_event = bool(self._patterns['explicit_event'].search(text_lower))
        has_count = bool(self._patterns['explicit_count'].search(text_lower))
        has_age = bool(self._patterns['explicit_age'].search(text_lower))

        # Need at least 3 of these
        indicators = sum([has_theme, has_event, has_count, has_age])

        return indicators >= 3


# Singleton instance
_router: Optional[SmartInputRouter] = None


def get_smart_router() -> SmartInputRouter:
    """Get global smart router instance"""
    global _router
    if _router is None:
        _router = SmartInputRouter()
    return _router


# Export
__all__ = ["SmartInputRouter", "InputComplexity", "get_smart_router"]
