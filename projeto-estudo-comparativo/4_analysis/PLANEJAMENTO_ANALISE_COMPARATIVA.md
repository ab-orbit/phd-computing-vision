# Planejamento: Análise Comparativa de Classificadores de Emoções

## Objetivo

Criar relatório completo de análise comparativa entre os classificadores Google Vision e Roboflow (e potencialmente YOLO11 quando disponível), seguindo metodologia científica rigorosa.

## Dados Disponíveis

### Datasets de Resultados

1. **Google Vision API**
   - Localização: `3_simulation/results/google_vision_emotion/results.csv`
   - Status: 30 simulações completas
   - Métricas: acurácia, precisão, recall, f1-score (por classe e macro)

2. **Roboflow API**
   - Localização: `3_simulation/results/roboflow_emotion/results.csv`
   - Status: 30 simulações completas
   - Métricas: acurácia, precisão, recall, f1-score (por classe e macro)


### Arquivos Já Gerados

- `3_simulation/results/comparative_summary.csv` - Resumo estatístico
- `3_simulation/results/wilcoxon_test_results.csv` - Testes de Wilcoxon
- `3_simulation/results/t_test_results.csv` - Testes t pareados
- `3_simulation/results/comparative_boxplots.png` - Boxplots 4 métricas
- `3_simulation/results/comparative_by_class.png` - Comparação por classe
- `3_simulation/generate_comparative_report.py` - Script existente

## Estrutura do Relatório

### 1. Introdução

**Conteúdo:**
- Contexto do estudo comparativo
- Objetivos da análise
- Metodologia de comparação (30 simulações, 50 imagens/classe)
- Descrição dos modelos comparados:
  - Google Cloud Vision API (API comercial)
  - Roboflow API (API de inference)
  - YOLO11 (foundation model local - quando disponível)

**Formato:** Markdown com seções claras

---

### 2. Metodologia

**Conteúdo:**

#### 2.1 Dataset
- Fonte: Human Face Emotions (Kaggle)
- Classes: Raiva e Alegria
- Estrutura: 30 simulações independentes
- Tamanho: 50 imagens por classe por simulação
- Total processado: 3.000 imagens por modelo

#### 2.2 Métricas Avaliadas
- **Acurácia**: (VP + VN) / Total
- **Precisão**: VP / (VP + FP)
- **Recall**: VP / (VP + FN)
- **F1-Score**: 2 × (Precisão × Recall) / (Precisão + Recall)
- **Tempo de Processamento**: millisegundos por simulação

Métricas calculadas:
- Por classe (alegria, raiva)
- Macro (média simples entre classes)
- Geral

#### 2.3 Análise Estatística
- **Estatísticas Descritivas**: média, desvio padrão, mediana
- **Visualizações**: boxplots, gráficos de linha
- **Testes de Hipótese**:
  - Teste t pareado (paramétrico)
  - Teste de Wilcoxon pareado (não-paramétrico)
  - Nível de significância: α = 0.05 (95% de confiança)
  - Cálculo de tamanho de efeito (Cohen's d)

**Formato:** Markdown com fórmulas e explicações

---

### 3. Resultados

**Conteúdo:**

#### 3.1 Estatísticas Descritivas

**Tabela Geral:**
```
| Modelo         | Acurácia      | Precisão      | Recall        | F1-Score      | Tempo (s) |
|----------------|---------------|---------------|---------------|---------------|-----------|
| Google Vision  | 0.164 ± 0.040 | 0.142 ± 0.035 | 0.164 ± 0.040 | 0.151 ± 0.036 | 139.4     |
| Roboflow       | 0.385 ± 0.037 | 0.340 ± 0.047 | 0.385 ± 0.037 | 0.339 ± 0.039 | 58.1      |
```

**Tabela por Classe:**
- Métricas separadas para alegria e raiva
- Identificar viés de cada modelo

#### 3.2 Visualizações

**Gráfico 1: Boxplots Comparativos**
- 4 subplots: Acurácia, Precisão, Recall, F1-Score
- Comparação lado a lado dos modelos
- Arquivo: `comparative_boxplots.png`

**Gráfico 2: Comparação por Classe**
- Métricas separadas por classe (alegria vs raiva)
- Identificar qual classe cada modelo performa melhor
- Arquivo: `comparative_by_class.png`

**Gráfico 3: Gráficos de Linha (a criar)**
- Eixo X: Número da simulação (1-30)
- Eixo Y duplo: Acurácia e F1-Score
- Linhas separadas por modelo
- Objetivo: Mostrar estabilidade ao longo das simulações

**Gráfico 4: Comparação de Tempo (a criar)**
- Gráfico de barras: tempo médio por simulação
- Análise de eficiência computacional

#### 3.3 Testes Estatísticos

**Teste de Wilcoxon Pareado:**
- Comparação não-paramétrica entre modelos
- Resultados para cada métrica (acurácia, precisão, recall, f1)
- Interpretação do p-value
- Tamanho do efeito (Cohen's d ou r)

**Exemplo de Tabela:**
```
| Métrica    | Mediana Google | Mediana Roboflow | Diferença | p-value | Significativo | Tamanho Efeito |
|------------|----------------|------------------|-----------|---------|---------------|----------------|
| Acurácia   | 0.16          | 0.38            | 0.22      | <0.001  | Sim           | Grande         |
| Precisão   | 0.14          | 0.34            | 0.20      | <0.001  | Sim           | Grande         |
| Recall     | 0.16          | 0.38            | 0.22      | <0.001  | Sim           | Grande         |
| F1-Score   | 0.15          | 0.34            | 0.19      | <0.001  | Sim           | Grande         |
```

**Formato:** Markdown com tabelas e referências aos gráficos

---

### 4. Discussão

**Conteúdo:**

#### 4.1 Análise de Performance

**Google Cloud Vision:**
- Acurácia geral muito baixa (16.4%)
- Forte viés para classe alegria
- Praticamente incapaz de detectar raiva (0-2% de acerto)
- Possíveis causas:
  - Modelo não otimizado para dataset específico
  - Mapeamento inadequado de emoções
  - Dataset pode ter características diferentes do treinamento

**Roboflow:**
- Acurácia melhor mas ainda baixa (38.5%)
- Também apresenta viés para alegria
- Performance em raiva ligeiramente melhor que Google Vision
- Limitações similares de generalização

#### 4.2 Comparação Estatística

**Diferença Significativa:**
- Roboflow significativamente superior ao Google Vision (p < 0.001)
- Tamanho de efeito grande (d > 0.8)
- Diferença consistente em todas as métricas

**Implicações:**
- APIs genéricas têm limitações para tarefas específicas
- Fine-tuning ou modelos especializados são necessários
- Trade-off entre conveniência e performance

#### 4.3 Análise de Custo-Benefício

**Google Vision:**
- Custo: ~$3.00 para 3000 imagens (após free tier)
- Performance: 16.4% acurácia
- Custo por ponto percentual: $0.18

**Roboflow:**
- Custo: Similar a Google Vision
- Performance: 38.5% acurácia
- Custo por ponto percentual: $0.08
- Melhor custo-benefício

#### 4.4 Análise de Tempo

**Google Vision:**
- Tempo médio: 139.4s por simulação (100 imagens)
- ~1.4s por imagem
- Latência de rede alta

**Roboflow:**
- Tempo médio: 58.1s por simulação
- ~0.6s por imagem
- Mais rápido, possivelmente infraestrutura otimizada

#### 4.5 Limitações do Estudo

- Ambos os modelos têm performance baixa (acurácia < 40%)
- Dataset pode ter características específicas
- Apenas 2 classes avaliadas
- APIs genéricas vs necessidade de fine-tuning
- Tamanho limitado de dataset (100 imagens/simulação)

**Formato:** Markdown com análise crítica e interpretação

---

### 5. Conclusões

**Conteúdo:**

#### 5.1 Principais Achados

1. **Roboflow superior ao Google Vision** em todas as métricas (p < 0.001)
2. **Ambos têm performance insatisfatória** para uso em produção
3. **Viés forte para classe alegria** em ambos os modelos
4. **APIs genéricas não substituem modelos especializados** para tarefas específicas

#### 5.2 Recomendações

**Para Produção:**
- Não utilizar APIs genéricas sem validação
- Considerar fine-tuning de modelos foundation locais (YOLO11)
- Treinar CNN específica para o domínio
- Avaliar custo-benefício de cada abordagem

**Para Pesquisa:**
- Incluir YOLO11 na comparação quando disponível
- Testar fine-tuning dos modelos
- Avaliar aumento de dataset
- Considerar ensemble de modelos

#### 5.3 Trabalhos Futuros

1. Executar e incluir YOLO11 na análise
2. Implementar e avaliar CNN treinada do zero
3. Testar fine-tuning de modelos foundation
4. Expandir para mais classes de emoções
5. Avaliar data augmentation
6. Implementar ensemble de modelos

**Formato:** Markdown com bullet points claros

---

### 6. Referências

**Conteúdo:**
- Google Cloud Vision API Documentation
- Roboflow API Documentation
- Papers relevantes sobre detecção de emoções
- Metodologia estatística (Wilcoxon, Cohen's d)
- Dataset original (Kaggle)

**Formato:** Formato bibliográfico padrão

---

### 7. Apêndices

**Apêndice A: Código de Análise**
- Link para `generate_comparative_report.py`
- Link para `add_metrics.py`

**Apêndice B: Dados Brutos**
- Tabelas completas das 30 simulações
- CSV com todos os resultados

**Apêndice C: Configuração de Experimentos**
- Estrutura do dataset
- Parâmetros de execução
- Ambiente de software

---

## Artefatos a Criar

### Scripts Python

#### 1. `4_analysis/generate_full_report.py`
**Função:** Gerar relatório completo em Markdown

**Entrada:**
- CSVs de resultados dos modelos
- CSVs de testes estatísticos já gerados

**Saída:**
- `4_analysis/comparative_analysis_report.md`

**Funcionalidades:**
- Leitura de todos os CSVs
- Cálculo de estatísticas adicionais
- Formatação de tabelas em Markdown
- Inserção de referências a gráficos
- Geração automática de seções

#### 2. `4_analysis/generate_additional_plots.py`
**Função:** Criar gráficos adicionais

**Gráficos a criar:**
1. Gráfico de linha: Acurácia e F1-Score por simulação
2. Gráfico de barras: Tempo de processamento
3. Heatmap: Matriz de confusão agregada
4. Gráfico de dispersão: Acurácia vs Tempo

**Saída:**
- `4_analysis/figures/line_plot_accuracy_f1.png`
- `4_analysis/figures/time_comparison.png`
- `4_analysis/figures/confusion_matrix_heatmap.png`
- `4_analysis/figures/accuracy_vs_time.png`

#### 3. `4_analysis/statistical_analysis.py`
**Função:** Análises estatísticas adicionais

**Análises:**
- Intervalos de confiança (95%)
- Teste de normalidade (Shapiro-Wilk)
- Análise de variância (ANOVA quando YOLO11 disponível)
- Correlação entre métricas
- Análise de outliers

**Saída:**
- `4_analysis/statistical_summary.json`
- `4_analysis/confidence_intervals.csv`

### Documentos Markdown

#### 1. `4_analysis/comparative_analysis_report.md`
**Conteúdo:** Relatório completo seguindo estrutura acima

#### 2. `4_analysis/executive_summary.md`
**Conteúdo:** Resumo executivo (1-2 páginas)
- Principais achados
- Recomendações
- Próximos passos

### Notebooks Jupyter (opcional)

#### 1. `4_analysis/interactive_analysis.ipynb`
**Conteúdo:**
- Análise exploratória interativa
- Visualizações dinâmicas
- Experimentos adicionais
- Testes de hipóteses

---

## Ordem de Execução

### Fase 1: Preparação de Dados
1. Validar integridade dos CSVs existentes
2. Verificar se todas as métricas estão calculadas
3. Consolidar dados em estrutura única

### Fase 2: Análises Adicionais
1. Executar `statistical_analysis.py`
2. Executar `generate_additional_plots.py`
3. Revisar e validar resultados

### Fase 3: Geração do Relatório
1. Executar `generate_full_report.py`
2. Revisar relatório gerado
3. Ajustar formatação e narrativa
4. Adicionar interpretações manuais

### Fase 4: Documentação Complementar
1. Criar executive summary
2. Preparar apresentação (slides - opcional)
3. Documentar código de análise

### Fase 5: Validação
1. Revisar conclusões
2. Verificar consistência estatística
3. Validar reprodutibilidade
4. Preparar para inclusão de YOLO11 (futuro)

---

## Comandos Principais

```bash
# 1. Gerar análises estatísticas adicionais
python 4_analysis/statistical_analysis.py

# 2. Criar gráficos adicionais
python 4_analysis/generate_additional_plots.py

# 3. Gerar relatório completo
python 4_analysis/generate_full_report.py

# 4. Ver relatório
cat 4_analysis/comparative_analysis_report.md
```

---

## Critérios de Qualidade

### Científico
- Metodologia clara e reprodutível
- Análise estatística rigorosa
- Interpretação baseada em evidências
- Discussão de limitações

### Técnico
- Código limpo e documentado
- Resultados reproduzíveis
- Gráficos profissionais
- Formatação consistente

### Pedagógico
- Explicações detalhadas de conceitos
- Interpretação didática de resultados
- Contexto e motivação claros
- Recomendações práticas

---

## Observações Importantes

1. **Modularidade**: Scripts devem ser independentes mas interoperáveis
2. **Reprodutibilidade**: Usar seeds fixos, documentar versões
3. **Flexibilidade**: Código deve suportar inclusão de YOLO11 facilmente
4. **Documentação**: Cada função deve ter docstrings detalhadas
5. **Validação**: Incluir testes de sanidade nos scripts
6. **Versionamento**: Commitar incrementalmente no git

---

## Métricas de Sucesso

- [ ] Relatório completo e bem estruturado
- [ ] Todas as visualizações criadas e referenciadas
- [ ] Análise estatística rigorosa e bem documentada
- [ ] Código reproduzível e documentado
- [ ] Interpretação clara e baseada em dados
- [ ] Recomendações práticas e acionáveis
- [ ] Preparado para inclusão de novos modelos (YOLO11)

---

## Cronograma Estimado

- **Fase 1**: 30 minutos
- **Fase 2**: 1-2 horas
- **Fase 3**: 2-3 horas
- **Fase 4**: 1 hora
- **Fase 5**: 1 hora

**Total**: 5-7 horas de trabalho
