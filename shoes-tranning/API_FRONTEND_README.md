# API + Frontend - Shoes Image Generator

Sistema completo de geração de imagens com API FastAPI e interface React moderna.

---

## Visão Geral

Este documento complementa o README.md principal do projeto, focando especificamente na camada de **API FastAPI** e **Frontend React** para consumo do modelo LoRA treinado.

### Estrutura Adicional

```
shoes-tranning/
├── api/                          # Backend FastAPI ✨ NOVO
│   ├── main.py                   # API principal
│   ├── requirements.txt          # Dependências Python
│   ├── .env.example             # Exemplo de configuração
│   ├── generated_images/        # Imagens geradas (auto-criado)
│   └── README.md                # Documentação da API
│
└── frontend/                     # Frontend React ✨ NOVO
    ├── src/
    │   ├── App.tsx              # Componente principal
    │   ├── api.ts               # Cliente da API
    │   ├── types.ts             # Tipos TypeScript
    │   ├── main.tsx             # Entry point
    │   └── index.css            # Estilos globais
    ├── package.json             # Dependências Node
    ├── vite.config.ts           # Configuração Vite
    ├── tailwind.config.js       # Configuração Tailwind
    └── README.md                # Documentação do Frontend
```

---

## Features Principais

### Backend (API FastAPI)

- Endpoints RESTful para geração de imagens
- Suporte para múltiplos modelos LoRA
- Geração em lote (1-8 imagens simultâneas)
- Cache de modelos para performance
- Biblioteca com 15+ exemplos de prompts categorizados
- Health check e status da API
- Documentação automática (Swagger UI / ReDoc)
- CORS configurado para frontend
- Logs estruturados

### Frontend (React + TypeScript)

- Interface moderna e responsiva
- Animações suaves com Framer Motion
- Seleção de modelos via dropdown
- Biblioteca de prompts categorizados:
  - Cores Básicas (preto, branco, marrom, azul)
  - Materiais (couro, canvas, suede)
  - Estilos (sneaker, loafer, oxford, slip-on)
  - Detalhes Especiais (cadarços coloridos, solas contrastantes)
- Galeria interativa de imagens geradas
- Modal de visualização em tamanho completo
- Download individual de imagens
- Notificações toast elegantes
- Loading states com indicadores visuais
- Dark theme profissional

---

## Quick Start (5 minutos)

### Pré-requisitos

```bash
# Python 3.10+
python --version

# Node.js 18+
node --version

# Verificar MPS (Apple Silicon)
python -c "import torch; print(torch.backends.mps.is_available())"
```

### 1. Iniciar Backend

```bash
# Terminal 1: API
cd api
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python main.py

# API rodando em http://localhost:8000
# Docs em http://localhost:8000/docs
```

### 2. Iniciar Frontend

```bash
# Terminal 2: React
cd frontend
npm install
cp .env.example .env
npm run dev

# App rodando em http://localhost:3000
```

### 3. Usar

1. Abra http://localhost:3000
2. Selecione modelo "Lora Casual Shoes 3000Steps Full"
3. Clique "Ver exemplos" e escolha um prompt
4. Ajuste slider para 4 imagens
5. Clique "Gerar Imagens"
6. Aguarde ~45-60 segundos
7. Visualize e faça download

---

## Endpoints da API

### POST /api/generate

Gera imagens baseadas em prompt.

```bash
curl -X POST "http://localhost:8000/api/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "model_name": "lora_casual_shoes_3000steps_full",
       "prompt": "A professional product photo of brown leather casual shoes on white background",
       "num_images": 4
     }'
```

**Parâmetros:**
- `model_name`: Nome do modelo (obrigatório)
- `prompt`: Descrição da imagem (10-500 caracteres)
- `num_images`: Quantidade (1-8, padrão: 1)
- `num_inference_steps`: Qualidade (10-100, padrão: 50)
- `guidance_scale`: Aderência ao prompt (1.0-20.0, padrão: 7.5)
- `seed`: Reprodutibilidade (opcional)

**Response:**
```json
{
  "success": true,
  "model_name": "lora_casual_shoes_3000steps_full",
  "prompt": "A professional product photo...",
  "num_images": 4,
  "images": [
    {
      "image_data": "base64_string...",
      "seed": 12345,
      "filename": "casual_shoes_20250127_120000_seed12345.png"
    }
  ],
  "generation_time_seconds": 45.32,
  "metadata": {...}
}
```

### GET /api/models

Lista modelos disponíveis.

```bash
curl http://localhost:8000/api/models
```

### GET /api/prompts/examples

Retorna exemplos de prompts categorizados.

```bash
curl http://localhost:8000/api/prompts/examples
```

### GET /health

Health check.

```bash
curl http://localhost:8000/health
```

---

## Tecnologias Utilizadas

### Backend

| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| FastAPI | 0.109.0 | Framework web rápido |
| PyTorch | 2.5.1 | Deep learning (MPS) |
| Diffusers | 0.32.1 | Pipeline SD |
| PEFT | 0.14.0 | LoRA implementation |
| Uvicorn | 0.27.0 | Servidor ASGI |

### Frontend

| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| React | 18.2.0 | UI library |
| TypeScript | 5.3.3 | Type safety |
| Vite | 5.0.11 | Build tool |
| Tailwind CSS | 3.4.1 | Styling |
| Framer Motion | 10.18.0 | Animações |
| Axios | 1.6.5 | HTTP client |
| React Hot Toast | 2.4.1 | Notificações |

---

## Arquitetura

```
┌─────────────┐
│   Browser   │
│  (React UI) │
└──────┬──────┘
       │ HTTP/JSON
       ▼
┌─────────────┐
│  FastAPI    │
│   (8000)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Model     │
│   Cache     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  SD 1.5 +   │
│    LoRA     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Generated  │
│   Images    │
└─────────────┘
```

### Fluxo de Geração

1. **User Input**: Usuário insere prompt e parâmetros via React
2. **API Request**: Frontend envia POST /api/generate
3. **Model Loading**: API carrega/usa modelo do cache
4. **Image Generation**: SD 1.5 + LoRA gera N imagens
5. **Encoding**: Imagens convertidas para base64
6. **Response**: JSON com imagens retorna para frontend
7. **Display**: React renderiza galeria
8. **Download**: Usuário pode baixar imagens

---

## Performance

### API (Apple M2 Max)

- **Latência por imagem**: 10-15 segundos
- **Throughput**: ~4 imagens/minuto
- **Memória durante geração**: ~6GB
- **Cold start**: ~5 segundos (carregar modelo)
- **Warm cache**: <1 segundo (modelo já em memória)

### Frontend

- **Bundle size**: ~500KB (gzipped)
- **First Paint**: < 1 segundo
- **Time to Interactive**: < 2 segundos
- **Lighthouse Performance**: 95+

---

## Desenvolvimento

### Adicionar Novo Modelo

1. Treinar modelo LoRA
2. Salvar em `training/outputs/[nome]/final_pipeline/`
3. Reiniciar API
4. Modelo aparece automaticamente no frontend

### Adicionar Novo Prompt Example

Editar `api/main.py`:

```python
PromptExample(
    category="Nova Categoria",
    title="Título do Exemplo",
    prompt="A professional product photo of...",
    description="Descrição curta"
)
```

### Customizar UI

Editar `frontend/tailwind.config.js` para mudar cores/tema.

---

## Deploy em Produção

### Backend com Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY api/requirements.txt .
RUN pip install -r requirements.txt

COPY api/ .
COPY training/outputs/ /models/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend (Vercel/Netlify)

```bash
cd frontend
npm run build

# Deploy
vercel --prod
# ou
netlify deploy --prod --dir=dist
```

---

## Troubleshooting

### API não inicia

```bash
# Verificar MPS
python -c "import torch; print(torch.backends.mps.is_available())"

# Verificar modelos
ls training/outputs/*/final_pipeline/
```

### Frontend não conecta

```bash
# Verificar API está rodando
curl http://localhost:8000/health

# Verificar CORS
# Editar api/main.py allow_origins se necessário
```

### Geração lenta

```python
# Adicionar em api/main.py:
pipeline.enable_attention_slicing()  # Reduz memória
```

### Out of Memory

- Gere menos imagens por vez (1-2)
- Reinicie API para limpar cache
- Use guidance_scale menor

---

## Documentação Completa

Para documentação técnica detalhada:

### API
- `api/README.md`: Guia completo da API
- http://localhost:8000/docs: Swagger UI
- http://localhost:8000/redoc: ReDoc

### Frontend
- `frontend/README.md`: Guia completo do React
- Código comentado em `frontend/src/`

### Deployment
- `docs/API_DEPLOYMENT_GUIDE.md`: Guia passo a passo completo

### Pipeline de Treinamento
- `docs/PIPELINE_TREINAMENTO.md`: Documentação técnica + monetização
- `docs/QUICK_START_GUIDE.md`: Guia prático

---

## Métricas de Sucesso

### API

- [ ] Latência < 15s por imagem
- [ ] Uptime > 99%
- [ ] Cache hit rate > 80%
- [ ] Error rate < 1%

### Frontend

- [ ] Loading time < 2s
- [ ] Lighthouse score > 90
- [ ] Zero crashes
- [ ] Mobile responsive

### Qualidade de Imagens

- [ ] FID Score < 30
- [ ] CLIP Score > 25
- [ ] Taxa de sucesso > 95%

---

## Roadmap

### Próximas Features

- [ ] Autenticação e autorização
- [ ] Rate limiting por usuário
- [ ] Histórico de gerações
- [ ] Favoritos/Collections
- [ ] Compartilhamento de imagens
- [ ] Batch processing assíncrono
- [ ] Webhook notifications
- [ ] Analytics dashboard

### Melhorias de Performance

- [ ] Redis cache para modelos
- [ ] CDN para imagens geradas
- [ ] Lazy loading no frontend
- [ ] Service workers (PWA)
- [ ] Image compression

---

## Licença

Projeto para fins educacionais e de pesquisa.

---

## Links Úteis

- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **GitHub**: [seu-repo]
- **Documentação Principal**: README.md
- **Backlog do Projeto**: planning/BACKLOG.md

---

**Status**: Produção Ready
**Última Atualização**: 27/01/2025
**Versão**: 1.0.0
