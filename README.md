# RAG Backend - Production-Ready Python RAG Pipeline

A production-ready Python backend implementing a Retrieval-Augmented Generation (RAG) pipeline on Azure. This application provides document upload, text extraction, chunking, embedding, vector storage, and chat Q&A capabilities.

## Architecture

The application follows a modular, enterprise-grade architecture:

```
┌─────────────┐
│   FastAPI   │  ← API Layer
└──────┬──────┘
       │
┌──────▼──────────────────┐
│   Service Layer         │
│  - Blob Service         │  ← Azure Blob Storage
│  - Document Parser      │  ← PDF/DOCX parsing
│  - Chunking Service     │  ← Token-aware chunking
│  - Embedding Service    │  ← Azure OpenAI
│  - Search Service       │  ← Azure AI Search
│  - RAG Service          │  ← Orchestration
└─────────────────────────┘
```

### Key Features

- **Document Processing**: Supports PDF, DOC, and DOCX files
- **Token-Aware Chunking**: Uses tiktoken for accurate token-based text splitting
- **Vector Search**: Azure AI Search with vector similarity search
- **Production-Ready**: Comprehensive error handling, logging, and type safety
- **No Framework Lock-in**: Uses official Azure SDKs directly (no LangChain/LlamaIndex)

## Project Structure

```
rag-backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   ├── logging.py         # Structured logging
│   │   └── security.py        # Security utilities
│   ├── api/
│   │   └── v1/
│   │       ├── routes/
│   │       │   ├── upload.py  # File upload endpoint
│   │       │   └── chat.py    # Chat/Q&A endpoint
│   │       └── api.py         # API router aggregation
│   ├── services/
│   │   ├── blob_service.py    # Azure Blob Storage
│   │   ├── document_parser.py # PDF/DOCX parsing
│   │   ├── chunking_service.py # Text chunking
│   │   ├── embedding_service.py # Vector embeddings
│   │   ├── search_service.py  # Azure AI Search
│   │   └── rag_service.py     # RAG orchestration
│   ├── models/
│   │   ├── upload.py          # Upload request/response models
│   │   └── chat.py            # Chat request/response models
│   └── utils/
│       └── file_utils.py       # File utility functions
├── requirements.txt
├── .env.example
├── README.md
└── run.sh
```

## Prerequisites

- Python 3.9 or higher
- Azure account with:
  - Azure OpenAI resource with embedding and chat deployments
  - Azure AI Search service
  - Azure Blob Storage account
- Environment variables configured (see `.env.example`)

## Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   # If .env.example exists, use it. Otherwise use env.example
   cp .env.example .env 2>/dev/null || cp env.example .env
   # Edit .env with your Azure credentials
   ```
   
   Note: If you see `env.example` instead of `.env.example`, you can rename it:
   ```bash
   mv env.example .env.example
   ```

## Configuration

Edit the `.env` file with your Azure credentials:

### Azure OpenAI
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
- `AZURE_OPENAI_API_KEY`: Your API key
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`: Embedding model deployment name
- `AZURE_OPENAI_CHAT_DEPLOYMENT`: Chat model deployment name

### Azure AI Search
- `AZURE_SEARCH_ENDPOINT`: Your Azure AI Search endpoint
- `AZURE_SEARCH_API_KEY`: Admin API key
- `AZURE_SEARCH_INDEX_NAME`: Index name (will be created automatically)

### Azure Blob Storage
- `AZURE_BLOB_CONNECTION_STRING`: Blob storage connection string
- `AZURE_BLOB_CONTAINER_NAME`: Container name (will be created automatically)

## Running the Application

### Using the run script:
```bash
chmod +x run.sh
./run.sh
```

### Or manually:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Health Check
```bash
GET /health
```

### Upload Document
```bash
POST /api/v1/upload
Content-Type: multipart/form-data

Form fields:
- file: PDF/DOC/DOCX file
```

**Example using curl**:
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@document.pdf"
```

**Response**:
```json
{
  "file_id": "file-789",
  "filename": "document.pdf",
  "blob_url": "https://storage.azure.com/...",
  "status": "success",
  "message": "File uploaded and indexed successfully. 15 chunks created."
}
```

### Chat/Q&A
```bash
POST /api/v1/chat
Content-Type: application/json

{
  "question": "What is the main topic of the document?",
  "top_k": 5
}
```

**Example using curl**:
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic?"
  }'
```

**Response**:
```json
{
  "answer": "The main topic is...",
  "sources": [
    {
      "content": "This document discusses...",
      "file_id": "file-789",
      "filename": "document.pdf",
      "chunk_index": 0,
      "score": 0.95
    }
  ],
  "question": "What is the main topic?"
}
```

## How It Works

### Upload Pipeline

1. **File Validation**: Validates file type and size
2. **Blob Storage**: Uploads file to Azure Blob Storage
3. **Text Extraction**: Parses PDF/DOCX to extract text
4. **Chunking**: Splits text into token-aware chunks with overlap
5. **Embedding**: Generates vector embeddings using Azure OpenAI
6. **Indexing**: Stores chunks and embeddings in Azure AI Search

### RAG Pipeline

1. **Query Embedding**: Converts user question to vector embedding
2. **Vector Search**: Searches Azure AI Search for relevant documents
3. **Context Building**: Assembles retrieved chunks into context
4. **Answer Generation**: Uses Azure OpenAI to generate answer STRICTLY from context only
5. **Source Attribution**: Returns answer with source documents

**Important**: The system is configured to answer questions ONLY from uploaded documents. It does not use any outside knowledge or general training data. If information is not in the uploaded documents, the system will explicitly state that the information is not available.

## Error Handling

The application includes comprehensive error handling:

- File validation errors (type, size)
- Azure service errors with retry logic
- Document parsing errors
- Graceful degradation when no results found

## Logging

Structured JSON logging is enabled in production mode:

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "logger": "app.services.rag_service",
  "message": "Processing RAG query",
  "module": "rag_service",
  "function": "query",
  "line": 45,
  "extra_fields": {
    "top_k": 5,
    "question_length": 50
  }
}
```

## Frontend UI

A React.js frontend application is available in the `ui/` directory. See [ui/README.md](ui/README.md) for setup and usage instructions.

### Quick Start (Frontend)

```bash
cd ui
npm install
npm start
```

The UI will be available at `http://localhost:3000` and connects to the backend at `http://localhost:8000`.

## Deployment to Azure App Service

1. **Create Azure App Service**:
   ```bash
   az webapp create --resource-group <rg> --plan <plan> --name <app-name>
   ```

2. **Configure environment variables**:
   ```bash
   az webapp config appsettings set --resource-group <rg> --name <app-name> --settings @.env
   ```

3. **Deploy application**:
   ```bash
   az webapp up --resource-group <rg> --name <app-name>
   ```

## Development

### Running Tests
```bash
# Add your test framework and run tests
pytest tests/
```

### Code Quality
```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## License

This project is provided as-is for production use.

## Support

For issues or questions, please refer to the Azure documentation:
- [Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/)
- [Azure AI Search](https://learn.microsoft.com/azure/search/)
- [Azure Blob Storage](https://learn.microsoft.com/azure/storage/blobs/)

# rag-123
