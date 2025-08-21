import axios from 'axios';

const BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api/v1' 
  : 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API functions
const apiClient = {
  // Health check
  health: () => api.get('/health'),
  
  // Document management
  uploadDocuments: (files) => {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    return api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  
  // New single file upload with immediate processing
  uploadAndProcessSingle: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload/process', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  
  getDocuments: (params = {}) => api.get('/documents', { params }),
  getDocument: (id) => api.get(`/documents/${id}`),
  updateDocument: (id, data) => api.put(`/documents/${id}`, data),
  deleteDocument: (id) => api.delete(`/documents/${id}`),
  downloadDocument: (id) => api.get(`/documents/${id}/download`, {
    responseType: 'blob'
  }),
  
  // Search
  searchDocuments: (searchRequest) => api.post('/search', searchRequest),
  getSearchSuggestions: (query) => api.get('/search/suggestions', { 
    params: { q: query } 
  }),
  getRecentDocuments: (limit = 10) => api.get('/search/recent', { 
    params: { limit } 
  }),
  
  // Statistics
  getStats: () => api.get('/stats'),
  getCategories: () => api.get('/categories'),
  
  // Upload status
  getUploadStatus: (documentId) => api.get(`/upload/status/${documentId}`),
  
  // Feedback
  submitFeedback: (feedbackData) => api.post('/feedback', feedbackData),
  
  // Analytics
  getAnalytics: () => api.get('/analytics'),
};

export default apiClient;
