"""
Services initialization and dependency injection
"""

from app.core.config import settings
from app.core.logging import logger


def get_storage_service():
    """
    Get storage service based on configuration
    Returns LocalStorageService or StorageService (Firebase)
    """
    if settings.USE_LOCAL_STORAGE:
        logger.info("Using local storage service (development mode)")
        from app.services.local_storage_service import LocalStorageService
        return LocalStorageService()
    else:
        logger.info("Using Firebase Cloud Storage (production mode)")
        from app.services.storage_service import StorageService
        return StorageService()


__all__ = ['get_storage_service']