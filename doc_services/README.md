# Document Classification API

API RESTful para classificação automática de tipos de documentos usando modelos de machine learning e LLMs.

## Funcionalidades

- Classificação de documentos em 17 categorias
- Suporte a múltiplos formatos (PDF, PNG, JPG, TIFF)
- Top-3 predições com probabilidades
- Metadados detalhados do documento
- Integração opcional com LLMs (Anthropic Claude, OpenAI GPT)
- Rastreamento de custos e tokens
- Cache inteligente
- Processamento em lote

## Tipos de Documentos Suportados

| Categoria | Descrição |
|-----------|-----------|
| `advertisement` | Anúncios publicitários |
| `budget` | Documentos de orçamento |
| `email` | Emails impressos |
| `file_folder` | Capas de pasta |
| `form` | Formulários |
| `handwritten` | Manuscritos |
| `invoice` | Notas fiscais |
| `letter` | Cartas formais |
| `memo` | Memorandos |
| `news_article` | Artigos de jornal |
| `presentation` | Slides |
| `questionnaire` | Questionários |
| `resume` | Currículos |
| `scientific_publication` | Artigos científicos |
| `scientific_report` | Relatórios técnicos |
| `specification` | Especificações técnicas |
| `contract` | Contratos legais |

## Instalação

### Requisitos

- Python 3.10+
- Docker (opcional)
- Modelo DocLayout-YOLO (baixado automaticamente)

### Setup Local

```bash
# 1. Clone o repositório
cd doc_services

# 2. Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações

# 5. Execute o servidor
python -m app.main
# ou
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Setup com Docker

```bash
# 1. Build da imagem
docker-compose build

# 2. Execute o container
docker-compose up -d

# 3. Verifique logs
docker-compose logs -f api
```

## Uso Rápido

### Health Check

```bash
curl http://localhost:8000/health
```

### Classificar Documento

**Python**:
```python
import requests

# Classificação simples
with open('documento.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/classify', files=files)

result = response.json()
print(f"Tipo: {result['predicted_type']}")
print(f"Probabilidade: {result['probability']:.2%}")
print(f"Alternativas: {result['alternatives']}")
```

**cURL**:
```bash
curl -X POST "http://localhost:8000/classify" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@documento.pdf" \
  -F "use_llm=false" \
  -F "include_alternatives=true"
```

**JavaScript (fetch)**:
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('use_llm', 'false');

const response = await fetch('http://localhost:8000/classify', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(`Tipo: ${result.predicted_type}`);
```

### Com LLM (Análise Complementar)

```python
import requests

with open('documento.pdf', 'rb') as f:
    files = {'file': f}
    data = {
        'use_llm': True,
        'confidence_threshold': 0.7
    }
    response = requests.post(
        'http://localhost:8000/classify',
        files=files,
        data=data
    )

result = response.json()
print(f"Tipo: {result['predicted_type']}")
print(f"Confiança: {result['confidence']}")

# Metadados do LLM
if result['llm_metadata']:
    llm = result['llm_metadata']
    print(f"Tokens: {llm['total_tokens']}")
    print(f"Custo: ${llm['total_cost_usd']}")
```

## Estrutura da Resposta

```json
{
  "predicted_type": "scientific_publication",
  "probability": 0.87,
  "confidence": "high",
  "alternatives": [
    {
      "document_type": "scientific_report",
      "probability": 0.08,
      "confidence": "low"
    },
    {
      "document_type": "presentation",
      "probability": 0.03,
      "confidence": "low"
    }
  ],
  "document_metadata": {
    "file_name": "paper.pdf",
    "file_format": "pdf",
    "file_size_bytes": 2458624,
    "file_size_human": "2.3 MB",
    "mime_type": "application/pdf",
    "num_pages": 12,
    "num_paragraphs": 45,
    "text_density": 0.68,
    "num_figures": 8,
    "num_tables": 3,
    "processing_time_ms": 3452.5
  },
  "llm_metadata": {
    "provider": "anthropic",
    "model_name": "claude-3-sonnet",
    "input_tokens": 1250,
    "output_tokens": 450,
    "total_cost_usd": "0.010500",
    "latency_ms": 3250.5
  },
  "request_id": "req_abc123",
  "timestamp": "2025-10-25T14:30:03Z",
  "api_version": "1.0.0"
}
```

## Documentação Interativa

Acesse a documentação Swagger interativa:

```
http://localhost:8000/docs
```

Ou ReDoc:

```
http://localhost:8000/redoc
```

## Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_VERSION=1.0.0

# Model Configuration
MODEL_PATH=/path/to/doclayout_yolo_docstructbench_imgsz1024.pt
CONFIDENCE_THRESHOLD=0.2
IMAGE_SIZE=1024

# LLM Configuration (opcional)
LLM_PROVIDER=anthropic  # anthropic, openai, local
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx

# LLM Model Selection
ANTHROPIC_MODEL=claude-3-sonnet-20240229
OPENAI_MODEL=gpt-4-turbo

# LLM Pricing (USD per token)
ANTHROPIC_INPUT_PRICE=0.000003
ANTHROPIC_OUTPUT_PRICE=0.000015
OPENAI_INPUT_PRICE=0.00001
OPENAI_OUTPUT_PRICE=0.00003

# Cache Configuration
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_SECONDS=3600

# File Upload Limits
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=pdf,png,jpg,jpeg,tiff,tif

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
```

## Arquitetura

```
doc_services/
├── app/
│   ├── api/                  # Endpoints da API
│   │   ├── __init__.py
│   │   └── classify.py       # Rotas de classificação
│   ├── models/               # Modelos Pydantic
│   │   ├── __init__.py
│   │   └── schemas.py        # Schemas de entrada/saída
│   ├── services/             # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── layout_analyzer.py      # Análise de layout (DocLayout-YOLO)
│   │   ├── heuristic_classifier.py # Classificador baseado em regras
│   │   ├── llm_service.py          # Cliente LLM genérico
│   │   ├── llm_anthropic.py        # Implementação Anthropic
│   │   ├── llm_openai.py           # Implementação OpenAI
│   │   └── pdf_processor.py        # Conversão PDF
│   ├── core/                 # Configuração e utils
│   │   ├── __init__.py
│   │   ├── config.py         # Configurações
│   │   ├── cache.py          # Sistema de cache
│   │   └── logging.py        # Setup de logging
│   └── main.py               # Aplicação FastAPI
├── tests/                    # Testes
│   ├── unit/
│   ├── integration/
│   └── load/
├── docker/                   # Configurações Docker
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/                     # Documentação adicional
├── requirements.txt          # Dependências Python
├── .env.example              # Exemplo de configuração
├── BACKLOG.md               # Backlog de desenvolvimento
└── README.md                # Este arquivo
```

## Desenvolvimento

### Executar Testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=app --cov-report=html

# Apenas unit tests
pytest tests/unit/

# Testes de integração
pytest tests/integration/
```

### Formatação de Código

```bash
# Black (formatador)
black app/ tests/

# Flake8 (linter)
flake8 app/ tests/

# MyPy (type checking)
mypy app/
```

### Pre-commit Hooks

```bash
# Instalar hooks
pre-commit install

# Executar manualmente
pre-commit run --all-files
```

## Performance

**Benchmarks Esperados** (hardware: CPU i7, 16GB RAM):

| Operação | Tempo Médio |
|----------|-------------|
| Classificação (apenas heurísticas) | < 100ms |
| Análise de layout (DocLayout-YOLO) | 2-5s |
| Classificação completa (sem LLM) | 3-6s |
| Classificação com LLM | 5-10s |
| Processamento em lote (10 docs) | ~10s |

**Otimizações**:
- Cache Redis reduz tempo para < 50ms em hits
- Processamento assíncrono permite múltiplas requisições simultâneas
- Batch processing com paralelização

## Custos Estimados (LLM)

Baseado em preços de outubro de 2025:

**Anthropic Claude 3 Sonnet**:
- Input: $3.00 / 1M tokens
- Output: $15.00 / 1M tokens
- **Custo médio por documento**: ~$0.01 - $0.02

**OpenAI GPT-4 Turbo**:
- Input: $10.00 / 1M tokens
- Output: $30.00 / 1M tokens
- **Custo médio por documento**: ~$0.03 - $0.05

**Recomendação**: Use heurísticas como padrão e LLM apenas para casos ambíguos (confidence < 0.7) para reduzir custos.

## Monitoramento

### Métricas Prometheus

Acesse métricas em `http://localhost:9090/metrics`:

```
# Contadores
doc_classification_total
doc_classification_success
doc_classification_failure
llm_calls_total
cache_hits_total
cache_misses_total

# Histogramas
doc_classification_duration_seconds
document_size_bytes
llm_latency_seconds
```

### Logs Estruturados

Logs em formato JSON para fácil parsing:

```json
{
  "timestamp": "2025-10-25T14:30:00Z",
  "level": "INFO",
  "message": "Document classified",
  "request_id": "req_abc123",
  "document_type": "scientific_publication",
  "probability": 0.87,
  "processing_time_ms": 3452.5
}
```

## FAQ

**P: Quais formatos de arquivo são suportados?**
R: PDF, PNG, JPG, JPEG, TIFF. PDFs são convertidos automaticamente para imagem.

**P: Qual o tamanho máximo de arquivo?**
R: 50MB por padrão (configurável via MAX_FILE_SIZE_MB).

**P: A API funciona offline?**
R: Sim, o classificador heurístico funciona offline. LLM requer conexão internet.

**P: Como melhorar a acurácia?**
R: Use `use_llm=True` para casos importantes ou ajuste heurísticas para seu domínio específico.

**P: Posso adicionar novas categorias?**
R: Sim, edite `DocumentType` em `schemas.py` e ajuste as heurísticas em `heuristic_classifier.py`.

**P: Existe rate limiting?**
R: Não implementado ainda. Veja backlog Sprint 4.

## Roadmap

- [x] MVP com classificador heurístico
- [ ] Integração LLM completa
- [ ] Sistema de cache
- [ ] Processamento em lote
- [ ] OCR opcional
- [ ] UI web simples
- [ ] Autenticação JWT
- [ ] Rate limiting

Veja [BACKLOG.md](BACKLOG.md) para detalhes.

## Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/amazing-feature`)
3. Commit suas mudanças (`git commit -m 'Add amazing feature'`)
4. Push para a branch (`git push origin feature/amazing-feature`)
5. Abra um Pull Request

## Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## Suporte

- GitHub Issues: [https://github.com/usuario/doc-classification-api/issues](https://github.com/usuario/doc-classification-api/issues)
- Email: support@docclassification.com
- Documentação: [http://localhost:8000/docs](http://localhost:8000/docs)

## Agradecimentos

- [DocLayout-YOLO](https://github.com/opendatalab/DocLayout-YOLO) pela análise de layout
- [FastAPI](https://fastapi.tiangolo.com/) pelo framework
- [Pydantic](https://pydantic-docs.helpmanual.io/) pela validação de dados
- Dataset [RVL-CDIP](https://www.cs.cmu.edu/~aharley/rvl-cdip/) para treinamento e validação
