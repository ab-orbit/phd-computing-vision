"""
Exemplos Práticos de Redução de Ruído
======================================

Código educacional com exemplos prontos para usar e modificar.
Cada exemplo é independente e pode ser executado separadamente.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


# =============================================================================
# EXEMPLO 1: Comparação Básica de Filtros
# =============================================================================

def exemplo1_comparacao_basica():
    """
    Compara os 3 filtros mais comuns lado a lado.

    OBJETIVO EDUCACIONAL:
    - Ver diferença entre mediana, gaussiano e bilateral
    - Entender qual funciona melhor para ruído sal e pimenta
    """
    print("\n" + "="*80)
    print("EXEMPLO 1: Comparação Básica de Filtros")
    print("="*80)

    # Carrega imagem
    image = cv2.imread('../images/fotografo_gonzales.png', cv2.IMREAD_GRAYSCALE)

    # Aplica três filtros básicos
    median = cv2.medianBlur(image, 5)
    gaussian = cv2.GaussianBlur(image, (5, 5), 1.0)
    bilateral = cv2.bilateralFilter(image, 9, 75, 75)

    # Visualiza
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))

    images = [
        ('Original (com ruído)', image),
        ('Mediana 5x5', median),
        ('Gaussiano σ=1.0', gaussian),
        ('Bilateral', bilateral)
    ]

    for ax, (title, img) in zip(axes, images):
        ax.imshow(img, cmap='gray', vmin=0, vmax=255)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.axis('off')

    plt.suptitle('Comparação de Filtros Básicos', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()

    print("\n✓ Observe:")
    print("  • Mediana: Remove bem os pontos de ruído")
    print("  • Gaussiano: Borra muito, ruído ainda visível")
    print("  • Bilateral: Remove ruído mantendo bordas")


# =============================================================================
# EXEMPLO 2: Efeito do Tamanho do Kernel
# =============================================================================

def exemplo2_tamanho_kernel():
    """
    Demonstra o efeito de diferentes tamanhos de kernel no filtro de mediana.

    OBJETIVO EDUCACIONAL:
    - Entender trade-off: mais suavização vs perda de detalhes
    - Escolher tamanho adequado para cada situação
    """
    print("\n" + "="*80)
    print("EXEMPLO 2: Efeito do Tamanho do Kernel")
    print("="*80)

    image = cv2.imread('../images/fotografo_gonzales.png', cv2.IMREAD_GRAYSCALE)

    # Testa diferentes tamanhos
    kernels = [3, 5, 7, 9, 11]
    results = []

    for k in kernels:
        filtered = cv2.medianBlur(image, k)
        results.append((f'Kernel {k}x{k}', filtered))

    # Visualiza
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    # Original
    axes[0].imshow(image, cmap='gray', vmin=0, vmax=255)
    axes[0].set_title('Original', fontweight='bold')
    axes[0].axis('off')

    # Filtrados
    for idx, (title, img) in enumerate(results):
        axes[idx+1].imshow(img, cmap='gray', vmin=0, vmax=255)
        axes[idx+1].set_title(title, fontweight='bold')
        axes[idx+1].axis('off')

    plt.suptitle('Filtro de Mediana - Efeito do Tamanho do Kernel', fontsize=14)
    plt.tight_layout()
    plt.show()

    print("\n✓ Observe:")
    print("  • Kernel 3x3: Preserva detalhes, remove menos ruído")
    print("  • Kernel 5x5: Bom equilíbrio")
    print("  • Kernel 9x9+: Remove muito ruído, mas borra demais")


# =============================================================================
# EXEMPLO 3: Criando e Testando com Ruído Artificial
# =============================================================================

def exemplo3_ruido_artificial():
    """
    Adiciona ruído controlado a uma imagem limpa e testa filtros.

    OBJETIVO EDUCACIONAL:
    - Entender como o ruído sal e pimenta é criado
    - Testar filtros em condições controladas
    - Medir eficácia quantitativamente (PSNR)
    """
    print("\n" + "="*80)
    print("EXEMPLO 3: Testando com Ruído Artificial")
    print("="*80)

    # Usa a imagem original como "limpa"
    clean = cv2.imread('../images/fotografo_gonzales.png', cv2.IMREAD_GRAYSCALE)

    # Função para adicionar ruído sal e pimenta
    def add_salt_pepper(img, salt_prob=0.02, pepper_prob=0.02):
        """
        Adiciona ruído sal e pimenta.

        Args:
            img: Imagem original
            salt_prob: Probabilidade de pixel virar branco (sal)
            pepper_prob: Probabilidade de pixel virar preto (pimenta)
        """
        noisy = img.copy()
        h, w = img.shape

        # Adiciona sal (pixels brancos)
        n_salt = int(h * w * salt_prob)
        coords = [np.random.randint(0, i-1, n_salt) for i in img.shape]
        noisy[coords[0], coords[1]] = 255

        # Adiciona pimenta (pixels pretos)
        n_pepper = int(h * w * pepper_prob)
        coords = [np.random.randint(0, i-1, n_pepper) for i in img.shape]
        noisy[coords[0], coords[1]] = 0

        return noisy

    # Adiciona ruído com diferentes intensidades
    noise_levels = [
        (0.01, 0.01, 'Baixo (2%)'),
        (0.03, 0.03, 'Médio (6%)'),
        (0.05, 0.05, 'Alto (10%)')
    ]

    fig, axes = plt.subplots(3, 3, figsize=(12, 12))

    for row, (s, p, level) in enumerate(noise_levels):
        # Adiciona ruído
        noisy = add_salt_pepper(clean, s, p)

        # Aplica mediana
        filtered = cv2.medianBlur(noisy, 5)

        # Calcula PSNR
        mse = np.mean((clean - filtered) ** 2)
        psnr = 20 * np.log10(255.0 / np.sqrt(mse)) if mse > 0 else float('inf')

        # Visualiza
        axes[row, 0].imshow(clean, cmap='gray', vmin=0, vmax=255)
        axes[row, 0].set_title('Original Limpa', fontweight='bold')
        axes[row, 0].axis('off')

        axes[row, 1].imshow(noisy, cmap='gray', vmin=0, vmax=255)
        axes[row, 1].set_title(f'Com Ruído {level}', fontweight='bold')
        axes[row, 1].axis('off')

        axes[row, 2].imshow(filtered, cmap='gray', vmin=0, vmax=255)
        axes[row, 2].set_title(f'Mediana 5x5\nPSNR: {psnr:.2f} dB', fontweight='bold')
        axes[row, 2].axis('off')

    plt.suptitle('Teste com Diferentes Níveis de Ruído', fontsize=14)
    plt.tight_layout()
    plt.show()

    print("\n✓ Observe:")
    print("  • PSNR diminui com mais ruído")
    print("  • Mediana funciona bem até certo nível")
    print("  • Ruído muito alto requer kernel maior")


# =============================================================================
# EXEMPLO 4: Pipeline Personalizado
# =============================================================================

def exemplo4_pipeline_personalizado():
    """
    Cria um pipeline customizado de filtros.

    OBJETIVO EDUCACIONAL:
    - Aprender a combinar múltiplos filtros
    - Entender ordem de aplicação
    - Criar soluções personalizadas
    """
    print("\n" + "="*80)
    print("EXEMPLO 4: Pipeline Personalizado de Filtros")
    print("="*80)

    image = cv2.imread('../images/fotografo_gonzales.png', cv2.IMREAD_GRAYSCALE)

    # PIPELINE 1: Conservador (preserva mais detalhes)
    print("\nPIPELINE 1: Conservador")
    print("  1. Mediana 3x3 (remove ruído impulsivo)")
    print("  2. Bilateral suave (suaviza sem borrar)")

    p1_step1 = cv2.medianBlur(image, 3)
    p1_final = cv2.bilateralFilter(p1_step1, 5, 50, 50)

    # PIPELINE 2: Balanceado
    print("\nPIPELINE 2: Balanceado")
    print("  1. Mediana 3x3 (remove ruído)")
    print("  2. Bilateral moderado (suaviza preservando bordas)")
    print("  3. Gaussiano leve (suavização final)")

    p2_step1 = cv2.medianBlur(image, 3)
    p2_step2 = cv2.bilateralFilter(p2_step1, 5, 75, 75)
    p2_final = cv2.GaussianBlur(p2_step2, (3, 3), 0.5)

    # PIPELINE 3: Agressivo (máxima remoção de ruído)
    print("\nPIPELINE 3: Agressivo")
    print("  1. Mediana 5x5 (remove muito ruído)")
    print("  2. Bilateral forte (suavização intensa)")
    print("  3. Gaussiano (suavização adicional)")

    p3_step1 = cv2.medianBlur(image, 5)
    p3_step2 = cv2.bilateralFilter(p3_step1, 9, 150, 150)
    p3_final = cv2.GaussianBlur(p3_step2, (5, 5), 1.0)

    # Visualiza
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))

    results = [
        ('Original', image),
        ('Conservador', p1_final),
        ('Balanceado', p2_final),
        ('Agressivo', p3_final)
    ]

    for ax, (title, img) in zip(axes, results):
        ax.imshow(img, cmap='gray', vmin=0, vmax=255)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.axis('off')

    plt.suptitle('Pipelines Personalizados', fontsize=14)
    plt.tight_layout()
    plt.show()

    print("\n✓ Observe:")
    print("  • Conservador: Mais detalhes, algum ruído residual")
    print("  • Balanceado: Bom equilíbrio")
    print("  • Agressivo: Muito limpo, mas perde detalhes")


# =============================================================================
# EXEMPLO 5: Análise de Bordas
# =============================================================================

def exemplo5_analise_bordas():
    """
    Compara como diferentes filtros afetam as bordas.

    OBJETIVO EDUCACIONAL:
    - Entender preservação de bordas
    - Ver diferença entre filtros
    - Usar detecção de bordas como métrica
    """
    print("\n" + "="*80)
    print("EXEMPLO 5: Análise de Preservação de Bordas")
    print("="*80)

    image = cv2.imread('../images/fotografo_gonzales.png', cv2.IMREAD_GRAYSCALE)

    # Aplica filtros
    median = cv2.medianBlur(image, 5)
    gaussian = cv2.GaussianBlur(image, (5, 5), 1.0)
    bilateral = cv2.bilateralFilter(image, 9, 75, 75)

    # Detecta bordas com Canny
    def detect_edges(img):
        return cv2.Canny(img, 50, 150)

    edges_orig = detect_edges(image)
    edges_median = detect_edges(median)
    edges_gauss = detect_edges(gaussian)
    edges_bilat = detect_edges(bilateral)

    # Visualiza
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))

    # Linha 1: Imagens filtradas
    images_filtered = [
        ('Original', image),
        ('Mediana', median),
        ('Gaussiano', gaussian),
        ('Bilateral', bilateral)
    ]

    for ax, (title, img) in zip(axes[0], images_filtered):
        ax.imshow(img, cmap='gray', vmin=0, vmax=255)
        ax.set_title(title, fontweight='bold')
        ax.axis('off')

    # Linha 2: Bordas detectadas
    edges_detected = [
        ('Bordas Original', edges_orig),
        ('Bordas Mediana', edges_median),
        ('Bordas Gaussiano', edges_gauss),
        ('Bordas Bilateral', edges_bilat)
    ]

    for ax, (title, img) in zip(axes[1], edges_detected):
        ax.imshow(img, cmap='gray', vmin=0, vmax=255)
        ax.set_title(title, fontweight='bold')
        ax.axis('off')

        # Conta quantidade de bordas
        edge_pixels = np.sum(img > 0)
        ax.text(0.5, -0.1, f'Pixels de borda: {edge_pixels}',
                transform=ax.transAxes, ha='center', fontsize=9)

    plt.suptitle('Preservação de Bordas', fontsize=14)
    plt.tight_layout()
    plt.show()

    print("\n✓ Observe:")
    print("  • Gaussiano: Perde muitas bordas (menos pixels)")
    print("  • Mediana: Preserva razoavelmente")
    print("  • Bilateral: Melhor preservação (mais pixels de borda)")


# =============================================================================
# EXEMPLO 6: Métricas de Qualidade
# =============================================================================

def exemplo6_metricas_qualidade():
    """
    Calcula e compara múltiplas métricas de qualidade.

    OBJETIVO EDUCACIONAL:
    - Aprender a calcular PSNR, MSE, MAE
    - Interpretar métricas
    - Entender limitações
    """
    print("\n" + "="*80)
    print("EXEMPLO 6: Métricas de Qualidade")
    print("="*80)

    original = cv2.imread('../images/fotografo_gonzales.png', cv2.IMREAD_GRAYSCALE)

    # Aplica diferentes filtros
    filters = {
        'Median 3x3': cv2.medianBlur(original, 3),
        'Median 5x5': cv2.medianBlur(original, 5),
        'Gaussian σ=1': cv2.GaussianBlur(original, (5, 5), 1.0),
        'Bilateral': cv2.bilateralFilter(original, 9, 75, 75),
        'NLM h=10': cv2.fastNlMeansDenoising(original, None, 10, 7, 21)
    }

    # Calcula métricas
    print("\n" + "-"*80)
    print(f"{'Filtro':<20} {'MSE':>12} {'PSNR (dB)':>12} {'MAE':>12} {'STD':>12}")
    print("-"*80)

    metrics_list = []

    for name, filtered in filters.items():
        # MSE
        mse = np.mean((original.astype(float) - filtered.astype(float)) ** 2)

        # PSNR
        psnr = 20 * np.log10(255.0 / np.sqrt(mse)) if mse > 0 else float('inf')

        # MAE
        mae = np.mean(np.abs(original.astype(float) - filtered.astype(float)))

        # STD
        std = np.std(filtered)

        metrics_list.append((name, mse, psnr, mae, std))

        print(f"{name:<20} {mse:>12.2f} {psnr:>12.2f} {mae:>12.2f} {std:>12.2f}")

    print("-"*80)

    # Encontra melhor por PSNR
    best = max(metrics_list, key=lambda x: x[2])
    print(f"\n✓ Melhor filtro (PSNR): {best[0]} com {best[2]:.2f} dB")

    # Gráfico de barras
    names = [m[0] for m in metrics_list]
    psnrs = [m[2] for m in metrics_list]

    plt.figure(figsize=(10, 6))
    plt.bar(names, psnrs, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
    plt.xlabel('Filtro', fontweight='bold')
    plt.ylabel('PSNR (dB)', fontweight='bold')
    plt.title('Comparação de Qualidade (PSNR)', fontweight='bold', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()

    print("\n✓ Observe:")
    print("  • Maior PSNR = melhor qualidade")
    print("  • NLM geralmente tem melhor PSNR")
    print("  • Métricas não capturam tudo (avaliação visual também importa)")


# =============================================================================
# MENU PRINCIPAL
# =============================================================================

def main():
    """Menu interativo para escolher exemplos"""
    print("\n" + "="*80)
    print("EXEMPLOS PRÁTICOS DE REDUÇÃO DE RUÍDO")
    print("="*80)

    print("\nEscolha um exemplo:")
    print("1 - Comparação Básica de Filtros")
    print("2 - Efeito do Tamanho do Kernel")
    print("3 - Testando com Ruído Artificial")
    print("4 - Pipeline Personalizado")
    print("5 - Análise de Preservação de Bordas")
    print("6 - Métricas de Qualidade")
    print("7 - Executar TODOS os exemplos")
    print("0 - Sair")

    exemplos = {
        '1': exemplo1_comparacao_basica,
        '2': exemplo2_tamanho_kernel,
        '3': exemplo3_ruido_artificial,
        '4': exemplo4_pipeline_personalizado,
        '5': exemplo5_analise_bordas,
        '6': exemplo6_metricas_qualidade
    }

    escolha = input("\nOpção: ").strip()

    if escolha == '7':
        for i in range(1, 7):
            exemplos[str(i)]()
            input("\nPressione Enter para próximo exemplo...")
    elif escolha in exemplos:
        exemplos[escolha]()
    elif escolha == '0':
        print("Saindo...")
    else:
        print("Opção inválida!")


if __name__ == "__main__":
    main()