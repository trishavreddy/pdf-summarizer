import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await api.post('/auth/jwt/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },

  register: async (email, password, firstName, lastName) => {
    const response = await api.post('/auth/register', {
      email,
      password,
      first_name: firstName,
      last_name: lastName,
    });
    return response.data;
  },

  getMe: async () => {
    const response = await api.get('/users/me');
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('token');
  },
};

// PDF API
export const pdfAPI = {
  upload: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/pdf/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getDocuments: async (skip = 0, limit = 20) => {
    const response = await api.get(`/pdf/documents?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  getDocument: async (id) => {
    const response = await api.get(`/pdf/documents/${id}`);
    return response.data;
  },

  deleteDocument: async (id) => {
    await api.delete(`/pdf/documents/${id}`);
  },
};

// Summary API
export const summaryAPI = {
  getSummaries: async (skip = 0, limit = 20) => {
    const response = await api.get(`/summaries?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  getSummary: async (id) => {
    const response = await api.get(`/summaries/${id}`);
    return response.data;
  },

  resendEmail: async (id) => {
    const response = await api.post(`/summaries/${id}/resend-email`);
    return response.data;
  },
};

export default api;
