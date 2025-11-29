#!/usr/bin/env python3
"""
Script de execução para Google Vision Emotion Classifier

Este script facilita a execução do classificador carregando
automaticamente as configurações do arquivo .env.

Uso:
    python run_google_vision.py --num_simulations 30
    python run_google_vision.py --simulation 1
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import argparse

# Adiciona diretório do projeto ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Importa classificador
from GoogleVisionEmotionClassifier import GoogleVisionEmotionClassifier

# Configuração de logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_api_key():
    """
    Carrega API key do arquivo .env.

    Returns:
        str: API key do Google Cloud

    Raises:
        SystemExit: Se API key não for encontrada
    """
    # Carrega .env do diretório raiz do projeto
    env_path = project_root / '.env'

    if not env_path.exists():
        logger.error(f"Arquivo .env não encontrado em: {env_path}")
        logger.error("\nCrie o arquivo .env com:")
        logger.error("GOOGLE_API_KEY=sua_chave_aqui")
        sys.exit(1)

    load_dotenv(env_path)
    api_key = os.getenv('GOOGLE_API_KEY')

    if not api_key:
        logger.error("GOOGLE_API_KEY não encontrada no .env")
        logger.error(f"Arquivo: {env_path}")
        logger.error("\nAdicione ao .env:")
        logger.error("GOOGLE_API_KEY=sua_chave_aqui")
        sys.exit(1)

    logger.info(f"API key carregada de: {env_path}")
    logger.info(f"API key: {api_key[:10]}...{api_key[-4:]}")

    return api_key


def main():
    """
    Função principal.
    """
    parser = argparse.ArgumentParser(
        description='Executa Google Vision Emotion Classifier'
    )

    parser.add_argument(
        '--dataset_dir',
        type=str,
        default='datasets',
        help='Diretório do dataset (padrão: datasets)'
    )

    parser.add_argument(
        '--results_dir',
        type=str,
        default='3_simulation/results',
        help='Diretório para resultados (padrão: 3_simulation/results)'
    )

    parser.add_argument(
        '--model_name',
        type=str,
        default='google_vision_emotion',
        help='Nome identificador do modelo (padrão: google_vision_emotion)'
    )

    parser.add_argument(
        '--num_simulations',
        type=int,
        default=30,
        help='Número de simulações a processar (padrão: 30)'
    )

    parser.add_argument(
        '--simulation',
        type=int,
        help='Processar apenas uma simulação específica'
    )

    args = parser.parse_args()

    # Carrega API key
    api_key = load_api_key()

    # Inicializa classificador
    logger.info("\nInicializando Google Vision Emotion Classifier...")
    classifier = GoogleVisionEmotionClassifier(
        api_key=api_key,
        dataset_dir=args.dataset_dir,
        results_dir=args.results_dir,
        model_name=args.model_name
    )

    # Processa simulações
    if args.simulation:
        # Processa apenas uma simulação
        logger.info(f"\nProcessando simulação {args.simulation}...")
        results = classifier.process_simulation(args.simulation)

        # Salva resultado
        import pandas as pd
        results_df = pd.DataFrame([results])
        results_path = classifier.results_dir / "results.csv"
        results_df.to_csv(results_path, index=False)

        logger.info(f"\nResultado salvo em: {results_path}")
        logger.info(f"Acurácia: {results['acuracia_geral']:.2%}")
    else:
        # Processa todas as simulações
        logger.info(f"\nProcessando {args.num_simulations} simulações...")
        results_df = classifier.process_all_simulations(args.num_simulations)

        logger.info("\nProcessamento concluído!")
        logger.info(f"Resultados: {classifier.results_dir}/results.csv")


if __name__ == "__main__":
    main()
