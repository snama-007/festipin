"""
Upload Route with Comprehensive Validation
Production-ready with security and performance optimizations
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import logging
import uuid
from datetime import datetime
import os

from app.models.motif import UploadResponse, ImageFormat
from app.utils.validators.file_validator import FileValidator, FileValidationError
from app.core.cache.redis_manager import redis_manager
# from app.services.motif.upload_service import UploadService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=200,
    summary="Upload decoration image",
    description="Upload a decoration image for AI processing. Supports JPEG, PNG, WEBP. Max 20MB.",
    responses={
        200: {
            "description": "Upload successful",
            "content": {
                "application/json": {
                    "example": {
                        "upload_id": "550e8400-e29b-41d4-a716-446655440000",
                        "image_url": "https://storage.googleapis.com/uploads/image.jpg",
                        "thumbnail_url": "https://storage.googleapis.com/uploads/image_thumb.jpg",
                        "estimated_processing_time": 45,
                        "image_dimensions": [1920, 1080],
                        "file_size": 2457600,
                        "format": "jpeg",
                        "created_at": "2025-01-13T10:30:00Z",
                        "status": "uploaded"
                    }
                }
            }
        },
        400: {"description": "Invalid file"},
        413: {"description": "File too large"},
        415: {"description": "Unsupported file type"},
        429: {"description": "Too many requests"},
        500: {"description": "Server error"}
    }
)
async def upload_decoration_image(
    file: UploadFile = File(
        ...,
        description="Image file (JPEG, PNG, WEBP, max 20MB)"
    ),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """
    Upload and validate decoration image

    Process:
    1. Validate file (type, size, content)
    2. Optimize and create thumbnail
    3. Upload to cloud storage
    4. Initialize processing state
    5. Return upload info

    Security measures:
    - File type validation (magic bytes)
    - Size limits enforced
    - Filename sanitization
    - Virus scanning (TODO)
    """
    upload_id = str(uuid.uuid4())
    start_time = datetime.utcnow()

    try:
        logger.info(f"📤 Upload started: {upload_id} - {file.filename}")

        # 1. Read file content
        try:
            file_content = await file.read()
        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            raise HTTPException(
                status_code=400,
                detail="Failed to read uploaded file"
            )

        # 2. Validate file
        is_valid, error_message, metadata = await FileValidator.validate_upload(
            file_content=file_content,
            filename=file.filename
        )

        if not is_valid:
            logger.warning(f"❌ Validation failed: {error_message}")
            raise HTTPException(
                status_code=400,
                detail=f"File validation failed: {error_message}"
            )

        # 3. Sanitize filename
        safe_filename = FileValidator.sanitize_filename(file.filename)
        logger.info(f"✅ File validated: {safe_filename} - {metadata}")

        # 4. Optimize image
        try:
            optimized_content, optimization_metadata = await FileValidator.optimize_image(
                file_content=file_content,
                max_dimension=2048,
                quality=85
            )
            logger.info(f"🎨 Image optimized: {optimization_metadata['compression_ratio']:.2%} size reduction")
        except FileValidationError as e:
            logger.error(f"Optimization failed: {e}")
            # Use original if optimization fails
            optimized_content = file_content
            optimization_metadata = {}

        # 5. Create thumbnail
        try:
            thumbnail_content = await FileValidator.create_thumbnail(
                file_content=file_content,
                size=(300, 300),
                quality=80
            )
            logger.info(f"🖼️ Thumbnail created")
        except FileValidationError as e:
            logger.error(f"Thumbnail creation failed: {e}")
            thumbnail_content = None

        # 6. Upload to cloud storage (mocked for now - implement with Firebase/S3)
        # TODO: Implement actual cloud storage upload
        image_url = f"https://storage.googleapis.com/festipin-uploads/{upload_id}/{safe_filename}"
        thumbnail_url = f"https://storage.googleapis.com/festipin-uploads/{upload_id}/thumb_{safe_filename}"

        # Simulate upload (replace with actual implementation)
        # await upload_service.upload_to_storage(upload_id, optimized_content, thumbnail_content)

        # 7. Store upload metadata in cache
        upload_metadata = {
            "upload_id": upload_id,
            "original_filename": file.filename,
            "safe_filename": safe_filename,
            "image_url": image_url,
            "thumbnail_url": thumbnail_url,
            "file_size": len(file_content),
            "optimized_size": len(optimized_content),
            "dimensions": [metadata["width"], metadata["height"]],
            "format": metadata["format"],
            "status": "uploaded",
            "created_at": start_time.isoformat(),
        }

        await redis_manager.set(
            f"motif:upload:{upload_id}",
            upload_metadata,
            ttl=3600  # 1 hour
        )

        # 8. Estimate processing time (based on image size and complexity)
        pixel_count = metadata["width"] * metadata["height"]
        estimated_time = min(
            max(15, int(pixel_count / 50000)),  # 15-120 seconds
            120
        )

        # 9. Schedule background processing (optional - can be triggered separately)
        # background_tasks.add_task(process_image_task, upload_id)

        # 10. Return response
        response = UploadResponse(
            upload_id=upload_id,
            image_url=image_url,
            thumbnail_url=thumbnail_url,
            estimated_processing_time=estimated_time,
            image_dimensions=(metadata["width"], metadata["height"]),
            file_size=len(file_content),
            format=ImageFormat(metadata["format"].lower()),
            created_at=start_time,
            status="uploaded"
        )

        elapsed = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"✅ Upload completed: {upload_id} in {elapsed:.2f}s")

        return response

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"❌ Upload failed: {upload_id} - {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )

    finally:
        # Cleanup
        await file.close()


@router.get(
    "/upload/{upload_id}",
    response_model=UploadResponse,
    summary="Get upload status",
    description="Retrieve upload information by ID"
)
async def get_upload_status(upload_id: str):
    """Get upload status and metadata"""
    try:
        # Validate UUID format
        try:
            uuid.UUID(upload_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid upload ID format"
            )

        # Get from cache
        upload_data = await redis_manager.get(f"motif:upload:{upload_id}")

        if not upload_data:
            raise HTTPException(
                status_code=404,
                detail=f"Upload not found: {upload_id}"
            )

        return upload_data

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error retrieving upload: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve upload information"
        )


@router.delete(
    "/upload/{upload_id}",
    status_code=204,
    summary="Delete upload",
    description="Delete an upload and its associated data"
)
async def delete_upload(upload_id: str):
    """Delete upload and cleanup resources"""
    try:
        # Validate UUID
        try:
            uuid.UUID(upload_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid upload ID format"
            )

        # Check if exists
        exists = await redis_manager.exists(f"motif:upload:{upload_id}")
        if not exists:
            raise HTTPException(
                status_code=404,
                detail=f"Upload not found: {upload_id}"
            )

        # Delete from cache
        deleted = await redis_manager.delete(
            f"motif:upload:{upload_id}",
            f"motif:processing:{upload_id}",
            f"motif:scene:{upload_id}"
        )

        # TODO: Delete from cloud storage
        # await upload_service.delete_from_storage(upload_id)

        logger.info(f"🗑️ Upload deleted: {upload_id} ({deleted} keys)")

        return JSONResponse(
            status_code=204,
            content=None
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error deleting upload: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete upload"
        )
