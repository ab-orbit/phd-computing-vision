# API de Geração de Imagens - Backend

API FastAPI para geração de imagens de sapatos usando Stable Diffusion com adaptadores LoRA.

## Instalação

```bash
# Navegar para o diretório da API
cd api

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

## Configuração

```bash
# Copiar arquivo de ambiente
cp .env.example .env

# Editar .env conforme necessário
vim .env
```

## Execução

```bash
# Desenvolvimento (com auto-reload)
python main.py

# Ou usando uvicorn diretamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em: http://localhost:8000

## Documentação Interativa

Após iniciar a API, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints Principais

### POST /api/generate

Gera imagens baseadas em um prompt.

**Request:**
```json
{
  "model_name": "casual_shoes",
  "prompt": "A professional product photo of brown leather casual shoes on white background",
  "num_images": 4,
  "num_inference_steps": 50,
  "guidance_scale": 7.5,
  "seed": null
}
```

**Response:**
```json
{
  "success": true,
  "model_name": "casual_shoes",
  "prompt": "A professional product photo...",
  "num_images": 4,
  "images": [
    {
      "image_data": "base64_encoded_image...",
      "seed": 12345,
      "filename": "casual_shoes_20250127_120000_seed12345.png"
    }
  ],
  "generation_time_seconds": 45.32,
  "metadata": {}
}
```

### GET /api/models

Lista modelos disponíveis.

**Response:**
```json
[
  {
    "name": "base",
    "display_name": "Stable Diffusion 1.5 (Base)",
    "description": "Modelo base sem fine-tuning",
    "path": "runwayml/stable-diffusion-v1-5",
    "available": true
  },
  {
    "name": "lora_casual_shoes_3000steps_full",
    "display_name": "Lora Casual Shoes 3000Steps Full",
    "description": "Modelo fine-tuned: lora_casual_shoes_3000steps_full",
    "path": "/path/to/final_pipeline",
    "available": true
  }
]
```

### GET /api/prompts/examples

Retorna exemplos de prompts categorizados.

### GET /health

Health check da API.

## Estrutura de Diretórios

```
api/
├── main.py              # Código principal da API
├── requirements.txt     # Dependências Python
├── .env.example        # Exemplo de variáveis de ambiente
├── generated_images/   # Imagens geradas (criado automaticamente)
└── README.md           # Esta documentação
```

## Desenvolvimento

### Adicionar Novo Endpoint

```python
@app.get("/api/my-endpoint")
async def my_endpoint():
    return {"message": "Hello World"}
```

### Cache de Modelos

A API mantém um cache de modelos carregados para melhorar performance. Modelos são carregados sob demanda na primeira requisição.

### Logs

A API usa logging padrão do Python. Logs aparecem no console durante desenvolvimento.

## Troubleshooting

### Erro: MPS não disponível

Certifique-se de estar em um Mac com Apple Silicon e PyTorch instalado corretamente.

### Erro: Modelo não encontrado

Verifique que o treinamento foi concluído e o modelo existe em `training/outputs/[nome_modelo]/final_pipeline/`

### Erro: Out of Memory

Reduza `num_images` ou feche outras aplicações que usam GPU.

## Produção

Para deploy em produção:

```bash
# Instalar com Gunicorn
pip install gunicorn

# Executar com workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Considere também:
- Configurar HTTPS (nginx/Caddy)
- Limitar rate limiting
- Adicionar autenticação
- Monitoramento e logging estruturado
