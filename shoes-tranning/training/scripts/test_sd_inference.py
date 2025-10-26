"""
Script para testar Stable Diffusion 1.5 com MPS.

Objetivos:
- Download e cache do modelo SD 1.5
- Teste de inferência básica
- Medição de tempo de geração
- Validação de memória e performance

Modelo: runwayml/stable-diffusion-v1-5
Device: MPS (Apple Silicon)
"""

import sys
import time
from pathlib import Path
from typing import Dict, Optional

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

    if torch.backends.mps.is_available():
        device = "mps"
        print(f"[OK] MPS disponível")
        print(f"  Device: {device}")
    elif torch.cuda.is_available():
        device = "cuda"
        print(f"[OK] CUDA disponível")
        print(f"  Device: {device}")
    else:
        device = "cpu"
        print(f"[AVISO] Usando CPU - treinamento será lento")
        print(f"  Device: {device}")

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


def download_model(device: str) -> Optional[StableDiffusionPipeline]:
    """
    Faz download e carrega o modelo SD 1.5.

    Args:
        device: Device para carregar o modelo ('mps', 'cuda', 'cpu')

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
        print("  [INFO] Primeira execução: ~4GB de download")
        print("  [INFO] Execuções futuras: modelo em cache")

        start_time = time.time()

        # Determinar dtype baseado no device
        if device == "mps":
            # MPS funciona melhor com float16
            torch_dtype = torch.float16
            print("  [INFO] Usando dtype: float16 (otimizado para MPS)")
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
            safety_checker=None,  # Desabilitar safety checker para velocidade
        )

        # Mover para device
        pipe = pipe.to(device)

        # Habilitar otimizações
        if device == "mps":
            # MPS-specific optimizations
            pipe.enable_attention_slicing()
            print("  [OK] Attention slicing habilitado (economia de memória)")

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
        'images': []
    }

    print(f"  Device: {device}")
    print(f"  Número de prompts: {len(test_prompts)}")
    print(f"  Steps: 25 (padrão)")
    print(f"  Guidance scale: 7.5 (padrão)")

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

            # Gerar imagem
            with torch.no_grad():
                output = pipe(
                    prompt,
                    num_inference_steps=25,
                    guidance_scale=7.5,
                    num_images_per_prompt=1,
                )

            generation_time = time.time() - start_time
            image = output.images[0]

            # Salvar imagem
            output_path = OUTPUT_DIR / f"test_inference_{idx}.png"
            image.save(output_path)

            print(f"  [OK] Imagem gerada em {generation_time:.2f}s")
            print(f"  Salvo em: {output_path}")

            results['prompts'].append(prompt)
            results['generation_times'].append(generation_time)
            results['images'].append(str(output_path))

        except Exception as e:
            print(f"  [ERRO] Falha na geração {idx}: {e}")
            import traceback
            traceback.print_exc()

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

    if not results['generation_times']:
        print("  [ERRO] Nenhuma imagem foi gerada com sucesso")
        return

    avg_time = sum(results['generation_times']) / len(results['generation_times'])
    min_time = min(results['generation_times'])
    max_time = max(results['generation_times'])

    print(f"  Device: {results['device']}")
    print(f"  Imagens geradas: {len(results['images'])}")
    print(f"\n  Tempo de Geração:")
    print(f"    Média: {avg_time:.2f}s por imagem")
    print(f"    Mínimo: {min_time:.2f}s")
    print(f"    Máximo: {max_time:.2f}s")

    print(f"\n  Estimativas para Treinamento:")
    # Estimativa: ~3000 steps, validação a cada 500 steps = 6 validações
    validation_images = 6 * 4  # 6 validações x 4 imagens
    validation_time = validation_images * avg_time
    print(f"    Tempo de validação (24 imagens): ~{validation_time/60:.1f} minutos")

    print(f"\n  Imagens salvas em:")
    for img_path in results['images']:
        print(f"    - {img_path}")

    print(f"\n  [OK] Testes concluídos com sucesso!")


def check_cache():
    """Verifica se o modelo já está em cache."""
    print_step("Verificação de Cache")

    model_cache_pattern = "models--runwayml--stable-diffusion-v1-5"

    if CACHE_DIR.exists():
        cache_dirs = list(CACHE_DIR.glob(f"*{model_cache_pattern}*"))
        if cache_dirs:
            cache_dir = cache_dirs[0]
            print(f"  [OK] Modelo encontrado em cache")
            print(f"  Localização: {cache_dir}")

            # Tentar calcular tamanho
            try:
                total_size = sum(
                    f.stat().st_size
                    for f in cache_dir.rglob('*')
                    if f.is_file()
                )
                size_gb = total_size / (1024**3)
                print(f"  Tamanho: {size_gb:.2f} GB")
            except:
                pass

            return True
        else:
            print(f"  [INFO] Modelo não encontrado em cache")
            print(f"  [INFO] Será necessário download (~4GB)")
            return False
    else:
        print(f"  [INFO] Diretório de cache não existe")
        return False


def main():
    """Função principal."""
    print_section("TESTE STABLE DIFFUSION 1.5 - TASK 1.4")
    print("Apple M2 Max - MPS Backend")

    # Verificar cache
    check_cache()

    # Verificar device
    device = check_device()

    # Download e carregar modelo
    pipe = download_model(device)

    if pipe is None:
        print("\n[ERRO] Não foi possível carregar o modelo")
        print("Verifique a conexão com internet e tente novamente")
        sys.exit(1)

    # Testar inferência
    results = test_inference(pipe, device)

    # Imprimir sumário
    print_summary(results)

    print_section("TASK 1.4 CONCLUÍDA")
    print("\nPróximos Passos:")
    print("  Task 1.5: Criar script de treinamento LoRA")
    print("  - Implementar loop de treinamento")
    print("  - Configurar LoRA")
    print("  - Adicionar validação e checkpoints")


if __name__ == "__main__":
    main()
