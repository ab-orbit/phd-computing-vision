"""
Módulo core da aplicação.

Contém configurações, utilitários centrais e inicialização.
"""

from app.core.config import settings, get_settings, Settings

__all__ = [
    "settings",
    "get_settings",
    "Settings",
]
