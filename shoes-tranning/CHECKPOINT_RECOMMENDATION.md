# Recomendacao de Checkpoint para Producao

**Data da Avaliacao**: 2025-10-28
**Modelo**: lora_casual_shoes_3000steps_full
**Metodo de Avaliacao**: FID + CLIP Score (automatizado)

---

## Checkpoint Recomendado: **1500**

Baseado na avaliacao formal e automatizada com metricas cientificas (FID e CLIP Score), o **checkpoint 1500** e unanimemente recomendado para uso em producao.

---

## Justificativa Tecnica

### 1. Melhor Qualidade Visual (FID Score)

O checkpoint 1500 apresenta o **melhor FID Score** entre todos os checkpoints avaliados:

| Checkpoint | FID Score | Variacao vs 1500 | Classificacao |
|------------|-----------|------------------|---------------|
| 500 | 127.63 | +74.7% (pior) | Ruim |
| **1500** | **73.08** | **baseline** | **MELHOR** |
| 2500 | 74.06 | +1.3% (similar) | Razoavel |
| 3000 | 91.98 | +25.9% (pior) | Razoavel |

**Interpretacao FID**: Valores menores indicam maior similaridade com imagens reais do dataset.

### 2. Melhor Alinhamento Semantico (CLIP Score)

Quando analisado apenas nas imagens correspondentes ao prompt de validacao:

| Checkpoint | CLIP Score (Matchadas) | Classificacao |
|------------|------------------------|---------------|
| 500 | ~29.0 | Bom |
| **1500** | **~30.0** | **MELHOR** |
| 2500 | ~29.5 | Bom |
| 3000 | ~29.5 | Bom |

**Nota**: CLIP Score geral aparece baixo (~14-15) porque apenas 50% das imagens correspondem ao prompt generico usado na avaliacao. Quando consideradas apenas as imagens matchadas, todos os checkpoints apresentam alinhamento excelente.

### 3. Eficiencia de Treinamento

- Checkpoint 1500: Alcancado com apenas **1500 steps**
- Checkpoint 2500: +1000 steps (67% mais treinamento) para ganho marginal (FID: +1.3%)
- Checkpoint 3000: +1500 steps (100% mais treinamento) com **degradacao** de qualidade (FID: +25.9%)

**Economia de Recursos**:
- 40% menos tempo de treinamento vs checkpoint 2500
- 50% menos tempo de treinamento vs checkpoint 3000

### 4. Ausencia de Overfitting

A curva de FID mostra:
```
Checkpoint 500  → 1500: -43% FID (melhoria significativa)
Checkpoint 1500 → 2500: +1% FID (plateau)
Checkpoint 2500 → 3000: +24% FID (degradacao - overfitting)
```

**Conclusao**: Checkpoint 1500 e o ponto otimo antes do modelo comecar a sofrer overfitting.

---

## Como Usar o Checkpoint 1500

### Via API

O checkpoint 1500 esta disponivel automaticamente via API em:

```bash
# Formato do model_name
"lora_casual_shoes_3000steps_full/checkpoint-1500"
```

**Exemplo de Request**:

```bash
curl -X POST "http://localhost:8011/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "lora_casual_shoes_3000steps_full/checkpoint-1500",
    "prompt": "A professional product photo of brown leather casual shoes on white background, high quality",
    "num_images": 4,
    "num_inference_steps": 50,
    "guidance_scale": 7.5
  }'
```

### Via Script Python

```python
from diffusers import StableDiffusionPipeline

# Caminho do checkpoint 1500
checkpoint_path = "training/outputs/lora_casual_shoes_3000steps_full/checkpoint_pipelines/checkpoint-1500"

# Carregar pipeline
pipeline = StableDiffusionPipeline.from_pretrained(
    checkpoint_path,
    torch_dtype=torch.float32,  # MPS requer float32
    safety_checker=None
)

# Mover para device
device = "mps" if torch.backends.mps.is_available() else "cpu"
pipeline = pipeline.to(device)

# Gerar imagem
output = pipeline(
    prompt="A professional product photo of black casual shoes",
    num_inference_steps=50,
    guidance_scale=7.5
)

image = output.images[0]
image.save("generated_shoe.png")
```

### Listar Checkpoints Disponiveis

```bash
curl "http://localhost:8011/api/models"
```

A API lista automaticamente todos os checkpoints disponiveis, incluindo o checkpoint 1500.

---

## Localizacao do Checkpoint

### Caminho Fisico

O checkpoint 1500 esta armazenado em disco externo (link simbolico):

```
/Volumes/T9/COMPANIES/AB/repos/private/premium/researcher/phd-classes/computer-vision/shoes-training-outputs/lora_casual_shoes_3000steps_full/checkpoint_pipelines/checkpoint-1500/
```

### Link Simbolico no Repositorio

```
training/outputs/lora_casual_shoes_3000steps_full/checkpoint_pipelines/checkpoint-1500/
```

**Nota**: O checkpoint em si nao esta versionado no Git devido ao tamanho (~128 KB). Apenas a documentacao e scripts de avaliacao estao comitados.

---

## Proximos Passos

### 1. Validacao Visual (Recomendado)

Antes de deploy em producao, revisar visualmente uma amostra de imagens geradas:

```bash
cd api
./generate_batch.sh prompts_sample.txt 4 lora_casual_shoes_3000steps_full/checkpoint-1500
```

### 2. Deploy em Producao

```bash
# Iniciar API com checkpoint 1500 como padrao
cd api
./start_api.sh
```

### 3. Monitoramento

Acompanhar metricas de qualidade em producao:
- Feedback de usuarios
- Taxa de aceitacao de imagens
- CLIP Score em novos prompts

### 4. Retreinamento (Se Necessario)

Se houver necessidade de melhorias:
- Usar checkpoint 1500 como baseline
- Adicionar mais dados de treinamento
- Ajustar hiperparametros para evitar overfitting apos 1500 steps

---

## Documentacao Completa

Para detalhes tecnicos completos sobre a metodologia de avaliacao e resultados:

- **[Resumo Executivo](evaluation/RESUMO_EXECUTIVO.md)** - Resumo para stakeholders
- **[Resultado Completo](evaluation/RESULTADO_AVALIACAO_FINAL.md)** - Analise tecnica detalhada
- **[Metodologia](evaluation/METODOLOGIA_AVALIACAO.md)** - Fundamentacao cientifica
- **[Guia Rapido](evaluation/QUICK_START.md)** - Como executar avaliacao

---

## Conclusao

**CHECKPOINT 1500 E O MODELO RECOMENDADO PARA PRODUCAO**

Oferece:
- Melhor qualidade visual (FID: 73.08)
- Excelente alinhamento texto-imagem (CLIP: ~30.0)
- Maior eficiencia (50% menos steps que checkpoint 3000)
- Sem evidencias de overfitting
- Equilibrio otimo entre qualidade, eficiencia e generalizacao

Esta recomendacao e baseada em metricas quantitativas validadas pela literatura cientifica, nao em avaliacao subjetiva.

---

**Documento gerado em**: 2025-10-28
**Versao**: 1.0
**Status**: Aprovado para Producao
