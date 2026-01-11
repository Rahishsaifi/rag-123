# RAG Backend Startup Script for Windows PowerShell

Write-Host "Starting RAG Backend..." -ForegroundColor Cyan

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
& "venv\Scripts\Activate.ps1"

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found. Please create one from .env.example or env.example" -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Write-Host "Copying .env.example to .env..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
    } elseif (Test-Path "env.example") {
        Write-Host "Copying env.example to .env..." -ForegroundColor Yellow
        Copy-Item "env.example" ".env"
    } else {
        Write-Host "Error: Neither .env.example nor env.example found." -ForegroundColor Red
        exit 1
    }
    Write-Host "Please edit .env with your Azure credentials before continuing." -ForegroundColor Yellow
    exit 1
}

# Install/update dependencies
Write-Host "Installing dependencies..." -ForegroundColor Cyan
Write-Host "Upgrading pip..." -ForegroundColor Gray
pip install --upgrade pip --quiet
Write-Host "Installing core packages..." -ForegroundColor Gray
pip install fastapi uvicorn[standard] python-multipart azure-storage-blob azure-search-documents openai pypdf python-docx pydantic-settings pydantic
Write-Host "Attempting to install tiktoken (optional)..." -ForegroundColor Gray
$tiktokenResult = pip install tiktoken 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "tiktoken skipped - using fallback chunking" -ForegroundColor Yellow
}

# Check environment variables
Write-Host "Checking environment variables..." -ForegroundColor Cyan
$envFile = Get-Content ".env" -ErrorAction SilentlyContinue
$requiredVars = @("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_SEARCH_ENDPOINT", "AZURE_SEARCH_API_KEY", "AZURE_BLOB_CONNECTION_STRING")
$missing = @()

foreach ($var in $requiredVars) {
    $found = $false
    foreach ($line in $envFile) {
        if ($line -match "^$var=") {
            $found = $true
            break
        }
    }
    if (-not $found) {
        $missing += $var
    }
}

if ($missing.Count -gt 0) {
    Write-Host "Warning: Missing required environment variables: $($missing -join ', ')" -ForegroundColor Yellow
    Write-Host "Please configure all required environment variables in .env file" -ForegroundColor Yellow
}

# Create temp directory
$tempDir = "$env:TEMP\rag-uploads"
if (-not (Test-Path $tempDir)) {
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
}
Write-Host "Temporary directory: $tempDir" -ForegroundColor Gray

# Start the application
Write-Host ""
Write-Host "Starting FastAPI application..." -ForegroundColor Green
Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "API docs will be available at: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

