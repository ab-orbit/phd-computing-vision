"""
Script para preparar dataset de Casual Shoes para treinamento.

Este script:
- Filtra e cria splits de Casual Shoes (70/15/15)
- Redimensiona imagens para 512x512
- Cria captions estruturados para treinamento
- Organiza dados prontos para Stable Diffusion + LoRA
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from PIL import Image
from typing import Dict, List, Tuple
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import shutil

from config import (
    STYLES_CSV, IMAGES_DIR, STYLES_JSON_DIR,
    RANDOM_SEED
)

# Configurações
TARGET_SIZE = 512  # Tamanho padrão para SD 1.5
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# Diretório de saída
OUTPUT_BASE = Path("/Users/jwcunha/Documents/COMPANIES/AB/repos/private/premium/researcher/phd-classes/shoes-tranning/data/casual_shoes")


def load_casual_shoes_data() -> pd.DataFrame:
    """
    Carrega e filtra dados de Casual Shoes.

    Returns:
        DataFrame com dados de Casual Shoes
    """
    print("Carregando dados de Casual Shoes...")
    df = pd.read_csv(STYLES_CSV, on_bad_lines='skip')
    df_casual = df[df['articleType'] == 'Casual Shoes'].copy()
    print(f"[OK] {len(df_casual):,} produtos de Casual Shoes")
    return df_casual


def create_stratified_splits(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Cria splits estratificados por cor base.

    Args:
        df: DataFrame de Casual Shoes

    Returns:
        Tupla (train_df, val_df, test_df)
    """
    print("\n[PROCESSANDO] Criando splits estratificados...")

    # Agrupar cores raras
    color_counts = df['baseColour'].value_counts()
    rare_colors = color_counts[color_counts < 10].index

    df_split = df.copy()
    if len(rare_colors) > 0:
        print(f"  [INFO] Agrupando {len(rare_colors)} cores raras em 'Other'")
        df_split.loc[df_split['baseColour'].isin(rare_colors), 'baseColour'] = 'Other'

    # Primeiro split: train vs (val + test)
    train_df, temp_df = train_test_split(
        df_split,
        test_size=(VAL_RATIO + TEST_RATIO),
        stratify=df_split['baseColour'],
        random_state=RANDOM_SEED
    )

    # Verificar cores raras no temp_df
    temp_color_counts = temp_df['baseColour'].value_counts()
    temp_rare = temp_color_counts[temp_color_counts < 2].index

    if len(temp_rare) > 0:
        temp_df = temp_df.copy()
        temp_df.loc[temp_df['baseColour'].isin(temp_rare), 'baseColour'] = 'Other'

    # Segundo split: val vs test
    val_proportion = VAL_RATIO / (VAL_RATIO + TEST_RATIO)
    val_df, test_df = train_test_split(
        temp_df,
        test_size=(1 - val_proportion),
        stratify=temp_df['baseColour'],
        random_state=RANDOM_SEED
    )

    print(f"\n[OK] Splits criados:")
    print(f"  Train: {len(train_df):,} ({len(train_df)/len(df)*100:.1f}%)")
    print(f"  Val: {len(val_df):,} ({len(val_df)/len(df)*100:.1f}%)")
    print(f"  Test: {len(test_df):,} ({len(test_df)/len(df)*100:.1f}%)")

    return train_df, val_df, test_df


def resize_and_save_image(img_path: Path, output_path: Path, size: int = TARGET_SIZE) -> bool:
    """
    Redimensiona e salva imagem mantendo aspect ratio com padding.

    Args:
        img_path: Caminho da imagem original
        output_path: Caminho de saída
        size: Tamanho alvo (quadrado)

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        with Image.open(img_path) as img:
            # Converter para RGB se necessário
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Calcular dimensões mantendo aspect ratio
            width, height = img.size
            aspect = width / height

            if aspect > 1:  # Largura maior
                new_width = size
                new_height = int(size / aspect)
            else:  # Altura maior ou quadrado
                new_height = size
                new_width = int(size * aspect)

            # Redimensionar
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Criar imagem com padding (fundo branco)
            img_padded = Image.new('RGB', (size, size), (255, 255, 255))

            # Calcular posição para centralizar
            paste_x = (size - new_width) // 2
            paste_y = (size - new_height) // 2

            # Colar imagem redimensionada no centro
            img_padded.paste(img_resized, (paste_x, paste_y))

            # Salvar
            img_padded.save(output_path, 'PNG', quality=95)

            return True

    except Exception as e:
        print(f"  [ERRO] Erro ao processar {img_path.name}: {e}")
        return False


def create_caption(row: pd.Series, json_data: Dict = None) -> str:
    """
    Cria caption estruturado para o produto.

    Args:
        row: Linha do DataFrame
        json_data: Dados do JSON (opcional)

    Returns:
        Caption formatado
    """
    # Template base
    caption_parts = ["A professional product photo of"]

    # Cor
    color = str(row['baseColour']).lower() if pd.notna(row['baseColour']) else 'colored'
    caption_parts.append(color)

    # Tipo
    caption_parts.append("casual shoes")

    # Estação
    if pd.notna(row['season']):
        season = str(row['season']).lower()
        caption_parts.append(f", {season} collection")

    # Gênero
    if pd.notna(row['gender']):
        gender = str(row['gender']).lower()
        caption_parts.append(f", {gender}")

    # Marca (do JSON)
    if json_data and 'brandName' in json_data.get('data', {}):
        brand = json_data['data']['brandName']
        caption_parts.append(f", {brand} brand")

    # Final
    caption_parts.append(", centered on white background, high quality, product photography")

    return ' '.join(caption_parts)


def process_split(df: pd.DataFrame, split_name: str, output_dir: Path) -> Dict:
    """
    Processa um split: redimensiona imagens e cria captions.

    Args:
        df: DataFrame do split
        split_name: Nome do split (train, val, test)
        output_dir: Diretório de saída

    Returns:
        Dicionário com estatísticas
    """
    print(f"\n[PROCESSANDO] Split: {split_name}")

    # Criar diretórios
    images_dir = output_dir / split_name / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # Estatísticas
    stats = {
        'total': len(df),
        'processed': 0,
        'errors': 0,
        'missing_images': 0,
        'captions': {}
    }

    captions_data = []

    # Processar cada imagem
    for idx, row in tqdm(df.iterrows(), total=len(df), desc=f"  Processando {split_name}"):
        img_id = row['id']
        img_path = IMAGES_DIR / f"{img_id}.jpg"
        output_path = images_dir / f"{img_id}.png"

        # Verificar se imagem existe
        if not img_path.exists():
            stats['missing_images'] += 1
            continue

        # Redimensionar e salvar
        success = resize_and_save_image(img_path, output_path)

        if success:
            stats['processed'] += 1

            # Carregar JSON para caption
            json_data = None
            json_path = STYLES_JSON_DIR / f"{img_id}.json"
            if json_path.exists():
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                except:
                    pass

            # Criar caption
            caption = create_caption(row, json_data)

            # Adicionar aos dados
            captions_data.append({
                'image_id': str(img_id),
                'image_file': f"{img_id}.png",
                'caption': caption,
                'metadata': {
                    'color': str(row['baseColour']) if pd.notna(row['baseColour']) else None,
                    'gender': str(row['gender']) if pd.notna(row['gender']) else None,
                    'season': str(row['season']) if pd.notna(row['season']) else None,
                    'usage': str(row['usage']) if pd.notna(row['usage']) else None,
                    'year': int(row['year']) if pd.notna(row['year']) else None,
                }
            })

        else:
            stats['errors'] += 1

    # Salvar captions em JSON
    captions_file = output_dir / split_name / "captions.json"
    with open(captions_file, 'w', encoding='utf-8') as f:
        json.dump(captions_data, f, indent=2, ensure_ascii=False)

    stats['captions'] = captions_data

    print(f"  [OK] Processadas: {stats['processed']:,}/{stats['total']:,}")
    if stats['missing_images'] > 0:
        print(f"  [AVISO] Imagens faltantes: {stats['missing_images']}")
    if stats['errors'] > 0:
        print(f"  [AVISO] Erros: {stats['errors']}")

    return stats


def verify_dataset_integrity(output_dir: Path, train_stats: Dict, val_stats: Dict, test_stats: Dict):
    """
    Verifica integridade do dataset preparado.

    Args:
        output_dir: Diretório base do dataset
        train_stats, val_stats, test_stats: Estatísticas dos splits
    """
    print("\n[VERIFICACAO] Verificando integridade do dataset...")

    total_expected = train_stats['total'] + val_stats['total'] + test_stats['total']
    total_processed = train_stats['processed'] + val_stats['processed'] + test_stats['processed']

    print(f"  Total esperado: {total_expected:,}")
    print(f"  Total processado: {total_processed:,}")
    print(f"  Taxa de sucesso: {total_processed/total_expected*100:.1f}%")

    # Verificar arquivos
    for split_name in ['train', 'val', 'test']:
        images_dir = output_dir / split_name / "images"
        captions_file = output_dir / split_name / "captions.json"

        n_images = len(list(images_dir.glob("*.png")))

        with open(captions_file, 'r') as f:
            captions = json.load(f)
            n_captions = len(captions)

        print(f"\n  {split_name.upper()}:")
        print(f"    Imagens: {n_images:,}")
        print(f"    Captions: {n_captions:,}")

        if n_images == n_captions:
            print(f"    [OK] Integridade verificada")
        else:
            print(f"    [AVISO] Discrepância: {abs(n_images - n_captions)} itens")


def save_dataset_metadata(output_dir: Path, train_df: pd.DataFrame,
                          val_df: pd.DataFrame, test_df: pd.DataFrame,
                          train_stats: Dict, val_stats: Dict, test_stats: Dict):
    """
    Salva metadados do dataset preparado.

    Args:
        output_dir: Diretório base
        train_df, val_df, test_df: DataFrames dos splits
        train_stats, val_stats, test_stats: Estatísticas
    """
    print("\n[SALVANDO] Salvando metadados...")

    metadata = {
        'dataset_info': {
            'name': 'Casual Shoes - Fashion Product Images',
            'category': 'Casual Shoes',
            'total_samples': len(train_df) + len(val_df) + len(test_df),
            'image_size': TARGET_SIZE,
            'format': 'PNG',
            'random_seed': RANDOM_SEED,
        },
        'splits': {
            'train': {
                'size': len(train_df),
                'ratio': TRAIN_RATIO,
                'processed': train_stats['processed'],
            },
            'val': {
                'size': len(val_df),
                'ratio': VAL_RATIO,
                'processed': val_stats['processed'],
            },
            'test': {
                'size': len(test_df),
                'ratio': TEST_RATIO,
                'processed': test_stats['processed'],
            }
        },
        'distributions': {
            'train_colors': train_df['baseColour'].value_counts().to_dict(),
            'train_genders': train_df['gender'].value_counts().to_dict(),
            'train_seasons': train_df['season'].value_counts().to_dict(),
        },
        'caption_template': "A professional product photo of [color] casual shoes, [season] collection, [gender], [brand], centered on white background, high quality, product photography",
        'preparation_date': pd.Timestamp.now().isoformat(),
    }

    metadata_file = output_dir / "metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"  [OK] {metadata_file}")

    # Salvar também IDs dos splits
    for split_name, df in [('train', train_df), ('val', val_df), ('test', test_df)]:
        ids_file = output_dir / split_name / "ids.txt"
        with open(ids_file, 'w') as f:
            for img_id in df['id']:
                f.write(f"{img_id}\n")
        print(f"  [OK] {output_dir / split_name / 'ids.txt'}")


def create_readme(output_dir: Path, train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame):
    """
    Cria README do dataset preparado.

    Args:
        output_dir: Diretório base
        train_df, val_df, test_df: DataFrames dos splits
    """
    print("\n[SALVANDO] Criando README...")

    readme_content = f"""# Casual Shoes Dataset - Preparado para Treinamento

Dataset preparado para fine-tuning de Stable Diffusion 1.5 com LoRA.

## Estrutura

```
casual_shoes/
├── train/
│   ├── images/          # {len(train_df):,} imagens 512x512 PNG
│   ├── captions.json    # Captions estruturados
│   └── ids.txt          # IDs das imagens
├── val/
│   ├── images/          # {len(val_df):,} imagens
│   ├── captions.json
│   └── ids.txt
├── test/
│   ├── images/          # {len(test_df):,} imagens
│   ├── captions.json
│   └── ids.txt
├── metadata.json        # Metadados completos
└── README.md           # Este arquivo
```

## Estatísticas

- **Total de imagens**: {len(train_df) + len(val_df) + len(test_df):,}
- **Train**: {len(train_df):,} ({TRAIN_RATIO*100:.0f}%)
- **Validation**: {len(val_df):,} ({VAL_RATIO*100:.0f}%)
- **Test**: {len(test_df):,} ({TEST_RATIO*100:.0f}%)

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
{chr(10).join([f"- {color}: {count:,}" for color, count in train_df['baseColour'].value_counts().head(5).items()])}

### Gêneros
{chr(10).join([f"- {gender}: {count:,}" for gender, count in train_df['gender'].value_counts().items()])}

### Estações
{chr(10).join([f"- {season}: {count:,}" for season, count in train_df['season'].value_counts().items()])}

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
- **Data**: {pd.Timestamp.now().strftime('%Y-%m-%d')}
- **Random Seed**: {RANDOM_SEED}
- **Estratificação**: Por cor base (baseColour)

## Próximos Passos

1. Treinar SD 1.5 + LoRA com split train
2. Validar durante treinamento com split val
3. Avaliar modelo final com split test
4. Gerar imagens sintéticas para expansão do dataset

---

**Preparado para**: SPRINT 1 - Task 1.2
**Projeto**: Geração de Dados Sintéticos - Casual Shoes
"""

    readme_file = output_dir / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f"  [OK] {readme_file}")


def main():
    """Função principal que prepara o dataset completo."""
    print("=" * 80)
    print("PREPARACAO DO DATASET - CASUAL SHOES")
    print("Objetivo: Dataset pronto para treinamento SD 1.5 + LoRA")
    print("=" * 80)

    # Criar diretório de saída
    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)

    # 1. Carregar dados
    df = load_casual_shoes_data()

    # 2. Criar splits estratificados
    train_df, val_df, test_df = create_stratified_splits(df)

    # 3. Processar cada split
    train_stats = process_split(train_df, 'train', OUTPUT_BASE)
    val_stats = process_split(val_df, 'val', OUTPUT_BASE)
    test_stats = process_split(test_df, 'test', OUTPUT_BASE)

    # 4. Verificar integridade
    verify_dataset_integrity(OUTPUT_BASE, train_stats, val_stats, test_stats)

    # 5. Salvar metadados
    save_dataset_metadata(OUTPUT_BASE, train_df, val_df, test_df,
                         train_stats, val_stats, test_stats)

    # 6. Criar README
    create_readme(OUTPUT_BASE, train_df, val_df, test_df)

    print("\n" + "=" * 80)
    print("[OK] Dataset de Casual Shoes preparado com sucesso!")
    print("=" * 80)
    print(f"\nDiretório: {OUTPUT_BASE}")
    print(f"Total de imagens processadas: {train_stats['processed'] + val_stats['processed'] + test_stats['processed']:,}")
    print("\nPróximo passo: Task 1.3 - Setup do Ambiente PyTorch MPS")


if __name__ == "__main__":
    main()
