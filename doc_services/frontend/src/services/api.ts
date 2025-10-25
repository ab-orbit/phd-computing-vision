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
 * - NOTA: Backend atual implementa apenas UC1 (classificação)
 * - Endpoint real: POST /classify
 * - UC2, UC3, UC4 retornam dados mock até backend implementar /api/v1/analyze
 * - Frontend preparado para quando backend tiver endpoint completo
 */
export async function analyzeDocument(
  file: File,
  onProgress?: (progress: number) => void
): Promise<AnalysisResult> {
  const formData = new FormData();
  formData.append('file', file);

  // TIFF não é suportado pela API Anthropic (Claude)
  // Detectar TIFF e desabilitar LLM automaticamente
  const isTiff = file.type === 'image/tiff' ||
                 file.name.toLowerCase().endsWith('.tif') ||
                 file.name.toLowerCase().endsWith('.tiff');

  formData.append('use_llm', isTiff ? 'false' : 'true');
  formData.append('include_alternatives', 'true');
  formData.append('extract_metadata', 'true');

  try {
    const response = await api.post('/classify', formData, {
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

    // Adaptar resposta do /classify para formato esperado por AnalysisResult
    const isScientificPaper =
      backendResponse.predicted_type === 'scientific_publication' ||
      backendResponse.predicted_type === 'scientific_report';

    // Construir AnalysisResult adaptado
    const adaptedResult: AnalysisResult = {
      // Metadados do documento
      document_id: backendResponse.request_id,
      filename: backendResponse.document_metadata?.file_name || file.name,
      analyzed_at: backendResponse.timestamp,
      processing_time_ms: backendResponse.document_metadata?.processing_time_ms || 0,

      // UC1: Classificação (dados reais do backend)
      is_scientific_paper: isScientificPaper,
      classification_confidence: backendResponse.probability,

      // UC2: Parágrafos (mock - backend não implementado)
      paragraphs: [],

      // UC3: Análise textual (mock - backend não implementado)
      text_analysis: {
        total_words: 0,
        unique_words: 0,
        word_frequencies: {},
        top_words: [],
      },

      // UC4: Conformidade (mock - backend não implementado)
      compliance: {
        is_compliant: false,
        words_compliant: false,
        paragraphs_compliant: false,
        word_count: 0,
        paragraph_count: 0,
        word_difference: 0,
        paragraph_difference: 0,
        recommended_actions: [
          'UC2, UC3 e UC4 não estão implementados no backend ainda.',
          'Aguarde futuras versões da API.',
        ],
      },
      compliance_report_markdown:
        '**Análise de conformidade não disponível ainda.**\n\n' +
        'UC2 (Detecção de Parágrafos), UC3 (Análise Textual) e UC4 (Conformidade) ' +
        'estão em desenvolvimento no backend.\n\n' +
        'Quando o endpoint `/api/v1/analyze` for implementado, esta análise estará disponível.',
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
