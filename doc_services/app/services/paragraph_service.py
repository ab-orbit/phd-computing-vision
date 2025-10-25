"""
Serviço de Detecção de Parágrafos (UC2).

Implementa o caso de uso 2: Detectar parágrafos e quantificar.

EXPLICAÇÃO EDUCATIVA:
Este serviço é responsável por:
1. Receber um documento aprovado (é científico)
2. Usar docling para detectar parágrafos (constraint UC2)
3. Retornar lista de parágrafos com texto e metadados

Esta é a segunda etapa do pipeline de análise.
"""

import logging
from pathlib import Path
from typing import List

from app.models import Paragraph
from app.integrations import DoclingWrapper

logger = logging.getLogger(__name__)


class ParagraphDetectionService:
    """
    Serviço de detecção de parágrafos.

    EXPLICAÇÃO EDUCATIVA:
    Este serviço usa docling (constraint UC2) para:
    - Analisar layout do documento
    - Identificar parágrafos visualmente
    - Extrair texto de cada parágrafo
    - Contar palavras
    - Capturar posição (bounding box)

    Docling é uma biblioteca especializada em análise de
    layout de documentos, capaz de:
    - Processar PDFs e imagens
    - Detectar elementos estruturais
    - Realizar OCR quando necessário
    - Preservar informações de posicionamento
    """

    def __init__(self):
        """Inicializa serviço de detecção de parágrafos."""
        self.docling = DoclingWrapper()
        logger.info("ParagraphDetectionService inicializado")

    def detect_paragraphs(self, file_path: Path) -> List[Paragraph]:
        """
        Detecta e extrai parágrafos de um documento.

        EXPLICAÇÃO EDUCATIVA:
        Este é o método principal do UC2.

        Fluxo:
        1. Usar docling para análise de layout
        2. Filtrar elementos do tipo "parágrafo"
        3. Extrair texto de cada parágrafo
        4. Contar palavras
        5. Capturar metadados (posição, confiança)
        6. Retornar lista estruturada

        Constraint UC2: DEVE usar docling.

        Args:
            file_path: Caminho do arquivo (PDF ou imagem)

        Returns:
            Lista de objetos Paragraph detectados

        Raises:
            RuntimeError: Se detecção falhar
        """
        logger.info(f"Detectando parágrafos em: {file_path.name}")

        try:
            # Usar docling para detectar parágrafos
            paragraphs = self.docling.detect_paragraphs(file_path)

            logger.info(f"Detectados {len(paragraphs)} parágrafos")

            # Log de algumas estatísticas
            if paragraphs:
                total_words = sum(p.word_count for p in paragraphs)
                avg_words = total_words / len(paragraphs)
                logger.debug(
                    f"Total de palavras: {total_words}, "
                    f"Média por parágrafo: {avg_words:.1f}"
                )

            return paragraphs

        except Exception as e:
            logger.error(f"Erro na detecção de parágrafos: {e}")
            raise RuntimeError(f"Falha na detecção de parágrafos: {str(e)}")

    def get_paragraph_count(self, file_path: Path) -> int:
        """
        Retorna apenas a contagem de parágrafos.

        EXPLICAÇÃO EDUCATIVA:
        Método de conveniência para quando só precisamos
        da contagem, não dos parágrafos completos.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Número de parágrafos detectados
        """
        paragraphs = self.detect_paragraphs(file_path)
        return len(paragraphs)

    def get_total_words(self, paragraphs: List[Paragraph]) -> int:
        """
        Calcula total de palavras de uma lista de parágrafos.

        EXPLICAÇÃO EDUCATIVA:
        Método auxiliar que soma word_count de todos os parágrafos.
        Útil para análises posteriores.

        Args:
            paragraphs: Lista de parágrafos

        Returns:
            Total de palavras
        """
        return sum(p.word_count for p in paragraphs)
