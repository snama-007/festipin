"""
Local Storage Service (Development/Testing Only)
Saves images to local filesystem instead of Firebase Cloud Storage
"""

import os
import hashlib
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

from app.core.logging import setup_logging
from app.core.errors import StorageError

logger = setup_logging()


class LocalStorageService:
    """
    Local file storage service for development/testing
    Stores images in backend/uploads/ directory
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """Initialize local storage service"""
        if base_path:
            self.base_path = Path(base_path)
        else:
            # Default: backend/uploads/
            self.base_path = Path(__file__).parent.parent.parent / "uploads"
        
        # Create base directory if it doesn't exist
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            "Local storage initialized",
            base_path=str(self.base_path),
            mode="development"
        )
    
    def _generate_filename(
        self,
        original_filename: str,
        user_id: str,
        folder: str
    ) -> str:
        """Generate unique filename with timestamp and hash"""
        # Extract extension
        ext = Path(original_filename).suffix or '.jpeg'
        
        # Create unique identifier
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        hash_input = f"{user_id}_{original_filename}_{timestamp}"
        file_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        
        # Clean user_id for filename
        safe_user_id = user_id.replace('/', '_').replace('\\', '_')[:20]
        
        # Generate filename: folder_userid_timestamp_hash.ext
        filename = f"{folder}_{safe_user_id}_{timestamp}_{file_hash}{ext}"
        
        return filename
    
    def _validate_image_content(self, image_bytes: bytes) -> bool:
        """Basic image validation"""
        # Check size (max 10MB)
        max_size = 10 * 1024 * 1024
        if len(image_bytes) > max_size:
            raise StorageError(f"Image too large: {len(image_bytes) / 1024 / 1024:.2f}MB (max 10MB)")
        
        # Check if it's likely an image (basic magic number check)
        if not image_bytes:
            raise StorageError("Empty image file")
        
        # JPEG magic numbers
        if image_bytes.startswith(b'\xff\xd8\xff'):
            return True
        # PNG magic numbers
        if image_bytes.startswith(b'\x89PNG'):
            return True
        # WebP magic numbers
        if image_bytes[8:12] == b'WEBP':
            return True
        
        logger.warning("Unknown image format, allowing anyway")
        return True
    
    async def upload_image(
        self,
        image_bytes: bytes,
        filename: str,
        user_id: str,
        folder: str = "general",
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Upload image to local filesystem
        
        Args:
            image_bytes: Raw image data
            filename: Original filename
            user_id: User identifier
            folder: Logical folder/category
            metadata: Optional metadata dict
        
        Returns:
            Local file URL (http://localhost:9000/uploads/...)
        """
        try:
            # Validate image
            self._validate_image_content(image_bytes)
            
            # Generate unique filename
            safe_filename = self._generate_filename(filename, user_id, folder)
            
            # Create subfolder if needed
            subfolder_path = self.base_path / folder
            subfolder_path.mkdir(parents=True, exist_ok=True)
            
            # Full file path
            file_path = subfolder_path / safe_filename
            
            logger.info(
                "Saving image locally",
                path=str(file_path),
                size_kb=round(len(image_bytes) / 1024, 2),
                original_filename=filename
            )
            
            # Write file
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
            
            # Generate public URL (served by backend)
            # Format: http://localhost:9000/uploads/folder/filename
            relative_path = f"{folder}/{safe_filename}"
            public_url = f"http://localhost:9000/uploads/{relative_path}"
            
            logger.info(
                "Image saved successfully",
                url=public_url,
                path=str(file_path)
            )
            
            # Save metadata if provided
            if metadata:
                meta_path = file_path.with_suffix(file_path.suffix + '.meta.json')
                import json
                with open(meta_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
            
            return public_url
            
        except Exception as e:
            logger.error(
                "Failed to save image locally",
                error=str(e),
                filename=filename
            )
            raise StorageError(f"Local storage upload failed: {str(e)}")
    
    async def get_image_url(
        self,
        filename: str,
        folder: str = "general"
    ) -> str:
        """Get public URL for an image"""
        relative_path = f"{folder}/{filename}"
        return f"http://localhost:9000/uploads/{relative_path}"
    
    async def delete_image(
        self,
        filename: str,
        folder: str = "general"
    ) -> bool:
        """Delete an image from local storage"""
        try:
            file_path = self.base_path / folder / filename
            
            if file_path.exists():
                file_path.unlink()
                logger.info("Image deleted", path=str(file_path))
                
                # Delete metadata if exists
                meta_path = file_path.with_suffix(file_path.suffix + '.meta.json')
                if meta_path.exists():
                    meta_path.unlink()
                
                return True
            else:
                logger.warning("Image not found for deletion", path=str(file_path))
                return False
                
        except Exception as e:
            logger.error("Failed to delete image", error=str(e), filename=filename)
            raise StorageError(f"Failed to delete image: {str(e)}")
    
    def get_stats(self) -> Dict:
        """Get storage statistics"""
        total_files = 0
        total_size = 0
        
        for file_path in self.base_path.rglob('*'):
            if file_path.is_file() and not file_path.name.endswith('.meta.json'):
                total_files += 1
                total_size += file_path.stat().st_size
        
        return {
            "total_files": total_files,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "base_path": str(self.base_path)
        }
