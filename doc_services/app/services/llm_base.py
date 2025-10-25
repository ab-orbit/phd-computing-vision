"""
Service base para integração com LLMs.

Define interface abstrata para diferentes provedores de LLM.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal
from dataclasses import dataclass

from app.models.schemas import LLMMetadata, DocumentType, LLMProvider


@dataclass
class LLMRequest:
    """Requisição para o LLM."""

    prompt: str
    max_tokens: int = 1000
    temperature: float = 0.0
    system_prompt: Optional[str] = None


@dataclass
class LLMResponse:
    """Resposta do LLM."""

    content: str
    input_tokens: int
    output_tokens: int
    model: str
    provider: str
    request_timestamp: datetime
    response_timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class BaseLLMService(ABC):
    """
    Service base para integração com LLMs.

    Implementações específicas devem herdar desta classe
    e implementar os métodos abstratos.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        input_price_per_1m: float,
        output_price_per_1m: float,
        provider: LLMProvider,
        max_retries: int = 3,
        timeout: int = 30
    ):
        """
        Inicializa o service LLM.

        Argumentos:
            api_key: Chave de API do provedor
            model: Nome do modelo a usar
            input_price_per_1m: Preço por 1M tokens de entrada (USD)
            output_price_per_1m: Preço por 1M tokens de saída (USD)
            provider: Provedor do LLM
            max_retries: Máximo de tentativas em caso de erro
            timeout: Timeout em segundos
        """
        self.api_key = api_key
        self.model = model
        self.input_price_per_1m = input_price_per_1m
        self.output_price_per_1m = output_price_per_1m
        self.provider = provider
        self.max_retries = max_retries
        self.timeout = timeout

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Gera resposta do LLM.

        Argumentos:
            request: Requisição com prompt e parâmetros

        Retorna:
            Resposta do LLM com tokens e metadados
        """
        pass

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> Dict[str, Decimal]:
        """
        Calcula custo da requisição.

        Argumentos:
            input_tokens: Número de tokens de entrada
            output_tokens: Número de tokens de saída

        Retorna:
            Dicionário com custos detalhados
        """
        input_cost = Decimal(str(input_tokens * self.input_price_per_1m / 1_000_000))
        output_cost = Decimal(str(output_tokens * self.output_price_per_1m / 1_000_000))
        total_cost = input_cost + output_cost

        return {
            "input_cost_usd": input_cost,
            "output_cost_usd": output_cost,
            "total_cost_usd": total_cost
        }

    def create_llm_metadata(self, response: LLMResponse) -> LLMMetadata:
        """
        Cria metadados estruturados do LLM.

        Argumentos:
            response: Resposta do LLM

        Retorna:
            Objeto LLMMetadata com todos os detalhes
        """
        costs = self.calculate_cost(response.input_tokens, response.output_tokens)
        latency_ms = (
            response.response_timestamp - response.request_timestamp
        ).total_seconds() * 1000

        return LLMMetadata(
            provider=self.provider,
            model_name=response.model,
            model_version=None,
            endpoint=self._get_endpoint_url(),
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            total_tokens=response.input_tokens + response.output_tokens,
            input_cost_usd=costs["input_cost_usd"],
            output_cost_usd=costs["output_cost_usd"],
            total_cost_usd=costs["total_cost_usd"],
            request_timestamp=response.request_timestamp,
            response_timestamp=response.response_timestamp,
            latency_ms=latency_ms,
            cache_hit=False,
            additional_metadata=response.metadata
        )

    @abstractmethod
    def _get_endpoint_url(self) -> str:
        """Retorna URL do endpoint da API."""
        pass

    @staticmethod
    def create_classification_prompt(
        document_name: str,
        available_types: List[str],
        features: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Cria prompt para classificação de documentos.

        Argumentos:
            document_name: Nome do arquivo
            available_types: Lista de tipos disponíveis
            features: Features opcionais extraídas (num_paragraphs, text_density, etc)

        Retorna:
            Prompt formatado para o LLM

        Explicação da abordagem:
            - Prompt estruturado com instruções claras
            - Lista explícita de categorias permitidas
            - Contexto de features quando disponível
            - Formato de saída JSON bem definido
            - Temperatura 0.0 para consistência
        """
        # Formattar tipos disponíveis
        types_list = "\n".join([f"  - {t}" for t in available_types])

        # Preparar informações de features se disponíveis
        features_section = ""
        if features:
            features_section = "\n\n**Informações extraídas do layout:**\n"
            if "num_paragraphs" in features:
                features_section += f"- Número de parágrafos: {features['num_paragraphs']}\n"
            if "text_density" in features:
                features_section += f"- Densidade de texto: {features['text_density']:.2%}\n"
            if "num_figures" in features:
                features_section += f"- Figuras detectadas: {features['num_figures']}\n"
            if "num_tables" in features:
                features_section += f"- Tabelas detectadas: {features['num_tables']}\n"
            if "num_equations" in features:
                features_section += f"- Equações detectadas: {features['num_equations']}\n"

        prompt = f"""Você é um especialista em classificação de documentos. Sua tarefa é classificar o documento fornecido em UMA das categorias abaixo.

**Documento:** {document_name}

**Categorias disponíveis:**
{types_list}

{features_section}

**Instruções:**
1. Analise o nome do arquivo e as informações fornecidas
2. Determine qual categoria melhor descreve este documento
3. Considere os padrões típicos de cada tipo de documento:
   - **email**: Mensagens impressas, 1-4 parágrafos, baixa densidade de texto
   - **scientific_publication**: Artigos científicos, 5+ parágrafos, alta densidade, equações/tabelas
   - **contract**: Contratos legais, 10+ parágrafos, alta densidade, estrutura formal
   - **advertisement**: Anúncios, muitas figuras, pouco texto, 0-1 parágrafos
   - **invoice**: Notas fiscais, tabelas de valores, informações estruturadas
   - **letter**: Cartas formais, 2-5 parágrafos, estrutura simples
   - **memo**: Memorandos, 2-4 parágrafos, comunicação interna
   - **presentation**: Slides, mix de texto e figuras, títulos destacados
   - **resume**: Currículos, listas, informações pessoais e profissionais

4. Retorne APENAS um JSON válido no seguinte formato (sem markdown, sem ```json):

{{
  "predicted_type": "tipo_escolhido",
  "confidence": 0.85,
  "reasoning": "Breve explicação da escolha (max 50 palavras)"
}}

**IMPORTANTE:**
- O campo "predicted_type" deve ser EXATAMENTE um dos tipos listados acima
- O campo "confidence" deve ser um número entre 0.0 e 1.0
- Retorne APENAS o JSON, sem texto adicional antes ou depois
"""
        return prompt

    @staticmethod
    def create_system_prompt() -> str:
        """
        Cria prompt de sistema para o LLM.

        Retorna:
            System prompt que define o comportamento do assistente
        """
        return """Você é um assistente especializado em classificação de documentos.
Você deve analisar documentos e classificá-los em categorias específicas com alta precisão.
Suas respostas devem ser sempre em formato JSON válido, sem formatação markdown.
Seja preciso e objetivo em suas análises."""


class LLMServiceError(Exception):
    """Erro genérico do service LLM."""
    pass


class LLMAPIError(LLMServiceError):
    """Erro de comunicação com a API do LLM."""
    pass


class LLMResponseError(LLMServiceError):
    """Erro ao processar resposta do LLM."""
    pass


class LLMTimeoutError(LLMServiceError):
    """Timeout ao chamar LLM."""
    pass
