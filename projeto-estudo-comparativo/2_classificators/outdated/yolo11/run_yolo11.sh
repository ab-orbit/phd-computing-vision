#!/bin/bash

# Script para executar classificador YOLO11
# Uso: ./run_yolo11.sh [num_simulations]

# Configurações
NUM_SIMULATIONS=${1:-30}  # Padrão: 30 simulações
PROJECT_ROOT="/Users/jwcunha/Documents/repos/phd-datascience/visao-computacional/projeto-estudo-comparativo"

echo "=========================================="
echo "Classificador YOLO11 - Emoções"
echo "=========================================="
echo "Simulações: $NUM_SIMULATIONS"
echo "=========================================="
echo ""

# Vai para diretório raiz do projeto
cd "$PROJECT_ROOT" || exit 1

# Verifica se ultralytics está instalado
python -c "import ultralytics" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Ultralytics não encontrado. Instalando..."
    pip install ultralytics opencv-python pillow pandas numpy
fi

# Executa classificador
echo "Iniciando processamento..."
echo ""

python 2_classificators/yolo11/YOLO11EmotionClassifier.py \
    --num_simulations "$NUM_SIMULATIONS"

# Verifica resultado
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "Processamento concluído com sucesso!"
    echo "=========================================="
    echo "Resultados em: 3_simulation/results/yolo11_emotion/"
    echo ""

    # Mostra estatísticas
    if [ -f "3_simulation/results/yolo11_emotion/stats.json" ]; then
        echo "Estatísticas:"
        cat 3_simulation/results/yolo11_emotion/stats.json | python -m json.tool | grep -E "(acuracia|tempo)"
    fi
else
    echo ""
    echo "Erro durante processamento!"
    exit 1
fi
