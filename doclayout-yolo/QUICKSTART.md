# Guia Rápido - Classificação de Documentos com DocLayout-YOLO

## Início Rápido (3 passos)

### 1. Instalar e Configurar

```bash
cd doclayout-yolo
./setup.sh
```

Isso irá:
- Instalar todas as dependências
- Baixar o modelo pré-treinado
- Criar estrutura de diretórios
- Testar a instalação

### 2. Executar Classificação

```bash
python classify_documents.py --dataset-path ../rvlp/data/test --num-samples 10
```

Isso irá:
- Selecionar 10 amostras de cada categoria (email, advertisement, scientific_publication)
- Analisar o layout de cada documento
- Classificar usando heurísticas baseadas no layout
- Gerar relatório com acurácia e matriz de confusão

### 3. Ver Resultados

```bash
# Relatório JSON
cat results/classification_report.json

# Imagens anotadas
open results/email/*_annotated.jpg
open results/advertisement/*_annotated.jpg
open results/scientific_publication/*_annotated.jpg
```

## Comandos Úteis

### Selecionar Amostras Apenas

```bash
python sample_selector.py \
    --dataset-path ../rvlp/data/test \
    --num-samples 10 \
    --categories email advertisement scientific_publication
```

### Analisar Um Documento Específico

```bash
python analyze_layout.py \
    --image-path sample/email/exemplo.tif \
    --output-path resultado_anotado.jpg \
    --save-json analise.json
```

### Classificar com Mais Amostras

```bash
python classify_documents.py \
    --dataset-path ../rvlp/data/test \
    --num-samples 50 \
    --output-dir results_50
```

### Usar GPU (se disponível)

```bash
python classify_documents.py \
    --dataset-path ../rvlp/data/test \
    --num-samples 10 \
    --device cuda
```

## Estrutura de Saída

Após executar a classificação, você terá:

```
results/
├── email/
│   ├── doc1_annotated.jpg      # Imagem com bounding boxes
│   ├── doc1_analysis.json       # Análise detalhada
│   ├── doc2_annotated.jpg
│   └── ...
├── advertisement/
│   └── ...
├── scientific_publication/
│   └── ...
└── classification_report.json   # Relatório consolidado
```

## Exemplo de Relatório

```json
{
  "overall_accuracy": 0.8333,
  "total_samples": 30,
  "total_correct": 25,
  "category_stats": {
    "email": {
      "accuracy": 0.9,
      "total_samples": 10,
      "correct": 9
    },
    "advertisement": {
      "accuracy": 0.8,
      "total_samples": 10,
      "correct": 8
    },
    "scientific_publication": {
      "accuracy": 0.8,
      "total_samples": 10,
      "correct": 8
    }
  },
  "confusion_matrix": {
    "email": {"email": 9, "advertisement": 1, "scientific_publication": 0},
    "advertisement": {"email": 0, "advertisement": 8, "scientific_publication": 2},
    "scientific_publication": {"email": 1, "advertisement": 1, "scientific_publication": 8}
  }
}
```

## Interpretação dos Resultados

### Elementos Detectados

O DocLayout-YOLO detecta:

- **text**: Blocos de texto
- **title**: Títulos e cabeçalhos
- **figure**: Imagens e figuras
- **table**: Tabelas
- **equation**: Equações matemáticas
- **caption**: Legendas
- **header**: Cabeçalhos de página
- **footer**: Rodapés
- **reference**: Seções de referências

### Heurísticas de Classificação

#### Email
- ✓ Poucos elementos (≤5)
- ✓ Densidade de texto moderada (20-50%)
- ✓ Sem equações
- ✓ Poucas ou nenhuma figura/tabela

#### Advertisement
- ✓ Muitas figuras (≥2)
- ✓ Baixa densidade de texto (<30%)
- ✓ Sem equações ou referências
- ✓ Títulos destacados

#### Scientific Publication
- ✓ Presença de equações
- ✓ Múltiplas tabelas e figuras
- ✓ Alta densidade de texto (≥40%)
- ✓ Seção de referências
- ✓ Múltiplos títulos/seções (≥3)

## Personalização

### Ajustar Heurísticas

Edite `classify_documents.py`, função `classify_from_layout()`:

```python
# Exemplo: aumentar peso de equações para scientific publications
if num_equations >= 1:
    scores['scientific_publication'] += 10.0  # Antes: 5.0
```

### Modificar Threshold de Confiança

```bash
python classify_documents.py \
    --dataset-path ../rvlp/data/test \
    --conf 0.3  # Aumentar de 0.2 para 0.3
```

Threshold mais alto = menos detecções mas mais confiáveis

### Alterar Tamanho de Inferência

```bash
python classify_documents.py \
    --dataset-path ../rvlp/data/test \
    --imgsz 640  # Menor = mais rápido, 1024 = mais preciso
```

## Troubleshooting

### Erro: "doclayout-yolo não instalado"

```bash
pip install doclayout-yolo
```

### Erro: "Modelo não encontrado"

```bash
wget https://huggingface.co/juliozhao/DocLayout-YOLO-DocStructBench/resolve/main/doclayout_yolo_docstructbench.pt
```

### Erro: "Categoria não encontrada"

Verifique se o caminho está correto:

```bash
ls ../rvlp/data/test/
# Deve mostrar: email, advertisement, scientific_publication, ...
```

### Performance Lenta

Use GPU:

```bash
python classify_documents.py --device cuda
```

Ou reduza tamanho da imagem:

```bash
python classify_documents.py --imgsz 640
```

## Próximos Passos

1. **Melhorar Heurísticas**: Ajuste os pesos em `classify_from_layout()`
2. **Machine Learning**: Use as features extraídas para treinar um classificador (SVM, Random Forest)
3. **Ensemble**: Combine com YOLO11-cls do outro notebook
4. **Fine-tuning**: Adapte o DocLayout-YOLO para o dataset RVL-CDIP

## Recursos

- [DocLayout-YOLO GitHub](https://github.com/opendatalab/DocLayout-YOLO)
- [Modelo DocStructBench](https://huggingface.co/juliozhao/DocLayout-YOLO-DocStructBench)
- [RVL-CDIP Dataset](https://www.cs.cmu.edu/~aharley/rvl-cdip/)
- [README Completo](README.md)
