"""
Script para análise exploratória básica do dataset Fashion Product Images.

Este script gera estatísticas descritivas, análise de distribuições e
identifica potenciais problemas nos dados (valores faltantes, duplicatas, etc.).
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple

from config import (
    STYLES_CSV, IMAGES_CSV, STYLES_JSON_DIR,
    OUTPUTS_DIR, FIGURES_DIR, FIGURE_SIZE, SEABORN_STYLE,
    COLOR_PALETTE, RANDOM_SEED, IMAGES_DIR
)

# Configurar estilo de visualização
sns.set_style(SEABORN_STYLE)
plt.rcParams['figure.figsize'] = FIGURE_SIZE


def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Carrega os dados dos CSVs.

    Returns:
        Tupla com (styles_df, images_df)
    """
    print("Carregando dados...")
    styles_df = pd.read_csv(STYLES_CSV, on_bad_lines='skip')
    images_df = pd.read_csv(IMAGES_CSV, on_bad_lines='skip')

    print(f"[OK] Styles CSV: {len(styles_df):,} registros")
    print(f"[OK] Images CSV: {len(images_df):,} registros")

    return styles_df, images_df


def analyze_basic_stats(df: pd.DataFrame) -> Dict:
    """
    Analisa estatísticas básicas do dataset.

    Args:
        df: DataFrame do styles.csv

    Returns:
        Dicionário com estatísticas
    """
    print("\n[ANALISE] Análise de Estatísticas Básicas:")

    stats = {
        'total_records': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isnull().sum().to_dict(),
        'duplicates': df.duplicated().sum(),
        'unique_ids': df['id'].nunique(),
    }

    print(f"  Total de registros: {stats['total_records']:,}")
    print(f"  Total de colunas: {stats['total_columns']}")
    print(f"  Registros duplicados: {stats['duplicates']}")
    print(f"  IDs únicos: {stats['unique_ids']:,}")

    # Valores faltantes
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print("\n  [AVISO]  Valores faltantes por coluna:")
        for col, count in missing[missing > 0].items():
            pct = (count / len(df)) * 100
            print(f"    - {col}: {count:,} ({pct:.2f}%)")
    else:
        print("  [OK] Nenhum valor faltante detectado")

    return stats


def analyze_categories(df: pd.DataFrame) -> Dict:
    """
    Analisa a distribuição de categorias.

    Args:
        df: DataFrame do styles.csv

    Returns:
        Dicionário com distribuições
    """
    print("\n[ANALISE] Análise de Categorias:")

    distributions = {}

    # Categorias para analisar
    category_cols = ['gender', 'masterCategory', 'subCategory',
                     'articleType', 'baseColour', 'season', 'usage']

    for col in category_cols:
        if col in df.columns:
            dist = df[col].value_counts()
            distributions[col] = dist.to_dict()

            print(f"\n  {col} ({df[col].nunique()} categorias únicas):")
            print(f"    Top 5:")
            for cat, count in dist.head(5).items():
                pct = (count / len(df)) * 100
                print(f"      - {cat}: {count:,} ({pct:.2f}%)")

    return distributions


def analyze_temporal(df: pd.DataFrame) -> Dict:
    """
    Analisa a distribuição temporal (anos).

    Args:
        df: DataFrame do styles.csv

    Returns:
        Dicionário com estatísticas temporais
    """
    print("\n[ANALISE] Análise Temporal:")

    if 'year' in df.columns:
        year_dist = df['year'].value_counts().sort_index()

        print(f"  Anos disponíveis: {df['year'].min()} - {df['year'].max()}")
        print(f"  Distribuição por ano:")
        for year, count in year_dist.items():
            pct = (count / len(df)) * 100
            print(f"    - {year}: {count:,} ({pct:.2f}%)")

        return {'year_distribution': year_dist.to_dict()}

    return {}


def check_data_integrity(styles_df: pd.DataFrame, images_df: pd.DataFrame) -> Dict:
    """
    Verifica a integridade dos dados entre CSVs e arquivos.

    Args:
        styles_df: DataFrame do styles.csv
        images_df: DataFrame do images.csv

    Returns:
        Dicionário com resultados de integridade
    """
    print("\n[VERIFICACAO] Verificação de Integridade:")

    # IDs em cada fonte
    styles_ids = set(styles_df['id'].astype(str))
    images_ids = set(images_df['filename'].str.replace('.jpg', ''))

    # Verificar arquivos de imagem
    actual_images = set([f.stem for f in IMAGES_DIR.glob('*.jpg')])

    # Verificar JSONs
    actual_jsons = set([f.stem for f in STYLES_JSON_DIR.glob('*.json')])

    # Comparações
    missing_images = styles_ids - actual_images
    missing_jsons = styles_ids - actual_jsons
    orphan_images = actual_images - styles_ids
    orphan_jsons = actual_jsons - styles_ids

    integrity = {
        'total_styles': len(styles_ids),
        'total_images': len(actual_images),
        'total_jsons': len(actual_jsons),
        'missing_images': len(missing_images),
        'missing_jsons': len(missing_jsons),
        'orphan_images': len(orphan_images),
        'orphan_jsons': len(orphan_jsons),
    }

    print(f"  Total de IDs em styles.csv: {integrity['total_styles']:,}")
    print(f"  Total de imagens no disco: {integrity['total_images']:,}")
    print(f"  Total de JSONs no disco: {integrity['total_jsons']:,}")

    if missing_images:
        print(f"  [AVISO]  Imagens faltantes: {len(missing_images):,}")
    else:
        print("  [OK] Todas as imagens presentes")

    if missing_jsons:
        print(f"  [AVISO]  JSONs faltantes: {len(missing_jsons):,}")
    else:
        print("  [OK] Todos os JSONs presentes")

    if orphan_images:
        print(f"  [INFO]  Imagens órfãs (sem registro no CSV): {len(orphan_images):,}")

    if orphan_jsons:
        print(f"  [INFO]  JSONs órfãos (sem registro no CSV): {len(orphan_jsons):,}")

    return integrity


def create_distribution_plots(df: pd.DataFrame):
    """
    Cria visualizações das distribuições principais.

    Args:
        df: DataFrame do styles.csv
    """
    print("\n[GERANDO] Gerando visualizações...")

    # 1. Distribuição de categorias principais
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Gender
    df['gender'].value_counts().plot(kind='bar', ax=axes[0, 0], color=sns.color_palette(COLOR_PALETTE, 10))
    axes[0, 0].set_title('Distribuição por Gênero', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Gênero')
    axes[0, 0].set_ylabel('Quantidade')
    axes[0, 0].tick_params(axis='x', rotation=45)

    # Master Category
    df['masterCategory'].value_counts().plot(kind='bar', ax=axes[0, 1], color=sns.color_palette(COLOR_PALETTE, 10))
    axes[0, 1].set_title('Distribuição por Categoria Principal', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Categoria')
    axes[0, 1].set_ylabel('Quantidade')
    axes[0, 1].tick_params(axis='x', rotation=45)

    # Season
    df['season'].value_counts().plot(kind='bar', ax=axes[1, 0], color=sns.color_palette(COLOR_PALETTE, 10))
    axes[1, 0].set_title('Distribuição por Estação', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Estação')
    axes[1, 0].set_ylabel('Quantidade')
    axes[1, 0].tick_params(axis='x', rotation=45)

    # Year
    if 'year' in df.columns:
        df['year'].value_counts().sort_index().plot(kind='line', marker='o', ax=axes[1, 1], color='steelblue', linewidth=2)
        axes[1, 1].set_title('Distribuição Temporal (Anos)', fontsize=14, fontweight='bold')
        axes[1, 1].set_xlabel('Ano')
        axes[1, 1].set_ylabel('Quantidade')
        axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'category_distributions.png', dpi=300, bbox_inches='tight')
    print(f"  [OK] Salvo: {FIGURES_DIR / 'category_distributions.png'}")

    # 2. Top 20 Article Types
    fig, ax = plt.subplots(figsize=(14, 8))
    top_articles = df['articleType'].value_counts().head(20)
    top_articles.plot(kind='barh', ax=ax, color=sns.color_palette(COLOR_PALETTE, 20))
    ax.set_title('Top 20 Tipos de Artigos', fontsize=16, fontweight='bold')
    ax.set_xlabel('Quantidade')
    ax.set_ylabel('Tipo de Artigo')
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'top_article_types.png', dpi=300, bbox_inches='tight')
    print(f"  [OK] Salvo: {FIGURES_DIR / 'top_article_types.png'}")

    # 3. Top 15 Colors
    fig, ax = plt.subplots(figsize=(12, 6))
    top_colors = df['baseColour'].value_counts().head(15)
    top_colors.plot(kind='bar', ax=ax, color=sns.color_palette(COLOR_PALETTE, 15))
    ax.set_title('Top 15 Cores Mais Frequentes', fontsize=16, fontweight='bold')
    ax.set_xlabel('Cor')
    ax.set_ylabel('Quantidade')
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'top_colors.png', dpi=300, bbox_inches='tight')
    print(f"  [OK] Salvo: {FIGURES_DIR / 'top_colors.png'}")

    # 4. Heatmap de categoria principal vs gênero
    fig, ax = plt.subplots(figsize=(10, 8))
    crosstab = pd.crosstab(df['masterCategory'], df['gender'])
    sns.heatmap(crosstab, annot=True, fmt='d', cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Contagem'})
    ax.set_title('Categoria Principal vs Gênero', fontsize=16, fontweight='bold')
    ax.set_xlabel('Gênero')
    ax.set_ylabel('Categoria Principal')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'category_gender_heatmap.png', dpi=300, bbox_inches='tight')
    print(f"  [OK] Salvo: {FIGURES_DIR / 'category_gender_heatmap.png'}")


def save_summary_report(stats: Dict, distributions: Dict, temporal: Dict, integrity: Dict):
    """
    Salva um relatório de resumo em formato texto.

    Args:
        stats: Estatísticas básicas
        distributions: Distribuições de categorias
        temporal: Análise temporal
        integrity: Verificação de integridade
    """
    print("\n[SALVANDO] Salvando relatório...")

    report_path = OUTPUTS_DIR / 'data_summary_report.txt'

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("RELATÓRIO DE ANÁLISE EXPLORATÓRIA - FASHION PRODUCT IMAGES DATASET\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. ESTATÍSTICAS BÁSICAS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total de registros: {stats['total_records']:,}\n")
        f.write(f"Total de colunas: {stats['total_columns']}\n")
        f.write(f"Registros duplicados: {stats['duplicates']}\n")
        f.write(f"IDs únicos: {stats['unique_ids']:,}\n\n")

        if any(v > 0 for v in stats['missing_values'].values()):
            f.write("Valores faltantes:\n")
            for col, count in stats['missing_values'].items():
                if count > 0:
                    pct = (count / stats['total_records']) * 100
                    f.write(f"  - {col}: {count:,} ({pct:.2f}%)\n")

        f.write("\n2. DISTRIBUIÇÕES DE CATEGORIAS\n")
        f.write("-" * 80 + "\n")
        for category, dist in distributions.items():
            f.write(f"\n{category.upper()}:\n")
            sorted_dist = sorted(dist.items(), key=lambda x: x[1], reverse=True)
            for cat, count in sorted_dist[:10]:  # Top 10
                pct = (count / stats['total_records']) * 100
                f.write(f"  {cat}: {count:,} ({pct:.2f}%)\n")

        f.write("\n3. ANÁLISE TEMPORAL\n")
        f.write("-" * 80 + "\n")
        if 'year_distribution' in temporal:
            for year, count in sorted(temporal['year_distribution'].items()):
                pct = (count / stats['total_records']) * 100
                f.write(f"  {year}: {count:,} ({pct:.2f}%)\n")

        f.write("\n4. INTEGRIDADE DOS DADOS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total de IDs em styles.csv: {integrity['total_styles']:,}\n")
        f.write(f"Total de imagens no disco: {integrity['total_images']:,}\n")
        f.write(f"Total de JSONs no disco: {integrity['total_jsons']:,}\n")
        f.write(f"Imagens faltantes: {integrity['missing_images']:,}\n")
        f.write(f"JSONs faltantes: {integrity['missing_jsons']:,}\n")
        f.write(f"Imagens órfãs: {integrity['orphan_images']:,}\n")
        f.write(f"JSONs órfãos: {integrity['orphan_jsons']:,}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("Relatório gerado com sucesso!\n")

    print(f"  [OK] Salvo: {report_path}")


def main():
    """Função principal que executa todas as análises."""
    print("=" * 80)
    print("ANALISE EXPLORATORIA - FASHION PRODUCT IMAGES DATASET")
    print("=" * 80)

    # Carregar dados
    styles_df, images_df = load_data()

    # Análises
    stats = analyze_basic_stats(styles_df)
    distributions = analyze_categories(styles_df)
    temporal = analyze_temporal(styles_df)
    integrity = check_data_integrity(styles_df, images_df)

    # Visualizações
    create_distribution_plots(styles_df)

    # Relatório
    save_summary_report(stats, distributions, temporal, integrity)

    print("\n" + "=" * 80)
    print("[OK] Analise concluida com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()