"""
Módulo de modelos de dados do sistema.

Exporta todos os modelos Pydantic usados no sistema de análise
de documentos científicos.

EXPLICAÇÃO EDUCATIVA:
O arquivo __init__.py torna um diretório em um pacote Python.
Aqui importamos e re-exportamos todos os modelos para facilitar
o uso em outros módulos.

Ao invés de:
    from app.models.document import Document
    from app.models.paragraph import Paragraph

Podemos fazer:
    from app.models import Document, Paragraph
"""

# Modelos de documento
from .document import Document, DocumentFormat

# Modelos de parágrafo
from .paragraph import Paragraph, BoundingBox

# Modelos de resultado de análise
from .analysis_result import (
    AnalysisResult,
    TextAnalysis,
    ComplianceResult,
    WordFrequency
)

# Modelos de relatório de conformidade
from .compliance_report import ComplianceReportData

# Modelos do schema (API)
from .schemas import (
    DocumentType,
    FileFormat,
    LLMProvider,
    ClassificationScore,
    DocumentMetadata,
    LLMMetadata,
    ClassificationResponse,
    ClassificationRequest,
    ErrorDetail,
    ErrorResponse,
    HealthResponse,
)

__all__ = [
    # Documento
    "Document",
    "DocumentFormat",

    # Parágrafo
    "Paragraph",
    "BoundingBox",

    # Análise
    "AnalysisResult",
    "TextAnalysis",
    "ComplianceResult",

    # Relatório
    "ComplianceReportData",

    # API Schemas
    "DocumentType",
    "FileFormat",
    "LLMProvider",
    "ClassificationScore",
    "DocumentMetadata",
    "LLMMetadata",
    "ClassificationResponse",
    "ClassificationRequest",
    "ErrorDetail",
    "ErrorResponse",
    "HealthResponse",
]
