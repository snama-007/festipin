"""
Vision to Text Converter

Converts Vision AI SceneData into natural language descriptions
for agent classification and understanding.
"""

from typing import List, Optional
from app.services.vision_processor import SceneData, DetectedObject
from app.core.logging import logger


class VisionToTextConverter:
    """
    Converts Vision AI analysis results into natural language descriptions

    This allows vision insights to be integrated with text-based agent classification
    """

    @staticmethod
    def scene_to_text(scene: SceneData, verbose: bool = True) -> str:
        """
        Convert SceneData to natural language description

        Args:
            scene: SceneData from vision analysis
            verbose: If True, include detailed object descriptions

        Returns:
            Natural language description of the party scene
        """

        parts = []

        # 1. Theme and occasion
        if scene.theme:
            parts.append(f"{scene.theme} theme party")

        if scene.occasion_type:
            if scene.occasion_type != scene.theme:
                parts.append(f"for {scene.occasion_type}")

        # 2. Age information
        if scene.age_range and len(scene.age_range) == 2:
            if scene.age_range[0] == scene.age_range[1]:
                parts.append(f"for {scene.age_range[0]} year old")
            else:
                parts.append(f"for ages {scene.age_range[0]}-{scene.age_range[1]}")

        # 3. Style tags
        if scene.style_tags:
            style_desc = ", ".join(scene.style_tags[:3])
            parts.append(f"with {style_desc} style")

        # 4. Objects and decorations
        if scene.objects and verbose:
            object_desc = VisionToTextConverter._describe_objects(scene.objects)
            if object_desc:
                parts.append(f"featuring {object_desc}")

        # 5. Color palette
        if scene.color_palette:
            colors = ", ".join(scene.color_palette[:4])
            parts.append(f"color scheme: {colors}")

        # 6. Venue suggestion
        if scene.recommended_venue:
            venue_desc = scene.recommended_venue.replace("_", " ")
            parts.append(f"suitable for {venue_desc} venue")

        # 7. Layout
        if scene.layout_type:
            layout_desc = scene.layout_type.replace("_", " ")
            parts.append(f"setup: {layout_desc}")

        # 8. Budget estimate
        if scene.budget_estimate:
            parts.append(
                f"estimated budget ${scene.budget_estimate['min']}-${scene.budget_estimate['max']}"
            )

        description = ". ".join(parts)

        logger.info(
            "Scene converted to text",
            theme=scene.theme,
            description_length=len(description)
        )

        return description

    @staticmethod
    def _describe_objects(objects: List[DetectedObject]) -> str:
        """
        Create a concise description of detected objects

        Groups objects by type and creates natural language summary
        """

        if not objects:
            return ""

        # Group objects by type
        object_groups = {}
        for obj in objects:
            obj_type = obj.type
            if obj_type not in object_groups:
                object_groups[obj_type] = {
                    "count": 0,
                    "colors": set(),
                    "total_confidence": 0.0
                }

            object_groups[obj_type]["count"] += obj.count
            if obj.color:
                object_groups[obj_type]["colors"].add(obj.color)
            object_groups[obj_type]["total_confidence"] += obj.confidence

        # Sort by count (most prominent first)
        sorted_objects = sorted(
            object_groups.items(),
            key=lambda x: (x[1]["count"], x[1]["total_confidence"]),
            reverse=True
        )

        # Create descriptions for top 5 object types
        descriptions = []
        for obj_type, data in sorted_objects[:5]:
            count = data["count"]
            colors = list(data["colors"])

            if count > 1:
                desc = f"{count} {obj_type}s"
            else:
                desc = obj_type

            # Add color if available
            if colors:
                color_str = " and ".join(colors[:2])
                desc = f"{color_str} {desc}"

            descriptions.append(desc)

        return ", ".join(descriptions)

    @staticmethod
    def scene_to_tags(scene: SceneData) -> List[str]:
        """
        Extract tags from scene for agent routing

        Returns list of tags like: ["theme", "cake", "decorations", "venue"]
        """

        tags = set()

        # Theme always triggers theme agent
        if scene.theme:
            tags.add("theme")

        # Check objects for cake-related items
        if scene.objects:
            cake_keywords = ["cake", "cupcake", "dessert", "bakery"]
            for obj in scene.objects:
                if any(keyword in obj.type.lower() for keyword in cake_keywords):
                    tags.add("cake")
                    break

        # Decorations
        if scene.objects:
            decoration_keywords = ["balloon", "streamer", "banner", "garland", "decoration"]
            for obj in scene.objects:
                if any(keyword in obj.type.lower() for keyword in decoration_keywords):
                    tags.add("decorations")
                    break

        # Venue type
        if scene.recommended_venue:
            tags.add("venue")

        # Food/catering
        if scene.objects:
            food_keywords = ["food", "plate", "table setting", "catering"]
            for obj in scene.objects:
                if any(keyword in obj.type.lower() for keyword in food_keywords):
                    tags.add("catering")
                    break

        return list(tags)

    @staticmethod
    def scene_to_agent_context(scene: SceneData) -> dict:
        """
        Extract structured context for agents from scene data

        Returns dict with agent-specific context
        """

        context = {}

        # Theme Agent context
        if scene.theme or scene.color_palette:
            context["theme_agent"] = {
                "detected_theme": scene.theme,
                "color_palette": scene.color_palette,
                "style_tags": scene.style_tags
            }

        # Venue Agent context
        if scene.recommended_venue or scene.layout_type:
            context["venue_agent"] = {
                "recommended_venue_type": scene.recommended_venue,
                "layout_type": scene.layout_type,
                "space_requirements": VisionToTextConverter._infer_space_requirements(scene)
            }

        # Cake Agent context
        if scene.theme:
            context["cake_agent"] = {
                "theme": scene.theme,
                "suggested_colors": scene.color_palette[:3] if scene.color_palette else [],
                "style": scene.style_tags[0] if scene.style_tags else None
            }

        # Budget Agent context
        if scene.budget_estimate:
            context["budget_agent"] = {
                "visual_budget_estimate": scene.budget_estimate,
                "complexity_level": VisionToTextConverter._estimate_complexity(scene)
            }

        return context

    @staticmethod
    def _infer_space_requirements(scene: SceneData) -> dict:
        """Infer space requirements from scene analysis"""

        requirements = {
            "indoor_outdoor": "indoor",  # Default
            "estimated_capacity": None
        }

        # Infer indoor/outdoor from venue type
        if scene.recommended_venue:
            if "outdoor" in scene.recommended_venue or "garden" in scene.recommended_venue:
                requirements["indoor_outdoor"] = "outdoor"
            elif "park" in scene.recommended_venue or "beach" in scene.recommended_venue:
                requirements["indoor_outdoor"] = "outdoor"

        # Infer capacity from layout
        if scene.layout_type:
            if "large" in scene.layout_type:
                requirements["estimated_capacity"] = 100
            elif "medium" in scene.layout_type:
                requirements["estimated_capacity"] = 50
            else:
                requirements["estimated_capacity"] = 30

        return requirements

    @staticmethod
    def _estimate_complexity(scene: SceneData) -> str:
        """Estimate complexity of party setup from scene"""

        complexity_score = 0

        # Object count indicates complexity
        if scene.objects:
            complexity_score += min(len(scene.objects), 10)

        # Multiple colors indicate complexity
        if scene.color_palette:
            complexity_score += min(len(scene.color_palette), 5)

        # Style tags
        if scene.style_tags:
            elaborate_styles = ["elaborate", "elegant", "formal", "luxurious"]
            if any(style in scene.style_tags for style in elaborate_styles):
                complexity_score += 10

        if complexity_score >= 15:
            return "high"
        elif complexity_score >= 8:
            return "medium"
        else:
            return "low"


# Singleton instance
_converter: Optional[VisionToTextConverter] = None


def get_vision_converter() -> VisionToTextConverter:
    """Get global vision converter instance"""
    global _converter
    if _converter is None:
        _converter = VisionToTextConverter()
    return _converter


# Export
__all__ = [
    "VisionToTextConverter",
    "get_vision_converter"
]
