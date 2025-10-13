#!/usr/bin/env python3
"""
Test Script: Process Sample Pin Images
Tests the complete flow: Upload → Storage → Vision Analysis
"""

import asyncio
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.storage_service import StorageService
from app.services.vision_processor import VisionProcessor
from app.core.logging import setup_logging

logger = setup_logging()


async def process_sample_image(image_path: Path, storage: StorageService, vision: VisionProcessor):
    """Process a single sample image through the pipeline"""
    
    print(f"\n{'='*60}")
    print(f"🎨 Processing: {image_path.name}")
    print(f"{'='*60}\n")
    
    try:
        # Read image
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        print(f"📦 Image size: {len(image_bytes) / 1024:.2f} KB")
        
        # Upload to Firebase Storage
        print("☁️  Uploading to Firebase Cloud Storage...")
        storage_url = await storage.upload_image(
            image_bytes=image_bytes,
            filename=image_path.name,
            user_id="sample_test",
            folder="samples",
            metadata={
                "source": "sample_pin_image",
                "test": True
            }
        )
        print(f"✅ Uploaded: {storage_url}\n")
        
        # Analyze with Vision AI
        print("🔍 Analyzing with GPT-4 Vision...")
        scene_data = await vision.analyze_party_image(storage_url)
        
        # Display results
        print(f"\n{'─'*60}")
        print("📊 ANALYSIS RESULTS:")
        print(f"{'─'*60}")
        print(f"🎭 Theme: {scene_data.theme}")
        print(f"🏷️  Style: {scene_data.style}")
        print(f"👥 Suggested Age: {scene_data.suggested_age_range}")
        print(f"🎯 Event Type: {scene_data.event_type}")
        
        print(f"\n🎨 Colors ({len(scene_data.colors)}):")
        for color in scene_data.colors[:5]:  # Show top 5
            print(f"  - {color.name}: {color.hex}")
        
        print(f"\n📦 Objects Detected ({len(scene_data.objects)}):")
        for obj in scene_data.objects[:10]:  # Show top 10
            print(f"  - {obj.name} ({obj.confidence:.0%}): {obj.description}")
        
        print(f"\n📐 Layout:")
        print(f"  - Background: {scene_data.layout.background}")
        print(f"  - Focal Points: {', '.join(scene_data.layout.focal_points)}")
        
        print(f"\n💡 Suggestions:")
        for suggestion in scene_data.suggestions[:5]:
            print(f"  - {suggestion}")
        
        # Save full JSON
        output_file = Path(__file__).parent / f"results_{image_path.stem}.json"
        with open(output_file, 'w') as f:
            json.dump(scene_data.to_dict(), f, indent=2)
        
        print(f"\n💾 Full results saved to: {output_file.name}")
        
        return {
            "filename": image_path.name,
            "storage_url": storage_url,
            "theme": scene_data.theme,
            "success": True
        }
        
    except Exception as e:
        print(f"❌ Error processing {image_path.name}: {str(e)}")
        logger.error(f"Failed to process {image_path.name}", error=str(e), exc_info=True)
        return {
            "filename": image_path.name,
            "success": False,
            "error": str(e)
        }


async def main():
    """Main test function"""
    
    print("\n" + "="*60)
    print("🎉 SAMPLE PIN IMAGE TESTING SUITE")
    print("="*60)
    
    # Initialize services
    storage = StorageService()
    vision = VisionProcessor()
    
    # Find sample images
    sample_dir = Path(__file__).parent.parent / "sample_images"
    image_files = sorted(sample_dir.glob("*.jpeg")) + sorted(sample_dir.glob("*.jpg"))
    
    if not image_files:
        print("❌ No sample images found in backend/sample_images/")
        return
    
    print(f"\n📁 Found {len(image_files)} sample images\n")
    
    # Process all images
    results = []
    for image_path in image_files:
        result = await process_sample_image(image_path, storage, vision)
        results.append(result)
        await asyncio.sleep(1)  # Rate limiting
    
    # Summary
    print(f"\n\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}\n")
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}\n")
    
    if successful:
        print("🎨 Detected Themes:")
        for result in successful:
            print(f"  - {result['filename']}: {result.get('theme', 'N/A')}")
    
    if failed:
        print("\n❌ Failures:")
        for result in failed:
            print(f"  - {result['filename']}: {result.get('error', 'Unknown error')}")
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
