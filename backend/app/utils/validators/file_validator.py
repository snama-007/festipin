"""
File Validation Utilities
Secure file upload validation with multiple checks
"""

from typing import Tuple, Optional
from pathlib import Path
import magic
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)


class FileValidationError(Exception):
    """Custom exception for file validation errors"""
    pass


class FileValidator:
    """
    Comprehensive file validator with security checks
    """

    # Allowed MIME types
    ALLOWED_MIME_TYPES = {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
    }

    # Allowed file extensions
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

    # File size limits (in bytes)
    MIN_FILE_SIZE = 1024  # 1 KB
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

    # Image dimension limits
    MIN_DIMENSION = 256  # pixels
    MAX_DIMENSION = 8192  # pixels

    # Aspect ratio limits
    MIN_ASPECT_RATIO = 0.2  # 1:5
    MAX_ASPECT_RATIO = 5.0  # 5:1

    @classmethod
    async def validate_upload(
        cls,
        file_content: bytes,
        filename: str,
    ) -> Tuple[bool, Optional[str], Optional[dict]]:
        """
        Comprehensive file validation

        Returns:
            (is_valid, error_message, metadata)
        """
        try:
            # 1. Check file size
            file_size = len(file_content)
            if file_size < cls.MIN_FILE_SIZE:
                return False, f"File too small (min {cls.MIN_FILE_SIZE} bytes)", None
            if file_size > cls.MAX_FILE_SIZE:
                return False, f"File too large (max {cls.MAX_FILE_SIZE / 1024 / 1024:.1f} MB)", None

            # 2. Check file extension
            file_ext = Path(filename).suffix.lower()
            if file_ext not in cls.ALLOWED_EXTENSIONS:
                return False, f"Invalid file extension (allowed: {', '.join(cls.ALLOWED_EXTENSIONS)})", None

            # 3. Check MIME type using python-magic
            try:
                mime_type = magic.from_buffer(file_content, mime=True)
                if mime_type not in cls.ALLOWED_MIME_TYPES:
                    return False, f"Invalid file type: {mime_type}", None
            except Exception as e:
                logger.warning(f"MIME type detection failed: {e}")
                # Continue with other checks

            # 4. Validate image with PIL
            try:
                image = Image.open(io.BytesIO(file_content))
                image.verify()  # Verify it's a valid image

                # Re-open for metadata (verify closes the file)
                image = Image.open(io.BytesIO(file_content))

                width, height = image.size
                format_name = image.format
                mode = image.mode

                # Check dimensions
                if width < cls.MIN_DIMENSION or height < cls.MIN_DIMENSION:
                    return False, f"Image too small (min {cls.MIN_DIMENSION}x{cls.MIN_DIMENSION})", None

                if width > cls.MAX_DIMENSION or height > cls.MAX_DIMENSION:
                    return False, f"Image too large (max {cls.MAX_DIMENSION}x{cls.MAX_DIMENSION})", None

                # Check aspect ratio
                aspect_ratio = width / height
                if aspect_ratio < cls.MIN_ASPECT_RATIO or aspect_ratio > cls.MAX_ASPECT_RATIO:
                    return False, f"Invalid aspect ratio: {aspect_ratio:.2f}", None

                # Check for image bombs (decompression attacks)
                pixel_count = width * height
                max_pixels = 50_000_000  # 50 megapixels
                if pixel_count > max_pixels:
                    return False, f"Image too large ({pixel_count:,} pixels, max {max_pixels:,})", None

                metadata = {
                    "width": width,
                    "height": height,
                    "format": format_name,
                    "mode": mode,
                    "file_size": file_size,
                    "aspect_ratio": aspect_ratio,
                }

                return True, None, metadata

            except Exception as e:
                return False, f"Invalid or corrupted image: {str(e)}", None

        except Exception as e:
            logger.error(f"File validation error: {e}")
            return False, f"Validation error: {str(e)}", None

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and other attacks
        """
        # Get just the filename, remove any path components
        filename = Path(filename).name

        # Remove any non-alphanumeric characters except dots, dashes, underscores
        import re
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

        # Limit length
        max_length = 200
        if len(filename) > max_length:
            name, ext = Path(filename).stem, Path(filename).suffix
            filename = name[:max_length - len(ext)] + ext

        return filename

    @classmethod
    async def optimize_image(
        cls,
        file_content: bytes,
        max_dimension: int = 2048,
        quality: int = 85,
    ) -> Tuple[bytes, dict]:
        """
        Optimize image for storage and processing

        Returns:
            (optimized_content, metadata)
        """
        try:
            image = Image.open(io.BytesIO(file_content))
            original_size = image.size
            original_format = image.format

            # Convert RGBA to RGB if necessary
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background

            # Resize if too large
            if max(image.size) > max_dimension:
                ratio = max_dimension / max(image.size)
                new_size = tuple(int(dim * ratio) for dim in image.size)
                image = image.resize(new_size, Image.Resampling.LANCZOS)

            # Save optimized
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            optimized_content = output.getvalue()

            metadata = {
                "original_size": original_size,
                "optimized_size": image.size,
                "original_format": original_format,
                "optimized_format": "JPEG",
                "original_bytes": len(file_content),
                "optimized_bytes": len(optimized_content),
                "compression_ratio": len(optimized_content) / len(file_content),
            }

            return optimized_content, metadata

        except Exception as e:
            logger.error(f"Image optimization error: {e}")
            raise FileValidationError(f"Failed to optimize image: {str(e)}")

    @classmethod
    async def create_thumbnail(
        cls,
        file_content: bytes,
        size: Tuple[int, int] = (300, 300),
        quality: int = 80,
    ) -> bytes:
        """
        Create thumbnail from image
        """
        try:
            image = Image.open(io.BytesIO(file_content))

            # Convert RGBA to RGB
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background

            # Create thumbnail (maintains aspect ratio)
            image.thumbnail(size, Image.Resampling.LANCZOS)

            # Save thumbnail
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            return output.getvalue()

        except Exception as e:
            logger.error(f"Thumbnail creation error: {e}")
            raise FileValidationError(f"Failed to create thumbnail: {str(e)}")
