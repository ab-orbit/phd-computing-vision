# Guia de Referência Rápida - Casual Shoes Training

**Última Atualização**: 2025-10-26
**Sprint**: 1 (Completo)

---

## Comandos Essenciais

### 1. Verificar Ambiente

```bash
cd training/scripts
python3 check_environment.py
```

**Esperado**: `[OK] Ambiente pronto para treinamento!`

---

### 2. Testar Setup de Treinamento

```bash
cd training/scripts
python3 test_training_setup.py
```

**Esperado**: `[OK] Todos os componentes testados com sucesso!`
**Duração**: ~2 minutos

---

### 3. Teste Rápido (100 steps)

```bash
cd training/scripts
python3 train_lora.py \
  --max_train_steps 100 \
  --validation_steps 50 \
  --checkpointing_steps 50 \
  --output_dir ../outputs/test_run
```

**Duração**: ~5-10 minutos
**Objetivo**: Validar pipeline completo

---

### 4. Treinamento Completo

```bash
cd training/scripts
python3 train_lora.py \
  --max_train_steps 3000 \
  --validation_steps 500 \
  --checkpointing_steps 500 \
  --output_dir ../outputs/lora_casual_shoes
```

**Duração**: ~3 horas
**Output**: `../outputs/lora_casual_shoes/`

---

### 5. Monitorar Progresso

```bash
# Ver logs em tempo real
tail -f ../logs/*/train_lora_casual_shoes/*/main_log.txt

# Ver imagens de validação
ls -lh ../outputs/lora_casual_shoes/validation/

# Contar checkpoints
ls -d ../outputs/lora_casual_shoes/checkpoints/checkpoint-* | wc -l
```

---

### 6. Continuar de Checkpoint

```bash
cd training/scripts
python3 train_lora.py \
  --resume_from_checkpoint ../outputs/lora_casual_shoes/checkpoints/checkpoint-1500 \
  --max_train_steps 3000 \
  --output_dir ../outputs/lora_casual_shoes
```

---

## Configurações Comuns

### Memória Limitada (OOM)

```bash
python3 train_lora.py \
  --train_batch_size 1 \
  --gradient_accumulation_steps 16 \
  --gradient_checkpointing
```

### Treinamento Rápido (Menor Qualidade)

```bash
python3 train_lora.py \
  --max_train_steps 1500 \
  --lora_rank 4 \
  --lora_alpha 8
```

### Máxima Qualidade

```bash
python3 train_lora.py \
  --max_train_steps 5000 \
  --lora_rank 16 \
  --lora_alpha 32 \
  --learning_rate 5e-5
```

---

## Estrutura de Diretórios

```
training/
├── scripts/           # Scripts principais
├── configs/           # Configurações
├── outputs/           # Outputs do treino
├── logs/              # Logs
└── docs/              # Documentação
```

---

## Arquivos Importantes

| Arquivo | Descrição |
|---------|-----------|
| `train_lora.py` | Script principal de treinamento |
| `test_training_setup.py` | Teste completo do setup |
| `check_environment.py` | Verificação do ambiente |
| `training_config.json` | Configurações padrão |
| `README.md` | Guia completo de uso |

---

## Troubleshooting Rápido

### Erro: Out of Memory

```bash
# Solução 1: Reduzir batch size
--train_batch_size 1 --gradient_accumulation_steps 16

# Solução 2: Fechar apps pesadas e reiniciar
```

### Erro: Dataset não encontrado

```bash
# Verificar que Task 1.2 foi executada
ls -lh ../../data/casual_shoes/train/
# Deve mostrar: images/, captions.json
```

### Erro: Loss = NaN

```bash
# Verificar que está usando float32 (não float16)
# Reduzir learning rate
--learning_rate 5e-5
```

### Imagens de Validação Pretas

```bash
# Problema: float16 no MPS
# Solução: Script usa float32 por padrão
# Verificar no código: weight_dtype = torch.float32
```

---

## Outputs Esperados

### Durante Treinamento

```
Step   Loss    Status
----   ----    ------
0      0.09    Inicial
500    0.05    Aprendendo
1500   0.03    Convergindo
3000   0.01    Excelente
```

### Após Treinamento

```
outputs/lora_casual_shoes/
├── checkpoints/        # 5 checkpoints (~100 MB)
├── validation/         # ~100 imagens PNG
├── lora_weights/       # Pesos LoRA (~3-5 MB)
└── final_pipeline/     # Pipeline completo (~4 GB)
```

---

## Próximos Passos (Após Treinamento)

### 1. Gerar Nova Imagem

```python
from diffusers import StableDiffusionPipeline

pipe = StableDiffusionPipeline.from_pretrained(
    "../outputs/lora_casual_shoes/final_pipeline"
)
pipe = pipe.to("mps")

image = pipe(
    "A professional product photo of red casual shoes on white background",
    num_inference_steps=25,
).images[0]

image.save("red_shoes.png")
```

### 2. Gerar Dataset Sintético

```python
# Loop para gerar múltiplas imagens
colors = ["black", "brown", "white", "blue", "red", "grey"]
for i, color in enumerate(colors):
    for j in range(100):
        prompt = f"A professional product photo of {color} casual shoes on white background"
        image = pipe(prompt).images[0]
        image.save(f"synthetic/{color}_{j:03d}.png")
```

---

## Métricas de Performance

| Métrica | Valor |
|---------|-------|
| Tempo/step | ~2.5s |
| Tempo/validação | ~45s (16 imagens) |
| Memória total | ~13 GB |
| Memória disponível | ~5-6 GB |
| Steps totais | 3000 |
| Tempo total | ~3 horas |

---

## Links Úteis

### Documentação Local

- `training/README.md` - Guia completo
- `training/ENVIRONMENT_SETUP.md` - Setup do ambiente
- `training/docs/TASK_1.5_DOCUMENTATION.md` - Documentação técnica
- `SPRINT_1_SUMMARY.md` - Sumário do Sprint 1

### Documentação Externa

- [Diffusers Docs](https://huggingface.co/docs/diffusers)
- [PEFT/LoRA Docs](https://huggingface.co/docs/peft)
- [PyTorch MPS](https://pytorch.org/docs/stable/notes/mps.html)

---

## Comandos de Depuração

### Verificar GPU/MPS

```python
import torch
print(f"MPS available: {torch.backends.mps.is_available()}")
print(f"MPS built: {torch.backends.mps.is_built()}")
```

### Verificar Memória

```python
import psutil
mem = psutil.virtual_memory()
print(f"Available: {mem.available / (1024**3):.1f} GB")
```

### Verificar Dataset

```bash
# Contar imagens
find ../../data/casual_shoes/train/images -name "*.png" | wc -l
# Esperado: 1991

# Verificar captions
cat ../../data/casual_shoes/train/captions.json | jq length
# Esperado: 1991
```

---

## Notas Importantes

### CRÍTICO: float32 no MPS

- Sempre usar `torch.float32` (não float16)
- float16 causa NaN values no MPS
- Problema documentado em `docs/TASK_1.4_ISSUE_REPORT.md`

### Otimizações Essenciais

- Gradient checkpointing: Reduz memória ~40%
- Attention slicing: Reduz picos ~30%
- Batch size 2 + grad accum 8: Batch efetivo 16

### LoRA Settings

- Rank 8 = balanço eficiência/qualidade
- Rank 4 = mais rápido, menor qualidade
- Rank 16 = melhor qualidade, mais lento

---

## Status do Projeto

**Sprint 1**: COMPLETO (5/5 tasks)
**Próximo**: Executar treinamento completo
**Sistema**: PRONTO PARA PRODUÇÃO

---

**Última Atualização**: 2025-10-26
**Versão**: 1.0
**Status**: PRONTO
