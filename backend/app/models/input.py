"""
Input processing models
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any
from enum import Enum


class InputType(str, Enum):
    """Supported input types"""
    PINTEREST_URL = "pinterest_url"
    MANUAL_UPLOAD = "manual_upload"
    TEXT_PROMPT = "text_prompt"


class PinterestUrlRequest(BaseModel):
    """Pinterest URL input request"""
    url: HttpUrl
    user_id: str


class PromptRequest(BaseModel):
    """Text prompt input request"""
    prompt: str = Field(..., min_length=10, max_length=1000)
    user_id: str


class ProcessedInput(BaseModel):
    """Processed input data"""
    source: InputType
    image_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProcessedInputResponse(BaseModel):
    """Response from input processing"""
    success: bool
    input_id: Optional[str] = None
    image_url: Optional[str] = None
    message: str = ""
    next_step: str = ""
    fallback_action: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)

