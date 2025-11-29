"""
Exemplo de Uso do Classificador Roboflow

Este script demonstra como usar o classificador Roboflow para
processar o dataset de emoções.

IMPORTANTE: Você precisa de uma API key do Roboflow
---------------------------------------------------
1. Crie uma conta em https://roboflow.com
2. Acesse https://app.roboflow.com/settings/api
3. Copie sua Private API Key
4. Configure como variável de ambiente ou passe como argumento

Instalação de Dependências:
---------------------------
pip install roboflow opencv-python pillow pandas

Exemplos de Uso:
----------------

1. Processar todas as simulações:
   python RoboflowEmotionClassifier.py --api_key YOUR_API_KEY

2. Processar apenas simulação 01:
   python RoboflowEmotionClassifier.py --api_key YOUR_API_KEY --simulation 1

3. Processar com modelo específico:
   python RoboflowEmotionClassifier.py \\
       --api_key YOUR_API_KEY \\
       --model_id emotions-dectection/human-face-emotions/1 \\
       --model_name roboflow_v1

4. Processar primeiras 5 simulações (teste):
   python RoboflowEmotionClassifier.py \\
       --api_key YOUR_API_KEY \\
       --num_simulations 5

Uso via Python (importando a classe):
-------------------------------------
"""

from RoboflowEmotionClassifier import RoboflowEmotionClassifier
import os

# Método 1: API Key via variável de ambiente
api_key = os.getenv('ROBOFLOW_API_KEY', 'YOUR_API_KEY_HERE')

# Método 2: API Key diretamente (NÃO recomendado para produção)
# api_key = 'sua_api_key_aqui'

# Inicializa classificador
classifier = RoboflowEmotionClassifier(
    api_key=api_key,
    model_id='emotions-dectection/human-face-emotions/1',
    dataset_dir='../../datasets',  # Ajuste conforme necessário
    results_dir='../../3_simulation/results',
    model_name='roboflow_emotion'
)

# Exemplo 1: Processar uma simulação
print("Exemplo 1: Processando simulação 01...")
results = classifier.process_simulation(1)
print(f"Acurácia geral: {results['acuracia_geral']:.4f}")

# Exemplo 2: Processar todas as simulações (DEMO - apenas 3 simulações)
print("\nExemplo 2: Processando primeiras 3 simulações...")
results_df = classifier.process_all_simulations(num_simulations=3)
print(results_df)

# Exemplo 3: Análise dos resultados
print("\nExemplo 3: Estatísticas dos resultados...")
print(f"Acurácia média alegria: {results_df['acuracia_alegria'].mean():.4f}")
print(f"Acurácia média raiva: {results_df['acuracia_raiva'].mean():.4f}")
print(f"Acurácia média geral: {results_df['acuracia_geral'].mean():.4f}")
