#!/bin/bash

# Script de instalação automática para Document Classification API
# Uso: ./install.sh [minimal|full]

set -e  # Exit on error

INSTALL_TYPE=${1:-minimal}

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Document Classification API - Instalação Automática       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar Python
echo "→ Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 não encontrado"
    echo "  Instale Python 3.10+ de https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "  ✓ Python $PYTHON_VERSION encontrado"

# Verificar versão mínima
REQUIRED_VERSION="3.10"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "✗ Python >= 3.10 necessário (encontrado: $PYTHON_VERSION)"
    exit 1
fi

# Criar ambiente virtual
echo ""
echo "→ Criando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  ✓ Ambiente virtual criado"
else
    echo "  ℹ Ambiente virtual já existe"
fi

# Ativar ambiente virtual
echo ""
echo "→ Ativando ambiente virtual..."
source venv/bin/activate
echo "  ✓ Ambiente ativado"

# Atualizar pip
echo ""
echo "→ Atualizando pip..."
pip install --quiet --upgrade pip
echo "  ✓ pip atualizado"

# Instalar dependências
echo ""
if [ "$INSTALL_TYPE" = "minimal" ]; then
    echo "→ Instalando dependências mínimas (LLM apenas)..."
    echo "  Isso pode levar 2-3 minutos..."
    pip install --quiet -r requirements-minimal.txt
    echo "  ✓ Dependências mínimas instaladas (~200MB)"
elif [ "$INSTALL_TYPE" = "full" ]; then
    echo "→ Instalando dependências completas..."
    echo "  ⚠️  AVISO: Isso pode levar 10-15 minutos (PyTorch é grande)"
    echo "  Tamanho total: ~2-3GB"
    echo ""
    read -p "  Continuar? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install -r requirements.txt
        echo "  ✓ Dependências completas instaladas"
    else
        echo "  Instalação cancelada"
        exit 0
    fi
else
    echo "✗ Tipo de instalação inválido: $INSTALL_TYPE"
    echo "  Use: ./install.sh minimal  ou  ./install.sh full"
    exit 1
fi

# Configurar .env
echo ""
echo "→ Configurando ambiente..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  ✓ Arquivo .env criado"
    echo ""
    echo "  ⚠️  IMPORTANTE: Configure sua API key da Anthropic"
    echo "     1. Obtenha em: https://console.anthropic.com/"
    echo "     2. Edite .env e adicione: ANTHROPIC_API_KEY=sk-ant-xxx"
else
    echo "  ℹ Arquivo .env já existe"
fi

# Verificar instalação
echo ""
echo "→ Verificando instalação..."

# Verificar imports
python3 -c "
try:
    from app.models.schemas import DocumentType, ClassificationResponse
    from app.services.llm_anthropic import create_anthropic_service
    from app.core.config import settings
    print('  ✓ Imports verificados')
except Exception as e:
    print(f'  ✗ Erro ao importar: {e}')
    exit(1)
"

# Sumário
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  Instalação Concluída!                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Tipo de instalação: $INSTALL_TYPE"
echo ""
echo "Próximos passos:"
echo ""
echo "  1. Ative o ambiente virtual:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Configure sua API key da Anthropic no arquivo .env:"
echo "     nano .env"
echo "     # Adicione: ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxx"
echo ""
echo "  3. Teste a instalação:"
echo "     python test_llm_classification.py"
echo ""
echo "  4. Inicie a API:"
echo "     python -m app.main"
echo "     # Acesse: http://localhost:8000/docs"
echo ""
echo "  5. Teste classificação:"
echo "     curl -X POST 'http://localhost:8000/classify' \\"
echo "       -F 'file=@documento.pdf' \\"
echo "       -F 'use_llm=true'"
echo ""
echo "Documentação:"
echo "  - README.md: Guia completo"
echo "  - LLM_USAGE.md: Uso de LLM"
echo "  - QUICKSTART.md: Início rápido"
echo ""
echo "Suporte:"
echo "  - GitHub Issues"
echo "  - Documentação: http://localhost:8000/docs"
echo ""
echo "✓ Instalação bem-sucedida!"
echo ""
