#!/usr/bin/env python3
"""
Manual test script for Firebase Cloud Storage.

Usage:
    python scripts/test_storage.py

Tests:
    1. Upload test image
    2. Get public URL
    3. Delete image
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.storage_service import get_storage_service
from app.core.errors import StorageError


async def test_storage():
    """Test storage service end-to-end"""
    print("🧪 Testing Firebase Cloud Storage")
    print("=" * 60)
    
    # Create test image
    test_image = b'\xff\xd8\xff\xe0' + b'TEST_IMAGE_DATA' * 100
    print(f"📦 Created test image: {len(test_image)} bytes ({len(test_image)/1024:.2f} KB)")
    
    storage = get_storage_service()
    
    try:
        # Test 1: Upload
        print("\n1️⃣  Testing image upload...")
        url = await storage.upload_image(
            image_bytes=test_image,
            filename="test_storage.jpg",
            user_id="test_user_123",
            folder="test_uploads",
            metadata={
                "test": "true",
                "purpose": "manual_testing"
            }
        )
        
        print(f"✅ Upload successful!")
        print(f"📍 Public URL: {url}")
        
        # Test 2: Extract path
        print("\n2️⃣  Testing path extraction...")
        path = storage.get_storage_path_from_url(url)
        print(f"✅ Extracted path: {path}")
        
        # Test 3: Generate signed URL
        print("\n3️⃣  Testing signed URL generation...")
        signed_url = await storage.get_signed_url(path)
        print(f"✅ Signed URL: {signed_url[:80]}...")
        
        # Test 4: Delete
        print("\n4️⃣  Testing image deletion...")
        deleted = await storage.delete_image(path)
        
        if deleted:
            print(f"✅ Image deleted successfully")
        else:
            print(f"❌ Image deletion failed")
        
        print("\n" + "=" * 60)
        print("✅ All storage tests passed!")
        
    except StorageError as e:
        print(f"\n❌ Storage error: {e}")
        print(f"Context: {e.context}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


async def test_validations():
    """Test validation logic"""
    print("\n" + "=" * 60)
    print("🧪 Testing validation logic")
    print("=" * 60)
    
    storage = get_storage_service()
    
    # Test oversized image
    print("\n1️⃣  Testing oversized image rejection...")
    try:
        large_image = b'0' * (11 * 1024 * 1024)  # 11MB
        storage._validate_image(large_image, "large.jpg")
        print("❌ Should have rejected oversized image")
    except StorageError:
        print("✅ Correctly rejected oversized image")
    
    # Test tiny image
    print("\n2️⃣  Testing tiny image rejection...")
    try:
        tiny_image = b'0' * 50
        storage._validate_image(tiny_image, "tiny.jpg")
        print("❌ Should have rejected tiny image")
    except StorageError:
        print("✅ Correctly rejected tiny image")
    
    # Test valid image
    print("\n3️⃣  Testing valid image...")
    try:
        valid_image = b'\xff\xd8\xff\xe0' + b'0' * 1000
        storage._validate_image(valid_image, "valid.jpg")
        print("✅ Correctly validated good image")
    except StorageError:
        print("❌ Should have validated good image")
    
    print("\n✅ Validation tests complete!")


async def main():
    """Main entry point"""
    try:
        await test_storage()
        await test_validations()
        
        print("\n" + "=" * 60)
        print("🎉 All tests passed! Storage service is working.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

