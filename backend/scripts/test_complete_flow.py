#!/usr/bin/env python3
"""
Test Complete Party Planning Flow
Upload Image → Vision Analysis → Plan Generation
"""

import asyncio
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services import get_storage_service
from app.services.vision_processor import VisionProcessor
from app.services.plan_generator import PlanGeneratorService


async def test_complete_flow():
    """Test the complete party planning pipeline"""
    
    print("🎉 Testing Complete Party Planning Flow")
    print("=" * 60)
    
    # Sample image
    sample_path = Path(__file__).parent.parent / "sample_images" / "pin1.jpeg"
    
    if not sample_path.exists():
        print(f"❌ Sample image not found: {sample_path}")
        return
    
    print(f"\n📸 Using sample: {sample_path.name}")
    
    # Step 1: Upload to storage
    print("\n📤 Step 1: Uploading image...")
    with open(sample_path, 'rb') as f:
        image_bytes = f.read()
    
    storage = get_storage_service()
    image_url = await storage.upload_image(
        image_bytes=image_bytes,
        filename=sample_path.name,
        user_id="test_flow",
        folder="test_flow"
    )
    print(f"   ✅ Uploaded: {image_url}")
    
    # Step 2: Vision Analysis
    print("\n🔍 Step 2: Analyzing with GPT-4 Vision...")
    vision = VisionProcessor()
    
    # For standalone testing, convert image to base64 directly
    import base64
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    data_url = f"data:image/jpeg;base64,{base64_image}"
    
    scene_data = await vision.analyze_party_image(data_url)
    
    print(f"   ✅ Theme: {scene_data.theme}")
    print(f"   ✅ Confidence: {scene_data.confidence}")
    print(f"   ✅ Colors: {len(scene_data.color_palette)} colors")
    print(f"   ✅ Objects: {len(scene_data.objects)} detected")
    print(f"   ✅ Layout: {scene_data.layout_type}")
    
    # Step 3: Generate Party Plan
    print("\n📋 Step 3: Generating comprehensive party plan...")
    plan_generator = PlanGeneratorService()
    
    user_context = {
        "honoree_name": "Sophia",
        "event_date": "2025-12-15",
        "guest_count": 25,
        "budget_range": [600, 1200],
        "location_type": "backyard"
    }
    
    party_plan = await plan_generator.generate_plan(
        scene_data=scene_data,
        user_context=user_context
    )
    
    print(f"   ✅ Plan generated!")
    print(f"\n{'─'*60}")
    print("📊 PARTY PLAN SUMMARY:")
    print(f"{'─'*60}")
    print(f"🎭 Event: {party_plan.event.theme}")
    print(f"👤 Honoree: {party_plan.event.honoree_name}, age {party_plan.event.honoree_age}")
    print(f"📅 Date: {party_plan.event.date} at {party_plan.event.time}")
    print(f"📍 Location: {party_plan.event.location}")
    print(f"👥 Guests: {party_plan.event.guest_count}")
    
    print(f"\n💰 Budget: ${party_plan.budget_total_min} - ${party_plan.budget_total_max}")
    
    print(f"\n✅ Checklist Categories: {len(party_plan.checklist)}")
    for category in party_plan.checklist:
        print(f"   - {category.name}: {len(category.items)} items")
    
    print(f"\n📅 Timeline: {len(party_plan.timeline)} milestones")
    if party_plan.timeline:
        print(f"   First task: {party_plan.timeline[0].task} ({party_plan.timeline[0].date})")
    
    print(f"\n🏪 Vendors: {len(party_plan.vendors)} recommended")
    for vendor in party_plan.vendors[:3]:
        print(f"   - {vendor.type}: ${vendor.budget_range[0]}-${vendor.budget_range[1]}")
    
    # Save plan to file
    output_file = Path(__file__).parent / "generated_plan.json"
    with open(output_file, 'w') as f:
        json.dump(party_plan.model_dump(), f, indent=2, default=str)
    
    print(f"\n💾 Full plan saved to: {output_file.name}")
    
    # Step 4: Test Plan Refinement
    print(f"\n🔄 Step 4: Testing plan refinement...")
    feedback = "Add a photo booth and change the guest count to 30"
    
    refined_plan = await plan_generator.refine_plan(
        existing_plan=party_plan,
        user_feedback=feedback
    )
    
    print(f"   ✅ Plan refined! Version: {refined_plan.version}")
    print(f"   New guest count: {refined_plan.event.guest_count}")
    
    print(f"\n{'='*60}")
    print("✅ COMPLETE FLOW TEST PASSED!")
    print("=" * 60)
    print("\n🎨 You now have a fully generated party plan ready for:")
    print("   - Interactive canvas editing")
    print("   - Checklist tracking")
    print("   - Budget management")
    print("   - Timeline view")
    print("   - Vendor matching")
    print("   - PDF/Notion export")


if __name__ == "__main__":
    asyncio.run(test_complete_flow())
