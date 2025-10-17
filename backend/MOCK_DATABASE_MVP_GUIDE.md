# 🚀 Mock Database MVP Guide

## Overview

This MVP implementation simulates **PostgreSQL** and **Vector DB (RAG)** without requiring actual database setup. Perfect for testing agent workflows and frontend UI before production database integration.

---

## 📦 What's Included

### 1. **Mock Database Service** (`app/services/mock_database.py`)

- **5 Venues** - Parks, ballrooms, restaurants, hotels, community centers
- **5 Vendors** - Decorations, entertainment, photography, rentals, planning
- **5 Bakeries** - Different price ranges, specialties, custom designs
- **5 Caterers** - Various cuisines, dietary options, pricing tiers

### 2. **Enhanced Agents** (`app/services/agent_registry.py`)

- `VenueAgentEnhanced` - Uses mock DB to find venues
- `VendorAgentEnhanced` - Searches vendors by category
- `CakeAgentEnhanced` - Finds bakeries and cake designs
- `CateringAgentEnhanced` - Locates caterers with dietary options

---

## 🎯 Key Features

### ✅ Simulates PostgreSQL Queries

```python
# Example: Query venues with filters
venues = mock_db.query_venues(
    venue_type="park",
    min_capacity=50,
    max_price=500,
    limit=5
)
```

**Returns:** 2-3 random venues matching filters (simulates realistic DB results)

### ✅ Simulates Vector Database (RAG)

```python
# Example: Semantic search for venues
venues = mock_db.semantic_search_venues(
    query="jungle themed party venue for kids",
    k=3
)
```

**Returns:** 1-2 random venues with mock similarity scores (0.75-0.95)

### ✅ Random Results Every Query

Each query returns **different random selections** from the 5-item dataset, simulating real database variability.

---

## 🔄 How Agent Flow Works

### Step-by-Step:

```
1. User sends request → POST /api/v1/orchestration/start

2. InputClassifierAgent → Classifies inputs

3. ThemeAgent → Detects "jungle" theme

4. VenueAgentEnhanced (NEW!)
   ↓
   ├─ Extracts: guest_count=75, budget=$1000, theme="jungle"
   ├─ Queries mock PostgreSQL: query_venues(min_capacity=75, max_price=1000)
   │   Returns: 2-3 random venues
   ├─ Queries mock RAG: semantic_search_venues("jungle party venue for 75 guests")
   │   Returns: 1-2 random venues with similarity scores
   └─ Combines results → Returns top 3 venues to frontend

5. CakeAgentEnhanced (NEW!)
   ↓
   ├─ Extracts: theme="jungle", budget=$200
   ├─ Queries mock DB: query_bakeries(max_budget=200, custom_designs=True)
   ├─ Queries mock RAG: semantic_search_bakeries("jungle birthday cake")
   └─ Returns: 2-3 bakeries with portfolio images

6. CateringAgentEnhanced (NEW!)
   ↓
   ├─ Extracts: guest_count=75, dietary_needs=["Vegetarian"]
   ├─ Queries mock DB: query_caterers(max_price_per_person=20, dietary_needs=["Vegetarian"])
   └─ Returns: 2-3 caterers with menus and pricing

7. VendorAgentEnhanced (NEW!)
   ↓
   ├─ Searches by category: decorations, entertainment, photography, rentals
   ├─ For each category:
   │   ├─ Mock PostgreSQL query
   │   └─ Mock RAG search
   └─ Returns: Vendors grouped by category

8. BudgetAgent → Calculates total budget

9. PlannerAgent → Assembles final plan

10. Frontend receives complete plan with real-looking data!
```

---

## 📊 Example Response to Frontend

### Venue Agent Response:

```json
{
  "recommended_venues": [
    {
      "id": 1,
      "name": "Sunshine Garden Park",
      "type": "park",
      "capacity": 100,
      "amenities": ["Picnic Tables", "Playground", "Restrooms", "BBQ Area"],
      "daily_price": 0,
      "hourly_price": 0,
      "contact": "(555) 123-4567",
      "rating": 4.7,
      "images": ["park1.jpg", "park2.jpg"],
      "description": "Beautiful outdoor park with playground and picnic areas, perfect for kids parties",
      "similarity_score": 0.92
    },
    {
      "id": 2,
      "name": "Crystal Ballroom",
      "type": "banquet_hall",
      "capacity": 200,
      "daily_price": 1500,
      "rating": 4.9,
      "similarity_score": 0.85
    }
  ],
  "total_matches": 3,
  "search_criteria": {
    "guest_count": 75,
    "budget": 1000,
    "theme": "jungle"
  },
  "data_source": "mock_database"
}
```

### Bakery Agent Response:

```json
{
  "recommended_bakeries": [
    {
      "id": 1,
      "name": "Sweet Dreams Bakery",
      "specialties": ["Custom Cakes", "Themed Designs", "Sculpted Cakes"],
      "price_range": {"small": 80, "medium": 150, "large": 300},
      "rating": 4.9,
      "portfolio_images": ["cake1.jpg", "cake2.jpg", "cake3.jpg"],
      "custom_designs": true,
      "similarity_score": 0.88
    }
  ],
  "cake_style": "themed",
  "theme": "jungle",
  "decorations": ["animal figurines", "leaf patterns", "safari colors"],
  "estimated_cost": {"min": 80, "max": 300},
  "data_source": "mock_database"
}
```

---

## 🎨 Frontend Integration

### Example React Component:

```tsx
// frontend/src/components/VenueResults.tsx
export function VenueResults({ venueData }) {
  const venues = venueData.recommended_venues;

  return (
    <div className="venue-results">
      <h2>Recommended Venues</h2>
      <p>Found {venueData.total_matches} venues for {venueData.search_criteria.guest_count} guests</p>

      {venues.map(venue => (
        <div key={venue.id} className="venue-card">
          <img src={venue.images[0]} alt={venue.name} />
          <h3>{venue.name}</h3>
          <div className="venue-type">{venue.type}</div>
          <div className="venue-rating">⭐ {venue.rating}</div>

          <div className="venue-details">
            <p><strong>Capacity:</strong> {venue.capacity} guests</p>
            <p><strong>Price:</strong> ${venue.daily_price}/day</p>
            <p><strong>Contact:</strong> {venue.contact}</p>
          </div>

          <div className="venue-amenities">
            <h4>Amenities:</h4>
            <ul>
              {venue.amenities.map(amenity => (
                <li key={amenity}>{amenity}</li>
              ))}
            </ul>
          </div>

          <p className="venue-description">{venue.description}</p>

          {venue.similarity_score && (
            <div className="ai-match">
              🤖 AI Match Score: {(venue.similarity_score * 100).toFixed(0)}%
            </div>
          )}

          <button className="btn-contact">Contact Venue</button>
        </div>
      ))}

      <p className="data-source">
        💡 Data from: {venueData.data_source}
      </p>
    </div>
  );
}
```

---

## 🧪 Testing

### Run the test script:

```bash
cd /Users/snama/s.space/Parx-Agentic-Verse/festipin/backend
python test_mock_database.py
```

### Test Output:

```
🧪 TESTING MOCK DATABASE SERVICE
✅ Found 3 venues via PostgreSQL query
✅ Found 2 venues via RAG semantic search
✅ Results are different each query (randomization working)
🤖 Agent executed successfully with mock data!
```

---

## 🔄 How Random Responses Work

### Mock PostgreSQL Query:

```python
def query_venues(self, min_capacity=None, max_price=None, limit=5):
    filtered = self.venues.copy()

    # Apply filters
    if min_capacity:
        filtered = [v for v in filtered if v.capacity >= min_capacity]
    if max_price:
        filtered = [v for v in filtered if v.daily_price <= max_price]

    # 🎲 Return random 2-3 results
    result_count = min(random.randint(2, 3), len(filtered))
    results = random.sample(filtered, result_count) if filtered else []

    return [asdict(v) for v in results]
```

### Mock RAG Search:

```python
def semantic_search_venues(self, query: str, k: int = 3):
    # 🎲 Return random 1-2 venues
    result_count = min(random.randint(1, 2), len(self.venues))
    results = random.sample(self.venues, result_count)

    # Add mock similarity score
    for venue in results:
        venue_dict = asdict(venue)
        venue_dict["similarity_score"] = random.uniform(0.75, 0.95)  # Mock AI score

    return results_with_scores[:k]
```

---

## 📈 API Endpoints

### Start Orchestration:

```bash
POST http://localhost:9000/api/v1/orchestration/start
Content-Type: application/json

{
  "inputs": [
    {
      "source_type": "text",
      "content": "I need a jungle themed party for 75 guests",
      "tags": ["theme", "venue"]
    }
  ],
  "metadata": {
    "user_id": "user123"
  }
}
```

**Response:**

```json
{
  "success": true,
  "event_id": "evt_abc123",
  "message": "Orchestration started with event ID: evt_abc123"
}
```

### Get Status (Polling):

```bash
GET http://localhost:9000/api/v1/orchestration/status/evt_abc123
```

**Response:**

```json
{
  "success": true,
  "event_id": "evt_abc123",
  "workflow_status": "running",
  "agent_results": {
    "input_classifier": { "status": "completed", ... },
    "theme_agent": { "status": "completed", "result": {...} },
    "venue_agent": { "status": "running", ... }
  },
  "final_plan": null
}
```

---

## 🎯 Why This MVP Approach?

### ✅ **Advantages:**

1. **No Database Setup Required** - Works immediately without PostgreSQL/Pinecone/Chroma
2. **Fast Testing** - Test full agent workflow in seconds
3. **Frontend Development** - Frontend team can build UI with real-looking data
4. **Realistic Responses** - Random selections mimic real database behavior
5. **Easy Migration** - Just replace `query_X()` methods with real DB calls later

### ⚠️ **Limitations:**

1. **Only 5 items per category** - Not realistic scale
2. **No persistence** - Data resets on restart
3. **Random results** - Not based on actual relevance
4. **No real semantic search** - Just returns random items with fake scores

### 🚀 **Migration to Production:**

When ready for production:

1. **Replace `mock_database.py` with real PostgreSQL**
   ```python
   # Before (MVP)
   venues = mock_db.query_venues(min_capacity=50)

   # After (Production)
   venues = await db.execute("SELECT * FROM venues WHERE capacity >= $1", [50])
   ```

2. **Replace semantic_search with real RAG**
   ```python
   # Before (MVP)
   venues = mock_db.semantic_search_venues(query, k=3)

   # After (Production)
   embeddings = openai.embeddings.create(input=query)
   venues = pinecone_index.query(vector=embeddings, top_k=3)
   ```

3. **Keep Agent Logic Same** - Agents don't need to change!

---

## 📋 Quick Start Checklist

- [✅] Mock database created (`app/services/mock_database.py`)
- [✅] Enhanced agents created (VenueAgent, VendorAgent, CakeAgent, CateringAgent)
- [✅] Agents registered in `get_agent_registry()`
- [✅] Test script created (`test_mock_database.py`)
- [✅] Tests passing ✅
- [ ] **Next:** Test with full orchestration workflow
- [ ] **Next:** Build frontend UI to display agent results
- [ ] **Next:** Add WebSocket for real-time updates (see architecture guide)
- [ ] **Future:** Replace with real PostgreSQL + Vector DB

---

## 🎉 Summary

You now have a **fully functional MVP** that:

✅ Simulates PostgreSQL with 5 venues, vendors, bakeries, caterers
✅ Simulates Vector DB (RAG) with semantic search
✅ Returns random results each query (realistic behavior)
✅ Agents return structured data to frontend
✅ No database setup required
✅ Ready for frontend integration
✅ Easy migration path to production databases

**Start the backend and test:**

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Test with curl:**

```bash
curl -X POST http://localhost:9000/api/v1/orchestration/start \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [{"source_type": "text", "content": "jungle party for 75 guests", "tags": ["theme", "venue"]}]
  }'
```

Then poll for results:

```bash
curl http://localhost:9000/api/v1/orchestration/status/{event_id}
```

🎊 Enjoy your MVP agent system!
