# Estudo Comparativo: Classificadores de Emoções Faciais

## Análise Comparativa entre Google Cloud Vision API e Roboflow API

---

**Disciplina**: Visão Computacional e PLN
**Professor**: Rodrigo Paiva - rfapo@cesar.school
**Grupo**: Los hijos del Donzelito

**Integrantes**:
- Regina Mafra - rma6@cesar.school
- Pedro Andrade - pfa@cesar.school
- Jefferson Cunha - jwc@cesar.school
- Frederico Nascimento - fgn@cesar.school
- Raymundo Reis - rmrn@cesar.school

---

## Sumário Executivo

Este projeto apresenta uma análise comparativa rigorosa entre dois classificadores de emoções faciais baseados em APIs de modelos foundation: **Google Cloud Vision API** e **Roboflow API**. Através de 30 simulações independentes (3.000 imagens por modelo), avaliamos objetivamente a performance, eficiência e adequação de cada abordagem para classificação binária de emoções (Alegria vs Raiva).

### Principais Resultados

- **Roboflow é estatisticamente superior** ao Google Vision em todas as métricas (p < 0.001)
- **Diferença substancial**: Roboflow alcança 38.5% vs Google Vision 16.4% de acurácia (+22.1%)
- **Tamanho de efeito grande** (r > 0.8), confirmando relevância prática
- **Roboflow é 2.4x mais rápido**: ~58s vs ~139s por simulação
- **Ambos apresentam performance insatisfatória** (< 40% acurácia) para uso em produção

---

## 1. Estrutura do Projeto

```
projeto-estudo-comparativo/
├── 1_dataprep/
│   ├── DataPreparation.py          # Preparação do dataset (30 simulações)
│   └── __init__.py
│
├── 2_classificators/
│   ├── gemini2/                    # Google Cloud Vision API
│   │   ├── GoogleVisionEmotionClassifier.py
│   │   ├── run_google_vision.py
│   │   ├── README.md
│   │   ├── QUICKSTART.md
│   │   ├── STATUS.md
│   │   └── requirements.txt
│   │
│   └── roboflow/                   # Roboflow API
│       ├── RoboflowEmotionClassifier.py
│       ├── run_roboflow.py
│       ├── README.md
│       └── requirements.txt
│
├── 3_simulation/
│   ├── results/
│   │   ├── google_vision_emotion/
│   │   │   ├── results.csv
│   │   │   └── stats.json
│   │   └── roboflow_emotion/
│   │       ├── results.csv
│   │       └── stats.json
│   │
│   ├── generate_comparative_report.py
│   ├── add_metrics.py
│   ├── wilcoxon_test_results.csv
│   ├── t_test_results.csv
│   ├── WILCOXON_TEST_EXPLANATION.md
│   └── README_COMPARATIVE_REPORT.md
│
├── 4_analysis/
│   ├── comparative_analysis_report.md    # Relatório Final
│   ├── data/
│   │   └── consolidated_results.csv
│   ├── results/
│   │   ├── descriptive_stats_summary.csv
│   │   ├── wilcoxon_test_results.csv
│   │   └── t_test_results.csv
│   └── figures/
│       ├── comparative_boxplots.png
│       ├── metrics_by_class.png
│       ├── line_plot_accuracy_f1.png
│       ├── time_comparison.png
│       ├── confusion_matrices.png
│       └── accuracy_vs_time.png
│
└── README.md                         # Este arquivo
```

---

## 2. Dataset

### Fonte
**Human Face Emotions** - Kaggle
https://www.kaggle.com/datasets/samithsachidanandan/human-face-emotions

### Classes
- **Alegria**: Expressões faciais de felicidade
- **Raiva**: Expressões faciais de irritação/raiva

### Estrutura Experimental
- **30 simulações independentes** para robustez estatística
- **50 imagens por classe** em cada simulação (100 imagens/simulação)
- **Total processado**: 3.000 imagens por modelo
- **Amostragem**: Aleatória e independente para cada simulação

### Justificativa Metodológica
A utilização de 30 simulações independentes permite:
1. Avaliar a variabilidade e estabilidade dos modelos
2. Calcular estatísticas descritivas robustas (média, desvio padrão)
3. Aplicar testes estatísticos pareados com poder adequado
4. Reduzir viés de seleção de amostras específicas

---

## 3. Modelos Avaliados

### 3.1 Google Cloud Vision API

**Tipo**: API comercial de visão computacional do Google Cloud

**Características**:
- Detecção de faces e análise de emoções nativa
- Infraestrutura robusta, modelo treinado em grande escala
- Implementação via REST HTTP API com API Key

**Vantagens**:
- Infraestrutura robusta e escalável
- API madura e bem documentada
- Detecção de faces nativa e confiável

**Limitações**:
- Acurácia muito baixa para esta tarefa (16.4%)
- Forte viés contra classe raiva (~4% de acurácia)
- Tempo de processamento mais lento (~139s/simulação)
- Custo por requisição
- Modelo genérico não otimizado para este domínio específico

### 3.2 Roboflow API

**Tipo**: Plataforma de inferência de modelos de visão computacional

**Modelo utilizado**: `computer-vision-projects-zhogq/emotion-detection-y0svj`

**Características**:
- API de inference com modelo pré-treinado para detecção de emoções
- Flexibilidade e integração simplificada
- Modelo especializado em emoções

**Vantagens**:
- Acurácia superior (38.5%)
- Processamento mais rápido (~58s/simulação)
- Melhor custo-benefício

**Limitações**:
- Acurácia ainda abaixo de 40% (inadequada para produção)
- Viés significativo para alegria (~64%) vs raiva (~13%)
- Performance depende do modelo hospedado

---

## 4. Metodologia

### 4.1 Métricas de Avaliação

#### Acurácia
```
Acurácia = (VP + VN) / Total
```
Proporção de predições corretas em relação ao total.

#### Precisão (Precision)
```
Precisão = VP / (VP + FP)
```
Das imagens classificadas como uma classe, quantas realmente pertencem a ela.

#### Recall (Sensibilidade)
```
Recall = VP / (VP + FN)
```
Das imagens que realmente pertencem a uma classe, quantas foram identificadas.

#### F1-Score
```
F1 = 2 × (Precisão × Recall) / (Precisão + Recall)
```
Média harmônica entre precisão e recall.

#### Métricas Macro
```
Métrica_Macro = (Métrica_Alegria + Métrica_Raiva) / 2
```
Média simples das métricas de cada classe, tratando classes igualmente.

### 4.2 Análise Estatística

#### Estatísticas Descritivas
- Média ± Desvio Padrão
- Mediana (percentil 50)
- Quartis (Q1: percentil 25, Q3: percentil 75)
- Intervalo Interquartil (IQR = Q3 - Q1)

#### Teste de Normalidade
- **Teste**: Shapiro-Wilk
- **Nível de significância**: α = 0.05
- **Resultado**: Todas as métricas passaram (p > 0.05)

#### Teste de Wilcoxon Pareado (Principal)
- **Tipo**: Não-paramétrico para amostras pareadas
- **Hipóteses**:
  - H₀: Não há diferença entre os modelos
  - H₁: Há diferença significativa entre os modelos
- **Nível de significância**: α = 0.05 (95% de confiança)
- **Tamanho de efeito**: r de Rosenthal

#### Teste t Pareado (Complementar)
- **Tipo**: Paramétrico para amostras pareadas
- **Uso**: Confirmação dos resultados
- **Tamanho de efeito**: Cohen's d

---

## 5. Resultados

### 5.1 Estatísticas Descritivas

| Modelo | Métrica | Média ± DP | Mediana | Min | Max |
|--------|---------|------------|---------|-----|-----|
| Google Vision | Acurácia | 0.1642 ± 0.0398 | 0.1600 | 0.0900 | 0.2300 |
| Google Vision | Precisão | 0.1421 ± 0.0352 | 0.1447 | 0.0818 | 0.2003 |
| Google Vision | Recall | 0.1643 ± 0.0398 | 0.1600 | 0.0900 | 0.2300 |
| Google Vision | F1-Score | 0.1510 ± 0.0360 | 0.1531 | 0.0855 | 0.2044 |
| **Roboflow** | **Acurácia** | **0.3850 ± 0.0369** | **0.3800** | **0.2800** | **0.4400** |
| **Roboflow** | **Precisão** | **0.3397 ± 0.0474** | **0.3398** | **0.2472** | **0.4286** |
| **Roboflow** | **Recall** | **0.3850 ± 0.0369** | **0.3800** | **0.2800** | **0.4400** |
| **Roboflow** | **F1-Score** | **0.3393 ± 0.0385** | **0.3386** | **0.2559** | **0.4167** |

**Observação**: Roboflow apresenta acurácia média 2.3x superior (38.5% vs 16.4%) com diferença absoluta de 22.1%.

### 5.2 Performance por Classe

| Modelo | Classe | Acurácia | Precisão | Recall | F1-Score |
|--------|--------|----------|----------|--------|----------|
| Google Vision | Alegria | 0.2845 | 0.2269 | 0.2845 | 0.2523 |
| Google Vision | Raiva | 0.0440 | 0.0572 | 0.0440 | 0.0496 |
| **Roboflow** | **Alegria** | **0.6427** | **0.4234** | **0.6427** | **0.5100** |
| **Roboflow** | **Raiva** | **0.1273** | **0.2560** | **0.1273** | **0.1686** |

**Análise de Viés**:
- **Google Vision**: Forte viés para Alegria (~28%) vs Raiva (~4%)
- **Roboflow**: Também apresenta viés para Alegria (~64%) vs Raiva (~13%)
- **Implicação**: Ambos têm dificuldade em identificar raiva

### 5.3 Teste de Wilcoxon Pareado

| Métrica | Mediana Google | Mediana Roboflow | Diferença | p-value | Significativo | Efeito (r) |
|---------|----------------|------------------|-----------|---------|---------------|------------|
| **Acurácia** | 0.1600 | 0.3800 | +0.2200 | 0.000002*** | Sim | 0.87 (Grande) |
| **Precisão** | 0.1447 | 0.3398 | +0.1951 | <0.000001*** | Sim | 1.10 (Grande) |
| **Recall** | 0.1600 | 0.3800 | +0.2200 | 0.000002*** | Sim | 0.87 (Grande) |
| **F1-Score** | 0.1531 | 0.3386 | +0.1855 | <0.000001*** | Sim | 1.10 (Grande) |

**Legenda**: *** p<0.001

**Interpretação**:
- **p-value < 0.001**: Diferença extremamente significativa (< 0.1% de chance de ser aleatória)
- **Wilcoxon Statistic = 0.00**: Em TODAS as 30 simulações, Roboflow > Google Vision
- **Tamanho de efeito r > 0.8**: Efeito grande, diferença substancial e praticamente relevante
- **Conclusão**: Roboflow é estatisticamente superior com 99.9% de confiança

### 5.4 Tempo de Processamento

| Modelo | Tempo Médio/Simulação | Tempo/Imagem | Velocidade Relativa |
|--------|-----------------------|--------------|---------------------|
| Google Vision | 139.37s ± 187.08s | ~1.39s | Baseline |
| **Roboflow** | **58.08s ± 8.39s** | **~0.58s** | **2.4x mais rápido** |

---

## 6. Visualizações

Todas as visualizações estão disponíveis em `4_analysis/figures/`:

1. **comparative_boxplots.png**: Boxplots das 4 métricas principais
2. **metrics_by_class.png**: Performance detalhada por classe (Alegria vs Raiva)
3. **line_plot_accuracy_f1.png**: Evolução da acurácia e F1-Score nas 30 simulações
4. **time_comparison.png**: Comparação de tempo de processamento
5. **confusion_matrices.png**: Matrizes de confusão agregadas
6. **accuracy_vs_time.png**: Trade-off entre acurácia e tempo

---

## 7. Conclusões

### 7.1 Principais Achados

1. **Roboflow é estatisticamente superior** ao Google Vision em todas as métricas (p < 0.001)

2. **Diferença Substancial**:
   - Acurácia: 38.5% vs 16.4% (diferença de 22.1%)
   - Tamanho de efeito grande (r > 0.8) indica relevância prática

3. **Ambos apresentam performance insatisfatória** (< 40% acurácia) para uso em produção

4. **Forte viés para classe Alegria** em ambos os modelos:
   - Google Vision: ~28% alegria vs ~4% raiva
   - Roboflow: ~64% alegria vs ~13% raiva

5. **Roboflow é mais rápido**: ~2.4x mais rápido que Google Vision

6. **APIs genéricas não substituem modelos especializados** para tarefas específicas

### 7.2 Recomendações Práticas

#### Para Uso em Produção
1. **Não utilizar esses modelos em produção** sem validação extensiva adicional
2. **Considerar fine-tuning** de modelos foundation locais (ex: YOLO11)
3. **Treinar CNN específica** para o domínio se alta acurácia for crítica
4. **Avaliar aumento de dataset** para treinar modelos mais robustos
5. **Entre as APIs testadas, preferir Roboflow** (melhor custo-benefício)

#### Para Pesquisa
1. **Incluir YOLO11** na análise comparativa
2. **Implementar CNN treinada do zero** como baseline
3. **Testar fine-tuning** dos modelos foundation
4. **Expandir para mais classes** de emoções
5. **Avaliar data augmentation** para melhorar generalização
6. **Testar ensemble** de modelos

### 7.3 Aprendizados Pedagógicos

Este estudo demonstra importantes conceitos de Machine Learning:

#### Trade-off: Conveniência vs Performance
- APIs comerciais oferecem conveniência (zero setup, infraestrutura pronta)
- Mas performance pode ser inadequada para tarefas específicas
- Fine-tuning ou modelos especializados são necessários para alta performance

#### Importância de Múltiplas Simulações
- Uma única avaliação pode ser enganosa devido a variabilidade
- 30 simulações permitem avaliar consistência e robustez
- Testes estatísticos requerem múltiplas amostras para poder adequado

#### Viés de Modelos
- Ambos os modelos apresentam viés forte para classe Alegria
- Viés pode resultar de desbalanceamento no treinamento ou características do dataset
- Análise por classe é essencial para identificar vieses

#### Teste de Hipóteses
- Diferença numérica não implica diferença estatística
- p-value quantifica evidência contra hipótese nula
- Tamanho de efeito indica relevância prática da diferença

---

## 8. Como Executar

### 8.1 Requisitos

```bash
Python 3.8+
pip install -r requirements.txt
```

Bibliotecas principais:
- pandas
- numpy
- matplotlib
- seaborn
- scipy
- requests
- python-dotenv

### 8.2 Configuração

1. Clone o repositório
2. Baixe o dataset do Kaggle
3. Crie arquivo `.env` com as chaves de API:

```env
GOOGLE_API_KEY=sua_chave_google_aqui
ROBOFLOW_API_KEY=sua_chave_roboflow_aqui
```

### 8.3 Execução Passo a Passo

#### Passo 1: Preparar Dataset (30 Simulações)
```bash
cd 1_dataprep
python DataPreparation.py
```

#### Passo 2: Executar Google Vision
```bash
cd 2_classificators/gemini2
python run_google_vision.py
```

#### Passo 3: Executar Roboflow
```bash
cd 2_classificators/roboflow
python run_roboflow.py
```

#### Passo 4: Adicionar Métricas (Precisão, Recall, F1)
```bash
cd 3_simulation
python add_metrics.py
```

#### Passo 5: Gerar Relatório Comparativo
```bash
cd 3_simulation
python generate_comparative_report.py
```

#### Passo 6: Visualizar Análise Completa
```bash
cd 4_analysis
# Consulte comparative_analysis_report.md
```

---

## 9. Trabalhos Futuros

1. **Executar e comparar YOLO11** (modelo foundation local)
2. **Implementar CNN treinada do zero** (SimpleCNN)
3. **Fine-tuning de modelos foundation** no dataset específico
4. **Análise de erros detalhada**: quais imagens são consistentemente mal classificadas?
5. **Expandir dataset**: mais simulações e mais imagens por simulação
6. **Outras métricas**: ROC-AUC, curvas PR, matriz de confusão normalizada
7. **Análise de custo total**: incluir custos de desenvolvimento e manutenção

---

## 10. Referências

1. **Google Cloud Vision API Documentation**: https://cloud.google.com/vision/docs
2. **Roboflow API Documentation**: https://docs.roboflow.com
3. **Human Face Emotions Dataset**: https://www.kaggle.com/datasets/samithsachidanandan/human-face-emotions
4. **Shapiro-Wilk Test**: Shapiro, S. S., & Wilk, M. B. (1965). An analysis of variance test for normality
5. **Wilcoxon Signed-Rank Test**: Wilcoxon, F. (1945). Individual comparisons by ranking methods
6. **Cohen's d**: Cohen, J. (1988). Statistical power analysis for the behavioral sciences
7. **Rosenthal's r**: Rosenthal, R. (1991). Meta-analytic procedures for social research

---

## 11. Licença e Autoria

**Projeto Acadêmico** - Estudo Comparativo de Classificadores de Emoções Faciais

Desenvolvido para fins educacionais e de pesquisa.

---

**Relatório Completo**: Consulte `4_analysis/comparative_analysis_report.md` para análise detalhada com todas as visualizações e interpretações estatísticas.

**Data de Atualização**: 29/11/2025
