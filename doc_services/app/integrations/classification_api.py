"""
Cliente HTTP para API externa de classificação de documentos (UC1).

Este módulo implementa a integração com o serviço de classificação
já disponível no projeto (rvlp/simple_classifier.py).

EXPLICAÇÃO EDUCATIVA:
Este é um cliente HTTP que permite comunicação com uma API externa.
Como a API ainda não está disponível via HTTP, este módulo fornece:
1. Interface para quando a API estiver disponível via HTTP
2. Fallback para usar o classificador diretamente (modo local)

Conceitos importantes:
- httpx: biblioteca HTTP moderna e assíncrona para Python
- Retry logic: tentar novamente em caso de falhas temporárias
- Timeout: limitar tempo de espera para evitar travamentos
- Error handling: tratamento robusto de erros de rede
"""

import httpx
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import sys

# Adicionar caminho do rvlp ao PYTHONPATH para importar o classificador
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "rvlp"))

logger = logging.getLogger(__name__)


class ClassificationAPIClient:
    """
    Cliente para API de classificação de documentos.

    EXPLICAÇÃO EDUCATIVA:
    Esta classe encapsula toda a lógica de comunicação com o serviço
    de classificação. Suporta dois modos:

    1. Modo API (quando USE_API=True):
       - Envia documento via HTTP POST
       - Recebe classificação como JSON
       - Trata erros de rede e timeouts

    2. Modo Local (quando USE_API=False):
       - Usa SimpleDocumentClassifier diretamente
       - Útil para desenvolvimento e testes
       - Não requer servidor externo rodando

    Atributos:
        api_url: URL base da API de classificação
        api_key: Chave de autenticação (opcional)
        timeout: Tempo máximo de espera em segundos
        use_api: Se True, usa HTTP; se False, usa classificador local
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30,
        use_api: bool = False
    ):
        """
        Inicializa o cliente da API.

        Args:
            api_url: URL da API de classificação (ex: http://localhost:8001)
            api_key: Chave de autenticação (se necessário)
            timeout: Timeout em segundos para requisições
            use_api: Se True, usa API HTTP; se False, usa classificador local
        """
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout
        self.use_api = use_api

        # Cliente HTTP com configurações
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            follow_redirects=True
        ) if use_api else None

        # Classificador local (fallback)
        self._local_classifier = None

        logger.info(
            f"ClassificationAPIClient inicializado: "
            f"modo={'API' if use_api else 'LOCAL'}, "
            f"timeout={timeout}s"
        )

    def _get_local_classifier(self):
        """
        Obtém instância do classificador local (lazy loading).

        EXPLICAÇÃO EDUCATIVA:
        Lazy loading significa carregar o recurso apenas quando necessário.
        Benefícios:
        - Economiza memória se não for usado
        - Acelera inicialização
        - Evita dependências desnecessárias
        """
        if self._local_classifier is None:
            try:
                from simple_classifier import SimpleDocumentClassifier
                self._local_classifier = SimpleDocumentClassifier()
                logger.info("Classificador local carregado com sucesso")
            except ImportError as e:
                logger.error(f"Erro ao importar SimpleDocumentClassifier: {e}")
                raise RuntimeError(
                    "Classificador local não disponível. "
                    "Verifique se simple_classifier.py está acessível."
                )
        return self._local_classifier

    async def classify_document(
        self,
        file_path: Path
    ) -> Dict[str, Any]:
        """
        Classifica um documento e retorna o tipo detectado.

        EXPLICAÇÃO EDUCATIVA:
        Este método é o ponto de entrada principal da integração.
        Decide automaticamente entre usar API HTTP ou classificador local.

        Fluxo:
        1. Verifica modo de operação (API ou Local)
        2. Chama método apropriado
        3. Retorna resultado padronizado

        Args:
            file_path: Caminho para o arquivo a ser classificado

        Returns:
            Dicionário com resultado da classificação:
            {
                "predicted_type": str,  # Tipo predito
                "confidence": float,    # Confiança (0.0 a 1.0)
                "is_scientific_paper": bool,  # True se for artigo científico
                "features": dict       # Features extraídas (opcional)
            }

        Raises:
            RuntimeError: Se classificação falhar
            FileNotFoundError: Se arquivo não existir
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        logger.info(f"Classificando documento: {file_path.name}")

        if self.use_api:
            return await self._classify_via_api(file_path)
        else:
            return await self._classify_locally(file_path)

    async def _classify_via_api(self, file_path: Path) -> Dict[str, Any]:
        """
        Classifica documento usando API HTTP.

        EXPLICAÇÃO EDUCATIVA:
        Envia arquivo para API externa usando multipart/form-data.
        Processo:
        1. Lê arquivo como bytes
        2. Cria requisição multipart
        3. Envia POST para API
        4. Parseia resposta JSON
        5. Trata erros HTTP

        Args:
            file_path: Caminho do arquivo

        Returns:
            Resultado da classificação

        Raises:
            RuntimeError: Se API retornar erro
        """
        if not self.api_url:
            raise RuntimeError("API URL não configurada")

        try:
            # Preparar arquivo para upload
            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f, "application/octet-stream")}

                # Headers com API key se disponível
                headers = {}
                if self.api_key:
                    headers["X-API-Key"] = self.api_key

                # Fazer requisição POST
                response = await self.client.post(
                    f"{self.api_url}/classify",
                    files=files,
                    headers=headers
                )

                # Verificar status
                response.raise_for_status()

                # Parsear resposta
                result = response.json()

                logger.info(
                    f"Classificação via API: {result.get('predicted_type')} "
                    f"(confiança: {result.get('confidence', 0):.2%})"
                )

                return result

        except httpx.TimeoutException:
            logger.error(f"Timeout ao classificar {file_path.name}")
            raise RuntimeError("Timeout na classificação via API")

        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP {e.response.status_code}: {e.response.text}")
            raise RuntimeError(f"Erro na API de classificação: {e.response.status_code}")

        except Exception as e:
            logger.error(f"Erro inesperado ao classificar via API: {e}")
            raise RuntimeError(f"Erro na classificação: {str(e)}")

    async def _classify_locally(self, file_path: Path) -> Dict[str, Any]:
        """
        Classifica documento usando classificador local.

        EXPLICAÇÃO EDUCATIVA:
        Usa SimpleDocumentClassifier diretamente sem rede.
        Útil para:
        - Desenvolvimento local
        - Testes
        - Ambientes sem acesso à API

        Args:
            file_path: Caminho do arquivo

        Returns:
            Resultado da classificação padronizado
        """
        try:
            classifier = self._get_local_classifier()

            # Classificar documento
            predicted_type, confidence, features = classifier.classify(file_path)

            # Determinar se é artigo científico
            is_scientific = (predicted_type == "scientific_publication")

            result = {
                "predicted_type": predicted_type,
                "confidence": confidence,
                "is_scientific_paper": is_scientific,
                "features": features
            }

            logger.info(
                f"Classificação local: {predicted_type} "
                f"(confiança: {confidence:.2%})"
            )

            return result

        except Exception as e:
            logger.error(f"Erro ao classificar localmente: {e}")
            raise RuntimeError(f"Erro na classificação local: {str(e)}")

    async def is_scientific_paper(self, file_path: Path) -> bool:
        """
        Verifica se documento é um artigo científico.

        EXPLICAÇÃO EDUCATIVA:
        Método de conveniência que retorna apenas True/False.
        Útil para o caso de uso UC1 que precisa apenas validar
        se o documento é científico.

        Args:
            file_path: Caminho do arquivo

        Returns:
            True se for artigo científico, False caso contrário
        """
        result = await self.classify_document(file_path)
        return result["is_scientific_paper"]

    async def close(self):
        """
        Fecha conexões HTTP.

        EXPLICAÇÃO EDUCATIVA:
        Cleanup method que libera recursos.
        Importante chamar ao finalizar uso do cliente para:
        - Fechar conexões HTTP abertas
        - Liberar sockets
        - Evitar warnings de recursos não liberados
        """
        if self.client:
            await self.client.aclose()
            logger.debug("Cliente HTTP fechado")

    async def __aenter__(self):
        """Suporte para async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup automático ao sair do context manager."""
        await self.close()
