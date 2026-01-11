# RAG Backend

Python RAG backend with FastAPI for document upload and Q&A.

## Setup

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp env.example .env
# Edit .env with your Azure credentials
```

4. Run:
```bash
./run.sh
# or
uvicorn app.main:app --reload
```

API available at: http://localhost:8000
Docs at: http://localhost:8000/docs

## Frontend

```bash
cd ui
npm install
npm start
```

Frontend at: http://localhost:3000

## Environment Variables

Required in `.env`:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_SEARCH_ENDPOINT`
- `AZURE_SEARCH_API_KEY`
- `AZURE_BLOB_CONNECTION_STRING`

Optional: See `env.example` for all options.
