#!/usr/bin/env python3
"""
Script para selecionar amostras aleatórias do dataset RVL-CDIP.

Este script copia N amostras de cada categoria especificada para um
diretório de saída, facilitando testes e experimentação.

Uso:
    python sample_selector.py --dataset-path ../rvlp/data/test --num-samples 10

Explicação dos parâmetros:
    --dataset-path: Caminho para o diretório contendo as categorias
    --num-samples: Número de amostras a copiar por categoria
    --output-dir: Diretório onde as amostras serão salvas
    --categories: Lista de categorias a processar (padrão: email, advertisement, scientific_publication)
    --seed: Semente para reprodutibilidade da seleção aleatória
"""

import argparse
import random
import shutil
from pathlib import Path
from typing import List, Dict
import json


def select_samples(
    dataset_path: Path,
    categories: List[str],
    num_samples: int,
    output_dir: Path,
    seed: int = 42
) -> Dict[str, List[Path]]:
    """
    Seleciona amostras aleatórias de cada categoria.

    Argumentos:
        dataset_path: Caminho base do dataset
        categories: Lista de categorias para processar
        num_samples: Número de amostras por categoria
        output_dir: Diretório de saída
        seed: Semente para random

    Retorna:
        Dicionário com categoria -> lista de caminhos copiados
    """
    random.seed(seed)
    selected_samples = {}

    print("=" * 80)
    print("SELEÇÃO DE AMOSTRAS DO DATASET RVL-CDIP")
    print("=" * 80)
    print(f"\nDataset base: {dataset_path}")
    print(f"Categorias: {', '.join(categories)}")
    print(f"Amostras por categoria: {num_samples}")
    print(f"Diretório de saída: {output_dir}")
    print(f"Semente aleatória: {seed}\n")

    # Criar diretório de saída
    output_dir.mkdir(parents=True, exist_ok=True)

    for category in categories:
        print(f"\nProcessando categoria: {category}")
        print("-" * 80)

        # Caminho da categoria no dataset
        category_path = dataset_path / category

        if not category_path.exists():
            print(f"⚠️  AVISO: Categoria não encontrada: {category_path}")
            selected_samples[category] = []
            continue

        # Listar todas as imagens
        images = list(category_path.glob('*.tif'))

        if len(images) == 0:
            print(f"⚠️  AVISO: Nenhuma imagem encontrada em: {category_path}")
            selected_samples[category] = []
            continue

        print(f"Total de imagens disponíveis: {len(images)}")

        # Selecionar N amostras aleatórias
        if len(images) < num_samples:
            print(f"⚠️  AVISO: Apenas {len(images)} imagens disponíveis, "
                  f"menor que {num_samples} solicitado")
            samples = images
        else:
            samples = random.sample(images, num_samples)

        print(f"Amostras selecionadas: {len(samples)}")

        # Criar diretório de saída para categoria
        category_output = output_dir / category
        category_output.mkdir(parents=True, exist_ok=True)

        # Copiar amostras
        copied_paths = []
        for i, sample_path in enumerate(samples, 1):
            dest_path = category_output / sample_path.name
            shutil.copy2(sample_path, dest_path)
            copied_paths.append(dest_path)
            print(f"  [{i}/{len(samples)}] {sample_path.name} → {dest_path}")

        selected_samples[category] = copied_paths
        print(f"✓ Categoria '{category}': {len(copied_paths)} amostras copiadas")

    # Salvar manifesto JSON
    manifest = {
        'dataset_path': str(dataset_path),
        'categories': categories,
        'num_samples_requested': num_samples,
        'seed': seed,
        'samples': {
            cat: [str(p) for p in paths]
            for cat, paths in selected_samples.items()
        },
        'total_samples': sum(len(paths) for paths in selected_samples.values())
    }

    manifest_path = output_dir / 'manifest.json'
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print("\n" + "=" * 80)
    print("RESUMO")
    print("=" * 80)
    for category, paths in selected_samples.items():
        print(f"{category:30s}: {len(paths):3d} amostras")
    print("-" * 80)
    print(f"{'TOTAL':30s}: {sum(len(p) for p in selected_samples.values()):3d} amostras")
    print(f"\nManifesto salvo em: {manifest_path}")
    print("=" * 80)

    return selected_samples


def main():
    """Função principal - parse de argumentos e execução."""
    parser = argparse.ArgumentParser(
        description='Seleciona amostras aleatórias do dataset RVL-CDIP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Selecionar 10 amostras de cada categoria
  python sample_selector.py --dataset-path ../rvlp/data/test --num-samples 10

  # Selecionar 5 amostras apenas de email e advertisement
  python sample_selector.py --dataset-path ../rvlp/data/test --num-samples 5 \\
      --categories email advertisement

  # Selecionar com semente específica para reprodutibilidade
  python sample_selector.py --dataset-path ../rvlp/data/test --num-samples 10 \\
      --seed 123
        """
    )

    parser.add_argument(
        '--dataset-path',
        type=str,
        required=True,
        help='Caminho para o diretório base do dataset (ex: ../rvlp/data/test)'
    )

    parser.add_argument(
        '--num-samples',
        type=int,
        default=10,
        help='Número de amostras por categoria (padrão: 10)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='sample',
        help='Diretório de saída para as amostras (padrão: sample)'
    )

    parser.add_argument(
        '--categories',
        nargs='+',
        default=['email', 'advertisement', 'scientific_publication'],
        help='Categorias a processar (padrão: email advertisement scientific_publication)'
    )

    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Semente para seleção aleatória (padrão: 42)'
    )

    args = parser.parse_args()

    # Converter para Path
    dataset_path = Path(args.dataset_path)
    output_dir = Path(args.output_dir)

    # Validar dataset_path
    if not dataset_path.exists():
        print(f"❌ ERRO: Caminho do dataset não existe: {dataset_path}")
        return 1

    # Executar seleção
    try:
        selected_samples = select_samples(
            dataset_path=dataset_path,
            categories=args.categories,
            num_samples=args.num_samples,
            output_dir=output_dir,
            seed=args.seed
        )

        if sum(len(paths) for paths in selected_samples.values()) == 0:
            print("\n❌ ERRO: Nenhuma amostra foi selecionada!")
            return 1

        print("\n✓ Seleção de amostras concluída com sucesso!")
        return 0

    except Exception as e:
        print(f"\n❌ ERRO durante seleção: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
