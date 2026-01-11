"""
Pydantic models for chat/Q&A requests and responses.
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat/Q&A."""
    
    question: str = Field(..., description="User question", min_length=1)
    top_k: Optional[int] = Field(None, description="Number of results to retrieve (overrides default)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the main topic of the document?",
                "top_k": 5
            }
        }


class SourceDocument(BaseModel):
    """Model for source document information."""
    
    content: str = Field(..., description="Chunk content")
    file_id: str = Field(..., description="Source file ID")
    filename: str = Field(..., description="Source filename")
    chunk_index: int = Field(..., description="Chunk index in the document")
    score: Optional[float] = Field(None, description="Relevance score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "This document discusses...",
                "file_id": "file-789",
                "filename": "document.pdf",
                "chunk_index": 0,
                "score": 0.95
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat/Q&A."""
    
    answer: str = Field(..., description="Generated answer")
    sources: List[SourceDocument] = Field(..., description="Source documents used")
    question: str = Field(..., description="Original question")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "The main topic is...",
                "sources": [
                    {
                        "content": "This document discusses...",
                        "file_id": "file-789",
                        "filename": "document.pdf",
                        "chunk_index": 0,
                        "score": 0.95
                    }
                ],
                "question": "What is the main topic of the document?"
            }
        }

