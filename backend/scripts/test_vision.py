#!/usr/bin/env python3
"""
Manual test script for Vision AI processor.

Usage:
    python scripts/test_vision.py <image_url>

Example:
    python scripts/test_vision.py "https://storage.googleapis.com/bucket/party.jpg"
"""

import asyncio
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.vision_processor import get_vision_processor
from app.core.errors import VisionProcessingError


async def test_vision(image_url: str):
    """Test vision processor with an image URL"""
    print("🎨 Testing GPT-4 Vision AI Processor")
    print("=" * 60)
    print(f"Image URL: {image_url}")
    print("-" * 60)
    
    processor = get_vision_processor()
    
    try:
        # Analyze image
        print("\n🔍 Analyzing party image...")
        scene_data = await processor.analyze_party_image(image_url)
        
        print("\n✅ Analysis successful!")
        print("=" * 60)
        
        # Display results
        print(f"\n🎉 Theme: {scene_data.theme}")
        print(f"📊 Confidence: {scene_data.confidence:.2f}")
        print(f"🎨 Layout Type: {scene_data.layout_type}")
        
        if scene_data.occasion_type:
            print(f"🎈 Occasion: {scene_data.occasion_type}")
        
        if scene_data.age_range:
            print(f"👶 Age Range: {scene_data.age_range[0]}-{scene_data.age_range[1]} years")
        
        if scene_data.recommended_venue:
            print(f"🏠 Recommended Venue: {scene_data.recommended_venue}")
        
        # Color palette
        print(f"\n🌈 Color Palette:")
        for i, color in enumerate(scene_data.color_palette, 1):
            print(f"  {i}. {color}")
        
        # Style tags
        if scene_data.style_tags:
            print(f"\n✨ Style Tags: {', '.join(scene_data.style_tags)}")
        
        # Objects
        print(f"\n📦 Objects Detected ({len(scene_data.objects)}):")
        for i, obj in enumerate(scene_data.objects, 1):
            print(f"\n  {i}. {obj.type}")
            print(f"     Color: {obj.color}")
            print(f"     Position: x={obj.position['x']:.2f}, y={obj.position['y']:.2f}")
            print(f"     Quantity: {obj.count}")
            print(f"     Confidence: {obj.confidence:.2f}")
            
            if obj.estimated_cost:
                print(f"     Estimated Cost: ${obj.estimated_cost[0]}-${obj.estimated_cost[1]}")
            
            if obj.materials:
                print(f"     Materials: {', '.join(obj.materials)}")
        
        # Budget estimate
        if scene_data.budget_estimate:
            print(f"\n💰 Budget Estimate:")
            print(f"   Min: ${scene_data.budget_estimate['min']}")
            print(f"   Max: ${scene_data.budget_estimate['max']}")
        
        # Test shopping list generation
        print("\n" + "=" * 60)
        print("🛒 Generating Shopping List...")
        shopping_list = await processor.extract_shopping_list(scene_data)
        
        print(f"\n📋 Shopping List by Category:")
        for category, items in shopping_list["categories"].items():
            print(f"\n  {category.replace('_', ' ').title()}:")
            for item in items:
                cost_str = ""
                if item.get("estimated_cost"):
                    cost_str = f" (${item['estimated_cost'][0]}-${item['estimated_cost'][1]})"
                print(f"    • {item['name']} x{item['quantity']} - {item['color']}{cost_str}")
        
        total = shopping_list["total_estimated_cost"]
        print(f"\n💵 Total Estimated Cost: ${total['min']}-${total['max']}")
        
        # Save results
        output_file = Path("vision_analysis_result.json")
        output_data = {
            "scene_data": scene_data.to_dict(),
            "shopping_list": shopping_list
        }
        output_file.write_text(json.dumps(output_data, indent=2))
        print(f"\n💾 Results saved to: {output_file.absolute()}")
        
        print("\n" + "=" * 60)
        print("✅ Vision AI test complete!")
        
    except VisionProcessingError as e:
        print(f"\n❌ Vision processing failed: {e}")
        print(f"Context: {e.context}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


async def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("📝 Usage:")
        print("  python scripts/test_vision.py <image_url>")
        print("\nExample:")
        print("  python scripts/test_vision.py 'https://storage.googleapis.com/bucket/party.jpg'")
        print("\n💡 Tip: Use a public image URL (Firebase Storage, Pinterest, etc.)")
        sys.exit(0)
    
    image_url = sys.argv[1]
    await test_vision(image_url)


if __name__ == "__main__":
    asyncio.run(main())

