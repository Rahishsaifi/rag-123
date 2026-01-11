# RAG Frontend - React UI

A modern React.js frontend application for the RAG Backend, providing document upload and chat interface capabilities.

## Features

- 📤 **File Upload**: Drag-and-drop file upload with progress indicators
- 💬 **Chat Interface**: Real-time Q&A interface with document sources
- 🎨 **Modern UI**: Clean, responsive design with smooth animations
- 📱 **Responsive**: Works on desktop, tablet, and mobile devices

## Prerequisites

- Node.js 16+ and npm
- Running RAG Backend (FastAPI) on `http://localhost:8000`

## Installation

1. **Navigate to the UI directory**:
   ```bash
   cd ui
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure API endpoint** (optional):
   Create a `.env` file in the `ui` directory:
   ```bash
   REACT_APP_API_URL=http://localhost:8000/api/v1
   ```
   
   If not set, it defaults to `http://localhost:8000/api/v1`.

## Running the Application

1. **Start the development server**:
   ```bash
   npm start
   ```

2. **Open your browser**:
   The app will open at `http://localhost:3000`

## Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build` folder.

## Project Structure

```
ui/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── FileUpload.js      # File upload component
│   │   ├── FileUpload.css
│   │   ├── Chat.js            # Chat interface component
│   │   └── Chat.css
│   ├── services/
│   │   └── api.js             # API client service
│   ├── App.js                 # Main app component
│   ├── App.css
│   ├── index.js               # Entry point
│   └── index.css
├── package.json
└── README.md
```

## Usage

### Uploading Documents

1. Click on the **Upload** tab
2. Drag and drop a file or click to select
3. Supported formats: PDF, DOC, DOCX (Max 50MB)
4. Click **Upload & Index Document**
5. Wait for the upload and indexing to complete

### Chatting with Documents

1. Click on the **Chat** tab
2. Type your question in the input box
3. Press **Enter** or click the send button
4. View the answer along with source documents
5. Continue the conversation with follow-up questions

**Important**: Answers are generated STRICTLY from your uploaded documents only. The system does not use any outside knowledge. If you ask about something not in your documents, it will explicitly state that the information is not available.

## API Integration

The frontend communicates with the backend through the following endpoints:

- `POST /api/v1/upload` - Upload and index documents
- `POST /api/v1/chat` - Send chat messages
- `GET /health` - Check backend health

See `src/services/api.js` for implementation details.

## Features in Detail

### File Upload Component

- Drag-and-drop support
- File type and size validation
- Upload progress indicators
- Error handling and user feedback
- File preview before upload

### Chat Component

- Real-time message display
- Source document attribution
- Relevance scores
- Loading indicators
- Error handling
- Message history
- Auto-scroll to latest message

### Responsive Design

- Desktop: Side-by-side layout with settings panel
- Tablet: Stacked layout
- Mobile: Optimized for small screens

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_API_URL` | `http://localhost:8000/api/v1` | Backend API base URL |

## Troubleshooting

### Backend Connection Issues

- Ensure the FastAPI backend is running on port 8000
- Check the backend status indicator in the header (should show 🟢 Connected)
- Verify CORS settings in the backend if accessing from a different origin

### Upload Fails

- Check file size (max 50MB)
- Verify file type is supported (PDF, DOC, DOCX)
- Check browser console for error messages

### Chat Not Working

- Ensure documents have been uploaded and indexed
- Check backend logs for errors

## Development

### Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests (if configured)

### Code Style

- Follow React best practices
- Use functional components with hooks
- Maintain component separation
- Keep styles component-scoped

## License

This project is provided as-is for production use.

