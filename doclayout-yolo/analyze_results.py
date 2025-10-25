#!/usr/bin/env python3
"""
Script para análise detalhada dos resultados de classificação.

Este script analisa os resultados salvos e gera:
- Estatísticas detalhadas por categoria
- Visualizações de performance
- Identificação de padrões de erro
- Análise das classes detectadas pelo modelo
- Recomendações de melhoria
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


def load_classification_report(results_dir: Path) -> Dict[str, Any]:
    """Carrega relatório principal de classificação."""
    report_path = results_dir / 'classification_report.json'
    with open(report_path, 'r') as f:
        return json.load(f)


def load_individual_analyses(results_dir: Path) -> Dict[str, List[Dict]]:
    """Carrega análises individuais de cada documento."""
    categories = ['email', 'advertisement', 'scientific_publication']
    analyses = {}

    for category in categories:
        category_dir = results_dir / category
        if not category_dir.exists():
            continue

        category_analyses = []
        for json_file in category_dir.glob('*_analysis.json'):
            with open(json_file, 'r') as f:
                analysis = json.load(f)
                category_analyses.append(analysis)

        analyses[category] = category_analyses

    return analyses


def analyze_detected_classes(analyses: Dict[str, List[Dict]]) -> pd.DataFrame:
    """
    Analisa quais classes estão sendo detectadas pelo modelo.

    Problema identificado: O modelo DocLayout-YOLO pode usar nomes
    de classes diferentes dos esperados pelo código de classificação.
    """
    all_classes = Counter()
    classes_by_category = defaultdict(Counter)

    for category, category_analyses in analyses.items():
        for analysis in category_analyses:
            element_counts = analysis.get('element_counts', {})
            for class_name, count in element_counts.items():
                all_classes[class_name] += count
                classes_by_category[category][class_name] += count

    print("\n" + "=" * 80)
    print("CLASSES DETECTADAS PELO MODELO")
    print("=" * 80)
    print("\nTodas as classes encontradas:")
    print("-" * 80)
    for class_name, count in all_classes.most_common():
        print(f"  {class_name:30s}: {count:4d} ocorrências")

    print("\n" + "=" * 80)
    print("CLASSES POR CATEGORIA")
    print("=" * 80)
    for category in sorted(classes_by_category.keys()):
        print(f"\n{category.upper()}:")
        print("-" * 80)
        for class_name, count in classes_by_category[category].most_common(10):
            print(f"  {class_name:30s}: {count:4d}")

    return all_classes, classes_by_category


def analyze_features(analyses: Dict[str, List[Dict]]) -> pd.DataFrame:
    """Analisa distribuição de features por categoria."""
    features_data = []

    for category, category_analyses in analyses.items():
        for analysis in category_analyses:
            features = analysis.get('features', {})
            features['true_category'] = category
            features['predicted_category'] = analysis.get('predicted_category', 'unknown')
            features['correct'] = analysis.get('correct', False)
            features['document'] = Path(analysis['image_path']).name
            features_data.append(features)

    df = pd.DataFrame(features_data)
    return df


def plot_confusion_matrix(report: Dict[str, Any], output_dir: Path):
    """Gera visualização da matriz de confusão."""
    confusion = report['confusion_matrix']
    categories = list(confusion.keys())

    # Criar matriz numpy
    matrix = np.zeros((len(categories), len(categories)))
    for i, true_cat in enumerate(categories):
        for j, pred_cat in enumerate(categories):
            matrix[i, j] = confusion[true_cat][pred_cat]

    # Plotar
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        matrix,
        annot=True,
        fmt='.0f',
        cmap='YlOrRd',
        xticklabels=[c.replace('_', '\n') for c in categories],
        yticklabels=[c.replace('_', '\n') for c in categories],
        cbar_kws={'label': 'Número de documentos'}
    )
    plt.xlabel('Categoria Predita', fontsize=12, fontweight='bold')
    plt.ylabel('Categoria Verdadeira', fontsize=12, fontweight='bold')
    plt.title('Matriz de Confusão - Classificação de Documentos', fontsize=14, fontweight='bold')
    plt.tight_layout()

    output_path = output_dir / 'confusion_matrix.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Matriz de confusão salva em: {output_path}")
    plt.close()


def plot_accuracy_by_category(report: Dict[str, Any], output_dir: Path):
    """Gera gráfico de acurácia por categoria."""
    categories = []
    accuracies = []
    corrects = []
    totals = []

    for cat, stats in report['category_stats'].items():
        categories.append(cat.replace('_', '\n'))
        accuracies.append(stats['accuracy'] * 100)
        corrects.append(stats['correct'])
        totals.append(stats['total_samples'])

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(categories, accuracies, color=['#2ecc71' if a >= 50 else '#e74c3c' for a in accuracies],
                  edgecolor='black', linewidth=1.5)

    # Adicionar valores no topo das barras
    for i, (bar, acc, cor, tot) in enumerate(zip(bars, accuracies, corrects, totals)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{acc:.1f}%\n({cor}/{tot})',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    # Linha de referência em 50%
    ax.axhline(y=50, color='orange', linestyle='--', linewidth=2, label='50% (Random)')
    ax.axhline(y=report['overall_accuracy']*100, color='blue', linestyle='--',
               linewidth=2, label=f'Média: {report["overall_accuracy"]*100:.1f}%')

    ax.set_ylabel('Acurácia (%)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Categoria', fontsize=12, fontweight='bold')
    ax.set_title('Acurácia por Categoria de Documento', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 110)
    ax.legend(loc='upper right')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    output_path = output_dir / 'accuracy_by_category.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Gráfico de acurácia salvo em: {output_path}")
    plt.close()


def plot_feature_distributions(df: pd.DataFrame, output_dir: Path):
    """Gera gráficos de distribuição de features por categoria."""
    key_features = [
        'num_equations', 'num_tables', 'num_figures',
        'num_titles', 'num_references', 'total_elements'
    ]

    # Verificar quais features existem
    available_features = [f for f in key_features if f in df.columns]

    if not available_features:
        print("⚠️  Nenhuma feature numérica disponível para plotar")
        return

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for idx, feature in enumerate(available_features):
        ax = axes[idx]

        for category in df['true_category'].unique():
            data = df[df['true_category'] == category][feature]
            ax.hist(data, alpha=0.6, label=category.replace('_', ' '), bins=10)

        ax.set_xlabel(feature.replace('_', ' ').title(), fontsize=10)
        ax.set_ylabel('Frequência', fontsize=10)
        ax.set_title(f'Distribuição: {feature.replace("_", " ").title()}', fontsize=11, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)

    # Remover axes extras
    for idx in range(len(available_features), len(axes)):
        fig.delaxes(axes[idx])

    plt.tight_layout()
    output_path = output_dir / 'feature_distributions.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Distribuições de features salvas em: {output_path}")
    plt.close()


def identify_error_patterns(df: pd.DataFrame) -> Dict[str, Any]:
    """Identifica padrões nos erros de classificação."""
    print("\n" + "=" * 80)
    print("ANÁLISE DE ERROS")
    print("=" * 80)

    errors = df[df['correct'] == False]
    total_errors = len(errors)

    print(f"\nTotal de erros: {total_errors}/{len(df)} ({total_errors/len(df)*100:.1f}%)")

    # Erros por categoria verdadeira
    print("\nErros por categoria verdadeira:")
    print("-" * 80)
    for category in df['true_category'].unique():
        cat_errors = errors[errors['true_category'] == category]
        cat_total = len(df[df['true_category'] == category])
        print(f"  {category:30s}: {len(cat_errors)}/{cat_total} "
              f"({len(cat_errors)/cat_total*100:.1f}%)")

    # Confusões mais comuns
    print("\nConfusões mais comuns (Verdadeiro → Predito):")
    print("-" * 80)
    confusion_pairs = errors.groupby(['true_category', 'predicted_category']).size()
    for (true_cat, pred_cat), count in confusion_pairs.sort_values(ascending=False).items():
        print(f"  {true_cat:30s} → {pred_cat:30s}: {count:2d} casos")

    return {
        'total_errors': total_errors,
        'error_rate': total_errors / len(df),
        'errors_by_category': errors.groupby('true_category').size().to_dict(),
        'confusion_pairs': confusion_pairs.to_dict()
    }


def diagnose_classification_problem(all_classes: Counter, df: pd.DataFrame):
    """Diagnóstico do problema principal de classificação."""
    print("\n" + "=" * 80)
    print("DIAGNÓSTICO DO PROBLEMA")
    print("=" * 80)

    # Verificar se classes esperadas estão sendo detectadas
    expected_classes = ['equation', 'reference', 'table', 'figure', 'text', 'title']
    detected_classes = set(all_classes.keys())

    print("\nClasses esperadas vs detectadas:")
    print("-" * 80)
    for expected in expected_classes:
        if expected in detected_classes:
            print(f"  ✓ {expected:20s}: DETECTADA ({all_classes[expected]} vezes)")
        else:
            print(f"  ✗ {expected:20s}: NÃO DETECTADA")

    # Verificar features zeradas
    feature_cols = [col for col in df.columns if col.startswith('num_') or col.startswith('has_')]
    zero_features = []

    for col in feature_cols:
        if df[col].sum() == 0:
            zero_features.append(col)

    if zero_features:
        print(f"\n⚠️  PROBLEMA IDENTIFICADO:")
        print("-" * 80)
        print(f"  {len(zero_features)} features estão SEMPRE ZERADAS:")
        for feature in zero_features:
            print(f"    - {feature}")

        print("\n💡 CAUSA PROVÁVEL:")
        print("-" * 80)
        print("  O modelo DocLayout-YOLO está usando nomes de classes")
        print("  DIFERENTES dos esperados pelo código de classificação.")
        print("")
        print("  Exemplo:")
        print("    - Código espera: 'text', 'equation', 'reference'")
        print("    - Modelo retorna: 'plain text', 'abandon', etc.")

    # Verificar se scientific_publication nunca é predito
    if 'predicted_category' in df.columns:
        pred_counts = df['predicted_category'].value_counts()
        print("\nDistribuição de predições:")
        print("-" * 80)
        for category, count in pred_counts.items():
            print(f"  {category:30s}: {count:3d} ({count/len(df)*100:.1f}%)")

        if 'scientific_publication' not in pred_counts or pred_counts['scientific_publication'] == 0:
            print("\n⚠️  PROBLEMA CRÍTICO:")
            print("-" * 80)
            print("  A categoria 'scientific_publication' NUNCA é predita!")
            print("  Isso indica que as heurísticas não estão funcionando.")


def generate_recommendations():
    """Gera recomendações de melhoria."""
    print("\n" + "=" * 80)
    print("RECOMENDAÇÕES DE MELHORIA")
    print("=" * 80)

    recommendations = [
        {
            'title': '1. Mapear Nomes de Classes',
            'description': 'Criar um mapeamento entre os nomes de classes do modelo e os esperados',
            'code': '''
# Em analyze_layout.py, adicionar mapeamento:
CLASS_MAPPING = {
    'plain text': 'text',
    'abandon': 'noise',  # ou ignorar
    'title': 'title',
    'figure': 'figure',
    # ... adicionar outros mapeamentos
}
'''
        },
        {
            'title': '2. Investigar Classes do Modelo',
            'description': 'Verificar documentação do modelo para ver todas as classes suportadas',
            'code': '''
# Listar classes do modelo:
from doclayout_yolo import YOLOv10
model = YOLOv10('modelo.pt')
print(model.names)  # Dicionário de classes
'''
        },
        {
            'title': '3. Ajustar Heurísticas',
            'description': 'Recalibrar os pesos baseado nas classes realmente detectadas',
            'code': '''
# Em classify_documents.py, ajustar pesos baseado em features disponíveis
# Usar 'plain text_density' em vez de 'text_density'
'''
        },
        {
            'title': '4. Usar Machine Learning',
            'description': 'Treinar um classificador com as features extraídas',
            'code': '''
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Extrair features de todos os documentos
# Treinar classificador supervisionado
# Isso aprende automaticamente os padrões
'''
        }
    ]

    for rec in recommendations:
        print(f"\n{rec['title']}")
        print("-" * 80)
        print(f"{rec['description']}")
        if 'code' in rec:
            print(f"\nExemplo:")
            print(rec['code'])


def main():
    """Função principal de análise."""
    results_dir = Path('results')

    if not results_dir.exists():
        print(f"❌ Diretório de resultados não encontrado: {results_dir}")
        print("Execute primeiro: python classify_documents.py")
        return 1

    print("=" * 80)
    print("ANÁLISE DETALHADA DOS RESULTADOS DE CLASSIFICAÇÃO")
    print("=" * 80)
    print(f"\nDiretório: {results_dir.absolute()}")

    try:
        # Carregar dados
        print("\n" + "-" * 80)
        print("Carregando dados...")
        print("-" * 80)

        report = load_classification_report(results_dir)
        print(f"✓ Relatório principal carregado")

        analyses = load_individual_analyses(results_dir)
        total_docs = sum(len(docs) for docs in analyses.values())
        print(f"✓ {total_docs} análises individuais carregadas")

        # Análise de classes detectadas
        all_classes, classes_by_category = analyze_detected_classes(analyses)

        # Análise de features
        print("\n" + "-" * 80)
        print("Analisando features...")
        print("-" * 80)
        df = analyze_features(analyses)
        print(f"✓ DataFrame criado com {len(df)} documentos")

        # Criar diretório de análise
        analysis_dir = results_dir / 'analysis'
        analysis_dir.mkdir(exist_ok=True)

        # Gerar visualizações
        print("\n" + "-" * 80)
        print("Gerando visualizações...")
        print("-" * 80)
        plot_confusion_matrix(report, analysis_dir)
        plot_accuracy_by_category(report, analysis_dir)
        plot_feature_distributions(df, analysis_dir)

        # Análise de erros
        error_patterns = identify_error_patterns(df)

        # Diagnóstico
        diagnose_classification_problem(all_classes, df)

        # Recomendações
        generate_recommendations()

        # Salvar análise completa
        analysis_report = {
            'summary': report,
            'detected_classes': dict(all_classes),
            'error_patterns': error_patterns,
            'feature_statistics': df.describe().to_dict()
        }

        report_path = analysis_dir / 'detailed_analysis.json'
        with open(report_path, 'w') as f:
            json.dump(analysis_report, f, indent=2)

        # Salvar DataFrame
        df.to_csv(analysis_dir / 'features_data.csv', index=False)

        print("\n" + "=" * 80)
        print("✓ ANÁLISE CONCLUÍDA")
        print("=" * 80)
        print(f"\nArquivos gerados em: {analysis_dir}")
        print(f"  - confusion_matrix.png")
        print(f"  - accuracy_by_category.png")
        print(f"  - feature_distributions.png")
        print(f"  - detailed_analysis.json")
        print(f"  - features_data.csv")
        print("=" * 80)

        return 0

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
