"""
Script para testar Stable Diffusion 1.5 com MPS - VERSÃO CORRIGIDA.

CORREÇÃO: Problema MPS + float16 gerando imagens pretas (NaN values).

Soluções implementadas:
1. Usar float32 em vez de float16 (mais estável no MPS)
2. Adicionar verificação de NaN/inf antes de salvar
3. Fallback para CPU se MPS falhar
4. Validação visual dos outputs

Modelo: runwayml/stable-diffusion-v1-5
Device: MPS (Apple Silicon) com fallbacks
"""

import sys
import time
import numpy as np
from pathlib import Path
from typing import Dict, Optional, List

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image


# Configurações
MODEL_ID = "runwayml/stable-diffusion-v1-5"
CACHE_DIR = Path.home() / ".cache" / "huggingface" / "hub"
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def print_section(text: str):
    """Imprime seção formatada."""
    print(f"\n{'=' * 80}")
    print(text)
    print('=' * 80)


def print_step(text: str):
    """Imprime passo formatado."""
    print(f"\n{text}")
    print('-' * 80)


def check_device() -> str:
    """Verifica e retorna o device disponível."""
    print_step("1. Verificando Device Disponível")

    # Tentar MPS primeiro
    if torch.backends.mps.is_available():
        device = "mps"
        print(f"[OK] MPS disponível")
        print(f"  Device primário: {device}")
        print(f"  [AVISO] MPS pode ter problemas com float16")
        print(f"  [INFO] Usando float32 para estabilidade")
    elif torch.cuda.is_available():
        device = "cuda"
        print(f"[OK] CUDA disponível")
        print(f"  Device: {device}")
    else:
        device = "cpu"
        print(f"[INFO] Usando CPU")
        print(f"  Device: {device}")
        print(f"  [AVISO] CPU é mais lento mas mais estável")

    return device


def get_memory_info():
    """Obtém informações de memória do sistema."""
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


def validate_image_array(image_array: np.ndarray, prompt: str) -> bool:
    """
    Valida se o array da imagem contém valores válidos.

    Args:
        image_array: Array numpy da imagem
        prompt: Prompt usado (para logging)

    Returns:
        True se válido, False se contém NaN/inf ou está toda preta
    """
    # Verificar NaN
    if np.isnan(image_array).any():
        print(f"  [ERRO] Imagem contém NaN values")
        return False

    # Verificar inf
    if np.isinf(image_array).any():
        print(f"  [ERRO] Imagem contém inf values")
        return False

    # Verificar se está toda preta (todos pixels = 0)
    if image_array.max() == 0:
        print(f"  [ERRO] Imagem está completamente preta")
        return False

    # Verificar se está toda branca (todos pixels = 255)
    if image_array.min() == 255:
        print(f"  [AVISO] Imagem está completamente branca")
        return False

    # Verificar range de valores
    if image_array.min() < 0 or image_array.max() > 255:
        print(f"  [ERRO] Valores fora do range [0, 255]: [{image_array.min()}, {image_array.max()}]")
        return False

    print(f"  [OK] Imagem válida - range: [{image_array.min()}, {image_array.max()}]")
    return True


def download_model(device: str, use_float16: bool = False) -> Optional[StableDiffusionPipeline]:
    """
    Faz download e carrega o modelo SD 1.5.

    Args:
        device: Device para carregar o modelo ('mps', 'cuda', 'cpu')
        use_float16: Se True, usa float16. Se False, usa float32 (mais estável)

    Returns:
        Pipeline carregado ou None em caso de erro
    """
    print_step("2. Download do Modelo Stable Diffusion 1.5")

    print(f"  Modelo: {MODEL_ID}")
    print(f"  Cache dir: {CACHE_DIR}")
    print(f"  Device: {device}")

    # Verificar memória antes do download
    mem_info = get_memory_info()
    if mem_info:
        print(f"\n  Memória antes do download:")
        print(f"    Total: {mem_info['total_gb']:.1f} GB")
        print(f"    Disponível: {mem_info['available_gb']:.1f} GB")
        print(f"    Usada: {mem_info['used_gb']:.1f} GB ({mem_info['percent']:.1f}%)")

    try:
        print("\n  Iniciando download...")

        start_time = time.time()

        # CORREÇÃO: Usar float32 para MPS (mais estável)
        if device == "mps" and not use_float16:
            torch_dtype = torch.float32
            print("  [INFO] Usando dtype: float32 (CORRIGIDO para MPS)")
            print("  [INFO] float32 usa mais memória mas evita NaN values")
        elif device == "mps" and use_float16:
            torch_dtype = torch.float16
            print("  [AVISO] Usando dtype: float16 (pode gerar NaN no MPS)")
        elif device == "cuda":
            torch_dtype = torch.float16
            print("  [INFO] Usando dtype: float16 (otimizado para CUDA)")
        else:
            torch_dtype = torch.float32
            print("  [INFO] Usando dtype: float32 (CPU)")

        # Carregar pipeline
        pipe = StableDiffusionPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=torch_dtype,
            safety_checker=None,
        )

        # Mover para device
        pipe = pipe.to(device)

        # Habilitar otimizações
        if device == "mps":
            pipe.enable_attention_slicing()
            print("  [OK] Attention slicing habilitado")

        download_time = time.time() - start_time

        print(f"\n  [OK] Modelo carregado com sucesso!")
        print(f"  Tempo de carregamento: {download_time:.2f}s")

        # Verificar memória após carregamento
        mem_info = get_memory_info()
        if mem_info:
            print(f"\n  Memória após carregamento:")
            print(f"    Disponível: {mem_info['available_gb']:.1f} GB")
            print(f"    Usada: {mem_info['used_gb']:.1f} GB ({mem_info['percent']:.1f}%)")

        return pipe

    except Exception as e:
        print(f"\n  [ERRO] Falha ao carregar modelo: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_inference(pipe: StableDiffusionPipeline, device: str) -> Dict:
    """
    Testa inferência básica com prompts relacionados a casual shoes.

    Args:
        pipe: Pipeline do Stable Diffusion
        device: Device usado

    Returns:
        Dicionário com resultados dos testes
    """
    print_step("3. Teste de Inferência")

    # Prompts de teste baseados no dataset
    test_prompts = [
        "A professional product photo of black casual shoes on white background, high quality, product photography",
        "A professional product photo of brown leather casual shoes, summer collection, centered on white background",
        "A professional product photo of white casual sneakers, men, modern design, clean white background",
    ]

    results = {
        'device': device,
        'prompts': [],
        'generation_times': [],
        'images': [],
        'valid_images': 0,
        'failed_images': 0,
    }

    print(f"  Device: {device}")
    print(f"  Número de prompts: {len(test_prompts)}")
    print(f"  Steps: 25")
    print(f"  Guidance scale: 7.5")

    # Verificar memória antes
    mem_before = get_memory_info()
    if mem_before:
        print(f"\n  Memória antes da inferência:")
        print(f"    Disponível: {mem_before['available_gb']:.1f} GB")

    for idx, prompt in enumerate(test_prompts, 1):
        print(f"\n  Teste {idx}/{len(test_prompts)}")
        print(f"  Prompt: {prompt[:70]}...")

        try:
            start_time = time.time()

            # Gerar imagem com torch.no_grad()
            with torch.no_grad():
                output = pipe(
                    prompt,
                    num_inference_steps=25,
                    guidance_scale=7.5,
                    num_images_per_prompt=1,
                )

            generation_time = time.time() - start_time
            image = output.images[0]

            # CORREÇÃO: Validar imagem antes de salvar
            image_array = np.array(image)
            print(f"  Validando imagem gerada...")
            print(f"  Shape: {image_array.shape}, dtype: {image_array.dtype}")

            is_valid = validate_image_array(image_array, prompt)

            if is_valid:
                # Salvar imagem
                output_path = OUTPUT_DIR / f"test_inference_fixed_{idx}.png"
                image.save(output_path)

                print(f"  [OK] Imagem válida gerada em {generation_time:.2f}s")
                print(f"  Salvo em: {output_path}")

                results['prompts'].append(prompt)
                results['generation_times'].append(generation_time)
                results['images'].append(str(output_path))
                results['valid_images'] += 1
            else:
                print(f"  [ERRO] Imagem inválida - não foi salva")
                results['failed_images'] += 1

        except Exception as e:
            print(f"  [ERRO] Falha na geração {idx}: {e}")
            import traceback
            traceback.print_exc()
            results['failed_images'] += 1

    # Verificar memória depois
    mem_after = get_memory_info()
    if mem_after:
        print(f"\n  Memória após inferência:")
        print(f"    Disponível: {mem_after['available_gb']:.1f} GB")
        if mem_before:
            mem_used = mem_before['available_gb'] - mem_after['available_gb']
            print(f"    Memória usada durante inferência: {mem_used:.2f} GB")

    return results


def print_summary(results: Dict):
    """Imprime sumário dos testes."""
    print_step("4. Sumário dos Testes")

    print(f"  Device: {results['device']}")
    print(f"  Imagens válidas: {results['valid_images']}")
    print(f"  Imagens falhas: {results['failed_images']}")
    print(f"  Total: {results['valid_images'] + results['failed_images']}")

    if results['valid_images'] == 0:
        print("\n  [ERRO] Nenhuma imagem válida foi gerada")
        print("  [AÇÃO] Tentar novamente com CPU ou ajustar configurações")
        return

    if not results['generation_times']:
        print("  [ERRO] Nenhum tempo registrado")
        return

    avg_time = sum(results['generation_times']) / len(results['generation_times'])
    min_time = min(results['generation_times'])
    max_time = max(results['generation_times'])

    print(f"\n  Tempo de Geração:")
    print(f"    Média: {avg_time:.2f}s por imagem")
    print(f"    Mínimo: {min_time:.2f}s")
    print(f"    Máximo: {max_time:.2f}s")

    if results['valid_images'] >= 2:
        print(f"\n  Estimativas para Treinamento:")
        validation_images = 6 * 4
        validation_time = validation_images * avg_time
        print(f"    Tempo de validação (24 imagens): ~{validation_time/60:.1f} minutos")

    print(f"\n  Imagens válidas salvas em:")
    for img_path in results['images']:
        print(f"    - {img_path}")

    if results['valid_images'] == results['valid_images'] + results['failed_images']:
        print(f"\n  [OK] Todos os testes concluídos com sucesso!")
    else:
        print(f"\n  [AVISO] Alguns testes falharam - verificar logs acima")


def main():
    """Função principal."""
    print_section("TESTE STABLE DIFFUSION 1.5 - VERSÃO CORRIGIDA")
    print("Apple M2 Max - MPS Backend")
    print("CORREÇÃO: Usando float32 para evitar NaN values no MPS")

    # Verificar device
    device = check_device()

    # Download e carregar modelo com float32 (mais estável)
    print("\n[INFO] Tentativa 1: float32 (estável, usa mais memória)")
    pipe = download_model(device, use_float16=False)

    if pipe is None:
        print("\n[ERRO] Não foi possível carregar o modelo")
        sys.exit(1)

    # Testar inferência
    results = test_inference(pipe, device)

    # Se falhou com MPS, tentar com CPU
    if results['valid_images'] == 0 and device == "mps":
        print_section("FALLBACK: Tentando com CPU")
        print("[INFO] MPS falhou - tentando CPU como fallback")

        device = "cpu"
        pipe = download_model(device, use_float16=False)

        if pipe:
            results = test_inference(pipe, device)

    # Imprimir sumário
    print_summary(results)

    print_section("TASK 1.4 - STATUS")
    if results['valid_images'] > 0:
        print("\n[OK] Teste concluído com sucesso!")
        print(f"Imagens válidas geradas: {results['valid_images']}/{results['valid_images'] + results['failed_images']}")
        print("\nPróximos Passos:")
        print("  Task 1.5: Criar script de treinamento LoRA")
    else:
        print("\n[ERRO] Teste falhou - nenhuma imagem válida")
        print("\nRecomendações:")
        print("  1. Verificar versões: PyTorch, Diffusers")
        print("  2. Tentar com CPU (mais lento mas estável)")
        print("  3. Atualizar PyTorch para versão mais recente")


if __name__ == "__main__":
    main()
