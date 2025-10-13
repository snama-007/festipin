"""
Sample Images API Routes
Provides access to sample pin images for testing
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from typing import List
from pydantic import BaseModel

router = APIRouter()

# Sample images directory
SAMPLE_DIR = Path(__file__).parent.parent.parent.parent / "sample_images"


class SampleImage(BaseModel):
    """Sample image metadata"""
    id: str
    filename: str
    url: str
    description: str
    estimated_theme: str


@router.get("/samples", response_model=List[SampleImage])
async def list_samples():
    """
    List all available sample pin images
    """
    samples = [
        {
            "id": "pin1",
            "filename": "pin1.jpeg",
            "url": "/api/v1/samples/pin1",
            "description": "Gold and white balloon party setup",
            "estimated_theme": "Elegant Birthday Party"
        },
        {
            "id": "pin2",
            "filename": "pin2.jpeg",
            "url": "/api/v1/samples/pin2",
            "description": "Colorful party decoration",
            "estimated_theme": "Vibrant Celebration"
        },
        {
            "id": "pin3",
            "filename": "pin3.jpeg",
            "url": "/api/v1/samples/pin3",
            "description": "Party setup with balloons and backdrop",
            "estimated_theme": "Modern Party Theme"
        }
    ]
    
    # Filter to only existing files
    available_samples = []
    for sample in samples:
        sample_path = SAMPLE_DIR / sample["filename"]
        if sample_path.exists():
            available_samples.append(SampleImage(**sample))
    
    return available_samples


@router.get("/samples/{sample_id}")
async def get_sample_image(sample_id: str):
    """
    Get a specific sample image by ID
    Returns the actual image file
    """
    # Map sample_id to filename
    filename_map = {
        "pin1": "pin1.jpeg",
        "pin2": "pin2.jpeg",
        "pin3": "pin3.jpeg"
    }
    
    if sample_id not in filename_map:
        raise HTTPException(404, f"Sample image '{sample_id}' not found")
    
    filename = filename_map[sample_id]
    image_path = SAMPLE_DIR / filename
    
    if not image_path.exists():
        raise HTTPException(404, f"Sample image file not found: {filename}")
    
    return FileResponse(
        image_path,
        media_type="image/jpeg",
        filename=filename
    )


@router.get("/samples/{sample_id}/metadata")
async def get_sample_metadata(sample_id: str):
    """
    Get metadata for a specific sample image
    """
    samples = await list_samples()
    
    for sample in samples:
        if sample.id == sample_id:
            return sample
    
    raise HTTPException(404, f"Sample '{sample_id}' not found")
