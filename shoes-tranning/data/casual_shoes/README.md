# Casual Shoes Dataset - Preparado para Treinamento

Dataset preparado para fine-tuning de Stable Diffusion 1.5 com LoRA.

## Estrutura

```
casual_shoes/
├── train/
│   ├── images/          # 1,991 imagens 512x512 PNG
│   ├── captions.json    # Captions estruturados
│   └── ids.txt          # IDs das imagens
├── val/
│   ├── images/          # 427 imagens
│   ├── captions.json
│   └── ids.txt
├── test/
│   ├── images/          # 427 imagens
│   ├── captions.json
│   └── ids.txt
├── metadata.json        # Metadados completos
└── README.md           # Este arquivo
```

## Estatísticas

- **Total de imagens**: 2,845
- **Train**: 1,991 (70%)
- **Validation**: 427 (15%)
- **Test**: 427 (15%)

## Formato

- **Tamanho**: 512x512 pixels (quadrado)
- **Formato**: PNG
- **Fundo**: Branco (padding quando necessário)
- **Aspect Ratio**: Preservado com padding

## Captions

Formato estruturado:
```
"A professional product photo of [color] casual shoes, [season] collection, [gender], [brand], centered on white background, high quality, product photography"
```

Exemplo:
```
"A professional product photo of black casual shoes, summer collection, men, Nike brand, centered on white background, high quality, product photography"
```

## Distribuições (Train Split)

### Top 5 Cores
- Black: 612
- Brown: 358
- White: 304
- Grey: 130
- Blue: 126

### Gêneros
- Men: 1,583
- Women: 230
- Unisex: 151
- Boys: 19
- Girls: 8

### Estações
- Summer: 979
- Fall: 624
- Winter: 296
- Spring: 92

## Uso

### Carregar Dataset (Python)

```python
import json
from pathlib import Path
from PIL import Image

# Carregar captions
with open('train/captions.json', 'r') as f:
    captions = json.load(f)

# Carregar imagem
img_path = Path('train/images') / captions[0]['image_file']
image = Image.open(img_path)
caption_text = captions[0]['caption']
```

### Para Treinamento SD 1.5

```python
from datasets import load_dataset

# Dataset em formato HuggingFace
dataset = load_dataset(
    'imagefolder',
    data_dir='./casual_shoes/train',
    split='train'
)
```

## Metadados

Cada entrada em `captions.json` contém:
- `image_id`: ID único do produto
- `image_file`: Nome do arquivo PNG
- `caption`: Caption formatado
- `metadata`: Atributos originais (cor, gênero, estação, etc.)

## Preparação

- **Script**: `prepare_casual_shoes_dataset.py`
- **Data**: 2025-10-26
- **Random Seed**: 42
- **Estratificação**: Por cor base (baseColour)

## Próximos Passos

1. Treinar SD 1.5 + LoRA com split train
2. Validar durante treinamento com split val
3. Avaliar modelo final com split test
4. Gerar imagens sintéticas para expansão do dataset

---

**Preparado para**: SPRINT 1 - Task 1.2
**Projeto**: Geração de Dados Sintéticos - Casual Shoes
