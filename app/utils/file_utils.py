"""
File utility functions for handling file operations.
"""
import uuid
from pathlib import Path
from typing import BinaryIO
from app.core.logging import get_logger

logger = get_logger(__name__)


def generate_file_id() -> str:
    """
    Generate a unique file ID.
    
    Returns:
        Unique file identifier
    """
    return f"file-{uuid.uuid4().hex[:12]}"


def save_temp_file(file_content: bytes, filename: str, temp_dir: Path) -> Path:
    """
    Save file content to temporary directory.
    
    Args:
        file_content: File content as bytes
        filename: Original filename
        temp_dir: Temporary directory path
        
    Returns:
        Path to saved temporary file
    """
    file_id = generate_file_id()
    temp_filename = f"{file_id}_{filename}"
    temp_path = temp_dir / temp_filename
    
    with open(temp_path, "wb") as f:
        f.write(file_content)
    
    logger.info(
        f"Saved temporary file: {temp_filename}",
        extra={"extra_fields": {"file_id": file_id, "temp_path": str(temp_path)}}
    )
    
    return temp_path


def read_file_chunks(file_path: Path, chunk_size: int = 8192) -> bytes:
    """
    Read file in chunks (for large files).
    
    Args:
        file_path: Path to file
        chunk_size: Size of each chunk in bytes
        
    Yields:
        File chunks as bytes
    """
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


def get_file_size(file_path: Path) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes
    """
    return file_path.stat().st_size

