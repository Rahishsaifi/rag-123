"""
Security utilities for file validation and tenant isolation.
"""
import os
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def validate_file_type(filename: str) -> bool:
    """
    Validate that the file extension is allowed.
    
    Args:
        filename: Name of the uploaded file
        
    Returns:
        True if file type is allowed, False otherwise
    """
    file_ext = Path(filename).suffix.lower()
    allowed_extensions = [ext.lower() for ext in settings.allowed_file_extensions]
    
    is_valid = file_ext in allowed_extensions
    
    if not is_valid:
        logger.warning(
            f"Rejected file with extension {file_ext}",
            extra={"extra_fields": {"filename": filename, "extension": file_ext}}
        )
    
    return is_valid


def validate_file_size(file_size: int) -> bool:
    """
    Validate that the file size is within limits.
    
    Args:
        file_size: Size of the file in bytes
        
    Returns:
        True if file size is within limits, False otherwise
    """
    max_size_bytes = settings.max_file_size_mb * 1024 * 1024
    is_valid = file_size <= max_size_bytes
    
    if not is_valid:
        logger.warning(
            f"Rejected file exceeding size limit",
            extra={
                "extra_fields": {
                    "file_size": file_size,
                    "max_size": max_size_bytes
                }
            }
        )
    
    return is_valid


def validate_upload_file(file: UploadFile) -> None:
    """
    Validate an uploaded file for type and size.
    
    Args:
        file: FastAPI UploadFile object
        
    Raises:
        HTTPException: If file validation fails
    """
    if not validate_file_type(file.filename or ""):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.allowed_file_extensions)}"
        )
    


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and other security issues.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    safe_name = Path(filename).name
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    for char in dangerous_chars:
        safe_name = safe_name.replace(char, '_')
    
    return safe_name


def ensure_temp_dir() -> Path:
    """
    Ensure temporary directory exists and return its path.
    
    Returns:
        Path to temporary directory
    """
    temp_path = Path(settings.temp_dir)
    temp_path.mkdir(parents=True, exist_ok=True)
    return temp_path

