# Relatório de Análise - Classificação de Documentos com DocLayout-YOLO

**Data**: 25 de outubro de 2025
**Dataset**: RVL-CDIP (3 categorias)
**Modelo**: DocLayout-YOLO DocStructBench
**Amostras**: 30 documentos (10 por categoria)

---

## Sumário Executivo

### Performance Geral

| Métrica | Valor |
|---------|-------|
| **Acurácia Geral** | **23.33%** |
| Total de Documentos | 30 |
| Classificações Corretas | 7 |
| Classificações Incorretas | 23 |
| Taxa de Erro | 76.67% |

### Performance por Categoria

| Categoria | Acurácia | Corretos | Total |
|-----------|----------|----------|-------|
| **Email** | 20.0% | 2/10 | ⚠️ Muito baixa |
| **Advertisement** | 50.0% | 5/10 | ⚠️ Abaixo do esperado |
| **Scientific Publication** | **0.0%** | 0/10 | ❌ **CRÍTICO** |

---

## Análise Detalhada

### 1. Matriz de Confusão

```
                            PREDITO
                    Email    Advertisement    Scientific_Pub
VERDADEIRO
Email                2           8                  0
Advertisement        5           5                  0
Scientific_Pub       2           8                  0
```

**Observações**:
- **Scientific Publication NUNCA é predita** (0 ocorrências)
- 70% das predições são "advertisement" (21/30)
- 30% das predições são "email" (9/30)
- O classificador está completamente enviesado para apenas 2 categorias

### 2. Padrões de Erro

**Confusões Mais Frequentes**:

1. **Email → Advertisement**: 8 casos (80% dos emails)
   - Emails sendo confundidos com anúncios

2. **Scientific Publication → Advertisement**: 8 casos (80% das publicações)
   - Publicações científicas sendo confundidas com anúncios

3. **Advertisement → Email**: 5 casos (50% dos anúncios)
   - Anúncios sendo confundidos com emails

4. **Scientific Publication → Email**: 2 casos (20% das publicações)
   - Publicações sendo confundidas com emails

**Taxa de Erro por Categoria**:
- Email: 80.0% (8 erros em 10)
- Advertisement: 50.0% (5 erros em 10)
- Scientific Publication: **100.0%** (10 erros em 10) ❌

---

## Diagnóstico do Problema

### Problema Principal Identificado

O modelo DocLayout-YOLO está detectando classes com **nomes diferentes** dos esperados pelo código de classificação.

#### Classes Esperadas vs Detectadas

| Esperado | Detectado? | Status |
|----------|------------|--------|
| `equation` | ❌ NÃO | Nunca detectada |
| `reference` | ❌ NÃO | Nunca detectada |
| `text` | ❌ NÃO | Detecta "plain text" |
| `table` | ✅ SIM | 4 ocorrências |
| `figure` | ✅ SIM | 19 ocorrências |
| `title` | ✅ SIM | 42 ocorrências |

#### Classes Realmente Detectadas pelo Modelo

| Classe | Ocorrências | Observação |
|--------|-------------|------------|
| `plain text` | 180 | ⚠️ Código espera "text" |
| `abandon` | 86 | ⚠️ Classe inesperada (noise?) |
| `title` | 42 | ✅ Correto |
| `figure` | 19 | ✅ Correto |
| `figure_caption` | 6 | ⚠️ Código não mapeia |
| `table` | 4 | ✅ Correto |
| `isolate_formula` | 4 | ⚠️ Código espera "equation" |
| `table_footnote` | 1 | ⚠️ Código não mapeia |

### Consequências do Problema

**9 Features Estão Sempre Zeradas**:
- `num_texts` = 0 (deveria contar "plain text")
- `num_equations` = 0 (deveria contar "isolate_formula")
- `num_captions` = 0 (deveria contar "figure_caption")
- `num_headers` = 0
- `num_footers` = 0
- `num_references` = 0
- `num_lists` = 0
- `has_equations` = 0
- `has_references` = 0

**Resultado**: As heurísticas de classificação não funcionam porque:
1. Não detecta texto (`text` vs `plain text`)
2. Não detecta equações (`equation` vs `isolate_formula`)
3. Não detecta referências (classe não existe no modelo)
4. Features críticas para identificar publicações científicas estão zeradas

### Distribuição de Detecções por Categoria Verdadeira

#### Advertisement
- `abandon`: 16 (ruído/artefatos)
- `figure`: 14 ✅ (esperado)
- `plain text`: 8
- `title`: 2

#### Email
- `plain text`: 93 ✅ (esperado)
- `abandon`: 31 (ruído)
- `title`: 19
- `table`: 3
- `figure`: 1

#### Scientific Publication
- `plain text`: 79 ✅
- `abandon`: 39 (ruído)
- `title`: 21 ✅
- `figure_caption`: 5 ✅ (mas não mapeado)
- `figure`: 4 ✅
- `isolate_formula`: 3 ✅ (equações! mas não mapeado como "equation")
- `table`: 1
- `table_footnote`: 1

**Observação Importante**: O modelo ESTÁ detectando elementos característicos de publicações científicas (`isolate_formula`, `figure_caption`), mas o código não está mapeando corretamente!

---

## Análise de Desempenho

### Por que Advertisement tem 50% de acurácia?

**Hipótese**: Anúncios têm muitas figuras, o que está sendo detectado corretamente:
- 14 figuras detectadas em 10 documentos
- Características visuais distintas

### Por que Email tem apenas 20% de acurácia?

**Hipótese**: Emails têm muito texto simples:
- 93 detecções de "plain text" (mas código não conta)
- Sem características visuais distintivas
- Confundido com advertisements (que também têm texto)

### Por que Scientific Publication tem 0% de acurácia?

**Causa Raiz Identificada**:
1. Código procura por `num_equations` (sempre 0)
2. Código procura por `num_references` (sempre 0)
3. Modelo detecta `isolate_formula` (não mapeado)
4. Modelo não detecta referências
5. Heurísticas falham completamente

---

## Recomendações

### 1. Correção Imediata: Mapear Classes (CRÍTICO)

**Prioridade**: 🔴 ALTA

Criar mapeamento de classes em `analyze_layout.py`:

```python
# Adicionar no início de analyze_document_layout()
CLASS_MAPPING = {
    'plain text': 'text',
    'isolate_formula': 'equation',
    'figure_caption': 'caption',
    'table_footnote': 'caption',
    'abandon': None,  # Ignorar (ruído)
    # Manter os que já existem
    'title': 'title',
    'figure': 'figure',
    'table': 'table',
}

# Aplicar mapeamento ao processar detecções
mapped_class = CLASS_MAPPING.get(class_name, class_name)
if mapped_class is None:
    continue  # Pular ruído
```

**Impacto Esperado**: Acurácia deve subir de 23% para ~60-70%

### 2. Ajustar Heurísticas (ALTA)

**Prioridade**: 🟡 MÉDIA

Após mapear classes, ajustar pesos em `classify_documents.py`:

```python
# Para Scientific Publication, usar as classes realmente detectadas
if num_equations >= 1:  # Agora vai detectar isolate_formula
    scores['scientific_publication'] += 5.0

if num_captions >= 1:  # figure_caption
    scores['scientific_publication'] += 2.0

# Adicionar peso para densidade de texto alta
if text_density >= 0.5:  # plain text density
    scores['scientific_publication'] += 3.0
```

### 3. Tratar Classe "abandon" (MÉDIA)

**Prioridade**: 🟢 BAIXA

A classe "abandon" aparece 86 vezes. Investigar:
- São artefatos de escaneamento?
- São elementos fora do layout principal?
- Devem ser ignorados ou contabilizados?

**Ação**: Analisar visualmente algumas imagens anotadas

### 4. Machine Learning (RECOMENDADO)

**Prioridade**: 🟡 MÉDIA-ALTA

Após corrigir o mapeamento, treinar um classificador supervisionado:

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

# Features já extraídas estão disponíveis
X = df[['num_titles', 'num_figures', 'num_tables',
        'num_equations', 'plain text_density', ...]]
y = df['true_category']

# Random Forest aprende automaticamente
clf = RandomForestClassifier(n_estimators=100)
scores = cross_val_score(clf, X, y, cv=5)
print(f"Acurácia média: {scores.mean():.2f}")
```

**Vantagens**:
- Aprende padrões automaticamente
- Não precisa ajustar heurísticas manualmente
- Provavelmente 70-85% de acurácia

### 5. Expandir Dataset (BAIXA)

Após corrigir problemas, testar com mais amostras:
- 50-100 documentos por categoria
- Validação mais robusta
- Identificar casos edge

---

## Visualizações Geradas

Os seguintes gráficos foram salvos em `results/analysis/`:

1. **confusion_matrix.png**: Matriz de confusão com heatmap
2. **accuracy_by_category.png**: Gráfico de barras de acurácia
3. **feature_distributions.png**: Histogramas de features por categoria

### Insights das Visualizações

**Matriz de Confusão**:
- Diagonal fraca (poucas classificações corretas)
- Concentração em "advertisement" (coluna do meio)
- Linha de scientific_publication completamente errada

**Acurácia por Categoria**:
- Advertisement é a única acima de random (50%)
- Email e Scientific Publication abaixo de random
- Linha azul mostra média geral em 23%

**Distribuição de Features**:
- Todas as features de equações/referências estão zeradas
- num_titles é a única com alguma variação
- Confirma visualmente o problema de mapeamento

---

## Conclusões

### Principais Achados

1. **Problema Crítico Identificado**: Incompatibilidade entre nomes de classes do modelo e código
2. **Solução Clara**: Implementar mapeamento de classes
3. **Viabilidade**: O modelo ESTÁ detectando elementos úteis (isolate_formula, figure_caption)
4. **Potencial**: Com correções, acurácia pode chegar a 60-80%

### Status Atual

- ❌ Sistema não está funcional (23% de acurácia)
- ✅ Diagnóstico completo realizado
- ✅ Solução identificada
- 🔧 Correções necessárias

### Próximos Passos

**Curto Prazo** (1-2 horas):
1. Implementar mapeamento de classes
2. Re-executar classificação
3. Validar melhoria

**Médio Prazo** (1 dia):
1. Ajustar heurísticas com novos dados
2. Testar com mais amostras
3. Comparar com YOLO11-cls

**Longo Prazo** (1 semana):
1. Treinar classificador ML
2. Ensemble de múltiplos modelos
3. Deploy em produção

---

## Apêndice: Comandos Úteis

### Re-executar Classificação Após Correções

```bash
# 1. Limpar resultados antigos
rm -rf results/

# 2. Re-executar classificação
python classify_documents.py --dataset-path ../rvlp/data/test --num-samples 10

# 3. Analisar novos resultados
python analyze_results.py
```

### Análise de Documento Individual

```bash
# Ver análise de um documento específico
cat results/scientific_publication/10142638_analysis.json | jq .

# Ver imagem anotada
open results/scientific_publication/10142638_annotated.jpg
```

### Explorar Features

```bash
# Carregar CSV de features em Python
import pandas as pd
df = pd.read_csv('results/analysis/features_data.csv')
print(df.describe())
```

---

**Relatório gerado por**: `analyze_results.py`
**Documentação**: Ver `README.md` e `QUICKSTART.md`
