# 🚀 Parx Planner - Complete Setup Guide

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Node.js** 18+ installed ([nodejs.org](https://nodejs.org))
- [ ] **Python** 3.11+ installed ([python.org](https://python.org))
- [ ] **Git** installed
- [ ] **Firebase** account ([console.firebase.google.com](https://console.firebase.google.com))
- [ ] **OpenAI** API key ([platform.openai.com](https://platform.openai.com))
- [ ] **Google Gemini** API key ([ai.google.dev](https://ai.google.dev))
- [ ] **Redis** (optional for MVP, can mock)

---

## 🔧 Step 1: Firebase Setup

### 1.1 Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click **"Add project"**
3. Name it `parx-planner` (or your choice)
4. Disable Google Analytics (optional for now)
5. Click **"Create project"**

### 1.2 Enable Firestore

1. In your Firebase project, go to **"Build" → "Firestore Database"**
2. Click **"Create database"**
3. Start in **"Test mode"** (for development)
4. Choose a location (closest to you)
5. Click **"Enable"**

### 1.3 Enable Cloud Storage

1. Go to **"Build" → "Storage"**
2. Click **"Get started"**
3. Start in **"Test mode"**
4. Click **"Done"**

### 1.4 Get Service Account Credentials

1. Go to **"Project settings"** (gear icon)
2. Select **"Service accounts"** tab
3. Click **"Generate new private key"**
4. Save the JSON file as `firebase-credentials.json`
5. Move it to: `festipin/backend/firebase-credentials.json`

### 1.5 Get Firebase Config for Frontend

1. Still in **"Project settings"**
2. Under **"General"** tab, scroll to **"Your apps"**
3. Click **"Web"** (</> icon)
4. Register app with nickname `parx-planner-web`
5. Copy the `firebaseConfig` object
6. Save for later (we'll add to `.env.local`)

---

## 🔧 Step 2: Backend Setup

### 2.1 Navigate to Backend Directory

```bash
cd festipin/backend
```

### 2.2 Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 2.3 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.4 Install Playwright (for Pinterest scraping)

```bash
playwright install chromium
```

### 2.5 Create `.env` File

Create `festipin/backend/.env` (copy from `.env.example`):

```env
# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_CORS_ORIGINS=http://localhost:3000

# AI Services
OPENAI_API_KEY=sk-your-actual-key-here
GEMINI_API_KEY=your-actual-gemini-key-here
OPENAI_MODEL=gpt-4-vision-preview
GEMINI_MODEL=gemini-2.0-flash

# Firebase
GOOGLE_APPLICATION_CREDENTIALS=./firebase-credentials.json
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com

# Redis (can be empty for now)
REDIS_URL=redis://localhost:6379

# Storage
MAX_UPLOAD_SIZE_MB=10
ALLOWED_IMAGE_FORMATS=image/jpeg,image/png,image/webp

# Security
SECRET_KEY=change-this-to-a-random-string-in-production
```

**Replace:**
- `OPENAI_API_KEY` with your actual OpenAI key
- `GEMINI_API_KEY` with your actual Gemini key
- `FIREBASE_PROJECT_ID` with your Firebase project ID
- `FIREBASE_STORAGE_BUCKET` with your storage bucket name

### 2.6 Test Backend Startup

```bash
uvicorn app.main:app --reload --port 9000
```

✅ **Success if you see:**
```
INFO:     Uvicorn running on http://0.0.0.0:9000 (Press CTRL+C to quit)
INFO:     Started reloader process
🚀 Starting Parx Planner Backend...
Environment: development
✅ All services initialized successfully
```

Visit: [http://localhost:8000/docs](http://localhost:8000/docs) to see API documentation

---

## 🔧 Step 3: Frontend Setup

### 3.1 Open New Terminal & Navigate to Frontend

```bash
cd festipin/frontend
```

### 3.2 Install Dependencies

```bash
npm install
```

### 3.3 Create `.env.local` File

Create `festipin/frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000

# Firebase Config (from Step 1.5)
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id
```

### 3.4 Start Development Server

```bash
npm run dev
```

✅ **Success if you see:**
```
  ▲ Next.js 14.1.0
  - Local:        http://localhost:3000
  - Network:      http://192.168.x.x:3000

 ✓ Ready in 2.5s
```

Visit: [http://localhost:3000](http://localhost:3000)

---

## 🧪 Step 4: Test the Integration

### 4.1 Test Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0"
}
```

### 4.2 Test Frontend → Backend Connection

1. Open [http://localhost:3000](http://localhost:3000)
2. Select **"Text Prompt"** tab
3. Enter: `"Plan a unicorn party for my 7-year-old"`
4. Click **"Generate Party Plan"**
5. Check browser console (F12) for API call logs

---

## 🔧 Optional: Redis Setup (for caching)

### Using Docker (Recommended)

```bash
docker run --name parx-redis -p 6379:6379 -d redis:alpine
```

### Using Homebrew (macOS)

```bash
brew install redis
brew services start redis
```

### Verify Redis

```bash
redis-cli ping
# Should return: PONG
```

---

## 📁 Project Structure Overview

```
festipin/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── api/routes/          # API endpoints
│   │   ├── models/              # Pydantic models
│   │   ├── core/                # Config & logging
│   │   └── services/            # Business logic (TODO)
│   ├── requirements.txt
│   ├── .env                     # YOUR SECRETS
│   └── firebase-credentials.json
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Home page
│   │   │   └── layout.tsx       # Root layout
│   │   ├── components/
│   │   │   └── input/           # Input components
│   │   └── styles/
│   │       └── globals.css
│   ├── package.json
│   └── .env.local               # YOUR SECRETS
│
└── README.md
```

---

## 🚨 Troubleshooting

### Backend won't start

**Error:** `No module named 'app'`
```bash
# Make sure you're in backend/ directory
cd backend
# Make sure venv is activated
source venv/bin/activate
# Try running from parent directory
cd ..
PYTHONPATH=backend uvicorn backend.app.main:app --reload
```

**Error:** `GOOGLE_APPLICATION_CREDENTIALS not found`
```bash
# Verify file exists
ls backend/firebase-credentials.json
# Check .env file has correct path
cat backend/.env | grep GOOGLE_APPLICATION_CREDENTIALS
```

### Frontend won't compile

**Error:** `Module not found: Can't resolve '@/components/...'`
```bash
# Clear Next.js cache
rm -rf frontend/.next
# Reinstall dependencies
cd frontend
rm -rf node_modules
npm install
```

### CORS errors in browser

- Make sure backend `API_CORS_ORIGINS` in `.env` includes `http://localhost:3000`
- Restart backend after changing `.env`

### Pinterest scraping fails

This is expected! We haven't implemented it yet. The endpoint returns a mock response.

---

## ✅ Next Steps After Setup

Once everything is running:

1. **Week 1 Remaining Tasks:**
   - [ ] Implement Pinterest scraping service
   - [ ] Integrate GPT-4 Vision API
   - [ ] Create Firestore service layer
   - [ ] Build storage upload handler

2. **Test API Endpoints:**
   - Visit http://localhost:8000/docs
   - Try POST `/api/v1/input/process` with different input types

3. **Explore Frontend:**
   - Test all three input modes (Pinterest URL, Upload, Prompt)
   - Check network tab to see API calls

---

## 📞 Getting Help

- Check [README.md](./README.md) for architecture overview
- API docs: http://localhost:8000/docs
- Frontend: http://localhost:3000

---

**🎉 You're all set! Ready to start building the Pinterest scraper and vision AI integration.**

