#!/usr/bin/env python3
"""
Installation Test Script
Verifies all critical dependencies are installed correctly
"""

import sys
from typing import Dict, List, Tuple


def test_import(module_name: str, package_name: str = None) -> Tuple[bool, str]:
    """Test if a module can be imported"""
    try:
        __import__(module_name)
        return True, f"✅ {package_name or module_name}"
    except ImportError as e:
        return False, f"❌ {package_name or module_name}: {str(e)}"


def main():
    print("=" * 60)
    print("🔍 FestiPin Backend - Installation Test")
    print("=" * 60)
    print()

    # Test Core Dependencies
    print("📦 Core Framework:")
    core_tests = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("pydantic_settings", "Pydantic Settings"),
    ]

    core_results = [test_import(module, pkg) for module, pkg in core_tests]
    for success, msg in core_results:
        print(f"  {msg}")
    print()

    # Test AI/ML Dependencies
    print("🤖 AI/ML:")
    ai_tests = [
        ("openai", "OpenAI"),
        ("google.generativeai", "Google Generative AI"),
        ("langchain", "LangChain"),
        ("langchain_openai", "LangChain OpenAI"),
        ("langgraph", "LangGraph"),
    ]

    ai_results = [test_import(module, pkg) for module, pkg in ai_tests]
    for success, msg in ai_results:
        print(f"  {msg}")
    print()

    # Test Image Processing
    print("🎨 Image Processing:")
    image_tests = [
        ("PIL", "Pillow"),
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("magic", "python-magic"),
    ]

    image_results = [test_import(module, pkg) for module, pkg in image_tests]
    for success, msg in image_results:
        print(f"  {msg}")
    print()

    # Test Database & Storage
    print("💾 Database & Storage:")
    db_tests = [
        ("firebase_admin", "Firebase Admin"),
        ("google.cloud.firestore", "Firestore"),
        ("google.cloud.storage", "Cloud Storage"),
    ]

    db_results = [test_import(module, pkg) for module, pkg in db_tests]
    for success, msg in db_results:
        print(f"  {msg}")
    print()

    # Test Caching
    print("⚡ Caching:")
    cache_tests = [
        ("redis", "Redis"),
        ("redis.asyncio", "Redis Asyncio"),
    ]

    cache_results = [test_import(module, pkg) for module, pkg in cache_tests]
    for success, msg in cache_results:
        print(f"  {msg}")
    print()

    # Test Scraping
    print("🕷️ Web Scraping:")
    scraping_tests = [
        ("playwright", "Playwright"),
        ("httpx", "HTTPX"),
        ("bs4", "BeautifulSoup4"),
        ("lxml", "lxml"),
    ]

    scraping_results = [test_import(module, pkg) for module, pkg in scraping_tests]
    for success, msg in scraping_results:
        print(f"  {msg}")
    print()

    # Test Utilities
    print("🛠️ Utilities:")
    util_tests = [
        ("dotenv", "python-dotenv"),
        ("jose", "python-jose"),
        ("passlib", "passlib"),
        ("celery", "Celery"),
    ]

    util_results = [test_import(module, pkg) for module, pkg in util_tests]
    for success, msg in util_results:
        print(f"  {msg}")
    print()

    # Test 3D Processing (Motif module)
    print("🎨 3D Processing (Motif):")
    threed_tests = [
        ("trimesh", "Trimesh"),
    ]

    threed_results = [test_import(module, pkg) for module, pkg in threed_tests]
    for success, msg in threed_results:
        print(f"  {msg}")
    print()

    # Optional: Test PyTorch (heavy dependency)
    print("🔥 PyTorch (Optional):")
    torch_success, torch_msg = test_import("torch", "PyTorch")
    print(f"  {torch_msg}")

    if torch_success:
        import torch
        cuda_available = torch.cuda.is_available()
        cuda_msg = "✅ CUDA Available" if cuda_available else "ℹ️  CPU Only"
        print(f"  {cuda_msg}")
    print()

    # Summary
    all_results = (
        core_results + ai_results + image_results +
        db_results + cache_results + scraping_results +
        util_results + threed_results
    )

    total = len(all_results)
    passed = sum(1 for success, _ in all_results if success)

    print("=" * 60)
    print(f"📊 Results: {passed}/{total} packages installed successfully")
    print("=" * 60)

    if passed == total:
        print("✅ All dependencies installed correctly!")
        print("🚀 Ready to run: uvicorn app.main:app --reload")
        return 0
    else:
        failed = total - passed
        print(f"⚠️  {failed} package(s) failed to import")
        print("📖 See INSTALLATION_GUIDE.md for troubleshooting")
        return 1


if __name__ == "__main__":
    sys.exit(main())
