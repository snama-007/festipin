"""
Input processing routes - Pinterest URLs, manual uploads, text prompts
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from enum import Enum
import time

from app.core.logging import logger
from app.core.errors import PinterestScrapingError, UserActionRequired, StorageError
from app.models.input import (
    InputType,
    ProcessedInputResponse,
    PinterestUrlRequest,
    PromptRequest
)
from app.services.pinterest_scraper import get_pinterest_scraper
from app.services import get_storage_service
from app.services.vision_processor import get_vision_processor

router = APIRouter()


@router.post("/input/process", response_model=ProcessedInputResponse)
async def process_input(
    input_type: InputType = Form(...),
    pinterest_url: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    prompt: Optional[str] = Form(None),
    user_id: str = Form(...)
) -> ProcessedInputResponse:
    """
    Universal input processor supporting:
    - Pinterest URLs (with scraping fallback)
    - Manual image uploads
    - Text prompts
    
    Returns:
        ProcessedInputResponse with input_id and processing status
    """
    logger.info(
        "Processing input",
        input_type=input_type,
        user_id=user_id
    )
    
    try:
        if input_type == InputType.PINTEREST_URL:
            if not pinterest_url:
                raise HTTPException(400, "pinterest_url required for PINTEREST_URL type")
            
            # Pinterest scraping with fallback strategies
            logger.info("Processing Pinterest URL", url=pinterest_url, user_id=user_id)
            
            try:
                scraper = get_pinterest_scraper()
                async with scraper:
                    # Extract pin metadata
                    pin_metadata = await scraper.extract_pin(pinterest_url)
                    
                    # Download image
                    image_bytes = await scraper.download_image(pin_metadata.image_url)
                    
                    logger.info(
                        "Pinterest extraction successful",
                        pin_id=pin_metadata.pin_id,
                        image_size_kb=round(len(image_bytes) / 1024, 2)
                    )
                    
                    # Upload to Cloud Storage
                    storage = get_storage_service()
                    storage_url = await storage.upload_image(
                        image_bytes=image_bytes,
                        filename=f"pinterest_{pin_metadata.pin_id}.jpg",
                        user_id=user_id,
                        folder="pinterest",
                        metadata={
                            "source": "pinterest",
                            "pin_id": pin_metadata.pin_id,
                            "original_url": pinterest_url
                        }
                    )
                    
                    logger.info(
                        "Image uploaded to storage",
                        storage_url=storage_url,
                        pin_id=pin_metadata.pin_id
                    )
                    
                    # Trigger vision processing
                    vision = get_vision_processor()
                    scene_data = await vision.analyze_party_image(storage_url)
                    
                    logger.info(
                        "Vision analysis complete",
                        theme=scene_data.theme,
                        objects_found=len(scene_data.objects)
                    )
                    
                    # TODO: Store input + scene_data in Firestore
                    
                    return ProcessedInputResponse(
                        success=True,
                        input_id=f"pin_{pin_metadata.pin_id}",
                        image_url=storage_url,
                        message=f"Successfully analyzed: {scene_data.theme}",
                        next_step="plan_generation",
                        context={
                            "pin_metadata": pin_metadata.to_dict(),
                            "storage_url": storage_url,
                            "scene_data": scene_data.to_dict()
                        }
                    )
                    
            except PinterestScrapingError as e:
                logger.error(
                    "Pinterest scraping failed",
                    error=str(e),
                    url=pinterest_url,
                    user_id=user_id
                )
                
                # Fallback: Ask user to upload manually
                return ProcessedInputResponse(
                    success=False,
                    fallback_action="manual_upload",
                    message="We couldn't fetch that Pinterest image. Please upload it manually.",
                    context={
                        "failed_url": pinterest_url,
                        "error": str(e)
                    }
                )
        
        elif input_type == InputType.MANUAL_UPLOAD:
            if not image:
                raise HTTPException(400, "image file required for MANUAL_UPLOAD type")
            
            # Validate image
            if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
                raise HTTPException(400, "Invalid image format. Use JPEG, PNG, or WebP")
            
            logger.info("Processing manual upload", filename=image.filename, user_id=user_id)
            
            try:
                # Read image bytes
                image_bytes = await image.read()
                
                # Upload to Cloud Storage
                storage = get_storage_service()
                storage_url = await storage.upload_image(
                    image_bytes=image_bytes,
                    filename=image.filename,
                    user_id=user_id,
                    folder="uploads",
                    metadata={
                        "source": "manual_upload",
                        "original_filename": image.filename
                    }
                )
                
                logger.info(
                    "Manual upload successful",
                    storage_url=storage_url,
                    filename=image.filename,
                    size_kb=round(len(image_bytes) / 1024, 2)
                )
                
                # Trigger vision processing
                vision = get_vision_processor()
                scene_data = await vision.analyze_party_image(storage_url)
                
                logger.info(
                    "Vision analysis complete",
                    theme=scene_data.theme,
                    objects_found=len(scene_data.objects)
                )
                
                # TODO: Store input + scene_data in Firestore
                
                return ProcessedInputResponse(
                    success=True,
                    input_id=f"upload_{user_id}_{int(time.time())}",
                    image_url=storage_url,
                    message=f"Successfully analyzed: {scene_data.theme}",
                    next_step="plan_generation",
                    context={
                        "storage_url": storage_url,
                        "filename": image.filename,
                        "scene_data": scene_data.to_dict()
                    }
                )
                
            except StorageError as e:
                logger.error(
                    "Storage upload failed",
                    error=str(e),
                    filename=image.filename
                )
                raise HTTPException(500, f"Failed to upload image: {str(e)}")
        
        elif input_type == InputType.TEXT_PROMPT:
            if not prompt:
                raise HTTPException(400, "prompt required for TEXT_PROMPT type")
            
            # TODO: Process text prompt
            logger.info("Processing text prompt", prompt=prompt[:100])
            return ProcessedInputResponse(
                success=True,
                input_id="temp_id",
                message="Prompt processed successfully",
                next_step="plan_generation"
            )
        
        else:
            raise HTTPException(400, f"Unsupported input type: {input_type}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error processing input", error=str(e), input_type=input_type)
        raise HTTPException(500, f"Failed to process input: {str(e)}")


@router.get("/input/status/{input_id}")
async def get_input_status(input_id: str):
    """Get processing status of an input"""
    # TODO: Implement status tracking
    return {
        "input_id": input_id,
        "status": "processing",
        "progress": 50
    }

