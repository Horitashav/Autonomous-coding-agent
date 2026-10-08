import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

// Automatically inject JWT bearer token into every outgoing request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;