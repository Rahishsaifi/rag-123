"""
Pydantic models for file upload requests and responses.
"""
from typing import Optional
from pydantic import BaseModel, Field


class UploadRequest(BaseModel):
    """Request model for file upload."""
    
    class Config:
        json_schema_extra = {
            "example": {}
        }


class UploadResponse(BaseModel):
    """Response model for file upload."""
    
    file_id: str = Field(..., description="Unique identifier for the uploaded file")
    filename: str = Field(..., description="Original filename")
    blob_url: Optional[str] = Field(None, description="Azure Blob Storage URL")
    status: str = Field(..., description="Upload status")
    message: str = Field(..., description="Status message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "file-789",
                "filename": "document.pdf",
                "blob_url": "https://storage.azure.com/...",
                "status": "success",
                "message": "File uploaded and indexed successfully"
            }
        }

