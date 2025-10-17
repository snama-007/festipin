"""
Mock Database Service for MVP
Simulates PostgreSQL + Vector DB without actual database setup
Just 5 items in each category for testing
"""

import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class MockVenue:
    """Mock venue data"""
    id: int
    name: str
    type: str
    address: str
    capacity: int
    amenities: List[str]
    daily_price: int
    hourly_price: int
    contact: str
    rating: float
    images: List[str]
    description: str


@dataclass
class MockVendor:
    """Mock vendor data"""
    id: int
    name: str
    category: str
    services: List[str]
    contact: str
    rating: float
    avg_price: int
    review_count: int
    description: str
    portfolio_images: List[str]


@dataclass
class MockBakery:
    """Mock bakery data"""
    id: int
    name: str
    specialties: List[str]
    price_range: Dict[str, int]
    contact: str
    rating: float
    portfolio_images: List[str]
    custom_designs: bool
    description: str


@dataclass
class MockCaterer:
    """Mock catering company data"""
    id: int
    name: str
    cuisine_types: List[str]
    menu_items: List[str]
    dietary_options: List[str]
    price_per_person: int
    contact: str
    rating: float
    description: str


class MockDatabaseService:
    """
    Mock database service that simulates PostgreSQL queries
    Returns random results from a small dataset (5 items each)
    """

    def __init__(self):
        self.venues = self._create_mock_venues()
        self.vendors = self._create_mock_vendors()
        self.bakeries = self._create_mock_bakeries()
        self.caterers = self._create_mock_caterers()

    # ==================== MOCK DATA CREATION ====================

    def _create_mock_venues(self) -> List[MockVenue]:
        """Create 5 mock venues"""
        return [
            MockVenue(
                id=1,
                name="Sunshine Garden Park",
                type="park",
                address="123 Park Ave, Downtown",
                capacity=100,
                amenities=["Picnic Tables", "Playground", "Restrooms", "BBQ Area"],
                daily_price=0,
                hourly_price=0,
                contact="(555) 123-4567",
                rating=4.7,
                images=["park1.jpg", "park2.jpg"],
                description="Beautiful outdoor park with playground and picnic areas, perfect for kids parties"
            ),
            MockVenue(
                id=2,
                name="Crystal Ballroom",
                type="banquet_hall",
                address="456 Event Blvd, Uptown",
                capacity=200,
                amenities=["Stage", "Sound System", "Catering Kitchen", "Parking", "Decorations"],
                daily_price=1500,
                hourly_price=200,
                contact="(555) 234-5678",
                rating=4.9,
                images=["ballroom1.jpg", "ballroom2.jpg"],
                description="Elegant ballroom with crystal chandeliers and full event services"
            ),
            MockVenue(
                id=3,
                name="Fun Zone Restaurant",
                type="restaurant",
                address="789 Family St, Midtown",
                capacity=60,
                amenities=["Private Room", "Kids Menu", "Games", "Entertainment"],
                daily_price=400,
                hourly_price=50,
                contact="(555) 345-6789",
                rating=4.5,
                images=["restaurant1.jpg", "restaurant2.jpg"],
                description="Family-friendly restaurant with arcade games and party packages"
            ),
            MockVenue(
                id=4,
                name="Community Center Hall",
                type="community_center",
                address="321 Community Dr, Suburban",
                capacity=120,
                amenities=["Kitchen", "Tables", "Chairs", "Parking", "Gymnasium"],
                daily_price=300,
                hourly_price=40,
                contact="(555) 456-7890",
                rating=4.3,
                images=["community1.jpg", "community2.jpg"],
                description="Affordable community space with kitchen and gym access"
            ),
            MockVenue(
                id=5,
                name="Grand Hotel Conference Center",
                type="hotel",
                address="999 Luxury Lane, Business District",
                capacity=250,
                amenities=["Conference Rooms", "Catering", "AV Equipment", "Valet", "Hotel Rooms"],
                daily_price=2000,
                hourly_price=250,
                contact="(555) 567-8901",
                rating=4.8,
                images=["hotel1.jpg", "hotel2.jpg"],
                description="Luxurious hotel conference center with full-service catering and accommodations"
            )
        ]

    def _create_mock_vendors(self) -> List[MockVendor]:
        """Create 5 mock vendors"""
        return [
            MockVendor(
                id=1,
                name="Magic Party Decorations",
                category="decorations",
                services=["Balloon Arch", "Theme Decorations", "Backdrop Setup", "Table Settings"],
                contact="magic@party.com",
                rating=4.8,
                avg_price=500,
                review_count=127,
                description="Specialized in themed party decorations with balloon artistry",
                portfolio_images=["decor1.jpg", "decor2.jpg", "decor3.jpg"]
            ),
            MockVendor(
                id=2,
                name="SuperHero Entertainment",
                category="entertainment",
                services=["Character Performers", "Face Painting", "Magic Shows", "Games"],
                contact="bookings@superheroent.com",
                rating=4.9,
                avg_price=350,
                review_count=203,
                description="Professional entertainers bringing characters to life at your party",
                portfolio_images=["ent1.jpg", "ent2.jpg"]
            ),
            MockVendor(
                id=3,
                name="Picture Perfect Photography",
                category="photography",
                services=["Event Photography", "Photo Booth", "Video Recording", "Same-Day Edits"],
                contact="info@pictureperfect.com",
                rating=4.7,
                avg_price=600,
                review_count=89,
                description="Capturing your special moments with professional photography and photo booths",
                portfolio_images=["photo1.jpg", "photo2.jpg", "photo3.jpg"]
            ),
            MockVendor(
                id=4,
                name="Party Rental Pro",
                category="rentals",
                services=["Tables", "Chairs", "Tents", "Bounce Houses", "Sound System"],
                contact="rentals@partypro.com",
                rating=4.6,
                avg_price=400,
                review_count=156,
                description="Complete party rental solutions from furniture to entertainment equipment",
                portfolio_images=["rental1.jpg", "rental2.jpg"]
            ),
            MockVendor(
                id=5,
                name="Event Coordination Experts",
                category="planning",
                services=["Full Planning", "Day-of Coordination", "Vendor Management", "Timeline Creation"],
                contact="events@coordinationexperts.com",
                rating=5.0,
                avg_price=800,
                review_count=67,
                description="Professional event planners ensuring your party runs smoothly from start to finish",
                portfolio_images=["planning1.jpg", "planning2.jpg"]
            )
        ]

    def _create_mock_bakeries(self) -> List[MockBakery]:
        """Create 5 mock bakeries"""
        return [
            MockBakery(
                id=1,
                name="Sweet Dreams Bakery",
                specialties=["Custom Cakes", "Themed Designs", "Sculpted Cakes"],
                price_range={"small": 80, "medium": 150, "large": 300},
                contact="orders@sweetdreams.com",
                rating=4.9,
                portfolio_images=["cake1.jpg", "cake2.jpg", "cake3.jpg"],
                custom_designs=True,
                description="Award-winning bakery specializing in custom themed birthday cakes"
            ),
            MockBakery(
                id=2,
                name="Cake Masters Studio",
                specialties=["Character Cakes", "3D Cakes", "Fondant Art"],
                price_range={"small": 100, "medium": 200, "large": 400},
                contact="hello@cakemasters.com",
                rating=5.0,
                portfolio_images=["cake4.jpg", "cake5.jpg"],
                custom_designs=True,
                description="Master cake artists creating stunning 3D character cakes for kids"
            ),
            MockBakery(
                id=3,
                name="Budget Bites Bakery",
                specialties=["Sheet Cakes", "Cupcakes", "Simple Designs"],
                price_range={"small": 40, "medium": 70, "large": 120},
                contact="info@budgetbites.com",
                rating=4.3,
                portfolio_images=["cake6.jpg", "cake7.jpg"],
                custom_designs=False,
                description="Affordable delicious cakes perfect for any budget"
            ),
            MockBakery(
                id=4,
                name="Organic Treats Bakery",
                specialties=["Organic Ingredients", "Allergen-Free", "Vegan Options"],
                price_range={"small": 90, "medium": 170, "large": 320},
                contact="orders@organictreats.com",
                rating=4.7,
                portfolio_images=["cake8.jpg", "cake9.jpg"],
                custom_designs=True,
                description="Health-conscious bakery using organic ingredients and allergen-free options"
            ),
            MockBakery(
                id=5,
                name="Classic Confections",
                specialties=["Traditional Cakes", "Buttercream Designs", "Tiered Cakes"],
                price_range={"small": 65, "medium": 130, "large": 250},
                contact="bakery@classicconfections.com",
                rating=4.6,
                portfolio_images=["cake10.jpg", "cake11.jpg"],
                custom_designs=True,
                description="Classic bakery with traditional recipes and beautiful buttercream designs"
            )
        ]

    def _create_mock_caterers(self) -> List[MockCaterer]:
        """Create 5 mock caterers"""
        return [
            MockCaterer(
                id=1,
                name="Kids Party Catering Co",
                cuisine_types=["American", "Kid-Friendly"],
                menu_items=["Pizza", "Chicken Tenders", "Mac & Cheese", "Fruit Platters", "Veggie Sticks"],
                dietary_options=["Vegetarian", "Gluten-Free"],
                price_per_person=15,
                contact="catering@kidsparty.com",
                rating=4.7,
                description="Specialized in kid-friendly menus with fun presentation"
            ),
            MockCaterer(
                id=2,
                name="Fiesta Flavors Catering",
                cuisine_types=["Mexican", "Tex-Mex"],
                menu_items=["Tacos", "Quesadillas", "Nachos", "Churros", "Fresh Salsa"],
                dietary_options=["Vegetarian", "Vegan", "Gluten-Free"],
                price_per_person=18,
                contact="events@fiestaflavors.com",
                rating=4.8,
                description="Bringing authentic Mexican flavors to your party with customizable menus"
            ),
            MockCaterer(
                id=3,
                name="Healthy Bites Catering",
                cuisine_types=["Healthy", "Organic"],
                menu_items=["Grain Bowls", "Salad Bar", "Fruit Kebabs", "Smoothies", "Veggie Wraps"],
                dietary_options=["Vegetarian", "Vegan", "Gluten-Free", "Nut-Free"],
                price_per_person=20,
                contact="info@healthybites.com",
                rating=4.6,
                description="Health-conscious catering with organic ingredients and allergy accommodations"
            ),
            MockCaterer(
                id=4,
                name="BBQ Masters Catering",
                cuisine_types=["BBQ", "American"],
                menu_items=["Pulled Pork", "Ribs", "Chicken", "Coleslaw", "Cornbread", "Baked Beans"],
                dietary_options=["Gluten-Free Options"],
                price_per_person=22,
                contact="bbq@bbqmasters.com",
                rating=4.9,
                description="Authentic BBQ catering with slow-smoked meats and classic sides"
            ),
            MockCaterer(
                id=5,
                name="Budget Buffet Catering",
                cuisine_types=["American", "Italian"],
                menu_items=["Pasta", "Sandwiches", "Chips", "Cookies", "Drinks"],
                dietary_options=["Vegetarian"],
                price_per_person=12,
                contact="bookings@budgetbuffet.com",
                rating=4.2,
                description="Affordable catering options perfect for large parties on a budget"
            )
        ]

    # ==================== QUERY METHODS (Simulate PostgreSQL) ====================

    def query_venues(self,
                     venue_type: Optional[str] = None,
                     min_capacity: Optional[int] = None,
                     max_price: Optional[int] = None,
                     limit: int = 5) -> List[Dict[str, Any]]:
        """
        Simulate PostgreSQL query for venues
        Returns random 2-3 venues that match filters
        """
        filtered = self.venues.copy()

        # Apply filters
        if venue_type:
            filtered = [v for v in filtered if v.type == venue_type]
        if min_capacity:
            filtered = [v for v in filtered if v.capacity >= min_capacity]
        if max_price:
            filtered = [v for v in filtered if v.daily_price <= max_price or v.daily_price == 0]

        # Return random 2-3 results (simulate realistic results)
        result_count = min(random.randint(2, 3), len(filtered))
        results = random.sample(filtered, result_count) if filtered else []

        return [asdict(v) for v in results]

    def query_vendors(self,
                      category: Optional[str] = None,
                      max_price: Optional[int] = None,
                      min_rating: Optional[float] = None,
                      limit: int = 5) -> List[Dict[str, Any]]:
        """
        Simulate PostgreSQL query for vendors
        Returns random 2-3 vendors that match filters
        """
        filtered = self.vendors.copy()

        # Apply filters
        if category:
            filtered = [v for v in filtered if v.category == category]
        if max_price:
            filtered = [v for v in filtered if v.avg_price <= max_price]
        if min_rating:
            filtered = [v for v in filtered if v.rating >= min_rating]

        # Return random 2-3 results
        result_count = min(random.randint(2, 3), len(filtered))
        results = random.sample(filtered, result_count) if filtered else []

        return [asdict(v) for v in results]

    def query_bakeries(self,
                       max_budget: Optional[int] = None,
                       custom_designs: Optional[bool] = None,
                       limit: int = 5) -> List[Dict[str, Any]]:
        """
        Simulate PostgreSQL query for bakeries
        Returns random 2-3 bakeries that match filters
        """
        filtered = self.bakeries.copy()

        # Apply filters
        if max_budget:
            filtered = [b for b in filtered if b.price_range["medium"] <= max_budget]
        if custom_designs is not None:
            filtered = [b for b in filtered if b.custom_designs == custom_designs]

        # Return random 2-3 results
        result_count = min(random.randint(2, 3), len(filtered))
        results = random.sample(filtered, result_count) if filtered else []

        return [asdict(b) for b in results]

    def query_caterers(self,
                       max_price_per_person: Optional[int] = None,
                       dietary_needs: Optional[List[str]] = None,
                       limit: int = 5) -> List[Dict[str, Any]]:
        """
        Simulate PostgreSQL query for caterers
        Returns random 2-3 caterers that match filters
        """
        filtered = self.caterers.copy()

        # Apply filters
        if max_price_per_person:
            filtered = [c for c in filtered if c.price_per_person <= max_price_per_person]
        if dietary_needs:
            filtered = [c for c in filtered
                       if any(need in c.dietary_options for need in dietary_needs)]

        # Return random 2-3 results
        result_count = min(random.randint(2, 3), len(filtered))
        results = random.sample(filtered, result_count) if filtered else []

        return [asdict(c) for c in results]

    # ==================== RAG SIMULATION (Simulate Vector DB) ====================

    def semantic_search_venues(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Simulate vector database semantic search for venues
        Just returns random 1-2 venues (simulating RAG results)
        """
        result_count = min(random.randint(1, 2), len(self.venues))
        results = random.sample(self.venues, result_count)

        # Add mock similarity score
        results_with_scores = []
        for venue in results:
            venue_dict = asdict(venue)
            venue_dict["similarity_score"] = random.uniform(0.75, 0.95)  # Mock relevance score
            results_with_scores.append(venue_dict)

        # Sort by similarity score (highest first)
        results_with_scores.sort(key=lambda x: x["similarity_score"], reverse=True)

        return results_with_scores[:k]

    def semantic_search_vendors(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Simulate vector database semantic search for vendors
        Just returns random 1-2 vendors (simulating RAG results)
        """
        result_count = min(random.randint(1, 2), len(self.vendors))
        results = random.sample(self.vendors, result_count)

        # Add mock similarity score
        results_with_scores = []
        for vendor in results:
            vendor_dict = asdict(vendor)
            vendor_dict["similarity_score"] = random.uniform(0.75, 0.95)
            results_with_scores.append(vendor_dict)

        results_with_scores.sort(key=lambda x: x["similarity_score"], reverse=True)

        return results_with_scores[:k]

    def semantic_search_bakeries(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Simulate vector database semantic search for bakeries
        Just returns random 1-2 bakeries (simulating RAG results)
        """
        result_count = min(random.randint(1, 2), len(self.bakeries))
        results = random.sample(self.bakeries, result_count)

        # Add mock similarity score
        results_with_scores = []
        for bakery in results:
            bakery_dict = asdict(bakery)
            bakery_dict["similarity_score"] = random.uniform(0.75, 0.95)
            results_with_scores.append(bakery_dict)

        results_with_scores.sort(key=lambda x: x["similarity_score"], reverse=True)

        return results_with_scores[:k]


# ==================== GLOBAL INSTANCE ====================

_mock_db: Optional[MockDatabaseService] = None


def get_mock_database() -> MockDatabaseService:
    """Get global mock database instance"""
    global _mock_db
    if _mock_db is None:
        _mock_db = MockDatabaseService()
    return _mock_db
