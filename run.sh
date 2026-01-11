#!/bin/bash

# RAG Backend Startup Script

echo "Starting RAG Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Please create one from .env.example or env.example"
    if [ -f ".env.example" ]; then
        echo "Copying .env.example to .env..."
        cp .env.example .env
    elif [ -f "env.example" ]; then
        echo "Copying env.example to .env..."
        cp env.example .env
    else
        echo "Error: Neither .env.example nor env.example found."
        exit 1
    fi
    echo "Please edit .env with your Azure credentials before continuing."
    exit 1
fi

# Install/update dependencies
echo "Installing dependencies..."
if [ -f "install.sh" ]; then
    ./install.sh
else
    echo "Upgrading pip..."
    pip install --upgrade pip --quiet
    echo "Installing core packages..."
    pip install -q fastapi uvicorn[standard] python-multipart azure-storage-blob azure-search-documents openai pypdf python-docx pydantic-settings pydantic python-dotenv
    echo "Attempting to install tiktoken (optional)..."
    pip install -q tiktoken 2>/dev/null || echo "⚠ tiktoken skipped (using fallback chunking)"
fi

# Check if all required environment variables are set
echo "Checking environment variables..."
python3 -c "
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file using python-dotenv
env_file = Path('.env')
if env_file.exists():
    load_dotenv(env_file)

required_vars = [
    'AZURE_OPENAI_ENDPOINT',
    'AZURE_OPENAI_API_KEY',
    'AZURE_SEARCH_ENDPOINT',
    'AZURE_SEARCH_API_KEY',
    'AZURE_BLOB_CONNECTION_STRING'
]

missing = [var for var in required_vars if not os.getenv(var)]
if missing:
    print(f'Error: Missing required environment variables: {', '.join(missing)}')
    sys.exit(1)
else:
    print('All required environment variables are set.')
"

if [ $? -ne 0 ]; then
    echo "Please configure all required environment variables in .env file"
    exit 1
fi

# Create temp directory if it doesn't exist
TEMP_DIR=${TEMP_DIR:-/tmp/rag-uploads}
mkdir -p "$TEMP_DIR"
echo "Temporary directory: $TEMP_DIR"

# Start the application
echo "Starting FastAPI application..."
echo "API will be available at: http://localhost:8000"
echo "API docs will be available at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

