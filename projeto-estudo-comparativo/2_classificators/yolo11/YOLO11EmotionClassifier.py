"""
Classificador de Emoções usando YOLO11

Este módulo implementa um classificador de emoções faciais (raiva vs alegria)
usando o modelo YOLO11 (Ultralytics) diretamente, sem APIs externas.

Objetivo Pedagógico:
-------------------
Demonstrar o uso de modelos foundation locais (YOLO11) para classificação
de emoções, comparando com:
- CNNs tradicionais treinadas do zero
- Modelos via API (Roboflow)

Vantagens do YOLO11 Local:
1. Sem custo por requisição (após download do modelo)
2. Sem latência de rede
3. Funciona offline
4. Controle total sobre inferência
5. Pode ser fine-tunado facilmente

Desvantagens:
1. Requer GPU para velocidade ideal
2. Modelo pode ser grande (~200MB)
3. Precisa configurar ambiente local

YOLO11 (You Only Look Once v11):
--------------------------------
- Modelo de detecção e classificação de objetos da Ultralytics
- Versão mais recente da família YOLO (2024)
- Arquitetura otimizada para velocidade e precisão
- Suporta classificação de imagens diretamente

Instalação:
----------
pip install ultralytics opencv-python pillow

Uso:
----
python YOLO11EmotionClassifier.py --num_simulations 30
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


class YOLO11EmotionClassifier:
    """
    Classificador de emoções usando YOLO11 local.

    Este classificador usa o modelo YOLO11 da Ultralytics rodando
    localmente (sem API) para classificar imagens em duas categorias:
    raiva e alegria.

    Diferente do Roboflow:
    - Roda localmente (sem chamadas de API)
    - Mais rápido (sem latência de rede)
    - Sem custo por requisição
    - Requer hardware adequado (GPU recomendado)

    Attributes:
        model: Modelo YOLO11 carregado
        dataset_dir (Path): Diretório do dataset
        results_dir (Path): Diretório para salvar resultados
        model_name (str): Nome do modelo para identificação
    """

    def __init__(
        self,
        model_type: str = "yolov8n-cls.pt",
        dataset_dir: str = "datasets",
        results_dir: str = "3_simulation/results",
        model_name: str = "yolo11_emotion",
        device: str = "auto"
    ):
        """
        Inicializa o classificador YOLO11.

        Args:
            model_type: Tipo do modelo YOLO (YOLOv8 Classification)
                - yolov8n-cls.pt: Nano (mais rápido, menos preciso)
                - yolov8s-cls.pt: Small
                - yolov8m-cls.pt: Medium
                - yolov8l-cls.pt: Large
                - yolov8x-cls.pt: Extra Large (mais lento, mais preciso)
            dataset_dir: Caminho para o diretório datasets/
            results_dir: Caminho para salvar resultados
            model_name: Nome identificador do modelo
            device: Dispositivo de inferência ('auto', 'cpu', 'cuda', 'mps')

        Nota sobre Modelos:
            YOLOv8 oferece trade-off entre velocidade e precisão.
            Para este projeto, usamos yolov8n-cls (nano) por ser rápido
            e suficiente para classificação binária.

            IMPORTANTE: Ultralytics faz download automático do modelo
            na primeira execução (~3-5MB para nano model).
        """
        self.model_type = model_type
        self.dataset_dir = Path(dataset_dir)
        self.model_name = model_name
        self.device = device

        # Cria diretório de resultados: results_dir/model_name/
        self.results_dir = Path(results_dir) / model_name
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Mapeamento de emoções para nossas classes
        # YOLO11 será fine-tunado ou usaremos transfer learning
        # Por enquanto, assumimos que detecta emoções genéricas
        self.emotion_mapping = {
            # Raiva e variações
            'angry': 'raiva',
            'anger': 'raiva',
            'mad': 'raiva',

            # Alegria e variações
            'happy': 'alegria',
            'joy': 'alegria',
            'smile': 'alegria',

            # Outras emoções (ignoradas)
            'sad': None,
            'neutral': None,
            'fear': None,
            'surprise': None,
        }

        # Inicializa modelo YOLO11
        self._initialize_yolo()

        logger.info(f"YOLO11EmotionClassifier inicializado:")
        logger.info(f"  Modelo: {self.model_type}")
        logger.info(f"  Dataset: {self.dataset_dir}")
        logger.info(f"  Resultados: {self.results_dir}")
        logger.info(f"  Dispositivo: {self.device}")

    def _initialize_yolo(self):
        """
        Inicializa modelo YOLOv8 Classification.

        Tenta importar e carregar o modelo YOLOv8 da Ultralytics.
        Se o modelo não existir localmente, faz download automaticamente.

        Estratégia:
        1. Tenta importar ultralytics
        2. Carrega modelo pré-treinado (download automático se necessário)
        3. Configura para modo de classificação
        4. Detecta dispositivo disponível (GPU/CPU)

        Raises:
            ImportError: Se ultralytics não estiver instalado
            Exception: Se não conseguir carregar o modelo
        """
        try:
            from ultralytics import YOLO

            logger.info(f"Carregando modelo YOLOv8: {self.model_type}")

            # Carrega modelo pré-treinado
            # Ultralytics faz download automaticamente se não existir localmente
            # O modelo será baixado para ~/.cache/ultralytics/
            logger.info("NOTA: Se for a primeira execução, o modelo será baixado (~3-10MB)")
            logger.info("Isso pode levar alguns segundos...")

            self.model = YOLO(self.model_type)
            logger.info(f"Modelo {self.model_type} carregado com sucesso")

            # Configura dispositivo
            if self.device == "auto":
                import torch
                if torch.cuda.is_available():
                    self.device = "cuda"
                    logger.info("GPU CUDA detectada - usando aceleração GPU")
                elif torch.backends.mps.is_available():
                    self.device = "mps"
                    logger.info("Apple Silicon (MPS) detectado - usando aceleração GPU")
                else:
                    self.device = "cpu"
                    logger.info("Usando CPU (pode ser lento)")

            logger.info(f"Modelo YOLO11 carregado com sucesso")
            logger.info(f"Dispositivo final: {self.device}")

        except ImportError:
            logger.error("Ultralytics não encontrado. Instalando...")
            logger.info("Execute: pip install ultralytics")
            raise ImportError(
                "Ultralytics YOLO não instalado. Execute: pip install ultralytics"
            )
        except Exception as e:
            logger.error(f"Erro ao carregar modelo YOLO11: {e}")
            raise

    def predict_image(self, image_path: Path) -> Dict:
        """
        Faz predição de emoção em uma única imagem usando YOLO11.

        YOLO11 Classification Mode:
        - Analisa imagem completa
        - Retorna probabilidades para cada classe
        - Muito rápido (especialmente com GPU)

        Args:
            image_path: Caminho para a imagem

        Returns:
            Dicionário com predições no formato:
            {
                'predictions': [
                    {'class': 'happy', 'confidence': 0.95},
                    ...
                ],
                'image': str(image_path),
                'inference_time_ms': float
            }

        Nota sobre Performance:
            YOLO11 é extremamente rápido:
            - Com GPU: ~2-5ms por imagem
            - Com CPU: ~20-50ms por imagem
        """
        try:
            start_time = time.time()

            # Faz predição usando YOLO11
            # verbose=False para não poluir logs
            results = self.model.predict(
                source=str(image_path),
                device=self.device,
                verbose=False
            )

            inference_time = (time.time() - start_time) * 1000  # em ms

            # Processa resultados
            # YOLO11 retorna lista de resultados (1 item para 1 imagem)
            result = results[0]

            # Extrai predições
            predictions = []

            if hasattr(result, 'probs'):
                # Modo classificação
                probs = result.probs

                # Pega top-5 classes com maiores probabilidades
                top5_indices = probs.top5
                top5_conf = probs.top5conf.cpu().numpy()

                # Nomes das classes (se disponível)
                if hasattr(result, 'names'):
                    names = result.names
                    for idx, conf in zip(top5_indices, top5_conf):
                        predictions.append({
                            'class': names[idx],
                            'confidence': float(conf)
                        })
                else:
                    # Se nomes não disponíveis, usa índices
                    for idx, conf in zip(top5_indices, top5_conf):
                        predictions.append({
                            'class': f'class_{idx}',
                            'confidence': float(conf)
                        })

            return {
                'predictions': predictions,
                'image': str(image_path),
                'inference_time_ms': inference_time
            }

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
        Classifica emoção baseado nas predições do YOLO11.

        Estratégia:
        1. Filtra predições com confiança > 0.4
        2. Mapeia classes detectadas para nossas categorias (raiva/alegria)
        3. Retorna classe com maior confiança
        4. Se nenhuma classe reconhecida, retorna 'unknown'

        Args:
            predictions: Lista de predições do modelo

        Returns:
            'raiva', 'alegria' ou 'unknown'

        Nota Pedagógica:
            Como YOLO11 pode não ter classes específicas de emoções
            em seu treinamento base, esta função faz o mapeamento
            entre classes genéricas e nossas categorias de interesse.
        """
        if not predictions:
            return 'unknown'

        # Filtra predições com confiança suficiente
        confident_preds = [
            p for p in predictions
            if p.get('confidence', 0) > 0.4
        ]

        if not confident_preds:
            return 'unknown'

        # Mapeia para nossas classes
        mapped_emotions = []
        for pred in confident_preds:
            class_name = pred.get('class', '').lower()
            mapped_emotion = self.emotion_mapping.get(class_name)

            if mapped_emotion:
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

        Pipeline idêntico ao Roboflow mas com YOLO11 local.

        Args:
            simulation_num: Número da simulação (1-30)

        Returns:
            Dicionário com métricas da simulação
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"Processando Simulação {simulation_num:02d}")
        logger.info(f"{'='*70}")

        sim_dir = self.dataset_dir / f"sim{simulation_num:02d}"

        if not sim_dir.exists():
            raise FileNotFoundError(
                f"Simulação {simulation_num} não encontrada em {sim_dir}"
            )

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
            image_files = [
                f for f in image_files
                if f.suffix.lower() in ['.png', '.jpg', '.jpeg']
            ]

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

                # Verifica acerto
                is_correct = predicted_emotion == class_name
                if is_correct:
                    successes += 1

                # Log de progresso
                if idx % 10 == 0:
                    logger.info(f"  Processadas: {idx}/{len(image_files)} imagens")

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
            results['acuracia_alegria'] = \
                results['qtd_sucesso_alegria'] / results['total_alegria']
        else:
            results['acuracia_alegria'] = 0.0

        if results['total_raiva'] > 0:
            results['acuracia_raiva'] = \
                results['qtd_sucesso_raiva'] / results['total_raiva']
        else:
            results['acuracia_raiva'] = 0.0

        # Acurácia geral
        total_images = results['total_alegria'] + results['total_raiva']
        total_successes = \
            results['qtd_sucesso_alegria'] + results['qtd_sucesso_raiva']

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

        Idêntico ao Roboflow mas usando YOLO11 local.
        Salva incrementalmente após cada simulação.

        Args:
            num_simulations: Número de simulações a processar

        Returns:
            DataFrame com resultados de todas as simulações
        """
        logger.info("\n" + "="*70)
        logger.info("INICIANDO PROCESSAMENTO - YOLO11")
        logger.info("="*70)
        logger.info(f"Total de simulações: {num_simulations}")
        logger.info(f"Modelo: {self.model_name}")
        logger.info(f"Dispositivo: {self.device}")
        logger.info("="*70 + "\n")

        all_results = []
        start_time = datetime.now()

        for sim_num in range(1, num_simulations + 1):
            try:
                results = self.process_simulation(sim_num)
                all_results.append(results)

                # Salva resultados incrementalmente após cada simulação
                results_df = pd.DataFrame(all_results)

                # Salva no arquivo principal (results.csv)
                results_path = self.results_dir / "results.csv"
                results_df.to_csv(results_path, index=False)
                logger.info(
                    f"Resultados salvos: {len(all_results)} simulações "
                    f"em {results_path}"
                )

                # Também salva backup
                partial_path = self.results_dir / "partial_results.csv"
                results_df.to_csv(partial_path, index=False)

            except Exception as e:
                logger.error(f"Erro na simulação {sim_num}: {e}")
                continue

        end_time = datetime.now()
        duration = end_time - start_time

        # DataFrame final
        results_df = pd.DataFrame(all_results)

        # Salva resultados finais
        results_path = self.results_dir / "results.csv"
        results_df.to_csv(results_path, index=False)

        # Estatísticas
        stats = {
            'modelo': self.model_name,
            'model_type': self.model_type,
            'device': self.device,
            'num_simulations': len(all_results),
            'acuracia_alegria_mean': results_df['acuracia_alegria'].mean(),
            'acuracia_alegria_std': results_df['acuracia_alegria'].std(),
            'acuracia_raiva_mean': results_df['acuracia_raiva'].mean(),
            'acuracia_raiva_std': results_df['acuracia_raiva'].std(),
            'acuracia_geral_mean': results_df['acuracia_geral'].mean(),
            'acuracia_geral_std': results_df['acuracia_geral'].std(),
            'tempo_total_segundos': duration.total_seconds(),
            'tempo_medio_por_simulacao': duration.total_seconds() / len(all_results),
            'timestamp': datetime.now().isoformat()
        }

        stats_path = self.results_dir / "stats.json"
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)

        logger.info("\n" + "="*70)
        logger.info("PROCESSAMENTO CONCLUÍDO - YOLO11")
        logger.info("="*70)
        logger.info(f"Simulações: {len(all_results)}")
        logger.info(f"Tempo total: {duration}")
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
        logger.info("="*70)

        return results_df


def main():
    """
    Função principal para execução via linha de comando.

    Uso:
        python YOLO11EmotionClassifier.py --num_simulations 30
        python YOLO11EmotionClassifier.py --simulation 1 --model_type yolov8s-cls.pt
    """
    parser = argparse.ArgumentParser(
        description='Classificador de Emoções usando YOLO11'
    )

    parser.add_argument(
        '--model_type',
        type=str,
        default='yolov8n-cls.pt',
        choices=['yolov8n-cls.pt', 'yolov8s-cls.pt', 'yolov8m-cls.pt',
                 'yolov8l-cls.pt', 'yolov8x-cls.pt'],
        help='Tipo do modelo YOLOv8 Classification'
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
        default='yolo11_emotion',
        help='Nome identificador do modelo'
    )

    parser.add_argument(
        '--device',
        type=str,
        default='auto',
        choices=['auto', 'cpu', 'cuda', 'mps'],
        help='Dispositivo de inferência'
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
    classifier = YOLO11EmotionClassifier(
        model_type=args.model_type,
        dataset_dir=args.dataset_dir,
        results_dir=args.results_dir,
        model_name=args.model_name,
        device=args.device
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
