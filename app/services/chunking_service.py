"""
Token-aware text chunking service for splitting documents into manageable pieces.
"""
from typing import List, Dict, Any
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    tiktoken = None
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ChunkingService:
    """Service for chunking text into smaller pieces with token awareness."""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize chunking service.
        
        Args:
            chunk_size: Size of each chunk in tokens (defaults to config)
            chunk_overlap: Overlap between chunks in tokens (defaults to config)
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        # Use cl100k_base encoding (used by GPT-4 and text-embedding-ada-002)
        if TIKTOKEN_AVAILABLE:
            try:
                self.encoding = tiktoken.get_encoding("cl100k_base")
                logger.info("Using tiktoken for token-aware chunking")
            except Exception as e:
                logger.warning(f"Failed to load tiktoken encoding, using fallback: {e}")
                self.encoding = None
        else:
            logger.info("tiktoken not available, using character-based chunking fallback")
            self.encoding = None
    
    def chunk_text(
        self,
        text: str,
        metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Split text into chunks with token awareness.
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of chunk dictionaries with content and metadata
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for chunking")
            return []
        
        metadata = metadata or {}
        
        if self.encoding:
            chunks = self._chunk_with_tokens(text, metadata)
        else:
            # Fallback to character-based chunking
            chunks = self._chunk_with_characters(text, metadata)
        
        logger.info(
            f"Chunked text into {len(chunks)} chunks",
            extra={
                "extra_fields": {
                    "chunk_size": self.chunk_size,
                    "chunk_overlap": self.chunk_overlap,
                    "num_chunks": len(chunks)
                }
            }
        )
        
        return chunks
    
    def _chunk_with_tokens(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Chunk text using token-based splitting."""
        # Encode text to tokens
        tokens = self.encoding.encode(text)
        
        chunks = []
        start_idx = 0
        
        while start_idx < len(tokens):
            # Calculate end index
            end_idx = min(start_idx + self.chunk_size, len(tokens))
            
            # Extract chunk tokens
            chunk_tokens = tokens[start_idx:end_idx]
            
            # Decode back to text
            chunk_text = self.encoding.decode(chunk_tokens)
            
            # Create chunk with metadata
            chunk = {
                "content": chunk_text,
                "chunk_index": len(chunks),
                "start_token": start_idx,
                "end_token": end_idx,
                **metadata
            }
            
            chunks.append(chunk)
            
            # Move start index with overlap
            if end_idx >= len(tokens):
                break
            start_idx = end_idx - self.chunk_overlap
        
        return chunks
    
    def _chunk_with_characters(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback character-based chunking (approximate)."""
        # Rough approximation: 1 token ≈ 4 characters
        char_chunk_size = self.chunk_size * 4
        char_overlap = self.chunk_overlap * 4
        
        chunks = []
        start_idx = 0
        
        while start_idx < len(text):
            end_idx = min(start_idx + char_chunk_size, len(text))
            
            # Try to break at word boundary
            if end_idx < len(text):
                # Look for last space or newline before end
                last_break = text.rfind(' ', start_idx, end_idx)
                last_newline = text.rfind('\n', start_idx, end_idx)
                break_point = max(last_break, last_newline)
                
                if break_point > start_idx:
                    end_idx = break_point + 1
            
            chunk_text = text[start_idx:end_idx].strip()
            
            if chunk_text:
                chunk = {
                    "content": chunk_text,
                    "chunk_index": len(chunks),
                    "start_char": start_idx,
                    "end_char": end_idx,
                    **metadata
                }
                chunks.append(chunk)
            
            if end_idx >= len(text):
                break
            start_idx = max(start_idx + 1, end_idx - char_overlap)
        
        return chunks

