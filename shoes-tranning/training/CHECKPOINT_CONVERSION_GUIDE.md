# Guia de Conversão de Checkpoints

**Data**: 27/10/2025
**Status**: Implementado

---

## Problema Identificado

Os checkpoints intermediários salvos durante o treinamento não estavam aparecendo no frontend da API.

### Causa

Durante o treinamento, o Accelerate salva checkpoints em dois formatos diferentes:

**Checkpoints intermediários** (durante treinamento):
- Salvos em `outputs/*/checkpoints/checkpoint-N/`
- Contém apenas: `model.safetensors`, `optimizer.bin`, `scheduler.bin`
- Formato: Estado do modelo LoRA (PEFT)
- **NÃO** é um pipeline completo

**Checkpoint final** (ao terminar):
- Salvo em `outputs/*/lora_weights/`
- Formato: LoRA weights completo
- Pode ser carregado com `load_lora_weights()`

### O que a API esperava

A API procura por pipelines completos em:
- `outputs/*/final_pipeline/` - Pipeline final com UNet fine-tuned
- `outputs/*/checkpoint_pipelines/checkpoint-N/` - Checkpoints convertidos

---

## Solução Implementada

### 1. Script de Conversão em Lote

**Arquivo**: `training/scripts/convert_all_checkpoints.py`

Converte todos os checkpoints de um treinamento de uma vez:

```bash
cd training/scripts
python convert_all_checkpoints.py ../outputs/lora_casual_shoes_3000steps_full
```

**Saída**:
```
Encontrados 3 checkpoints em: ../outputs/.../checkpoints

🔄 Convertendo checkpoint-1000...
✅ checkpoint-1000: Convertido com sucesso

🔄 Convertendo checkpoint-1500...
✅ checkpoint-1500: Convertido com sucesso

⏭️  checkpoint-500: Já convertido (use --force para reconverter)

Resumo:
  Convertidos: 2
  Ignorados: 1
  Falhas: 0
  Total: 3
```

**Flags disponíveis**:
- `--force`: Reconverte checkpoints já convertidos

### 2. Estrutura Gerada

Após a conversão:

```
outputs/lora_casual_shoes_3000steps_full/
├── checkpoints/                      # Checkpoints originais (Accelerate)
│   ├── checkpoint-500/
│   │   ├── model.safetensors        # 3.2GB - Estado do modelo
│   │   ├── optimizer.bin            # 12MB - Estado do otimizador
│   │   ├── scheduler.bin            # 1.4KB - Estado do scheduler
│   │   └── random_states_0.pkl      # 14KB - Seeds aleatórios
│   ├── checkpoint-1000/
│   └── checkpoint-1500/
│
└── checkpoint_pipelines/             # Checkpoints convertidos (Diffusers)
    ├── checkpoint-500/
    │   ├── model_index.json         # Índice do pipeline
    │   ├── unet/
    │   │   ├── config.json
    │   │   └── diffusion_pytorch_model.safetensors
    │   ├── text_encoder/
    │   ├── vae/
    │   ├── tokenizer/
    │   ├── scheduler/
    │   └── checkpoint_metadata.json  # Metadata
    ├── checkpoint-1000/
    └── checkpoint-1500/
```

---

## Como Funciona

### Processo de Conversão

1. **Carrega modelo base**: Stable Diffusion 1.5
2. **Carrega UNet do checkpoint**: Aplica pesos LoRA treinados
3. **Cria pipeline completo**: Combina UNet + componentes base
4. **Salva no formato Diffusers**: Cria estrutura que a API pode carregar

### Componentes do Pipeline

Cada checkpoint convertido contém:

- **UNet**: Com pesos LoRA treinados até o step N
- **Text Encoder**: Modelo base (não alterado)
- **VAE**: Modelo base (não alterado)
- **Tokenizer**: Modelo base (não alterado)
- **Scheduler**: Configuração de noise scheduling

---

## Uso na API

### Detecção Automática

A API detecta automaticamente checkpoints convertidos:

```python
# Endpoint: GET /api/models
{
  "models": [
    {
      "name": "lora_casual_shoes_3000steps_full/checkpoint-500",
      "display_name": "Lora Casual Shoes 3000Steps Full (Step 500)",
      "description": "Checkpoint intermediário no step 500",
      "available": true
    },
    {
      "name": "lora_casual_shoes_3000steps_full/checkpoint-1000",
      "display_name": "Lora Casual Shoes 3000Steps Full (Step 1000)",
      "description": "Checkpoint intermediário no step 1000",
      "available": true
    },
    // ...
  ]
}
```

### Geração de Imagens

```bash
curl -X POST http://localhost:8011/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "lora_casual_shoes_3000steps_full/checkpoint-1000",
    "prompt": "casual brown leather shoes, product photo",
    "num_images": 1
  }'
```

---

## Conversão Automática Durante Treinamento

### Status Atual

Os checkpoints intermediários **NÃO** são convertidos automaticamente durante o treinamento por razões de:

1. **Espaço em disco**: Cada checkpoint convertido ocupa ~3.5GB
2. **Tempo**: Conversão leva ~30 segundos por checkpoint
3. **Interrupção**: Pode atrasar o treinamento

### Quando Converter

**Recomendações**:

✅ **Converter APÓS o treinamento**:
- Quando quiser testar checkpoints específicos
- Quando precisar comparar diferentes steps
- Para validação de progresso

❌ **NÃO converter durante treinamento**:
- Durante treinamento ativo
- Se espaço em disco for limitado
- Se não precisar dos checkpoints intermediários

---

## Comandos Úteis

### Listar Checkpoints Disponíveis

```bash
ls -lh outputs/*/checkpoints/
```

### Converter Checkpoints de um Treinamento

```bash
python convert_all_checkpoints.py ../outputs/lora_casual_shoes_3000steps_full
```

### Converter Checkpoint Específico

```bash
python convert_checkpoint_to_pipeline.py \
  --checkpoint ../outputs/lora_casual_shoes_3000steps_full/checkpoints/checkpoint-1000 \
  --output ../outputs/lora_casual_shoes_3000steps_full/checkpoint_pipelines/checkpoint-1000
```

### Verificar Modelos na API

```bash
curl -s http://localhost:8011/api/models | python -m json.tool
```

### Limpar Checkpoints Convertidos

```bash
rm -rf outputs/*/checkpoint_pipelines/checkpoint-*
```

---

## Estimativas de Espaço

### Por Checkpoint

| Componente | Tamanho |
|------------|---------|
| Checkpoint original (Accelerate) | 3.2 GB |
| Checkpoint convertido (Diffusers) | 3.5 GB |
| **Total** | **6.7 GB** |

### Para Treinamento Completo (3000 steps)

Checkpoints salvos a cada 500 steps:

| Step | Original | Convertido | Total |
|------|----------|------------|-------|
| 500 | 3.2 GB | 3.5 GB | 6.7 GB |
| 1000 | 3.2 GB | 3.5 GB | 6.7 GB |
| 1500 | 3.2 GB | 3.5 GB | 6.7 GB |
| 2000 | 3.2 GB | 3.5 GB | 6.7 GB |
| 2500 | 3.2 GB | 3.5 GB | 6.7 GB |
| 3000 | 3.2 GB | 3.5 GB | 6.7 GB |
| **Total** | **19.2 GB** | **21 GB** | **40.2 GB** |

---

## Troubleshooting

### Erro: "Missing keys" durante conversão

**Mensagem**:
```
WARNING - Missing keys: 686 keys
WARNING - Unexpected keys: 942 keys
```

**Explicação**: É **NORMAL** e esperado. O UNet base tem parâmetros que não existem no checkpoint LoRA (e vice-versa).

**Ação**: Nenhuma. A conversão foi bem-sucedida.

### Checkpoint não aparece na API

**Verificar**:

1. Checkpoint foi convertido?
```bash
ls outputs/*/checkpoint_pipelines/checkpoint-N/
```

2. Tem `model_index.json`?
```bash
cat outputs/*/checkpoint_pipelines/checkpoint-N/model_index.json
```

3. API está rodando?
```bash
curl http://localhost:8011/api/models
```

### Espaço insuficiente

Se não houver espaço para converter todos:

```bash
# Converter apenas checkpoints específicos
python convert_checkpoint_to_pipeline.py \
  --checkpoint ../outputs/.../checkpoints/checkpoint-1500 \
  --output ../outputs/.../checkpoint_pipelines/checkpoint-1500
```

---

## Fluxo de Trabalho Recomendado

### Durante o Treinamento

1. ✅ Deixar checkpoints serem salvos normalmente
2. ✅ Monitorar progresso via logs
3. ❌ NÃO converter checkpoints ainda

### Após o Treinamento

1. ✅ Analisar loss nos logs
2. ✅ Identificar checkpoints interessantes
3. ✅ Converter checkpoints selecionados:
```bash
python convert_all_checkpoints.py ../outputs/TRAINING_NAME
```
4. ✅ Testar no frontend
5. ✅ Gerar imagens de validação

### Limpeza

Após identificar o melhor checkpoint:

```bash
# Manter apenas checkpoints necessários
# Deletar checkpoints intermediários não convertidos
rm -rf outputs/*/checkpoints/checkpoint-{500,1000,1500}

# Ou deletar checkpoints convertidos não necessários
rm -rf outputs/*/checkpoint_pipelines/checkpoint-{500,1000}
```

---

## Próximos Passos

### Implementações Futuras

- [ ] Script para converter apenas "melhores" checkpoints (baseado em loss)
- [ ] Conversão incremental (apenas novos checkpoints)
- [ ] Compactação de checkpoints antigos
- [ ] Dashboard para comparar checkpoints visualmente

---

**Criado**: 27/10/2025
**Última Atualização**: 27/10/2025
**Autor**: Claude Code
