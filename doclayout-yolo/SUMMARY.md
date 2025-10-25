# Sumário: Evolução do Sistema de Classificação DocLayout-YOLO

Data: 25 de outubro de 2025

## Evolução da Acurácia

### Progresso Geral

```
Versão 1.0 (Sem Mapeamento)      23.33% ████████░░░░░░░░░░░░░░░░░░░░░░░░
Versão 1.1 (Com Mapeamento)      46.67% ████████████████░░░░░░░░░░░░░░░░
Versão 1.2 (Densidade Texto)     56.67% ███████████████████░░░░░░░░░░░░░

Melhoria Total: +33.34 pontos (+143%)
```

### Evolução por Categoria

#### Email
```
V1.0: 20%  ██████░░░░░░░░░░░░░░░░░░░░░░░░
V1.1: 80%  ████████████████████████░░░░░░
V1.2: 80%  ████████████████████████░░░░░░  ← ESTÁVEL
```

#### Advertisement
```
V1.0: 50%  ███████████████░░░░░░░░░░░░░░░
V1.1: 50%  ███████████████░░░░░░░░░░░░░░░
V1.2: 40%  ████████████░░░░░░░░░░░░░░░░░░  ← LEVE QUEDA
```

#### Scientific Publication
```
V1.0:  0%  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
V1.1: 10%  ███░░░░░░░░░░░░░░░░░░░░░░░░░░░
V1.2: 50%  ███████████████░░░░░░░░░░░░░░░  ← GRANDE MELHORIA
```

## Mudanças Implementadas

### Versão 1.0 → 1.1: Mapeamento de Classes

**Problema Identificado**: Classes do modelo não correspondiam às esperadas pelo código

**Solução**: Implementar CLASS_MAPPING dictionary

```python
CLASS_MAPPING = {
    'plain text': 'text',           # CRÍTICO
    'isolate_formula': 'equation',
    'figure_caption': 'caption',
    'abandon': None,                # Filtrar ruído
    ...
}
```

**Resultado**: +23.34 pontos (100% de melhoria)

**Impacto por Categoria**:
- Email: +60 pontos (20% → 80%)
- Advertisement: 0 pontos (50% → 50%)
- Scientific Publication: +10 pontos (0% → 10%)

---

### Versão 1.1 → 1.2: Densidade de Texto e Parágrafos

**Problema Identificado**: Publicações científicas confundidas com emails

**Solução**: Heurísticas baseadas em densidade texto/área em branco

**Conceitos Implementados**:

1. **Emails têm MENOS texto** (mais área vazia)
   ```python
   if text_density < 0.20:
       scores['email'] += 3.0
   elif text_density >= 0.45:
       scores['email'] -= 3.0  # Penalizar alta densidade
   ```

2. **Publicações têm MAIS texto** (menos área vazia)
   ```python
   if text_density >= 0.45:
       scores['scientific_publication'] += 4.0
   ```

3. **Parágrafos como feature discriminante**
   ```python
   # Emails: 1-4 parágrafos
   if 1 <= num_paragraphs <= 4:
       scores['email'] += 2.5

   # Publicações: 5+ parágrafos
   if num_paragraphs >= 5:
       scores['scientific_publication'] += 4.0  # CRÍTICO
   ```

**Resultado**: +10 pontos (46.67% → 56.67%)

**Impacto por Categoria**:
- Email: 0 pontos (80% → 80%)
- Advertisement: -10 pontos (50% → 40%)
- Scientific Publication: **+40 pontos (10% → 50%)** ← SUCESSO

---

## Análise de Erros por Versão

### Versão 1.2 (Atual)

#### Classificações Corretas: 17/30 (56.67%)

**Email**: 8/10 corretas
- Acertos: Emails com 1-4 parágrafos, baixa densidade
- Erros (2): Emails complexos com 4+ parágrafos, múltiplos títulos

**Advertisement**: 4/10 corretas
- Acertos: Advertisements com 2+ figuras, 0-1 parágrafos
- Erros (6): Advertisements com apenas 1 figura

**Scientific Publication**: 5/10 corretas
- Acertos: Publicações com 5+ parágrafos, múltiplos títulos
- Erros (5): Publicações fragmentadas (1-2 parágrafos apenas)

### Matriz de Confusão (V1.2)

```
                    │ Predito →  │ Email │ Adv │ Sci │
────────────────────┼────────────┼───────┼─────┼─────┤
Verdadeiro ↓        │            │       │     │     │
                    │            │       │     │     │
Email               │            │   8   │  0  │  2  │
Advertisement       │            │   6   │  4  │  0  │
Sci. Publication    │            │   5   │  0  │  5  │
```

**Principais Confusões**:
1. **Advertisement → Email**: 6 casos (advertisements com 1 figura)
2. **Sci. Publication → Email**: 5 casos (publicações com poucos parágrafos)
3. **Email → Sci. Publication**: 2 casos (emails complexos)

---

## Features Mais Importantes

Ranking de importância para classificação:

| Rank | Feature | Importância | Categorias Afetadas |
|------|---------|-------------|---------------------|
| 1 | **text_density** | CRÍTICA | Email vs Sci. Publication |
| 2 | **num_paragraphs** | CRÍTICA | Email vs Sci. Publication |
| 3 | **num_figures** | ALTA | Advertisement |
| 4 | **num_titles** | MODERADA | Sci. Publication |
| 5 | **num_equations** | MODERADA | Sci. Publication |
| 6 | **num_tables** | MODERADA | Sci. Publication |
| 7 | **num_references** | BAIXA | Sci. Publication |
| 8 | **total_elements** | BAIXA | Todas |

### Análise de Impacto

**text_density**:
- Range: 0.0 - 1.0 (proporção de área coberta por texto)
- Email médio: ~0.20 (80% área vazia)
- Publicação média: ~0.45 (55% área vazia)
- **Separabilidade**: EXCELENTE

**num_paragraphs**:
- Range: 0 - 15+
- Email médio: 2-3 parágrafos
- Advertisement médio: 0-1 parágrafos
- Publicação média: 6-8 parágrafos
- **Separabilidade**: EXCELENTE

**num_figures**:
- Range: 0 - 5+
- Email médio: 0-1 figuras
- Advertisement médio: 1-3 figuras
- Publicação média: 1-2 figuras
- **Separabilidade**: MODERADA (overlap entre categorias)

---

## Problemas Remanescentes

### 1. Advertisements com 1 Figura (ALTA PRIORIDADE)

**Problema**: 6/10 advertisements classificados como email

**Causa**: Threshold `num_figures >= 2` muito restritivo

**Exemplos**:
- `502610099+-0099.tif`: 1 figura → Email (ERRO)
- `502593752.tif`: 1 figura → Email (ERRO)
- `89903865.tif`: 1 figura → Email (ERRO)

**Solução Proposta**:
```python
# Flexibilizar threshold
if num_figures >= 1:
    if num_paragraphs == 0 and text_density < 0.15:
        scores['advertisement'] += 5.0
```

**Melhoria Esperada**: Advertisement 40% → 60-70%

---

### 2. Publicações Fragmentadas (MÉDIA PRIORIDADE)

**Problema**: 5/10 publicações classificadas como email

**Causa**: Páginas individuais com poucos parágrafos (1-2)

**Exemplos**:
- `10142638.tif`: 1 parágrafo, 3 elementos → Email (ERRO)
- `2501652649.tif`: 1 parágrafo, 4 textos → Email (ERRO)
- `2057365020_5026.tif`: 1 parágrafo, 4 textos, 2 captions → Email (ERRO)

**Solução Proposta**:
```python
# Adicionar compensação por elementos formais
if num_paragraphs < 3:
    if num_titles >= 2 or num_equations >= 1 or num_tables >= 1:
        scores['scientific_publication'] += 2.0
```

**Melhoria Esperada**: Scientific Publication 50% → 65-70%

---

### 3. Emails Complexos (BAIXA PRIORIDADE)

**Problema**: 2/10 emails classificados como publicações

**Causa**: Estrutura formal similar (4+ parágrafos, múltiplos títulos)

**Exemplos**:
- `531531568+-1573.tif`: 4 parágrafos, 20 elementos, 6 títulos → Sci. Pub. (ERRO)
- `530483694+-3698.tif`: 3 parágrafos, 14 elementos, 4 títulos → Sci. Pub. (ERRO)

**Observação**: Podem ser falsos negativos no ground truth (memos/relatórios)

**Solução Proposta**: Análise de conteúdo textual (OCR) para confirmar

---

## Próximos Passos

### Curto Prazo (Acurácia alvo: 65-70%)

1. **Ajustar threshold de figuras** ← ALTA PRIORIDADE
   - Mudança simples, alto impacto em advertisements
   - Estimativa: 1 hora de trabalho
   - Ganho esperado: +10-15 pontos em advertisements

2. **Adicionar compensação para publicações fragmentadas**
   - Usar títulos/equações/tabelas como features secundárias
   - Estimativa: 2 horas de trabalho
   - Ganho esperado: +10-15 pontos em publications

3. **Testar em dataset maior**
   - 50+ amostras por categoria
   - Validar estabilidade das heurísticas
   - Estimativa: 3 horas de trabalho

**Total estimado**: 6 horas de trabalho
**Acurácia esperada**: 65-70%

---

### Médio Prazo (Acurácia alvo: 75-80%)

1. **Implementar Random Forest**
   - Treinar com features extraídas
   - Validação cruzada 5-fold
   - Feature importance analysis
   - Estimativa: 1 dia de trabalho

2. **Feature engineering adicional**
   - Complexidade estrutural
   - Razão títulos/parágrafos
   - Distribuição espacial de elementos
   - Estimativa: 1 dia de trabalho

3. **Expandir para mais categorias**
   - Adicionar 3-4 categorias do RVL-CDIP
   - Ajustar heurísticas
   - Estimativa: 2 dias de trabalho

**Total estimado**: 4 dias de trabalho
**Acurácia esperada**: 75-80%

---

### Longo Prazo (Acurácia alvo: 85-90%)

1. **Ensemble de modelos**
   - Combinar heurísticas + Random Forest
   - Votação ponderada ou stacking
   - Estimativa: 3 dias de trabalho

2. **Análise de conteúdo textual**
   - OCR + análise de palavras-chave
   - Detecção de estrutura semântica
   - Estimativa: 1 semana de trabalho

3. **Fine-tuning DocLayout-YOLO**
   - Retreinar modelo em RVL-CDIP
   - Transfer learning
   - Estimativa: 2 semanas de trabalho

**Total estimado**: 3-4 semanas de trabalho
**Acurácia esperada**: 85-90%

---

## Arquivos Gerados

### Relatórios
- `SUMMARY.md` - Este resumo (você está aqui)
- `HEURISTICS_IMPROVEMENT_REPORT.md` - Análise detalhada V1.1 → V1.2
- `COMPARISON_REPORT.md` - Comparação V1.0 → V1.1
- `CHANGELOG.md` - Histórico de versões

### Backups de Resultados
- `results_old_nomapping/` - Resultados V1.0 (sem mapeamento)
- `results_old_basic_heuristics/` - Resultados V1.1 (com mapeamento)
- `results/` - Resultados V1.2 (densidade texto) ← ATUAL

### Scripts
- `classify_documents.py` - Pipeline de classificação
- `analyze_layout.py` - Análise de layout + detecção de parágrafos
- `compare_results.py` - Script de comparação de versões
- `test_paragraph_detection.py` - Teste de detecção de parágrafos

---

## Conclusão

### Sucessos

1. Melhoria de **143% na acurácia geral** (23% → 57%)
2. **Email**: Acurácia excelente (80%)
3. **Scientific Publications**: Melhorou de 0% para 50% (+400%)
4. Implementação de features críticas:
   - `text_density`: Razão texto/área em branco
   - `num_paragraphs`: Contagem de parágrafos

### Desafios Remanescentes

1. **Advertisements**: Threshold de figuras muito restritivo (40% acurácia)
2. **Scientific Publications**: Publicações fragmentadas difíceis (50% acurácia)
3. **Heurísticas**: Ainda há espaço para ajustes finos

### Lições Aprendidas

1. **Mapeamento de classes é CRÍTICO**
   - Verificar sempre a correspondência modelo ↔ código
   - Preservar classes originais para debugging

2. **Features espaciais são poderosas**
   - Densidade de texto captura diferença estrutural
   - Número de parágrafos é altamente discriminante

3. **Threshold tuning é importante**
   - Valores muito restritivos criam falsos negativos
   - Testar em amostras diversas antes de finalizar

4. **Heurísticas vs ML**
   - Heurísticas: rápidas, interpretáveis, bom ponto de partida
   - ML: necessário para acurácia >70%

---

**Versão do Sistema**: 1.2.0
**Data**: 25 de outubro de 2025
**Acurácia Atual**: 56.67%
**Próximo Objetivo**: 65-70% (curto prazo)
**Objetivo Final**: 85-90% (longo prazo)

---

Para mais detalhes, consulte:
- `HEURISTICS_IMPROVEMENT_REPORT.md` - Análise completa V1.2
- `COMPARISON_REPORT.md` - Análise completa V1.1
- `CHANGELOG.md` - Histórico de mudanças
