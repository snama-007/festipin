"""
Pinterest URL Scraper Service with Multiple Fallback Strategies

Strategy Priority:
1. Undocumented API endpoint (fastest)
2. HTML parsing with BeautifulSoup (most stable)
3. Playwright headless browser (most reliable, slowest)
"""

import json
import re
import time
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, asdict
from enum import Enum

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

from app.core.config import settings
from app.core.logging import logger
from app.core.errors import PinterestScrapingError


class ScrapingStrategy(str, Enum):
    """Scraping strategy types"""
    API_ENDPOINT = "api_endpoint"
    HTML_SCRAPE = "html_scrape"
    PLAYWRIGHT_RENDER = "playwright_render"


@dataclass
class PinMetadata:
    """Pinterest pin metadata"""
    pin_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    board_name: Optional[str] = None
    creator: Optional[str] = None
    original_source: Optional[str] = None
    engagement: Dict[str, int] = None
    
    def __post_init__(self):
        if self.engagement is None:
            self.engagement = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class PinterestScraperService:
    """
    Multi-strategy Pinterest scraping service with fallbacks.
    Priority: Speed → Reliability → Data completeness
    """
    
    def __init__(self):
        self.timeout = settings.PINTEREST_TIMEOUT_SECONDS
        self.max_retries = settings.PINTEREST_MAX_RETRIES
        self.client: Optional[httpx.AsyncClient] = None
        
        # Parse strategies from settings
        self.scraping_strategies = [
            ScrapingStrategy(s.strip()) 
            for s in settings.PINTEREST_SCRAPING_STRATEGY.split(',')
        ]
        
        logger.info(
            "Pinterest scraper initialized",
            strategies=self.scraping_strategies,
            timeout=self.timeout
        )
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.client = httpx.AsyncClient(
            headers=self._get_headers(),
            timeout=self.timeout,
            follow_redirects=True
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.client:
            await self.client.aclose()
    
    def _get_headers(self) -> Dict[str, str]:
        """Generate realistic browser headers to avoid detection"""
        return {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.pinterest.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'max-age=0'
        }
    
    def _extract_pin_id(self, url: str) -> str:
        """
        Extract pin ID from various Pinterest URL formats.
        
        Supported formats:
        - https://www.pinterest.com/pin/123456789/
        - https://pin.it/abc123
        - https://pinterest.com/pin/123456789/
        """
        patterns = [
            r'pinterest\.com/pin/(\d+)',
            r'pin\.it/(\w+)',
            r'/pin/(\d+)/',
        ]
        
        for pattern in patterns:
            if match := re.search(pattern, url):
                pin_id = match.group(1)
                logger.debug("Extracted pin ID", pin_id=pin_id, pattern=pattern)
                return pin_id
        
        raise ValueError(f"Invalid Pinterest URL format: {url}")
    
    async def extract_pin(
        self, 
        pinterest_url: str,
        force_strategy: Optional[ScrapingStrategy] = None
    ) -> PinMetadata:
        """
        Extract pin metadata using cascading fallback strategies.
        
        Args:
            pinterest_url: Full Pinterest URL
            force_strategy: Force specific strategy (for testing)
            
        Returns:
            PinMetadata object with image URL and metadata
            
        Raises:
            PinterestScrapingError: If all strategies fail
        """
        start_time = time.time()
        pin_id = self._extract_pin_id(pinterest_url)
        
        strategies = [force_strategy] if force_strategy else self.scraping_strategies
        
        logger.info(
            "Starting Pinterest extraction",
            url=pinterest_url,
            pin_id=pin_id,
            strategies=strategies
        )
        
        last_error = None
        
        for strategy in strategies:
            try:
                logger.debug(f"Trying strategy: {strategy}")
                
                if strategy == ScrapingStrategy.API_ENDPOINT:
                    metadata = await self._scrape_via_api(pin_id)
                elif strategy == ScrapingStrategy.HTML_SCRAPE:
                    metadata = await self._scrape_via_html(pin_id, pinterest_url)
                elif strategy == ScrapingStrategy.PLAYWRIGHT_RENDER:
                    metadata = await self._scrape_via_playwright(pinterest_url)
                else:
                    logger.warning(f"Unknown strategy: {strategy}")
                    continue
                
                elapsed = time.time() - start_time
                logger.info(
                    "Pinterest extraction successful",
                    strategy=strategy,
                    pin_id=pin_id,
                    elapsed_seconds=round(elapsed, 2)
                )
                
                return metadata
                
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Strategy {strategy} failed",
                    error=str(e),
                    pin_id=pin_id
                )
                continue
        
        # All strategies failed
        elapsed = time.time() - start_time
        logger.error(
            "All Pinterest scraping strategies failed",
            pin_id=pin_id,
            url=pinterest_url,
            elapsed_seconds=round(elapsed, 2),
            last_error=str(last_error)
        )
        
        raise PinterestScrapingError(
            f"Failed to scrape Pinterest URL after trying all strategies. Last error: {str(last_error)}",
            context={"pin_id": pin_id, "url": pinterest_url}
        )
    
    async def _scrape_via_api(self, pin_id: str) -> PinMetadata:
        """
        Strategy 1: Use undocumented Pinterest API endpoint.
        Fast but may break if Pinterest changes structure.
        """
        api_url = "https://www.pinterest.com/resource/PinResource/get/"
        
        params = {
            'source_url': f'/pin/{pin_id}/',
            'data': json.dumps({
                'options': {
                    'field_set_key': 'detailed',
                    'id': pin_id
                },
                'context': {}
            })
        }
        
        if not self.client:
            raise RuntimeError("HTTP client not initialized. Use async context manager.")
        
        response = await self.client.get(api_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if 'resource_response' not in data or 'data' not in data['resource_response']:
            raise PinterestScrapingError("Unexpected API response structure")
        
        pin_data = data['resource_response']['data']
        
        # Extract image URL (prefer original quality)
        image_url = None
        if 'images' in pin_data:
            if 'orig' in pin_data['images']:
                image_url = pin_data['images']['orig']['url']
            elif '736x' in pin_data['images']:
                image_url = pin_data['images']['736x']['url']
        
        return PinMetadata(
            pin_id=pin_id,
            title=pin_data.get('title'),
            description=pin_data.get('description'),
            image_url=image_url,
            board_name=pin_data.get('board', {}).get('name'),
            creator=pin_data.get('pinner', {}).get('username'),
            original_source=pin_data.get('link'),
            engagement={
                'saves': pin_data.get('aggregated_pin_data', {}).get('aggregated_stats', {}).get('saves', 0),
                'comments': pin_data.get('comment_count', 0)
            }
        )
    
    async def _scrape_via_html(self, pin_id: str, url: str) -> PinMetadata:
        """
        Strategy 2: Parse HTML with BeautifulSoup.
        More stable, relies on Open Graph and JSON-LD metadata.
        """
        if not self.client:
            raise RuntimeError("HTTP client not initialized. Use async context manager.")
        
        response = await self.client.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract Open Graph metadata
        og_image = soup.find('meta', property='og:image')
        og_title = soup.find('meta', property='og:title')
        og_description = soup.find('meta', property='og:description')
        
        # Extract JSON-LD structured data
        json_ld_script = soup.find('script', type='application/ld+json')
        structured_data = {}
        if json_ld_script:
            try:
                structured_data = json.loads(json_ld_script.string)
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON-LD data")
        
        # Extract image URL
        image_url = None
        if og_image:
            image_url = og_image.get('content')
        elif structured_data.get('image'):
            image_url = structured_data['image']
        
        if not image_url:
            raise PinterestScrapingError("Could not extract image URL from HTML")
        
        return PinMetadata(
            pin_id=pin_id,
            title=og_title['content'] if og_title else structured_data.get('name'),
            description=og_description['content'] if og_description else structured_data.get('description'),
            image_url=image_url,
            board_name=None,  # Not available in HTML
            creator=structured_data.get('author', {}).get('name') if isinstance(structured_data.get('author'), dict) else None,
            original_source=structured_data.get('url'),
            engagement={}
        )
    
    async def _scrape_via_playwright(self, url: str) -> PinMetadata:
        """
        Strategy 3: Use headless browser for dynamic content.
        Slowest but most reliable, handles client-side rendering.
        """
        pin_id = self._extract_pin_id(url)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            try:
                page = await browser.new_page()
                
                # Set realistic viewport and user agent
                await page.set_viewport_size({"width": 1920, "height": 1080})
                
                # Navigate to page
                await page.goto(url, wait_until='networkidle', timeout=self.timeout * 1000)
                
                # Wait for image to load
                try:
                    await page.wait_for_selector('img[src*="pinimg.com"]', timeout=10000)
                except PlaywrightTimeout:
                    logger.warning("Image selector timeout, continuing anyway")
                
                # Extract data via JavaScript
                data = await page.evaluate('''() => {
                    const meta = {
                        title: document.querySelector('meta[property="og:title"]')?.content || 
                               document.querySelector('h1')?.textContent,
                        description: document.querySelector('meta[property="og:description"]')?.content,
                        image: document.querySelector('meta[property="og:image"]')?.content ||
                               document.querySelector('img[src*="pinimg.com"]')?.src,
                    };
                    return meta;
                }''')
                
                if not data.get('image'):
                    raise PinterestScrapingError("Could not extract image URL via Playwright")
                
                return PinMetadata(
                    pin_id=pin_id,
                    title=data['title'],
                    description=data['description'],
                    image_url=data['image'],
                    board_name=None,
                    creator=None,
                    original_source=url,
                    engagement={}
                )
                
            finally:
                await browser.close()
    
    async def download_image(self, image_url: str) -> bytes:
        """
        Download image from Pinterest CDN.
        
        Args:
            image_url: Pinterest image URL
            
        Returns:
            Image bytes
        """
        if not self.client:
            raise RuntimeError("HTTP client not initialized. Use async context manager.")
        
        logger.info("Downloading Pinterest image", url=image_url)
        
        response = await self.client.get(image_url)
        response.raise_for_status()
        
        image_bytes = response.content
        
        logger.info(
            "Image downloaded",
            size_kb=round(len(image_bytes) / 1024, 2)
        )
        
        return image_bytes


# Singleton instance
_scraper_instance: Optional[PinterestScraperService] = None


def get_pinterest_scraper() -> PinterestScraperService:
    """Get or create Pinterest scraper singleton"""
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = PinterestScraperService()
    return _scraper_instance

