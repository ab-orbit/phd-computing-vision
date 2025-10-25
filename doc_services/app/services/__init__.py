"""
Módulo de serviços do sistema.

Exporta todos os serviços que implementam os casos de uso.

EXPLICAÇÃO EDUCATIVA:
Service Layer contém a lógica de negócio da aplicação:
- UC1: ClassificationService - classificação de documentos
- UC2: ParagraphDetectionService - detecção de parágrafos
- UC3: TextAnalysisService - análise textual
- UC4: ComplianceService - validação de conformidade
- Orchestrator: coordena todos os UCs

Também inclui serviços LLM existentes para outros casos de uso.
"""

# Serviços LLM (existentes)
from app.services.llm_base import (
    BaseLLMService,
    LLMRequest,
    LLMResponse,
    LLMServiceError,
    LLMAPIError,
    LLMResponseError,
    LLMTimeoutError,
)

from app.services.llm_anthropic import (
    AnthropicService,
    create_anthropic_service,
)

# Novos serviços para análise de documentos científicos
from .classification_service import ClassificationService
from .paragraph_service import ParagraphDetectionService
from .text_analysis_service import TextAnalysisService
from .compliance_service import ComplianceService
from .orchestrator import DocumentAnalysisOrchestrator, InvalidDocumentError

__all__ = [
    # Base LLM
    "BaseLLMService",
    "LLMRequest",
    "LLMResponse",
    "LLMServiceError",
    "LLMAPIError",
    "LLMResponseError",
    "LLMTimeoutError",
    # Anthropic
    "AnthropicService",
    "create_anthropic_service",
    # Análise de documentos científicos
    "ClassificationService",
    "ParagraphDetectionService",
    "TextAnalysisService",
    "ComplianceService",
    "DocumentAnalysisOrchestrator",
    "InvalidDocumentError",
]
