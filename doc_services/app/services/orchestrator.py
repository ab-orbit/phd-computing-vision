"""
Orquestrador de Análise de Documentos.

Este módulo implementa o padrão Orchestrator que coordena
a execução sequencial de todos os casos de uso (UC1 a UC4).

EXPLICAÇÃO EDUCATIVA:
O padrão Orchestrator centraliza a lógica de coordenação:

Benefícios:
- Separa coordenação de lógica de negócio
- Define ordem de execução clara
- Trata erros em ponto centralizado
- Facilita adição de novos passos
- Permite reutilização dos serviços

Fluxo de execução:
UC1 → UC2 → UC3 → UC4

Se UC1 falhar (não é científico), pipeline para.
Demais UCs executam em sequência.
"""

import logging
import time
from pathlib import Path
from typing import Optional
import uuid

from app.models import AnalysisResult
from app.services.classification_service import ClassificationService
from app.services.paragraph_service import ParagraphDetectionService
from app.services.text_analysis_service import TextAnalysisService
from app.services.compliance_service import ComplianceService

logger = logging.getLogger(__name__)


class InvalidDocumentError(Exception):
    """
    Exceção para documento inválido (não é artigo científico).

    EXPLICAÇÃO EDUCATIVA:
    Exceções customizadas permitem:
    - Identificar tipo específico de erro
    - Tratamento diferenciado
    - Mensagens mais claras
    """
    pass


class DocumentAnalysisOrchestrator:
    """
    Orquestrador de análise de documentos.

    EXPLICAÇÃO EDUCATIVA:
    Esta classe coordena o pipeline completo de análise:

    1. UC1: Classificação
       - Verifica se é artigo científico
       - Para se não for

    2. UC2: Detecção de parágrafos
       - Usa docling para extrair parágrafos

    3. UC3: Análise textual
       - Conta palavras
       - Calcula frequências

    4. UC4: Relatório de conformidade
       - Valida regras
       - Gera relatório markdown

    Coordena todos os serviços e agrega resultados.
    """

    def __init__(
        self,
        classification_service: ClassificationService,
        paragraph_service: ParagraphDetectionService,
        text_analysis_service: TextAnalysisService,
        compliance_service: ComplianceService
    ):
        """
        Inicializa orchestrator com serviços.

        EXPLICAÇÃO EDUCATIVA:
        Dependency Injection: serviços são passados como parâmetros.
        Benefícios:
        - Facilita testes (pode passar mocks)
        - Desacopla código
        - Permite diferentes configurações

        Args:
            classification_service: Serviço de classificação (UC1)
            paragraph_service: Serviço de detecção de parágrafos (UC2)
            text_analysis_service: Serviço de análise textual (UC3)
            compliance_service: Serviço de conformidade (UC4)
        """
        self.classification_service = classification_service
        self.paragraph_service = paragraph_service
        self.text_analysis_service = text_analysis_service
        self.compliance_service = compliance_service

        logger.info("DocumentAnalysisOrchestrator inicializado")

    async def analyze_document(
        self,
        file_path: Path,
        document_id: Optional[str] = None
    ) -> AnalysisResult:
        """
        Executa análise completa de um documento.

        EXPLICAÇÃO EDUCATIVA:
        Este é o método principal que orquestra todos os UCs.

        Fluxo sequencial:
        1. UC1: Classificar documento
           - Se não for científico: raise InvalidDocumentError
        2. UC2: Detectar parágrafos
        3. UC3: Analisar texto
        4. UC4: Gerar relatório de conformidade

        Medição de performance:
        - time.time() para medir duração total
        - Importante para monitoramento e otimização

        Args:
            file_path: Caminho do arquivo a analisar
            document_id: ID opcional do documento

        Returns:
            AnalysisResult com todos os resultados agregados

        Raises:
            InvalidDocumentError: Se documento não é artigo científico
            RuntimeError: Se algum passo falhar
        """
        start_time = time.time()

        if document_id is None:
            document_id = str(uuid.uuid4())

        filename = file_path.name

        logger.info(f"Iniciando análise de {filename} (ID: {document_id})")

        try:
            # ================================================================
            # UC1: CLASSIFICAÇÃO
            # ================================================================
            logger.info("[UC1] Classificando documento...")

            is_scientific, confidence = await self.classification_service.is_scientific_paper(
                file_path
            )

            if not is_scientific:
                logger.warning(
                    f"Documento rejeitado: não é artigo científico "
                    f"(confiança: {confidence:.2%})"
                )
                raise InvalidDocumentError(
                    f"Documento '{filename}' não é um artigo científico. "
                    f"Tipo detectado com confiança de {confidence:.2%}."
                )

            logger.info(f"[UC1] Documento aprovado como artigo científico")

            # ================================================================
            # UC2: DETECÇÃO DE PARÁGRAFOS
            # ================================================================
            logger.info("[UC2] Detectando parágrafos...")

            paragraphs = self.paragraph_service.detect_paragraphs(file_path)

            logger.info(f"[UC2] Detectados {len(paragraphs)} parágrafos")

            # ================================================================
            # UC3: ANÁLISE TEXTUAL
            # ================================================================
            logger.info("[UC3] Analisando texto...")

            text_analysis = self.text_analysis_service.analyze_text(
                paragraphs=paragraphs,
                top_n=10
            )

            logger.info(
                f"[UC3] Análise concluída: {text_analysis.total_words} palavras, "
                f"{text_analysis.unique_words} únicas"
            )

            # ================================================================
            # UC4: RELATÓRIO DE CONFORMIDADE
            # ================================================================
            logger.info("[UC4] Gerando relatório de conformidade...")

            # Validar conformidade
            compliance = self.compliance_service.validate_compliance(
                word_count=text_analysis.total_words,
                paragraph_count=len(paragraphs)
            )

            # Gerar relatório markdown
            report_markdown = self.compliance_service.generate_report(
                filename=filename,
                word_count=text_analysis.total_words,
                paragraph_count=len(paragraphs),
                document_id=document_id,
                notes=None
            )

            logger.info(
                f"[UC4] Relatório gerado - Status: "
                f"{'CONFORME' if compliance.is_compliant else 'NÃO CONFORME'}"
            )

            # ================================================================
            # CONSOLIDAR RESULTADOS
            # ================================================================
            processing_time = (time.time() - start_time) * 1000  # em milissegundos

            result = AnalysisResult(
                document_id=document_id,
                filename=filename,
                is_scientific_paper=is_scientific,
                classification_confidence=confidence,
                paragraphs=paragraphs,
                text_analysis=text_analysis,
                compliance=compliance,
                compliance_report_markdown=report_markdown,
                processing_time_ms=processing_time
            )

            logger.info(
                f"Análise concluída com sucesso em {processing_time:.2f}ms"
            )

            return result

        except InvalidDocumentError:
            # Re-raise: documento inválido não é erro do sistema
            raise

        except Exception as e:
            logger.error(f"Erro durante análise: {e}", exc_info=True)
            raise RuntimeError(f"Falha na análise do documento: {str(e)}")

    async def close(self):
        """
        Libera recursos de todos os serviços.

        EXPLICAÇÃO EDUCATIVA:
        Cleanup method que garante liberação de recursos:
        - Fecha conexões HTTP
        - Libera memória
        - Evita resource leaks
        """
        await self.classification_service.close()
        logger.info("Recursos liberados")
