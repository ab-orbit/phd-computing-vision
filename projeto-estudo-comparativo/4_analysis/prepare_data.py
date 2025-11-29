#!/usr/bin/env python3
"""
Fase 1: Preparação e Validação de Dados

Este script valida e consolida os dados dos classificadores de emoções
para análise comparativa.

Funcionalidades:
1. Verificar existência dos arquivos CSV
2. Validar integridade dos dados (30 simulações, colunas corretas)
3. Verificar presença de valores nulos ou inconsistentes
4. Consolidar dados em estrutura unificada
5. Gerar relatório de validação

Saídas:
- data/consolidated_results.csv - Dados consolidados de todos os modelos
- data/data_validation_report.txt - Relatório de validação
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Configurações
BASE_PATH = Path(__file__).parent.parent / '3_simulation' / 'results'
OUTPUT_PATH = Path(__file__).parent / 'data'

# Modelos a analisar
MODELS = {
    'google_vision_emotion': 'Google Vision',
    'roboflow_emotion': 'Roboflow',
    'yolo11_emotion': 'YOLO11'
}

# Colunas esperadas
REQUIRED_COLUMNS = [
    'numero_simulacao', 'nome_modelo',
    'qtd_sucesso_alegria', 'qtd_sucesso_raiva',
    'total_alegria', 'total_raiva',
    'tempo_total_ms',
    'acuracia_alegria', 'acuracia_raiva', 'acuracia_geral',
    'precisao_alegria', 'recall_alegria', 'f1_alegria',
    'precisao_raiva', 'recall_raiva', 'f1_raiva',
    'precisao_macro', 'recall_macro', 'f1_macro'
]


def validar_dataset(caminho_csv, nome_modelo):
    """
    Valida CSV de resultados de um modelo.

    Args:
        caminho_csv: Path do arquivo CSV
        nome_modelo: Nome amigável do modelo

    Returns:
        tuple: (DataFrame validado ou None, lista de problemas encontrados)
    """
    problemas = []

    # Verificar existência
    if not caminho_csv.exists():
        problemas.append(f"❌ Arquivo não encontrado: {caminho_csv}")
        return None, problemas

    problemas.append(f"✓ Arquivo encontrado: {caminho_csv}")

    # Carregar CSV
    try:
        df = pd.read_csv(caminho_csv)
    except Exception as e:
        problemas.append(f"❌ Erro ao ler CSV: {e}")
        return None, problemas

    problemas.append(f"✓ CSV carregado com sucesso")

    # Validar número de simulações
    num_sims = len(df)
    if num_sims != 30:
        problemas.append(f"⚠️  Esperado 30 simulações, encontrado {num_sims}")
    else:
        problemas.append(f"✓ 30 simulações encontradas")

    # Validar colunas
    colunas_faltantes = set(REQUIRED_COLUMNS) - set(df.columns)
    if colunas_faltantes:
        problemas.append(f"⚠️  Colunas faltantes: {colunas_faltantes}")
    else:
        problemas.append(f"✓ Todas as colunas necessárias presentes")

    # Verificar valores nulos em colunas críticas
    colunas_criticas = ['acuracia_geral', 'precisao_macro', 'recall_macro', 'f1_macro']
    for col in colunas_criticas:
        if col in df.columns:
            nulos = df[col].isnull().sum()
            if nulos > 0:
                problemas.append(f"⚠️  {nulos} valores nulos em '{col}'")
            else:
                problemas.append(f"✓ Sem valores nulos em '{col}'")

    # Verificar valores fora do intervalo [0, 1] para métricas
    metricas = [col for col in df.columns if any(x in col for x in ['acuracia', 'precisao', 'recall', 'f1'])]
    for col in metricas:
        if col in df.columns:
            fora_range = ((df[col] < 0) | (df[col] > 1)).sum()
            if fora_range > 0:
                problemas.append(f"⚠️  {fora_range} valores fora do intervalo [0,1] em '{col}'")

    # Verificar valores negativos em contagens
    colunas_contagem = ['qtd_sucesso_alegria', 'qtd_sucesso_raiva', 'total_alegria', 'total_raiva']
    for col in colunas_contagem:
        if col in df.columns:
            negativos = (df[col] < 0).sum()
            if negativos > 0:
                problemas.append(f"⚠️  {negativos} valores negativos em '{col}'")

    # Verificar consistência de totais
    if 'total_alegria' in df.columns and 'total_raiva' in df.columns:
        total_alegria_unico = df['total_alegria'].nunique()
        total_raiva_unico = df['total_raiva'].nunique()

        if total_alegria_unico == 1 and total_raiva_unico == 1:
            problemas.append(f"✓ Totais consistentes: {df['total_alegria'].iloc[0]} alegria, {df['total_raiva'].iloc[0]} raiva")
        else:
            problemas.append(f"⚠️  Totais inconsistentes entre simulações")

    # Adicionar coluna identificadora do modelo
    df['modelo'] = nome_modelo

    return df, problemas


def consolidar_dados(dataframes):
    """
    Consolida múltiplos DataFrames em um único.

    Args:
        dataframes: Lista de tuplas (nome_modelo, DataFrame)

    Returns:
        DataFrame consolidado
    """
    dfs_validos = []

    for nome_modelo, df in dataframes:
        if df is not None:
            dfs_validos.append(df)

    if not dfs_validos:
        raise ValueError("Nenhum DataFrame válido para consolidar")

    # Concatenar todos os DataFrames
    df_consolidated = pd.concat(dfs_validos, ignore_index=True)

    # Ordenar por modelo e número de simulação
    df_consolidated = df_consolidated.sort_values(['modelo', 'numero_simulacao']).reset_index(drop=True)

    return df_consolidated


def gerar_relatorio_validacao(resultados_validacao, output_path):
    """
    Gera relatório de validação em formato texto.

    Args:
        resultados_validacao: Lista de tuplas (nome_modelo, problemas)
        output_path: Path para salvar o relatório
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("RELATÓRIO DE VALIDAÇÃO DE DADOS\n")
        f.write("Análise Comparativa de Classificadores de Emoções\n")
        f.write("="*80 + "\n\n")

        for nome_modelo, problemas in resultados_validacao:
            f.write(f"\n{nome_modelo}\n")
            f.write("-" * len(nome_modelo) + "\n\n")

            for problema in problemas:
                f.write(f"{problema}\n")

            f.write("\n")

        f.write("\n" + "="*80 + "\n")
        f.write("FIM DO RELATÓRIO\n")
        f.write("="*80 + "\n")


def main():
    """Executa a preparação e validação de dados."""

    print("="*80)
    print("FASE 1: PREPARAÇÃO E VALIDAÇÃO DE DADOS")
    print("="*80)
    print()

    resultados_validacao = []
    dataframes = []

    # Validar cada modelo
    for modelo_dir, nome_modelo in MODELS.items():
        print(f"\n📊 Validando {nome_modelo}...")
        print("-" * 80)

        caminho_csv = BASE_PATH / modelo_dir / 'results.csv'
        df, problemas = validar_dataset(caminho_csv, nome_modelo)

        # Exibir problemas
        for problema in problemas:
            print(f"  {problema}")

        resultados_validacao.append((nome_modelo, problemas))
        dataframes.append((nome_modelo, df))

    # Consolidar dados
    print("\n\n📦 Consolidando dados...")
    print("-" * 80)

    try:
        df_consolidated = consolidar_dados(dataframes)
        print(f"✓ Dados consolidados com sucesso")
        print(f"  Total de registros: {len(df_consolidated)}")
        print(f"  Modelos incluídos: {df_consolidated['modelo'].nunique()}")
        print(f"  Simulações por modelo:")
        for modelo in df_consolidated['modelo'].unique():
            count = len(df_consolidated[df_consolidated['modelo'] == modelo])
            print(f"    - {modelo}: {count} simulações")

        # Salvar dados consolidados
        output_csv = OUTPUT_PATH / 'consolidated_results.csv'
        df_consolidated.to_csv(output_csv, index=False)
        print(f"\n✓ Dados consolidados salvos em: {output_csv}")

    except Exception as e:
        print(f"\n❌ Erro ao consolidar dados: {e}")
        sys.exit(1)

    # Gerar relatório de validação
    print("\n\n📄 Gerando relatório de validação...")
    print("-" * 80)

    output_report = OUTPUT_PATH / 'data_validation_report.txt'
    gerar_relatorio_validacao(resultados_validacao, output_report)
    print(f"✓ Relatório salvo em: {output_report}")

    # Estatísticas gerais
    print("\n\n📈 Estatísticas Gerais")
    print("=" * 80)
    print(f"\nModelos analisados: {df_consolidated['modelo'].nunique()}")
    print(f"Total de simulações: {len(df_consolidated)}")
    print(f"\nMétricas disponíveis:")
    metricas_cols = [col for col in df_consolidated.columns if any(x in col for x in ['acuracia', 'precisao', 'recall', 'f1'])]
    for col in metricas_cols:
        print(f"  - {col}")

    print("\n\n✅ Fase 1 concluída com sucesso!")
    print("="*80)

    return df_consolidated


if __name__ == '__main__':
    df = main()
