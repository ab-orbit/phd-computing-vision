"""
Noise Reduction using Digital Image Processing Techniques
==========================================================

Implementação de várias técnicas de PDI para redução de ruído:
- Filtro de Mediana
- Filtro Gaussiano
- Filtro Bilateral
- Filtro de Média
- Filtros Morfológicos
- Filtro de Wiener
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import median_filter, gaussian_filter
from scipy.signal import wiener
from pathlib import Path


class NoiseReducer:
    """Classe para aplicar diferentes técnicas de redução de ruído"""

    def __init__(self, image_path):
        """
        Inicializa o redutor de ruído

        Args:
            image_path: Caminho para a imagem
        """
        self.image_path = Path(image_path)
        self.original = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

        if self.original is None:
            raise ValueError(f"Não foi possível carregar a imagem: {image_path}")

        self.results = {'original': self.original.copy()}

    def median_filter(self, kernel_size=5):
        """
        Filtro de Mediana - Excelente para ruído sal e pimenta

        Args:
            kernel_size: Tamanho do kernel (deve ser ímpar)

        Returns:
            Imagem filtrada
        """
        # OpenCV median blur
        filtered = cv2.medianBlur(self.original, kernel_size)
        self.results[f'median_{kernel_size}x{kernel_size}'] = filtered
        return filtered

    def gaussian_filter(self, kernel_size=5, sigma=1.0):
        """
        Filtro Gaussiano - Suavização geral da imagem

        Args:
            kernel_size: Tamanho do kernel (deve ser ímpar)
            sigma: Desvio padrão da gaussiana

        Returns:
            Imagem filtrada
        """
        filtered = cv2.GaussianBlur(self.original, (kernel_size, kernel_size), sigma)
        self.results[f'gaussian_{kernel_size}x{kernel_size}_sigma{sigma}'] = filtered
        return filtered

    def bilateral_filter(self, d=9, sigma_color=75, sigma_space=75):
        """
        Filtro Bilateral - Preserva bordas enquanto suaviza

        Args:
            d: Diâmetro do pixel neighborhood
            sigma_color: Filtro sigma no espaço de cor
            sigma_space: Filtro sigma no espaço de coordenadas

        Returns:
            Imagem filtrada
        """
        filtered = cv2.bilateralFilter(self.original, d, sigma_color, sigma_space)
        self.results[f'bilateral_d{d}'] = filtered
        return filtered

    def mean_filter(self, kernel_size=5):
        """
        Filtro de Média - Suavização simples

        Args:
            kernel_size: Tamanho do kernel

        Returns:
            Imagem filtrada
        """
        kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size ** 2)
        filtered = cv2.filter2D(self.original, -1, kernel)
        self.results[f'mean_{kernel_size}x{kernel_size}'] = filtered
        return filtered

    def morphological_opening(self, kernel_size=3):
        """
        Abertura Morfológica - Remove ruído sal (pixels brancos)

        Args:
            kernel_size: Tamanho do elemento estruturante

        Returns:
            Imagem filtrada
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        filtered = cv2.morphologyEx(self.original, cv2.MORPH_OPEN, kernel)
        self.results[f'morpho_open_{kernel_size}x{kernel_size}'] = filtered
        return filtered

    def morphological_closing(self, kernel_size=3):
        """
        Fechamento Morfológico - Remove ruído pimenta (pixels pretos)

        Args:
            kernel_size: Tamanho do elemento estruturante

        Returns:
            Imagem filtrada
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        filtered = cv2.morphologyEx(self.original, cv2.MORPH_CLOSE, kernel)
        self.results[f'morpho_close_{kernel_size}x{kernel_size}'] = filtered
        return filtered

    def morphological_gradient(self, kernel_size=3):
        """
        Gradiente Morfológico - Detecta bordas

        Args:
            kernel_size: Tamanho do elemento estruturante

        Returns:
            Imagem com gradiente
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        filtered = cv2.morphologyEx(self.original, cv2.MORPH_GRADIENT, kernel)
        self.results[f'morpho_gradient_{kernel_size}x{kernel_size}'] = filtered
        return filtered

    def non_local_means(self, h=10, template_window_size=7, search_window_size=21):
        """
        Non-Local Means Denoising - Técnica avançada

        Args:
            h: Força da filtragem
            template_window_size: Tamanho da janela template
            search_window_size: Tamanho da janela de busca

        Returns:
            Imagem filtrada
        """
        filtered = cv2.fastNlMeansDenoising(self.original, None, h,
                                           template_window_size, search_window_size)
        self.results[f'nlm_h{h}'] = filtered
        return filtered

    def adaptive_median_filter(self, max_kernel_size=7):
        """
        Filtro de Mediana Adaptativo - Ajusta tamanho do kernel baseado no ruído local

        Args:
            max_kernel_size: Tamanho máximo do kernel

        Returns:
            Imagem filtrada
        """
        # Implementação simplificada do filtro adaptativo
        result = self.original.copy()
        padded = cv2.copyMakeBorder(self.original, max_kernel_size, max_kernel_size,
                                    max_kernel_size, max_kernel_size, cv2.BORDER_REFLECT)

        for i in range(self.original.shape[0]):
            for j in range(self.original.shape[1]):
                # Tenta kernels de tamanho crescente
                for k_size in range(3, max_kernel_size + 1, 2):
                    half_k = k_size // 2
                    window = padded[i:i+k_size, j:j+k_size]

                    z_min = np.min(window)
                    z_max = np.max(window)
                    z_med = np.median(window)
                    z_xy = padded[i + half_k, j + half_k]

                    # Estágio A
                    if z_min < z_med < z_max:
                        # Estágio B
                        if z_min < z_xy < z_max:
                            result[i, j] = z_xy
                        else:
                            result[i, j] = z_med
                        break

                    # Se chegou ao tamanho máximo, usa mediana
                    if k_size == max_kernel_size:
                        result[i, j] = z_med

        self.results[f'adaptive_median_max{max_kernel_size}'] = result
        return result

    def combined_filter(self):
        """
        Filtro Combinado - Usa múltiplas técnicas em sequência

        Returns:
            Imagem filtrada
        """
        # 1. Mediana para remover sal e pimenta
        step1 = cv2.medianBlur(self.original, 3)

        # 2. Bilateral para suavizar mantendo bordas
        step2 = cv2.bilateralFilter(step1, 5, 50, 50)

        # 3. Leve gaussiana para suavização final
        step3 = cv2.GaussianBlur(step2, (3, 3), 0.5)

        self.results['combined'] = step3
        return step3

    def calculate_metrics(self, filtered_image):
        """
        Calcula métricas de qualidade da imagem filtrada

        Args:
            filtered_image: Imagem filtrada

        Returns:
            Dict com métricas
        """
        # MSE (Mean Squared Error)
        mse = np.mean((self.original.astype(float) - filtered_image.astype(float)) ** 2)

        # PSNR (Peak Signal-to-Noise Ratio)
        if mse == 0:
            psnr = float('inf')
        else:
            psnr = 20 * np.log10(255.0 / np.sqrt(mse))

        # Desvio padrão (menor indica mais suavização)
        std_original = np.std(self.original)
        std_filtered = np.std(filtered_image)

        # Diferença absoluta média
        mae = np.mean(np.abs(self.original.astype(float) - filtered_image.astype(float)))

        return {
            'MSE': mse,
            'PSNR': psnr,
            'STD_original': std_original,
            'STD_filtered': std_filtered,
            'MAE': mae
        }

    def apply_all_filters(self):
        """Aplica todos os filtros e retorna resultados"""
        print("Aplicando filtros...")

        # Filtros básicos
        self.median_filter(kernel_size=3)
        self.median_filter(kernel_size=5)
        self.gaussian_filter(kernel_size=5, sigma=1.0)
        self.bilateral_filter(d=9, sigma_color=75, sigma_space=75)
        self.mean_filter(kernel_size=5)

        # Filtros morfológicos
        self.morphological_opening(kernel_size=3)
        self.morphological_closing(kernel_size=3)

        # Filtros avançados
        self.non_local_means(h=10)
        self.adaptive_median_filter(max_kernel_size=7)

        # Filtro combinado
        self.combined_filter()

        print(f"Total de filtros aplicados: {len(self.results) - 1}")

        return self.results

    def visualize_results(self, save_path=None):
        """
        Visualiza os resultados de todos os filtros

        Args:
            save_path: Caminho para salvar a imagem (opcional)
        """
        n_images = len(self.results)
        cols = 4
        rows = (n_images + cols - 1) // cols

        fig, axes = plt.subplots(rows, cols, figsize=(20, 5 * rows))
        axes = axes.flatten()

        for idx, (name, img) in enumerate(self.results.items()):
            axes[idx].imshow(img, cmap='gray', vmin=0, vmax=255)
            axes[idx].set_title(name.replace('_', ' ').title(), fontsize=10)
            axes[idx].axis('off')

        # Remove eixos extras
        for idx in range(n_images, len(axes)):
            axes[idx].axis('off')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Resultados salvos em: {save_path}")

        plt.show()

    def compare_best_filters(self, filter_names=None, save_path=None):
        """
        Compara os melhores filtros lado a lado

        Args:
            filter_names: Lista de nomes de filtros para comparar
            save_path: Caminho para salvar a comparação
        """
        if filter_names is None:
            # Seleciona os mais importantes
            filter_names = [
                'original',
                'median_5x5',
                'bilateral_d9',
                'nlm_h10',
                'adaptive_median_max7',
                'combined'
            ]

        # Filtra apenas os que existem
        filter_names = [name for name in filter_names if name in self.results]

        n_filters = len(filter_names)
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()

        for idx, name in enumerate(filter_names):
            img = self.results[name]
            axes[idx].imshow(img, cmap='gray', vmin=0, vmax=255)
            axes[idx].set_title(name.replace('_', ' ').title(), fontsize=14, fontweight='bold')
            axes[idx].axis('off')

            # Adiciona métricas se não for original
            if name != 'original':
                metrics = self.calculate_metrics(img)
                metrics_text = f"PSNR: {metrics['PSNR']:.2f} dB\nSTD: {metrics['STD_filtered']:.2f}"
                axes[idx].text(0.02, 0.98, metrics_text,
                             transform=axes[idx].transAxes,
                             fontsize=10, verticalalignment='top',
                             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        # Remove eixos extras
        for idx in range(n_filters, len(axes)):
            axes[idx].axis('off')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Comparação salva em: {save_path}")

        plt.show()

    def print_metrics_report(self):
        """Imprime relatório com métricas de todos os filtros"""
        print("\n" + "=" * 80)
        print("RELATÓRIO DE MÉTRICAS DE QUALIDADE")
        print("=" * 80)

        metrics_data = []
        for name, img in self.results.items():
            if name == 'original':
                continue
            metrics = self.calculate_metrics(img)
            metrics_data.append((name, metrics))

        # Ordena por PSNR (maior é melhor)
        metrics_data.sort(key=lambda x: x[1]['PSNR'], reverse=True)

        print(f"\n{'Filtro':<30} {'PSNR (dB)':<12} {'MSE':<12} {'MAE':<12} {'STD':<10}")
        print("-" * 80)

        for name, metrics in metrics_data:
            print(f"{name:<30} {metrics['PSNR']:>10.2f}  {metrics['MSE']:>10.2f}  "
                  f"{metrics['MAE']:>10.2f}  {metrics['STD_filtered']:>8.2f}")

        print("=" * 80)
        print("\nMelhor filtro (maior PSNR):", metrics_data[0][0])
        print("=" * 80)


def main():
    """Função principal de demonstração"""
    import sys

    # Caminho da imagem
    image_path = "/Users/jwcunha/Documents/repos/phd-datascience/visao-computacional/images/fotografo_gonzales.png"
    output_dir = Path("/Users/jwcunha/Documents/repos/phd-datascience/visao-computacional/pdi/output")
    output_dir.mkdir(exist_ok=True)

    print("=" * 80)
    print("REDUÇÃO DE RUÍDO USANDO PDI")
    print("=" * 80)
    print(f"Imagem: {image_path}")
    print(f"Output: {output_dir}")
    print("=" * 80)

    # Inicializa o redutor de ruído
    reducer = NoiseReducer(image_path)

    # Aplica todos os filtros
    results = reducer.apply_all_filters()

    # Imprime métricas
    reducer.print_metrics_report()

    # Visualiza comparação dos melhores
    print("\nGerando visualizações...")
    reducer.compare_best_filters(
        save_path=output_dir / "comparison_best_filters.png"
    )

    # Visualiza todos os resultados
    reducer.visualize_results(
        save_path=output_dir / "all_filters.png"
    )

    # Salva as melhores versões individualmente
    print("\nSalvando versões filtradas...")
    for name in ['median_5x5', 'bilateral_d9', 'nlm_h10', 'combined']:
        if name in results:
            output_path = output_dir / f"{name}.png"
            cv2.imwrite(str(output_path), results[name])
            print(f"  Salvo: {output_path.name}")

    print("\n" + "=" * 80)
    print("PROCESSAMENTO CONCLUÍDO!")
    print("=" * 80)


if __name__ == "__main__":
    main()