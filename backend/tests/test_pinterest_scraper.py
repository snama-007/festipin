"""
Tests for Pinterest scraper service
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.pinterest_scraper import (
    PinterestScraperService,
    PinMetadata,
    ScrapingStrategy
)
from app.core.errors import PinterestScrapingError


class TestPinterestScraper:
    """Test suite for Pinterest scraper"""
    
    def test_extract_pin_id_standard_url(self):
        """Test extracting pin ID from standard Pinterest URL"""
        scraper = PinterestScraperService()
        
        url = "https://www.pinterest.com/pin/123456789/"
        pin_id = scraper._extract_pin_id(url)
        
        assert pin_id == "123456789"
    
    def test_extract_pin_id_short_url(self):
        """Test extracting pin ID from pin.it short URL"""
        scraper = PinterestScraperService()
        
        url = "https://pin.it/abc123def"
        pin_id = scraper._extract_pin_id(url)
        
        assert pin_id == "abc123def"
    
    def test_extract_pin_id_invalid_url(self):
        """Test error handling for invalid URL"""
        scraper = PinterestScraperService()
        
        with pytest.raises(ValueError, match="Invalid Pinterest URL"):
            scraper._extract_pin_id("https://example.com/not-pinterest")
    
    @pytest.mark.asyncio
    async def test_scrape_via_api_success(self):
        """Test successful API endpoint scraping"""
        scraper = PinterestScraperService()
        
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'resource_response': {
                'data': {
                    'id': '123456789',
                    'title': 'Test Party',
                    'description': 'A beautiful party setup',
                    'images': {
                        'orig': {'url': 'https://i.pinimg.com/originals/test.jpg'}
                    },
                    'board': {'name': 'Party Ideas'},
                    'pinner': {'username': 'testuser'},
                    'link': 'https://example.com',
                    'aggregated_pin_data': {
                        'aggregated_stats': {'saves': 100}
                    },
                    'comment_count': 5
                }
            }
        }
        
        async with scraper:
            with patch.object(scraper.client, 'get', return_value=mock_response):
                metadata = await scraper._scrape_via_api('123456789')
        
        assert metadata.pin_id == '123456789'
        assert metadata.title == 'Test Party'
        assert metadata.image_url == 'https://i.pinimg.com/originals/test.jpg'
        assert metadata.engagement['saves'] == 100
    
    @pytest.mark.asyncio
    async def test_scrape_via_html_success(self):
        """Test successful HTML scraping"""
        scraper = PinterestScraperService()
        
        html_content = '''
        <html>
            <head>
                <meta property="og:title" content="Party Setup" />
                <meta property="og:description" content="Beautiful party" />
                <meta property="og:image" content="https://i.pinimg.com/test.jpg" />
            </head>
        </html>
        '''
        
        mock_response = MagicMock()
        mock_response.text = html_content
        mock_response.raise_for_status = MagicMock()
        
        async with scraper:
            with patch.object(scraper.client, 'get', return_value=mock_response):
                metadata = await scraper._scrape_via_html(
                    '123456789',
                    'https://pinterest.com/pin/123456789/'
                )
        
        assert metadata.pin_id == '123456789'
        assert metadata.title == 'Party Setup'
        assert metadata.image_url == 'https://i.pinimg.com/test.jpg'
    
    @pytest.mark.asyncio
    async def test_extract_pin_with_fallback(self):
        """Test fallback to second strategy when first fails"""
        scraper = PinterestScraperService()
        scraper.scraping_strategies = [
            ScrapingStrategy.API_ENDPOINT,
            ScrapingStrategy.HTML_SCRAPE
        ]
        
        # Mock API failure
        async def mock_api_fail(*args, **kwargs):
            raise Exception("API failed")
        
        # Mock HTML success
        async def mock_html_success(*args, **kwargs):
            return PinMetadata(
                pin_id='123456789',
                title='Test',
                image_url='https://i.pinimg.com/test.jpg'
            )
        
        with patch.object(
            scraper,
            '_scrape_via_api',
            side_effect=mock_api_fail
        ):
            with patch.object(
                scraper,
                '_scrape_via_html',
                side_effect=mock_html_success
            ):
                async with scraper:
                    metadata = await scraper.extract_pin(
                        'https://pinterest.com/pin/123456789/'
                    )
        
        assert metadata.pin_id == '123456789'
        assert metadata.image_url == 'https://i.pinimg.com/test.jpg'
    
    @pytest.mark.asyncio
    async def test_extract_pin_all_strategies_fail(self):
        """Test error when all strategies fail"""
        scraper = PinterestScraperService()
        scraper.scraping_strategies = [
            ScrapingStrategy.API_ENDPOINT,
            ScrapingStrategy.HTML_SCRAPE
        ]
        
        async def mock_fail(*args, **kwargs):
            raise Exception("Failed")
        
        with patch.object(scraper, '_scrape_via_api', side_effect=mock_fail):
            with patch.object(scraper, '_scrape_via_html', side_effect=mock_fail):
                async with scraper:
                    with pytest.raises(PinterestScrapingError):
                        await scraper.extract_pin(
                            'https://pinterest.com/pin/123456789/'
                        )
    
    @pytest.mark.asyncio
    async def test_download_image(self):
        """Test image download"""
        scraper = PinterestScraperService()
        
        mock_response = MagicMock()
        mock_response.content = b'fake_image_data'
        mock_response.raise_for_status = MagicMock()
        
        async with scraper:
            with patch.object(scraper.client, 'get', return_value=mock_response):
                image_bytes = await scraper.download_image('https://i.pinimg.com/test.jpg')
        
        assert image_bytes == b'fake_image_data'
    
    def test_pin_metadata_to_dict(self):
        """Test PinMetadata serialization"""
        metadata = PinMetadata(
            pin_id='123',
            title='Test',
            image_url='https://example.com/img.jpg',
            engagement={'saves': 10}
        )
        
        result = metadata.to_dict()
        
        assert result['pin_id'] == '123'
        assert result['title'] == 'Test'
        assert result['engagement']['saves'] == 10


# Integration test (requires actual Pinterest URL - mark as slow)
@pytest.mark.slow
@pytest.mark.asyncio
async def test_real_pinterest_url():
    """
    Integration test with real Pinterest URL.
    Only run this with a valid Pinterest URL.
    """
    # NOTE: Replace with actual Pinterest URL for testing
    test_url = "https://www.pinterest.com/pin/12345/"  # Replace with real URL
    
    scraper = PinterestScraperService()
    
    async with scraper:
        try:
            metadata = await scraper.extract_pin(test_url)
            assert metadata.pin_id is not None
            assert metadata.image_url is not None
            print(f"Successfully scraped: {metadata.title}")
        except PinterestScrapingError as e:
            pytest.skip(f"Pinterest scraping failed (expected in CI): {e}")

