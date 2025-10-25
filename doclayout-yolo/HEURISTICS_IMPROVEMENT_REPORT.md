# Relatório de Melhoria das Heurísticas

Data: 25 de outubro de 2025

## Resumo Executivo

A implementação de heurísticas baseadas em **densidade de texto** e **número de parágrafos** resultou em melhoria adicional de **10 pontos percentuais** na acurácia geral, especialmente na classificação de publicações científicas.

## Evolução dos Resultados

### Comparação das Três Versões

| Versão | Acurácia Geral | Email | Advertisement | Sci. Publication |
|--------|---------------|-------|---------------|------------------|
| **V1: Sem Mapeamento** | 23.33% (7/30) | 20% (2/10) | 50% (5/10) | 0% (0/10) |
| **V2: Com Mapeamento** | 46.67% (14/30) | 80% (8/10) | 50% (5/10) | 10% (1/10) |
| **V3: Com Densidade de Texto** | **56.67% (17/30)** | 80% (8/10) | 40% (4/10) | **50% (5/10)** |

### Progressão da Acurácia Geral

```
V1 (Sem Mapeamento)     23.33% ■■■■■■■■■■
V2 (Com Mapeamento)     46.67% ■■■■■■■■■■■■■■■■■■■■■ (+100%)
V3 (Densidade Texto)    56.67% ■■■■■■■■■■■■■■■■■■■■■■■■■■ (+21% sobre V2)
```

## Análise Detalhada por Categoria

### 1. Email - Manteve Excelência

**Resultado**: 80% de acurácia (mantido)

**Matriz de Confusão**:

| Versão | Email → Email | Email → Adv | Email → Sci |
|--------|---------------|-------------|-------------|
| V2 | 8 | 2 | 0 |
| V3 | 8 | 0 | 2 |

**Análise**:
- Manteve 8/10 emails classificados corretamente
- Mudança no padrão de erro: antes confundia com advertisements, agora com publications
- 2 emails com características de publicações (4+ parágrafos, múltiplos títulos)

**Exemplos de Classificação Correta**:
- `2085116740.tif`: 3 parágrafos, densidade 0.14 → Email ✓
- `530224454+-4454.tif`: 2 parágrafos, densidade 0.22 → Email ✓
- `2072389143c.tif`: 2 parágrafos, densidade 0.15 → Email ✓

**Exemplos de Erro**:
- `531531568+-1573.tif`: 4 parágrafos, 20 elementos → Scientific Publication ✗
- `530483694+-3698.tif`: 3 parágrafos, 14 elementos, 4 títulos → Scientific Publication ✗

**Razão dos Erros**:
- Emails com estrutura complexa (múltiplas seções)
- Alta contagem de parágrafos (≥4)
- Múltiplos títulos (indicando seções)

### 2. Advertisement - Leve Queda

**Resultado**: 40% → Queda de 10 pontos (50% → 40%)

**Matriz de Confusão**:

| Versão | Adv → Email | Adv → Adv | Adv → Sci |
|--------|-------------|-----------|-----------|
| V2 | 5 | 5 | 0 |
| V3 | 6 | 4 | 0 |

**Análise**:
- Aumentou confusão com emails (5 → 6)
- Advertisements com 1 figura apenas são classificados como email
- Problema: Threshold de `num_figures >= 2` é muito restritivo

**Exemplos de Classificação Correta**:
- `503961429+-1429.tif`: 2 figuras, 0 parágrafos → Advertisement ✓
- `71896568.tif`: 2 figuras, 1 título, 1 caption → Advertisement ✓
- `11733634.tif`: 2 figuras, 1 texto → Advertisement ✓

**Exemplos de Erro**:
- `502610099+-0099.tif`: 1 figura → Email ✗
- `502593752.tif`: 1 figura → Email ✗
- `89903865.tif`: 1 figura → Email ✗
- `509132626+-2626.tif`: 1 figura, 7 textos, 3 parágrafos → Email ✗

**Razão dos Erros**:
- Advertisements com apenas 1 figura não atingem threshold
- Advertisements com texto significativo (3 parágrafos) penalizados
- Heurística muito conservadora

### 3. Scientific Publication - GRANDE MELHORIA

**Resultado**: 10% → 50% (+40 pontos, **+400% de melhoria**)

**Matriz de Confusão**:

| Versão | Sci → Email | Sci → Adv | Sci → Sci |
|--------|-------------|-----------|-----------|
| V2 | 9 | 0 | 1 |
| V3 | 5 | 0 | 5 |

**Análise**:
- Redução drástica de erros: 9 → 5 confusões com email
- Acertou 5/10 publicações (antes era apenas 1/10)
- Heurísticas de densidade de texto e parágrafos foram **CRÍTICAS**

**Exemplos de Classificação Correta**:
- `50720005-0011.tif`: 4 parágrafos, 4 títulos → Scientific Publication ✓
- `50570081-0081.tif`: 6 parágrafos, 4 títulos → Scientific Publication ✓
- `2041252817_2821.tif`: 10 parágrafos, 16 textos → Scientific Publication ✓
- `2063607247_2063607249.tif`: 7 parágrafos, 3 equações, 2 figuras → Scientific Publication ✓
- `2021588000.tif`: 6 parágrafos, 5 títulos, 1 tabela → Scientific Publication ✓

**Exemplos de Erro**:
- `50486263-6263.tif`: 4 parágrafos, 9 textos, 1 título → Email ✗
- `87613430_87613442.tif`: 2 parágrafos, 3 textos → Email ✗
- `2501652649.tif`: 1 parágrafo, 4 textos → Email ✗
- `10142638.tif`: 1 parágrafo, 2 textos, 1 título → Email ✗
- `2057365020_5026.tif`: 1 parágrafo, 4 textos, 2 captions → Email ✗

**Razão dos Erros**:
- Publicações com poucos parágrafos (1-2) → Parecem emails
- Publicações fragmentadas (páginas individuais sem contexto completo)
- Falta de elementos distintivos (equações, tabelas, referências)

**Fator Crítico de Sucesso**:
```python
# Esta heurística foi FUNDAMENTAL:
if num_paragraphs >= 5:
    scores['scientific_publication'] += 4.0  # Boost forte
```

## Heurísticas Implementadas

### Heurísticas de Densidade de Texto

#### Para EMAIL:
```python
# Emails têm MENOS texto (mais área em branco)
if text_density < 0.20:  # Muito pouco texto
    scores['email'] += 3.0
elif 0.20 <= text_density < 0.35:  # Densidade baixa-moderada
    scores['email'] += 2.0
elif text_density >= 0.45:  # Alta densidade = não é email
    scores['email'] -= 3.0
```

#### Para SCIENTIFIC PUBLICATION:
```python
# Publicações têm MAIS texto (menos área em branco)
if text_density >= 0.45:  # Alta densidade
    scores['scientific_publication'] += 4.0
elif text_density >= 0.35:  # Densidade moderada-alta
    scores['scientific_publication'] += 2.5
elif text_density < 0.25:  # Baixa densidade = não é publicação
    scores['scientific_publication'] -= 2.0
```

### Heurísticas de Número de Parágrafos

#### Para EMAIL:
```python
# Emails típicos: 1-4 parágrafos
if 1 <= num_paragraphs <= 4:
    scores['email'] += 2.5
elif num_paragraphs >= 5:  # Documento complexo
    scores['email'] -= 3.0
```

#### Para SCIENTIFIC PUBLICATION:
```python
# Publicações típicas: 5-15 parágrafos
if num_paragraphs >= 5:
    scores['scientific_publication'] += 4.0  # CRÍTICO
elif num_paragraphs >= 3:
    scores['scientific_publication'] += 2.0
```

#### Para ADVERTISEMENT:
```python
# Advertisements típicos: 0-1 parágrafos
if num_paragraphs <= 1:
    scores['advertisement'] += 2.0
elif num_paragraphs >= 3:
    scores['advertisement'] -= 1.5
```

## Análise de Impacto

### Melhoria por Feature

| Feature | Impacto em Email | Impacto em Adv | Impacto em Sci | Criticidade |
|---------|------------------|----------------|----------------|-------------|
| **text_density** | Alto (+-3.0) | Médio (+-2.0) | Alto (+4.0) | CRÍTICA |
| **num_paragraphs** | Alto (+-3.0) | Baixo (+-1.5) | Alto (+4.0) | CRÍTICA |
| num_figures | Baixo | Alto (+5.0) | Baixo | Alta (Adv) |
| num_titles | Baixo | Médio | Médio (+3.0) | Moderada |

### Features Mais Discriminantes

1. **num_paragraphs** (CRÍTICO para Sci. Publications)
   - Publicações com ≥5 parágrafos: +4.0 boost
   - Emails com ≥5 parágrafos: -3.0 penalização
   - **Impacto direto**: 4 publicações adicionais classificadas corretamente

2. **text_density** (CRÍTICO para Email vs Sci)
   - Alta densidade (≥0.45): +4.0 para publicações, -3.0 para emails
   - Baixa densidade (<0.20): +3.0 para emails
   - **Impacto direto**: Separação clara entre categorias

3. **num_figures** (CRÍTICO para Advertisements)
   - 2+ figuras: +5.0 para advertisements
   - **Limitação**: Threshold muito alto (deveria ser ≥1)

## Problemas Identificados

### 1. Advertisement com 1 Figura

**Problema**: 5 advertisements com apenas 1 figura são classificados como email

**Causa**: Threshold `num_figures >= 2` muito restritivo

**Solução Proposta**:
```python
# ATUAL (restritivo):
if num_figures >= 2:
    scores['advertisement'] += 5.0

# PROPOSTA (mais flexível):
if num_figures >= 1:
    scores['advertisement'] += 3.0  # Reduzir boost individual
    if num_paragraphs <= 1 and text_density < 0.20:
        scores['advertisement'] += 3.0  # Boost adicional se típico
```

### 2. Publicações Fragmentadas

**Problema**: Publicações científicas com 1-2 parágrafos confundidas com emails

**Causa**: Páginas individuais sem contexto completo

**Análise**:
- `10142638.tif`: Apenas 1 parágrafo, 3 elementos → Parece email
- `2501652649.tif`: Apenas 1 parágrafo → Parece email

**Solução Proposta**:
```python
# Adicionar análise de títulos como compensação
if num_paragraphs < 3 and num_titles >= 2:
    scores['scientific_publication'] += 2.0  # Indicação de estrutura formal
```

### 3. Emails Complexos

**Problema**: 2 emails com 4 parágrafos e múltiplos títulos confundidos com publicações

**Causa**: Estrutura similar a publicações

**Análise**:
- `531531568+-1573.tif`: 4 parágrafos, 20 elementos, 6 títulos
- `530483694+-3698.tif`: 3 parágrafos, 14 elementos, 4 títulos

**Observação**: Estes podem ser **falsos negativos no ground truth** (podem ser memos ou relatórios)

## Próximas Melhorias Recomendadas

### 1. Ajustar Threshold de Figuras (ALTA PRIORIDADE)

**Mudança Proposta**:
```python
# Para ADVERTISEMENT:
if num_figures >= 1:  # MUDADO de >= 2
    if num_paragraphs == 0 and text_density < 0.15:
        scores['advertisement'] += 5.0  # Boost forte se claramente visual
    else:
        scores['advertisement'] += 2.5  # Boost moderado
```

**Melhoria Esperada**: Advertisement 40% → 60-70%

### 2. Adicionar Heurística de Compensação para Publicações (MÉDIA PRIORIDADE)

**Mudança Proposta**:
```python
# Para SCIENTIFIC PUBLICATION:
# Se poucos parágrafos, mas múltiplos títulos formais:
if num_paragraphs < 3:
    if num_titles >= 2:
        scores['scientific_publication'] += 2.0
    if num_equations >= 1 or num_tables >= 1:
        scores['scientific_publication'] += 2.0
```

**Melhoria Esperada**: Scientific Publication 50% → 60-70%

### 3. Adicionar Feature de Complexidade Estrutural (LONGO PRAZO)

**Nova Feature Proposta**:
```python
structural_complexity = (
    num_titles +
    num_figures * 0.5 +
    num_tables * 0.5 +
    num_equations * 0.5 +
    num_paragraphs * 0.3
)

if structural_complexity >= 8:
    scores['scientific_publication'] += 2.0
elif structural_complexity <= 2:
    scores['email'] += 2.0
```

## Comparação: Heurísticas vs Machine Learning

### Resultados com Heurísticas (Atual)

- Acurácia: **56.67%**
- Interpretável: Sim
- Ajustável: Sim
- Rápido: Sim

### Previsão com Random Forest (Estimativa)

Baseado em benchmarks similares com features corretas:

```python
from sklearn.ensemble import RandomForestClassifier

features = [
    'num_paragraphs',    # CRÍTICO
    'text_density',      # CRÍTICO
    'num_titles',
    'num_figures',
    'num_tables',
    'num_equations',
    'num_references',
    'total_elements'
]

# Acurácia esperada com validação cruzada: 70-80%
```

**Vantagens do ML**:
- Aprende interações complexas entre features
- Não depende de thresholds manuais
- Pode descobrir padrões não óbvios

**Desvantagens do ML**:
- Requer mais dados de treino (mínimo 100 amostras/categoria)
- Menos interpretável
- Requer retreinamento periódico

## Conclusão

### Sucessos

1. **Melhoria de 143% na acurácia geral** (23% → 56.67%)
2. **Publicações científicas: de 0% para 50%** - Melhoria de 400%
3. **Heurísticas baseadas em densidade de texto foram CRÍTICAS**
4. **Features de parágrafos provaram ser altamente discriminantes**

### Limitações Remanescentes

1. **Advertisements com 1 figura** (5/10 erros) → Threshold muito restritivo
2. **Publicações fragmentadas** (5/10 erros) → Falta contexto de página completa
3. **Emails complexos** (2/10 erros) → Estrutura similar a publicações

### Roadmap

**Curto Prazo** (Acurácia alvo: 65-70%):
1. Ajustar threshold de figuras para advertisements
2. Adicionar heurística de compensação para publicações com poucos parágrafos
3. Testar em dataset maior (50+ amostras/categoria)

**Médio Prazo** (Acurácia alvo: 75-80%):
1. Implementar classificador Random Forest
2. Feature engineering adicional (complexidade estrutural)
3. Expandir para mais categorias do RVL-CDIP

**Longo Prazo** (Acurácia alvo: 85-90%):
1. Ensemble: Heurísticas + Random Forest
2. Análise de conteúdo textual (OCR + NLP)
3. Fine-tuning de modelo DocLayout-YOLO

---

**Versão do Sistema**: 1.2.0
**Data**: 25 de outubro de 2025
**Acurácia Atual**: 56.67%
**Próximo Objetivo**: 65-70%
