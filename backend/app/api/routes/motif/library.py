"""
Motif Library Routes
"""

from fastapi import APIRouter

router = APIRouter(prefix="/library", tags=["Library"])

@router.get("/test")
async def test_library():
    """Test library endpoint"""
    return {"message": "Library endpoint working"}
