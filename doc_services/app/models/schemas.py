"""
Modelos Pydantic para API de Classificação de Documentos.

Define as estruturas de entrada e saída para os endpoints da API,
incluindo validação de dados e serialização.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, ConfigDict
from decimal import Decimal


class DocumentType(str, Enum):
    """Tipos de documentos suportados pelo classificador."""

    ADVERTISEMENT = "advertisement"
    BUDGET = "budget"
    EMAIL = "email"
    FILE_FOLDER = "file_folder"
    FORM = "form"
    HANDWRITTEN = "handwritten"
    INVOICE = "invoice"
    LETTER = "letter"
    MEMO = "memo"
    NEWS_ARTICLE = "news_article"
    PRESENTATION = "presentation"
    QUESTIONNAIRE = "questionnaire"
    RESUME = "resume"
    SCIENTIFIC_PUBLICATION = "scientific_publication"
    SCIENTIFIC_REPORT = "scientific_report"
    SPECIFICATION = "specification"
    CONTRACT = "contract"  # Adicionado conforme requisito


class FileFormat(str, Enum):
    """Formatos de arquivo suportados."""

    PDF = "pdf"
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    TIFF = "tiff"
    TIF = "tif"


class LLMProvider(str, Enum):
    """Provedores de LLM suportados."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    LOCAL = "local"


# ============================================================================
# Modelos de Saída (Response)
# ============================================================================

class ClassificationScore(BaseModel):
    """
    Score de classificação para um tipo de documento.

    Representa a probabilidade de um documento pertencer a uma categoria específica.
    """

    document_type: DocumentType = Field(
        ...,
        description="Tipo do documento"
    )

    probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Probabilidade de pertencer a esta categoria (0.0 - 1.0)"
    )

    confidence: str = Field(
        ...,
        description="Nível de confiança: 'high' (>0.8), 'medium' (0.5-0.8), 'low' (<0.5)"
    )

    @validator('confidence', always=True)
    def set_confidence_level(cls, v, values):
        """Calcula nível de confiança baseado na probabilidade."""
        if 'probability' in values:
            prob = values['probability']
            if prob >= 0.8:
                return 'high'
            elif prob >= 0.5:
                return 'medium'
            else:
                return 'low'
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document_type": "scientific_publication",
                "probability": 0.87,
                "confidence": "high"
            }
        }
    )


class DocumentMetadata(BaseModel):
    """
    Metadados do documento analisado.

    Contém informações sobre o arquivo enviado e características detectadas.
    """

    file_name: str = Field(
        ...,
        description="Nome original do arquivo"
    )

    file_format: FileFormat = Field(
        ...,
        description="Formato do arquivo (pdf, png, jpg, etc)"
    )

    file_size_bytes: int = Field(
        ...,
        ge=0,
        description="Tamanho do arquivo em bytes"
    )

    file_size_human: str = Field(
        ...,
        description="Tamanho do arquivo em formato legível (ex: '2.5 MB')"
    )

    mime_type: str = Field(
        ...,
        description="MIME type do arquivo"
    )

    # Metadados extraídos da análise
    num_pages: Optional[int] = Field(
        None,
        ge=1,
        description="Número de páginas (para PDFs)"
    )

    image_dimensions: Optional[Dict[str, int]] = Field(
        None,
        description="Dimensões da imagem (width, height) se aplicável"
    )

    num_paragraphs: Optional[int] = Field(
        None,
        ge=0,
        description="Número de parágrafos detectados"
    )

    text_density: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Densidade de texto no documento (0.0 - 1.0)"
    )

    num_figures: Optional[int] = Field(
        None,
        ge=0,
        description="Número de figuras detectadas"
    )

    num_tables: Optional[int] = Field(
        None,
        ge=0,
        description="Número de tabelas detectadas"
    )

    num_equations: Optional[int] = Field(
        None,
        ge=0,
        description="Número de equações detectadas"
    )

    processing_time_ms: float = Field(
        ...,
        ge=0,
        description="Tempo de processamento em milissegundos"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "file_name": "research_paper.pdf",
                "file_format": "pdf",
                "file_size_bytes": 2458624,
                "file_size_human": "2.3 MB",
                "mime_type": "application/pdf",
                "num_pages": 12,
                "num_paragraphs": 45,
                "text_density": 0.68,
                "num_figures": 8,
                "num_tables": 3,
                "num_equations": 15,
                "processing_time_ms": 3452.5
            }
        }
    )


class LLMMetadata(BaseModel):
    """
    Metadados do serviço LLM utilizado.

    Rastreia uso de tokens, custos e informações técnicas da inferência.
    """

    provider: LLMProvider = Field(
        ...,
        description="Provedor do serviço LLM"
    )

    model_name: str = Field(
        ...,
        description="Nome do modelo utilizado (ex: 'claude-3-opus', 'gpt-4')"
    )

    model_version: Optional[str] = Field(
        None,
        description="Versão específica do modelo"
    )

    endpoint: str = Field(
        ...,
        description="Endpoint utilizado para a inferência"
    )

    # Tokens
    input_tokens: int = Field(
        ...,
        ge=0,
        description="Número de tokens de entrada processados"
    )

    output_tokens: int = Field(
        ...,
        ge=0,
        description="Número de tokens de saída gerados"
    )

    total_tokens: int = Field(
        ...,
        ge=0,
        description="Total de tokens (entrada + saída)"
    )

    # Custos
    input_cost_usd: Decimal = Field(
        ...,
        ge=0,
        description="Custo dos tokens de entrada em USD",
        decimal_places=6
    )

    output_cost_usd: Decimal = Field(
        ...,
        ge=0,
        description="Custo dos tokens de saída em USD",
        decimal_places=6
    )

    total_cost_usd: Decimal = Field(
        ...,
        ge=0,
        description="Custo total em USD",
        decimal_places=6
    )

    # Metadados temporais
    request_timestamp: datetime = Field(
        ...,
        description="Timestamp da requisição ao LLM"
    )

    response_timestamp: datetime = Field(
        ...,
        description="Timestamp da resposta do LLM"
    )

    latency_ms: float = Field(
        ...,
        ge=0,
        description="Latência da requisição em milissegundos"
    )

    # Informações adicionais
    cache_hit: bool = Field(
        default=False,
        description="Indica se a resposta veio de cache"
    )

    additional_metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Metadados adicionais específicos do provedor"
    )

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "provider": "anthropic",
                "model_name": "claude-3-sonnet-20240229",
                "model_version": "2024-02-29",
                "endpoint": "https://api.anthropic.com/v1/messages",
                "input_tokens": 1250,
                "output_tokens": 450,
                "total_tokens": 1700,
                "input_cost_usd": "0.003750",
                "output_cost_usd": "0.006750",
                "total_cost_usd": "0.010500",
                "request_timestamp": "2025-10-25T14:30:00Z",
                "response_timestamp": "2025-10-25T14:30:03Z",
                "latency_ms": 3250.5,
                "cache_hit": False
            }
        }
    )


class ClassificationResponse(BaseModel):
    """
    Resposta completa da API de classificação.

    Contém o resultado da classificação, alternativas, e metadados.
    """

    # Resultado principal
    predicted_type: DocumentType = Field(
        ...,
        description="Tipo de documento predito com maior probabilidade"
    )

    probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Probabilidade do tipo predito"
    )

    confidence: str = Field(
        ...,
        description="Nível de confiança da predição"
    )

    # Alternativas (top 3)
    alternatives: List[ClassificationScore] = Field(
        ...,
        min_length=0,
        max_length=3,
        description="Top 3 tipos alternativos com suas probabilidades"
    )

    # Metadados
    document_metadata: DocumentMetadata = Field(
        ...,
        description="Metadados do documento analisado"
    )

    llm_metadata: Optional[LLMMetadata] = Field(
        None,
        description="Metadados do serviço LLM (se aplicável)"
    )

    # Informações gerais
    request_id: str = Field(
        ...,
        description="ID único da requisição para rastreamento"
    )

    timestamp: datetime = Field(
        ...,
        description="Timestamp da resposta"
    )

    api_version: str = Field(
        default="1.0.0",
        description="Versão da API"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "predicted_type": "scientific_publication",
                "probability": 0.87,
                "confidence": "high",
                "alternatives": [
                    {
                        "document_type": "scientific_report",
                        "probability": 0.08,
                        "confidence": "low"
                    },
                    {
                        "document_type": "presentation",
                        "probability": 0.03,
                        "confidence": "low"
                    },
                    {
                        "document_type": "specification",
                        "probability": 0.02,
                        "confidence": "low"
                    }
                ],
                "document_metadata": {
                    "file_name": "research_paper.pdf",
                    "file_format": "pdf",
                    "file_size_bytes": 2458624,
                    "file_size_human": "2.3 MB",
                    "mime_type": "application/pdf",
                    "num_pages": 12,
                    "num_paragraphs": 45,
                    "text_density": 0.68,
                    "num_figures": 8,
                    "num_tables": 3,
                    "num_equations": 15,
                    "processing_time_ms": 3452.5
                },
                "llm_metadata": {
                    "provider": "anthropic",
                    "model_name": "claude-3-sonnet-20240229",
                    "endpoint": "https://api.anthropic.com/v1/messages",
                    "input_tokens": 1250,
                    "output_tokens": 450,
                    "total_tokens": 1700,
                    "input_cost_usd": "0.010500",
                    "output_cost_usd": "0.006750",
                    "total_cost_usd": "0.017250",
                    "request_timestamp": "2025-10-25T14:30:00Z",
                    "response_timestamp": "2025-10-25T14:30:03Z",
                    "latency_ms": 3250.5,
                    "cache_hit": False
                },
                "request_id": "req_abc123def456",
                "timestamp": "2025-10-25T14:30:03.5Z",
                "api_version": "1.0.0"
            }
        }
    )


# ============================================================================
# Modelos de Entrada (Request)
# ============================================================================

class ClassificationRequest(BaseModel):
    """
    Requisição de classificação de documento.

    Nota: O arquivo é enviado via multipart/form-data separadamente.
    Este modelo representa campos adicionais opcionais.
    """

    use_llm: bool = Field(
        default=False,
        description="Se True, usa LLM para análise adicional além do modelo base"
    )

    include_alternatives: bool = Field(
        default=True,
        description="Se True, retorna top 3 alternativas além da predição principal"
    )

    extract_metadata: bool = Field(
        default=True,
        description="Se True, extrai metadados detalhados do documento"
    )

    confidence_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Threshold mínimo de confiança para aceitar predição"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "use_llm": True,
                "include_alternatives": True,
                "extract_metadata": True,
                "confidence_threshold": 0.7
            }
        }
    )


# ============================================================================
# Modelos de Erro
# ============================================================================

class ErrorDetail(BaseModel):
    """Detalhe de erro estruturado."""

    code: str = Field(
        ...,
        description="Código do erro"
    )

    message: str = Field(
        ...,
        description="Mensagem descritiva do erro"
    )

    field: Optional[str] = Field(
        None,
        description="Campo relacionado ao erro (se aplicável)"
    )

    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Informações adicionais sobre o erro"
    )


class ErrorResponse(BaseModel):
    """Resposta de erro da API."""

    error: bool = Field(
        default=True,
        description="Indica que ocorreu um erro"
    )

    error_type: str = Field(
        ...,
        description="Tipo do erro (validation, processing, etc)"
    )

    errors: List[ErrorDetail] = Field(
        ...,
        description="Lista de erros ocorridos"
    )

    request_id: str = Field(
        ...,
        description="ID da requisição para rastreamento"
    )

    timestamp: datetime = Field(
        ...,
        description="Timestamp do erro"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": True,
                "error_type": "validation",
                "errors": [
                    {
                        "code": "INVALID_FILE_FORMAT",
                        "message": "Formato de arquivo não suportado",
                        "field": "file",
                        "details": {
                            "supported_formats": ["pdf", "png", "jpg", "tiff"]
                        }
                    }
                ],
                "request_id": "req_abc123def456",
                "timestamp": "2025-10-25T14:30:00Z"
            }
        }
    )


# ============================================================================
# Modelos de Status/Health
# ============================================================================

class HealthResponse(BaseModel):
    """Resposta do endpoint de health check."""

    status: str = Field(
        ...,
        description="Status do serviço (healthy, degraded, unhealthy)"
    )

    version: str = Field(
        ...,
        description="Versão da API"
    )

    uptime_seconds: float = Field(
        ...,
        ge=0,
        description="Tempo de atividade em segundos"
    )

    models_loaded: bool = Field(
        ...,
        description="Indica se os modelos estão carregados"
    )

    llm_available: bool = Field(
        ...,
        description="Indica se o serviço LLM está disponível"
    )

    timestamp: datetime = Field(
        ...,
        description="Timestamp do health check"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "uptime_seconds": 86400.5,
                "models_loaded": True,
                "llm_available": True,
                "timestamp": "2025-10-25T14:30:00Z"
            }
        }
    )
