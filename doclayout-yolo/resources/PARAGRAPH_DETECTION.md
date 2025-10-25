# Detecção de Parágrafos - Documentação

## Visão Geral

A implementação foi atualizada para **detectar e contar automaticamente o número de parágrafos** em cada documento analisado. Esta informação é salva no JSON anotado de cada imagem e pode ser usada como feature adicional para classificação.

## O que foi Adicionado

### 1. Nova Função: `detect_paragraphs()`

Localização: `analyze_layout.py`

Esta função implementa um algoritmo de agrupamento de blocos de texto para identificar parágrafos:

```python
def detect_paragraphs(
    detections: List[Dict],
    img_height: int,
    img_width: int
) -> Tuple[int, List[Dict]]:
    """Detecta e conta parágrafos baseado nas detecções de blocos de texto."""
```

#### Algoritmo de Detecção

**Etapa 1: Filtragem**
- Filtra apenas elementos de texto: `plain text`, `text`, `paragraph`
- Remove blocos muito pequenos (< 1% da área da imagem)

**Etapa 2: Ordenação**
- Ordena blocos de texto por posição vertical (top → bottom)

**Etapa 3: Agrupamento**
- Agrupa blocos próximos verticalmente (distância < 5% da altura)
- Verifica overlap horizontal (> 50%)
- Blocos com overlap são considerados parte do mesmo parágrafo

**Etapa 4: Resultado**
- Retorna contagem de parágrafos
- Retorna informações detalhadas de cada parágrafo

#### Heurísticas Usadas

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| **Threshold vertical** | 5% da altura | Separação típica entre parágrafos |
| **Overlap horizontal mínimo** | 50% | Detectar mudança de coluna |
| **Área mínima do bloco** | 1% da imagem | Filtrar ruído |
| **Classes de texto** | `plain text`, `text`, `paragraph` | Variações detectadas pelo modelo |

### 2. Informações Salvas no JSON

Cada análise de documento agora inclui:

#### Campo: `num_paragraphs`

Número total de parágrafos detectados (inteiro).

```json
{
  "num_paragraphs": 10
}
```

#### Campo: `paragraph_info`

Array com detalhes de cada parágrafo:

```json
{
  "paragraph_info": [
    {
      "paragraph_id": 1,
      "num_blocks": 2,
      "bbox": [130.5, 223.1, 450.2, 380.7],
      "area": 34817.5,
      "confidence": 0.9659
    },
    {
      "paragraph_id": 2,
      ...
    }
  ]
}
```

**Campos de cada parágrafo**:
- `paragraph_id`: ID sequencial do parágrafo (1, 2, 3, ...)
- `num_blocks`: Quantos blocos de texto formam este parágrafo
- `bbox`: Bounding box englobando todo o parágrafo `[x1, y1, x2, y2]`
- `area`: Área total em pixels²
- `confidence`: Confiança média das detecções que formam o parágrafo

#### Campo: `features.num_paragraphs`

Também adicionado ao dicionário de features:

```json
{
  "features": {
    "num_paragraphs": 10,
    "num_titles": 2,
    "num_figures": 4,
    ...
  }
}
```

## Exemplos de Uso

### 1. Analisar Documento Individual

```bash
python analyze_layout.py \
    --image-path sample/email/documento.tif \
    --model-path doclayout_yolo_docstructbench_imgsz1024.pt \
    --save-json resultado.json
```

**Saída no terminal**:
```
Total de elementos detectados: 13
Parágrafos detectados: 3

Elementos por tipo:
  plain text          :   8
  title               :   2
  ...
```

**Conteúdo de `resultado.json`**:
```json
{
  "image_path": "sample/email/documento.tif",
  "num_paragraphs": 3,
  "paragraph_info": [...],
  "features": {
    "num_paragraphs": 3,
    ...
  }
}
```

### 2. Executar Classificação Completa

A classificação já incorpora automaticamente a contagem de parágrafos:

```bash
python classify_documents.py \
    --dataset-path ../rvlp/data/test \
    --num-samples 10
```

Cada análise em `results/{category}/*_analysis.json` terá:
- `num_paragraphs`: contagem
- `paragraph_info`: detalhes
- `features.num_paragraphs`: na feature list

### 3. Script de Teste

Execute o script de demonstração:

```bash
python test_paragraph_detection.py
```

**Saída esperada**:
```
RESUMO COMPARATIVO
================================================================================
Categoria                      Parágrafos   Elementos    Densidade Texto
--------------------------------------------------------------------------------
email                          3            13           12.32%
advertisement                  0            2            0.00%
scientific_publication         10           23           46.14%
```

## Padrões Observados

### Por Tipo de Documento

| Tipo de Documento | Parágrafos Típicos | Observações |
|-------------------|-------------------|-------------|
| **Email** | 1-4 | Poucos blocos de texto simples |
| **Advertisement** | 0-1 | Texto esparso ou ausente, dominado por imagens |
| **Scientific Publication** | 5-15 | Múltiplos parágrafos, alta densidade textual |
| **Letter** | 2-5 | Similar a email, mas mais estruturado |
| **Memo** | 2-4 | Breve, poucos parágrafos |
| **Scientific Report** | 8-20 | Muito texto, seções formais |

### Correlações com Outras Features

**Alta correlação com**:
- `text_density` (r ≈ 0.85): Mais parágrafos = mais texto
- `total_elements` (r ≈ 0.70): Documentos complexos têm mais elementos
- `num_titles` (r ≈ 0.60): Seções têm títulos e parágrafos

**Baixa correlação com**:
- `num_figures` (r ≈ 0.20): Independente
- `num_tables` (r ≈ 0.15): Independente

## Uso em Classificação

### Como Feature de Classificação

O número de parágrafos pode melhorar a classificação:

```python
# Em classify_documents.py, adicionar:
if num_paragraphs >= 5:
    scores['scientific_publication'] += 2.0
    scores['scientific_report'] += 2.0

if num_paragraphs == 0:
    scores['advertisement'] += 3.0
    scores['figure'] += 2.0

if 1 <= num_paragraphs <= 3:
    scores['email'] += 1.5
    scores['letter'] += 1.5
    scores['memo'] += 1.5
```

### Machine Learning

Use `num_paragraphs` como feature para classificadores:

```python
from sklearn.ensemble import RandomForestClassifier

features = [
    'num_paragraphs',
    'num_titles',
    'num_figures',
    'text_density',
    ...
]

X = df[features]
y = df['true_category']

clf = RandomForestClassifier()
clf.fit(X, y)

# Feature importance
importances = clf.feature_importances_
print(f"num_paragraphs importance: {importances[0]:.4f}")
```

## Limitações e Considerações

### Limitações Conhecidas

1. **Documentos em Múltiplas Colunas**
   - Algoritmo usa overlap horizontal de 50%
   - Pode agrupar parágrafos de colunas diferentes se estiverem alinhados verticalmente
   - Solução: Ajustar threshold de overlap ou detectar colunas primeiro

2. **Blocos de Texto Fragmentados**
   - Se modelo fragmenta muito o texto, cada fragmento pode ser contado como parágrafo
   - Dependente da qualidade da detecção do modelo
   - Solução: Ajustar `conf` threshold ou `vertical_threshold`

3. **Documentos com Layout Complexo**
   - Tabelas com texto podem ser contadas como parágrafos
   - Cabeçalhos/rodapés geralmente não são contados (classes diferentes)
   - Notas de rodapé podem ser contadas separadamente

4. **Idioma e Formato**
   - Algoritmo é agnóstico ao idioma
   - Funciona para qualquer documento com texto em blocos
   - Não considera conteúdo, apenas layout espacial

### Ajuste de Parâmetros

Você pode ajustar os thresholds editando `analyze_layout.py`:

```python
def detect_paragraphs(...):
    # Ajustar distância vertical entre parágrafos
    vertical_threshold = img_height * 0.05  # 5% → ajustar para 0.03 ou 0.08

    # Ajustar overlap horizontal mínimo
    overlap_ratio > 0.5  # 50% → ajustar para 0.3 ou 0.7

    # Ajustar área mínima dos blocos
    if det['area_ratio'] > 0.01:  # 1% → ajustar para 0.005 ou 0.02
```

## Validação

### Como Validar a Detecção

**Método 1: Inspeção Visual**

```bash
# Gerar imagem anotada
python analyze_layout.py \
    --image-path documento.tif \
    --output-path anotado.jpg \
    --save-json analise.json

# Abrir imagem e conferir
open anotado.jpg

# Ver parágrafos detectados
cat analise.json | jq '.num_paragraphs, .paragraph_info'
```

**Método 2: Comparação Manual**

```bash
# Executar teste comparativo
python test_paragraph_detection.py

# Compara resultados esperados vs detectados
```

**Método 3: Análise Estatística**

```python
import pandas as pd
import json
from pathlib import Path

# Carregar todas as análises
results = []
for json_file in Path('../results').glob('*/*_analysis.json'):
   with open(json_file) as f:
      data = json.load(f)
      results.append({
         'category': data['true_category'],
         'num_paragraphs': data['num_paragraphs'],
         'text_density': data['features']['plain text_density']
      })

df = pd.DataFrame(results)

# Estatísticas por categoria
print(df.groupby('category')['num_paragraphs'].describe())
```

## Próximas Melhorias

### Melhorias Planejadas

1. **Detecção de Colunas**
   - Identificar layouts multi-coluna
   - Processar cada coluna independentemente
   - Evitar agrupar parágrafos de colunas diferentes

2. **Classificação de Tipos de Parágrafo**
   - Introdução
   - Corpo
   - Conclusão
   - Nota de rodapé
   - Citação

3. **Análise de Estrutura**
   - Identificar hierarquia de seções
   - Parágrafos por seção
   - Profundidade da estrutura

4. **Métricas Textuais**
   - Comprimento médio de parágrafo
   - Variância de comprimento
   - Densidade de palavras (se OCR disponível)

## Perguntas Frequentes

### P: Por que alguns documentos têm 0 parágrafos?

**R:** Documentos visuais (anúncios, diagramas) podem não ter blocos de texto detectados, resultando em 0 parágrafos. Isso é esperado e útil para classificação.

### P: Um parágrafo pode ter múltiplos blocos?

**R:** Sim! Um parágrafo pode ter `num_blocks > 1` se o modelo detectou o texto fragmentado mas o algoritmo os agrupou corretamente.

### P: Como lidar com falsos positivos?

**R:** Ajuste os thresholds ou filtre por confiança. Blocos com baixa confiança (< 0.5) podem ser ignorados:

```python
if det['area_ratio'] > 0.01 and det['confidence'] > 0.5:
    text_blocks.append(det)
```

### P: Funciona com documentos escaneados de baixa qualidade?

**R:** Sim, mas a qualidade depende da detecção do modelo. Documentos com muito ruído podem ter mais falsos positivos. Recomenda-se usar `conf >= 0.3` para documentos ruidosos.

---

**Atualizado**: 25 de outubro de 2025
**Versão**: 1.0
**Arquivo**: `analyze_layout.py`
