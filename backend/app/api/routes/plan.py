"""
Party plan generation and management routes
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Optional, List

from app.core.logging import logger
from app.models.plan import (
    PlanGenerationRequest,
    PlanResponse,
    PartyPlan
)
from app.models.vision import SceneData
from app.services.plan_generator import get_plan_generator

router = APIRouter()


@router.post("/plan/generate", response_model=PlanResponse)
async def generate_plan(request: PlanGenerationRequest) -> PlanResponse:
    """
    Generate a comprehensive party plan from vision analysis.
    
    Args:
        request: PlanGenerationRequest with scene_data and user_context
    
    Returns:
        PlanResponse with generated party plan
    """
    logger.info("Plan generation requested", has_scene_data=bool(request.scene_data))
    
    try:
        # Validate scene data
        if not request.scene_data:
            raise HTTPException(400, "scene_data is required")
        
        # Convert scene_data dict to SceneData object
        scene_data = SceneData(**request.scene_data)
        
        # Generate plan
        generator = get_plan_generator()
        plan = await generator.generate_plan(
            scene_data=scene_data,
            user_context=request.user_context or {}
        )
        
        logger.info(
            "Plan generated successfully",
            theme=plan.event.theme,
            categories=len(plan.checklist),
            budget_max=plan.budget_total_max
        )
        
        return PlanResponse(
            success=True,
            plan=plan,
            message=f"Generated comprehensive plan for {plan.event.theme} party"
        )
        
    except ValueError as e:
        logger.error("Plan generation validation error", error=str(e))
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error("Plan generation failed", error=str(e), exc_info=True)
        raise HTTPException(500, f"Failed to generate plan: {str(e)}")


@router.post("/plan/refine", response_model=PlanResponse)
async def refine_plan(
    plan: PartyPlan = Body(...),
    feedback: str = Body(...)
) -> PlanResponse:
    """
    Refine an existing party plan based on user feedback.
    
    Args:
        plan: Existing party plan
        feedback: User's modification request
    
    Returns:
        PlanResponse with updated party plan
    """
    logger.info("Plan refinement requested", feedback=feedback[:100])
    
    try:
        generator = get_plan_generator()
        updated_plan = await generator.refine_plan(
            existing_plan=plan,
            user_feedback=feedback
        )
        
        logger.info(
            "Plan refined successfully",
            version=updated_plan.version,
            changes=feedback[:50]
        )
        
        return PlanResponse(
            success=True,
            plan=updated_plan,
            message=f"Plan updated to version {updated_plan.version}"
        )
        
    except ValueError as e:
        logger.error("Plan refinement validation error", error=str(e))
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error("Plan refinement failed", error=str(e), exc_info=True)
        raise HTTPException(500, f"Failed to refine plan: {str(e)}")


@router.get("/plan/{plan_id}")
async def get_plan(plan_id: str):
    """
    Retrieve a specific plan by ID.
    TODO: Implement Firestore integration
    """
    logger.info("Get plan requested", plan_id=plan_id)
    raise HTTPException(501, "Plan storage/retrieval not yet implemented - coming in Firestore integration")


@router.put("/plan/{plan_id}")
async def update_plan(plan_id: str, plan: PartyPlan):
    """
    Update an existing plan.
    TODO: Implement Firestore integration
    """
    logger.info("Update plan requested", plan_id=plan_id)
    raise HTTPException(501, "Plan storage/retrieval not yet implemented - coming in Firestore integration")


@router.delete("/plan/{plan_id}")
async def delete_plan(plan_id: str):
    """
    Delete a plan.
    TODO: Implement Firestore integration
    """
    logger.info("Delete plan requested", plan_id=plan_id)
    raise HTTPException(501, "Plan storage/retrieval not yet implemented - coming in Firestore integration")


@router.get("/plans/user/{user_id}")
async def get_user_plans(user_id: str) -> List:
    """
    Get all plans for a user.
    TODO: Implement Firestore integration
    """
    logger.info("Get user plans requested", user_id=user_id)
    raise HTTPException(501, "Plan storage/retrieval not yet implemented - coming in Firestore integration")