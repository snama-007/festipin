"""
Base provider interface and models for image generation services.

This module provides the abstract base class and standardized models
that all image generation providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import uuid

class ServiceStatus(str, Enum):
    """Service health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNAVAILABLE = "unavailable"

class GenerationQuality(str, Enum):
    """Generation quality levels"""
    FAST = "fast"
    STANDARD = "standard"
    PREMIUM = "premium"

class GenerationType(str, Enum):
    """Types of image generation"""
    TEXT_TO_IMAGE = "text_to_image"
    IMAGE_TO_IMAGE = "image_to_image"
    INPAINTING = "inpainting"
    OUTPAINTING = "outpainting"

class GenerationRequest(BaseModel):
    """Standardized request format for all providers"""
    
    # Core generation parameters
    prompt: str = Field(..., min_length=1, max_length=2000, description="Text prompt for image generation")
    negative_prompt: Optional[str] = Field(None, max_length=2000, description="Negative prompt to avoid certain elements")
    style: Optional[str] = Field(None, description="Style preset to apply")
    
    # Image parameters
    width: int = Field(1024, ge=256, le=2048, description="Image width in pixels")
    height: int = Field(1024, ge=256, le=2048, description="Image height in pixels")
    quality: GenerationQuality = Field(GenerationQuality.STANDARD, description="Generation quality level")
    
    # Reference image (for image-to-image, inpainting, outpainting)
    reference_image: Optional[str] = Field(None, description="Base64 encoded reference image")
    image_strength: float = Field(0.8, ge=0.0, le=1.0, description="Strength of reference image influence")
    mask_image: Optional[str] = Field(None, description="Base64 encoded mask for inpainting")
    
    # Advanced parameters
    steps: Optional[int] = Field(None, ge=1, le=100, description="Number of generation steps")
    guidance_scale: Optional[float] = Field(None, ge=1.0, le=20.0, description="Guidance scale for generation")
    seed: Optional[int] = Field(None, description="Random seed for reproducible results")
    
    # Service preferences
    preferred_provider: Optional[str] = Field(None, description="Preferred provider to use")
    max_cost: Optional[float] = Field(None, ge=0.0, description="Maximum cost for generation")
    timeout: int = Field(30, ge=5, le=300, description="Request timeout in seconds")
    
    # User context
    user_id: str = Field(..., description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique request identifier")

class GenerationResponse(BaseModel):
    """Standardized response format for all providers"""
    
    # Core response fields
    success: bool = Field(..., description="Whether generation was successful")
    generation_id: str = Field(..., description="Unique identifier for this generation")
    image_data: str = Field(..., description="Generated image data (base64, URL, or data URI)")
    
    # Provider information
    provider_used: str = Field(..., description="Provider that generated the image")
    provider_version: Optional[str] = Field(None, description="Provider version used")
    
    # Cost and performance
    cost: Optional[float] = Field(None, ge=0.0, description="Cost of generation")
    processing_time: float = Field(..., ge=0.0, description="Processing time in seconds")
    
    # Generation details
    seed: Optional[int] = Field(None, description="Seed used for generation")
    steps_used: Optional[int] = Field(None, description="Number of steps used")
    guidance_scale_used: Optional[float] = Field(None, description="Guidance scale used")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional provider-specific metadata")
    error: Optional[str] = Field(None, description="Error message if generation failed")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")

class BatchGenerationRequest(BaseModel):
    """Request for batch image generation"""
    requests: List[GenerationRequest] = Field(..., min_items=1, max_items=10, description="List of generation requests")
    max_concurrent: int = Field(3, ge=1, le=10, description="Maximum concurrent generations")
    fail_fast: bool = Field(False, description="Stop on first failure")

class BatchGenerationResponse(BaseModel):
    """Response for batch image generation"""
    success: bool = Field(..., description="Whether batch generation was successful")
    batch_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique batch identifier")
    results: List[GenerationResponse] = Field(..., description="List of generation results")
    total_cost: Optional[float] = Field(None, ge=0.0, description="Total cost of batch generation")
    total_processing_time: float = Field(..., ge=0.0, description="Total processing time")
    successful_count: int = Field(..., ge=0, description="Number of successful generations")
    failed_count: int = Field(..., ge=0, description="Number of failed generations")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Batch creation timestamp")

class ServiceHealth(BaseModel):
    """Service health information"""
    status: ServiceStatus = Field(..., description="Current service status")
    last_check: datetime = Field(default_factory=datetime.utcnow, description="Last health check timestamp")
    response_time: Optional[float] = Field(None, ge=0.0, description="Average response time in seconds")
    queue_length: Optional[int] = Field(None, ge=0, description="Current queue length")
    error_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="Error rate (0.0 to 1.0)")
    uptime: Optional[float] = Field(None, ge=0.0, description="Service uptime percentage")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional health metrics")

class CostEstimate(BaseModel):
    """Cost estimation for generation request"""
    estimated_cost: float = Field(..., ge=0.0, description="Estimated cost")
    currency: str = Field("USD", description="Currency code")
    breakdown: Dict[str, float] = Field(default_factory=dict, description="Cost breakdown by component")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence in estimate (0.0 to 1.0)")

class ImageGenerationProvider(ABC):
    """
    Abstract base class for all image generation providers.
    
    This interface ensures all providers implement the same methods
    and return standardized responses.
    """
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this provider"""
        pass
    
    @property
    @abstractmethod
    def provider_version(self) -> str:
        """Return the version of this provider"""
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the provider.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def generate_image(self, request: GenerationRequest) -> GenerationResponse:
        """
        Generate a single image.
        
        Args:
            request: Generation request parameters
            
        Returns:
            GenerationResponse: Standardized response
        """
        pass
    
    @abstractmethod
    async def generate_batch(self, request: BatchGenerationRequest) -> BatchGenerationResponse:
        """
        Generate multiple images in batch.
        
        Args:
            request: Batch generation request
            
        Returns:
            BatchGenerationResponse: Standardized batch response
        """
        pass
    
    @abstractmethod
    async def get_service_health(self) -> ServiceHealth:
        """
        Get current service health status.
        
        Returns:
            ServiceHealth: Current health information
        """
        pass
    
    @abstractmethod
    async def estimate_cost(self, request: GenerationRequest) -> CostEstimate:
        """
        Estimate cost for generation request.
        
        Args:
            request: Generation request to estimate
            
        Returns:
            CostEstimate: Cost estimation
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close provider connections and cleanup resources"""
        pass
    
    # Optional methods that providers can override
    async def get_supported_models(self) -> List[str]:
        """Get list of supported models"""
        return []
    
    async def get_supported_styles(self) -> List[str]:
        """Get list of supported styles"""
        return []
    
    async def validate_request(self, request: GenerationRequest) -> List[str]:
        """
        Validate generation request.
        
        Args:
            request: Request to validate
            
        Returns:
            List[str]: List of validation errors (empty if valid)
        """
        return []
