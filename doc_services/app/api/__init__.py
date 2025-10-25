"""
Módulo de API REST.

Define os endpoints HTTP para o sistema de análise de documentos.

EXPLICAÇÃO EDUCATIVA:
Este módulo contém:
- routes.py: Definição dos endpoints
- dependencies.py: Dependências injetáveis do FastAPI
"""

from .routes import router

__all__ = ["router"]
