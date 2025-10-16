"""
3D Scene Models with Optimization Features
"""

from pydantic import BaseModel, Field, validator, HttpUrl
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from enum import Enum


class RenderQuality(str, Enum):
    """Rendering quality levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"


class Element3D(BaseModel):
    """3D transformed decoration element"""
    id: str = Field(..., description="Element identifier")
    source_element_id: str = Field(..., description="Source 2D element ID")
    name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(...)
    type: str = Field(...)

    # 3D Assets
    mesh_url: HttpUrl = Field(..., description="3D mesh URL (GLB/GLTF)")
    texture_url: Optional[HttpUrl] = Field(None, description="Texture URL")
    normal_map_url: Optional[HttpUrl] = Field(None, description="Normal map URL")

    # Transform properties
    position: Tuple[float, float, float] = Field(..., description="3D position (x, y, z)")
    rotation: Tuple[float, float, float] = Field(
        default=(0, 0, 0),
        description="Rotation in radians (rx, ry, rz)"
    )
    scale: Tuple[float, float, float] = Field(
        default=(1, 1, 1),
        description="Scale factors (sx, sy, sz)"
    )

    # Visual properties
    colors: List[str] = Field(default_factory=list)
    material: str = Field(default="standard")
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)

    # Interaction properties
    interactable: bool = Field(default=True)
    replaceable: bool = Field(default=True)
    deletable: bool = Field(default=True)
    duplicatable: bool = Field(default=True)

    # AI metadata
    confidence: float = Field(..., ge=0.0, le=1.0)

    # Optimization
    lod_levels: Dict[str, HttpUrl] = Field(
        default_factory=dict,
        description="Level of Detail meshes (low, medium, high)"
    )
    bounding_box: Tuple[Tuple[float, float, float], Tuple[float, float, float]] = Field(
        ...,
        description="Min and Max corners of bounding box"
    )
    polygon_count: Optional[int] = Field(None, ge=0, description="Triangle count")

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('scale')
    def validate_scale(cls, v):
        """Ensure positive scale values"""
        if any(s <= 0 for s in v):
            raise ValueError("Scale values must be positive")
        return v

    @validator('rotation')
    def validate_rotation(cls, v):
        """Normalize rotation to -π to π"""
        import math
        return tuple(((r + math.pi) % (2 * math.pi)) - math.pi for r in v)


class BackgroundPlane(BaseModel):
    """3D background representation with depth"""
    texture_url: HttpUrl = Field(..., description="Background texture")
    depth_map_url: HttpUrl = Field(..., description="Depth map texture")
    normal_map_url: Optional[HttpUrl] = Field(None, description="Normal map for lighting")

    # Dimensions
    dimensions: Tuple[float, float] = Field(..., description="Width x Height in meters")
    depth_scale: float = Field(default=1.0, gt=0, description="Depth exaggeration factor")

    # Position
    position: Tuple[float, float, float] = Field(default=(0, 0, 0))
    rotation: Tuple[float, float, float] = Field(default=(0, 0, 0))

    # Optimization
    subdivision_level: int = Field(default=64, ge=8, le=512, description="Mesh subdivision")

    @validator('dimensions')
    def validate_dimensions(cls, v):
        """Ensure positive dimensions"""
        if v[0] <= 0 or v[1] <= 0:
            raise ValueError("Dimensions must be positive")
        return v


class SceneLighting(BaseModel):
    """Scene lighting configuration"""
    ambient_intensity: float = Field(default=0.5, ge=0, le=1, description="Ambient light")
    ambient_color: str = Field(default="#ffffff", description="Ambient color hex")

    # Primary light
    primary_light_position: Tuple[float, float, float] = Field(default=(5, 5, 5))
    primary_light_intensity: float = Field(default=1.0, ge=0, le=5)
    primary_light_color: str = Field(default="#ffffff")

    # Additional lights
    additional_lights: List[Dict[str, Any]] = Field(default_factory=list)

    # Environment
    environment_map: Optional[HttpUrl] = Field(None, description="HDRI environment")
    color_temperature: int = Field(default=6500, ge=1000, le=15000, description="Kelvin")

    # Shadows
    cast_shadows: bool = Field(default=True)
    shadow_quality: str = Field(default="medium")


class SpatialRelationship(BaseModel):
    """Spatial relationship between elements"""
    element1_id: str
    element2_id: str
    relationship_type: str = Field(..., description="above, below, left_of, right_of, in_front, behind")
    distance: float = Field(..., ge=0, description="Distance in meters")
    confidence: float = Field(..., ge=0, le=1)


class Scene3D(BaseModel):
    """Complete 3D scene representation"""
    id: str = Field(..., description="Scene identifier")
    upload_id: str = Field(..., description="Source upload ID")
    name: str = Field(default="Untitled Scene", max_length=200)

    # Scene components
    background: BackgroundPlane = Field(..., description="Background plane with depth")
    elements: List[Element3D] = Field(..., description="3D decoration elements")
    lighting: SceneLighting = Field(..., description="Scene lighting")

    # Spatial analysis
    relationships: List[SpatialRelationship] = Field(
        default_factory=list,
        description="Spatial relationships"
    )

    # Scene graph for optimization
    scene_graph: Dict[str, Any] = Field(
        default_factory=dict,
        description="Hierarchical scene structure"
    )

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    statistics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Scene statistics (element counts, polygon counts, etc.)"
    )

    # Optimization settings
    render_quality: RenderQuality = Field(default=RenderQuality.MEDIUM)
    use_lod: bool = Field(default=True, description="Use Level of Detail")
    use_frustum_culling: bool = Field(default=True)
    use_occlusion_culling: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time: Optional[float] = Field(None, ge=0, description="Total processing seconds")

    @validator('elements')
    def validate_elements(cls, v):
        """Ensure at least one element"""
        if len(v) == 0:
            raise ValueError("Scene must contain at least one element")
        return v

    def get_element_by_id(self, element_id: str) -> Optional[Element3D]:
        """Helper to find element by ID"""
        return next((e for e in self.elements if e.id == element_id), None)

    def get_total_polygons(self) -> int:
        """Calculate total polygon count"""
        return sum(e.polygon_count or 0 for e in self.elements)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "scene_001",
                "upload_id": "upload_001",
                "name": "Birthday Party Scene",
                "background": {
                    "texture_url": "https://cdn.example.com/bg/texture.jpg",
                    "depth_map_url": "https://cdn.example.com/bg/depth.jpg",
                    "dimensions": [5.0, 3.0],
                    "depth_scale": 1.2
                },
                "elements": [],
                "lighting": {
                    "ambient_intensity": 0.5,
                    "primary_light_intensity": 1.0
                },
                "metadata": {
                    "total_elements": 8,
                    "categories": {"balloons": 4, "banners": 2, "centerpieces": 2}
                },
                "render_quality": "medium",
                "created_at": "2025-01-13T10:31:00Z"
            }
        }
