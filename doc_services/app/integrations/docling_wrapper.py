"""
Wrapper para biblioteca docling - Detecção de parágrafos (UC2).

Este módulo integra a biblioteca docling para análise de layout
e extração de parágrafos de documentos.

EXPLICAÇÃO EDUCATIVA:
Docling é uma biblioteca especializada em análise de layout de documentos.
Principais capacidades:
- Detecção de elementos: parágrafos, títulos, tabelas, figuras
- Extração de texto estruturado
- OCR integrado para imagens
- Suporte a PDF e imagens

Este wrapper:
- Encapsula a complexidade do docling
- Fornece interface simplificada
- Converte resultado para nossos modelos Pydantic
- Trata erros e casos especiais
"""

import logging
from pathlib import Path
from typing import List, Optional
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

from app.models import Paragraph, BoundingBox

logger = logging.getLogger(__name__)


class DoclingWrapper:
    """
    Wrapper para biblioteca docling.

    EXPLICAÇÃO EDUCATIVA:
    Esta classe simplifica o uso do docling para nosso caso de uso específico:
    detectar e extrair parágrafos de documentos.

    O docling retorna uma estrutura complexa com muitos elementos.
    Este wrapper:
    1. Configura docling adequadamente
    2. Executa conversão do documento
    3. Filtra apenas parágrafos
    4. Converte para nosso modelo Paragraph
    5. Adiciona metadados úteis

    Atributos:
        converter: Instância do DocumentConverter do docling
        options: Opções de pipeline para processamento
    """

    def __init__(self):
        """
        Inicializa o wrapper do docling.

        EXPLICAÇÃO EDUCATIVA:
        Configuração do pipeline de processamento:
        - do_ocr: Habilita OCR para imagens sem texto
        - do_table_structure: Detecta estrutura de tabelas
        - table_structure_options: Configurações finas de tabelas
        """
        # Configurar opções de pipeline
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True  # Habilitar OCR para imagens
        pipeline_options.do_table_structure = True  # Detectar tabelas

        # Criar converter com opções
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: pipeline_options,
            }
        )

        logger.info("DoclingWrapper inicializado com OCR e detecção de tabelas")

    def detect_paragraphs(self, file_path: Path) -> List[Paragraph]:
        """
        Detecta e extrai parágrafos de um documento.

        EXPLICAÇÃO EDUCATIVA:
        Processo de detecção:
        1. Converter documento usando docling
        2. Extrair elementos do tipo "text" (parágrafos)
        3. Para cada parágrafo:
           - Extrair texto
           - Contar palavras
           - Extrair bounding box (localização)
           - Calcular índice sequencial
        4. Retornar lista de objetos Paragraph

        Docling detecta vários tipos de elementos:
        - text: parágrafos normais
        - title: títulos e cabeçalhos
        - list: listas
        - table: tabelas
        - figure: figuras e imagens

        Filtramos apenas "text" pois o UC2 pede especificamente parágrafos.

        Args:
            file_path: Caminho do arquivo (PDF ou imagem)

        Returns:
            Lista de parágrafos detectados

        Raises:
            RuntimeError: Se conversão falhar
            FileNotFoundError: Se arquivo não existir
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        logger.info(f"Detectando parágrafos em: {file_path.name}")

        try:
            # Converter documento
            result = self.converter.convert(str(file_path))

            # Extrair parágrafos
            paragraphs = []
            paragraph_index = 0

            # Iterar sobre elementos do documento
            # EXPLICAÇÃO: Na API atual do docling (>=1.0.0), precisamos usar
            # iterate_items() que retorna tuplas (item_key, item_value)
            # onde item_key contém os atributos label, text, prov, etc.
            for item_key, item_value in result.document.iterate_items():
                # Filtrar apenas elementos de texto (parágrafos)
                # item_key.label é um enum DocItemLabel
                if hasattr(item_key, 'label') and str(item_key.label.value) == "text":
                    # Extrair texto
                    if not hasattr(item_key, 'text'):
                        continue

                    text = item_key.text.strip()

                    # Pular parágrafos vazios
                    if not text:
                        continue

                    # Contar palavras
                    # NOTA: Split simples por espaços
                    # Para análise mais robusta, considerar tokenização
                    words = text.split()
                    word_count = len(words)

                    # Extrair bounding box se disponível
                    bbox = None
                    if hasattr(item_key, 'prov') and len(item_key.prov) > 0:
                        # Pegar primeira provenance (localização)
                        prov = item_key.prov[0]
                        if hasattr(prov, 'bbox'):
                            # Converter para nosso modelo BoundingBox
                            bbox = BoundingBox(
                                x1=prov.bbox.l,  # left
                                y1=prov.bbox.t,  # top
                                x2=prov.bbox.r,  # right
                                y2=prov.bbox.b   # bottom
                            )

                    # Criar objeto Paragraph
                    paragraph = Paragraph(
                        index=paragraph_index,
                        text=text,
                        word_count=word_count,
                        bbox=bbox,
                        confidence=1.0  # Docling não fornece confidence
                    )

                    paragraphs.append(paragraph)
                    paragraph_index += 1

            logger.info(f"Detectados {len(paragraphs)} parágrafos")

            return paragraphs

        except Exception as e:
            logger.error(f"Erro ao detectar parágrafos: {e}", exc_info=True)
            raise RuntimeError(f"Erro na detecção de parágrafos: {str(e)}")

    def extract_full_text(self, file_path: Path) -> str:
        """
        Extrai todo o texto do documento.

        EXPLICAÇÃO EDUCATIVA:
        Método auxiliar que retorna todo o texto do documento
        como uma string única. Útil para análises que não precisam
        da estrutura de parágrafos separados.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Texto completo do documento
        """
        paragraphs = self.detect_paragraphs(file_path)
        return "\n\n".join(p.text for p in paragraphs)

    def get_document_stats(self, file_path: Path) -> dict:
        """
        Obtém estatísticas básicas do documento.

        EXPLICAÇÃO EDUCATIVA:
        Método de conveniência que retorna métricas úteis:
        - Número de parágrafos
        - Número total de palavras
        - Tamanho médio dos parágrafos
        - Parágrafos vazios ou muito curtos

        Args:
            file_path: Caminho do arquivo

        Returns:
            Dicionário com estatísticas
        """
        paragraphs = self.detect_paragraphs(file_path)

        if not paragraphs:
            return {
                "num_paragraphs": 0,
                "total_words": 0,
                "avg_words_per_paragraph": 0,
                "min_words": 0,
                "max_words": 0
            }

        word_counts = [p.word_count for p in paragraphs]

        return {
            "num_paragraphs": len(paragraphs),
            "total_words": sum(word_counts),
            "avg_words_per_paragraph": sum(word_counts) / len(word_counts),
            "min_words": min(word_counts),
            "max_words": max(word_counts)
        }
