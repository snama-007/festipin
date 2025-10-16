"""
Generation History API Routes

API endpoints for managing image generation history, favorites, and user statistics.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
import logging
from datetime import datetime

from app.models.motif.history import (
    GenerationHistoryRequest, GenerationHistoryResponse,
    FavoriteRequest, FavoriteResponse, TagRequest, TagResponse,
    GenerationStatsResponse, GenerationHistory, GenerationStatus, GenerationType
)
from app.services.motif.history_service import GenerationHistoryService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/history", tags=["Generation History"])

# Dependency to get history service
def get_history_service() -> GenerationHistoryService:
    return GenerationHistoryService()

@router.get("/{user_id}", response_model=GenerationHistoryResponse)
async def get_generation_history(
    user_id: str,
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    status: Optional[GenerationStatus] = Query(None, description="Filter by status"),
    generation_type: Optional[GenerationType] = Query(None, description="Filter by type"),
    style: Optional[str] = Query(None, description="Filter by style"),
    favorites_only: bool = Query(False, description="Show only favorites"),
    search_query: Optional[str] = Query(None, description="Search in prompts"),
    history_service: GenerationHistoryService = Depends(get_history_service)
):
    """Get generation history for a user with filtering and pagination"""
    try:
        request = GenerationHistoryRequest(
            user_id=user_id,
            limit=limit,
            offset=offset,
            status=status,
            generation_type=generation_type,
            style=style,
            favorites_only=favorites_only,
            search_query=search_query
        )
        
        response = await history_service.get_generation_history(request)
        return response
        
    except Exception as e:
        logger.error(f"Failed to get generation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/favorite", response_model=FavoriteResponse)
async def toggle_favorite(
    request: FavoriteRequest,
    history_service: GenerationHistoryService = Depends(get_history_service)
):
    """Toggle favorite status for a generation"""
    try:
        response = await history_service.toggle_favorite(request)
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to toggle favorite: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tags", response_model=TagResponse)
async def update_tags(
    request: TagRequest,
    history_service: GenerationHistoryService = Depends(get_history_service)
):
    """Add or remove tags from a generation"""
    try:
        if request.action not in ['add', 'remove']:
            raise HTTPException(status_code=400, detail="Action must be 'add' or 'remove'")
        
        response = await history_service.update_tags(request)
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/{user_id}", response_model=GenerationStatsResponse)
async def get_user_stats(
    user_id: str,
    history_service: GenerationHistoryService = Depends(get_history_service)
):
    """Get generation statistics for a user"""
    try:
        response = await history_service.get_user_stats(user_id)
        return response
        
    except Exception as e:
        logger.error(f"Failed to get user stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{generation_id}")
async def delete_generation(
    generation_id: str,
    user_id: str = Query(..., description="User ID"),
    history_service: GenerationHistoryService = Depends(get_history_service)
):
    """Delete a generation (soft delete)"""
    try:
        success = await history_service.delete_generation(generation_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Generation not found or unauthorized")
        
        return {"success": True, "message": "Generation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/favorites/{user_id}", response_model=GenerationHistoryResponse)
async def get_favorites(
    user_id: str,
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    history_service: GenerationHistoryService = Depends(get_history_service)
):
    """Get user's favorite generations"""
    try:
        request = GenerationHistoryRequest(
            user_id=user_id,
            limit=limit,
            offset=offset,
            favorites_only=True
        )
        
        response = await history_service.get_generation_history(request)
        return response
        
    except Exception as e:
        logger.error(f"Failed to get favorites: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent/{user_id}", response_model=GenerationHistoryResponse)
async def get_recent_generations(
    user_id: str,
    limit: int = Query(10, ge=1, le=50, description="Number of recent generations to return"),
    history_service: GenerationHistoryService = Depends(get_history_service)
):
    """Get user's recent generations"""
    try:
        request = GenerationHistoryRequest(
            user_id=user_id,
            limit=limit,
            offset=0
        )
        
        response = await history_service.get_generation_history(request)
        return response
        
    except Exception as e:
        logger.error(f"Failed to get recent generations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
