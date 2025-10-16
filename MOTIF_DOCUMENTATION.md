# Project Motif - Gemini Flash Image Generation System

## Overview

Project Motif is an AI-powered image generation system that creates beautiful party decorations using Google Gemini Flash. The system supports both text-to-image and image-to-image generation with various style presets, batch processing, and comprehensive history management.

## Features

### 🎨 **Core Image Generation**
- **Text-to-Image**: Generate decorations from text prompts
- **Image-to-Image**: Generate decorations inspired by uploaded images
- **Style Presets**: 7 predefined styles (party, elegant, fun, romantic, birthday, wedding, holiday)
- **Prompt Enhancement**: Automatic prompt enhancement with style keywords
- **Mock Mode**: Fallback mode when API key is not configured

### 🚀 **Batch Processing**
- **Concurrent Generation**: Generate multiple images simultaneously
- **Rate Limiting**: Configurable concurrency control (max 3 concurrent by default)
- **Batch Validation**: Input validation for batch requests
- **Error Handling**: Graceful handling of individual failures in batch operations

### 📚 **History & Management**
- **Generation History**: Complete history of all generated images
- **Favorites System**: Mark generations as favorites
- **Tagging**: Add custom tags to generations
- **Search & Filter**: Search prompts and filter by style, type, or favorites
- **Statistics**: User statistics including success rates and usage patterns

### 🔧 **Technical Features**
- **RESTful API**: Complete REST API with FastAPI
- **Real-time Updates**: WebSocket support for live generation updates
- **File Storage**: Local file-based storage for development
- **Error Tracking**: Comprehensive error logging and tracking
- **Performance Monitoring**: Generation time tracking and optimization

## Architecture

### Backend Components

```
festipin/backend/
├── app/
│   ├── api/routes/motif/
│   │   ├── generation.py      # Image generation endpoints
│   │   ├── history.py         # History management endpoints
│   │   └── __init__.py        # Router configuration
│   ├── services/motif/
│   │   ├── gemini_image_generator.py  # Core generation service
│   │   └── history_service.py         # History management service
│   ├── models/motif/
│   │   ├── generation.py      # Generation request/response models
│   │   ├── history.py         # History and stats models
│   │   └── __init__.py        # Model exports
│   └── core/
│       └── config.py          # Configuration management
```

### Frontend Components

```
festipin/frontend/src/
├── app/motif/
│   └── page.tsx               # Main Motif page with tabs
├── components/motif/
│   ├── ImageGenerationViewer.tsx      # Generation interface
│   └── GenerationHistoryViewer.tsx    # History management interface
```

## API Documentation

### Base URL
```
http://localhost:8000/motif
```

### Authentication
Currently uses simple user ID-based authentication. In production, implement proper JWT or OAuth2.

### Endpoints

#### Image Generation

##### Generate from Prompt
```http
POST /generation/generate-from-prompt
Content-Type: application/json

{
  "prompt": "A beautiful birthday party setup with colorful balloons",
  "style": "party",
  "user_id": "user123"
}
```

**Response:**
```json
{
  "success": true,
  "generation_id": "uuid",
  "image_data": "data:image/png;base64,...",
  "prompt_used": "Enhanced prompt with style",
  "style_applied": "party",
  "generated_at": "2025-10-15T21:34:39.967287",
  "mock_mode": false
}
```

##### Generate from Inspiration Image
```http
POST /generation/generate-from-inspiration
Content-Type: multipart/form-data

inspiration_image: [file]
prompt: "Transform this into a party decoration"
style: "elegant"
user_id: "user123"
```

##### Batch Generation
```http
POST /generation/generate-batch
Content-Type: application/json

{
  "prompts": [
    "A beautiful birthday party setup",
    "An elegant wedding decoration",
    "A fun children party"
  ],
  "style": "party",
  "user_id": "user123",
  "max_concurrent": 3
}
```

**Response:**
```json
{
  "success": true,
  "batch_id": "uuid",
  "total_prompts": 3,
  "successful_count": 3,
  "failed_count": 0,
  "successful_generations": [...],
  "failed_generations": [],
  "generated_at": "2025-10-15T21:34:39.967287",
  "mock_mode": true
}
```

#### History Management

##### Get Generation History
```http
GET /history/{user_id}?limit=20&offset=0&style=party&favorites_only=false&search_query=birthday
```

##### Toggle Favorite
```http
POST /history/favorite
Content-Type: application/json

{
  "generation_id": "uuid",
  "user_id": "user123",
  "is_favorite": true
}
```

##### Update Tags
```http
POST /history/tags
Content-Type: application/json

{
  "generation_id": "uuid",
  "user_id": "user123",
  "tags": ["birthday", "colorful"],
  "action": "add"
}
```

##### Get User Statistics
```http
GET /history/stats/{user_id}
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "user_id": "user123",
    "total_generations": 25,
    "successful_generations": 23,
    "failed_generations": 2,
    "favorite_count": 8,
    "total_processing_time": 45.2,
    "average_rating": 4.2,
    "most_used_style": "party",
    "most_used_type": "text_to_image",
    "last_generation": "2025-10-15T21:34:39.967287"
  }
}
```

#### Style Management

##### Get Available Styles
```http
GET /generation/styles
```

**Response:**
```json
{
  "success": true,
  "styles": [
    {
      "key": "party",
      "name": "Party",
      "description": "vibrant, colorful, festive, celebration, balloons, confetti, fun"
    },
    {
      "key": "elegant",
      "name": "Elegant", 
      "description": "sophisticated, refined, minimalist, classy, elegant, upscale"
    }
  ]
}
```

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_MODEL=gemini-2.0-flash
```

### Google Gemini API Setup

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Add the key to your `.env` file
4. The system will automatically detect the key and enable real generation

Without an API key, the system runs in mock mode for testing.

## Installation & Setup

### Backend Setup

```bash
cd festipin/backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your API keys

# Run the server
python3 -m uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd festipin/frontend

# Install dependencies
npm install

# Run the development server
npm run dev -- -p 3000
```

## Usage Examples

### Basic Text-to-Image Generation

```python
import requests

# Generate a single image
response = requests.post(
    "http://localhost:8000/motif/generation/generate-from-prompt",
    json={
        "prompt": "A beautiful birthday party setup with colorful balloons and confetti",
        "style": "party",
        "user_id": "user123"
    }
)

result = response.json()
if result["success"]:
    print(f"Generated image: {result['generation_id']}")
    # Save image data
    with open("generated_image.png", "wb") as f:
        f.write(base64.b64decode(result["image_data"].split(",")[1]))
```

### Batch Generation

```python
# Generate multiple images
response = requests.post(
    "http://localhost:8000/motif/generation/generate-batch",
    json={
        "prompts": [
            "A birthday party with balloons",
            "A wedding decoration with flowers",
            "A children party with toys"
        ],
        "style": "party",
        "user_id": "user123",
        "max_concurrent": 2
    }
)

result = response.json()
print(f"Batch ID: {result['batch_id']}")
print(f"Successful: {result['successful_count']}/{result['total_prompts']}")
```

### History Management

```python
# Get user's generation history
response = requests.get(
    "http://localhost:8000/motif/history/user123?limit=10&favorites_only=true"
)

history = response.json()
for generation in history["generations"]:
    print(f"Prompt: {generation['prompt']}")
    print(f"Style: {generation['style']}")
    print(f"Favorite: {generation['is_favorite']}")

# Mark as favorite
requests.post(
    "http://localhost:8000/motif/history/favorite",
    json={
        "generation_id": "uuid",
        "user_id": "user123",
        "is_favorite": True
    }
)
```

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "Prompt must be at least 10 characters long"
}
```

#### 404 Not Found
```json
{
  "detail": "Generation not found"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error: API connection failed"
}
```

### Error Recovery

The system includes comprehensive error handling:

1. **API Failures**: Automatic fallback to mock mode
2. **Rate Limiting**: Configurable concurrency control
3. **Validation**: Input validation for all endpoints
4. **Logging**: Detailed error logging for debugging

## Performance Optimization

### Generation Speed
- **Concurrent Processing**: Batch operations use asyncio for parallel processing
- **Rate Limiting**: Prevents API rate limit violations
- **Caching**: Mock images are cached for faster testing

### Memory Management
- **Streaming**: Large images are handled efficiently
- **Cleanup**: Temporary files are automatically cleaned up
- **Background Tasks**: Non-blocking operations for better performance

## Security Considerations

### API Key Management
- Store API keys in environment variables
- Never commit API keys to version control
- Use different keys for development and production

### Input Validation
- All user inputs are validated
- File uploads are restricted to image formats
- Prompt length limits prevent abuse

### Rate Limiting
- Built-in concurrency control
- Per-user rate limiting (configurable)
- API quota management

## Troubleshooting

### Common Issues

#### "API connection test failed"
- Check your GEMINI_API_KEY in the .env file
- Verify the API key is valid and has proper permissions
- The system will fall back to mock mode automatically

#### "Generation failed"
- Check the prompt length (minimum 10 characters)
- Verify the style parameter is valid
- Check server logs for detailed error messages

#### "History not showing"
- Background tasks may take time to complete
- Check if the history service is running
- Verify user_id is consistent across requests

### Debug Mode

Enable debug logging by setting the environment variable:
```bash
export DEBUG=true
```

This will provide detailed logs for troubleshooting.

## Future Enhancements

### Planned Features
- **Real-time Generation**: WebSocket support for live updates
- **Advanced Styles**: Custom style creation and management
- **Image Editing**: In-browser image editing capabilities
- **Social Features**: Sharing and collaboration features
- **Analytics**: Advanced usage analytics and insights

### Performance Improvements
- **Caching Layer**: Redis-based caching for faster responses
- **CDN Integration**: Image delivery optimization
- **Database Migration**: Move from file-based to database storage
- **Microservices**: Split into smaller, focused services

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Standards
- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Add comprehensive docstrings
- Include error handling for all new features

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation
- Contact the development team

---

**Last Updated**: October 15, 2025  
**Version**: 1.0.0  
**Status**: Active Development
