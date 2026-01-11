"""
Application configuration management using pydantic-settings.
Loads environment variables and provides type-safe configuration.
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_ignore_empty=True,
        populate_by_name=True
    )
    
    azure_openai_endpoint: str = Field(..., description="Azure OpenAI endpoint URL")
    azure_openai_api_key: str = Field(..., description="Azure OpenAI API key")
    azure_openai_embedding_deployment: str = Field(
        default="text-embedding-ada-002",
        description="Azure OpenAI embedding model deployment name"
    )
    azure_openai_chat_deployment: str = Field(
        default="gpt-4",
        description="Azure OpenAI chat model deployment name"
    )
    azure_openai_api_version: str = Field(
        default="2024-02-15-preview",
        description="Azure OpenAI API version"
    )
    
    azure_search_endpoint: str = Field(..., description="Azure AI Search endpoint URL")
    azure_search_api_key: str = Field(..., description="Azure AI Search admin API key")
    azure_search_index_name: str = Field(
        default="rag-index",
        description="Azure AI Search index name"
    )
    
    azure_blob_connection_string: str = Field(
        ...,
        description="Azure Blob Storage connection string"
    )
    azure_blob_container_name: str = Field(
        default="documents",
        description="Azure Blob Storage container name"
    )
    
    chunk_size: int = Field(
        default=1000,
        description="Default chunk size in tokens"
    )
    chunk_overlap: int = Field(
        default=200,
        description="Default chunk overlap in tokens"
    )
    
    top_k_results: int = Field(
        default=5,
        description="Number of top results to retrieve for RAG"
    )
    
    app_name: str = Field(
        default="RAG Backend",
        description="Application name"
    )
    app_version: str = Field(
        default="1.0.0",
        description="Application version"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    
    max_file_size_mb: int = Field(
        default=50,
        description="Maximum file size in MB"
    )
    allowed_file_extensions_str: str = Field(
        default=".pdf,.doc,.docx",
        alias="allowed_file_extensions",
        description="Allowed file extensions"
    )
    
    @property
    def allowed_file_extensions(self) -> list[str]:
        """Parse file extensions from string to list."""
        if not self.allowed_file_extensions_str:
            return [".pdf", ".doc", ".docx"]
        
        if ',' in self.allowed_file_extensions_str:
            extensions = [ext.strip() for ext in self.allowed_file_extensions_str.split(',') if ext.strip()]
            return extensions if extensions else [".pdf", ".doc", ".docx"]
        
        import json
        try:
            parsed = json.loads(self.allowed_file_extensions_str)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass
        
        if self.allowed_file_extensions_str.strip():
            return [self.allowed_file_extensions_str.strip()]
        
        return [".pdf", ".doc", ".docx"]
    
    temp_dir: str = Field(
        default="/tmp/rag-uploads",
        description="Temporary directory for file uploads"
    )


settings = Settings()

