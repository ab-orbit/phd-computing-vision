"""
Modelo de dados para relatório de conformidade.

Este módulo define os dados necessários para gerar o relatório
de conformidade em formato Markdown (UC4).

EXPLICAÇÃO EDUCATIVA:
O relatório de conformidade é gerado a partir de um template que
será preenchido com dados. Este modelo organiza todos os dados
necessários para o preenchimento do template.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator


class ComplianceReportData(BaseModel):
    """
    Dados para geração do relatório de conformidade (UC4).

    EXPLICAÇÃO EDUCATIVA:
    Este modelo contém todos os dados necessários para preencher
    o template do relatório de conformidade. O template usa
    sintaxe {{variavel}} que será substituída pelos valores aqui.

    Regras verificadas:
    - Mínimo de 2000 palavras
    - Exatamente 8 parágrafos

    O relatório deve informar:
    - Se cada regra está conforme
    - Status geral
    - Diferenças em relação ao esperado
    - Ações recomendadas para correção

    Atributos:
        file_name: Nome do arquivo analisado
        document_id: ID do documento (opcional)
        analysis_datetime: Data e hora da análise
        word_count: Total de palavras encontradas
        paragraph_count: Total de parágrafos encontrados
        words_ok: "Conforme" ou "Não conforme" para regra de palavras
        paragraphs_ok: "Conforme" ou "Não conforme" para regra de parágrafos
        overall_status: "Conforme" ou "Não conforme" geral
        summary_sentence_1: Primeira frase do resumo automático
        summary_sentence_2: Segunda frase do resumo automático
        words_action: Ação recomendada para ajustar palavras
        paragraphs_action: Ação recomendada para ajustar parágrafos
        notes: Observações adicionais (opcional)
    """

    file_name: str = Field(
        ...,
        description="Nome do arquivo analisado",
        examples=["artigo_cientifico.pdf", "documento_pesquisa.pdf"]
    )

    document_id: Optional[str] = Field(
        None,
        description="ID do documento (opcional)",
        examples=["DOC-2025-001", "550e8400-e29b-41d4-a716-446655440000"]
    )

    analysis_datetime: datetime = Field(
        default_factory=datetime.now,
        description="Data e hora da análise"
    )

    word_count: int = Field(
        ...,
        description="Total de palavras no documento",
        ge=0,
        examples=[2534, 1850, 2100]
    )

    paragraph_count: int = Field(
        ...,
        description="Total de parágrafos no documento",
        ge=0,
        examples=[8, 7, 10]
    )

    words_ok: str = Field(
        ...,
        description="Status da regra de palavras: 'Conforme' ou 'Não conforme'",
        pattern="^(Conforme|Não conforme)$"
    )

    paragraphs_ok: str = Field(
        ...,
        description="Status da regra de parágrafos: 'Conforme' ou 'Não conforme'",
        pattern="^(Conforme|Não conforme)$"
    )

    overall_status: str = Field(
        ...,
        description="Status geral: 'Conforme' ou 'Não conforme'",
        pattern="^(Conforme|Não conforme)$"
    )

    summary_sentence_1: str = Field(
        ...,
        description="Primeira frase do resumo (métricas detectadas)",
        examples=[
            "O texto possui 2534 palavras (534 acima do mínimo) e 8 parágrafos (conforme o exigido).",
            "O texto possui 1850 palavras (150 abaixo do mínimo) e 7 parágrafos (1 abaixo do exigido)."
        ]
    )

    summary_sentence_2: str = Field(
        ...,
        description="Segunda frase do resumo (conclusão)",
        examples=[
            "Com base nas regras estabelecidas, o documento está Conforme.",
            "Com base nas regras estabelecidas, o documento está Não conforme."
        ]
    )

    words_action: str = Field(
        ...,
        description="Ação recomendada para ajustar contagem de palavras",
        examples=[
            "Nenhuma ação necessária",
            "Adicionar 150 palavras",
            "Reduzir 100 palavras"
        ]
    )

    paragraphs_action: str = Field(
        ...,
        description="Ação recomendada para ajustar número de parágrafos",
        examples=[
            "Nenhuma ação necessária",
            "Adicionar 1 parágrafo",
            "Fundir/redistribuir para reduzir 2 parágrafos"
        ]
    )

    notes: Optional[str] = Field(
        None,
        description="Observações adicionais sobre o documento",
        examples=[
            "Documento bem estruturado com distribuição equilibrada de conteúdo.",
            "Alguns parágrafos muito longos poderiam ser divididos para melhor legibilidade."
        ]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "file_name": "artigo_cientifico.pdf",
                "document_id": "DOC-2025-001",
                "analysis_datetime": "2025-10-25T14:30:00",
                "word_count": 2534,
                "paragraph_count": 8,
                "words_ok": "Conforme",
                "paragraphs_ok": "Conforme",
                "overall_status": "Conforme",
                "summary_sentence_1": "O texto possui 2534 palavras (534 acima do mínimo) e 8 parágrafos (conforme o exigido).",
                "summary_sentence_2": "Com base nas regras estabelecidas, o documento está Conforme.",
                "words_action": "Nenhuma ação necessária",
                "paragraphs_action": "Nenhuma ação necessária",
                "notes": "Documento bem estruturado."
            }
        }
    )

    @field_validator('words_ok', 'paragraphs_ok', 'overall_status')
    @classmethod
    def validate_status_values(cls, v: str) -> str:
        """
        Valida que os campos de status contêm apenas valores válidos.

        EXPLICAÇÃO EDUCATIVA:
        Field validators são funções que validam campos específicos.
        Aqui verificamos que os status são exatamente "Conforme" ou
        "Não conforme" para manter consistência no relatório.
        """
        if v not in ["Conforme", "Não conforme"]:
            raise ValueError(f"Status deve ser 'Conforme' ou 'Não conforme', recebido: {v}")
        return v

    @classmethod
    def from_analysis(
        cls,
        filename: str,
        word_count: int,
        paragraph_count: int,
        document_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> "ComplianceReportData":
        """
        Cria dados de relatório a partir de contagens.

        EXPLICAÇÃO EDUCATIVA:
        Este factory method calcula automaticamente:
        - Se cada regra está conforme
        - Status geral
        - Diferenças em relação ao esperado
        - Ações recomendadas

        Lógica:
        - Palavras: >= 2000 é conforme
        - Parágrafos: exatamente 8 é conforme
        - Geral: conforme apenas se AMBOS conformes

        Args:
            filename: Nome do arquivo
            word_count: Total de palavras
            paragraph_count: Total de parágrafos
            document_id: ID opcional do documento
            notes: Observações opcionais

        Returns:
            Instância de ComplianceReportData com todos os campos calculados
        """
        # Constantes das regras
        MIN_WORDS = 2000
        EXPECTED_PARAGRAPHS = 8

        # Verificar conformidade de palavras
        words_compliant = word_count >= MIN_WORDS
        words_ok = "Conforme" if words_compliant else "Não conforme"

        # Verificar conformidade de parágrafos
        paragraphs_compliant = paragraph_count == EXPECTED_PARAGRAPHS
        paragraphs_ok = "Conforme" if paragraphs_compliant else "Não conforme"

        # Status geral (ambos devem estar conformes)
        overall_compliant = words_compliant and paragraphs_compliant
        overall_status = "Conforme" if overall_compliant else "Não conforme"

        # Calcular diferenças
        word_diff = word_count - MIN_WORDS
        paragraph_diff = paragraph_count - EXPECTED_PARAGRAPHS

        # Gerar frases do resumo
        # Frase 1: Métricas detectadas
        word_diff_text = ""
        if word_diff > 0:
            word_diff_text = f"{word_diff} acima do mínimo"
        elif word_diff < 0:
            word_diff_text = f"{abs(word_diff)} abaixo do mínimo"
        else:
            word_diff_text = "conforme o mínimo"

        paragraph_diff_text = ""
        if paragraph_diff > 0:
            paragraph_diff_text = f"{paragraph_diff} acima do exigido"
        elif paragraph_diff < 0:
            paragraph_diff_text = f"{abs(paragraph_diff)} abaixo do exigido"
        else:
            paragraph_diff_text = "conforme o exigido"

        summary_sentence_1 = (
            f"O texto possui {word_count} palavras ({word_diff_text}) "
            f"e {paragraph_count} parágrafos ({paragraph_diff_text})."
        )

        # Frase 2: Conclusão
        summary_sentence_2 = f"Com base nas regras estabelecidas, o documento está {overall_status}."

        # Calcular ações recomendadas
        if words_compliant:
            words_action = "Nenhuma ação necessária"
        elif word_diff < 0:
            words_action = f"Adicionar {abs(word_diff)} palavras"
        else:
            words_action = f"Reduzir {word_diff} palavras"

        if paragraphs_compliant:
            paragraphs_action = "Nenhuma ação necessária"
        elif paragraph_diff < 0:
            paragraphs_action = f"Adicionar {abs(paragraph_diff)} parágrafo(s)"
        else:
            paragraphs_action = f"Fundir/redistribuir para reduzir {paragraph_diff} parágrafo(s)"

        return cls(
            file_name=filename,
            document_id=document_id,
            analysis_datetime=datetime.now(),
            word_count=word_count,
            paragraph_count=paragraph_count,
            words_ok=words_ok,
            paragraphs_ok=paragraphs_ok,
            overall_status=overall_status,
            summary_sentence_1=summary_sentence_1,
            summary_sentence_2=summary_sentence_2,
            words_action=words_action,
            paragraphs_action=paragraphs_action,
            notes=notes
        )
