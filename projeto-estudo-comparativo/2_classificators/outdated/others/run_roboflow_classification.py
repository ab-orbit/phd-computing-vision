"""
Script para Executar Classificação Roboflow com API Key do .env

Este script carrega automaticamente a API key do arquivo .env
e executa a classificação usando o modelo Roboflow.

Uso:
    # Processar apenas simulação 1 (teste)
    python run_roboflow_classification.py --simulation 1

    # Processar primeiras 5 simulações
    python run_roboflow_classification.py --num_simulations 5

    # Processar todas as 30 simulações
    python run_roboflow_classification.py --num_simulations 30
"""

import os
import sys
from pathlib import Path
import argparse
from dotenv import load_dotenv

# Adiciona diretório raiz ao path para importar o classificador
sys.path.insert(0, str(Path(__file__).parent))

from RoboflowEmotionClassifier import RoboflowEmotionClassifier


def load_api_key():
    """
    Carrega API key do arquivo .env na raiz do projeto.

    O arquivo .env deve conter:
    ROBOFLOW_API_KEY=sua_chave_aqui

    Returns:
        API key string

    Raises:
        ValueError: Se API key não for encontrada
    """
    # Localiza arquivo .env na raiz do projeto
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / '.env'

    if not env_path.exists():
        raise FileNotFoundError(
            f"Arquivo .env não encontrado em {env_path}\n"
            "Crie o arquivo .env com: ROBOFLOW_API_KEY=sua_chave_aqui"
        )

    # Carrega variáveis de ambiente
    load_dotenv(env_path)

    # Obtém API key
    api_key = os.getenv('ROBOFLOW_API_KEY')

    if not api_key:
        raise ValueError(
            "ROBOFLOW_API_KEY não encontrada no arquivo .env\n"
            "Adicione a linha: ROBOFLOW_API_KEY=sua_chave_aqui"
        )

    print(f"API key carregada do .env: {api_key[:10]}...")
    return api_key


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description='Executa Classificação Roboflow (API key do .env)'
    )

    parser.add_argument(
        '--model_id',
        type=str,
        default='computer-vision-projects-zhogq/emotion-detection-y0svj',
        help='ID do modelo Roboflow'
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
        help='Processar apenas uma simulação específica (1-30)'
    )

    args = parser.parse_args()

    try:
        # Carrega API key do .env
        print("Carregando API key do arquivo .env...")
        api_key = load_api_key()

        # Inicializa classificador
        print("\nInicializando classificador Roboflow...")
        classifier = RoboflowEmotionClassifier(
            api_key=api_key,
            model_id=args.model_id,
            dataset_dir=args.dataset_dir,
            results_dir=args.results_dir,
            model_name=args.model_name
        )

        # Processa simulações
        if args.simulation:
            print(f"\nProcessando apenas simulação {args.simulation}...")
            results = classifier.process_simulation(args.simulation)
            print("\nResultados:")
            for key, value in results.items():
                print(f"  {key}: {value}")
        else:
            print(f"\nProcessando {args.num_simulations} simulações...")
            print("ATENÇÃO: Isso pode levar várias horas e consumir créditos de API!")
            print("Pressione Ctrl+C para cancelar nos próximos 5 segundos...\n")

            import time
            for i in range(5, 0, -1):
                print(f"{i}...")
                time.sleep(1)

            print("\nIniciando processamento...\n")
            results_df = classifier.process_all_simulations(args.num_simulations)

            print("\nResumo dos Resultados:")
            print(results_df.describe())

    except FileNotFoundError as e:
        print(f"\nERRO: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"\nERRO: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nProcessamento cancelado pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\nERRO inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
