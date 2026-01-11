@echo off
REM RAG Backend Startup Script for Windows

echo Starting RAG Backend...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env file exists
if not exist ".env" (
    echo Warning: .env file not found. Please create one from .env.example or env.example
    if exist ".env.example" (
        echo Copying .env.example to .env...
        copy .env.example .env
    ) else if exist "env.example" (
        echo Copying env.example to .env...
        copy env.example .env
    ) else (
        echo Error: Neither .env.example nor env.example found.
        exit /b 1
    )
    echo Please edit .env with your Azure credentials before continuing.
    exit /b 1
)

REM Install/update dependencies
echo Installing dependencies...
if exist "install.sh" (
    REM Try to use install script if available (requires WSL or Git Bash)
    echo Note: install.sh requires WSL or Git Bash. Installing manually...
    pip install --upgrade pip --quiet
    pip install fastapi uvicorn[standard] python-multipart azure-storage-blob azure-search-documents openai pypdf python-docx pydantic-settings pydantic
    echo Attempting to install tiktoken (optional)...
    pip install tiktoken 2>nul || echo tiktoken skipped - using fallback chunking
) else (
    echo Upgrading pip...
    pip install --upgrade pip --quiet
    echo Installing core packages...
    pip install fastapi uvicorn[standard] python-multipart azure-storage-blob azure-search-documents openai pypdf python-docx pydantic-settings pydantic
    echo Attempting to install tiktoken (optional)...
    pip install tiktoken 2>nul || echo tiktoken skipped - using fallback chunking
)

REM Check if all required environment variables are set
echo Checking environment variables...
python -c "import os; from pathlib import Path; env_file = Path('.env'); vars_required = ['AZURE_OPENAI_ENDPOINT', 'AZURE_OPENAI_API_KEY', 'AZURE_SEARCH_ENDPOINT', 'AZURE_SEARCH_API_KEY', 'AZURE_BLOB_CONNECTION_STRING']; missing = [v for v in vars_required if not os.getenv(v)]; exit(1) if missing else exit(0)" 2>nul
if errorlevel 1 (
    echo Warning: Some required environment variables may be missing.
    echo Please configure all required environment variables in .env file
)

REM Create temp directory if it doesn't exist
set TEMP_DIR=%TEMP%\rag-uploads
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"
echo Temporary directory: %TEMP_DIR%

REM Start the application
echo.
echo Starting FastAPI application...
echo API will be available at: http://localhost:8000
echo API docs will be available at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

