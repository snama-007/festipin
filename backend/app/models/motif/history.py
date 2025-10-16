"""
Generation History Models

Models for storing and managing image generation history and user favorites.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class GenerationStatus(str, Enum):
    """Generation status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class GenerationType(str, Enum):
    """Types of image generation"""
    TEXT_TO_IMAGE = "text_to_image"
    IMAGE_TO_IMAGE = "image_to_image"
    INSPIRATION_BASED = "inspiration_based"

class GenerationHistory(BaseModel):
    """Model for storing generation history"""
    id: str = Field(..., description="Unique generation ID")
    user_id: str = Field(..., description="User ID")
    prompt: str = Field(..., description="Original prompt")
    enhanced_prompt: str = Field(..., description="Enhanced prompt with style")
    style: Optional[str] = Field(None, description="Applied style preset")
    generation_type: GenerationType = Field(..., description="Type of generation")
    status: GenerationStatus = Field(..., description="Generation status")
    image_data: Optional[str] = Field(None, description="Base64 image data or URL")
    image_url: Optional[str] = Field(None, description="Stored image URL")
    inspiration_image_url: Optional[str] = Field(None, description="Original inspiration image URL")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    rating: Optional[int] = Field(None, ge=1, le=5, description="User rating (1-5)")
    feedback: Optional[str] = Field(None, description="User feedback comment")
    is_favorite: bool = Field(False, description="Whether marked as favorite")
    tags: List[str] = Field(default_factory=list, description="User-defined tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class GenerationHistoryRequest(BaseModel):
    """Request model for getting generation history"""
    user_id: str = Field(..., description="User ID")
    limit: int = Field(20, ge=1, le=100, description="Number of results to return")
    offset: int = Field(0, ge=0, description="Number of results to skip")
    status: Optional[GenerationStatus] = Field(None, description="Filter by status")
    generation_type: Optional[GenerationType] = Field(None, description="Filter by type")
    style: Optional[str] = Field(None, description="Filter by style")
    favorites_only: bool = Field(False, description="Show only favorites")
    search_query: Optional[str] = Field(None, description="Search in prompts")

class GenerationHistoryResponse(BaseModel):
    """Response model for generation history"""
    success: bool = Field(..., description="True if request was successful")
    generations: List[GenerationHistory] = Field(..., description="List of generations")
    total_count: int = Field(..., description="Total number of generations")
    has_more: bool = Field(..., description="True if there are more results")

class FavoriteRequest(BaseModel):
    """Request model for marking/unmarking favorites"""
    generation_id: str = Field(..., description="Generation ID")
    user_id: str = Field(..., description="User ID")
    is_favorite: bool = Field(..., description="Whether to mark as favorite")

class FavoriteResponse(BaseModel):
    """Response model for favorite operations"""
    success: bool = Field(..., description="True if operation was successful")
    is_favorite: bool = Field(..., description="Current favorite status")
    message: str = Field(..., description="Operation message")

class TagRequest(BaseModel):
    """Request model for adding/removing tags"""
    generation_id: str = Field(..., description="Generation ID")
    user_id: str = Field(..., description="User ID")
    tags: List[str] = Field(..., description="List of tags to add/remove")
    action: str = Field(..., description="'add' or 'remove'")

class TagResponse(BaseModel):
    """Response model for tag operations"""
    success: bool = Field(..., description="True if operation was successful")
    tags: List[str] = Field(..., description="Updated list of tags")
    message: str = Field(..., description="Operation message")

class GenerationStats(BaseModel):
    """Model for generation statistics"""
    user_id: str = Field(..., description="User ID")
    total_generations: int = Field(0, description="Total number of generations")
    successful_generations: int = Field(0, description="Number of successful generations")
    failed_generations: int = Field(0, description="Number of failed generations")
    favorite_count: int = Field(0, description="Number of favorites")
    total_processing_time: float = Field(0, description="Total processing time")
    average_rating: Optional[float] = Field(None, description="Average user rating")
    most_used_style: Optional[str] = Field(None, description="Most frequently used style")
    most_used_type: Optional[GenerationType] = Field(None, description="Most frequently used type")
    last_generation: Optional[datetime] = Field(None, description="Last generation timestamp")

class GenerationStatsResponse(BaseModel):
    """Response model for generation statistics"""
    success: bool = Field(..., description="True if request was successful")
    stats: GenerationStats = Field(..., description="Generation statistics")
