# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Visão Geral do Projeto

Este é um projeto de pesquisa comparativa para classificação de emoções faciais (raiva vs alegria) usando diferentes abordagens de Machine Learning. O objetivo é comparar CNNs tradicionais, APIs de foundation models e foundation models locais através de análise estatística robusta com 30 simulações independentes.

Dataset: Human Face Emotions (Kaggle)
Classes: Raiva e Alegria
Metodologia: 30 simulações com 50 imagens por classe (total de 100 imagens por simulação)

## Estrutura do Projeto

```
1_dataprep/          - Preparação de datasets em múltiplas simulações
2_classificators/    - Implementações dos diferentes classificadores
3_simulation/        - Resultados e análises das simulações
4_analysis/          - Análises comparativas (vazio atualmente)
datasets/            - Datasets organizados em sim01/ a sim30/
```

## Arquitetura de Classificadores

O projeto implementa 4 abordagens diferentes, todas gerando saída no mesmo formato:

### 1. CNN Tradicional (SimpleCNN)
Localização: `2_classificators/others/SimpleCNN_BinaryClassifier.ipynb`
- Treinamento necessário
- Alta acurácia esperada (85-95%)
- Notebook Jupyter completo
- Função principal: `run_all_simulations()`

### 2. API Roboflow
Localização: `2_classificators/others/RoboflowEmotionClassifier.py`
- API externa (requer ROBOFLOW_API_KEY no .env)
- Baixa acurácia (30-40%) mas setup zero
- Classe principal: `RoboflowEmotionClassifier`

### 3. YOLO11 Local
Localização: `2_classificators/yolo11/YOLO11EmotionClassifier.py`
- Foundation model local usando Ultralytics
- Modelo padrão: yolov8n-cls.pt (nano)
- Classe principal: `YOLO11EmotionClassifier`
- Detecção automática de GPU (CUDA/MPS)

### 4. Google Cloud Vision API
Localização: `2_classificators/gemini2/GoogleVisionEmotionClassifier.py`
- API do Google Cloud (requer GOOGLE_API_KEY no .env)
- Alta qualidade de detecção de emoções
- Classe principal: `GoogleVisionEmotionClassifier`

## Formato Padrão de Saída

Todos os classificadores salvam resultados em:
```
3_simulation/results/{nome_modelo}/
├── results.csv      - Resultados de todas simulações
└── stats.json       - Estatísticas agregadas
```

CSV padrão:
```csv
numero_simulacao,nome_modelo,qtd_sucesso_alegria,qtd_sucesso_raiva,total_alegria,total_raiva,tempo_total_ms,acuracia_alegria,acuracia_raiva,acuracia_geral,precisao_alegria,recall_alegria,f1_alegria,precisao_raiva,recall_raiva,f1_raiva,precisao_macro,recall_macro,f1_macro
```

## Comandos Principais

### Preparação de Dados
```bash
# Criar 30 simulações com 50 imagens por classe
python 1_dataprep/DataPreparation.py
```

### Executar Classificadores

```bash
# YOLO11 (30 simulações)
cd /Users/jwcunha/Documents/repos/phd-datascience/visao-computacional/projeto-estudo-comparativo
python 2_classificators/yolo11/YOLO11EmotionClassifier.py --num_simulations 30

# YOLO11 (teste com 1 simulação)
python 2_classificators/yolo11/YOLO11EmotionClassifier.py --simulation 1

# Google Vision (30 simulações)
python 2_classificators/gemini2/GoogleVisionEmotionClassifier.py --num_simulations 30

# Roboflow (30 simulações)
python 2_classificators/others/run_roboflow_classification.py --num_simulations 30

# CNN tradicional
jupyter notebook 2_classificators/others/SimpleCNN_BinaryClassifier.ipynb
```

### Adicionar Métricas
```bash
# Adiciona precisão, recall, f1-score aos resultados
python 3_simulation/add_metrics.py 3_simulation/results/yolo11_emotion/results.csv
python 3_simulation/add_metrics.py 3_simulation/results/google_vision_emotion/results.csv
python 3_simulation/add_metrics.py 3_simulation/results/roboflow_emotion/results.csv
```

## Estrutura de Datasets

```
datasets/
├── sim01/
│   ├── raiva/      - 50 imagens
│   └── alegria/    - 50 imagens
├── sim02/
│   ├── raiva/
│   └── alegria/
...
└── sim30/
    ├── raiva/
    └── alegria/
```

Cada simulação contém amostra aleatória diferente para garantir robustez estatística.

## Configuração de API Keys

Arquivo `.env` na raiz do projeto:
```bash
ROBOFLOW_API_KEY=sua_chave_aqui
GOOGLE_API_KEY=sua_chave_aqui
```

## Classes de Classificadores - Interface Comum

Todos os classificadores implementam interface similar:

```python
classifier = ClassificadorX(
    dataset_dir='datasets',
    results_dir='3_simulation/results',
    model_name='nome_modelo'
)

# Processar uma simulação
results = classifier.process_simulation(1)

# Processar todas as simulações
df = classifier.process_all_simulations(num_simulations=30)
```

## Hardware e Performance

### YOLO11
- GPU recomendado (CUDA ou Apple MPS)
- CPU funciona mas é mais lento
- Detecção automática via device='auto'

### CNN Tradicional
- GPU necessária para treinamento
- CPU pode ser usado para inferência

### APIs (Roboflow, Google Vision)
- Não requerem GPU
- Dependem de conexão de internet
- Latência de rede (~450-600ms por imagem)

## Análise de Resultados

Após executar classificadores, os resultados podem ser comparados:
- Acurácia por classe e geral
- Precisão, recall, f1-score
- Tempo de processamento
- Desvio padrão (robustez)

Ver `2_classificators/COMPARISON.md` para comparação detalhada entre abordagens.

## Conceitos Pedagógicos

Este projeto demonstra:
1. Trade-off controle vs conveniência (CNN vs API)
2. Trade-off velocidade vs acurácia (YOLO11 vs CNN vs API)
3. Trade-off custo inicial vs recorrente (GPU vs $/requisição)
4. Importância de múltiplas simulações para validação estatística
5. Padronização de interface para comparação justa

## Metodologia Científica

- 30 simulações independentes
- 50 imagens por classe por simulação
- Total: 3000 imagens processadas por modelo
- Métricas: acurácia, precisão, recall, f1-score
- Análise estatística: média, desvio padrão, intervalos de confiança
- Validação: Teste Pareado de Wilcoxon (p=0.05)

## Troubleshooting Comum

### YOLO11
- "No module named 'ultralytics'": `pip install ultralytics`
- "CUDA out of memory": use `--device cpu` ou modelo menor
- Baixa acurácia: modelo pré-treinado pode precisar de fine-tuning

### Google Vision
- "GOOGLE_API_KEY não encontrada": adicionar ao .env
- "Quota exceeded": excedeu free tier de 1000 req/mês
- "No face detected": imagem sem face detectável

### Roboflow
- "ROBOFLOW_API_KEY não encontrada": adicionar ao .env
- Rate limiting: adicionar delay entre requisições
