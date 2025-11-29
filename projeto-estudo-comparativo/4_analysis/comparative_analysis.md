# Planejamento: Análise Comparativa de Classificadores de Emoções

## Objetivo

Criar análise estatística comparativa completa entre classificadores de emoções faciais (Google Vision, Roboflow e YOLO11), seguindo metodologia científica rigorosa com visualizações e testes estatísticos.

## Dados Disponíveis

### Datasets de Resultados

1. **Google Vision API**
   - Localização: `../3_simulation/results/google_vision_emotion/results.csv`
   - Status: 30 simulações completas
   - Colunas esperadas: numero_simulacao, nome_modelo, qtd_sucesso_alegria, qtd_sucesso_raiva, total_alegria, total_raiva, tempo_total_ms, acuracia_alegria, acuracia_raiva, acuracia_geral, precisao_alegria, recall_alegria, f1_alegria, precisao_raiva, recall_raiva, f1_raiva, precisao_macro, recall_macro, f1_macro

2. **Roboflow API**
   - Localização: `../3_simulation/results/roboflow_emotion/results.csv`
   - Status: 30 simulações completas
   - Formato: Idêntico ao Google Vision

3. **YOLO11 Local**
   - Localização: `../3_simulation/results/yolo11_emotion/results.csv`
   - Status: Verificar se existe, se não, executar primeiro
   - Formato: Idêntico aos anteriores

## Estrutura de Implementação

### Fase 1: Preparação e Validação de Dados

#### Script: `prepare_data.py`

**Objetivo:** Validar e consolidar dados dos classificadores

**Funcionalidades:**
1. Verificar existência dos arquivos CSV
2. Validar integridade dos dados (30 simulações, colunas corretas)
3. Verificar presença de valores nulos ou inconsistentes
4. Consolidar dados em estrutura unificada
5. Calcular métricas adicionais se necessário

**Saídas:**
- `data/consolidated_results.csv` - Dados consolidados de todos os modelos
- `data/data_validation_report.txt` - Relatório de validação

**Código esperado:**
```python
def validar_dataset(caminho_csv, nome_modelo):
    """Valida CSV de resultados."""
    # Verificar existência
    # Validar 30 simulações
    # Validar colunas obrigatórias
    # Verificar valores nulos
    # Retornar relatório

def consolidar_dados(lista_csv):
    """Consolida múltiplos CSVs em um único DataFrame."""
    # Carregar todos os CSVs
    # Adicionar coluna identificadora de modelo
    # Concatenar
    # Retornar DataFrame consolidado
```

---

### Fase 2: Estatísticas Descritivas

#### Script: `descriptive_statistics.py`

**Objetivo:** Calcular estatísticas descritivas para todos os modelos

**Análises:**

1. **Por Modelo - Métricas Gerais:**
   - Média ± Desvio Padrão
   - Mediana
   - Mínimo e Máximo
   - Quartis (Q1, Q3)
   - Intervalo Interquartil (IQR)

2. **Métricas a Analisar:**
   - acuracia_geral
   - acuracia_alegria
   - acuracia_raiva
   - precisao_macro
   - recall_macro
   - f1_macro
   - tempo_total_ms

3. **Por Classe:**
   - Estatísticas separadas para alegria e raiva
   - Identificar viés de cada modelo

**Saídas:**
- `results/descriptive_stats_summary.csv` - Tabela resumo
- `results/descriptive_stats_detailed.json` - Estatísticas completas em JSON
- `results/stats_by_class.csv` - Estatísticas por classe

**Formato da Tabela:**
```csv
Modelo,Métrica,Média,DP,Mediana,Min,Max,Q1,Q3
Google Vision,acuracia_geral,0.164,0.040,0.160,0.100,0.240,0.140,0.180
```

---

### Fase 3: Visualizações

#### Script: `generate_visualizations.py`

**Objetivo:** Criar todas as visualizações necessárias

**Visualizações Planejadas:**

**1. Boxplots Comparativos (Requisito 1)**
- Arquivo: `figures/comparative_boxplots.png`
- Descrição: 2x2 grid com 4 subplots
- Subplots:
  1. Acurácia Geral
  2. Precisão Macro
  3. Recall Macro
  4. F1-Score Macro
- Eixo X: Modelos (Google Vision, Roboflow, YOLO11)
- Eixo Y: Valor da métrica (0-1)
- Características:
  - Mostrar mediana, quartis, outliers
  - Cores diferentes por modelo
  - Grid de fundo
  - Título descritivo em cada subplot

**2. Gráficos de Linha - Acurácia e F1-Score (Requisito 2)**
- Arquivo: `figures/line_plot_accuracy_f1.png`
- Descrição: 2 subplots verticais
- Subplot 1: Acurácia Geral por Simulação
  - Eixo X: Número da simulação (1-30)
  - Eixo Y: Acurácia (0-1)
  - Linhas: Uma por modelo
- Subplot 2: F1-Score Macro por Simulação
  - Eixo X: Número da simulação (1-30)
  - Eixo Y: F1-Score (0-1)
  - Linhas: Uma por modelo
- Características:
  - Legendas claras
  - Marcadores em cada ponto
  - Mostrar tendências/estabilidade

**3. Comparação por Classe**
- Arquivo: `figures/metrics_by_class.png`
- Descrição: 3x2 grid (3 métricas x 2 classes)
- Métricas: Precisão, Recall, F1-Score
- Classes: Alegria e Raiva
- Formato: Boxplots agrupados por modelo

**4. Comparação de Tempo**
- Arquivo: `figures/time_comparison.png`
- Descrição: Gráfico de barras
- Eixo X: Modelos
- Eixo Y: Tempo médio (segundos)
- Barras de erro: Desvio padrão
- Anotações: Tempo médio em cada barra

**5. Matriz de Confusão Agregada**
- Arquivo: `figures/confusion_matrices.png`
- Descrição: 3 heatmaps (um por modelo)
- Formato: 2x2 (Alegria Predita/Real, Raiva Predita/Real)
- Agregação: Soma de todas as 30 simulações
- Valores: Contagens absolutas
- Colormap: Blues

**6. Dispersão Acurácia vs Tempo**
- Arquivo: `figures/accuracy_vs_time.png`
- Descrição: Scatter plot
- Eixo X: Tempo médio (segundos)
- Eixo Y: Acurácia média
- Pontos: Um por modelo
- Anotações: Nome do modelo próximo ao ponto
- Interpretação: Trade-off velocidade vs acurácia

**Código esperado:**
```python
def criar_boxplots_comparativos(df, metricas, output_path):
    """Cria grid 2x2 de boxplots."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    # Implementação

def criar_graficos_linha(df, output_path):
    """Cria gráficos de linha para acurácia e f1."""
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    # Implementação
```

---

### Fase 4: Testes Estatísticos

#### Script: `statistical_tests.py`

**Objetivo:** Realizar testes de hipótese pareados (Requisito 3)

**Testes a Realizar:**

**1. Teste de Wilcoxon Pareado (Principal)**
- Comparações:
  - Google Vision vs Roboflow
  - Google Vision vs YOLO11
  - Roboflow vs YOLO11
- Métricas testadas:
  - acuracia_geral
  - precisao_macro
  - recall_macro
  - f1_macro
- Nível de significância: α = 0.05 (95% de confiança)
- Hipóteses:
  - H0: Não há diferença entre os modelos
  - H1: Há diferença significativa entre os modelos

**2. Teste t Pareado (Complementar)**
- Mesmas comparações que Wilcoxon
- Assumindo distribuição normal (validar com Shapiro-Wilk)

**3. Tamanho de Efeito**
- Cohen's d para teste t
- r de Rosenthal para Wilcoxon
- Interpretação:
  - Pequeno: d < 0.5 ou r < 0.3
  - Médio: 0.5 ≤ d < 0.8 ou 0.3 ≤ r < 0.5
  - Grande: d ≥ 0.8 ou r ≥ 0.5

**4. Teste de Normalidade**
- Shapiro-Wilk para cada métrica
- Validar premissas do teste t

**Saídas:**
- `results/wilcoxon_test_results.csv` - Resultados do Wilcoxon
- `results/t_test_results.csv` - Resultados do teste t
- `results/effect_sizes.csv` - Tamanhos de efeito
- `results/normality_tests.csv` - Testes de normalidade

**Formato da Tabela de Wilcoxon:**
```csv
Comparação,Métrica,Mediana_Modelo1,Mediana_Modelo2,Statistic,p_value,Significativo,Tamanho_Efeito,Interpretação
Google vs Roboflow,acuracia_geral,0.16,0.38,0.0,<0.001,Sim,0.87,Grande
```

---

### Fase 5: Geração do Relatório

#### Script: `generate_report.py`

**Objetivo:** Gerar relatório completo em Markdown

**Estrutura do Relatório:**

```markdown
# Relatório de Análise Comparativa: Classificadores de Emoções Faciais

## 1. Introdução
- Contexto do estudo
- Modelos comparados
- Objetivos da análise

## 2. Metodologia
### 2.1 Dataset
- Fonte e descrição
- Estrutura (30 simulações, 50 imagens/classe)
- Total de imagens processadas

### 2.2 Métricas
- Definições de acurácia, precisão, recall, f1-score
- Métricas por classe e macro

### 2.3 Análise Estatística
- Estatísticas descritivas
- Teste de Wilcoxon pareado
- Tamanho de efeito
- Nível de significância

## 3. Resultados

### 3.1 Estatísticas Descritivas
[Tabela com média ± DP para cada modelo e métrica]

![Boxplots Comparativos](figures/comparative_boxplots.png)

### 3.2 Análise por Classe
[Discussão sobre viés para alegria vs raiva]

![Métricas por Classe](figures/metrics_by_class.png)

### 3.3 Evolução por Simulação
[Análise de estabilidade]

![Gráficos de Linha](figures/line_plot_accuracy_f1.png)

### 3.4 Comparação de Tempo
[Análise de eficiência computacional]

![Tempo de Processamento](figures/time_comparison.png)

### 3.5 Matrizes de Confusão
[Análise de erros]

![Matrizes de Confusão](figures/confusion_matrices.png)

### 3.6 Trade-off Acurácia vs Tempo
![Dispersão](figures/accuracy_vs_time.png)

### 3.7 Testes Estatísticos
[Tabelas de Wilcoxon com interpretação]

## 4. Discussão

### 4.1 Performance dos Modelos
- Ranking de performance
- Pontos fortes e fracos de cada modelo
- Viés identificado

### 4.2 Significância Estatística
- Diferenças significativas encontradas
- Tamanho do efeito
- Implicações práticas

### 4.3 Análise de Custo-Benefício
- Acurácia vs Tempo
- Acurácia vs Custo financeiro
- Recomendações por caso de uso

### 4.4 Limitações
- Limitações do estudo
- Possíveis vieses
- Sugestões de melhorias

## 5. Conclusões
- Principais achados
- Recomendações
- Próximos passos

## 6. Referências

## Apêndices
- Apêndice A: Dados completos
- Apêndice B: Código de análise
```

**Saída:**
- `comparative_analysis_report.md`

---

### Fase 6: Resumo Executivo

#### Script: `generate_executive_summary.py`

**Objetivo:** Criar resumo executivo de 1-2 páginas

**Conteúdo:**
- Objetivos do estudo
- Principais resultados (bullet points)
- Recomendações práticas
- Próximos passos

**Saída:**
- `executive_summary.md`

---

## Estrutura de Diretórios

```
4_analysis/
├── comparative_analysis.md           # Este arquivo (planejamento)
├── prepare_data.py                   # Fase 1
├── descriptive_statistics.py         # Fase 2
├── generate_visualizations.py        # Fase 3
├── statistical_tests.py              # Fase 4
├── generate_report.py                # Fase 5
├── generate_executive_summary.py     # Fase 6
├── data/                             # Dados consolidados
│   ├── consolidated_results.csv
│   └── data_validation_report.txt
├── results/                          # Resultados das análises
│   ├── descriptive_stats_summary.csv
│   ├── descriptive_stats_detailed.json
│   ├── stats_by_class.csv
│   ├── wilcoxon_test_results.csv
│   ├── t_test_results.csv
│   ├── effect_sizes.csv
│   └── normality_tests.csv
├── figures/                          # Visualizações
│   ├── comparative_boxplots.png
│   ├── line_plot_accuracy_f1.png
│   ├── metrics_by_class.png
│   ├── time_comparison.png
│   ├── confusion_matrices.png
│   └── accuracy_vs_time.png
├── comparative_analysis_report.md    # Relatório final
└── executive_summary.md              # Resumo executivo
```

---

## Ordem de Execução

```bash
# Fase 1: Preparação
python 4_analysis/prepare_data.py

# Fase 2: Estatísticas
python 4_analysis/descriptive_statistics.py

# Fase 3: Visualizações
python 4_analysis/generate_visualizations.py

# Fase 4: Testes estatísticos
python 4_analysis/statistical_tests.py

# Fase 5: Relatório
python 4_analysis/generate_report.py

# Fase 6: Resumo executivo
python 4_analysis/generate_executive_summary.py
```

Ou executar tudo de uma vez:
```bash
# Script mestre que executa todas as fases
python 4_analysis/run_full_analysis.py
```

---

## Dependências Python

```python
# requirements.txt para análise
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
seaborn>=0.12.0
scipy>=1.9.0
```

---

## Checklist de Validação

Antes de executar a análise, verificar:
- [ ] Arquivo `google_vision_emotion/results.csv` existe e tem 30 linhas
- [ ] Arquivo `roboflow_emotion/results.csv` existe e tem 30 linhas
- [ ] Arquivo `yolo11_emotion/results.csv` existe e tem 30 linhas (ou executar YOLO11 primeiro)
- [ ] Todas as colunas necessárias estão presentes
- [ ] Não há valores nulos em métricas críticas
- [ ] Diretórios `data/`, `results/` e `figures/` foram criados

---

## Critérios de Qualidade

### Estatístico
- Testes apropriados para dados pareados
- Validação de premissas (normalidade)
- Cálculo correto de tamanhos de efeito
- Interpretação correta de p-values

### Visual
- Gráficos profissionais e claros
- Cores consistentes por modelo
- Legendas e rótulos legíveis
- Títulos descritivos
- Escala apropriada

### Documental
- Relatório estruturado e fluente
- Interpretação baseada em dados
- Discussão de limitações
- Recomendações práticas
- Referências citadas

---

## Cronograma Estimado

- **Fase 1** (Preparação): 30 minutos
- **Fase 2** (Estatísticas): 1 hora
- **Fase 3** (Visualizações): 2 horas
- **Fase 4** (Testes): 1 hora
- **Fase 5** (Relatório): 2 horas
- **Fase 6** (Resumo): 30 minutos

**Total**: ~7 horas