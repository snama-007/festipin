"""
Motif Module API Routes
Complete with validation, error handling, and monitoring
"""

from fastapi import APIRouter

# Import sub-routers
from .upload import router as upload_router
from .process import router as process_router
from .scene import router as scene_router
from .elements import router as elements_router
from .replacement import router as replacement_router
from .library import router as library_router
from .export import router as export_router
from .generation import router as generation_router
from .history import router as history_router
from .performance import router as performance_router

# Main router
router = APIRouter(prefix="/motif", tags=["Motif"])

# Include all sub-routers
router.include_router(upload_router)
router.include_router(process_router)
router.include_router(scene_router)
router.include_router(elements_router)
router.include_router(replacement_router)
router.include_router(library_router)
router.include_router(export_router)
router.include_router(generation_router)
router.include_router(history_router)
router.include_router(performance_router)

__all__ = ["router"]
