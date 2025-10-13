"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
from typing import Generator


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_pinterest_urls():
    """Sample Pinterest URLs for testing"""
    return {
        'standard': 'https://www.pinterest.com/pin/123456789/',
        'short': 'https://pin.it/abc123',
        'with_slash': 'https://pinterest.com/pin/987654321/',
        'invalid': 'https://example.com/not-pinterest'
    }


@pytest.fixture
def sample_pin_metadata():
    """Sample pin metadata for testing"""
    return {
        'pin_id': '123456789',
        'title': 'Beautiful Party Setup',
        'description': 'Gold and white balloon party',
        'image_url': 'https://i.pinimg.com/originals/test.jpg',
        'board_name': 'Party Ideas',
        'creator': 'partyplanner',
        'engagement': {
            'saves': 150,
            'comments': 10
        }
    }

