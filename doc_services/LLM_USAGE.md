# Uso de LLM para Classificação de Documentos

Guia completo para usar a API com LLMs para classificação de documentos.

## Visão Geral

A API suporta classificação de documentos usando Large Language Models (LLMs) como complemento ou alternativa ao classificador heurístico. Atualmente implementado:

- **Anthropic Claude 3.5 Haiku** (modelo mais barato)
- **Anthropic Claude 3.5 Sonnet** (modelo intermediário)

## Configuração

### 1. Obter API Key

**Anthropic**:
1. Acesse https://console.anthropic.com/
2. Crie uma conta ou faça login
3. Vá em "API Keys"
4. Crie uma nova chave e copie

### 2. Configurar .env

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar e adicionar sua API key
nano .env
```

Adicione:
```env
# LLM Configuration
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Modelo (escolha o mais adequado)
ANTHROPIC_MODEL=claude-3-5-haiku-20241022  # Mais barato
# ANTHROPIC_MODEL=claude-3-5-sonnet-20241022  # Mais preciso
```

## Modelos Disponíveis

### Anthropic Claude

| Modelo | Input ($/1M tokens) | Output ($/1M tokens) | Custo/Doc | Uso Recomendado |
|--------|---------------------|----------------------|-----------|-----------------|
| **Claude 3.5 Haiku** | $1.00 | $5.00 | ~$0.003-0.005 | **Produção** (melhor custo-benefício) |
| Claude 3.5 Sonnet | $3.00 | $15.00 | ~$0.010-0.015 | Casos que exigem maior precisão |
| Claude 3 Opus | $15.00 | $75.00 | ~$0.050-0.080 | Uso especializado |

**Recomendação**: Use **Claude 3.5 Haiku** para a maioria dos casos. É 3x mais barato que Sonnet e tem performance excelente para classificação.

## Uso da API

### 1. Classificação Básica com LLM

```python
import requests

# Classificar documento usando LLM
with open('documento.pdf', 'rb') as f:
    files = {'file': f}
    data = {'use_llm': True}  # Habilitar LLM

    response = requests.post(
        'http://localhost:8000/classify',
        files=files,
        data=data
    )

result = response.json()

print(f"Tipo: {result['predicted_type']}")
print(f"Confiança: {result['confidence']}")
print(f"Probabilidade: {result['probability']:.1%}")

# Metadados do LLM
if result['llm_metadata']:
    llm = result['llm_metadata']
    print(f"\nTokens: {llm['total_tokens']}")
    print(f"Custo: ${llm['total_cost_usd']}")
    print(f"Latência: {llm['latency_ms']:.0f}ms")
```

### 2. cURL

```bash
curl -X POST "http://localhost:8000/classify" \
  -H "accept: application/json" \
  -F "file=@documento.pdf" \
  -F "use_llm=true" \
  -F "include_alternatives=true"
```

### 3. Python Assíncrono

```python
import httpx

async def classify_with_llm(file_path: str):
    async with httpx.AsyncClient() as client:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'use_llm': True}

            response = await client.post(
                'http://localhost:8000/classify',
                files=files,
                data=data,
                timeout=60.0  # LLM pode demorar
            )

            return response.json()

# Usar
result = await classify_with_llm('documento.pdf')
```

## Resposta da API

### Estrutura Completa

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
    }
  ],
  "document_metadata": {
    "file_name": "paper.pdf",
    "file_size_human": "2.3 MB",
    "processing_time_ms": 3452.5
  },
  "llm_metadata": {
    "provider": "anthropic",
    "model_name": "claude-3-5-haiku-20241022",
    "endpoint": "https://api.anthropic.com/v1/messages",
    "input_tokens": 1250,
    "output_tokens": 450,
    "total_tokens": 1700,
    "input_cost_usd": "0.001250",
    "output_cost_usd": "0.002250",
    "total_cost_usd": "0.003500",
    "request_timestamp": "2025-10-25T14:30:00Z",
    "response_timestamp": "2025-10-25T14:30:03Z",
    "latency_ms": 3250.5,
    "cache_hit": false
  },
  "request_id": "req_abc123",
  "timestamp": "2025-10-25T14:30:03.5Z",
  "api_version": "1.0.0"
}
```

## Como Funciona

### Fluxo de Classificação com LLM

```
1. API recebe documento
   ↓
2. Extrai metadados básicos (nome, tamanho, formato)
   ↓
3. [Opcional] Extrai features de layout (DocLayout-YOLO)
   ↓
4. Cria prompt estruturado para LLM
   ↓
5. Envia para Anthropic Claude API
   ↓
6. Claude analisa e retorna classificação JSON
   ↓
7. Parse da resposta + validação
   ↓
8. Calcula custos baseado em tokens
   ↓
9. Retorna resultado completo
```

### Prompt Enviado ao LLM

O prompt inclui:

```
Você é um especialista em classificação de documentos...

Documento: contract_2024.pdf

Categorias disponíveis:
  - advertisement
  - budget
  - email
  - contract
  - invoice
  ... (17 categorias)

Informações extraídas do layout:
- Número de parágrafos: 15
- Densidade de texto: 0.65
- Figuras: 0
- Tabelas: 2

Instruções:
1. Analise o nome e informações
2. Determine a categoria mais adequada
3. Considere padrões típicos...

Retorne JSON:
{
  "predicted_type": "contract",
  "confidence": 0.92,
  "reasoning": "Documento formal com..."
}
```

## Cálculo de Custos

### Fórmula

```
Custo Total = (Input Tokens × Input Price) + (Output Tokens × Output Price)

Exemplo com Claude 3.5 Haiku:
- Input tokens: 1200
- Output tokens: 400
- Input price: $1.00 / 1M tokens
- Output price: $5.00 / 1M tokens

Cálculo:
Input Cost  = 1200 × ($1.00 / 1,000,000) = $0.0012
Output Cost = 400 × ($5.00 / 1,000,000)  = $0.0020
Total Cost  = $0.0012 + $0.0020 = $0.0032
```

### Projeções de Custo

**Claude 3.5 Haiku** (~$0.003-0.005 por documento):

| Volume | Custo Estimado |
|--------|----------------|
| 100 documentos | $0.30 - $0.50 |
| 1.000 documentos | $3.00 - $5.00 |
| 10.000 documentos | $30 - $50 |
| 100.000 documentos | $300 - $500 |

**Claude 3.5 Sonnet** (~$0.010-0.015 por documento):

| Volume | Custo Estimado |
|--------|----------------|
| 100 documentos | $1.00 - $1.50 |
| 1.000 documentos | $10 - $15 |
| 10.000 documentos | $100 - $150 |
| 100.000 documentos | $1.000 - $1.500 |

**Economia usando Haiku**: 70-80% mais barato que Sonnet

## Testes

### Executar Script de Teste

```bash
cd doc_services

# Garantir que .env está configurado
# ANTHROPIC_API_KEY=sk-ant-xxx

# Executar testes
python test_llm_classification.py
```

### Testes Incluídos

1. **Classificação Simples**: Testa 5 documentos de tipos diferentes
2. **Classificação com Features**: Demonstra uso de features do layout
3. **Análise de Custos**: Compara Haiku vs Sonnet

### Exemplo de Saída

```
================================================================================
TESTE 1: Classificação Simples
================================================================================

Modelo: claude-3-5-haiku-20241022
Provider: Anthropic Claude
Custo estimado: ~$0.005 por documento

[1/5] Classificando: research_paper_2024.pdf
--------------------------------------------------------------------------------
Tipo predito: scientific_publication
Tipo esperado: scientific_publication
Confiança: 92.00%
Razão: Documento acadêmico com estrutura formal...

Tokens: 1650 (in:1200, out:450)
Custo: $0.003450
Latência: 2850ms

Status: ✓ CORRETO
```

## Otimização de Custos

### 1. Usar Modo Híbrido (Recomendado)

```python
# Usar heurísticas primeiro
# Se confiança < 0.7, validar com LLM

def classify_smart(document):
    # Classificar com heurísticas (grátis)
    heuristic_result = classify_heuristic(document)

    if heuristic_result['confidence'] < 0.7:
        # Casos ambíguos: usar LLM
        llm_result = classify_llm(document)
        return llm_result
    else:
        # Alta confiança: economizar usando heurística
        return heuristic_result
```

**Economia**: 60-80% dos documentos não precisam de LLM

### 2. Implementar Cache

```python
import hashlib

def get_document_hash(file_content):
    return hashlib.md5(file_content).hexdigest()

# Antes de chamar LLM, verificar cache
doc_hash = get_document_hash(file_content)
cached = redis.get(f"classification:{doc_hash}")

if cached:
    return cached  # Custo: $0
else:
    result = classify_llm(document)
    redis.set(f"classification:{doc_hash}", result, ttl=3600)
    return result
```

**Economia**: Documentos repetidos custam $0

### 3. Batch Processing

```python
# Processar documentos similares em lote
# Compartilhar contexto no prompt

async def classify_batch_smart(documents):
    # Agrupar documentos similares
    # Uma chamada LLM para múltiplos documentos
    # Reduz overhead de tokens do sistema
    pass
```

**Economia**: 20-30% em tokens de sistema

## Tratamento de Erros

### Erros Comuns

#### 1. API Key Inválida

```json
{
  "error": true,
  "error_type": "http_error",
  "errors": [
    {
      "code": "HTTP_500",
      "message": "Erro ao classificar com LLM: Invalid API key"
    }
  ]
}
```

**Solução**: Verificar `ANTHROPIC_API_KEY` no .env

#### 2. Timeout

```json
{
  "error": true,
  "errors": [
    {
      "code": "HTTP_500",
      "message": "Erro ao classificar com LLM: Timeout ao chamar Anthropic API"
    }
  ]
}
```

**Solução**: Aumentar timeout no .env (`LLM_TIMEOUT_SECONDS=60`)

#### 3. Rate Limit

```
429 Too Many Requests
```

**Solução**: Implementar retry com backoff exponencial

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def classify_with_retry(document):
    return await llm_service.classify_document(document)
```

## Métricas e Monitoramento

### Métricas a Rastrear

```python
# Prometheus metrics
llm_calls_total
llm_calls_success
llm_calls_failure
llm_latency_seconds (histogram)
llm_tokens_total (by type: input/output)
llm_cost_usd_total
```

### Logs Estruturados

```json
{
  "timestamp": "2025-10-25T14:30:00Z",
  "level": "INFO",
  "event": "llm_classification",
  "request_id": "req_abc123",
  "document_name": "contract.pdf",
  "llm_provider": "anthropic",
  "llm_model": "claude-3-5-haiku-20241022",
  "predicted_type": "contract",
  "confidence": 0.92,
  "tokens": 1650,
  "cost_usd": 0.00345,
  "latency_ms": 2850
}
```

## Comparação: LLM vs Heurísticas

| Aspecto | Heurísticas | LLM (Claude Haiku) |
|---------|-------------|-------------------|
| **Custo** | $0 | ~$0.003-0.005 |
| **Latência** | <100ms | 2-5s |
| **Acurácia** | ~55-60% | ~80-90% |
| **Escalabilidade** | Excelente | Boa (com cache) |
| **Manutenção** | Alta (ajustar regras) | Baixa (prompt engineering) |
| **Interpretabilidade** | Alta | Média (via reasoning) |
| **Tipos novos** | Requer código | Apenas atualizar prompt |

## Próximos Passos

1. **Implementar OpenAI GPT-4o-mini** (comparar custos)
2. **Implementar Google Gemini Flash** (pode ser mais barato)
3. **Cache com Redis** (reduzir custos de documentos repetidos)
4. **Modo híbrido inteligente** (heurísticas → LLM apenas se necessário)
5. **Fine-tuning** (treinar modelo específico, reduzir custos)

## Recursos

- **Anthropic Docs**: https://docs.anthropic.com/
- **Pricing**: https://www.anthropic.com/pricing
- **API Status**: https://status.anthropic.com/
- **Rate Limits**: https://docs.anthropic.com/claude/reference/rate-limits

## Suporte

Para problemas ou dúvidas:
1. Verificar logs: `docker-compose logs -f api`
2. Testar conexão: `python test_llm_classification.py`
3. Abrir issue no GitHub
4. Consultar documentação da Anthropic

---

**Última Atualização**: 25 de outubro de 2025
**Versão**: 1.0.0
