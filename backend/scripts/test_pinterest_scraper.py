#!/usr/bin/env python3
"""
Manual test script for Pinterest scraper.

Usage:
    python scripts/test_pinterest_scraper.py <pinterest_url>

Example:
    python scripts/test_pinterest_scraper.py "https://www.pinterest.com/pin/123456789/"
"""

import asyncio
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.pinterest_scraper import PinterestScraperService, ScrapingStrategy
from app.core.errors import PinterestScrapingError


async def test_scraper(url: str, strategy: str = None):
    """Test Pinterest scraper with a URL"""
    print(f"🔍 Testing Pinterest scraper")
    print(f"URL: {url}")
    print(f"Strategy: {strategy or 'Auto (all strategies)'}")
    print("-" * 60)
    
    scraper = PinterestScraperService()
    
    async with scraper:
        try:
            # Force specific strategy if provided
            force_strategy = ScrapingStrategy(strategy) if strategy else None
            
            # Extract pin metadata
            print("\n📥 Extracting pin metadata...")
            metadata = await scraper.extract_pin(url, force_strategy=force_strategy)
            
            print("\n✅ Success! Pin metadata:")
            print(json.dumps(metadata.to_dict(), indent=2))
            
            # Download image
            print(f"\n📸 Downloading image from: {metadata.image_url}")
            image_bytes = await scraper.download_image(metadata.image_url)
            
            print(f"✅ Image downloaded: {len(image_bytes):,} bytes ({len(image_bytes)/1024:.2f} KB)")
            
            # Optionally save image
            save_path = Path("temp_pinterest_image.jpg")
            save_path.write_bytes(image_bytes)
            print(f"💾 Image saved to: {save_path.absolute()}")
            
        except PinterestScrapingError as e:
            print(f"\n❌ Pinterest scraping failed: {e}")
            print(f"Context: {e.context}")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            sys.exit(1)


def test_url_extraction():
    """Test URL pattern extraction"""
    print("\n🧪 Testing URL pattern extraction...")
    
    test_urls = [
        "https://www.pinterest.com/pin/123456789/",
        "https://pin.it/abc123",
        "https://pinterest.com/pin/987654321/",
        "https://www.pinterest.com/pin/555666777/"
    ]
    
    scraper = PinterestScraperService()
    
    for url in test_urls:
        try:
            pin_id = scraper._extract_pin_id(url)
            print(f"✅ {url} → pin_id: {pin_id}")
        except ValueError as e:
            print(f"❌ {url} → Error: {e}")


async def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("📝 Usage:")
        print("  python scripts/test_pinterest_scraper.py <pinterest_url> [strategy]")
        print("\nStrategies:")
        print("  - api_endpoint (fastest)")
        print("  - html_scrape (most stable)")
        print("  - playwright_render (most reliable)")
        print("\nExamples:")
        print("  python scripts/test_pinterest_scraper.py 'https://www.pinterest.com/pin/123/'")
        print("  python scripts/test_pinterest_scraper.py 'https://pin.it/abc123' html_scrape")
        print("\n🧪 Running URL extraction tests...")
        test_url_extraction()
        sys.exit(0)
    
    url = sys.argv[1]
    strategy = sys.argv[2] if len(sys.argv) > 2 else None
    
    await test_scraper(url, strategy)


if __name__ == "__main__":
    asyncio.run(main())

