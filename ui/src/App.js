/**
 * Main App component with navigation between Upload and Chat.
 */
import React, { useState, useEffect } from 'react';
import FileUpload from './components/FileUpload';
import Chat from './components/Chat';
import { checkHealth } from './services/api';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('upload');
  const [backendStatus, setBackendStatus] = useState('checking');
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    // Check backend health on mount
    const checkBackend = async () => {
      try {
        const health = await checkHealth();
        setBackendStatus('connected');
        console.log('Backend health:', health);
      } catch (error) {
        setBackendStatus('disconnected');
        console.error('Backend connection failed:', error);
      }
    };

    checkBackend();
    // Check every 30 seconds
    const interval = setInterval(checkBackend, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleUploadSuccess = (response) => {
    setNotification({
      type: 'success',
      message: response.message || 'File uploaded and indexed successfully!',
    });
    setTimeout(() => setNotification(null), 5000);
    
    // Optionally switch to chat tab after successful upload
    // setActiveTab('chat');
  };

  const handleUploadError = (error) => {
    setNotification({
      type: 'error',
      message: error || 'Upload failed. Please try again.',
    });
    setTimeout(() => setNotification(null), 5000);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>📚 RAG Document Assistant</h1>
          <div className="backend-status">
            <span
              className={`status-indicator ${
                backendStatus === 'connected' ? 'connected' : 'disconnected'
              }`}
            >
              {backendStatus === 'connected' ? '🟢' : '🔴'}
            </span>
            <span className="status-text">
              {backendStatus === 'connected' ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </header>

      <div className="app-container">
        <div className="main-content">
          <div className="tab-navigation">
            <button
              className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
              onClick={() => setActiveTab('upload')}
            >
              📤 Upload
            </button>
            <button
              className={`tab-button ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              💬 Chat
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'upload' && (
              <FileUpload
                onUploadSuccess={handleUploadSuccess}
                onUploadError={handleUploadError}
              />
            )}
            {activeTab === 'chat' && (
              <div className="chat-wrapper">
                <Chat />
              </div>
            )}
          </div>
        </div>
      </div>

      {notification && (
        <div className={`notification ${notification.type}`}>
          {notification.type === 'success' ? '✅' : '⚠️'} {notification.message}
        </div>
      )}
    </div>
  );
}

export default App;

