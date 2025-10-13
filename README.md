# 🎉 Parx Planner (FestiPin)

**AI-Powered Party Planning from Pinterest URLs & Prompts**

Transform Pinterest party inspiration into structured, editable, vendor-ready event plans in seconds.

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and **npm**
- **Python** 3.11+
- **Redis** (for caching)
- **Firebase** project with Firestore enabled

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd festipin

# Install frontend dependencies
cd frontend
npm install

# Install backend dependencies
cd ../backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables

Create `.env` files in both frontend and backend:

**Backend `.env`:**
```env
# AI Services
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here

# Firebase
GOOGLE_APPLICATION_CREDENTIALS=path/to/firebase-credentials.json
FIREBASE_PROJECT_ID=your_project_id

# Redis
REDIS_URL=redis://localhost:6379

# Storage
STORAGE_BUCKET=your_storage_bucket_name

# App Config
ENVIRONMENT=development
DEBUG=true
```

**Frontend `.env.local`:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
```

### Run Development Servers

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

Access the app at: **http://localhost:3000**

---

## 📋 Features (MVP v1)

### ✅ Dual Input System
- 🔗 Pinterest URL scraping (with fallbacks)
- 📤 Manual image upload
- 💬 Text prompt planning

### 🎨 Interactive Canvas
- Drag-and-drop party layout editing
- Visual scene representation
- Real-time item positioning

### 📝 Smart Missing Info Collection
- AI detects required event details
- Conversational form filling
- Smart defaults based on context

### ✅ Structured Checklist
- Vendor-ready task breakdown
- Budget tracking by category
- Timeline with dependencies

### 📤 Export Options
- PDF party plan
- Vendor brief
- Notion integration
- Calendar export (ICS)

---

## 🏗️ Architecture

```
┌─────────────┐
│   Next.js   │  → Frontend (React + Konva Canvas)
│  Frontend   │
└──────┬──────┘
       │
       ↓ HTTP/REST
┌─────────────┐
│   FastAPI   │  → Backend (Python)
│   Backend   │
└──────┬──────┘
       │
       ├→ GPT-4 Vision (Image analysis)
       ├→ Firestore (Data storage)
       ├→ Cloud Storage (Images)
       └→ Redis (Caching)
```

---

## 📊 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS, Konva.js, Zustand |
| **Backend** | FastAPI, Python 3.11+, Pydantic v2 |
| **AI/ML** | GPT-4 Vision, GPT-4 Turbo, Gemini Flash |
| **Database** | Firestore (NoSQL) |
| **Storage** | Cloud Storage |
| **Cache** | Redis |
| **Scraping** | Playwright, httpx, BeautifulSoup4 |

---

## 📁 Project Structure

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed structure.

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

---

## 📚 Documentation

- [API Documentation](./docs/API.md)
- [Component Guide](./docs/COMPONENTS.md)
- [Pinterest Scraping Strategy](./docs/SCRAPING.md)
- [Canvas Implementation](./docs/CANVAS.md)

---

## 🗓️ Roadmap

### Phase 1: Foundation (Weeks 1-3) ✅
- [x] Project setup
- [x] Pinterest scraper
- [x] Vision AI integration
- [ ] Input processing

### Phase 2: Core Features (Weeks 4-7)
- [ ] Missing info collector
- [ ] Plan generator
- [ ] Interactive canvas
- [ ] Real-time sync

### Phase 3: Advanced (Weeks 8-10)
- [ ] Vendor integration
- [ ] Export engine
- [ ] Collaboration features

### Phase 4: Polish (Weeks 11-12)
- [ ] Testing & optimization
- [ ] Documentation
- [ ] Beta launch

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

---

## 🙏 Acknowledgments

- OpenAI for GPT-4 Vision API
- Google for Gemini API
- Pinterest for inspiration
- The party planning community

---

**Built with ❤️ for making party planning effortless**

