"""
Script para testar o setup de treinamento antes de iniciar o treino completo.

Valida:
- Dataset carrega corretamente
- Modelos carregam no device correto
- LoRA está configurado
- DataLoader funciona
- Forward pass funciona
- Memória está adequada

Executa 5 steps de teste sem salvar nada.
"""

import sys
import json
from pathlib import Path

import torch
from diffusers import AutoencoderKL, UNet2DConditionModel, DDPMScheduler
from transformers import CLIPTextModel, CLIPTokenizer
from peft import LoraConfig, get_peft_model
from torch.utils.data import DataLoader

# Importar dataset do train_lora
sys.path.insert(0, str(Path(__file__).parent))
from train_lora import CasualShoesDataset, collate_fn


def print_section(text: str):
    """Imprime seção."""
    print(f"\n{'=' * 80}")
    print(text)
    print('=' * 80)


def print_step(text: str):
    """Imprime passo."""
    print(f"\n{text}")
    print('-' * 80)


def get_memory_info():
    """Obtém info de memória."""
    try:
        import psutil
        mem = psutil.virtual_memory()
        return {
            'total_gb': mem.total / (1024**3),
            'available_gb': mem.available / (1024**3),
            'used_gb': mem.used / (1024**3),
            'percent': mem.percent
        }
    except ImportError:
        return None


def main():
    """Função principal de teste."""
    print_section("TESTE DE SETUP DE TREINAMENTO - TASK 1.5")

    # Configurações
    model_id = "runwayml/stable-diffusion-v1-5"
    data_dir = Path(__file__).parent.parent.parent / "data" / "casual_shoes" / "train"
    lora_rank = 8
    lora_alpha = 16
    batch_size = 2
    resolution = 512

    # Verificar device
    print_step("1. Verificando Device")
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print(f"[OK] MPS disponível: {device}")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"[OK] CUDA disponível: {device}")
    else:
        device = torch.device("cpu")
        print(f"[INFO] Usando CPU: {device}")

    # Memória inicial
    mem_info = get_memory_info()
    if mem_info:
        print(f"\n  Memória inicial:")
        print(f"    Total: {mem_info['total_gb']:.1f} GB")
        print(f"    Disponível: {mem_info['available_gb']:.1f} GB")
        print(f"    Usada: {mem_info['used_gb']:.1f} GB ({mem_info['percent']:.1f}%)")

    # Verificar dataset
    print_step("2. Verificando Dataset")
    print(f"  Data dir: {data_dir}")

    if not data_dir.exists():
        print(f"[ERRO] Diretório não existe: {data_dir}")
        return False

    captions_file = data_dir / "captions.json"
    images_dir = data_dir / "images"

    if not captions_file.exists():
        print(f"[ERRO] captions.json não encontrado: {captions_file}")
        return False

    if not images_dir.exists():
        print(f"[ERRO] Diretório images não encontrado: {images_dir}")
        return False

    # Carregar captions
    with open(captions_file, 'r') as f:
        captions = json.load(f)

    print(f"[OK] Captions carregado: {len(captions)} entradas")

    # Contar imagens
    images = list(images_dir.glob("*.png"))
    print(f"[OK] Imagens encontradas: {len(images)} PNG files")

    # Carregar tokenizer
    print_step("3. Carregando Tokenizer")
    tokenizer = CLIPTokenizer.from_pretrained(model_id, subfolder="tokenizer")
    print(f"[OK] Tokenizer carregado")
    print(f"  Vocab size: {tokenizer.vocab_size}")
    print(f"  Max length: {tokenizer.model_max_length}")

    # Criar dataset
    print_step("4. Criando Dataset")
    try:
        dataset = CasualShoesDataset(
            data_root=str(data_dir),
            tokenizer=tokenizer,
            size=resolution,
        )
        print(f"[OK] Dataset criado: {len(dataset)} amostras")
    except Exception as e:
        print(f"[ERRO] Falha ao criar dataset: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Testar loading de uma amostra
    print("\n  Testando load de amostra...")
    try:
        sample = dataset[0]
        print(f"[OK] Amostra carregada")
        print(f"  pixel_values shape: {sample['pixel_values'].shape}")
        print(f"  input_ids shape: {sample['input_ids'].shape}")
        print(f"  pixel_values range: [{sample['pixel_values'].min():.2f}, {sample['pixel_values'].max():.2f}]")
    except Exception as e:
        print(f"[ERRO] Falha ao carregar amostra: {e}")
        return False

    # Criar DataLoader
    print_step("5. Criando DataLoader")
    try:
        dataloader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=True,
            collate_fn=collate_fn,
            num_workers=0,
        )
        print(f"[OK] DataLoader criado")
        print(f"  Batch size: {batch_size}")
        print(f"  Num batches: {len(dataloader)}")
    except Exception as e:
        print(f"[ERRO] Falha ao criar DataLoader: {e}")
        return False

    # Testar batch
    print("\n  Testando batch...")
    try:
        batch = next(iter(dataloader))
        print(f"[OK] Batch carregado")
        print(f"  pixel_values shape: {batch['pixel_values'].shape}")
        print(f"  input_ids shape: {batch['input_ids'].shape}")
    except Exception as e:
        print(f"[ERRO] Falha ao carregar batch: {e}")
        return False

    # Carregar modelos
    print_step("6. Carregando Modelos")

    # Memória antes
    mem_before = get_memory_info()

    print("  Carregando VAE...")
    vae = AutoencoderKL.from_pretrained(model_id, subfolder="vae")
    print("[OK] VAE carregado")

    print("\n  Carregando Text Encoder...")
    text_encoder = CLIPTextModel.from_pretrained(model_id, subfolder="text_encoder")
    print("[OK] Text Encoder carregado")

    print("\n  Carregando UNet...")
    unet = UNet2DConditionModel.from_pretrained(model_id, subfolder="unet")
    print("[OK] UNet carregado")

    # Configurar LoRA
    print_step("7. Configurando LoRA")
    print(f"  Rank: {lora_rank}")
    print(f"  Alpha: {lora_alpha}")

    try:
        lora_config = LoraConfig(
            r=lora_rank,
            lora_alpha=lora_alpha,
            init_lora_weights="gaussian",
            target_modules=["to_k", "to_q", "to_v", "to_out.0"],
            lora_dropout=0.0,
        )
        unet = get_peft_model(unet, lora_config)
        print("[OK] LoRA configurado no UNet")

        # Printar parâmetros treináveis
        unet.print_trainable_parameters()
    except Exception as e:
        print(f"[ERRO] Falha ao configurar LoRA: {e}")
        return False

    # Mover para device
    print_step("8. Movendo Modelos para Device")
    weight_dtype = torch.float32
    print(f"  Device: {device}")
    print(f"  dtype: {weight_dtype}")

    vae.to(device, dtype=weight_dtype)
    print("[OK] VAE movido")

    text_encoder.to(device, dtype=weight_dtype)
    print("[OK] Text Encoder movido")

    unet.to(device, dtype=weight_dtype)
    print("[OK] UNet movido")

    # Memória após load
    mem_after = get_memory_info()
    if mem_after and mem_before:
        mem_used = mem_before['available_gb'] - mem_after['available_gb']
        print(f"\n  Memória usada pelos modelos: {mem_used:.2f} GB")
        print(f"  Memória disponível: {mem_after['available_gb']:.1f} GB")

    # Congelar modelos
    print_step("9. Configurando Training Mode")
    vae.requires_grad_(False)
    text_encoder.requires_grad_(False)
    unet.train()
    print("[OK] VAE e Text Encoder congelados")
    print("[OK] UNet em modo treino")

    # Criar scheduler
    print_step("10. Criando Noise Scheduler")
    noise_scheduler = DDPMScheduler.from_pretrained(model_id, subfolder="scheduler")
    print(f"[OK] Scheduler criado")
    print(f"  Num train timesteps: {noise_scheduler.config.num_train_timesteps}")

    # Testar forward pass
    print_step("11. Testando Forward Pass")
    print("  Executando 5 steps de teste...")

    vae.eval()
    text_encoder.eval()
    unet.train()

    try:
        for i in range(5):
            # Pegar batch
            batch = next(iter(dataloader))
            pixel_values = batch["pixel_values"].to(device, dtype=weight_dtype)
            input_ids = batch["input_ids"].to(device)

            # Encode para latents
            with torch.no_grad():
                latents = vae.encode(pixel_values).latent_dist.sample()
                latents = latents * vae.config.scaling_factor

            # Sample noise
            noise = torch.randn_like(latents)
            bsz = latents.shape[0]

            # Sample timesteps
            timesteps = torch.randint(
                0, noise_scheduler.config.num_train_timesteps, (bsz,),
                device=device
            ).long()

            # Add noise
            noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)

            # Get text embeddings
            with torch.no_grad():
                encoder_hidden_states = text_encoder(input_ids)[0]

            # Predict noise (forward pass)
            model_pred = unet(noisy_latents, timesteps, encoder_hidden_states).sample

            # Calcular loss
            import torch.nn.functional as F
            loss = F.mse_loss(model_pred.float(), noise.float(), reduction="mean")

            print(f"  Step {i+1}/5: loss = {loss.item():.4f}")

        print("\n[OK] Forward pass funcionando corretamente!")

    except Exception as e:
        print(f"\n[ERRO] Falha no forward pass: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Memória final
    mem_final = get_memory_info()
    if mem_final:
        print_step("12. Memória Final")
        print(f"  Total: {mem_final['total_gb']:.1f} GB")
        print(f"  Disponível: {mem_final['available_gb']:.1f} GB")
        print(f"  Usada: {mem_final['used_gb']:.1f} GB ({mem_final['percent']:.1f}%)")

    # Sumário
    print_section("RESULTADO DO TESTE")
    print("\n[OK] Todos os componentes testados com sucesso!")
    print("\nComponentes validados:")
    print("  [OK] Dataset carrega corretamente")
    print("  [OK] DataLoader funciona")
    print("  [OK] Modelos carregam no device")
    print("  [OK] LoRA configurado no UNet")
    print("  [OK] Forward pass funciona")
    print("  [OK] Loss é calculado corretamente")

    if mem_final:
        print(f"\nMemória disponível para treino: {mem_final['available_gb']:.1f} GB")
        if mem_final['available_gb'] > 4:
            print("[OK] Memória suficiente para treinamento")
        else:
            print("[AVISO] Memória pode ser limitada - considerar batch_size=1")

    print("\nPróximo passo:")
    print("  Executar treinamento completo com train_lora.py")
    print("\nComando sugerido:")
    print("  python3 train_lora.py --max_train_steps 100 --validation_steps 50")
    print("  (teste rápido com 100 steps)")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
