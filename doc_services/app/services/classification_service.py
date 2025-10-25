"""
Serviço de Classificação de Documentos (UC1).

Implementa o caso de uso 1: Identificar se o documento é um artigo científico.

EXPLICAÇÃO EDUCATIVA:
Este serviço é responsável por:
1. Receber um documento (arquivo)
2. Chamar API externa de classificação (constraint UC1)
3. Retornar se é artigo científico ou não

Se não for científico, o processamento deve parar (rejeitar documento).

Este é o primeiro passo do pipeline de análise.
"""

import logging
from pathlib import Path
from typing import Tuple

from app.integrations import ClassificationAPIClient

logger = logging.getLogger(__name__)


class ClassificationService:
    """
    Serviço de classificação de documentos.

    EXPLICAÇÃO EDUCATIVA:
    Pattern de Service Layer:
    - Encapsula lógica de negócio
    - Orquestra chamadas a integrações
    - Independente de framework web
    - Facilita testes unitários

    Este serviço usa ClassificationAPIClient para comunicar
    com a API externa de classificação.
    """

    def __init__(
        self,
        api_url: str = None,
        api_key: str = None,
        use_api: bool = False
    ):
        """
        Inicializa serviço de classificação.

        Args:
            api_url: URL da API de classificação
            api_key: Chave de autenticação
            use_api: Se True, usa API HTTP; se False, usa classificador local
        """
        self.client = ClassificationAPIClient(
            api_url=api_url,
            api_key=api_key,
            use_api=use_api
        )
        logger.info("ClassificationService inicializado")

    async def is_scientific_paper(
        self,
        file_path: Path
    ) -> Tuple[bool, float]:
        """
        Verifica se documento é um artigo científico.

        EXPLICAÇÃO EDUCATIVA:
        Este é o método principal do UC1.

        Fluxo:
        1. Chama API/classificador via client
        2. Extrai resultado da classificação
        3. Retorna (é_científico, confiança)

        Constraint UC1: DEVE usar serviço API já implementado.

        Args:
            file_path: Caminho do arquivo a classificar

        Returns:
            Tupla (is_scientific, confidence)
            - is_scientific: True se for artigo científico
            - confidence: Nível de confiança (0.0 a 1.0)

        Raises:
            RuntimeError: Se classificação falhar
        """
        logger.info(f"Classificando documento: {file_path.name}")

        try:
            # Chamar API de classificação
            result = await self.client.classify_document(file_path)

            is_scientific = result["is_scientific_paper"]
            confidence = result.get("confidence", 0.0)

            logger.info(
                f"Resultado: {'CIENTÍFICO' if is_scientific else 'NÃO CIENTÍFICO'} "
                f"(confiança: {confidence:.2%})"
            )

            return is_scientific, confidence

        except Exception as e:
            logger.error(f"Erro na classificação: {e}")
            raise RuntimeError(f"Falha na classificação do documento: {str(e)}")

    async def close(self):
        """Libera recursos do cliente."""
        await self.client.close()
