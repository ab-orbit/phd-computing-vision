#!/bin/bash
# Script de configuração para DocLayout-YOLO Document Classification

set -e  # Parar em caso de erro

echo "================================================================================================="
echo "CONFIGURAÇÃO DO AMBIENTE DOCLAYOUT-YOLO"
echo "================================================================================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir com cor
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# 1. Verificar Python
echo ""
echo "1. Verificando Python..."
echo "-------------------------------------------------------------------------------------------------"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python encontrado: $PYTHON_VERSION"
else
    print_error "Python 3 não encontrado. Instale Python 3.10 ou superior."
    exit 1
fi

# 2. Instalar dependências
echo ""
echo "2. Instalando dependências..."
echo "-------------------------------------------------------------------------------------------------"
if pip3 install -r requirements.txt; then
    print_success "Dependências instaladas"
else
    print_error "Falha ao instalar dependências"
    exit 1
fi

# 3. Baixar modelo (se não existir)
echo ""
echo "3. Verificando modelo DocLayout-YOLO..."
echo "-------------------------------------------------------------------------------------------------"
MODEL_FILE="doclayout_yolo_docstructbench_imgsz1024"
if [ -f "$MODEL_FILE" ]; then
    print_info "Modelo já existe: $MODEL_FILE"
else
    print_info "Baixando modelo DocStructBench..."
    MODEL_URL="https://huggingface.co/juliozhao/DocLayout-YOLO-DocStructBench/resolve/main/doclayout_yolo_docstructbench_imgsz1024.pt"

    if command -v wget &> /dev/null; then
        wget -q --show-progress "$MODEL_URL" -O "$MODEL_FILE"
        print_success "Modelo baixado: $MODEL_FILE"
    elif command -v curl &> /dev/null; then
        curl -L "$MODEL_URL" -o "$MODEL_FILE"
        print_success "Modelo baixado: $MODEL_FILE"
    else
        print_error "wget ou curl não encontrado. Baixe manualmente:"
        echo "  $MODEL_URL"
        exit 1
    fi
fi

# 4. Criar diretórios
echo ""
echo "4. Criando estrutura de diretórios..."
echo "-------------------------------------------------------------------------------------------------"
mkdir -p sample
mkdir -p results
print_success "Diretórios criados: sample/, results/"

# 5. Testar instalação
echo ""
echo "5. Testando instalação..."
echo "-------------------------------------------------------------------------------------------------"
if python3 -c "from doclayout_yolo import YOLOv10; print('✓ DocLayout-YOLO importado com sucesso')"; then
    print_success "Importação do DocLayout-YOLO funcionando"
else
    print_error "Falha ao importar DocLayout-YOLO"
    exit 1
fi

# Resumo
echo ""
echo "================================================================================================="
echo "CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!"
echo "================================================================================================="
echo ""
echo "Próximos passos:"
echo ""
echo "1. Execute o classificador completo:"
echo "   python classify_documents.py --dataset-path ../rvlp/data/test --num-samples 10"
echo ""
echo "2. Ou selecione amostras primeiro:"
echo "   python sample_selector.py --dataset-path ../rvlp/data/test --num-samples 10"
echo ""
echo "3. Analise um documento individual:"
echo "   python analyze_layout.py --image-path sample/email/exemplo.tif --output-path resultado.jpg"
echo ""
echo "================================================================================================="
