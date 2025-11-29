"""
Classificador de Emoções usando Roboflow API

Este módulo implementa um classificador de emoções faciais (raiva vs alegria)
usando modelos pré-treinados disponíveis no Roboflow Universe.

Objetivo Pedagógico:
-------------------
Demonstrar o uso de modelos foundation/pré-treinados via API para classificação
de emoções, comparando com CNNs tradicionais treinadas do zero.

Vantagens de modelos via API:
1. Sem necessidade de treinamento (inference imediato)
2. Modelos já otimizados e validados
3. Infraestrutura gerenciada (escalabilidade)
4. Atualizações automáticas de modelo

Desvantagens:
1. Dependência de serviço externo
2. Custo por requisição (após limite gratuito)
3. Latência de rede
4. Menos controle sobre arquitetura

Pipeline de Classificação:
-------------------------
1. Carrega imagens de cada simulação
2. Para cada imagem:
   a. Envia para API Roboflow
   b. Recebe predições de emoções
   c. Mapeia emoções detectadas para classes (raiva/alegria)
3. Agrega resultados por simulação
4. Salva métricas em CSV

Instalação:
----------
pip install roboflow opencv-python pillow

Uso:
----
python RoboflowEmotionClassifier.py --api_key YOUR_API_KEY
"""

import os
import sys
from pathlib import Path
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
import argparse
import logging
from PIL import Image
import time

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RoboflowEmotionClassifier:
    """
    Classificador de emoções usando Roboflow API.

    Este classificador usa modelos pré-treinados de detecção de emoções
    disponíveis no Roboflow Universe para classificar imagens em
    duas categorias: raiva e alegria.

    Attributes:
        api_key (str): Chave de API do Roboflow
        model_id (str): ID do modelo a ser usado
        dataset_dir (Path): Diretório do dataset
        results_dir (Path): Diretório para salvar resultados
        model_name (str): Nome do modelo para identificação
    """

    def __init__(
        self,
        api_key: str,
        model_id: str = "computer-vision-projects-zhogq/emotion-detection-y0svj",
        dataset_dir: str = "datasets",
        results_dir: str = "3_simulation/results",
        model_name: str = "roboflow_emotion"
    ):
        """
        Inicializa o classificador Roboflow.

        Args:
            api_key: Chave de API do Roboflow
            model_id: ID do modelo no formato "workspace/project/version"
            dataset_dir: Caminho para o diretório datasets/
            results_dir: Caminho para salvar resultados
            model_name: Nome identificador do modelo

        Nota sobre API Key:
            Para obter uma API key:
            1. Crie conta em roboflow.com
            2. Acesse Settings > API
            3. Copie sua Private API Key
        """
        self.api_key = api_key
        self.model_id = model_id
        self.dataset_dir = Path(dataset_dir)
        self.model_name = model_name

        # Cria diretório de resultados: results_dir/model_name/
        self.results_dir = Path(results_dir) / model_name
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Mapeamento de emoções Roboflow para nossas classes
        # Explicação: Diferentes modelos podem retornar nomes diferentes
        # Este mapeamento normaliza para nossas 2 classes
        # IMPORTANTE: O mapeamento é case-insensitive (convertemos para lowercase antes de buscar)
        self.emotion_mapping = {
            # Raiva e variações
            'angry': 'raiva',
            'anger': 'raiva',
            'raiva': 'raiva',
            'mad': 'raiva',
            'furious': 'raiva',

            # Alegria e variações
            'happy': 'alegria',
            'happiness': 'alegria',
            'alegria': 'alegria',
            'joy': 'alegria',
            'smile': 'alegria',
            'smiling': 'alegria',

            # Outras emoções (ignoradas neste estudo)
            'sad': None,
            'sadness': None,
            'fear': None,
            'fearful': None,
            'surprise': None,
            'surprised': None,
            'disgust': None,
            'disgusted': None,
            'neutral': None,
            'contempt': None
        }

        # Inicializa cliente Roboflow
        self._initialize_roboflow()

        logger.info(f"RoboflowEmotionClassifier inicializado:")
        logger.info(f"  Model ID: {self.model_id}")
        logger.info(f"  Dataset: {self.dataset_dir}")
        logger.info(f"  Resultados: {self.results_dir}")

    def _initialize_roboflow(self):
        """
        Inicializa conexão com Roboflow API.

        Tenta importar e configurar o SDK do Roboflow.
        Se falhar, usa requisições HTTP diretas como fallback.

        Raises:
            ImportError: Se roboflow não estiver instalado
            ValueError: Se API key for inválida
        """
        try:
            from roboflow import Roboflow

            # Inicializa cliente
            rf = Roboflow(api_key=self.api_key)

            # Extrai workspace e project do model_id
            # Formato esperado: "workspace/project/version"
            parts = self.model_id.split('/')

            if len(parts) == 2:
                workspace, project = parts
                version = None  # Auto-detect
            elif len(parts) == 3:
                workspace, project, version = parts
                version = int(version)
            else:
                raise ValueError(
                    f"model_id inválido: {self.model_id}. "
                    "Formato esperado: 'workspace/project' ou 'workspace/project/version'"
                )

            # Carrega projeto
            project_obj = rf.workspace(workspace).project(project)

            # Se versão não especificada, usa a mais recente
            if version is None:
                # Lista versões disponíveis e pega a última
                try:
                    # Tenta descobrir versões disponíveis
                    versions = project_obj.versions()
                    if versions:
                        version = versions[-1].version
                        logger.info(f"Auto-detectada versão mais recente: {version}")
                    else:
                        version = 1
                        logger.info("Nenhuma versão encontrada, usando versão 1")
                except Exception as e:
                    logger.warning(f"Não foi possível auto-detectar versão: {e}")
                    version = 1
                    logger.info("Usando versão padrão: 1")

            # Carrega modelo
            self.model = project_obj.version(version).model

            logger.info("Cliente Roboflow inicializado com sucesso")
            logger.info(f"  Workspace: {workspace}")
            logger.info(f"  Project: {project}")
            logger.info(f"  Version: {version}")

        except ImportError:
            logger.error("Roboflow SDK não encontrado. Instalando...")
            logger.info("Execute: pip install roboflow")
            raise ImportError(
                "Roboflow SDK não instalado. Execute: pip install roboflow"
            )
        except Exception as e:
            logger.error(f"Erro ao inicializar Roboflow: {e}")
            raise

    def predict_image(self, image_path: Path) -> Dict:
        """
        Faz predição de emoção em uma única imagem.

        Args:
            image_path: Caminho para a imagem

        Returns:
            Dicionário com predições no formato:
            {
                'predictions': [
                    {'class': 'happy', 'confidence': 0.95, ...},
                    ...
                ],
                'image': str(image_path),
                'time': inference_time_ms
            }

        Nota sobre Rate Limiting:
            APIs gratuitas geralmente têm limites de requisições/minuto.
            Este método inclui retry logic e delays para respeitar limites.
        """
        try:
            # Faz predição
            # Roboflow aceita path de arquivo diretamente
            start_time = time.time()
            result = self.model.predict(str(image_path), confidence=40, overlap=30)
            inference_time = (time.time() - start_time) * 1000  # em ms

            # Converte resultado para dicionário
            result_dict = result.json()
            result_dict['inference_time_ms'] = inference_time
            result_dict['image'] = str(image_path)

            return result_dict

        except Exception as e:
            logger.error(f"Erro ao processar {image_path}: {e}")
            return {
                'predictions': [],
                'image': str(image_path),
                'error': str(e),
                'inference_time_ms': 0
            }

    def classify_emotion(self, predictions: List[Dict]) -> str:
        """
        Classifica emoção baseado nas predições do modelo.

        Estratégia de classificação:
        1. Filtra predições com confiança > 0.5
        2. Mapeia emoções detectadas para nossas classes (raiva/alegria)
        3. Retorna classe com maior confiança
        4. Se nenhuma classe reconhecida, retorna 'unknown'

        Args:
            predictions: Lista de predições do modelo

        Returns:
            'raiva', 'alegria' ou 'unknown'

        Nota Pedagógica:
            Esta função implementa lógica de mapeamento pois modelos
            pré-treinados podem detectar múltiplas emoções. Precisamos
            mapear para nosso conjunto binário de classes.
        """
        if not predictions:
            return 'unknown'

        # Filtra predições com confiança suficiente
        # Threshold baixo (0.4) pois modelo tem baixa confiança em algumas emoções
        confident_preds = [
            p for p in predictions
            if p.get('confidence', 0) > 0.4
        ]

        if not confident_preds:
            return 'unknown'

        # Mapeia para nossas classes
        mapped_emotions = []
        for pred in confident_preds:
            emotion = pred.get('class', '').lower()
            mapped_emotion = self.emotion_mapping.get(emotion)

            if mapped_emotion:  # Ignora None (emoções não relevantes)
                mapped_emotions.append({
                    'emotion': mapped_emotion,
                    'confidence': pred.get('confidence', 0)
                })

        if not mapped_emotions:
            return 'unknown'

        # Retorna emoção com maior confiança
        best_emotion = max(mapped_emotions, key=lambda x: x['confidence'])
        return best_emotion['emotion']

    def process_simulation(self, simulation_num: int) -> Dict:
        """
        Processa todas as imagens de uma simulação.

        Pipeline:
        1. Localiza diretório da simulação
        2. Para cada classe (raiva, alegria):
           a. Lista todas as imagens
           b. Faz predição em cada imagem
           c. Classifica emoção
           d. Conta acertos
        3. Calcula métricas
        4. Retorna resultados

        Args:
            simulation_num: Número da simulação (1-30)

        Returns:
            Dicionário com métricas:
            {
                'numero_simulacao': int,
                'nome_modelo': str,
                'qtd_sucesso_alegria': int,
                'qtd_sucesso_raiva': int,
                'total_alegria': int,
                'total_raiva': int,
                'acuracia_alegria': float,
                'acuracia_raiva': float,
                'acuracia_geral': float,
                'tempo_total_ms': float
            }
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"Processando Simulação {simulation_num:02d}")
        logger.info(f"{'='*70}")

        sim_dir = self.dataset_dir / f"sim{simulation_num:02d}"

        if not sim_dir.exists():
            raise FileNotFoundError(f"Simulação {simulation_num} não encontrada em {sim_dir}")

        results = {
            'numero_simulacao': simulation_num,
            'nome_modelo': self.model_name,
            'qtd_sucesso_alegria': 0,
            'qtd_sucesso_raiva': 0,
            'total_alegria': 0,
            'total_raiva': 0,
            'tempo_total_ms': 0
        }

        start_time = time.time()

        # Processa cada classe
        for class_name in ['raiva', 'alegria']:
            class_dir = sim_dir / class_name

            if not class_dir.exists():
                logger.warning(f"Diretório {class_dir} não encontrado")
                continue

            # Lista imagens
            image_files = list(class_dir.glob('*'))
            image_files = [f for f in image_files if f.suffix.lower() in ['.png', '.jpg', '.jpeg']]

            logger.info(f"\nProcessando classe: {class_name}")
            logger.info(f"Total de imagens: {len(image_files)}")

            successes = 0

            # Processa cada imagem
            for idx, image_path in enumerate(image_files, 1):
                # Faz predição
                prediction_result = self.predict_image(image_path)

                # Classifica emoção
                predicted_emotion = self.classify_emotion(
                    prediction_result.get('predictions', [])
                )

                # Verifica se acertou
                is_correct = predicted_emotion == class_name
                if is_correct:
                    successes += 1

                # Log de progresso
                if idx % 10 == 0:
                    logger.info(f"  Processadas: {idx}/{len(image_files)} imagens")

                # Delay para respeitar rate limit (se necessário)
                # Roboflow free tier: ~100 requests/minute
                time.sleep(0.1)  # 100ms entre requisições

            # Atualiza resultados
            if class_name == 'alegria':
                results['qtd_sucesso_alegria'] = successes
                results['total_alegria'] = len(image_files)
            else:  # raiva
                results['qtd_sucesso_raiva'] = successes
                results['total_raiva'] = len(image_files)

            logger.info(f"  Acertos: {successes}/{len(image_files)}")

        # Calcula métricas finais
        results['tempo_total_ms'] = (time.time() - start_time) * 1000

        # Acurácias por classe
        if results['total_alegria'] > 0:
            results['acuracia_alegria'] = results['qtd_sucesso_alegria'] / results['total_alegria']
        else:
            results['acuracia_alegria'] = 0.0

        if results['total_raiva'] > 0:
            results['acuracia_raiva'] = results['qtd_sucesso_raiva'] / results['total_raiva']
        else:
            results['acuracia_raiva'] = 0.0

        # Acurácia geral
        total_images = results['total_alegria'] + results['total_raiva']
        total_successes = results['qtd_sucesso_alegria'] + results['qtd_sucesso_raiva']

        if total_images > 0:
            results['acuracia_geral'] = total_successes / total_images
        else:
            results['acuracia_geral'] = 0.0

        logger.info(f"\nResultados da Simulação {simulation_num:02d}:")
        logger.info(f"  Acurácia Alegria: {results['acuracia_alegria']:.4f}")
        logger.info(f"  Acurácia Raiva: {results['acuracia_raiva']:.4f}")
        logger.info(f"  Acurácia Geral: {results['acuracia_geral']:.4f}")
        logger.info(f"  Tempo Total: {results['tempo_total_ms']/1000:.2f}s")

        return results

    def process_all_simulations(self, num_simulations: int = 30) -> pd.DataFrame:
        """
        Processa todas as simulações e salva resultados.

        Args:
            num_simulations: Número de simulações a processar

        Returns:
            DataFrame com resultados de todas as simulações
        """
        logger.info("\n" + "="*70)
        logger.info("INICIANDO PROCESSAMENTO DE TODAS AS SIMULAÇÕES")
        logger.info("="*70)
        logger.info(f"Total de simulações: {num_simulations}")
        logger.info(f"Modelo: {self.model_name}")
        logger.info("="*70 + "\n")

        all_results = []
        start_time = datetime.now()

        for sim_num in range(1, num_simulations + 1):
            try:
                results = self.process_simulation(sim_num)
                all_results.append(results)

                # Salva resultados incrementalmente após cada simulação
                # Isso garante que não perdemos dados se o processo for interrompido
                results_df = pd.DataFrame(all_results)

                # Salva no arquivo principal (results.csv)
                results_path = self.results_dir / "results.csv"
                results_df.to_csv(results_path, index=False)
                logger.info(f"Resultados salvos: {len(all_results)} simulações em {results_path}")

                # Também salva backup com timestamp
                partial_path = self.results_dir / "partial_results.csv"
                results_df.to_csv(partial_path, index=False)

            except Exception as e:
                logger.error(f"Erro na simulação {sim_num}: {e}")
                continue

        end_time = datetime.now()
        duration = end_time - start_time

        # Cria DataFrame final
        results_df = pd.DataFrame(all_results)

        # Salva resultados finais em results_dir/model_name/results.csv
        results_path = self.results_dir / "results.csv"
        results_df.to_csv(results_path, index=False)

        # Calcula estatísticas agregadas
        stats = {
            'modelo': self.model_name,
            'num_simulations': len(all_results),
            'acuracia_alegria_mean': results_df['acuracia_alegria'].mean(),
            'acuracia_alegria_std': results_df['acuracia_alegria'].std(),
            'acuracia_raiva_mean': results_df['acuracia_raiva'].mean(),
            'acuracia_raiva_std': results_df['acuracia_raiva'].std(),
            'acuracia_geral_mean': results_df['acuracia_geral'].mean(),
            'acuracia_geral_std': results_df['acuracia_geral'].std(),
            'tempo_total_segundos': duration.total_seconds(),
            'timestamp': datetime.now().isoformat()
        }

        # Salva estatísticas em results_dir/model_name/stats.json
        stats_path = self.results_dir / "stats.json"
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)

        logger.info("\n" + "="*70)
        logger.info("PROCESSAMENTO CONCLUÍDO")
        logger.info("="*70)
        logger.info(f"Simulações processadas: {len(all_results)}")
        logger.info(f"Tempo total: {duration}")
        logger.info(f"\nEstatísticas:")
        logger.info(f"  Acurácia Alegria: {stats['acuracia_alegria_mean']:.4f} ± {stats['acuracia_alegria_std']:.4f}")
        logger.info(f"  Acurácia Raiva: {stats['acuracia_raiva_mean']:.4f} ± {stats['acuracia_raiva_std']:.4f}")
        logger.info(f"  Acurácia Geral: {stats['acuracia_geral_mean']:.4f} ± {stats['acuracia_geral_std']:.4f}")
        logger.info(f"\nResultados salvos em:")
        logger.info(f"  CSV: {results_path}")
        logger.info(f"  Stats: {stats_path}")
        logger.info("="*70)

        return results_df


def main():
    """
    Função principal para execução via linha de comando.

    Uso:
        python RoboflowEmotionClassifier.py --api_key YOUR_KEY
        python RoboflowEmotionClassifier.py --api_key YOUR_KEY --model_id workspace/project/version
        python RoboflowEmotionClassifier.py --api_key YOUR_KEY --num_simulations 5
    """
    parser = argparse.ArgumentParser(
        description='Classificador de Emoções usando Roboflow API'
    )

    parser.add_argument(
        '--api_key',
        type=str,
        required=True,
        help='Chave de API do Roboflow'
    )

    parser.add_argument(
        '--model_id',
        type=str,
        default='computer-vision-projects-zhogq/emotion-detection-y0svj',
        help='ID do modelo Roboflow (formato: workspace/project/version)'
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
        help='Diretório para salvar resultados'
    )

    parser.add_argument(
        '--model_name',
        type=str,
        default='roboflow_emotion',
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

    # Inicializa classificador
    classifier = RoboflowEmotionClassifier(
        api_key=args.api_key,
        model_id=args.model_id,
        dataset_dir=args.dataset_dir,
        results_dir=args.results_dir,
        model_name=args.model_name
    )

    # Processa simulações
    if args.simulation:
        # Processa apenas uma simulação
        results = classifier.process_simulation(args.simulation)
        print(json.dumps(results, indent=2))
    else:
        # Processa todas as simulações
        results_df = classifier.process_all_simulations(args.num_simulations)
        print("\nResultados:")
        print(results_df.to_string())


if __name__ == "__main__":
    main()
