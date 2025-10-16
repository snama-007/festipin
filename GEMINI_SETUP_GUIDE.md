# Gemini Flash Image Generation Setup Guide

## Overview
This guide explains how to set up Google Gemini Flash for image generation in the Motif section of Festipin.

## Prerequisites
- Google Cloud account with Gemini API access
- Python 3.9+ environment
- FastAPI backend running

## Step 1: Get Gemini API Key

1. **Visit Google AI Studio**
   - Go to [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account

2. **Create API Key**
   - Click "Create API Key"
   - Choose your project or create a new one
   - Copy the generated API key

3. **Enable Gemini API**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to "APIs & Services" > "Library"
   - Search for "Generative Language API"
   - Click "Enable"

## Step 2: Configure Environment Variables

### Option A: Environment File (.env)
Create a `.env` file in the backend directory:

```bash
# Gemini Configuration
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Other required variables
OPENAI_API_KEY=your_openai_key_here
FIREBASE_PROJECT_ID=your_firebase_project_id
```

### Option B: System Environment Variables
Export the variables in your shell:

```bash
export GEMINI_API_KEY="your_actual_gemini_api_key_here"
export OPENAI_API_KEY="your_openai_key_here"
export FIREBASE_PROJECT_ID="your_firebase_project_id"
```

## Step 3: Test the Configuration

1. **Start the Backend Server**
   ```bash
   cd backend
   python3 -m uvicorn app.main:app --reload --port 8000
   ```

2. **Test API Endpoints**
   ```bash
   # Test styles endpoint
   curl -X GET "http://localhost:8000/motif/generation/styles"
   
   # Test image generation
   curl -X POST "http://localhost:8000/motif/generation/generate-from-prompt" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "A beautiful birthday party decoration with colorful balloons", "style": "party", "user_id": "test_user"}'
   ```

## Step 4: Frontend Integration

1. **Start Frontend Server**
   ```bash
   cd frontend
   npm run dev -- -p 3000
   ```

2. **Access Motif Page**
   - Open [http://localhost:3000/motif](http://localhost:3000/motif)
   - Upload an image or enter a prompt
   - Select a style and generate

## Available Models

The system automatically tries these models in order:
1. `gemini-1.5-pro` (Recommended)
2. `gemini-1.5-flash` (Faster)
3. `gemini-pro` (Legacy)
4. `gemini-pro-vision` (Vision-focused)

## Style Presets

Available style presets:
- **Party**: Vibrant, colorful, festive, celebration, balloons, confetti, fun
- **Elegant**: Sophisticated, refined, minimalist, classy, elegant, upscale
- **Fun**: Playful, whimsical, cheerful, bright, cartoonish, cute
- **Romantic**: Soft, dreamy, intimate, warm, pastel, romantic, gentle
- **Birthday**: Colorful, celebratory, cake, balloons, party hats, festive
- **Wedding**: Elegant, romantic, white, flowers, sophisticated, beautiful
- **Holiday**: Festive, seasonal, traditional, celebratory, themed

## Troubleshooting

### Common Issues

1. **"API key not configured"**
   - Ensure `GEMINI_API_KEY` is set correctly
   - Check that the API key is valid and active

2. **"Model not found"**
   - The system will automatically fall back to mock mode
   - Check your Google Cloud project has Gemini API enabled

3. **"Rate limit exceeded"**
   - Wait a few minutes before retrying
   - Consider upgrading your Google Cloud plan

4. **"Invalid API key"**
   - Verify the API key is correct
   - Check that the key has proper permissions

### Mock Mode

If the API key is not configured or there are connection issues, the system automatically falls back to mock mode:
- Generates placeholder images
- Simulates API responses
- Allows frontend testing without API costs

### Logs

Check the backend logs for detailed error messages:
```bash
tail -f backend.log
```

## API Endpoints

### GET /motif/generation/styles
Returns available style presets.

### POST /motif/generation/generate-from-prompt
Generate image from text prompt only.

**Request Body:**
```json
{
  "prompt": "A beautiful birthday party decoration",
  "style": "party",
  "user_id": "user123"
}
```

### POST /motif/generation/generate-from-inspiration
Generate image from inspiration image + prompt.

**Request:**
- `inspiration_image`: File upload
- `prompt`: Text prompt
- `style`: Optional style preset
- `user_id`: Optional user ID

### POST /motif/generation/feedback/{generation_id}
Submit user feedback for generated images.

**Request Body:**
```json
{
  "rating": 5,
  "comment": "Great image quality!"
}
```

## Cost Considerations

- Gemini API has usage limits and costs
- Free tier includes limited requests per month
- Monitor usage in Google Cloud Console
- Consider implementing rate limiting for production

## Security Notes

- Never commit API keys to version control
- Use environment variables for sensitive data
- Implement proper authentication for production
- Consider API key rotation policies

## Next Steps

1. **Production Deployment**
   - Set up proper environment variable management
   - Implement rate limiting
   - Add monitoring and alerting

2. **Feature Enhancements**
   - Batch image generation
   - Image history and favorites
   - Advanced style customization
   - User feedback analytics

3. **Performance Optimization**
   - Caching generated images
   - Async processing for large batches
   - CDN integration for image delivery
