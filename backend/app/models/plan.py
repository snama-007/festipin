"""
Pydantic models for party plan structure
Comprehensive data models matching the PRD requirements
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ===== Event Details =====

class EventDetails(BaseModel):
    """Core event information"""
    event_type: str = Field(..., description="Type of event (birthday, wedding, baby shower, etc.)")
    theme: str = Field(..., description="Party theme")
    honoree_name: str = Field(default="Guest of Honor")
    honoree_age: Optional[int] = None
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    guest_count: int = Field(default=20)
    guest_age_range: Optional[List[int]] = None


# ===== Checklist Models =====

class ChecklistItem(BaseModel):
    """Individual checklist task"""
    task: str = Field(..., description="Task description")
    description: Optional[str] = None
    quantity: int = Field(default=1)
    estimated_cost_min: Optional[int] = None
    estimated_cost_max: Optional[int] = None
    vendor_type: Optional[str] = None
    priority: str = Field(default="medium", description="low, medium, high, critical")
    status: str = Field(default="pending", description="pending, in_progress, completed, cancelled")
    due_date: Optional[str] = None
    duration_minutes: Optional[int] = None
    diy_alternative: Optional[str] = None
    assigned_to: Optional[str] = None
    completed_at: Optional[str] = None
    notes: Optional[str] = None


class ChecklistCategory(BaseModel):
    """Category of checklist items"""
    name: str = Field(..., description="Category name (Decor, Food, Entertainment, etc.)")
    items: List[ChecklistItem] = Field(default_factory=list)
    
    @property
    def total_items(self) -> int:
        return len(self.items)
    
    @property
    def completed_items(self) -> int:
        return len([item for item in self.items if item.status == "completed"])


# ===== Budget Models =====

class BudgetItem(BaseModel):
    """Budget breakdown by category"""
    category: str
    amount_min: int
    amount_max: int
    items: List[str] = Field(default_factory=list)


# ===== Timeline Models =====

class TimelineTask(BaseModel):
    """Timeline task with date"""
    date: str
    task: str
    category: str
    status: str = Field(default="pending")
    notes: Optional[str] = None


# ===== Vendor Models =====

class VendorRecommendation(BaseModel):
    """Recommended vendor type"""
    type: str = Field(..., description="Type of vendor (Balloon Decorator, Caterer, etc.)")
    why_needed: str
    budget_range: List[int] = Field(default_factory=lambda: [0, 0])
    book_by: Optional[str] = None
    suggested_vendors: Optional[List[str]] = Field(default_factory=list)


# ===== Main Party Plan Model =====

class PartyPlan(BaseModel):
    """
    Complete party plan structure
    This is the core data model that drives the entire planner
    """
    # Event Details
    event: EventDetails
    
    # Checklist (organized by categories)
    checklist: List[ChecklistCategory] = Field(default_factory=list)
    
    # Budget
    budget_total_min: int = 0
    budget_total_max: int = 0
    budget_breakdown: List[BudgetItem] = Field(default_factory=list)
    
    # Timeline
    timeline: List[TimelineTask] = Field(default_factory=list)
    
    # Vendors
    vendors: List[VendorRecommendation] = Field(default_factory=list)
    
    # Additional Info
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # Vision Analysis Reference
    scene_analysis: Optional[Any] = None  # SceneData object
    
    # Metadata
    plan_id: Optional[str] = None
    user_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    version: int = 1
    status: str = Field(default="draft", description="draft, in_progress, finalized")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event": {
                    "event_type": "birthday",
                    "theme": "unicorn princess",
                    "honoree_name": "Sophia",
                    "honoree_age": 7,
                    "date": "2025-11-15",
                    "time": "2:00 PM - 5:00 PM",
                    "location": "Home backyard",
                    "guest_count": 20
                },
                "budget_total_min": 500,
                "budget_total_max": 1000,
                "status": "draft",
                "version": 1
            }
        }


# ===== API Request/Response Models =====

class PlanGenerationRequest(BaseModel):
    """Request to generate a new plan"""
    scene_analysis_id: Optional[str] = None
    scene_data: Optional[Dict] = None  # SceneData as dict
    user_context: Optional[Dict] = Field(
        default_factory=dict,
        description="User-provided context (name, date, budget, etc.)"
    )


class PlanRefinementRequest(BaseModel):
    """Request to refine an existing plan"""
    plan_id: str
    feedback: str = Field(..., description="User's modification request")


class PlanResponse(BaseModel):
    """API response with party plan"""
    success: bool
    plan: PartyPlan
    message: Optional[str] = None


class PlanListResponse(BaseModel):
    """API response with list of plans"""
    success: bool
    plans: List[PartyPlan]
    total: int


# ===== Plan Statistics =====

class PlanStatistics(BaseModel):
    """Computed statistics for a plan"""
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    completion_percentage: float
    total_budget_min: int
    total_budget_max: int
    days_until_event: Optional[int] = None
    overdue_tasks: int = 0
    high_priority_tasks: int = 0