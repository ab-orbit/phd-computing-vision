#!/bin/bash

#
# Script para gerar imagens em lote usando a API
#
# Uso:
#   ./generate_batch.sh prompts.txt 3 [model_name]
#
# Argumentos:
#   prompts.txt  - Arquivo com um prompt por linha
#   3            - Número de imagens por prompt
#   model_name   - (Opcional) Nome do modelo. Se não informado, usa o mais recente
#

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
API_URL="http://localhost:8011"
OUTPUT_DIR="generated_batch"

# Função para exibir uso
usage() {
    echo "Uso: $0 <prompt_file> <num_images> [model_name]"
    echo ""
    echo "Argumentos:"
    echo "  prompt_file  - Arquivo de texto com um prompt por linha"
    echo "  num_images   - Número de imagens a gerar por prompt (1-10)"
    echo "  model_name   - (Opcional) Nome do modelo. Se omitido, usa o mais recente"
    echo ""
    echo "Exemplos:"
    echo "  $0 prompts.txt 3"
    echo "  $0 prompts.txt 5 lora_casual_shoes_3000steps_full/checkpoint-1500"
    echo ""
    exit 1
}

# Função para obter o modelo mais recente
get_latest_model() {
    echo -e "${BLUE}[INFO]${NC} Detectando modelo mais recente..."

    # Chamar API para listar modelos
    local models_json=$(curl -s "${API_URL}/api/models")

    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} Falha ao conectar à API em ${API_URL}"
        exit 1
    fi

    # Extrair modelo com maior step number (exceto "base" e "final")
    # Prioridade: checkpoint-N > final > base
    local latest=$(echo "$models_json" | python3 -c "
import sys
import json

data = json.load(sys.stdin)
models = data.get('models', [])

# Filtrar modelos válidos
valid_models = []
for model in models:
    name = model['name']
    if name == 'base':
        continue

    # Extrair step number se for checkpoint
    if 'checkpoint-' in name:
        try:
            step = int(name.split('checkpoint-')[-1])
            valid_models.append((step, name, 'checkpoint'))
        except:
            pass
    elif 'final' in name:
        valid_models.append((999999, name, 'final'))

# Ordenar por step (maior primeiro)
valid_models.sort(reverse=True)

if valid_models:
    print(valid_models[0][1])
else:
    print('base')
")

    if [ -z "$latest" ]; then
        echo -e "${YELLOW}[WARN]${NC} Nenhum modelo encontrado. Usando 'base'"
        latest="base"
    fi

    echo -e "${GREEN}[INFO]${NC} Modelo selecionado: ${latest}"
    echo "$latest"
}

# Validar argumentos
if [ $# -lt 2 ]; then
    usage
fi

PROMPT_FILE="$1"
NUM_IMAGES="$2"
MODEL_NAME="${3:-}"

# Validar arquivo de prompts
if [ ! -f "$PROMPT_FILE" ]; then
    echo -e "${RED}[ERROR]${NC} Arquivo não encontrado: $PROMPT_FILE"
    exit 1
fi

# Validar número de imagens
if ! [[ "$NUM_IMAGES" =~ ^[0-9]+$ ]] || [ "$NUM_IMAGES" -lt 1 ] || [ "$NUM_IMAGES" -gt 10 ]; then
    echo -e "${RED}[ERROR]${NC} Número de imagens deve ser entre 1 e 10"
    exit 1
fi

# Se modelo não foi informado, detectar o mais recente
if [ -z "$MODEL_NAME" ]; then
    MODEL_NAME=$(get_latest_model)
fi

# Criar diretório de output
mkdir -p "$OUTPUT_DIR"

# Contar total de prompts
TOTAL_PROMPTS=$(grep -c . "$PROMPT_FILE" || echo 0)

if [ "$TOTAL_PROMPTS" -eq 0 ]; then
    echo -e "${RED}[ERROR]${NC} Arquivo de prompts está vazio"
    exit 1
fi

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Geração em Lote de Imagens${NC}"
echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}Arquivo de prompts:${NC} $PROMPT_FILE"
echo -e "${GREEN}Total de prompts:${NC} $TOTAL_PROMPTS"
echo -e "${GREEN}Imagens por prompt:${NC} $NUM_IMAGES"
echo -e "${GREEN}Modelo:${NC} $MODEL_NAME"
echo -e "${GREEN}Diretório de saída:${NC} $OUTPUT_DIR"
echo -e "${BLUE}================================${NC}"
echo ""

# Contador
CURRENT=0
SUCCESS=0
FAILED=0

# Timestamp do lote
BATCH_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BATCH_DIR="${OUTPUT_DIR}/batch_${BATCH_TIMESTAMP}"
mkdir -p "$BATCH_DIR"

# Processar cada prompt
while IFS= read -r prompt || [ -n "$prompt" ]; do
    # Ignorar linhas vazias e comentários
    if [ -z "$prompt" ] || [[ "$prompt" =~ ^# ]]; then
        continue
    fi

    CURRENT=$((CURRENT + 1))

    echo -e "${YELLOW}[${CURRENT}/${TOTAL_PROMPTS}]${NC} Gerando imagens para: ${BLUE}\"${prompt}\"${NC}"

    # Criar nome de arquivo seguro a partir do prompt
    SAFE_PROMPT=$(echo "$prompt" | tr ' ' '_' | tr -cd '[:alnum:]_' | cut -c1-50)
    PROMPT_DIR="${BATCH_DIR}/prompt_${CURRENT}_${SAFE_PROMPT}"
    mkdir -p "$PROMPT_DIR"

    # Salvar prompt original
    echo "$prompt" > "${PROMPT_DIR}/prompt.txt"

    # Preparar JSON payload
    JSON_PAYLOAD=$(cat <<EOF
{
  "model_name": "${MODEL_NAME}",
  "prompt": "${prompt}",
  "num_images": ${NUM_IMAGES},
  "num_inference_steps": 50,
  "guidance_scale": 7.5,
  "seed": null
}
EOF
)

    # Chamar API
    RESPONSE=$(curl -s -X POST "${API_URL}/api/generate" \
        -H "Content-Type: application/json" \
        -d "$JSON_PAYLOAD")

    # Verificar se foi bem-sucedido
    if echo "$RESPONSE" | grep -q '"success":true'; then
        echo -e "${GREEN}  ✓ Geração bem-sucedida${NC}"

        # Extrair e salvar imagens
        IMAGE_COUNT=0
        echo "$RESPONSE" | python3 -c "
import sys
import json
import base64
from pathlib import Path

data = json.load(sys.stdin)
images = data.get('images', [])

for idx, img_data in enumerate(images, 1):
    img_b64 = img_data.get('image')
    if img_b64:
        img_bytes = base64.b64decode(img_b64)
        output_path = Path('${PROMPT_DIR}') / f'image_{idx:02d}.png'
        output_path.write_bytes(img_bytes)
        print(f'  Salva: {output_path.name}')
" && IMAGE_COUNT=$?

        SUCCESS=$((SUCCESS + 1))
        echo -e "${GREEN}  ✓ ${NUM_IMAGES} imagens salvas em: ${PROMPT_DIR}${NC}"
    else
        echo -e "${RED}  ✗ Falha na geração${NC}"
        echo "$RESPONSE" > "${PROMPT_DIR}/error.json"
        FAILED=$((FAILED + 1))
    fi

    echo ""

done < "$PROMPT_FILE"

# Resumo final
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Resumo da Geração${NC}"
echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}Total processado:${NC} $TOTAL_PROMPTS prompts"
echo -e "${GREEN}Bem-sucedidos:${NC} $SUCCESS"
echo -e "${RED}Falhas:${NC} $FAILED"
echo -e "${GREEN}Total de imagens:${NC} $((SUCCESS * NUM_IMAGES))"
echo -e "${GREEN}Diretório:${NC} $BATCH_DIR"
echo -e "${BLUE}================================${NC}"
echo ""

# Criar índice HTML para visualização
HTML_INDEX="${BATCH_DIR}/index.html"
cat > "$HTML_INDEX" <<'HTMLEOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Batch Generation Results</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }
        .prompt-section {
            background: white;
            margin: 20px 0;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .prompt-text {
            font-size: 16px;
            color: #555;
            margin-bottom: 15px;
            padding: 10px;
            background: #f9f9f9;
            border-left: 4px solid #4CAF50;
        }
        .images {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
        }
        .images img {
            width: 100%;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }
        .stats {
            background: #4CAF50;
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <h1>Batch Generation Results</h1>
    <div class="stats">
        <strong>Model:</strong> MODEL_NAME_PLACEHOLDER<br>
        <strong>Total Prompts:</strong> TOTAL_PROMPTS_PLACEHOLDER<br>
        <strong>Images per Prompt:</strong> NUM_IMAGES_PLACEHOLDER<br>
        <strong>Generated:</strong> TIMESTAMP_PLACEHOLDER
    </div>
HTMLEOF

# Adicionar cada prompt ao HTML
PROMPT_NUM=0
while IFS= read -r prompt || [ -n "$prompt" ]; do
    if [ -z "$prompt" ] || [[ "$prompt" =~ ^# ]]; then
        continue
    fi

    PROMPT_NUM=$((PROMPT_NUM + 1))
    SAFE_PROMPT=$(echo "$prompt" | tr ' ' '_' | tr -cd '[:alnum:]_' | cut -c1-50)
    PROMPT_DIR_NAME="prompt_${PROMPT_NUM}_${SAFE_PROMPT}"

    cat >> "$HTML_INDEX" <<HTMLEOF
    <div class="prompt-section">
        <div class="prompt-text"><strong>Prompt ${PROMPT_NUM}:</strong> ${prompt}</div>
        <div class="images">
HTMLEOF

    for img in "${BATCH_DIR}/${PROMPT_DIR_NAME}"/image_*.png; do
        if [ -f "$img" ]; then
            IMG_NAME=$(basename "$img")
            echo "            <img src=\"${PROMPT_DIR_NAME}/${IMG_NAME}\" alt=\"${prompt}\">" >> "$HTML_INDEX"
        fi
    done

    cat >> "$HTML_INDEX" <<HTMLEOF
        </div>
    </div>
HTMLEOF

done < "$PROMPT_FILE"

cat >> "$HTML_INDEX" <<'HTMLEOF'
</body>
</html>
HTMLEOF

# Substituir placeholders
sed -i.bak "s/MODEL_NAME_PLACEHOLDER/${MODEL_NAME}/g" "$HTML_INDEX"
sed -i.bak "s/TOTAL_PROMPTS_PLACEHOLDER/${TOTAL_PROMPTS}/g" "$HTML_INDEX"
sed -i.bak "s/NUM_IMAGES_PLACEHOLDER/${NUM_IMAGES}/g" "$HTML_INDEX"
sed -i.bak "s/TIMESTAMP_PLACEHOLDER/$(date)/g" "$HTML_INDEX"
rm "${HTML_INDEX}.bak"

echo -e "${GREEN}✓ Índice HTML criado: ${HTML_INDEX}${NC}"
echo ""
echo -e "${BLUE}Para visualizar os resultados, abra:${NC}"
echo -e "  open ${HTML_INDEX}"
echo ""

exit 0
