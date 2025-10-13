"""
API Routes for Data Extraction
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from app.services.data_extraction_agent import data_extraction_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/extraction", tags=["data-extraction"])

class ExtractionRequest(BaseModel):
    input_text: str
    image_description: Optional[str] = None

class ExtractionResponse(BaseModel):
    extracted_data: Dict[str, Any]
    confidence: float
    missing_fields: list[str]
    suggestions: list[str]
    needs_user_input: bool
    error: Optional[str] = None

@router.post("/extract", response_model=ExtractionResponse)
async def extract_event_data(request: ExtractionRequest):
    """
    Extract structured event data from text and image description using LangGraph
    """
    try:
        logger.info(f"Extracting data from text: {request.input_text[:100]}...")
        
        result = await data_extraction_agent.extract_data(
            input_text=request.input_text,
            image_description=request.image_description
        )
        
        return ExtractionResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in data extraction endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data extraction failed: {str(e)}")

@router.post("/validate")
async def validate_party_content(request: ExtractionRequest):
    """
    Validate if the input content is party-related
    """
    try:
        # Use the validation from the agent
        combined_text = f"{request.input_text} {request.image_description or ''}".lower()
        
        party_keywords = (
            data_extraction_agent.event_types + 
            data_extraction_agent.themes + 
            data_extraction_agent.activities + 
            data_extraction_agent.food_keywords
        )
        
        has_party_content = any(keyword in combined_text for keyword in party_keywords)
        
        return {
            "is_party_related": has_party_content,
            "confidence": 85.0 if has_party_content else 15.0,
            "suggestions": [
                "Include party-related keywords like 'birthday', 'celebration', 'party theme'",
                "Mention decorations, activities, or food items"
            ] if not has_party_content else []
        }
        
    except Exception as e:
        logger.error(f"Error in validation endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")
