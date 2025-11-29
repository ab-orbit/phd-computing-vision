# Classificador de Emoções - YOLO11

## Visão Geral

Este módulo implementa um classificador de emoções faciais usando YOLO11 (Ultralytics) rodando localmente, sem necessidade de APIs externas.

## Objetivo Pedagógico

### Por que usar YOLO11?

1. **Modelo Foundation Local**: Acesso a modelo state-of-the-art sem APIs
2. **Velocidade**: Extremamente rápido, especialmente com GPU
3. **Sem Custos Recorrentes**: Após download, sem custo por requisição
4. **Offline**: Funciona sem conexão à internet
5. **Flexibilidade**: Pode ser fine-tunado para domínio específico

### Comparação com Outras Abordagens

| Aspecto | CNN do Zero | Roboflow API | YOLO11 Local |
|---------|-------------|--------------|--------------|
| Treinamento | Necessário | Não | Não (pré-treinado) |
| Velocidade | Média | Lenta (rede) | Rápida (local) |
| Custo | GPU (uma vez) | $/requisição | GPU (uma vez) |
| Customização | Total | Limitada | Moderada |
| Offline | Sim | Não | Sim |

## Instalação

### Dependências

```bash
pip install -r requirements.txt
```

### Verificar GPU (Opcional mas Recomendado)

```bash
# NVIDIA GPU
python -c "import torch; print(f'CUDA disponível: {torch.cuda.is_available()}')"

# Apple Silicon (M1/M2/M3)
python -c "import torch; print(f'MPS disponível: {torch.backends.mps.is_available()}')"
```

## YOLO11 - Modelos Disponíveis

YOLO11 oferece 5 variantes com trade-off entre velocidade e precisão:

| Modelo | Tamanho | Velocidade | Precisão | Uso Recomendado |
|--------|---------|------------|----------|-----------------|
| yolov8n-cls.pt | 3 MB | Muito Rápido | Boa | Produção, tempo real |
| yolov8s-cls.pt | 10 MB | Rápido | Melhor | Balanceado |
| yolov8m-cls.pt | 25 MB | Médio | Muito Boa | Precisão > Velocidade |
| yolov8l-cls.pt | 50 MB | Lento | Excelente | Pesquisa |
| yolov8x-cls.pt | 100 MB | Muito Lento | Máxima | Benchmarks |

**Padrão deste projeto**: yolov8n-cls.pt (nano) - equilíbrio ideal

## Uso

### Via Linha de Comando

#### 1. Processar todas as 30 simulações

```bash
# Do diretório raiz do projeto
cd /Users/jwcunha/Documents/repos/phd-datascience/visao-computacional/projeto-estudo-comparativo

python 2_classificators/yolo11/YOLO11EmotionClassifier.py --num_simulations 30
```

#### 2. Processar apenas uma simulação (teste)

```bash
python 2_classificators/yolo11/YOLO11EmotionClassifier.py --simulation 1
```

#### 3. Usar modelo diferente

```bash
# Modelo Small (mais preciso, mais lento)
python 2_classificators/yolo11/YOLO11EmotionClassifier.py \
    --model_type yolov8s-cls.pt \
    --num_simulations 30
```

#### 4. Forçar uso de CPU

```bash
python 2_classificators/yolo11/YOLO11EmotionClassifier.py \
    --device cpu \
    --num_simulations 30
```

### Via Python (importando a classe)

```python
from YOLO11EmotionClassifier import YOLO11EmotionClassifier

# Inicializa classificador
classifier = YOLO11EmotionClassifier(
   model_type='yolov8n-cls.pt',
   dataset_dir='../../../datasets',
   results_dir='../../../3_simulation/results',
   model_name='yolo11_emotion',
   device='auto'  # auto-detecta GPU
)

# Processar uma simulação
results = classifier.process_simulation(1)
print(f"Acurácia: {results['acuracia_geral']:.2%}")

# Processar todas as simulações
df = classifier.process_all_simulations(num_simulations=30)
print(df.describe())
```

## Estrutura de Saída

### Formato de Arquivos

```
3_simulation/results/yolo11_emotion/
├── results.csv           # Resultados principais (atualizado incrementalmente)
├── stats.json            # Estatísticas agregadas
└── partial_results.csv   # Backup incremental
```

### CSV (results.csv)

```csv
numero_simulacao,nome_modelo,qtd_sucesso_alegria,qtd_sucesso_raiva,total_alegria,total_raiva,tempo_total_ms,acuracia_alegria,acuracia_raiva,acuracia_geral
1,yolo11_emotion,42,38,50,50,1234.56,0.84,0.76,0.80
2,yolo11_emotion,40,36,50,50,1198.23,0.80,0.72,0.76
...
```

### JSON (stats.json)

```json
{
  "modelo": "yolo11_emotion",
  "model_type": "yolov8n-cls.pt",
  "device": "cuda",
  "num_simulations": 30,
  "acuracia_alegria_mean": 0.82,
  "acuracia_alegria_std": 0.05,
  "acuracia_raiva_mean": 0.75,
  "acuracia_raiva_std": 0.06,
  "acuracia_geral_mean": 0.785,
  "acuracia_geral_std": 0.04,
  "tempo_total_segundos": 45.67,
  "tempo_medio_por_simulacao": 1.52,
  "timestamp": "2025-11-29T12:00:00"
}
```

## Performance Esperada

### Velocidade (por simulação - 100 imagens)

| Dispositivo | Modelo Nano | Modelo Small | Modelo Medium |
|-------------|-------------|--------------|---------------|
| CPU | ~3-5s | ~8-12s | ~20-30s |
| NVIDIA GPU | ~0.5-1s | ~1-2s | ~3-5s |
| Apple M1/M2 | ~1-2s | ~2-4s | ~5-10s |

### Acurácia Esperada

Baseado em modelos foundation similares:
- **Acurácia Geral**: 70-85%
- **Acurácia Alegria**: 75-90%
- **Acurácia Raiva**: 65-80%

*Nota: YOLO11 pré-treinado pode não ter classes específicas de emoções.
Performance dependerá do mapeamento de classes genéricas.*

## Como Funciona

### Pipeline de Classificação

1. **Carregamento do Modelo**
   - YOLO11 carrega pesos pré-treinados
   - Auto-detecta melhor dispositivo (GPU/CPU)

2. **Processamento de Imagem**
   - Redimensiona para tamanho de entrada do YOLO
   - Normaliza pixels
   - Passa pela rede neural

3. **Inferência**
   - YOLO retorna probabilidades para classes
   - Muito rápido (~2-50ms por imagem)

4. **Mapeamento**
   - Mapeia classes genéricas para raiva/alegria
   - Aplica threshold de confiança

5. **Salvamento**
   - Resultados salvos incrementalmente
   - CSV atualizado após cada simulação

## Vantagens e Desvantagens

### Vantagens

1. **Velocidade**: 10-50x mais rápido que API Roboflow
2. **Custo**: Sem custos recorrentes
3. **Privacidade**: Dados não saem do seu computador
4. **Offline**: Funciona sem internet
5. **Controle**: Total controle sobre inferência

### Desvantagens

1. **Hardware**: Requer GPU para velocidade ideal
2. **Download Inicial**: ~3-100MB dependendo do modelo
3. **Classes Limitadas**: Modelo pré-treinado pode não ter emoções específicas
4. **Fine-tuning**: Para melhor performance, requer fine-tuning

## Troubleshooting

### Erro: "No module named 'ultralytics'"

```bash
pip install ultralytics
```

### Erro: "CUDA out of memory"

Use modelo menor ou CPU:

```bash
python YOLO11EmotionClassifier.py --model_type yolov8n-cls.pt --device cpu
```

### Baixa Acurácia

1. Modelo pré-treinado pode não ter classes de emoções
2. Considere fine-tuning com seu dataset
3. Teste modelos maiores (yolo11s, yolo11m)

### Lentidão

1. Verifique se está usando GPU
2. Use modelo menor (yolo11n)
3. Reduza batch size

## Fine-tuning (Opcional)

Para melhor performance, você pode fine-tunar YOLO11 no seu dataset:

```python
from ultralytics import YOLO

# Carrega modelo pré-treinado
model = YOLO('yolov8n-cls.pt')

# Fine-tuna no seu dataset
model.train(
    data='path/to/your/dataset',
    epochs=50,
    imgsz=128,
    device='auto'
)

# Salva modelo fine-tunado
model.save('yolo11n-emotions-finetuned.pt')
```

## Comparação de Resultados

Após executar, compare com outros modelos:

```python
import pandas as pd

# Carrega resultados
yolo = pd.read_csv('3_simulation/results/yolo11_emotion/results.csv')
roboflow = pd.read_csv('3_simulation/results/roboflow_emotion/results.csv')

# Compara acurácia média
print(f"YOLO11: {yolo['acuracia_geral'].mean():.2%}")
print(f"Roboflow: {roboflow['acuracia_geral'].mean():.2%}")
```

## Referências

- [Ultralytics YOLO11](https://docs.ultralytics.com/models/yolo11/) - Documentação oficial
- [YOLO11 GitHub](https://github.com/ultralytics/ultralytics) - Código fonte
- [YOLO11 Paper](https://arxiv.org/abs/2304.00501) - Artigo científico

## Licença

- Código deste classificador: Uso educacional livre
- YOLO11 (Ultralytics): [AGPL-3.0](https://github.com/ultralytics/ultralytics/blob/main/LICENSE)
