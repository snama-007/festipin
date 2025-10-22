"""
Enhanced Confidence Scoring System

Provides sophisticated confidence metrics beyond simple field counting.
Considers data quality, completeness, validation, and source clarity.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from app.core.logging import logger


@dataclass
class ConfidenceMetrics:
    """Detailed confidence breakdown"""
    overall_score: float  # 0-100
    field_completeness: float  # 0-100
    field_quality: float  # 0-100
    data_consistency: float  # 0-100
    source_clarity: float  # 0-100
    validation_score: float  # 0-100
    critical_fields_present: bool
    missing_critical_fields: List[str]
    quality_issues: List[str]
    recommendations: List[str]


class ConfidenceScorer:
    """
    Enhanced confidence scoring system with quality metrics

    Provides multi-dimensional confidence assessment:
    - Field completeness (how many fields extracted)
    - Field quality (specificity and usefulness of data)
    - Data consistency (cross-field validation)
    - Source clarity (how clear was the input)
    - Validation score (hallucination prevention)
    """

    # Critical fields required for party planning
    CRITICAL_FIELDS = [
        "event_type",
        "theme",
        "guest_count",
        "honoree_age"
    ]

    # Important but optional fields
    IMPORTANT_FIELDS = [
        "location",
        "date",
        "budget",
        "dietary_restrictions",
        "special_requirements"
    ]

    # Field quality weights
    FIELD_WEIGHTS = {
        "event_type": 20,
        "theme": 20,
        "honoree_age": 12,
        "guest_count": 12,
        "location": 10,
        "date": 8,
        "budget": 8,
        "dietary_restrictions": 5,
        "special_requirements": 5
    }

    def calculate_confidence(
        self,
        extracted_data: Dict[str, Any],
        source_input: str,
        extraction_method: str = "unknown",
        image_confidence: Optional[float] = None,
        validation_passed: bool = True
    ) -> ConfidenceMetrics:
        """
        Calculate comprehensive confidence metrics

        Args:
            extracted_data: Extracted structured data
            source_input: Original user input
            extraction_method: "regex", "llm", or "hybrid"
            image_confidence: Vision analysis confidence if applicable
            validation_passed: Whether hallucination validation passed

        Returns:
            ConfidenceMetrics with detailed breakdown
        """

        logger.debug(
            "Calculating enhanced confidence",
            method=extraction_method,
            fields_count=len(extracted_data),
            has_vision=image_confidence is not None
        )

        # 1. Field completeness (30% of total score)
        completeness = self._calculate_field_completeness(extracted_data)

        # 2. Field quality (25% of total score)
        quality = self._calculate_field_quality(extracted_data)

        # 3. Data consistency (20% of total score)
        consistency = self._calculate_data_consistency(extracted_data)

        # 4. Source clarity (15% of total score)
        source_clarity = self._calculate_source_clarity(
            source_input,
            extracted_data,
            extraction_method
        )

        # 5. Validation score (10% of total score)
        validation = self._calculate_validation_score(
            extracted_data,
            validation_passed,
            image_confidence
        )

        # Calculate weighted overall score
        overall = (
            completeness * 0.30 +
            quality * 0.25 +
            consistency * 0.20 +
            source_clarity * 0.15 +
            validation * 0.10
        )

        # Boost from high-quality vision analysis
        if image_confidence and image_confidence > 0.9:
            overall = min(100, overall + 5)  # +5 bonus for high-confidence vision

        # Check critical fields
        missing_critical = [
            field for field in self.CRITICAL_FIELDS
            if not self._has_meaningful_value(extracted_data.get(field))
        ]

        critical_present = len(missing_critical) == 0

        # Identify quality issues
        quality_issues = self._identify_quality_issues(
            extracted_data,
            completeness,
            quality,
            consistency
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            missing_critical,
            quality_issues,
            extraction_method
        )

        logger.info(
            "Confidence calculated",
            overall=round(overall, 2),
            completeness=round(completeness, 2),
            quality=round(quality, 2),
            consistency=round(consistency, 2),
            critical_present=critical_present
        )

        return ConfidenceMetrics(
            overall_score=round(overall, 2),
            field_completeness=round(completeness, 2),
            field_quality=round(quality, 2),
            data_consistency=round(consistency, 2),
            source_clarity=round(source_clarity, 2),
            validation_score=round(validation, 2),
            critical_fields_present=critical_present,
            missing_critical_fields=missing_critical,
            quality_issues=quality_issues,
            recommendations=recommendations
        )

    def _calculate_field_completeness(self, data: Dict[str, Any]) -> float:
        """
        Calculate field completeness score

        Weighted by field importance:
        - Critical fields: 40% of score
        - Important fields: 40% of score
        - Other fields: 20% of score
        """

        critical_score = 0.0
        critical_max = len(self.CRITICAL_FIELDS)
        for field in self.CRITICAL_FIELDS:
            if self._has_meaningful_value(data.get(field)):
                critical_score += 1

        important_score = 0.0
        important_max = len(self.IMPORTANT_FIELDS)
        for field in self.IMPORTANT_FIELDS:
            if self._has_meaningful_value(data.get(field)):
                important_score += 1

        # Check for additional fields (bonus)
        additional_score = 0.0
        additional_fields = [
            k for k in data.keys()
            if k not in self.CRITICAL_FIELDS and k not in self.IMPORTANT_FIELDS
        ]
        additional_score = min(5, len(additional_fields))  # Max 5 bonus fields

        # Calculate weighted completeness
        completeness = (
            (critical_score / critical_max) * 40 +
            (important_score / important_max) * 40 +
            (additional_score / 5) * 20
        )

        return completeness

    def _calculate_field_quality(self, data: Dict[str, Any]) -> float:
        """
        Calculate field quality score based on specificity and usefulness

        Quality factors:
        - Specific values > vague values
        - Structured data > plain text
        - Numeric precision
        - Detailed requirements
        """

        quality_score = 0.0
        max_score = 100.0

        # Event type quality (20 points)
        event_type = data.get("event_type")
        if event_type:
            if isinstance(event_type, str) and len(event_type) > 3:
                quality_score += 20
            else:
                quality_score += 10  # Vague or short

        # Theme quality (20 points)
        theme = data.get("theme")
        if theme:
            if isinstance(theme, str) and len(theme) > 5:
                quality_score += 20
            else:
                quality_score += 10

        # Age specificity (15 points)
        age = data.get("honoree_age")
        if age is not None:
            if isinstance(age, int) and 1 <= age <= 120:
                quality_score += 15  # Specific age
            elif isinstance(age, str):
                quality_score += 8  # Age range or description

        # Guest count specificity (15 points)
        guest_count = data.get("guest_count")
        if guest_count:
            if isinstance(guest_count, int) and guest_count > 0:
                quality_score += 15  # Exact count
            elif isinstance(guest_count, dict):
                quality_score += 12  # Breakdown (adults/kids)
            else:
                quality_score += 7  # Vague estimate

        # Location detail (10 points)
        location = data.get("location")
        if location:
            if isinstance(location, dict) and location.get("address"):
                quality_score += 10  # Specific address
            elif isinstance(location, str):
                quality_score += 5  # General description

        # Budget specificity (10 points)
        budget = data.get("budget")
        if budget:
            if isinstance(budget, (int, float)) and budget > 0:
                quality_score += 10  # Specific amount
            elif isinstance(budget, dict) and budget.get("amount"):
                quality_score += 8  # Budget object
            else:
                quality_score += 4  # Vague budget

        # Requirements detail (10 points)
        requirements = data.get("explicit_requirements") or data.get("special_requirements")
        if requirements:
            if isinstance(requirements, dict) and len(requirements) > 2:
                quality_score += 10  # Detailed requirements
            elif isinstance(requirements, dict):
                quality_score += 6  # Some requirements
            else:
                quality_score += 3  # Vague

        return (quality_score / max_score) * 100

    def _calculate_data_consistency(self, data: Dict[str, Any]) -> float:
        """
        Calculate data consistency score

        Checks:
        - Age matches event type
        - Guest count reasonable for event
        - Theme appropriate for age
        - Budget aligns with guest count
        """

        consistency_score = 100.0  # Start at perfect, deduct for issues
        issues = []

        event_type = data.get("event_type", "").lower()
        age = data.get("honoree_age")
        guest_count = data.get("guest_count")
        theme = data.get("theme", "").lower()

        # Check age consistency with event type
        if age and event_type:
            if "birthday" in event_type and (age < 1 or age > 120):
                consistency_score -= 15
                issues.append("Age out of range for birthday")

            if "baby shower" in event_type and age and age > 0:
                consistency_score -= 10
                issues.append("Age shouldn't be specified for baby shower")

        # Check theme consistency with age
        if theme and age:
            kids_themes = ["unicorn", "dinosaur", "superhero", "princess", "paw patrol"]
            adult_themes = ["elegant", "sophisticated", "vintage", "rustic"]

            if any(kt in theme for kt in kids_themes) and age > 16:
                consistency_score -= 10
                issues.append("Kids theme for adult age")

            if any(at in theme for at in adult_themes) and age < 12:
                consistency_score -= 10
                issues.append("Adult theme for child age")

        # Check guest count reasonableness
        if guest_count:
            count = guest_count if isinstance(guest_count, int) else guest_count.get("total", 0)
            if count > 1000:
                consistency_score -= 10
                issues.append("Very high guest count")
            elif count < 1:
                consistency_score -= 20
                issues.append("Invalid guest count")

        # Check budget vs guest count
        budget = data.get("budget")
        if budget and guest_count:
            amount = budget if isinstance(budget, (int, float)) else budget.get("amount", 0)
            count = guest_count if isinstance(guest_count, int) else guest_count.get("total", 0)

            if amount > 0 and count > 0:
                per_person = amount / count
                if per_person < 5:
                    consistency_score -= 10
                    issues.append("Budget very low for guest count")
                elif per_person > 500:
                    consistency_score -= 5
                    issues.append("Budget very high for guest count")

        if issues:
            logger.debug("Data consistency issues found", issues=issues)

        return max(0, consistency_score)

    def _calculate_source_clarity(
        self,
        source: str,
        extracted: Dict[str, Any],
        method: str
    ) -> float:
        """
        Calculate source clarity score

        Factors:
        - Input length and structure
        - Explicit vs implicit information
        - Extraction method success
        """

        clarity_score = 0.0

        # Length check (30 points)
        word_count = len(source.split())
        if 10 <= word_count <= 50:
            clarity_score += 30  # Optimal length
        elif 5 <= word_count < 10 or 50 < word_count <= 100:
            clarity_score += 20  # Acceptable
        elif word_count < 5:
            clarity_score += 10  # Too short
        else:
            clarity_score += 15  # Too long

        # Structure check (30 points)
        has_commas = "," in source
        has_keywords = any(kw in source.lower() for kw in [
            "theme", "guests", "party", "birthday", "venue", "location"
        ])

        if has_commas and has_keywords:
            clarity_score += 30  # Well-structured
        elif has_keywords:
            clarity_score += 20  # Some structure
        else:
            clarity_score += 10  # Narrative

        # Explicit information (40 points)
        explicit_count = 0
        if any(str(num) in source for num in range(1, 200)):
            explicit_count += 1  # Has numbers
        if any(theme in source.lower() for theme in [
            "unicorn", "superhero", "princess", "jungle", "space"
        ]):
            explicit_count += 1  # Has explicit theme
        if any(event in source.lower() for event in [
            "birthday", "wedding", "anniversary", "shower"
        ]):
            explicit_count += 1  # Has explicit event type

        clarity_score += (explicit_count / 3) * 40

        return clarity_score

    def _calculate_validation_score(
        self,
        data: Dict[str, Any],
        validation_passed: bool,
        vision_confidence: Optional[float]
    ) -> float:
        """
        Calculate validation score

        Factors:
        - Hallucination prevention validation
        - Vision confidence (if applicable)
        - Cross-reference checks
        """

        validation_score = 0.0

        # Base validation (60 points)
        if validation_passed:
            validation_score += 60
        else:
            validation_score += 20  # Partial credit

        # Vision confidence boost (40 points)
        if vision_confidence is not None:
            validation_score += vision_confidence * 40
        else:
            # No vision, assume reasonable confidence
            validation_score += 30

        return validation_score

    def _has_meaningful_value(self, value: Any) -> bool:
        """Check if a value is meaningful (not None, empty, or placeholder)"""

        if value is None:
            return False

        if isinstance(value, str):
            if not value or value.strip() == "":
                return False
            # Check for placeholder text
            placeholders = ["to be determined", "tbd", "n/a", "unknown", "user to provide"]
            if value.lower() in placeholders:
                return False

        if isinstance(value, dict):
            return len(value) > 0 and any(self._has_meaningful_value(v) for v in value.values())

        if isinstance(value, list):
            return len(value) > 0

        return True

    def _identify_quality_issues(
        self,
        data: Dict[str, Any],
        completeness: float,
        quality: float,
        consistency: float
    ) -> List[str]:
        """Identify specific quality issues"""

        issues = []

        if completeness < 40:
            issues.append("Low field completeness - many fields missing")

        if quality < 50:
            issues.append("Low field quality - data is vague or imprecise")

        if consistency < 80:
            issues.append("Data consistency issues detected")

        # Check for specific missing critical fields
        for field in self.CRITICAL_FIELDS:
            if not self._has_meaningful_value(data.get(field)):
                issues.append(f"Missing critical field: {field}")

        return issues

    def _generate_recommendations(
        self,
        missing_critical: List[str],
        quality_issues: List[str],
        extraction_method: str
    ) -> List[str]:
        """Generate recommendations for improving confidence"""

        recommendations = []

        if missing_critical:
            recommendations.append(
                f"Request user to provide: {', '.join(missing_critical)}"
            )

        if "Low field quality" in quality_issues:
            recommendations.append(
                "Ask user for more specific details"
            )

        if extraction_method == "regex" and len(quality_issues) > 2:
            recommendations.append(
                "Consider using LLM for better understanding"
            )

        if not recommendations:
            recommendations.append("Extraction looks good, proceed with agents")

        return recommendations


# Singleton instance
_confidence_scorer: Optional[ConfidenceScorer] = None


def get_confidence_scorer() -> ConfidenceScorer:
    """Get global confidence scorer instance"""
    global _confidence_scorer
    if _confidence_scorer is None:
        _confidence_scorer = ConfidenceScorer()
    return _confidence_scorer


# Export
__all__ = ["ConfidenceScorer", "ConfidenceMetrics", "get_confidence_scorer"]
