# Avaliacao Automatica de Qualidade de Imagens Geradas

Este modulo implementa uma metodologia formal e automatizada para avaliar a qualidade dos checkpoints do modelo LoRA de Stable Diffusion.

## Visao Geral

A avaliacao de checkpoints e essencial para:
1. Identificar o melhor checkpoint para producao
2. Evitar overfitting (checkpoints tardios podem ter pior desempenho)
3. Tomar decisoes baseadas em metricas objetivas, nao apenas inspecao visual
4. Documentar formalmente a qualidade do modelo

## Arquivos Principais

- **evaluate_all_checkpoints.py**: Script principal para avaliacao automatizada de todos os checkpoints
- **calculate_metrics.py**: Calcula FID e CLIP Score para um conjunto de imagens
- **prepare_prompts.py**: Prepara arquivo de prompts necessario para CLIP Score
- **METODOLOGIA_AVALIACAO.md**: Documentacao completa da metodologia cientifica
- **QUICK_START.md**: Guia rapido para execucao em 5 minutos
- **requirements.txt**: Dependencias necessarias

## Metricas Implementadas

### 1. FID (Frechet Inception Distance)
Mede qualidade e diversidade das imagens comparando distribuicoes de features.
- **Valores menores = melhor** (0 = ideal)
- FID < 20: Excelente | FID < 50: Bom | FID > 100: Ruim

### 2. CLIP Score
Mede alinhamento semantico entre prompts de texto e imagens.
- **Valores maiores = melhor** (escala 0-100)
- CLIP > 30: Excelente | CLIP > 25: Bom | CLIP < 20: Ruim

## Inicio Rapido

### 1. Instalar

```bash
pip install -r requirements.txt
```

### 2. Avaliar Todos os Checkpoints

```bash
python evaluate_all_checkpoints.py \
    --real_images_dir ../data/casual_shoes/train/images \
    --validation_base_dir ../training/outputs/lora_casual_shoes_3000steps_full/validation \
    --output_dir ./results
```

### 3. Ver Resultados

```bash
cat results/comparative_report.md
```

**Para mais detalhes**, veja [QUICK_START.md](QUICK_START.md)

## Indice

- [Instalacao](#instalacao)
- [Metricas Implementadas](#metricas-implementadas)
  - [FID (Frechet Inception Distance)](#fid-frechet-inception-distance)
  - [CLIP Score](#clip-score)
- [Uso Rapido](#uso-rapido)
- [Uso Detalhado](#uso-detalhado)
- [Avaliacao de Checkpoints](#avaliacao-de-checkpoints)
- [Interpretacao dos Resultados](#interpretacao-dos-resultados)
- [Exemplos](#exemplos)
- [Troubleshooting](#troubleshooting)

## Instalacao

### 1. Instalar dependencias

```bash
cd evaluation
pip install -r requirements.txt
```

**Nota para Apple Silicon (M1/M2/M3):**
```bash
# Certifique-se de ter PyTorch com suporte MPS
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

**Nota para CUDA:**
```bash
# Instale PyTorch com suporte CUDA apropriado
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### 2. Verificar instalacao

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import clip; print('CLIP instalado com sucesso')"
```

## Metricas Implementadas

### FID (Frechet Inception Distance)

**O que e:**
- Metrica estatistica que compara a distribuicao de features entre imagens reais e geradas
- Usa o modelo Inception v3 pre-treinado em ImageNet para extrair features
- Calcula a distancia de Frechet entre as distribuicoes gaussianas multivariadas

**Como funciona:**
1. Extrai features de 2048 dimensoes de cada imagem usando Inception v3
2. Calcula media e matriz de covariancia para imagens reais e geradas
3. Aplica a formula da distancia de Frechet:
   ```
   FID = ||μ_real - μ_gen||² + Tr(Σ_real + Σ_gen - 2√(Σ_real · Σ_gen))
   ```

**Interpretacao:**
- **Valores menores sao melhores** (0 = identico ao real)
- FID < 10: Excelente qualidade
- FID < 20: Muito boa qualidade
- FID < 50: Boa qualidade
- FID < 100: Razoavel
- FID >= 100: Qualidade ruim

**Vantagens:**
- Considera tanto qualidade quanto diversidade
- Padrão da industria para avaliar GANs e modelos generativos
- Correlaciona bem com avaliacao humana

**Limitacoes:**
- Requer numero significativo de imagens (minimo ~50, ideal >1000)
- Sensivel ao tamanho do dataset
- Pode ser influenciado por artefatos de compressao

### CLIP Score

**O que e:**
- Metrica que mede o alinhamento semantico entre texto (prompt) e imagem
- Usa o modelo CLIP (Contrastive Language-Image Pre-training) da OpenAI
- Calcula similaridade coseno entre embeddings de texto e imagem

**Como funciona:**
1. Codifica a imagem em um embedding de 512 dimensoes
2. Codifica o prompt em um embedding de 512 dimensoes
3. Calcula similaridade coseno normalizada:
   ```
   score = (image_emb · text_emb) / (||image_emb|| × ||text_emb||) × 100
   ```

**Interpretacao:**
- **Valores maiores sao melhores** (escala 0-100)
- CLIP > 30: Excelente alinhamento texto-imagem
- CLIP > 27: Muito bom alinhamento
- CLIP > 25: Bom alinhamento
- CLIP > 20: Razoavel
- CLIP <= 20: Alinhamento ruim

**Vantagens:**
- Mede alinhamento semantico especifico ao prompt
- Funciona com poucas imagens
- Multimodal (entende texto e imagem simultaneamente)

**Limitacoes:**
- Nao mede qualidade visual absoluta (resolucao, nitidez)
- Pode dar scores altos para imagens de baixa qualidade se alinhadas ao texto
- Dependente da qualidade do prompt

## Uso Rapido

### Calcular FID e CLIP Score

```bash
# 1. Preparar arquivo de prompts (se necessario para CLIP Score)
python prepare_prompts.py \
    --images_dir ../api/generated_images \
    --output prompts.json \
    --default_prompt "A professional product photo of casual shoes"

# 2. Calcular metricas
python calculate_metrics.py \
    --real_images_dir ../data/casual_shoes/train/images \
    --generated_images_dir ../api/generated_images \
    --prompts_file prompts.json \
    --output_file results.json
```

### Calcular apenas FID (mais rapido)

```bash
python calculate_metrics.py \
    --real_images_dir ../data/casual_shoes/train/images \
    --generated_images_dir ../api/generated_images \
    --skip_clip \
    --output_file results_fid_only.json
```

### Calcular apenas CLIP Score

```bash
python calculate_metrics.py \
    --real_images_dir ../data/casual_shoes/train/images \
    --generated_images_dir ../api/generated_images \
    --prompts_file prompts.json \
    --skip_fid \
    --output_file results_clip_only.json
```

## Uso Detalhado

### Script: calculate_metrics.py

Calcula FID e/ou CLIP Score para avaliar qualidade das imagens.

**Parametros principais:**

| Parametro | Obrigatorio | Descricao |
|-----------|-------------|-----------|
| `--real_images_dir` | Sim | Diretorio com imagens reais do dataset |
| `--generated_images_dir` | Sim | Diretorio com imagens geradas |
| `--prompts_file` | Nao* | Arquivo JSON com prompts (necessario para CLIP Score) |
| `--output_file` | Nao | Arquivo de saida JSON (padrao: `metrics_results.json`) |
| `--batch_size` | Nao | Tamanho do batch (padrao: 32) |
| `--device` | Nao | Dispositivo: `auto`, `cuda`, `mps`, `cpu` (padrao: `auto`) |
| `--skip_fid` | Nao | Pula calculo do FID |
| `--skip_clip` | Nao | Pula calculo do CLIP Score |

\* Obrigatorio se `--skip_clip` nao for usado

**Exemplos:**

```bash
# Exemplo basico com ambas as metricas
python calculate_metrics.py \
    --real_images_dir ../data/casual_shoes/train/images \
    --generated_images_dir ../api/generated_images \
    --prompts_file prompts.json

# Especificar dispositivo e batch size
python calculate_metrics.py \
    --real_images_dir ../data/casual_shoes/train/images \
    --generated_images_dir ../api/generated_images \
    --prompts_file prompts.json \
    --device mps \
    --batch_size 16 \
    --output_file metrics_checkpoint_2000.json

# Comparar diferentes checkpoints
python calculate_metrics.py \
    --real_images_dir ../data/casual_shoes/train/images \
    --generated_images_dir ../training/outputs/lora_casual_shoes_3000steps_full/validation/checkpoint-2000 \
    --skip_clip \
    --output_file fid_checkpoint_2000.json
```

### Script: prepare_prompts.py

Prepara arquivo de prompts necessario para calcular CLIP Score.

**Parametros principais:**

| Parametro | Obrigatorio | Descricao |
|-----------|-------------|-----------|
| `--images_dir` | Sim | Diretorio com imagens geradas |
| `--output` | Sim | Arquivo de saida JSON |
| `--from_filename` | Nao | Extrai prompts dos nomes de arquivo |
| `--default_prompt` | Nao | Usa mesmo prompt para todas as imagens |
| `--metadata_file` | Nao | Le prompts de arquivo de metadados |
| `--from_batch_dirs` | Nao | Extrai prompts de nomes de diretorios batch |

**Exemplos:**

```bash
# Usar prompt padrao para todas as imagens
python prepare_prompts.py \
    --images_dir ../api/generated_images \
    --output prompts.json \
    --default_prompt "A professional product photo of casual shoes"

# Extrair de diretorios batch (ex: prompt_1_description/)
python prepare_prompts.py \
    --images_dir ../api/generated_batch/batch_20251027_232616 \
    --output prompts_batch.json \
    --from_batch_dirs

# Ler de arquivo de metadados
python prepare_prompts.py \
    --images_dir ../api/generated_images \
    --output prompts.json \
    --metadata_file ../api/generation_metadata.json
```

## Avaliacao de Checkpoints

### Script: evaluate_all_checkpoints.py

Este e o script principal para avaliacao formal e automatizada de todos os checkpoints do treinamento LoRA.

**Funcionalidade**:
- Detecta automaticamente checkpoints disponiveis
- Calcula FID e CLIP Score para cada checkpoint
- Gera relatorio comparativo identificando o melhor checkpoint
- Fornece recomendacao baseada em criterios objetivos

**Uso Basico**:

```bash
python evaluate_all_checkpoints.py \
    --real_images_dir ../data/casual_shoes/train/images \
    --validation_base_dir ../training/outputs/lora_casual_shoes_3000steps_full/validation \
    --output_dir ./checkpoint_evaluation_results
```

**Parametros**:

| Parametro | Obrigatorio | Descricao |
|-----------|-------------|-----------|
| `--real_images_dir` | Sim | Diretorio com imagens reais do dataset |
| `--validation_base_dir` | Sim | Diretorio base contendo subdiretorios checkpoint-N |
| `--output_dir` | Nao | Diretorio de saida (default: ./checkpoint_evaluation_results) |
| `--checkpoints` | Nao | Lista de checkpoints a avaliar (default: 500 1000 1500 2000 2500 3000) |
| `--skip_fid` | Nao | Pula calculo de FID |
| `--skip_clip` | Nao | Pula calculo de CLIP Score |

**Exemplos**:

```bash
# Avaliar apenas checkpoints especificos
python evaluate_all_checkpoints.py \
    --real_images_dir ../data/casual_shoes/train/images \
    --validation_base_dir ../training/outputs/lora_casual_shoes_3000steps_full/validation \
    --checkpoints 1500 2000 2500 3000

# Apenas FID (mais rapido, ~10 min)
python evaluate_all_checkpoints.py \
    --real_images_dir ../data/casual_shoes/train/images \
    --validation_base_dir ../training/outputs/lora_casual_shoes_3000steps_full/validation \
    --skip_clip

# Apenas CLIP Score
python evaluate_all_checkpoints.py \
    --real_images_dir ../data/casual_shoes/train/images \
    --validation_base_dir ../training/outputs/lora_casual_shoes_3000steps_full/validation \
    --skip_fid
```

**Arquivos Gerados**:

```
checkpoint_evaluation_results/
├── consolidated_results.json          # Todos os resultados em JSON
├── comparative_report.md              # Relatorio comparativo em Markdown
├── metrics_checkpoint_500.json        # Metricas individuais
├── metrics_checkpoint_1000.json
├── metrics_checkpoint_1500.json
├── metrics_checkpoint_2000.json
├── metrics_checkpoint_2500.json
├── metrics_checkpoint_3000.json
└── prompts_checkpoint_*.json          # Arquivos de prompts
```

**Saida Esperada**:

```
======================================================================
VERIFICACAO DE CHECKPOINTS DISPONIVEIS
======================================================================
  [OK] Checkpoint 500: 4 imagens encontradas
  [OK] Checkpoint 1000: 8 imagens encontradas
  [OK] Checkpoint 1500: 16 imagens encontradas
  [OK] Checkpoint 2000: 4 imagens encontradas
  [OK] Checkpoint 2500: 4 imagens encontradas
  [OK] Checkpoint 3000: 8 imagens encontradas

Resumo: 6/6 checkpoints disponiveis

======================================================================
AVALIANDO CHECKPOINT 500
======================================================================
  [1/2] Preparando prompts...
  [2/2] Calculando metricas (FID=True, CLIP=True)...
  FID Score: 85.34 (Razoavel (< 100))
  CLIP Score: 22.15 ± 3.21 (Ruim (<= 20))

...

======================================================================
RELATORIO COMPARATIVO
======================================================================

| Checkpoint | FID Score | CLIP Score      | Interpretacao |
|------------|-----------|-----------------|---------------|
| 500        | 85.34     | 22.15 ± 3.21   | Razoavel      |
| 1000       | 62.78     | 24.82 ± 2.45   | Razoavel      |
| 1500       | 35.21     | 27.34 ± 1.89   | Bom           |
| 2000       | 28.12     | 28.91 ± 1.56   | Excelente     |
| 2500       | 29.47     | 28.67 ± 1.71   | Excelente     |
| 3000       | 31.25     | 27.83 ± 2.01   | Bom           |

RECOMENDACAO PARA PRODUCAO
Checkpoint Recomendado: 2000

- FID Score: 28.12 (Muito Bom)
- CLIP Score: 28.91 (Excelente)
```

**Tempo de Execucao Estimado**:

| Hardware | FID (6 ckpts) | CLIP (6 ckpts) | Total |
|----------|---------------|----------------|-------|
| Apple M2 Pro | ~15 min | ~10 min | ~25 min |
| CPU i7 | ~30 min | ~20 min | ~50 min |
| GPU RTX 3080 | ~8 min | ~6 min | ~14 min |

**Documentacao Adicional**:

- [METODOLOGIA_AVALIACAO.md](METODOLOGIA_AVALIACAO.md): Fundamentacao teorica completa
- [QUICK_START.md](QUICK_START.md): Guia rapido passo a passo

## Interpretacao dos Resultados

### Formato do arquivo de saida (JSON)

```json
{
  "metadata": {
    "real_images_count": 1991,
    "generated_images_count": 100,
    "device": "mps",
    "real_images_dir": "/path/to/real/images",
    "generated_images_dir": "/path/to/generated/images"
  },
  "fid": {
    "score": 23.45,
    "interpretation": "Muito Bom (< 20)"
  },
  "clip_score": {
    "mean": 28.67,
    "std": 2.34,
    "min": 23.12,
    "max": 32.45,
    "median": 28.89,
    "interpretation": "Muito Bom (> 27)",
    "individual_scores": [28.1, 29.3, ...]
  }
}
```

### Analise Combinada

Para uma avaliacao completa, considere ambas as metricas:

| FID | CLIP Score | Interpretacao |
|-----|------------|---------------|
| < 20 | > 27 | **Excelente**: Alta qualidade e alinhamento perfeito |
| < 50 | > 25 | **Bom**: Qualidade aceitavel com bom alinhamento |
| < 50 | < 20 | **Problema**: Imagens OK mas nao seguem os prompts |
| > 100 | > 25 | **Problema**: Baixa qualidade mas segue prompts |
| > 100 | < 20 | **Ruim**: Baixa qualidade e nao segue prompts |

### Exemplo de Analise

```python
import json

# Carregar resultados
with open('metrics_results.json', 'r') as f:
    results = json.load(f)

fid = results['fid']['score']
clip_mean = results['clip_score']['mean']
clip_std = results['clip_score']['std']

print(f"FID Score: {fid:.2f}")
print(f"CLIP Score: {clip_mean:.2f} ± {clip_std:.2f}")

# Analise
if fid < 20 and clip_mean > 27:
    print("Status: EXCELENTE - Modelo pronto para producao")
elif fid < 50 and clip_mean > 25:
    print("Status: BOM - Pode ser melhorado com mais treinamento")
elif fid > 100:
    print("Status: PRECISA RETREINAR - Qualidade muito baixa")
elif clip_mean < 20:
    print("Status: REVISAR PROMPTS - Baixo alinhamento texto-imagem")
```

## Exemplos

### Exemplo 1: Avaliar checkpoint especifico

```bash
# Preparar prompts
python prepare_prompts.py \
    --images_dir ../training/outputs/lora_casual_shoes_3000steps_full/validation/checkpoint-2000 \
    --output prompts_ckpt2000.json \
    --default_prompt "A professional product photo of casual shoes"

# Calcular metricas
python calculate_metrics.py \
    --real_images_dir ../data/casual_shoes/train/images \
    --generated_images_dir ../training/outputs/lora_casual_shoes_3000steps_full/validation/checkpoint-2000 \
    --prompts_file prompts_ckpt2000.json \
    --output_file metrics_checkpoint_2000.json \
    --device mps
```

### Exemplo 2: Comparar multiplos checkpoints

```bash
#!/bin/bash

# Script para avaliar todos os checkpoints
CHECKPOINTS=(500 1000 1500 2000 2500 3000)
REAL_DIR="../data/casual_shoes/train/images"
OUTPUT_BASE="../training/outputs/lora_casual_shoes_3000steps_full"

for ckpt in "${CHECKPOINTS[@]}"; do
    echo "Avaliando checkpoint $ckpt..."

    gen_dir="$OUTPUT_BASE/validation/checkpoint-$ckpt"

    # Pula se diretorio nao existe
    if [ ! -d "$gen_dir" ]; then
        echo "  Diretorio nao encontrado: $gen_dir"
        continue
    fi

    # Calcula apenas FID (mais rapido)
    python calculate_metrics.py \
        --real_images_dir "$REAL_DIR" \
        --generated_images_dir "$gen_dir" \
        --skip_clip \
        --output_file "results_checkpoint_${ckpt}.json" \
        --device mps

    echo "  Resultados salvos em: results_checkpoint_${ckpt}.json"
done

echo "Avaliacao completa!"
```

### Exemplo 3: Avaliar imagens da API

```bash
# Para imagens geradas pela API REST
python prepare_prompts.py \
    --images_dir ../api/generated_images \
    --output prompts_api.json \
    --from_filename

python calculate_metrics.py \
    --real_images_dir ../data/casual_shoes/train/images \
    --generated_images_dir ../api/generated_images \
    --prompts_file prompts_api.json \
    --output_file metrics_api_generated.json
```

### Exemplo 4: Avaliar batch de imagens

```bash
# Para imagens geradas em batch (com prompts nos nomes dos diretorios)
python prepare_prompts.py \
    --images_dir ../api/generated_batch/batch_20251027_232616 \
    --output prompts_batch.json \
    --from_batch_dirs

python calculate_metrics.py \
    --real_images_dir ../data/casual_shoes/train/images \
    --generated_images_dir ../api/generated_batch/batch_20251027_232616 \
    --prompts_file prompts_batch.json \
    --output_file metrics_batch.json
```

## Troubleshooting

### Erro: "CUDA out of memory"

**Solucao:**
```bash
# Reduzir batch size
python calculate_metrics.py ... --batch_size 8

# Ou usar CPU (mais lento)
python calculate_metrics.py ... --device cpu
```

### Erro: "No module named 'clip'"

**Solucao:**
```bash
pip install git+https://github.com/openai/CLIP.git
```

### Erro: "MPS backend out of memory"

**Solucao:**
```bash
# Para Apple Silicon, usar batch size menor
python calculate_metrics.py ... --batch_size 8 --device mps

# Ou usar CPU
python calculate_metrics.py ... --device cpu
```

### Aviso: "Not enough images for reliable FID"

**Explicacao:**
FID requer numero significativo de imagens para estimar distribuicoes. Idealmente:
- Minimo: 50 imagens
- Recomendado: 100+ imagens
- Ideal: 1000+ imagens

**Solucao:**
- Gerar mais imagens, ou
- Usar apenas CLIP Score (funciona bem com poucas imagens)

### FID muito alto (> 200)

**Possiveis causas:**
1. Modelo subtreinado ou overtreinado
2. Mismatch entre dataset real e gerado (resolucao, estilo)
3. Dataset gerado muito pequeno
4. Problemas na geracao (artefatos, baixa qualidade)

**Solucoes:**
- Verificar qualidade visual das imagens geradas
- Comparar com checkpoints anteriores
- Aumentar numero de steps de treinamento
- Ajustar hyperparametros (learning rate, rank LoRA)

### CLIP Score baixo (< 20)

**Possiveis causas:**
1. Prompts nao correspondem as imagens
2. Prompts muito vagos ou genericos
3. Imagens geradas nao seguem os prompts

**Solucoes:**
- Revisar arquivo de prompts
- Usar prompts mais especificos e descritivos
- Verificar se o modelo foi treinado com prompts similares
- Ajustar prompt no tempo de inferencia

## Benchmark de Performance

Hardware testado: Apple M2 Pro (16GB RAM)

| Operacao | Tempo (100 imagens) | Memoria |
|----------|---------------------|---------|
| Extracao de features (FID) | ~30s | ~2GB |
| Calculo de FID | <1s | ~100MB |
| CLIP Score (individual) | ~0.2s/imagem | ~1.5GB |
| CLIP Score (100 imagens) | ~20s | ~1.5GB |
| **Total (FID + CLIP)** | **~50s** | **~2GB** |

**Nota:** Tempos variam com hardware, batch size e resolucao das imagens.

## Referencias

- FID: [GANs Trained by a Two Time-Scale Update Rule Converge to a Local Nash Equilibrium](https://arxiv.org/abs/1706.08500)
- CLIP: [Learning Transferable Visual Models From Natural Language Supervision](https://arxiv.org/abs/2103.00020)
- Clean-FID: [On Aliased Resizing and Surprising Subtleties in GAN Evaluation](https://arxiv.org/abs/2104.11222)
