"""
Venue Database Service
Provides venue data for external venues like parks, event halls, restaurants, etc.
"""

from typing import Dict, List, Optional, Any
import json
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class VenueData:
    """Venue data structure"""
    name: str
    type: str
    address: str
    capacity: int
    amenities: List[str]
    pricing: Dict[str, Any]
    contact_info: Dict[str, str]
    rating: float
    images: List[str]

class VenueDatabaseService:
    """Service to provide venue data from database"""
    
    def __init__(self):
        self.venues = self._load_venue_database()
        logger.info(f"Loaded {len(self.venues)} venues from database")
    
    def _load_venue_database(self) -> Dict[str, List[VenueData]]:
        """Load venue database - in production this would be from a real database"""
        return {
            "park": [
                VenueData(
                    name="Central Park",
                    type="Park",
                    address="123 Park Avenue, City Center",
                    capacity=100,
                    amenities=["Picnic Tables", "Playground", "Restrooms", "Parking"],
                    pricing={"hourly": 0, "daily": 0, "permit": 50},
                    contact_info={"phone": "(555) 123-4567", "email": "centralpark@city.gov"},
                    rating=4.5,
                    images=["park1.jpg", "park2.jpg"]
                ),
                VenueData(
                    name="Riverside Park",
                    type="Park",
                    address="456 River Road, Riverside",
                    capacity=75,
                    amenities=["BBQ Area", "Walking Trails", "Restrooms"],
                    pricing={"hourly": 0, "daily": 0, "permit": 35},
                    contact_info={"phone": "(555) 234-5678", "email": "riverside@city.gov"},
                    rating=4.2,
                    images=["riverside1.jpg", "riverside2.jpg"]
                ),
                VenueData(
                    name="Sunset Gardens",
                    type="Park",
                    address="789 Garden Lane, Sunset District",
                    capacity=50,
                    amenities=["Gazebo", "Flower Gardens", "Parking"],
                    pricing={"hourly": 0, "daily": 0, "permit": 25},
                    contact_info={"phone": "(555) 345-6789", "email": "sunset@city.gov"},
                    rating=4.7,
                    images=["sunset1.jpg", "sunset2.jpg"]
                )
            ],
            "banquet_hall": [
                VenueData(
                    name="Grand Ballroom",
                    type="Banquet Hall",
                    address="1000 Event Center Blvd, Downtown",
                    capacity=300,
                    amenities=["Stage", "Sound System", "Catering Kitchen", "Parking"],
                    pricing={"hourly": 150, "daily": 1200, "permit": 0},
                    contact_info={"phone": "(555) 456-7890", "email": "events@grandballroom.com"},
                    rating=4.8,
                    images=["ballroom1.jpg", "ballroom2.jpg"]
                ),
                VenueData(
                    name="Community Center Hall",
                    type="Banquet Hall",
                    address="200 Community Drive, Midtown",
                    capacity=150,
                    amenities=["Kitchen", "Tables & Chairs", "Parking"],
                    pricing={"hourly": 75, "daily": 600, "permit": 0},
                    contact_info={"phone": "(555) 567-8901", "email": "rentals@communitycenter.org"},
                    rating=4.3,
                    images=["community1.jpg", "community2.jpg"]
                ),
                VenueData(
                    name="Elegant Events",
                    type="Banquet Hall",
                    address="500 Luxury Lane, Uptown",
                    capacity=200,
                    amenities=["Full Catering", "Decorations", "Photography", "Valet"],
                    pricing={"hourly": 200, "daily": 1600, "permit": 0},
                    contact_info={"phone": "(555) 678-9012", "email": "info@elegantevents.com"},
                    rating=4.9,
                    images=["elegant1.jpg", "elegant2.jpg"]
                )
            ],
            "restaurant": [
                VenueData(
                    name="Family Fun Restaurant",
                    type="Restaurant",
                    address="300 Family Street, Family District",
                    capacity=80,
                    amenities=["Private Room", "Kids Menu", "Entertainment", "Parking"],
                    pricing={"hourly": 50, "daily": 400, "permit": 0},
                    contact_info={"phone": "(555) 789-0123", "email": "parties@familyfun.com"},
                    rating=4.4,
                    images=["family1.jpg", "family2.jpg"]
                ),
                VenueData(
                    name="Pizza Palace",
                    type="Restaurant",
                    address="400 Pizza Avenue, Food District",
                    capacity=60,
                    amenities=["Party Room", "Arcade Games", "Birthday Packages"],
                    pricing={"hourly": 30, "daily": 240, "permit": 0},
                    contact_info={"phone": "(555) 890-1234", "email": "parties@pizzapalace.com"},
                    rating=4.6,
                    images=["pizza1.jpg", "pizza2.jpg"]
                )
            ],
            "hotel": [
                VenueData(
                    name="Grand Hotel Conference Center",
                    type="Hotel",
                    address="600 Hotel Boulevard, Business District",
                    capacity=250,
                    amenities=["Conference Rooms", "Catering", "Audio/Visual", "Parking"],
                    pricing={"hourly": 125, "daily": 1000, "permit": 0},
                    contact_info={"phone": "(555) 901-2345", "email": "events@grandhotel.com"},
                    rating=4.7,
                    images=["hotel1.jpg", "hotel2.jpg"]
                )
            ],
            "community_center": [
                VenueData(
                    name="Neighborhood Community Center",
                    type="Community Center",
                    address="700 Community Way, Residential Area",
                    capacity=100,
                    amenities=["Gymnasium", "Kitchen", "Tables", "Parking"],
                    pricing={"hourly": 25, "daily": 200, "permit": 0},
                    contact_info={"phone": "(555) 012-3456", "email": "rentals@neighborhoodcc.org"},
                    rating=4.1,
                    images=["neighborhood1.jpg", "neighborhood2.jpg"]
                )
            ]
        }
    
    def get_venues_by_type(self, venue_type: str, guest_count: Optional[int] = None) -> List[VenueData]:
        """Get venues by type, optionally filtered by capacity"""
        venues = self.venues.get(venue_type.lower(), [])
        
        if guest_count:
            # Filter venues that can accommodate the guest count
            venues = [v for v in venues if v.capacity >= guest_count]
        
        # Sort by rating (highest first)
        venues.sort(key=lambda x: x.rating, reverse=True)
        
        logger.info(f"Found {len(venues)} venues of type '{venue_type}' for {guest_count or 'any'} guests")
        return venues
    
    def get_venue_by_name(self, venue_name: str) -> Optional[VenueData]:
        """Get specific venue by name"""
        for venue_type, venues in self.venues.items():
            for venue in venues:
                if venue.name.lower() == venue_name.lower():
                    return venue
        return None
    
    def get_recommended_venue(self, venue_type: str, guest_count: int, budget_range: Optional[Dict[str, int]] = None) -> Optional[VenueData]:
        """Get recommended venue based on type, capacity, and budget"""
        venues = self.get_venues_by_type(venue_type, guest_count)
        
        if not venues:
            return None
        
        # If budget is specified, filter by budget
        if budget_range:
            max_budget = budget_range.get("max", float('inf'))
            venues = [v for v in venues if v.pricing.get("daily", 0) <= max_budget]
        
        # Return the highest rated venue that meets criteria
        return venues[0] if venues else None
    
    def get_all_venue_types(self) -> List[str]:
        """Get all available venue types"""
        return list(self.venues.keys())

# Global venue database service
venue_db = VenueDatabaseService()
