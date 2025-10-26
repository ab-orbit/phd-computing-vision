"""
Script de Treinamento LoRA para Stable Diffusion 1.5 - Casual Shoes.

Implementa fine-tuning do SD 1.5 usando PEFT/LoRA no dataset de casual shoes
preparado na Task 1.2, otimizado para Apple Silicon (MPS).

Características:
- LoRA (Low-Rank Adaptation) para eficiência
- Otimizado para MPS (float32, gradient checkpointing)
- Validação durante treinamento
- Checkpointing automático
- Logging detalhado

Dataset: 1,991 imagens de casual shoes (512x512 PNG)
Device: MPS (Apple Silicon)
"""

import argparse
import json
import logging
import math
import os
import random
import shutil
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from tqdm.auto import tqdm

from accelerate import Accelerator
from accelerate.logging import get_logger
from accelerate.utils import set_seed
from diffusers import (
    AutoencoderKL,
    DDPMScheduler,
    StableDiffusionPipeline,
    UNet2DConditionModel,
)
from diffusers.optimization import get_scheduler
from peft import LoraConfig, get_peft_model
from transformers import CLIPTextModel, CLIPTokenizer


logger = get_logger(__name__)


class CasualShoesDataset(Dataset):
    """
    Dataset de Casual Shoes preparado na Task 1.2.

    Estrutura:
        train/
            images/         # 1,991 imagens PNG 512x512
            captions.json   # Captions estruturados
    """

    def __init__(
        self,
        data_root: str,
        tokenizer: CLIPTokenizer,
        size: int = 512,
    ):
        """
        Args:
            data_root: Caminho para data/casual_shoes/train
            tokenizer: CLIP tokenizer
            size: Tamanho das imagens (512)
        """
        self.data_root = Path(data_root)
        self.tokenizer = tokenizer
        self.size = size

        # Carregar captions
        captions_file = self.data_root / "captions.json"
        if not captions_file.exists():
            raise FileNotFoundError(f"Captions não encontrado: {captions_file}")

        with open(captions_file, 'r') as f:
            self.captions_data = json.load(f)

        # Diretório de imagens
        self.images_dir = self.data_root / "images"
        if not self.images_dir.exists():
            raise FileNotFoundError(f"Diretório de imagens não encontrado: {self.images_dir}")

        # Verificar que todas as imagens existem
        self.valid_samples = []
        for item in self.captions_data:
            img_path = self.images_dir / item['image_file']
            if img_path.exists():
                self.valid_samples.append(item)

        if len(self.valid_samples) == 0:
            raise ValueError("Nenhuma imagem válida encontrada no dataset")

        # Usar print em vez de logger (logger requer Accelerator inicializado)
        print(f"[INFO] Dataset carregado: {len(self.valid_samples)} amostras válidas")

    def __len__(self):
        return len(self.valid_samples)

    def __getitem__(self, idx):
        """
        Retorna um item do dataset.

        Returns:
            dict com:
                - pixel_values: Tensor [3, 512, 512]
                - input_ids: Tensor [77] (tokens do caption)
        """
        item = self.valid_samples[idx]

        # Carregar imagem
        img_path = self.images_dir / item['image_file']
        image = Image.open(img_path).convert('RGB')

        # Verificar tamanho
        if image.size != (self.size, self.size):
            image = image.resize((self.size, self.size), Image.LANCZOS)

        # Converter para tensor [0, 1]
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image).permute(2, 0, 1)  # [H, W, C] -> [C, H, W]

        # Normalizar para [-1, 1] (esperado pelo VAE)
        image = (image - 0.5) / 0.5

        # Tokenizar caption
        caption = item['caption']
        input_ids = self.tokenizer(
            caption,
            padding="max_length",
            max_length=self.tokenizer.model_max_length,
            truncation=True,
            return_tensors="pt",
        ).input_ids[0]

        return {
            "pixel_values": image,
            "input_ids": input_ids,
        }


def collate_fn(examples):
    """Collate function para DataLoader."""
    pixel_values = torch.stack([example["pixel_values"] for example in examples])
    input_ids = torch.stack([example["input_ids"] for example in examples])

    return {
        "pixel_values": pixel_values,
        "input_ids": input_ids,
    }


def parse_args():
    """Parse argumentos de linha de comando."""
    parser = argparse.ArgumentParser(description="Treinamento LoRA SD 1.5 - Casual Shoes")

    # Modelo e Dataset
    parser.add_argument(
        "--pretrained_model_name_or_path",
        type=str,
        default="runwayml/stable-diffusion-v1-5",
        help="Modelo base SD 1.5",
    )
    parser.add_argument(
        "--train_data_dir",
        type=str,
        default="../../data/casual_shoes/train",
        help="Diretório com dados de treinamento",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="../outputs/lora_casual_shoes",
        help="Diretório para salvar checkpoints",
    )

    # Configurações de Treinamento
    parser.add_argument(
        "--resolution",
        type=int,
        default=512,
        help="Resolução das imagens",
    )
    parser.add_argument(
        "--train_batch_size",
        type=int,
        default=2,
        help="Batch size por device (ajustado para MPS + float32)",
    )
    parser.add_argument(
        "--gradient_accumulation_steps",
        type=int,
        default=8,
        help="Número de steps para acumular gradientes (batch efetivo = batch_size * grad_accum)",
    )
    parser.add_argument(
        "--num_train_epochs",
        type=int,
        default=1,
        help="Número de épocas de treinamento",
    )
    parser.add_argument(
        "--max_train_steps",
        type=int,
        default=3000,
        help="Número máximo de steps de treinamento",
    )
    parser.add_argument(
        "--learning_rate",
        type=float,
        default=1e-4,
        help="Learning rate inicial",
    )
    parser.add_argument(
        "--lr_scheduler",
        type=str,
        default="cosine",
        choices=["linear", "cosine", "cosine_with_restarts", "polynomial", "constant", "constant_with_warmup"],
        help="Tipo de scheduler",
    )
    parser.add_argument(
        "--lr_warmup_steps",
        type=int,
        default=500,
        help="Número de steps para warmup",
    )
    parser.add_argument(
        "--gradient_checkpointing",
        action="store_true",
        default=True,
        help="Habilitar gradient checkpointing (economia de memória ~40%)",
    )

    # Configurações LoRA
    parser.add_argument(
        "--lora_rank",
        type=int,
        default=8,
        help="Rank do LoRA (4, 8, 16, 32). Maior = mais parâmetros = melhor qualidade",
    )
    parser.add_argument(
        "--lora_alpha",
        type=int,
        default=16,
        help="Alpha do LoRA (tipicamente 2x rank)",
    )
    parser.add_argument(
        "--lora_dropout",
        type=float,
        default=0.0,
        help="Dropout do LoRA",
    )

    # Validação
    parser.add_argument(
        "--validation_prompt",
        type=str,
        nargs="+",
        default=[
            "A professional product photo of black casual shoes on white background, high quality, product photography",
            "A professional product photo of brown leather casual shoes on white background, high quality",
            "A professional product photo of white casual sneakers on white background, centered, product photography",
            "A professional product photo of blue casual shoes on white background, modern design, product photography",
        ],
        help="Prompts para validação",
    )
    parser.add_argument(
        "--validation_steps",
        type=int,
        default=500,
        help="Validar a cada N steps",
    )
    parser.add_argument(
        "--num_validation_images",
        type=int,
        default=4,
        help="Número de imagens de validação por prompt",
    )

    # Checkpointing
    parser.add_argument(
        "--checkpointing_steps",
        type=int,
        default=500,
        help="Salvar checkpoint a cada N steps",
    )
    parser.add_argument(
        "--checkpoints_total_limit",
        type=int,
        default=5,
        help="Número máximo de checkpoints a manter",
    )
    parser.add_argument(
        "--resume_from_checkpoint",
        type=str,
        default=None,
        help="Caminho para checkpoint para continuar treinamento",
    )

    # Logging
    parser.add_argument(
        "--logging_dir",
        type=str,
        default="../logs",
        help="Diretório para logs",
    )
    parser.add_argument(
        "--report_to",
        type=str,
        default="tensorboard",
        choices=["tensorboard", "wandb", "none"],
        help="Sistema de logging",
    )

    # Outros
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed para reprodutibilidade",
    )
    parser.add_argument(
        "--dataloader_num_workers",
        type=int,
        default=0,
        help="Número de workers para DataLoader (0 = main thread)",
    )

    args = parser.parse_args()

    # Converter paths relativos para absolutos (relativo ao script)
    script_dir = Path(__file__).parent
    if not Path(args.train_data_dir).is_absolute():
        args.train_data_dir = str((script_dir / args.train_data_dir).resolve())
    if not Path(args.output_dir).is_absolute():
        args.output_dir = str((script_dir / args.output_dir).resolve())
    if not Path(args.logging_dir).is_absolute():
        args.logging_dir = str((script_dir / args.logging_dir).resolve())

    # Validar que train_data_dir existe
    if not Path(args.train_data_dir).exists():
        raise FileNotFoundError(
            f"Dataset não encontrado: {args.train_data_dir}\n"
            f"Certifique-se de que Task 1.2 foi executada e que o dataset está em:\n"
            f"  data/casual_shoes/train/"
        )

    return args


def log_validation(
    vae,
    text_encoder,
    tokenizer,
    unet,
    args,
    accelerator,
    weight_dtype,
    epoch,
    step,
):
    """
    Executa validação gerando imagens com os prompts de validação.

    Args:
        vae: VAE decoder
        text_encoder: CLIP text encoder
        tokenizer: CLIP tokenizer
        unet: UNet (com LoRA)
        args: Argumentos
        accelerator: Accelerator
        weight_dtype: Tipo de dados (float32)
        epoch: Época atual
        step: Step atual
    """
    logger.info(f"Executando validação (epoch {epoch}, step {step})...")

    # Criar pipeline para inferência
    pipeline = StableDiffusionPipeline.from_pretrained(
        args.pretrained_model_name_or_path,
        vae=accelerator.unwrap_model(vae),
        text_encoder=accelerator.unwrap_model(text_encoder),
        tokenizer=tokenizer,
        unet=accelerator.unwrap_model(unet),
        safety_checker=None,
        torch_dtype=weight_dtype,
    )
    pipeline = pipeline.to(accelerator.device)
    pipeline.set_progress_bar_config(disable=True)

    # Modo eval
    pipeline.unet.eval()

    # Gerar imagens
    generator = torch.Generator(device=accelerator.device).manual_seed(args.seed)

    validation_dir = Path(args.output_dir) / "validation"
    validation_dir.mkdir(parents=True, exist_ok=True)

    for i, prompt in enumerate(args.validation_prompt):
        images = []
        for _ in range(args.num_validation_images):
            with torch.no_grad():
                image = pipeline(
                    prompt,
                    num_inference_steps=25,
                    generator=generator,
                ).images[0]
                images.append(image)

        # Salvar imagens
        for j, image in enumerate(images):
            filename = f"epoch{epoch:03d}_step{step:05d}_prompt{i}_img{j}.png"
            image.save(validation_dir / filename)

    logger.info(f"Validação concluída: {len(args.validation_prompt) * args.num_validation_images} imagens salvas")

    # Limpar memória
    del pipeline
    torch.cuda.empty_cache() if torch.cuda.is_available() else None


def save_checkpoint(accelerator, args, step, checkpoints_dir):
    """
    Salva checkpoint do modelo.

    Args:
        accelerator: Accelerator
        args: Argumentos
        step: Step atual
        checkpoints_dir: Diretório de checkpoints
    """
    checkpoint_path = checkpoints_dir / f"checkpoint-{step}"
    accelerator.save_state(checkpoint_path)
    logger.info(f"Checkpoint salvo: {checkpoint_path}")

    # Limitar número de checkpoints
    checkpoints = sorted(checkpoints_dir.glob("checkpoint-*"), key=lambda x: int(x.name.split('-')[1]))
    if len(checkpoints) > args.checkpoints_total_limit:
        for checkpoint in checkpoints[:-args.checkpoints_total_limit]:
            logger.info(f"Removendo checkpoint antigo: {checkpoint}")
            shutil.rmtree(checkpoint)


def main():
    """Função principal de treinamento."""
    args = parse_args()

    # Criar diretórios
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoints_dir = output_dir / "checkpoints"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)

    # Configurar logging
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
    )

    # Configurar Accelerator
    accelerator = Accelerator(
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        log_with=args.report_to if args.report_to != "none" else None,
        project_dir=args.logging_dir,
    )

    # Configurar logging
    logger.info(f"Accelerator state: {accelerator.state}")
    logger.info(f"Device: {accelerator.device}")
    logger.info(f"Num processes: {accelerator.num_processes}")
    logger.info(f"Mixed precision: {accelerator.mixed_precision}")

    # Set seed
    if args.seed is not None:
        set_seed(args.seed)

    # Carregar tokenizer e text encoder
    logger.info("Carregando tokenizer e text encoder...")
    tokenizer = CLIPTokenizer.from_pretrained(
        args.pretrained_model_name_or_path,
        subfolder="tokenizer",
    )
    text_encoder = CLIPTextModel.from_pretrained(
        args.pretrained_model_name_or_path,
        subfolder="text_encoder",
    )

    # Carregar VAE
    logger.info("Carregando VAE...")
    vae = AutoencoderKL.from_pretrained(
        args.pretrained_model_name_or_path,
        subfolder="vae",
    )

    # Carregar UNet
    logger.info("Carregando UNet...")
    unet = UNet2DConditionModel.from_pretrained(
        args.pretrained_model_name_or_path,
        subfolder="unet",
    )

    # Configurar LoRA no UNet
    logger.info(f"Configurando LoRA (rank={args.lora_rank}, alpha={args.lora_alpha})...")
    lora_config = LoraConfig(
        r=args.lora_rank,
        lora_alpha=args.lora_alpha,
        init_lora_weights="gaussian",
        target_modules=["to_k", "to_q", "to_v", "to_out.0"],
        lora_dropout=args.lora_dropout,
    )
    unet = get_peft_model(unet, lora_config)
    unet.print_trainable_parameters()

    # Congelar VAE e text encoder
    vae.requires_grad_(False)
    text_encoder.requires_grad_(False)

    # Habilitar gradient checkpointing
    if args.gradient_checkpointing:
        unet.enable_gradient_checkpointing()
        logger.info("Gradient checkpointing habilitado no UNet")

    # CRÍTICO: Usar float32 para MPS (não float16!)
    weight_dtype = torch.float32
    logger.info(f"Weight dtype: {weight_dtype} (float32 para estabilidade MPS)")

    # Mover modelos para device
    vae.to(accelerator.device, dtype=weight_dtype)
    text_encoder.to(accelerator.device, dtype=weight_dtype)
    unet.to(accelerator.device, dtype=weight_dtype)

    # Criar dataset e dataloader
    logger.info("Carregando dataset...")
    train_dataset = CasualShoesDataset(
        data_root=args.train_data_dir,
        tokenizer=tokenizer,
        size=args.resolution,
    )

    train_dataloader = DataLoader(
        train_dataset,
        batch_size=args.train_batch_size,
        shuffle=True,
        collate_fn=collate_fn,
        num_workers=args.dataloader_num_workers,
    )

    # Optimizer
    optimizer = torch.optim.AdamW(
        unet.parameters(),
        lr=args.learning_rate,
        betas=(0.9, 0.999),
        weight_decay=1e-2,
        eps=1e-8,
    )

    # Noise scheduler
    noise_scheduler = DDPMScheduler.from_pretrained(
        args.pretrained_model_name_or_path,
        subfolder="scheduler",
    )

    # Calcular número de steps
    num_update_steps_per_epoch = math.ceil(len(train_dataloader) / args.gradient_accumulation_steps)
    if args.max_train_steps is None:
        args.max_train_steps = args.num_train_epochs * num_update_steps_per_epoch

    # LR Scheduler
    lr_scheduler = get_scheduler(
        args.lr_scheduler,
        optimizer=optimizer,
        num_warmup_steps=args.lr_warmup_steps * args.gradient_accumulation_steps,
        num_training_steps=args.max_train_steps * args.gradient_accumulation_steps,
    )

    # Preparar com Accelerator
    unet, optimizer, train_dataloader, lr_scheduler = accelerator.prepare(
        unet, optimizer, train_dataloader, lr_scheduler
    )

    # Resumir configuração
    total_batch_size = args.train_batch_size * accelerator.num_processes * args.gradient_accumulation_steps
    logger.info("***** Configuração de Treinamento *****")
    logger.info(f"  Num examples = {len(train_dataset)}")
    logger.info(f"  Num epochs = {args.num_train_epochs}")
    logger.info(f"  Batch size per device = {args.train_batch_size}")
    logger.info(f"  Gradient accumulation steps = {args.gradient_accumulation_steps}")
    logger.info(f"  Total batch size = {total_batch_size}")
    logger.info(f"  Total optimization steps = {args.max_train_steps}")
    logger.info(f"  Learning rate = {args.learning_rate}")
    logger.info(f"  LoRA rank = {args.lora_rank}")
    logger.info(f"  LoRA alpha = {args.lora_alpha}")

    # Inicializar tracking
    if accelerator.is_main_process:
        tracker_config = vars(args)
        accelerator.init_trackers("train_lora_casual_shoes", config=tracker_config)

    # Variáveis de tracking
    global_step = 0
    first_epoch = 0

    # Resumir de checkpoint se especificado
    if args.resume_from_checkpoint:
        if args.resume_from_checkpoint != "latest":
            path = args.resume_from_checkpoint
        else:
            # Pegar último checkpoint
            dirs = os.listdir(checkpoints_dir)
            dirs = [d for d in dirs if d.startswith("checkpoint")]
            dirs = sorted(dirs, key=lambda x: int(x.split("-")[1]))
            path = checkpoints_dir / dirs[-1] if len(dirs) > 0 else None

        if path is not None:
            accelerator.load_state(path)
            global_step = int(path.name.split("-")[1])
            first_epoch = global_step // num_update_steps_per_epoch
            logger.info(f"Resumindo de checkpoint: {path}")
            logger.info(f"  Global step = {global_step}")
            logger.info(f"  First epoch = {first_epoch}")

    # Progress bar
    progress_bar = tqdm(
        range(global_step, args.max_train_steps),
        disable=not accelerator.is_local_main_process,
        desc="Steps",
    )

    # Loop de treinamento
    for epoch in range(first_epoch, args.num_train_epochs):
        unet.train()

        for step, batch in enumerate(train_dataloader):
            with accelerator.accumulate(unet):
                # Converter imagens para latents
                pixel_values = batch["pixel_values"].to(weight_dtype)
                latents = vae.encode(pixel_values).latent_dist.sample()
                latents = latents * vae.config.scaling_factor

                # Sample noise
                noise = torch.randn_like(latents)
                bsz = latents.shape[0]

                # Sample timesteps
                timesteps = torch.randint(
                    0, noise_scheduler.config.num_train_timesteps, (bsz,),
                    device=latents.device
                )
                timesteps = timesteps.long()

                # Add noise aos latents
                noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)

                # Get text embeddings
                encoder_hidden_states = text_encoder(batch["input_ids"])[0]

                # Predict noise
                model_pred = unet(noisy_latents, timesteps, encoder_hidden_states).sample

                # Calcular loss
                loss = F.mse_loss(model_pred.float(), noise.float(), reduction="mean")

                # Backprop
                accelerator.backward(loss)

                # Clip gradients
                if accelerator.sync_gradients:
                    accelerator.clip_grad_norm_(unet.parameters(), 1.0)

                optimizer.step()
                lr_scheduler.step()
                optimizer.zero_grad()

            # Atualizar progress bar
            if accelerator.sync_gradients:
                progress_bar.update(1)
                global_step += 1

                # Logging
                logs = {
                    "loss": loss.detach().item(),
                    "lr": lr_scheduler.get_last_lr()[0],
                    "epoch": epoch,
                }
                progress_bar.set_postfix(**logs)
                accelerator.log(logs, step=global_step)

                # Validação
                if global_step % args.validation_steps == 0:
                    if accelerator.is_main_process:
                        log_validation(
                            vae=vae,
                            text_encoder=text_encoder,
                            tokenizer=tokenizer,
                            unet=unet,
                            args=args,
                            accelerator=accelerator,
                            weight_dtype=weight_dtype,
                            epoch=epoch,
                            step=global_step,
                        )

                # Checkpoint
                if global_step % args.checkpointing_steps == 0:
                    if accelerator.is_main_process:
                        save_checkpoint(accelerator, args, global_step, checkpoints_dir)

            # Parar se atingiu max_train_steps
            if global_step >= args.max_train_steps:
                break

    # Salvar checkpoint final
    accelerator.wait_for_everyone()
    if accelerator.is_main_process:
        # Salvar modelo LoRA
        unet_lora = accelerator.unwrap_model(unet)
        unet_lora.save_pretrained(output_dir / "lora_weights")
        logger.info(f"Modelo LoRA salvo em: {output_dir / 'lora_weights'}")

        # Salvar pipeline completo
        pipeline = StableDiffusionPipeline.from_pretrained(
            args.pretrained_model_name_or_path,
            unet=accelerator.unwrap_model(unet),
            text_encoder=text_encoder,
            vae=vae,
            safety_checker=None,
            torch_dtype=weight_dtype,
        )
        pipeline.save_pretrained(output_dir / "final_pipeline")
        logger.info(f"Pipeline completo salvo em: {output_dir / 'final_pipeline'}")

    accelerator.end_training()
    logger.info("Treinamento concluído!")


if __name__ == "__main__":
    main()
