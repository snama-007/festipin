"""
Vision analysis models
"""

from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Any, Optional


class VisionAnalysisRequest(BaseModel):
    """Request for vision analysis"""
    image_url: HttpUrl
    input_id: str
    user_id: str


class DetectedObject(BaseModel):
    """Detected object in scene"""
    type: str
    color: str
    position: Dict[str, float]
    dimensions: Optional[Dict[str, float]] = None
    count: int = 1
    confidence: float = 0.0


class SceneData(BaseModel):
    """Parsed scene data from vision analysis"""
    theme: str
    confidence: float
    objects: List[DetectedObject]
    color_palette: List[str]
    layout_type: str
    recommended_venue: Optional[str] = None
    occasion_type: Optional[str] = None
    style_tags: Optional[List[str]] = None
    age_range: Optional[List[int]] = None
    budget_estimate: Optional[Dict[str, int]] = None


class VisionAnalysisResponse(BaseModel):
    """Response from vision analysis"""
    success: bool
    scene: Optional[SceneData] = None
    error: Optional[str] = None

