"""
Export Models
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from enum import Enum
from datetime import datetime


class ExportFormat(str, Enum):
    """Supported export formats"""
    GLB = "glb"
    GLTF = "gltf"
    FBX = "fbx"
    OBJ = "obj"
    JSON = "json"
    PNG = "png"
    JPG = "jpg"
    PDF = "pdf"


class ExportQuality(str, Enum):
    """Export quality levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"


class ExportRequest(BaseModel):
    """Request to export scene"""
    scene_id: str = Field(..., description="Scene to export")
    format: ExportFormat = Field(..., description="Export format")
    quality: ExportQuality = Field(default=ExportQuality.MEDIUM)
    include_textures: bool = Field(default=True)
    optimize_filesize: bool = Field(default=True)
    width: Optional[int] = Field(None, ge=256, le=4096, description="Image width (for PNG/JPG)")
    height: Optional[int] = Field(None, ge=256, le=4096, description="Image height (for PNG/JPG)")

    class Config:
        json_schema_extra = {
            "example": {
                "scene_id": "scene_001",
                "format": "glb",
                "quality": "medium",
                "include_textures": True,
                "optimize_filesize": True
            }
        }


class ExportResponse(BaseModel):
    """Response after export"""
    success: bool = Field(...)
    scene_id: str = Field(...)
    format: ExportFormat = Field(...)
    download_url: HttpUrl = Field(..., description="Download URL")
    file_size: int = Field(..., gt=0, description="File size in bytes")
    expires_at: datetime = Field(..., description="URL expiration")
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "scene_id": "scene_001",
                "format": "glb",
                "download_url": "https://cdn.example.com/exports/scene_001.glb",
                "file_size": 2457600,
                "expires_at": "2025-01-14T10:30:00Z",
                "metadata": {
                    "polygon_count": 45000,
                    "texture_count": 12
                },
                "created_at": "2025-01-13T10:30:00Z"
            }
        }
