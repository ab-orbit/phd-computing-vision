# Quick Start - Google Vision Emotion Classifier

## Instalação Rápida

```bash
# 1. Instalar dependências
pip install google-cloud-vision pillow pandas python-dotenv

# 2. Configurar API key no .env
echo "GOOGLE_API_KEY=sua_chave_aqui" >> .env
```

## Obter API Key

### Opção 1: Service Account (Recomendado)

1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Crie novo projeto
3. Ative Cloud Vision API
4. Vá em IAM & Admin > Service Accounts
5. Crie service account
6. Baixe JSON de credenciais
7. Configure:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

### Opção 2: API Key (Mais Simples)

1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Crie novo projeto
3. Ative Cloud Vision API
4. Vá em APIs & Services > Credentials
5. Crie API Key
6. Adicione ao .env:

```bash
GOOGLE_API_KEY=AIzaSy...sua_chave_aqui
```

## Execução Rápida

### Teste (1 simulação)

```bash
cd /Users/jwcunha/Documents/repos/phd-datascience/visao-computacional/projeto-estudo-comparativo

python 2_classificators/gemini2/GoogleVisionEmotionClassifier.py --simulation 1
```

### Completo (30 simulações)

```bash
python 2_classificators/gemini2/GoogleVisionEmotionClassifier.py --num_simulations 30
```

## Estimativas

### Tempo

- Por simulação: ~30-45 segundos (100 imagens)
- 30 simulações: ~15-25 minutos
- Depende da conexão de internet

### Acurácia Esperada

- Geral: 80-90%
- Alegria: 85-95%
- Raiva: 75-85%

### Custo

- Free tier: 1000 imagens/mês grátis
- Após: $1.50 por 1000 imagens
- 30 simulações (3000 imagens): ~$3.00

## Resultados

Após execução:

```bash
# Ver CSV
cat 3_simulation/results/google_vision_emotion/results.csv | column -t -s,

# Ver estatísticas
cat 3_simulation/results/google_vision_emotion/stats.json | python -m json.tool

# Comparar com outros modelos
python -c "
import pandas as pd
gv = pd.read_csv('3_simulation/results/google_vision_emotion/results.csv')
print(f'Google Vision: {gv[\"acuracia_geral\"].mean():.2%}')
"
```

## Troubleshooting

### GOOGLE_API_KEY não encontrada

```bash
# Verifique se .env existe
cat .env | grep GOOGLE_API_KEY

# Se não existir, adicione
echo "GOOGLE_API_KEY=sua_chave" >> .env
```

### Quota exceeded

Você excedeu 1000 requisições/mês grátis.

Soluções:
- Ative billing no Google Cloud
- Use outro projeto
- Aguarde próximo mês

### Muito lento

Causas:
- Internet lenta
- Rate limiting da API
- Muitas requisições simultâneas

### No face detected

A API não detectou face na imagem. Normal para algumas imagens de baixa qualidade.

## Próximos Passos

1. Execute teste (1 simulação)
2. Verifique acurácia
3. Execute completo (30 simulações)
4. Compare com CNN, Roboflow, YOLO11
5. Analise trade-offs

## Comparação Rápida

| Modelo | Acurácia | Tempo | Custo |
|--------|----------|-------|-------|
| CNN | 90% | 10ms | GPU 1x |
| Roboflow | 35% | 600ms | $/req |
| YOLO11 | 0% | 2ms | GPU 1x |
| Google Vision | 85% | 450ms | $/req |

## Vantagens Google Vision

- Alta acurácia sem treinar
- API robusta do Google
- Suporta múltiplas emoções
- Detecção de faces nativa

## Pronto para executar
