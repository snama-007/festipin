"""
Motif Replacement Routes
"""

from fastapi import APIRouter

router = APIRouter(prefix="/replacement", tags=["Replacement"])

@router.get("/test")
async def test_replacement():
    """Test replacement endpoint"""
    return {"message": "Replacement endpoint working"}
