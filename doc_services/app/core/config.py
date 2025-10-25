"""
Configurações da aplicação carregadas de variáveis de ambiente.
"""

from typing import Optional, List
from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Configurações da aplicação.

    Todas as configurações são carregadas de variáveis de ambiente
    ou do arquivo .env na raiz do projeto.
    """

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_VERSION: str = "1.0.0"
    API_TITLE: str = "Document Classification API"

    # Model Configuration
    MODEL_PATH: str = "../doclayout-yolo/doclayout_yolo_docstructbench_imgsz1024.pt"
    CONFIDENCE_THRESHOLD: float = 0.2
    IMAGE_SIZE: int = 1024
    DEVICE: str = "cpu"

    # LLM Configuration
    LLM_PROVIDER: str = "anthropic"  # anthropic, openai, google, local
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None

    # LLM Model Selection (modelos mais baratos)
    ANTHROPIC_MODEL: str = "claude-3-5-haiku-20241022"  # Mais barato
    OPENAI_MODEL: str = "gpt-4o-mini"  # Mais barato
    GOOGLE_MODEL: str = "gemini-1.5-flash"  # Mais barato

    # LLM Pricing (USD per 1M tokens) - Preços de outubro 2024
    # Claude 3.5 Haiku
    ANTHROPIC_INPUT_PRICE_PER_1M: float = 1.00
    ANTHROPIC_OUTPUT_PRICE_PER_1M: float = 5.00

    # GPT-4o-mini
    OPENAI_INPUT_PRICE_PER_1M: float = 0.150
    OPENAI_OUTPUT_PRICE_PER_1M: float = 0.600

    # Gemini 1.5 Flash
    GOOGLE_INPUT_PRICE_PER_1M: float = 0.075
    GOOGLE_OUTPUT_PRICE_PER_1M: float = 0.30

    # LLM Behavior
    LLM_MAX_TOKENS: int = 1000
    LLM_TEMPERATURE: float = 0.0
    LLM_TIMEOUT_SECONDS: int = 30
    LLM_MAX_RETRIES: int = 3

    # Cache Configuration
    ENABLE_CACHE: bool = True
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 3600
    CACHE_MAX_SIZE_MB: int = 500

    # File Upload Limits
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: str = "pdf,png,jpg,jpeg,tiff,tif"

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Retorna lista de extensões permitidas."""
        if isinstance(self.ALLOWED_EXTENSIONS, str):
            return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(',')]
        return self.ALLOWED_EXTENSIONS

    # Processing Configuration
    MAX_CONCURRENT_REQUESTS: int = 10
    REQUEST_TIMEOUT_SECONDS: int = 60
    ENABLE_ASYNC_PROCESSING: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "logs/api.log"

    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    # CORS
    CORS_ORIGINS: str = "*"
    CORS_ALLOW_CREDENTIALS: bool = True

    @property
    def cors_origins_list(self) -> List[str]:
        """Retorna lista de origens CORS permitidas."""
        if isinstance(self.CORS_ORIGINS, str):
            if self.CORS_ORIGINS == "*":
                return ["*"]
            return [origin.strip() for origin in self.CORS_ORIGINS.split(',')]
        return self.CORS_ORIGINS

    # Security
    API_KEY_ENABLED: bool = False
    API_KEY: Optional[str] = None
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_PER_MINUTE: int = 60

    # Development
    DEBUG: bool = False
    RELOAD: bool = False

    model_config = ConfigDict(
        extra='ignore',
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna singleton de configurações.

    Cached para evitar recarregar em cada chamada.
    """
    return Settings()


# Exportar instância global
settings = get_settings()
