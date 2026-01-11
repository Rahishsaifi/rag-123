"""
Chat/Q&A API endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends
from app.models.chat import ChatRequest, ChatResponse
from app.services.rag_service import RAGService
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


def get_rag_service() -> RAGService:
    """Dependency for RAGService."""
    return RAGService()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service)
) -> ChatResponse:
    """
    Process a chat question using RAG pipeline.
    
    Args:
        request: Chat request with question
        rag_service: RAG service for orchestration
        
    Returns:
        ChatResponse with answer and source documents
    """
    try:
        logger.info(
            f"Processing chat request",
            extra={
                "extra_fields": {
                    "question_length": len(request.question)
                }
            }
        )
        
        # Process query through RAG pipeline
        result = rag_service.query(
            question=request.question,
            top_k=request.top_k
        )
        
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            question=result["question"]
        )
        
    except Exception as e:
        logger.error(
            f"Error processing chat request: {e}",
            extra={"extra_fields": {"error": str(e)}}
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat request: {str(e)}"
        )

