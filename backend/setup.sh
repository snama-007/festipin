#!/bin/bash

# Quick Setup Script for Agent Orchestration System

echo "🚀 Setting up Agent Orchestration System..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Please run this script from the backend directory"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed successfully"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Create memory store directory
echo "📁 Creating memory store directory..."
mkdir -p memory_store/events
mkdir -p memory_store/backups
mkdir -p memory_store/temp

echo "✅ Memory store directories created"

# Test the system
echo "🧪 Testing the system..."
python3 -c "
try:
    from app.services.simple_orchestrator import get_orchestrator
    from app.services.local_memory_store import get_memory_store, update_workflow_status, add_user_feedback
    from app.services.agent_registry import get_agent_registry
    print('✅ All imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ System test passed"
else
    echo "❌ System test failed"
    exit 1
fi

echo ""
echo "🎉 Setup complete! You can now start the server:"
echo "   uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload"
echo ""
echo "📚 For more information, see QUICK_START_GUIDE.md"
