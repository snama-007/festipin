"""
Firebase Cloud Storage Service

Handles image uploads, file management, and URL generation for Firebase Storage.
"""

import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
import mimetypes

from firebase_admin import storage
import firebase_admin
from firebase_admin import credentials

from app.core.config import settings
from app.core.logging import logger
from app.core.errors import StorageError


class StorageService:
    """
    Firebase Cloud Storage service for image management.
    
    Features:
    - Upload images with automatic content-type detection
    - Generate unique filenames with collision prevention
    - Create public access URLs
    - Support for different storage paths (users, pinterest, uploads, etc.)
    - Automatic image validation
    """
    
    def __init__(self):
        self.bucket_name = settings.FIREBASE_STORAGE_BUCKET
        self.bucket = None
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize Firebase Storage bucket"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
                firebase_admin.initialize_app(cred, {
                    'storageBucket': self.bucket_name
                })
                logger.info("Firebase Admin initialized for storage")
            
            # Get bucket reference
            self.bucket = storage.bucket(self.bucket_name)
            logger.info("Firebase Storage bucket initialized", bucket=self.bucket_name)
            
        except Exception as e:
            logger.error("Failed to initialize Firebase Storage", error=str(e))
            raise StorageError(
                f"Storage initialization failed: {str(e)}",
                context={"bucket": self.bucket_name}
            )
    
    def _generate_unique_filename(
        self, 
        original_filename: Optional[str] = None,
        user_id: Optional[str] = None,
        prefix: str = "image"
    ) -> str:
        """
        Generate unique filename with collision prevention.
        
        Format: {prefix}_{user_id}_{timestamp}_{uuid}_{hash}.{ext}
        
        Args:
            original_filename: Original file name (to extract extension)
            user_id: User identifier
            prefix: Filename prefix (e.g., 'pinterest', 'upload')
            
        Returns:
            Unique filename string
        """
        # Extract extension
        if original_filename:
            ext = Path(original_filename).suffix.lower()
            if not ext:
                ext = '.jpg'  # Default to jpg
        else:
            ext = '.jpg'
        
        # Generate components
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        # Create hash for extra uniqueness
        hash_input = f"{prefix}_{user_id}_{timestamp}_{unique_id}"
        file_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        
        # Build filename
        parts = [prefix]
        if user_id:
            parts.append(user_id[:8])  # Truncate long user IDs
        parts.extend([timestamp, unique_id, file_hash])
        
        filename = '_'.join(parts) + ext
        
        logger.debug("Generated unique filename", filename=filename)
        return filename
    
    def _get_content_type(self, filename: str, image_bytes: bytes) -> str:
        """
        Determine content type from filename or bytes.
        
        Args:
            filename: Filename to check
            image_bytes: Image data (for fallback detection)
            
        Returns:
            Content-Type string (e.g., 'image/jpeg')
        """
        # Try to get from filename
        content_type, _ = mimetypes.guess_type(filename)
        
        if content_type and content_type.startswith('image/'):
            return content_type
        
        # Fallback: check magic bytes
        if image_bytes[:4] == b'\xff\xd8\xff\xe0' or image_bytes[:4] == b'\xff\xd8\xff\xe1':
            return 'image/jpeg'
        elif image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
            return 'image/png'
        elif image_bytes[:6] in (b'GIF87a', b'GIF89a'):
            return 'image/gif'
        elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
            return 'image/webp'
        
        # Default fallback
        return 'image/jpeg'
    
    def _validate_image(self, image_bytes: bytes, filename: str) -> None:
        """
        Validate image data.
        
        Args:
            image_bytes: Image data to validate
            filename: Filename for logging
            
        Raises:
            StorageError: If validation fails
        """
        # Check size
        max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if len(image_bytes) > max_size_bytes:
            raise StorageError(
                f"Image size ({len(image_bytes)/1024/1024:.2f}MB) exceeds maximum ({settings.MAX_UPLOAD_SIZE_MB}MB)",
                context={"filename": filename, "size_mb": len(image_bytes)/1024/1024}
            )
        
        # Check minimum size (avoid empty files)
        if len(image_bytes) < 100:  # Less than 100 bytes is suspicious
            raise StorageError(
                "Image data too small (possibly corrupted)",
                context={"filename": filename, "size_bytes": len(image_bytes)}
            )
        
        # Validate allowed formats
        content_type = self._get_content_type(filename, image_bytes)
        allowed_formats = settings.ALLOWED_IMAGE_FORMATS.split(',')
        
        if content_type not in allowed_formats:
            raise StorageError(
                f"Image format {content_type} not allowed",
                context={"filename": filename, "allowed": allowed_formats}
            )
    
    async def upload_image(
        self,
        image_bytes: bytes,
        filename: Optional[str] = None,
        user_id: Optional[str] = None,
        folder: str = "uploads",
        metadata: Optional[Dict[str, str]] = None,
        public: bool = True
    ) -> str:
        """
        Upload image to Firebase Cloud Storage.
        
        Args:
            image_bytes: Image data as bytes
            filename: Original filename (for extension detection)
            user_id: User identifier
            folder: Storage folder/prefix (e.g., 'uploads', 'pinterest')
            metadata: Custom metadata to attach
            public: Make file publicly accessible
            
        Returns:
            Public URL of uploaded image
            
        Raises:
            StorageError: If upload fails
        """
        try:
            # Validate image
            self._validate_image(image_bytes, filename or 'unknown')
            
            # Generate unique filename
            unique_filename = self._generate_unique_filename(
                original_filename=filename,
                user_id=user_id,
                prefix=folder
            )
            
            # Full path in storage
            storage_path = f"{folder}/{unique_filename}"
            
            # Get content type
            content_type = self._get_content_type(unique_filename, image_bytes)
            
            logger.info(
                "Uploading image to storage",
                path=storage_path,
                size_kb=round(len(image_bytes) / 1024, 2),
                content_type=content_type
            )
            
            # Create blob
            blob = self.bucket.blob(storage_path)
            
            # Set metadata
            blob_metadata = {
                'contentType': content_type,
                'uploadedBy': user_id or 'anonymous',
                'uploadedAt': datetime.utcnow().isoformat(),
                'originalFilename': filename or 'unknown'
            }
            
            if metadata:
                blob_metadata.update(metadata)
            
            blob.metadata = blob_metadata
            
            # Upload
            blob.upload_from_string(
                image_bytes,
                content_type=content_type
            )
            
            # Make public if requested
            if public:
                blob.make_public()
            
            # Get public URL
            public_url = blob.public_url
            
            logger.info(
                "Image uploaded successfully",
                path=storage_path,
                url=public_url,
                size_kb=round(len(image_bytes) / 1024, 2)
            )
            
            return public_url
            
        except StorageError:
            raise
        except Exception as e:
            logger.error(
                "Failed to upload image",
                error=str(e),
                filename=filename
            )
            raise StorageError(
                f"Image upload failed: {str(e)}",
                context={"filename": filename, "folder": folder}
            )
    
    async def delete_image(self, storage_path: str) -> bool:
        """
        Delete image from storage.
        
        Args:
            storage_path: Full path in storage (e.g., 'uploads/image_123.jpg')
            
        Returns:
            True if deleted successfully
        """
        try:
            blob = self.bucket.blob(storage_path)
            blob.delete()
            
            logger.info("Image deleted", path=storage_path)
            return True
            
        except Exception as e:
            logger.error("Failed to delete image", error=str(e), path=storage_path)
            return False
    
    async def get_signed_url(
        self,
        storage_path: str,
        expiration: timedelta = timedelta(hours=1)
    ) -> str:
        """
        Generate signed URL for temporary access.
        
        Args:
            storage_path: Path in storage
            expiration: URL validity duration
            
        Returns:
            Signed URL string
        """
        try:
            blob = self.bucket.blob(storage_path)
            url = blob.generate_signed_url(expiration=expiration)
            
            logger.debug("Generated signed URL", path=storage_path)
            return url
            
        except Exception as e:
            logger.error("Failed to generate signed URL", error=str(e))
            raise StorageError(f"Signed URL generation failed: {str(e)}")
    
    def get_storage_path_from_url(self, public_url: str) -> Optional[str]:
        """
        Extract storage path from public URL.
        
        Args:
            public_url: Public URL from Firebase Storage
            
        Returns:
            Storage path (e.g., 'uploads/image_123.jpg') or None
        """
        try:
            # Firebase Storage URL format:
            # https://storage.googleapis.com/{bucket}/{path}
            if 'storage.googleapis.com' in public_url:
                parts = public_url.split(f"{self.bucket_name}/")
                if len(parts) > 1:
                    return parts[1].split('?')[0]  # Remove query params
            return None
        except Exception as e:
            logger.warning("Failed to extract storage path from URL", error=str(e))
            return None


# Singleton instance
_storage_instance: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Get or create StorageService singleton"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = StorageService()
    return _storage_instance

