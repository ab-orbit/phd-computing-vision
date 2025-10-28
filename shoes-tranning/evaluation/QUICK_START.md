# Guia Rapido: Avaliacao de Checkpoints

Guia pratico para executar avaliacao formal dos checkpoints em 5 minutos.

## Passo 1: Instalar Dependencias (2-3 minutos)

```bash
cd shoes-tranning/evaluation
pip install -r requirements.txt
```

**Tempo estimado**: 2-3 minutos (download e instalacao)

## Passo 2: Executar Avaliacao Automatizada (5-30 minutos)

### Opcao A: Avaliacao Completa (FID + CLIP Score)

```bash
python evaluate_all_checkpoints.py \
    --real_images_dir ../data/casual_shoes/train/images \
    --validation_base_dir ../training/outputs/lora_casual_shoes_3000steps_full/validation \
    --output_dir ./results
```

**Tempo estimado**: 20-30 minutos (depende do hardware)

### Opcao B: Avaliacao Rapida (Apenas FID)

```bash
python evaluate_all_checkpoints.py \
    --real_images_dir ../data/casual_shoes/train/images \
    --validation_base_dir ../training/outputs/lora_casual_shoes_3000steps_full/validation \
    --output_dir ./results \
    --skip_clip
```

**Tempo estimado**: 5-10 minutos

### Opcao C: Apenas Checkpoints Especificos

```bash
python evaluate_all_checkpoints.py \
    --real_images_dir ../data/casual_shoes/train/images \
    --validation_base_dir ../training/outputs/lora_casual_shoes_3000steps_full/validation \
    --output_dir ./results \
    --checkpoints 1500 2000 2500 3000
```

**Tempo estimado**: 10-15 minutos

## Passo 3: Ver Resultados (30 segundos)

### Ver Relatorio Comparativo

```bash
cat results/comparative_report.md
```

### Ver Resultados em JSON

```bash
cat results/consolidated_results.json | python -m json.tool
```

### Resumo Rapido

```bash
# Extrair apenas tabela de resultados
grep -A 10 "Resumo Comparativo" results/comparative_report.md
```

## Exemplo de Saida Esperada

```
======================================================================
RESUMO COMPARATIVO
======================================================================

| Checkpoint | FID Score | CLIP Score      | Num. Imagens | Interpretacao    |
|------------|-----------|-----------------|--------------|------------------|
| 500        | 85.34     | 22.15 ± 3.21   | 4            | Qualidade Baixa  |
| 1000       | 62.78     | 24.82 ± 2.45   | 8            | Razoavel         |
| 1500       | 35.21     | 27.34 ± 1.89   | 16           | Bom              |
| 2000       | 28.12     | 28.91 ± 1.56   | 4            | Excelente        |
| 2500       | 29.47     | 28.67 ± 1.71   | 4            | Excelente        |
| 3000       | 31.25     | 27.83 ± 2.01   | 8            | Bom              |

RECOMENDACAO PARA PRODUCAO
Checkpoint Recomendado: 2000

- FID Score: 28.12 (Muito Bom)
- CLIP Score: 28.91 (Excelente)

Este checkpoint oferece o melhor equilibrio entre qualidade visual (FID)
e alinhamento semantico (CLIP Score).
```

## Interpretacao Rapida

### FID Score (quanto menor, melhor)
- < 20: Excelente
- 20-50: Bom
- 50-100: Razoavel
- > 100: Ruim

### CLIP Score (quanto maior, melhor)
- > 30: Excelente
- 27-30: Muito Bom
- 25-27: Bom
- 20-25: Razoavel
- < 20: Ruim

## Troubleshooting

### Erro: "No module named 'clip'"

```bash
pip install git+https://github.com/openai/CLIP.git
```

### Erro: "CUDA out of memory"

```bash
# Usar CPU
python evaluate_all_checkpoints.py ... --device cpu

# Ou reduzir batch size (editar calculate_metrics.py linha ~16)
```

### Erro: "Nenhuma imagem encontrada"

```bash
# Verificar caminhos
ls ../data/casual_shoes/train/images/*.png | head
ls ../training/outputs/lora_casual_shoes_3000steps_full/validation/checkpoint-1500/*.png | head
```

## Proximos Passos

1. Analisar relatorio em `results/comparative_report.md`
2. Identificar checkpoint recomendado
3. Validar visualmente imagens do checkpoint selecionado
4. Usar checkpoint em producao

## Comandos Uteis

```bash
# Ver todos os arquivos de resultados
ls -lh results/

# Comparar FID de todos os checkpoints
for f in results/metrics_checkpoint_*.json; do
    ckpt=$(basename $f | grep -oP '\d+')
    fid=$(cat $f | python -c "import sys, json; print(json.load(sys.stdin).get('fid', {}).get('score', 'N/A'))")
    echo "Checkpoint $ckpt: FID = $fid"
done

# Limpar resultados antigos
rm -rf results/
```

## Performance Esperada

Hardware testado: Apple M2 Pro, 16GB RAM

| Operacao | Tempo |
|----------|-------|
| FID (6 checkpoints) | ~15 min |
| CLIP (6 checkpoints) | ~10 min |
| Total (FID + CLIP) | ~25 min |

CPU: ~2-3x mais lento
GPU CUDA: ~2x mais rapido
