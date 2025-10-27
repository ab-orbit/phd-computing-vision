# Guia de Recuperação do Treinamento

**Situacao**: Treinamento interrompido no step 1000 (33%) por falta de espaço em disco.

**Checkpoint salvo com sucesso**: checkpoint-500 (step 500, 17% completo)

**Checkpoint incompleto**: checkpoint-1000 (1.5GB em vez de 3.2GB)

---

## Resumo da Solução

1. Mover outputs para HD externo T9
2. Remover checkpoint-1000 incompleto
3. Retomar treinamento do checkpoint-500
4. Treinamento continuará salvando no T9 automaticamente

---

## Passo a Passo

### 1. Parar Treinamento Atual

Se o treinamento ainda estiver rodando:

```bash
# No terminal onde o treinamento está rodando
Ctrl+C
```

### 2. Executar Script de Migração

```bash
cd /Users/jwcunha/Documents/COMPANIES/AB/repos/private/premium/researcher/phd-classes/shoes-tranning/training/scripts
./move_and_resume_training.sh
```

O script irá:
- Analisar espaço usado
- Perguntar se deseja remover checkpoint-1000 incompleto (recomendado: **SIM**)
- Mover outputs/ para `/Volumes/T9/COMPANIES/AB/repos/private/premium/researcher/phd-classes/computer-vision/shoes-training-outputs`
- Criar symlink transparente

### 3. Retomar Treinamento

Após a migração, execute:

```bash
cd /Users/jwcunha/Documents/COMPANIES/AB/repos/private/premium/researcher/phd-classes/shoes-tranning/training/scripts

python train_lora.py \
  --resume_from_checkpoint=../outputs/lora_casual_shoes_3000steps_full/checkpoints/checkpoint-500 \
  --max_train_steps=3000 \
  --train_batch_size=2 \
  --gradient_accumulation_steps=8 \
  --validation_steps=500 \
  --checkpointing_steps=500 \
  --num_train_epochs=100 \
  --output_dir=../outputs/lora_casual_shoes_3000steps_full \
  2>&1 | tee training_log_resumed.txt
```

---

## O Que Vai Acontecer

### Comportamento da Retomada

1. **Step de início**: O treinamento retomará do step 501 (após o checkpoint-500)
2. **Progresso**: Faltam 2500 steps para completar (500 → 3000)
3. **Tempo estimado**: ~9-10 horas para os 2500 steps restantes
4. **Checkpoints futuros**:
   - checkpoint-1000: Será salvo novamente (agora no T9)
   - checkpoint-1500: step 1500
   - checkpoint-2000: step 2000
   - checkpoint-2500: step 2500

### Estrutura após Migração

```
/Users/.../training/outputs/  →  (symlink para T9)
    ↓
/Volumes/T9/COMPANIES/.../shoes-training-outputs/
└── lora_casual_shoes_3000steps_full/
    ├── checkpoints/
    │   ├── checkpoint-500/         ← Ponto de retomada
    │   ├── checkpoint-1000/        ← Será recriado
    │   ├── checkpoint-1500/        ← Novo
    │   └── ...
    └── validation/
```

---

## Verificação Pós-Migração

### Confirmar Symlink

```bash
ls -lh /Users/jwcunha/Documents/COMPANIES/AB/repos/private/premium/researcher/phd-classes/shoes-tranning/training/outputs

# Deve mostrar: outputs -> /Volumes/T9/.../shoes-training-outputs
```

### Verificar Espaço no T9

```bash
df -h /Volumes/T9
```

### Verificar Checkpoint-500

```bash
ls -lh /Volumes/T9/COMPANIES/AB/repos/private/premium/researcher/phd-classes/computer-vision/shoes-training-outputs/lora_casual_shoes_3000steps_full/checkpoints/checkpoint-500/

# Deve mostrar:
# model.safetensors:   3.2GB
# optimizer.bin:       12MB
# scheduler.bin:       <1MB
# random_states_0.pkl: <1MB
```

---

## Monitoramento do Treinamento Retomado

### Ver Progresso em Tempo Real

```bash
# Terminal 1: Treinamento
cd training/scripts
python train_lora.py --resume_from_checkpoint=...

# Terminal 2: Monitoramento
tail -f training_log_resumed.txt
```

### Verificar Steps

O log mostrará algo como:
```
Steps:  17%|█▋        | 501/3000 [...]
```

Isso confirma que retomou do checkpoint-500.

---

## Troubleshooting

### Erro: "checkpoint not found"

```bash
# Verificar se checkpoint existe
ls -lh ../outputs/lora_casual_shoes_3000steps_full/checkpoints/checkpoint-500/
```

### Erro: "No space left"

Se ainda ocorrer:
```bash
# Verificar espaço no T9
df -h /Volumes/T9

# Verificar symlink
ls -la ../outputs
```

### Treinamento Não Retoma

Remover `--resume_from_checkpoint` iniciará do zero. **CUIDADO!**

Para realmente retomar, o parâmetro é **obrigatório**.

---

## Estimativas

### Progresso Atual
- **Completo**: 500 steps (17%)
- **Restante**: 2500 steps (83%)
- **Tempo**: ~9-10 horas

### Espaço em Disco
- **Checkpoint-500**: 3.2 GB
- **Checkpoints futuros (5×)**: ~16 GB
- **Total estimado**: ~25 GB no T9

---

## Comandos Rápidos

### Resumo de 1 Linha

```bash
# Parar treinamento, migrar, retomar
./move_and_resume_training.sh && python train_lora.py --resume_from_checkpoint=../outputs/lora_casual_shoes_3000steps_full/checkpoints/checkpoint-500 --max_train_steps=3000 --train_batch_size=2 --gradient_accumulation_steps=8 --validation_steps=500 --checkpointing_steps=500 --num_train_epochs=100 --output_dir=../outputs/lora_casual_shoes_3000steps_full
```

---

## Notas Importantes

1. **Não desconecte o T9** durante o treinamento
2. **Checkpoint-500 é confiável** - foi salvo com sucesso antes do erro
3. **Symlink é transparente** - scripts funcionam normalmente
4. **Checkpoints futuros** serão salvos automaticamente no T9
5. **API e frontend** continuam funcionando com o symlink

---

Criado: 27/10/2025
Status: Pronto para execução
