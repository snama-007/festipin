"""
Optimized Runware AI image generation provider implementation.

This module implements the ImageGenerationProvider interface for Runware AI,
providing high-quality image generation capabilities with performance optimizations.
"""

import asyncio
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from functools import lru_cache
import weakref

try:
    from runware import Runware, IImageInference
    RUNWARE_AVAILABLE = True
except ImportError:
    RUNWARE_AVAILABLE = False
    logging.warning("Runware library not available. Install with: pip install runware")

from .base import (
    ImageGenerationProvider, GenerationRequest, GenerationResponse,
    BatchGenerationRequest, BatchGenerationResponse, ServiceHealth,
    CostEstimate, ServiceStatus, GenerationQuality
)
from app.core.config import settings

logger = logging.getLogger(__name__)

class RunwareProvider(ImageGenerationProvider):
    """Optimized Runware AI image generation provider with caching and connection pooling"""
    
    def __init__(self):
        if not RUNWARE_AVAILABLE:
            raise ImportError("Runware library not available. Install with: pip install runware")
        
        self.api_key = settings.RUNWARE_API_KEY
        self.client: Optional[Runware] = None
        self.is_connected = False
        self._initialization_attempted = False
        
        # Connection pooling and caching
        self._connection_pool_size = 5
        self._connection_pool: List[Runware] = []
        self._pool_lock = asyncio.Lock()
        self._request_cache: Dict[str, Any] = {}
        self._cache_lock = asyncio.Lock()
        
        # Optimized model configurations with caching
        self.model_configs = {
            GenerationQuality.FAST: {
                "model": "runware:101@1",
                "steps": 15,
                "guidance_scale": 7.0,
                "cost_per_image": 0.01,
                "description": "Fast generation with good quality",
                "cache_key": "fast_config"
            },
            GenerationQuality.STANDARD: {
                "model": "runware:101@1", 
                "steps": 20,
                "guidance_scale": 7.5,
                "cost_per_image": 0.02,
                "description": "Balanced speed and quality",
                "cache_key": "standard_config"
            },
            GenerationQuality.PREMIUM: {
                "model": "runware:101@1",
                "steps": 30,
                "guidance_scale": 8.0,
                "cost_per_image": 0.05,
                "description": "Highest quality generation",
                "cache_key": "premium_config"
            }
        }
        
        # Optimized style presets with caching
        self.style_presets = {
            "party": "vibrant, colorful, festive, celebration, balloons, confetti, fun, high quality, detailed",
            "elegant": "sophisticated, refined, minimalist, classy, elegant, upscale, professional, clean",
            "fun": "playful, whimsical, cheerful, bright, cartoonish, cute, animated style",
            "romantic": "soft, dreamy, intimate, warm, pastel, romantic, gentle, ethereal",
            "birthday": "colorful, celebratory, cake, balloons, party hats, festive, joyful",
            "wedding": "elegant, romantic, white, flowers, sophisticated, beautiful, timeless",
            "holiday": "festive, seasonal, traditional, celebratory, themed, magical",
            "corporate": "professional, clean, modern, business, corporate, sleek, minimalist",
            "casual": "relaxed, informal, comfortable, everyday, simple, natural"
        }
        
        # Health tracking with optimized data structures
        self._health_history = []
        self._last_health_check = None
        self._consecutive_failures = 0
        self._health_lock = asyncio.Lock()
        
        # Performance metrics
        self._response_times = []
        self._success_count = 0
        self._total_requests = 0
    
    @property
    def provider_name(self) -> str:
        """Return the name of this provider"""
        return "runware"
    
    @property
    def provider_version(self) -> str:
        """Return the version of this provider"""
        return "1.0.0"
    
    async def initialize(self) -> bool:
        """
        Initialize Runware client connection with retry logic.

        Returns:
            bool: True if initialization successful, False otherwise
        """
        if self._initialization_attempted:
            return self.is_connected

        self._initialization_attempted = True
        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                # Validate API key
                if not self.api_key:
                    logger.error("Runware API key is None or empty")
                    return False

                if not isinstance(self.api_key, str):
                    logger.error(f"Runware API key must be string, got {type(self.api_key)}")
                    return False

                if self.api_key == "your_runware_api_key_here":
                    logger.warning("Runware API key not configured (using placeholder)")
                    return False

                if len(self.api_key.strip()) < 10:
                    logger.error(f"Runware API key too short ({len(self.api_key)} chars)")
                    return False

                logger.info(f"Initializing Runware provider (attempt {attempt + 1}/{max_retries})...")

                # Create and connect client with timeout
                self.client = Runware(api_key=self.api_key.strip())

                # Connect with timeout
                connect_task = asyncio.create_task(self.client.connect())
                await asyncio.wait_for(connect_task, timeout=10.0)

                self.is_connected = True
                logger.info("🎨 RunwareProvider initialized successfully!")
                return True

            except asyncio.TimeoutError:
                logger.warning(f"Runware connection timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error("Failed to connect to Runware after all retries")
                    self.is_connected = False
                    return False

            except Exception as e:
                logger.error(f"Failed to initialize RunwareProvider (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    self.is_connected = False
                    return False

        return False
    
    async def generate_image(self, request: GenerationRequest) -> GenerationResponse:
        """
        Optimized image generation using Runware API with connection pooling.

        Args:
            request: Generation request parameters

        Returns:
            GenerationResponse: Standardized response with image data or error
        """
        start_time = time.time()
        client = None

        try:
            # Input validation
            if not request:
                return self._create_error_response(
                    None,
                    "Request is None", start_time
                )

            if not isinstance(request, GenerationRequest):
                return self._create_error_response(
                    None,
                    f"Invalid request type: {type(request)}", start_time
                )

            # Ensure provider is initialized
            if not self.is_connected:
                logger.info("Provider not connected, attempting to initialize...")
                if not await self.initialize():
                    return self._create_error_response(
                        request, "Runware service unavailable", start_time
                    )

            # Validate request parameters
            validation_errors = await self.validate_request(request)
            if validation_errors:
                logger.warning(f"Request validation failed: {validation_errors}")
                return self._create_error_response(
                    request, f"Validation errors: {', '.join(validation_errors)}", start_time
                )
            
            # Get client from pool with timeout
            try:
                client = await asyncio.wait_for(
                    self._get_client_from_pool(),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                logger.error("Timeout getting client from pool")
                return self._create_error_response(
                    request, "Timeout getting client from pool", start_time
                )

            if not client:
                return self._create_error_response(
                    request, "Failed to get client from pool", start_time
                )

            # Enhance prompt with caching (with error handling)
            try:
                enhanced_prompt = self._enhance_prompt_cached(request.prompt, request.style)
                if not enhanced_prompt or len(enhanced_prompt.strip()) == 0:
                    enhanced_prompt = request.prompt + ", high quality, detailed"
            except Exception as e:
                logger.warning(f"Prompt enhancement failed: {e}, using original prompt")
                enhanced_prompt = request.prompt

            # Get cached model configuration
            try:
                config = await asyncio.wait_for(
                    self._get_cached_config(request.quality),
                    timeout=1.0
                )
            except asyncio.TimeoutError:
                logger.warning("Config fetch timeout, using default")
                config = self.model_configs[GenerationQuality.STANDARD]
            except Exception as e:
                logger.warning(f"Failed to get config: {e}, using default")
                config = self.model_configs[GenerationQuality.STANDARD]

            # Prepare Runware request with validation
            try:
                runware_request = IImageInference(
                    positivePrompt=enhanced_prompt,
                    model=config["model"],
                    width=max(256, min(2048, request.width)),  # Clamp width
                    height=max(256, min(2048, request.height)),  # Clamp height
                    negativePrompt=request.negative_prompt if request.negative_prompt else None,
                    steps=request.steps if request.steps else config["steps"],
                    CFGScale=request.guidance_scale if request.guidance_scale else config["guidance_scale"],
                    seed=request.seed if request.seed and request.seed > 0 else None,
                    numberResults=1
                )

                # Add reference image if provided (image-to-image)
                if request.reference_image:
                    # Runware accepts data URI strings directly for seedImage
                    try:
                        # Pass the data URI directly - Runware SDK handles the conversion
                        runware_request.seedImage = request.reference_image

                        # Set strength for image-to-image generation
                        if request.image_strength is not None:
                            runware_request.strength = max(0.0, min(1.0, request.image_strength))
                        else:
                            runware_request.strength = 0.8  # Default strength

                        logger.info(f"Using seed image for image-to-image generation with strength {runware_request.strength}")
                    except Exception as e:
                        logger.error(f"Failed to process seed image: {e}")
                        # Continue without seed image rather than failing completely
                        pass

                # Add mask for inpainting
                if request.mask_image:
                    runware_request.maskImage = request.mask_image

            except Exception as e:
                logger.error(f"Failed to create Runware request: {e}")
                return self._create_error_response(
                    request, f"Invalid request parameters: {e}", start_time
                )

            # Generate image with timeout
            logger.info(f"Generating image with Runware: {enhanced_prompt[:50]}...")
            try:
                generation_timeout = request.timeout if hasattr(request, 'timeout') else 60.0
                result = await asyncio.wait_for(
                    client.imageInference(requestImage=runware_request),
                    timeout=generation_timeout
                )
            except asyncio.TimeoutError:
                logger.error(f"Image generation timeout after {generation_timeout}s")
                self._consecutive_failures += 1
                return self._create_error_response(
                    request, f"Generation timeout after {generation_timeout}s", start_time
                )
            
            if not result or len(result) == 0:
                self._consecutive_failures += 1
                return self._create_error_response(
                    request, "No image generated", start_time
                )
            
            image_result = result[0]
            processing_time = time.time() - start_time
            
            # Update performance metrics
            self._response_times.append(processing_time)
            self._total_requests += 1
            self._success_count += 1
            self._consecutive_failures = 0
            
            # Keep only last 100 response times
            if len(self._response_times) > 100:
                self._response_times = self._response_times[-100:]
            
            return GenerationResponse(
                success=True,
                generation_id=f"runware_{getattr(image_result, 'imageUUID', int(time.time()))}",
                image_data=getattr(image_result, 'imageURL', ''),
                provider_used=self.provider_name,
                provider_version=self.provider_version,
                cost=getattr(image_result, 'cost', 0.0),
                processing_time=processing_time,
                seed=getattr(image_result, 'seed', None),
                steps_used=config["steps"],
                guidance_scale_used=config["guidance_scale"],
                metadata={
                    "image_uuid": getattr(image_result, 'imageUUID', None),
                    "task_uuid": getattr(image_result, 'taskUUID', None),
                    "model_used": config["model"],
                    "enhanced_prompt": enhanced_prompt,
                    "style_applied": request.style,
                    "quality_tier": request.quality.value
                }
            )
            
        except Exception as e:
            self._consecutive_failures += 1
            self._total_requests += 1
            logger.error(f"Runware generation failed: {e}")
            return self._create_error_response(request, str(e), start_time)
        
        finally:
            # Return client to pool
            if client:
                await self._return_client_to_pool(client)
    
    async def generate_batch(self, request: BatchGenerationRequest) -> BatchGenerationResponse:
        """Generate multiple images concurrently"""
        start_time = time.time()
        
        try:
            # Ensure provider is initialized
            if not self.is_connected:
                if not await self.initialize():
                    return BatchGenerationResponse(
                        success=False,
                        results=[self._create_error_response(
                            req, "Runware service unavailable", start_time
                        ) for req in request.requests],
                        total_processing_time=time.time() - start_time,
                        successful_count=0,
                        failed_count=len(request.requests)
                    )
            
            # Use semaphore to limit concurrent requests
            semaphore = asyncio.Semaphore(request.max_concurrent)
            
            async def generate_single(req: GenerationRequest) -> GenerationResponse:
                async with semaphore:
                    return await self.generate_image(req)
            
            # Generate all images concurrently
            tasks = [generate_single(req) for req in request.requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append(self._create_error_response(
                        request.requests[i], str(result), start_time
                    ))
                else:
                    processed_results.append(result)
            
            successful_count = sum(1 for r in processed_results if r.success)
            failed_count = len(processed_results) - successful_count
            total_cost = sum(r.cost or 0 for r in processed_results)
            
            return BatchGenerationResponse(
                success=failed_count == 0 or not request.fail_fast,
                results=processed_results,
                total_cost=total_cost,
                total_processing_time=time.time() - start_time,
                successful_count=successful_count,
                failed_count=failed_count
            )
            
        except Exception as e:
            logger.error(f"Runware batch generation failed: {e}")
            return BatchGenerationResponse(
                success=False,
                results=[self._create_error_response(
                    req, str(e), start_time
                ) for req in request.requests],
                total_processing_time=time.time() - start_time,
                successful_count=0,
                failed_count=len(request.requests)
            )
    
    async def get_service_health(self) -> ServiceHealth:
        """Check Runware service health"""
        try:
            current_time = datetime.utcnow()
            
            # Use cached health if recent
            if (self._last_health_check and 
                (current_time - self._last_health_check).seconds < 30):
                return self._get_cached_health()
            
            # Check if provider is initialized
            if not self.is_connected:
                if not await self.initialize():
                    return ServiceHealth(
                        status=ServiceStatus.UNAVAILABLE,
                        metadata={"error": "Failed to initialize"}
                    )
            
            # Perform health check with minimal request
            start_time = time.time()
            test_request = GenerationRequest(
                prompt="test health check",
                user_id="health_check",
                quality=GenerationQuality.FAST,
                width=512,
                height=512
            )
            
            result = await self.generate_image(test_request)
            response_time = time.time() - start_time
            
            # Determine health status
            if result.success and response_time < 10:
                status = ServiceStatus.HEALTHY
            elif result.success and response_time < 30:
                status = ServiceStatus.DEGRADED
            elif self._consecutive_failures < 3:
                status = ServiceStatus.UNHEALTHY
            else:
                status = ServiceStatus.UNAVAILABLE
            
            # Update health history
            health = ServiceHealth(
                status=status,
                response_time=response_time,
                error_rate=self._consecutive_failures / max(len(self._health_history), 1),
                metadata={
                    "consecutive_failures": self._consecutive_failures,
                    "last_success": result.success,
                    "test_generation_id": result.generation_id
                }
            )
            
            self._health_history.append(health)
            self._last_health_check = current_time
            
            # Keep only last 10 health checks
            if len(self._health_history) > 10:
                self._health_history = self._health_history[-10:]
            
            return health
            
        except Exception as e:
            logger.error(f"Runware health check failed: {e}")
            return ServiceHealth(
                status=ServiceStatus.UNAVAILABLE,
                metadata={"error": str(e)}
            )
    
    async def estimate_cost(self, request: GenerationRequest) -> CostEstimate:
        """Estimate cost for generation request"""
        try:
            config = self.model_configs.get(request.quality, self.model_configs[GenerationQuality.STANDARD])
            base_cost = config["cost_per_image"]
            
            # Adjust for image size
            size_multiplier = (request.width * request.height) / (1024 * 1024)
            
            # Adjust for steps
            steps_multiplier = (request.steps or config["steps"]) / 20
            
            # Adjust for guidance scale
            guidance_multiplier = (request.guidance_scale or config["guidance_scale"]) / 7.5
            
            estimated_cost = base_cost * size_multiplier * steps_multiplier * guidance_multiplier
            
            return CostEstimate(
                estimated_cost=estimated_cost,
                currency="USD",
                breakdown={
                    "base_cost": base_cost,
                    "size_multiplier": size_multiplier,
                    "steps_multiplier": steps_multiplier,
                    "guidance_multiplier": guidance_multiplier
                },
                confidence=0.9  # High confidence for Runware estimates
            )
            
        except Exception as e:
            logger.error(f"Cost estimation failed: {e}")
            return CostEstimate(
                estimated_cost=0.02,  # Default estimate
                currency="USD",
                confidence=0.5
            )
    
    async def close(self) -> None:
        """Close Runware connection"""
        if self.client and self.is_connected:
            try:
                # Runware SDK doesn't have a close method, just mark as disconnected
                self.is_connected = False
                self.client = None
                logger.info("Runware connection closed")
            except Exception as e:
                logger.error(f"Error closing Runware connection: {e}")
    
    async def get_supported_models(self) -> List[str]:
        """Get list of supported models"""
        return ["runware:101@1"]  # Add more models as they become available
    
    async def get_supported_styles(self) -> List[str]:
        """Get list of supported styles"""
        return list(self.style_presets.keys())
    
    async def validate_request(self, request: GenerationRequest) -> List[str]:
        """Validate generation request"""
        errors = []
        
        # Check prompt length
        if len(request.prompt.strip()) < 1:
            errors.append("Prompt cannot be empty")
        
        if len(request.prompt) > 2000:
            errors.append("Prompt too long (max 2000 characters)")
        
        # Check image dimensions
        if request.width < 256 or request.width > 2048:
            errors.append("Width must be between 256 and 2048 pixels")
        
        if request.height < 256 or request.height > 2048:
            errors.append("Height must be between 256 and 2048 pixels")
        
        # Check steps
        if request.steps and (request.steps < 1 or request.steps > 100):
            errors.append("Steps must be between 1 and 100")
        
        # Check guidance scale
        if request.guidance_scale and (request.guidance_scale < 1.0 or request.guidance_scale > 20.0):
            errors.append("Guidance scale must be between 1.0 and 20.0")
        
        # Check image strength (only if provided)
        if request.image_strength is not None and (request.image_strength < 0.0 or request.image_strength > 1.0):
            errors.append("Image strength must be between 0.0 and 1.0")
        
        return errors
    
    @lru_cache(maxsize=128)
    def _enhance_prompt_cached(self, prompt: str, style: Optional[str] = None) -> str:
        """Cached prompt enhancement for better performance"""
        enhanced = prompt.strip()
        
        if style and style in self.style_presets:
            enhanced += f", {self.style_presets[style]}"
        
        # Add quality enhancements
        enhanced += ", high quality, detailed, professional"
        
        return enhanced
    
    async def _get_client_from_pool(self) -> Optional[Runware]:
        """Get client from connection pool for better performance"""
        async with self._pool_lock:
            if self._connection_pool:
                return self._connection_pool.pop()
            
            # Create new client if pool is empty
            try:
                client = Runware(api_key=self.api_key)
                await client.connect()
                return client
            except Exception as e:
                logger.error(f"Failed to create new client: {e}")
                return None
    
    async def _return_client_to_pool(self, client: Runware):
        """Return client to connection pool"""
        async with self._pool_lock:
            if len(self._connection_pool) < self._connection_pool_size:
                self._connection_pool.append(client)
            else:
                # Runware SDK doesn't have a close method, just discard excess clients
                pass
    
    async def _get_cached_config(self, quality: GenerationQuality) -> Dict[str, Any]:
        """Get cached model configuration"""
        cache_key = f"config_{quality.value}"
        
        async with self._cache_lock:
            if cache_key in self._request_cache:
                return self._request_cache[cache_key]
        
        config = self.model_configs.get(quality, self.model_configs[GenerationQuality.STANDARD])
        
        async with self._cache_lock:
            self._request_cache[cache_key] = config
        
        return config
    
    def _create_error_response(self, request: Optional[GenerationRequest], error: str, start_time: float) -> GenerationResponse:
        """Create error response with safe null handling"""
        return GenerationResponse(
            success=False,
            generation_id=f"runware_error_{int(time.time())}",
            image_data="",
            provider_used=self.provider_name,
            provider_version=self.provider_version,
            processing_time=time.time() - start_time,
            error=error,
            metadata={"request_id": request.request_id if request else "unknown"}
        )
    
    def _get_cached_health(self) -> ServiceHealth:
        """Get cached health information"""
        if self._health_history:
            return self._health_history[-1]
        
        return ServiceHealth(
            status=ServiceStatus.UNAVAILABLE,
            metadata={"error": "No health history available"}
        )
