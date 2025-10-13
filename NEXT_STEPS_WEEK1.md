# 📅 Week 1: Implementation Roadmap

## ✅ Completed (Day 1-2)

### Project Structure
- [x] Monorepo initialized (`festipin/`)
- [x] Backend scaffolding (FastAPI + Python 3.11)
- [x] Frontend scaffolding (Next.js 14 + TypeScript)
- [x] Design system (Tailwind with purple/pink/gold palette)
- [x] Comprehensive documentation (README, SETUP_GUIDE)

### Backend Core
- [x] FastAPI main application (`app/main.py`)
- [x] Configuration system with Pydantic (`core/config.py`)
- [x] Structured JSON logging (`core/logging.py`)
- [x] API route structure:
  - [x] `/api/v1/input/process` - Input handler (stub)
  - [x] `/api/v1/vision/analyze` - Vision AI (stub)
  - [x] `/api/v1/plan/generate` - Plan generator (stub)
  - [x] `/api/v1/export/*` - Export routes (stubs)

### Backend Models
- [x] Input models (`InputType`, `ProcessedInputResponse`)
- [x] Vision models (`VisionAnalysisRequest`, `SceneData`)
- [x] Plan models (`FullPlan`, `ChecklistItem`, matching PRD JSON)

### Frontend Core
- [x] Next.js 14 App Router setup
- [x] Tailwind design system with custom colors
- [x] Landing page with tabbed input modes
- [x] Three input components:
  - [x] `PinterestUrlInput` (with validation)
  - [x] `ManualUploader` (with drag-drop)
  - [x] `PromptInput` (with examples)

### DevOps
- [x] Environment configuration templates
- [x] Requirements.txt with all dependencies
- [x] Package.json with frontend deps
- [x] Git-ready structure

---

## 🔨 Week 1 Remaining Tasks (Day 3-7)

### Day 3: Pinterest Scraping Implementation

**Goal:** Implement the Pinterest scraping service with fallback strategies

```python
# File: backend/app/services/pinterest_scraper.py

class PinterestScraperService:
    async def extract_pin(url: str) -> PinMetadata:
        # Strategy 1: Undocumented API endpoint
        # Strategy 2: HTML parsing (BeautifulSoup)
        # Strategy 3: Playwright headless browser
```

**Tasks:**
- [ ] Create `pinterest_scraper.py` service
- [ ] Implement 3 scraping strategies
- [ ] Add retry logic with exponential backoff
- [ ] Create `PinMetadata` model
- [ ] Test with 10+ different Pinterest URLs
- [ ] Document which patterns work best

**Testing:**
```bash
# Test Pinterest scraper
curl -X POST http://localhost:8000/api/v1/input/process \
  -F "input_type=pinterest_url" \
  -F "pinterest_url=https://pinterest.com/pin/..." \
  -F "user_id=test_user"
```

---

### Day 4: Cloud Storage Integration

**Goal:** Upload images to Firebase Cloud Storage

```python
# File: backend/app/services/storage_service.py

class StorageService:
    async def upload_image(image_bytes: bytes, filename: str) -> str:
        # Upload to Firebase Cloud Storage
        # Return public URL
```

**Tasks:**
- [ ] Create `storage_service.py`
- [ ] Implement Firebase Storage upload
- [ ] Add image validation (size, format)
- [ ] Generate unique filenames
- [ ] Return public URLs
- [ ] Test with different image formats

**Testing:**
```bash
# Test manual upload
curl -X POST http://localhost:8000/api/v1/input/process \
  -F "input_type=manual_upload" \
  -F "image=@party-image.jpg" \
  -F "user_id=test_user"
```

---

### Day 5: GPT-4 Vision Integration

**Goal:** Analyze party images using GPT-4 Vision API

```python
# File: backend/app/services/vision_processor.py

class VisionProcessor:
    async def analyze_party_image(image_url: str) -> SceneData:
        # Call GPT-4 Vision API
        # Extract: theme, objects, colors, layout
        # Return structured SceneData
```

**Tasks:**
- [ ] Create `vision_processor.py` service
- [ ] Craft effective vision prompt for party analysis
- [ ] Parse GPT-4 Vision response into `SceneData`
- [ ] Add fallback to Gemini Vision if GPT-4 fails
- [ ] Implement caching for analyzed images
- [ ] Test with diverse party images

**Vision Prompt Template:**
```
Analyze this party setup image. Extract:
1. Overall theme (e.g., "gold and white balloons", "princess")
2. Objects with positions (balloon arch, cake table, backdrop)
3. Color palette (hex codes)
4. Layout type (arch + backdrop + table, etc.)
5. Recommended venue type (indoor/outdoor/home)

Return as JSON.
```

**Testing:**
```bash
# Test vision analysis
curl -X POST http://localhost:8000/api/v1/vision/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://storage.googleapis.com/...",
    "input_id": "test_input_123",
    "user_id": "test_user"
  }'
```

---

### Day 6: Firestore Integration

**Goal:** Store and retrieve plans in Firestore

```python
# File: backend/app/services/firestore_service.py

class FirestoreService:
    async def create_plan(plan: FullPlan) -> str:
        # Store in Firestore 'plans' collection
        # Return plan_id
    
    async def get_plan(plan_id: str) -> FullPlan:
        # Fetch from Firestore
```

**Tasks:**
- [ ] Create `firestore_service.py`
- [ ] Implement CRUD operations for plans
- [ ] Create Firestore collections:
  - `users` - user profiles
  - `plans` - party plans
  - `user_inputs` - input history
  - `vendors` (future)
- [ ] Add indexes for queries
- [ ] Test data persistence

**Firestore Structure:**
```
plans/
  {plan_id}/
    event: {...}
    checklist: [...]
    budget_summary: {...}
    created_at: timestamp
    updated_at: timestamp
    user_id: string

user_inputs/
  {input_id}/
    type: "pinterest_url" | "manual_upload" | "text_prompt"
    source_url: string
    image_url: string
    user_id: string
    timestamp: timestamp
```

---

### Day 7: Integration Testing & Refinement

**Goal:** End-to-end testing of input → vision → plan flow

**Tasks:**
- [ ] Test full Pinterest URL flow:
  1. Scrape URL → 2. Upload image → 3. Analyze → 4. Store
- [ ] Test manual upload flow:
  1. Upload → 2. Analyze → 3. Store
- [ ] Test prompt flow:
  1. Parse prompt → 2. Generate plan → 3. Store
- [ ] Add error handling for all failure scenarios
- [ ] Implement logging for debugging
- [ ] Update frontend to handle responses
- [ ] Create simple loading states

**Integration Test Script:**
```python
# File: backend/tests/test_integration.py

async def test_pinterest_to_plan_flow():
    # 1. Submit Pinterest URL
    response = await client.post("/api/v1/input/process", ...)
    assert response.status_code == 200
    
    # 2. Wait for vision processing
    await asyncio.sleep(3)
    
    # 3. Check plan was created
    plan = await firestore.get_plan(response.json()["plan_id"])
    assert plan is not None
```

---

## 📊 Week 1 Success Metrics

By end of Week 1, you should have:

- [ ] **Pinterest scraping working** (at least 2 of 3 strategies)
- [ ] **Image upload** successfully saves to Cloud Storage
- [ ] **Vision AI** extracts theme + 3+ objects from images
- [ ] **Firestore** stores and retrieves plans
- [ ] **End-to-end test** passes for 1 complete flow
- [ ] **Frontend** shows loading states and handles responses

---

## 🔄 Daily Workflow

```bash
# Morning: Pull latest code
git pull origin main

# Start backend (Terminal 1)
cd festipin/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Start frontend (Terminal 2)
cd festipin/frontend
npm run dev

# Start Redis (Terminal 3 - optional)
redis-server

# Code → Test → Commit
# ... make changes ...
pytest  # Run backend tests
npm test  # Run frontend tests
git add .
git commit -m "feat: implement pinterest scraper"
git push origin main
```

---

## 🐛 Known Issues to Address

1. **Pinterest Scraping:** May be blocked by Pinterest's anti-scraping
   - **Solution:** Rotate user agents, add delays, use proxies (future)

2. **Vision API Costs:** GPT-4 Vision is expensive ($0.01/image)
   - **Solution:** Implement aggressive caching, use Gemini as primary

3. **No Authentication:** Currently using `temp_user_id`
   - **Solution:** Add Firebase Auth in Week 2

4. **No Rate Limiting:** API is open to abuse
   - **Solution:** Add rate limiting middleware

---

## 📚 Resources for Week 1

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js 14 Docs](https://nextjs.org/docs)
- [OpenAI Vision API](https://platform.openai.com/docs/guides/vision)
- [Firebase Firestore](https://firebase.google.com/docs/firestore)

### Tools
- [Postman](https://www.postman.com/) - API testing
- [Insomnia](https://insomnia.rest/) - Alternative API client
- [DB Browser](https://console.firebase.google.com) - Firestore GUI

---

## 🚀 Week 2 Preview

After Week 1 foundation is solid, Week 2 will focus on:

- **Missing Info Collector** - Conversational form to gather event details
- **Plan Generator** - LLM-based checklist generation
- **Interactive Canvas** (Konva.js) - Visual party layout editing
- **Right Panel** - Tabs for Chat, Details, Checklist, Budget

---

**Let's build something amazing! 🎉**

