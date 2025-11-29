# Quick Start - Classificador Roboflow

## Instalação Rápida

```bash
cd 2_classificators/others
pip install -r requirements_roboflow.txt
```

## Opção 1: Teste Rápido (Mock - SEM API)

```bash
# Processa apenas simulação 01 (teste rápido)
python MockRoboflowClassifier.py --simulation 1

# Processa todas as 30 simulações
python MockRoboflowClassifier.py --num_simulations 30
```

**Resultados salvos em**: `3_simulation/results/mock_roboflow.csv`

## Opção 2: API Real do Roboflow

### Passo 1: Obter API Key

1. Criar conta: https://roboflow.com
2. Obter key: https://app.roboflow.com/settings/api
3. Copiar **Private API Key**

### Passo 2: Executar Classificação

```bash
# Teste com uma simulação
python RoboflowEmotionClassifier.py --api_key YOUR_API_KEY --simulation 1

# Primeiras 5 simulações (teste)
python RoboflowEmotionClassifier.py --api_key YOUR_API_KEY --num_simulations 5

# ATENÇÃO: Todas as 30 simulações = 3000 requisições!
python RoboflowEmotionClassifier.py --api_key YOUR_API_KEY --num_simulations 30
```

**Resultados salvos em**: `3_simulation/results/roboflow_emotion.csv`

## Análise de Resultados

```python
import pandas as pd

# Carrega resultados
df = pd.read_csv('../../3_simulation/results/roboflow_emotion.csv')

# Estatísticas
print(f"Acurácia média alegria: {df['acuracia_alegria'].mean():.2%}")
print(f"Acurácia média raiva: {df['acuracia_raiva'].mean():.2%}")
print(f"Acurácia média geral: {df['acuracia_geral'].mean():.2%}")
```

## Formato de Saída (CSV)

```csv
numero_simulacao,nome_modelo,qtd_sucesso_alegria,qtd_sucesso_raiva,total_alegria,total_raiva,acuracia_alegria,acuracia_raiva,acuracia_geral
1,roboflow_emotion,42,38,50,50,0.84,0.76,0.80
2,roboflow_emotion,40,36,50,50,0.80,0.72,0.76
...
```

## Solução de Problemas

### Erro: "Roboflow SDK não instalado"
```bash
pip install roboflow
```

### Erro: "API key inválida"
Verifique se copiou a **Private API Key** do Roboflow.

### Erro: "Rate limit exceeded"
Você excedeu o limite de requisições. Aguarde ou use plano pago.

## Documentação Completa

- **README_ROBOFLOW.md**: Documentação detalhada
- **IMPLEMENTATION_SUMMARY.md**: Visão geral da implementação
- **example_roboflow_usage.py**: Exemplos de uso em Python

## Comparação com CNN

Após executar, compare com resultados da CNN em:
`results/simple_cnn/all_simulations_results.csv`
