#!/bin/bash

#
# Script para mover outputs para HD externo e preparar para retomar treinamento
#

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Migração e Retomada de Treinamento${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Diretórios
TRAINING_DIR="/Users/jwcunha/Documents/COMPANIES/AB/repos/private/premium/researcher/phd-classes/shoes-tranning/training"
OUTPUTS_DIR="$TRAINING_DIR/outputs"
EXTERNAL_OUTPUTS_DIR="/Volumes/T9/COMPANIES/AB/repos/private/premium/researcher/phd-classes/computer-vision/shoes-training-outputs"

echo -e "${YELLOW}[1/5]${NC} Verificando estrutura..."
echo "  Origem: $OUTPUTS_DIR"
echo "  Destino: $EXTERNAL_OUTPUTS_DIR"
echo ""

# Verificar se HD está montado
if [ ! -d "/Volumes/T9" ]; then
    echo -e "${RED}[ERROR]${NC} HD externo T9 não encontrado!"
    echo "  Conecte o HD T9 e tente novamente"
    exit 1
fi

# Verificar se outputs existe
if [ ! -d "$OUTPUTS_DIR" ]; then
    echo -e "${RED}[ERROR]${NC} Diretório de outputs não encontrado: $OUTPUTS_DIR"
    exit 1
fi

# Analisar espaço
echo -e "${YELLOW}[2/5]${NC} Analisando uso de espaço..."
TOTAL_SIZE=$(du -sh "$OUTPUTS_DIR" | awk '{print $1}')
echo "  Tamanho total: $TOTAL_SIZE"
echo ""

# Verificar checkpoint incompleto
INCOMPLETE_CHECKPOINT="$OUTPUTS_DIR/lora_casual_shoes_3000steps_full/checkpoints/checkpoint-1000"
if [ -d "$INCOMPLETE_CHECKPOINT" ]; then
    CHECKPOINT_SIZE=$(du -sh "$INCOMPLETE_CHECKPOINT" | awk '{print $1}')
    echo -e "${YELLOW}[INFO]${NC} Checkpoint incompleto detectado:"
    echo "  $INCOMPLETE_CHECKPOINT"
    echo "  Tamanho: $CHECKPOINT_SIZE (esperado: ~3.2GB)"
    echo ""

    read -p "Deseja remover o checkpoint incompleto? (y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}[INFO]${NC} Removendo checkpoint incompleto..."
        rm -rf "$INCOMPLETE_CHECKPOINT"
        echo -e "${GREEN}✓${NC} Checkpoint-1000 removido"
    fi
    echo ""
fi

# Confirmar migração
echo -e "${YELLOW}[ATENÇÃO]${NC} Esta operação irá:"
echo "  1. Criar diretório no T9: $EXTERNAL_OUTPUTS_DIR"
echo "  2. Mover outputs/ para o T9"
echo "  3. Criar symlink: outputs -> $EXTERNAL_OUTPUTS_DIR"
echo "  4. Preparar para retomar treinamento do checkpoint-500"
echo ""
read -p "Deseja continuar? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}[INFO]${NC} Operação cancelada"
    exit 0
fi

echo ""
echo -e "${YELLOW}[3/5]${NC} Criando estrutura no HD externo..."
mkdir -p "$EXTERNAL_OUTPUTS_DIR"
echo -e "${GREEN}✓${NC} Diretório criado"

echo -e "${YELLOW}[4/5]${NC} Movendo arquivos..."
echo -e "${BLUE}        Isto pode levar alguns minutos para $TOTAL_SIZE...${NC}"
mv "$OUTPUTS_DIR" "$EXTERNAL_OUTPUTS_DIR"
echo -e "${GREEN}✓${NC} Arquivos movidos"

echo -e "${YELLOW}[5/5]${NC} Criando symlink..."
ln -s "$EXTERNAL_OUTPUTS_DIR" "$OUTPUTS_DIR"
echo -e "${GREEN}✓${NC} Symlink criado"

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Migração Concluída!${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "${GREEN}[INFO]${NC} Configuração:"
echo "  Diretório local: $OUTPUTS_DIR (symlink)"
echo "  Dados reais em: $EXTERNAL_OUTPUTS_DIR"
echo ""
echo -e "${GREEN}[INFO]${NC} Para retomar o treinamento:"
echo "  1. Pare o treinamento atual (Ctrl+C se estiver rodando)"
echo "  2. Execute o comando de retomada fornecido abaixo"
echo ""
echo -e "${BLUE}Comando para retomar do checkpoint-500:${NC}"
echo ""
echo "cd $TRAINING_DIR/scripts"
echo "python train_lora.py \\"
echo "  --resume_from_checkpoint=../outputs/lora_casual_shoes_3000steps_full/checkpoints/checkpoint-500 \\"
echo "  --max_train_steps=3000 \\"
echo "  --train_batch_size=2 \\"
echo "  --gradient_accumulation_steps=8 \\"
echo "  --validation_steps=500 \\"
echo "  --checkpointing_steps=500 \\"
echo "  --num_train_epochs=100 \\"
echo "  --output_dir=../outputs/lora_casual_shoes_3000steps_full"
echo ""
echo -e "${GREEN}✓ Pronto para retomar!${NC}"
