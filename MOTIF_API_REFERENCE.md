# Project Motif - API Reference

## Base URL
```
http://localhost:8000/motif
```

## Authentication
Currently uses simple user ID-based authentication. Include `user_id` in request body or as a query parameter.

## Response Format

All API responses follow this format:

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional success message"
}
```

### Error Response
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Image Generation Endpoints

### Generate from Text Prompt

**Endpoint:** `POST /generation/generate-from-prompt`

**Description:** Generate an image from a text prompt with optional style enhancement.

**Request Body:**
```json
{
  "prompt": "string (required, min 10 chars, max 1000 chars)",
  "style": "string (optional, one of: party, elegant, fun, romantic, birthday, wedding, holiday)",
  "user_id": "string (optional, defaults to 'anonymous')"
}
```

**Response:**
```json
{
  "success": true,
  "generation_id": "uuid",
  "image_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
  "prompt_used": "Enhanced prompt with style keywords",
  "style_applied": "party",
  "generated_at": "2025-10-15T21:34:39.967287",
  "mock_mode": false
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/motif/generation/generate-from-prompt" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful birthday party setup with colorful balloons",
    "style": "party",
    "user_id": "user123"
  }'
```

### Generate from Inspiration Image

**Endpoint:** `POST /generation/generate-from-inspiration`

**Description:** Generate an image inspired by an uploaded image and text prompt.

**Request:** `multipart/form-data`
- `inspiration_image`: File (required, image file)
- `prompt`: String (required, min 10 chars, max 1000 chars)
- `style`: String (optional, style preset)
- `user_id`: String (optional, defaults to 'anonymous')

**Response:** Same as text-to-image generation

**Example:**
```bash
curl -X POST "http://localhost:8000/motif/generation/generate-from-inspiration" \
  -F "inspiration_image=@inspiration.jpg" \
  -F "prompt=A party decoration inspired by this image" \
  -F "style=elegant" \
  -F "user_id=user123"
```

### Batch Generation

**Endpoint:** `POST /generation/generate-batch`

**Description:** Generate multiple images from multiple prompts concurrently.

**Request Body:**
```json
{
  "prompts": ["string array (required, 1-10 prompts, each min 10 chars, max 1000 chars)"],
  "style": "string (optional, style preset)",
  "user_id": "string (optional, defaults to 'anonymous')",
  "max_concurrent": "integer (optional, 1-5, defaults to 3)"
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
  "successful_generations": [
    {
      "prompt": "Original prompt",
      "generation_id": "uuid",
      "image_data": "data:image/png;base64,...",
      "prompt_used": "Enhanced prompt",
      "style_applied": "party",
      "index": 0
    }
  ],
  "failed_generations": [],
  "generated_at": "2025-10-15T21:34:39.967287",
  "mock_mode": true
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/motif/generation/generate-batch" \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": [
      "A birthday party with balloons",
      "A wedding decoration with flowers",
      "A children party with toys"
    ],
    "style": "party",
    "user_id": "user123",
    "max_concurrent": 2
  }'
```

### Get Available Styles

**Endpoint:** `GET /generation/styles`

**Description:** Get list of available style presets.

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

## History Management Endpoints

### Get Generation History

**Endpoint:** `GET /history/{user_id}`

**Description:** Get paginated list of user's generation history with optional filtering.

**Query Parameters:**
- `limit`: Integer (optional, 1-100, defaults to 20)
- `offset`: Integer (optional, ≥0, defaults to 0)
- `status`: String (optional, filter by status: pending, processing, completed, failed)
- `generation_type`: String (optional, filter by type: text_to_image, image_to_image, inspiration_based)
- `style`: String (optional, filter by style preset)
- `favorites_only`: Boolean (optional, show only favorites)
- `search_query`: String (optional, search in prompts)

**Response:**
```json
{
  "success": true,
  "generations": [
    {
      "id": "uuid",
      "user_id": "user123",
      "prompt": "Original prompt",
      "enhanced_prompt": "Enhanced prompt",
      "style": "party",
      "generation_type": "text_to_image",
      "status": "completed",
      "image_data": "data:image/png;base64,...",
      "created_at": "2025-10-15T21:34:39.967287",
      "completed_at": "2025-10-15T21:34:41.123456",
      "processing_time": 1.156,
      "rating": 5,
      "feedback": "Great result!",
      "is_favorite": true,
      "tags": ["birthday", "colorful"],
      "metadata": {}
    }
  ],
  "total_count": 25,
  "has_more": true
}
```

**Example:**
```bash
curl "http://localhost:8000/motif/history/user123?limit=10&favorites_only=true&search_query=birthday"
```

### Toggle Favorite

**Endpoint:** `POST /history/favorite`

**Description:** Mark or unmark a generation as favorite.

**Request Body:**
```json
{
  "generation_id": "uuid (required)",
  "user_id": "string (required)",
  "is_favorite": "boolean (required)"
}
```

**Response:**
```json
{
  "success": true,
  "is_favorite": true,
  "message": "Generation marked as favorite"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/motif/history/favorite" \
  -H "Content-Type: application/json" \
  -d '{
    "generation_id": "uuid",
    "user_id": "user123",
    "is_favorite": true
  }'
```

### Update Tags

**Endpoint:** `POST /history/tags`

**Description:** Add or remove tags from a generation.

**Request Body:**
```json
{
  "generation_id": "uuid (required)",
  "user_id": "string (required)",
  "tags": ["string array (required)"],
  "action": "string (required, 'add' or 'remove')"
}
```

**Response:**
```json
{
  "success": true,
  "tags": ["birthday", "colorful", "fun"],
  "message": "Tags added successfully"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/motif/history/tags" \
  -H "Content-Type: application/json" \
  -d '{
    "generation_id": "uuid",
    "user_id": "user123",
    "tags": ["birthday", "colorful"],
    "action": "add"
  }'
```

### Get User Statistics

**Endpoint:** `GET /history/stats/{user_id}`

**Description:** Get comprehensive statistics for a user's generation activity.

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

**Example:**
```bash
curl "http://localhost:8000/motif/history/stats/user123"
```

### Get Favorites

**Endpoint:** `GET /history/favorites/{user_id}`

**Description:** Get user's favorite generations.

**Query Parameters:**
- `limit`: Integer (optional, 1-100, defaults to 20)
- `offset`: Integer (optional, ≥0, defaults to 0)

**Response:** Same as generation history response

**Example:**
```bash
curl "http://localhost:8000/motif/history/favorites/user123?limit=5"
```

### Get Recent Generations

**Endpoint:** `GET /history/recent/{user_id}`

**Description:** Get user's most recent generations.

**Query Parameters:**
- `limit`: Integer (optional, 1-50, defaults to 10)

**Response:** Same as generation history response

**Example:**
```bash
curl "http://localhost:8000/motif/history/recent/user123?limit=5"
```

### Delete Generation

**Endpoint:** `DELETE /history/{generation_id}`

**Description:** Soft delete a generation (marks as deleted, doesn't actually remove).

**Query Parameters:**
- `user_id`: String (required, must own the generation)

**Response:**
```json
{
  "success": true,
  "message": "Generation deleted successfully"
}
```

**Example:**
```bash
curl -X DELETE "http://localhost:8000/motif/history/uuid?user_id=user123"
```

## Error Codes

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Common Error Messages

#### Validation Errors
```json
{
  "detail": "Prompt must be at least 10 characters long"
}
```

```json
{
  "detail": "Maximum 10 prompts allowed per batch"
}
```

```json
{
  "detail": "Action must be 'add' or 'remove'"
}
```

#### Not Found Errors
```json
{
  "detail": "Generation not found"
}
```

```json
{
  "detail": "Generation not found or unauthorized"
}
```

#### Server Errors
```json
{
  "detail": "Internal server error: API connection failed"
}
```

```json
{
  "detail": "Internal server error: name 'uuid' is not defined"
}
```

## Rate Limiting

### Batch Generation Limits
- Maximum 10 prompts per batch request
- Maximum 5 concurrent requests (configurable)
- Rate limiting prevents API quota exhaustion

### Individual Generation Limits
- Prompt length: 10-1000 characters
- File size: Reasonable image file sizes
- Concurrent users: No hard limit (depends on server capacity)

## Mock Mode

When no valid API key is provided, the system runs in mock mode:

- Generates placeholder 1x1 pixel PNG images
- Simulates real API response times
- All functionality works except actual image generation
- Perfect for development and testing

## WebSocket Support (Planned)

Future versions will include WebSocket endpoints for:
- Real-time generation progress updates
- Live batch generation status
- Push notifications for completed generations

## SDK Examples

### Python SDK Example

```python
import requests
import base64

class MotifClient:
    def __init__(self, base_url="http://localhost:8000/motif"):
        self.base_url = base_url
    
    def generate_image(self, prompt, style=None, user_id="anonymous"):
        response = requests.post(
            f"{self.base_url}/generation/generate-from-prompt",
            json={
                "prompt": prompt,
                "style": style,
                "user_id": user_id
            }
        )
        return response.json()
    
    def generate_batch(self, prompts, style=None, user_id="anonymous", max_concurrent=3):
        response = requests.post(
            f"{self.base_url}/generation/generate-batch",
            json={
                "prompts": prompts,
                "style": style,
                "user_id": user_id,
                "max_concurrent": max_concurrent
            }
        )
        return response.json()
    
    def get_history(self, user_id, limit=20, offset=0, **filters):
        params = {"limit": limit, "offset": offset, **filters}
        response = requests.get(f"{self.base_url}/history/{user_id}", params=params)
        return response.json()
    
    def toggle_favorite(self, generation_id, user_id, is_favorite):
        response = requests.post(
            f"{self.base_url}/history/favorite",
            json={
                "generation_id": generation_id,
                "user_id": user_id,
                "is_favorite": is_favorite
            }
        )
        return response.json()

# Usage
client = MotifClient()

# Generate single image
result = client.generate_image(
    "A beautiful birthday party setup",
    style="party",
    user_id="user123"
)

# Generate batch
batch_result = client.generate_batch([
    "A birthday party with balloons",
    "A wedding decoration with flowers"
], style="party")

# Get history
history = client.get_history("user123", limit=10, favorites_only=True)
```

### JavaScript SDK Example

```javascript
class MotifClient {
    constructor(baseUrl = 'http://localhost:8000/motif') {
        this.baseUrl = baseUrl;
    }
    
    async generateImage(prompt, style = null, userId = 'anonymous') {
        const response = await fetch(`${this.baseUrl}/generation/generate-from-prompt`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, style, user_id: userId })
        });
        return response.json();
    }
    
    async generateBatch(prompts, style = null, userId = 'anonymous', maxConcurrent = 3) {
        const response = await fetch(`${this.baseUrl}/generation/generate-batch`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompts, style, user_id: userId, max_concurrent: maxConcurrent })
        });
        return response.json();
    }
    
    async getHistory(userId, options = {}) {
        const params = new URLSearchParams(options);
        const response = await fetch(`${this.baseUrl}/history/${userId}?${params}`);
        return response.json();
    }
    
    async toggleFavorite(generationId, userId, isFavorite) {
        const response = await fetch(`${this.baseUrl}/history/favorite`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ generation_id: generationId, user_id: userId, is_favorite: isFavorite })
        });
        return response.json();
    }
}

// Usage
const client = new MotifClient();

// Generate single image
const result = await client.generateImage(
    'A beautiful birthday party setup',
    'party',
    'user123'
);

// Generate batch
const batchResult = await client.generateBatch([
    'A birthday party with balloons',
    'A wedding decoration with flowers'
], 'party');

// Get history
const history = await client.getHistory('user123', { limit: 10, favorites_only: true });
```

---

**Last Updated**: October 15, 2025  
**API Version**: 1.0.0
