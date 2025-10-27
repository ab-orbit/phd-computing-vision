#!/bin/bash

#
# Script rápido para testar o primeiro checkpoint (step 500)
#
# Este script:
# 1. Aguarda checkpoint-500 ser criado
# 2. Converte automaticamente
# 3. Testa geração de imagem
# 4. Mostra resultado
#
# Uso: ./quick_test_checkpoint.sh
#

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Quick Checkpoint Test${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Configuração
TRAINING_DIR="../outputs/lora_casual_shoes_3000steps_full"
CHECKPOINT_DIR="$TRAINING_DIR/checkpoints/checkpoint-500"
OUTPUT_DIR="$TRAINING_DIR/checkpoint_pipelines/checkpoint-500"

# 1. Aguardar checkpoint
echo -e "${YELLOW}[1/4]${NC} Aguardando checkpoint-500 ser salvo..."

while [ ! -d "$CHECKPOINT_DIR" ]; do
    echo "  Checkpoint ainda não existe, aguardando 30s..."
    sleep 30
done

echo -e "${GREEN}✓${NC} Checkpoint-500 detectado!"
echo ""

# 2. Aguardar arquivo ser completamente salvo
echo -e "${YELLOW}[2/4]${NC} Aguardando salvamento completo..."
sleep 10  # Aguardar garantir que arquivo foi completamente salvo

# 3. Converter
echo -e "${YELLOW}[3/4]${NC} Convertendo checkpoint para pipeline..."
echo ""

python convert_checkpoint_to_pipeline.py \
    --checkpoint_path "$CHECKPOINT_DIR" \
    --output_dir "$OUTPUT_DIR" \
    --test_prompt "A professional product photo of black casual shoes on white background, high quality, product photography"

echo ""
echo -e "${GREEN}✓${NC} Conversão concluída!"
echo ""

# 4. Instruções
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Próximos Passos${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo "1. Reinicie a API (se estiver rodando):"
echo "   cd api"
echo "   # Ctrl+C para parar"
echo "   python main.py"
echo ""
echo "2. No frontend (http://localhost:3000):"
echo "   - Selecione: 'Lora Casual Shoes 3000Steps Full (Step 500)'"
echo "   - Use um prompt de exemplo"
echo "   - Gere 4 imagens"
echo ""
echo "3. Imagem de teste salva em:"
echo "   $PWD/test_checkpoint_output.png"
echo ""
echo -e "${GREEN}✓ Checkpoint pronto para uso!${NC}"
