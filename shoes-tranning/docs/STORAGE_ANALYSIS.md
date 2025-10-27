# Análise de Uso de Armazenamento

Documento criado: 27/10/2025

## Resumo Executivo

O treinamento de modelos LoRA gera arquivos grandes que crescem durante o processo. Este documento analisa o uso de armazenamento e fornece recomendações.

## Uso Atual de Espaço

### Diretórios Principais

```
training/outputs/
├── lora_casual_shoes_3000steps_full/    8.7 GB  ← Treinamento ativo
│   ├── checkpoints/                     4.7 GB  ← Vai crescer até ~14 GB
│   ├── checkpoint_pipelines/            4.0 GB  ← Vai crescer até ~12 GB
│   └── validation/                       13 MB
├── test_run_quick/                      7.2 GB  ← Pode ser removido
├── test_run/                            7.2 GB  ← Pode ser removido
├── lora_casual_shoes_3000steps/       796 MB
└── lora_casual_shoes/                 796 MB
```

**Total atual: ~24 GB**

**Estimativa ao final do treinamento: ~35 GB**

### Arquivos Grandes por Tipo

#### Checkpoints (model.safetensors)
Cada checkpoint completo ocupa aproximadamente 3.2 GB:

```
checkpoint-500/model.safetensors:   3.2 GB
checkpoint-1000/model.safetensors:  1.5 GB (em progresso)
checkpoint-1500/model.safetensors:  ~3.2 GB (futuro)
checkpoint-2000/model.safetensors:  ~3.2 GB (futuro)
checkpoint-2500/model.safetensors:  ~3.2 GB (futuro)
checkpoint-3000/model.safetensors:  ~3.2 GB (futuro)
```

**Total esperado de checkpoints: ~19 GB**

#### Checkpoint Pipelines Convertidos
Cada pipeline convertido ocupa aproximadamente 4 GB:

```
checkpoint-500/
├── unet/diffusion_pytorch_model.safetensors:     3.2 GB
├── text_encoder/model.safetensors:               469 MB
├── vae/diffusion_pytorch_model.safetensors:      319 MB
└── outros arquivos (scheduler, tokenizer):       ~20 MB
```

Se convertermos todos os 6 checkpoints: **~24 GB**

#### Arquivos de Otimização
```
optimizer.bin:         12 MB por checkpoint
scheduler.bin:        <1 MB por checkpoint
random_states_0.pkl:  <1 MB por checkpoint
```

## Crescimento Durante Treinamento

### Projeção de Espaço

| Step    | Checkpoints | Pipelines | Validation | Total Aprox |
|---------|-------------|-----------|------------|-------------|
| 500     | 3.2 GB      | 4.0 GB    | 2 MB       | 7.2 GB      |
| 1000    | 6.4 GB      | 8.0 GB    | 4 MB       | 14.4 GB     |
| 1500    | 9.6 GB      | 12.0 GB   | 6 MB       | 21.6 GB     |
| 2000    | 12.8 GB     | 16.0 GB   | 8 MB       | 28.8 GB     |
| 2500    | 16.0 GB     | 20.0 GB   | 10 MB      | 36.0 GB     |
| 3000    | 19.2 GB     | 24.0 GB   | 12 MB      | 43.2 GB     |

**Nota**: A projeção assume conversão de todos os checkpoints. Se não converter, reduz pela metade.

### Taxa de Crescimento

- **Checkpoints**: ~3.2 GB a cada 500 steps (aproximadamente 1.7 horas)
- **Pipelines convertidos**: +4 GB por conversão manual
- **Validação**: +2 MB a cada 500 steps (negligível)

## Recomendações

### 1. Mover para HD Externo (Recomendado)

**Vantagens:**
- Libera espaço no disco principal
- Mantém todos os checkpoints para análise posterior
- Scripts e API continuam funcionando via symlink
- Pode ser desconectado após treinamento

**Como fazer:**
```bash
cd training
./move_to_external_drive.sh /Volumes/T9
```

O script:
1. Move todo conteúdo de `outputs/` para o T9
2. Cria symlink `outputs -> /Volumes/T9/shoes-training-outputs`
3. Tudo continua funcionando transparentemente

### 2. Limpar Treinamentos Antigos

Diretórios que podem ser removidos com segurança:

```bash
# Remover treinamentos de teste (14.4 GB)
rm -rf training/outputs/test_run
rm -rf training/outputs/test_run_quick

# Isso libera ~14 GB imediatamente
```

### 3. Converter Apenas Checkpoints Necessários

Não converta todos os checkpoints automaticamente. Converta apenas:
- Checkpoint-500 (validação inicial)
- Checkpoint-1500 (meio do treinamento)
- Checkpoint-3000 (final)

Isso economiza ~16 GB comparado a converter todos.

### 4. Remover Checkpoints Após Avaliação

Após avaliar cada checkpoint e determinar que não é o melhor:
```bash
# Exemplo: se checkpoint-500 não for útil após validar checkpoint-1000
rm -rf training/outputs/lora_casual_shoes_3000steps_full/checkpoints/checkpoint-500
rm -rf training/outputs/lora_casual_shoes_3000steps_full/checkpoint_pipelines/checkpoint-500
# Libera ~7.2 GB
```

## Plano de Ação Recomendado

### Curto Prazo (Agora)

1. Conectar HD externo T9
2. Executar `./move_to_external_drive.sh /Volumes/T9`
3. Verificar que treinamento continua funcionando
4. Remover `test_run` e `test_run_quick` (libera 14 GB)

### Durante o Treinamento

1. Converter apenas checkpoint-500 (já feito)
2. Avaliar checkpoint-500 visualmente
3. Aguardar checkpoint-1500 antes de próxima conversão
4. Se checkpoint-500 não for útil, removê-lo

### Após Treinamento

1. Converter checkpoint-3000 (final)
2. Comparar checkpoint-1500, checkpoint-2500 e checkpoint-3000
3. Manter apenas os 2 melhores checkpoints
4. Remover checkpoints intermediários desnecessários
5. Backup do melhor checkpoint para cloud/outro HD

## Estrutura Final Recomendada

```
/Volumes/T9/shoes-training-outputs/
└── lora_casual_shoes_3000steps_full/
    ├── checkpoints/
    │   ├── checkpoint-1500/        (se for melhor que 3000)
    │   └── checkpoint-3000/        (final)
    ├── checkpoint_pipelines/
    │   ├── checkpoint-1500/
    │   └── checkpoint-3000/
    ├── lora_weights/              (pesos LoRA finais - apenas MB)
    ├── final_pipeline/            (pipeline final completo)
    └── validation/                (imagens de validação)
```

**Espaço estimado final (otimizado): ~15-20 GB**

## Comandos Úteis

### Verificar uso de espaço
```bash
# Tamanho de cada diretório de output
du -sh training/outputs/* | sort -hr

# Tamanho total
du -sh training/outputs

# Arquivos grandes
find training/outputs -size +1G -exec ls -lh {} \;
```

### Verificar espaço no HD externo
```bash
df -h /Volumes/T9
```

### Listar checkpoints
```bash
ls -lh training/outputs/lora_casual_shoes_3000steps_full/checkpoints/
```

### Remover checkpoint específico
```bash
# Checkpoint bruto
rm -rf training/outputs/lora_casual_shoes_3000steps_full/checkpoints/checkpoint-500

# Pipeline convertido
rm -rf training/outputs/lora_casual_shoes_3000steps_full/checkpoint_pipelines/checkpoint-500
```

## FAQ

### P: O treinamento para se eu desconectar o T9?
R: Sim, se o treinamento estiver salvando no T9 via symlink. Mantenha conectado durante treinamento.

### P: Posso mover de volta para o disco principal depois?
R: Sim, basta:
```bash
rm training/outputs  # Remove symlink
mv /Volumes/T9/shoes-training-outputs training/outputs
```

### P: Preciso converter todos os checkpoints?
R: Não. Converta apenas os que você deseja testar na API/frontend.

### P: Checkpoint incompleto ocupa menos espaço?
R: Sim, checkpoint-1000 está em progresso e ocupa apenas 1.5 GB vs 3.2 GB completo.

### P: Qual o tamanho mínimo que preciso manter?
R: Pipeline final (~4 GB) + lora_weights (~10 MB). Total: ~4 GB.

## Conclusão

O treinamento LoRA gera arquivos significativos, mas gerenciáveis. A melhor estratégia é:

1. Usar HD externo para todo processo de treinamento
2. Converter apenas checkpoints selecionados
3. Remover checkpoints intermediários após avaliação
4. Manter apenas o melhor checkpoint final

Isso permite validação completa mantendo uso de espaço controlado.
