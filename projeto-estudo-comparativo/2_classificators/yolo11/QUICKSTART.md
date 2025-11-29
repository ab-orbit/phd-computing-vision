# Quick Start - YOLO11 Emotion Classifier

## Instalação Rápida

```bash
# 1. Instalar dependências
pip install ultralytics opencv-python pillow pandas numpy

# 2. Verificar GPU (opcional)
python -c "import torch; print(f'GPU: {torch.cuda.is_available() or torch.backends.mps.is_available()}')"
```

## Execução Rápida

### Opção 1: Teste (1 simulação)

```bash
# Do diretório raiz do projeto
cd /Users/jwcunha/Documents/repos/phd-datascience/visao-computacional/projeto-estudo-comparativo

python 2_classificators/yolo11/YOLO11EmotionClassifier.py --simulation 1
```

### Opção 2: Completo (30 simulações)

```bash
cd /Users/jwcunha/Documents/repos/phd-datascience/visao-computacional/projeto-estudo-comparativo

python 2_classificators/yolo11/YOLO11EmotionClassifier.py --num_simulations 30
```

### Opção 3: Usar script shell

```bash
# Tornar executável
chmod +x 2_classificators/yolo11/run_yolo11.sh

# Executar
./2_classificators/yolo11/run_yolo11.sh 30
```

## Estimativas

### Tempo (com GPU)
- Por simulação: ~0.5-2 segundos
- 30 simulações: ~15-60 segundos

### Tempo (sem GPU - CPU)
- Por simulação: ~3-10 segundos
- 30 simulações: ~1.5-5 minutos

### Acurácia Esperada
- Geral: 70-85%
- Alegria: 75-90%
- Raiva: 65-80%

## Resultados

Após execução:

```bash
# Ver CSV
cat 3_simulation/results/yolo11_emotion/results.csv | column -t -s,

# Ver estatísticas
cat 3_simulation/results/yolo11_emotion/stats.json | python -m json.tool

# Comparar com Roboflow
python -c "
import pandas as pd
yolo = pd.read_csv('3_simulation/results/yolo11_emotion/results.csv')
robo = pd.read_csv('3_simulation/results/roboflow_emotion/results.csv')
print(f'YOLO11: {yolo[\"acuracia_geral\"].mean():.2%}')
print(f'Roboflow: {robo[\"acuracia_geral\"].mean():.2%}')
"
```

## Troubleshooting

### "No module named 'ultralytics'"
```bash
pip install ultralytics
```

### Muito lento
```bash
# Verificar se GPU está sendo usada
python -c "import torch; print(torch.cuda.is_available())"

# Se não tem GPU, usar modelo nano (mais rápido)
python 2_classificators/yolo11/YOLO11EmotionClassifier.py \
    --model_type yolov8n-cls.pt \
    --num_simulations 30
```

### GPU out of memory
```bash
# Usar CPU
python 2_classificators/yolo11/YOLO11EmotionClassifier.py \
    --device cpu \
    --num_simulations 30
```

## Próximos Passos

1. Execute todas as simulações
2. Compare resultados com Roboflow e CNN
3. Analise qual abordagem é melhor para seu caso
4. Documente conclusões

## Vantagens do YOLO11

- Rápido (10-50x mais que Roboflow API)
- Sem custo por requisição
- Funciona offline
- Controle total

**Pronto para executar!** 🚀
