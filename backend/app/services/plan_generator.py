"""
AI Party Plan Generator Service

Converts vision analysis data into comprehensive, structured party plans
using GPT-4 with function calling and structured outputs.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import logger
from app.models.vision import SceneData
from app.models.plan import (
    PartyPlan,
    EventDetails,
    ChecklistCategory,
    ChecklistItem,
    BudgetItem,
    TimelineTask,
    VendorRecommendation
)


class PlanGeneratorService:
    """
    Generates comprehensive party plans from vision analysis data
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o"  # Using GPT-4o for structured outputs
        
        logger.info("Plan generator initialized", model=self.model)
    
    def _build_plan_generation_prompt(self, scene_data: SceneData, user_context: Dict) -> str:
        """Build comprehensive prompt for plan generation"""
        
        return f"""You are an expert party planner AI. Generate a comprehensive, actionable party plan.

**Vision Analysis Data:**
- Theme: {scene_data.theme}
- Style: {', '.join(scene_data.style_tags) if scene_data.style_tags else 'Not specified'}
- Colors: {', '.join(scene_data.color_palette[:5]) if scene_data.color_palette else 'Not specified'}
- Detected Objects: {len(scene_data.objects)} items
- Layout: {scene_data.layout_type}
- Event Type: {scene_data.occasion_type or 'Not specified'}
- Age Range: {scene_data.age_range if scene_data.age_range else 'Not specified'}

**User Context:**
{json.dumps(user_context, indent=2)}

**Your Task:**
Create a detailed party plan including:
1. Event details (name, date, time, location)
2. Comprehensive checklist organized by categories (Decor, Food, Entertainment, Setup)
3. Budget breakdown with estimated costs
4. Timeline with key milestones
5. Vendor recommendations (generic, can be matched to local vendors later)
6. DIY alternatives where applicable

**Requirements:**
- Be specific and actionable
- Include realistic cost estimates (USD)
- Create a timeline working backwards from event date
- Suggest 3-5 vendor types needed
- Include setup/teardown tasks
- Add safety considerations for children's parties
- Make it parent/host-friendly

Return a structured JSON following this format:
{{
  "event": {{
    "type": "birthday",
    "theme": "gold and white balloons",
    "honoree_name": "Sophia",
    "honoree_age": 7,
    "date": "2025-11-02",
    "time": "2:00 PM - 5:00 PM",
    "location": "Home backyard",
    "guest_count": 20,
    "guest_age_range": [5, 9]
  }},
  "checklist": [
    {{
      "category": "Decor",
      "items": [
        {{
          "task": "Set up balloon arch",
          "description": "Gold and white balloon arch at entrance, approximately 8ft wide",
          "quantity": 1,
          "estimated_cost_min": 150,
          "estimated_cost_max": 300,
          "vendor_type": "balloon decorator",
          "priority": "high",
          "due_date": "2025-11-01",
          "duration_minutes": 60,
          "diy_alternative": "Purchase balloon kit from Party City ($50) and assemble 2 hours before"
        }}
      ]
    }}
  ],
  "budget": {{
    "total_min": 500,
    "total_max": 1000,
    "breakdown": [
      {{
        "category": "Decor",
        "amount_min": 200,
        "amount_max": 400,
        "items": ["Balloons", "Backdrop", "Table decor"]
      }}
    ]
  }},
  "timeline": [
    {{
      "date": "2025-10-20",
      "task": "Send invitations",
      "category": "Planning",
      "status": "pending"
    }}
  ],
  "vendors": [
    {{
      "type": "Balloon Decorator",
      "why_needed": "Professional balloon arch and column setup",
      "budget_range": [150, 300],
      "book_by": "2025-10-15"
    }}
  ],
  "notes": "Remember to confirm dietary restrictions with parents. Have backup indoor plan if weather is bad."
}}

Be creative, practical, and thorough!"""
    
    async def generate_plan(
        self,
        scene_data: SceneData,
        user_context: Optional[Dict] = None
    ) -> PartyPlan:
        """
        Generate a comprehensive party plan from vision analysis.
        
        Args:
            scene_data: Vision analysis results
            user_context: Additional user-provided context (name, date, budget, etc.)
        
        Returns:
            PartyPlan object with complete planning data
        """
        
        # Merge user context with defaults
        context = {
            "honoree_name": "Guest of Honor",
            "event_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "guest_count": 20,
            "budget_range": [500, 1500],
            "location_type": "home",
            **(user_context or {})
        }
        
        logger.info(
            "Generating party plan",
            theme=scene_data.theme,
            occasion_type=scene_data.occasion_type,
            context=context
        )
        
        try:
            # Build prompt
            prompt = self._build_plan_generation_prompt(scene_data, context)
            
            # Call GPT-4 with structured output
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert party planner AI that creates detailed, actionable party plans."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.7,  # Balanced creativity and consistency
                max_tokens=3000
            )
            
            # Parse response
            content = response.choices[0].message.content
            plan_data = json.loads(content)
            
            logger.info(
                "Plan generated successfully",
                categories=len(plan_data.get('checklist', [])),
                budget_min=plan_data.get('budget', {}).get('total_min'),
                timeline_items=len(plan_data.get('timeline', []))
            )
            
            # Convert to Pydantic model
            party_plan = self._parse_plan_data(plan_data, scene_data)
            
            return party_plan
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse plan JSON", error=str(e), content=content[:200])
            raise ValueError(f"Failed to parse generated plan: {str(e)}")
        except Exception as e:
            logger.error("Plan generation failed", error=str(e), exc_info=True)
            raise ValueError(f"Failed to generate plan: {str(e)}")
    
    def _parse_plan_data(self, data: Dict, scene_data: SceneData) -> PartyPlan:
        """Parse raw JSON into PartyPlan Pydantic model"""
        
        # Parse event details
        event_data = data.get('event', {})
        event_details = EventDetails(
            event_type=event_data.get('type', scene_data.occasion_type),
            theme=event_data.get('theme', scene_data.theme),
            honoree_name=event_data.get('honoree_name', 'Guest of Honor'),
            honoree_age=event_data.get('honoree_age'),
            date=event_data.get('date'),
            time=event_data.get('time'),
            location=event_data.get('location'),
            guest_count=event_data.get('guest_count', 20),
            guest_age_range=event_data.get('guest_age_range')
        )
        
        # Parse checklist
        checklist_categories = []
        for category_data in data.get('checklist', []):
            items = []
            for item_data in category_data.get('items', []):
                item = ChecklistItem(
                    task=item_data.get('task', ''),
                    description=item_data.get('description'),
                    quantity=item_data.get('quantity', 1),
                    estimated_cost_min=item_data.get('estimated_cost_min'),
                    estimated_cost_max=item_data.get('estimated_cost_max'),
                    vendor_type=item_data.get('vendor_type'),
                    priority=item_data.get('priority', 'medium'),
                    status=item_data.get('status', 'pending'),
                    due_date=item_data.get('due_date'),
                    duration_minutes=item_data.get('duration_minutes'),
                    diy_alternative=item_data.get('diy_alternative'),
                    assigned_to=item_data.get('assigned_to'),
                    completed_at=item_data.get('completed_at')
                )
                items.append(item)
            
            category = ChecklistCategory(
                name=category_data.get('category', 'Other'),
                items=items
            )
            checklist_categories.append(category)
        
        # Parse budget
        budget_data = data.get('budget', {})
        budget_items = []
        for breakdown in budget_data.get('breakdown', []):
            budget_item = BudgetItem(
                category=breakdown.get('category', ''),
                amount_min=breakdown.get('amount_min', 0),
                amount_max=breakdown.get('amount_max', 0),
                items=breakdown.get('items', [])
            )
            budget_items.append(budget_item)
        
        # Parse timeline
        timeline_tasks = []
        for task_data in data.get('timeline', []):
            task = TimelineTask(
                date=task_data.get('date', ''),
                task=task_data.get('task', ''),
                category=task_data.get('category', ''),
                status=task_data.get('status', 'pending')
            )
            timeline_tasks.append(task)
        
        # Parse vendors
        vendors = []
        for vendor_data in data.get('vendors', []):
            vendor = VendorRecommendation(
                type=vendor_data.get('type', ''),
                why_needed=vendor_data.get('why_needed', ''),
                budget_range=vendor_data.get('budget_range', [0, 0]),
                book_by=vendor_data.get('book_by')
            )
            vendors.append(vendor)
        
        # Create PartyPlan
        plan = PartyPlan(
            event=event_details,
            checklist=checklist_categories,
            budget_total_min=budget_data.get('total_min', 0),
            budget_total_max=budget_data.get('total_max', 0),
            budget_breakdown=budget_items,
            timeline=timeline_tasks,
            vendors=vendors,
            notes=data.get('notes', ''),
            scene_analysis=scene_data,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            version=1
        )
        
        return plan
    
    async def refine_plan(
        self,
        existing_plan: PartyPlan,
        user_feedback: str
    ) -> PartyPlan:
        """
        Refine an existing plan based on user feedback.
        
        Args:
            existing_plan: Current party plan
            user_feedback: User's modification request
        
        Returns:
            Updated PartyPlan
        """
        
        logger.info("Refining plan", feedback=user_feedback)
        
        try:
            prompt = f"""You are refining a party plan based on user feedback.

**Current Plan:**
{existing_plan.model_dump_json(indent=2)}

**User Feedback:**
{user_feedback}

**Task:**
Update the plan according to the user's request. Maintain the JSON structure and only modify what's needed.
Increment the version number.

Return the complete updated plan as JSON."""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful party planning assistant."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.5,
                max_tokens=3000
            )
            
            updated_data = json.loads(response.choices[0].message.content)
            updated_plan = self._parse_plan_data(updated_data, existing_plan.scene_analysis)
            updated_plan.version = existing_plan.version + 1
            updated_plan.updated_at = datetime.utcnow().isoformat()
            
            logger.info("Plan refined successfully", new_version=updated_plan.version)
            
            return updated_plan
            
        except Exception as e:
            logger.error("Plan refinement failed", error=str(e))
            raise ValueError(f"Failed to refine plan: {str(e)}")


def get_plan_generator() -> PlanGeneratorService:
    """Factory function for plan generator service"""
    return PlanGeneratorService()
