#!/usr/bin/env python3
"""
Fase 4: Testes Estatísticos

Este script realiza testes de hipótese pareados para comparar os modelos.

Testes realizados:
1. Teste de Wilcoxon pareado (não-paramétrico) - Principal
2. Teste t pareado (paramétrico) - Complementar
3. Cálculo de tamanhos de efeito (Cohen's d e r de Rosenthal)
4. Teste de normalidade (Shapiro-Wilk)

Saídas:
- results/wilcoxon_test_results.csv
- results/t_test_results.csv
- results/effect_sizes.csv
- results/normality_tests.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
from itertools import combinations

# Configurações
DATA_PATH = Path(__file__).parent / 'data' / 'consolidated_results.csv'
OUTPUT_PATH = Path(__file__).parent / 'results'


def teste_normalidade(df, metricas):
    """
    Realiza teste de Shapiro-Wilk para verificar normalidade.

    Args:
        df: DataFrame consolidado
        metricas: Lista de métricas para testar

    Returns:
        DataFrame com resultados
    """
    resultados = []

    for modelo in df['modelo'].unique():
        df_modelo = df[df['modelo'] == modelo]

        for metrica in metricas:
            if metrica not in df_modelo.columns:
                continue

            valores = df_modelo[metrica].dropna()

            if len(valores) < 3:
                continue

            # Teste de Shapiro-Wilk
            stat, p_value = stats.shapiro(valores)

            resultados.append({
                'Modelo': modelo,
                'Métrica': metrica,
                'Statistic': stat,
                'p_value': p_value,
                'Normal': 'Sim' if p_value > 0.05 else 'Não',
                'Alpha': 0.05
            })

    return pd.DataFrame(resultados)


def calcular_cohens_d(grupo1, grupo2):
    """
    Calcula Cohen's d (tamanho de efeito para teste t).

    Args:
        grupo1, grupo2: Arrays de valores

    Returns:
        float: Cohen's d
    """
    n1, n2 = len(grupo1), len(grupo2)
    var1, var2 = np.var(grupo1, ddof=1), np.var(grupo2, ddof=1)

    # Pooled standard deviation
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))

    # Cohen's d
    d = (np.mean(grupo1) - np.mean(grupo2)) / pooled_std

    return d


def interpretar_cohens_d(d):
    """
    Interpreta o valor de Cohen's d.

    Args:
        d: Valor de Cohen's d

    Returns:
        str: Interpretação
    """
    d_abs = abs(d)

    if d_abs < 0.2:
        return 'Trivial'
    elif d_abs < 0.5:
        return 'Pequeno'
    elif d_abs < 0.8:
        return 'Médio'
    else:
        return 'Grande'


def calcular_r_rosenthal(z, n):
    """
    Calcula r de Rosenthal (tamanho de efeito para Wilcoxon).

    Args:
        z: Valor Z do teste de Wilcoxon
        n: Tamanho da amostra

    Returns:
        float: r de Rosenthal
    """
    return abs(z) / np.sqrt(n)


def interpretar_r_rosenthal(r):
    """
    Interpreta o valor de r de Rosenthal.

    Args:
        r: Valor de r

    Returns:
        str: Interpretação
    """
    r_abs = abs(r)

    if r_abs < 0.1:
        return 'Trivial'
    elif r_abs < 0.3:
        return 'Pequeno'
    elif r_abs < 0.5:
        return 'Médio'
    else:
        return 'Grande'


def teste_wilcoxon_pareado(df, metricas):
    """
    Realiza teste de Wilcoxon pareado entre pares de modelos.

    Args:
        df: DataFrame consolidado
        metricas: Lista de métricas para comparar

    Returns:
        DataFrame com resultados
    """
    resultados = []
    modelos = sorted(df['modelo'].unique())

    # Gerar todos os pares de modelos
    pares = list(combinations(modelos, 2))

    for modelo1, modelo2 in pares:
        df_modelo1 = df[df['modelo'] == modelo1].sort_values('numero_simulacao')
        df_modelo2 = df[df['modelo'] == modelo2].sort_values('numero_simulacao')

        # Verificar se têm o mesmo número de simulações
        if len(df_modelo1) != len(df_modelo2):
            print(f"⚠️  {modelo1} e {modelo2} têm número diferente de simulações. Pulando...")
            continue

        for metrica in metricas:
            if metrica not in df_modelo1.columns or metrica not in df_modelo2.columns:
                continue

            valores1 = df_modelo1[metrica].values
            valores2 = df_modelo2[metrica].values

            # Teste de Wilcoxon pareado
            try:
                stat, p_value = stats.wilcoxon(valores1, valores2, alternative='two-sided')

                # Calcular Z para tamanho de efeito
                n = len(valores1)
                z = stats.norm.ppf(1 - p_value/2)  # Aproximação
                r = calcular_r_rosenthal(z, n)

                resultados.append({
                    'Comparação': f'{modelo1} vs {modelo2}',
                    'Métrica': metrica,
                    'Mediana_Modelo1': np.median(valores1),
                    'Mediana_Modelo2': np.median(valores2),
                    'Diferença': np.median(valores2) - np.median(valores1),
                    'Statistic': stat,
                    'p_value': p_value,
                    'Significativo': 'Sim' if p_value < 0.05 else 'Não',
                    'Tamanho_Efeito_r': r,
                    'Interpretação': interpretar_r_rosenthal(r),
                    'Alpha': 0.05
                })

            except Exception as e:
                print(f"⚠️  Erro ao calcular Wilcoxon para {modelo1} vs {modelo2}, {metrica}: {e}")

    return pd.DataFrame(resultados)


def teste_t_pareado(df, metricas):
    """
    Realiza teste t pareado entre pares de modelos.

    Args:
        df: DataFrame consolidado
        metricas: Lista de métricas para comparar

    Returns:
        DataFrame com resultados
    """
    resultados = []
    modelos = sorted(df['modelo'].unique())

    # Gerar todos os pares de modelos
    pares = list(combinations(modelos, 2))

    for modelo1, modelo2 in pares:
        df_modelo1 = df[df['modelo'] == modelo1].sort_values('numero_simulacao')
        df_modelo2 = df[df['modelo'] == modelo2].sort_values('numero_simulacao')

        # Verificar se têm o mesmo número de simulações
        if len(df_modelo1) != len(df_modelo2):
            continue

        for metrica in metricas:
            if metrica not in df_modelo1.columns or metrica not in df_modelo2.columns:
                continue

            valores1 = df_modelo1[metrica].values
            valores2 = df_modelo2[metrica].values

            # Teste t pareado
            try:
                stat, p_value = stats.ttest_rel(valores1, valores2)

                # Cohen's d
                d = calcular_cohens_d(valores1, valores2)

                resultados.append({
                    'Comparação': f'{modelo1} vs {modelo2}',
                    'Métrica': metrica,
                    'Média_Modelo1': np.mean(valores1),
                    'Média_Modelo2': np.mean(valores2),
                    'Diferença': np.mean(valores2) - np.mean(valores1),
                    't_statistic': stat,
                    'p_value': p_value,
                    'Significativo': 'Sim' if p_value < 0.05 else 'Não',
                    'Cohens_d': d,
                    'Interpretação': interpretar_cohens_d(d),
                    'Alpha': 0.05
                })

            except Exception as e:
                print(f"⚠️  Erro ao calcular teste t para {modelo1} vs {modelo2}, {metrica}: {e}")

    return pd.DataFrame(resultados)


def calcular_tamanhos_efeito(df, metricas):
    """
    Consolida tamanhos de efeito de ambos os testes.

    Args:
        df: DataFrame consolidado
        metricas: Lista de métricas

    Returns:
        DataFrame com tamanhos de efeito
    """
    resultados = []
    modelos = sorted(df['modelo'].unique())
    pares = list(combinations(modelos, 2))

    for modelo1, modelo2 in pares:
        df_modelo1 = df[df['modelo'] == modelo1].sort_values('numero_simulacao')
        df_modelo2 = df[df['modelo'] == modelo2].sort_values('numero_simulacao')

        if len(df_modelo1) != len(df_modelo2):
            continue

        for metrica in metricas:
            if metrica not in df_modelo1.columns or metrica not in df_modelo2.columns:
                continue

            valores1 = df_modelo1[metrica].values
            valores2 = df_modelo2[metrica].values

            # Cohen's d
            d = calcular_cohens_d(valores1, valores2)

            # r de Rosenthal (aproximação via Wilcoxon)
            try:
                stat, p_value = stats.wilcoxon(valores1, valores2)
                n = len(valores1)
                z = stats.norm.ppf(1 - p_value/2)
                r = calcular_r_rosenthal(z, n)
            except:
                r = np.nan

            resultados.append({
                'Comparação': f'{modelo1} vs {modelo2}',
                'Métrica': metrica,
                'Cohens_d': d,
                'Interpretação_d': interpretar_cohens_d(d),
                'r_Rosenthal': r,
                'Interpretação_r': interpretar_r_rosenthal(r) if not np.isnan(r) else 'N/A'
            })

    return pd.DataFrame(resultados)


def main():
    """Executa testes estatísticos."""

    print("="*100)
    print("FASE 4: TESTES ESTATÍSTICOS")
    print("="*100)
    print()

    # Carregar dados
    print("📂 Carregando dados consolidados...")
    df = pd.read_csv(DATA_PATH)
    print(f"✓ {len(df)} registros carregados ({df['modelo'].nunique()} modelos)\n")

    # Definir métricas para testar
    metricas = ['acuracia_geral', 'precisao_macro', 'recall_macro', 'f1_macro']

    # 1. Teste de Normalidade
    print("📊 Realizando teste de normalidade (Shapiro-Wilk)...")
    df_normalidade = teste_normalidade(df, metricas)
    output_normalidade = OUTPUT_PATH / 'normality_tests.csv'
    df_normalidade.to_csv(output_normalidade, index=False)
    print(f"✓ Resultados salvos em: {output_normalidade}\n")

    # Exibir resultados de normalidade
    print("Resultados do Teste de Normalidade:")
    print("-" * 100)
    for _, row in df_normalidade.iterrows():
        print(f"  {row['Modelo']:<20} | {row['Métrica']:<20} | p={row['p_value']:.4f} | Normal: {row['Normal']}")

    # 2. Teste de Wilcoxon
    print("\n\n📊 Realizando teste de Wilcoxon pareado...")
    df_wilcoxon = teste_wilcoxon_pareado(df, metricas)
    output_wilcoxon = OUTPUT_PATH / 'wilcoxon_test_results.csv'
    df_wilcoxon.to_csv(output_wilcoxon, index=False)
    print(f"✓ Resultados salvos em: {output_wilcoxon}\n")

    # Exibir resultados de Wilcoxon
    print("Resultados do Teste de Wilcoxon:")
    print("="*100)
    for _, row in df_wilcoxon.iterrows():
        sig_symbol = "***" if row['p_value'] < 0.001 else ("**" if row['p_value'] < 0.01 else ("*" if row['p_value'] < 0.05 else "ns"))
        print(f"\n{row['Comparação']} - {row['Métrica']}")
        print(f"  Mediana Modelo 1: {row['Mediana_Modelo1']:.4f}")
        print(f"  Mediana Modelo 2: {row['Mediana_Modelo2']:.4f}")
        print(f"  Diferença: {row['Diferença']:.4f}")
        print(f"  p-value: {row['p_value']:.6f} {sig_symbol}")
        print(f"  Significativo: {row['Significativo']} (α=0.05)")
        print(f"  Tamanho de Efeito (r): {row['Tamanho_Efeito_r']:.4f} ({row['Interpretação']})")

    # 3. Teste t Pareado
    print("\n\n📊 Realizando teste t pareado...")
    df_ttest = teste_t_pareado(df, metricas)
    output_ttest = OUTPUT_PATH / 't_test_results.csv'
    df_ttest.to_csv(output_ttest, index=False)
    print(f"✓ Resultados salvos em: {output_ttest}\n")

    # Exibir resultados de teste t
    print("Resultados do Teste t Pareado:")
    print("="*100)
    for _, row in df_ttest.iterrows():
        sig_symbol = "***" if row['p_value'] < 0.001 else ("**" if row['p_value'] < 0.01 else ("*" if row['p_value'] < 0.05 else "ns"))
        print(f"\n{row['Comparação']} - {row['Métrica']}")
        print(f"  Média Modelo 1: {row['Média_Modelo1']:.4f}")
        print(f"  Média Modelo 2: {row['Média_Modelo2']:.4f}")
        print(f"  Diferença: {row['Diferença']:.4f}")
        print(f"  p-value: {row['p_value']:.6f} {sig_symbol}")
        print(f"  Significativo: {row['Significativo']} (α=0.05)")
        print(f"  Cohen's d: {row['Cohens_d']:.4f} ({row['Interpretação']})")

    # 4. Tamanhos de Efeito Consolidados
    print("\n\n📊 Calculando tamanhos de efeito consolidados...")
    df_efeito = calcular_tamanhos_efeito(df, metricas)
    output_efeito = OUTPUT_PATH / 'effect_sizes.csv'
    df_efeito.to_csv(output_efeito, index=False)
    print(f"✓ Resultados salvos em: {output_efeito}\n")

    # Resumo final
    print("\n\n📈 RESUMO DOS TESTES ESTATÍSTICOS")
    print("="*100)
    print(f"\nNível de significância (α): 0.05")
    print(f"Número de comparações: {len(df_wilcoxon) // len(metricas)}")
    print(f"Métricas testadas: {', '.join(metricas)}")

    # Contagem de diferenças significativas
    sig_wilcoxon = df_wilcoxon[df_wilcoxon['Significativo'] == 'Sim']
    sig_ttest = df_ttest[df_ttest['Significativo'] == 'Sim']

    print(f"\nDiferenças significativas encontradas:")
    print(f"  Wilcoxon: {len(sig_wilcoxon)}/{len(df_wilcoxon)} testes")
    print(f"  Teste t: {len(sig_ttest)}/{len(df_ttest)} testes")

    print("\n\n✅ Fase 4 concluída com sucesso!")
    print("="*100)


if __name__ == '__main__':
    main()
