#!/bin/bash

# 🚀 Festipin Backend - Quick Start Script
# Starts the backend server ready for frontend integration

echo "🎉 Starting Festipin Backend..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv-3.12" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Run: python3.12 -m venv venv-3.12"
    echo "   Then: source venv-3.12/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv-3.12/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found, using defaults"
fi

# Display configuration
echo ""
echo "📋 Configuration:"
echo "   • Backend URL: http://localhost:9000"
echo "   • API Docs: http://localhost:9000/docs"
echo "   • Frontend CORS: http://localhost:9010"
echo "   • WebSocket: ws://localhost:9000/ws/party/{party_id}"
echo ""
echo "🔗 API Endpoints Ready:"
echo "   • POST /api/v1/input/process-hybrid - Hybrid input processing"
echo "   • POST /api/v1/event-driven/party - Event-driven planning"
echo "   • POST /api/v1/vision/analyze - Image analysis"
echo "   • GET  /health - Health check"
echo ""

# Start server
echo "🚀 Starting server..."
echo "   (Press Ctrl+C to stop)"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
