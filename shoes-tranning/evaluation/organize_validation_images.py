"""
Script para organizar imagens de validacao por checkpoint.

As imagens geradas durante o treinamento estao todas em um unico diretorio
com nomes como epoch003_step00500_prompt0_img0.png. Este script organiza
essas imagens em subdiretorios checkpoint-500, checkpoint-1000, etc.
"""

import shutil
from pathlib import Path
import re


def organize_validation_images(validation_dir: Path):
    """
    Organiza imagens de validacao em subdiretorios por checkpoint.

    Args:
        validation_dir: Diretorio contendo as imagens de validacao
    """
    validation_dir = Path(validation_dir)

    print(f"Organizando imagens em: {validation_dir}")

    # Mapeia step para checkpoint
    step_to_checkpoint = {
        '00500': 500,
        '01000': 1000,
        '01500': 1500,
        '02000': 2000,
        '02500': 2500,
        '03000': 3000
    }

    # Cria subdiretorios para cada checkpoint
    for checkpoint in step_to_checkpoint.values():
        checkpoint_dir = validation_dir / f"checkpoint-{checkpoint}"
        checkpoint_dir.mkdir(exist_ok=True)

    # Processa cada imagem
    pattern = re.compile(r'epoch\d+_step(\d+)_.*\.png')

    for img_file in validation_dir.glob('epoch*.png'):
        match = pattern.match(img_file.name)
        if match:
            step = match.group(1)
            if step in step_to_checkpoint:
                checkpoint = step_to_checkpoint[step]
                dest_dir = validation_dir / f"checkpoint-{checkpoint}"
                dest_file = dest_dir / img_file.name

                # Copia apenas se ainda nao existe
                if not dest_file.exists():
                    shutil.copy2(img_file, dest_file)

    # Relatorio
    print("\nResumo:")
    print("-" * 50)
    for checkpoint in sorted(step_to_checkpoint.values()):
        checkpoint_dir = validation_dir / f"checkpoint-{checkpoint}"
        num_images = len(list(checkpoint_dir.glob('*.png')))
        print(f"Checkpoint {checkpoint}: {num_images} imagens")

    print("\nImagens organizadas com sucesso!")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        validation_dir = Path(sys.argv[1])
    else:
        # Usa caminho padrao
        validation_dir = Path('../training/outputs/lora_casual_shoes_3000steps_full/validation')

    organize_validation_images(validation_dir)
