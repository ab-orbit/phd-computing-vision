# Plano de Desenvolvimento: Modelo de Geração de Dados Sintéticos para E-commerce de Moda

## 1. Visão Geral do Projeto
### 1.1 Objetivo
Desenvolver um sistema de geração de dados sintéticos para produtos de moda (e-commerce) que seja capaz de:
- Gerar imagens realistas de produtos
- Criar descrições textuais coerentes
- Produzir metadados estruturados consistentes
- Manter correspondência multimodal entre imagem, texto e metadados

### 1.2 Dataset Base
- **Fonte**: Fashion Product Images Dataset (Kaggle)
- **Localização**: `/Users/jwcunha/.cache/kagglehub/datasets/paramaggarwal/fashion-product-images-dataset/versions/1/fashion-dataset/fashion-dataset/`
- **Estrutura**:
  - `styles.csv`: Mapeamento de produtos com categorias (44,446 registros)
  - `images/`: Imagens de alta resolução (44,441 arquivos .jpg)
  - `styles/`: Metadados completos (44,446 arquivos .json)
  - `images.csv`: Mapeamento de imagens com URLs originais
- **Tamanho Total**: ~30GB
- **Características**: Imagens profissionais + atributos manuais + descrições textuais

### 1.3 Análise Inicial do Dataset (REALIZADA)

> **Nota**: Esta seção documenta os insights obtidos da análise exploratória inicial realizada em 2025-10-26.
> Scripts de análise disponíveis em: `shoes-tranning/exploratory/`

#### 1.3.1 Estatísticas Gerais
- **Total de Produtos**: 44,446 produtos únicos
- **Período Temporal**: 2010-2017 (8 anos de dados)
- **Integridade dos Dados**:
  - ✓ Baixa taxa de valores faltantes
  - ✓ Sem registros duplicados
  - ⚠️ 5 imagens faltantes (~0.01%)
  - ✓ Alta completude de metadados JSON

#### 1.3.2 Distribuição por Categorias Principais

**Master Categories** (3 principais):
1. **Apparel**: ~31,000 produtos (70% do dataset)
2. **Footwear**: ~8,500 produtos (19%)
3. **Accessories**: ~4,000 produtos (9%)
4. Personal Care, Free Items, Home: <2% cada

**Top 10 Article Types** (mais representados):
| Rank | Tipo de Artigo | Quantidade | % do Dataset |
|------|----------------|------------|--------------|
| 1 | Tshirts | ~6,200 | 14.0% |
| 2 | Shirts | ~5,700 | 12.8% |
| 3 | Casual Shoes | ~2,500 | 5.6% |
| 4 | Watches | ~2,200 | 5.0% |
| 5 | Sports Shoes | ~1,900 | 4.3% |
| 6 | Kurtas | ~1,600 | 3.6% |
| 7 | Tops | ~1,500 | 3.4% |
| 8 | Handbags | ~1,450 | 3.3% |
| 9 | Sunglasses | ~1,400 | 3.1% |
| 10 | Jeans | ~1,350 | 3.0% |

*Top 10 cobrem ~57% do dataset total*

**Distribuição por Gênero**:
- Men: ~60%
- Women: ~38%
- Boys/Girls/Unisex: ~2%

**Distribuição por Estação**:
- Summer: ~34%
- Fall: ~26%
- Winter: ~21%
- Spring: ~19%
(Distribuição relativamente equilibrada)

**Distribuição por Uso**:
- Casual: ~76%
- Formal: ~11%
- Sports: ~8%
- Ethnic: ~4%
- Party/Smart Casual: <1% cada

**Top 10 Cores**:
1. Black (~8,500 produtos)
2. White (~5,000)
3. Blue (~4,500)
4. Grey (~3,000)
5. Navy Blue (~2,500)
6. Red (~2,000)
7. Brown (~1,800)
8. Pink (~1,500)
9. Green (~1,400)
10. Purple (~1,200)

#### 1.3.3 Características das Imagens

**Resoluções Comuns**:
- Variação significativa de resoluções (não padronizadas)
- Resoluções típicas: 80x60, 60x80, 2400x3200
- Aspect ratios predominantes: ~0.75 (retrato)
- Maioria das imagens em modo RGB

**Qualidade Visual**:
- ✓ Fotografias profissionais de produtos
- ✓ Fundo limpo/branco (excelente para treinamento)
- ✓ Boa iluminação e enquadramento consistente
- ✓ Produto centralizado e em destaque

**Tamanho de Arquivos**:
- Variação: ~10 KB a ~500 KB por imagem
- Média: ~150 KB
- Formato: JPEG com compressão variável

#### 1.3.4 Metadados JSON - Estrutura Rica

**Campos Principais** (presentes em >90% dos registros):
- `id`, `productDisplayName`
- `gender`, `masterCategory`, `subCategory`, `articleType`
- `baseColour`, `season`, `year`, `usage`
- `brandName`, `brandUserProfile`
- `price`, `discountedPrice`
- `styleImages` (múltiplas resoluções)

**Descrições de Produtos**:
- **productDescriptors.description**: Descrição técnica do produto
  - Média: 15-30 palavras
  - Formato: HTML (requer limpeza)
  - Conteúdo: Características físicas, materiais, detalhes

- **productDescriptors.style_note**: Nota de estilo
  - Média: 30-50 palavras
  - Formato: HTML
  - Conteúdo: Como usar, ocasiões, combinações

- **productDescriptors.materials_care_desc**: Materiais e cuidados
  - Média: 10-20 palavras
  - Informações sobre composição e manutenção

**Atributos Adicionais** (articleAttributes):
- Fit (Regular, Slim, Loose, etc.)
- Fabric (Cotton, Polyester, Leather, etc.)
- Occasion (Casual, Formal, Party, etc.)
- Neck (Round, V-Neck, Collar, etc.)
- Pattern (Solid, Striped, Printed, etc.)
- Sleeve (Short, Long, Sleeveless, etc.)

**Informações de Preço**:
- Faixa de preços: ₹100 - ₹50,000+
- Média: ~₹2,000-₹3,000
- Desconto médio: 10-15%

**Marcas**:
- Total de marcas únicas: ~2,000+
- Top marcas: Nike, Puma, Adidas, Roadster, United Colors of Benetton
- Mix de marcas premium e acessíveis

#### 1.3.5 Análise Temporal

**Distribuição por Ano**:
- 2010-2012: Crescimento gradual
- 2011-2012: Pico de produtos adicionados (~15,000-18,000/ano)
- 2013-2015: Estabilização
- 2016-2017: Menor volume

**Implicações**:
- Dataset cobre tendências de moda de 8 anos
- Possível usar temporal conditioning na geração
- Estilos vintage (2010-2012) vs modernos (2016-2017)

#### 1.3.6 Insights Multimodais

**Consistência Imagem-Metadados**:
- ✓ Cores base geralmente correspondem às cores visíveis nas imagens
- ✓ Categorias (articleType) alinhadas com o produto fotografado
- ✓ Gênero consistente com estilo visual do produto

**Descrições vs Imagens**:
- Descrições mencionam características visíveis
- Style notes complementam com contexto de uso
- Oportunidade para validação multimodal durante geração

#### 1.3.7 Desafios Identificados

1. **Variação de Resolução**: Imagens não padronizadas
   - Solução: Redimensionamento e normalização no pré-processamento

2. **HTML em Descrições**: Tags HTML nos textos
   - Solução: Limpeza com regex antes do treinamento

3. **Desbalanceamento de Categorias**: Algumas categorias com <100 exemplos
   - Solução: Focar em top 20-30 categorias para MVP

4. **Imagens Faltantes**: 5 produtos sem imagem
   - Impacto: Negligível (<0.01%)

5. **Atributos Opcionais**: Nem todos os produtos têm todos os atributos
   - Solução: Tratar campos faltantes como "não especificado" ou usar valores padrão

#### 1.3.8 Oportunidades Estratégicas

1. **Categorias Prioritárias para MVP** (ATUALIZADO):
   - **Fase 1 (ATUAL)**: Casual Shoes (~2,845 exemplos)
     - Justificativa: Categoria com boa quantidade de exemplos
     - Fundo limpo facilita treinamento de modelos generativos
     - Variação controlada: cores, materiais, estilos
     - 3ª categoria mais popular do dataset
   - Fase 2 (FUTURO): Tshirts (~7,067), Shirts (~3,217)
   - Fase 3 (FUTURO): Top 20 categorias

2. **Estratégia de Desenvolvimento Incremental**:
   - **Sprint 1-2**: Geração de imagens sintéticas (Casual Shoes)
   - **Sprint 3**: Expansão do dataset com imagens geradas
   - **Sprint 4**: Validação e métricas de qualidade
   - **Sprint 5+**: Geração de texto e metadados (futuro)

3. **Vantagens do Dataset**:
   - ✓ Tamanho suficiente para fine-tuning (~44K produtos)
   - ✓ Diversidade de categorias, cores, estilos
   - ✓ Metadados ricos para condicionamento
   - ✓ Descrições textuais para training de LLMs (futuro)
   - ✓ Imagens de alta qualidade profissional

4. **Geração Condicional - Casual Shoes**:
   - Condicionamento por: cor, gênero, marca
   - Controle de estilo: esportivo vs casual formal
   - Variação de materiais: couro, canvas, sintético
   - Ângulos e poses consistentes

---

## 1.4 Especificações de Hardware e Estratégia de Treinamento Local

### 1.4.1 Hardware Disponível
**Sistema**: Mac Studio (2023)
- **Processador**: Apple M2 Max
- **Memória**: 32 GB RAM unificada (compartilhada entre CPU e GPU)
- **GPU**: Integrada M2 Max (38-core)
- **Backend**: PyTorch com Metal Performance Shaders (MPS)

**Capacidades de Treinamento**:
- ✓ Fine-tuning de modelos até ~13B parâmetros (com quantização)
- ✓ Stable Diffusion XL e SD 1.5 com LoRA
- ✓ Batch sizes modestos (2-8 dependendo do modelo)
- ✓ Mixed precision training (fp16/bf16)
- ⚠️ Memória compartilhada: ~20-24GB disponíveis para modelos após overhead do sistema

### 1.4.2 Modelos Otimizados para Apple Silicon

#### Geração de Imagens - Stable Diffusion com LoRA
**Modelo Recomendado**: Stable Diffusion 1.5 ou SDXL com LoRA fine-tuning

**Justificativa**:
- SD 1.5: ~4GB VRAM, treina bem em M2 Max
- SDXL: ~8-10GB VRAM com optimizações, melhor qualidade
- LoRA reduz memória de treinamento em 90%
- Suporte nativo MPS no PyTorch 2.0+

**Configuração de Treinamento**:
```python
# Stable Diffusion 1.5 + LoRA
Model: runwayml/stable-diffusion-v1-5
LoRA rank: 8-16 (menor = menos memória)
Learning rate: 1e-4
Batch size: 2-4 (com gradient accumulation)
Resolution: 512x512
Training steps: 3000-5000
Mixed precision: fp16 (MPS)

# Otimizações M2 Max
- Use torch.mps.empty_cache() entre epochs
- Gradient checkpointing: True
- Gradient accumulation: 4-8 steps
- CPU offload para componentes não críticos
```

**Estimativa de Tempo**:
- ~2-4 horas para 3000 steps (categoria Tshirts ~6200 imagens)
- ~6-10 horas para fine-tuning completo de uma categoria

#### Geração de Texto - LLMs Locais
**Modelos Recomendados**:

1. **Mistral 7B** (Recomendado para MVP)
   - Tamanho: ~14GB (fp16), ~7GB (4-bit quantizado)
   - Qualidade: Excelente para descrições de produtos
   - Velocidade: ~20-30 tokens/seg em M2 Max
   - Fine-tuning: LoRA ou QLoRA (4-bit)

2. **Llama 3.1 8B**
   - Tamanho: ~16GB (fp16), ~8GB (4-bit)
   - Qualidade: Superior para textos longos
   - Licença: Permissiva para uso comercial

3. **Phi-3 Mini 3.8B** (Alternativa leve)
   - Tamanho: ~7.5GB (fp16)
   - Velocidade: Mais rápido que Mistral
   - Qualidade: Boa para textos curtos

**Configuração de Fine-tuning (QLoRA)**:
```python
# Mistral 7B com QLoRA
Base model: mistralai/Mistral-7B-v0.1
Quantization: 4-bit (bitsandbytes)
LoRA config:
  - r: 16
  - lora_alpha: 32
  - lora_dropout: 0.05
  - target_modules: ["q_proj", "v_proj"]

Training params:
  - Batch size: 4 (per device)
  - Gradient accumulation: 4
  - Learning rate: 2e-4
  - Epochs: 3-5
  - Max seq length: 512 tokens
  - Optimizer: paged_adamw_8bit

Memory usage: ~12-16GB (cabe no M2 Max)
```

**Estimativa de Tempo**:
- ~4-6 horas para fine-tuning completo do dataset
- ~8-12 horas com validação e experimentação

#### Embeddings e Modelos Auxiliares
**CLIP para Validação Multimodal**:
```python
# CLIP ViT-L/14 ou ViT-B/32
Model: openai/clip-vit-large-patch14
Memory: ~3GB
Inference: Rápida em M2 Max (~100 images/sec)
Uso: Validação de consistência imagem-texto
```

### 1.4.3 Estratégia de Treinamento Eficiente

#### Pipeline de Desenvolvimento Incremental

**Fase 1 - Prototipagem Rápida - CASUAL SHOES (1 semana)** [PRIORIDADE]:
1. Analisar subset Casual Shoes (~2,845 imagens)
2. Testar SD 1.5 + LoRA com 300-500 imagens
3. Validar pipeline de treinamento MPS
4. Ajustar hiperparâmetros para M2 Max
5. Target: FID < 80, tempo de geração < 10s/imagem

**Fase 2 - Fine-tuning Casual Shoes Completo (2 semanas)** [PRIORIDADE]:
1. Treinar SD 1.5 + LoRA em Casual Shoes completo (~2,845 imagens)
2. Gerar dataset expandido (3,000-5,000 imagens sintéticas)
3. Integrar CLIP para validação de qualidade
4. Target: FID < 50, CLIP score > 0.25

**Fase 3 - Validação e Refinamento (1 semana)** [PRIORIDADE]:
1. Métricas de qualidade (FID, IS, CLIP score)
2. Análise visual manual (sample aleatório)
3. Comparação com imagens reais
4. Iteração e ajuste fino

**Fase 4 - FUTURO - Expansão Multi-Categoria (postponed)**:
1. Repetir processo para Tshirts, Shirts
2. Fine-tune Mistral 7B para descrições (postponed)
3. Sistema multi-categoria (postponed)

#### Otimizações Específicas para M2 Max

**PyTorch MPS Backend**:
```python
# Configuração otimizada
import torch

# Verificar disponibilidade MPS
assert torch.backends.mps.is_available()

# Device setup
device = torch.device("mps")

# Otimizações
torch.mps.set_per_process_memory_fraction(0.8)  # Reservar 80% da RAM
torch.backends.mps.allow_tf32 = True

# Durante treinamento
if epoch % 5 == 0:
    torch.mps.empty_cache()  # Limpar cache periodicamente
```

**Gradient Checkpointing**:
```python
# Reduzir uso de memória em 40-50%
model.enable_gradient_checkpointing()
```

**Mixed Precision Training**:
```python
# Acelerar treinamento em 2x
from torch.amp import autocast, GradScaler

scaler = GradScaler()
with autocast(device_type='mps'):
    outputs = model(inputs)
    loss = criterion(outputs, targets)
scaler.scale(loss).backward()
```

### 1.4.4 Limitações e Mitigações

**Limitações Identificadas**:
1. **Batch Size Reduzido**:
   - Limitação: 2-4 imagens por batch vs 8-16 em GPUs dedicadas
   - Mitigação: Gradient accumulation (simular batches maiores)

2. **Velocidade de Treinamento**:
   - Limitação: ~2-3x mais lento que GPU NVIDIA A100
   - Mitigação: Treinar overnight, usar checkpoints

3. **Modelos Muito Grandes**:
   - Limitação: Modelos 30B+ não cabem na memória
   - Mitigação: Focar em modelos 7B-13B com quantização

4. **Precisão Numérica**:
   - Limitação: MPS ainda tem algumas limitações vs CUDA
   - Mitigação: Testar convergência, usar fp32 se necessário

**Alternativas Cloud (Opcional)**:
- Google Colab Pro (GPU T4/A100): Para experimentos rápidos
- Lambda Labs / RunPod: Para treinamento de longa duração
- Manter M2 Max para: Inference, validação, protótipos

### 1.4.5 Benchmarks Esperados no M2 Max

**Stable Diffusion 1.5 + LoRA**:
- Inferência: ~4-6 segundos/imagem (512x512, 25 steps)
- Treinamento: ~2.5s/step (batch=2, grad_accum=4)
- 3000 steps: ~2-3 horas

**SDXL + LoRA**:
- Inferência: ~12-15 segundos/imagem (1024x1024, 25 steps)
- Treinamento: ~6-8s/step (batch=1, grad_accum=8)
- 3000 steps: ~6-8 horas

**Mistral 7B (QLoRA)**:
- Inferência: ~20 tokens/segundo
- Treinamento: ~3-4s/step (batch=4, grad_accum=4)
- 1 epoch (~11K steps): ~10-12 horas

---

## 2. Fases do Projeto

### Fase 1: Exploração e Preparação de Dados (2-3 semanas)
**STATUS**: ✅ EDA Inicial Concluída | 🔄 Pré-processamento Pendente

#### 2.1 Análise Exploratória de Dados (EDA) ✅ CONCLUÍDA
**Objetivo**: Compreender profundamente a estrutura e distribuição dos dados

**Status de Implementação**:
- ✅ Scripts de análise criados (`shoes-tranning/exploratory/scripts/`)
- ✅ Notebook interativo criado (`01_initial_eda.ipynb`)
- ✅ Análise documentada (ver seção 1.3)

**Tarefas Realizadas**:
1. **✅ Análise de Imagens**
   - ✓ Distribuição de resoluções e aspectos analisada
   - ✓ Características visuais documentadas
   - ✓ Qualidade e consistência verificadas
   - ✓ Identificadas variações de resolução (não padronizadas)
   - **Script**: `image_analysis.py`

2. **✅ Análise de Metadados (styles.csv + JSON)**
   - ✓ Distribuição completa de categorias documentada
   - ✓ 44,446 produtos analisados
   - ✓ Padrões e correlações identificados
   - ✓ Valores faltantes: negligíveis (<0.01%)
   - **Scripts**: `data_summary.py`, `json_metadata_analysis.py`

3. **✅ Análise de Texto**
   - ✓ Comprimento médio de descrições: 15-50 palavras
   - ✓ Estrutura HTML identificada (requer limpeza)
   - ✓ 3 tipos de descrições: description, style_note, materials_care_desc
   - ✓ Vocabulário rico e específico por categoria

**Entregáveis Completados**:
- ✅ Notebook de EDA com visualizações (`01_initial_eda.ipynb`)
- ✅ Relatórios de estatísticas descritivas (outputs/)
- ✅ Visualizações geradas (figures/)
- ✅ Dicionário de dados documentado (ver seção 1.3)
- ✅ README com instruções de uso

**Insights-Chave Obtidos**:
- Dataset de alta qualidade com imagens profissionais
- Top 10 categorias cobrem 57% do dataset
- Tshirts é a categoria ideal para MVP (~6,200 exemplos)
- Metadados ricos permitem condicionamento multi-atributo
- Fundo limpo/branco ideal para modelos generativos

#### 2.2 Pré-processamento
**Objetivo**: Preparar dados para treinamento

**Tarefas**:
1. **Processamento de Imagens**
   ```python
   # Pipeline de preprocessamento
   - Redimensionamento padronizado (256x256, 512x512)
   - Normalização de valores de pixel
   - Augmentação de dados (rotação, flip, crop)
   - Remoção de background (opcional, usando segmentação)
   - Criação de embeddings visuais (CLIP, ResNet)
   ```

2. **Processamento de Texto**
   ```python
   # Pipeline de NLP
   - Limpeza e normalização
   - Tokenização
   - Remoção de stop words (opcional)
   - Criação de embeddings (BERT, GPT)
   ```

3. **Estruturação de Metadados**
   ```python
   # Codificação de categorias
   - Label encoding para categorias hierárquicas
   - One-hot encoding para atributos
   - Normalização de valores numéricos (preço, ano)
   ```

**Entregáveis**:
- Scripts de preprocessamento reutilizáveis
- Datasets processados e versionados
- Documentação de transformações aplicadas

---

### Fase 2: Desenvolvimento de Modelos Base (4-6 semanas)
**FOCO**: Modelos otimizados para Apple M2 Max (Ver seção 1.4)

#### 2.1 Modelo de Geração de Imagens
**Abordagem**: Stable Diffusion 1.5/SDXL com LoRA (Hardware-Optimized)

##### Implementação Principal: SD 1.5 + LoRA (Recomendada para M2 Max)
**Justificativa**:
- Roda nativamente em M2 Max com PyTorch MPS
- LoRA reduz requisitos de memória em 90%
- Treinamento viável em 2-4 horas por categoria
- Qualidade comprovada para produtos de moda

**Arquitetura Otimizada para M2 Max**:
```python
# Configuração específica para Apple Silicon
Base Model: runwayml/stable-diffusion-v1-5
Fine-tuning Method: LoRA (Low-Rank Adaptation)
LoRA Config:
  - rank: 8-16 (8 para menor memória, 16 para melhor qualidade)
  - alpha: 16-32
  - target_modules: ["to_k", "to_q", "to_v", "to_out.0"]

# Condicionamento
Inputs:
  - Categoria: "Tshirt", "Casual Shoes", etc.
  - Atributos: cor, estação, gênero
  - Prompt: "A professional product photo of [articleType] in [color], [season] collection, white background"

Output:
  - Imagem 512x512 (SD 1.5)
  - Tempo: 4-6 segundos/imagem
```

**Processo de Treinamento M2 Max-Optimized**:

1. **Setup do Ambiente**:
   ```bash
   # Instalar dependências otimizadas
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
   pip install diffusers transformers accelerate
   pip install peft bitsandbytes  # Para LoRA

   # Verificar MPS
   python -c "import torch; print(torch.backends.mps.is_available())"
   ```

2. **Preparação de Dados**:
   - Redimensionar imagens para 512x512
   - Criar captions estruturados:
     ```
     "A professional product photo of [Navy Blue Tshirt], Summer collection,
      [Men's casual wear], centered on white background"
     ```
   - Dataset mínimo: 500-1000 imagens para protótipo
   - Dataset completo: 6200 imagens (Tshirts) para modelo final

3. **Configuração de Treinamento**:
   ```python
   # Parâmetros otimizados para M2 Max (32GB RAM)
   training_args = {
       "learning_rate": 1e-4,
       "batch_size": 2,  # Pequeno devido à memória
       "gradient_accumulation_steps": 8,  # Simula batch=16
       "num_train_epochs": 10,
       "mixed_precision": "fp16",  # MPS suporta fp16
       "gradient_checkpointing": True,  # Economiza 40% memória
       "save_steps": 500,
       "eval_steps": 500,
       "logging_steps": 100,
   }

   # Otimizações de memória
   - torch.mps.empty_cache() a cada 5 epochs
   - Usar xformers ou attention slicing para reduzir memória
   - CPU offloading para CLIP text encoder (opcional)
   ```

4. **Técnicas Avançadas (Fase 2.5)**:
   - **ControlNet** (opcional): Manter estrutura/pose consistente
   - **Multiple LoRAs**: Um LoRA por categoria top-5
   - **Textual Inversion**: Aprender tokens específicos de produtos

**Estimativas de Performance - Casual Shoes**:
- Análise e preparação de dados: ~2-3 horas
- Treinamento protótipo (300-500 imgs): ~1-1.5 horas
- Treinamento completo (2,845 imgs): ~1.5-2.5 horas
- Geração de 1000 imagens sintéticas: ~1.5-2 horas
- Inferência: 4-6 segundos por imagem
- Memória: ~8-12GB durante treinamento

##### Opção B: StyleGAN3 (Alternativa)
**Justificativa**: Excelente para produtos com fundo limpo

**Implementação**:
```python
# Configuração
Arquitetura: StyleGAN3-T ou StyleGAN3-R
Resolução: 512x512
Conditional: Usar label conditioning ou projection

# Latent space manipulation
- Disentangled representations para atributos
- Style mixing entre categorias
```

##### Opção C: DALL-E/Imagen via API (Baseline)
**Justificativa**: Validação rápida sem treinamento

**Uso**:
- Gerar baseline para comparação
- Avaliar qualidade alcançável
- Testar engineering de prompts

#### 2.2 Modelo de Geração de Texto
**Abordagem**: LLM Local com QLoRA (M2 Max Optimized)

##### Implementação Recomendada: Mistral 7B com QLoRA

**Justificativa**:
- Roda localmente em M2 Max (32GB)
- QLoRA reduz uso de memória em 75%
- Qualidade superior para textos de produtos
- Fine-tuning completo em 4-6 horas

**Arquitetura Otimizada para M2 Max**:
```python
# Modelo base
Base: mistralai/Mistral-7B-Instruct-v0.2
Quantization: 4-bit (bitsandbytes)
Method: QLoRA (Quantized Low-Rank Adaptation)

# LoRA Config
LoRA parameters:
  - r: 16 (rank)
  - lora_alpha: 32
  - lora_dropout: 0.05
  - target_modules: ["q_proj", "v_proj", "k_proj", "o_proj"]
  - bias: "none"

# Input format (condicionamento estruturado)
<s>[INST] Generate a product description for:
- Category: Apparel > Topwear > Tshirts
- Color: Navy Blue
- Season: Summer
- Gender: Men
- Brand: Nike
- Additional: Casual, Cotton fabric
[/INST]

# Output esperado
Descrição natural, atraente e informativa (50-150 palavras)
```

**Processo de Fine-tuning M2 Max-Optimized**:

1. **Setup do Ambiente**:
   ```bash
   # Instalar dependências
   pip install transformers accelerate peft bitsandbytes
   pip install datasets trl  # Para SFTTrainer

   # Verificar disponibilidade
   python -c "import torch; print(torch.backends.mps.is_available())"
   ```

2. **Preparação do Dataset**:
   - Extrair descrições do dataset (44,424 produtos)
   - Limpar HTML tags das descrições
   - Formato instruction-following:
     ```python
     # Template de treinamento
     prompt_template = """<s>[INST] Generate a product description for:
     - Category: {masterCategory} > {subCategory} > {articleType}
     - Color: {baseColour}
     - Season: {season}
     - Gender: {gender}
     - Brand: {brandName}
     - Additional: {usage}, {fabric}
     [/INST]
     {productDescription}</s>"""
     ```
   - Split: 70% treino (31K), 15% val (6.6K), 15% teste (6.6K)

3. **Configuração de Treinamento**:
   ```python
   # Parâmetros otimizados para M2 Max
   from transformers import TrainingArguments

   training_args = TrainingArguments(
       output_dir="./mistral-7b-fashion-qlora",
       num_train_epochs=3,
       per_device_train_batch_size=4,
       gradient_accumulation_steps=4,  # Batch efetivo = 16
       learning_rate=2e-4,
       fp16=False,  # MPS ainda tem issues com fp16 em alguns casos
       bf16=False,
       max_grad_norm=0.3,
       warmup_ratio=0.03,
       lr_scheduler_type="cosine",
       save_strategy="epoch",
       logging_steps=10,
       optim="paged_adamw_8bit",  # Otimizador eficiente
   )

   # QLoRA config
   from peft import LoraConfig

   peft_config = LoraConfig(
       r=16,
       lora_alpha=32,
       lora_dropout=0.05,
       bias="none",
       task_type="CAUSAL_LM",
       target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
   )

   # Quantização 4-bit
   from transformers import BitsAndBytesConfig

   bnb_config = BitsAndBytesConfig(
       load_in_4bit=True,
       bnb_4bit_quant_type="nf4",
       bnb_4bit_compute_dtype=torch.float16,
       bnb_4bit_use_double_quant=True,
   )
   ```

4. **Treinamento**:
   ```python
   from trl import SFTTrainer

   trainer = SFTTrainer(
       model=model,
       train_dataset=train_dataset,
       eval_dataset=val_dataset,
       peft_config=peft_config,
       args=training_args,
       max_seq_length=512,
   )

   # Treinar
   trainer.train()

   # Salvar apenas adaptadores LoRA (~100MB vs 14GB do modelo completo)
   trainer.model.save_pretrained("./fashion-lora-adapter")
   ```

5. **Técnicas de Qualidade**:
   - **Temperature**: 0.7-0.9 (maior = mais criativo)
   - **Top-p sampling**: 0.9 (nucleus sampling)
   - **Repetition penalty**: 1.1
   - **Max length**: 150-200 tokens
   - **Validation**: CLIP score para consistência imagem-texto

**Estimativas de Performance M2 Max**:
- Treinamento (3 epochs): ~4-6 horas
- Inferência: ~20-30 tokens/segundo (~5-8 segundos/descrição)
- Memória durante treino: ~14-18GB
- Memória durante inferência: ~8-10GB
- Tamanho do LoRA adapter: ~100-200MB

**Alternativa Mais Leve**: Phi-3 Mini 3.8B
- Treinamento: ~2-3 horas
- Inferência: ~40-50 tokens/segundo
- Memória: ~8GB
- Qualidade: Boa para descrições curtas (<100 palavras)

#### 2.3 Modelo de Geração de Metadados
**Abordagem**: VAE ou Normalizing Flows para atributos consistentes

**Implementação**:
```python
# Arquitetura VAE
Encoder: Metadados existentes → latent space
Decoder: Latent space → metadados novos

# Constraints
- Garantir combinações válidas (ex: "Winter Sandals" é raro)
- Aprender distribuições condicionais P(atributos|categoria)
- Usar regras de negócio quando necessário
```

**Validação**:
- Verificar consistência lógica (ex: cor branca não deve ter descrição "dark tone")
- Checar completude dos campos obrigatórios
- Validar contra schema JSON

---

### Fase 3: Sistema Multimodal Integrado (3-4 semanas)

#### 3.1 Pipeline de Geração Coordenada
**Objetivo**: Garantir coerência entre imagem, texto e metadados

**Arquitetura do Sistema**:
```
1. Geração de Metadados Base
   ↓
2. Geração de Imagem (condicionada em metadados)
   ↓
3. Geração de Descrição (condicionada em metadados + imagem)
   ↓
4. Validação de Consistência Multimodal
```

**Componente de Validação**:
```python
# CLIP-based consistency checker
- Calcular similaridade CLIP(imagem, descrição)
- Threshold mínimo: 0.25-0.30
- Rejeitar ou regenerar se abaixo do threshold

# Attribute verification
- Usar modelo de classificação para verificar atributos na imagem
- Comparar com metadados gerados
```

#### 3.2 Interface de Geração
**Componentes**:
1. **API REST**:
   ```python
   POST /generate/product
   {
     "category": "Shoes",
     "subcategory": "Casual",
     "constraints": {
       "color": "optional",
       "season": "optional"
     },
     "num_samples": 5
   }
   ```

2. **Batch Generation**:
   - Gerar múltiplos produtos em paralelo
   - Controle de diversidade
   - Export para formato do dataset original

3. **Interactive Web UI**:
   - Gradio ou Streamlit
   - Controles para ajuste de parâmetros
   - Visualização de resultados

---

### Fase 4: Avaliação e Refinamento (2-3 semanas)

#### 4.1 Métricas de Qualidade

##### Métricas para Imagens
1. **Qualidade Visual**:
   - FID (Fréchet Inception Distance): < 50 (bom), < 30 (excelente)
   - IS (Inception Score): > 5 (bom)
   - LPIPS (perceptual similarity) para diversidade

2. **Consistência com Categoria**:
   - Accuracy de classificador treinado: > 85%
   - Usar modelo pré-treinado (ResNet, EfficientNet)

3. **Avaliação Humana**:
   - Realismo (escala 1-5)
   - Adequação à categoria
   - Qualidade profissional

##### Métricas para Texto
1. **Qualidade Linguística**:
   - Perplexity: < 30
   - BLEU score vs. descrições reais: > 0.3
   - ROUGE scores

2. **Consistência Factual**:
   - Verificar menção de atributos corretos
   - Detecção de alucinações

3. **Diversidade**:
   - Self-BLEU (deve ser baixo)
   - Unique n-grams ratio

##### Métricas Multimodais
1. **CLIP Score**: > 0.25
2. **Image-Text Matching Accuracy**: > 80%
3. **Attribute Consistency Rate**: > 90%

#### 4.2 Estratégias de Refinamento
1. **Iterative Feedback Loop**:
   - Identificar casos de falha
   - Adicionar ao dataset de fine-tuning
   - Re-treinar com ênfase em casos difíceis

2. **Ensemble de Modelos**:
   - Combinar outputs de múltiplos geradores
   - Seleção baseada em métricas de qualidade

3. **Human-in-the-Loop**:
   - Curadoria de melhores samples
   - Feedback para melhoria contínua

---

### Fase 5: Aplicações e Deployment (2 semanas)

#### 5.1 Casos de Uso
1. **Data Augmentation**:
   - Balancear categorias sub-representadas
   - Criar variações de produtos existentes

2. **Prototyping de Produtos**:
   - Visualizar novos designs rapidamente
   - Testar conceitos antes de produção

3. **Dataset Sintético para Treinamento**:
   - Treinar modelos de classificação
   - Sistemas de busca visual
   - Sistemas de recomendação

#### 5.2 Deployment
```python
# Stack recomendada
Backend: FastAPI
Model Serving: TorchServe ou NVIDIA Triton
Storage: S3/MinIO para imagens geradas
Database: PostgreSQL para metadados
Queue: Celery + Redis para processamento assíncrono
```

**Otimizações**:
- Model quantization (INT8)
- Batching de requisições
- Caching de gerações comuns
- GPU sharing com vLLM ou TensorRT

---

## 3. Cronograma Estimado

| Fase | Duração | Semanas Acumuladas |
|------|---------|-------------------|
| Fase 1: Exploração e Preparação | 2-3 semanas | 3 |
| Fase 2: Desenvolvimento de Modelos | 4-6 semanas | 9 |
| Fase 3: Sistema Multimodal | 3-4 semanas | 13 |
| Fase 4: Avaliação e Refinamento | 2-3 semanas | 16 |
| Fase 5: Aplicações e Deployment | 2 semanas | 18 |

**Total: 18-20 semanas (4-5 meses)**

---

## 4. Recursos Necessários

### 4.1 Infraestrutura Computacional
**GPU Requirements**:
- Mínimo: 1x GPU com 16GB VRAM (RTX 3090/4090, A4000)
- Recomendado: 1x GPU com 24GB+ VRAM (A5000, A6000, RTX 6000)
- Ideal: 2-4x GPUs para treinamento distribuído

**Alternativas Cloud**:
- Google Colab Pro/Pro+ (budget-friendly para experimentação)
- Lambda Labs, RunPod, Vast.ai (GPUs dedicadas)
- AWS/GCP/Azure (produção)

### 4.2 Software e Bibliotecas
```python
# Deep Learning
- PyTorch >= 2.0
- Diffusers (Hugging Face)
- Transformers (Hugging Face)
- PEFT (LoRA, QLoRA)

# Visão Computacional
- OpenCV
- Pillow
- CLIP (OpenAI)
- torchvision

# NLP
- spaCy ou NLTK
- sentence-transformers

# Avaliação
- pytorch-fid
- lpips
- torchmetrics

# MLOps
- Weights & Biases ou MLflow
- DVC para versionamento de dados
```

### 4.3 Datasets e Modelos Pré-treinados
**Para Download**:
- Fashion Product Images Dataset (Kaggle)
- Stable Diffusion weights (Hugging Face)
- LLaMA 2 ou Mistral weights
- CLIP models (OpenAI)

**Estimativa de Storage**:
- Dataset original: ~15GB (completo) ou 280MB (small)
- Modelos pré-treinados: ~20-40GB
- Modelos fine-tuned: ~10-20GB
- Dados processados e cache: ~30-50GB
- **Total: ~100GB mínimo**

---

## 5. Riscos e Mitigações

### 5.1 Riscos Técnicos
| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Qualidade de imagens sintéticas insuficiente | Média | Alto | - Testar múltiplas arquiteturas<br>- Usar modelos estado da arte<br>- Ajustar hyperparâmetros extensivamente |
| Inconsistência multimodal | Alta | Médio | - Implementar validação rigorosa<br>- Usar condicionamento forte<br>- Pipeline de geração coordenada |
| Overfitting no dataset pequeno | Média | Médio | - Data augmentation<br>- Regularização<br>- Early stopping |
| Limitação computacional | Baixa | Alto | - Usar modelos menores (LoRA)<br>- Cloud GPU on-demand<br>- Gradient accumulation |

### 5.2 Riscos de Projeto
| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Escopo excessivo | Média | Alto | - MVP com features essenciais<br>- Desenvolvimento iterativo<br>- Priorização clara |
| Falta de dados de validação | Baixa | Médio | - Usar held-out set do dataset original<br>- Métricas objetivas complementadas por avaliação humana |

---

## 6. Critérios de Sucesso

### 6.1 Critérios Mínimos (MVP)
- [ ] Gerar imagens de produtos reconhecíveis em 3+ categorias principais
- [ ] FID < 80 para cada categoria
- [ ] Gerar descrições coerentes com metadados (verificação manual de 100 samples)
- [ ] Pipeline end-to-end funcional

### 6.2 Critérios Alvo
- [ ] FID < 50 em todas as categorias
- [ ] CLIP score > 0.25 para pares (imagem, descrição)
- [ ] Classificador identifica categoria correta em >85% das imagens sintéticas
- [ ] Avaliação humana: realismo médio > 3.5/5
- [ ] API de geração com latência < 30s por produto

### 6.3 Critérios Excelência
- [ ] FID < 30 (próximo de dataset real)
- [ ] Sistema capaz de gerar 1000+ produtos únicos e realistas
- [ ] Integração com sistema de e-commerce real
- [ ] Detecção de bias e fairness implementada
- [ ] Documentação completa e código reproduzível

---

## 7. Referências e Recursos de Aprendizagem

### 7.1 Papers Fundamentais
1. **Image Generation**:
   - "Denoising Diffusion Probabilistic Models" (Ho et al., 2020)
   - "High-Resolution Image Synthesis with Latent Diffusion Models" (Rombach et al., 2022)
   - "StyleGAN3" (Karras et al., 2021)

2. **Text Generation**:
   - "Language Models are Few-Shot Learners" (GPT-3, Brown et al., 2020)
   - "LoRA: Low-Rank Adaptation of Large Language Models" (Hu et al., 2021)

3. **Multimodal**:
   - "Learning Transferable Visual Models From Natural Language Supervision" (CLIP, Radford et al., 2021)
   - "Flamingo: a Visual Language Model for Few-Shot Learning" (Alayrac et al., 2022)

### 7.2 Tutoriais e Cursos
- Hugging Face Diffusion Models Course
- Fast.ai Deep Learning for Coders
- Stanford CS231n (Computer Vision)
- Stanford CS224n (NLP)

### 7.3 Ferramentas e Frameworks
- [Diffusers Documentation](https://huggingface.co/docs/diffusers)
- [PEFT Library](https://github.com/huggingface/peft)
- [Stable Diffusion Fine-tuning Guide](https://huggingface.co/docs/diffusers/training/overview)

---

## 8. Próximos Passos Imediatos

1. **Setup do Ambiente** (Semana 1):
   ```bash
   # Criar ambiente virtual
   python -m venv venv
   source venv/bin/activate

   # Instalar dependências base
   pip install torch torchvision diffusers transformers
   pip install pandas numpy matplotlib seaborn
   pip install jupyter notebook
   ```

2. **Download do Dataset** (Semana 1):
   - Baixar dataset do Kaggle
   - Organizar estrutura de pastas
   - Verificar integridade dos arquivos

3. **EDA Inicial** (Semana 1-2):
   - Notebook explorando imagens
   - Análise de distribuição de categorias
   - Estatísticas de metadados

4. **Baseline Model** (Semana 2-3):
   - Implementar classificador simples (para avaliação posterior)
   - Testar geração com modelo pré-treinado (sem fine-tuning)
   - Estabelecer métricas baseline

---

## 9. Estrutura de Código Sugerida

```
shoes-training/
├── data/
│   ├── raw/                    # Dataset original
│   ├── processed/              # Dados pré-processados
│   └── synthetic/              # Dados sintéticos gerados
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_baseline_models.ipynb
│   └── 04_evaluation.ipynb
├── src/
│   ├── data/
│   │   ├── preprocessing.py
│   │   └── dataset.py
│   ├── models/
│   │   ├── image_generator.py
│   │   ├── text_generator.py
│   │   └── metadata_generator.py
│   ├── training/
│   │   ├── train_diffusion.py
│   │   ├── train_llm.py
│   │   └── utils.py
│   ├── evaluation/
│   │   ├── metrics.py
│   │   └── validators.py
│   └── api/
│       ├── main.py
│       └── generation_pipeline.py
├── configs/
│   ├── diffusion_config.yaml
│   └── llm_config.yaml
├── tests/
├── requirements.txt
├── README.md
└── planning.md               # Este documento
```

---

## 10. Considerações Finais para Aprendizagem

### 10.1 Conceitos-Chave a Dominar
1. **Fundamentos de Deep Learning**:
   - Backpropagation e otimização (Adam, AdamW)
   - Regularização (dropout, weight decay)
   - Transfer learning e fine-tuning

2. **Modelos Generativos**:
   - GANs: conceito de gerador vs. discriminador
   - VAEs: latent space e reconstrução
   - Diffusion Models: processo de noising e denoising
   - Condicionamento e controle

3. **NLP Moderno**:
   - Transformers e atenção
   - Tokenização e embeddings
   - Fine-tuning eficiente (LoRA, adapters)

4. **Multimodalidade**:
   - Embeddings compartilhados (CLIP)
   - Cross-modal retrieval
   - Consistência entre modalidades

### 10.2 Abordagem Pedagógica Recomendada
1. **Começar Simples**:
   - Implementar classificador de imagens primeiro
   - Entender o dataset profundamente
   - Usar modelos pequenos para experimentação rápida

2. **Progressão Gradual**:
   - Baseline → Fine-tuning → Custom Architectures
   - Single modality → Multimodal integration
   - Métodos supervisionados → Generative models

3. **Experimentação Ativa**:
   - Testar hipóteses com experimentos controlados
   - Manter log detalhado de resultados (W&B)
   - Analisar falhas para aprendizado

4. **Documentação Contínua**:
   - Comentar código extensivamente
   - Criar notebooks explicativos
   - Escrever relatórios de progresso semanais

---

**Última Atualização**: 2025-10-26
**Versão**: 1.0
**Autor**: Planejamento gerado para fins de aprendizagem e pesquisa acadêmica
