/**
 * File upload component with drag-and-drop support.
 */
import React, { useState, useRef } from 'react';
import { uploadFile } from '../services/api';
import './FileUpload.css';

const FileUpload = ({ onUploadSuccess, onUploadError }) => {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const allowedTypes = ['.pdf', '.doc', '.docx'];
  const maxSizeMB = 50;

  const validateFile = (fileToValidate) => {
    const fileExt = '.' + fileToValidate.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(fileExt)) {
      throw new Error(`File type not allowed. Allowed types: ${allowedTypes.join(', ')}`);
    }

    const fileSizeMB = fileToValidate.size / (1024 * 1024);
    if (fileSizeMB > maxSizeMB) {
      throw new Error(`File size exceeds maximum allowed size of ${maxSizeMB}MB`);
    }

    return true;
  };

  const handleFileSelect = (selectedFile) => {
    setError(null);
    try {
      validateFile(selectedFile);
      setFile(selectedFile);
    } catch (err) {
      setError(err.message);
      if (onUploadError) {
        onUploadError(err.message);
      }
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFileSelect(droppedFile);
    }
  };

  const handleFileInputChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      handleFileSelect(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setIsUploading(true);
    setError(null);
    setUploadProgress('Uploading file...');

    try {
      const response = await uploadFile(file);
      setUploadProgress('Processing document...');
      
      // Simulate processing delay for better UX
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setUploadProgress('Indexing document...');
      await new Promise(resolve => setTimeout(resolve, 1000));

      setUploadProgress(null);
      setFile(null);
      
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      if (onUploadSuccess) {
        onUploadSuccess(response);
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Upload failed';
      setError(errorMessage);
      if (onUploadError) {
        onUploadError(errorMessage);
      }
    } finally {
      setIsUploading(false);
      setUploadProgress(null);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="file-upload-container">
      <h2>Upload Document</h2>
      <p className="upload-description">
        Upload PDF, DOC, or DOCX files to build your knowledge base. 
        You can upload multiple files. Questions will be answered ONLY from these uploaded documents.
      </p>
      
      <div
        className={`drop-zone ${isDragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.doc,.docx"
          onChange={handleFileInputChange}
          style={{ display: 'none' }}
        />
        
        {!file ? (
          <div className="drop-zone-content">
            <div className="upload-icon">📄</div>
            <p className="drop-zone-text">
              Drag and drop a file here, or click to select
            </p>
            <p className="drop-zone-hint">
              Supported formats: PDF, DOC, DOCX (Max {maxSizeMB}MB)
            </p>
          </div>
        ) : (
          <div className="file-info">
            <div className="file-icon">📎</div>
            <div className="file-details">
              <p className="file-name">{file.name}</p>
              <p className="file-size">{formatFileSize(file.size)}</p>
            </div>
            {!isUploading && (
              <button
                className="remove-file-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  handleRemoveFile();
                }}
                aria-label="Remove file"
              >
                ×
              </button>
            )}
          </div>
        )}
      </div>

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {uploadProgress && (
        <div className="upload-progress">
          {uploadProgress}
        </div>
      )}

      <button
        className="upload-button"
        onClick={handleUpload}
        disabled={!file || isUploading}
      >
        {isUploading ? 'Uploading...' : 'Upload & Index Document'}
      </button>
    </div>
  );
};

export default FileUpload;

