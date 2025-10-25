"""
Dependências do FastAPI para injeção.

EXPLICAÇÃO EDUCATIVA:
FastAPI suporta Dependency Injection, permitindo:
- Reutilizar código
- Compartilhar conexões/recursos
- Facilitar testes (pode substituir dependências)
"""

import logging
from pathlib import Path
from functools import lru_cache

from app.core.config import get_settings
from app.services import (
    ClassificationService,
    ParagraphDetectionService,
    TextAnalysisService,
    ComplianceService,
    DocumentAnalysisOrchestrator
)

logger = logging.getLogger(__name__)


@lru_cache()
def get_orchestrator() -> DocumentAnalysisOrchestrator:
    """
    Cria e retorna orchestrator de análise (singleton).

    EXPLICAÇÃO EDUCATIVA:
    @lru_cache() garante que apenas uma instância é criada.
    FastAPI reutiliza esta instância em todas as requisições.
    """
    settings = get_settings()

    # Criar serviços
    classification_service = ClassificationService(
        api_url=None,  # Configurar se tiver API externa
        api_key=None,
        use_api=False  # Usar classificador local
    )

    paragraph_service = ParagraphDetectionService()

    text_analysis_service = TextAnalysisService()

    template_path = Path(__file__).parent.parent / "templates" / "compliance_report.md"
    compliance_service = ComplianceService(template_path=template_path)

    # Criar orchestrator
    orchestrator = DocumentAnalysisOrchestrator(
        classification_service=classification_service,
        paragraph_service=paragraph_service,
        text_analysis_service=text_analysis_service,
        compliance_service=compliance_service
    )

    logger.info("Orchestrator criado e pronto para uso")

    return orchestrator
