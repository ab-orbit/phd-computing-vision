# Shoes AI Generator

## Pipeline de Treinamento e Geração de Imagens de Sapatos usando LoRA + Stable Diffusion

![API Interface](execution_evidences/api.png)
![App Interface](execution_evidences/app.png)

Sistema completo para treinamento de modelos LoRA especializados em geração de imagens fotorealistas de sapatos casuais. Inclui pipeline de treinamento otimizado para Apple Silicon, API REST para inferência, e interface web interativa.

---

## Índice

- [Visão Geral](#visão-geral)
- [Características Principais](#características-principais)
- [Arquitetura do Sistema](#arquitetura-do-sistema)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação e Setup](#instalação-e-setup)
- [Treinamento do Modelo](#treinamento-do-modelo)
- [API e Inferência](#api-e-inferência)
- [Interface Web](#interface-web)
- [Scripts Disponíveis](#scripts-disponíveis)
- [Exemplos Visuais](#exemplos-visuais)
- [Documentação Técnica](#documentação-técnica)
- [Performance e Requisitos](#performance-e-requisitos)
- [Roadmap e Futuras Melhorias](#roadmap-e-futuras-melhorias)
- [Licença e Contato](#licença-e-contato)

---

## Visão Geral

Este projeto implementa um pipeline completo de fine-tuning do Stable Diffusion 1.5 usando técnica LoRA (Low-Rank Adaptation) para gerar imagens de alta qualidade de sapatos casuais no estilo de fotografia de produto profissional.

### Objetivo

Criar um sistema capaz de gerar imagens fotorealistas de sapatos casuais com:
- Fundo branco profissional
- Iluminação consistente
- Enquadramento de produto padronizado
- Controle preciso via prompts textuais
- Alta fidelidade a cores e materiais

### Tecnologia Base

- **Modelo Base**: Stable Diffusion v1.5 (runwayml/stable-diffusion-v1-5)
- **Técnica de Fine-tuning**: LoRA (Low-Rank Adaptation)
- **Framework**: PyTorch + Diffusers + PEFT + Accelerate
- **Otimização**: Apple Silicon (MPS backend)
- **Dataset**: 1,991 imagens de sapatos casuais (512x512)

---

## Características Principais

### Pipeline de Treinamento

- **Eficiência de Memória**: LoRA treina apenas 0.19% dos parâmetros (1.6M de 861M)
- **Treinamento Incremental**: Checkpoints automáticos a cada 500 steps
- **Validação Contínua**: Geração de imagens de teste durante treinamento
- **Otimizado para Apple Silicon**: Gradient checkpointing, float32, MPS backend
- **Reprodutibilidade**: Seeds fixos e estados aleatórios salvos

### API REST

- **FastAPI**: API moderna e rápida com documentação automática (OpenAPI/Swagger)
- **Endpoints**:
  - `POST /api/generate`: Gera imagens a partir de prompts
  - `GET /api/models`: Lista modelos e checkpoints disponíveis
  - `GET /api/health`: Status e diagnóstico do sistema
- **Geração em Lote**: Suporte para múltiplas imagens por request
- **Hot-swap de Modelos**: Troca dinâmica entre checkpoints sem restart

### Interface Web

- **React + TypeScript**: Interface moderna e responsiva
- **Visualização em Tempo Real**: Preview das imagens geradas
- **Controle Fino**: Ajuste de parâmetros (steps, guidance scale, seed)
- **Galeria**: Histórico de gerações com metadata
- **Download Individual ou em Lote**: Exportação das imagens geradas

---

## Arquitetura do Sistema

```
┌──────────────────────────────────────────────────────────────────┐
│                        SHOES AI GENERATOR                         │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────┐      ┌─────────────────┐      ┌──────────────┐
│   TRAINING      │      │   INFERENCE     │      │   FRONTEND   │
│   PIPELINE      │─────▶│   API (FastAPI) │◀─────│   (React)    │
└─────────────────┘      └─────────────────┘      └──────────────┘
        │                         │                        │
        │                         │                        │
        ▼                         ▼                        ▼
┌─────────────────┐      ┌─────────────────┐      ┌──────────────┐
│  Dataset        │      │  LoRA Models    │      │  User        │
│  (1,991 imgs)   │      │  + Checkpoints  │      │  Interface   │
└─────────────────┘      └─────────────────┘      └──────────────┘
        │
        │
        ▼
┌─────────────────────────────────────────────────┐
│  Stable Diffusion 1.5 + LoRA                    │
│  - UNet (denoising)                              │
│  - VAE (encoding/decoding)                       │
│  - CLIP Text Encoder                             │
└─────────────────────────────────────────────────┘
```

### Fluxo de Dados

**Treinamento:**
```
Dataset → Preprocessing → LoRA Training → Checkpoints → Model Export
```

**Inferência:**
```
Text Prompt → API → Model Loading → Diffusion Process → Image Generation → Response
```

---

## Estrutura do Projeto

```
shoes-tranning/
├── api/                          # API REST para inferência
│   ├── main.py                   # FastAPI application
│   ├── start_api.sh              # Script de inicialização da API
│   ├── generate_batch.sh         # Geração em lote via CLI
│   └── generated_batch/          # Imagens geradas em lote
│
├── frontend/                     # Interface web React
│   ├── src/
│   │   ├── App.tsx              # Componente principal
│   │   ├── api.ts               # Cliente da API
│   │   └── types.ts             # Tipos TypeScript
│   ├── package.json
│   └── vite.config.ts
│
├── training/                     # Pipeline de treinamento
│   ├── scripts/
│   │   ├── train_lora.py                    # Script principal de treinamento
│   │   ├── convert_checkpoint_to_pipeline.py # Conversão de checkpoints
│   │   ├── convert_all_checkpoints.sh       # Conversão em lote
│   │   ├── resume_training.sh               # Retomar treinamento
│   │   ├── check_environment.py             # Verificação de setup
│   │   ├── test_training_setup.py           # Testes pré-treinamento
│   │   ├── test_sd_inference.py             # Testes de inferência
│   │   └── quick_test_checkpoint.sh         # Teste rápido de checkpoint
│   │
│   └── outputs/                 # Outputs do treinamento
│       └── lora_casual_shoes_3000steps_full/
│           ├── checkpoints/     # Checkpoints incrementais
│           ├── validation/      # Imagens de validação
│           ├── lora_weights/    # Pesos LoRA finais
│           └── final_pipeline/  # Pipeline completo
│
├── data/                        # Dataset
│   └── casual_shoes/
│       └── train/
│           ├── images/          # 1,991 imagens PNG (512x512)
│           └── captions.json    # Captions estruturados
│
├── execution_evidences/         # Evidências de execução
│   ├── gallery.md              # Galeria completa de resultados
│   ├── black/                  # Exemplos de sapatos pretos
│   ├── brown_lether/           # Exemplos de couro marrom
│   ├── grey/                   # Exemplos de sapatos cinza
│   ├── sculptural/             # Designs esculturais
│   └── watermelon/             # Tema melancia (experimento)
│
├── docs/                        # Documentação técnica
│   ├── PIPELINE_TREINAMENTO.md  # Documentação completa do pipeline
│   ├── API_REFERENCE.md         # Referência da API
│   └── TRAINING_GUIDE.md        # Guia de treinamento
│
├── exploratory/                 # Notebooks e experimentos
│   └── *.ipynb                 # Jupyter notebooks
│
├── README.md                    # Este arquivo
├── API_FRONTEND_README.md       # Documentação específica API/Frontend
└── requirements.txt             # Dependências Python
```

---

## Instalação e Setup

### Requisitos de Sistema

**Hardware:**
- Apple Silicon (M1/M2/M3) recomendado para treinamento
- 16 GB RAM mínimo (32 GB recomendado)
- 50 GB espaço em disco livre
- GPU com suporte MPS ou CUDA (opcional para inferência)

**Software:**
- Python 3.10+
- Node.js 18+ (para frontend)
- Git

### Instalação do Ambiente Python

```bash
# Clonar repositório
git clone <repository-url>
cd shoes-tranning

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Verificar instalação
python training/scripts/check_environment.py
```

### Instalação do Frontend

```bash
cd frontend
npm install
npm run dev
```

### Instalação da API

```bash
cd api
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn python-multipart pillow torch diffusers peft accelerate
```

---

## Treinamento do Modelo

### Preparação do Dataset

1. **Organizar Imagens**
   ```bash
   data/casual_shoes/train/images/
   ├── 100001.png
   ├── 100002.png
   └── ...
   ```

2. **Criar Captions**
   ```json
   [
     {
       "image_file": "100001.png",
       "caption": "A professional product photo of black casual shoes on white background, high quality, product photography"
     }
   ]
   ```

### Executar Treinamento

```bash
cd training/scripts

# Treinamento completo (3000 steps)
python train_lora.py \
  --pretrained_model_name_or_path="runwayml/stable-diffusion-v1-5" \
  --dataset_path="../../data/casual_shoes/train" \
  --output_dir="../outputs/lora_casual_shoes_3000steps_full" \
  --resolution=512 \
  --train_batch_size=2 \
  --gradient_accumulation_steps=8 \
  --learning_rate=1e-4 \
  --max_train_steps=3000 \
  --checkpointing_steps=500 \
  --validation_steps=500
```

### Monitoramento

```bash
# Seguir logs em tempo real
tail -f training/scripts/training_log_full.txt

# Ver progresso
watch -n 5 'ls -lh training/outputs/lora_casual_shoes_3000steps_full/checkpoints/'
```

### Retomar Treinamento Interrompido

```bash
cd training/scripts
./resume_training.sh checkpoint-2000
```

---

## API e Inferência

### Iniciar API

```bash
cd api
./start_api.sh
```

A API estará disponível em `http://localhost:8011`

Documentação interativa: `http://localhost:8011/docs`

### Endpoints Principais

#### 1. Gerar Imagens

```bash
curl -X POST "http://localhost:8011/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "lora_casual_shoes_3000steps_full/checkpoint-1500",
    "prompt": "A professional product photo of brown leather casual shoes on white background, high quality",
    "num_images": 4,
    "num_inference_steps": 50,
    "guidance_scale": 7.5,
    "seed": 42
  }'
```

**Resposta:**
```json
{
  "success": true,
  "images": [
    {
      "image": "<base64_encoded_image>",
      "seed": 42,
      "metadata": {
        "model": "checkpoint-1500",
        "steps": 50,
        "guidance_scale": 7.5
      }
    }
  ],
  "generation_time": 12.5
}
```

#### 2. Listar Modelos

```bash
curl "http://localhost:8011/api/models"
```

**Resposta:**
```json
{
  "models": [
    {
      "name": "lora_casual_shoes_3000steps_full/checkpoint-500",
      "path": "/path/to/checkpoint-500",
      "type": "checkpoint",
      "step": 500
    },
    {
      "name": "lora_casual_shoes_3000steps_full/checkpoint-1500",
      "path": "/path/to/checkpoint-1500",
      "type": "checkpoint",
      "step": 1500
    }
  ]
}
```

#### 3. Health Check

```bash
curl "http://localhost:8011/api/health"
```

### Geração em Lote via CLI

```bash
cd api

# Criar arquivo de prompts
cat > prompts.txt <<EOF
brown leather casual oxford shoes on white background
black formal shoes side view
white canvas sneakers top view
EOF

# Gerar 6 imagens por prompt
./generate_batch.sh prompts.txt 6 lora_casual_shoes_3000steps_full/checkpoint-1500

# Resultados salvos em: generated_batch/batch_YYYYMMDD_HHMMSS/
```

---

## Interface Web

### Iniciar Frontend

```bash
cd frontend
npm run dev
```

Acesse: `http://localhost:5173`

### Funcionalidades

1. **Geração de Imagens**
   - Campo de prompt com sugestões
   - Seleção de modelo/checkpoint
   - Controles de parâmetros:
     - Número de imagens (1-10)
     - Inference steps (25-100)
     - Guidance scale (5-15)
     - Seed (opcional)

2. **Visualização**
   - Grid responsivo de imagens
   - Zoom e preview
   - Metadata de cada geração

3. **Galeria**
   - Histórico de gerações
   - Filtro por modelo
   - Busca por prompt

4. **Download**
   - Download individual (PNG)
   - Download em lote (ZIP)
   - Exportar metadata (JSON)

---

## Scripts Disponíveis

### Scripts de Treinamento

| Script | Descrição | Uso |
|--------|-----------|-----|
| `train_lora.py` | Script principal de treinamento LoRA | `python train_lora.py [args]` |
| `resume_training.sh` | Retomar treinamento interrompido | `./resume_training.sh checkpoint-N` |
| `check_environment.py` | Verificar dependências e GPU | `python check_environment.py` |
| `test_training_setup.py` | Testar configuração antes de treinar | `python test_training_setup.py` |
| `test_sd_inference.py` | Testar inferência do modelo base | `python test_sd_inference.py` |

### Scripts de Conversão

| Script | Descrição | Uso |
|--------|-----------|-----|
| `convert_checkpoint_to_pipeline.py` | Converter checkpoint para pipeline | `python convert_checkpoint_to_pipeline.py [checkpoint]` |
| `convert_all_checkpoints.sh` | Converter todos os checkpoints | `./convert_all_checkpoints.sh` |
| `convert_peft_to_diffusers.py` | Converter formato PEFT para Diffusers | `python convert_peft_to_diffusers.py` |

### Scripts de Teste

| Script | Descrição | Uso |
|--------|-----------|-----|
| `test_checkpoint_loading.py` | Testar carregamento de checkpoint | `python test_checkpoint_loading.py [checkpoint]` |
| `quick_test_checkpoint.sh` | Teste rápido de geração | `./quick_test_checkpoint.sh checkpoint-N` |

### Scripts da API

| Script | Descrição | Uso |
|--------|-----------|-----|
| `start_api.sh` | Iniciar servidor FastAPI | `./start_api.sh` |
| `generate_batch.sh` | Geração em lote via CLI | `./generate_batch.sh prompts.txt N [model]` |

### Scripts Utilitários

| Script | Descrição | Uso |
|--------|-----------|-----|
| `move_to_external_drive.sh` | Mover outputs para drive externo | `./move_to_external_drive.sh` |
| `move_and_resume_training.sh` | Mover + retomar treinamento | `./move_and_resume_training.sh` |

---

## Exemplos Visuais

### Sapatos Pretos

Gerados com checkpoint-1500:

![Black Shoes 1](execution_evidences/black/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_221732_seed3898295219.png)
![Black Shoes 2](execution_evidences/black/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_221802_seed3898295220.png)

### Sapatos de Couro Marrom

Gerados com checkpoint-1500:

![Brown Leather 1](execution_evidences/brown_lether/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_230636_seed3101469424.png)
![Brown Leather 2](execution_evidences/brown_lether/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_230706_seed3101469425.png)

### Sapatos Cinza

Série de variações com checkpoint-1500:

![Grey Shoes 1](execution_evidences/grey/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_224720_seed2784716826.png)
![Grey Shoes 2](execution_evidences/grey/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_224754_seed2784716827.png)
![Grey Shoes 3](execution_evidences/grey/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_224824_seed2784716828.png)

### Designs Esculturais

Experimentação com designs mais artísticos:

![Sculptural 1](execution_evidences/sculptural/lora_casual_shoes_3000steps_full_checkpoint-1500_20251027_225552_seed974209925.png)
![Sculptural 2](execution_evidences/sculptural/lora_casual_shoes_3000steps_full_checkpoint-3000_20251028_061917_seed138612625.png)

### Galeria Completa

Para ver todos os exemplos gerados durante o desenvolvimento, consulte:
- [Galeria Completa de Imagens](execution_evidences/gallery.md) - 54 imagens catalogadas

---

## Documentação Técnica

### Documentos Principais

1. **[Pipeline de Treinamento](docs/PIPELINE_TREINAMENTO.md)**
   - Arquitetura detalhada do sistema
   - Explicação do LoRA e matemática envolvida
   - Configuração de hiperparâmetros
   - Processo de treinamento passo a passo
   - Descrição completa dos artefatos gerados
   - Validação e métricas
   - Potencial de monetização

2. **[API e Frontend](API_FRONTEND_README.md)**
   - Arquitetura da API REST
   - Endpoints e exemplos de uso
   - Estrutura do frontend React
   - Guia de integração

3. **[Galeria de Resultados](execution_evidences/gallery.md)**
   - 54 imagens geradas catalogadas
   - Organização por categoria e checkpoint
   - Análise de evolução do treinamento

### Conceitos Técnicos Chave

**LoRA (Low-Rank Adaptation)**

LoRA é uma técnica de fine-tuning eficiente que adiciona matrizes de baixo rank aos pesos do modelo:

```
W' = W + ΔW
ΔW = B × A

onde:
- W: Pesos originais (frozen)
- B, A: Matrizes treináveis de rank r << d
- r=8 (rank usado neste projeto)
```

**Vantagens:**
- Treina apenas 0.19% dos parâmetros (1.6M de 861M)
- Redução de 99.8% no uso de memória
- Arquivo final compacto (~6 MB vs 4.2 GB)
- Múltiplos LoRAs podem ser combinados

**Diffusion Process**

O modelo aprende a remover ruído progressivamente:

```
1. Forward Process: x₀ → [+ noise] → x_t (corrupted)
2. Training: UNet aprende a predizer o ruído adicionado
3. Inference: x_T (ruído puro) → [- noise iterativo] → x₀ (imagem limpa)
```

**Hiperparâmetros de Treinamento**

```python
{
  "batch_size": 16,              # Efetivo (2 × 8 gradient accumulation)
  "learning_rate": 1e-4,         # Com warmup de 500 steps
  "max_steps": 3000,             # ~24 épocas no dataset
  "lora_rank": 8,                # Dimensão do espaço latente
  "lora_alpha": 16,              # Fator de escala (2× rank)
  "gradient_checkpointing": True # Economia de 40% memória
}
```

---

## Performance e Requisitos

### Tempo de Treinamento

**Apple Silicon:**
```
M2 Max (38-core GPU): ~10.8 - 12.5 horas (3000 steps)
M1 Max (32-core GPU): ~12.5 - 15.0 horas (3000 steps)
M1 Pro (16-core GPU): ~16.7 - 20.8 horas (3000 steps)
```

**Tempo por step:** ~13-15 segundos

### Uso de Memória

**Durante Treinamento:**
```
Modelo Base (frozen):     ~4.2 GB
LoRA Adapters:            ~24 MB
Batch Processing:         ~1.5 GB
────────────────────────────────
Total:                    ~5.7 GB
```

**Durante Inferência:**
```
Pipeline Completo:        ~4.2 GB
Overhead API:             ~500 MB
────────────────────────────────
Total:                    ~4.7 GB
```

### Armazenamento

**Treinamento Completo:**
```
Checkpoints (5×):         ~4.2 GB
Final Pipeline:           ~4.2 GB
LoRA Weights:             ~6 MB
Validation Images:        ~20 MB
Logs:                     ~2 MB
────────────────────────────────
Total:                    ~8.4 GB
```

### Tempo de Geração

**Por Imagem (512×512):**
```
25 inference steps:       ~6-8 segundos
50 inference steps:       ~12-15 segundos
100 inference steps:      ~25-30 segundos
```

**Batch de 4 imagens:**
```
50 inference steps:       ~50 segundos (paralelo)
```

---

## Roadmap e Futuras Melhorias

### Curto Prazo (1-3 meses)

- [ ] Implementar cache de modelos na API
- [ ] Adicionar suporte a múltiplos LoRAs simultâneos
- [ ] Criar dataset de validação separado
- [ ] Implementar métricas automáticas (FID, CLIP Score)
- [ ] Adicionar autenticação na API
- [ ] Melhorar UI/UX do frontend

### Médio Prazo (3-6 meses)

- [ ] Treinar modelos para outras categorias:
  - Sapatos formais
  - Botas
  - Sandálias
  - Tênis esportivos
- [ ] Implementar geração condicionada por imagem de referência
- [ ] Adicionar controle de ângulo/pose
- [ ] Criar sistema de fine-tuning one-shot
- [ ] Implementar geração em alta resolução (1024×1024)

### Longo Prazo (6+ meses)

- [ ] Migrar para Stable Diffusion XL
- [ ] Implementar controlNet para pose
- [ ] Sistema de personalização por marca
- [ ] Marketplace de modelos customizados
- [ ] Integração com plataformas e-commerce
- [ ] Deploy em produção com escalabilidade
- [ ] Criação de plugin Shopify/WooCommerce

---

## Troubleshooting

### Problemas Comuns

**1. Erro de memória durante treinamento**
```bash
# Reduzir batch size
--train_batch_size=1
--gradient_accumulation_steps=16
```

**2. API não encontra modelos**
```bash
# Verificar variável de ambiente
export MODELS_DIR="/caminho/para/outputs"
```

**3. Frontend não conecta na API**
```bash
# Verificar CORS e porta
# api/main.py - linha CORS config
```

**4. Geração de imagens muito lenta**
```bash
# Reduzir inference steps
"num_inference_steps": 25  # ao invés de 50
```

---

## Contribuindo

Este é um projeto de pesquisa acadêmica. Contribuições são bem-vindas:

1. Fork do repositório
2. Criar branch para feature (`git checkout -b feature/MinhaFeature`)
3. Commit das mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para branch (`git push origin feature/MinhaFeature`)
5. Abrir Pull Request

### Guidelines

- Seguir PEP 8 para código Python
- Adicionar docstrings em funções
- Incluir testes quando possível
- Atualizar documentação relevante

---

## Licença e Contato

### Licença

Este projeto é licenciado sob os termos da licença MIT. Veja arquivo LICENSE para mais detalhes.

**Nota sobre Stable Diffusion:**
Este projeto usa Stable Diffusion v1.5, que está sob licença CreativeML Open RAIL-M. Uso comercial permitido com restrições. Consulte: https://huggingface.co/runwayml/stable-diffusion-v1-5

### Citação

Se você usar este projeto em sua pesquisa, por favor cite:

```bibtex
@software{shoes_ai_generator,
  title={Shoes AI Generator: LoRA Fine-tuning Pipeline for Product Photography},
  author={Aeon Bridge Research Team},
  year={2025},
  url={https://github.com/aeonbridge/shoes-ai-generator}
}
```

### Contato e Suporte

**Sponsored by:**

**Aeon Bridge Co.**
- Email: contact@aeonbridge.com
- Website: https://aeonbridge.com

Para questões técnicas, bugs ou sugestões:
- Abra uma issue no GitHub
- Entre em contato via email

---

## Agradecimentos

- **Hugging Face** - Diffusers, PEFT, Accelerate libraries
- **Stability AI** - Stable Diffusion model
- **Runway ML** - SD v1.5 weights
- **Microsoft** - LoRA paper e implementação
- **Comunidade Open Source** - Ferramentas e bibliotecas

---

## Referências

**Papers:**
- LoRA: Low-Rank Adaptation of Large Language Models (https://arxiv.org/abs/2106.09685)
- Stable Diffusion (https://arxiv.org/abs/2112.10752)
- Denoising Diffusion Probabilistic Models (https://arxiv.org/abs/2006.11239)

**Recursos:**
- Hugging Face Diffusers Documentation
- PEFT Documentation
- Apple Metal Performance Shaders (MPS)

---

**Última Atualização:** 28 de Outubro de 2025

**Versão:** 1.0.0

**Status do Projeto:** Ativo - Em Desenvolvimento
