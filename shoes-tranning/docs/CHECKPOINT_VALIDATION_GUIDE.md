# Guia de Validação com Checkpoints Intermediários

Como testar modelos durante o treinamento sem esperar a conclusão completa.

---

## Por que Validar Checkpoints?

Durante um treinamento longo (10-11 horas para 3000 steps), é crucial validar o progresso intermediário:

1. **Detecção Precoce de Problemas**: Identificar overfitting ou underfitting cedo
2. **Ajuste de Hiperparâmetros**: Decidir se continuar ou reiniciar com configurações diferentes
3. **Early Stopping Manual**: Escolher o melhor checkpoint se o modelo começar a degradar
4. **Exploração**: Comparar qualidade em diferentes estágios do treinamento

---

## Visão Geral do Processo

```
Treinamento Rodando
      ↓
Checkpoint Salvo (ex: step 500)
      ↓
Converter Checkpoint → Pipeline
      ↓
API Detecta Automaticamente
      ↓
Frontend Lista Checkpoint
      ↓
Testar Geração de Imagens
      ↓
Comparar com Outros Checkpoints
```

---

## Passo 1: Verificar Checkpoints Disponíveis

Durante o treinamento, checkpoints são salvos a cada 500 steps:

```bash
# Ver checkpoints salvos
ls -lh training/outputs/lora_casual_shoes_3000steps_full/checkpoints/

# Saída esperada:
# checkpoint-500/
# checkpoint-1000/
# checkpoint-1500/
# checkpoint-2000/
# checkpoint-2500/
```

Cada checkpoint contém:
- `model.safetensors`: Pesos do UNet + LoRA
- `optimizer.bin`: Estado do otimizador
- `scheduler.bin`: Estado do LR scheduler
- `random_states_0.pkl`: Estados aleatórios

---

## Passo 2: Converter Checkpoint para Pipeline

### Opção A: Converter Um Checkpoint Específico

```bash
cd training/scripts

# Converter checkpoint do step 500
python convert_checkpoint_to_pipeline.py \
    --checkpoint_path ../outputs/lora_casual_shoes_3000steps_full/checkpoints/checkpoint-500 \
    --output_dir ../outputs/lora_casual_shoes_3000steps_full/checkpoint_pipelines/checkpoint-500

# Com teste de geração
python convert_checkpoint_to_pipeline.py \
    --checkpoint_path ../outputs/lora_casual_shoes_3000steps_full/checkpoints/checkpoint-500 \
    --output_dir ../outputs/lora_casual_shoes_3000steps_full/checkpoint_pipelines/checkpoint-500 \
    --test_prompt "A professional product photo of black casual shoes on white background"
```

**Tempo estimado**: ~30 segundos por checkpoint

### Opção B: Converter Todos os Checkpoints de Uma Vez

```bash
cd training/scripts

# Converter automaticamente todos os checkpoints
./convert_all_checkpoints.sh ../outputs/lora_casual_shoes_3000steps_full

# O script:
# 1. Detecta todos os checkpoints
# 2. Converte cada um
# 3. Pula os já convertidos
# 4. Mostra resumo
```

**Tempo estimado**: ~30s × número de checkpoints

---

## Passo 3: Verificar Conversão

```bash
# Listar pipelines convertidos
ls -lh training/outputs/lora_casual_shoes_3000steps_full/checkpoint_pipelines/

# Verificar estrutura de um pipeline
ls training/outputs/lora_casual_shoes_3000steps_full/checkpoint_pipelines/checkpoint-500/

# Deve conter:
# - model_index.json
# - unet/
# - vae/
# - text_encoder/
# - scheduler/
# - tokenizer/
# - checkpoint_metadata.json
```

---

## Passo 4: Usar na API

### Iniciar/Reiniciar API

Se a API já está rodando, reinicie para detectar novos checkpoints:

```bash
# Parar API (Ctrl+C no terminal)

# Reiniciar
cd api
python main.py
```

### Verificar Modelos Disponíveis

```bash
# Listar modelos via API
curl http://localhost:8000/api/models | python -m json.tool

# Resposta esperada inclui checkpoints:
# [
#   {
#     "name": "base",
#     "display_name": "Stable Diffusion 1.5 (Base)",
#     ...
#   },
#   {
#     "name": "lora_casual_shoes_3000steps_full/checkpoint-500",
#     "display_name": "Lora Casual Shoes 3000Steps Full (Step 500)",
#     "description": "Checkpoint intermediário no step 500",
#     ...
#   },
#   {
#     "name": "lora_casual_shoes_3000steps_full/checkpoint-1000",
#     "display_name": "Lora Casual Shoes 3000Steps Full (Step 1000)",
#     ...
#   }
# ]
```

---

## Passo 5: Testar no Frontend

1. **Abra o Frontend**: http://localhost:3000

2. **Selecione Checkpoint**: No dropdown "Modelo", agora aparecerão:
   - Stable Diffusion 1.5 (Base)
   - Lora Casual Shoes 3000Steps Full (Step 500)
   - Lora Casual Shoes 3000Steps Full (Step 1000)
   - Lora Casual Shoes 3000Steps Full (Step 1500)
   - Etc.

3. **Gere Imagens**: Use o mesmo prompt para todos os checkpoints

4. **Compare Resultados**: Observe a evolução da qualidade

---

## Passo 6: Análise Comparativa

### Script de Comparação Automática

Crie um script para gerar com múltiplos checkpoints:

```bash
cat > test_all_checkpoints.sh << 'EOF'
#!/bin/bash

PROMPT="A professional product photo of brown leather casual shoes on white background"

for step in 500 1000 1500 2000 2500; do
    echo "Testando checkpoint step $step..."

    curl -X POST "http://localhost:8000/api/generate" \
         -H "Content-Type: application/json" \
         -d "{
               \"model_name\": \"lora_casual_shoes_3000steps_full/checkpoint-$step\",
               \"prompt\": \"$PROMPT\",
               \"num_images\": 4,
               \"seed\": 42
             }" > "checkpoint_${step}_results.json"

    echo "Resultados salvos em checkpoint_${step}_results.json"
    echo ""
done

echo "Comparação concluída!"
EOF

chmod +x test_all_checkpoints.sh
./test_all_checkpoints.sh
```

### Extrair e Visualizar Imagens

```python
import json
import base64
from PIL import Image
import io

for step in [500, 1000, 1500, 2000, 2500]:
    with open(f'checkpoint_{step}_results.json', 'r') as f:
        data = json.load(f)

    for i, img_data in enumerate(data['images']):
        # Decodificar base64
        image_bytes = base64.b64decode(img_data['image_data'])
        image = Image.open(io.BytesIO(image_bytes))

        # Salvar
        image.save(f'comparison_step{step}_img{i}.png')

print("Imagens extraídas! Compare visualmente.")
```

---

## Critérios de Avaliação

### Qualidade Visual (Subjetiva)

Para cada checkpoint, avaliar:

1. **Aderência ao Prompt**:
   - [ ] Cor correta (ex: marrom)
   - [ ] Material correto (ex: couro)
   - [ ] Estilo correto (ex: casual)
   - [ ] Background branco limpo

2. **Realismo**:
   - [ ] Texturas realistas
   - [ ] Proporções corretas
   - [ ] Detalhes finos (costuras, cadarços)
   - [ ] Iluminação natural

3. **Problemas**:
   - [ ] Artefatos visuais
   - [ ] Deformações
   - [ ] Elementos extras indesejados
   - [ ] Borramento excessivo

### Métricas Quantitativas

```python
# Calcular CLIP Score para cada checkpoint
from transformers import CLIPProcessor, CLIPModel

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

scores = {}
for step in [500, 1000, 1500, 2000, 2500]:
    # Carregar imagem
    image = Image.open(f'comparison_step{step}_img0.png')

    # Calcular score
    inputs = processor(
        text=["A professional product photo of brown leather casual shoes"],
        images=image,
        return_tensors="pt",
        padding=True
    )

    outputs = model(**inputs)
    score = outputs.logits_per_image.item()

    scores[step] = score
    print(f"Step {step}: CLIP Score = {score:.2f}")

# Plotar evolução
import matplotlib.pyplot as plt

steps = list(scores.keys())
clip_scores = list(scores.values())

plt.figure(figsize=(10, 6))
plt.plot(steps, clip_scores, marker='o', linewidth=2, markersize=8)
plt.xlabel('Training Steps')
plt.ylabel('CLIP Score')
plt.title('Model Quality Evolution')
plt.grid(True, alpha=0.3)
plt.savefig('checkpoint_evolution.png', dpi=150)
print("Gráfico salvo: checkpoint_evolution.png")
```

---

## Decisões com Base nos Checkpoints

### Cenário 1: Qualidade Estável

Se checkpoints 1500, 2000, 2500 têm qualidade similar:

**Ação**: Considerar usar checkpoint 1500 (economia de tempo)

### Cenário 2: Melhoria Contínua

Se qualidade melhora a cada checkpoint:

**Ação**: Aguardar treinamento completo (3000 steps)

### Cenário 3: Degradação

Se checkpoint 2000 é melhor que 2500:

**Ação**: Usar checkpoint 2000 (early stopping manual)

### Cenário 4: Problemas Persistentes

Se todos os checkpoints têm problemas graves:

**Ações**:
1. Parar treinamento
2. Revisar hiperparâmetros
3. Verificar dataset
4. Reiniciar treinamento

---

## Workflow Recomendado

### Durante o Treinamento (a cada 500 steps)

```bash
# 1. Aguardar checkpoint ser salvo (~1 minuto após step 500)
# 2. Converter checkpoint
cd training/scripts
python convert_checkpoint_to_pipeline.py \
    --checkpoint_path ../outputs/.../checkpoints/checkpoint-500 \
    --output_dir ../outputs/.../checkpoint_pipelines/checkpoint-500 \
    --test_prompt "A professional product photo of black casual shoes"

# 3. Reiniciar API (se rodando)
# 4. Testar no frontend
# 5. Decidir: continuar ou ajustar?
```

### Ao Final do Treinamento

```bash
# 1. Converter todos os checkpoints que faltam
./convert_all_checkpoints.sh ../outputs/lora_casual_shoes_3000steps_full

# 2. Fazer comparação completa
./test_all_checkpoints.sh

# 3. Escolher melhor checkpoint
# 4. Usar na produção
```

---

## Troubleshooting

### Checkpoint não converte

**Problema**: `FileNotFoundError: model.safetensors not found`

**Solução**:
- Aguarde o checkpoint ser completamente salvo
- Verifique se o treinamento não foi interrompido durante salvamento

### API não detecta checkpoint

**Problema**: Checkpoint não aparece em `/api/models`

**Soluções**:
1. Verificar estrutura do pipeline:
   ```bash
   ls checkpoint_pipelines/checkpoint-500/model_index.json
   ```
2. Reiniciar API
3. Verificar logs da API

### Geração muito lenta

**Problema**: Checkpoint demora mais que modelo final

**Explicação**: Normal, checkpoint pode ter menos otimizações

**Soluções**:
- Usar menos `num_inference_steps` (25-30 em vez de 50)
- Gerar menos imagens por vez
- Adicionar `pipeline.enable_attention_slicing()` (já incluso na API)

---

## Checklist de Validação

```
[ ] Checkpoints salvos durante treinamento
[ ] Pelo menos 1 checkpoint convertido (step 500)
[ ] Pipeline convertido validado (model_index.json existe)
[ ] API reiniciada e detecta checkpoint
[ ] Frontend mostra checkpoint no dropdown
[ ] Consegue gerar imagem com checkpoint
[ ] Imagem gerada tem qualidade aceitável
[ ] Comparação com outros checkpoints feita
[ ] Decisão tomada: continuar/parar/usar checkpoint específico
```

---

## Resumo

1. **Durante Treinamento**: Converter checkpoints a cada 500 steps
2. **Testar**: Gerar imagens e comparar qualidade
3. **Decidir**: Continuar, parar, ou usar checkpoint específico
4. **Produção**: Usar melhor checkpoint (nem sempre é o final!)

---

**Tempo total por checkpoint**: ~2-3 minutos
- Conversão: 30 segundos
- Gerar 4 imagens de teste: 45-60 segundos
- Análise visual: 1 minuto

**Vantagem**: Feedback rápido sem esperar treinamento completo!

---

**Criado**: 27/01/2025
**Atualizado**: 27/01/2025
