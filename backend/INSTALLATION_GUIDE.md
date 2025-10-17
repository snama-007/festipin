# 🚀 FestiPin Backend - Installation Guide

## Issues Fixed
✅ Resolved dependency conflicts (langchain, langgraph versions)
✅ Fixed duplicate `httpx` and `redis` entries
✅ Changed to `opencv-python-headless` (no GUI dependencies)
✅ Added explicit version constraints for stability
✅ Python 3.9+ compatible

---

## 📋 Prerequisites

- **Python**: 3.9, 3.10, or 3.11
- **pip**: Latest version
- **Redis**: For caching (optional but recommended)
- **libmagic**: For file type detection

---

## 🔧 Installation Steps

### Step 1: Clean Environment

```bash
cd backend

# Remove old virtual environment if it exists
rm -rf venv .venv

# Remove any cached pip files
rm -rf ~/.cache/pip/*

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
```

### Step 2: Create Fresh Virtual Environment

```bash
# Create new virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Upgrade pip, setuptools, wheel
pip install --upgrade pip setuptools wheel
```

### Step 3: Install System Dependencies (macOS)

```bash
# Install libmagic for python-magic
brew install libmagic

# Install Redis (optional but recommended)
brew install redis

# Start Redis
brew services start redis
```

### Step 4: Install Python Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# This should now work without conflicts!
```

### Step 5: Install Playwright Browsers (for scraping)

```bash
# Install Playwright browser binaries
playwright install chromium

# Or install all browsers
playwright install
```

### Step 6: Verify Installation

```bash
# Test imports
python3 -c "
import fastapi
import pydantic
import langchain
import openai
import redis
print('✅ All core dependencies installed successfully!')
"
```

---

## 🤖 AI Model Setup (Optional - For Motif Module)

The Motif module requires additional AI models. Install based on your system:

### Option A: CPU-Only (Development)

```bash
# Install PyTorch CPU version
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install transformers
pip install transformers==4.37.0

# Install Segment Anything
pip install git+https://github.com/facebookresearch/segment-anything.git
```

### Option B: GPU/CUDA (Production)

```bash
# For CUDA 11.8 (check your CUDA version first)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Install transformers
pip install transformers==4.37.0

# Install Segment Anything
pip install git+https://github.com/facebookresearch/segment-anything.git

# Verify GPU access
python3 -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
```

---

## 🔍 Troubleshooting

### Issue 1: "No module named 'magic'"

```bash
# Install python-magic and libmagic
pip install python-magic
brew install libmagic  # macOS
# OR
apt-get install libmagic1  # Ubuntu/Debian
```

### Issue 2: Redis Connection Error

```bash
# Check if Redis is running
redis-cli ping

# Should return: PONG

# If not running:
brew services start redis  # macOS
# OR
sudo systemctl start redis  # Linux
```

### Issue 3: OpenCV Import Error

```bash
# Uninstall opencv-python if installed
pip uninstall opencv-python opencv-contrib-python

# Install headless version
pip install opencv-python-headless==4.9.0.80
```

### Issue 4: Playwright Browser Not Found

```bash
# Reinstall Playwright browsers
playwright install --force chromium
```

### Issue 5: Still Getting Conflicts?

```bash
# Nuclear option: Fresh start
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
```

---

## 🧪 Test Installation

Create a test file to verify everything works:

```python
# test_installation.py

import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
import redis.asyncio as redis

app = FastAPI()

class HealthCheck(BaseModel):
    status: str
    message: str

@app.get("/health", response_model=HealthCheck)
async def health_check():
    # Test Redis connection
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        await r.ping()
        redis_status = "✅ Connected"
    except Exception as e:
        redis_status = f"❌ Error: {str(e)}"

    return HealthCheck(
        status="healthy",
        message=f"Redis: {redis_status}"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Run the test:
```bash
python test_installation.py

# In another terminal:
curl http://localhost:9000/health
```

---

## 📦 Dependency Summary

### Core Dependencies (Required)
- **FastAPI**: Web framework
- **Pydantic**: Data validation
- **Redis**: Caching
- **Pillow**: Image processing
- **python-magic**: File type detection

### AI/ML Dependencies (Optional)
- **langchain**: LLM orchestration
- **openai**: GPT-4 API
- **google-generativeai**: Gemini API
- **torch**: PyTorch (for Segment Anything)
- **transformers**: HuggingFace models

### Scraping Dependencies
- **playwright**: Browser automation
- **httpx**: Async HTTP client
- **beautifulsoup4**: HTML parsing

---

## 🚀 Quick Start After Installation

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Set environment variables
cp .env.example .env
# Edit .env with your API keys

# 3. Run development server
uvicorn app.main:app --reload --port 8000

# 4. Access API docs
# Open: http://localhost:9000/docs
```

---

## 📊 Verify Versions

```bash
# Check installed versions
pip list | grep -E "fastapi|pydantic|langchain|redis|opencv"

# Expected output:
# fastapi              0.109.0
# pydantic             2.5.3
# langchain            0.1.0
# redis                5.0.1
# opencv-python-headless 4.9.0.80
```

---

## 🆘 Still Having Issues?

### Check Python Version
```bash
python3 --version
# Must be 3.9.x, 3.10.x, or 3.11.x
```

### Check pip Version
```bash
pip --version
# Should be 23.x or higher
```

### Create Issue Log
```bash
# Save installation log for debugging
pip install -r requirements.txt > install.log 2>&1
cat install.log
```

---

## 💡 Pro Tips

1. **Always use virtual environment** - Never install globally
2. **Pin versions** - The requirements.txt has tested versions
3. **Upgrade pip first** - Old pip causes many issues
4. **Check system dependencies** - libmagic, Redis, etc.
5. **Use --no-cache-dir** - If having persistent issues

---

## ✅ Success Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] pip upgraded to latest
- [ ] requirements.txt installed without errors
- [ ] libmagic installed (for python-magic)
- [ ] Redis installed and running
- [ ] Playwright browsers installed
- [ ] Test script runs successfully
- [ ] Can access http://localhost:9000/docs

---

**Installation should now complete successfully! 🎉**

If you still encounter issues, please share the complete error message.
