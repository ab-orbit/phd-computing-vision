#!/usr/bin/env python3
"""
Fase 3: Geração de Visualizações

Este script cria todas as visualizações necessárias para a análise comparativa.

Visualizações:
1. Boxplots comparativos (4 métricas principais)
2. Gráficos de linha (acurácia e F1-score por simulação)
3. Comparação por classe
4. Comparação de tempo
5. Matrizes de confusão agregadas
6. Dispersão acurácia vs tempo

Saídas:
- figures/comparative_boxplots.png
- figures/line_plot_accuracy_f1.png
- figures/metrics_by_class.png
- figures/time_comparison.png
- figures/confusion_matrices.png
- figures/accuracy_vs_time.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configurações de estilo
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10

# Caminhos
DATA_PATH = Path(__file__).parent / 'data' / 'consolidated_results.csv'
OUTPUT_PATH = Path(__file__).parent / 'figures'

# Cores para os modelos
CORES_MODELOS = {
    'Google Vision': '#3498db',  # Azul
    'Roboflow': '#e74c3c',       # Vermelho
    'YOLO11': '#2ecc71'          # Verde
}


def criar_boxplots_comparativos(df, output_path):
    """
    Cria grid 2x2 de boxplots para as 4 métricas principais.

    Args:
        df: DataFrame consolidado
        output_path: Path para salvar a figura
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Comparação de Métricas entre Modelos', fontsize=16, fontweight='bold', y=0.995)

    metricas = [
        ('acuracia_geral', 'Acurácia Geral'),
        ('precisao_macro', 'Precisão Macro'),
        ('recall_macro', 'Recall Macro'),
        ('f1_macro', 'F1-Score Macro')
    ]

    for idx, (metrica, titulo) in enumerate(metricas):
        ax = axes[idx // 2, idx % 2]

        # Preparar dados para boxplot
        dados_plot = []
        labels_plot = []

        for modelo in df['modelo'].unique():
            df_modelo = df[df['modelo'] == modelo]
            dados_plot.append(df_modelo[metrica].values)
            labels_plot.append(modelo)

        # Criar boxplot
        bp = ax.boxplot(dados_plot, labels=labels_plot, patch_artist=True,
                        widths=0.6, showmeans=True,
                        meanprops=dict(marker='D', markerfacecolor='red', markersize=6))

        # Colorir boxes
        for patch, label in zip(bp['boxes'], labels_plot):
            patch.set_facecolor(CORES_MODELOS.get(label, '#95a5a6'))
            patch.set_alpha(0.7)

        # Configurar eixos
        ax.set_ylabel('Valor da Métrica', fontweight='bold')
        ax.set_title(titulo, fontweight='bold', pad=10)
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)

        # Adicionar linha em 0.5
        ax.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5, linewidth=1)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

    print(f"✓ Boxplots comparativos salvos em: {output_path}")


def criar_graficos_linha(df, output_path):
    """
    Cria gráficos de linha para acurácia e F1-score por simulação.

    Args:
        df: DataFrame consolidado
        output_path: Path para salvar a figura
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    fig.suptitle('Evolução das Métricas por Simulação', fontsize=16, fontweight='bold')

    metricas = [
        ('acuracia_geral', 'Acurácia Geral'),
        ('f1_macro', 'F1-Score Macro')
    ]

    for idx, (metrica, titulo) in enumerate(metricas):
        ax = axes[idx]

        for modelo in sorted(df['modelo'].unique()):
            df_modelo = df[df['modelo'] == modelo].sort_values('numero_simulacao')

            ax.plot(df_modelo['numero_simulacao'], df_modelo[metrica],
                   marker='o', markersize=4, linewidth=1.5,
                   label=modelo, color=CORES_MODELOS.get(modelo, '#95a5a6'),
                   alpha=0.8)

        # Configurar eixos
        ax.set_xlabel('Número da Simulação', fontweight='bold')
        ax.set_ylabel(titulo, fontweight='bold')
        ax.set_title(f'{titulo} por Simulação', fontweight='bold', pad=10)
        ax.legend(loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        ax.set_xlim(0, 31)
        ax.set_ylim(-0.05, 1.05)

        # Linha em 0.5
        ax.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5, linewidth=1)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

    print(f"✓ Gráficos de linha salvos em: {output_path}")


def criar_metricas_por_classe(df, output_path):
    """
    Cria comparação de métricas por classe (alegria vs raiva).

    Args:
        df: DataFrame consolidado
        output_path: Path para salvar a figura
    """
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle('Comparação de Métricas por Classe', fontsize=16, fontweight='bold', y=0.995)

    classes = ['alegria', 'raiva']
    metricas = ['acuracia', 'precisao', 'recall', 'f1']

    for idx_classe, classe in enumerate(classes):
        for idx_metrica, metrica_base in enumerate(metricas[:3]):  # Apenas 3 métricas
            ax = axes[idx_classe, idx_metrica]

            metrica = f'{metrica_base}_{classe}'
            titulo = f'{metrica_base.capitalize()} - {classe.capitalize()}'

            # Preparar dados
            dados_plot = []
            labels_plot = []

            for modelo in df['modelo'].unique():
                df_modelo = df[df['modelo'] == modelo]
                if metrica in df_modelo.columns:
                    dados_plot.append(df_modelo[metrica].values)
                    labels_plot.append(modelo)

            # Criar boxplot
            bp = ax.boxplot(dados_plot, labels=labels_plot, patch_artist=True,
                            widths=0.5, showmeans=True,
                            meanprops=dict(marker='D', markerfacecolor='red', markersize=5))

            # Colorir
            for patch, label in zip(bp['boxes'], labels_plot):
                patch.set_facecolor(CORES_MODELOS.get(label, '#95a5a6'))
                patch.set_alpha(0.7)

            # Configurar
            ax.set_ylabel('Valor', fontweight='bold')
            ax.set_title(titulo, fontweight='bold', pad=10)
            ax.set_ylim(-0.05, 1.05)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.set_axisbelow(True)
            ax.tick_params(axis='x', rotation=15)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

    print(f"✓ Métricas por classe salvas em: {output_path}")


def criar_comparacao_tempo(df, output_path):
    """
    Cria gráfico de barras comparando tempo de processamento.

    Args:
        df: DataFrame consolidado
        output_path: Path para salvar a figura
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Calcular médias e desvios padrão
    modelos = []
    tempos_medios = []
    tempos_std = []

    for modelo in sorted(df['modelo'].unique()):
        df_modelo = df[df['modelo'] == modelo]
        modelos.append(modelo)
        # Converter de ms para segundos
        tempos_medios.append(df_modelo['tempo_total_ms'].mean() / 1000)
        tempos_std.append(df_modelo['tempo_total_ms'].std() / 1000)

    # Criar gráfico de barras
    x_pos = np.arange(len(modelos))
    bars = ax.bar(x_pos, tempos_medios, yerr=tempos_std,
                   color=[CORES_MODELOS.get(m, '#95a5a6') for m in modelos],
                   alpha=0.7, capsize=5, edgecolor='black', linewidth=1.5)

    # Adicionar valores nas barras
    for i, (bar, tempo, std) in enumerate(zip(bars, tempos_medios, tempos_std)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + std + 5,
                f'{tempo:.1f}s\n±{std:.1f}s',
                ha='center', va='bottom', fontweight='bold', fontsize=11)

    # Configurar
    ax.set_ylabel('Tempo Médio por Simulação (segundos)', fontweight='bold', fontsize=12)
    ax.set_xlabel('Modelo', fontweight='bold', fontsize=12)
    ax.set_title('Comparação de Tempo de Processamento', fontweight='bold', fontsize=14, pad=15)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(modelos, fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

    print(f"✓ Comparação de tempo salva em: {output_path}")


def criar_matrizes_confusao(df, output_path):
    """
    Cria matrizes de confusão agregadas para cada modelo.

    Args:
        df: DataFrame consolidado
        output_path: Path para salvar a figura
    """
    modelos = sorted(df['modelo'].unique())
    n_modelos = len(modelos)

    fig, axes = plt.subplots(1, n_modelos, figsize=(6*n_modelos, 5))
    if n_modelos == 1:
        axes = [axes]

    fig.suptitle('Matrizes de Confusão Agregadas (30 simulações)',
                 fontsize=16, fontweight='bold', y=1.02)

    for idx, modelo in enumerate(modelos):
        df_modelo = df[df['modelo'] == modelo]

        # Calcular valores da matriz de confusão
        # VP alegria = qtd_sucesso_alegria
        # FN alegria = total_alegria - qtd_sucesso_alegria
        # VP raiva = qtd_sucesso_raiva
        # FN raiva = total_raiva - qtd_sucesso_raiva
        # FP alegria = FN raiva (raiva classificada como alegria)
        # FP raiva = FN alegria (alegria classificada como raiva)

        vp_alegria = int(df_modelo['qtd_sucesso_alegria'].sum())
        fn_alegria = int((df_modelo['total_alegria'] - df_modelo['qtd_sucesso_alegria']).sum())
        vp_raiva = int(df_modelo['qtd_sucesso_raiva'].sum())
        fn_raiva = int((df_modelo['total_raiva'] - df_modelo['qtd_sucesso_raiva']).sum())

        # Matriz de confusão
        # Linhas: Real, Colunas: Predito
        matriz = np.array([
            [vp_alegria, fn_alegria],  # Real Alegria
            [fn_raiva, vp_raiva]       # Real Raiva
        ], dtype=int)

        # Criar heatmap
        ax = axes[idx]
        sns.heatmap(matriz, annot=True, fmt='d', cmap='Blues',
                   xticklabels=['Alegria', 'Raiva'],
                   yticklabels=['Alegria', 'Raiva'],
                   ax=ax, cbar_kws={'label': 'Contagem'},
                   linewidths=2, linecolor='white')

        ax.set_title(f'{modelo}', fontweight='bold', pad=10, fontsize=13)
        ax.set_ylabel('Classe Real', fontweight='bold', fontsize=11)
        ax.set_xlabel('Classe Predita', fontweight='bold', fontsize=11)

        # Adicionar total
        total = matriz.sum()
        acuracia = (matriz.diagonal().sum() / total) * 100
        ax.text(1, 2.3, f'Total: {total} | Acurácia: {acuracia:.1f}%',
               ha='center', va='top', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

    print(f"✓ Matrizes de confusão salvas em: {output_path}")


def criar_acuracia_vs_tempo(df, output_path):
    """
    Cria scatter plot de acurácia vs tempo (trade-off).

    Args:
        df: DataFrame consolidado
        output_path: Path para salvar a figura
    """
    fig, ax = plt.subplots(figsize=(10, 7))

    # Calcular médias
    modelos = []
    acuracias = []
    tempos = []

    for modelo in df['modelo'].unique():
        df_modelo = df[df['modelo'] == modelo]
        modelos.append(modelo)
        acuracias.append(df_modelo['acuracia_geral'].mean())
        tempos.append(df_modelo['tempo_total_ms'].mean() / 1000)  # Converter para segundos

    # Criar scatter plot
    for modelo, acuracia, tempo in zip(modelos, acuracias, tempos):
        ax.scatter(tempo, acuracia, s=300, alpha=0.7,
                  color=CORES_MODELOS.get(modelo, '#95a5a6'),
                  edgecolors='black', linewidth=2,
                  label=modelo)

        # Adicionar anotação
        ax.annotate(modelo, (tempo, acuracia),
                   xytext=(10, 10), textcoords='offset points',
                   fontsize=11, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))

    # Configurar
    ax.set_xlabel('Tempo Médio por Simulação (segundos)', fontweight='bold', fontsize=12)
    ax.set_ylabel('Acurácia Geral Média', fontweight='bold', fontsize=12)
    ax.set_title('Trade-off: Acurácia vs Tempo de Processamento',
                fontweight='bold', fontsize=14, pad=15)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    # Adicionar quadrantes de referência
    ax.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5, linewidth=1.5)

    # Ajustar limites
    ax.set_ylim(-0.05, 1.05)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

    print(f"✓ Gráfico acurácia vs tempo salvo em: {output_path}")


def main():
    """Executa geração de todas as visualizações."""

    print("="*100)
    print("FASE 3: GERAÇÃO DE VISUALIZAÇÕES")
    print("="*100)
    print()

    # Carregar dados
    print("📂 Carregando dados consolidados...")
    df = pd.read_csv(DATA_PATH)
    print(f"✓ {len(df)} registros carregados ({df['modelo'].nunique()} modelos)\n")

    # Criar visualizações
    print("📊 Gerando visualizações...\n")

    # 1. Boxplots comparativos
    print("1/6 Criando boxplots comparativos...")
    criar_boxplots_comparativos(df, OUTPUT_PATH / 'comparative_boxplots.png')

    # 2. Gráficos de linha
    print("2/6 Criando gráficos de linha...")
    criar_graficos_linha(df, OUTPUT_PATH / 'line_plot_accuracy_f1.png')

    # 3. Métricas por classe
    print("3/6 Criando comparação por classe...")
    criar_metricas_por_classe(df, OUTPUT_PATH / 'metrics_by_class.png')

    # 4. Comparação de tempo
    print("4/6 Criando comparação de tempo...")
    criar_comparacao_tempo(df, OUTPUT_PATH / 'time_comparison.png')

    # 5. Matrizes de confusão
    print("5/6 Criando matrizes de confusão...")
    criar_matrizes_confusao(df, OUTPUT_PATH / 'confusion_matrices.png')

    # 6. Acurácia vs Tempo
    print("6/6 Criando gráfico acurácia vs tempo...")
    criar_acuracia_vs_tempo(df, OUTPUT_PATH / 'accuracy_vs_time.png')

    print("\n\n✅ Fase 3 concluída com sucesso!")
    print("="*100)


if __name__ == '__main__':
    main()
