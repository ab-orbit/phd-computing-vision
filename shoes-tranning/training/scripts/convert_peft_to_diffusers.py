"""
Script para converter pesos LoRA de formato PEFT para formato Diffusers.

Remove o prefixo 'base_model.model.' das chaves para compatibilidade com diffusers.
"""

import sys
from pathlib import Path
import safetensors.torch

def convert_peft_lora_to_diffusers(input_path: Path, output_path: Path = None):
    """
    Converte arquivo LoRA de PEFT para Diffusers.

    Args:
        input_path: Caminho para adapter_model.safetensors (formato PEFT)
        output_path: Caminho de saída (padrão: pytorch_lora_weights.safetensors)
    """
    if output_path is None:
        output_path = input_path.parent / "pytorch_lora_weights.safetensors"

    print(f"Carregando pesos LoRA de: {input_path}")

    # Carregar pesos originais
    state_dict = safetensors.torch.load_file(str(input_path))

    print(f"Total de chaves carregadas: {len(state_dict)}")

    # Remover prefixo 'base_model.model.'
    converted_state_dict = {}
    prefix_to_remove = "base_model.model."

    for key, value in state_dict.items():
        if key.startswith(prefix_to_remove):
            new_key = key[len(prefix_to_remove):]
            converted_state_dict[new_key] = value
            if len(converted_state_dict) <= 5:
                print(f"  Convertido: {key} -> {new_key}")
        else:
            converted_state_dict[key] = value
            print(f"  Mantido: {key}")

    print(f"\nTotal de chaves convertidas: {len(converted_state_dict)}")

    # Salvar pesos convertidos
    print(f"\nSalvando pesos convertidos em: {output_path}")
    safetensors.torch.save_file(converted_state_dict, str(output_path))

    print("Conversão concluída com sucesso!")

    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python convert_peft_to_diffusers.py <caminho_para_lora_weights_dir>")
        print("Exemplo: python convert_peft_to_diffusers.py ../outputs/lora_casual_shoes_3000steps/lora_weights")
        sys.exit(1)

    lora_weights_dir = Path(sys.argv[1])
    input_file = lora_weights_dir / "adapter_model.safetensors"

    if not input_file.exists():
        print(f"Erro: Arquivo não encontrado: {input_file}")
        sys.exit(1)

    convert_peft_lora_to_diffusers(input_file)
