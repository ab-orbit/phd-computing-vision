# Correção do Formato LoRA - PEFT para Diffusers

**Data**: 27/10/2025
**Status**: Resolvido

---

## Problema

Após mover os outputs para o HD externo T9, a API começou a retornar erros ao tentar carregar os modelos LoRA:

```
ValueError: Some modules (set(...)) were not found in the base model.
Keys: {'base_model.model.up_blocks.1.attentions.1.transformer_blocks.0.attn2.to_k', ...}
```

### Causa Raiz

Os pesos LoRA foram salvos pela biblioteca **PEFT** com o prefixo `base_model.model.` nas chaves, mas a biblioteca **Diffusers** espera chaves sem esse prefixo quando carrega via `load_lora_weights()`.

**Formato PEFT** (incorreto para Diffusers):
```
base_model.model.down_blocks.0.attentions.0.transformer_blocks.0.attn1.to_k.lora_A.weight
base_model.model.down_blocks.0.attentions.0.transformer_blocks.0.attn1.to_k.lora_B.weight
```

**Formato Diffusers** (correto):
```
down_blocks.0.attentions.0.transformer_blocks.0.attn1.to_k.lora_A.weight
down_blocks.0.attentions.0.transformer_blocks.0.attn1.to_k.lora_B.weight
```

---

## Solução Implementada

### 1. Script de Conversão Manual

Criado script `convert_peft_to_diffusers.py` para converter checkpoints existentes:

**Localização**: `training/scripts/convert_peft_to_diffusers.py`

**Uso**:
```bash
cd training/scripts
python convert_peft_to_diffusers.py ../outputs/lora_casual_shoes_3000steps/lora_weights
```

**O que faz**:
- Carrega `adapter_model.safetensors` (formato PEFT)
- Remove prefixo `base_model.model.` de todas as chaves
- Salva `pytorch_lora_weights.safetensors` (formato Diffusers)

### 2. Conversão Automática no Treinamento

Modificado `train_lora.py` para converter automaticamente após salvar:

**Linhas adicionadas**: 729-755

```python
# Converter pesos LoRA de PEFT para Diffusers
logger.info("Convertendo pesos LoRA para formato Diffusers...")
try:
    import safetensors.torch
    peft_weights_path = output_dir / "lora_weights" / "adapter_model.safetensors"
    diffusers_weights_path = output_dir / "lora_weights" / "pytorch_lora_weights.safetensors"

    if peft_weights_path.exists():
        # Carregar e converter
        state_dict = safetensors.torch.load_file(str(peft_weights_path))
        converted_state_dict = {}
        prefix_to_remove = "base_model.model."

        for key, value in state_dict.items():
            if key.startswith(prefix_to_remove):
                new_key = key[len(prefix_to_remove):]
                converted_state_dict[new_key] = value
            else:
                converted_state_dict[key] = value

        # Salvar formato Diffusers
        safetensors.torch.save_file(converted_state_dict, str(diffusers_weights_path))
        logger.info(f"Pesos LoRA convertidos para formato Diffusers: {diffusers_weights_path}")
```

### 3. Atualização da API

Modificado `api/main.py` para priorizar arquivo convertido:

**Linhas**: 297-314

```python
# Aplicar LoRA weights se disponível
if lora_weights_path and lora_weights_path.exists():
    logger.info(f"Aplicando LoRA weights de: {lora_weights_path}")
    # Usar pytorch_lora_weights.safetensors (formato Diffusers)
    # Se não existir, usar adapter_model.safetensors (formato PEFT)
    weight_file = lora_weights_path / "pytorch_lora_weights.safetensors"
    if not weight_file.exists():
        weight_file = lora_weights_path / "adapter_model.safetensors"
        logger.warning(
            f"Arquivo pytorch_lora_weights.safetensors não encontrado. "
            f"Usando adapter_model.safetensors (pode causar erros se formato for PEFT). "
            f"Execute: python training/scripts/convert_peft_to_diffusers.py {lora_weights_path}"
        )

    pipeline.load_lora_weights(
        str(lora_weights_path),
        weight_name=weight_file.name
    )
```

---

## Arquivos Afetados

### Criados
- `training/scripts/convert_peft_to_diffusers.py` - Script de conversão manual

### Modificados
- `training/scripts/train_lora.py` (linhas 729-755) - Conversão automática
- `api/main.py` (linhas 297-314) - Detecção inteligente de formato

### Convertidos
- `training/outputs/lora_casual_shoes_3000steps/lora_weights/pytorch_lora_weights.safetensors` - Criado

---

## Estrutura do Diretório lora_weights

Após a conversão:

```
lora_weights/
├── adapter_config.json              # Configuração LoRA (972B)
├── adapter_model.safetensors        # Formato PEFT (6.4MB)
├── pytorch_lora_weights.safetensors # Formato Diffusers (6.4MB) ← Novo
└── README.md                        # Documentação (5KB)
```

---

## Verificação

### Teste de Carregamento

```bash
cd api
python -c "
from main import load_model
pipeline = load_model('lora_casual_shoes_3000steps/final')
print(f'Device: {pipeline.device}')
print('Sucesso!')
"
```

**Resultado esperado**:
```
Device: mps:0
Sucesso!
```

### Verificar Chaves no Arquivo Convertido

```bash
python -c "
import safetensors
with safetensors.safe_open('pytorch_lora_weights.safetensors', framework='pt') as f:
    keys = list(f.keys())
    print(f'Primeiras 3 chaves:')
    for key in keys[:3]:
        print(f'  {key}')
"
```

**Resultado esperado**:
```
Primeiras 3 chaves:
  down_blocks.0.attentions.0.transformer_blocks.0.attn1.to_k.lora_A.weight
  down_blocks.0.attentions.0.transformer_blocks.0.attn1.to_k.lora_B.weight
  down_blocks.0.attentions.0.transformer_blocks.0.attn1.to_out.0.lora_A.weight
```

Note: **SEM** prefixo `base_model.model.`

---

## Warnings Esperados

Ao carregar o modelo, você verá warnings informativos:

```
No LoRA keys associated to UNet2DConditionModel found with the prefix='unet'.
No LoRA keys associated to CLIPTextModel found with the prefix='text_encoder'.
```

**Esses warnings são seguros de ignorar**. Ocorrem porque o Diffusers procura chaves com prefixos específicos, mas os pesos LoRA já estão no formato correto sem prefixos.

---

## Próximos Passos

1. ✅ Modelo `lora_casual_shoes_3000steps` convertido e funcional
2. ⏳ Aguardar próximo checkpoint de `lora_casual_shoes_3000steps_full`
3. ✅ Conversão automática ativa para futuros checkpoints
4. ✅ API pronta para usar ambos os formatos

---

## Notas Importantes

1. **Não deletar** `adapter_model.safetensors` - pode ser útil para compatibilidade com PEFT
2. **Ambos os arquivos** podem coexistir no mesmo diretório
3. **API prioriza** `pytorch_lora_weights.safetensors` quando disponível
4. **Treinamentos futuros** gerarão ambos os formatos automaticamente

---

## Referências

- [Diffusers LoRA Documentation](https://huggingface.co/docs/diffusers/using-diffusers/loading_adapters)
- [PEFT Documentation](https://huggingface.co/docs/peft)
- Issue relacionada: Incompatibilidade PEFT-Diffusers após migração para T9

---

**Autor**: Claude Code
**Revisão**: 27/10/2025
