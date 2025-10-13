#!/usr/bin/env python3
"""
Quick Test: Upload one sample image and analyze it
Usage: python quick_test_sample.py [pin1|pin2|pin3]
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.storage_service import StorageService
from app.services.vision_processor import VisionProcessor


async def quick_test(image_name="pin1.jpeg"):
    """Quick test with a single sample image"""
    
    sample_path = Path(__file__).parent.parent / "sample_images" / image_name
    
    if not sample_path.exists():
        print(f"❌ Image not found: {sample_path}")
        return
    
    print(f"🎨 Testing with: {image_name}\n")
    
    # Read image
    with open(sample_path, 'rb') as f:
        image_bytes = f.read()
    
    print(f"📦 Size: {len(image_bytes) / 1024:.2f} KB")
    
    # Upload to storage
    print("☁️  Uploading...")
    storage = StorageService()
    url = await storage.upload_image(
        image_bytes=image_bytes,
        filename=image_name,
        user_id="quick_test",
        folder="test"
    )
    print(f"✅ Uploaded: {url}\n")
    
    # Analyze
    print("🔍 Analyzing...")
    vision = VisionProcessor()
    scene = await vision.analyze_party_image(url)
    
    print(f"\n🎭 Theme: {scene.theme}")
    print(f"🎨 Colors: {', '.join([c.name for c in scene.colors[:3]])}")
    print(f"📦 Objects: {len(scene.objects)} detected")
    print(f"💡 First suggestion: {scene.suggestions[0] if scene.suggestions else 'None'}")
    
    print(f"\n✅ Test complete!")


if __name__ == "__main__":
    image_name = sys.argv[1] if len(sys.argv) > 1 else "pin1.jpeg"
    if not image_name.endswith('.jpeg'):
        image_name = f"{image_name}.jpeg"
    
    asyncio.run(quick_test(image_name))
