#!/usr/bin/env python3
"""
Fase 2: Estatísticas Descritivas

Este script calcula estatísticas descritivas completas para todos os modelos.

Análises:
1. Por Modelo - Métricas Gerais (média, DP, mediana, min, max, quartis)
2. Métricas principais: acurácia, precisão, recall, f1-score, tempo
3. Análise por classe (alegria vs raiva)

Saídas:
- results/descriptive_stats_summary.csv - Tabela resumo
- results/descriptive_stats_detailed.json - Estatísticas completas
- results/stats_by_class.csv - Estatísticas por classe
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

# Configurações
DATA_PATH = Path(__file__).parent / 'data' / 'consolidated_results.csv'
OUTPUT_PATH = Path(__file__).parent / 'results'


def calcular_estatisticas_descritivas(df, metricas):
    """
    Calcula estatísticas descritivas para cada modelo e métrica.

    Args:
        df: DataFrame consolidado
        metricas: Lista de colunas de métricas para analisar

    Returns:
        DataFrame com estatísticas
    """
    resultados = []

    for modelo in df['modelo'].unique():
        df_modelo = df[df['modelo'] == modelo]

        for metrica in metricas:
            if metrica not in df_modelo.columns:
                continue

            valores = df_modelo[metrica]

            stats = {
                'Modelo': modelo,
                'Métrica': metrica,
                'Média': valores.mean(),
                'DP': valores.std(),
                'Mediana': valores.median(),
                'Min': valores.min(),
                'Max': valores.max(),
                'Q1': valores.quantile(0.25),
                'Q3': valores.quantile(0.75),
                'IQR': valores.quantile(0.75) - valores.quantile(0.25),
                'N': len(valores)
            }

            resultados.append(stats)

    return pd.DataFrame(resultados)


def calcular_estatisticas_por_classe(df):
    """
    Calcula estatísticas separadas para as classes alegria e raiva.

    Args:
        df: DataFrame consolidado

    Returns:
        DataFrame com estatísticas por classe
    """
    resultados = []

    metricas_por_classe = {
        'alegria': ['acuracia_alegria', 'precisao_alegria', 'recall_alegria', 'f1_alegria'],
        'raiva': ['acuracia_raiva', 'precisao_raiva', 'recall_raiva', 'f1_raiva']
    }

    for modelo in df['modelo'].unique():
        df_modelo = df[df['modelo'] == modelo]

        for classe, metricas in metricas_por_classe.items():
            for metrica in metricas:
                if metrica not in df_modelo.columns:
                    continue

                valores = df_modelo[metrica]
                nome_metrica = metrica.replace(f'_{classe}', '')

                stats = {
                    'Modelo': modelo,
                    'Classe': classe.capitalize(),
                    'Métrica': nome_metrica.capitalize(),
                    'Média': valores.mean(),
                    'DP': valores.std(),
                    'Mediana': valores.median(),
                    'Min': valores.min(),
                    'Max': valores.max()
                }

                resultados.append(stats)

    return pd.DataFrame(resultados)


def gerar_estatisticas_detalhadas(df):
    """
    Gera dicionário com estatísticas detalhadas em formato hierárquico.

    Args:
        df: DataFrame consolidado

    Returns:
        dict com estatísticas detalhadas
    """
    estatisticas = {}

    for modelo in df['modelo'].unique():
        df_modelo = df[df['modelo'] == modelo]
        estatisticas[modelo] = {}

        # Métricas gerais
        metricas_gerais = ['acuracia_geral', 'precisao_macro', 'recall_macro', 'f1_macro', 'tempo_total_ms']

        for metrica in metricas_gerais:
            if metrica not in df_modelo.columns:
                continue

            valores = df_modelo[metrica]

            # Converter tempo de ms para segundos
            if metrica == 'tempo_total_ms':
                valores = valores / 1000

            estatisticas[modelo][metrica] = {
                'media': float(valores.mean()),
                'desvio_padrao': float(valores.std()),
                'mediana': float(valores.median()),
                'minimo': float(valores.min()),
                'maximo': float(valores.max()),
                'q1': float(valores.quantile(0.25)),
                'q3': float(valores.quantile(0.75)),
                'iqr': float(valores.quantile(0.75) - valores.quantile(0.25)),
                'n_simulacoes': int(len(valores))
            }

        # Métricas por classe
        estatisticas[modelo]['por_classe'] = {}

        for classe in ['alegria', 'raiva']:
            estatisticas[modelo]['por_classe'][classe] = {}

            metricas_classe = [f'acuracia_{classe}', f'precisao_{classe}', f'recall_{classe}', f'f1_{classe}']

            for metrica_completa in metricas_classe:
                if metrica_completa not in df_modelo.columns:
                    continue

                valores = df_modelo[metrica_completa]
                nome_metrica = metrica_completa.replace(f'_{classe}', '')

                estatisticas[modelo]['por_classe'][classe][nome_metrica] = {
                    'media': float(valores.mean()),
                    'desvio_padrao': float(valores.std()),
                    'mediana': float(valores.median()),
                    'minimo': float(valores.min()),
                    'maximo': float(valores.max())
                }

    return estatisticas


def exibir_resumo_console(df_summary):
    """
    Exibe resumo formatado no console.

    Args:
        df_summary: DataFrame com estatísticas resumidas
    """
    print("\n" + "="*100)
    print("RESUMO ESTATÍSTICO POR MODELO")
    print("="*100)

    for modelo in df_summary['Modelo'].unique():
        print(f"\n{'='*100}")
        print(f"  {modelo}")
        print(f"{'='*100}\n")

        df_modelo = df_summary[df_summary['Modelo'] == modelo]

        # Formatar como tabela
        print(f"{'Métrica':<20} {'Média':>10} {'DP':>10} {'Mediana':>10} {'Min':>10} {'Max':>10}")
        print("-" * 100)

        for _, row in df_modelo.iterrows():
            metrica = row['Métrica']
            if 'tempo' in metrica.lower():
                # Converter ms para s
                print(f"{metrica:<20} {row['Média']/1000:>10.2f}s {row['DP']/1000:>9.2f}s "
                      f"{row['Mediana']/1000:>9.2f}s {row['Min']/1000:>9.2f}s {row['Max']/1000:>9.2f}s")
            else:
                print(f"{metrica:<20} {row['Média']:>10.4f} {row['DP']:>10.4f} "
                      f"{row['Mediana']:>10.4f} {row['Min']:>10.4f} {row['Max']:>10.4f}")


def main():
    """Executa análise de estatísticas descritivas."""

    print("="*100)
    print("FASE 2: ESTATÍSTICAS DESCRITIVAS")
    print("="*100)
    print()

    # Carregar dados consolidados
    print("📂 Carregando dados consolidados...")
    df = pd.read_csv(DATA_PATH)
    print(f"✓ {len(df)} registros carregados ({df['modelo'].nunique()} modelos)")

    # Definir métricas a analisar
    metricas_principais = [
        'acuracia_geral',
        'acuracia_alegria',
        'acuracia_raiva',
        'precisao_macro',
        'recall_macro',
        'f1_macro',
        'tempo_total_ms'
    ]

    # Calcular estatísticas descritivas
    print("\n📊 Calculando estatísticas descritivas...")
    df_stats = calcular_estatisticas_descritivas(df, metricas_principais)

    # Salvar resumo
    output_summary = OUTPUT_PATH / 'descriptive_stats_summary.csv'
    df_stats.to_csv(output_summary, index=False)
    print(f"✓ Resumo salvo em: {output_summary}")

    # Calcular estatísticas por classe
    print("\n📊 Calculando estatísticas por classe...")
    df_stats_class = calcular_estatisticas_por_classe(df)

    # Salvar estatísticas por classe
    output_class = OUTPUT_PATH / 'stats_by_class.csv'
    df_stats_class.to_csv(output_class, index=False)
    print(f"✓ Estatísticas por classe salvas em: {output_class}")

    # Gerar estatísticas detalhadas em JSON
    print("\n📊 Gerando estatísticas detalhadas...")
    stats_detailed = gerar_estatisticas_detalhadas(df)

    # Salvar JSON
    output_json = OUTPUT_PATH / 'descriptive_stats_detailed.json'
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(stats_detailed, f, indent=2, ensure_ascii=False)
    print(f"✓ Estatísticas detalhadas salvas em: {output_json}")

    # Exibir resumo no console
    exibir_resumo_console(df_stats)

    # Exibir estatísticas por classe
    print("\n\n" + "="*100)
    print("ESTATÍSTICAS POR CLASSE")
    print("="*100)

    for modelo in df_stats_class['Modelo'].unique():
        print(f"\n{modelo}")
        print("-" * 100)

        df_modelo_class = df_stats_class[df_stats_class['Modelo'] == modelo]

        for classe in df_modelo_class['Classe'].unique():
            df_classe = df_modelo_class[df_modelo_class['Classe'] == classe]

            print(f"\n  {classe}:")
            print(f"  {'Métrica':<15} {'Média':>10} {'DP':>10} {'Mediana':>10}")
            print(f"  {'-' * 50}")

            for _, row in df_classe.iterrows():
                print(f"  {row['Métrica']:<15} {row['Média']:>10.4f} {row['DP']:>10.4f} {row['Mediana']:>10.4f}")

    print("\n\n✅ Fase 2 concluída com sucesso!")
    print("="*100)


if __name__ == '__main__':
    main()
