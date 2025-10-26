"""
Script para análise dos metadados JSON do dataset Fashion Product Images.

Este script analisa a estrutura e conteúdo dos arquivos JSON de metadados,
incluindo descrições de produtos, atributos, preços, e outras informações ricas.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

from config import (
    STYLES_JSON_DIR, STYLES_CSV,
    OUTPUTS_DIR, FIGURES_DIR, FIGURE_SIZE,
    SEABORN_STYLE, COLOR_PALETTE, RANDOM_SEED, SAMPLE_SIZE
)

# Configurar
sns.set_style(SEABORN_STYLE)
plt.rcParams['figure.figsize'] = FIGURE_SIZE
np.random.seed(RANDOM_SEED)


def load_json_sample(sample_size: int = None) -> List[Dict]:
    """
    Carrega uma amostra de arquivos JSON.

    Args:
        sample_size: Número de JSONs a carregar (None = todos)

    Returns:
        Lista de dicionários com metadados
    """
    print("[ANALISE] Carregando metadados JSON...")

    json_files = list(STYLES_JSON_DIR.glob('*.json'))

    if sample_size and sample_size < len(json_files):
        json_files = np.random.choice(json_files, sample_size, replace=False)

    print(f"  Carregando {len(json_files):,} arquivos JSON...")

    metadata_list = []
    failed = []

    for json_path in tqdm(json_files, desc="Lendo JSONs"):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Extrair apenas a seção 'data' se existir
                if 'data' in data:
                    metadata_list.append(data['data'])
                else:
                    metadata_list.append(data)
        except Exception as e:
            failed.append((str(json_path), str(e)))

    print(f"  [OK] Carregados: {len(metadata_list):,}")
    if failed:
        print(f"  [AVISO]  Falhas: {len(failed)}")

    return metadata_list


def analyze_json_structure(metadata_list: List[Dict]) -> Dict:
    """
    Analisa a estrutura dos metadados JSON.

    Args:
        metadata_list: Lista de dicionários de metadados

    Returns:
        Dicionário com análise de estrutura
    """
    print("\n[BUSCA] Analisando estrutura dos metadados...")

    # Campos presentes
    all_fields = set()
    field_presence = defaultdict(int)

    for item in metadata_list:
        fields = set(item.keys())
        all_fields.update(fields)
        for field in fields:
            field_presence[field] += 1

    total_items = len(metadata_list)

    # Calcular completude
    field_completeness = {
        field: (count / total_items) * 100
        for field, count in field_presence.items()
    }

    # Ordenar por completude
    sorted_fields = sorted(field_completeness.items(), key=lambda x: x[1], reverse=True)

    print(f"\n  Total de campos únicos: {len(all_fields)}")
    print(f"\n  Top 20 campos por completude:")
    for field, completeness in sorted_fields[:20]:
        print(f"    {field}: {completeness:.1f}% ({field_presence[field]:,}/{total_items:,})")

    return {
        'total_fields': len(all_fields),
        'all_fields': list(all_fields),
        'field_presence': dict(field_presence),
        'field_completeness': field_completeness,
    }


def analyze_product_descriptions(metadata_list: List[Dict]) -> Dict:
    """
    Analisa as descrições de produtos.

    Args:
        metadata_list: Lista de metadados

    Returns:
        Estatísticas sobre descrições
    """
    print("\n[TEXTO] Analisando descrições de produtos...")

    descriptions = []
    style_notes = []
    materials_care = []

    for item in metadata_list:
        # productDisplayName
        if 'productDisplayName' in item:
            descriptions.append(item['productDisplayName'])

        # productDescriptors
        if 'productDescriptors' in item:
            descriptors = item['productDescriptors']

            if 'description' in descriptors and 'value' in descriptors['description']:
                desc_value = descriptors['description']['value']
                descriptions.append(desc_value)

            if 'style_note' in descriptors and 'value' in descriptors['style_note']:
                style_notes.append(descriptors['style_note']['value'])

            if 'materials_care_desc' in descriptors and 'value' in descriptors['materials_care_desc']:
                materials_care.append(descriptors['materials_care_desc']['value'])

    # Remover HTML tags para análise de texto
    import re

    def remove_html(text):
        if isinstance(text, str):
            return re.sub(r'<[^>]+>', '', text)
        return ""

    descriptions_clean = [remove_html(d) for d in descriptions]
    style_notes_clean = [remove_html(s) for s in style_notes]

    # Análise de comprimento
    desc_lengths = [len(d.split()) for d in descriptions_clean if d]
    style_lengths = [len(s.split()) for s in style_notes_clean if s]

    stats = {
        'total_descriptions': len(descriptions),
        'total_style_notes': len(style_notes),
        'total_materials_care': len(materials_care),
        'description_lengths': {
            'min': min(desc_lengths) if desc_lengths else 0,
            'max': max(desc_lengths) if desc_lengths else 0,
            'mean': np.mean(desc_lengths) if desc_lengths else 0,
            'median': np.median(desc_lengths) if desc_lengths else 0,
        },
        'style_note_lengths': {
            'min': min(style_lengths) if style_lengths else 0,
            'max': max(style_lengths) if style_lengths else 0,
            'mean': np.mean(style_lengths) if style_lengths else 0,
            'median': np.median(style_lengths) if style_lengths else 0,
        },
        'raw_data': {
            'desc_lengths': desc_lengths,
            'style_lengths': style_lengths,
        }
    }

    print(f"  Total de descrições: {stats['total_descriptions']:,}")
    print(f"  Total de style notes: {stats['total_style_notes']:,}")
    print(f"  Total de materials & care: {stats['total_materials_care']:,}")
    print(f"\n  Comprimento das descrições (palavras):")
    print(f"    Min: {stats['description_lengths']['min']:.0f}")
    print(f"    Max: {stats['description_lengths']['max']:.0f}")
    print(f"    Média: {stats['description_lengths']['mean']:.1f}")
    print(f"    Mediana: {stats['description_lengths']['median']:.0f}")

    return stats


def analyze_prices(metadata_list: List[Dict]) -> Dict:
    """
    Analisa a distribuição de preços.

    Args:
        metadata_list: Lista de metadados

    Returns:
        Estatísticas de preços
    """
    print("\n[PRECOS] Analisando preços...")

    prices = []
    discounted_prices = []
    discount_percentages = []

    for item in metadata_list:
        if 'price' in item and item['price'] is not None:
            try:
                price = float(item['price'])
                prices.append(price)

                if 'discountedPrice' in item and item['discountedPrice'] is not None:
                    disc_price = float(item['discountedPrice'])
                    discounted_prices.append(disc_price)

                    if price > 0:
                        discount_pct = ((price - disc_price) / price) * 100
                        discount_percentages.append(discount_pct)
            except (ValueError, TypeError):
                continue

    stats = {
        'total_with_price': len(prices),
        'price': {
            'min': min(prices) if prices else 0,
            'max': max(prices) if prices else 0,
            'mean': np.mean(prices) if prices else 0,
            'median': np.median(prices) if prices else 0,
            'std': np.std(prices) if prices else 0,
        },
        'discount_percentage': {
            'mean': np.mean(discount_percentages) if discount_percentages else 0,
            'median': np.median(discount_percentages) if discount_percentages else 0,
            'max': max(discount_percentages) if discount_percentages else 0,
        },
        'raw_data': {
            'prices': prices,
            'discount_percentages': discount_percentages,
        }
    }

    print(f"  Produtos com preço: {stats['total_with_price']:,}")
    print(f"  Preço (min/max/média): {stats['price']['min']:.2f} / {stats['price']['max']:.2f} / {stats['price']['mean']:.2f}")
    print(f"  Desconto médio: {stats['discount_percentage']['mean']:.1f}%")

    return stats


def analyze_attributes(metadata_list: List[Dict]) -> Dict:
    """
    Analisa atributos de produtos (Fit, Fabric, Occasion, etc.).

    Args:
        metadata_list: Lista de metadados

    Returns:
        Estatísticas de atributos
    """
    print("\n[ATRIBUTOS]  Analisando atributos de produtos...")

    all_attributes = defaultdict(Counter)

    for item in metadata_list:
        if 'articleAttributes' in item and isinstance(item['articleAttributes'], dict):
            for attr_name, attr_value in item['articleAttributes'].items():
                if attr_value and attr_value != 'NA':
                    all_attributes[attr_name][attr_value] += 1

    print(f"\n  Total de tipos de atributos: {len(all_attributes)}")
    print(f"\n  Top atributos:")
    for attr_name, values in sorted(all_attributes.items(), key=lambda x: sum(x[1].values()), reverse=True)[:10]:
        total = sum(values.values())
        print(f"\n    {attr_name} ({total:,} valores, {len(values)} únicos):")
        for value, count in values.most_common(5):
            print(f"      - {value}: {count:,}")

    return {
        'attribute_types': len(all_attributes),
        'attributes': {name: dict(values) for name, values in all_attributes.items()},
    }


def analyze_brands(metadata_list: List[Dict]) -> Dict:
    """
    Analisa marcas de produtos.

    Args:
        metadata_list: Lista de metadados

    Returns:
        Estatísticas de marcas
    """
    print("\n[MARCAS] Analisando marcas...")

    brands = []

    for item in metadata_list:
        if 'brandName' in item and item['brandName']:
            brands.append(item['brandName'])

    brand_counts = Counter(brands)

    print(f"  Total de marcas únicas: {len(brand_counts):,}")
    print(f"\n  Top 15 marcas:")
    for brand, count in brand_counts.most_common(15):
        pct = (count / len(brands)) * 100 if brands else 0
        print(f"    {brand}: {count:,} ({pct:.2f}%)")

    return {
        'total_brands': len(brand_counts),
        'brand_distribution': dict(brand_counts),
    }


def create_metadata_visualizations(desc_stats: Dict, price_stats: Dict):
    """
    Cria visualizações para metadados.

    Args:
        desc_stats: Estatísticas de descrições
        price_stats: Estatísticas de preços
    """
    print("\n[GERANDO] Gerando visualizações de metadados...")

    # 1. Distribuição de comprimento de descrições
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    if desc_stats['raw_data']['desc_lengths']:
        axes[0].hist(desc_stats['raw_data']['desc_lengths'], bins=50, color='steelblue', edgecolor='black', alpha=0.7)
        axes[0].axvline(desc_stats['description_lengths']['mean'], color='red', linestyle='--', linewidth=2,
                       label=f"Média: {desc_stats['description_lengths']['mean']:.1f}")
        axes[0].set_title('Comprimento das Descrições de Produtos', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('Número de Palavras')
        axes[0].set_ylabel('Frequência')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

    if desc_stats['raw_data']['style_lengths']:
        axes[1].hist(desc_stats['raw_data']['style_lengths'], bins=50, color='forestgreen', edgecolor='black', alpha=0.7)
        axes[1].axvline(desc_stats['style_note_lengths']['mean'], color='red', linestyle='--', linewidth=2,
                       label=f"Média: {desc_stats['style_note_lengths']['mean']:.1f}")
        axes[1].set_title('Comprimento das Style Notes', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Número de Palavras')
        axes[1].set_ylabel('Frequência')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'description_lengths.png', dpi=300, bbox_inches='tight')
    print(f"  [OK] Salvo: {FIGURES_DIR / 'description_lengths.png'}")

    # 2. Distribuição de preços
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    if price_stats['raw_data']['prices']:
        # Remover outliers extremos para melhor visualização
        prices_clean = [p for p in price_stats['raw_data']['prices'] if p < np.percentile(price_stats['raw_data']['prices'], 99)]

        axes[0].hist(prices_clean, bins=50, color='gold', edgecolor='black', alpha=0.7)
        axes[0].axvline(price_stats['price']['mean'], color='red', linestyle='--', linewidth=2,
                       label=f"Média: {price_stats['price']['mean']:.2f}")
        axes[0].set_title('Distribuição de Preços (99% percentil)', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('Preço')
        axes[0].set_ylabel('Frequência')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

    if price_stats['raw_data']['discount_percentages']:
        axes[1].hist(price_stats['raw_data']['discount_percentages'], bins=50, color='coral', edgecolor='black', alpha=0.7)
        axes[1].axvline(price_stats['discount_percentage']['mean'], color='red', linestyle='--', linewidth=2,
                       label=f"Média: {price_stats['discount_percentage']['mean']:.1f}%")
        axes[1].set_title('Distribuição de Descontos', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Desconto (%)')
        axes[1].set_ylabel('Frequência')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'price_distribution.png', dpi=300, bbox_inches='tight')
    print(f"  [OK] Salvo: {FIGURES_DIR / 'price_distribution.png'}")


def save_metadata_report(structure: Dict, desc_stats: Dict, price_stats: Dict, attr_stats: Dict, brand_stats: Dict):
    """
    Salva relatório de análise de metadados.
    """
    print("\n[SALVANDO] Salvando relatório de metadados...")

    report_path = OUTPUTS_DIR / 'metadata_analysis_report.txt'

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("RELATÓRIO DE ANÁLISE DE METADADOS JSON\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. ESTRUTURA DOS METADADOS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total de campos únicos: {structure['total_fields']}\n\n")
        f.write("Completude dos campos (top 30):\n")
        sorted_fields = sorted(structure['field_completeness'].items(), key=lambda x: x[1], reverse=True)
        for field, completeness in sorted_fields[:30]:
            count = structure['field_presence'][field]
            f.write(f"  {field}: {completeness:.1f}% ({count:,} registros)\n")

        f.write("\n2. DESCRIÇÕES DE PRODUTOS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total de descrições: {desc_stats['total_descriptions']:,}\n")
        f.write(f"Total de style notes: {desc_stats['total_style_notes']:,}\n")
        f.write(f"Total de materials & care: {desc_stats['total_materials_care']:,}\n\n")
        f.write("Comprimento das descrições (palavras):\n")
        f.write(f"  Min: {desc_stats['description_lengths']['min']:.0f}\n")
        f.write(f"  Max: {desc_stats['description_lengths']['max']:.0f}\n")
        f.write(f"  Média: {desc_stats['description_lengths']['mean']:.1f}\n")
        f.write(f"  Mediana: {desc_stats['description_lengths']['median']:.0f}\n")

        f.write("\n3. PREÇOS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Produtos com preço: {price_stats['total_with_price']:,}\n")
        f.write(f"Preço mínimo: {price_stats['price']['min']:.2f}\n")
        f.write(f"Preço máximo: {price_stats['price']['max']:.2f}\n")
        f.write(f"Preço médio: {price_stats['price']['mean']:.2f}\n")
        f.write(f"Preço mediano: {price_stats['price']['median']:.2f}\n")
        f.write(f"Desconto médio: {price_stats['discount_percentage']['mean']:.1f}%\n")

        f.write("\n4. ATRIBUTOS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Tipos de atributos: {attr_stats['attribute_types']}\n")

        f.write("\n5. MARCAS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total de marcas únicas: {brand_stats['total_brands']:,}\n\n")
        f.write("Top 20 marcas:\n")
        sorted_brands = sorted(brand_stats['brand_distribution'].items(), key=lambda x: x[1], reverse=True)
        for brand, count in sorted_brands[:20]:
            f.write(f"  {brand}: {count:,}\n")

        f.write("\n" + "=" * 80 + "\n")

    print(f"  [OK] Salvo: {report_path}")


def main():
    """Função principal."""
    print("=" * 80)
    print("ANÁLISE DE METADADOS JSON - FASHION PRODUCT IMAGES DATASET")
    print("=" * 80)

    # Carregar JSONs (usar sample para testes, None para completo)
    sample = SAMPLE_SIZE if SAMPLE_SIZE else None
    metadata_list = load_json_sample(sample_size=sample)

    # Análises
    structure = analyze_json_structure(metadata_list)
    desc_stats = analyze_product_descriptions(metadata_list)
    price_stats = analyze_prices(metadata_list)
    attr_stats = analyze_attributes(metadata_list)
    brand_stats = analyze_brands(metadata_list)

    # Visualizações
    create_metadata_visualizations(desc_stats, price_stats)

    # Relatório
    save_metadata_report(structure, desc_stats, price_stats, attr_stats, brand_stats)

    print("\n" + "=" * 80)
    print("✅ Análise de metadados concluída!")
    print("=" * 80)


if __name__ == "__main__":
    main()