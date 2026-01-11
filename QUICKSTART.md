# Quick Start Guide

This guide will help you get both the backend and frontend running quickly.

## Prerequisites

- Python 3.9+ (for backend)
- Node.js 16+ and npm (for frontend)
- Azure account with OpenAI, AI Search, and Blob Storage configured

## Backend Setup

1. **Navigate to project root**:
   ```bash
   cd /Users/wishaur/Documents/python-rag
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your Azure credentials
   ```

5. **Start backend**:
   ```bash
   ./run.sh
   # or
   uvicorn app.main:app --reload
   ```

   Backend will run at: `http://localhost:8000`
   API docs at: `http://localhost:8000/docs`

## Frontend Setup

1. **Navigate to UI directory**:
   ```bash
   cd ui
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start frontend** (in a new terminal):
   ```bash
   npm start
   ```

   Frontend will run at: `http://localhost:3000`

## Using the Application

1. **Open the frontend** in your browser: `http://localhost:3000`

2. **Upload a document**:
   - Go to the "Upload" tab
   - Drag and drop a PDF, DOC, or DOCX file
   - Click "Upload & Index Document"
   - Wait for the upload and indexing to complete

4. **Chat with your documents**:
   - Go to the "Chat" tab
   - Type a question about your uploaded document
   - Press Enter or click send
   - View the answer with source citations

## Troubleshooting

### Backend won't start
- Check that all environment variables in `.env` are set correctly
- Verify Azure credentials are valid
- Check port 8000 is not in use

### Frontend can't connect to backend
- Ensure backend is running on `http://localhost:8000`
- Check the backend status indicator in the UI header
- Verify CORS is enabled in backend (it is by default)

### Upload fails
- Check file size (max 50MB)
- Verify file type is PDF, DOC, or DOCX
- Check backend logs for errors

### Chat returns no results
- Ensure documents have been uploaded successfully
- Check that documents were indexed (check backend logs)

## Next Steps

- Review the full [README.md](README.md) for detailed documentation
- Check [ui/README.md](ui/README.md) for frontend-specific details
- Explore the API documentation at `http://localhost:8000/docs`

