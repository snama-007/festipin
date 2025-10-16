"""
Motif Image Generation Models

Pydantic models for image generation requests and responses
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class GenerationType(str, Enum):
    """Types of image generation"""
    TEXT_TO_IMAGE = "text_to_image"
    IMAGE_TO_IMAGE = "image_to_image"
    INSPIRATION_BASED = "inspiration_based"

class GenerationStatus(str, Enum):
    """Generation status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class StylePreset(BaseModel):
    """Style preset model"""
    key: str = Field(..., description="Style key")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="Style description")

class ImageGenerationRequest(BaseModel):
    """Request for image generation"""
    prompt: str = Field(..., min_length=1, max_length=1000, description="Text prompt for generation")
    style: Optional[str] = Field(None, description="Style preset to apply")
    user_id: Optional[str] = Field(None, description="User ID for tracking")
    generation_type: GenerationType = Field(default=GenerationType.TEXT_TO_IMAGE, description="Type of generation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "A beautiful birthday party decoration with balloons and confetti",
                "style": "party",
                "user_id": "user_123",
                "generation_type": "text_to_image"
            }
        }

class ImageGenerationResponse(BaseModel):
    """Response for image generation"""
    success: bool = Field(..., description="Whether generation was successful")
    generation_id: str = Field(..., description="Unique generation ID")
    image_data: str = Field(..., description="Base64 encoded image data or URL")
    prompt_used: str = Field(..., description="Final prompt used for generation")
    style_applied: Optional[str] = Field(None, description="Style that was applied")
    generated_at: datetime = Field(..., description="Generation timestamp")
    inspiration_analysis: Optional[Dict[str, Any]] = Field(None, description="Analysis of inspiration image")
    error: Optional[str] = Field(None, description="Error message if generation failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "generation_id": "gemini_user_123_1234567890",
                "image_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
                "prompt_used": "A beautiful birthday party decoration with balloons and confetti, vibrant, colorful, festive, celebration, balloons, confetti, fun, high quality, detailed, professional",
                "style_applied": "party",
                "generated_at": "2024-01-13T10:30:00Z"
            }
        }

class FeedbackRequest(BaseModel):
    """Request for submitting feedback"""
    generation_id: str = Field(..., description="Generation ID to provide feedback for")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    feedback: Optional[str] = Field(None, max_length=500, description="Optional text feedback")
    user_id: Optional[str] = Field(None, description="User ID")

class FeedbackResponse(BaseModel):
    """Response for feedback submission"""
    success: bool = Field(..., description="Whether feedback was submitted successfully")
    message: str = Field(..., description="Response message")

class GenerationStatusResponse(BaseModel):
    """Response for generation status"""
    success: bool = Field(..., description="Whether status was retrieved successfully")
    generation_id: str = Field(..., description="Generation ID")
    status: GenerationStatus = Field(..., description="Current status")
    created_at: datetime = Field(..., description="Creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    error: Optional[str] = Field(None, description="Error message if failed")

class BatchGenerationRequest(BaseModel):
    """Request for batch image generation"""
    prompts: List[str] = Field(..., min_items=1, max_items=10, description="List of prompts")
    style: Optional[str] = Field(None, description="Style preset to apply to all")
    user_id: Optional[str] = Field(None, description="User ID for tracking")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompts": [
                    "A birthday cake decoration",
                    "Party balloons arrangement",
                    "Confetti celebration setup"
                ],
                "style": "party",
                "user_id": "user_123"
            }
        }

class BatchGenerationResponse(BaseModel):
    """Response for batch generation"""
    success: bool = Field(..., description="Whether batch generation was successful")
    generation_ids: List[str] = Field(..., description="List of generation IDs")
    results: List[ImageGenerationResponse] = Field(..., description="Individual generation results")
    total_generated: int = Field(..., description="Total number of images generated")
    failed_count: int = Field(..., description="Number of failed generations")

class StyleAnalysisRequest(BaseModel):
    """Request for style analysis"""
    image_data: str = Field(..., description="Base64 encoded image data")
    user_id: Optional[str] = Field(None, description="User ID")

class StyleAnalysisResponse(BaseModel):
    """Response for style analysis"""
    success: bool = Field(..., description="Whether analysis was successful")
    analysis: Dict[str, Any] = Field(..., description="Style analysis results")
    suggested_styles: List[str] = Field(..., description="Suggested style presets")
    color_palette: List[str] = Field(..., description="Detected color palette")
    mood: str = Field(..., description="Detected mood/atmosphere")
    elements: List[str] = Field(..., description="Detected visual elements")
