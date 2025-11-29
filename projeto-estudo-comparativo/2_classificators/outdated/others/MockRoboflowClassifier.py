"""
Mock Classificador Roboflow - Para Testes Sem API

Este módulo simula o comportamento do classificador Roboflow
sem fazer chamadas reais à API. Útil para:
1. Desenvolvimento e testes
2. Validação do pipeline sem consumir créditos de API
3. Prototipagem rápida

ATENÇÃO: Este é um MOCK. As predições são simuladas e não representam
desempenho real do modelo Roboflow.

Estratégia de Simulação:
------------------------
- Usa heurísticas simples baseadas em propriedades da imagem
- Simula variabilidade de acurácia realista
- Mantém mesmo formato de saída do classificador real
"""

import os
import sys
from pathlib import Path
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List
import argparse
import logging
from PIL import Image
import time
import random

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockRoboflowClassifier:
    """
    Classificador Mock que simula comportamento do Roboflow.

    Este classificador NÃO faz chamadas à API real. Ele simula predições
    usando heurísticas simples para permitir testes do pipeline completo.

    Heurísticas usadas:
    1. Brilho médio da imagem (imagens mais claras = maior chance de alegria)
    2. Ruído aleatório para simular variabilidade
    3. Acurácia simulada: ~70-80% (realista para modelos foundation)
    """

    def __init__(
        self,
        dataset_dir: str = "datasets",
        results_dir: str = "3_simulation/results",
        model_name: str = "mock_roboflow",
        base_accuracy: float = 0.75,
        seed: int = 42
    ):
        """
        Inicializa o classificador mock.

        Args:
            dataset_dir: Diretório do dataset
            results_dir: Diretório para salvar resultados
            model_name: Nome identificador do modelo
            base_accuracy: Acurácia base simulada (0.0-1.0)
            seed: Semente para reprodutibilidade
        """
        self.dataset_dir = Path(dataset_dir)
        self.model_name = model_name
        self.base_accuracy = base_accuracy
        self.seed = seed

        # Define seed para reprodutibilidade
        random.seed(seed)
        np.random.seed(seed)

        # Cria diretório de resultados: results_dir/model_name/
        self.results_dir = Path(results_dir) / model_name
        self.results_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"MockRoboflowClassifier inicializado:")
        logger.info(f"  Dataset: {self.dataset_dir}")
        logger.info(f"  Resultados: {self.results_dir}")
        logger.info(f"  Acurácia base: {self.base_accuracy:.2%}")
        logger.info(f"  ATENÇÃO: Este é um classificador MOCK (não usa API real)")

    def _calculate_image_features(self, image_path: Path) -> Dict:
        """
        Calcula características simples da imagem.

        Extrai features básicas que serão usadas para simular predição:
        - Brilho médio
        - Desvio padrão de intensidade
        - Proporção de pixels claros

        Args:
            image_path: Caminho para a imagem

        Returns:
            Dicionário com features
        """
        try:
            img = Image.open(image_path).convert('L')  # Converte para grayscale
            pixels = np.array(img)

            features = {
                'mean_brightness': pixels.mean(),
                'std_brightness': pixels.std(),
                'bright_pixel_ratio': (pixels > 128).mean()
            }

            return features

        except Exception as e:
            logger.error(f"Erro ao processar imagem {image_path}: {e}")
            return {
                'mean_brightness': 128,
                'std_brightness': 50,
                'bright_pixel_ratio': 0.5
            }

    def predict_image(self, image_path: Path, true_class: str) -> Dict:
        """
        Simula predição de emoção em uma imagem.

        Estratégia de simulação:
        1. Extrai features da imagem
        2. Usa heurística: imagens mais claras = mais provável alegria
        3. Adiciona ruído aleatório para simular variabilidade
        4. Decide se acerta ou erra baseado em base_accuracy

        Args:
            image_path: Caminho para a imagem
            true_class: Classe verdadeira ('raiva' ou 'alegria')

        Returns:
            Dicionário com predição simulada
        """
        # Extrai features
        features = self._calculate_image_features(image_path)

        # Heurística: imagens mais claras tendem a ser alegria
        brightness_score = features['mean_brightness'] / 255.0

        # Adiciona ruído aleatório
        noise = np.random.normal(0, 0.1)
        score = np.clip(brightness_score + noise, 0, 1)

        # Decide predição
        # Score alto = alegria, Score baixo = raiva
        predicted_class = 'alegria' if score > 0.5 else 'raiva'

        # Simula erro baseado em base_accuracy
        # Com probabilidade (1 - base_accuracy), inverte predição
        if random.random() > self.base_accuracy:
            predicted_class = 'raiva' if predicted_class == 'alegria' else 'alegria'

        # Calcula confiança simulada
        confidence = abs(score - 0.5) * 2  # 0.5 = incerto, 0/1 = muito certo
        confidence = np.clip(confidence + np.random.normal(0, 0.1), 0.5, 1.0)

        # Simula tempo de inferência (~100-500ms)
        inference_time = random.uniform(100, 500)

        return {
            'predictions': [
                {
                    'class': predicted_class,
                    'confidence': float(confidence)
                }
            ],
            'image': str(image_path),
            'inference_time_ms': inference_time,
            'is_correct': predicted_class == true_class,
            'features': features
        }

    def process_simulation(self, simulation_num: int) -> Dict:
        """
        Processa todas as imagens de uma simulação.

        Args:
            simulation_num: Número da simulação (1-30)

        Returns:
            Dicionário com métricas da simulação
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"Processando Simulação {simulation_num:02d} (MOCK)")
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
                # Faz predição simulada
                prediction_result = self.predict_image(image_path, class_name)

                # Verifica acerto
                if prediction_result['is_correct']:
                    successes += 1

                # Log de progresso
                if idx % 10 == 0:
                    logger.info(f"  Processadas: {idx}/{len(image_files)} imagens")

                # Simula pequeno delay (muito menor que API real)
                time.sleep(0.001)  # 1ms

            # Atualiza resultados
            if class_name == 'alegria':
                results['qtd_sucesso_alegria'] = successes
                results['total_alegria'] = len(image_files)
            else:
                results['qtd_sucesso_raiva'] = successes
                results['total_raiva'] = len(image_files)

            logger.info(f"  Acertos: {successes}/{len(image_files)}")

        # Calcula métricas
        results['tempo_total_ms'] = (time.time() - start_time) * 1000

        if results['total_alegria'] > 0:
            results['acuracia_alegria'] = results['qtd_sucesso_alegria'] / results['total_alegria']
        else:
            results['acuracia_alegria'] = 0.0

        if results['total_raiva'] > 0:
            results['acuracia_raiva'] = results['qtd_sucesso_raiva'] / results['total_raiva']
        else:
            results['acuracia_raiva'] = 0.0

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

        return results

    def process_all_simulations(self, num_simulations: int = 30) -> pd.DataFrame:
        """
        Processa todas as simulações.

        Args:
            num_simulations: Número de simulações

        Returns:
            DataFrame com resultados
        """
        logger.info("\n" + "="*70)
        logger.info("INICIANDO PROCESSAMENTO - MOCK ROBOFLOW")
        logger.info("="*70)
        logger.info("ATENÇÃO: Usando classificador MOCK (não usa API real)")
        logger.info(f"Acurácia base simulada: {self.base_accuracy:.2%}")
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

        # DataFrame final
        results_df = pd.DataFrame(all_results)

        # Salva resultados em results_dir/model_name/results.csv
        results_path = self.results_dir / "results.csv"
        results_df.to_csv(results_path, index=False)

        # Estatísticas
        stats = {
            'modelo': self.model_name,
            'is_mock': True,
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

        stats_path = self.results_dir / "stats.json"
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)

        logger.info("\n" + "="*70)
        logger.info("PROCESSAMENTO CONCLUÍDO (MOCK)")
        logger.info("="*70)
        logger.info(f"Simulações: {len(all_results)}")
        logger.info(f"Tempo: {duration}")
        logger.info(f"\nEstatísticas:")
        logger.info(f"  Acurácia Alegria: {stats['acuracia_alegria_mean']:.4f} ± {stats['acuracia_alegria_std']:.4f}")
        logger.info(f"  Acurácia Raiva: {stats['acuracia_raiva_mean']:.4f} ± {stats['acuracia_raiva_std']:.4f}")
        logger.info(f"  Acurácia Geral: {stats['acuracia_geral_mean']:.4f} ± {stats['acuracia_geral_std']:.4f}")
        logger.info(f"\nResultados salvos em: {results_path}")
        logger.info("="*70)

        return results_df


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description='Mock Classificador Roboflow (sem API)'
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
        default='mock_roboflow',
        help='Nome do modelo'
    )

    parser.add_argument(
        '--base_accuracy',
        type=float,
        default=0.75,
        help='Acurácia base simulada (0.0-1.0)'
    )

    parser.add_argument(
        '--num_simulations',
        type=int,
        default=30,
        help='Número de simulações'
    )

    parser.add_argument(
        '--simulation',
        type=int,
        help='Processar apenas uma simulação'
    )

    args = parser.parse_args()

    # Inicializa classificador mock
    classifier = MockRoboflowClassifier(
        dataset_dir=args.dataset_dir,
        results_dir=args.results_dir,
        model_name=args.model_name,
        base_accuracy=args.base_accuracy
    )

    # Processa
    if args.simulation:
        results = classifier.process_simulation(args.simulation)
        print(json.dumps(results, indent=2))
    else:
        results_df = classifier.process_all_simulations(args.num_simulations)
        print("\nResultados:")
        print(results_df.to_string())


if __name__ == "__main__":
    main()
