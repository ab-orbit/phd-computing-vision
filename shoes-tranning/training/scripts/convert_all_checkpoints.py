"""
Script para converter todos os checkpoints Accelerate para formato Diffusers Pipeline.

Converte checkpoints de training/outputs/*/checkpoints/checkpoint-*
para training/outputs/*/checkpoint_pipelines/checkpoint-*
"""

import sys
from pathlib import Path
import argparse
from convert_checkpoint_to_pipeline import create_pipeline

def convert_all_checkpoints(output_dir: Path, force: bool = False):
    """
    Converte todos os checkpoints de um diretório de treinamento.

    Args:
        output_dir: Diretório de output do treinamento
        force: Se True, reconverte checkpoints já convertidos
    """
    checkpoints_dir = output_dir / "checkpoints"

    if not checkpoints_dir.exists():
        print(f"Diretório de checkpoints não encontrado: {checkpoints_dir}")
        return

    # Listar checkpoints
    checkpoints = sorted([
        d for d in checkpoints_dir.iterdir()
        if d.is_dir() and d.name.startswith("checkpoint-")
    ])

    if not checkpoints:
        print(f"Nenhum checkpoint encontrado em: {checkpoints_dir}")
        return

    print(f"Encontrados {len(checkpoints)} checkpoints em: {checkpoints_dir}")
    print()

    checkpoint_pipelines_dir = output_dir / "checkpoint_pipelines"

    converted_count = 0
    skipped_count = 0
    failed_count = 0

    for checkpoint_path in checkpoints:
        checkpoint_name = checkpoint_path.name
        output_path = checkpoint_pipelines_dir / checkpoint_name

        # Verificar se já foi convertido
        if output_path.exists() and not force:
            print(f"⏭️  {checkpoint_name}: Já convertido (use --force para reconverter)")
            skipped_count += 1
            continue

        print(f"🔄 Convertendo {checkpoint_name}...")

        try:
            create_pipeline(
                checkpoint_path=checkpoint_path,
                base_model="runwayml/stable-diffusion-v1-5",
                output_dir=output_path
            )
            print(f"✅ {checkpoint_name}: Convertido com sucesso")
            converted_count += 1
        except Exception as e:
            print(f"❌ {checkpoint_name}: Erro - {e}")
            failed_count += 1

        print()

    # Resumo
    print("="*60)
    print("Resumo da Conversão:")
    print(f"  Convertidos: {converted_count}")
    print(f"  Ignorados: {skipped_count}")
    print(f"  Falhas: {failed_count}")
    print(f"  Total: {len(checkpoints)}")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Converte todos os checkpoints Accelerate para formato Diffusers"
    )
    parser.add_argument(
        "output_dir",
        type=str,
        help="Diretório de output do treinamento (ex: ../outputs/lora_casual_shoes_3000steps_full)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reconverte checkpoints já convertidos"
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir)

    if not output_dir.exists():
        print(f"Erro: Diretório não encontrado: {output_dir}")
        sys.exit(1)

    convert_all_checkpoints(output_dir, force=args.force)


if __name__ == "__main__":
    main()
