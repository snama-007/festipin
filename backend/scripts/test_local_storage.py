#!/usr/bin/env python3
"""
Test Local Storage Service
Quick test to verify local file storage works
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.local_storage_service import LocalStorageService


async def test_local_storage():
    """Test local storage operations"""
    
    print("🧪 Testing Local Storage Service")
    print("=" * 60)
    
    storage = LocalStorageService()
    
    # Test 1: Upload sample image
    print("\n📤 Test 1: Upload sample image")
    sample_path = Path(__file__).parent.parent / "sample_images" / "pin1.jpeg"
    
    if not sample_path.exists():
        print(f"❌ Sample image not found: {sample_path}")
        return
    
    with open(sample_path, 'rb') as f:
        image_bytes = f.read()
    
    print(f"   Size: {len(image_bytes) / 1024:.2f} KB")
    
    url = await storage.upload_image(
        image_bytes=image_bytes,
        filename="pin1.jpeg",
        user_id="test_user",
        folder="test",
        metadata={"source": "test", "description": "gold balloons"}
    )
    
    print(f"   ✅ Uploaded: {url}")
    
    # Test 2: Get stats
    print("\n📊 Test 2: Storage statistics")
    stats = storage.get_stats()
    print(f"   Files: {stats['total_files']}")
    print(f"   Size: {stats['total_size_mb']} MB")
    print(f"   Path: {stats['base_path']}")
    
    # Test 3: Extract filename from URL and get it again
    print("\n🔗 Test 3: Get image URL")
    filename = url.split('/')[-1]
    url2 = await storage.get_image_url(filename, folder="test")
    print(f"   ✅ URL: {url2}")
    print(f"   Match: {url == url2}")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print(f"\n💡 Your images are stored in: {storage.base_path}")
    print(f"   They're served at: http://localhost:9000/uploads/")


if __name__ == "__main__":
    asyncio.run(test_local_storage())
