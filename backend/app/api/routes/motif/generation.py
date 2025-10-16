"""
Motif Image Generation Routes

API endpoints for Gemini Flash image generation
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form, BackgroundTasks, Depends
from typing import Optional, List, Dict, Any
import logging
import uuid
import asyncio
from datetime import datetime

from app.core.config import settings
from app.services.motif.gemini_image_generator import MotifGeminiGenerator
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

# Initialize Gemini generator
gemini_generator = None

async def get_gemini_generator():
    """Get or initialize Gemini generator"""
    global gemini_generator
    if gemini_generator is None:
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key:
            raise HTTPException(
                status_code=500, 
                detail="Gemini API key not configured"
            )
        gemini_generator = MotifGeminiGenerator(api_key)
        await gemini_generator.initialize()
    return gemini_generator

@router.post("/generate-from-prompt")
async def generate_from_prompt(
    request: ImageGenerationRequest,
    background_tasks: BackgroundTasks,
    generator: MotifGeminiGenerator = Depends(get_gemini_generator)
):
    """Generate image from text prompt only"""
    try:
        # Validate request
        if not request.prompt or len(request.prompt.strip()) < 10:
            raise HTTPException(status_code=400, detail="Prompt must be at least 10 characters long")
        
        if len(request.prompt) > 1000:
            raise HTTPException(status_code=400, detail="Prompt must be less than 1000 characters")
        
        # Generate image
        result = await generator.generate_image_from_prompt(
            prompt=request.prompt,
            style=request.style,
            user_id=request.user_id
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Store generation metadata in background
        background_tasks.add_task(
            _store_generation_metadata,
            result["generation_id"],
            request.prompt,
            request.style,
            "text_to_image",
            result.get("image_data"),
            request.user_id
        )
        
        # Save to history
        history_service = GenerationHistoryService()
        generation_history = GenerationHistory(
            id=result["generation_id"],
            user_id=request.user_id or "anonymous",
            prompt=request.prompt,
            enhanced_prompt=result["prompt_used"],
            style=request.style,
            generation_type=GenerationType.TEXT_TO_IMAGE,
            status=GenerationStatus.COMPLETED,
            image_data=result["image_data"],
            completed_at=datetime.utcnow(),
            metadata={"mock_mode": generator.mock_mode}
        )
        background_tasks.add_task(history_service.save_generation, generation_history)
        
        return ImageGenerationResponse(
            success=True,
            generation_id=result["generation_id"],
            image_data=result["image_data"],
            prompt_used=result["prompt_used"],
            style_applied=result["style_applied"],
            generated_at=datetime.utcnow(),
            mock_mode=generator.mock_mode
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

async def _mock_generation(prompt: str, style: Optional[str], user_id: Optional[str]) -> Dict[str, Any]:
    """Mock generation for testing"""
    import asyncio
    await asyncio.sleep(1)  # Simulate generation time
    
    enhanced_prompt = f"{prompt}, {style or 'default'} style, high quality, detailed, professional"
    
    return {
        "success": True,
        "image_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
        "prompt_used": enhanced_prompt,
        "style_applied": style,
        "generation_id": f"mock_{user_id}_{asyncio.get_event_loop().time()}"
    }

@router.post("/generate-batch")
async def generate_batch_images(
    request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    generator: MotifGeminiGenerator = Depends(get_gemini_generator)
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
        
        # Generate batch
        result = await generator.generate_batch_images(
            prompts=prompts,
            style=style,
            user_id=user_id,
            max_concurrent=max_concurrent
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Store generation metadata in background for each successful generation
        for gen in result["successful_generations"]:
            background_tasks.add_task(
                _store_generation_metadata,
                gen["generation_id"],
                gen["prompt"],
                style,
                "batch_text_to_image",
                gen.get("image_data"),
                user_id
            )
            
            # Save to history
            history_service = GenerationHistoryService()
            generation_history = GenerationHistory(
                id=gen["generation_id"],
                user_id=user_id,
                prompt=gen["prompt"],
                enhanced_prompt=gen["prompt_used"],
                style=style,
                generation_type=GenerationType.TEXT_TO_IMAGE,
                status=GenerationStatus.COMPLETED,
                image_data=gen["image_data"],
                completed_at=datetime.utcnow(),
                metadata={"batch_id": result["batch_id"], "mock_mode": generator.mock_mode}
            )
            background_tasks.add_task(history_service.save_generation, generation_history)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/generate-from-inspiration")
async def generate_from_inspiration(
    inspiration_image: UploadFile = File(...),
    prompt: str = Form(...),
    style: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Generate image from inspiration image + prompt"""
    try:
        # Validate file
        if not inspiration_image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read image data
        image_data = await inspiration_image.read()
        
        generator = await get_gemini_generator()
        
        # Generate image
        result = await generator.generate_image_from_inspiration(
            inspiration_image=image_data,
            prompt=prompt,
            style=style,
            user_id=user_id
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Store generation metadata in background
        background_tasks.add_task(
            _store_generation_metadata,
            result["generation_id"],
            prompt,
            style,
            "image_to_image",
            inspiration_analysis=result.get("inspiration_analysis")
        )
        
        return ImageGenerationResponse(
            success=True,
            generation_id=result["generation_id"],
            image_data=result["image_data"],
            prompt_used=result["prompt_used"],
            style_applied=result["style_applied"],
            generated_at=datetime.utcnow(),
            inspiration_analysis=result.get("inspiration_analysis")
        )
        
    except Exception as e:
        logger.error(f"Inspiration-based generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/qualities")
async def get_available_qualities(
    generator: MotifGeminiGenerator = Depends(get_gemini_generator)
):
    """Get available quality settings"""
    try:
        qualities = await generator.get_available_qualities()
        return {
            "success": True,
            "qualities": qualities
        }
    except Exception as e:
        logger.error(f"Failed to get qualities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/styles")
async def get_available_styles():
    """Get available style presets"""
    try:
        generator = await get_gemini_generator()
        styles = await generator.get_available_styles()
        
        return {
            "success": True,
            "styles": styles
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
        generator = await get_gemini_generator()
        
        success = await generator.collect_feedback(
            generation_id=generation_id,
            rating=rating,
            feedback=feedback
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to submit feedback")
        
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
        # TODO: Implement status tracking
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
    inspiration_analysis: Optional[Dict[str, Any]] = None
):
    """Store generation metadata for training data collection"""
    try:
        # TODO: Store in database
        metadata = {
            "generation_id": generation_id,
            "prompt": prompt,
            "style": style,
            "type": generation_type,
            "inspiration_analysis": inspiration_analysis,
            "timestamp": datetime.utcnow()
        }
        
        logger.info(f"Stored metadata for generation {generation_id}")
        
    except Exception as e:
        logger.error(f"Failed to store metadata: {e}")
