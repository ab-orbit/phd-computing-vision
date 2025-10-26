"""
Script para análise de imagens do dataset Fashion Product Images.

Este script analisa as características visuais das imagens:
- Dimensões e resoluções
- Formatos e canais de cor
- Distribuição de cores
- Qualidade e aspectos técnicos
"""

import pandas as pd
import numpy as np
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import json
from tqdm import tqdm

from config import (
    IMAGES_DIR, STYLES_CSV,
    OUTPUTS_DIR, FIGURES_DIR, FIGURE_SIZE,
    SEABORN_STYLE, COLOR_PALETTE, RANDOM_SEED, SAMPLE_SIZE
)

# Configurar estilo
sns.set_style(SEABORN_STYLE)
plt.rcParams['figure.figsize'] = FIGURE_SIZE
np.random.seed(RANDOM_SEED)


def analyze_image_properties(sample_size: int = None) -> Dict:
    """
    Analisa propriedades das imagens (dimensões, formato, etc.).

    Args:
        sample_size: Número de imagens a analisar (None = todas)

    Returns:
        Dicionário com estatísticas das imagens
    """
    print("[IMAGENS]  Analisando propriedades das imagens...")

    image_files = list(IMAGES_DIR.glob('*.jpg'))

    if sample_size and sample_size < len(image_files):
        image_files = np.random.choice(image_files, sample_size, replace=False)
        print(f"  Amostra de {len(image_files):,} imagens")
    else:
        print(f"  Analisando todas as {len(image_files):,} imagens")

    # Coletar propriedades
    widths = []
    heights = []
    aspects = []
    modes = []
    sizes_kb = []
    failed = []

    for img_path in tqdm(image_files, desc="Processando imagens"):
        try:
            img = Image.open(img_path)
            width, height = img.size
            widths.append(width)
            heights.append(height)
            aspects.append(width / height)
            modes.append(img.mode)

            # Tamanho do arquivo
            size_kb = img_path.stat().st_size / 1024
            sizes_kb.append(size_kb)

        except Exception as e:
            failed.append((str(img_path), str(e)))

    # Estatísticas
    stats = {
        'total_analyzed': len(image_files),
        'failed': len(failed),
        'width': {
            'min': min(widths) if widths else 0,
            'max': max(widths) if widths else 0,
            'mean': np.mean(widths) if widths else 0,
            'median': np.median(widths) if widths else 0,
            'std': np.std(widths) if widths else 0,
        },
        'height': {
            'min': min(heights) if heights else 0,
            'max': max(heights) if heights else 0,
            'mean': np.mean(heights) if heights else 0,
            'median': np.median(heights) if heights else 0,
            'std': np.std(heights) if heights else 0,
        },
        'aspect_ratio': {
            'min': min(aspects) if aspects else 0,
            'max': max(aspects) if aspects else 0,
            'mean': np.mean(aspects) if aspects else 0,
            'median': np.median(aspects) if aspects else 0,
        },
        'modes': Counter(modes),
        'size_kb': {
            'min': min(sizes_kb) if sizes_kb else 0,
            'max': max(sizes_kb) if sizes_kb else 0,
            'mean': np.mean(sizes_kb) if sizes_kb else 0,
            'median': np.median(sizes_kb) if sizes_kb else 0,
        },
        'failed_images': failed,
        'raw_data': {
            'widths': widths,
            'heights': heights,
            'aspects': aspects,
            'sizes_kb': sizes_kb,
        }
    }

    # Resumo
    print(f"\n  [GERANDO] Resumo:")
    print(f"    Imagens analisadas: {stats['total_analyzed']:,}")
    print(f"    Falhas: {stats['failed']}")
    print(f"\n    Largura: {stats['width']['min']:.0f} - {stats['width']['max']:.0f} pixels (média: {stats['width']['mean']:.0f})")
    print(f"    Altura: {stats['height']['min']:.0f} - {stats['height']['max']:.0f} pixels (média: {stats['height']['mean']:.0f})")
    print(f"    Aspect Ratio: {stats['aspect_ratio']['min']:.2f} - {stats['aspect_ratio']['max']:.2f} (média: {stats['aspect_ratio']['mean']:.2f})")
    print(f"    Tamanho: {stats['size_kb']['min']:.1f} - {stats['size_kb']['max']:.1f} KB (média: {stats['size_kb']['mean']:.1f} KB)")
    print(f"\n    Modos de cor:")
    for mode, count in stats['modes'].most_common():
        pct = (count / stats['total_analyzed']) * 100
        print(f"      {mode}: {count:,} ({pct:.2f}%)")

    return stats


def detect_common_resolutions(widths: List[int], heights: List[int], top_n: int = 10) -> Dict:
    """
    Detecta as resoluções mais comuns.

    Args:
        widths: Lista de larguras
        heights: Lista de alturas
        top_n: Número de resoluções mais comuns a retornar

    Returns:
        Dicionário com resoluções comuns
    """
    print("\n[BUSCA] Detectando resoluções comuns...")

    resolutions = [(w, h) for w, h in zip(widths, heights)]
    res_counter = Counter(resolutions)

    top_resolutions = res_counter.most_common(top_n)

    print(f"  Top {top_n} resoluções:")
    for (w, h), count in top_resolutions:
        pct = (count / len(resolutions)) * 100
        print(f"    {w}x{h}: {count:,} ({pct:.2f}%)")

    return {
        'top_resolutions': top_resolutions,
        'unique_resolutions': len(res_counter),
    }


def analyze_color_distributions(sample_size: int = 500) -> Dict:
    """
    Analisa a distribuição de cores nas imagens.

    Args:
        sample_size: Número de imagens a analisar

    Returns:
        Dicionário com estatísticas de cores
    """
    print(f"\n[CORES] Analisando distribuição de cores ({sample_size} amostras)...")

    image_files = list(IMAGES_DIR.glob('*.jpg'))
    if sample_size < len(image_files):
        image_files = np.random.choice(image_files, sample_size, replace=False)

    dominant_colors = []
    brightness_values = []

    for img_path in tqdm(image_files, desc="Analisando cores"):
        try:
            img = Image.open(img_path)

            # Converter para RGB se necessário
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Redimensionar para análise mais rápida
            img_small = img.resize((100, 100))
            pixels = np.array(img_small).reshape(-1, 3)

            # Cor dominante (média)
            mean_color = pixels.mean(axis=0)
            dominant_colors.append(mean_color)

            # Brilho médio (luminância)
            brightness = 0.299 * mean_color[0] + 0.587 * mean_color[1] + 0.114 * mean_color[2]
            brightness_values.append(brightness)

        except Exception as e:
            continue

    dominant_colors = np.array(dominant_colors)
    brightness_values = np.array(brightness_values)

    stats = {
        'mean_r': dominant_colors[:, 0].mean(),
        'mean_g': dominant_colors[:, 1].mean(),
        'mean_b': dominant_colors[:, 2].mean(),
        'brightness': {
            'mean': brightness_values.mean(),
            'median': np.median(brightness_values),
            'std': brightness_values.std(),
        },
        'raw_data': {
            'dominant_colors': dominant_colors,
            'brightness': brightness_values,
        }
    }

    print(f"  Cor média (RGB): ({stats['mean_r']:.1f}, {stats['mean_g']:.1f}, {stats['mean_b']:.1f})")
    print(f"  Brilho médio: {stats['brightness']['mean']:.1f}/255")

    return stats


def create_image_visualizations(image_stats: Dict, color_stats: Dict, resolution_stats: Dict):
    """
    Cria visualizações das análises de imagem.

    Args:
        image_stats: Estatísticas de propriedades de imagem
        color_stats: Estatísticas de cores
        resolution_stats: Estatísticas de resoluções
    """
    print("\n[GERANDO] Gerando visualizações de imagens...")

    # 1. Distribuições de dimensões
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Largura
    axes[0, 0].hist(image_stats['raw_data']['widths'], bins=50, color='steelblue', edgecolor='black', alpha=0.7)
    axes[0, 0].axvline(image_stats['width']['mean'], color='red', linestyle='--', linewidth=2, label=f"Média: {image_stats['width']['mean']:.0f}")
    axes[0, 0].axvline(image_stats['width']['median'], color='orange', linestyle='--', linewidth=2, label=f"Mediana: {image_stats['width']['median']:.0f}")
    axes[0, 0].set_title('Distribuição de Largura', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Largura (pixels)')
    axes[0, 0].set_ylabel('Frequência')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # Altura
    axes[0, 1].hist(image_stats['raw_data']['heights'], bins=50, color='forestgreen', edgecolor='black', alpha=0.7)
    axes[0, 1].axvline(image_stats['height']['mean'], color='red', linestyle='--', linewidth=2, label=f"Média: {image_stats['height']['mean']:.0f}")
    axes[0, 1].axvline(image_stats['height']['median'], color='orange', linestyle='--', linewidth=2, label=f"Mediana: {image_stats['height']['median']:.0f}")
    axes[0, 1].set_title('Distribuição de Altura', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Altura (pixels)')
    axes[0, 1].set_ylabel('Frequência')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # Aspect Ratio
    axes[1, 0].hist(image_stats['raw_data']['aspects'], bins=50, color='coral', edgecolor='black', alpha=0.7)
    axes[1, 0].axvline(image_stats['aspect_ratio']['mean'], color='red', linestyle='--', linewidth=2, label=f"Média: {image_stats['aspect_ratio']['mean']:.2f}")
    axes[1, 0].set_title('Distribuição de Aspect Ratio', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Aspect Ratio (largura/altura)')
    axes[1, 0].set_ylabel('Frequência')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # Tamanho de arquivo
    axes[1, 1].hist(image_stats['raw_data']['sizes_kb'], bins=50, color='purple', edgecolor='black', alpha=0.7)
    axes[1, 1].axvline(image_stats['size_kb']['mean'], color='red', linestyle='--', linewidth=2, label=f"Média: {image_stats['size_kb']['mean']:.1f} KB")
    axes[1, 1].set_title('Distribuição de Tamanho de Arquivo', fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('Tamanho (KB)')
    axes[1, 1].set_ylabel('Frequência')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'image_dimensions.png', dpi=300, bbox_inches='tight')
    print(f"  [OK] Salvo: {FIGURES_DIR / 'image_dimensions.png'}")

    # 2. Scatter plot: largura vs altura
    fig, ax = plt.subplots(figsize=(10, 8))
    scatter = ax.scatter(image_stats['raw_data']['widths'], image_stats['raw_data']['heights'],
                         alpha=0.3, c=image_stats['raw_data']['aspects'], cmap='viridis', s=10)
    ax.set_title('Largura vs Altura das Imagens', fontsize=16, fontweight='bold')
    ax.set_xlabel('Largura (pixels)')
    ax.set_ylabel('Altura (pixels)')
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Aspect Ratio')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'width_vs_height.png', dpi=300, bbox_inches='tight')
    print(f"  [OK] Salvo: {FIGURES_DIR / 'width_vs_height.png'}")

    # 3. Top resoluções
    if resolution_stats['top_resolutions']:
        fig, ax = plt.subplots(figsize=(12, 6))
        resolutions = [f"{w}x{h}" for (w, h), _ in resolution_stats['top_resolutions'][:15]]
        counts = [count for _, count in resolution_stats['top_resolutions'][:15]]
        ax.barh(resolutions, counts, color=sns.color_palette(COLOR_PALETTE, 15))
        ax.set_title('Top 15 Resoluções Mais Comuns', fontsize=16, fontweight='bold')
        ax.set_xlabel('Quantidade')
        ax.set_ylabel('Resolução')
        ax.invert_yaxis()
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / 'top_resolutions.png', dpi=300, bbox_inches='tight')
        print(f"  [OK] Salvo: {FIGURES_DIR / 'top_resolutions.png'}")

    # 4. Distribuição de brilho
    if 'raw_data' in color_stats and 'brightness' in color_stats['raw_data']:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(color_stats['raw_data']['brightness'], bins=50, color='gold', edgecolor='black', alpha=0.7)
        ax.axvline(color_stats['brightness']['mean'], color='red', linestyle='--', linewidth=2,
                   label=f"Média: {color_stats['brightness']['mean']:.1f}")
        ax.set_title('Distribuição de Brilho das Imagens', fontsize=16, fontweight='bold')
        ax.set_xlabel('Brilho (0-255)')
        ax.set_ylabel('Frequência')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / 'brightness_distribution.png', dpi=300, bbox_inches='tight')
        print(f"  [OK] Salvo: {FIGURES_DIR / 'brightness_distribution.png'}")

    # 5. Distribuição RGB
    if 'raw_data' in color_stats and 'dominant_colors' in color_stats['raw_data']:
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        colors_data = color_stats['raw_data']['dominant_colors']

        axes[0].hist(colors_data[:, 0], bins=50, color='red', alpha=0.6, edgecolor='black')
        axes[0].set_title('Canal Vermelho (R)', fontsize=12, fontweight='bold')
        axes[0].set_xlabel('Valor')
        axes[0].set_ylabel('Frequência')

        axes[1].hist(colors_data[:, 1], bins=50, color='green', alpha=0.6, edgecolor='black')
        axes[1].set_title('Canal Verde (G)', fontsize=12, fontweight='bold')
        axes[1].set_xlabel('Valor')
        axes[1].set_ylabel('Frequência')

        axes[2].hist(colors_data[:, 2], bins=50, color='blue', alpha=0.6, edgecolor='black')
        axes[2].set_title('Canal Azul (B)', fontsize=12, fontweight='bold')
        axes[2].set_xlabel('Valor')
        axes[2].set_ylabel('Frequência')

        plt.tight_layout()
        plt.savefig(FIGURES_DIR / 'rgb_channels.png', dpi=300, bbox_inches='tight')
        print(f"  [OK] Salvo: {FIGURES_DIR / 'rgb_channels.png'}")


def save_image_report(image_stats: Dict, color_stats: Dict, resolution_stats: Dict):
    """
    Salva relatório de análise de imagens.

    Args:
        image_stats: Estatísticas de imagens
        color_stats: Estatísticas de cores
        resolution_stats: Estatísticas de resoluções
    """
    print("\n[SALVANDO] Salvando relatório de imagens...")

    report_path = OUTPUTS_DIR / 'image_analysis_report.txt'

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("RELATÓRIO DE ANÁLISE DE IMAGENS - FASHION PRODUCT IMAGES DATASET\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. PROPRIEDADES DAS IMAGENS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total analisado: {image_stats['total_analyzed']:,}\n")
        f.write(f"Falhas: {image_stats['failed']}\n\n")

        f.write("Dimensões:\n")
        f.write(f"  Largura - Min: {image_stats['width']['min']:.0f}, Max: {image_stats['width']['max']:.0f}, "
                f"Média: {image_stats['width']['mean']:.0f}, Mediana: {image_stats['width']['median']:.0f}\n")
        f.write(f"  Altura - Min: {image_stats['height']['min']:.0f}, Max: {image_stats['height']['max']:.0f}, "
                f"Média: {image_stats['height']['mean']:.0f}, Mediana: {image_stats['height']['median']:.0f}\n")
        f.write(f"  Aspect Ratio - Min: {image_stats['aspect_ratio']['min']:.2f}, "
                f"Max: {image_stats['aspect_ratio']['max']:.2f}, Média: {image_stats['aspect_ratio']['mean']:.2f}\n\n")

        f.write("Tamanho de arquivo:\n")
        f.write(f"  Min: {image_stats['size_kb']['min']:.1f} KB\n")
        f.write(f"  Max: {image_stats['size_kb']['max']:.1f} KB\n")
        f.write(f"  Média: {image_stats['size_kb']['mean']:.1f} KB\n\n")

        f.write("Modos de cor:\n")
        for mode, count in image_stats['modes'].most_common():
            pct = (count / image_stats['total_analyzed']) * 100
            f.write(f"  {mode}: {count:,} ({pct:.2f}%)\n")

        f.write("\n2. RESOLUÇÕES\n")
        f.write("-" * 80 + "\n")
        f.write(f"Resoluções únicas: {resolution_stats['unique_resolutions']}\n\n")
        f.write("Top 20 resoluções:\n")
        for (w, h), count in resolution_stats['top_resolutions'][:20]:
            pct = (count / image_stats['total_analyzed']) * 100
            f.write(f"  {w}x{h}: {count:,} ({pct:.2f}%)\n")

        f.write("\n3. ANÁLISE DE CORES\n")
        f.write("-" * 80 + "\n")
        f.write(f"Cor média (RGB): ({color_stats['mean_r']:.1f}, {color_stats['mean_g']:.1f}, {color_stats['mean_b']:.1f})\n")
        f.write(f"Brilho médio: {color_stats['brightness']['mean']:.1f}/255\n")
        f.write(f"Brilho mediano: {color_stats['brightness']['median']:.1f}/255\n")
        f.write(f"Desvio padrão de brilho: {color_stats['brightness']['std']:.1f}\n")

        f.write("\n" + "=" * 80 + "\n")

    print(f"  [OK] Salvo: {report_path}")

    # Salvar também em JSON
    json_path = OUTPUTS_DIR / 'image_analysis_stats.json'
    # Remover dados brutos do numpy para JSON
    image_stats_clean = {k: v for k, v in image_stats.items() if k != 'raw_data'}
    color_stats_clean = {k: v for k, v in color_stats.items() if k != 'raw_data'}

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'image_stats': image_stats_clean,
            'color_stats': color_stats_clean,
            'resolution_stats': resolution_stats,
        }, f, indent=2)

    print(f"  [OK] Salvo: {json_path}")


def main():
    """Função principal."""
    print("=" * 80)
    print("ANÁLISE DE IMAGENS - FASHION PRODUCT IMAGES DATASET")
    print("=" * 80)

    # Análise de propriedades (sample para testes, None para completo)
    sample = SAMPLE_SIZE if SAMPLE_SIZE else None
    image_stats = analyze_image_properties(sample_size=sample)

    # Detectar resoluções comuns
    resolution_stats = detect_common_resolutions(
        image_stats['raw_data']['widths'],
        image_stats['raw_data']['heights'],
        top_n=20
    )

    # Análise de cores (sempre sample para performance)
    color_stats = analyze_color_distributions(sample_size=500)

    # Visualizações
    create_image_visualizations(image_stats, color_stats, resolution_stats)

    # Relatório
    save_image_report(image_stats, color_stats, resolution_stats)

    print("\n" + "=" * 80)
    print("✅ Análise de imagens concluída!")
    print("=" * 80)


if __name__ == "__main__":
    main()