"""
Tests for Firebase Storage service
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import timedelta

from app.services.storage_service import StorageService, get_storage_service
from app.core.errors import StorageError


class TestStorageService:
    """Test suite for Storage service"""
    
    def test_generate_unique_filename_with_all_params(self):
        """Test filename generation with all parameters"""
        service = StorageService()
        
        filename = service._generate_unique_filename(
            original_filename="party.jpg",
            user_id="user_123",
            prefix="pinterest"
        )
        
        assert filename.startswith("pinterest_")
        assert "user_123" in filename
        assert filename.endswith(".jpg")
        assert len(filename) > 30  # Should be reasonably long
    
    def test_generate_unique_filename_without_extension(self):
        """Test filename generation defaults to .jpg if no extension"""
        service = StorageService()
        
        filename = service._generate_unique_filename(
            original_filename="party",
            prefix="upload"
        )
        
        assert filename.endswith(".jpg")
    
    def test_generate_unique_filename_uniqueness(self):
        """Test that generated filenames are unique"""
        service = StorageService()
        
        filenames = set()
        for _ in range(100):
            filename = service._generate_unique_filename()
            filenames.add(filename)
        
        # All should be unique
        assert len(filenames) == 100
    
    def test_get_content_type_from_filename(self):
        """Test content type detection from filename"""
        service = StorageService()
        
        # Mock image bytes (won't be used if filename works)
        mock_bytes = b'\xff\xd8\xff\xe0'  # JPEG magic bytes
        
        assert service._get_content_type("test.jpg", mock_bytes) == "image/jpeg"
        assert service._get_content_type("test.png", mock_bytes) == "image/png"
        assert service._get_content_type("test.webp", mock_bytes) == "image/webp"
    
    def test_get_content_type_from_magic_bytes(self):
        """Test content type detection from magic bytes"""
        service = StorageService()
        
        # JPEG
        jpeg_bytes = b'\xff\xd8\xff\xe0' + b'0' * 100
        assert service._get_content_type("unknown", jpeg_bytes) == "image/jpeg"
        
        # PNG
        png_bytes = b'\x89PNG\r\n\x1a\n' + b'0' * 100
        assert service._get_content_type("unknown", png_bytes) == "image/png"
        
        # GIF
        gif_bytes = b'GIF89a' + b'0' * 100
        assert service._get_content_type("unknown", gif_bytes) == "image/gif"
    
    def test_validate_image_size_too_large(self):
        """Test validation fails for oversized images"""
        service = StorageService()
        
        # Create 11MB image (exceeds 10MB default limit)
        large_image = b'0' * (11 * 1024 * 1024)
        
        with pytest.raises(StorageError, match="exceeds maximum"):
            service._validate_image(large_image, "large.jpg")
    
    def test_validate_image_size_too_small(self):
        """Test validation fails for suspiciously small images"""
        service = StorageService()
        
        tiny_image = b'0' * 50  # Less than 100 bytes
        
        with pytest.raises(StorageError, match="too small"):
            service._validate_image(tiny_image, "tiny.jpg")
    
    def test_validate_image_invalid_format(self):
        """Test validation fails for disallowed formats"""
        service = StorageService()
        
        # Mock settings to allow only JPEG
        with patch('app.services.storage_service.settings') as mock_settings:
            mock_settings.ALLOWED_IMAGE_FORMATS = "image/jpeg"
            mock_settings.MAX_UPLOAD_SIZE_MB = 10
            
            # Create valid-sized PNG image
            png_image = b'\x89PNG\r\n\x1a\n' + b'0' * 1000
            
            with pytest.raises(StorageError, match="not allowed"):
                service._validate_image(png_image, "test.png")
    
    def test_validate_image_success(self):
        """Test successful image validation"""
        service = StorageService()
        
        # Valid JPEG
        valid_image = b'\xff\xd8\xff\xe0' + b'0' * 1000
        
        # Should not raise
        service._validate_image(valid_image, "test.jpg")
    
    @pytest.mark.asyncio
    async def test_upload_image_success(self):
        """Test successful image upload"""
        service = StorageService()
        
        # Mock bucket
        mock_blob = MagicMock()
        mock_blob.public_url = "https://storage.googleapis.com/bucket/test.jpg"
        service.bucket.blob = MagicMock(return_value=mock_blob)
        
        # Valid image bytes
        image_bytes = b'\xff\xd8\xff\xe0' + b'0' * 1000
        
        url = await service.upload_image(
            image_bytes=image_bytes,
            filename="test.jpg",
            user_id="user_123",
            folder="uploads"
        )
        
        assert url == "https://storage.googleapis.com/bucket/test.jpg"
        mock_blob.upload_from_string.assert_called_once()
        mock_blob.make_public.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_upload_image_with_metadata(self):
        """Test upload with custom metadata"""
        service = StorageService()
        
        mock_blob = MagicMock()
        mock_blob.public_url = "https://storage.googleapis.com/bucket/test.jpg"
        service.bucket.blob = MagicMock(return_value=mock_blob)
        
        image_bytes = b'\xff\xd8\xff\xe0' + b'0' * 1000
        
        await service.upload_image(
            image_bytes=image_bytes,
            filename="test.jpg",
            user_id="user_123",
            metadata={"source": "pinterest", "pin_id": "123"}
        )
        
        # Check that metadata was set
        assert mock_blob.metadata is not None
        assert mock_blob.metadata.get("source") == "pinterest"
        assert mock_blob.metadata.get("pin_id") == "123"
    
    @pytest.mark.asyncio
    async def test_delete_image_success(self):
        """Test successful image deletion"""
        service = StorageService()
        
        mock_blob = MagicMock()
        service.bucket.blob = MagicMock(return_value=mock_blob)
        
        result = await service.delete_image("uploads/test.jpg")
        
        assert result is True
        mock_blob.delete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_image_failure(self):
        """Test image deletion failure handling"""
        service = StorageService()
        
        mock_blob = MagicMock()
        mock_blob.delete.side_effect = Exception("Delete failed")
        service.bucket.blob = MagicMock(return_value=mock_blob)
        
        result = await service.delete_image("uploads/test.jpg")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_signed_url(self):
        """Test signed URL generation"""
        service = StorageService()
        
        mock_blob = MagicMock()
        mock_blob.generate_signed_url.return_value = "https://storage.googleapis.com/bucket/test.jpg?signature=abc"
        service.bucket.blob = MagicMock(return_value=mock_blob)
        
        url = await service.get_signed_url("uploads/test.jpg", expiration=timedelta(hours=1))
        
        assert "signature=" in url
        mock_blob.generate_signed_url.assert_called_once()
    
    def test_get_storage_path_from_url(self):
        """Test extracting storage path from public URL"""
        service = StorageService()
        service.bucket_name = "test-bucket"
        
        url = "https://storage.googleapis.com/test-bucket/uploads/test.jpg"
        path = service.get_storage_path_from_url(url)
        
        assert path == "uploads/test.jpg"
    
    def test_get_storage_path_from_url_with_query(self):
        """Test extracting storage path from URL with query parameters"""
        service = StorageService()
        service.bucket_name = "test-bucket"
        
        url = "https://storage.googleapis.com/test-bucket/uploads/test.jpg?alt=media"
        path = service.get_storage_path_from_url(url)
        
        assert path == "uploads/test.jpg"
    
    def test_get_storage_path_invalid_url(self):
        """Test handling of invalid URL"""
        service = StorageService()
        
        path = service.get_storage_path_from_url("https://example.com/image.jpg")
        
        assert path is None
    
    def test_singleton_pattern(self):
        """Test that get_storage_service returns singleton"""
        service1 = get_storage_service()
        service2 = get_storage_service()
        
        assert service1 is service2


# Integration test (requires Firebase setup)
@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_upload_and_delete():
    """
    Integration test with real Firebase Storage.
    Only run when Firebase is configured.
    """
    service = get_storage_service()
    
    # Create test image
    test_image = b'\xff\xd8\xff\xe0' + b'TEST_IMAGE' * 100
    
    try:
        # Upload
        url = await service.upload_image(
            image_bytes=test_image,
            filename="test_integration.jpg",
            user_id="test_user",
            folder="test_uploads"
        )
        
        assert url is not None
        assert "storage.googleapis.com" in url
        
        # Extract path and delete
        path = service.get_storage_path_from_url(url)
        deleted = await service.delete_image(path)
        
        assert deleted is True
        
    except Exception as e:
        pytest.skip(f"Firebase not configured: {e}")

