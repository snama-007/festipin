"""
Processing Status Models
Real-time processing feedback with detailed stages
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime


class ProcessingStage(str, Enum):
    """Processing pipeline stages"""
    IDLE = "idle"
    UPLOADED = "uploaded"
    PREPROCESSING = "preprocessing"
    SEGMENTATION = "segmentation"
    RECOGNITION = "recognition"
    DEPTH_ESTIMATION = "depth_estimation"
    MESH_GENERATION = "mesh_generation"
    SCENE_COMPOSITION = "scene_composition"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingStatus(str, Enum):
    """Overall processing status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessingProgress(BaseModel):
    """Detailed processing progress"""
    upload_id: str = Field(..., description="Upload identifier")
    stage: ProcessingStage = Field(..., description="Current stage")
    status: ProcessingStatus = Field(..., description="Overall status")
    percentage: int = Field(..., ge=0, le=100, description="Progress percentage")
    message: str = Field(..., description="Human-readable message")
    elapsed_time: float = Field(0.0, ge=0, description="Elapsed seconds")
    estimated_remaining: Optional[float] = Field(None, ge=0, description="Estimated remaining seconds")
    current_operation: Optional[str] = Field(None, description="Detailed operation")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('percentage')
    def validate_percentage(cls, v, values):
        """Ensure percentage matches stage"""
        stage = values.get('stage')
        if stage == ProcessingStage.COMPLETED and v != 100:
            return 100
        if stage == ProcessingStage.FAILED:
            return max(0, v)
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "upload_id": "550e8400-e29b-41d4-a716-446655440000",
                "stage": "segmentation",
                "status": "running",
                "percentage": 35,
                "message": "Detecting decoration elements...",
                "elapsed_time": 12.5,
                "estimated_remaining": 32.5,
                "current_operation": "Running SAM segmentation model",
                "errors": [],
                "warnings": [],
                "metadata": {
                    "segments_found": 8
                },
                "updated_at": "2025-01-13T10:30:15Z"
            }
        }


class StageTimings(BaseModel):
    """Performance metrics for each stage"""
    stage: ProcessingStage
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
