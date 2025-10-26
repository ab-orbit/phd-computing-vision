# Setup do Ambiente de Treinamento - Concluído

**Data**: 2025-10-26
**Hardware**: Mac Studio M2 Max (32GB RAM)
**Status**: ✅ PRONTO PARA TREINAMENTO

---

## Verificação Completa do Ambiente

### 1. Sistema Operacional
- **OS**: macOS 26.0.1 (arm64)
- **Arquitetura**: Apple Silicon (arm64)
- **Python**: 3.12.9
- **Memória Total**: 32.0 GB
- **Memória Disponível**: ~10-12 GB (suficiente)

### 2. PyTorch e Backend

✅ **PyTorch**: 2.7.1
- CUDA: Não disponível (esperado no macOS)
- **MPS (Metal Performance Shaders)**: ✅ Disponível e funcionando
- MPS Built: ✅ Sim
- Device de teste: `mps` - OK

**Teste realizado**: Criação de tensor em MPS bem-sucedida

### 3. Bibliotecas de Difusão

✅ **Diffusers**: 0.35.2
- StableDiffusionPipeline: ✅ Disponível
- Todos os componentes importados com sucesso

✅ **Transformers**: 4.56.1
- CLIP models: ✅ Disponível
- Tokenizers: ✅ Funcionando

### 4. Treinamento e Fine-tuning

✅ **Accelerate**: 1.11.0
- Suporte para treinamento distribuído
- Otimizações de memória

✅ **PEFT (Parameter-Efficient Fine-Tuning)**: 0.17.1
- LoraConfig: ✅ Disponível
- get_peft_model: ✅ Funcionando
- Pronto para LoRA training

### 5. Processamento de Dados

✅ **Datasets**: 4.0.0 (Hugging Face)
✅ **Pillow (PIL)**: 11.2.1
✅ **NumPy**: 2.2.5

### 6. Componentes do Stable Diffusion

Todos testados e funcionando:
- ✅ UNet2DConditionModel
- ✅ AutoencoderKL
- ✅ CLIPTextModel
- ✅ CLIPTokenizer

### 7. Dataset Preparado

✅ **Casual Shoes Dataset**:
- Localização: `/Users/jwcunha/Documents/.../data/casual_shoes/`
- Train: 1,991 imagens (512x512 PNG)
- Val: 427 imagens
- Test: 427 imagens
- **Total**: 2,845 imagens prontas

### 8. Pacotes Opcionais

Status dos pacotes não-críticos:

| Pacote | Status | Necessário? |
|--------|--------|-------------|
| xformers | Não instalado | Opcional - otimizações de atenção |
| wandb | Não instalado | Opcional - tracking de experimentos |
| tensorboard | Não instalado | Opcional - visualização |
| bitsandbytes | Não instalado | Opcional - quantização |

**Nota**: Estes pacotes podem ser instalados posteriormente se necessário, mas não são críticos para iniciar o treinamento.

---

## Configurações de Treinamento Recomendadas

### Para M2 Max (32GB RAM)

**Stable Diffusion 1.5 + LoRA**:
```python
# Configurações otimizadas
training_config = {
    'model': 'runwayml/stable-diffusion-v1-5',
    'resolution': 512,
    'train_batch_size': 2,
    'gradient_accumulation_steps': 8,  # Batch efetivo = 16
    'learning_rate': 1e-4,
    'mixed_precision': 'fp16',
    'gradient_checkpointing': True,
    'use_8bit_adam': False,  # Não usar com MPS

    # LoRA Config
    'lora_rank': 8,  # Ou 16 para melhor qualidade
    'lora_alpha': 16,  # Ou 32
    'lora_dropout': 0.0,
}
```

**Memória Esperada**:
- Durante treinamento: ~8-12 GB
- Durante inferência: ~4-6 GB

**Performance Esperada**:
- Tempo por step: ~2-3 segundos (batch=2, grad_accum=8)
- Tempo total (3000 steps): ~2-3 horas
- Geração de imagem: ~4-6 segundos

---

## Versões Instaladas

```
torch==2.7.1
torchvision==0.22.0+cpu
diffusers==0.35.2
transformers==4.56.1
accelerate==1.11.0
peft==0.17.1
datasets==4.0.0
Pillow==11.2.1
numpy==2.2.5
safetensors==0.5.3
omegaconf==2.3.0
einops==0.8.1
tqdm==4.67.1
psutil==7.1.2
```

---

## Como Usar

### 1. Verificar Ambiente

```bash
cd training/scripts
python3 check_environment.py
```

### 2. Instalar Dependências Adicionais (se necessário)

```bash
pip install -r training/requirements-training.txt
```

### 3. Próximos Passos

1. ✅ Task 1.3: Setup do ambiente - **CONCLUÍDO**
2. ⏭️ Task 1.4: Download e teste de SD 1.5
3. ⏭️ Task 1.5: Criar script de treinamento LoRA

---

## Troubleshooting

### Problema: MPS não disponível
**Solução**: Verificar versão do PyTorch (requer 2.0+)
```bash
pip install --upgrade torch torchvision
```

### Problema: Erro de memória durante treinamento
**Soluções**:
1. Reduzir `train_batch_size` para 1
2. Aumentar `gradient_accumulation_steps`
3. Reduzir `lora_rank` para 4
4. Usar `resolution=256` para teste

### Problema: Treinamento muito lento
**Soluções**:
1. Verificar se está usando MPS (não CPU)
2. Instalar xformers (opcional): `pip install xformers`
3. Usar `gradient_checkpointing=False` se houver memória suficiente

---

## Referências

- **PyTorch MPS**: https://pytorch.org/docs/stable/notes/mps.html
- **Diffusers**: https://huggingface.co/docs/diffusers
- **PEFT/LoRA**: https://huggingface.co/docs/peft
- **Stable Diffusion**: https://github.com/CompVis/stable-diffusion

---

**Última Atualização**: 2025-10-26
**Preparado por**: Task 1.3 - Setup do Ambiente PyTorch MPS
**Status**: ✅ AMBIENTE PRONTO PARA TREINAMENTO
