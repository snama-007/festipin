# Project Motif - Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide will help you get Project Motif running locally for development and testing.

## Prerequisites

- Python 3.9+
- Node.js 16+
- npm or yarn
- Google Gemini API key (optional - system works in mock mode without it)

## Quick Setup

### 1. Backend Setup

```bash
# Navigate to backend
cd festipin/backend

# Install dependencies
pip install -r requirements.txt

# Set up environment (optional)
echo "GEMINI_API_KEY=your_key_here" > .env

# Start the server
python3 -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
# Navigate to frontend (in a new terminal)
cd festipin/frontend

# Install dependencies
npm install

# Start the development server
npm run dev -- -p 3000
```

### 3. Access the Application

- **Frontend**: http://localhost:3000/motif
- **Backend API**: http://localhost:8000/motif
- **API Docs**: http://localhost:8000/docs

## 🎨 First Generation

### Using the Web Interface

1. Go to http://localhost:3000/motif
2. Click the "Generate" tab
3. Enter a prompt like: "A beautiful birthday party setup with colorful balloons"
4. Select a style (optional)
5. Click "Generate Decoration"
6. View your generated image!

### Using the API

```bash
# Generate an image
curl -X POST "http://localhost:8000/motif/generation/generate-from-prompt" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful birthday party setup with colorful balloons",
    "style": "party",
    "user_id": "test_user"
  }'
```

## 📚 View History

1. Go to http://localhost:3000/motif
2. Click the "History" tab
3. View all your generated images
4. Mark favorites, add tags, and search

## 🔧 Configuration

### Environment Variables

Create `.env` in the backend directory:

```bash
# Required for real generation (optional - works in mock mode without)
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
OPENAI_API_KEY=your_openai_key_here
GEMINI_MODEL=gemini-2.0-flash
```

### Getting a Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API key"
4. Copy the key and add it to your `.env` file

## 🧪 Testing Features

### Mock Mode (No API Key Required)

The system automatically runs in mock mode when no API key is provided:
- Generates placeholder images
- Simulates real API responses
- Perfect for development and testing

### Batch Generation

```bash
# Generate multiple images at once
curl -X POST "http://localhost:8000/motif/generation/generate-batch" \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": [
      "A birthday party with balloons",
      "A wedding decoration with flowers",
      "A children party with toys"
    ],
    "style": "party",
    "user_id": "test_user",
    "max_concurrent": 2
  }'
```

### History Management

```bash
# Get generation history
curl "http://localhost:8000/motif/history/test_user?limit=5"

# Get user statistics
curl "http://localhost:8000/motif/history/stats/test_user"

# Mark as favorite
curl -X POST "http://localhost:8000/motif/history/favorite" \
  -H "Content-Type: application/json" \
  -d '{
    "generation_id": "your_generation_id",
    "user_id": "test_user",
    "is_favorite": true
  }'
```

## 🎯 Available Styles

- **party**: Vibrant, colorful, festive
- **elegant**: Sophisticated, refined, minimalist
- **fun**: Playful, whimsical, cheerful
- **romantic**: Soft, dreamy, intimate
- **birthday**: Colorful, celebratory, cake
- **wedding**: Elegant, romantic, white flowers
- **holiday**: Festive, seasonal, traditional

## 🐛 Troubleshooting

### Common Issues

#### Server won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing processes
pkill -f "uvicorn.*8000"

# Try a different port
python3 -m uvicorn app.main:app --reload --port 8001
```

#### Frontend won't start
```bash
# Check if port 3000 is in use
lsof -i :3000

# Try a different port
npm run dev -- -p 3001
```

#### API errors
- Check the backend logs for detailed error messages
- Verify your API key is correct (if using real generation)
- The system automatically falls back to mock mode if there are issues

### Debug Mode

Enable detailed logging:

```bash
export DEBUG=true
python3 -m uvicorn app.main:app --reload --port 8000
```

## 📖 Next Steps

1. **Read the full documentation**: [MOTIF_DOCUMENTATION.md](./MOTIF_DOCUMENTATION.md)
2. **Explore the API**: Visit http://localhost:8000/docs
3. **Try different styles**: Experiment with various style presets
4. **Generate batches**: Create multiple images at once
5. **Manage history**: Use favorites and tags to organize your generations

## 🆘 Need Help?

- **Documentation**: Check [MOTIF_DOCUMENTATION.md](./MOTIF_DOCUMENTATION.md)
- **API Reference**: Visit http://localhost:8000/docs
- **Issues**: Create an issue in the repository
- **Debug**: Enable debug mode and check logs

---

**Happy Generating! 🎉**
