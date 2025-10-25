/**
 * Serviço de integração com API FastAPI
 *
 * Endpoint principal: POST /api/v1/analyze
 * Retorna UC1 + UC2 + UC3 + UC4 em uma única chamada
 */

import axios, { AxiosProgressEvent } from 'axios';
import { AnalysisResult } from '@/types';

/**
 * Configuração base do axios
 *
 * Explicação:
 * - baseURL: URL base da API (variável de ambiente ou fallback localhost:8000)
 * - timeout: 2 minutos (análise pode ser demorada para documentos grandes)
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 120000, // 2 minutos
});

// Interceptor para logging (útil para debug)
api.interceptors.request.use(
  (config) => {
    console.log('[API Request]', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    console.log('[API Response]', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('[API Response Error]', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

/**
 * Analisa um documento completo (UC1 + UC2 + UC3 + UC4)
 *
 * @param file - Arquivo PDF ou imagem (PNG, JPG, JPEG, TIFF)
 * @param onProgress - Callback para progresso do upload (0-100)
 * @returns Resultado completo da análise
 *
 * Explicação:
 * - Endpoint: POST /api/v1/analyze
 * - Processa UC1 + UC2 + UC3 + UC4 em uma única chamada
 * - Frontend adaptado para a estrutura de resposta da API
 */
export async function analyzeDocument(
  file: File,
  onProgress?: (progress: number) => void
): Promise<AnalysisResult> {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post('/api/v1/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent: AxiosProgressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    const backendResponse = response.data;

    // A API /api/v1/analyze retorna todos os UCs completos
    // Apenas precisamos garantir que a estrutura corresponda ao tipo AnalysisResult
    const adaptedResult: AnalysisResult = {
      document_id: backendResponse.document_id,
      filename: backendResponse.filename,
      analyzed_at: backendResponse.analyzed_at,
      processing_time_ms: backendResponse.processing_time_ms,

      // UC1: Classificação
      is_scientific_paper: backendResponse.is_scientific_paper,
      classification_confidence: backendResponse.classification_confidence,

      // UC2: Parágrafos detectados
      paragraphs: backendResponse.paragraphs || [],

      // UC3: Análise textual
      text_analysis: {
        total_words: backendResponse.text_analysis?.total_words || 0,
        unique_words: backendResponse.text_analysis?.unique_words || 0,
        word_frequencies: backendResponse.text_analysis?.word_frequencies || {},
        top_words: backendResponse.text_analysis?.top_words || [],
      },

      // UC4: Conformidade
      compliance: {
        is_compliant: backendResponse.compliance?.is_compliant || false,
        words_compliant: backendResponse.compliance?.words_compliant || false,
        paragraphs_compliant: backendResponse.compliance?.paragraphs_compliant || false,
        word_count: backendResponse.compliance?.word_count || 0,
        paragraph_count: backendResponse.compliance?.paragraph_count || 0,
        word_difference: backendResponse.compliance?.word_difference || 0,
        paragraph_difference: backendResponse.compliance?.paragraph_difference || 0,
        recommended_actions: backendResponse.compliance?.recommended_actions || [],
      },
      compliance_report_markdown: backendResponse.compliance_report_markdown || '',
    };

    return adaptedResult;

  } catch (error: any) {
    // Tratamento de erros HTTP
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data;

      // 400: Formato inválido
      if (status === 400) {
        const errorMsg = data.errors?.[0]?.message || data.detail || 'Formato de arquivo inválido.';
        throw new Error(errorMsg);
      }

      // 415: Formato não suportado
      if (status === 415) {
        throw new Error('Formato de arquivo não suportado. Use PDF, PNG, JPG ou TIFF.');
      }

      // 413: Arquivo muito grande
      if (status === 413) {
        throw new Error('Arquivo muito grande. Tamanho máximo: 10MB.');
      }

      // 500: Erro interno do servidor
      if (status === 500) {
        throw new Error('Erro no servidor. Tente novamente mais tarde.');
      }

      // Outros erros
      const errorMsg = data.errors?.[0]?.message || data.detail || 'Erro desconhecido na análise.';
      throw new Error(errorMsg);
    }

    // Erro de rede ou timeout
    if (error.code === 'ECONNABORTED') {
      throw new Error('Tempo limite excedido. O documento pode ser muito grande.');
    }

    throw new Error('Erro de conexão com a API. Verifique sua internet.');
  }
}

/**
 * Classificação rápida (apenas UC1)
 *
 * @param file - Arquivo PDF ou imagem
 * @returns Resultado da classificação
 *
 * Explicação:
 * - Endpoint mais leve, executa apenas UC1
 * - Útil para validação rápida antes de análise completa
 *
 * Endpoint: POST /api/v1/classify
 */
export async function classifyDocument(file: File) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/v1/classify', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
}

/**
 * Verifica saúde da API
 *
 * @returns Status da API
 *
 * Endpoint: GET /api/v1/health
 */
export async function checkHealth() {
  const response = await api.get('/api/v1/health');
  return response.data;
}

export default api;
