"""
Motif Module Models
Optimized Pydantic models with strict validation
"""

from .upload import UploadResponse, UploadRequest, ImageFormat
from .scene import Scene3D, Element3D, BackgroundPlane, SceneLighting
from .element import DecorationElement, Segment, LibraryElement
from .processing import ProcessingStatus, ProcessingStage, ProcessingProgress
from .replacement import ReplacementRequest, ReplacementResponse
from .export import ExportRequest, ExportResponse
from .generation import (
    ImageGenerationRequest, ImageGenerationResponse, StylePreset,
    GenerationType, GenerationStatus, FeedbackRequest, FeedbackResponse,
    GenerationStatusResponse, BatchGenerationRequest, BatchGenerationResponse,
    StyleAnalysisRequest, StyleAnalysisResponse
)
from .history import (
    GenerationHistory, GenerationHistoryRequest, GenerationHistoryResponse,
    FavoriteRequest, FavoriteResponse, TagRequest, TagResponse,
    GenerationStats, GenerationStatsResponse
)

__all__ = [
    "UploadResponse",
    "UploadRequest",
    "ImageFormat",
    "Scene3D",
    "Element3D",
    "BackgroundPlane",
    "SceneLighting",
    "DecorationElement",
    "Segment",
    "LibraryElement",
    "ProcessingStatus",
    "ProcessingStage",
    "ProcessingProgress",
    "ReplacementRequest",
    "ReplacementResponse",
    "ExportRequest",
    "ExportResponse",
    "ImageGenerationRequest",
    "ImageGenerationResponse",
    "StylePreset",
    "GenerationType",
    "GenerationStatus",
    "FeedbackRequest",
    "FeedbackResponse",
    "GenerationStatusResponse",
    "BatchGenerationRequest",
    "BatchGenerationResponse",
    "StyleAnalysisRequest",
    "StyleAnalysisResponse",
    "GenerationHistory",
    "GenerationHistoryRequest",
    "GenerationHistoryResponse",
    "FavoriteRequest",
    "FavoriteResponse",
    "TagRequest",
    "TagResponse",
    "GenerationStats",
    "GenerationStatsResponse",
]
