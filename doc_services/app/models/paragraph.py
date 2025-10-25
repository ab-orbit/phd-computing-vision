"""
Modelo de dados para parágrafos detectados em documentos.

Este módulo define a estrutura para representar parágrafos extraídos
pela análise de layout do documento (UC2).

EXPLICAÇÃO EDUCATIVA:
A detecção de parágrafos é fundamental para análise de estrutura de documentos.
O DocLayout-YOLO detecta elementos visuais, e cada parágrafo tem:
- Texto extraído
- Posição no documento (bounding box)
- Ordem sequencial
- Metadados adicionais
"""

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class BoundingBox(BaseModel):
    """
    Coordenadas de uma caixa delimitadora (bounding box).

    EXPLICAÇÃO EDUCATIVA:
    Bounding box é um retângulo que delimita uma região de interesse em uma imagem.
    É definido por 4 coordenadas:
    - x1, y1: canto superior esquerdo
    - x2, y2: canto inferior direito

    Usado para localizar visualmente onde cada parágrafo está no documento.
    """

    x1: float = Field(
        ...,
        description="Coordenada X do canto superior esquerdo",
        ge=0.0
    )

    y1: float = Field(
        ...,
        description="Coordenada Y do canto superior esquerdo",
        ge=0.0
    )

    x2: float = Field(
        ...,
        description="Coordenada X do canto inferior direito",
        ge=0.0
    )

    y2: float = Field(
        ...,
        description="Coordenada Y do canto inferior direito",
        ge=0.0
    )

    def get_width(self) -> float:
        """Calcula a largura da caixa."""
        return self.x2 - self.x1

    def get_height(self) -> float:
        """Calcula a altura da caixa."""
        return self.y2 - self.y1

    def get_area(self) -> float:
        """Calcula a área da caixa."""
        return self.get_width() * self.get_height()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "x1": 100.5,
                "y1": 200.3,
                "x2": 500.8,
                "y2": 350.6
            }
        }
    )


class Paragraph(BaseModel):
    """
    Modelo de parágrafo detectado em documento.

    Representa um parágrafo extraído durante a análise de layout (UC2).

    EXPLICAÇÃO EDUCATIVA:
    Um parágrafo é uma unidade de texto identificada visualmente no documento.
    Contém:
    - index: posição sequencial no documento (1º, 2º, 3º parágrafo...)
    - text: conteúdo textual extraído
    - word_count: número de palavras (útil para análise UC3)
    - bbox: localização visual no documento (opcional)
    - confidence: confiança da detecção pelo modelo

    Atributos:
        index: Índice sequencial do parágrafo (começando em 0)
        text: Texto completo do parágrafo
        word_count: Número de palavras no parágrafo
        bbox: Coordenadas da caixa delimitadora (opcional)
        confidence: Nível de confiança da detecção (0.0 a 1.0)
    """

    index: int = Field(
        ...,
        description="Índice sequencial do parágrafo no documento",
        ge=0,
        examples=[0, 1, 2]
    )

    text: str = Field(
        ...,
        description="Conteúdo textual do parágrafo",
        min_length=1,
        examples=[
            "Este é o primeiro parágrafo do documento.",
            "A metodologia utilizada neste estudo consiste em..."
        ]
    )

    word_count: int = Field(
        ...,
        description="Número de palavras no parágrafo",
        ge=0,
        examples=[8, 42, 156]
    )

    bbox: Optional[BoundingBox] = Field(
        None,
        description="Coordenadas da caixa delimitadora do parágrafo no documento"
    )

    confidence: Optional[float] = Field(
        None,
        description="Nível de confiança da detecção (0.0 a 1.0)",
        ge=0.0,
        le=1.0,
        examples=[0.95, 0.87, 0.76]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "index": 0,
                "text": "A inteligência artificial tem revolucionado diversos setores da sociedade moderna.",
                "word_count": 10,
                "bbox": {
                    "x1": 100.5,
                    "y1": 200.3,
                    "x2": 500.8,
                    "y2": 250.6
                },
                "confidence": 0.95
            }
        }
    )

    @classmethod
    def from_text(cls, text: str, index: int, confidence: Optional[float] = None):
        """
        Cria um parágrafo a partir de texto puro.

        EXPLICAÇÃO EDUCATIVA:
        Este é um factory method (método de fábrica) que simplifica a criação
        de objetos Paragraph. Útil quando temos apenas o texto e queremos
        calcular automaticamente outras propriedades.

        Args:
            text: Texto do parágrafo
            index: Índice do parágrafo
            confidence: Confiança opcional da detecção

        Returns:
            Instância de Paragraph
        """
        # Conta palavras simples (split por espaços)
        # NOTA: Para análise mais robusta, considerar tokenização avançada
        words = text.split()
        word_count = len(words)

        return cls(
            index=index,
            text=text,
            word_count=word_count,
            confidence=confidence
        )
