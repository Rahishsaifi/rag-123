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
        # Get endpoint and clean it
        endpoint = settings.azure_openai_endpoint.strip().rstrip('/')
        
        # Debug: Log the exact values being used
        logger.info(f"Initializing Azure OpenAI client:")
        logger.info(f"  Endpoint: '{endpoint}' (length: {len(endpoint)})")
        logger.info(f"  Deployment: '{settings.azure_openai_embedding_deployment}'")
        logger.info(f"  API Version: '{settings.azure_openai_api_version}'")
        logger.info(f"  API Key (first 10 chars): '{settings.azure_openai_api_key[:10] if settings.azure_openai_api_key else 'None'}...'")
        
        # Validate endpoint format
        if not endpoint.startswith('https://'):
            logger.warning(f"Endpoint should start with https://, got: {endpoint}")
        if not '.openai.azure.com' in endpoint:
            logger.warning(f"Endpoint should contain .openai.azure.com, got: {endpoint}")
        
        try:
            # Initialize client exactly like test_credentials.py does (no timeout/retry params)
            self.client = AzureOpenAI(
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
                azure_endpoint=endpoint
            )
            logger.info(f"Azure OpenAI client initialized successfully")
            
        except TypeError as e:
            if "proxies" in str(e):
                logger.error("OpenAI SDK compatibility error - upgrade with: pip install --upgrade 'openai>=1.55.3'")
                raise
            raise
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
                # Log attempt details for debugging
                if attempt == 0:
                    logger.info(
                        f"Attempting to generate embeddings",
                        extra={
                            "extra_fields": {
                                "deployment": self.deployment,
                                "endpoint": settings.azure_openai_endpoint,
                                "num_texts": len(valid_texts),
                                "api_version": settings.azure_openai_api_version
                            }
                        }
                    )
                
                # Log the exact request being made
                logger.info(f"Making embedding request: model={self.deployment}, num_texts={len(valid_texts)}")
                logger.info(f"Client endpoint: {self.client._client.base_url if hasattr(self.client, '_client') else 'N/A'}")
                
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
                
                # Extract additional error details if available
                error_details = {
                    "error_type": error_type,
                    "error": error_msg,
                    "endpoint": settings.azure_openai_endpoint,
                    "deployment": self.deployment,
                    "api_version": settings.azure_openai_api_version
                }
                
                # Try to get HTTP response details if available
                if hasattr(e, 'response'):
                    try:
                        error_details["http_status"] = getattr(e.response, 'status_code', None)
                        error_details["http_headers"] = dict(getattr(e.response, 'headers', {}))
                        if hasattr(e.response, 'text'):
                            error_details["http_body"] = e.response.text[:500]  # First 500 chars
                    except:
                        pass
                
                # Try to get OpenAI API error details
                if hasattr(e, 'status_code'):
                    error_details["status_code"] = e.status_code
                if hasattr(e, 'body'):
                    try:
                        import json
                        error_details["api_error_body"] = json.loads(e.body) if isinstance(e.body, str) else str(e.body)[:500]
                    except:
                        error_details["api_error_body"] = str(e.body)[:500]
                
                # Log detailed error information
                logger.error(
                    f"Embedding generation failed (attempt {attempt + 1}/{self.max_retries}): {error_type}: {error_msg}",
                    extra={"extra_fields": error_details}
                )
                
                # Print to console for immediate visibility
                print(f"\n❌ Embedding Error (attempt {attempt + 1}/{self.max_retries}):")
                print(f"   Type: {error_type}")
                print(f"   Message: {error_msg}")
                print(f"   Endpoint: {settings.azure_openai_endpoint}")
                print(f"   Deployment: {self.deployment}")
                print(f"   API Version: {settings.azure_openai_api_version}")
                if "http_status" in error_details:
                    print(f"   HTTP Status: {error_details['http_status']}")
                if "api_error_body" in error_details:
                    print(f"   API Error: {error_details['api_error_body']}")
                print()
                
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

