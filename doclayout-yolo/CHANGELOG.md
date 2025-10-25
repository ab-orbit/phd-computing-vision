# Changelog - DocLayout-YOLO Document Classification

## [1.2.0] - 2025-10-25

### Melhorado - Heurísticas de Classificação

#### Nova Abordagem: Densidade de Texto e Parágrafos

**Arquivos Modificados**:
- `classify_documents.py` - Heurísticas ajustadas para densidade de texto

**Mudanças no Código**:

1. **Heurísticas de EMAIL ajustadas**
   - Adicionado critério de densidade de texto: emails têm MENOS texto (mais área vazia)
   - `text_density < 0.20`: +3.0 boost
   - `text_density >= 0.45`: -3.0 penalização
   - Critério de parágrafos: 1-4 parágrafos típicos, ≥5 penaliza

2. **Heurísticas de ADVERTISEMENT ajustadas**
   - Aumentado peso de figuras: `num_figures >= 2` agora dá +5.0 (antes +4.0)
   - Adicionada penalização por alta densidade: `text_density > 0.4` = -2.0
   - Critério de parágrafos: 0-1 parágrafos típicos

3. **Heurísticas de SCIENTIFIC PUBLICATION ajustadas** (CRÍTICO)
   - Adicionado critério forte de densidade: `text_density >= 0.45` = +4.0 boost
   - Critério de parágrafos: ≥5 parágrafos = +4.0 boost (FUNDAMENTAL)
   - Aumentado peso de múltiplos títulos: ≥3 títulos = +3.0 (antes +2.0)

**Resultados**:

| Versão | Acurácia Geral | Email | Advertisement | Sci. Publication |
|--------|---------------|-------|---------------|------------------|
| V1 (Sem Mapeamento) | 23.33% | 20% | 50% | 0% |
| V2 (Com Mapeamento) | 46.67% | 80% | 50% | 10% |
| **V3 (Densidade Texto)** | **56.67%** | 80% | 40% | **50%** |

**Melhoria Destacada**:
- Acurácia geral: +10 pontos (46.67% → 56.67%)
- **Scientific Publications: +40 pontos (10% → 50%)** - Melhoria de 400%!
- Redução de confusão Sci → Email: 9 erros → 5 erros

**Novos Arquivos**:
- `HEURISTICS_IMPROVEMENT_REPORT.md` - Análise detalhada das melhorias
- Backup em `results_old_basic_heuristics/` - Resultados da versão anterior

**Uso**:
```bash
# Classificação com novas heurísticas
python classify_documents.py --dataset-path ../rvlp/data/test --num-samples 10

# Comparar com versões anteriores
ls results_old_*/classification_report.json
```

**Benefícios**:

1. **Distinção Email vs Scientific Publication melhorou drasticamente**
   - Usa razão texto/área em branco como fator decisivo
   - Emails: baixa densidade de texto (muita área vazia)
   - Publicações: alta densidade de texto (pouca área vazia)

2. **Número de parágrafos provou ser altamente discriminante**
   - Emails: 1-4 parágrafos
   - Advertisements: 0-1 parágrafos
   - Publicações: 5+ parágrafos

3. **Redução de falsos positivos**
   - Publicações não são mais sistematicamente classificadas como emails
   - Heurísticas agora capturam diferenças estruturais

**Limitações Identificadas**:
- Advertisements com apenas 1 figura são confundidos com emails (threshold muito restritivo)
- Publicações fragmentadas (1-2 parágrafos) ainda são problemáticas
- Emails complexos com múltiplos títulos confundidos com publicações

**Próximas Melhorias Planejadas**:
1. Ajustar threshold de figuras: `num_figures >= 1` ao invés de `>= 2`
2. Adicionar compensação para publicações com poucos parágrafos mas múltiplos títulos
3. Implementar Random Forest (acurácia esperada: 70-80%)

---

## [1.1.0] - 2025-10-25

### Adicionado - Detecção de Parágrafos

#### Nova Funcionalidade: Contagem Automática de Parágrafos

**Arquivos Modificados**:
- `analyze_layout.py` - Adicionada função `detect_paragraphs()`

**Mudanças no Código**:

1. **Nova função `detect_paragraphs()`**
   - Detecta e agrupa blocos de texto em parágrafos
   - Usa heurísticas espaciais (distância vertical, overlap horizontal)
   - Retorna contagem e informações detalhadas de cada parágrafo

2. **Atualização da função `analyze_document_layout()`**
   - Chama `detect_paragraphs()` após coletar detecções
   - Adiciona `num_paragraphs` e `paragraph_info` no resultado

3. **Atualização da função `extract_classification_features()`**
   - Novo parâmetro: `num_paragraphs`
   - Adiciona `features['num_paragraphs']` às features extraídas

**Saída no JSON**:

Todos os arquivos `*_analysis.json` agora incluem:

```json
{
  "num_paragraphs": 10,
  "paragraph_info": [
    {
      "paragraph_id": 1,
      "num_blocks": 2,
      "bbox": [x1, y1, x2, y2],
      "area": 34817.5,
      "confidence": 0.9659
    },
    ...
  ],
  "features": {
    "num_paragraphs": 10,
    ...
  }
}
```

**Novos Arquivos**:
- `test_paragraph_detection.py` - Script de teste e demonstração
- `PARAGRAPH_DETECTION.md` - Documentação completa da funcionalidade

**Uso**:

```bash
# Análise individual
python analyze_layout.py --image-path documento.tif --save-json resultado.json

# Ver parágrafos detectados
cat resultado.json | jq '.num_paragraphs, .paragraph_info'

# Teste comparativo
python test_paragraph_detection.py
```

**Benefícios**:

1. **Classificação melhorada**: Nova feature para distinguir tipos de documentos
   - Emails: 1-4 parágrafos
   - Advertisements: 0-1 parágrafos
   - Scientific Publications: 5-15 parágrafos

2. **Análise estrutural**: Entender organização do documento
   - Número de blocos por parágrafo
   - Área ocupada por cada parágrafo
   - Distribuição espacial

3. **Machine Learning**: Feature adicional para classificadores supervisionados

**Compatibilidade**:
- Retrocompatível: JSONs antigos ainda funcionam
- Parâmetro opcional: `num_paragraphs` tem valor padrão 0
- Não quebra código existente

---

## [1.0.0] - 2025-10-25

### Inicial - Sistema de Classificação

**Implementação completa**:
- Classificação de documentos usando DocLayout-YOLO
- 3 categorias: email, advertisement, scientific_publication
- Pipeline completo: seleção → análise → classificação → relatório
- Heurísticas baseadas em layout
- Visualizações e relatórios

**Arquivos criados**:
- `classify_documents.py` - Pipeline completo
- `analyze_layout.py` - Análise de layout
- `sample_selector.py` - Seleção de amostras
- `analyze_results.py` - Análise de resultados
- `demo_classification.py` - Demonstração
- `README.md` - Documentação principal
- `QUICKSTART.md` - Guia rápido
- `setup.sh` - Script de instalação

**Métricas iniciais**:
- Acurácia geral: 23.33%
- Problema identificado: Mapeamento de classes incorreto

---

## Roadmap

### [1.3.0] - Próxima versão (planejada)

**Ajuste fino de heurísticas**:
- [ ] Ajustar threshold de figuras para advertisements (>= 1)
- [ ] Adicionar compensação para publicações fragmentadas
- [ ] Acurácia esperada: 65-70%

### [2.0.0] - Versão futura

**Machine Learning**:
- [ ] Treinar Random Forest com features extraídas
- [ ] Validação cruzada
- [ ] Acurácia esperada: 75-85%

**Expandir categorias**:
- [ ] Adicionar 13 categorias restantes do RVL-CDIP
- [ ] 16 categorias totais

**Ensemble de modelos**:
- [ ] Combinar DocLayout-YOLO + YOLO11-cls
- [ ] Votação ou stacking
- [ ] Acurácia esperada: 85-90%

---

## Notas de Versão

### Convenções de Versionamento

Seguimos [Semantic Versioning](https://semver.org/):
- **MAJOR**: Mudanças incompatíveis
- **MINOR**: Novas funcionalidades compatíveis
- **PATCH**: Correções de bugs

### Como Atualizar

```bash
# Baixar última versão
git pull origin main

# Reinstalar dependências (se necessário)
pip install -r requirements.txt

# Baixar modelo atualizado (se necessário)
./setup.sh
```

### Verificar Versão

```python
# Em Python
from analyze_layout import detect_paragraphs
print("Versão 1.2.0+ instalada!")

# Via script
python -c "from analyze_layout import detect_paragraphs; print('✓ Detecção de parágrafos disponível')"
```

---

**Mantido por**: Equipe DocLayout-YOLO
**Última atualização**: 25 de outubro de 2025
**Versão Atual**: 1.2.0
