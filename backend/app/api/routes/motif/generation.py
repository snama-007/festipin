"""
Motif Image Generation Routes

API endpoints for intelligent image generation with service management
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form, BackgroundTasks, Depends
from typing import Optional, List, Dict, Any
import logging
import uuid
import asyncio
from datetime import datetime

from app.core.config import settings
from app.services.motif.service_manager import ServiceManager
from app.services.motif.providers.base import GenerationRequest, GenerationQuality
from app.services.motif.history_service import GenerationHistoryService
from app.models.motif.generation import (
    ImageGenerationRequest,
    ImageGenerationResponse,
    StylePreset,
    GenerationStatus
)
from app.models.motif.history import GenerationHistory, GenerationType

router = APIRouter(prefix="/generation", tags=["Image Generation"])
logger = logging.getLogger(__name__)

# Initialize service manager
service_manager = ServiceManager()

async def get_service_manager():
    """Get or initialize service manager"""
    if not service_manager._initialized:
        await service_manager.initialize()
    return service_manager

@router.post("/generate-from-prompt", response_model=ImageGenerationResponse)
async def generate_from_prompt(
    request: ImageGenerationRequest,
    background_tasks: BackgroundTasks,
    manager: ServiceManager = Depends(get_service_manager)
):
    """Generate image from text prompt using intelligent provider selection"""
    try:
        # Validate request
        if not request.prompt or len(request.prompt.strip()) < 10:
            raise HTTPException(status_code=400, detail="Prompt must be at least 10 characters long")
        
        if len(request.prompt) > 1000:
            raise HTTPException(status_code=400, detail="Prompt must be less than 1000 characters")
        
        # Convert to standardized request format
        generation_request = GenerationRequest(
            prompt=request.prompt,
            style=request.style,
            width=1024,
            height=1024,
            quality=GenerationQuality.STANDARD,
            user_id=request.user_id or "anonymous"
        )
        
        # Generate image using service manager
        result = await manager.generate_image(generation_request)
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)
        
        # Store generation metadata in background
        background_tasks.add_task(
            _store_generation_metadata,
            result.generation_id,
            request.prompt,
            request.style,
            "text_to_image",
            result.image_data,
            request.user_id,
            result.provider_used
        )
        
        return ImageGenerationResponse(
            success=True,
            generation_id=result.generation_id,
            image_data=result.image_data,
            prompt_used=request.prompt,
            style_applied=request.style,
            generated_at=datetime.utcnow(),
            mock_mode=False,  # Real generation
            provider_used=result.provider_used,
            cost=result.cost,
            processing_time=result.processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/generate-from-inspiration")
async def generate_from_inspiration(
    inspiration_image: Optional[UploadFile] = File(None),
    prompt: Optional[str] = Form(None),
    style: Optional[str] = Form(None),
    user_id: str = Form("anonymous"),
    quality: str = Form("standard"),
    width: int = Form(1024),
    height: int = Form(1024),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    manager: ServiceManager = Depends(get_service_manager)
):
    """
    Unified image generation endpoint supporting:
    - Prompt only (text-to-image)
    - Inspiration image only (image-to-image)
    - Inspiration image + prompt (combined generation)

    At least one of prompt or inspiration_image must be provided.
    """
    try:
        # Validation: At least one input must be provided
        has_prompt = prompt and len(prompt.strip()) > 0
        has_image = inspiration_image is not None

        if not has_prompt and not has_image:
            raise HTTPException(
                status_code=400,
                detail="At least one of 'prompt' or 'inspiration_image' must be provided"
            )

        # Validate prompt if provided
        if has_prompt:
            if len(prompt.strip()) < 3:
                raise HTTPException(
                    status_code=400,
                    detail="Prompt must be at least 3 characters long"
                )
            if len(prompt) > 1000:
                raise HTTPException(
                    status_code=400,
                    detail="Prompt must be less than 1000 characters"
                )

        # Process inspiration image if provided
        image_data_uri = None
        generation_type = "text_to_image"

        if has_image:
            # Validate file type
            if not inspiration_image.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=400,
                    detail="Uploaded file must be an image (JPEG, PNG, WEBP, etc.)"
                )

            # Validate file size (max 10MB)
            file_size = 0
            image_data = await inspiration_image.read()
            file_size = len(image_data)

            if file_size > 10 * 1024 * 1024:  # 10MB limit
                raise HTTPException(
                    status_code=400,
                    detail="Image file size must be less than 10MB"
                )

            if file_size == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Image file is empty"
                )

            # Encode image to base64
            import base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            image_data_uri = f"data:{inspiration_image.content_type};base64,{image_base64}"

            # Determine generation type
            if has_prompt:
                generation_type = "image_to_image_with_prompt"
            else:
                generation_type = "image_to_image"

        # Map quality string to enum
        quality_map = {
            "fast": GenerationQuality.FAST,
            "standard": GenerationQuality.STANDARD,
            "premium": GenerationQuality.PREMIUM
        }
        quality_enum = quality_map.get(quality.lower(), GenerationQuality.STANDARD)

        # Create generation request
        # If no prompt provided but image is, use a default prompt
        effective_prompt = prompt if has_prompt else "Generate an image based on this inspiration"

        # Build request parameters
        request_params = {
            "prompt": effective_prompt,
            "style": style,
            "width": width,
            "height": height,
            "quality": quality_enum,
            "user_id": user_id
        }

        # Add image-specific parameters only if image is provided
        if has_image:
            request_params["reference_image"] = image_data_uri
            request_params["image_strength"] = 0.8

        generation_request = GenerationRequest(**request_params)

        logger.info(f"Generation request: type={generation_type}, has_prompt={has_prompt}, has_image={has_image}, style={style}")

        # Generate image using service manager
        result = await manager.generate_image(generation_request)

        if not result.success:
            raise HTTPException(status_code=400, detail=result.error or "Generation failed")

        # Store generation metadata in background
        background_tasks.add_task(
            _store_generation_metadata,
            result.generation_id,
            effective_prompt,
            style,
            generation_type,
            result.image_data,
            user_id,
            result.provider_used
        )

        return ImageGenerationResponse(
            success=True,
            generation_id=result.generation_id,
            image_data=result.image_data,
            prompt_used=effective_prompt,
            style_applied=style,
            generated_at=datetime.utcnow(),
            mock_mode=False,
            provider_used=result.provider_used,
            cost=result.cost,
            processing_time=result.processing_time
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/generate-batch")
async def generate_batch_images(
    request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    manager: ServiceManager = Depends(get_service_manager)
):
    """Generate multiple images in batch"""
    try:
        prompts = request.get("prompts", [])
        style = request.get("style")
        user_id = request.get("user_id", "anonymous")
        max_concurrent = request.get("max_concurrent", 3)
        
        # Validate request
        if not prompts or not isinstance(prompts, list):
            raise HTTPException(status_code=400, detail="Prompts must be a non-empty list")
        
        if len(prompts) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 prompts allowed per batch")
        
        # Validate each prompt
        for i, prompt in enumerate(prompts):
            if not isinstance(prompt, str) or len(prompt.strip()) < 10:
                raise HTTPException(status_code=400, detail=f"Prompt {i+1} must be at least 10 characters long")
            if len(prompt) > 1000:
                raise HTTPException(status_code=400, detail=f"Prompt {i+1} must be less than 1000 characters")
        
        # Convert to batch request
        from app.services.motif.providers.base import BatchGenerationRequest
        batch_request = BatchGenerationRequest(
            requests=[
                GenerationRequest(
                    prompt=prompt,
                    style=style,
                    width=1024,
                    height=1024,
                    quality=GenerationQuality.STANDARD,
                    user_id=user_id
                ) for prompt in prompts
            ],
            max_concurrent=max_concurrent
        )
        
        # Generate batch
        result = await manager.generate_batch(batch_request)
        
        if not result.success:
            raise HTTPException(status_code=400, detail="Batch generation failed")
        
        # Store generation metadata in background for each successful generation
        for gen in result.results:
            if gen.success:
                background_tasks.add_task(
                    _store_generation_metadata,
                    gen.generation_id,
                    gen.metadata.get("enhanced_prompt", ""),
                    style,
                    "batch_text_to_image",
                    gen.image_data,
                    user_id,
                    gen.provider_used
                )
        
        return {
            "success": True,
            "batch_id": result.batch_id,
            "total_prompts": len(prompts),
            "successful_count": result.successful_count,
            "failed_count": result.failed_count,
            "results": [
                {
                    "success": gen.success,
                    "generation_id": gen.generation_id,
                    "image_data": gen.image_data,
                    "provider_used": gen.provider_used,
                    "cost": gen.cost,
                    "processing_time": gen.processing_time,
                    "error": gen.error
                } for gen in result.results
            ],
            "total_cost": result.total_cost,
            "total_processing_time": result.total_processing_time,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/qualities")
async def get_available_qualities():
    """Get available quality settings"""
    try:
        return {
            "success": True,
            "qualities": [
                {"key": "fast", "name": "Fast", "description": "Quick generation with good quality"},
                {"key": "standard", "name": "Standard", "description": "Balanced speed and quality"},
                {"key": "premium", "name": "Premium", "description": "Highest quality generation"}
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get qualities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/styles")
async def get_available_styles():
    """Get available style presets"""
    try:
        return {
            "success": True,
            "styles": [
                {"key": "party", "name": "Party", "description": "Vibrant and festive decorations"},
                {"key": "elegant", "name": "Elegant", "description": "Sophisticated and refined style"},
                {"key": "fun", "name": "Fun", "description": "Playful and cheerful designs"},
                {"key": "romantic", "name": "Romantic", "description": "Soft and dreamy atmosphere"},
                {"key": "birthday", "name": "Birthday", "description": "Colorful birthday celebrations"},
                {"key": "wedding", "name": "Wedding", "description": "Elegant wedding decorations"},
                {"key": "holiday", "name": "Holiday", "description": "Festive holiday themes"},
                {"key": "corporate", "name": "Corporate", "description": "Professional business style"},
                {"key": "casual", "name": "Casual", "description": "Relaxed and informal"}
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get styles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback/{generation_id}")
async def submit_feedback(
    generation_id: str,
    rating: int = Form(..., ge=1, le=5),
    feedback: Optional[str] = Form(None)
):
    """Submit feedback for generated image"""
    try:
        # TODO: Implement feedback collection with service manager
        return {
            "success": True,
            "message": "Feedback submitted successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{generation_id}")
async def get_generation_status(generation_id: str):
    """Get generation status and metadata"""
    try:
        # TODO: Implement status tracking with service manager
        return {
            "success": True,
            "generation_id": generation_id,
            "status": "completed",
            "created_at": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _store_generation_metadata(
    generation_id: str,
    prompt: str,
    style: Optional[str],
    generation_type: str,
    image_data: str,
    user_id: Optional[str],
    provider_used: str
):
    """Store generation metadata for training data collection"""
    try:
        # TODO: Store in database
        metadata = {
            "generation_id": generation_id,
            "prompt": prompt,
            "style": style,
            "type": generation_type,
            "image_data": image_data[:100] + "..." if len(image_data) > 100 else image_data,  # Truncate for logging
            "user_id": user_id,
            "provider_used": provider_used,
            "timestamp": datetime.utcnow()
        }
        
        logger.info(f"Stored metadata for generation {generation_id} using {provider_used}")
        
    except Exception as e:
        logger.error(f"Failed to store metadata: {e}")