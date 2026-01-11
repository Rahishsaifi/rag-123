"""
Azure AI Search service for vector storage and similarity search.
"""
from typing import List, Dict, Any, Optional
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchFieldDataType,
    VectorSearch,
    VectorSearchAlgorithmConfiguration,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SearchField
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import AzureError
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class SearchService:
    """Service for interacting with Azure AI Search."""
    
    def __init__(self):
        """Initialize Azure AI Search client."""
        credential = AzureKeyCredential(settings.azure_search_api_key)
        self.index_name = settings.azure_search_index_name
        
        self.index_client = SearchIndexClient(
            endpoint=settings.azure_search_endpoint,
            credential=credential
        )
        
        self.search_client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=self.index_name,
            credential=credential
        )
        
        self._ensure_index()
    
    def _ensure_index(self) -> None:
        """Ensure the search index exists, create if it doesn't."""
        try:
            if not self.index_client.get_index(self.index_name):
                self._create_index()
        except Exception:
            self._create_index()
    
    def _create_index(self) -> None:
        """Create the search index with vector support."""
        try:
            fields = [
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SimpleField(name="file_id", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="filename", type=SearchFieldDataType.String, searchable=True),
                SimpleField(name="chunk_index", type=SearchFieldDataType.Int32, filterable=True),
                SearchField(
                    name="content",
                    type=SearchFieldDataType.String,
                    searchable=True,
                    retrievable=True
                ),
                SearchField(
                    name="content_vector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=1536,  # text-embedding-ada-002 dimension
                    vector_search_profile_name="my-vector-profile"
                ),
                SimpleField(name="metadata", type=SearchFieldDataType.String, retrievable=True)
            ]
            
            vector_search = VectorSearch(
                algorithms=[
                    VectorSearchAlgorithmConfiguration(
                        name="my-hnsw-config",
                        kind="hnsw",
                        parameters=HnswAlgorithmConfiguration(
                            name="my-hnsw-params",
                            m=4,
                            ef_construction=400,
                            ef_search=500,
                            metric="cosine"
                        )
                    )
                ],
                profiles=[
                    VectorSearchProfile(
                        name="my-vector-profile",
                        algorithm_configuration_name="my-hnsw-config"
                    )
                ]
            )
            
            index = SearchIndex(
                name=self.index_name,
                fields=fields,
                vector_search=vector_search
            )
            
            self.index_client.create_index(index)
            
            logger.info(f"Created search index: {self.index_name}")
            
        except AzureError as e:
            logger.error(f"Error creating search index: {e}")
            raise
    
    def upload_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Upload documents to the search index.
        
        Args:
            documents: List of document dictionaries with required fields
            
        Raises:
            AzureError: If upload fails
        """
        if not documents:
            logger.warning("No documents provided for upload")
            return
        
        try:
            search_docs = []
            for doc in documents:
                search_doc = {
                    "id": doc.get("id"),
                    "file_id": doc.get("file_id"),
                    "filename": doc.get("filename"),
                    "chunk_index": doc.get("chunk_index"),
                    "content": doc.get("content"),
                    "content_vector": doc.get("content_vector"),
                    "metadata": str(doc.get("metadata", {}))
                }
                search_docs.append(search_doc)
            
            result = self.search_client.upload_documents(documents=search_docs)
            
            failed = [r for r in result if not r.succeeded]
            if failed:
                logger.error(f"Failed to upload {len(failed)} documents")
                for failure in failed:
                    logger.error(f"Upload error: {failure.error_message}")
                raise Exception(f"Failed to upload {len(failed)} documents")
            
            logger.info(
                f"Uploaded {len(search_docs)} documents to search index",
                extra={"extra_fields": {"num_documents": len(search_docs)}}
            )
            
        except AzureError as e:
            logger.error(f"Error uploading documents to search index: {e}")
            raise
    
    def search(
        self,
        query_vector: List[float],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of search results with content and metadata
        """
        try:
            search_results = self.search_client.search(
                search_text=None,
                vector={
                    "value": query_vector,
                    "k_nearest_neighbors": top_k,
                    "fields": "content_vector"
                },
                top=top_k,
                select=["id", "file_id", "filename", "content", "chunk_index", "metadata"]
            )
            
            results = []
            for result in search_results:
                results.append({
                    "id": result.get("id"),
                    "file_id": result.get("file_id"),
                    "filename": result.get("filename"),
                    "content": result.get("content"),
                    "chunk_index": result.get("chunk_index"),
                    "score": result.get("@search.score"),
                    "metadata": result.get("metadata")
                })
            
            logger.info(
                f"Search returned {len(results)} results",
                extra={
                    "extra_fields": {
                        "top_k": top_k,
                        "num_results": len(results)
                    }
                }
            )
            
            return results
            
        except AzureError as e:
            logger.error(f"Error performing search: {e}")
            raise

