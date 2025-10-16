"""
Motif Scene Routes - STALLED (3D Feature Disabled)
"""

from fastapi import APIRouter

router = APIRouter(prefix="/scene", tags=["Scene - STALLED"])

@router.get("/test")
async def test_scene():
    """3D Scene endpoint - STALLED"""
    return {
        "message": "3D Scene feature is currently stalled",
        "status": "disabled",
        "reason": "Focusing on image generation instead"
    }

@router.get("/test-room-scene")
async def test_room_scene():
    """3D Room scene endpoint - STALLED"""
    return {
        "message": "3D Room scene generation is currently stalled",
        "status": "disabled", 
        "reason": "Focusing on Gemini Flash image generation",
        "alternative": "Use /motif/generation endpoints for image generation"
    }
