/**
 * Serviço para comunicação com a API FastAPI.
 */

import axios from 'axios';
import type {
  Model,
  PromptExample,
  GenerateRequest,
  GenerateResponse,
  HealthStatus
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutos (geração pode demorar)
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  /**
   * Health check da API
   */
  async healthCheck(): Promise<HealthStatus> {
    const response = await api.get<HealthStatus>('/health');
    return response.data;
  },

  /**
   * Lista modelos disponíveis
   */
  async listModels(): Promise<Model[]> {
    const response = await api.get<Model[]>('/api/models');
    return response.data;
  },

  /**
   * Retorna exemplos de prompts
   */
  async getPromptExamples(): Promise<PromptExample[]> {
    const response = await api.get<PromptExample[]>('/api/prompts/examples');
    return response.data;
  },

  /**
   * Gera imagens baseadas no prompt
   */
  async generateImages(request: GenerateRequest): Promise<GenerateResponse> {
    const response = await api.post<GenerateResponse>('/api/generate', request);
    return response.data;
  },
};

export default apiService;
