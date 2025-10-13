#!/bin/bash

# Test Sample Image Upload via API
# Tests the complete flow: Manual Upload → Storage → Vision Analysis

echo "🎨 Testing Sample Image Upload"
echo "================================"

# Check if sample image exists
SAMPLE_IMAGE="./backend/sample_images/pin1.jpeg"

if [ ! -f "$SAMPLE_IMAGE" ]; then
    echo "❌ Sample image not found: $SAMPLE_IMAGE"
    exit 1
fi

echo "📦 Image: $SAMPLE_IMAGE"
echo "📊 Size: $(du -h "$SAMPLE_IMAGE" | cut -f1)"
echo ""

# Upload and analyze
echo "☁️  Uploading to API..."
response=$(curl -s -X POST http://localhost:9000/api/v1/input/process \
  -F "input_type=manual_upload" \
  -F "image=@$SAMPLE_IMAGE" \
  -F "user_id=test_sample")

echo "$response" | jq '.'

# Check if successful
success=$(echo "$response" | jq -r '.success')

if [ "$success" = "true" ]; then
    echo ""
    echo "✅ Upload and Analysis Successful!"
    echo ""
    echo "🎭 Theme: $(echo "$response" | jq -r '.message' | sed 's/Successfully analyzed: //')"
else
    echo ""
    echo "❌ Upload failed"
    echo "Error: $(echo "$response" | jq -r '.message')"
fi
