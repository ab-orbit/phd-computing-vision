/**
 * Tipos TypeScript para aplicação de análise de documentos científicos
 *
 * Representam os modelos de dados do backend FastAPI
 */

// UC1: Classificação
export interface ClassificationResult {
  is_scientific_paper: boolean;
  document_type: string;
  confidence: number;
  alternatives?: ClassificationAlternative[];
  metadata?: DocumentMetadata;
}

export interface ClassificationAlternative {
  type: string;
  confidence: number;
}

export interface DocumentMetadata {
  file_name: string;
  file_size: string;
  processing_time_ms: number;
}

// UC2: Parágrafo detectado
export interface Paragraph {
  index: number;
  text: string;
  word_count: number;
  confidence: number;
  bbox?: BoundingBox;
}

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

// UC3: Análise de texto
export interface TextAnalysis {
  total_words: number;
  word_frequencies: Record<string, number>;
  top_words: [string, number][];
}

// UC4: Relatório de conformidade
export interface ComplianceReport {
  file_name: string;
  document_id?: string;
  analysis_datetime: string;
  word_count: number;
  paragraph_count: number;
  is_compliant: boolean;
  words_compliant: boolean;
  paragraphs_compliant: boolean;
  words_status: string;
  paragraphs_status: string;
  overall_status: string;
  recommended_actions: RecommendedActions;
  report_markdown: string;
}

export interface RecommendedActions {
  words_action: string;
  paragraphs_action: string;
}

// Resultado completo da análise (todos os UCs)
// Mapeia resposta de POST /api/v1/analyze
export interface AnalysisResult {
  // Metadados do documento
  document_id: string;
  filename: string;
  analyzed_at: string;
  processing_time_ms: number;

  // UC1: Classificação
  is_scientific_paper: boolean;
  classification_confidence: number;

  // UC2: Parágrafos detectados
  paragraphs: Paragraph[];

  // UC3: Análise textual
  text_analysis: {
    total_words: number;
    unique_words: number;
    word_frequencies: Record<string, number>;
    top_words: Array<{ word: string; count: number }>;
  };

  // UC4: Conformidade
  compliance: {
    is_compliant: boolean;
    words_compliant: boolean;
    paragraphs_compliant: boolean;
    word_count: number;
    paragraph_count: number;
    word_difference: number;
    paragraph_difference: number;
    recommended_actions: string[];
  };
  compliance_report_markdown: string;
}

// Wrapper para tratamento de erros
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// Estado da análise (para UI)
// Simplificado para refletir única chamada à API
export enum AnalysisStage {
  IDLE = 'idle',           // Aguardando upload
  UPLOADING = 'uploading', // Enviando arquivo
  PROCESSING = 'processing', // API processando (UC1+UC2+UC3+UC4)
  COMPLETED = 'completed', // Análise completa
  ERROR = 'error',         // Erro na análise
}

export interface AnalysisProgress {
  stage: AnalysisStage;
  progress: number; // 0-100
  message: string;
}

// Tipo para upload
export interface FileUpload {
  file: File;
  preview?: string;
}
