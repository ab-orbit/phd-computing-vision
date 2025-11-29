# Comparação de Classificadores - Projeto Comparativo

## Visão Geral

Este projeto implementa **3 abordagens diferentes** para classificação de emoções faciais (raiva vs alegria):

1. **CNN Tradicional** (SimpleCNN)
2. **API Foundation Model** (Roboflow)
3. **Foundation Model Local** (YOLO11)

## 📊 Comparação Rápida

| Aspecto | CNN do Zero | Roboflow API | YOLO11 Local |
|---------|-------------|--------------|--------------|
| **Localização** | `2_classificators/SimpleCNN_BinaryClassifier.ipynb` | `2_classificators/others/RoboflowEmotionClassifier.py` | `2_classificators/yolo11/YOLO11EmotionClassifier.py` |
| **Treinamento** | Sim (horas) | Não | Não |
| **Velocidade** | ~10ms/img | ~600ms/img | ~2-50ms/img |
| **Hardware** | GPU (treino) | Nenhum | GPU (inferência) |
| **Custo** | GPU 1x | $/requisição | GPU 1x |
| **Offline** | ✅ Sim | ❌ Não | ✅ Sim |
| **Customização** | ✅✅✅ Total | ❌ Limitada | ✅✅ Moderada |
| **Acurácia Esperada** | 85-95% | 30-40% | 70-85% |

## 🎯 Quando Usar Cada Abordagem

### Use CNN do Zero quando:
- ✅ Dataset é muito específico/único
- ✅ Precisa de máxima acurácia
- ✅ Tem tempo e GPU para treinar
- ✅ Precisa total controle sobre arquitetura
- ✅ Dataset é grande (>10k imagens)

### Use Roboflow quando:
- ✅ Prototipagem ultra-rápida
- ✅ Não tem hardware (GPU)
- ✅ Dataset muito pequeno
- ✅ Orçamento para API ($)
- ✅ Quer testar viabilidade antes de investir

### Use YOLO11 quando:
- ✅ Quer velocidade sem treinar
- ✅ Tem GPU disponível
- ✅ Precisa funcionar offline
- ✅ Quer evitar custos recorrentes
- ✅ Dataset médio (1k-10k imagens)

## 📁 Estrutura de Implementação

```
2_classificators/
├── SimpleCNN_BinaryClassifier.ipynb  # CNN do zero
│   └── Notebook Jupyter completo
│
├── others/
│   ├── RoboflowEmotionClassifier.py  # API Roboflow
│   ├── MockRoboflowClassifier.py     # Versão mock para testes
│   ├── run_roboflow_classification.py
│   ├── README_ROBOFLOW.md
│   ├── QUICKSTART.md
│   └── requirements_roboflow.txt
│
└── yolo11/
    ├── YOLO11EmotionClassifier.py    # YOLO11 local
    ├── run_yolo11.sh
    ├── README.md
    ├── QUICKSTART.md
    └── requirements.txt
```

## 🚀 Como Executar Cada Um

### 1. CNN Tradicional

```bash
# Abrir notebook Jupyter
jupyter notebook 2_classificators/SimpleCNN_BinaryClassifier.ipynb

# Executar todas as células
# Ou usar função:
# run_all_simulations()
```

### 2. Roboflow API

```bash
cd /Users/jwcunha/Documents/repos/phd-datascience/visao-computacional/projeto-estudo-comparativo

# API key já está no .env
python 2_classificators/others/run_roboflow_classification.py --num_simulations 30
```

### 3. YOLO11 Local

```bash
cd /Users/jwcunha/Documents/repos/phd-datascience/visao-computacional/projeto-estudo-comparativo

python 2_classificators/yolo11/YOLO11EmotionClassifier.py --num_simulations 30
```

## 📊 Formato de Saída (Todos Idênticos)

Todos os três classificadores geram saída no mesmo formato:

```
3_simulation/results/
├── simple_cnn/
│   ├── results.csv
│   └── stats.json
├── roboflow_emotion/
│   ├── results.csv
│   └── stats.json
└── yolo11_emotion/
    ├── results.csv
    └── stats.json
```

### CSV Padrão
```csv
numero_simulacao,nome_modelo,qtd_sucesso_alegria,qtd_sucesso_raiva,total_alegria,total_raiva,tempo_total_ms,acuracia_alegria,acuracia_raiva,acuracia_geral
1,{modelo},X,Y,50,50,TTTT.TT,0.XX,0.YY,0.ZZ
...
```

## ⏱️ Tempo de Execução Estimado

### Por Simulação (100 imagens)

| Abordagem | GPU | CPU |
|-----------|-----|-----|
| **CNN** | ~5-10s | ~30-60s |
| **Roboflow** | ~60s | ~60s (API) |
| **YOLO11** | ~1-2s | ~3-10s |

### Total (30 Simulações)

| Abordagem | GPU | CPU |
|-----------|-----|-----|
| **CNN** | ~2.5-5min | ~15-30min |
| **Roboflow** | ~30min | ~30min |
| **YOLO11** | ~30-60s | ~1.5-5min |

## 💰 Análise de Custo

### Custo Inicial (Setup)

| Abordagem | Hardware | Software | Total |
|-----------|----------|----------|-------|
| **CNN** | GPU ($0-2000) | Grátis | $0-2000 |
| **Roboflow** | $0 | Grátis (1k req) | $0 |
| **YOLO11** | GPU ($0-2000) | Grátis | $0-2000 |

### Custo Recorrente (Produção)

| Abordagem | Por 1000 Predições | Por Mês (10k pred) |
|-----------|-------------------|-------------------|
| **CNN** | $0 | $0 |
| **Roboflow** | $5-50 | $50-500 |
| **YOLO11** | $0 | $0 |

## 🎓 Conceitos Pedagógicos Aprendidos

### 1. Trade-off Fundamental: Controle vs Conveniência

```
Mais Controle ←→ Mais Conveniência
CNN do Zero ←→ Roboflow API
```

### 2. Trade-off: Velocidade vs Acurácia

```
Mais Rápido ←→ Mais Preciso
YOLO11 (~2ms) ←→ CNN (~10ms) ←→ Roboflow (~600ms)
```

### 3. Trade-off: Custo Inicial vs Recorrente

```
Alto Inicial, Baixo Recorrente ←→ Baixo Inicial, Alto Recorrente
CNN/YOLO11 (GPU 1x) ←→ Roboflow ($/req)
```

## 📈 Resultados Esperados

### Acurácia (Estimativa)

| Classe | CNN | Roboflow | YOLO11 |
|--------|-----|----------|--------|
| **Alegria** | 90-95% | 50-60% | 75-85% |
| **Raiva** | 85-90% | 10-20% | 70-80% |
| **Geral** | 87-92% | 30-40% | 72-82% |

### Velocidade (GPU)

| Métrica | CNN | Roboflow | YOLO11 |
|---------|-----|----------|--------|
| **ms/imagem** | ~10 | ~600 | ~2 |
| **img/segundo** | ~100 | ~1.7 | ~500 |
| **Simulação** | ~1s | ~60s | ~0.2s |

## 🔬 Metodologia de Comparação

### 1. Dataset
- **30 simulações** independentes
- **50 imagens por classe** em cada simulação
- **Total**: 3000 imagens processadas por modelo

### 2. Métricas
- Acurácia por classe (alegria, raiva)
- Acurácia geral
- Tempo de processamento
- Desvio padrão (robustez)

### 3. Análise Estatística
- Média ± desvio padrão
- Intervalos de confiança (95%)
- Teste t para significância

## 📝 Script de Comparação

Após executar os três, compare resultados:

```python
import pandas as pd
import matplotlib.pyplot as plt

# Carrega resultados
cnn = pd.read_csv('3_simulation/results/simple_cnn/results.csv')
roboflow = pd.read_csv('3_simulation/results/roboflow_emotion/results.csv')
yolo = pd.read_csv('3_simulation/results/yolo11_emotion/results.csv')

# Compara acurácias
print("Acurácia Média Geral:")
print(f"CNN:      {cnn['acuracia_geral'].mean():.2%} ± {cnn['acuracia_geral'].std():.2%}")
print(f"Roboflow: {roboflow['acuracia_geral'].mean():.2%} ± {roboflow['acuracia_geral'].std():.2%}")
print(f"YOLO11:   {yolo['acuracia_geral'].mean():.2%} ± {yolo['acuracia_geral'].std():.2%}")

# Compara tempo
print("\nTempo Médio por Simulação:")
print(f"CNN:      {cnn['tempo_total_ms'].mean()/1000:.2f}s")
print(f"Roboflow: {roboflow['tempo_total_ms'].mean()/1000:.2f}s")
print(f"YOLO11:   {yolo['tempo_total_ms'].mean()/1000:.2f}s")

# Gráfico comparativo
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

# Acurácia
axes[0].boxplot([cnn['acuracia_geral'], roboflow['acuracia_geral'], yolo['acuracia_geral']])
axes[0].set_xticklabels(['CNN', 'Roboflow', 'YOLO11'])
axes[0].set_ylabel('Acurácia Geral')
axes[0].set_title('Comparação de Acurácia')

# Tempo
axes[1].bar(['CNN', 'Roboflow', 'YOLO11'],
            [cnn['tempo_total_ms'].mean(), roboflow['tempo_total_ms'].mean(), yolo['tempo_total_ms'].mean()])
axes[1].set_ylabel('Tempo (ms)')
axes[1].set_title('Comparação de Velocidade')

plt.tight_layout()
plt.savefig('3_simulation/results/comparison.png')
plt.show()
```

## 🎯 Conclusões Esperadas

### CNN Tradicional
**Vantagens:**
- ✅ Máxima acurácia
- ✅ Total customização
- ✅ Sem custos recorrentes

**Desvantagens:**
- ❌ Requer treinamento (tempo)
- ❌ Precisa de dataset grande
- ❌ Expertise em ML necessária

### Roboflow API
**Vantagens:**
- ✅ Zero setup
- ✅ Prototipagem rápida
- ✅ Sem necessidade de GPU

**Desvantagens:**
- ❌ Baixa acurácia (genérico)
- ❌ Lento (rede)
- ❌ Custo recorrente
- ❌ Requer internet

### YOLO11 Local
**Vantagens:**
- ✅ Melhor custo-benefício
- ✅ Muito rápido
- ✅ Boa acurácia
- ✅ Offline

**Desvantagens:**
- ❌ Requer GPU
- ❌ Menos customizável que CNN
- ❌ Pode precisar fine-tuning

## 🏆 Recomendação Final

Para este projeto específico (classificação binária de emoções):

1. **Pesquisa/Benchmark**: Use **CNN** (máxima acurácia)
2. **Prototipagem**: Use **Roboflow** (zero setup)
3. **Produção**: Use **YOLO11** (velocidade + custo)

## 📚 Documentação Completa

- **CNN**: `2_classificators/SimpleCNN_BinaryClassifier.ipynb`
- **Roboflow**: `2_classificators/others/README_ROBOFLOW.md`
- **YOLO11**: `2_classificators/yolo11/README.md`

---

**Este projeto demonstra o espectro completo de soluções em ML:**
**Do zero (CNN) → API (Roboflow) → Local Foundation (YOLO11)**

Cada abordagem tem seu lugar. A escolha depende de:
- Requisitos de acurácia
- Orçamento (tempo + dinheiro)
- Hardware disponível
- Expertise da equipe
