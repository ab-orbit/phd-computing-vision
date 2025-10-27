#!/bin/bash

#
# Script para converter todos os checkpoints de um treinamento para pipelines utilizáveis.
#
# Uso:
#   ./convert_all_checkpoints.sh [training_output_dir]
#
# Exemplo:
#   ./convert_all_checkpoints.sh ../outputs/lora_casual_shoes_3000steps_full
#

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função de log
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar argumentos
if [ $# -eq 0 ]; then
    error "Uso: $0 <training_output_dir>"
    echo "Exemplo: $0 ../outputs/lora_casual_shoes_3000steps_full"
    exit 1
fi

TRAINING_DIR="$1"

# Verificar se diretório existe
if [ ! -d "$TRAINING_DIR" ]; then
    error "Diretório não encontrado: $TRAINING_DIR"
    exit 1
fi

CHECKPOINTS_DIR="$TRAINING_DIR/checkpoints"

if [ ! -d "$CHECKPOINTS_DIR" ]; then
    error "Diretório de checkpoints não encontrado: $CHECKPOINTS_DIR"
    exit 1
fi

# Criar diretório de output
OUTPUT_DIR="$TRAINING_DIR/checkpoint_pipelines"
mkdir -p "$OUTPUT_DIR"

log "Iniciando conversão de checkpoints..."
log "Origem: $CHECKPOINTS_DIR"
log "Destino: $OUTPUT_DIR"
echo ""

# Contar checkpoints
CHECKPOINT_COUNT=$(find "$CHECKPOINTS_DIR" -maxdepth 1 -type d -name "checkpoint-*" | wc -l)

if [ "$CHECKPOINT_COUNT" -eq 0 ]; then
    warn "Nenhum checkpoint encontrado em $CHECKPOINTS_DIR"
    exit 0
fi

log "Encontrados $CHECKPOINT_COUNT checkpoints"
echo ""

# Converter cada checkpoint
SUCCESS_COUNT=0
FAIL_COUNT=0

for checkpoint_path in "$CHECKPOINTS_DIR"/checkpoint-*; do
    if [ ! -d "$checkpoint_path" ]; then
        continue
    fi

    checkpoint_name=$(basename "$checkpoint_path")
    checkpoint_step="${checkpoint_name#checkpoint-}"
    output_path="$OUTPUT_DIR/$checkpoint_name"

    # Verificar se já foi convertido
    if [ -d "$output_path" ] && [ -f "$output_path/model_index.json" ]; then
        log "[$checkpoint_name] Já convertido, pulando..."
        ((SUCCESS_COUNT++))
        continue
    fi

    log "[$checkpoint_name] Convertendo (step $checkpoint_step)..."

    # Executar conversão
    if python convert_checkpoint_to_pipeline.py \
        --checkpoint_path "$checkpoint_path" \
        --output_dir "$output_path" 2>&1 | grep -q "Conversão concluída"; then

        log "[$checkpoint_name] ✓ Conversão bem-sucedida"
        ((SUCCESS_COUNT++))
    else
        error "[$checkpoint_name] ✗ Falha na conversão"
        ((FAIL_COUNT++))
    fi

    echo ""
done

# Resumo
echo "================================"
echo "Resumo da Conversão"
echo "================================"
log "Total de checkpoints: $CHECKPOINT_COUNT"
log "Conversões bem-sucedidas: $SUCCESS_COUNT"

if [ "$FAIL_COUNT" -gt 0 ]; then
    error "Conversões falhadas: $FAIL_COUNT"
fi

echo ""
log "Pipelines disponíveis em: $OUTPUT_DIR"

# Listar pipelines
echo ""
echo "Checkpoints convertidos:"
for pipeline_dir in "$OUTPUT_DIR"/checkpoint-*; do
    if [ -d "$pipeline_dir" ]; then
        checkpoint_name=$(basename "$pipeline_dir")
        step="${checkpoint_name#checkpoint-}"
        echo "  - Step $step: $pipeline_dir"
    fi
done

echo ""
log "Para usar na API, os modelos serão detectados automaticamente!"
log "Reinicie a API se ela já estiver rodando."

exit 0
