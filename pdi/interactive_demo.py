"""
Demonstração Interativa de Filtros de Redução de Ruído
=======================================================

Script educacional que permite explorar diferentes filtros de forma interativa,
com explicações detalhadas e visualizações comparativas.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys


class InteractiveFilterDemo:
    """Demonstração interativa de filtros"""

    def __init__(self, image_path):
        self.original = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if self.original is None:
            raise ValueError(f"Não foi possível carregar: {image_path}")

    def demo_median_filter(self):
        """
        DEMONSTRAÇÃO: Filtro de Mediana
        ================================

        O filtro de mediana é especialmente eficaz para ruído sal e pimenta
        porque a MEDIANA é resistente a valores extremos (outliers).
        """
        print("\n" + "=" * 80)
        print("DEMONSTRAÇÃO: FILTRO DE MEDIANA")
        print("=" * 80)

        print("\n📖 CONCEITO:")
        print("   Para cada pixel, substitui o valor pela MEDIANA da vizinhança")
        print("   Mediana = valor do meio quando ordenamos os pixels")

        print("\n💡 POR QUE FUNCIONA:")
        print("   Pixels de ruído (0 ou 255) são extremos")
        print("   A mediana ignora estes extremos!")

        print("\n🔍 EXEMPLO NUMÉRICO:")
        print("   Vizinhança 3x3:")
        print("   [120, 122, 255]    <- 255 é ruído (sal)")
        print("   [115, 125, 130]")
        print("   [ 10, 132, 123]    <- 10 é ruído (pimenta)")

        print("\n   Ordenando: [10, 115, 120, 122, 123, 125, 130, 132, 255]")
        print("   Mediana = 123 (valor do meio)")
        print("   ✓ Ruído ignorado!")

        # Aplica com diferentes tamanhos
        sizes = [3, 5, 7]
        results = []

        for size in sizes:
            filtered = cv2.medianBlur(self.original, size)
            results.append((f"Median {size}x{size}", filtered))

        # Visualiza
        self._visualize_progression(results, "Filtro de Mediana - Efeito do Tamanho do Kernel")

        print("\n📊 OBSERVAÇÕES:")
        print("   • Kernel 3x3: Remove ruído, preserva detalhes")
        print("   • Kernel 5x5: Mais suavização, menos detalhes")
        print("   • Kernel 7x7: Muito suavizado, pode perder informação")

    def demo_gaussian_filter(self):
        """
        DEMONSTRAÇÃO: Filtro Gaussiano
        ===============================

        O filtro gaussiano usa uma distribuição normal para dar pesos aos pixels vizinhos.
        Pixels mais próximos têm mais influência.
        """
        print("\n" + "=" * 80)
        print("DEMONSTRAÇÃO: FILTRO GAUSSIANO")
        print("=" * 80)

        print("\n📖 CONCEITO:")
        print("   Convolução com kernel gaussiano")
        print("   Peso dos pixels diminui com a distância (distribuição normal)")

        print("\n🧮 FÓRMULA:")
        print("   G(x,y) = (1/(2πσ²)) * e^(-(x²+y²)/(2σ²))")
        print("   σ (sigma) = desvio padrão")

        print("\n💡 EXEMPLO DE KERNEL 3x3 (σ=1.0):")
        kernel_example = cv2.getGaussianKernel(3, 1.0)
        kernel_2d = kernel_example @ kernel_example.T
        print("   Valores normalizados:")
        for row in kernel_2d:
            print(f"   [{', '.join([f'{v:.3f}' for v in row])}]")

        print("\n   Note: Centro tem maior peso (0.204)")
        print("         Cantos têm menor peso (0.075)")

        # Testa diferentes sigmas
        sigmas = [0.5, 1.0, 2.0, 4.0]
        results = []

        for sigma in sigmas:
            filtered = cv2.GaussianBlur(self.original, (9, 9), sigma)
            results.append((f"Gaussian σ={sigma}", filtered))

        self._visualize_progression(results, "Filtro Gaussiano - Efeito do Sigma")

        print("\n📊 OBSERVAÇÕES:")
        print("   • σ pequeno (0.5): Suavização local, preserva detalhes")
        print("   • σ médio (1.0-2.0): Suavização moderada")
        print("   • σ grande (4.0+): Forte blur, perde detalhes")

    def demo_bilateral_filter(self):
        """
        DEMONSTRAÇÃO: Filtro Bilateral
        ===============================

        O filtro bilateral é revolucionário porque combina distância espacial
        com similaridade de intensidade para preservar bordas.
        """
        print("\n" + "=" * 80)
        print("DEMONSTRAÇÃO: FILTRO BILATERAL")
        print("=" * 80)

        print("\n📖 CONCEITO:")
        print("   Usa DOIS pesos para cada pixel:")
        print("   1. Peso Espacial (distância física)")
        print("   2. Peso de Intensidade (diferença de cor)")

        print("\n💡 A MÁGICA:")
        print("   Em regiões homogêneas: Ambos os pesos são altos → suaviza")
        print("   Em bordas: Peso de intensidade é baixo → NÃO suaviza")
        print("   Resultado: SUAVIZA sem BORRAR bordas!")

        print("\n🔍 EXEMPLO:")
        print("   Pixel A = 100, Pixel B = 102, Pixel C = 200")
        print("   ")
        print("   Gaussiano normal:")
        print("   → usa A, B, C igualmente")
        print("   → borra a borda entre B e C")
        print("   ")
        print("   Bilateral:")
        print("   → detecta que C é muito diferente")
        print("   → reduz peso de C")
        print("   → borda preservada!")

        # Testa diferentes parâmetros
        configs = [
            (5, 50, 50, "Leve"),
            (9, 75, 75, "Moderado"),
            (9, 150, 150, "Forte")
        ]

        results = []
        for d, sc, ss, label in configs:
            filtered = cv2.bilateralFilter(self.original, d, sc, ss)
            results.append((f"Bilateral {label}", filtered))

        self._visualize_progression(results, "Filtro Bilateral - Diferentes Intensidades")

        print("\n📊 PARÂMETROS:")
        print("   • d: diâmetro da vizinhança")
        print("   • sigmaColor: sensibilidade a diferenças de cor")
        print("   • sigmaSpace: alcance espacial")

    def demo_morphological_filters(self):
        """
        DEMONSTRAÇÃO: Filtros Morfológicos
        ===================================

        Operações baseadas em teoria dos conjuntos que transformam a forma
        (morfologia) dos objetos na imagem.
        """
        print("\n" + "=" * 80)
        print("DEMONSTRAÇÃO: FILTROS MORFOLÓGICOS")
        print("=" * 80)

        print("\n📖 OPERAÇÕES BÁSICAS:")
        print("   1. EROSÃO: Encolhe objetos brancos")
        print("   2. DILATAÇÃO: Expande objetos brancos")

        print("\n📖 OPERAÇÕES COMPOSTAS:")
        print("   3. ABERTURA = Erosão + Dilatação")
        print("      → Remove ruído SAL (pontos brancos)")
        print("   ")
        print("   4. FECHAMENTO = Dilatação + Erosão")
        print("      → Remove ruído PIMENTA (pontos pretos)")

        print("\n💡 VISUALIZAÇÃO ASCII:")
        print("\n   ABERTURA (Remove ruído sal):")
        print("   Original:        Erosão:         Dilatação:")
        print("   X X X X X        . . . . .       X X X X X")
        print("   X ■ ■ ■ X   →    . ■ ■ ■ .   →   X ■ ■ ■ X")
        print("   X ■ ■ ■ X        . ■ ■ ■ .       X ■ ■ ■ X")
        print("   X X X X X        . . . . .       X X X X X")
        print("   (X=ruído)        (removido)      (objeto ok)")

        print("\n   FECHAMENTO (Remove ruído pimenta):")
        print("   Original:        Dilatação:      Erosão:")
        print("   ■ ■ ■ ■ ■        ■ ■ ■ ■ ■       ■ ■ ■ ■ ■")
        print("   ■ ■ X ■ ■   →    ■ ■ ■ ■ ■   →   ■ ■ ■ ■ ■")
        print("   ■ ■ ■ ■ ■        ■ ■ ■ ■ ■       ■ ■ ■ ■ ■")
        print("   (X=buraco)       (preenchido)    (objeto ok)")

        # Aplica operações morfológicas
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

        opening = cv2.morphologyEx(self.original, cv2.MORPH_OPEN, kernel)
        closing = cv2.morphologyEx(self.original, cv2.MORPH_CLOSE, kernel)
        gradient = cv2.morphologyEx(self.original, cv2.MORPH_GRADIENT, kernel)

        results = [
            ("Original", self.original),
            ("Opening", opening),
            ("Closing", closing),
            ("Gradient", gradient)
        ]

        self._visualize_comparison(results, "Operações Morfológicas")

        print("\n📊 USOS:")
        print("   • Opening: Remove ruído sal, separar objetos")
        print("   • Closing: Remove ruído pimenta, conectar objetos")
        print("   • Gradient: Detecta bordas")

    def demo_nlm_filter(self):
        """
        DEMONSTRAÇÃO: Non-Local Means
        ==============================

        Técnica avançada que usa padrões similares de TODA a imagem,
        não apenas vizinhos locais.
        """
        print("\n" + "=" * 80)
        print("DEMONSTRAÇÃO: NON-LOCAL MEANS (NLM)")
        print("=" * 80)

        print("\n📖 IDEIA REVOLUCIONÁRIA:")
        print("   Filtros tradicionais: 'Olho apenas meus vizinhos próximos'")
        print("   NLM: 'Busco padrões similares em TODA a imagem'")

        print("\n💡 COMO FUNCIONA:")
        print("   1. Para cada pixel, define um 'patch' (janela pequena)")
        print("   2. Busca patches SIMILARES em toda imagem")
        print("   3. Usa média ponderada destes patches similares")

        print("\n🔍 EXEMPLO:")
        print("   Imagem de grama (textura repetitiva):")
        print("   ")
        print("   Patch em (10,10):    Patch similar em (200,150):")
        print("   [50 52 51]           [51 52 50]")
        print("   [52 48 50]           [53 49 51]")
        print("   [51 50 49]           [50 51 48]")
        print("   ")
        print("   Alta similaridade → alto peso → usa para filtrar")
        print("   Preserva textura da grama!")

        print("\n⏱️  PROCESSANDO... (pode demorar)")

        # Aplica NLM com diferentes h
        h_values = [5, 10, 20]
        results = []

        for h in h_values:
            print(f"   Aplicando NLM com h={h}...")
            filtered = cv2.fastNlMeansDenoising(self.original, None, h, 7, 21)
            results.append((f"NLM h={h}", filtered))

        self._visualize_progression(results, "Non-Local Means - Efeito do Parâmetro h")

        print("\n📊 PARÂMETRO h:")
        print("   • h pequeno (5): Preserva mais detalhes, menos ruído removido")
        print("   • h médio (10): Bom balanço")
        print("   • h grande (20): Remove muito ruído, pode borrar")

    def _visualize_progression(self, results, title):
        """Visualiza progressão de filtros"""
        n = len(results)
        fig, axes = plt.subplots(1, n + 1, figsize=(4 * (n + 1), 4))

        # Original
        axes[0].imshow(self.original, cmap='gray', vmin=0, vmax=255)
        axes[0].set_title('Original', fontweight='bold')
        axes[0].axis('off')

        # Filtros
        for idx, (name, img) in enumerate(results):
            axes[idx + 1].imshow(img, cmap='gray', vmin=0, vmax=255)
            axes[idx + 1].set_title(name, fontweight='bold')
            axes[idx + 1].axis('off')

        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

    def _visualize_comparison(self, results, title):
        """Visualiza comparação lado a lado"""
        n = len(results)
        fig, axes = plt.subplots(1, n, figsize=(4 * n, 4))

        for idx, (name, img) in enumerate(results):
            axes[idx].imshow(img, cmap='gray', vmin=0, vmax=255)
            axes[idx].set_title(name, fontweight='bold')
            axes[idx].axis('off')

        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

    def run_all_demos(self):
        """Executa todas as demonstrações"""
        print("\n" + "=" * 80)
        print("TUTORIAL INTERATIVO: REDUÇÃO DE RUÍDO EM IMAGENS")
        print("=" * 80)
        print("\nEste tutorial demonstra diferentes técnicas de PDI para redução de ruído")
        print("com explicações detalhadas e exemplos práticos.")
        print("\nPressione Enter após cada demonstração para continuar...")

        demos = [
            ("Filtro de Mediana", self.demo_median_filter),
            ("Filtro Gaussiano", self.demo_gaussian_filter),
            ("Filtro Bilateral", self.demo_bilateral_filter),
            ("Filtros Morfológicos", self.demo_morphological_filters),
            ("Non-Local Means", self.demo_nlm_filter)
        ]

        for idx, (name, demo_func) in enumerate(demos, 1):
            print(f"\n{'─' * 80}")
            print(f"DEMONSTRAÇÃO {idx}/{len(demos)}: {name}")
            print(f"{'─' * 80}")

            demo_func()

            if idx < len(demos):
                input("\nPressione Enter para próxima demonstração...")

        print("\n" + "=" * 80)
        print("TUTORIAL CONCLUÍDO!")
        print("=" * 80)
        print("\nPara mais informações, consulte: NOISE_REDUCTION_GUIDE.md")


def main():
    """Função principal"""
    image_path = "/Users/jwcunha/Documents/repos/phd-datascience/visao-computacional/images/fotografo_gonzales.png"

    print("=" * 80)
    print("TUTORIAL INTERATIVO: REDUÇÃO DE RUÍDO")
    print("=" * 80)

    try:
        demo = InteractiveFilterDemo(image_path)

        print("\nEscolha uma opção:")
        print("1 - Tutorial completo (todas as demonstrações)")
        print("2 - Demonstração individual")
        print("0 - Sair")

        choice = input("\nOpção: ").strip()

        if choice == '1':
            demo.run_all_demos()
        elif choice == '2':
            print("\nDemonstrações disponíveis:")
            print("1 - Filtro de Mediana")
            print("2 - Filtro Gaussiano")
            print("3 - Filtro Bilateral")
            print("4 - Filtros Morfológicos")
            print("5 - Non-Local Means")

            sub_choice = input("\nEscolha: ").strip()

            demos = {
                '1': demo.demo_median_filter,
                '2': demo.demo_gaussian_filter,
                '3': demo.demo_bilateral_filter,
                '4': demo.demo_morphological_filters,
                '5': demo.demo_nlm_filter
            }

            if sub_choice in demos:
                demos[sub_choice]()
            else:
                print("Opção inválida!")
        else:
            print("Saindo...")

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())