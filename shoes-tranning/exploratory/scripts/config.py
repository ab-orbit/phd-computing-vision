"""
Configurações e caminhos do dataset para análise exploratória.

Este módulo centraliza todos os caminhos e configurações necessárias
para acessar o Fashion Product Images Dataset.
"""

from pathlib import Path

# Caminhos base do dataset
DATASET_BASE = Path("/Users/jwcunha/.cache/kagglehub/datasets/paramaggarwal/fashion-product-images-dataset/versions/1/fashion-dataset/fashion-dataset")

# Caminhos específicos
IMAGES_DIR = DATASET_BASE / "images"
STYLES_JSON_DIR = DATASET_BASE / "styles"
STYLES_CSV = DATASET_BASE / "styles.csv"
IMAGES_CSV = DATASET_BASE / "images.csv"

# Caminhos de saída para análise
EXPLORATORY_BASE = Path("/Users/jwcunha/Documents/COMPANIES/AB/repos/private/premium/researcher/phd-classes/shoes-tranning/exploratory")
OUTPUTS_DIR = EXPLORATORY_BASE / "outputs"
FIGURES_DIR = EXPLORATORY_BASE / "figures"

# Criar diretórios se não existirem
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Configurações de visualização
FIGURE_SIZE = (12, 6)
FIGURE_DPI = 100
SEABORN_STYLE = "whitegrid"
COLOR_PALETTE = "husl"

# Sample size para análises rápidas (usar None para dataset completo)
SAMPLE_SIZE = None  # ou um número como 1000 para testes rápidos

# Seed para reprodutibilidade
RANDOM_SEED = 42