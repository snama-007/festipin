"""
Vision AI Processor Service

Analyzes party images using GPT-4 Vision API to extract:
- Theme and style
- Objects and decorations
- Color palette
- Layout and arrangement
- Venue recommendations
"""

import json
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

import google.generativeai as genai
import httpx

from app.core.config import settings
from app.core.logging import logger
from app.core.errors import VisionProcessingError


@dataclass
class DetectedObject:
    """Represents a detected object in the party scene"""
    type: str
    color: str
    position: Dict[str, float]  # {x: 0.0-1.0, y: 0.0-1.0}
    dimensions: Optional[Dict[str, float]] = None  # {width, height}
    count: int = 1
    confidence: float = 0.0
    estimated_cost: Optional[List[int]] = None  # [min, max] in USD
    materials: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class SceneData:
    """Complete scene analysis data"""
    theme: str
    confidence: float
    objects: List[DetectedObject]
    color_palette: List[str]
    layout_type: str
    recommended_venue: Optional[str] = None
    style_tags: Optional[List[str]] = None
    occasion_type: Optional[str] = None
    age_range: Optional[List[int]] = None
    budget_estimate: Optional[Dict[str, int]] = None  # {min, max}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert DetectedObject instances to dicts
        data['objects'] = [obj.to_dict() if hasattr(obj, 'to_dict') else obj for obj in self.objects]
        return data


class VisionProcessor:
    """
    GPT-4 Vision API processor for party image analysis.
    
    Features:
    - Theme detection
    - Object identification
    - Color palette extraction
    - Layout analysis
    - Venue recommendations
    """
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        logger.info("Vision processor initialized", model=settings.GEMINI_MODEL)
    
    async def _get_image_base64(self, image_url: str) -> str:
        """
        Convert image to base64. Handles both local and remote URLs.
        For localhost URLs, fetches the image and converts to base64.
        For data URLs, returns as-is.
        """
        # Check if it's already a data URL
        if image_url.startswith("data:"):
            logger.info("Image is already base64 data URL")
            return image_url
        
        # Check if it's a localhost URL
        if "localhost" in image_url or "127.0.0.1" in image_url:
            logger.info("Converting localhost image to base64", url=image_url)
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_url)
                    response.raise_for_status()
                    
                    # Convert to base64
                    image_data = response.content
                    base64_image = base64.b64encode(image_data).decode('utf-8')
                    
                    # Determine image format from content-type
                    content_type = response.headers.get('content-type', 'image/jpeg')
                    format_prefix = f"data:{content_type};base64,"
                    
                    logger.info("Image converted to base64", size_kb=len(image_data) / 1024)
                    return format_prefix + base64_image
                    
            except Exception as e:
                logger.error("Failed to fetch local image", error=str(e), url=image_url)
                raise VisionProcessingError(f"Failed to fetch local image: {str(e)}")
        
        # For remote URLs, return as-is (OpenAI can fetch them)
        return image_url
    
    def _build_vision_prompt(self) -> str:
        """
        Build the system prompt for vision analysis.
        
        Returns optimized prompt for party scene analysis.
        """
        return """Analyze this party/event image and return a JSON object with the following structure. Do not include any text before or after the JSON.

{
  "theme": "descriptive theme name",
  "confidence": 0.95,
  "objects": [
    {
      "type": "object name",
      "color": "primary color (hex code or name)",
      "position": {"x": 0.2, "y": 0.1},
      "dimensions": {"width": 0.4, "height": 0.6},
      "count": 1,
      "confidence": 0.9,
      "estimated_cost": [80, 150],
      "materials": ["material1", "material2"]
    }
  ],
  "color_palette": ["#FFD700", "#FFFFFF", "#F5F5DC"],
  "layout_type": "arch_backdrop_table",
  "recommended_venue": "indoor_medium",
  "style_tags": ["elegant", "modern", "minimalist"],
  "occasion_type": "birthday",
  "age_range": [5, 10],
  "budget_estimate": {"min": 300, "max": 600}
}

Requirements:
- Return ONLY valid JSON, no markdown formatting
- Use hex codes for colors when possible
- Position coordinates are relative (0.0 to 1.0)
- Estimate realistic costs in USD
- Layout types: arch_backdrop_table, centerpiece_focus, wall_display, full_room, outdoor_setup
- Venue types: indoor_small, indoor_medium, indoor_large, outdoor_backyard, outdoor_venue, home"""
    
    async def analyze_party_image(
        self,
        image_url: str,
        additional_context: Optional[str] = None
    ) -> SceneData:
        """
        Analyze a party image using GPT-4 Vision.
        
        Args:
            image_url: Public URL of the image
            additional_context: Optional user-provided context
            
        Returns:
            SceneData object with analysis results
            
        Raises:
            VisionProcessingError: If analysis fails
        """
        logger.info("Starting vision analysis", image_url=image_url)
        
        try:
            # Convert local URLs to base64
            image_data = await self._get_image_base64(image_url)
            
            # Prepare content for Gemini
            prompt = f"{self._build_vision_prompt()}\n\n{additional_context or 'Analyze this party setup image in detail.'}"
            
            # Call Gemini API
            try:
                response = self.model.generate_content([
                    prompt,
                    {
                        "mime_type": "image/jpeg" if "jpeg" in image_data else "image/png",
                        "data": base64.b64decode(image_data.split(",")[1]) if "," in image_data else base64.b64decode(image_data)
                    }
                ])
                
                # Extract response
                content = response.text
                
                # Check if response is empty or None
                if not content or content.strip() == "":
                    logger.error("Gemini returned empty response", image_url=image_url)
                    raise VisionProcessingError("Gemini API returned empty response")
                    
            except Exception as e:
                logger.error("Gemini API call failed", error=str(e), image_url=image_url)
                raise VisionProcessingError(f"Gemini API call failed: {str(e)}")
            
            logger.debug("Raw vision response", content=content[:200])
            
            # Clean the response - remove any markdown formatting
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error("Failed to parse Gemini response as JSON", error=str(e), content=content[:500])
                # Try to extract JSON from the response if it's wrapped in text
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        data = json.loads(json_match.group())
                        logger.info("Successfully extracted JSON from wrapped response")
                    except json.JSONDecodeError:
                        raise VisionProcessingError(f"Gemini returned invalid JSON: {str(e)}")
                else:
                    raise VisionProcessingError(f"Gemini returned invalid JSON: {str(e)}")
            
            # Convert to SceneData
            scene_data = self._parse_scene_data(data)
            
            logger.info(
                "Vision analysis successful",
                theme=scene_data.theme,
                object_count=len(scene_data.objects),
                confidence=scene_data.confidence
            )
            
            return scene_data
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse vision response as JSON", error=str(e))
            # Create a fallback response if JSON parsing fails
            logger.warning("Creating fallback response due to JSON parsing error")
            fallback_data = {
                "theme": "Party Setup",
                "confidence": 0.5,
                "objects": [],
                "color_palette": ["#FFFFFF", "#F0F0F0"],
                "layout_type": "unknown",
                "recommended_venue": "indoor_medium",
                "style_tags": ["party"],
                "occasion_type": "party",
                "age_range": [5, 50],
                "budget_estimate": {"min": 100, "max": 500}
            }
            scene_data = self._parse_scene_data(fallback_data)
            logger.info("Using fallback scene data due to parsing error")
            return scene_data
        except Exception as e:
            logger.error("Vision processing failed", error=str(e), image_url=image_url)
            raise VisionProcessingError(
                f"Vision analysis failed: {str(e)}",
                context={"image_url": image_url}
            )
    
    def _parse_scene_data(self, data: Dict[str, Any]) -> SceneData:
        """
        Parse raw API response into SceneData object.
        
        Args:
            data: Parsed JSON from API
            
        Returns:
            SceneData instance
        """
        # Parse objects
        objects = []
        for obj_data in data.get('objects', []):
            obj = DetectedObject(
                type=obj_data.get('type', 'unknown'),
                color=obj_data.get('color', '#FFFFFF'),
                position=obj_data.get('position', {'x': 0.5, 'y': 0.5}),
                dimensions=obj_data.get('dimensions'),
                count=obj_data.get('count', 1),
                confidence=obj_data.get('confidence', 0.0),
                estimated_cost=obj_data.get('estimated_cost'),
                materials=obj_data.get('materials')
            )
            objects.append(obj)
        
        # Create SceneData
        scene = SceneData(
            theme=data.get('theme', 'Party Setup'),
            confidence=data.get('confidence', 0.5),
            objects=objects,
            color_palette=data.get('color_palette', ['#FFFFFF']),
            layout_type=data.get('layout_type', 'unknown'),
            recommended_venue=data.get('recommended_venue'),
            style_tags=data.get('style_tags', []),
            occasion_type=data.get('occasion_type'),
            age_range=data.get('age_range'),
            budget_estimate=data.get('budget_estimate')
        )
        
        return scene
    
    async def analyze_with_prompt(
        self,
        image_url: str,
        user_prompt: str
    ) -> SceneData:
        """
        Analyze image with user-provided prompt for better context.
        
        Args:
            image_url: Public URL of the image
            user_prompt: User's description or requirements
            
        Returns:
            SceneData with analysis
        """
        enhanced_prompt = f"""User context: {user_prompt}

Based on the image and user's requirements, provide a detailed party plan analysis."""
        
        return await self.analyze_party_image(image_url, enhanced_prompt)
    
    async def extract_shopping_list(self, scene_data: SceneData) -> Dict[str, Any]:
        """
        Generate shopping list from scene analysis.
        
        Args:
            scene_data: Analyzed scene data
            
        Returns:
            Structured shopping list with categories
        """
        shopping_list = {
            "categories": {},
            "total_estimated_cost": {
                "min": 0,
                "max": 0
            }
        }
        
        # Group objects by type
        for obj in scene_data.objects:
            category = self._categorize_object(obj.type)
            
            if category not in shopping_list["categories"]:
                shopping_list["categories"][category] = []
            
            item = {
                "name": obj.type,
                "quantity": obj.count,
                "color": obj.color,
                "estimated_cost": obj.estimated_cost,
                "materials": obj.materials
            }
            
            shopping_list["categories"][category].append(item)
            
            # Add to total cost
            if obj.estimated_cost:
                shopping_list["total_estimated_cost"]["min"] += obj.estimated_cost[0]
                shopping_list["total_estimated_cost"]["max"] += obj.estimated_cost[1]
        
        return shopping_list
    
    def _categorize_object(self, obj_type: str) -> str:
        """Categorize object into shopping categories"""
        obj_lower = obj_type.lower()
        
        if any(word in obj_lower for word in ['balloon', 'arch', 'garland']):
            return 'balloons_decorations'
        elif any(word in obj_lower for word in ['table', 'chair', 'furniture']):
            return 'furniture_rentals'
        elif any(word in obj_lower for word in ['backdrop', 'curtain', 'banner']):
            return 'backdrops_signage'
        elif any(word in obj_lower for word in ['cake', 'food', 'dessert']):
            return 'food_beverages'
        elif any(word in obj_lower for word in ['plate', 'cup', 'utensil', 'napkin']):
            return 'tableware'
        elif any(word in obj_lower for word in ['flower', 'plant', 'greenery']):
            return 'florals'
        else:
            return 'miscellaneous'


# Singleton instance
_vision_processor: Optional[VisionProcessor] = None


def get_vision_processor() -> VisionProcessor:
    """Get or create VisionProcessor singleton"""
    global _vision_processor
    if _vision_processor is None:
        _vision_processor = VisionProcessor()
    return _vision_processor

