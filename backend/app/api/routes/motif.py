"""
Motif API Routes

Desktop-first party decoration image processing and room scene generation.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import asyncio

from ..services.motif import (
    PartyDecorationClassifier,
    PartyElementAnalyzer, 
    RoomSceneGenerator
)

router = APIRouter(prefix="/motif", tags=["motif"])

@router.post("/upload-and-classify")
async def upload_and_classify(file: UploadFile = File(...)):
    """Complete desktop task flow: upload -> classify -> analyze -> generate room scene"""
    
    try:
        # Step 1: Upload and validate
        image_data = await file.read()
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )
        
        # Step 2: Classify as party decoration
        classifier = PartyDecorationClassifier()
        classification_result = await classifier.classify_image(image_data)
        
        if not classification_result['is_party_decoration']:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Not a party decoration image",
                    "message": "Please upload an image containing balloons, banners, flowers, cake, or other party decorations.",
                    "confidence": classification_result['confidence']
                }
            )
        
        # Step 3: Analyze elements
        analyzer = PartyElementAnalyzer()
        elements = await analyzer.analyze_elements(image_data, classification_result)
        
        # Step 4: Generate 3D room scene
        scene_generator = RoomSceneGenerator()
        scene_3d = await scene_generator.generate_scene(elements)
        
        return {
            "success": True,
            "classification": classification_result,
            "elements": [
                {
                    "type": element.type.value,
                    "count": element.count,
                    "colors": element.colors,
                    "positions": element.positions,
                    "sizes": element.sizes
                }
                for element in elements
            ],
            "scene": {
                "id": scene_3d.id,
                "name": scene_3d.name,
                "elements": [
                    {
                        "id": element.id,
                        "type": element.type,
                        "geometry": element.geometry,
                        "material": element.material,
                        "position": element.position,
                        "rotation": element.rotation,
                        "scale": element.scale
                    }
                    for element in scene_3d.elements
                ],
                "lighting": scene_3d.lighting,
                "camera": scene_3d.camera,
                "environment": scene_3d.environment
            },
            "message": "Room scene generated successfully!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Processing failed",
                "message": str(e)
            }
        )

@router.get("/test-room-scene")
async def test_room_scene():
    """Test endpoint to generate a sample room scene"""
    
    try:
        # Create mock elements for testing
        from ..services.motif.room_scene_generator import DecorationElement, DecorationType
        
        mock_elements = [
            DecorationElement(
                type=DecorationType.BALLOONS,
                count=5,
                elements=[
                    {"center": [0, 2], "radius": 0.8, "color": "#ff69b4"},
                    {"center": [-3, 1.5], "radius": 0.7, "color": "#87ceeb"},
                    {"center": [3, 1.8], "radius": 0.75, "color": "#ffd700"},
                    {"center": [-5, 2.2], "radius": 0.65, "color": "#9370db"},
                    {"center": [5, 1.6], "radius": 0.68, "color": "#ff6347"}
                ],
                colors=["#ff69b4", "#87ceeb", "#ffd700", "#9370db", "#ff6347"],
                positions=[[0, 2], [-3, 1.5], [3, 1.8], [-5, 2.2], [5, 1.6]],
                sizes=[0.8, 0.7, 0.75, 0.65, 0.68]
            ),
            DecorationElement(
                type=DecorationType.BANNERS,
                count=1,
                elements=[
                    {"bbox": [0, 5.5, 8, 0.4], "colors": ["#ff1493"], "type": "banner"}
                ],
                colors=["#ff1493"],
                positions=[[0, 5.5]],
                sizes=[8, 0.4]
            ),
            DecorationElement(
                type=DecorationType.CONFETTI,
                count=15,
                elements=[
                    {"position": [0, 0, -2], "rotation": [0, 0, 0], "color": "#ff69b4"}
                    for _ in range(15)
                ],
                colors=["#ff69b4", "#87ceeb", "#ffd700", "#9370db", "#ff6347", "#32cd32"],
                positions=[[0, 0, -2] for _ in range(15)],
                sizes=[0.1, 0.2, 0.02]
            )
        ]
        
        # Generate room scene
        scene_generator = RoomSceneGenerator()
        scene_3d = await scene_generator.generate_scene(mock_elements)
        
        return {
            "success": True,
            "scene": {
                "id": scene_3d.id,
                "name": scene_3d.name,
                "elements": [
                    {
                        "id": element.id,
                        "type": element.type,
                        "geometry": element.geometry,
                        "material": element.material,
                        "position": element.position,
                        "rotation": element.rotation,
                        "scale": element.scale
                    }
                    for element in scene_3d.elements
                ],
                "lighting": scene_3d.lighting,
                "camera": scene_3d.camera,
                "environment": scene_3d.environment
            },
            "message": "Test room scene generated successfully!"
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Test failed",
                "message": str(e)
            }
        )
