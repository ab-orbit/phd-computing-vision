# Classificação de Documentos com DocLayout-YOLO

## Conceito

Este projeto utiliza o **DocLayout-YOLO** para classificar documentos em 3 categorias do dataset RVL-CDIP:
- **Email**: Emails impressos
- **Advertisement**: Anúncios e propagandas
- **Scientific Publication**: Publicações científicas

### Diferença entre Layout Detection e Document Classification

**DocLayout-YOLO** foi originalmente criado para **detecção de layout**, ou seja, identificar elementos dentro de um documento como:
- Títulos
- Parágrafos
- Tabelas
- Figuras
- Equações
- Cabeçalhos/rodapés

**Nossa Abordagem**: Usamos a análise de layout como *features* para classificação. Documentos diferentes têm padrões de layout característicos:

| Tipo de Documento | Características de Layout |
|-------------------|--------------------------|
| **Email** | Cabeçalho (From/To/Subject), corpo de texto, assinatura |
| **Advertisement** | Muitas imagens, títulos grandes, pouco texto denso |
| **Scientific Publication** | Títulos, parágrafos densos, equações, referências, tabelas |

## Estrutura do Projeto

```
doclayout-yolo/
├── README.md                    # Este arquivo
├── requirements.txt             # Dependências
├── classify_documents.py        # Script principal de classificação
├── analyze_layout.py            # Análise de layout com DocLayout-YOLO
├── sample_selector.py           # Seleção de amostras do dataset
├── results/                     # Resultados da classificação
│   ├── email/                   # Resultados de emails
│   ├── advertisement/           # Resultados de anúncios
│   ├── scientific_publication/  # Resultados de publicações
│   └── report.json              # Relatório consolidado
└── sample/                      # Amostras selecionadas
    ├── email/
    ├── advertisement/
    └── scientific_publication/
```

## Instalação

### 1. Criar ambiente virtual (opcional mas recomendado)

```bash
conda create -n doclayout python=3.10
conda activate doclayout
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

Isso instalará:
- `doclayout-yolo`: Modelo de detecção de layout
- `ultralytics`: Framework YOLO
- `opencv-python`: Processamento de imagens
- `pillow`: Manipulação de imagens
- `pandas`: Análise de dados
- `matplotlib`: Visualização

### 3. Baixar modelo pré-treinado

O modelo será baixado automaticamente na primeira execução, ou você pode baixar manualmente:

```bash
# Modelo DocStructBench (recomendado)
wget https://huggingface.co/juliozhao/DocLayout-YOLO-DocStructBench/resolve/main/doclayout_yolo_docstructbench.pt
```

## Uso

### Classificação Completa (Pipeline Completo)

```bash
python classify_documents.py \
    --dataset-path ../rvlp/data/test \
    --model-path doclayout_yolo_docstructbench.pt \
    --num-samples 10 \
    --output-dir results
```

**Parâmetros**:
- `--dataset-path`: Caminho para o dataset RVL-CDIP
- `--model-path`: Caminho para o modelo DocLayout-YOLO
- `--num-samples`: Número de amostras por categoria (padrão: 10)
- `--output-dir`: Diretório de saída (padrão: results)
- `--conf`: Threshold de confiança (padrão: 0.2)
- `--imgsz`: Tamanho da imagem para inferência (padrão: 1024)

### Seleção de Amostras Apenas

```bash
python sample_selector.py \
    --dataset-path ../rvlp/data/test \
    --num-samples 10 \
    --output-dir sample
```

### Análise de Layout Apenas

```bash
python analyze_layout.py \
    --image-path sample/email/example.tif \
    --model-path doclayout_yolo_docstructbench.pt \
    --output-path results/email_layout.jpg
```

## Como Funciona

### Etapa 1: Seleção de Amostras

O script `sample_selector.py` seleciona aleatoriamente N amostras de cada categoria:

```
rvlp/data/test/email/           → sample/email/
rvlp/data/test/advertisement/   → sample/advertisement/
rvlp/data/test/scientific_publication/ → sample/scientific_publication/
```

### Etapa 2: Análise de Layout

Para cada documento, o DocLayout-YOLO detecta elementos de layout:

```python
detections = model.predict(image_path, imgsz=1024, conf=0.2)
```

**Elementos detectados** (exemplo DocStructBench):
- Text
- Title
- Figure
- Table
- Equation
- Caption
- Header
- Footer
- Reference

### Etapa 3: Extração de Features

Para cada documento, extraímos features baseadas no layout:

```python
features = {
    'num_titles': count(Title),
    'num_figures': count(Figure),
    'num_tables': count(Table),
    'num_equations': count(Equation),
    'text_density': area(Text) / total_area,
    'has_references': presence(Reference),
    'num_headers': count(Header),
    ...
}
```

### Etapa 4: Classificação Baseada em Regras

Usamos heurísticas para classificar baseado nas features:

#### Email
- Presença de header típico
- Texto em blocos simples
- Poucas ou nenhuma figura/tabela
- Sem equações

#### Advertisement
- Muitas figuras
- Títulos grandes e destacados
- Texto esparso (baixa densidade)
- Sem equações ou referências

#### Scientific Publication
- Presença de equações
- Múltiplas tabelas e figuras
- Alta densidade de texto
- Presença de referências
- Múltiplos títulos (seções)

### Etapa 5: Relatório de Resultados

Gera relatório JSON e visualizações:

```json
{
  "email": {
    "total_samples": 10,
    "classified_correct": 8,
    "accuracy": 0.8,
    "avg_confidence": 0.75
  },
  "advertisement": {
    "total_samples": 10,
    "classified_correct": 9,
    "accuracy": 0.9,
    "avg_confidence": 0.85
  },
  "scientific_publication": {
    "total_samples": 10,
    "classified_correct": 7,
    "accuracy": 0.7,
    "avg_confidence": 0.80
  }
}
```

## Saída Esperada

Para cada documento processado:

1. **Imagem Anotada**: `results/{category}/{image_name}_annotated.jpg`
   - Bounding boxes dos elementos detectados
   - Labels de cada elemento

2. **Análise JSON**: `results/{category}/{image_name}_analysis.json`
   - Features extraídas
   - Elementos detectados
   - Classificação predita
   - Confiança

3. **Relatório Consolidado**: `results/report.json`
   - Estatísticas por categoria
   - Acurácia geral
   - Matriz de confusão

## Limitações

1. **DocLayout-YOLO é para detecção de layout**, não classificação de tipo de documento
2. A classificação baseada em regras pode ter precisão limitada
3. Requer ajuste fino das heurísticas para melhor performance
4. Melhor performance em documentos com layouts bem definidos

## Melhorias Futuras

1. **Machine Learning**: Treinar um classificador (SVM, Random Forest) usando as features de layout
2. **Fine-tuning**: Adaptar o DocLayout-YOLO para o dataset RVL-CDIP
3. **Ensemble**: Combinar layout detection com classificação tradicional (YOLO11-cls)
4. **Features avançadas**: Análise de distribuição espacial, densidade por região, etc.

## Referências

- [DocLayout-YOLO GitHub](https://github.com/opendatalab/DocLayout-YOLO)
- [DocStructBench Dataset](https://huggingface.co/datasets/juliozhao/DocStructBench)
- [RVL-CDIP Dataset](https://www.cs.cmu.edu/~aharley/rvl-cdip/)

## Licença

Este projeto segue a licença do DocLayout-YOLO original.
