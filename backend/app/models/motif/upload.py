"""
Upload Models with Strict Validation
"""

from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ImageFormat(str, Enum):
    """Supported image formats"""
    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"
    WEBP = "webp"


class UploadRequest(BaseModel):
    """Upload request validation"""
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UploadResponse(BaseModel):
    """Upload response with comprehensive metadata"""
    upload_id: str = Field(..., description="Unique upload identifier")
    image_url: HttpUrl = Field(..., description="Stored image URL")
    thumbnail_url: HttpUrl = Field(..., description="Thumbnail URL")
    estimated_processing_time: int = Field(..., ge=5, le=300, description="Seconds")
    image_dimensions: tuple[int, int] = Field(..., description="Width x Height")
    file_size: int = Field(..., gt=0, description="File size in bytes")
    format: ImageFormat = Field(..., description="Image format")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="uploaded", description="Initial status")

    class Config:
        json_schema_extra = {
            "example": {
                "upload_id": "550e8400-e29b-41d4-a716-446655440000",
                "image_url": "https://storage.googleapis.com/uploads/image.jpg",
                "thumbnail_url": "https://storage.googleapis.com/uploads/image_thumb.jpg",
                "estimated_processing_time": 45,
                "image_dimensions": [1920, 1080],
                "file_size": 2457600,
                "format": "jpeg",
                "created_at": "2025-01-13T10:30:00Z",
                "status": "uploaded"
            }
        }
