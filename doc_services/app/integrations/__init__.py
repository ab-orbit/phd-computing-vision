"""
Módulo de integrações com serviços externos.

Este módulo contém wrappers e clientes para integração com:
- API externa de classificação de documentos (UC1)
- Biblioteca docling para detecção de parágrafos (UC2)

EXPLICAÇÃO EDUCATIVA:
Integrações são camadas de abstração que encapsulam a comunicação
com serviços/bibliotecas externas. Benefícios:
- Isola dependências externas
- Facilita testes (pode-se mockar as integrações)
- Centraliza configuração de acesso
- Permite trocar implementações facilmente
"""

from .classification_api import ClassificationAPIClient
from .docling_wrapper import DoclingWrapper

__all__ = [
    "ClassificationAPIClient",
    "DoclingWrapper"
]
