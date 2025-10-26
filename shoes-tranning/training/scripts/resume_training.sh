#!/bin/bash
# Script para retomar treinamento do último checkpoint
# Uso: ./resume_training.sh

echo "=================================="
echo "Retomando Treinamento LoRA"
echo "=================================="
echo ""

# Diretório de output
OUTPUT_DIR="../outputs/lora_casual_shoes"
CHECKPOINTS_DIR="${OUTPUT_DIR}/checkpoints"

# Verificar se existem checkpoints
if [ ! -d "$CHECKPOINTS_DIR" ]; then
    echo "[ERRO] Diretório de checkpoints não encontrado: $CHECKPOINTS_DIR"
    echo "Execute o treinamento inicial primeiro:"
    echo "  python3 train_lora.py"
    exit 1
fi

# Contar checkpoints
NUM_CHECKPOINTS=$(ls -d ${CHECKPOINTS_DIR}/checkpoint-* 2>/dev/null | wc -l)

if [ $NUM_CHECKPOINTS -eq 0 ]; then
    echo "[ERRO] Nenhum checkpoint encontrado em $CHECKPOINTS_DIR"
    echo "Execute o treinamento inicial primeiro:"
    echo "  python3 train_lora.py"
    exit 1
fi

echo "[INFO] Checkpoints encontrados: $NUM_CHECKPOINTS"
echo ""

# Listar checkpoints disponíveis
echo "Checkpoints disponíveis:"
ls -1 ${CHECKPOINTS_DIR} | grep "checkpoint-" | sort -V
echo ""

# Pegar último checkpoint
LATEST_CHECKPOINT=$(ls -d ${CHECKPOINTS_DIR}/checkpoint-* | sort -V | tail -1)
CHECKPOINT_STEP=$(basename $LATEST_CHECKPOINT | cut -d'-' -f2)

echo "[INFO] Último checkpoint: checkpoint-${CHECKPOINT_STEP}"
echo ""

# Confirmar com usuário
read -p "Deseja retomar do checkpoint-${CHECKPOINT_STEP}? (s/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Operação cancelada."
    exit 0
fi

echo ""
echo "[INFO] Retomando treinamento do step ${CHECKPOINT_STEP}..."
echo "[INFO] Continuará até max_train_steps (padrão: 3000)"
echo ""

# Executar treinamento
python3 train_lora.py \
    --resume_from_checkpoint latest \
    --max_train_steps 3000 \
    --validation_steps 500 \
    --checkpointing_steps 500 \
    --output_dir ${OUTPUT_DIR}

echo ""
echo "=================================="
echo "Treinamento Concluído ou Interrompido"
echo "=================================="
