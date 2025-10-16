"""
Motif Export Routes
"""

from fastapi import APIRouter

router = APIRouter(prefix="/export", tags=["Export"])

@router.get("/test")
async def test_export():
    """Test export endpoint"""
    return {"message": "Export endpoint working"}
