"""
Azure OpenAI embedding service for generating vector embeddings.
"""
from typing import List
import time
from openai import AzureOpenAI
from azure.core.exceptions import AzureError
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating embeddings using Azure OpenAI."""
    
    def __init__(self):
        """Initialize Azure OpenAI client."""
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint.rstrip('/')
        )
        self.deployment = settings.azure_openai_embedding_deployment
        self.max_retries = 3
        self.retry_delay = 1.0
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
            
        Raises:
            Exception: If embedding generation fails
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return []
        
        return self.generate_embeddings([text])[0]
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts with retry logic.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            Exception: If embedding generation fails after retries
        """
        if not texts:
            return []
        
        valid_texts = [text for text in texts if text and text.strip()]
        if not valid_texts:
            logger.warning("No valid texts provided for embedding")
            return []
        
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.embeddings.create(
                    model=self.deployment,
                    input=valid_texts
                )
                
                embeddings = [item.embedding for item in response.data]
                
                logger.info(
                    f"Generated {len(embeddings)} embeddings",
                    extra={
                        "extra_fields": {
                            "deployment": self.deployment,
                            "num_texts": len(valid_texts)
                        }
                    }
                )
                
                return embeddings
                
            except (AzureError, Exception) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(
                        f"Embedding generation failed (attempt {attempt + 1}/{self.max_retries}), retrying in {wait_time}s: {e}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"Embedding generation failed after {self.max_retries} attempts: {e}",
                        extra={"extra_fields": {"error": str(e)}}
                    )
        
        raise Exception(f"Failed to generate embeddings after {self.max_retries} attempts: {last_exception}")

