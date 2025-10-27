"""
Script para testar carregamento de checkpoint convertido.
"""

import sys
from pathlib import Path

# Adicionar caminho para imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from diffusers import StableDiffusionPipeline
import torch

checkpoint_path = Path(__file__).parent.parent / "outputs" / "lora_casual_shoes_3000steps_full" / "checkpoint_pipelines" / "checkpoint-500"

print(f"Testando carregamento de: {checkpoint_path}")
print(f"Checkpoint existe: {checkpoint_path.exists()}")
print()

# Listar arquivos
print("Estrutura do checkpoint:")
for item in sorted(checkpoint_path.rglob("*")):
    if item.is_file():
        size = item.stat().st_size / (1024**2)  # MB
        print(f"  {item.relative_to(checkpoint_path)}: {size:.2f} MB")
print()

# Verificar model_index.json
model_index = checkpoint_path / "model_index.json"
if model_index.exists():
    import json
    with open(model_index) as f:
        data = json.load(f)
    print("model_index.json:")
    for key, value in data.items():
        print(f"  {key}: {value}")
    print()

# Tentar carregar
print("Tentando carregar pipeline...")
try:
    pipeline = StableDiffusionPipeline.from_pretrained(
        str(checkpoint_path),
        torch_dtype=torch.float32,
        safety_checker=None,
        local_files_only=True
    )
    print("✓ Pipeline carregado com sucesso!")
    print(f"  Componentes: {list(pipeline.components.keys())}")
except Exception as e:
    print(f"✗ Erro ao carregar pipeline:")
    print(f"  {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
