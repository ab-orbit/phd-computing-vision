#!/usr/bin/env python3
"""
Script para adicionar métricas de classificação (precisão, recall, f1-score)
aos arquivos CSV de resultados dos classificadores.

Uso:
    python add_metrics.py <caminho_para_results.csv>

Exemplo:
    python add_metrics.py 3_simulation/results/roboflow_emotion/results.csv
    python add_metrics.py 3_simulation/results/simple_cnn/results.csv
    python add_metrics.py 3_simulation/results/yolo11_emotion/results.csv

O script:
1. Lê o CSV de resultados
2. Calcula precisão, recall e f1-score para cada classe e macro
3. Atualiza o CSV com novas colunas
4. Atualiza stats.json com estatísticas das novas métricas
"""

import pandas as pd
import numpy as np
import json
import sys
from pathlib import Path


def calcular_metricas(row):
    """
    Calcula precisão, recall e f1-score para classificação binária.

    Para classificação binária (alegria vs raiva), calculamos
    a matriz de confusão e as métricas para cada classe.

    Args:
        row: Linha do DataFrame com colunas:
            - qtd_sucesso_alegria: VP para alegria
            - qtd_sucesso_raiva: VP para raiva
            - total_alegria: Total de imagens de alegria
            - total_raiva: Total de imagens de raiva

    Returns:
        pd.Series com métricas calculadas
    """

    # Verdadeiros Positivos e Falsos Negativos
    vp_alegria = row['qtd_sucesso_alegria']
    fn_alegria = row['total_alegria'] - vp_alegria
    vp_raiva = row['qtd_sucesso_raiva']
    fn_raiva = row['total_raiva'] - vp_raiva

    # Falsos Positivos (classificação binária)
    # Em classificação binária: FP de uma classe = FN da outra
    fp_alegria = fn_raiva  # Raiva classificada como alegria
    fp_raiva = fn_alegria  # Alegria classificada como raiva

    # Precisão para alegria
    if (vp_alegria + fp_alegria) > 0:
        precisao_alegria = vp_alegria / (vp_alegria + fp_alegria)
    else:
        precisao_alegria = 0.0

    # Recall para alegria
    if (vp_alegria + fn_alegria) > 0:
        recall_alegria = vp_alegria / (vp_alegria + fn_alegria)
    else:
        recall_alegria = 0.0

    # F1-score para alegria
    if (precisao_alegria + recall_alegria) > 0:
        f1_alegria = 2 * (precisao_alegria * recall_alegria) / (precisao_alegria + recall_alegria)
    else:
        f1_alegria = 0.0

    # Precisão para raiva
    if (vp_raiva + fp_raiva) > 0:
        precisao_raiva = vp_raiva / (vp_raiva + fp_raiva)
    else:
        precisao_raiva = 0.0

    # Recall para raiva
    if (vp_raiva + fn_raiva) > 0:
        recall_raiva = vp_raiva / (vp_raiva + fn_raiva)
    else:
        recall_raiva = 0.0

    # F1-score para raiva
    if (precisao_raiva + recall_raiva) > 0:
        f1_raiva = 2 * (precisao_raiva * recall_raiva) / (precisao_raiva + recall_raiva)
    else:
        f1_raiva = 0.0

    # Média macro (média simples das métricas de cada classe)
    precisao_macro = (precisao_alegria + precisao_raiva) / 2
    recall_macro = (recall_alegria + recall_raiva) / 2
    f1_macro = (f1_alegria + f1_raiva) / 2

    return pd.Series({
        'precisao_alegria': precisao_alegria,
        'recall_alegria': recall_alegria,
        'f1_alegria': f1_alegria,
        'precisao_raiva': precisao_raiva,
        'recall_raiva': recall_raiva,
        'f1_raiva': f1_raiva,
        'precisao_macro': precisao_macro,
        'recall_macro': recall_macro,
        'f1_macro': f1_macro
    })


def adicionar_metricas_csv(csv_path):
    """
    Adiciona métricas ao CSV de resultados.

    Args:
        csv_path: Caminho para arquivo CSV

    Returns:
        DataFrame atualizado
    """
    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")

    print(f"Processando: {csv_path}")

    # Lê CSV
    df = pd.read_csv(csv_path)

    # Remove linhas vazias
    df = df.dropna(subset=['numero_simulacao'])

    print(f"  Total de simulações: {len(df)}")

    # Verifica se colunas necessárias existem
    required_cols = ['qtd_sucesso_alegria', 'qtd_sucesso_raiva',
                     'total_alegria', 'total_raiva']

    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Colunas faltando no CSV: {missing_cols}")

    # Calcula métricas
    print("  Calculando métricas...")
    metricas = df.apply(calcular_metricas, axis=1)

    # Adiciona colunas de métricas
    df = pd.concat([df, metricas], axis=1)

    # Reordena colunas
    colunas_base = [
        'numero_simulacao',
        'nome_modelo',
        'qtd_sucesso_alegria',
        'qtd_sucesso_raiva',
        'total_alegria',
        'total_raiva',
        'tempo_total_ms',
        'acuracia_alegria',
        'acuracia_raiva',
        'acuracia_geral'
    ]

    colunas_metricas = [
        'precisao_alegria',
        'recall_alegria',
        'f1_alegria',
        'precisao_raiva',
        'recall_raiva',
        'f1_raiva',
        'precisao_macro',
        'recall_macro',
        'f1_macro'
    ]

    # Mantém outras colunas que possam existir
    outras_colunas = [col for col in df.columns
                     if col not in colunas_base + colunas_metricas]

    colunas_ordenadas = colunas_base + colunas_metricas + outras_colunas
    df = df[[col for col in colunas_ordenadas if col in df.columns]]

    # Salva CSV atualizado
    df.to_csv(csv_path, index=False)
    print(f"  CSV atualizado: {csv_path}")

    return df


def atualizar_stats_json(df, results_dir):
    """
    Atualiza arquivo stats.json com estatísticas das novas métricas.

    Args:
        df: DataFrame com resultados
        results_dir: Diretório dos resultados
    """
    results_dir = Path(results_dir)
    stats_path = results_dir / 'stats.json'

    # Lê stats.json existente (se houver)
    if stats_path.exists():
        with open(stats_path, 'r') as f:
            stats = json.load(f)
    else:
        stats = {}

    # Adiciona estatísticas das novas métricas
    stats.update({
        # Precisão
        'precisao_alegria_mean': float(df['precisao_alegria'].mean()),
        'precisao_alegria_std': float(df['precisao_alegria'].std()),
        'precisao_raiva_mean': float(df['precisao_raiva'].mean()),
        'precisao_raiva_std': float(df['precisao_raiva'].std()),
        'precisao_macro_mean': float(df['precisao_macro'].mean()),
        'precisao_macro_std': float(df['precisao_macro'].std()),

        # Recall
        'recall_alegria_mean': float(df['recall_alegria'].mean()),
        'recall_alegria_std': float(df['recall_alegria'].std()),
        'recall_raiva_mean': float(df['recall_raiva'].mean()),
        'recall_raiva_std': float(df['recall_raiva'].std()),
        'recall_macro_mean': float(df['recall_macro'].mean()),
        'recall_macro_std': float(df['recall_macro'].std()),

        # F1-Score
        'f1_alegria_mean': float(df['f1_alegria'].mean()),
        'f1_alegria_std': float(df['f1_alegria'].std()),
        'f1_raiva_mean': float(df['f1_raiva'].mean()),
        'f1_raiva_std': float(df['f1_raiva'].std()),
        'f1_macro_mean': float(df['f1_macro'].mean()),
        'f1_macro_std': float(df['f1_macro'].std())
    })

    # Salva stats.json
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"  stats.json atualizado: {stats_path}")


def main():
    """Função principal."""
    if len(sys.argv) < 2:
        print("Uso: python add_metrics.py <caminho_para_results.csv>")
        print("\nExemplos:")
        print("  python add_metrics.py 3_simulation/results/roboflow_emotion/results.csv")
        print("  python add_metrics.py 3_simulation/results/simple_cnn/results.csv")
        print("  python add_metrics.py 3_simulation/results/yolo11_emotion/results.csv")
        sys.exit(1)

    csv_path = Path(sys.argv[1])

    try:
        # Adiciona métricas ao CSV
        df = adicionar_metricas_csv(csv_path)

        # Atualiza stats.json
        results_dir = csv_path.parent
        atualizar_stats_json(df, results_dir)

        # Mostra resumo
        print("\n" + "="*70)
        print("RESUMO DAS MÉTRICAS")
        print("="*70)
        print(f"\nAcurácia:")
        print(f"  Alegria: {df['acuracia_alegria'].mean():.4f} ± {df['acuracia_alegria'].std():.4f}")
        print(f"  Raiva:   {df['acuracia_raiva'].mean():.4f} ± {df['acuracia_raiva'].std():.4f}")
        print(f"  Geral:   {df['acuracia_geral'].mean():.4f} ± {df['acuracia_geral'].std():.4f}")
        print(f"\nPrecisão:")
        print(f"  Alegria: {df['precisao_alegria'].mean():.4f} ± {df['precisao_alegria'].std():.4f}")
        print(f"  Raiva:   {df['precisao_raiva'].mean():.4f} ± {df['precisao_raiva'].std():.4f}")
        print(f"  Macro:   {df['precisao_macro'].mean():.4f} ± {df['precisao_macro'].std():.4f}")
        print(f"\nRecall:")
        print(f"  Alegria: {df['recall_alegria'].mean():.4f} ± {df['recall_alegria'].std():.4f}")
        print(f"  Raiva:   {df['recall_raiva'].mean():.4f} ± {df['recall_raiva'].std():.4f}")
        print(f"  Macro:   {df['recall_macro'].mean():.4f} ± {df['recall_macro'].std():.4f}")
        print(f"\nF1-Score:")
        print(f"  Alegria: {df['f1_alegria'].mean():.4f} ± {df['f1_alegria'].std():.4f}")
        print(f"  Raiva:   {df['f1_raiva'].mean():.4f} ± {df['f1_raiva'].std():.4f}")
        print(f"  Macro:   {df['f1_macro'].mean():.4f} ± {df['f1_macro'].std():.4f}")
        print("="*70)
        print("\nProcessamento concluído com sucesso!")

    except Exception as e:
        print(f"\nERRO: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
