#!/usr/bin/env python3
"""
Test script to validate Azure credentials from .env file.
Tests connections to Azure OpenAI, Azure AI Search, and Azure Blob Storage.
"""
import os
import sys
from pathlib import Path

# Load .env file
env_path = Path('.env')
if not env_path.exists():
    print("❌ Error: .env file not found!")
    print("   Please create a .env file from env.example")
    sys.exit(1)

# Load environment variables from .env file
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    
    class EnvSettings(BaseSettings):
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore"
        )
        
        azure_openai_endpoint: str = ""
        azure_openai_api_key: str = ""
        azure_openai_api_version: str = "2024-02-15-preview"
        azure_search_endpoint: str = ""
        azure_search_api_key: str = ""
        azure_blob_connection_string: str = ""
        azure_blob_container_name: str = "documents"
    
    settings = EnvSettings()
    
    # Set environment variables for compatibility
    os.environ["AZURE_OPENAI_ENDPOINT"] = settings.azure_openai_endpoint
    os.environ["AZURE_OPENAI_API_KEY"] = settings.azure_openai_api_key
    os.environ["AZURE_OPENAI_API_VERSION"] = settings.azure_openai_api_version
    os.environ["AZURE_SEARCH_ENDPOINT"] = settings.azure_search_endpoint
    os.environ["AZURE_SEARCH_API_KEY"] = settings.azure_search_api_key
    os.environ["AZURE_BLOB_CONNECTION_STRING"] = settings.azure_blob_connection_string
    os.environ["AZURE_BLOB_CONTAINER_NAME"] = settings.azure_blob_container_name
    
except Exception as e:
    print(f"❌ Error: Could not load .env file: {e}")
    print("   Make sure pydantic-settings is installed: pip install pydantic-settings")
    sys.exit(1)

print("=" * 60)
print("Azure Credentials Validation Test")
print("=" * 60)
print()

# Track results
results = {
    "openai": False,
    "search": False,
    "blob": False
}

# Test Azure OpenAI
print("1. Testing Azure OpenAI...")
try:
    from openai import AzureOpenAI
    
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    if not endpoint or not api_key:
        print("   ❌ Missing AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY")
    elif "your-" in endpoint or "your-" in api_key:
        print("   ❌ Placeholder values detected (contains 'your-')")
    else:
        # Remove trailing slash from endpoint if present
        endpoint_clean = endpoint.rstrip('/')
        
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint_clean
        )
        # Try a simple API call to test connection
        try:
            # Try embeddings endpoint (most reliable test)
            test_response = client.embeddings.create(
                model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002"),
                input="test"
            )
            print(f"   ✅ Azure OpenAI connection successful")
            print(f"      Endpoint: {endpoint_clean}")
            results["openai"] = True
        except Exception as e:
            print(f"   ❌ Azure OpenAI connection failed: {str(e)}")
            print(f"      Endpoint: {endpoint}")
except ImportError:
    print("   ❌ openai package not installed. Run: pip install openai")
except Exception as e:
    print(f"   ❌ Error testing Azure OpenAI: {str(e)}")

print()

# Test Azure AI Search
print("2. Testing Azure AI Search...")
try:
    from azure.search.documents.indexes import SearchIndexClient
    from azure.core.credentials import AzureKeyCredential
    
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    api_key = os.getenv("AZURE_SEARCH_API_KEY")
    
    if not endpoint or not api_key:
        print("   ❌ Missing AZURE_SEARCH_ENDPOINT or AZURE_SEARCH_API_KEY")
    elif "your-" in endpoint or "your-" in api_key:
        print("   ❌ Placeholder values detected (contains 'your-')")
    else:
        client = SearchIndexClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key)
        )
        # Try to list indexes (lightweight check)
        try:
            indexes = list(client.list_indexes())
            print(f"   ✅ Azure AI Search connection successful")
            print(f"      Endpoint: {endpoint}")
            print(f"      Found {len(indexes)} index(es)")
            results["search"] = True
        except Exception as e:
            print(f"   ❌ Azure AI Search connection failed: {str(e)}")
            print(f"      Endpoint: {endpoint}")
except ImportError:
    print("   ❌ azure-search-documents package not installed. Run: pip install azure-search-documents")
except Exception as e:
    print(f"   ❌ Error testing Azure AI Search: {str(e)}")

print()

# Test Azure Blob Storage
print("3. Testing Azure Blob Storage...")
try:
    from azure.storage.blob import BlobServiceClient
    
    connection_string = os.getenv("AZURE_BLOB_CONNECTION_STRING")
    container_name = os.getenv("AZURE_BLOB_CONTAINER_NAME", "documents")
    
    if not connection_string:
        print("   ❌ Missing AZURE_BLOB_CONNECTION_STRING")
    elif "your-" in connection_string:
        print("   ❌ Placeholder values detected (contains 'your-')")
    else:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        # Try to list containers (lightweight check)
        try:
            containers = list(blob_service_client.list_containers())
            print(f"   ✅ Azure Blob Storage connection successful")
            print(f"      Account: {blob_service_client.account_name}")
            print(f"      Found {len(containers)} container(s)")
            
            # Check if target container exists
            container_client = blob_service_client.get_container_client(container_name)
            if container_client.exists():
                print(f"      Container '{container_name}' exists")
            else:
                print(f"      ⚠️  Container '{container_name}' does not exist (will be created automatically)")
            
            results["blob"] = True
        except Exception as e:
            print(f"   ❌ Azure Blob Storage connection failed: {str(e)}")
except ImportError:
    print("   ❌ azure-storage-blob package not installed. Run: pip install azure-storage-blob")
except Exception as e:
    print(f"   ❌ Error testing Azure Blob Storage: {str(e)}")

print()
print("=" * 60)
print("Summary")
print("=" * 60)

total = sum(results.values())
total_tests = len(results)

if total == total_tests:
    print(f"✅ All {total_tests} credential tests passed!")
    sys.exit(0)
elif total > 0:
    print(f"⚠️  {total}/{total_tests} credential tests passed")
    print()
    print("Failed tests:")
    for service, passed in results.items():
        if not passed:
            print(f"   ❌ {service.upper()}")
    sys.exit(1)
else:
    print("❌ All credential tests failed!")
    print()
    print("Please check your .env file and ensure:")
    print("   1. All credentials are set (no placeholder values)")
    print("   2. Credentials are valid and have proper permissions")
    print("   3. Network connectivity to Azure services")
    sys.exit(1)

