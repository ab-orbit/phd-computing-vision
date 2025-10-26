"""
Script para análise específica da categoria Casual Shoes.

Este script foca na análise detalhada de Casual Shoes para preparação
do treinamento de modelo generativo (Stable Diffusion + LoRA).

Análises incluídas:
- Distribuições de cores, gêneros, marcas, materiais
- Características visuais das imagens
- Padrões e insights para condicionamento do modelo
- Grid de amostras para inspeção visual
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
from PIL import Image
import random

from config import (
    STYLES_CSV, IMAGES_DIR, STYLES_JSON_DIR,
    OUTPUTS_DIR, FIGURES_DIR, FIGURE_SIZE, SEABORN_STYLE,
    COLOR_PALETTE, RANDOM_SEED
)

# Configurar estilo de visualização
sns.set_style(SEABORN_STYLE)
plt.rcParams['figure.figsize'] = FIGURE_SIZE
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


def load_data() -> pd.DataFrame:
    """
    Carrega os dados do CSV e filtra apenas Casual Shoes.

    Returns:
        DataFrame filtrado com apenas Casual Shoes
    """
    print("Carregando dados completos...")
    df = pd.read_csv(STYLES_CSV, on_bad_lines='skip')
    print(f"[OK] Total de registros: {len(df):,}")

    # Filtrar apenas Casual Shoes
    df_casual_shoes = df[df['articleType'] == 'Casual Shoes'].copy()
    print(f"[OK] Casual Shoes filtrados: {len(df_casual_shoes):,}")

    return df_casual_shoes


def analyze_basic_statistics(df: pd.DataFrame) -> Dict:
    """
    Analisa estatísticas básicas da categoria Casual Shoes.

    Args:
        df: DataFrame de Casual Shoes

    Returns:
        Dicionário com estatísticas
    """
    print("\n[ANALISE] Estatísticas Básicas - Casual Shoes:")

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
        print("\n  [AVISO] Valores faltantes por coluna:")
        for col, count in missing[missing > 0].items():
            pct = (count / len(df)) * 100
            print(f"    - {col}: {count:,} ({pct:.2f}%)")
    else:
        print("  [OK] Nenhum valor faltante detectado")

    return stats


def analyze_distributions(df: pd.DataFrame) -> Dict:
    """
    Analisa distribuições de atributos principais.

    Args:
        df: DataFrame de Casual Shoes

    Returns:
        Dicionário com distribuições
    """
    print("\n[ANALISE] Distribuições de Atributos:")

    distributions = {}

    # Atributos para analisar
    attributes = ['gender', 'baseColour', 'season', 'usage', 'year']

    for attr in attributes:
        if attr in df.columns:
            dist = df[attr].value_counts()
            distributions[attr] = dist.to_dict()

            print(f"\n  {attr.upper()} ({df[attr].nunique()} valores únicos):")
            print(f"    Top 10:")
            for value, count in dist.head(10).items():
                pct = (count / len(df)) * 100
                print(f"      - {value}: {count:,} ({pct:.2f}%)")

    return distributions


def analyze_brands(df: pd.DataFrame) -> Dict:
    """
    Analisa distribuição de marcas em Casual Shoes.

    Args:
        df: DataFrame de Casual Shoes

    Returns:
        Dicionário com estatísticas de marcas
    """
    print("\n[ANALISE] Análise de Marcas:")

    # Carregar marcas dos JSONs
    brands = []
    ids_with_brands = []

    for idx, row in df.iterrows():
        json_path = STYLES_JSON_DIR / f"{row['id']}.json"
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'brandName' in data['data']:
                        brand = data['data']['brandName']
                        brands.append(brand)
                        ids_with_brands.append(row['id'])
            except:
                continue

    brand_counts = Counter(brands)

    print(f"  Total de produtos com marca: {len(brands):,}")
    print(f"  Marcas únicas: {len(brand_counts)}")
    print(f"\n  Top 15 Marcas:")

    for brand, count in brand_counts.most_common(15):
        pct = (count / len(brands)) * 100
        print(f"    - {brand}: {count:,} ({pct:.2f}%)")

    return {
        'total_with_brand': len(brands),
        'unique_brands': len(brand_counts),
        'brand_distribution': dict(brand_counts.most_common(20))
    }


def analyze_image_properties(df: pd.DataFrame) -> Dict:
    """
    Analisa propriedades das imagens de Casual Shoes.

    Args:
        df: DataFrame de Casual Shoes

    Returns:
        Dicionário com estatísticas de imagens
    """
    print("\n[ANALISE] Análise de Propriedades das Imagens:")

    widths = []
    heights = []
    aspect_ratios = []
    file_sizes = []
    existing_images = 0

    print("  Processando imagens...")

    for idx, row in df.iterrows():
        img_path = IMAGES_DIR / f"{row['id']}.jpg"

        if img_path.exists():
            existing_images += 1

            # Dimensões
            try:
                with Image.open(img_path) as img:
                    width, height = img.size
                    widths.append(width)
                    heights.append(height)
                    aspect_ratios.append(width / height if height > 0 else 0)
            except:
                continue

            # Tamanho do arquivo
            file_sizes.append(img_path.stat().st_size / 1024)  # KB

    stats = {
        'total_images': len(df),
        'existing_images': existing_images,
        'missing_images': len(df) - existing_images,
        'width_stats': {
            'min': int(np.min(widths)) if widths else 0,
            'max': int(np.max(widths)) if widths else 0,
            'mean': int(np.mean(widths)) if widths else 0,
            'median': int(np.median(widths)) if widths else 0,
        },
        'height_stats': {
            'min': int(np.min(heights)) if heights else 0,
            'max': int(np.max(heights)) if heights else 0,
            'mean': int(np.mean(heights)) if heights else 0,
            'median': int(np.median(heights)) if heights else 0,
        },
        'aspect_ratio_stats': {
            'min': float(np.min(aspect_ratios)) if aspect_ratios else 0,
            'max': float(np.max(aspect_ratios)) if aspect_ratios else 0,
            'mean': float(np.mean(aspect_ratios)) if aspect_ratios else 0,
            'median': float(np.median(aspect_ratios)) if aspect_ratios else 0,
        },
        'file_size_stats': {
            'min_kb': float(np.min(file_sizes)) if file_sizes else 0,
            'max_kb': float(np.max(file_sizes)) if file_sizes else 0,
            'mean_kb': float(np.mean(file_sizes)) if file_sizes else 0,
            'median_kb': float(np.median(file_sizes)) if file_sizes else 0,
        }
    }

    print(f"  Imagens encontradas: {existing_images:,} de {len(df):,}")
    if stats['missing_images'] > 0:
        print(f"  [AVISO] Imagens faltantes: {stats['missing_images']}")
    else:
        print(f"  [OK] Todas as imagens presentes")

    print(f"\n  Dimensões:")
    print(f"    Largura: {stats['width_stats']['min']} - {stats['width_stats']['max']} (média: {stats['width_stats']['mean']})")
    print(f"    Altura: {stats['height_stats']['min']} - {stats['height_stats']['max']} (média: {stats['height_stats']['mean']})")
    print(f"    Aspect Ratio: {stats['aspect_ratio_stats']['min']:.2f} - {stats['aspect_ratio_stats']['max']:.2f} (média: {stats['aspect_ratio_stats']['mean']:.2f})")

    print(f"\n  Tamanho de Arquivo:")
    print(f"    Min: {stats['file_size_stats']['min_kb']:.1f} KB")
    print(f"    Max: {stats['file_size_stats']['max_kb']:.1f} KB")
    print(f"    Média: {stats['file_size_stats']['mean_kb']:.1f} KB")

    return stats


def create_visualizations(df: pd.DataFrame):
    """
    Cria visualizações das distribuições de Casual Shoes.

    Args:
        df: DataFrame de Casual Shoes
    """
    print("\n[GERANDO] Gerando visualizações...")

    # 1. Distribuições principais (2x2)
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Gender
    gender_counts = df['gender'].value_counts()
    axes[0, 0].bar(range(len(gender_counts)), gender_counts.values,
                   color=sns.color_palette(COLOR_PALETTE, len(gender_counts)))
    axes[0, 0].set_xticks(range(len(gender_counts)))
    axes[0, 0].set_xticklabels(gender_counts.index, rotation=45)
    axes[0, 0].set_title('Distribuição por Gênero', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Gênero')
    axes[0, 0].set_ylabel('Quantidade')
    axes[0, 0].grid(True, alpha=0.3, axis='y')

    # Base Colour (Top 15)
    color_counts = df['baseColour'].value_counts().head(15)
    axes[0, 1].barh(range(len(color_counts)), color_counts.values,
                    color=sns.color_palette(COLOR_PALETTE, len(color_counts)))
    axes[0, 1].set_yticks(range(len(color_counts)))
    axes[0, 1].set_yticklabels(color_counts.index)
    axes[0, 1].set_title('Top 15 Cores', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Quantidade')
    axes[0, 1].set_ylabel('Cor')
    axes[0, 1].invert_yaxis()
    axes[0, 1].grid(True, alpha=0.3, axis='x')

    # Season
    season_counts = df['season'].value_counts()
    axes[1, 0].bar(range(len(season_counts)), season_counts.values,
                   color=sns.color_palette(COLOR_PALETTE, len(season_counts)))
    axes[1, 0].set_xticks(range(len(season_counts)))
    axes[1, 0].set_xticklabels(season_counts.index, rotation=45)
    axes[1, 0].set_title('Distribuição por Estação', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Estação')
    axes[1, 0].set_ylabel('Quantidade')
    axes[1, 0].grid(True, alpha=0.3, axis='y')

    # Year
    if 'year' in df.columns:
        year_counts = df['year'].value_counts().sort_index()
        axes[1, 1].plot(year_counts.index, year_counts.values,
                       marker='o', linewidth=2, markersize=8, color='steelblue')
        axes[1, 1].set_title('Distribuição Temporal', fontsize=14, fontweight='bold')
        axes[1, 1].set_xlabel('Ano')
        axes[1, 1].set_ylabel('Quantidade')
        axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    output_path = FIGURES_DIR / 'casual_shoes_distributions.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"  [OK] {output_path}")
    plt.close()

    # 2. Grid de amostras (10x10 = 100 imagens)
    print("\n[GERANDO] Criando grid de amostras...")
    create_sample_grid(df, grid_size=(10, 10))


def create_sample_grid(df: pd.DataFrame, grid_size: Tuple[int, int] = (10, 10)):
    """
    Cria um grid de imagens de amostra.

    Args:
        df: DataFrame de Casual Shoes
        grid_size: Tupla (linhas, colunas) para o grid
    """
    rows, cols = grid_size
    n_samples = rows * cols

    # Selecionar amostras aleatórias
    sample_ids = df.sample(n=min(n_samples, len(df)), random_state=RANDOM_SEED)['id'].tolist()

    # Criar figura
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 2, rows * 2))
    fig.suptitle(f'Amostras Aleatórias - Casual Shoes (n={len(sample_ids)})',
                 fontsize=16, fontweight='bold')

    for idx, (ax, img_id) in enumerate(zip(axes.flat, sample_ids)):
        img_path = IMAGES_DIR / f"{img_id}.jpg"

        if img_path.exists():
            try:
                img = Image.open(img_path)
                ax.imshow(img)
                ax.axis('off')
            except:
                ax.text(0.5, 0.5, 'Erro', ha='center', va='center')
                ax.axis('off')
        else:
            ax.text(0.5, 0.5, 'N/A', ha='center', va='center')
            ax.axis('off')

    # Desabilitar axes vazios
    for idx in range(len(sample_ids), rows * cols):
        axes.flat[idx].axis('off')

    plt.tight_layout()
    output_path = FIGURES_DIR / 'casual_shoes_sample_grid.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  [OK] {output_path}")
    plt.close()


def identify_patterns(df: pd.DataFrame, distributions: Dict, brands: Dict) -> Dict:
    """
    Identifica padrões importantes para treinamento do modelo.

    Args:
        df: DataFrame de Casual Shoes
        distributions: Distribuições de atributos
        brands: Estatísticas de marcas

    Returns:
        Dicionário com insights e padrões
    """
    print("\n[ANALISE] Identificando Padrões para Treinamento:")

    patterns = {}

    # 1. Cores dominantes
    top_colors = df['baseColour'].value_counts().head(5)
    patterns['top_colors'] = top_colors.to_dict()
    print(f"\n  Cores Dominantes (Top 5):")
    for color, count in top_colors.items():
        pct = (count / len(df)) * 100
        print(f"    - {color}: {count} ({pct:.1f}%)")

    # 2. Gênero predominante
    top_gender = df['gender'].value_counts().head(3)
    patterns['top_genders'] = top_gender.to_dict()
    print(f"\n  Gêneros Predominantes:")
    for gender, count in top_gender.items():
        pct = (count / len(df)) * 100
        print(f"    - {gender}: {count} ({pct:.1f}%)")

    # 3. Estações
    season_dist = df['season'].value_counts()
    patterns['season_distribution'] = season_dist.to_dict()
    print(f"\n  Distribuição por Estação:")
    for season, count in season_dist.items():
        pct = (count / len(df)) * 100
        print(f"    - {season}: {count} ({pct:.1f}%)")

    # 4. Combinações comuns (cor + gênero)
    combinations = df.groupby(['baseColour', 'gender']).size().sort_values(ascending=False).head(10)
    patterns['top_combinations'] = {f"{c[0]}_{c[1]}": count for c, count in combinations.items()}
    print(f"\n  Top 10 Combinações (Cor + Gênero):")
    for (color, gender), count in combinations.items():
        print(f"    - {color} + {gender}: {count}")

    # 5. Recomendações para condicionamento
    print(f"\n  [INFO] Recomendações para Treinamento:")
    print(f"    - Usar cores como condicionamento principal")
    print(f"    - Incluir gênero no prompt")
    print(f"    - Considerar estação para variação de estilo")
    print(f"    - Balancear dataset por cor (sobreamostrar cores raras)")

    return patterns


def save_report(stats: Dict, distributions: Dict, brands: Dict,
                image_stats: Dict, patterns: Dict):
    """
    Salva relatório completo da análise.

    Args:
        stats: Estatísticas básicas
        distributions: Distribuições de atributos
        brands: Estatísticas de marcas
        image_stats: Estatísticas de imagens
        patterns: Padrões identificados
    """
    print("\n[SALVANDO] Salvando relatório...")

    report_path = OUTPUTS_DIR / 'casual_shoes_report.txt'

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("RELATÓRIO DE ANÁLISE - CASUAL SHOES\n")
        f.write("Dataset: Fashion Product Images\n")
        f.write("Objetivo: Preparação para Treinamento de Modelo Generativo\n")
        f.write("=" * 80 + "\n\n")

        # 1. Estatísticas Básicas
        f.write("1. ESTATÍSTICAS BÁSICAS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total de registros: {stats['total_records']:,}\n")
        f.write(f"IDs únicos: {stats['unique_ids']:,}\n")
        f.write(f"Registros duplicados: {stats['duplicates']}\n\n")

        if any(v > 0 for v in stats['missing_values'].values()):
            f.write("Valores faltantes:\n")
            for col, count in stats['missing_values'].items():
                if count > 0:
                    pct = (count / stats['total_records']) * 100
                    f.write(f"  - {col}: {count:,} ({pct:.2f}%)\n")
        f.write("\n")

        # 2. Distribuições
        f.write("2. DISTRIBUIÇÕES DE ATRIBUTOS\n")
        f.write("-" * 80 + "\n")
        for attr, dist in distributions.items():
            f.write(f"\n{attr.upper()}:\n")
            sorted_dist = sorted(dist.items(), key=lambda x: x[1], reverse=True)
            for value, count in sorted_dist[:10]:
                pct = (count / stats['total_records']) * 100
                f.write(f"  {value}: {count:,} ({pct:.2f}%)\n")
        f.write("\n")

        # 3. Marcas
        f.write("3. ANÁLISE DE MARCAS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total com marca: {brands['total_with_brand']:,}\n")
        f.write(f"Marcas únicas: {brands['unique_brands']}\n\n")
        f.write("Top 15 Marcas:\n")
        for brand, count in list(brands['brand_distribution'].items())[:15]:
            pct = (count / brands['total_with_brand']) * 100
            f.write(f"  {brand}: {count:,} ({pct:.2f}%)\n")
        f.write("\n")

        # 4. Propriedades de Imagens
        f.write("4. PROPRIEDADES DAS IMAGENS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total de imagens: {image_stats['total_images']:,}\n")
        f.write(f"Imagens existentes: {image_stats['existing_images']:,}\n")
        f.write(f"Imagens faltantes: {image_stats['missing_images']}\n\n")

        f.write("Dimensões:\n")
        f.write(f"  Largura: {image_stats['width_stats']['min']} - {image_stats['width_stats']['max']} ")
        f.write(f"(média: {image_stats['width_stats']['mean']}, mediana: {image_stats['width_stats']['median']})\n")
        f.write(f"  Altura: {image_stats['height_stats']['min']} - {image_stats['height_stats']['max']} ")
        f.write(f"(média: {image_stats['height_stats']['mean']}, mediana: {image_stats['height_stats']['median']})\n")
        f.write(f"  Aspect Ratio: {image_stats['aspect_ratio_stats']['min']:.2f} - {image_stats['aspect_ratio_stats']['max']:.2f} ")
        f.write(f"(média: {image_stats['aspect_ratio_stats']['mean']:.2f})\n\n")

        f.write("Tamanho de Arquivo:\n")
        f.write(f"  Min: {image_stats['file_size_stats']['min_kb']:.1f} KB\n")
        f.write(f"  Max: {image_stats['file_size_stats']['max_kb']:.1f} KB\n")
        f.write(f"  Média: {image_stats['file_size_stats']['mean_kb']:.1f} KB\n")
        f.write(f"  Mediana: {image_stats['file_size_stats']['median_kb']:.1f} KB\n\n")

        # 5. Padrões para Treinamento
        f.write("5. PADRÕES IDENTIFICADOS PARA TREINAMENTO\n")
        f.write("-" * 80 + "\n")

        f.write("\nCores Dominantes (Top 5):\n")
        for color, count in patterns['top_colors'].items():
            pct = (count / stats['total_records']) * 100
            f.write(f"  {color}: {count} ({pct:.1f}%)\n")

        f.write("\nGêneros Predominantes:\n")
        for gender, count in patterns['top_genders'].items():
            pct = (count / stats['total_records']) * 100
            f.write(f"  {gender}: {count} ({pct:.1f}%)\n")

        f.write("\nTop 10 Combinações (Cor + Gênero):\n")
        for combo, count in list(patterns['top_combinations'].items())[:10]:
            color, gender = combo.split('_')
            f.write(f"  {color} + {gender}: {count}\n")

        # 6. Recomendações
        f.write("\n6. RECOMENDAÇÕES PARA TREINAMENTO\n")
        f.write("-" * 80 + "\n")
        f.write("1. Estratégia de Condicionamento:\n")
        f.write("   - Usar cor como condicionamento principal\n")
        f.write("   - Incluir gênero no prompt\n")
        f.write("   - Adicionar estação para variação de estilo\n")
        f.write("   - Considerar marca para produtos específicos\n\n")

        f.write("2. Preparação de Imagens:\n")
        f.write("   - Redimensionar para 512x512 (padrão SD 1.5)\n")
        f.write("   - Normalizar aspect ratio (padding se necessário)\n")
        f.write("   - Manter fundo branco limpo\n\n")

        f.write("3. Formato de Prompt Sugerido:\n")
        f.write('   "A professional product photo of [color] casual shoes, [season] collection, ')
        f.write('[gender], centered on white background, high quality"\n\n')

        f.write("4. Balanceamento de Dataset:\n")
        f.write("   - Sobreamostrar cores raras durante treinamento\n")
        f.write("   - Usar data augmentation moderado (flip horizontal)\n")
        f.write("   - Evitar augmentation que mude características do produto\n\n")

        f.write("5. Métricas de Validação:\n")
        f.write("   - FID Score: Target < 50 (< 40 excelente)\n")
        f.write("   - CLIP Score: Target > 0.25 (> 0.28 excelente)\n")
        f.write("   - Inspeção visual manual de amostras\n")
        f.write("   - Verificar consistência de cores e proporções\n\n")

        f.write("=" * 80 + "\n")
        f.write("Análise concluída com sucesso!\n")
        f.write("Próximo passo: Task 1.2 - Preparação do Subset de Treinamento\n")

    print(f"  [OK] {report_path}")

    # Salvar também em JSON para uso programático
    json_path = OUTPUTS_DIR / 'casual_shoes_analysis.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'statistics': stats,
            'distributions': distributions,
            'brands': brands,
            'image_properties': image_stats,
            'patterns': patterns
        }, f, indent=2, default=str)
    print(f"  [OK] {json_path}")


def main():
    """Função principal que executa toda a análise de Casual Shoes."""
    print("=" * 80)
    print("ANALISE ESPECIFICA - CASUAL SHOES")
    print("Objetivo: Preparação para Treinamento de Modelo Generativo (SD 1.5 + LoRA)")
    print("=" * 80)

    # Carregar e filtrar dados
    df = load_data()

    # Análises
    stats = analyze_basic_statistics(df)
    distributions = analyze_distributions(df)
    brands = analyze_brands(df)
    image_stats = analyze_image_properties(df)

    # Visualizações
    create_visualizations(df)

    # Identificar padrões
    patterns = identify_patterns(df, distributions, brands)

    # Salvar relatório
    save_report(stats, distributions, brands, image_stats, patterns)

    print("\n" + "=" * 80)
    print("[OK] Análise de Casual Shoes concluída com sucesso!")
    print("=" * 80)
    print("\nArquivos gerados:")
    print("  - exploratory/outputs/casual_shoes_report.txt")
    print("  - exploratory/outputs/casual_shoes_analysis.json")
    print("  - exploratory/figures/casual_shoes_distributions.png")
    print("  - exploratory/figures/casual_shoes_sample_grid.png")
    print("\nPróximo passo: Task 1.2 - Preparação do Subset de Treinamento")


if __name__ == "__main__":
    main()
