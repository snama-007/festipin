"""
Motif Processing Routes
"""

from fastapi import APIRouter

router = APIRouter(prefix="/process", tags=["Processing"])

@router.get("/test")
async def test_processing():
    """Test processing endpoint"""
    return {"message": "Processing endpoint working"}
