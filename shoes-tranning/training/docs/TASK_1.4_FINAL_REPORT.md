# Task 1.4: Download e Teste de Stable Diffusion 1.5 - Relatório Final

**Data**: 2025-10-26
**Hardware**: Mac Studio M2 Max (32GB RAM)
**Status**: CONCLUÍDO COM SUCESSO (após correção)

---

## Sumário Executivo

Task 1.4 foi concluída com sucesso após identificar e corrigir um problema crítico relacionado ao uso de float16 no backend MPS. O modelo Stable Diffusion 1.5 está agora totalmente funcional e pronto para fine-tuning LoRA.

**Resultado Final**:
- Modelo SD 1.5 baixado e em cache (~4GB)
- 3/3 imagens de teste geradas com sucesso
- Performance adequada (~11s/imagem)
- Validação implementada para garantir qualidade

---

## Processo de Implementação

### Fase 1: Implementação Inicial (FALHA)

**Script**: `test_sd_inference.py`

**Configuração**:
```python
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,  # ERRO: Causa NaN no MPS
    safety_checker=None,
)
pipe = pipe.to("mps")
```

**Resultado**:
- [ERRO] Todas as 3 imagens geradas estavam completamente pretas
- Causa: valores NaN devido a float16 + MPS
- Detecção: Usuário identificou o problema ao visualizar as imagens

### Fase 2: Diagnóstico e Correção (SUCESSO)

**Problema Identificado**:
- MPS (Metal Performance Shaders) não é totalmente compatível com float16
- Operações de denoising geram valores NaN com float16
- NaN × 255 = 0 → imagens pretas

**Solução Implementada**:
```python
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float32,  # CORRIGIDO
    safety_checker=None,
)
pipe = pipe.to("mps")
```

**Script Corrigido**: `test_sd_inference_fixed.py`

---

## Resultados Finais

### Performance de Inferência

**Configuração**:
- Device: MPS (Apple Silicon)
- dtype: float32
- Steps: 25
- Guidance scale: 7.5
- Attention slicing: Habilitado

**Tempos de Geração**:

| Teste | Prompt | Tempo (s) | Status |
|-------|--------|-----------|--------|
| 1 | Black casual shoes | 14.20 | [OK] |
| 2 | Brown leather shoes | 9.95 | [OK] |
| 3 | White sneakers | 9.95 | [OK] |

**Estatísticas**:
- Média: 11.37s por imagem
- Mínimo: 9.95s (steady state)
- Máximo: 14.20s (primeira geração com warmup)

### Validação de Qualidade

**Teste 1 - Black Casual Shoes**:
```
Shape: (512, 512, 3)
dtype: uint8
Range: [0, 255] ✓
Qualidade: Alta
Background: Cinza/texturizado
Realismo: Excelente
```

**Teste 2 - Brown Leather Shoes**:
```
Shape: (512, 512, 3)
dtype: uint8
Range: [0, 255] ✓
Qualidade: Excelente
Background: Ambiente profissional
Realismo: Muito alto
```

**Teste 3 - White Sneakers**:
```
Shape: (512, 512, 3)
dtype: uint8
Range: [0, 255] ✓
Qualidade: Boa
Background: Cinza neutro
Realismo: Alto (par de sapatos)
```

**Conclusão**: Todas as 3 imagens passaram na validação e apresentam boa qualidade visual.

### Uso de Memória

**Durante Carregamento**:
- Antes: 11.9 GB disponível
- Depois: 6.6 GB disponível
- Usado pelo modelo: ~5.3 GB

**Durante Inferência**:
- Antes: 6.6 GB disponível
- Depois: 6.2 GB disponível
- Usado por geração: ~0.4 GB

**Total**: ~6-8 GB (modelo + inferência)

**Análise**: Viável para treinamento com M2 Max (32GB RAM).

---

## Análise Técnica

### Por que float32 em vez de float16?

**float16 (Problema)**:
- 16 bits de precisão
- Range limitado: ±65,504
- MPS tem bugs conhecidos com operações float16
- Gera valores NaN durante denoising
- Resultado: imagens pretas (inválidas)

**float32 (Solução)**:
- 32 bits de precisão
- Range amplo: ±3.4×10³⁸
- Operações estáveis no MPS
- Não gera NaN
- Resultado: imagens corretas

**Trade-off**:
- Usa ~2× mais memória (~6-8 GB vs ~4-5 GB)
- ~10-20% mais lento
- Mas: funciona corretamente (essencial!)

### Validação Implementada

Para evitar futuros problemas, implementamos validação automática:

```python
def validate_image_array(image_array: np.ndarray, prompt: str) -> bool:
    # Verifica NaN
    if np.isnan(image_array).any():
        return False

    # Verifica inf
    if np.isinf(image_array).any():
        return False

    # Verifica se está toda preta
    if image_array.max() == 0:
        return False

    # Verifica range válido [0, 255]
    if image_array.min() < 0 or image_array.max() > 255:
        return False

    return True
```

Esta validação será incorporada ao script de treinamento.

---

## Implicações para Treinamento LoRA

### Configurações Recomendadas

Com base nos testes, as seguintes configurações são recomendadas:

```python
training_config = {
    # Modelo e Device
    'model_id': 'runwayml/stable-diffusion-v1-5',
    'torch_dtype': torch.float32,  # CRÍTICO: Não usar float16 no MPS
    'device': 'mps',

    # Otimizações de Memória
    'gradient_checkpointing': True,  # Essencial com float32
    'enable_attention_slicing': True,
    'mixed_precision': 'no',  # Desabilitar para MPS

    # Treinamento
    'train_batch_size': 2,  # Ajustado para float32
    'gradient_accumulation_steps': 8,  # Batch efetivo = 16
    'learning_rate': 1e-4,
    'max_train_steps': 3000,

    # LoRA
    'lora_rank': 8,
    'lora_alpha': 16,
    'lora_dropout': 0.0,

    # Validação
    'validation_steps': 500,
    'num_validation_images': 4,
}
```

### Estimativas de Tempo

**Baseado em 11.37s/imagem**:

**Durante Treinamento**:
- 3,000 steps × ~2-3s/step = ~2.5-3 horas
- 6 validações × 4 imagens × 11.37s = ~4.5 minutos
- **Total estimado: ~3 horas**

**Geração de Dataset Sintético (Após Treinamento)**:
- 1,000 imagens × 11.37s = ~3.2 horas
- 3,000 imagens × 11.37s = ~9.5 horas
- **Viável em uma noite**

### Estimativas de Memória

**Treinamento**:
- Modelo base: ~5-6 GB
- Gradientes: ~2-3 GB
- Ativações: ~2-3 GB (com gradient checkpointing)
- Overhead: ~1-2 GB
- **Total: ~10-14 GB**

**Disponível**: 32 GB total, ~20-22 GB após sistema operacional

**Análise**: Margem confortável de ~8-10 GB livres.

---

## Observações Importantes

### 1. Qualidade dos Backgrounds

As imagens geradas não têm fundo branco puro, conforme solicitado nos prompts. Isso é **esperado** por dois motivos:

1. **Modelo Base Não Especializado**: SD 1.5 foi treinado em imagens gerais da internet, não em product photography profissional

2. **Fine-tuning é Necessário**: O treinamento LoRA com nosso dataset (que tem fundos brancos consistentes) ensinará o modelo a gerar fundos brancos

**Expectativa Pós-Fine-tuning**:
- Backgrounds brancos consistentes
- Melhor centralização dos produtos
- Estilo mais próximo do dataset original

### 2. Diversidade de Estilos

O modelo base gera:
- Diferentes ângulos (frontal, 3/4, par)
- Diferentes contextos (pessoa usando, produto isolado)
- Diferentes iluminações

Isso é **positivo** para treino, pois mostra que o modelo tem capacidade expressiva.

### 3. Responsividade a Prompts

O modelo respondeu corretamente aos atributos solicitados:
- "black" → sapatos pretos ✓
- "brown leather" → couro marrom ✓
- "white sneakers" → tênis brancos ✓

Isso confirma que o text encoder (CLIP) está funcionando.

---

## Arquivos Criados

### Scripts

1. **training/scripts/test_sd_inference.py** (481 linhas)
   - Versão inicial (float16 - com bug)
   - Mantido para referência

2. **training/scripts/test_sd_inference_fixed.py** (510 linhas)
   - Versão corrigida (float32)
   - Com validação de imagens
   - **Usar esta versão**

### Outputs - Primeira Tentativa (FALHAS)

1. `training/outputs/test_inference_1.png` - Preta (inválida)
2. `training/outputs/test_inference_2.png` - Preta (inválida)
3. `training/outputs/test_inference_3.png` - Preta (inválida)

### Outputs - Versão Corrigida (SUCESSO)

1. `training/outputs/test_inference_fixed_1.png` - Black shoes ✓
2. `training/outputs/test_inference_fixed_2.png` - Brown leather shoes ✓
3. `training/outputs/test_inference_fixed_3.png` - White sneakers ✓

### Documentação

1. **training/docs/TASK_1.4_DOCUMENTATION.md**
   - Documentação inicial (antes da correção)

2. **training/docs/TASK_1.4_ISSUE_REPORT.md**
   - Análise detalhada do problema float16 → NaN
   - Solução e troubleshooting guide

3. **training/docs/TASK_1.4_FINAL_REPORT.md** (este arquivo)
   - Relatório final completo

---

## Lições Aprendidas

### 1. MPS != CUDA

Configurações que funcionam em CUDA não necessariamente funcionam em MPS. Sempre testar especificamente para MPS.

### 2. Validação é Essencial

Não confiar apenas em "sem erro = sucesso". Implementar validações explícitas de outputs.

### 3. Warnings São Importantes

```
RuntimeWarning: invalid value encountered in cast
```

Este warning deveria ter sido investigado imediatamente. Foi o primeiro sinal do problema.

### 4. float32 > float16 para MPS (2024)

Apesar de usar mais memória, float32 é a única opção estável para MPS com Stable Diffusion.

### 5. Documentação de Problemas é Valiosa

Documentar problemas encontrados e soluções economiza tempo futuro e ajuda a comunidade.

---

## Próximos Passos

### Task 1.5: Script de Treinamento LoRA

Com SD 1.5 validado e funcionando, estamos prontos para:

1. **Implementar Loop de Treinamento**:
   - Carregar dataset casual_shoes (1,991 imagens)
   - Processar captions estruturados
   - Batch processing com DataLoader

2. **Configurar LoRA**:
   - rank=8 (ou 16 para melhor qualidade)
   - alpha=16 (ou 32)
   - target_modules=['to_q', 'to_k', 'to_v', 'to_out.0']

3. **Implementar Validação**:
   - Gerar 4 imagens a cada 500 steps
   - Salvar checkpoints
   - Calcular métricas (loss)

4. **Logging**:
   - TensorBoard ou wandb
   - Tracking de loss, learning rate
   - Salvar imagens geradas

**Estimativa**: 3-4 horas de implementação

---

## Conclusão

Task 1.4 foi concluída com **SUCESSO COMPLETO** após identificar e resolver um bug crítico relacionado a float16 no MPS.

**Aprendizados Principais**:
- float32 é essencial para MPS + Stable Diffusion
- Validação de outputs deve ser parte do pipeline
- Debugging sistemático economiza tempo

**Ambiente Atual**:
- [OK] Modelo SD 1.5 funcionando
- [OK] Performance adequada (~11s/imagem)
- [OK] Memória sob controle (~6-8 GB)
- [OK] Validação implementada
- [OK] Pronto para Task 1.5

**Status Final**: APROVADO PARA TREINAMENTO

**Progresso Sprint 1**: 4/5 tasks concluídas (80%)

---

**Última Atualização**: 2025-10-26
**Autor**: Task 1.4 - Download e Teste de SD 1.5
**Status**: CONCLUÍDO E DOCUMENTADO
**Próximo**: Task 1.5 - Script de Treinamento LoRA
