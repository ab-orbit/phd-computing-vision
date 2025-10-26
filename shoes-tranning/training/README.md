# Treinamento LoRA - Stable Diffusion 1.5 para Casual Shoes

Sistema de fine-tuning do Stable Diffusion 1.5 usando LoRA (Low-Rank Adaptation) otimizado para Apple Silicon (MPS).

**Status**: Pronto para treinamento
**Dataset**: 1,991 imagens de casual shoes (512x512 PNG)
**Modelo Base**: runwayml/stable-diffusion-v1-5
**Hardware**: Mac Studio M2 Max (32GB RAM)

---

## Índice

- [Quick Start](#quick-start)
- [Estrutura de Arquivos](#estrutura-de-arquivos)
- [Scripts Disponíveis](#scripts-disponíveis)
- [Configurações](#configurações)
- [Troubleshooting](#troubleshooting)
- [Resultados Esperados](#resultados-esperados)

---

## Quick Start

### 1. Verificar Ambiente

Certifique-se de que o ambiente está configurado (Task 1.3):

```bash
cd training/scripts
python3 ../scripts/check_environment.py
```

Deve mostrar `[OK] Ambiente pronto para treinamento!`

### 2. Testar Setup de Treinamento

Antes de iniciar o treinamento completo, valide que tudo está funcionando:

```bash
cd training/scripts
python3 test_training_setup.py
```

Este teste:
- Carrega dataset (1,991 amostras)
- Carrega modelos no MPS
- Configura LoRA
- Executa 5 forward passes
- Valida uso de memória

Deve mostrar `[OK] Todos os componentes testados com sucesso!`

### 3. Treinamento Rápido (Teste)

Execute um treinamento curto para validar o pipeline completo:

```bash
cd training/scripts
python3 train_lora.py \
  --max_train_steps 100 \
  --validation_steps 50 \
  --checkpointing_steps 50 \
  --output_dir ../outputs/test_run
```

**Duração**: ~5-10 minutos
**Objetivo**: Validar que treinamento, validação e checkpointing funcionam

### 4. Treinamento Completo

Execute o treinamento completo (3,000 steps):

```bash
cd training/scripts
python3 train_lora.py \
  --max_train_steps 3000 \
  --validation_steps 500 \
  --checkpointing_steps 500 \
  --output_dir ../outputs/lora_casual_shoes
```

**Duração Estimada**: ~3 horas no M2 Max
**Checkpoints**: Salvos a cada 500 steps em `outputs/lora_casual_shoes/checkpoints/`
**Validações**: 6 validações com 16 imagens cada

### 5. Monitorar Progresso

Durante o treinamento, acompanhe em outra janela:

```bash
# Ver logs em tempo real
tail -f ../logs/*/train_lora_casual_shoes/*/main_log.txt

# Ver imagens de validação
ls -lh ../outputs/lora_casual_shoes/validation/

# Tensorboard (se habilitado)
tensorboard --logdir ../logs
```

---

## Estrutura de Arquivos

```
training/
├── scripts/
│   ├── check_environment.py         # Verificação do ambiente (Task 1.3)
│   ├── test_sd_inference_fixed.py   # Teste SD 1.5 (Task 1.4)
│   ├── test_training_setup.py       # Teste setup de treino (Task 1.5)
│   └── train_lora.py                # Script principal de treinamento
│
├── configs/
│   └── training_config.json         # Configurações padrão
│
├── outputs/                         # Criado durante treinamento
│   └── lora_casual_shoes/
│       ├── checkpoints/             # Checkpoints a cada 500 steps
│       ├── validation/              # Imagens de validação
│       ├── lora_weights/            # Pesos LoRA finais
│       └── final_pipeline/          # Pipeline completo final
│
├── logs/                            # Logs do treinamento
│
├── docs/
│   ├── TASK_1.3_DOCUMENTATION.md
│   ├── TASK_1.4_ISSUE_REPORT.md
│   ├── TASK_1.4_FINAL_REPORT.md
│   └── TASK_1.5_DOCUMENTATION.md
│
├── ENVIRONMENT_SETUP.md             # Setup do ambiente
└── README.md                        # Este arquivo
```

---

## Scripts Disponíveis

### check_environment.py

Valida que o ambiente está configurado corretamente.

```bash
python3 check_environment.py
```

**Verifica**:
- PyTorch + MPS
- Diffusers, Transformers, PEFT
- Dataset preparado
- Memória disponível

### test_sd_inference_fixed.py

Testa geração de imagens com SD 1.5 base (sem LoRA).

```bash
python3 test_sd_inference_fixed.py
```

**Gera**: 3 imagens de teste em `outputs/`

### test_training_setup.py

Valida todo o pipeline de treinamento sem executar treinamento completo.

```bash
python3 test_training_setup.py
```

**Testa**:
- Dataset loading
- Model loading
- LoRA configuration
- Forward pass
- Memory usage

### train_lora.py

Script principal de treinamento LoRA.

```bash
python3 train_lora.py [OPTIONS]
```

**Principais opções**:

```bash
# Modelo e dados
--pretrained_model_name_or_path  # Modelo base (padrão: SD 1.5)
--train_data_dir                 # Diretório do dataset
--output_dir                     # Onde salvar outputs

# Treinamento
--train_batch_size 2             # Batch size (ajustar se OOM)
--gradient_accumulation_steps 8  # Batch efetivo = 2*8=16
--max_train_steps 3000           # Número total de steps
--learning_rate 1e-4             # Learning rate

# LoRA
--lora_rank 8                    # Rank (4, 8, 16, 32)
--lora_alpha 16                  # Alpha (tipicamente 2x rank)

# Validação e Checkpoint
--validation_steps 500           # Validar a cada N steps
--checkpointing_steps 500        # Checkpoint a cada N steps
--checkpoints_total_limit 5      # Max checkpoints a manter

# Outros
--seed 42                        # Seed para reprodutibilidade
--gradient_checkpointing         # Economia de memória
```

**Ver todas as opções**:
```bash
python3 train_lora.py --help
```

---

## Configurações

### Configurações Padrão (Recomendadas)

As configurações em `configs/training_config.json` foram otimizadas para M2 Max:

```json
{
  "train_batch_size": 2,
  "gradient_accumulation_steps": 8,
  "max_train_steps": 3000,
  "learning_rate": 1e-4,
  "lora_rank": 8,
  "lora_alpha": 16,
  "gradient_checkpointing": true
}
```

**Batch Efetivo**: 2 × 8 = 16
**Memória Esperada**: ~10-14 GB
**Tempo Estimado**: ~3 horas

### Ajustes para Diferentes Cenários

#### Memória Limitada

Se encontrar erro de memória (OOM):

```bash
python3 train_lora.py \
  --train_batch_size 1 \
  --gradient_accumulation_steps 16 \
  --gradient_checkpointing
```

#### Treinamento Mais Rápido

Se quiser treinar mais rápido (menor qualidade):

```bash
python3 train_lora.py \
  --max_train_steps 1500 \
  --lora_rank 4 \
  --lora_alpha 8
```

#### Melhor Qualidade

Para melhor qualidade (mais memória, mais lento):

```bash
python3 train_lora.py \
  --max_train_steps 5000 \
  --lora_rank 16 \
  --lora_alpha 32 \
  --train_batch_size 2
```

---

## Troubleshooting

### Erro: Out of Memory (OOM)

**Sintomas**: `RuntimeError: MPS backend out of memory`

**Soluções**:
1. Reduzir batch_size para 1
2. Aumentar gradient_accumulation_steps para 16
3. Verificar se gradient_checkpointing está habilitado
4. Fechar aplicações pesadas

```bash
python3 train_lora.py --train_batch_size 1 --gradient_accumulation_steps 16
```

### Erro: Imagens de Validação Pretas

**Sintomas**: Imagens em `validation/` estão todas pretas

**Causa**: float16 sendo usado no MPS

**Solução**: Verificar que está usando float32 (padrão no script)

### Erro: Dataset não encontrado

**Sintomas**: `FileNotFoundError: Captions não encontrado`

**Solução**: Verificar que Task 1.2 foi executada:

```bash
ls -lh ../../data/casual_shoes/train/
# Deve mostrar: images/, captions.json, ids.txt
```

### Treinamento Muito Lento

**Sintomas**: >5s por step

**Diagnósticos**:
1. Verificar que está usando MPS:
   ```python
   import torch
   print(torch.backends.mps.is_available())  # Deve ser True
   ```

2. Verificar num_workers:
   ```bash
   python3 train_lora.py --dataloader_num_workers 0
   ```

### Loss não Diminui

**Sintomas**: Loss fica constante ou aumenta

**Soluções**:
1. Verificar learning rate (tentar 5e-5 ou 2e-4)
2. Aumentar warmup steps (--lr_warmup_steps 1000)
3. Verificar dataset (todas imagens carregando?)

---

## Resultados Esperados

### Durante Treinamento

**Loss**:
- Inicial: ~0.08-0.10
- Após 500 steps: ~0.04-0.06
- Após 1500 steps: ~0.02-0.03
- Após 3000 steps: ~0.01-0.02

**Performance**:
- ~2-3s por step (batch_size=2, grad_accum=8)
- ~30-40 steps/min
- Validação: ~45s para 16 imagens

### Imagens de Validação

**Progressão Esperada**:

**Steps 0-500**:
- Formas básicas de sapatos aparecem
- Backgrounds ainda caóticos
- Cores aleatórias

**Steps 500-1500**:
- Sapatos mais definidos
- Backgrounds começam a ficar mais limpos
- Cores respondem melhor aos prompts

**Steps 1500-3000**:
- Sapatos realistas e detalhados
- Backgrounds brancos ou neutros
- Cores corretas conforme prompt
- Estilo de product photography evidente

### Outputs Finais

Após treinamento completo (3000 steps):

```
outputs/lora_casual_shoes/
├── lora_weights/              # ~3-5 MB (apenas LoRA)
│   └── adapter_model.safetensors
├── final_pipeline/            # ~4 GB (pipeline completo)
│   ├── model_index.json
│   ├── unet/
│   ├── vae/
│   └── text_encoder/
├── checkpoints/               # Checkpoints intermediários
│   ├── checkpoint-500/
│   ├── checkpoint-1000/
│   ├── checkpoint-1500/
│   ├── checkpoint-2000/
│   └── checkpoint-2500/
└── validation/                # ~100-150 imagens
    └── epoch000_step*_*.png
```

---

## Próximos Passos

Após o treinamento:

### 1. Avaliar Qualidade

```bash
# Ver todas as imagens de validação
open ../outputs/lora_casual_shoes/validation/
```

### 2. Gerar Novas Imagens

Criar script de geração usando o modelo treinado:

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

image.save("generated_red_shoes.png")
```

### 3. Gerar Dataset Sintético

Usar o modelo treinado para gerar 3,000-5,000 imagens sintéticas de casual shoes para expansão do dataset original.

### 4. Avaliar Métricas

Calcular métricas de qualidade:
- FID (Fréchet Inception Distance)
- CLIP Score (consistência imagem-texto)
- Diversidade de outputs

---

## Referências

- **Documentação**: `docs/TASK_1.5_DOCUMENTATION.md`
- **Setup Ambiente**: `ENVIRONMENT_SETUP.md`
- **Problema MPS float16**: `docs/TASK_1.4_ISSUE_REPORT.md`
- **Diffusers**: https://huggingface.co/docs/diffusers
- **PEFT/LoRA**: https://huggingface.co/docs/peft
- **Stable Diffusion**: https://github.com/CompVis/stable-diffusion

---

**Última Atualização**: 2025-10-26
**Task**: 1.5 - Script de Treinamento LoRA
**Status**: PRONTO PARA TREINAMENTO
