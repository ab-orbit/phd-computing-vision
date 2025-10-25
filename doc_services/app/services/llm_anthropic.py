"""
Service para integração com Anthropic Claude.

Implementa comunicação com a API da Anthropic usando SDK oficial.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
import asyncio

from anthropic import AsyncAnthropic, APIError, APITimeoutError
import httpx

from app.services.llm_base import (
    BaseLLMService,
    LLMRequest,
    LLMResponse,
    LLMAPIError,
    LLMResponseError,
    LLMTimeoutError
)
from app.models.schemas import LLMProvider


class AnthropicService(BaseLLMService):
    """
    Service para integração com Anthropic Claude.

    Utiliza o SDK oficial da Anthropic para comunicação com a API.
    Suporta modelos Claude 3.5 Haiku (mais barato) e outros.

    Preços (outubro 2024):
    - Claude 3.5 Haiku: $1.00/1M input, $5.00/1M output
    - Claude 3.5 Sonnet: $3.00/1M input, $15.00/1M output
    - Claude 3 Opus: $15.00/1M input, $75.00/1M output
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-haiku-20241022",
        input_price_per_1m: float = 1.00,
        output_price_per_1m: float = 5.00,
        max_retries: int = 3,
        timeout: int = 30
    ):
        """
        Inicializa o service Anthropic.

        Argumentos:
            api_key: Chave de API da Anthropic
            model: Nome do modelo Claude (padrão: claude-3-5-haiku-20241022)
            input_price_per_1m: Preço por 1M tokens de entrada
            output_price_per_1m: Preço por 1M tokens de saída
            max_retries: Máximo de tentativas em caso de erro
            timeout: Timeout em segundos
        """
        super().__init__(
            api_key=api_key,
            model=model,
            input_price_per_1m=input_price_per_1m,
            output_price_per_1m=output_price_per_1m,
            provider=LLMProvider.ANTHROPIC,
            max_retries=max_retries,
            timeout=timeout
        )

        # Criar cliente assíncrono
        self.client = AsyncAnthropic(
            api_key=api_key,
            timeout=httpx.Timeout(timeout, connect=10.0),
            max_retries=max_retries
        )

    async def generate(self, request: LLMRequest, image_data: Optional[Dict[str, Any]] = None) -> LLMResponse:
        """
        Gera resposta usando Anthropic Claude.

        Argumentos:
            request: Requisição com prompt e parâmetros
            image_data: Dados da imagem (base64 e mime_type) para análise visual

        Retorna:
            Resposta do Claude com tokens e metadados

        Raises:
            LLMAPIError: Erro de comunicação com API
            LLMTimeoutError: Timeout na requisição
            LLMResponseError: Erro ao processar resposta

        Explicação:
            - Usa Messages API da Anthropic
            - System prompt separado do user prompt
            - Suporta análise de imagens (vision)
            - Temperatura 0.0 para respostas determinísticas
            - Rastreamento de tokens para cálculo de custo
            - Retry automático em caso de erros transientes
        """
        request_timestamp = datetime.utcnow()

        try:
            # Preparar conteúdo da mensagem
            if image_data:
                # Mensagem com imagem
                content = [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": image_data["mime_type"],
                            "data": image_data["base64_data"]
                        }
                    },
                    {
                        "type": "text",
                        "text": request.prompt
                    }
                ]
            else:
                # Mensagem apenas com texto
                content = request.prompt

            # Preparar mensagens
            messages = [
                {
                    "role": "user",
                    "content": content
                }
            ]

            # Fazer requisição à API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system=request.system_prompt or self.create_system_prompt(),
                messages=messages
            )

            response_timestamp = datetime.utcnow()

            # Extrair conteúdo da resposta
            content = ""
            if response.content and len(response.content) > 0:
                # Claude retorna lista de blocos de conteúdo
                content = response.content[0].text

            # Criar resposta estruturada
            return LLMResponse(
                content=content,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                model=response.model,
                provider=self.provider.value,
                request_timestamp=request_timestamp,
                response_timestamp=response_timestamp,
                metadata={
                    "stop_reason": response.stop_reason,
                    "id": response.id
                }
            )

        except APITimeoutError as e:
            raise LLMTimeoutError(
                f"Timeout ao chamar Anthropic API: {str(e)}"
            ) from e

        except APIError as e:
            raise LLMAPIError(
                f"Erro na API Anthropic: {str(e)}"
            ) from e

        except Exception as e:
            raise LLMResponseError(
                f"Erro ao processar resposta Anthropic: {str(e)}"
            ) from e

    def _get_endpoint_url(self) -> str:
        """Retorna URL do endpoint da API Anthropic."""
        return "https://api.anthropic.com/v1/messages"

    def create_classification_prompt_with_image(
        self,
        document_name: str,
        available_types: list,
        features: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Cria prompt para classificação visual de documentos com imagem.

        Argumentos:
            document_name: Nome do arquivo
            available_types: Lista de tipos disponíveis
            features: Features opcionais extraídas

        Retorna:
            Prompt formatado para análise visual

        Explicação:
            - Instrui o LLM a analisar o conteúdo VISUAL da imagem
            - Desconsidera o nome do arquivo como indicativo principal
            - Foca em características visuais (layout, estrutura, elementos)
        """
        types_list = "\n".join([f"  - {t}" for t in available_types])

        # Preparar informações de features se disponíveis
        features_section = ""
        if features:
            features_section = "\n\n**Informações adicionais do documento:**\n"
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

        prompt = f"""Você é um especialista em classificação de documentos. Analise a IMAGEM do documento fornecida acima e classifique-a em UMA das categorias abaixo.

**IMPORTANTE:**
- Analise o CONTEÚDO VISUAL da imagem (layout, estrutura, elementos textuais e gráficos)
- NÃO se baseie apenas no nome do arquivo: "{document_name}"
- Considere características visuais como: cabeçalhos, rodapés, formatação, tabelas, gráficos, logotipos, estrutura de parágrafos, etc.

**Categorias disponíveis:**
{types_list}

{features_section}

**Instruções:**
1. Analise cuidadosamente o conteúdo visual da imagem
2. Identifique elementos característicos (layout, formatação, estrutura)
3. Classifique em UMA categoria da lista acima
4. Forneça uma explicação baseada no que você VÊ na imagem
5. Atribua um nível de confiança (0.0 a 1.0)

**Responda APENAS em formato JSON válido:**
```json
{{
  "predicted_type": "tipo_do_documento",
  "confidence": 0.85,
  "reasoning": "Explicação baseada na análise VISUAL da imagem"
}}
```

Analise a imagem e responda:"""

        return prompt

    async def classify_document(
        self,
        document_name: str,
        available_types: list,
        features: Optional[Dict[str, Any]] = None,
        image_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Classifica documento usando Claude com análise visual.

        Argumentos:
            document_name: Nome do arquivo
            available_types: Lista de tipos disponíveis
            features: Features opcionais do documento
            image_data: Dados da imagem (base64 e mime_type) para análise visual

        Retorna:
            Dicionário com:
            - predicted_type: Tipo predito
            - confidence: Confiança (0.0-1.0)
            - reasoning: Explicação da escolha
            - llm_metadata: Metadados da chamada LLM

        Explicação do fluxo:
            1. Cria prompt estruturado com documento e features
            2. Se imagem fornecida, envia para análise visual
            3. Envia para Claude com temperatura 0.0
            4. Parse da resposta JSON
            5. Validação do tipo retornado
            6. Cálculo de custos e metadados
        """
        # Criar prompt (adaptado se há imagem)
        if image_data:
            prompt = self.create_classification_prompt_with_image(
                document_name=document_name,
                available_types=available_types,
                features=features
            )
        else:
            prompt = self.create_classification_prompt(
                document_name=document_name,
                available_types=available_types,
                features=features
            )

        # Criar requisição
        llm_request = LLMRequest(
            prompt=prompt,
            max_tokens=500,  # Resposta JSON é curta
            temperature=0.0,  # Determinístico
            system_prompt=self.create_system_prompt()
        )

        # Gerar resposta (com imagem se fornecida)
        llm_response = await self.generate(llm_request, image_data=image_data)

        # Parse JSON da resposta
        try:
            # Limpar resposta (remover markdown se presente)
            content = llm_response.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()

            result = json.loads(content)

            # Validar campos obrigatórios
            if "predicted_type" not in result:
                raise ValueError("Campo 'predicted_type' não encontrado na resposta")

            # Validar que o tipo está na lista
            if result["predicted_type"] not in available_types:
                # Tentar encontrar tipo similar
                predicted = result["predicted_type"].lower().replace(" ", "_")
                if predicted not in available_types:
                    raise ValueError(
                        f"Tipo '{result['predicted_type']}' não está na lista de tipos disponíveis"
                    )
                result["predicted_type"] = predicted

            # Garantir confidence padrão
            if "confidence" not in result:
                result["confidence"] = 0.5

            # Adicionar metadados
            result["llm_metadata"] = self.create_llm_metadata(llm_response)

            return result

        except json.JSONDecodeError as e:
            raise LLMResponseError(
                f"Resposta LLM não é JSON válido: {llm_response.content[:200]}"
            ) from e

        except Exception as e:
            raise LLMResponseError(
                f"Erro ao processar classificação: {str(e)}"
            ) from e


# Factory function para facilitar criação
def create_anthropic_service(
    api_key: str,
    model: str = "claude-3-5-haiku-20241022",
    **kwargs
) -> AnthropicService:
    """
    Cria instância do AnthropicService.

    Argumentos:
        api_key: Chave de API da Anthropic
        model: Modelo a usar (padrão: claude-3-5-haiku-20241022)
        **kwargs: Argumentos adicionais para AnthropicService

    Retorna:
        Instância configurada do AnthropicService

    Exemplo:
        ```python
        service = create_anthropic_service(
            api_key=settings.ANTHROPIC_API_KEY,
            model="claude-3-5-haiku-20241022"
        )

        result = await service.classify_document(
            document_name="contract.pdf",
            available_types=["contract", "letter", "invoice"],
            features={"num_paragraphs": 15, "text_density": 0.65}
        )

        print(f"Tipo: {result['predicted_type']}")
        print(f"Confiança: {result['confidence']}")
        print(f"Custo: ${result['llm_metadata'].total_cost_usd}")
        ```
    """
    # Preços por modelo
    pricing = {
        "claude-3-5-haiku-20241022": (1.00, 5.00),
        "claude-3-5-sonnet-20241022": (3.00, 15.00),
        "claude-3-opus-20240229": (15.00, 75.00),
    }

    input_price, output_price = pricing.get(model, (1.00, 5.00))

    return AnthropicService(
        api_key=api_key,
        model=model,
        input_price_per_1m=input_price,
        output_price_per_1m=output_price,
        **kwargs
    )
