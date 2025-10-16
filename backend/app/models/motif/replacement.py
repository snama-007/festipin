"""
Replacement Models
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ReplacementRequest(BaseModel):
    """Request to replace an element"""
    scene_id: str = Field(..., description="Scene identifier")
    old_element_id: str = Field(..., description="Element to replace")
    new_element_id: str = Field(..., description="Replacement from library")
    preserve_transform: bool = Field(
        default=True,
        description="Preserve position, rotation, scale"
    )
    preserve_properties: bool = Field(
        default=False,
        description="Preserve custom properties"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "scene_id": "scene_001",
                "old_element_id": "elem_001",
                "new_element_id": "lib_balloon_002",
                "preserve_transform": True,
                "preserve_properties": False
            }
        }


class ReplacementResponse(BaseModel):
    """Response after replacement"""
    success: bool = Field(...)
    scene_id: str = Field(...)
    old_element_id: str = Field(...)
    new_element_id: str = Field(...)
    updated_element: Dict[str, Any] = Field(..., description="New element data")
    message: str = Field(default="Element replaced successfully")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
