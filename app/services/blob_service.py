"""
Azure Blob Storage service for storing uploaded documents.
"""
from pathlib import Path
from typing import Optional
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.core.exceptions import AzureError
from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import sanitize_filename

logger = get_logger(__name__)


class BlobService:
    """Service for interacting with Azure Blob Storage."""
    
    def __init__(self):
        """Initialize Blob Storage client."""
        self.blob_service_client = BlobServiceClient.from_connection_string(
            settings.azure_blob_connection_string
        )
        self.container_name = settings.azure_blob_container_name
        self._ensure_container()
    
    def _ensure_container(self) -> None:
        """Ensure the container exists, create if it doesn't."""
        try:
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            if not container_client.exists():
                container_client.create_container()
                logger.info(f"Created container: {self.container_name}")
        except AzureError as e:
            logger.error(f"Error ensuring container exists: {e}")
            raise
    
    def upload_file(
        self,
        file_path: Path,
        file_id: str
    ) -> str:
        """
        Upload a file to Azure Blob Storage.
        
        Args:
            file_path: Local path to the file
            file_id: Unique file identifier
            
        Returns:
            Blob URL of the uploaded file
            
        Raises:
            AzureError: If upload fails
        """
        try:
            # Create blob name
            blob_name = f"{file_id}/{file_path.name}"
            blob_name = sanitize_filename(blob_name)
            
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Upload file
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            
            blob_url = blob_client.url
            
            logger.info(
                f"Uploaded file to blob storage: {blob_name}",
                extra={
                    "extra_fields": {
                        "file_id": file_id,
                        "blob_url": blob_url
                    }
                }
            )
            
            return blob_url
            
        except AzureError as e:
            logger.error(
                f"Failed to upload file to blob storage: {e}",
                extra={"extra_fields": {"file_id": file_id, "error": str(e)}}
            )
            raise
    
    def get_blob_url(self, file_id: str, filename: str) -> Optional[str]:
        """
        Get the blob URL for a file.
        
        Args:
            file_id: Unique file identifier
            filename: Original filename
            
        Returns:
            Blob URL if exists, None otherwise
        """
        try:
            blob_name = f"{file_id}/{filename}"
            blob_name = sanitize_filename(blob_name)
            
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            if blob_client.exists():
                return blob_client.url
            return None
            
        except AzureError as e:
            logger.error(f"Error getting blob URL: {e}")
            return None
    
    def delete_file(self, file_id: str, filename: str) -> bool:
        """
        Delete a file from blob storage.
        
        Args:
            file_id: Unique file identifier
            filename: Original filename
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            blob_name = f"{file_id}/{filename}"
            blob_name = sanitize_filename(blob_name)
            
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            blob_client.delete_blob()
            
            logger.info(f"Deleted blob: {blob_name}")
            return True
            
        except AzureError as e:
            logger.error(f"Error deleting blob: {e}")
            return False

