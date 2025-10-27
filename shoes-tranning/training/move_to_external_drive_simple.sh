#!/bin/bash

#
# Versão simplificada - usa cp em vez de rsync
# Mais compatível mas sem barra de progresso
#

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Verificar argumentos
if [ $# -eq 0 ]; then
    echo -e "${RED}[ERROR]${NC} Uso: $0 <caminho_hd_externo>"
    echo "Exemplo: $0 /Volumes/T9"
    exit 1
fi

EXTERNAL_DRIVE="$1"

# Verificar se HD externo existe
if [ ! -d "$EXTERNAL_DRIVE" ]; then
    echo -e "${RED}[ERROR]${NC} HD externo não encontrado: $EXTERNAL_DRIVE"
    exit 1
fi

# Diretórios
CURRENT_DIR="$(pwd)"
OUTPUTS_DIR="$CURRENT_DIR/outputs"
EXTERNAL_OUTPUTS_DIR="$EXTERNAL_DRIVE/shoes-training-outputs"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Migração para HD Externo T9${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Análise de espaço
TOTAL_SIZE=$(du -sh "$OUTPUTS_DIR" | awk '{print $1}')
echo -e "${GREEN}[INFO]${NC} Tamanho total a mover: $TOTAL_SIZE"
echo ""

# Confirmar
echo -e "${YELLOW}[ATENÇÃO]${NC} Esta operação irá:"
echo "  1. Criar diretório no T9: $EXTERNAL_OUTPUTS_DIR"
echo "  2. Mover todo conteúdo de outputs/ para o T9"
echo "  3. Criar symlink: outputs -> $EXTERNAL_OUTPUTS_DIR"
echo ""
read -p "Deseja continuar? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}[INFO]${NC} Operação cancelada"
    exit 0
fi

echo ""
echo -e "${GREEN}[1/3]${NC} Movendo arquivos para o HD externo..."
echo -e "${BLUE}        Isto pode levar vários minutos...${NC}"
echo ""

# Usar mv direto (mais rápido e simples)
mv "$OUTPUTS_DIR" "$EXTERNAL_OUTPUTS_DIR"

echo -e "${GREEN}[2/3]${NC} Criando symlink..."
ln -s "$EXTERNAL_OUTPUTS_DIR" "$OUTPUTS_DIR"

echo -e "${GREEN}[3/3]${NC} Verificando integridade..."
if [ -L "$OUTPUTS_DIR" ] && [ -d "$OUTPUTS_DIR" ]; then
    echo -e "${GREEN}✓${NC} Symlink criado com sucesso"
else
    echo -e "${RED}✗${NC} Erro ao criar symlink"
    exit 1
fi

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Migração Concluída!${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "${GREEN}[INFO]${NC} Diretório original: $OUTPUTS_DIR (agora é um symlink)"
echo -e "${GREEN}[INFO]${NC} Dados reais em: $EXTERNAL_OUTPUTS_DIR"
echo ""
echo -e "${GREEN}✓ Migração concluída com sucesso!${NC}"
