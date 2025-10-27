"""
Script para converter checkpoints intermediários em pipelines utilizáveis.

Este script permite testar modelos durante o treinamento, sem aguardar conclusão.

Uso:
    python convert_checkpoint_to_pipeline.py \
        --checkpoint_path ../outputs/lora_casual_shoes_3000steps_full/checkpoints/checkpoint-500 \
        --output_dir ../outputs/checkpoint_pipelines/checkpoint-500

Após conversão, o pipeline pode ser usado na API normalmente.
"""

import argparse
import logging
from pathlib import Path
import torch
from diffusers import (
    StableDiffusionPipeline,
    UNet2DConditionModel,
    DDPMScheduler,
)
from transformers import CLIPTextModel, CLIPTokenizer
from diffusers.models import AutoencoderKL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Converte checkpoint de treinamento para pipeline utilizável"
    )

    parser.add_argument(
        "--checkpoint_path",
        type=str,
        required=True,
        help="Caminho para o checkpoint (ex: ../outputs/.../checkpoints/checkpoint-500)"
    )

    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="Diretório de saída para o pipeline"
    )

    parser.add_argument(
        "--base_model",
        type=str,
        default="runwayml/stable-diffusion-v1-5",
        help="Modelo base SD 1.5"
    )

    parser.add_argument(
        "--test_prompt",
        type=str,
        default=None,
        help="Prompt para testar o pipeline após conversão (opcional)"
    )

    return parser.parse_args()


def load_checkpoint_unet(checkpoint_path: Path, base_model: str) -> UNet2DConditionModel:
    """
    Carrega UNet com LoRA do checkpoint.

    Args:
        checkpoint_path: Caminho para o checkpoint
        base_model: Nome do modelo base

    Returns:
        UNet com LoRA carregado
    """
    logger.info(f"Carregando UNet base de {base_model}...")

    # Carregar UNet base
    unet = UNet2DConditionModel.from_pretrained(
        base_model,
        subfolder="unet",
        torch_dtype=torch.float32
    )

    # Carregar state dict do checkpoint
    model_path = checkpoint_path / "model.safetensors"

    if not model_path.exists():
        # Tentar .bin se .safetensors não existir
        model_path = checkpoint_path / "pytorch_model.bin"

    if not model_path.exists():
        raise FileNotFoundError(f"Modelo não encontrado em {checkpoint_path}")

    logger.info(f"Carregando pesos do checkpoint: {model_path}")

    # Carregar pesos
    if model_path.suffix == ".safetensors":
        from safetensors.torch import load_file
        state_dict = load_file(str(model_path))
    else:
        state_dict = torch.load(str(model_path), map_location="cpu")

    # Aplicar pesos ao UNet
    # Nota: O Accelerator salva com prefixos, precisamos filtrar
    unet_state_dict = {}
    for key, value in state_dict.items():
        # Remover prefixos se existirem
        if key.startswith("module."):
            key = key[7:]  # Remove "module."
        if key.startswith("unet."):
            key = key[5:]  # Remove "unet."
        unet_state_dict[key] = value

    # Carregar pesos no UNet
    missing_keys, unexpected_keys = unet.load_state_dict(unet_state_dict, strict=False)

    if missing_keys:
        logger.warning(f"Missing keys: {len(missing_keys)} keys")
    if unexpected_keys:
        logger.warning(f"Unexpected keys: {len(unexpected_keys)} keys")

    logger.info("UNet carregado com sucesso!")

    return unet


def create_pipeline(checkpoint_path: Path, base_model: str, output_dir: Path):
    """
    Cria pipeline completo a partir do checkpoint.

    Args:
        checkpoint_path: Caminho para o checkpoint
        base_model: Nome do modelo base
        output_dir: Diretório de saída
    """
    logger.info("=" * 50)
    logger.info("Convertendo checkpoint para pipeline")
    logger.info("=" * 50)
    logger.info(f"Checkpoint: {checkpoint_path}")
    logger.info(f"Output: {output_dir}")
    logger.info("=" * 50)

    # Criar diretório de saída
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Carregar componentes do modelo base (que não foram treinados)
    logger.info("\n[1/5] Carregando componentes do modelo base...")

    tokenizer = CLIPTokenizer.from_pretrained(base_model, subfolder="tokenizer")
    text_encoder = CLIPTextModel.from_pretrained(
        base_model,
        subfolder="text_encoder",
        torch_dtype=torch.float32
    )
    vae = AutoencoderKL.from_pretrained(
        base_model,
        subfolder="vae",
        torch_dtype=torch.float32
    )
    scheduler = DDPMScheduler.from_pretrained(base_model, subfolder="scheduler")

    logger.info("✓ Componentes base carregados")

    # 2. Carregar UNet com LoRA do checkpoint
    logger.info("\n[2/5] Carregando UNet com LoRA do checkpoint...")
    unet = load_checkpoint_unet(checkpoint_path, base_model)
    logger.info("✓ UNet com LoRA carregado")

    # 3. Criar pipeline
    logger.info("\n[3/5] Criando pipeline...")
    pipeline = StableDiffusionPipeline(
        vae=vae,
        text_encoder=text_encoder,
        tokenizer=tokenizer,
        unet=unet,
        scheduler=scheduler,
        safety_checker=None,
        feature_extractor=None,
    )
    logger.info("✓ Pipeline criado")

    # 4. Salvar pipeline
    logger.info(f"\n[4/5] Salvando pipeline em {output_dir}...")
    pipeline.save_pretrained(output_dir)
    logger.info("✓ Pipeline salvo")

    # 5. Criar arquivo de metadata
    logger.info("\n[5/5] Criando metadata...")
    metadata = {
        "checkpoint_path": str(checkpoint_path),
        "checkpoint_step": checkpoint_path.name.split("-")[-1],
        "base_model": base_model,
        "converted_at": str(Path(__file__).parent),
    }

    import json
    with open(output_dir / "checkpoint_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info("✓ Metadata criada")

    logger.info("\n" + "=" * 50)
    logger.info("✓ Conversão concluída com sucesso!")
    logger.info("=" * 50)
    logger.info(f"\nPipeline disponível em: {output_dir}")
    logger.info("\nPara usar na API:")
    logger.info(f"  - O pipeline será detectado automaticamente")
    logger.info(f"  - Nome do modelo: {output_dir.parent.name}/{output_dir.name}")

    return pipeline


def test_pipeline(pipeline: StableDiffusionPipeline, prompt: str):
    """
    Testa o pipeline gerando uma imagem.

    Args:
        pipeline: Pipeline carregado
        prompt: Prompt para teste
    """
    logger.info("\n" + "=" * 50)
    logger.info("Testando pipeline")
    logger.info("=" * 50)
    logger.info(f"Prompt: {prompt}")

    # Mover para device
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    logger.info(f"Device: {device}")

    pipeline = pipeline.to(device)

    # Gerar imagem
    logger.info("Gerando imagem de teste...")

    generator = torch.Generator(device=device).manual_seed(42)

    image = pipeline(
        prompt,
        num_inference_steps=30,  # Menos steps para teste rápido
        guidance_scale=7.5,
        generator=generator,
    ).images[0]

    # Salvar
    output_path = Path("test_checkpoint_output.png")
    image.save(output_path)

    logger.info(f"✓ Imagem de teste salva em: {output_path}")
    logger.info("=" * 50)


def main():
    """Função principal."""
    args = parse_args()

    checkpoint_path = Path(args.checkpoint_path)
    output_dir = Path(args.output_dir)

    # Validar checkpoint existe
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint não encontrado: {checkpoint_path}")

    # Converter
    pipeline = create_pipeline(checkpoint_path, args.base_model, output_dir)

    # Testar se solicitado
    if args.test_prompt:
        test_pipeline(pipeline, args.test_prompt)

    logger.info("\n✓ Processo completo!")


if __name__ == "__main__":
    main()
