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

# Load environment variables from .env file using python-dotenv
try:
    from dotenv import load_dotenv
    load_dotenv(env_path)
except ImportError:
    print("❌ Error: python-dotenv package not installed")
    print("   Install it with: pip install python-dotenv")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: Could not load .env file: {e}")
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
        # Check OpenAI version first
        try:
            import openai
            openai_version = openai.__version__
            version_parts = [int(x) for x in openai_version.split('.')[:3]]
            if version_parts < [1, 55, 3]:
                print(f"   ⚠️  OpenAI version {openai_version} detected (needs >= 1.55.3)")
                print(f"      Run: pip install --upgrade 'openai>=1.55.3'")
                print(f"      Or run: ./fix_openai.sh")
        except:
            pass
        
        # Remove trailing slash from endpoint if present
        endpoint_clean = endpoint.rstrip('/')
        
        try:
            client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=endpoint_clean
            )
        except TypeError as e:
            if "proxies" in str(e):
                print(f"   ❌ OpenAI SDK compatibility error: {str(e)}")
                print(f"      This is a known issue with OpenAI SDK < 1.55.3")
                print(f"      Solution:")
                print(f"        1. Run: pip install --upgrade 'openai>=1.55.3'")
                print(f"        2. Or run: ./fix_openai.sh")
                print(f"        3. Then run this test again")
                sys.exit(1)
            raise
        
        # Try a simple API call to test connection
        try:
            # Try embeddings endpoint (most reliable test)
            embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
            
            print(f"      Testing connection to: {endpoint_clean}")
            print(f"      Using deployment: {embedding_deployment}")
            
            test_response = client.embeddings.create(
                model=embedding_deployment,
                input="test"
            )
            print(f"   ✅ Azure OpenAI connection successful")
            print(f"      Endpoint: {endpoint_clean}")
            print(f"      Tested with deployment: {embedding_deployment}")
            results["openai"] = True
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            print(f"   ❌ Azure OpenAI connection failed")
            print(f"      Error Type: {error_type}")
            print(f"      Error Message: {error_msg}")
            print(f"      Endpoint: {endpoint_clean}")
            print(f"      API Version: {api_version}")
            print(f"      Deployment: {embedding_deployment}")
            
            # Provide specific troubleshooting based on error type
            if "Connection" in error_msg or "timeout" in error_msg.lower() or "ConnectionError" in error_type:
                print(f"      🔍 Connection Error Troubleshooting:")
                print(f"         1. Verify endpoint format: https://YOUR-RESOURCE.openai.azure.com")
                print(f"         2. Check network connectivity: ping {endpoint_clean.replace('https://', '').split('/')[0]}")
                print(f"         3. Verify firewall/proxy isn't blocking Azure")
                print(f"         4. Ensure endpoint doesn't include /v1 or other paths")
                print(f"         5. Try accessing endpoint in browser (should show Azure OpenAI page)")
            elif "401" in error_msg or "Unauthorized" in error_msg or "Authentication" in error_type:
                print(f"      🔍 Authentication Error Troubleshooting:")
                print(f"         1. Verify API key is correct (check for extra spaces)")
                print(f"         2. Check if API key has expired")
                print(f"         3. Ensure API key has proper permissions")
                print(f"         4. Verify key is from the correct Azure OpenAI resource")
            elif "404" in error_msg or "not found" in error_msg.lower():
                print(f"      🔍 Not Found Error Troubleshooting:")
                print(f"         1. Verify deployment name '{embedding_deployment}' exists in Azure portal")
                print(f"         2. Check if deployment is active and not deleted")
                print(f"         3. Verify deployment is in the same resource as endpoint")
                print(f"         4. Check deployment name spelling (case-sensitive)")
            elif "403" in error_msg or "Forbidden" in error_msg:
                print(f"      🔍 Forbidden Error Troubleshooting:")
                print(f"         1. Check if your Azure subscription has access to OpenAI")
                print(f"         2. Verify deployment permissions and quotas")
                print(f"         3. Check regional availability")
                print(f"         4. Verify resource group permissions")
            else:
                print(f"      🔍 General Troubleshooting:")
                print(f"         1. Check Azure OpenAI resource status in Azure portal")
                print(f"         2. Verify all credentials are correct")
                print(f"         3. Check Azure service health status")
                print(f"         4. Review error details above for specific issues")
except ImportError:
    print("   ❌ openai package not installed.")
    print("      Run: pip install 'openai>=1.55.3'")
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

