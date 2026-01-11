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
        endpoint = settings.azure_openai_endpoint.rstrip('/')
        
        # Validate endpoint format
        if not endpoint.startswith('https://'):
            logger.warning(f"Endpoint should start with https://, got: {endpoint}")
        if not '.openai.azure.com' in endpoint:
            logger.warning(f"Endpoint should contain .openai.azure.com, got: {endpoint}")
        
        try:
            self.client = AzureOpenAI(
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
                azure_endpoint=endpoint
            )
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
            logger.error(f"Endpoint: {endpoint}")
            logger.error(f"API Version: {settings.azure_openai_api_version}")
            raise
        
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
                
            except Exception as e:
                last_exception = e
                error_type = type(e).__name__
                error_msg = str(e)
                
                # Log detailed error information
                logger.warning(
                    f"Embedding generation failed (attempt {attempt + 1}/{self.max_retries}): {error_type}: {error_msg}",
                    extra={
                        "extra_fields": {
                            "error_type": error_type,
                            "error": error_msg,
                            "endpoint": settings.azure_openai_endpoint,
                            "deployment": self.deployment,
                            "api_version": settings.azure_openai_api_version
                        }
                    }
                )
                
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"Embedding generation failed after {self.max_retries} attempts",
                        extra={
                            "extra_fields": {
                                "error_type": error_type,
                                "error": error_msg,
                                "endpoint": settings.azure_openai_endpoint,
                                "deployment": self.deployment
                            }
                        }
                    )
        
        # Provide more detailed error message
        error_type = type(last_exception).__name__
        error_msg = str(last_exception)
        
        if "Connection" in error_msg or "ConnectionError" in error_type:
            detailed_error = (
                f"Connection error to Azure OpenAI. "
                f"Endpoint: {settings.azure_openai_endpoint}, "
                f"Deployment: {self.deployment}. "
                f"Check: 1) Endpoint URL is correct, 2) Network connectivity, 3) Deployment name exists"
            )
        elif "401" in error_msg or "Unauthorized" in error_msg:
            detailed_error = (
                f"Authentication failed. "
                f"Check: 1) API key is correct, 2) API key has not expired, 3) API key has proper permissions"
            )
        elif "404" in error_msg or "not found" in error_msg.lower():
            detailed_error = (
                f"Deployment not found: {self.deployment}. "
                f"Check: 1) Deployment name is correct, 2) Deployment exists in Azure portal, 3) Deployment is active"
            )
        else:
            detailed_error = f"{error_type}: {error_msg}"
        
        raise Exception(f"Failed to generate embeddings after {self.max_retries} attempts: {detailed_error}")

