"""
Classificador de Emoções usando Google Vision API

Este módulo implementa um classificador de emoções faciais (raiva vs alegria)
usando a Google Cloud Vision API para detecção de faces e análise de emoções.

Objetivo Pedagógico:
-------------------
Demonstrar o uso de APIs de ML comerciais (Google Vision) para classificação
de emoções, comparando com:
- CNNs tradicionais treinadas do zero
- Modelos via API (Roboflow)
- Modelos foundation locais (YOLO11)

Vantagens do Google Vision API:
1. Detecção de faces e emoções de alta qualidade
2. Sem necessidade de treinamento
3. API robusta e bem documentada
4. Suporta múltiplas emoções (joy, sorrow, anger, surprise)
5. Funciona imediatamente (zero setup de modelo)

Desvantagens:
1. Custo por requisição (após free tier)
2. Requer internet
3. Latência de rede
4. Menor controle sobre modelo
5. Dependência de serviço externo

Google Cloud Vision API:
------------------------
- API de visão computacional do Google Cloud
- Detecção de faces com análise de emoções
- Likelihood scores: VERY_UNLIKELY, UNLIKELY, POSSIBLE, LIKELY, VERY_LIKELY
- Emoções suportadas: joy, sorrow, anger, surprise

Instalação:
----------
pip install requests pillow pandas python-dotenv

Configuração:
------------
1. Criar projeto no Google Cloud Console
2. Ativar Cloud Vision API
3. Criar API key
4. Adicionar GOOGLE_API_KEY ao .env

Uso:
----
python GoogleVisionEmotionClassifier.py --num_simulations 30
"""

import os
import sys
from pathlib import Path
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import argparse
import logging
from PIL import Image
import time
from dotenv import load_dotenv
import base64
import requests

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GoogleVisionEmotionClassifier:
    """
    Classificador de emoções usando Google Cloud Vision API.

    Este classificador usa a API do Google Cloud Vision para detectar
    faces e analisar emoções, classificando imagens em duas categorias:
    raiva e alegria.

    Diferente de outros classificadores:
    - Usa API comercial especializada em detecção de faces
    - Análise de emoções nativa da API
    - Não requer treinamento
    - Alta qualidade mas tem custo

    Attributes:
        api_key (str): API key do Google Cloud
        dataset_dir (Path): Diretório do dataset
        results_dir (Path): Diretório para salvar resultados
        model_name (str): Nome do modelo para identificação
    """

    # URL da API
    API_URL = "https://vision.googleapis.com/v1/images:annotate"

    # Mapeamento de likelihood para valores numéricos
    LIKELIHOOD_MAP = {
        'UNKNOWN': 0,
        'VERY_UNLIKELY': 1,
        'UNLIKELY': 2,
        'POSSIBLE': 3,
        'LIKELY': 4,
        'VERY_LIKELY': 5
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        dataset_dir: str = "datasets",
        results_dir: str = "3_simulation/results",
        model_name: str = "google_vision_emotion"
    ):
        """
        Inicializa o classificador Google Vision.

        Args:
            api_key: API key do Google Cloud (ou None para usar variável ambiente)
            dataset_dir: Diretório do dataset
            results_dir: Diretório para salvar resultados
            model_name: Nome do modelo para identificação

        Raises:
            ValueError: Se API key não fornecida e não encontrada em env
        """
        self.model_name = model_name
        self.dataset_dir = Path(dataset_dir)
        self.results_dir = Path(results_dir) / model_name
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Configura API key
        if api_key:
            self.api_key = api_key
        elif 'GOOGLE_API_KEY' in os.environ:
            self.api_key = os.environ['GOOGLE_API_KEY']
        else:
            raise ValueError(
                "GOOGLE_API_KEY não encontrada. "
                "Forneça via parâmetro ou variável de ambiente."
            )

        logger.info(f"GoogleVisionEmotionClassifier inicializado:")
        logger.info(f"  Modelo: {self.model_name}")
        logger.info(f"  Dataset: {self.dataset_dir}")
        logger.info(f"  Resultados: {self.results_dir}")
        logger.info(f"  API Key: {self.api_key[:10]}...{self.api_key[-4:]}")

    def detect_emotion(self, image_path: Path) -> Tuple[Optional[str], float, Dict]:
        """
        Detecta emoção em uma imagem usando Google Vision API.

        Args:
            image_path: Caminho para imagem

        Returns:
            Tupla com (emoção_detectada, confiança, detalhes)
            - emoção_detectada: 'raiva', 'alegria', ou None
            - confiança: score de confiança (0-5)
            - detalhes: dict com todas as emoções detectadas

        Análise:
        -------
        Google Vision retorna likelihood para cada emoção:
        - joyLikelihood
        - sorrowLikelihood
        - angerLikelihood
        - surpriseLikelihood

        Mapeamento para nosso dataset:
        - angerLikelihood -> raiva
        - joyLikelihood -> alegria
        """
        try:
            # Lê e codifica imagem em base64
            with open(image_path, 'rb') as image_file:
                image_content = image_file.read()

            encoded_image = base64.b64encode(image_content).decode('utf-8')

            # Monta requisição
            request_body = {
                "requests": [
                    {
                        "image": {
                            "content": encoded_image
                        },
                        "features": [
                            {
                                "type": "FACE_DETECTION",
                                "maxResults": 1
                            }
                        ]
                    }
                ]
            }

            # Faz chamada à API
            response = requests.post(
                f"{self.API_URL}?key={self.api_key}",
                json=request_body,
                timeout=30
            )

            if response.status_code != 200:
                logger.error(f"API retornou erro {response.status_code}: {response.text}")
                return None, 0.0, {'error': f'api_error_{response.status_code}'}

            result = response.json()

            # Verifica se há resposta
            if 'responses' not in result or not result['responses']:
                return None, 0.0, {'error': 'no_response'}

            response_data = result['responses'][0]

            # Verifica se há erro
            if 'error' in response_data:
                error_msg = response_data['error'].get('message', 'unknown')
                logger.error(f"API error: {error_msg}")
                return None, 0.0, {'error': error_msg}

            # Verifica se detectou faces
            if 'faceAnnotations' not in response_data or not response_data['faceAnnotations']:
                return None, 0.0, {'error': 'no_face_detected'}

            # Usa primeira face detectada
            face = response_data['faceAnnotations'][0]

            # Extrai likelihoods
            joy_likelihood = face.get('joyLikelihood', 'UNKNOWN')
            anger_likelihood = face.get('angerLikelihood', 'UNKNOWN')
            sorrow_likelihood = face.get('sorrowLikelihood', 'UNKNOWN')
            surprise_likelihood = face.get('surpriseLikelihood', 'UNKNOWN')

            # Converte para valores numéricos
            joy_score = self.LIKELIHOOD_MAP.get(joy_likelihood, 0)
            anger_score = self.LIKELIHOOD_MAP.get(anger_likelihood, 0)
            sorrow_score = self.LIKELIHOOD_MAP.get(sorrow_likelihood, 0)
            surprise_score = self.LIKELIHOOD_MAP.get(surprise_likelihood, 0)

            # Detalhes de todas as emoções
            details = {
                'joy': joy_score,
                'anger': anger_score,
                'sorrow': sorrow_score,
                'surprise': surprise_score,
                'detection_confidence': face.get('detectionConfidence', 0.0)
            }

            # Classifica como raiva ou alegria baseado em scores
            # Escolhe a emoção com maior score
            if joy_score > anger_score and joy_score >= 3:  # POSSIBLE ou maior
                return 'alegria', joy_score, details
            elif anger_score > joy_score and anger_score >= 3:
                return 'raiva', anger_score, details
            elif joy_score == anger_score and joy_score >= 3:
                # Empate: considera alegria se alegria >= raiva
                return 'alegria', joy_score, details
            else:
                # Nenhuma emoção forte detectada
                # Retorna a maior mesmo que baixa
                if joy_score >= anger_score:
                    return 'alegria', joy_score, details
                else:
                    return 'raiva', anger_score, details

        except requests.exceptions.Timeout:
            logger.error(f"Timeout ao processar {image_path.name}")
            return None, 0.0, {'error': 'timeout'}
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de requisição ao processar {image_path.name}: {e}")
            return None, 0.0, {'error': 'request_error'}
        except Exception as e:
            logger.error(f"Erro ao processar {image_path.name}: {e}")
            return None, 0.0, {'error': str(e)}

    def process_simulation(self, sim_num: int) -> Dict:
        """
        Processa uma simulação completa.

        Args:
            sim_num: Número da simulação (1-30)

        Returns:
            Dict com resultados da simulação no formato padrão

        Formato de retorno:
        {
            'numero_simulacao': int,
            'nome_modelo': str,
            'qtd_sucesso_alegria': int,
            'qtd_sucesso_raiva': int,
            'total_alegria': int,
            'total_raiva': int,
            'tempo_total_ms': float,
            'acuracia_alegria': float,
            'acuracia_raiva': float,
            'acuracia_geral': float
        }
        """
        logger.info("=" * 70)
        logger.info(f"Processando Simulação {sim_num:02d}")
        logger.info("=" * 70)

        start_time = time.time()

        # Diretório da simulação
        sim_dir = self.dataset_dir / f"sim{sim_num:02d}"

        if not sim_dir.exists():
            raise FileNotFoundError(f"Simulação {sim_num} não encontrada em {sim_dir}")

        # Contadores
        total_raiva = 0
        total_alegria = 0
        sucesso_raiva = 0
        sucesso_alegria = 0

        # Processar classe RAIVA
        raiva_dir = sim_dir / "raiva"
        if raiva_dir.exists():
            raiva_images = list(raiva_dir.glob("*.jpg")) + list(raiva_dir.glob("*.png"))
            raiva_images = sorted(raiva_images)
            total_raiva = len(raiva_images)

            logger.info(f"\nProcessando classe: raiva")
            logger.info(f"Total de imagens: {total_raiva}")

            for idx, img_path in enumerate(raiva_images, 1):
                emotion, confidence, details = self.detect_emotion(img_path)

                if emotion == 'raiva':
                    sucesso_raiva += 1

                # Log a cada 10 imagens
                if idx % 10 == 0:
                    logger.info(f"  Processadas: {idx}/{total_raiva} imagens")

                # Pequeno delay para evitar rate limiting
                time.sleep(0.1)

            logger.info(f"  Acertos: {sucesso_raiva}/{total_raiva}")

        # Processar classe ALEGRIA
        alegria_dir = sim_dir / "alegria"
        if alegria_dir.exists():
            alegria_images = list(alegria_dir.glob("*.jpg")) + list(alegria_dir.glob("*.png"))
            alegria_images = sorted(alegria_images)
            total_alegria = len(alegria_images)

            logger.info(f"\nProcessando classe: alegria")
            logger.info(f"Total de imagens: {total_alegria}")

            for idx, img_path in enumerate(alegria_images, 1):
                emotion, confidence, details = self.detect_emotion(img_path)

                if emotion == 'alegria':
                    sucesso_alegria += 1

                # Log a cada 10 imagens
                if idx % 10 == 0:
                    logger.info(f"  Processadas: {idx}/{total_alegria} imagens")

                # Pequeno delay para evitar rate limiting
                time.sleep(0.1)

            logger.info(f"  Acertos: {sucesso_alegria}/{total_alegria}")

        # Calcula métricas
        tempo_total_ms = (time.time() - start_time) * 1000

        acuracia_alegria = sucesso_alegria / total_alegria if total_alegria > 0 else 0.0
        acuracia_raiva = sucesso_raiva / total_raiva if total_raiva > 0 else 0.0
        total_imagens = total_alegria + total_raiva
        total_acertos = sucesso_alegria + sucesso_raiva
        acuracia_geral = total_acertos / total_imagens if total_imagens > 0 else 0.0

        # Resultados
        results = {
            'numero_simulacao': sim_num,
            'nome_modelo': self.model_name,
            'qtd_sucesso_alegria': sucesso_alegria,
            'qtd_sucesso_raiva': sucesso_raiva,
            'total_alegria': total_alegria,
            'total_raiva': total_raiva,
            'tempo_total_ms': tempo_total_ms,
            'acuracia_alegria': acuracia_alegria,
            'acuracia_raiva': acuracia_raiva,
            'acuracia_geral': acuracia_geral
        }

        # Log resultados
        logger.info(f"\nResultados da Simulação {sim_num:02d}:")
        logger.info(f"  Acurácia Alegria: {acuracia_alegria:.4f}")
        logger.info(f"  Acurácia Raiva: {acuracia_raiva:.4f}")
        logger.info(f"  Acurácia Geral: {acuracia_geral:.4f}")
        logger.info(f"  Tempo Total: {tempo_total_ms/1000:.2f}s")

        return results

    def process_all_simulations(self, num_simulations: int = 30) -> pd.DataFrame:
        """
        Processa todas as simulações com salvamento incremental.

        Args:
            num_simulations: Número de simulações a processar (padrão: 30)

        Returns:
            DataFrame com todos os resultados

        Comportamento:
        -------------
        - Processa simulações de 1 a num_simulations
        - Salva CSV incrementalmente após cada simulação
        - Gera estatísticas finais em JSON
        - Continua mesmo se uma simulação falhar
        """
        logger.info("\n" + "=" * 70)
        logger.info(f"Iniciando processamento de {num_simulations} simulações")
        logger.info(f"Modelo: {self.model_name}")
        logger.info("=" * 70 + "\n")

        all_results = []
        start_time = time.time()

        # Processa cada simulação
        for sim_num in range(1, num_simulations + 1):
            try:
                results = self.process_simulation(sim_num)
                all_results.append(results)

                # Salvamento incremental
                results_df = pd.DataFrame(all_results)
                results_path = self.results_dir / "results.csv"
                results_df.to_csv(results_path, index=False)

                logger.info(f"\nResultados salvos: {len(all_results)} simulações em {results_path}")
                logger.info("")

            except Exception as e:
                logger.error(f"Erro na simulação {sim_num}: {e}")
                logger.error("Continuando com próxima simulação...")
                continue

        # Estatísticas finais
        if not all_results:
            logger.error("Nenhuma simulação processada com sucesso!")
            return pd.DataFrame()

        results_df = pd.DataFrame(all_results)

        # Calcula estatísticas
        duration = time.time() - start_time
        stats = {
            'modelo': self.model_name,
            'num_simulations': len(all_results),
            'acuracia_alegria_mean': float(results_df['acuracia_alegria'].mean()),
            'acuracia_alegria_std': float(results_df['acuracia_alegria'].std()),
            'acuracia_raiva_mean': float(results_df['acuracia_raiva'].mean()),
            'acuracia_raiva_std': float(results_df['acuracia_raiva'].std()),
            'acuracia_geral_mean': float(results_df['acuracia_geral'].mean()),
            'acuracia_geral_std': float(results_df['acuracia_geral'].std()),
            'tempo_total_segundos': duration,
            'tempo_medio_por_simulacao': duration / len(all_results),
            'tempo_medio_ms': float(results_df['tempo_total_ms'].mean()),
            'tempo_std_ms': float(results_df['tempo_total_ms'].std()),
            'timestamp': datetime.now().isoformat()
        }

        stats_path = self.results_dir / "stats.json"
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)

        logger.info("\n" + "=" * 70)
        logger.info("PROCESSAMENTO CONCLUÍDO - GOOGLE VISION API")
        logger.info("=" * 70)
        logger.info(f"Simulações: {len(all_results)}")
        logger.info(f"Tempo total: {duration:.2f}s")
        logger.info(f"Tempo médio/simulação: "
                   f"{stats['tempo_medio_por_simulacao']:.2f}s")
        logger.info(f"\nEstatísticas:")
        logger.info(f"  Acurácia Alegria: "
                   f"{stats['acuracia_alegria_mean']:.4f} ± "
                   f"{stats['acuracia_alegria_std']:.4f}")
        logger.info(f"  Acurácia Raiva: "
                   f"{stats['acuracia_raiva_mean']:.4f} ± "
                   f"{stats['acuracia_raiva_std']:.4f}")
        logger.info(f"  Acurácia Geral: "
                   f"{stats['acuracia_geral_mean']:.4f} ± "
                   f"{stats['acuracia_geral_std']:.4f}")
        logger.info(f"\nResultados salvos em:")
        logger.info(f"  CSV: {results_path}")
        logger.info(f"  Stats: {stats_path}")
        logger.info("=" * 70)

        return results_df


def main():
    """
    Função principal para execução via linha de comando.

    Uso:
        python GoogleVisionEmotionClassifier.py --num_simulations 30
        python GoogleVisionEmotionClassifier.py --simulation 1
    """
    parser = argparse.ArgumentParser(
        description='Classificador de Emoções usando Google Vision API'
    )

    parser.add_argument(
        '--dataset_dir',
        type=str,
        default='datasets',
        help='Diretório do dataset'
    )

    parser.add_argument(
        '--results_dir',
        type=str,
        default='3_simulation/results',
        help='Diretório para resultados'
    )

    parser.add_argument(
        '--model_name',
        type=str,
        default='google_vision_emotion',
        help='Nome identificador do modelo'
    )

    parser.add_argument(
        '--num_simulations',
        type=int,
        default=30,
        help='Número de simulações a processar'
    )

    parser.add_argument(
        '--simulation',
        type=int,
        help='Processar apenas uma simulação específica'
    )

    args = parser.parse_args()

    # Carrega API key do .env
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / '.env'
    load_dotenv(env_path)

    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        logger.error("GOOGLE_API_KEY não encontrada no .env")
        logger.error(f"Procurado em: {env_path}")
        logger.error("\nAdicione ao .env:")
        logger.error("GOOGLE_API_KEY=sua_chave_aqui")
        sys.exit(1)

    # Inicializa classificador
    classifier = GoogleVisionEmotionClassifier(
        api_key=api_key,
        dataset_dir=args.dataset_dir,
        results_dir=args.results_dir,
        model_name=args.model_name
    )

    # Processa simulações
    if args.simulation:
        # Processa apenas uma simulação
        results = classifier.process_simulation(args.simulation)
        print(json.dumps(results, indent=2))

        # Salva resultado em CSV
        results_df = pd.DataFrame([results])
        results_path = classifier.results_dir / "results.csv"
        results_df.to_csv(results_path, index=False)
        logger.info(f"\nResultado salvo em: {results_path}")
    else:
        # Processa todas as simulações
        results_df = classifier.process_all_simulations(args.num_simulations)
        print("\nResultados:")
        print(results_df.to_string())


if __name__ == "__main__":
    main()
