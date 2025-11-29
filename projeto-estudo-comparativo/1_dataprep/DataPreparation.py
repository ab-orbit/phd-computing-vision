"""
Módulo de Preparação de Dataset para Classificação de Emoções

Este módulo implementa a preparação do dataset de emoções faciais (raiva vs alegria)
organizando-o em múltiplas simulações para análise estatística robusta.

Estrutura do Dataset Final:
---------------------------
datasets/
  sim01/
    raiva/       # 50 imagens de raiva
    alegria/     # 50 imagens de alegria
  sim02/
    raiva/
    alegria/
  ...
  sim30/
    raiva/
    alegria/

Objetivo Pedagógico:
-------------------
A criação de 30 simulações independentes permite:
1. Avaliar a variabilidade do modelo com diferentes subconjuntos de dados
2. Calcular métricas estatísticas (média, desvio padrão, intervalos de confiança)
3. Reduzir viés de seleção de amostras específicas
4. Validar a robustez e generalização do modelo

Cada simulação contém uma amostra aleatória diferente de 50 imagens por classe,
garantindo diversidade nas avaliações.
"""

import os
import shutil
import random
from pathlib import Path
from typing import List, Tuple
import logging

# Configuração de logging para acompanhamento do processo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatasetPreparation:
    """
    Classe responsável pela preparação e organização do dataset de emoções.

    Esta classe encapsula toda a lógica necessária para:
    - Localizar imagens no dataset original
    - Criar estrutura de diretórios para simulações
    - Amostrar aleatoriamente imagens para cada simulação
    - Copiar imagens mantendo diversidade entre simulações

    Attributes:
        source_path (Path): Caminho para o dataset original do Kaggle
        output_path (Path): Caminho para o dataset organizado em simulações
        num_simulations (int): Número de simulações a criar (padrão: 30)
        images_per_class (int): Número de imagens por classe em cada simulação (padrão: 50)
        seed (int): Semente para reprodutibilidade dos experimentos
    """

    def __init__(
        self,
        source_path: str,
        output_path: str = "datasets",
        num_simulations: int = 30,
        images_per_class: int = 50,
        seed: int = 42
    ):
        """
        Inicializa o preparador de dataset.

        Args:
            source_path: Caminho completo para a pasta Data do dataset original
            output_path: Caminho onde serão criadas as simulações
            num_simulations: Quantidade de simulações independentes a criar
            images_per_class: Quantidade de imagens por classe em cada simulação
            seed: Semente aleatória para garantir reprodutibilidade

        Nota sobre Reprodutibilidade:
            A semente aleatória garante que os mesmos conjuntos de imagens sejam
            selecionados em execuções diferentes, permitindo comparações justas
            entre diferentes modelos e configurações.
        """
        self.source_path = Path(source_path)
        self.output_path = Path(output_path)
        self.num_simulations = num_simulations
        self.images_per_class = images_per_class
        self.seed = seed

        # Mapeamento das classes originais para as classes do projeto
        # Angry (raiva) e Happy (alegria) são as emoções mais distintas
        # facilitando a classificação binária
        self.class_mapping = {
            'raiva': 'Angry',
            'alegria': 'Happy'
        }

        # Define semente para reprodutibilidade
        random.seed(self.seed)

        logger.info(f"DatasetPreparation inicializado:")
        logger.info(f"  - Origem: {self.source_path}")
        logger.info(f"  - Destino: {self.output_path}")
        logger.info(f"  - Simulações: {self.num_simulations}")
        logger.info(f"  - Imagens por classe: {self.images_per_class}")
        logger.info(f"  - Semente: {self.seed}")

    def get_all_images(self, class_name: str) -> List[Path]:
        """
        Obtém lista de todos os arquivos de imagem de uma classe.

        Args:
            class_name: Nome da classe no dataset original (Angry ou Happy)

        Returns:
            Lista de Path objects para cada imagem encontrada

        Raises:
            FileNotFoundError: Se a pasta da classe não existir

        Nota sobre Formatos de Imagem:
            O dataset contém imagens em diversos formatos (png, jpg, jpeg).
            Esta função coleta todos os formatos válidos para maximizar
            a diversidade do dataset final.
        """
        class_path = self.source_path / class_name

        if not class_path.exists():
            raise FileNotFoundError(f"Pasta não encontrada: {class_path}")

        # Extensões de imagem suportadas
        valid_extensions = {'.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'}

        # Coleta todas as imagens válidas
        images = [
            img for img in class_path.iterdir()
            if img.is_file() and img.suffix in valid_extensions
        ]

        logger.info(f"Encontradas {len(images)} imagens em {class_name}")

        return images

    def create_simulation_structure(self) -> None:
        """
        Cria a estrutura de diretórios para todas as simulações.

        Estrutura criada:
            datasets/
              sim01/raiva/
              sim01/alegria/
              sim02/raiva/
              sim02/alegria/
              ...
              sim30/raiva/
              sim30/alegria/

        Comportamento:
            - Se o diretório de saída já existir, remove e recria
            - Garante estrutura limpa em cada execução
            - Cria todos os diretórios necessários de uma vez

        Nota sobre Recriação:
            A remoção do diretório existente garante que não haja
            imagens residuais de execuções anteriores, evitando
            contaminação dos dados.
        """
        # Remove diretório existente se houver
        if self.output_path.exists():
            logger.warning(f"Removendo estrutura existente em {self.output_path}")
            shutil.rmtree(self.output_path)

        # Cria estrutura de diretórios
        logger.info("Criando estrutura de diretórios...")

        for sim_num in range(1, self.num_simulations + 1):
            sim_folder = self.output_path / f"sim{sim_num:02d}"

            for class_name in self.class_mapping.keys():
                class_folder = sim_folder / class_name
                class_folder.mkdir(parents=True, exist_ok=True)

        logger.info(f"Estrutura criada: {self.num_simulations} simulações")

    def sample_images_for_simulation(
        self,
        all_images: List[Path],
        num_samples: int
    ) -> List[Path]:
        """
        Amostra aleatoriamente imagens para uma simulação.

        Args:
            all_images: Lista completa de imagens disponíveis
            num_samples: Quantidade de imagens a amostrar

        Returns:
            Lista de Path objects das imagens selecionadas

        Raises:
            ValueError: Se não houver imagens suficientes

        Estratégia de Amostragem:
            - Usa amostragem sem reposição (cada imagem aparece no máximo uma vez)
            - Garante diversidade entre simulações
            - Valida disponibilidade de imagens suficientes

        Nota Pedagógica:
            A amostragem sem reposição é crucial para criar simulações
            verdadeiramente independentes, permitindo análise estatística
            robusta dos resultados.
        """
        if len(all_images) < num_samples:
            raise ValueError(
                f"Imagens insuficientes: disponíveis={len(all_images)}, "
                f"necessárias={num_samples}"
            )

        # Amostragem sem reposição
        sampled = random.sample(all_images, num_samples)

        return sampled

    def copy_images_to_simulation(
        self,
        images: List[Path],
        destination: Path,
        class_name: str,
        sim_num: int
    ) -> None:
        """
        Copia imagens para o diretório de destino de uma simulação.

        Args:
            images: Lista de imagens a copiar
            destination: Pasta de destino
            class_name: Nome da classe (para logging)
            sim_num: Número da simulação (para logging)

        Comportamento:
            - Mantém o nome original do arquivo
            - Preserva extensão e formato
            - Reporta progresso a cada 10 imagens

        Nota sobre Nomenclatura:
            Os nomes originais são mantidos para facilitar rastreabilidade
            e debugging, permitindo identificar a origem de cada imagem.
        """
        logger.info(f"Copiando {len(images)} imagens para sim{sim_num:02d}/{class_name}")

        for idx, img_path in enumerate(images, 1):
            # Mantém o nome original do arquivo
            dest_file = destination / img_path.name
            shutil.copy2(img_path, dest_file)

            # Reporta progresso
            if idx % 10 == 0:
                logger.info(f"  Progresso: {idx}/{len(images)} imagens copiadas")

    def prepare_dataset(self) -> Tuple[int, int]:
        """
        Executa o processo completo de preparação do dataset.

        Este é o método principal que orquestra todo o pipeline:
        1. Valida existência do dataset original
        2. Coleta todas as imagens disponíveis por classe
        3. Cria estrutura de diretórios
        4. Para cada simulação:
           a. Amostra aleatoriamente imagens de cada classe
           b. Copia imagens para a estrutura de simulação

        Returns:
            Tupla (total_simulations, total_images) com estatísticas

        Raises:
            FileNotFoundError: Se dataset original não existir
            ValueError: Se não houver imagens suficientes

        Fluxo de Execução:
            1. Validação inicial
            2. Coleta de imagens
            3. Criação de estrutura
            4. Loop de simulações (com amostragem e cópia)
            5. Validação final

        Nota sobre Robustez:
            O método valida cada etapa e reporta erros claros,
            facilitando diagnóstico de problemas no dataset original.
        """
        logger.info("=" * 70)
        logger.info("INICIANDO PREPARAÇÃO DO DATASET")
        logger.info("=" * 70)

        # Validação inicial
        if not self.source_path.exists():
            raise FileNotFoundError(
                f"Dataset original não encontrado: {self.source_path}"
            )

        # Coleta todas as imagens por classe
        logger.info("\n[1/4] Coletando imagens do dataset original...")
        images_by_class = {}

        for class_name, original_name in self.class_mapping.items():
            images_by_class[class_name] = self.get_all_images(original_name)

            # Validação de quantidade suficiente
            total_needed = self.num_simulations * self.images_per_class
            available = len(images_by_class[class_name])

            if available < total_needed:
                logger.warning(
                    f"Atenção: {class_name} tem {available} imagens, "
                    f"mas idealmente precisaria de {total_needed} para "
                    f"simulações sem sobreposição"
                )

        # Cria estrutura de diretórios
        logger.info("\n[2/4] Criando estrutura de diretórios...")
        self.create_simulation_structure()

        # Prepara cada simulação
        logger.info("\n[3/4] Criando simulações...")
        total_images_copied = 0

        for sim_num in range(1, self.num_simulations + 1):
            logger.info(f"\n--- Simulação {sim_num:02d}/{self.num_simulations} ---")
            sim_folder = self.output_path / f"sim{sim_num:02d}"

            for class_name in self.class_mapping.keys():
                # Amostra imagens para esta simulação
                sampled_images = self.sample_images_for_simulation(
                    images_by_class[class_name],
                    self.images_per_class
                )

                # Copia imagens
                destination = sim_folder / class_name
                self.copy_images_to_simulation(
                    sampled_images,
                    destination,
                    class_name,
                    sim_num
                )

                total_images_copied += len(sampled_images)

        # Validação final
        logger.info("\n[4/4] Validando estrutura criada...")
        self._validate_structure()

        logger.info("\n" + "=" * 70)
        logger.info("PREPARAÇÃO CONCLUÍDA COM SUCESSO!")
        logger.info(f"Total de simulações: {self.num_simulations}")
        logger.info(f"Total de imagens copiadas: {total_images_copied}")
        logger.info(f"Dataset salvo em: {self.output_path.absolute()}")
        logger.info("=" * 70)

        return self.num_simulations, total_images_copied

    def _validate_structure(self) -> None:
        """
        Valida se a estrutura foi criada corretamente.

        Verificações realizadas:
        - Todas as pastas de simulação existem
        - Cada simulação tem pastas de ambas as classes
        - Cada pasta tem exatamente o número esperado de imagens

        Raises:
            AssertionError: Se alguma validação falhar

        Nota sobre Qualidade:
            Esta validação é crucial para garantir que o dataset está
            corretamente preparado antes de iniciar o treinamento,
            evitando erros silenciosos que poderiam comprometer os resultados.
        """
        logger.info("Validando estrutura criada...")

        for sim_num in range(1, self.num_simulations + 1):
            sim_folder = self.output_path / f"sim{sim_num:02d}"
            assert sim_folder.exists(), f"Pasta sim{sim_num:02d} não existe"

            for class_name in self.class_mapping.keys():
                class_folder = sim_folder / class_name
                assert class_folder.exists(), \
                    f"Pasta {class_name} não existe em sim{sim_num:02d}"

                # Conta imagens
                images = list(class_folder.glob('*'))
                images = [img for img in images if img.is_file()]

                assert len(images) == self.images_per_class, \
                    f"sim{sim_num:02d}/{class_name} tem {len(images)} imagens, " \
                    f"esperado {self.images_per_class}"

        logger.info("Validação concluída: estrutura OK!")

    def get_dataset_statistics(self) -> dict:
        """
        Calcula estatísticas sobre o dataset preparado.

        Returns:
            Dicionário com estatísticas:
            - num_simulations: Quantidade de simulações
            - classes: Lista de classes
            - images_per_class: Imagens por classe
            - total_images: Total de imagens no dataset
            - disk_usage_mb: Espaço em disco utilizado (MB)

        Nota Pedagógica:
            Estas estatísticas são úteis para documentação do experimento
            e para verificar se o dataset atende aos requisitos do projeto.
        """
        if not self.output_path.exists():
            return {
                'status': 'Dataset não preparado',
                'exists': False
            }

        # Calcula tamanho em disco
        total_size = 0
        for file in self.output_path.rglob('*'):
            if file.is_file():
                total_size += file.stat().st_size

        disk_usage_mb = total_size / (1024 * 1024)

        total_images = self.num_simulations * len(self.class_mapping) * self.images_per_class

        return {
            'status': 'Dataset preparado',
            'exists': True,
            'num_simulations': self.num_simulations,
            'classes': list(self.class_mapping.keys()),
            'images_per_class': self.images_per_class,
            'images_per_simulation': len(self.class_mapping) * self.images_per_class,
            'total_images': total_images,
            'disk_usage_mb': round(disk_usage_mb, 2),
            'path': str(self.output_path.absolute())
        }


def main():
    """
    Função principal para execução do script.

    Esta função demonstra o uso da classe DatasetPreparation e pode ser
    executada diretamente para preparar o dataset.

    Configuração:
        - Dataset original: ~/.cache/kagglehub/...
        - Dataset preparado: datasets/ (no diretório atual)
        - 30 simulações com 50 imagens por classe

    Exemplo de Uso:
        python DataPreparation.py
    """
    # Configuração dos caminhos
    SOURCE_PATH = "/Users/jwcunha/.cache/kagglehub/datasets/samithsachidanandan/human-face-emotions/versions/2/Data"
    OUTPUT_PATH = "datasets"

    # Inicializa o preparador
    preparator = DatasetPreparation(
        source_path=SOURCE_PATH,
        output_path=OUTPUT_PATH,
        num_simulations=30,
        images_per_class=50,
        seed=42  # Garante reprodutibilidade
    )

    try:
        # Executa preparação
        num_sims, num_images = preparator.prepare_dataset()

        # Exibe estatísticas
        print("\n" + "=" * 70)
        print("ESTATÍSTICAS DO DATASET")
        print("=" * 70)

        stats = preparator.get_dataset_statistics()
        for key, value in stats.items():
            print(f"{key}: {value}")

        print("=" * 70)

    except Exception as e:
        logger.error(f"Erro durante a preparação: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
