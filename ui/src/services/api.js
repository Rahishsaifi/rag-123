/**
 * API client service for communicating with the FastAPI backend.
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Upload a document file.
 * @param {File} file - The file to upload
 * @returns {Promise} Upload response
 */
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * Send a chat message/question.
 * @param {string} question - User question
 * @param {number} topK - Number of results to retrieve (optional)
 * @returns {Promise} Chat response
 */
export const sendChatMessage = async (question, topK = null) => {
  const payload = {
    question,
  };

  if (topK !== null) {
    payload.top_k = topK;
  }

  const response = await apiClient.post('/chat', payload);
  return response.data;
};

/**
 * Check backend health.
 * @returns {Promise} Health check response
 */
export const checkHealth = async () => {
  const response = await axios.get(
    process.env.REACT_APP_API_URL?.replace('/api/v1', '') || 'http://localhost:8000/health'
  );
  return response.data;
};

export default apiClient;

