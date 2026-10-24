import os
import uuid
import re
import logging
from typing import Tuple, Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger("mindsync.storage")

# Root uploads directory under backend/uploads
BACKEND_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BACKEND_DIR / "uploads"
IMAGES_DIR = UPLOAD_DIR / "images"

# Ensure upload directories exist
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Allowed image formats & extensions
ALLOWED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif", ".gif", ".heic", ".heif"
}

ALLOWED_MIME_TYPES = {
    "image/png", "image/jpeg", "image/pjpeg", "image/webp", "image/bmp",
    "image/tiff", "image/gif", "image/x-ms-bmp", "image/heic", "image/heif"
}

# 25 MB max limit
MAX_IMAGE_FILE_SIZE_BYTES = 25 * 1024 * 1024


def sanitize_filename(filename: str) -> str:
    """Strip dangerous characters and keep only safe alphanumerics and dots/underscores."""
    name = os.path.basename(filename)
    clean = re.sub(r'[^a-zA-Z0-9_.-]', '_', name)
    return clean[:80] if len(clean) > 80 else clean


def validate_image_file(filename: str, content_type: Optional[str], file_bytes: bytes) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Validate format, file size, and image integrity.
    Returns:
        (is_valid: bool, error_message: Optional[str], metadata: Optional[Dict])
    """
    if not file_bytes or len(file_bytes) == 0:
        return False, "Uploaded file is empty (0 bytes).", None

    # 1. Size Validation
    size_bytes = len(file_bytes)
    if size_bytes > MAX_IMAGE_FILE_SIZE_BYTES:
        size_mb = size_bytes / (1024 * 1024)
        return False, f"Image size ({size_mb:.1f} MB) exceeds maximum allowed limit of 25 MB.", None

    # 2. Extension Validation
    ext = os.path.splitext(filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file extension '{ext}'. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}.", None

    # 3. MIME Type Validation (if provided)
    if content_type and content_type.lower() not in ALLOWED_MIME_TYPES and not content_type.startswith("image/"):
        return False, f"Unsupported media type '{content_type}'. Please upload a valid image file.", None

    # 4. Image Data Integrity & Dimension Check via Pillow
    try:
        from PIL import Image
        import io
        with Image.open(io.BytesIO(file_bytes)) as img:
            img.verify()  # Verifies image structure
        
        # Re-open to read dimensions safely after verify
        with Image.open(io.BytesIO(file_bytes)) as img:
            width, height = img.size
            img_format = img.format or ext.replace(".", "").upper()

        file_size_formatted = f"{(size_bytes / (1024 * 1024)):.2f} MB" if size_bytes >= 1024 * 1024 else f"{(size_bytes / 1024):.1f} KB"

        metadata = {
            "width": width,
            "height": height,
            "format": img_format,
            "sizeBytes": size_bytes,
            "fileSize": file_size_formatted,
            "extension": ext
        }
        return True, None, metadata

    except Exception as e:
        logger.warning(f"Image integrity verification failed for {filename}: {e}")
        return False, f"The file could not be decoded as a valid image: {str(e)}", None


def save_image_file(file_bytes: bytes, original_filename: str) -> Dict[str, Any]:
    """
    Persist image file on disk in backend/uploads/images with unique UUID filename.
    Returns storage details including static URL and disk paths.
    """
    safe_name = sanitize_filename(original_filename)
    ext = os.path.splitext(safe_name)[1].lower() or ".png"
    unique_filename = f"{uuid.uuid4().hex[:12]}_{safe_name}"

    dest_path = IMAGES_DIR / unique_filename
    with open(dest_path, "wb") as f:
        f.write(file_bytes)

    # Relative URL served by FastAPI static mount
    relative_url = f"/api/uploads/images/{unique_filename}"
    file_size_formatted = f"{(len(file_bytes) / (1024 * 1024)):.2f} MB" if len(file_bytes) >= 1024 * 1024 else f"{(len(file_bytes) / 1024):.1f} KB"

    return {
        "fileName": unique_filename,
        "originalFileName": original_filename,
        "fileUrl": relative_url,
        "filePath": str(dest_path),
        "fileSize": file_size_formatted,
        "sizeBytes": len(file_bytes)
    }
