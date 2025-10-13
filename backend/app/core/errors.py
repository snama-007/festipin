"""
Custom exception classes for the application
"""

from typing import Optional, Dict, Any


class ParxPlannerError(Exception):
    """Base exception for Parx Planner"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        self.message = message
        self.context = context or {}
        super().__init__(self.message)


class PinterestScrapingError(ParxPlannerError):
    """Raised when Pinterest scraping fails"""
    pass


class UserActionRequired(ParxPlannerError):
    """Raised when user action is needed (e.g., manual upload)"""
    def __init__(
        self, 
        message: str, 
        action: str, 
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, context)
        self.action = action


class VisionProcessingError(ParxPlannerError):
    """Raised when vision AI processing fails"""
    pass


class StorageError(ParxPlannerError):
    """Raised when storage operations fail"""
    pass


class ValidationError(ParxPlannerError):
    """Raised when data validation fails"""
    pass

