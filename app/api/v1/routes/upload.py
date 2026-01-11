"""
File upload API endpoints.
"""
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from app.models.upload import UploadRequest, UploadResponse
from app.services.blob_service import BlobService
from app.services.document_parser import DocumentParser
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.search_service import SearchService
from app.core.security import validate_upload_file, ensure_temp_dir, validate_file_size
from app.core.config import settings
from app.core.logging import get_logger
from app.utils.file_utils import generate_file_id, save_temp_file, get_file_size
import json

logger = get_logger(__name__)
router = APIRouter()


def get_blob_service() -> BlobService:
    return BlobService()


def get_parser() -> DocumentParser:
    return DocumentParser()


def get_chunking_service() -> ChunkingService:
    return ChunkingService()


def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()


def get_search_service() -> SearchService:
    return SearchService()


@router.post("", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    blob_service: BlobService = Depends(get_blob_service),
    parser: DocumentParser = Depends(get_parser),
    chunking_service: ChunkingService = Depends(get_chunking_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    search_service: SearchService = Depends(get_search_service)
) -> UploadResponse:
    """
    Upload a document file and trigger ingestion pipeline.
    
    Args:
        file: Uploaded file (PDF, DOC, or DOCX)
        blob_service: Blob storage service
        parser: Document parser service
        chunking_service: Chunking service
        embedding_service: Embedding service
        search_service: Search service
        
    Returns:
        UploadResponse with file ID and status
    """
    try:
        validate_upload_file(file)
        file_id = generate_file_id()
        
        logger.info(
            f"Starting file upload",
            extra={
                "extra_fields": {
                    "file_id": file_id,
                    "filename": file.filename
                }
            }
        )
        
        file_content = await file.read()
        file_size = len(file_content)
        if not validate_file_size(file_size):
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB"
            )
        
        temp_dir = ensure_temp_dir()
        temp_path = save_temp_file(file_content, file.filename or "document", temp_dir)
        
        try:
            blob_url = blob_service.upload_file(
                file_path=temp_path,
                file_id=file_id
            )
            
            text = parser.parse_file(temp_path)
            
            if not text or not text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Failed to extract text from document. The file may be empty or corrupted."
                )
            
            chunk_metadata = {
                "file_id": file_id,
                "filename": file.filename or "document"
            }
            chunks = chunking_service.chunk_text(text, metadata=chunk_metadata)
            
            if not chunks:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to chunk document. The document may be too short."
                )
            
            chunk_texts = [chunk["content"] for chunk in chunks]
            embeddings = embedding_service.generate_embeddings(chunk_texts)
            
            if len(embeddings) != len(chunks):
                raise HTTPException(
                    status_code=500,
                    detail="Mismatch between chunks and embeddings"
                )
            
            search_documents = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                doc_id = f"{file_id}-chunk-{i}"
                search_doc = {
                    "id": doc_id,
                    "file_id": file_id,
                    "filename": file.filename or "document",
                    "chunk_index": chunk["chunk_index"],
                    "content": chunk["content"],
                    "content_vector": embedding,
                    "metadata": json.dumps(chunk_metadata)
                }
                search_documents.append(search_doc)
            
            search_service.upload_documents(search_documents)
            
            logger.info(
                f"File upload and indexing completed successfully",
                extra={
                    "extra_fields": {
                        "file_id": file_id,
                        "num_chunks": len(chunks)
                    }
                }
            )
            
            return UploadResponse(
                file_id=file_id,
                filename=file.filename or "document",
                blob_url=blob_url,
                status="success",
                message=f"File uploaded and indexed successfully. {len(chunks)} chunks created."
            )
            
        finally:
            try:
                if temp_path.exists():
                    temp_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {e}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error during file upload: {e}",
            extra={"extra_fields": {"error": str(e)}}
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload and index file: {str(e)}"
        )

