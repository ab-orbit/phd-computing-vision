#!/bin/bash

#
# Script para mover outputs de treinamento para HD externo T9
# e criar symlinks no local original para manter compatibilidade
#
# Uso:
#   ./move_to_external_drive.sh /Volumes/T9
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
    echo "Verifique se o HD T9 está conectado e montado"
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
echo -e "${GREEN}[INFO]${NC} Origem: $OUTPUTS_DIR"
echo -e "${GREEN}[INFO]${NC} Destino: $EXTERNAL_OUTPUTS_DIR"
echo ""

# Análise de espaço
echo -e "${YELLOW}[ANÁLISE]${NC} Calculando tamanho dos dados..."
TOTAL_SIZE=$(du -sh "$OUTPUTS_DIR" | awk '{print $1}')
echo -e "${GREEN}[INFO]${NC} Tamanho total a mover: $TOTAL_SIZE"
echo ""

# Verificar espaço disponível no HD externo
AVAILABLE_SPACE=$(df -h "$EXTERNAL_DRIVE" | tail -1 | awk '{print $4}')
echo -e "${GREEN}[INFO]${NC} Espaço disponível no T9: $AVAILABLE_SPACE"
echo ""

# Listar diretórios grandes
echo -e "${YELLOW}[RESUMO]${NC} Principais diretórios:"
du -sh "$OUTPUTS_DIR"/* 2>/dev/null | sort -hr | head -10
echo ""

# Confirmar
echo -e "${YELLOW}[ATENÇÃO]${NC} Esta operação irá:"
echo "  1. Criar diretório no T9: $EXTERNAL_OUTPUTS_DIR"
echo "  2. Mover todo conteúdo de outputs/ para o T9"
echo "  3. Criar symlink: outputs -> $EXTERNAL_OUTPUTS_DIR"
echo "  4. Treinamentos e API continuarão funcionando normalmente"
echo ""
read -p "Deseja continuar? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}[INFO]${NC} Operação cancelada"
    exit 0
fi

echo ""
echo -e "${GREEN}[1/4]${NC} Criando diretório no HD externo..."
mkdir -p "$EXTERNAL_OUTPUTS_DIR"

echo -e "${GREEN}[2/4]${NC} Movendo arquivos (isso pode levar alguns minutos)..."
echo -e "${BLUE}        Movendo aproximadamente $TOTAL_SIZE...${NC}"

# Usar rsync com opções compatíveis com macOS
if command -v rsync &> /dev/null; then
    # macOS rsync não suporta --info=progress2, usar --progress
    rsync -ah --progress "$OUTPUTS_DIR/" "$EXTERNAL_OUTPUTS_DIR/"
    echo ""
    echo -e "${GREEN}[INFO]${NC} Cópia concluída, removendo originais..."
    rm -rf "$OUTPUTS_DIR"
else
    # Fallback para mv simples
    echo -e "${YELLOW}[INFO]${NC} Usando mv (sem barra de progresso)..."
    mv "$OUTPUTS_DIR" "$EXTERNAL_OUTPUTS_DIR.tmp"
    mv "$EXTERNAL_OUTPUTS_DIR.tmp"/* "$EXTERNAL_OUTPUTS_DIR/"
    rmdir "$EXTERNAL_OUTPUTS_DIR.tmp"
fi

echo -e "${GREEN}[3/4]${NC} Criando symlink..."
ln -s "$EXTERNAL_OUTPUTS_DIR" "$OUTPUTS_DIR"

echo -e "${GREEN}[4/4]${NC} Verificando integridade..."
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
echo -e "${YELLOW}[NOTA]${NC} Todos os scripts e API continuam funcionando normalmente"
echo -e "${YELLOW}[NOTA]${NC} O treinamento em andamento continuará salvando no T9"
echo ""

# Mostrar uso de espaço
echo -e "${GREEN}[ESPAÇO]${NC} Uso do HD externo após migração:"
df -h "$EXTERNAL_DRIVE" | tail -1
echo ""

echo -e "${GREEN}✓ Migração concluída com sucesso!${NC}"
