"""
Motif Elements Routes
"""

from fastapi import APIRouter

router = APIRouter(prefix="/elements", tags=["Elements"])

@router.get("/test")
async def test_elements():
    """Test elements endpoint"""
    return {"message": "Elements endpoint working"}
