#!/usr/bin/env python3
"""
Direct test of motif service components
"""

import sys
import os
import traceback

# Add the backend directory to Python path
sys.path.insert(0, '/Users/snama/s.space/Parx-Agentic-Verse/festipin/backend')

def test_step_by_step():
    """Test each component step by step"""
    print("=== Testing Motif Service Components ===\n")
    
    # Step 1: Test config
    try:
        from app.core.config import settings
        print(f"✓ Config loaded")
        print(f"  GEMINI_API_KEY: {bool(settings.GEMINI_API_KEY)}")
        print(f"  RUNWARE_API_KEY: {bool(settings.RUNWARE_API_KEY)}")
    except Exception as e:
        print(f"✗ Config error: {e}")
        traceback.print_exc()
        return False
    
    # Step 2: Test MotifGeminiGenerator
    try:
        from app.services.motif.gemini_image_generator import MotifGeminiGenerator
        print(f"✓ MotifGeminiGenerator imported")
        
        # Try to create instance
        generator = MotifGeminiGenerator("test_key")
        print(f"✓ MotifGeminiGenerator created")
    except Exception as e:
        print(f"✗ MotifGeminiGenerator error: {e}")
        traceback.print_exc()
        return False
    
    # Step 3: Test GeminiProvider
    try:
        from app.services.motif.providers.gemini_provider import GeminiProvider
        print(f"✓ GeminiProvider imported")
        
        # Try to create instance
        provider = GeminiProvider()
        print(f"✓ GeminiProvider created")
    except Exception as e:
        print(f"✗ GeminiProvider error: {e}")
        traceback.print_exc()
        return False
    
    # Step 4: Test ServiceManager
    try:
        from app.services.motif.service_manager import ServiceManager
        print(f"✓ ServiceManager imported")
        
        # Try to create instance
        manager = ServiceManager()
        print(f"✓ ServiceManager created")
    except Exception as e:
        print(f"✗ ServiceManager error: {e}")
        traceback.print_exc()
        return False
    
    # Step 5: Test API routes
    try:
        from app.api.routes.motif.generation import router
        print(f"✓ Generation router imported")
    except Exception as e:
        print(f"✗ Generation router error: {e}")
        traceback.print_exc()
        return False
    
    print("\n=== All components imported successfully! ===")
    return True

if __name__ == "__main__":
    test_step_by_step()
