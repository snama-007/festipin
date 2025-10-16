#!/bin/bash
# Quick fix for OpenAI DefaultHttpxClient error

echo "🔧 Fixing OpenAI + LangChain compatibility..."
echo ""

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "❌ No virtual environment found. Run ./QUICK_INSTALL.sh first"
    exit 1
fi

# Uninstall problematic packages
echo ""
echo "🗑️  Removing old langchain packages..."
pip uninstall -y langchain langchain-openai langchain-core langchain-community 2>/dev/null

# Reinstall with correct versions
echo ""
echo "📥 Installing compatible versions..."
pip install langchain==0.1.20 langchain-openai==0.1.8 langchain-core==0.1.52 langchain-community==0.0.38

# Test
echo ""
echo "🧪 Testing OpenAI + LangChain..."
python3 -c "
from openai import AsyncOpenAI
from langchain_openai import ChatOpenAI
print('✅ OpenAI and LangChain are now compatible!')
"

echo ""
echo "✅ Fix complete! You can now run your application."
