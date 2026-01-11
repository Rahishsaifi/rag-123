#!/bin/bash

# Installation script that handles tiktoken gracefully

echo "Installing RAG Backend dependencies..."

# Upgrade pip first
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install core dependencies first (required)
echo "Installing core dependencies..."
pip install -q fastapi uvicorn[standard] python-multipart azure-storage-blob azure-search-documents openai pypdf python-docx pydantic-settings pydantic python-dotenv

# Try to install tiktoken (optional)
echo "Attempting to install tiktoken (optional, for better chunking)..."
if pip install -q tiktoken 2>/dev/null; then
    echo "✓ tiktoken installed successfully"
else
    echo "⚠ tiktoken installation failed (this is OK - using fallback chunking)"
    echo "  The app will use character-based chunking instead of token-based chunking."
    echo "  To install tiktoken later, run: pip install tiktoken"
fi

echo ""
echo "Installation complete!"
echo "Note: If tiktoken is not installed, chunking will use character-based method (still works fine)."

