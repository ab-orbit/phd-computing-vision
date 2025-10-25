"""
Serviço de Análise de Conformidade (UC4).

Implementa o caso de uso 4: Criar resumo informando se texto está conforme regras.

EXPLICAÇÃO EDUCATIVA:
Este serviço é responsável por:
1. Receber dados de análise (palavras, parágrafos)
2. Validar contra regras:
   - Mínimo 2000 palavras
   - Exatamente 8 parágrafos
3. Calcular diferenças e ações recomendadas
4. Renderizar template markdown do relatório

Constraint UC4: DEVE usar programação básica e template fornecido.
Usa apenas lógica condicional e string.Template para renderização.
"""

import logging
from datetime import datetime
from pathlib import Path
from string import Template
from typing import Optional

from app.models import ComplianceResult, ComplianceReportData

logger = logging.getLogger(__name__)


class ComplianceService:
    """
    Serviço de análise de conformidade.

    EXPLICAÇÃO EDUCATIVA:
    Este serviço implementa validação de regras de negócio:

    Regras fixas:
    - MIN_WORDS = 2000 (mínimo de palavras)
    - EXPECTED_PARAGRAPHS = 8 (exatamente 8 parágrafos)

    Para cada regra, calcula:
    - Se está conforme (bool)
    - Diferença do esperado (int)
    - Ação recomendada (str)

    Status geral é conforme apenas se TODAS as regras conformes.

    Template:
    - Usa string.Template (Python stdlib)
    - Sintaxe ${variavel}
    - Simples e suficiente para UC4
    """

    # Constantes das regras
    MIN_WORDS = 2000
    EXPECTED_PARAGRAPHS = 8

    def __init__(self, template_path: Path):
        """
        Inicializa serviço de conformidade.

        Args:
            template_path: Caminho para arquivo de template markdown
        """
        self.template_path = template_path
        self._template = None
        logger.info("ComplianceService inicializado")

    def _load_template(self) -> Template:
        """
        Carrega template markdown.

        EXPLICAÇÃO EDUCATIVA:
        Lazy loading do template:
        - Carrega apenas quando necessário
        - Cacheia após primeira leitura
        - Usa string.Template (Python stdlib)

        Returns:
            Objeto Template
        """
        if self._template is None:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            self._template = Template(template_content)
            logger.debug(f"Template carregado de {self.template_path}")

        return self._template

    def validate_compliance(
        self,
        word_count: int,
        paragraph_count: int
    ) -> ComplianceResult:
        """
        Valida conformidade com as regras.

        EXPLICAÇÃO EDUCATIVA:
        Este método implementa a lógica de validação:

        1. Verificar cada regra individualmente
        2. Calcular diferenças
        3. Gerar ações recomendadas
        4. Determinar status geral

        Lógica condicional básica (if/else) conforme constraint UC4.

        Args:
            word_count: Total de palavras no documento
            paragraph_count: Total de parágrafos no documento

        Returns:
            Objeto ComplianceResult com resultado da validação
        """
        logger.info(
            f"Validando conformidade: {word_count} palavras, "
            f"{paragraph_count} parágrafos"
        )

        # Validar regra de palavras (>= 2000)
        words_compliant = word_count >= self.MIN_WORDS
        word_difference = word_count - self.MIN_WORDS

        # Validar regra de parágrafos (== 8)
        paragraphs_compliant = paragraph_count == self.EXPECTED_PARAGRAPHS
        paragraph_difference = paragraph_count - self.EXPECTED_PARAGRAPHS

        # Status geral (ambas regras devem estar conformes)
        is_compliant = words_compliant and paragraphs_compliant

        # Gerar ações recomendadas
        recommended_actions = []

        # Ação para palavras
        if not words_compliant:
            if word_difference < 0:
                recommended_actions.append(
                    f"Adicionar {abs(word_difference)} palavras para "
                    f"atingir o mínimo de {self.MIN_WORDS}"
                )
            else:
                # Não deveria acontecer (seria > 2000 mas não conforme)
                # Mas incluímos por completude
                recommended_actions.append(
                    f"Revisar contagem de palavras (detectado: {word_count})"
                )

        # Ação para parágrafos
        if not paragraphs_compliant:
            if paragraph_difference < 0:
                recommended_actions.append(
                    f"Adicionar {abs(paragraph_difference)} parágrafo(s) "
                    f"para atingir exatamente {self.EXPECTED_PARAGRAPHS}"
                )
            else:
                recommended_actions.append(
                    f"Fundir ou redistribuir conteúdo para reduzir "
                    f"{paragraph_difference} parágrafo(s) e ter exatamente "
                    f"{self.EXPECTED_PARAGRAPHS}"
                )

        logger.info(
            f"Resultado: {'CONFORME' if is_compliant else 'NÃO CONFORME'}"
        )

        return ComplianceResult(
            is_compliant=is_compliant,
            words_compliant=words_compliant,
            paragraphs_compliant=paragraphs_compliant,
            word_count=word_count,
            paragraph_count=paragraph_count,
            word_difference=word_difference,
            paragraph_difference=paragraph_difference,
            recommended_actions=recommended_actions
        )

    def generate_report(
        self,
        filename: str,
        word_count: int,
        paragraph_count: int,
        document_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """
        Gera relatório de conformidade em formato Markdown.

        EXPLICAÇÃO EDUCATIVA:
        Este é o método principal do UC4.

        Fluxo:
        1. Validar conformidade (método acima)
        2. Preparar dados para template
        3. Carregar template markdown
        4. Substituir variáveis ${nome} por valores
        5. Retornar markdown formatado

        Usa ComplianceReportData.from_analysis que calcula
        automaticamente todas as strings do template.

        Constraint UC4: Programação básica + template fornecido.

        Args:
            filename: Nome do arquivo analisado
            word_count: Total de palavras
            paragraph_count: Total de parágrafos
            document_id: ID opcional do documento
            notes: Observações opcionais

        Returns:
            Relatório formatado em Markdown
        """
        logger.info(f"Gerando relatório de conformidade para {filename}")

        # Preparar dados do relatório
        report_data = ComplianceReportData.from_analysis(
            filename=filename,
            word_count=word_count,
            paragraph_count=paragraph_count,
            document_id=document_id,
            notes=notes
        )

        # Carregar template
        template = self._load_template()

        # Preparar dicionário de substituição
        # EXPLICAÇÃO: Template.substitute() substitui ${var} por valores
        substitutions = {
            "file_name": report_data.file_name,
            "document_id": report_data.document_id or "N/A",
            "analysis_datetime": report_data.analysis_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "word_count": str(report_data.word_count),
            "paragraph_count": str(report_data.paragraph_count),
            "words_ok": report_data.words_ok,
            "paragraphs_ok": report_data.paragraphs_ok,
            "overall_status": report_data.overall_status,
            "summary_sentence_1": report_data.summary_sentence_1,
            "summary_sentence_2": report_data.summary_sentence_2,
            "words_action": report_data.words_action,
            "paragraphs_action": report_data.paragraphs_action,
            "notes": report_data.notes or "Nenhuma observação adicional."
        }

        # Renderizar template
        report_markdown = template.substitute(substitutions)

        logger.info("Relatório gerado com sucesso")

        return report_markdown
