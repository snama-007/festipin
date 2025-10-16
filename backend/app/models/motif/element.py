"""
Element Models with Comprehensive Validation
"""

from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
from datetime import datetime


class DecorationCategory(str, Enum):
    """Standard decoration categories"""
    BALLOONS = "balloons"
    BANNERS = "banners"
    CENTERPIECES = "centerpieces"
    BACKDROPS = "backdrops"
    TABLE_SETTINGS = "table_settings"
    LIGHTING = "lighting"
    PROPS = "props"
    FURNITURE = "furniture"
    FLORALS = "florals"
    SIGNAGE = "signage"
    UNKNOWN = "unknown"


class MaterialType(str, Enum):
    """Material classifications"""
    FOIL = "foil"
    LATEX = "latex"
    PAPER = "paper"
    FABRIC = "fabric"
    PLASTIC = "plastic"
    WOOD = "wood"
    METAL = "metal"
    GLASS = "glass"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class StyleType(str, Enum):
    """Style classifications"""
    MODERN = "modern"
    VINTAGE = "vintage"
    RUSTIC = "rustic"
    ELEGANT = "elegant"
    MINIMALIST = "minimalist"
    BOHEMIAN = "bohemian"
    INDUSTRIAL = "industrial"
    TROPICAL = "tropical"
    CLASSIC = "classic"
    UNKNOWN = "unknown"


class SizeCategory(str, Enum):
    """Size categories"""
    EXTRA_SMALL = "xs"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "xl"


class Segment(BaseModel):
    """Image segmentation result"""
    id: str = Field(..., description="Segment identifier")
    bbox: Tuple[int, int, int, int] = Field(..., description="Bounding box (x, y, w, h)")
    area: int = Field(..., gt=0, description="Segment area in pixels")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Segmentation confidence")
    mask_url: Optional[HttpUrl] = Field(None, description="Binary mask URL")
    center_point: Tuple[int, int] = Field(..., description="Segment center (x, y)")

    @validator('bbox')
    def validate_bbox(cls, v):
        """Ensure valid bounding box"""
        x, y, w, h = v
        if w <= 0 or h <= 0:
            raise ValueError("Width and height must be positive")
        if x < 0 or y < 0:
            raise ValueError("Coordinates must be non-negative")
        return v


class DecorationElement(BaseModel):
    """Detected decoration element with AI analysis"""
    id: str = Field(..., description="Element identifier")
    segment_id: str = Field(..., description="Source segment ID")
    name: str = Field(..., min_length=1, max_length=200, description="Element name")
    category: DecorationCategory = Field(..., description="Element category")
    type: str = Field(..., description="Specific type (e.g., 'foil balloon')")

    # Visual properties
    colors: List[str] = Field(default_factory=list, description="Hex color codes")
    material: MaterialType = Field(default=MaterialType.UNKNOWN)
    style: StyleType = Field(default=StyleType.UNKNOWN)
    size_category: SizeCategory = Field(default=SizeCategory.MEDIUM)

    # Spatial properties
    bbox: Tuple[int, int, int, int] = Field(..., description="Bounding box")
    position_2d: Tuple[int, int] = Field(..., description="Center position (x, y)")
    estimated_depth: Optional[float] = Field(None, ge=0, description="Estimated depth")

    # AI analysis
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence")
    detected_text: Optional[str] = Field(None, description="Any visible text")
    patterns: List[str] = Field(default_factory=list, description="Detected patterns")

    # Metadata
    placement_suggestion: Optional[str] = Field(None, description="Suggested placement")
    tags: List[str] = Field(default_factory=list, description="Search tags")
    raw_analysis: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('colors')
    def validate_colors(cls, v):
        """Validate hex color codes"""
        import re
        hex_pattern = re.compile(r'^#(?:[0-9a-fA-F]{3}){1,2}$')
        for color in v:
            if not hex_pattern.match(color):
                raise ValueError(f"Invalid hex color: {color}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "elem_001",
                "segment_id": "seg_001",
                "name": "Purple Foil Balloon",
                "category": "balloons",
                "type": "foil_balloon_number",
                "colors": ["#6b46c1", "#8b5cf6"],
                "material": "foil",
                "style": "modern",
                "size_category": "large",
                "bbox": [450, 200, 180, 250],
                "position_2d": [540, 325],
                "estimated_depth": 2.5,
                "confidence": 0.94,
                "detected_text": "5",
                "patterns": ["number", "holographic"],
                "placement_suggestion": "wall_or_ceiling",
                "tags": ["balloon", "number", "purple", "birthday"],
                "raw_analysis": {},
                "created_at": "2025-01-13T10:30:20Z"
            }
        }


class LibraryElement(BaseModel):
    """Pre-built decoration element from library"""
    id: str = Field(..., description="Library element ID")
    name: str = Field(..., min_length=1, max_length=200)
    category: DecorationCategory = Field(...)
    type: str = Field(...)

    # Assets
    thumbnail_url: HttpUrl = Field(..., description="Preview thumbnail")
    mesh_url: HttpUrl = Field(..., description="3D mesh file URL")
    texture_url: Optional[HttpUrl] = Field(None, description="Texture file URL")

    # Properties
    colors: List[str] = Field(default_factory=list)
    style: StyleType = Field(default=StyleType.UNKNOWN)
    material: MaterialType = Field(default=MaterialType.UNKNOWN)

    # Dimensions (in meters)
    dimensions: Optional[Tuple[float, float, float]] = Field(None, description="Width, Height, Depth")

    # Metadata
    tags: List[str] = Field(default_factory=list)
    popularity: int = Field(default=0, ge=0, description="Usage count")
    rating: Optional[float] = Field(None, ge=0, le=5, description="User rating")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # File sizes for optimization
    file_sizes: Dict[str, int] = Field(default_factory=dict, description="Asset file sizes")

    @validator('dimensions')
    def validate_dimensions(cls, v):
        """Ensure positive dimensions"""
        if v is not None:
            w, h, d = v
            if w <= 0 or h <= 0 or d <= 0:
                raise ValueError("Dimensions must be positive")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "lib_balloon_001",
                "name": "Number 5 Foil Balloon - Purple",
                "category": "balloons",
                "type": "foil_balloon_number",
                "thumbnail_url": "https://cdn.example.com/thumbs/balloon_001.jpg",
                "mesh_url": "https://cdn.example.com/models/balloon_001.glb",
                "texture_url": "https://cdn.example.com/textures/balloon_001.png",
                "colors": ["#6b46c1"],
                "style": "modern",
                "material": "foil",
                "dimensions": [0.6, 0.9, 0.1],
                "tags": ["balloon", "number", "5", "purple", "foil"],
                "popularity": 156,
                "rating": 4.7,
                "file_sizes": {
                    "mesh": 245600,
                    "texture": 102400
                }
            }
        }
