"""
Vision AI processing routes
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from app.core.logging import logger
from app.core.errors import VisionProcessingError
from app.models.vision import VisionAnalysisRequest, VisionAnalysisResponse
from app.services.vision_processor import get_vision_processor
from app.services import get_storage_service
import uuid

router = APIRouter()


@router.post("/vision/analyze", response_model=VisionAnalysisResponse)
async def analyze_image(request: VisionAnalysisRequest) -> VisionAnalysisResponse:
    """
    Analyze party image using GPT-4 Vision API.
    
    Args:
        request: VisionAnalysisRequest with image_url
    
    Returns:
        VisionAnalysisResponse with scene data, objects, theme
    """
    logger.info(
        "Analyzing image with Vision AI",
        image_url=request.image_url,
        user_id=request.user_id
    )
    
    try:
        # Get vision processor
        processor = get_vision_processor()
        
        # Analyze image
        scene_data = await processor.analyze_party_image(request.image_url)
        
        logger.info(
            "Vision analysis successful",
            theme=scene_data.theme,
            objects_found=len(scene_data.objects),
            confidence=scene_data.confidence
        )
        
        # Convert to response format
        return VisionAnalysisResponse(
            success=True,
            scene=scene_data.to_dict()
        )
    
    except VisionProcessingError as e:
        logger.error(
            "Vision processing error",
            error=str(e),
            context=e.context,
            image_url=request.image_url
        )
        return VisionAnalysisResponse(
            success=False,
            error=str(e)
        )
    
    except Exception as e:
        logger.error(
            "Unexpected vision analysis error",
            error=str(e),
            image_url=request.image_url
        )
        raise HTTPException(500, f"Vision analysis failed: {str(e)}")


@router.post("/vision/upload")
async def upload_and_analyze(file: UploadFile = File(...)):
    """
    Upload an image file and analyze it using GPT-4 Vision API.
    
    Args:
        file: Image file to upload and analyze
    
    Returns:
        VisionAnalysisResponse with scene data
    """
    logger.info("Uploading and analyzing image", filename=file.filename)
    
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(400, "File must be an image")
        
        # Read file content
        content = await file.read()
        
        # Generate unique filename
        file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        original_filename = f"upload_{uuid.uuid4().hex[:12]}.{file_ext}"
        
        # Upload to storage (use anonymous user for now, TODO: add authentication)
        storage = get_storage_service()
        image_url = await storage.upload_image(
            content, 
            original_filename,
            user_id="anonymous",
            folder="uploads"
        )
        
        logger.info("Image uploaded", image_url=image_url)
        
        # Get vision processor
        processor = get_vision_processor()
        
        # Analyze image
        scene_data = await processor.analyze_party_image(image_url)
        
        logger.info(
            "Vision analysis successful",
            theme=scene_data.theme,
            objects_found=len(scene_data.objects)
        )
        
        # Return response
        return {
            "scene_data": scene_data.to_dict(),
            "image_url": image_url,
            "processing_time": 0  # TODO: Track actual processing time
        }
    
    except HTTPException:
        raise
    except VisionProcessingError as e:
        logger.error("Vision processing error", error=str(e))
        raise HTTPException(500, f"Vision analysis failed: {str(e)}")
    except Exception as e:
        logger.error("Upload and analyze failed", error=str(e))
        raise HTTPException(500, f"Failed to process image: {str(e)}")


@router.post("/vision/shopping-list")
async def generate_shopping_list(request: VisionAnalysisRequest):
    """
    Analyze image and generate shopping list.
    
    Args:
        request: VisionAnalysisRequest with image_url
    
    Returns:
        Shopping list with categories and cost estimates
    """
    logger.info("Generating shopping list", image_url=request.image_url)
    
    try:
        processor = get_vision_processor()
        
        # Analyze image
        scene_data = await processor.analyze_party_image(request.image_url)
        
        # Generate shopping list
        shopping_list = await processor.extract_shopping_list(scene_data)
        
        return {
            "success": True,
            "scene_summary": {
                "theme": scene_data.theme,
                "object_count": len(scene_data.objects)
            },
            "shopping_list": shopping_list
        }
    
    except Exception as e:
        logger.error("Shopping list generation failed", error=str(e))
        raise HTTPException(500, f"Failed to generate shopping list: {str(e)}")

