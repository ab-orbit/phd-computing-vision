"""
Modelo de dados para documentos.

Este módulo define a estrutura de dados para representar documentos
no sistema de análise. Utiliza Pydantic para validação e serialização.

EXPLICAÇÃO EDUCATIVA:
Pydantic é uma biblioteca Python que fornece validação de dados usando type hints.
Principais benefícios:
- Validação automática de tipos de dados
- Conversão automática de tipos quando possível
- Geração de esquemas JSON Schema
- Documentação integrada com docstrings
- Desempenho otimizado com Rust (versão 2.x)
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class DocumentFormat(str, Enum):
    """
    Formatos de documento suportados pelo sistema.

    EXPLICAÇÃO EDUCATIVA:
    Enum (Enumeração) é uma forma de criar constantes nomeadas.
    Benefícios:
    - Evita valores inválidos (type safety)
    - Autocomplete no IDE
    - Documentação clara dos valores aceitos
    - Facilita manutenção (mudar em um só lugar)
    """
    PDF = "pdf"
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    TIFF = "tiff"
    TIF = "tif"


class Document(BaseModel):
    """
    Modelo de documento para processamento.

    Representa um documento carregado no sistema com seus metadados básicos.

    EXPLICAÇÃO EDUCATIVA:
    Este modelo é usado para:
    1. Validar dados de entrada (FastAPI usa isso automaticamente)
    2. Documentar a estrutura esperada
    3. Serializar/deserializar de/para JSON
    4. Garantir consistência em todo o sistema

    Atributos:
        id: Identificador único do documento (UUID)
        filename: Nome original do arquivo
        content: Conteúdo binário do arquivo
        mime_type: Tipo MIME (ex: application/pdf, image/png)
        file_size: Tamanho do arquivo em bytes
        format: Formato do arquivo (enum)
        uploaded_at: Timestamp de quando foi carregado
    """

    id: str = Field(
        ...,
        description="Identificador único do documento (UUID)",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    filename: str = Field(
        ...,
        description="Nome original do arquivo",
        min_length=1,
        max_length=255,
        examples=["artigo_cientifico.pdf", "documento.png"]
    )

    content: bytes = Field(
        ...,
        description="Conteúdo binário do arquivo"
    )

    mime_type: str = Field(
        ...,
        description="Tipo MIME do arquivo",
        examples=["application/pdf", "image/png", "image/tiff"]
    )

    file_size: int = Field(
        ...,
        description="Tamanho do arquivo em bytes",
        gt=0,  # Greater than 0
        examples=[1024000, 2458624]
    )

    format: DocumentFormat = Field(
        ...,
        description="Formato do arquivo"
    )

    uploaded_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp de upload do documento"
    )

    # Configuração do modelo Pydantic
    model_config = ConfigDict(
        # Permite uso de tipos arbitrários (como bytes)
        arbitrary_types_allowed=True,
        # Exemplo para documentação automática
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "filename": "artigo_cientifico.pdf",
                "content": "<binary data>",
                "mime_type": "application/pdf",
                "file_size": 2458624,
                "format": "pdf",
                "uploaded_at": "2025-10-25T14:30:00"
            }
        }
    )

    def get_file_size_human(self) -> str:
        """
        Retorna o tamanho do arquivo em formato legível para humanos.

        EXPLICAÇÃO EDUCATIVA:
        Este método converte bytes para unidades mais legíveis (KB, MB, GB).
        Usa divisão sucessiva por 1024 (base binária).

        Returns:
            String formatada com tamanho e unidade (ex: "2.3 MB")
        """
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
