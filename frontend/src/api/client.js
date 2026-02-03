import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Health check
  healthCheck: async () => {
    const response = await apiClient.get('/');
    return response.data;
  },

  // Generate synthetic data
  generateData: async (params) => {
    const response = await apiClient.post('/api/generate-data', params);
    return response.data;
  },

  // Get proxy scores
  getProxyScores: async () => {
    const response = await apiClient.get('/api/proxy-scores');
    return response.data;
  },

  // Get fragility for a specific metric
  getFragility: async (metric, minCount = 500) => {
    const response = await apiClient.get(`/api/fragility/${metric}`, {
      params: { min_count: minCount }
    });
    return response.data;
  },

  // Get decision simulation results
  getDecisionSimulation: async () => {
    const response = await apiClient.get('/api/decision-simulation');
    return response.data;
  },

  // Get full analysis
  getFullAnalysis: async () => {
    const response = await apiClient.get('/api/full-analysis');
    return response.data;
  },
};

export default apiClient;

