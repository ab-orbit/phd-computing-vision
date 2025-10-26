"""
Script para criar splits de treino/validação/teste do dataset Fashion Product Images.

Este script realiza:
- Split estratificado baseado em categorias principais
- Preservação da distribuição de categorias em cada split
- Geração de arquivos CSV com os IDs de cada split
- Verificação de integridade dos splits
- Análise de distribuição por split
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
from sklearn.model_selection import train_test_split
import json
import matplotlib.pyplot as plt
import seaborn as sns

from config import (
    STYLES_CSV, OUTPUTS_DIR, FIGURES_DIR,
    RANDOM_SEED, SEABORN_STYLE, COLOR_PALETTE
)

# Configurar estilo de visualização
sns.set_style(SEABORN_STYLE)

# Configurações de split
TRAIN_SIZE = 0.70  # 70% treino
VAL_SIZE = 0.15    # 15% validação
TEST_SIZE = 0.15   # 15% teste

# Coluna para estratificação (garantir distribuição balanceada)
STRATIFY_COL = 'articleType'


def load_data() -> pd.DataFrame:
    """
    Carrega os dados do CSV.

    Returns:
        DataFrame do styles.csv
    """
    print("Carregando dados...")
    df = pd.read_csv(STYLES_CSV, on_bad_lines='skip')
    print(f"[OK] {len(df):,} registros carregados")
    return df


def create_stratified_splits(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Cria splits estratificados de treino/validação/teste.

    Args:
        df: DataFrame completo

    Returns:
        Tupla com (train_df, val_df, test_df)
    """
    print(f"\n[PROCESSANDO] Criando splits estratificados por '{STRATIFY_COL}'...")

    # Remover linhas com valores faltantes na coluna de estratificação
    df_clean = df.dropna(subset=[STRATIFY_COL]).copy()
    print(f"  Registros após limpeza: {len(df_clean):,}")

    # Algumas categorias podem ter poucos exemplos
    # Agrupar categorias raras em "Other" para evitar erro de estratificação
    category_counts = df_clean[STRATIFY_COL].value_counts()
    min_samples = 10  # Mínimo de amostras por categoria para split (aumentado para garantir split duplo)
    rare_categories = category_counts[category_counts < min_samples].index

    if len(rare_categories) > 0:
        print(f"  [INFO] {len(rare_categories)} categorias raras agrupadas em 'Other'")
        df_clean.loc[df_clean[STRATIFY_COL].isin(rare_categories), STRATIFY_COL] = 'Other'

    # Primeiro split: treino vs (val + test)
    train_df, temp_df = train_test_split(
        df_clean,
        test_size=(VAL_SIZE + TEST_SIZE),
        stratify=df_clean[STRATIFY_COL],
        random_state=RANDOM_SEED
    )

    # Segundo split: val vs test
    # Verificar novamente por categorias raras no temp_df
    temp_category_counts = temp_df[STRATIFY_COL].value_counts()
    temp_rare_categories = temp_category_counts[temp_category_counts < 2].index

    if len(temp_rare_categories) > 0:
        print(f"  [INFO] {len(temp_rare_categories)} categorias adicionais agrupadas em 'Other' no split val/test")
        temp_df = temp_df.copy()
        temp_df.loc[temp_df[STRATIFY_COL].isin(temp_rare_categories), STRATIFY_COL] = 'Other'

    # Ajustar proporção para manter val_size e test_size corretos
    val_proportion = VAL_SIZE / (VAL_SIZE + TEST_SIZE)
    val_df, test_df = train_test_split(
        temp_df,
        test_size=(1 - val_proportion),
        stratify=temp_df[STRATIFY_COL],
        random_state=RANDOM_SEED
    )

    print(f"\n[OK] Splits criados:")
    print(f"  Treino: {len(train_df):,} ({len(train_df)/len(df_clean)*100:.1f}%)")
    print(f"  Validação: {len(val_df):,} ({len(val_df)/len(df_clean)*100:.1f}%)")
    print(f"  Teste: {len(test_df):,} ({len(test_df)/len(df_clean)*100:.1f}%)")
    print(f"  Total: {len(train_df) + len(val_df) + len(test_df):,}")

    return train_df, val_df, test_df


def verify_split_integrity(train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame) -> Dict:
    """
    Verifica a integridade dos splits.

    Args:
        train_df, val_df, test_df: DataFrames dos splits

    Returns:
        Dicionário com resultados de verificação
    """
    print("\n[VERIFICACAO] Verificando integridade dos splits...")

    # Verificar sobreposição
    train_ids = set(train_df['id'])
    val_ids = set(val_df['id'])
    test_ids = set(test_df['id'])

    overlap_train_val = train_ids & val_ids
    overlap_train_test = train_ids & test_ids
    overlap_val_test = val_ids & test_ids

    total_overlap = len(overlap_train_val) + len(overlap_train_test) + len(overlap_val_test)

    if total_overlap == 0:
        print("  [OK] Nenhuma sobreposição entre splits")
    else:
        print(f"  [ERRO] Encontrada sobreposição de {total_overlap} registros!")
        if overlap_train_val:
            print(f"    - Treino/Val: {len(overlap_train_val)}")
        if overlap_train_test:
            print(f"    - Treino/Teste: {len(overlap_train_test)}")
        if overlap_val_test:
            print(f"    - Val/Teste: {len(overlap_val_test)}")

    # Verificar cobertura total
    all_ids = train_ids | val_ids | test_ids
    print(f"  IDs únicos totais: {len(all_ids):,}")

    integrity = {
        'overlap_train_val': len(overlap_train_val),
        'overlap_train_test': len(overlap_train_test),
        'overlap_val_test': len(overlap_val_test),
        'total_unique_ids': len(all_ids),
    }

    return integrity


def analyze_split_distributions(train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame):
    """
    Analisa e compara distribuições entre splits.

    Args:
        train_df, val_df, test_df: DataFrames dos splits
    """
    print("\n[ANALISE] Analisando distribuições por split...")

    # Categorias para analisar
    categories = ['gender', 'masterCategory', 'subCategory', 'articleType', 'baseColour', 'season']

    for cat in categories:
        if cat not in train_df.columns:
            continue

        print(f"\n  {cat.upper()}:")

        # Distribuições
        train_dist = train_df[cat].value_counts(normalize=True)
        val_dist = val_df[cat].value_counts(normalize=True)
        test_dist = test_df[cat].value_counts(normalize=True)

        # Top 5 categorias
        top_cats = train_dist.head(5).index

        print("    Categoria | Treino | Val | Teste")
        print("    " + "-" * 45)
        for top_cat in top_cats:
            train_pct = train_dist.get(top_cat, 0) * 100
            val_pct = val_dist.get(top_cat, 0) * 100
            test_pct = test_dist.get(top_cat, 0) * 100
            print(f"    {top_cat:20} | {train_pct:5.1f}% | {val_pct:5.1f}% | {test_pct:5.1f}%")


def save_splits(train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame):
    """
    Salva os splits em arquivos CSV.

    Args:
        train_df, val_df, test_df: DataFrames dos splits
    """
    print("\n[SALVANDO] Salvando splits...")

    # Criar diretório de splits
    splits_dir = OUTPUTS_DIR / 'splits'
    splits_dir.mkdir(exist_ok=True)

    # Salvar CSVs completos
    train_df.to_csv(splits_dir / 'train.csv', index=False)
    print(f"  [OK] {splits_dir / 'train.csv'}")

    val_df.to_csv(splits_dir / 'val.csv', index=False)
    print(f"  [OK] {splits_dir / 'val.csv'}")

    test_df.to_csv(splits_dir / 'test.csv', index=False)
    print(f"  [OK] {splits_dir / 'test.csv'}")

    # Salvar apenas IDs (mais leve)
    train_df[['id']].to_csv(splits_dir / 'train_ids.csv', index=False)
    val_df[['id']].to_csv(splits_dir / 'val_ids.csv', index=False)
    test_df[['id']].to_csv(splits_dir / 'test_ids.csv', index=False)
    print(f"  [OK] IDs salvos em {splits_dir}")

    # Salvar metadados do split
    metadata = {
        'train_size': len(train_df),
        'val_size': len(val_df),
        'test_size': len(test_df),
        'train_ratio': TRAIN_SIZE,
        'val_ratio': VAL_SIZE,
        'test_ratio': TEST_SIZE,
        'stratify_column': STRATIFY_COL,
        'random_seed': RANDOM_SEED,
    }

    with open(splits_dir / 'split_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"  [OK] {splits_dir / 'split_metadata.json'}")


def create_distribution_visualizations(train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame):
    """
    Cria visualizações comparando distribuições entre splits.

    Args:
        train_df, val_df, test_df: DataFrames dos splits
    """
    print("\n[GERANDO] Gerando visualizações de distribuição...")

    # 1. Comparação de categorias principais
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    categories = ['gender', 'masterCategory', 'season', 'usage']

    for idx, cat in enumerate(categories):
        if cat not in train_df.columns:
            continue

        ax = axes[idx // 2, idx % 2]

        # Criar dataframe para comparação
        train_counts = train_df[cat].value_counts()
        val_counts = val_df[cat].value_counts()
        test_counts = test_df[cat].value_counts()

        # Combinar em um único DataFrame
        comparison_df = pd.DataFrame({
            'Treino': train_counts,
            'Validação': val_counts,
            'Teste': test_counts
        }).fillna(0)

        # Plot
        comparison_df.plot(kind='bar', ax=ax, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
        ax.set_title(f'Distribuição: {cat}', fontsize=14, fontweight='bold')
        ax.set_xlabel(cat)
        ax.set_ylabel('Quantidade')
        ax.tick_params(axis='x', rotation=45)
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'split_distributions.png', dpi=300, bbox_inches='tight')
    print(f"  [OK] {FIGURES_DIR / 'split_distributions.png'}")

    # 2. Top 15 Article Types comparação
    fig, ax = plt.subplots(figsize=(14, 8))

    top_articles = train_df['articleType'].value_counts().head(15).index

    train_articles = train_df[train_df['articleType'].isin(top_articles)]['articleType'].value_counts()
    val_articles = val_df[val_df['articleType'].isin(top_articles)]['articleType'].value_counts()
    test_articles = test_df[test_df['articleType'].isin(top_articles)]['articleType'].value_counts()

    comparison_articles = pd.DataFrame({
        'Treino': train_articles,
        'Validação': val_articles,
        'Teste': test_articles
    }).fillna(0)

    comparison_articles.plot(kind='barh', ax=ax, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    ax.set_title('Top 15 Tipos de Artigos por Split', fontsize=16, fontweight='bold')
    ax.set_xlabel('Quantidade')
    ax.set_ylabel('Tipo de Artigo')
    ax.invert_yaxis()
    ax.legend()
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'split_article_types.png', dpi=300, bbox_inches='tight')
    print(f"  [OK] {FIGURES_DIR / 'split_article_types.png'}")

    # 3. Distribuição temporal
    fig, ax = plt.subplots(figsize=(12, 6))

    if 'year' in train_df.columns:
        train_years = train_df['year'].value_counts().sort_index()
        val_years = val_df['year'].value_counts().sort_index()
        test_years = test_df['year'].value_counts().sort_index()

        comparison_years = pd.DataFrame({
            'Treino': train_years,
            'Validação': val_years,
            'Teste': test_years
        }).fillna(0)

        comparison_years.plot(kind='line', marker='o', ax=ax, linewidth=2)
        ax.set_title('Distribuição Temporal por Split', fontsize=16, fontweight='bold')
        ax.set_xlabel('Ano')
        ax.set_ylabel('Quantidade')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(FIGURES_DIR / 'split_temporal.png', dpi=300, bbox_inches='tight')
        print(f"  [OK] {FIGURES_DIR / 'split_temporal.png'}")


def save_split_report(train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame, integrity: Dict):
    """
    Salva relatório detalhado sobre os splits.

    Args:
        train_df, val_df, test_df: DataFrames dos splits
        integrity: Dicionário com resultados de integridade
    """
    print("\n[SALVANDO] Gerando relatório de splits...")

    report_path = OUTPUTS_DIR / 'dataset_splits_report.txt'

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("RELATÓRIO DE SPLITS - FASHION PRODUCT IMAGES DATASET\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. CONFIGURAÇÃO DOS SPLITS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Proporções: Treino={TRAIN_SIZE*100:.0f}% | Val={VAL_SIZE*100:.0f}% | Teste={TEST_SIZE*100:.0f}%\n")
        f.write(f"Coluna de estratificação: {STRATIFY_COL}\n")
        f.write(f"Random seed: {RANDOM_SEED}\n\n")

        f.write("2. TAMANHOS DOS SPLITS\n")
        f.write("-" * 80 + "\n")
        total = len(train_df) + len(val_df) + len(test_df)
        f.write(f"Treino: {len(train_df):,} ({len(train_df)/total*100:.1f}%)\n")
        f.write(f"Validação: {len(val_df):,} ({len(val_df)/total*100:.1f}%)\n")
        f.write(f"Teste: {len(test_df):,} ({len(test_df)/total*100:.1f}%)\n")
        f.write(f"Total: {total:,}\n\n")

        f.write("3. INTEGRIDADE DOS SPLITS\n")
        f.write("-" * 80 + "\n")
        f.write(f"IDs únicos totais: {integrity['total_unique_ids']:,}\n")
        f.write(f"Sobreposição Treino/Val: {integrity['overlap_train_val']}\n")
        f.write(f"Sobreposição Treino/Teste: {integrity['overlap_train_test']}\n")
        f.write(f"Sobreposição Val/Teste: {integrity['overlap_val_test']}\n")

        if (integrity['overlap_train_val'] + integrity['overlap_train_test'] + integrity['overlap_val_test']) == 0:
            f.write("\n[OK] Splits são completamente disjuntos (sem sobreposição)\n\n")
        else:
            f.write("\n[ERRO] Encontrada sobreposição entre splits!\n\n")

        f.write("4. DISTRIBUIÇÕES POR CATEGORIA\n")
        f.write("-" * 80 + "\n")

        categories = ['gender', 'masterCategory', 'subCategory', 'articleType']

        for cat in categories:
            if cat not in train_df.columns:
                continue

            f.write(f"\n{cat.upper()}:\n")

            train_dist = train_df[cat].value_counts()
            val_dist = val_df[cat].value_counts()
            test_dist = test_df[cat].value_counts()

            # Top 10 categorias
            top_cats = train_dist.head(10).index

            f.write(f"  {'Categoria':<30} | {'Treino':>10} | {'Val':>10} | {'Teste':>10}\n")
            f.write("  " + "-" * 70 + "\n")

            for top_cat in top_cats:
                train_count = train_dist.get(top_cat, 0)
                val_count = val_dist.get(top_cat, 0)
                test_count = test_dist.get(top_cat, 0)
                f.write(f"  {str(top_cat):<30} | {train_count:>10,} | {val_count:>10,} | {test_count:>10,}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("Relatório gerado com sucesso!\n")

    print(f"  [OK] {report_path}")


def main():
    """Função principal que executa todo o processo de criação de splits."""
    print("=" * 80)
    print("CRIACAO DE SPLITS - FASHION PRODUCT IMAGES DATASET")
    print("=" * 80)

    # Carregar dados
    df = load_data()

    # Criar splits
    train_df, val_df, test_df = create_stratified_splits(df)

    # Verificar integridade
    integrity = verify_split_integrity(train_df, val_df, test_df)

    # Analisar distribuições
    analyze_split_distributions(train_df, val_df, test_df)

    # Salvar splits
    save_splits(train_df, val_df, test_df)

    # Criar visualizações
    create_distribution_visualizations(train_df, val_df, test_df)

    # Salvar relatório
    save_split_report(train_df, val_df, test_df, integrity)

    print("\n" + "=" * 80)
    print("[OK] Processo de criacao de splits concluido com sucesso!")
    print("=" * 80)
    print("\nArquivos gerados:")
    print("  - outputs/splits/train.csv, val.csv, test.csv")
    print("  - outputs/splits/train_ids.csv, val_ids.csv, test_ids.csv")
    print("  - outputs/splits/split_metadata.json")
    print("  - outputs/dataset_splits_report.txt")
    print("  - figures/split_distributions.png")
    print("  - figures/split_article_types.png")
    print("  - figures/split_temporal.png")


if __name__ == "__main__":
    main()