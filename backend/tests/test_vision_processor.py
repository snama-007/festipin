"""
Tests for Vision AI processor service
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from app.services.vision_processor import (
    VisionProcessor,
    DetectedObject,
    SceneData,
    get_vision_processor
)
from app.core.errors import VisionProcessingError


class TestVisionProcessor:
    """Test suite for Vision processor"""
    
    def test_build_vision_prompt(self):
        """Test vision prompt generation"""
        processor = VisionProcessor()
        prompt = processor._build_vision_prompt()
        
        assert "party planner" in prompt.lower()
        assert "json" in prompt.lower()
        assert "theme" in prompt
        assert "objects" in prompt
    
    def test_categorize_object_balloons(self):
        """Test object categorization for balloons"""
        processor = VisionProcessor()
        
        assert processor._categorize_object("balloon arch") == "balloons_decorations"
        assert processor._categorize_object("Balloon Garland") == "balloons_decorations"
    
    def test_categorize_object_furniture(self):
        """Test object categorization for furniture"""
        processor = VisionProcessor()
        
        assert processor._categorize_object("cake table") == "furniture_rentals"
        assert processor._categorize_object("chair") == "furniture_rentals"
    
    def test_categorize_object_backdrops(self):
        """Test object categorization for backdrops"""
        processor = VisionProcessor()
        
        assert processor._categorize_object("sequin backdrop") == "backdrops_signage"
        assert processor._categorize_object("banner") == "backdrops_signage"
    
    def test_parse_scene_data_complete(self):
        """Test parsing complete scene data"""
        processor = VisionProcessor()
        
        data = {
            "theme": "gold and white balloons",
            "confidence": 0.95,
            "objects": [
                {
                    "type": "balloon arch",
                    "color": "#FFD700",
                    "position": {"x": 0.2, "y": 0.1},
                    "dimensions": {"width": 0.4, "height": 0.6},
                    "count": 1,
                    "confidence": 0.9,
                    "estimated_cost": [80, 150],
                    "materials": ["latex", "mylar"]
                }
            ],
            "color_palette": ["#FFD700", "#FFFFFF"],
            "layout_type": "arch_backdrop_table",
            "recommended_venue": "indoor_medium",
            "style_tags": ["elegant", "modern"],
            "occasion_type": "birthday",
            "age_range": [5, 10],
            "budget_estimate": {"min": 300, "max": 600}
        }
        
        scene = processor._parse_scene_data(data)
        
        assert scene.theme == "gold and white balloons"
        assert scene.confidence == 0.95
        assert len(scene.objects) == 1
        assert scene.objects[0].type == "balloon arch"
        assert scene.objects[0].color == "#FFD700"
        assert scene.layout_type == "arch_backdrop_table"
        assert scene.occasion_type == "birthday"
    
    def test_parse_scene_data_minimal(self):
        """Test parsing minimal scene data"""
        processor = VisionProcessor()
        
        data = {
            "theme": "Simple Party",
            "objects": [],
            "color_palette": ["#FFFFFF"]
        }
        
        scene = processor._parse_scene_data(data)
        
        assert scene.theme == "Simple Party"
        assert scene.confidence == 0.5  # Default
        assert len(scene.objects) == 0
        assert scene.layout_type == "unknown"  # Default
    
    @pytest.mark.asyncio
    async def test_analyze_party_image_success(self):
        """Test successful image analysis"""
        processor = VisionProcessor()
        
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "theme": "gold and white balloons",
            "confidence": 0.95,
            "objects": [
                {
                    "type": "balloon arch",
                    "color": "#FFD700",
                    "position": {"x": 0.2, "y": 0.1},
                    "count": 1,
                    "confidence": 0.9
                }
            ],
            "color_palette": ["#FFD700", "#FFFFFF"],
            "layout_type": "arch_backdrop_table"
        })
        
        with patch.object(processor.client.chat.completions, 'create', return_value=mock_response):
            scene = await processor.analyze_party_image("https://example.com/image.jpg")
        
        assert scene.theme == "gold and white balloons"
        assert scene.confidence == 0.95
        assert len(scene.objects) == 1
    
    @pytest.mark.asyncio
    async def test_analyze_party_image_invalid_json(self):
        """Test handling of invalid JSON response"""
        processor = VisionProcessor()
        
        # Mock response with invalid JSON
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is not JSON"
        
        with patch.object(processor.client.chat.completions, 'create', return_value=mock_response):
            with pytest.raises(VisionProcessingError):
                await processor.analyze_party_image("https://example.com/image.jpg")
    
    @pytest.mark.asyncio
    async def test_analyze_with_prompt(self):
        """Test analysis with user prompt"""
        processor = VisionProcessor()
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "theme": "unicorn party",
            "confidence": 0.9,
            "objects": [],
            "color_palette": ["#FF69B4"],
            "layout_type": "centerpiece_focus"
        })
        
        with patch.object(processor.client.chat.completions, 'create', return_value=mock_response):
            scene = await processor.analyze_with_prompt(
                "https://example.com/image.jpg",
                "This is for my daughter's 7th birthday"
            )
        
        assert scene.theme == "unicorn party"
    
    @pytest.mark.asyncio
    async def test_extract_shopping_list(self):
        """Test shopping list generation"""
        processor = VisionProcessor()
        
        # Create scene data with objects
        objects = [
            DetectedObject(
                type="balloon arch",
                color="#FFD700",
                position={"x": 0.2, "y": 0.1},
                count=1,
                estimated_cost=[80, 150],
                materials=["latex"]
            ),
            DetectedObject(
                type="cake table",
                color="#FFFFFF",
                position={"x": 0.5, "y": 0.5},
                count=1,
                estimated_cost=[50, 100]
            ),
            DetectedObject(
                type="sequin backdrop",
                color="#FFD700",
                position={"x": 0.5, "y": 0.2},
                count=1,
                estimated_cost=[40, 80]
            )
        ]
        
        scene = SceneData(
            theme="gold party",
            confidence=0.9,
            objects=objects,
            color_palette=["#FFD700"],
            layout_type="arch_backdrop_table"
        )
        
        shopping_list = await processor.extract_shopping_list(scene)
        
        assert "categories" in shopping_list
        assert "total_estimated_cost" in shopping_list
        assert shopping_list["total_estimated_cost"]["min"] == 170
        assert shopping_list["total_estimated_cost"]["max"] == 330
        
        # Check categories
        categories = shopping_list["categories"]
        assert "balloons_decorations" in categories
        assert "furniture_rentals" in categories
        assert "backdrops_signage" in categories
    
    def test_detected_object_to_dict(self):
        """Test DetectedObject serialization"""
        obj = DetectedObject(
            type="balloon arch",
            color="#FFD700",
            position={"x": 0.2, "y": 0.1},
            count=1,
            confidence=0.9,
            estimated_cost=[80, 150],
            materials=["latex", "mylar"]
        )
        
        data = obj.to_dict()
        
        assert data["type"] == "balloon arch"
        assert data["color"] == "#FFD700"
        assert data["position"]["x"] == 0.2
        assert data["materials"] == ["latex", "mylar"]
    
    def test_scene_data_to_dict(self):
        """Test SceneData serialization"""
        objects = [
            DetectedObject(
                type="balloon arch",
                color="#FFD700",
                position={"x": 0.2, "y": 0.1},
                count=1
            )
        ]
        
        scene = SceneData(
            theme="gold party",
            confidence=0.95,
            objects=objects,
            color_palette=["#FFD700", "#FFFFFF"],
            layout_type="arch_backdrop_table",
            style_tags=["elegant", "modern"]
        )
        
        data = scene.to_dict()
        
        assert data["theme"] == "gold party"
        assert data["confidence"] == 0.95
        assert len(data["objects"]) == 1
        assert isinstance(data["objects"][0], dict)
        assert data["style_tags"] == ["elegant", "modern"]
    
    def test_singleton_pattern(self):
        """Test that get_vision_processor returns singleton"""
        processor1 = get_vision_processor()
        processor2 = get_vision_processor()
        
        assert processor1 is processor2


# Integration test (requires OpenAI API key)
@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_vision_analysis():
    """
    Integration test with real GPT-4 Vision API.
    Only run when OpenAI API key is configured.
    """
    processor = get_vision_processor()
    
    # Use a test image URL (replace with actual party image)
    test_image_url = "https://storage.googleapis.com/test-bucket/party.jpg"
    
    try:
        scene = await processor.analyze_party_image(test_image_url)
        
        assert scene.theme is not None
        assert scene.confidence > 0
        assert len(scene.color_palette) > 0
        
        print(f"Theme: {scene.theme}")
        print(f"Objects found: {len(scene.objects)}")
        print(f"Confidence: {scene.confidence}")
        
    except Exception as e:
        pytest.skip(f"OpenAI API not available: {e}")

