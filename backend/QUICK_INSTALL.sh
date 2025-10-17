#!/bin/bash
# ============================================
# FestiPin Backend - Quick Installation Script
# ============================================

set -e  # Exit on error

echo "🚀 FestiPin Backend - Quick Installation"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"
else
    echo -e "${RED}✗${NC} Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Check if in backend directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}✗${NC} requirements.txt not found. Are you in the backend directory?"
    exit 1
fi

# Clean old installation
echo ""
echo "🧹 Cleaning old installation..."
rm -rf venv .venv
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}✓${NC} Cleaned"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv
echo -e "${GREEN}✓${NC} Virtual environment created"

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓${NC} Activated"

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel --quiet
echo -e "${GREEN}✓${NC} pip upgraded"

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
echo "   This may take 2-5 minutes..."
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓${NC} Dependencies installed"

# Install Playwright browsers
echo ""
echo "🎭 Installing Playwright browsers..."
playwright install chromium --quiet
echo -e "${GREEN}✓${NC} Playwright browsers installed"

# Check for Redis
echo ""
echo "🔍 Checking Redis..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Redis is running"
    else
        echo -e "${YELLOW}⚠${NC}  Redis installed but not running"
        echo "   Start with: brew services start redis"
    fi
else
    echo -e "${YELLOW}⚠${NC}  Redis not found (optional but recommended)"
    echo "   Install with: brew install redis"
fi

# Run test script
echo ""
echo "🧪 Running installation tests..."
python3 test_installation.py

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# FestiPin Backend Configuration

# Environment
ENVIRONMENT=development
DEBUG=true

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_CORS_ORIGINS=http://localhost:3000,http://localhost:9010

# AI Services
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here

# Firebase
GOOGLE_APPLICATION_CREDENTIALS=firebase-credentials.json
FIREBASE_PROJECT_ID=your_project_id

# Redis
REDIS_URL=redis://localhost:6379
REDIS_DB=0

# Storage
STORAGE_BUCKET=your_storage_bucket_name

# Logging
LOG_LEVEL=INFO
EOF
    echo -e "${GREEN}✓${NC} .env file created"
    echo -e "   ${YELLOW}⚠${NC}  Remember to add your API keys!"
fi

# Success message
echo ""
echo "========================================"
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys"
echo "2. Start Redis: brew services start redis"
echo "3. Run server: uvicorn app.main:app --reload"
echo "4. Access docs: http://localhost:9000/docs"
echo ""
echo "Happy coding! 🎉"
