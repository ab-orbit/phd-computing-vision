"""
Script auxiliar para preparar arquivo de prompts para cálculo de CLIP Score.

Este script ajuda a criar o arquivo JSON de prompts necessário para calcular
o CLIP Score. Ele pode extrair prompts de:
1. Nomes de arquivo (se contiverem o prompt)
2. Arquivo de metadados JSON
3. Prompt padrão para todas as imagens

Uso:
    # Extrai prompts dos nomes de arquivo
    python prepare_prompts.py --images_dir ../api/generated_images \
                             --output prompts.json \
                             --from_filename

    # Usa prompt padrão
    python prepare_prompts.py --images_dir ../api/generated_images \
                             --output prompts.json \
                             --default_prompt "A professional product photo of casual shoes"

    # Extrai de arquivo de metadados
    python prepare_prompts.py --images_dir ../api/generated_images \
                             --output prompts.json \
                             --metadata_file metadata.json
"""

import json
import argparse
import re
from pathlib import Path
from typing import Dict


def extract_prompt_from_filename(filename: str) -> str:
    """
    Tenta extrair o prompt do nome do arquivo.

    Assume que o nome do arquivo pode conter informações sobre:
    - Checkpoint usado (ex: checkpoint-2000)
    - Timestamp
    - Seed
    - Potencialmente parte do prompt

    Args:
        filename: Nome do arquivo da imagem

    Returns:
        Prompt extraído ou prompt genérico
    """
    # Remove extensão
    name = Path(filename).stem

    # Tenta identificar padrões comuns nos nomes de arquivo gerados
    # Exemplo: lora_casual_shoes_3000steps_full_checkpoint-2000_20251028_073749_seed756280262

    # Procura por informações do modelo
    checkpoint_match = re.search(r'checkpoint-(\d+)', name)
    seed_match = re.search(r'seed(\d+)', name)

    # Para este projeto específico, sabemos que são sapatos casuais
    prompt = "A professional product photo of casual shoes"

    # Adiciona informações do checkpoint se disponível
    if checkpoint_match:
        checkpoint = checkpoint_match.group(1)
        prompt += f" (checkpoint {checkpoint})"

    return prompt


def prepare_prompts_from_filenames(images_dir: Path) -> Dict[str, str]:
    """
    Prepara dicionário de prompts a partir dos nomes de arquivo.

    Args:
        images_dir: Diretório contendo as imagens

    Returns:
        Dicionário mapeando nome de arquivo para prompt
    """
    prompts = {}

    # Busca todas as imagens
    for ext in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']:
        for img_path in images_dir.glob(f'*{ext}'):
            prompt = extract_prompt_from_filename(img_path.name)
            prompts[img_path.name] = prompt

    return prompts


def prepare_prompts_with_default(images_dir: Path, default_prompt: str) -> Dict[str, str]:
    """
    Prepara dicionário de prompts usando um prompt padrão para todas as imagens.

    Args:
        images_dir: Diretório contendo as imagens
        default_prompt: Prompt padrão a usar para todas as imagens

    Returns:
        Dicionário mapeando nome de arquivo para prompt
    """
    prompts = {}

    # Busca todas as imagens
    for ext in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']:
        for img_path in images_dir.glob(f'*{ext}'):
            prompts[img_path.name] = default_prompt

    return prompts


def prepare_prompts_from_metadata(images_dir: Path, metadata_file: Path) -> Dict[str, str]:
    """
    Prepara dicionário de prompts a partir de arquivo de metadados.

    Formato esperado do metadata.json:
    {
        "image1.png": {
            "prompt": "texto do prompt",
            "seed": 12345,
            ...
        },
        ...
    }

    ou

    [
        {
            "filename": "image1.png",
            "prompt": "texto do prompt",
            ...
        },
        ...
    ]

    Args:
        images_dir: Diretório contendo as imagens
        metadata_file: Arquivo JSON com metadados

    Returns:
        Dicionário mapeando nome de arquivo para prompt
    """
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    prompts = {}

    if isinstance(metadata, dict):
        # Formato dicionário
        for filename, meta in metadata.items():
            if isinstance(meta, dict) and 'prompt' in meta:
                prompts[filename] = meta['prompt']
            elif isinstance(meta, str):
                # Se meta for uma string, assume que é o prompt direto
                prompts[filename] = meta

    elif isinstance(metadata, list):
        # Formato lista
        for item in metadata:
            if 'filename' in item and 'prompt' in item:
                prompts[item['filename']] = item['prompt']

    return prompts


def prepare_prompts_from_batch_dirs(batch_dir: Path) -> Dict[str, str]:
    """
    Prepara prompts a partir de diretórios de batch que contêm o prompt no nome.

    Estrutura esperada:
    batch_TIMESTAMP/
        prompt_1_A_professional_product_photo_of_minimalist_white_s/
            image1.png
            image2.png
        prompt_2_A_professional_product_photo_of_futuristic_silver_/
            image3.png

    Args:
        batch_dir: Diretório raiz contendo os batches

    Returns:
        Dicionário mapeando nome de arquivo para prompt
    """
    prompts = {}

    # Procura por diretórios de prompt
    for prompt_dir in batch_dir.glob('prompt_*'):
        # Extrai o prompt do nome do diretório
        # Remove "prompt_N_" do início
        dir_name = prompt_dir.name
        match = re.match(r'prompt_\d+_(.*)', dir_name)

        if match:
            # Reconstrói o prompt substituindo underscores por espaços
            # e removando truncamento se necessário
            prompt_text = match.group(1).replace('_', ' ')

            # Se o prompt parece truncado, adiciona reticências
            if len(prompt_text) > 50 and not prompt_text.endswith('.'):
                prompt_text += '...'

            # Adiciona todas as imagens deste diretório
            for ext in ['.png', '.jpg', '.jpeg']:
                for img_path in prompt_dir.glob(f'*{ext}'):
                    prompts[img_path.name] = prompt_text

    return prompts


def main():
    parser = argparse.ArgumentParser(
        description='Prepara arquivo de prompts para cálculo de CLIP Score'
    )

    parser.add_argument(
        '--images_dir',
        type=str,
        required=True,
        help='Diretório contendo as imagens geradas'
    )

    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Arquivo de saída JSON para salvar os prompts'
    )

    parser.add_argument(
        '--from_filename',
        action='store_true',
        help='Extrai prompts dos nomes de arquivo'
    )

    parser.add_argument(
        '--default_prompt',
        type=str,
        default=None,
        help='Usa este prompt para todas as imagens'
    )

    parser.add_argument(
        '--metadata_file',
        type=str,
        default=None,
        help='Arquivo JSON com metadados contendo prompts'
    )

    parser.add_argument(
        '--from_batch_dirs',
        action='store_true',
        help='Extrai prompts dos nomes de diretórios batch (formato: prompt_N_texto)'
    )

    args = parser.parse_args()

    images_dir = Path(args.images_dir)
    output_file = Path(args.output)

    if not images_dir.exists():
        raise ValueError(f"Diretório de imagens não encontrado: {images_dir}")

    print(f"Preparando prompts para imagens em: {images_dir}")

    # Determina método de extração
    if args.from_batch_dirs:
        print("Modo: Extraindo prompts de diretórios batch")
        prompts = prepare_prompts_from_batch_dirs(images_dir)

    elif args.metadata_file:
        metadata_file = Path(args.metadata_file)
        if not metadata_file.exists():
            raise ValueError(f"Arquivo de metadados não encontrado: {metadata_file}")
        print(f"Modo: Lendo prompts de {metadata_file}")
        prompts = prepare_prompts_from_metadata(images_dir, metadata_file)

    elif args.default_prompt:
        print(f"Modo: Usando prompt padrão: '{args.default_prompt}'")
        prompts = prepare_prompts_with_default(images_dir, args.default_prompt)

    elif args.from_filename:
        print("Modo: Extraindo prompts dos nomes de arquivo")
        prompts = prepare_prompts_from_filenames(images_dir)

    else:
        raise ValueError(
            "Especifique um método de extração: "
            "--from_filename, --default_prompt, --metadata_file, ou --from_batch_dirs"
        )

    if not prompts:
        raise ValueError("Nenhum prompt foi gerado. Verifique o diretório de imagens.")

    # Salva prompts
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(prompts, f, indent=2, ensure_ascii=False)

    print(f"\nPrompts salvos com sucesso!")
    print(f"Total de imagens: {len(prompts)}")
    print(f"Arquivo de saída: {output_file}")

    # Mostra exemplo
    if prompts:
        print("\nExemplo de prompts gerados:")
        for i, (filename, prompt) in enumerate(list(prompts.items())[:3]):
            print(f"  {filename}: {prompt}")
        if len(prompts) > 3:
            print(f"  ... e mais {len(prompts) - 3} prompts")


if __name__ == '__main__':
    main()
