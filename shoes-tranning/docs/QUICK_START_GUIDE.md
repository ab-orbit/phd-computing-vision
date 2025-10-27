# Quick Start Guide - Pipeline de Treinamento LoRA

Guia rápido para executar o pipeline de treinamento e validar os resultados.

---

## Pré-requisitos

```bash
# Python 3.10+
python --version

# PyTorch com MPS (Apple Silicon)
python -c "import torch; print(torch.backends.mps.is_available())"

# Dependências instaladas
pip install -r requirements.txt
```

---

## Passo 1: Verificar Dataset

```bash
# Navegar para o projeto
cd /path/to/shoes-tranning

# Verificar estrutura do dataset
ls -la data/casual_shoes/train/images/ | head -10

# Verificar número de imagens
ls data/casual_shoes/train/images/ | wc -l
# Deve mostrar: 1991

# Verificar captions
cat data/casual_shoes/train/captions.json | head -20
```

---

## Passo 2: Iniciar Treinamento

```bash
# Navegar para scripts
cd training/scripts

# Iniciar treinamento (modo completo - 3000 steps)
python train_lora.py \
  --max_train_steps 3000 \
  --train_batch_size 2 \
  --gradient_accumulation_steps 8 \
  --validation_steps 500 \
  --checkpointing_steps 500 \
  --num_train_epochs 100 \
  --output_dir ../outputs/lora_casual_shoes_full

# Ou usar configuração padrão
python train_lora.py
```

**Tempo estimado:** 10-11 horas em Apple M2 Max

---

## Passo 3: Monitorar Progresso

### Opção 1: Tail do Log

```bash
# Em outro terminal
cd training/scripts
tail -f training_log_full.txt
```

### Opção 2: Script de Monitoramento

```bash
# Criar script de monitoramento
cat > monitor.sh << 'EOF'
#!/bin/bash
while true; do
    clear
    echo "=== TRAINING PROGRESS ==="
    grep "Steps:" training_log_full.txt | tail -5
    echo ""
    echo "Latest checkpoint:"
    ls -lt ../outputs/lora_casual_shoes_full/checkpoints/ | head -2
    sleep 30
done
EOF

chmod +x monitor.sh
./monitor.sh
```

### Opção 3: Verificar Última Linha

```bash
grep "Steps:" training_log_full.txt | tail -1
```

---

## Passo 4: Validação Visual

### Após Step 500

```bash
# Ver imagens de validação
cd ../outputs/lora_casual_shoes_full/validation
ls -lh | head -20

# Abrir imagens no sistema
open epoch000_step00500_*
```

### Comparar Checkpoints

```bash
# Script para comparar checkpoints
python << EOF
import os
from PIL import Image
import matplotlib.pyplot as plt

val_dir = "../outputs/lora_casual_shoes_full/validation"
checkpoints = [500, 1000, 1500, 2000, 2500, 3000]

fig, axes = plt.subplots(len(checkpoints), 4, figsize=(16, len(checkpoints)*4))

for i, step in enumerate(checkpoints):
    for j in range(4):
        img_path = f"{val_dir}/epoch{i:03d}_step{step:05d}_prompt0_img{j}.png"
        if os.path.exists(img_path):
            img = Image.open(img_path)
            axes[i, j].imshow(img)
            axes[i, j].axis('off')
            if j == 0:
                axes[i, j].set_title(f"Step {step}", fontsize=12)

plt.tight_layout()
plt.savefig("validation_comparison.png", dpi=150)
print("Comparação salva em: validation_comparison.png")
EOF
```

---

## Passo 5: Testar Modelo Final

```bash
cd training/scripts

# Script de teste
cat > test_model.py << 'EOF'
from diffusers import StableDiffusionPipeline
import torch

# Carregar modelo
pipeline = StableDiffusionPipeline.from_pretrained(
    "../outputs/lora_casual_shoes_full/final_pipeline"
)
pipeline = pipeline.to("mps")

# Prompts de teste
prompts = [
    "A professional product photo of black leather casual shoes on white background",
    "A professional product photo of white canvas sneakers on white background",
    "A professional product photo of brown suede loafers on white background",
    "A professional product photo of navy blue casual shoes on white background",
]

# Gerar imagens
for i, prompt in enumerate(prompts):
    print(f"Gerando: {prompt}")

    image = pipeline(
        prompt,
        num_inference_steps=50,
        guidance_scale=7.5,
    ).images[0]

    image.save(f"test_output_{i}.png")
    print(f"  Salvo: test_output_{i}.png")

print("\nGeração completa!")
EOF

python test_model.py
```

---

## Passo 6: Comparar com Modelo Base

```bash
cat > compare_models.py << 'EOF'
from diffusers import StableDiffusionPipeline
import torch
from PIL import Image
import numpy as np

# Prompt de teste
prompt = "A professional product photo of brown leather casual shoes on white background, high quality, product photography"

# Modelo base
print("Gerando com modelo base...")
base_pipeline = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5"
)
base_pipeline = base_pipeline.to("mps")
base_image = base_pipeline(prompt, num_inference_steps=50).images[0]
base_image.save("comparison_base.png")

# Modelo fine-tuned
print("Gerando com modelo fine-tuned...")
ft_pipeline = StableDiffusionPipeline.from_pretrained(
    "../outputs/lora_casual_shoes_full/final_pipeline"
)
ft_pipeline = ft_pipeline.to("mps")
ft_image = ft_pipeline(prompt, num_inference_steps=50).images[0]
ft_image.save("comparison_finetuned.png")

# Criar comparação lado a lado
comparison = Image.new('RGB', (1024, 512))
comparison.paste(base_image, (0, 0))
comparison.paste(ft_image, (512, 0))
comparison.save("comparison_sidebyside.png")

print("\nComparação salva:")
print("  - comparison_base.png")
print("  - comparison_finetuned.png")
print("  - comparison_sidebyside.png")
EOF

python compare_models.py
```

---

## Passo 7: Calcular Métricas

```bash
cat > calculate_metrics.py << 'EOF'
from diffusers import StableDiffusionPipeline
import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

# Carregar modelo CLIP
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Carregar pipeline
pipeline = StableDiffusionPipeline.from_pretrained(
    "../outputs/lora_casual_shoes_full/final_pipeline"
)
pipeline = pipeline.to("mps")

# Prompts de teste
test_prompts = [
    "A professional product photo of black casual shoes on white background",
    "A professional product photo of brown leather shoes on white background",
    "A professional product photo of white sneakers on white background",
]

clip_scores = []

for prompt in test_prompts:
    # Gerar imagem
    image = pipeline(prompt, num_inference_steps=50).images[0]

    # Calcular CLIP score
    inputs = clip_processor(
        text=[prompt],
        images=image,
        return_tensors="pt",
        padding=True
    )

    outputs = clip_model(**inputs)
    clip_score = outputs.logits_per_image.item()
    clip_scores.append(clip_score)

    print(f"Prompt: {prompt[:50]}...")
    print(f"CLIP Score: {clip_score:.2f}\n")

print(f"Average CLIP Score: {sum(clip_scores)/len(clip_scores):.2f}")
print(f"(Score > 25 é bom, > 30 é excelente)")
EOF

python calculate_metrics.py
```

---

## Passo 8: Análise de Loss

```bash
cat > analyze_training.py << 'EOF'
import re
import matplotlib.pyplot as plt
import numpy as np

# Ler log
with open('training_log_full.txt', 'r') as f:
    lines = f.readlines()

# Extrair losses
losses = []
steps = []

for line in lines:
    if 'loss=' in line:
        match = re.search(r'(\d+)/3000.*loss=([0-9.]+)', line)
        if match:
            step = int(match.group(1))
            loss = float(match.group(2))
            steps.append(step)
            losses.append(loss)

# Plotar
plt.figure(figsize=(12, 6))

# Loss raw
plt.subplot(1, 2, 1)
plt.plot(steps, losses, alpha=0.3, linewidth=0.5)
plt.xlabel('Training Steps')
plt.ylabel('MSE Loss')
plt.title('Training Loss (Raw)')
plt.grid(True, alpha=0.3)

# Loss smoothed
plt.subplot(1, 2, 2)
window = 50
smoothed = np.convolve(losses, np.ones(window)/window, mode='valid')
plt.plot(steps[window-1:], smoothed, linewidth=2, color='red')
plt.xlabel('Training Steps')
plt.ylabel('MSE Loss')
plt.title(f'Training Loss (Moving Average, window={window})')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('training_loss_analysis.png', dpi=150)
print("Gráfico salvo em: training_loss_analysis.png")

# Estatísticas
print(f"\nEstatísticas:")
print(f"  Loss inicial: {losses[0]:.4f}")
print(f"  Loss final: {losses[-1]:.4f}")
print(f"  Redução: {(1 - losses[-1]/losses[0])*100:.1f}%")
print(f"  Loss média: {np.mean(losses):.4f}")
print(f"  Loss mediana: {np.median(losses):.4f}")
EOF

python analyze_training.py
```

---

## Passo 9: Preparar para Produção

### Exportar apenas LoRA weights

```bash
cd ../outputs/lora_casual_shoes_full

# LoRA weights são compactos (~6MB)
du -sh lora_weights/
ls -lh lora_weights/

# Testar carregamento
python << EOF
from peft import PeftModel
from diffusers import UNet2DConditionModel

# Carregar UNet base
unet = UNet2DConditionModel.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    subfolder="unet"
)

# Aplicar LoRA
unet = PeftModel.from_pretrained(unet, "lora_weights")
print("LoRA weights carregados com sucesso!")
print(f"Parâmetros treináveis: {sum(p.numel() for p in unet.parameters() if p.requires_grad):,}")
EOF
```

### Criar package de distribuição

```bash
# Criar diretório de distribuição
mkdir -p distribution/casual_shoes_lora_v1

# Copiar artefatos essenciais
cp -r lora_weights distribution/casual_shoes_lora_v1/
cp -r final_pipeline/model_index.json distribution/casual_shoes_lora_v1/

# Criar README
cat > distribution/casual_shoes_lora_v1/README.md << 'EOF'
# Casual Shoes LoRA Model v1.0

Fine-tuned Stable Diffusion 1.5 model for generating professional product photos of casual shoes.

## Usage

```python
from diffusers import StableDiffusionPipeline
from peft import PeftModel

# Load base model
pipeline = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5"
)

# Load LoRA weights
pipeline.unet = PeftModel.from_pretrained(
    pipeline.unet,
    "lora_weights"
)

# Generate image
image = pipeline(
    "A professional product photo of brown leather casual shoes on white background",
    num_inference_steps=50
).images[0]

image.save("output.png")
```

## Model Details

- Base: Stable Diffusion v1.5
- Training steps: 3,000
- Dataset: 1,991 casual shoes images
- LoRA rank: 8
- LoRA alpha: 16
- Training time: ~11 hours on Apple M2 Max
EOF

# Compactar para distribuição
cd distribution
tar -czf casual_shoes_lora_v1.tar.gz casual_shoes_lora_v1/
echo "Package criado: casual_shoes_lora_v1.tar.gz"
ls -lh casual_shoes_lora_v1.tar.gz
```

---

## Troubleshooting

### Erro: Out of Memory

```bash
# Reduzir batch size
python train_lora.py --train_batch_size 1

# Ou aumentar gradient accumulation
python train_lora.py --gradient_accumulation_steps 16
```

### Erro: MPS não disponível

```bash
# Verificar versão do PyTorch
python -c "import torch; print(torch.__version__)"

# Reinstalar PyTorch com suporte MPS
pip install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cpu
```

### Loss não diminui

```bash
# Verificar learning rate
grep "lr=" training_log_full.txt | tail -10

# Se muito baixo, reiniciar com LR maior
python train_lora.py --learning_rate 2e-4
```

### Imagens de baixa qualidade

```bash
# Aumentar número de steps
python train_lora.py --max_train_steps 5000

# Ou aumentar LoRA rank
python train_lora.py --lora_rank 16 --lora_alpha 32
```

---

## Checklist de Validação

```
[ ] Treinamento completou 3000 steps
[ ] Loss final < 0.02
[ ] Checkpoints salvos corretamente (5 checkpoints)
[ ] Imagens de validação geradas (96 imagens)
[ ] Modelo final salvo em final_pipeline/
[ ] LoRA weights salvos (~6MB)
[ ] Teste de geração bem-sucedido
[ ] CLIP Score > 25
[ ] Comparação com base mostra melhoria
[ ] Package de distribuição criado
```

---

## Próximos Passos

1. Testar em casos de uso reais
2. Coletar feedback de usuários
3. Iterar no dataset (adicionar mais imagens)
4. Explorar outras categorias (roupas, acessórios)
5. Desenvolver API de produção
6. Construir interface web/mobile

---

**Documentação completa:** Ver `PIPELINE_TREINAMENTO.md`
