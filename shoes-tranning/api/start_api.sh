#!/bin/bash

# Script para iniciar a API com verificação de configuração

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Shoes Image Generation API${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Verificar se .env existe
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}[WARN]${NC} Arquivo .env não encontrado, usando configurações padrão"
else
    echo -e "${GREEN}[INFO]${NC} Carregando configurações do .env..."
    source .env
    echo -e "${GREEN}[INFO]${NC} API Host: ${API_HOST:-0.0.0.0}"
    echo -e "${GREEN}[INFO]${NC} API Port: ${API_PORT:-8011}"
    echo -e "${GREEN}[INFO]${NC} CORS Origins: ${CORS_ORIGINS}"
fi

echo ""
echo -e "${GREEN}[INFO]${NC} Iniciando API..."
echo ""

# Iniciar API
python main.py
