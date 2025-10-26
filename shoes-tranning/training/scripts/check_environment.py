"""
Script para verificar o ambiente de treinamento.

Verifica:
- PyTorch e suporte MPS
- Diffusers e Transformers
- PEFT e LoRA
- Memória disponível
- Versões das bibliotecas
"""

import sys
import platform
from pathlib import Path


def print_header(text):
    """Imprime cabeçalho formatado."""
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80)


def print_section(text):
    """Imprime seção formatada."""
    print(f"\n{text}")
    print("-" * 80)


def check_python():
    """Verifica versão do Python."""
    print_section("1. Python")

    version = sys.version_info
    print(f"  Versão: {version.major}.{version.minor}.{version.micro}")
    print(f"  Executável: {sys.executable}")
    print(f"  Plataforma: {platform.platform()}")
    print(f"  Arquitetura: {platform.machine()}")

    if version.major == 3 and version.minor >= 10:
        print("  [OK] Python 3.10+ detectado")
        return True
    else:
        print("  [AVISO] Recomendado Python 3.10+")
        return False


def check_pytorch():
    """Verifica PyTorch e suporte MPS."""
    print_section("2. PyTorch e MPS")

    try:
        import torch

        print(f"  PyTorch versão: {torch.__version__}")
        print(f"  CUDA disponível: {torch.cuda.is_available()}")

        # Verificar MPS (Apple Silicon)
        if hasattr(torch.backends, 'mps'):
            mps_available = torch.backends.mps.is_available()
            mps_built = torch.backends.mps.is_built()

            print(f"  MPS disponível: {mps_available}")
            print(f"  MPS built: {mps_built}")

            if mps_available:
                print("  [OK] MPS disponível para treinamento!")

                # Testar criação de tensor
                try:
                    device = torch.device("mps")
                    x = torch.randn(10, 10).to(device)
                    print(f"  [OK] Teste de tensor MPS: OK")
                    print(f"  Device: {device}")
                    return True
                except Exception as e:
                    print(f"  [ERRO] Falha ao criar tensor MPS: {e}")
                    return False
            else:
                print("  [AVISO] MPS não disponível")
                return False
        else:
            print("  [AVISO] torch.backends.mps não encontrado")
            print("  Recomendado: PyTorch 2.0+ para suporte MPS")
            return False

    except ImportError:
        print("  [ERRO] PyTorch não instalado")
        return False


def check_diffusers():
    """Verifica Diffusers e Transformers."""
    print_section("3. Diffusers e Transformers")

    try:
        import diffusers
        print(f"  Diffusers versão: {diffusers.__version__}")
        print("  [OK] Diffusers instalado")

        # Verificar componentes principais
        try:
            from diffusers import StableDiffusionPipeline, DDPMScheduler
            print("  [OK] StableDiffusionPipeline disponível")
        except ImportError as e:
            print(f"  [AVISO] Erro ao importar componentes: {e}")

    except ImportError:
        print("  [ERRO] Diffusers não instalado")
        return False

    try:
        import transformers
        print(f"  Transformers versão: {transformers.__version__}")
        print("  [OK] Transformers instalado")
    except ImportError:
        print("  [ERRO] Transformers não instalado")
        return False

    return True


def check_accelerate():
    """Verifica Accelerate."""
    print_section("4. Accelerate")

    try:
        import accelerate
        print(f"  Accelerate versão: {accelerate.__version__}")
        print("  [OK] Accelerate instalado")
        return True
    except ImportError:
        print("  [ERRO] Accelerate não instalado")
        return False


def check_peft():
    """Verifica PEFT para LoRA."""
    print_section("5. PEFT (LoRA)")

    try:
        import peft
        print(f"  PEFT versão: {peft.__version__}")
        print("  [OK] PEFT instalado")

        # Verificar LoRA config
        try:
            from peft import LoraConfig, get_peft_model
            print("  [OK] LoraConfig disponível")
        except ImportError as e:
            print(f"  [AVISO] Erro ao importar LoRA: {e}")

        return True
    except ImportError:
        print("  [ERRO] PEFT não instalado")
        return False


def check_optional_packages():
    """Verifica pacotes opcionais."""
    print_section("6. Pacotes Opcionais")

    packages = {
        'xformers': 'Otimizações de atenção',
        'wandb': 'Tracking de experimentos',
        'tensorboard': 'Visualização de métricas',
        'bitsandbytes': 'Quantização',
    }

    for package, description in packages.items():
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown')
            print(f"  [OK] {package} ({description}): {version}")
        except ImportError:
            print(f"  [INFO] {package} ({description}): Não instalado (opcional)")


def check_datasets():
    """Verifica datasets e PIL."""
    print_section("7. Datasets e Processamento")

    try:
        import datasets
        print(f"  Datasets versão: {datasets.__version__}")
        print("  [OK] Datasets instalado")
    except ImportError:
        print("  [ERRO] Datasets não instalado")
        return False

    try:
        from PIL import Image
        print(f"  PIL/Pillow versão: {Image.__version__}")
        print("  [OK] Pillow instalado")
    except ImportError:
        print("  [ERRO] Pillow não instalado")
        return False

    return True


def check_memory():
    """Verifica memória disponível."""
    print_section("8. Memória do Sistema")

    try:
        import psutil

        mem = psutil.virtual_memory()
        total_gb = mem.total / (1024**3)
        available_gb = mem.available / (1024**3)
        used_gb = mem.used / (1024**3)
        percent = mem.percent

        print(f"  Total: {total_gb:.1f} GB")
        print(f"  Usado: {used_gb:.1f} GB ({percent:.1f}%)")
        print(f"  Disponível: {available_gb:.1f} GB")

        if available_gb < 8:
            print("  [AVISO] Menos de 8GB disponível - pode ser insuficiente")
        elif available_gb < 16:
            print("  [INFO] 8-16GB disponível - suficiente para batch pequeno")
        else:
            print("  [OK] 16GB+ disponível - ótimo para treinamento")

    except ImportError:
        print("  [INFO] psutil não instalado - não foi possível verificar memória")


def check_dataset_paths():
    """Verifica se os datasets preparados existem."""
    print_section("9. Datasets Preparados")

    base_path = Path("/Users/jwcunha/Documents/COMPANIES/AB/repos/private/premium/researcher/phd-classes/shoes-tranning/data/casual_shoes")

    if not base_path.exists():
        print(f"  [AVISO] Dataset não encontrado em: {base_path}")
        return False

    print(f"  Dataset base: {base_path}")

    for split in ['train', 'val', 'test']:
        split_path = base_path / split / "images"
        if split_path.exists():
            n_images = len(list(split_path.glob("*.png")))
            print(f"  [OK] {split}: {n_images:,} imagens")
        else:
            print(f"  [AVISO] {split}: Diretório não encontrado")

    return True


def test_sd_components():
    """Testa carregamento de componentes do SD."""
    print_section("10. Teste de Componentes SD")

    try:
        import torch
        from diffusers import UNet2DConditionModel, AutoencoderKL
        from transformers import CLIPTextModel, CLIPTokenizer

        print("  Testando componentes do Stable Diffusion...")

        # Apenas verificar se consegue importar
        print("  [OK] UNet2DConditionModel importado")
        print("  [OK] AutoencoderKL importado")
        print("  [OK] CLIPTextModel importado")
        print("  [OK] CLIPTokenizer importado")

        # Verificar se pode criar modelo pequeno
        print("\n  Testando criação de modelo pequeno...")
        try:
            device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
            print(f"  Device para teste: {device}")

            # Criar tensor pequeno
            x = torch.randn(1, 4, 64, 64).to(device)
            print("  [OK] Tensor de teste criado no device")

            return True
        except Exception as e:
            print(f"  [AVISO] Erro ao testar device: {e}")
            return True  # Não é crítico

    except Exception as e:
        print(f"  [ERRO] Falha ao importar componentes: {e}")
        return False


def create_summary():
    """Cria sumário final."""
    print_header("RESUMO DA VERIFICAÇÃO")

    checks = {
        'Python 3.10+': check_python(),
        'PyTorch + MPS': check_pytorch(),
        'Diffusers': check_diffusers(),
        'Accelerate': check_accelerate(),
        'PEFT (LoRA)': check_peft(),
        'Datasets': check_datasets(),
        'Dataset Preparado': check_dataset_paths(),
        'Componentes SD': test_sd_components(),
    }

    print("\nStatus dos componentes:")
    for component, status in checks.items():
        status_str = "[OK]" if status else "[ERRO]"
        print(f"  {status_str} {component}")

    # Verificar opcionais separadamente
    check_optional_packages()
    check_memory()

    all_critical_ok = all(checks.values())

    print("\n" + "=" * 80)
    if all_critical_ok:
        print("[OK] Ambiente pronto para treinamento!")
        print("\nPróximos passos:")
        print("  1. Task 1.4: Download e teste de SD 1.5")
        print("  2. Task 1.5: Criar script de treinamento LoRA")
    else:
        print("[ERRO] Ambiente incompleto")
        print("\nInstale as dependências faltantes:")
        print("  pip install -r training/requirements-training.txt")
    print("=" * 80)

    return all_critical_ok


def main():
    """Função principal."""
    print_header("VERIFICAÇÃO DO AMBIENTE DE TREINAMENTO")
    print("Apple M2 Max - Stable Diffusion 1.5 + LoRA")

    create_summary()


if __name__ == "__main__":
    main()
