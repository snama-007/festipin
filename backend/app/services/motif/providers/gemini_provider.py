"""
Gemini Provider Adapter

Adapts MotifGeminiGenerator to implement ImageGenerationProvider interface
"""

import asyncio
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .base import (
    ImageGenerationProvider, GenerationRequest, GenerationResponse,
    BatchGenerationRequest, BatchGenerationResponse, ServiceHealth,
    CostEstimate, ServiceStatus, GenerationQuality
)
from app.services.motif.gemini_image_generator import MotifGeminiGenerator
from app.core.config import settings

logger = logging.getLogger(__name__)

class GeminiProvider(ImageGenerationProvider):
    """Adapter for MotifGeminiGenerator to implement ImageGenerationProvider interface"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        # Initialize with API key or use mock mode if no key
        if self.api_key and self.api_key != "your_gemini_api_key_here":
            self.gemini_generator = MotifGeminiGenerator(self.api_key)
        else:
            # Create with mock key for testing
            self.gemini_generator = MotifGeminiGenerator("mock_key")
            self.gemini_generator.mock_mode = True
        self.is_connected = False
        self._initialization_attempted = False
        
        # Health tracking
        self._consecutive_failures = 0
        self._total_requests = 0
        self._success_count = 0
        self._response_times = []
    
    @property
    def provider_name(self) -> str:
        """Return the name of this provider"""
        return "gemini"
    
    @property
    def provider_version(self) -> str:
        """Return the version of this provider"""
        return "1.0.0"
    
    async def initialize(self) -> bool:
        """Initialize the Gemini provider"""
        if self._initialization_attempted:
            return self.is_connected
        
        self._initialization_attempted = True
        
        try:
            logger.info("Initializing Gemini provider...")
            
            # Initialize the underlying generator
            await self.gemini_generator.initialize()
            
            self.is_connected = True
            logger.info("Gemini provider initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini provider: {e}")
            self.is_connected = False
            return False
    
    async def generate_image(self, request: GenerationRequest) -> GenerationResponse:
        """Generate image using Gemini"""
        start_time = time.time()
        
        try:
            # Ensure provider is initialized
            if not self.is_connected:
                if not await self.initialize():
                    return self._create_error_response(
                        request, "Gemini service unavailable", start_time
                    )
            
            # Convert GenerationRequest to the format expected by MotifGeminiGenerator
            result = await self.gemini_generator.generate_image_from_prompt(
                prompt=request.prompt,
                style=request.style,
                quality=request.quality.value if request.quality else "standard",
                user_id=request.user_id or "anonymous"
            )
            
            processing_time = time.time() - start_time
            
            if result.get("success", False):
                self._success_count += 1
                self._consecutive_failures = 0
                self._response_times.append(processing_time)
                
                return GenerationResponse(
                    success=True,
                    generation_id=f"gemini_{result.get('generation_id', 'unknown')}",
                    image_data=result.get("image_data", ""),
                    provider_used=self.provider_name,
                    provider_version=self.provider_version,
                    cost=0.0,  # Gemini doesn't provide cost info
                    processing_time=processing_time,
                    metadata={
                        "prompt": request.prompt,
                        "style": request.style,
                        "quality": request.quality.value if request.quality else "standard",
                        "mock_mode": result.get("mock_mode", False)
                    }
                )
            else:
                self._consecutive_failures += 1
                return self._create_error_response(
                    request, result.get("error", "Generation failed"), start_time
                )
                
        except Exception as e:
            self._consecutive_failures += 1
            self._total_requests += 1
            logger.error(f"Gemini generation failed: {e}")
            return self._create_error_response(request, str(e), start_time)
    
    async def generate_batch(self, request: BatchGenerationRequest) -> BatchGenerationResponse:
        """Generate multiple images using Gemini"""
        start_time = time.time()
        
        try:
            # Ensure provider is initialized
            if not self.is_connected:
                if not await self.initialize():
                    return BatchGenerationResponse(
                        success=False,
                        batch_id=f"gemini_batch_{int(time.time())}",
                        results=[],
                        successful_count=0,
                        failed_count=len(request.requests),
                        total_cost=0.0,
                        total_processing_time=time.time() - start_time,
                        error="Gemini service unavailable"
                    )
            
            # Convert batch request to the format expected by MotifGeminiGenerator
            prompts = [req.prompt for req in request.requests]
            
            result = await self.gemini_generator.generate_batch_images(
                prompts=prompts,
                style=request.requests[0].style if request.requests else None,
                quality="standard",
                user_id=request.requests[0].user_id if request.requests else "anonymous"
            )
            
            processing_time = time.time() - start_time
            
            if result.get("success", False):
                # Convert results to GenerationResponse format
                responses = []
                for i, gen_result in enumerate(result.get("generations", [])):
                    if gen_result.get("success", False):
                        responses.append(GenerationResponse(
                            success=True,
                            generation_id=f"gemini_{gen_result.get('generation_id', f'batch_{i}')}",
                            image_data=gen_result.get("image_data", ""),
                            provider_used=self.provider_name,
                            provider_version=self.provider_version,
                            cost=0.0,
                            processing_time=processing_time / len(request.requests),
                            metadata=gen_result.get("metadata", {})
                        ))
                    else:
                        responses.append(self._create_error_response(
                            request.requests[i], gen_result.get("error", "Generation failed"), start_time
                        ))
                
                return BatchGenerationResponse(
                    success=True,
                    batch_id=f"gemini_batch_{int(time.time())}",
                    results=responses,
                    successful_count=len([r for r in responses if r.success]),
                    failed_count=len([r for r in responses if not r.success]),
                    total_cost=0.0,
                    total_processing_time=processing_time
                )
            else:
                return BatchGenerationResponse(
                    success=False,
                    batch_id=f"gemini_batch_{int(time.time())}",
                    results=[],
                    successful_count=0,
                    failed_count=len(request.requests),
                    total_cost=0.0,
                    total_processing_time=processing_time,
                    error=result.get("error", "Batch generation failed")
                )
                
        except Exception as e:
            logger.error(f"Gemini batch generation failed: {e}")
            return BatchGenerationResponse(
                success=False,
                batch_id=f"gemini_batch_{int(time.time())}",
                results=[],
                successful_count=0,
                failed_count=len(request.requests),
                total_cost=0.0,
                total_processing_time=time.time() - start_time,
                error=str(e)
            )
    
    async def get_service_health(self) -> ServiceHealth:
        """Get Gemini service health status"""
        try:
            if not self.is_connected:
                return ServiceHealth(
                    status=ServiceStatus.UNAVAILABLE,
                    response_time=0.0,
                    last_check=datetime.utcnow(),
                    error_message="Not connected"
                )
            
            # Test connection
            start_time = time.time()
            await self.gemini_generator._test_connection()
            response_time = time.time() - start_time
            
            # Determine status based on recent performance
            if self._consecutive_failures > 3:
                status = ServiceStatus.UNHEALTHY
            elif self._consecutive_failures > 0:
                status = ServiceStatus.DEGRADED
            else:
                status = ServiceStatus.HEALTHY
            
            return ServiceHealth(
                status=status,
                response_time=response_time,
                last_check=datetime.utcnow(),
                error_message=None
            )
            
        except Exception as e:
            return ServiceHealth(
                status=ServiceStatus.UNHEALTHY,
                response_time=0.0,
                last_check=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def estimate_cost(self, request: GenerationRequest) -> CostEstimate:
        """Estimate cost for Gemini generation"""
        # Gemini doesn't provide cost estimates, return 0
        return CostEstimate(
            estimated_cost=0.0,
            currency="USD",
            breakdown={
                "base_cost": 0.0,
                "quality_multiplier": 1.0,
                "size_multiplier": 1.0
            }
        )
    
    async def close(self):
        """Close Gemini provider connection"""
        try:
            self.is_connected = False
            logger.info("Gemini provider closed")
        except Exception as e:
            logger.error(f"Error closing Gemini provider: {e}")
    
    def _create_error_response(self, request: GenerationRequest, error: str, start_time: float) -> GenerationResponse:
        """Create error response"""
        return GenerationResponse(
            success=False,
            generation_id=f"gemini_error_{int(time.time())}",
            image_data="",
            provider_used=self.provider_name,
            provider_version=self.provider_version,
            cost=0.0,
            processing_time=time.time() - start_time,
            error=error,
            metadata={"error": error}
        )
