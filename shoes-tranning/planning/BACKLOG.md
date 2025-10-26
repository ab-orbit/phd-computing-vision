# Backlog - Geração de Imagens Sintéticas: Casual Shoes

**Objetivo**: Desenvolver modelo de geração de imagens sintéticas para expansão do dataset de Casual Shoes usando Stable Diffusion 1.5 + LoRA otimizado para Apple M2 Max.

**Meta**: Gerar 3,000-5,000 imagens sintéticas de alta qualidade para expansão do dataset.

---

## SPRINT 1: Análise e Preparação (Semana 1)
**Duração**: 3-5 dias
**Objetivo**: Preparar dados e ambiente para treinamento

### PRIORIDADE ALTA

#### Task 1.1: Análise Exploratória - Casual Shoes
**Estimativa**: 2-3 horas
**Status**: PENDENTE

**Descrição**:
Analisar especificamente a categoria Casual Shoes do dataset para entender distribuições e características.

**Subtarefas**:
- [ ] Criar script `casual_shoes_analysis.py`
- [ ] Filtrar dataset por articleType == "Casual Shoes"
- [ ] Analisar distribuições:
  - [ ] Cores (baseColour)
  - [ ] Gênero (gender)
  - [ ] Marcas (brandName)
  - [ ] Materiais (articleAttributes.fabric)
  - [ ] Estações (season)
- [ ] Gerar visualizações:
  - [ ] Distribuição de cores
  - [ ] Grid de amostras (5x5 ou 10x10)
  - [ ] Análise de dimensões das imagens
- [ ] Identificar padrões visuais comuns
- [ ] Documentar findings em `outputs/casual_shoes_report.txt`

**Outputs Esperados**:
- `exploratory/scripts/casual_shoes_analysis.py`
- `exploratory/outputs/casual_shoes_report.txt`
- `exploratory/figures/casual_shoes_distributions.png`
- `exploratory/figures/casual_shoes_sample_grid.png`

**Critérios de Aceitação**:
- Relatório com estatísticas completas de Casual Shoes
- Entendimento claro das características visuais
- Identificação de subgrupos para condicionamento

---

#### Task 1.2: Preparação do Subset de Treinamento
**Estimativa**: 1-2 horas
**Status**: PENDENTE
**Depende de**: Task 1.1

**Descrição**:
Criar splits específicos para Casual Shoes e preparar dados para treinamento.

**Subtarefas**:
- [ ] Criar script `prepare_casual_shoes_dataset.py`
- [ ] Filtrar 2,845 imagens de Casual Shoes
- [ ] Criar splits estratificados:
  - [ ] Train: 70% (~1,992 imagens)
  - [ ] Val: 15% (~427 imagens)
  - [ ] Test: 15% (~426 imagens)
- [ ] Redimensionar imagens para 512x512:
  - [ ] Manter aspect ratio
  - [ ] Padding se necessário
  - [ ] Salvar em formato PNG (sem perdas)
- [ ] Criar captions estruturados:
  - [ ] Template: "A professional product photo of [color] [articleType], [season] collection, [gender], centered on white background"
  - [ ] Incluir atributos adicionais quando disponíveis
  - [ ] Salvar em `casual_shoes_captions.json`
- [ ] Validar integridade:
  - [ ] Todas as imagens carregam corretamente
  - [ ] Captions correspondem às imagens
  - [ ] Sem duplicatas

**Outputs Esperados**:
- `data/casual_shoes/train/` (1,992 imagens 512x512)
- `data/casual_shoes/val/` (427 imagens)
- `data/casual_shoes/test/` (426 imagens)
- `data/casual_shoes/captions_train.json`
- `data/casual_shoes/captions_val.json`
- `data/casual_shoes/metadata.json`

**Critérios de Aceitação**:
- Imagens redimensionadas corretamente
- Captions bem formatados e informativos
- Splits balanceados por cor/gênero

---

#### Task 1.3: Setup do Ambiente de Treinamento
**Estimativa**: 1-2 horas
**Status**: PENDENTE

**Descrição**:
Configurar ambiente Python com todas as dependências necessárias para Stable Diffusion + LoRA no M2 Max.

**Subtarefas**:
- [ ] Criar ambiente virtual específico:
  ```bash
  python -m venv venv-sd-training
  source venv-sd-training/bin/activate
  ```
- [ ] Instalar PyTorch com suporte MPS:
  ```bash
  pip install torch torchvision torchaudio
  ```
- [ ] Instalar bibliotecas de difusão:
  ```bash
  pip install diffusers transformers accelerate
  pip install peft bitsandbytes  # Para LoRA
  pip install xformers  # Otimizações de atenção (opcional)
  ```
- [ ] Instalar utilitários:
  ```bash
  pip install wandb  # Tracking de experimentos
  pip install pillow numpy tqdm
  pip install datasets huggingface_hub
  ```
- [ ] Verificar instalação:
  - [ ] PyTorch detecta MPS
  - [ ] diffusers carrega modelos
  - [ ] CUDA não é necessário
- [ ] Criar script de verificação `check_environment.py`
- [ ] Documentar versões em `requirements-training.txt`

**Outputs Esperados**:
- `requirements-training.txt`
- `training/scripts/check_environment.py`
- Ambiente virtual funcional

**Critérios de Aceitação**:
- PyTorch MPS disponível e funcionando
- Todas as bibliotecas instaladas
- Script de verificação executa sem erros

---

#### Task 1.4: Download e Teste do Modelo Base
**Estimativa**: 30-60 minutos
**Status**: PENDENTE
**Depende de**: Task 1.3

**Descrição**:
Fazer download do Stable Diffusion 1.5 e testar inferência básica.

**Subtarefas**:
- [ ] Criar script `test_sd_inference.py`
- [ ] Download do modelo base:
  ```python
  from diffusers import StableDiffusionPipeline

  model_id = "runwayml/stable-diffusion-v1-5"
  pipe = StableDiffusionPipeline.from_pretrained(
      model_id,
      torch_dtype=torch.float16
  )
  pipe = pipe.to("mps")
  ```
- [ ] Testar geração de imagem simples:
  - [ ] Prompt: "A professional product photo of black casual shoes on white background"
  - [ ] Verificar tempo de geração
  - [ ] Validar qualidade da imagem
- [ ] Documentar uso de memória:
  - [ ] Durante load do modelo
  - [ ] Durante inferência
- [ ] Salvar imagem de teste

**Outputs Esperados**:
- `training/scripts/test_sd_inference.py`
- `training/outputs/test_inference.png`
- Modelo base baixado em cache (~4GB)

**Critérios de Aceitação**:
- Modelo carrega em <2 minutos
- Geração funciona em M2 Max (MPS)
- Tempo de inferência < 10 segundos
- Memória usada < 8GB

---

### PRIORIDADE MÉDIA

#### Task 1.5: Criar Script de Treinamento Base
**Estimativa**: 3-4 horas
**Status**: PENDENTE
**Depende de**: Task 1.3, 1.4

**Descrição**:
Desenvolver script de treinamento LoRA para Stable Diffusion otimizado para M2 Max.

**Subtarefas**:
- [ ] Criar `training/scripts/train_lora_sd15.py`
- [ ] Implementar configurações LoRA:
  ```python
  from peft import LoraConfig, get_peft_model

  lora_config = LoraConfig(
      r=8,  # Rank (começar pequeno)
      lora_alpha=16,
      target_modules=["to_k", "to_q", "to_v", "to_out.0"],
      lora_dropout=0.0,
      bias="none",
  )
  ```
- [ ] Implementar training loop:
  - [ ] DataLoader para imagens + captions
  - [ ] Gradient accumulation (steps=8)
  - [ ] Mixed precision (fp16)
  - [ ] Gradient checkpointing
  - [ ] Checkpoint saving
- [ ] Adicionar logging:
  - [ ] Loss por step
  - [ ] Learning rate scheduling
  - [ ] Tempo por step
  - [ ] Uso de memória
- [ ] Integrar Weights & Biases (opcional):
  - [ ] Track de métricas
  - [ ] Visualização de amostras
- [ ] Criar arquivo de configuração `config/train_config.yaml`:
  ```yaml
  model:
    base: "runwayml/stable-diffusion-v1-5"
    lora_rank: 8
    lora_alpha: 16

  training:
    batch_size: 2
    gradient_accumulation: 8
    learning_rate: 1e-4
    num_epochs: 10
    mixed_precision: "fp16"

  data:
    train_dir: "data/casual_shoes/train"
    val_dir: "data/casual_shoes/val"
    resolution: 512
  ```

**Outputs Esperados**:
- `training/scripts/train_lora_sd15.py`
- `training/configs/casual_shoes_config.yaml`
- Script pronto para execução

**Critérios de Aceitação**:
- Script roda sem erros
- Configurações parametrizadas
- Logging funcional
- Suporta checkpoint e resume

---

## SPRINT 2: Prototipagem e Ajuste (Semana 2)
**Duração**: 5-7 dias
**Objetivo**: Treinar modelo protótipo e validar pipeline

### PRIORIDADE ALTA

#### Task 2.1: Treinamento Protótipo (Subset Pequeno)
**Estimativa**: 4-6 horas (inclui 1.5h de treinamento)
**Status**: PENDENTE
**Depende de**: Task 1.5

**Descrição**:
Treinar LoRA com subset reduzido (300-500 imagens) para validar pipeline e ajustar hiperparâmetros.

**Subtarefas**:
- [ ] Criar subset de 300-500 imagens:
  - [ ] Amostragem estratificada (cores balanceadas)
  - [ ] Copiar para `data/casual_shoes/prototype/`
- [ ] Executar treinamento:
  ```bash
  python training/scripts/train_lora_sd15.py \
    --config training/configs/prototype_config.yaml \
    --output_dir training/checkpoints/prototype_v1
  ```
- [ ] Monitorar métricas:
  - [ ] Loss convergindo
  - [ ] Tempo por step (~2-3s)
  - [ ] Memória estável (~8-10GB)
- [ ] Gerar amostras durante treinamento:
  - [ ] A cada 100 steps
  - [ ] Prompts fixos para comparação
- [ ] Salvar checkpoints:
  - [ ] A cada epoch
  - [ ] Best model (menor loss)
- [ ] Documentar resultados:
  - [ ] Loss final
  - [ ] Tempo total
  - [ ] Qualidade visual (subjetiva)

**Outputs Esperados**:
- `training/checkpoints/prototype_v1/`
- `training/outputs/prototype_v1/samples/`
- `training/logs/prototype_v1.log`

**Critérios de Aceitação**:
- Treinamento completa sem crashes
- Loss diminui consistentemente
- Amostras mostram aprendizado
- Tempo < 2 horas total

---

#### Task 2.2: Avaliação do Protótipo
**Estimativa**: 2-3 horas
**Status**: PENDENTE
**Depende de**: Task 2.1

**Descrição**:
Avaliar qualidade do modelo protótipo usando métricas objetivas e análise visual.

**Subtarefas**:
- [ ] Criar script `evaluate_model.py`
- [ ] Gerar 100 imagens sintéticas:
  - [ ] Variação de cores
  - [ ] Variação de prompts
  - [ ] Seed fixo para reprodutibilidade
- [ ] Calcular métricas:
  - [ ] CLIP Score (imagem vs texto)
  - [ ] IS (Inception Score) - opcional
  - [ ] Análise de diversidade (feature distance)
- [ ] Análise visual manual:
  - [ ] Grid de 100 imagens
  - [ ] Identificar artifacts comuns
  - [ ] Avaliar realismo
- [ ] Comparar com imagens reais:
  - [ ] Side-by-side comparison
  - [ ] Identificar diferenças
- [ ] Documentar findings:
  - [ ] Pontos fortes
  - [ ] Pontos fracos
  - [ ] Sugestões de melhoria

**Outputs Esperados**:
- `training/scripts/evaluate_model.py`
- `training/outputs/prototype_v1/evaluation/`
- `training/outputs/prototype_v1/evaluation_report.txt`
- `training/outputs/prototype_v1/samples_grid.png`

**Critérios de Aceitação**:
- CLIP Score > 0.20 (baseline)
- Imagens reconhecíveis como sapatos
- Poucos artifacts graves
- Fundo geralmente limpo

---

#### Task 2.3: Ajuste de Hiperparâmetros
**Estimativa**: 4-8 horas
**Status**: PENDENTE
**Depende de**: Task 2.2

**Descrição**:
Iterar sobre hiperparâmetros para melhorar qualidade antes do treinamento completo.

**Subtarefas**:
- [ ] Testar variações de LoRA rank:
  - [ ] rank=4 (mais rápido, menos capacidade)
  - [ ] rank=8 (baseline)
  - [ ] rank=16 (mais lento, maior capacidade)
- [ ] Testar learning rates:
  - [ ] 5e-5 (conservador)
  - [ ] 1e-4 (baseline)
  - [ ] 2e-4 (agressivo)
- [ ] Testar número de epochs:
  - [ ] 5 epochs
  - [ ] 10 epochs (baseline)
  - [ ] 15 epochs
- [ ] Para cada configuração:
  - [ ] Treinar em subset de 300 imagens
  - [ ] Avaliar com métricas
  - [ ] Gerar grid de amostras
- [ ] Comparar resultados:
  - [ ] Tabela de métricas
  - [ ] Visual comparison
- [ ] Selecionar melhor configuração

**Outputs Esperados**:
- `training/experiments/hyperparameter_search/`
- `training/experiments/comparison_report.md`
- Configuração otimizada para treinamento completo

**Critérios de Aceitação**:
- Pelo menos 3 configurações testadas
- Melhor configuração identificada
- Melhoria de 10-20% em CLIP Score
- Qualidade visual superior ao baseline

---

## SPRINT 3: Treinamento Completo (Semana 3)
**Duração**: 5-7 dias
**Objetivo**: Treinar modelo final e gerar dataset expandido

### PRIORIDADE ALTA

#### Task 3.1: Treinamento Completo - Casual Shoes
**Estimativa**: 4-6 horas (inclui 2-3h de treinamento)
**Status**: PENDENTE
**Depende de**: Task 2.3

**Descrição**:
Treinar modelo LoRA final usando todas as 2,845 imagens de Casual Shoes com hiperparâmetros otimizados.

**Subtarefas**:
- [ ] Preparar configuração final:
  - [ ] Usar melhor configuração de Task 2.3
  - [ ] Ajustar epochs se necessário
- [ ] Executar treinamento completo:
  ```bash
  python training/scripts/train_lora_sd15.py \
    --config training/configs/casual_shoes_final.yaml \
    --output_dir training/checkpoints/casual_shoes_v1
  ```
- [ ] Monitorar progresso:
  - [ ] Loss no train e validation
  - [ ] Gerar amostras a cada epoch
  - [ ] Early stopping se necessário
- [ ] Salvar checkpoints:
  - [ ] A cada epoch
  - [ ] Best model
  - [ ] Final model
- [ ] Calcular tempo total e estatísticas

**Outputs Esperados**:
- `training/checkpoints/casual_shoes_v1/`
- `training/outputs/casual_shoes_v1/samples/`
- `training/logs/casual_shoes_v1.log`

**Critérios de Aceitação**:
- Treinamento completo sem interrupções
- Loss validation estável/decrescente
- Amostras de alta qualidade
- Tempo < 4 horas

---

#### Task 3.2: Geração de Dataset Expandido
**Estimativa**: 4-6 horas (inclui 2h de geração)
**Status**: PENDENTE
**Depende de**: Task 3.1

**Descrição**:
Gerar 3,000-5,000 imagens sintéticas de Casual Shoes para expansão do dataset.

**Subtarefas**:
- [ ] Criar script `generate_synthetic_dataset.py`
- [ ] Definir distribuição de prompts:
  - [ ] Cores: proporções similares ao dataset original
  - [ ] Gêneros: 60% Men, 40% Women
  - [ ] Estilos: variado
- [ ] Implementar geração em lote:
  - [ ] Batch de 10-20 imagens
  - [ ] Progress bar
  - [ ] Checkpoint a cada 500 imagens
- [ ] Gerar 3,000 imagens (Phase 1):
  - [ ] Seeds aleatórios mas reprodutíveis
  - [ ] Salvar prompts usados
  - [ ] Salvar metadados
- [ ] Organizar output:
  ```
  data/synthetic_casual_shoes/
    images/
      00001.png
      00002.png
      ...
    metadata.json
    prompts.txt
  ```
- [ ] Validar qualidade:
  - [ ] Remover imagens com artifacts graves
  - [ ] Verificar diversidade

**Outputs Esperados**:
- `training/scripts/generate_synthetic_dataset.py`
- `data/synthetic_casual_shoes/images/` (3,000+ imagens)
- `data/synthetic_casual_shoes/metadata.json`
- `data/synthetic_casual_shoes/generation_report.txt`

**Critérios de Aceitação**:
- 3,000+ imagens geradas
- Diversidade visual mantida
- < 5% de imagens com artifacts graves
- Metadados completos

---

## SPRINT 4: Validação e Métricas (Semana 4)
**Duração**: 3-5 dias
**Objetivo**: Avaliar qualidade do dataset expandido

### PRIORIDADE ALTA

#### Task 4.1: Avaliação Completa do Dataset Sintético
**Estimativa**: 3-4 horas
**Status**: PENDENTE
**Depende de**: Task 3.2

**Descrição**:
Avaliar rigorosamente o dataset sintético usando métricas objetivas e análise manual.

**Subtarefas**:
- [ ] Criar script `evaluate_synthetic_dataset.py`
- [ ] Calcular métricas objetivas:
  - [ ] FID (Fréchet Inception Distance):
    - [ ] Entre real e sintético
    - [ ] Target: FID < 50 (bom), < 30 (excelente)
  - [ ] CLIP Score médio:
    - [ ] Imagens vs prompts
    - [ ] Target: > 0.25
  - [ ] Inception Score (IS):
    - [ ] Diversidade e qualidade
    - [ ] Comparar com dataset real
  - [ ] Diversidade:
    - [ ] Feature distance médio
    - [ ] Clustering analysis
- [ ] Análise visual manual:
  - [ ] Amostrar 200 imagens aleatórias
  - [ ] Classificar em 5 categorias:
    - Excelente (4-5)
    - Boa (3-4)
    - Aceitável (2-3)
    - Ruim (1-2)
    - Inaceitável (0-1)
  - [ ] Identificar padrões de falhas
- [ ] Comparação com dataset real:
  - [ ] Grid lado-a-lado (50 real, 50 sintético)
  - [ ] Teste cego (identificar qual é sintético)
  - [ ] Análise de distribuição de features
- [ ] Documentar resultados detalhados

**Outputs Esperados**:
- `evaluation/scripts/evaluate_synthetic_dataset.py`
- `evaluation/outputs/metrics_report.json`
- `evaluation/outputs/visual_analysis_report.txt`
- `evaluation/outputs/comparison_grids/`

**Critérios de Aceitação**:
- FID < 50
- CLIP Score médio > 0.25
- 80%+ das imagens classificadas como Boa ou melhor
- Distribuição similar ao dataset real

---

#### Task 4.2: Análise de Falhas e Iteração
**Estimativa**: 2-3 horas
**Status**: PENDENTE
**Depende de**: Task 4.1

**Descrição**:
Identificar e categorizar falhas comuns, propor melhorias para iteração futura.

**Subtarefas**:
- [ ] Analisar imagens com baixo score:
  - [ ] Extrair bottom 10% por CLIP score
  - [ ] Identificar padrões comuns
- [ ] Categorizar tipos de falhas:
  - [ ] Artifacts (borrões, deformações)
  - [ ] Fundo incorreto
  - [ ] Proporções erradas
  - [ ] Cores incorretas
  - [ ] Outros
- [ ] Quantificar cada tipo de falha
- [ ] Propor melhorias:
  - [ ] Ajustes de prompt
  - [ ] Mais treinamento
  - [ ] Negative prompts
  - [ ] Outras técnicas
- [ ] Criar roadmap de melhorias
- [ ] Documentar lições aprendidas

**Outputs Esperados**:
- `evaluation/outputs/failure_analysis.md`
- `evaluation/outputs/improvement_roadmap.md`
- `evaluation/outputs/failed_samples/` (exemplos)

**Critérios de Aceitação**:
- Falhas categorizadas e quantificadas
- Causas identificadas
- Plano de ação para melhorias
- Documentação completa

---

#### Task 4.3: Documentação Final do MVP
**Estimativa**: 2-3 horas
**Status**: PENDENTE
**Depende de**: Task 4.1, 4.2

**Descrição**:
Criar documentação completa do MVP incluindo resultados, aprendizados e próximos passos.

**Subtarefas**:
- [ ] Criar documento `MVP_CASUAL_SHOES.md`:
  - [ ] Objetivo e escopo
  - [ ] Metodologia
  - [ ] Resultados:
    - Métricas finais
    - Visualizações
    - Comparações
  - [ ] Análise:
    - Pontos fortes
    - Limitações
    - Falhas comuns
  - [ ] Lições aprendidas
  - [ ] Próximos passos
- [ ] Criar apresentação resumida:
  - [ ] Slides com principais achados
  - [ ] Visualizações chave
  - [ ] Recomendações
- [ ] Atualizar README principal
- [ ] Documentar setup e uso:
  - [ ] Como treinar modelo
  - [ ] Como gerar imagens
  - [ ] Como avaliar resultados
- [ ] Criar guia de reprodução

**Outputs Esperados**:
- `docs/MVP_CASUAL_SHOES.md`
- `docs/TRAINING_GUIDE.md`
- `docs/GENERATION_GUIDE.md`
- `docs/presentation.pdf` (opcional)

**Critérios de Aceitação**:
- Documentação completa e clara
- Resultados bem apresentados
- Guias reproduzíveis
- Próximos passos definidos

---

## BACKLOG (Prioridade Baixa / Futuro)

### Melhorias de Modelo

#### Task B.1: Implementar Negative Prompts
**Estimativa**: 1-2 horas

Adicionar suporte para negative prompts para reduzir artifacts:
- "blurry, low quality, deformed, distorted, watermark, text"

---

#### Task B.2: Treinar com Resoluções Maiores
**Estimativa**: 4-6 horas

Testar treinamento em 768x768 ou usar SDXL para melhor qualidade.

---

#### Task B.3: Implementar ControlNet
**Estimativa**: 8-12 horas

Adicionar ControlNet para controle de pose/estrutura dos sapatos.

---

#### Task B.4: Multi-LoRA por Subcategoria
**Estimativa**: 6-8 horas

Treinar LoRAs separados para:
- Casual Shoes - Esportivo
- Casual Shoes - Formal
- Casual Shoes - Canvas

---

### Expansão de Funcionalidades

#### Task B.5: Geração de Descrições (Mistral 7B)
**Estimativa**: 12-16 horas

Fine-tune Mistral 7B para gerar descrições das imagens sintéticas.

---

#### Task B.6: Geração de Metadados Completos
**Estimativa**: 6-8 horas

Gerar metadados JSON completos para cada imagem sintética.

---

#### Task B.7: Interface Web (Gradio)
**Estimativa**: 4-6 horas

Criar interface interativa para gerar imagens on-demand.

---

### Outras Categorias

#### Task B.8: Replicar para Tshirts
**Estimativa**: 10-15 horas

Repetir processo completo para categoria Tshirts (~7,000 imagens).

---

#### Task B.9: Replicar para Shirts
**Estimativa**: 10-15 horas

Repetir processo para categoria Shirts (~3,200 imagens).

---

## DEFINIÇÕES E CRITÉRIOS

### Definition of Done (DoD)

Uma task é considerada "DONE" quando:

1. **Código**:
   - Implementado e testado
   - Comentado adequadamente
   - Segue padrões do projeto
   - Sem erros ou warnings

2. **Documentação**:
   - README/docs atualizados
   - Docstrings completas
   - Exemplo de uso fornecido

3. **Outputs**:
   - Arquivos gerados conforme especificado
   - Qualidade validada
   - Organizados corretamente

4. **Testes**:
   - Script executa sem erros
   - Resultados validados
   - Edge cases considerados

5. **Revisão**:
   - Critérios de aceitação atendidos
   - Performance aceitável
   - Prontos para próxima task

---

### Métricas de Sucesso do MVP

**Quantitativas**:
- FID Score < 50 (target: < 40)
- CLIP Score médio > 0.25 (target: > 0.28)
- 3,000+ imagens sintéticas geradas
- Taxa de falhas < 10%
- Tempo de geração < 6s/imagem

**Qualitativas**:
- 80%+ das imagens visualmente aceitáveis
- Fundo limpo em 90%+ das imagens
- Cores consistentes com prompts
- Proporções realistas
- Diversidade visual mantida

---

## TIMELINE ESTIMADO

**Semana 1** (Sprint 1):
- Dias 1-2: Tasks 1.1, 1.2
- Dia 3: Tasks 1.3, 1.4
- Dias 4-5: Task 1.5

**Semana 2** (Sprint 2):
- Dias 1-2: Task 2.1
- Dia 3: Task 2.2
- Dias 4-5: Task 2.3

**Semana 3** (Sprint 3):
- Dias 1-2: Task 3.1
- Dias 3-5: Task 3.2

**Semana 4** (Sprint 4):
- Dias 1-2: Task 4.1
- Dia 3: Task 4.2
- Dias 4-5: Task 4.3

**Total**: 4 semanas (20-25 dias úteis)

---

## RISCOS E MITIGAÇÕES

### Risco 1: Modelo não converge
**Probabilidade**: Média
**Impacto**: Alto
**Mitigação**:
- Começar com subset pequeno (Task 2.1)
- Ajuste de hiperparâmetros (Task 2.3)
- Usar configurações comprovadas

### Risco 2: Qualidade insuficiente (FID > 80)
**Probabilidade**: Média
**Impacto**: Alto
**Mitigação**:
- Iteração rápida de protótipos
- Análise detalhada de falhas (Task 4.2)
- Ajustes de prompts e configurações

### Risco 3: Problemas de memória no M2 Max
**Probabilidade**: Baixa
**Impacto**: Médio
**Mitigação**:
- Configurações otimizadas (batch=2, grad_accum=8)
- Gradient checkpointing
- Monitoramento contínuo de memória

### Risco 4: Tempo de treinamento muito longo
**Probabilidade**: Baixa
**Impacto**: Médio
**Mitigação**:
- Treinamento overnight
- Otimizações MPS
- Subset menor se necessário

---

**Última Atualização**: 2025-10-26
**Versão**: 1.0
**Status Geral**: SPRINT 1 - PRONTO PARA INICIAR
