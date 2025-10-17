"""
Agent Registry and Router for LangGraph Orchestration

This module provides agent registration, routing, and execution management
for the agentic party planning system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from enum import Enum
import asyncio
import time
from dataclasses import dataclass

from app.core.logging import logger


class AgentType(Enum):
    """Available agent types"""
    INPUT_CLASSIFIER = "input_classifier"
    THEME = "theme_agent"
    CAKE = "cake_agent"
    VENUE = "venue_agent"
    CATERING = "catering_agent"
    BUDGET = "budget_agent"
    VENDOR = "vendor_agent"
    PLANNER = "planner_agent"


@dataclass
class AgentInput:
    """Standardized agent input"""
    agent_type: AgentType
    inputs: List[Dict[str, Any]]
    context: Dict[str, Any]
    event_id: str


@dataclass
class AgentOutput:
    """Standardized agent output"""
    agent_type: AgentType
    result: Dict[str, Any]
    confidence: float
    execution_time: float
    metadata: Dict[str, Any]


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.name = agent_type.value
        self.is_initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize agent resources"""
        pass
    
    @abstractmethod
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute agent logic"""
        pass
    
    @abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        """Return expected input schema"""
        pass
    
    @abstractmethod
    def get_output_schema(self) -> Dict[str, Any]:
        """Return output schema"""
        pass
    
    @abstractmethod
    def can_handle(self, inputs: List[Dict[str, Any]]) -> bool:
        """Check if agent can handle given inputs"""
        pass
    
    async def _execute_with_timing(self, agent_input: AgentInput) -> AgentOutput:
        """Execute with timing and error handling"""
        start_time = time.time()
        
        try:
            if not self.is_initialized:
                await self.initialize()
                self.is_initialized = True
            
            result = await self.execute(agent_input)
            execution_time = time.time() - start_time
            
            return AgentOutput(
                agent_type=self.agent_type,
                result=result.result,
                confidence=result.confidence,
                execution_time=execution_time,
                metadata=result.metadata
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error("Agent execution failed", 
                        agent=self.name, 
                        error=str(e), 
                        execution_time=execution_time)
            
            return AgentOutput(
                agent_type=self.agent_type,
                result={"error": str(e)},
                confidence=0.0,
                execution_time=execution_time,
                metadata={"error": True}
            )


class InputClassifierAgent(BaseAgent):
    """Classifies and routes inputs to appropriate agents"""
    
    def __init__(self):
        super().__init__(AgentType.INPUT_CLASSIFIER)
        self.routing_rules = {
            'cake': ['cake', 'dessert', 'sweet', 'tier', 'frosting'],
            'venue': ['venue', 'location', 'space', 'hall', 'room'],
            'catering': ['food', 'menu', 'catering', 'meal', 'dining'],
            'theme': ['theme', 'decor', 'decoration', 'style', 'aesthetic'],
            'budget': ['budget', 'cost', 'price', 'money', 'expensive'],
            'vendor': ['vendor', 'supplier', 'service', 'professional']
        }
    
    async def initialize(self) -> None:
        """Initialize classifier"""
        logger.info("Input classifier agent initialized")
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Classify inputs and determine routing"""
        classified_inputs = {}
        
        for input_item in agent_input.inputs:
            tags = input_item.get('tags', [])
            content = input_item.get('content', '').lower()
            source_type = input_item.get('source_type', '')
            
            # Determine which agents should handle this input
            target_agents = set()
            
            # Check tags
            for tag in tags:
                for category, keywords in self.routing_rules.items():
                    if any(keyword in tag.lower() for keyword in keywords):
                        target_agents.add(category)
            
            # Check content
            for category, keywords in self.routing_rules.items():
                if any(keyword in content for keyword in keywords):
                    target_agents.add(category)
            
            # Default routing based on source type
            if source_type == 'image':
                # Images might contain multiple elements
                target_agents.update(['theme', 'cake', 'venue'])
            elif source_type == 'url':
                target_agents.add('theme')
            
            # Always include theme agent for context
            target_agents.add('theme')
            
            # Store classification
            for agent in target_agents:
                if agent not in classified_inputs:
                    classified_inputs[agent] = []
                classified_inputs[agent].append(input_item)
        
        return AgentOutput(
            agent_type=self.agent_type,
            result={"classified_inputs": classified_inputs},
            confidence=0.9,
            execution_time=0.0,
            metadata={"routing_complete": True}
        )
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "inputs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source_type": {"type": "string"},
                            "content": {"type": "string"},
                            "tags": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }
            }
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "classified_inputs": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "array",
                        "items": {"type": "object"}
                    }
                }
            }
        }
    
    def can_handle(self, inputs: List[Dict[str, Any]]) -> bool:
        return len(inputs) > 0


class ThemeAgent(BaseAgent):
    """Detects and defines party themes"""
    
    def __init__(self):
        super().__init__(AgentType.THEME)
        self.theme_keywords = {
            'jungle': ['jungle', 'safari', 'animal', 'wild', 'nature'],
            'space': ['space', 'astronaut', 'galaxy', 'planet', 'rocket'],
            'princess': ['princess', 'castle', 'royal', 'crown', 'magic'],
            'superhero': ['superhero', 'batman', 'spiderman', 'superman', 'hero'],
            'unicorn': ['unicorn', 'rainbow', 'magical', 'sparkle', 'fairy'],
            'dinosaur': ['dinosaur', 'dino', 'prehistoric', 'fossil', 'jurassic']
        }
    
    async def initialize(self) -> None:
        """Initialize theme detection"""
        logger.info("Theme agent initialized")
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Detect theme from inputs"""
        theme_scores = {}
        
        for input_item in agent_input.inputs:
            content = input_item.get('content', '').lower()
            tags = [tag.lower() for tag in input_item.get('tags', [])]
            
            # Score each theme
            for theme, keywords in self.theme_keywords.items():
                score = 0
                
                # Check content
                for keyword in keywords:
                    if keyword in content:
                        score += 2
                
                # Check tags
                for tag in tags:
                    for keyword in keywords:
                        if keyword in tag:
                            score += 3
                
                theme_scores[theme] = theme_scores.get(theme, 0) + score
        
        # Determine primary theme
        if theme_scores:
            primary_theme = max(theme_scores, key=theme_scores.get)
            confidence = min(theme_scores[primary_theme] / 10.0, 1.0)
        else:
            primary_theme = "general"
            confidence = 0.5
        
        # Generate theme details
        theme_result = {
            "primary_theme": primary_theme,
            "theme_scores": theme_scores,
            "confidence": confidence,
            "colors": self._get_theme_colors(primary_theme),
            "decorations": self._get_theme_decorations(primary_theme),
            "activities": self._get_theme_activities(primary_theme)
        }
        
        return AgentOutput(
            agent_type=self.agent_type,
            result=theme_result,
            confidence=confidence,
            execution_time=0.0,
            metadata={"theme_detected": True}
        )
    
    def _get_theme_colors(self, theme: str) -> List[str]:
        """Get colors for theme"""
        color_map = {
            'jungle': ['green', 'brown', 'yellow', 'orange'],
            'space': ['blue', 'purple', 'silver', 'black'],
            'princess': ['pink', 'purple', 'gold', 'white'],
            'superhero': ['red', 'blue', 'yellow', 'black'],
            'unicorn': ['pink', 'purple', 'rainbow', 'white'],
            'dinosaur': ['green', 'brown', 'orange', 'yellow']
        }
        return color_map.get(theme, ['blue', 'white', 'silver'])
    
    def _get_theme_decorations(self, theme: str) -> List[str]:
        """Get decorations for theme"""
        decoration_map = {
            'jungle': ['animal balloons', 'leaf garlands', 'safari props'],
            'space': ['planet decorations', 'star lights', 'rocket props'],
            'princess': ['crowns', 'castle backdrop', 'magic wands'],
            'superhero': ['cape', 'mask', 'cityscape backdrop'],
            'unicorn': ['unicorn horns', 'rainbow streamers', 'sparkles'],
            'dinosaur': ['dino balloons', 'fossil props', 'volcano backdrop']
        }
        return decoration_map.get(theme, ['balloons', 'streamers', 'banners'])
    
    def _get_theme_activities(self, theme: str) -> List[str]:
        """Get activities for theme"""
        activity_map = {
            'jungle': ['animal charades', 'safari hunt', 'jungle obstacle course'],
            'space': ['planet making', 'rocket building', 'space exploration'],
            'princess': ['crown decorating', 'castle building', 'royal tea party'],
            'superhero': ['cape decorating', 'superhero training', 'city rescue'],
            'unicorn': ['horn making', 'rainbow crafts', 'magical story time'],
            'dinosaur': ['fossil digging', 'dino dance', 'prehistoric crafts']
        }
        return activity_map.get(theme, ['party games', 'crafts', 'dancing'])
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "inputs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "tags": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }
            }
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "primary_theme": {"type": "string"},
                "theme_scores": {"type": "object"},
                "confidence": {"type": "number"},
                "colors": {"type": "array", "items": {"type": "string"}},
                "decorations": {"type": "array", "items": {"type": "string"}},
                "activities": {"type": "array", "items": {"type": "string"}}
            }
        }
    
    def can_handle(self, inputs: List[Dict[str, Any]]) -> bool:
        return len(inputs) > 0


class CakeAgent(BaseAgent):
    """Handles cake planning and design"""
    
    def __init__(self):
        super().__init__(AgentType.CAKE)
        self.cake_types = ['birthday', 'wedding', 'anniversary', 'graduation']
        self.flavors = ['chocolate', 'vanilla', 'strawberry', 'red velvet', 'carrot']
        self.styles = ['traditional', 'modern', 'themed', 'custom']
    
    async def initialize(self) -> None:
        """Initialize cake agent"""
        logger.info("Cake agent initialized")
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Generate cake plan"""
        # Extract cake-related inputs
        cake_inputs = [inp for inp in agent_input.inputs 
                      if any(tag in inp.get('tags', []) for tag in ['cake', 'dessert', 'sweet'])]
        
        if not cake_inputs:
            return AgentOutput(
                agent_type=self.agent_type,
                result={"error": "No cake-related inputs found"},
                confidence=0.0,
                execution_time=0.0,
                metadata={"error": True}
            )
        
        # Analyze cake requirements
        cake_plan = {
            "cake_type": "birthday",  # Default
            "flavor": "chocolate",     # Default
            "style": "themed",
            "tiers": 2,
            "size": "medium",
            "decorations": [],
            "special_requests": [],
            "estimated_cost": {"min": 150, "max": 300},
            "bakery_suggestions": []
        }
        
        # Extract theme from context
        theme_context = agent_input.context.get('theme_result', {})
        if theme_context:
            primary_theme = theme_context.get('primary_theme', 'general')
            cake_plan['decorations'] = self._get_theme_cake_decorations(primary_theme)
        
        return AgentOutput(
            agent_type=self.agent_type,
            result=cake_plan,
            confidence=0.8,
            execution_time=0.0,
            metadata={"cake_planned": True}
        )
    
    def _get_theme_cake_decorations(self, theme: str) -> List[str]:
        """Get cake decorations based on theme"""
        decoration_map = {
            'jungle': ['animal figurines', 'leaf patterns', 'safari colors'],
            'space': ['planet toppers', 'star sprinkles', 'galaxy frosting'],
            'princess': ['crown topper', 'pink frosting', 'sparkles'],
            'superhero': ['superhero figurines', 'cityscape design', 'cape details'],
            'unicorn': ['unicorn horn', 'rainbow layers', 'magical sprinkles'],
            'dinosaur': ['dino topper', 'volcano design', 'prehistoric colors']
        }
        return decoration_map.get(theme, ['basic decorations', 'colored frosting'])
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "inputs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "tags": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }
            }
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "cake_type": {"type": "string"},
                "flavor": {"type": "string"},
                "style": {"type": "string"},
                "tiers": {"type": "integer"},
                "size": {"type": "string"},
                "decorations": {"type": "array", "items": {"type": "string"}},
                "estimated_cost": {
                    "type": "object",
                    "properties": {
                        "min": {"type": "integer"},
                        "max": {"type": "integer"}
                    }
                }
            }
        }
    
    def can_handle(self, inputs: List[Dict[str, Any]]) -> bool:
        return any('cake' in inp.get('tags', []) or 'dessert' in inp.get('tags', []) 
                  for inp in inputs)


class BudgetAgent(BaseAgent):
    """Handles budget estimation and cost planning"""
    
    def __init__(self):
        super().__init__(AgentType.BUDGET)
        self.cost_estimates = {
            'cake': {'min': 100, 'max': 500},
            'venue': {'min': 200, 'max': 1000},
            'catering': {'min': 300, 'max': 800},
            'decorations': {'min': 100, 'max': 400},
            'entertainment': {'min': 200, 'max': 600},
            'photography': {'min': 150, 'max': 400}
        }
    
    async def initialize(self) -> None:
        """Initialize budget agent"""
        logger.info("Budget agent initialized")
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Generate budget estimate from actual agent results"""
        # Get context from other agents
        agent_results = agent_input.context.get('agent_results', {})

        budget_breakdown = {}
        total_min = 0
        total_max = 0

        # Extract actual venue costs
        venue_result = agent_results.get('venue_agent', {})
        if venue_result and venue_result.get('recommended_venues'):
            venue = venue_result['recommended_venues'][0]
            venue_price = venue.get('daily_price', 0)
            if venue_price > 0:
                budget_breakdown['venue'] = {'min': venue_price, 'max': venue_price}
                total_min += venue_price
                total_max += venue_price
            else:
                # Free venue (permit required)
                budget_breakdown['venue'] = {'min': 0, 'max': 0, 'note': 'Free (permit required)'}

        # Extract actual bakery/cake costs
        cake_result = agent_results.get('cake_agent', {})
        if cake_result and cake_result.get('recommended_bakeries'):
            bakery = cake_result['recommended_bakeries'][0]
            price_range = bakery.get('price_range', {})
            if price_range:
                cake_min = price_range.get('small', 80)
                cake_max = price_range.get('large', 300)
                budget_breakdown['cake'] = {'min': cake_min, 'max': cake_max}
                total_min += cake_min
                total_max += cake_max
        elif cake_result:
            # Use estimated cost from cake agent if available
            estimated_cost = cake_result.get('estimated_cost', self.cost_estimates.get('cake', {}))
            if estimated_cost:
                budget_breakdown['cake'] = estimated_cost
                total_min += estimated_cost.get('min', 0)
                total_max += estimated_cost.get('max', 0)

        # Extract actual catering costs
        catering_result = agent_results.get('catering_agent', {})
        if catering_result and catering_result.get('estimated_total_cost'):
            catering_cost = catering_result['estimated_total_cost']
            budget_breakdown['catering'] = catering_cost
            total_min += catering_cost.get('min', 0)
            total_max += catering_cost.get('max', 0)

        # Extract actual vendor costs by category
        vendor_result = agent_results.get('vendor_agent', {})
        if vendor_result and vendor_result.get('vendors_by_category'):
            vendors_by_cat = vendor_result['vendors_by_category']

            for category, vendors in vendors_by_cat.items():
                if vendors and len(vendors) > 0:
                    # Use average price from recommended vendors
                    avg_price = vendors[0].get('avg_price', 0)
                    if avg_price > 0:
                        budget_breakdown[category] = {
                            'min': int(avg_price * 0.8),  # -20% estimate
                            'max': int(avg_price * 1.2)   # +20% estimate
                        }
                        total_min += budget_breakdown[category]['min']
                        total_max += budget_breakdown[category]['max']

        # Add default estimates for missing categories
        if not budget_breakdown:
            # Fallback to static estimates if no agent results available
            budget_breakdown = self.cost_estimates.copy()
            for costs in budget_breakdown.values():
                total_min += costs['min']
                total_max += costs['max']

        budget_plan = {
            "total_budget": {"min": total_min, "max": total_max},
            "breakdown": budget_breakdown,
            "recommendations": self._get_budget_recommendations(total_min, total_max),
            "cost_saving_tips": self._get_cost_saving_tips(),
            "data_source": "actual_agent_results" if agent_results else "estimates"
        }

        return AgentOutput(
            agent_type=self.agent_type,
            result=budget_plan,
            confidence=0.9 if agent_results else 0.6,
            execution_time=0.0,
            metadata={
                "budget_calculated": True,
                "based_on_actual_data": bool(agent_results)
            }
        )
    
    def _get_budget_recommendations(self, min_cost: int, max_cost: int) -> List[str]:
        """Get budget recommendations"""
        if max_cost > 2000:
            return ["Consider DIY decorations", "Look for package deals", "Book vendors early for discounts"]
        elif max_cost > 1000:
            return ["Compare vendor quotes", "Consider off-peak timing", "Limit guest count"]
        else:
            return ["Focus on essential items", "Use home venue", "DIY entertainment"]
    
    def _get_cost_saving_tips(self) -> List[str]:
        """Get cost saving tips"""
        return [
            "Book vendors 2-3 months in advance",
            "Consider weekday parties for better rates",
            "DIY decorations for personal touch",
            "Potluck style catering",
            "Use digital invitations"
        ]
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "context": {
                    "type": "object",
                    "properties": {
                        "agent_results": {"type": "object"}
                    }
                }
            }
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "total_budget": {
                    "type": "object",
                    "properties": {
                        "min": {"type": "integer"},
                        "max": {"type": "integer"}
                    }
                },
                "breakdown": {"type": "object"},
                "recommendations": {"type": "array", "items": {"type": "string"}},
                "cost_saving_tips": {"type": "array", "items": {"type": "string"}}
            }
        }
    
    def can_handle(self, inputs: List[Dict[str, Any]]) -> bool:
        return True  # Budget agent can always run


class VenueAgentEnhanced(BaseAgent):
    """Enhanced venue agent using mock database"""

    def __init__(self):
        super().__init__(AgentType.VENUE)
        self.mock_db = None

    async def initialize(self) -> None:
        """Initialize venue agent with mock database"""
        from app.services.mock_database import get_mock_database
        self.mock_db = get_mock_database()
        logger.info("Venue agent initialized with mock database")

    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Find venues using mock database"""
        # Extract requirements from inputs and context
        guest_count = self._extract_guest_count(agent_input.inputs)
        budget = self._extract_budget(agent_input.context)
        theme = agent_input.context.get('theme_result', {}).get('primary_theme', 'general')

        # Query mock PostgreSQL
        db_venues = self.mock_db.query_venues(
            min_capacity=guest_count,
            max_price=budget,
            limit=5
        )

        # Query mock RAG (vector search)
        rag_venues = self.mock_db.semantic_search_venues(
            query=f"{theme} party venue for {guest_count} guests",
            k=3
        )

        # Combine results (prefer RAG matches but include DB results)
        all_venues = {v['id']: v for v in db_venues}
        for v in rag_venues:
            all_venues[v['id']] = v

        recommendations = list(all_venues.values())[:3]

        result = {
            "recommended_venues": recommendations,
            "total_matches": len(all_venues),
            "search_criteria": {
                "guest_count": guest_count,
                "budget": budget,
                "theme": theme
            },
            "data_source": "mock_database"
        }

        return AgentOutput(
            agent_type=self.agent_type,
            result=result,
            confidence=0.85,
            execution_time=0.0,
            metadata={"venue_search_complete": True, "mock_data": True}
        )

    def _extract_guest_count(self, inputs: List[Dict[str, Any]]) -> int:
        """Extract guest count from inputs"""
        for inp in inputs:
            content = inp.get('content', '').lower()
            if 'guest' in content or 'people' in content:
                # Simple extraction - in production use NLP
                import re
                numbers = re.findall(r'\d+', content)
                if numbers:
                    return int(numbers[0])
        return 50  # Default

    def _extract_budget(self, context: Dict[str, Any]) -> int:
        """Extract budget from context"""
        agent_results = context.get('agent_results', {})
        budget_result = agent_results.get('budget_agent', {})
        total_budget = budget_result.get('total_budget', {})
        return total_budget.get('max', 1000)

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "inputs": {"type": "array"},
                "context": {"type": "object"}
            }
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "recommended_venues": {"type": "array"},
                "total_matches": {"type": "integer"},
                "search_criteria": {"type": "object"}
            }
        }

    def can_handle(self, inputs: List[Dict[str, Any]]) -> bool:
        return True


class VendorAgentEnhanced(BaseAgent):
    """Enhanced vendor agent using mock database"""

    def __init__(self):
        super().__init__(AgentType.VENDOR)
        self.mock_db = None

    async def initialize(self) -> None:
        """Initialize vendor agent with mock database"""
        from app.services.mock_database import get_mock_database
        self.mock_db = get_mock_database()
        logger.info("Vendor agent initialized with mock database")

    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Find vendors using mock database"""
        # Get context from other agents
        agent_results = agent_input.context.get('agent_results', {})
        theme = agent_results.get('theme_agent', {}).get('primary_theme', 'general')
        budget = agent_results.get('budget_agent', {}).get('total_budget', {})

        # Search for different categories of vendors
        vendors_by_category = {}
        categories = ['decorations', 'entertainment', 'photography', 'rentals']

        for category in categories:
            # Mock PostgreSQL query
            db_vendors = self.mock_db.query_vendors(
                category=category,
                max_price=budget.get('max', 5000),
                min_rating=4.0,
                limit=3
            )

            # Mock RAG search
            rag_vendors = self.mock_db.semantic_search_vendors(
                query=f"{category} vendor for {theme} party",
                k=2
            )

            # Combine results
            all_vendors = {v['id']: v for v in db_vendors}
            for v in rag_vendors:
                all_vendors[v['id']] = v

            vendors_by_category[category] = list(all_vendors.values())[:2]

        result = {
            "vendors_by_category": vendors_by_category,
            "total_vendors_found": sum(len(v) for v in vendors_by_category.values()),
            "search_criteria": {
                "theme": theme,
                "budget": budget
            },
            "data_source": "mock_database"
        }

        return AgentOutput(
            agent_type=self.agent_type,
            result=result,
            confidence=0.8,
            execution_time=0.0,
            metadata={"vendor_search_complete": True, "mock_data": True}
        )

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "context": {"type": "object"}
            }
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "vendors_by_category": {"type": "object"},
                "total_vendors_found": {"type": "integer"}
            }
        }

    def can_handle(self, inputs: List[Dict[str, Any]]) -> bool:
        return True


class CakeAgentEnhanced(BaseAgent):
    """Enhanced cake agent using mock bakery database"""

    def __init__(self):
        super().__init__(AgentType.CAKE)
        self.mock_db = None

    async def initialize(self) -> None:
        """Initialize cake agent with mock database"""
        from app.services.mock_database import get_mock_database
        self.mock_db = get_mock_database()
        logger.info("Cake agent initialized with mock database")

    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Find bakeries using mock database"""
        # Extract theme from context
        theme_context = agent_input.context.get('theme_result', {})
        primary_theme = theme_context.get('primary_theme', 'general')

        # Extract budget (rough estimate for cake)
        budget = 200  # Default cake budget

        # Query mock database for bakeries
        db_bakeries = self.mock_db.query_bakeries(
            max_budget=budget,
            custom_designs=True,
            limit=3
        )

        # Mock RAG search for similar cake designs
        rag_bakeries = self.mock_db.semantic_search_bakeries(
            query=f"{primary_theme} birthday cake design",
            k=2
        )

        # Combine results
        all_bakeries = {b['id']: b for b in db_bakeries}
        for b in rag_bakeries:
            all_bakeries[b['id']] = b

        recommendations = list(all_bakeries.values())[:3]

        result = {
            "recommended_bakeries": recommendations,
            "cake_style": "themed",
            "theme": primary_theme,
            "decorations": self._get_theme_cake_decorations(primary_theme),
            "estimated_cost": {"min": 80, "max": 300},
            "data_source": "mock_database"
        }

        return AgentOutput(
            agent_type=self.agent_type,
            result=result,
            confidence=0.85,
            execution_time=0.0,
            metadata={"bakery_search_complete": True, "mock_data": True}
        )

    def _get_theme_cake_decorations(self, theme: str) -> List[str]:
        """Get cake decorations based on theme"""
        decoration_map = {
            'jungle': ['animal figurines', 'leaf patterns', 'safari colors'],
            'space': ['planet toppers', 'star sprinkles', 'galaxy frosting'],
            'princess': ['crown topper', 'pink frosting', 'sparkles'],
            'superhero': ['superhero figurines', 'cityscape design', 'cape details'],
            'unicorn': ['unicorn horn', 'rainbow layers', 'magical sprinkles'],
            'dinosaur': ['dino topper', 'volcano design', 'prehistoric colors']
        }
        return decoration_map.get(theme, ['basic decorations', 'colored frosting'])

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "inputs": {"type": "array"},
                "context": {"type": "object"}
            }
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "recommended_bakeries": {"type": "array"},
                "cake_style": {"type": "string"},
                "estimated_cost": {"type": "object"}
            }
        }

    def can_handle(self, inputs: List[Dict[str, Any]]) -> bool:
        return True


class CateringAgentEnhanced(BaseAgent):
    """Enhanced catering agent using mock database"""

    def __init__(self):
        super().__init__(AgentType.CATERING)
        self.mock_db = None

    async def initialize(self) -> None:
        """Initialize catering agent with mock database"""
        from app.services.mock_database import get_mock_database
        self.mock_db = get_mock_database()
        logger.info("Catering agent initialized with mock database")

    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Find caterers using mock database"""
        # Extract requirements
        guest_count = self._extract_guest_count(agent_input.inputs)
        dietary_needs = self._extract_dietary_needs(agent_input.inputs)
        budget_per_person = 20  # Default

        # Query mock database
        db_caterers = self.mock_db.query_caterers(
            max_price_per_person=budget_per_person,
            dietary_needs=dietary_needs,
            limit=3
        )

        # Calculate total catering cost
        total_cost = {
            "min": min([c['price_per_person'] for c in db_caterers] or [12]) * guest_count,
            "max": max([c['price_per_person'] for c in db_caterers] or [20]) * guest_count
        }

        result = {
            "recommended_caterers": db_caterers,
            "guest_count": guest_count,
            "dietary_accommodations": dietary_needs,
            "estimated_total_cost": total_cost,
            "data_source": "mock_database"
        }

        return AgentOutput(
            agent_type=self.agent_type,
            result=result,
            confidence=0.8,
            execution_time=0.0,
            metadata={"catering_search_complete": True, "mock_data": True}
        )

    def _extract_guest_count(self, inputs: List[Dict[str, Any]]) -> int:
        """Extract guest count from inputs"""
        for inp in inputs:
            content = inp.get('content', '').lower()
            if 'guest' in content or 'people' in content:
                import re
                numbers = re.findall(r'\d+', content)
                if numbers:
                    return int(numbers[0])
        return 30  # Default

    def _extract_dietary_needs(self, inputs: List[Dict[str, Any]]) -> List[str]:
        """Extract dietary needs from inputs"""
        needs = []
        keywords = {
            'vegetarian': 'Vegetarian',
            'vegan': 'Vegan',
            'gluten': 'Gluten-Free',
            'nut': 'Nut-Free'
        }

        for inp in inputs:
            content = inp.get('content', '').lower()
            for keyword, formal_name in keywords.items():
                if keyword in content:
                    needs.append(formal_name)

        return needs if needs else ['Vegetarian']  # Default

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "inputs": {"type": "array"}
            }
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "recommended_caterers": {"type": "array"},
                "guest_count": {"type": "integer"},
                "estimated_total_cost": {"type": "object"}
            }
        }

    def can_handle(self, inputs: List[Dict[str, Any]]) -> bool:
        return True


class AgentRegistry:
    """Registry for managing agents"""

    def __init__(self):
        self.agents: Dict[AgentType, BaseAgent] = {}
        self.initialized = False
    
    def register_agent(self, agent_type: AgentType, agent: BaseAgent):
        """Register an agent"""
        self.agents[agent_type] = agent
        logger.info("Registered agent", agent_type=agent_type.value)
    
    async def initialize_all(self):
        """Initialize all registered agents"""
        if self.initialized:
            return
        
        for agent in self.agents.values():
            await agent.initialize()
        
        self.initialized = True
        logger.info("All agents initialized", count=len(self.agents))
    
    def get_agent(self, agent_type: AgentType) -> Optional[BaseAgent]:
        """Get agent by type"""
        return self.agents.get(agent_type)
    
    def get_available_agents(self) -> List[AgentType]:
        """Get list of available agent types"""
        return list(self.agents.keys())
    
    async def execute_agent(self, agent_type: AgentType, agent_input: AgentInput) -> AgentOutput:
        """Execute specific agent"""
        agent = self.get_agent(agent_type)
        if not agent:
            raise ValueError(f"Agent {agent_type.value} not found")
        
        return await agent._execute_with_timing(agent_input)
    
    def can_execute_agent(self, agent_type: AgentType, inputs: List[Dict[str, Any]]) -> bool:
        """Check if agent can handle inputs"""
        agent = self.get_agent(agent_type)
        if not agent:
            return False
        
        return agent.can_handle(inputs)


# Global registry instance
_agent_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    """Get global agent registry"""
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = AgentRegistry()

        # Register default agents
        _agent_registry.register_agent(AgentType.INPUT_CLASSIFIER, InputClassifierAgent())
        _agent_registry.register_agent(AgentType.THEME, ThemeAgent())

        # Register enhanced agents with mock database support
        _agent_registry.register_agent(AgentType.CAKE, CakeAgentEnhanced())
        _agent_registry.register_agent(AgentType.VENUE, VenueAgentEnhanced())
        _agent_registry.register_agent(AgentType.CATERING, CateringAgentEnhanced())
        _agent_registry.register_agent(AgentType.VENDOR, VendorAgentEnhanced())

        _agent_registry.register_agent(AgentType.BUDGET, BudgetAgent())

    return _agent_registry
