"""
Modelo de dados para resultados de análise de documentos.

Este módulo define a estrutura completa do resultado da análise,
incluindo classificação, parágrafos, análise textual e conformidade.

EXPLICAÇÃO EDUCATIVA:
Este é o modelo de resposta principal do sistema. Ele agrega os
resultados de todos os casos de uso (UC1 a UC4) em uma estrutura
única e coerente que será retornada pela API.
"""

from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict

from .paragraph import Paragraph


class WordFrequency(BaseModel):
    """
    Representa uma palavra e sua frequência no texto.

    EXPLICAÇÃO EDUCATIVA:
    Modelo auxiliar para representar uma entrada de frequência de palavras.
    Usado no resultado de análise textual (UC3).

    Atributos:
        word: A palavra
        count: Número de ocorrências da palavra no texto
    """

    word: str = Field(
        ...,
        description="A palavra",
        examples=["análise", "dados", "sistema"]
    )

    count: int = Field(
        ...,
        description="Número de ocorrências da palavra",
        ge=1,
        examples=[45, 32, 28]
    )


class TextAnalysis(BaseModel):
    """
    Resultado da análise textual (UC3).

    EXPLICAÇÃO EDUCATIVA:
    Esta análise usa técnicas básicas de programação para extrair
    informações estatísticas do texto:
    - Contagem total de palavras
    - Frequência de cada palavra (quantas vezes aparece)
    - Palavras mais comuns (top N)

    Usa estruturas de dados nativas do Python:
    - Counter (collections): para contar eficientemente
    - dict: para armazenar frequências
    - list: para ordenar e pegar top N

    Atributos:
        total_words: Número total de palavras em todos os parágrafos
        unique_words: Número de palavras únicas (vocabulário)
        word_frequencies: Dicionário com frequência de cada palavra
        top_words: Lista das N palavras mais frequentes com suas contagens
    """

    total_words: int = Field(
        ...,
        description="Número total de palavras no documento",
        ge=0,
        examples=[2500, 3200, 1800]
    )

    unique_words: int = Field(
        ...,
        description="Número de palavras únicas (tamanho do vocabulário)",
        ge=0,
        examples=[450, 680, 320]
    )

    word_frequencies: Dict[str, int] = Field(
        ...,
        description="Frequência de cada palavra no documento",
        examples=[{"análise": 45, "dados": 32, "sistema": 28}]
    )

    top_words: List[WordFrequency] = Field(
        ...,
        description="Top 10 palavras mais frequentes",
        examples=[
            [
                WordFrequency(word="análise", count=45),
                WordFrequency(word="dados", count=32),
                WordFrequency(word="sistema", count=28)
            ]
        ]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_words": 2534,
                "unique_words": 678,
                "word_frequencies": {
                    "análise": 45,
                    "dados": 32,
                    "sistema": 28,
                    "pesquisa": 25
                },
                "top_words": [
                    {"word": "análise", "count": 45},
                    {"word": "dados", "count": 32},
                    {"word": "sistema", "count": 28}
                ]
            }
        }
    )


class ComplianceResult(BaseModel):
    """
    Resultado da análise de conformidade (UC4).

    EXPLICAÇÃO EDUCATIVA:
    Verifica se o documento atende às regras estabelecidas:
    - Mínimo de 2000 palavras
    - Exatamente 8 parágrafos

    Para cada regra, calcula:
    - Se está conforme (bool)
    - Diferença do valor esperado (positivo = excesso, negativo = falta)
    - Ação recomendada (adicionar/remover X palavras/parágrafos)

    Atributos:
        is_compliant: True se atende TODAS as regras
        words_compliant: True se tem >= 2000 palavras
        paragraphs_compliant: True se tem exatamente 8 parágrafos
        word_count: Contagem atual de palavras
        paragraph_count: Contagem atual de parágrafos
        word_difference: Diferença em relação ao mínimo (2000)
        paragraph_difference: Diferença em relação ao esperado (8)
        recommended_actions: Lista de ações para ficar conforme
    """

    is_compliant: bool = Field(
        ...,
        description="Indica se o documento está conforme com TODAS as regras"
    )

    words_compliant: bool = Field(
        ...,
        description="Indica se atende ao mínimo de 2000 palavras"
    )

    paragraphs_compliant: bool = Field(
        ...,
        description="Indica se tem exatamente 8 parágrafos"
    )

    word_count: int = Field(
        ...,
        description="Contagem total de palavras",
        ge=0
    )

    paragraph_count: int = Field(
        ...,
        description="Contagem total de parágrafos",
        ge=0
    )

    word_difference: int = Field(
        ...,
        description="Diferença em relação ao mínimo de 2000 palavras (positivo = excesso, negativo = falta)"
    )

    paragraph_difference: int = Field(
        ...,
        description="Diferença em relação a 8 parágrafos (positivo = excesso, negativo = falta)"
    )

    recommended_actions: List[str] = Field(
        ...,
        description="Lista de ações recomendadas para tornar o documento conforme"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "is_compliant": False,
                "words_compliant": False,
                "paragraphs_compliant": True,
                "word_count": 1850,
                "paragraph_count": 8,
                "word_difference": -150,
                "paragraph_difference": 0,
                "recommended_actions": [
                    "Adicionar 150 palavras para atingir o mínimo de 2000"
                ]
            }
        }
    )


class AnalysisResult(BaseModel):
    """
    Resultado completo da análise de documento.

    EXPLICAÇÃO EDUCATIVA:
    Este é o modelo principal que agrega todos os resultados:
    - UC1: Classificação do documento
    - UC2: Parágrafos detectados
    - UC3: Análise textual
    - UC4: Relatório de conformidade

    É o objeto retornado pelo endpoint principal da API.

    Atributos:
        document_id: ID único do documento analisado
        filename: Nome do arquivo
        is_scientific_paper: Resultado da classificação (UC1)
        paragraphs: Lista de parágrafos detectados (UC2)
        text_analysis: Estatísticas textuais (UC3)
        compliance: Análise de conformidade (UC4)
        compliance_report_markdown: Relatório formatado em Markdown (UC4)
        analyzed_at: Timestamp da análise
        processing_time_ms: Tempo total de processamento
    """

    document_id: str = Field(
        ...,
        description="Identificador único do documento",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    filename: str = Field(
        ...,
        description="Nome original do arquivo",
        examples=["artigo_cientifico.pdf"]
    )

    is_scientific_paper: bool = Field(
        ...,
        description="Indica se o documento é um artigo científico (UC1)"
    )

    classification_confidence: Optional[float] = Field(
        None,
        description="Confiança da classificação (0.0 a 1.0)",
        ge=0.0,
        le=1.0
    )

    paragraphs: List[Paragraph] = Field(
        ...,
        description="Lista de parágrafos detectados no documento (UC2)"
    )

    text_analysis: TextAnalysis = Field(
        ...,
        description="Análise estatística do texto (UC3)"
    )

    compliance: ComplianceResult = Field(
        ...,
        description="Resultado da análise de conformidade (UC4)"
    )

    compliance_report_markdown: str = Field(
        ...,
        description="Relatório de conformidade formatado em Markdown (UC4)"
    )

    analyzed_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp da análise"
    )

    processing_time_ms: float = Field(
        ...,
        description="Tempo total de processamento em milissegundos",
        ge=0.0
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "filename": "artigo_cientifico.pdf",
                "is_scientific_paper": True,
                "classification_confidence": 0.95,
                "paragraphs": [
                    {
                        "index": 0,
                        "text": "Este estudo apresenta uma análise...",
                        "word_count": 45,
                        "confidence": 0.98
                    }
                ],
                "text_analysis": {
                    "total_words": 2534,
                    "unique_words": 678,
                    "word_frequencies": {"análise": 45, "dados": 32},
                    "top_words": [{"word": "análise", "count": 45}]
                },
                "compliance": {
                    "is_compliant": True,
                    "words_compliant": True,
                    "paragraphs_compliant": True,
                    "word_count": 2534,
                    "paragraph_count": 8,
                    "word_difference": 534,
                    "paragraph_difference": 0,
                    "recommended_actions": []
                },
                "compliance_report_markdown": "# Relatório de Conformidade...",
                "analyzed_at": "2025-10-25T14:30:00",
                "processing_time_ms": 3452.5
            }
        }
    )
