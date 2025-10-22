"""
LangGraph Data Extraction Agent
Extracts structured data from prompts and images for party planning using LangGraph workflow
"""

from typing import Dict, Any, List, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
import json
import re
from datetime import datetime
import logging

from app.services.venue_database import venue_db
from app.services.keyword_expansions import (
    get_all_theme_keywords,
    get_all_event_keywords,
    VENUE_KEYWORDS,
    PARTY_ELEMENT_KEYWORDS
)

logger = logging.getLogger(__name__)

class ExtractedEventData(TypedDict):
    eventType: Optional[str]
    title: Optional[str]
    hostName: Optional[str]
    honoreeName: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    theme: Optional[str]
    date: Optional[str]
    time: Optional[Dict[str, str]]
    guestCount: Optional[Dict[str, int]]
    location: Optional[Dict[str, str]]
    budget: Optional[Dict[str, int]]
    foodPreference: Optional[str]
    activities: Optional[List[str]]
    rsvpDeadline: Optional[str]
    contactInfo: Optional[str]

class ExtractionState(TypedDict):
    input_text: str
    image_description: Optional[str]
    extracted_data: ExtractedEventData
    confidence: float
    missing_fields: List[str]
    suggestions: List[str]
    friendly_message: str
    needs_user_input: bool
    is_party_related: bool
    error: Optional[str]

class DataExtractionAgent:
    """LangGraph-based data extraction agent"""
    
    def __init__(self):
        # Use expanded keyword lists for better coverage
        self.event_types = get_all_event_keywords()
        self.themes = get_all_theme_keywords()

        # Get activity/entertainment keywords
        self.activities = PARTY_ELEMENT_KEYWORDS.get('entertainment', [])

        # Food and catering keywords
        self.food_keywords = [
            'vegetarian', 'veg', 'non-vegetarian', 'non veg', 'mixed', 'catering',
            'cake', 'cupcakes', 'cookies', 'snacks', 'appetizers', 'finger foods',
            'desserts', 'ice cream', 'pizza', 'hot dogs', 'hamburgers', 'sandwiches',
            'buffet', 'plated', 'family style', 'cocktail', 'hors d\'oeuvres'
        ]

        # Location keywords - combine all venue types
        self.location_keywords = []
        for venue_type, keywords in VENUE_KEYWORDS.items():
            self.location_keywords.extend(keywords)

        logger.info(
            f"DataExtractionAgent initialized with expanded keywords: "
            f"event_types={len(self.event_types)}, themes={len(self.themes)}, "
            f"activities={len(self.activities)}, locations={len(self.location_keywords)}"
        )
        
        self.build_graph()
    
    def build_graph(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(ExtractionState)
        
        # Add nodes
        workflow.add_node("validate_input", self.validate_input)
        workflow.add_node("extract_basic_info", self.extract_basic_info)
        workflow.add_node("extract_event_details", self.extract_event_details)
        workflow.add_node("extract_logistics", self.extract_logistics)
        workflow.add_node("calculate_confidence", self.calculate_confidence)
        workflow.add_node("generate_suggestions", self.generate_suggestions)
        
        # Add edges
        workflow.add_edge("validate_input", "extract_basic_info")
        workflow.add_edge("extract_basic_info", "extract_event_details")
        workflow.add_edge("extract_event_details", "extract_logistics")
        workflow.add_edge("extract_logistics", "calculate_confidence")
        workflow.add_edge("calculate_confidence", "generate_suggestions")
        workflow.add_edge("generate_suggestions", END)
        
        # Set entry point
        workflow.set_entry_point("validate_input")
        
        self.app = workflow.compile()
    
    def validate_input(self, state: ExtractionState) -> ExtractionState:
        """Validate input text and image description"""
        logger.info("Validating input for data extraction")
        
        if not state["input_text"] and not state["image_description"]:
            state["error"] = "No input provided for extraction"
            state["is_party_related"] = False
            return state
        
        # Combine text sources
        combined_text = f"{state['input_text']} {state['image_description'] or ''}".lower()
        
        # Basic validation - check if it contains party-related keywords
        party_keywords = self.event_types + self.themes + self.activities + self.food_keywords
        has_party_content = any(keyword in combined_text for keyword in party_keywords)
        
        if not has_party_content:
            state["error"] = "Input does not appear to contain party-related content"
            state["is_party_related"] = False
            return state
        
        state["is_party_related"] = True
        logger.info("Input validation passed")
        return state
    
    def extract_basic_info(self, state: ExtractionState) -> ExtractionState:
        """Extract basic event information"""
        logger.info("Extracting basic event information")
        
        text = f"{state['input_text']} {state['image_description'] or ''}".lower()
        extracted = state["extracted_data"]
        
        # Extract event type
        for event_type in self.event_types:
            if event_type in text:
                extracted["eventType"] = event_type.title()
                break
        
        # Extract age
        age_patterns = [
            r'(\d+)\s*(?:years?|yrs?|old)',
            r'(\d+)\s*(?:year|yr)\s*old',
            r'age\s*(\d+)',
            r'(\d+)\s*th\s*birthday'
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text)
            if match:
                extracted["age"] = int(match.group(1))
                break
        
        # Extract theme
        for theme in self.themes:
            if theme in text:
                extracted["theme"] = theme.title()
                break
        
        # Extract title (look for patterns like "X's birthday", "X party", etc.)
        title_patterns = [
            r"(\w+)'s\s+(?:birthday|party|celebration)",
            r"(\w+)\s+(?:birthday|party|celebration)",
            r"celebrating\s+(\w+)",
            r"(\w+)\s+turns\s+\d+"
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text)
            if match:
                extracted["honoreeName"] = match.group(1).title()
                break
        
        state["extracted_data"] = extracted
        logger.info(f"Extracted basic info: {extracted}")
        return state
    
    def extract_event_details(self, state: ExtractionState) -> ExtractionState:
        """Extract detailed event information"""
        logger.info("Extracting event details")
        
        text = f"{state['input_text']} {state['image_description'] or ''}".lower()
        extracted = state["extracted_data"]
        
        # Extract guest count
        guest_patterns = [
            r'(\d+)\s*(?:guests?|people|attendees?)',
            r'(\d+)\s*(?:adults?|grown-ups)',
            r'(\d+)\s*(?:kids?|children)',
            r'about\s*(\d+)\s*(?:people|guests?)',
            r'around\s*(\d+)\s*(?:people|guests?)'
        ]
        
        for pattern in guest_patterns:
            match = re.search(pattern, text)
            if match:
                total_guests = int(match.group(1))
                # Estimate adult/kid split
                adults = int(total_guests * 0.6)
                kids = int(total_guests * 0.4)
                extracted["guestCount"] = {"adults": adults, "kids": kids}
                break
        
        # Extract budget
        budget_patterns = [
            r'\$?(\d+)(?:\s*-\s*\$?(\d+))?',
            r'budget\s*(?:of\s*)?\$?(\d+)',
            r'spend\s*(?:up\s*to\s*)?\$?(\d+)',
            r'around\s*\$?(\d+)'
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, text)
            if match:
                min_budget = int(match.group(1))
                max_budget = int(match.group(2)) if match.group(2) else int(min_budget * 1.5)
                extracted["budget"] = {"min": min_budget, "max": max_budget}
                break
        
        # Extract food preference
        if any(keyword in text for keyword in ['vegetarian', 'veg']):
            extracted["foodPreference"] = "Veg"
        elif any(keyword in text for keyword in ['non-vegetarian', 'non veg', 'meat']):
            extracted["foodPreference"] = "Non-Veg"
        elif 'mixed' in text:
            extracted["foodPreference"] = "Mixed"
        
        # Extract activities
        activities = []
        for activity in self.activities:
            if activity in text:
                activities.append(activity.title())
        if activities:
            extracted["activities"] = activities
        
        # Extract location with venue database lookup
        location_extracted = False
        
        # Check for home/private venues (user needs to provide address)
        if any(keyword in text for keyword in ['home', 'house', 'backyard', 'private']):
            extracted["location"] = {
                "type": "Home", 
                "name": "Home", 
                "address": "User to provide",
                "needs_user_input": True,
                "venue_data": None
            }
            location_extracted = True
        
        # Check for external venues (fetch from database)
        elif any(keyword in text for keyword in ['park', 'garden', 'outdoor']):
            # Get guest count for capacity filtering
            guest_count = None
            if extracted.get("guestCount"):
                guest_count = extracted["guestCount"].get("adults", 0) + extracted["guestCount"].get("kids", 0)
            
            # Get recommended park
            recommended_venue = venue_db.get_recommended_venue("park", guest_count or 50)
            if recommended_venue:
                extracted["location"] = {
                    "type": "Park",
                    "name": recommended_venue.name,
                    "address": recommended_venue.address,
                    "needs_user_input": False,
                    "venue_data": {
                        "capacity": recommended_venue.capacity,
                        "amenities": recommended_venue.amenities,
                        "pricing": recommended_venue.pricing,
                        "contact_info": recommended_venue.contact_info,
                        "rating": recommended_venue.rating,
                        "images": recommended_venue.images
                    }
                }
                location_extracted = True
        
        elif any(keyword in text for keyword in ['hall', 'venue', 'banquet', 'conference']):
            # Get guest count for capacity filtering
            guest_count = None
            if extracted.get("guestCount"):
                guest_count = extracted["guestCount"].get("adults", 0) + extracted["guestCount"].get("kids", 0)
            
            # Get recommended banquet hall
            recommended_venue = venue_db.get_recommended_venue("banquet_hall", guest_count or 100)
            if recommended_venue:
                extracted["location"] = {
                    "type": "Banquet Hall",
                    "name": recommended_venue.name,
                    "address": recommended_venue.address,
                    "needs_user_input": False,
                    "venue_data": {
                        "capacity": recommended_venue.capacity,
                        "amenities": recommended_venue.amenities,
                        "pricing": recommended_venue.pricing,
                        "contact_info": recommended_venue.contact_info,
                        "rating": recommended_venue.rating,
                        "images": recommended_venue.images
                    }
                }
                location_extracted = True
        
        elif any(keyword in text for keyword in ['restaurant', 'cafe', 'dining']):
            # Get guest count for capacity filtering
            guest_count = None
            if extracted.get("guestCount"):
                guest_count = extracted["guestCount"].get("adults", 0) + extracted["guestCount"].get("kids", 0)
            
            # Get recommended restaurant
            recommended_venue = venue_db.get_recommended_venue("restaurant", guest_count or 30)
            if recommended_venue:
                extracted["location"] = {
                    "type": "Restaurant",
                    "name": recommended_venue.name,
                    "address": recommended_venue.address,
                    "needs_user_input": False,
                    "venue_data": {
                        "capacity": recommended_venue.capacity,
                        "amenities": recommended_venue.amenities,
                        "pricing": recommended_venue.pricing,
                        "contact_info": recommended_venue.contact_info,
                        "rating": recommended_venue.rating,
                        "images": recommended_venue.images
                    }
                }
                location_extracted = True
        
        elif any(keyword in text for keyword in ['hotel', 'resort']):
            # Get guest count for capacity filtering
            guest_count = None
            if extracted.get("guestCount"):
                guest_count = extracted["guestCount"].get("adults", 0) + extracted["guestCount"].get("kids", 0)
            
            # Get recommended hotel
            recommended_venue = venue_db.get_recommended_venue("hotel", guest_count or 100)
            if recommended_venue:
                extracted["location"] = {
                    "type": "Hotel",
                    "name": recommended_venue.name,
                    "address": recommended_venue.address,
                    "needs_user_input": False,
                    "venue_data": {
                        "capacity": recommended_venue.capacity,
                        "amenities": recommended_venue.amenities,
                        "pricing": recommended_venue.pricing,
                        "contact_info": recommended_venue.contact_info,
                        "rating": recommended_venue.rating,
                        "images": recommended_venue.images
                    }
                }
                location_extracted = True
        
        elif any(keyword in text for keyword in ['community', 'center', 'club']):
            # Get guest count for capacity filtering
            guest_count = None
            if extracted.get("guestCount"):
                guest_count = extracted["guestCount"].get("adults", 0) + extracted["guestCount"].get("kids", 0)
            
            # Get recommended community center
            recommended_venue = venue_db.get_recommended_venue("community_center", guest_count or 50)
            if recommended_venue:
                extracted["location"] = {
                    "type": "Community Center",
                    "name": recommended_venue.name,
                    "address": recommended_venue.address,
                    "needs_user_input": False,
                    "venue_data": {
                        "capacity": recommended_venue.capacity,
                        "amenities": recommended_venue.amenities,
                        "pricing": recommended_venue.pricing,
                        "contact_info": recommended_venue.contact_info,
                        "rating": recommended_venue.rating,
                        "images": recommended_venue.images
                    }
                }
                location_extracted = True
        
        # If no specific venue type detected, don't set location (will be asked in suggestions)
        if not location_extracted:
            logger.info("No specific venue type detected, location will be requested from user")
        
        state["extracted_data"] = extracted
        logger.info(f"Extracted event details: {extracted}")
        return state
    
    def extract_logistics(self, state: ExtractionState) -> ExtractionState:
        """Extract logistics information"""
        logger.info("Extracting logistics information")
        
        text = f"{state['input_text']} {state['image_description'] or ''}".lower()
        extracted = state["extracted_data"]
        
        # Extract date
        date_patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})',
            r'(\d{1,2})\s+(?:of\s+)?(january|february|march|april|may|june|july|august|september|october|november|december)',
            r'(next\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'(tomorrow|today|next\s+week)'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                if pattern == date_patterns[2]:  # Month name format
                    month_names = ['january', 'february', 'march', 'april', 'may', 'june',
                                 'july', 'august', 'september', 'october', 'november', 'december']
                    month = month_names.index(match.group(1)) + 1
                    day = int(match.group(2))
                    year = datetime.now().year
                    extracted["date"] = f"{year}-{month:02d}-{day:02d}"
                elif pattern == date_patterns[0]:  # MM/DD/YYYY
                    month, day, year = match.groups()
                    extracted["date"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                elif pattern == date_patterns[1]:  # YYYY-MM-DD
                    year, month, day = match.groups()
                    extracted["date"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                break
        
        # Extract time
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(?:am|pm|AM|PM)',
            r'(\d{1,2})\s*(?:am|pm|AM|PM)',
            r'at\s*(\d{1,2}):(\d{2})',
            r'from\s*(\d{1,2}):(\d{2})\s*to\s*(\d{1,2}):(\d{2})'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 4:  # Start and end time
                    start_hour, start_min, end_hour, end_min = match.groups()
                    extracted["time"] = {
                        "start": f"{start_hour.zfill(2)}:{start_min}",
                        "end": f"{end_hour.zfill(2)}:{end_min}"
                    }
                else:
                    hour, minute = match.groups()
                    extracted["time"] = {
                        "start": f"{hour.zfill(2)}:{minute}",
                        "end": f"{int(hour) + 3:02d}:{minute}"
                    }
                break
        
        state["extracted_data"] = extracted
        logger.info(f"Extracted logistics: {extracted}")
        return state
    
    def calculate_confidence(self, state: ExtractionState) -> ExtractionState:
        """Calculate extraction confidence"""
        logger.info("Calculating extraction confidence")
        
        extracted = state["extracted_data"]
        total_fields = 10  # Total number of important fields
        extracted_fields = sum(1 for value in extracted.values() if value is not None)
        
        confidence = (extracted_fields / total_fields) * 100
        state["confidence"] = round(confidence, 2)
        
        # Determine if user input is needed
        state["needs_user_input"] = extracted_fields < 6 or confidence < 60
        
        logger.info(f"Confidence: {confidence}%, Needs input: {state['needs_user_input']}")
        return state
    
    def generate_suggestions(self, state: ExtractionState) -> ExtractionState:
        """Generate suggestions for missing fields"""
        logger.info("Generating suggestions for missing fields")
        
        extracted = state["extracted_data"]
        missing_fields = []
        suggestions = []
        
        # Check for missing fields - location is now mandatory
        if not extracted.get("eventType"):
            missing_fields.append("eventType")
            suggestions.append("What type of event is this? (birthday, wedding, etc.)")
        
        if not extracted.get("theme"):
            missing_fields.append("theme")
            suggestions.append("What theme would you like? (princess, superhero, etc.)")
        
        if not extracted.get("location"):
            missing_fields.append("location")
            suggestions.append("Where will the event be held? Please provide city/zip code.")
        elif extracted.get("location", {}).get("needs_user_input", False):
            # For home venues, require city/zip
            missing_fields.append("location_address")
            suggestions.append("Please provide your city and zip code for the event")
        
        if not extracted.get("guestCount"):
            missing_fields.append("guestCount")
            suggestions.append("How many guests will attend?")
        
        if not extracted.get("date"):
            missing_fields.append("date")
            suggestions.append("When is the event?")
        
        if not extracted.get("budget"):
            missing_fields.append("budget")
            suggestions.append("What is your budget range?")
        
        if not extracted.get("foodPreference"):
            missing_fields.append("foodPreference")
            suggestions.append("What are your food preferences?")
        
        # Generate friendly message
        friendly_message = self.generateFriendlyMessage(extracted, missing_fields)
        
        state["missing_fields"] = missing_fields
        state["suggestions"] = suggestions
        state["friendly_message"] = friendly_message
        
        logger.info(f"Missing fields: {missing_fields}")
        logger.info(f"Friendly message: {friendly_message}")
        return state
    
    def checkMinimumDataRequirements(self, data: ExtractedEventData) -> bool:
        """Check if we have minimum required data to build a party plan"""
        required_fields = ['eventType', 'theme', 'location']
        return all(data.get(field) is not None for field in required_fields)
    
    def generateFriendlyMessage(self, extracted_data: ExtractedEventData, missing_fields: List[str]) -> str:
        """Generate a friendly message about extracted data"""
        messages = []
        
        if extracted_data.get('eventType'):
            messages.append(f"🎉 {extracted_data['eventType']} party")
        
        if extracted_data.get('theme'):
            messages.append(f"with {extracted_data['theme']} theme")
        
        if extracted_data.get('age'):
            messages.append(f"for {extracted_data['age']} year old")
        
        if extracted_data.get('honoreeName'):
            messages.append(f"celebrating {extracted_data['honoreeName']}")
        
        if extracted_data.get('guestCount'):
            adults = extracted_data['guestCount'].get('adults', 0)
            kids = extracted_data['guestCount'].get('kids', 0)
            total = adults + kids
            messages.append(f"with {total} guests")
        
        if extracted_data.get('location'):
            location = extracted_data['location']
            if location.get('type') == 'Home':
                messages.append("at home")
            else:
                messages.append(f"at {location.get('name', 'venue')}")
        
        base_message = " ".join(messages) if messages else "party"
        
        if missing_fields:
            return f"You're looking for a {base_message}! Awesome! To build the perfect plan, we need a few more details. Would you like to add more information?"
        else:
            return f"You're looking for a {base_message}! Perfect! We have all the details we need to build your amazing party plan."
    
    async def extract_data(self, input_text: str, image_description: Optional[str] = None) -> Dict[str, Any]:
        """Main extraction method using LangGraph workflow"""
        logger.info("Starting LangGraph data extraction workflow")
        
        initial_state = ExtractionState(
            input_text=input_text,
            image_description=image_description,
            extracted_data=ExtractedEventData(),
            confidence=0.0,
            missing_fields=[],
            suggestions=[],
            friendly_message="",
            needs_user_input=False,
            is_party_related=False,
            error=None
        )
        
        try:
            result = await self.app.ainvoke(initial_state)
            
            return {
                "extracted_data": result["extracted_data"],
                "confidence": result["confidence"],
                "missing_fields": result["missing_fields"],
                "suggestions": result["suggestions"],
                "friendly_message": result["friendly_message"],
                "needs_user_input": result["needs_user_input"],
                "is_party_related": result["is_party_related"],
                "error": result.get("error")
            }
        except Exception as e:
            logger.error(f"Error in LangGraph data extraction: {str(e)}")
            return {
                "extracted_data": ExtractedEventData(),
                "confidence": 0.0,
                "missing_fields": ["eventType", "theme", "location"],
                "suggestions": ["Please provide more details about your event"],
                "friendly_message": "We need more information to help you plan your party. Would you like to add more details?",
                "needs_user_input": True,
                "is_party_related": False,
                "error": str(e)
            }

# Global instance
data_extraction_agent = DataExtractionAgent()