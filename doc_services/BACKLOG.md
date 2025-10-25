# Backlog - API de Classificação de Documentos

## Visão Geral

API RESTful para classificação automática de tipos de documentos usando modelos de machine learning e opcionalmente LLMs para análise complementar.

**Stack Tecnológica**:
- FastAPI (framework web)
- Pydantic (validação de dados)
- DocLayout-YOLO (análise de layout)
- Anthropic Claude / OpenAI GPT (LLM opcional)
- Python 3.10+

---

## Sprint 1: Fundação e MVP (Estimativa: 5 dias)

### 1.1 Setup e Infraestrutura [DONE]

**Objetivo**: Criar estrutura base do projeto e configuração inicial

**Tarefas**:
- [x] Criar estrutura de diretórios
- [x] Definir modelos Pydantic (schemas.py)
- [x] Criar endpoints FastAPI básicos (main.py)
- [ ] Criar arquivo de configuração (config.py)
- [ ] Criar requirements.txt
- [ ] Criar Dockerfile
- [ ] Criar docker-compose.yml
- [ ] Setup de ambiente virtual

**Critérios de Aceitação**:
- Projeto estruturado e organizado
- Servidor FastAPI rodando em http://localhost:8000
- Documentação interativa disponível em /docs
- Health check funcionando

**Prioridade**: CRÍTICA
**Estimativa**: 1 dia

---

### 1.2 Integração com DocLayout-YOLO [TODO]

**Objetivo**: Integrar modelo DocLayout-YOLO para análise de layout

**Tarefas**:
- [ ] Criar service class para DocLayout-YOLO (services/layout_analyzer.py)
- [ ] Implementar carregamento do modelo
- [ ] Implementar análise de documento (imagem)
- [ ] Extrair features: num_paragraphs, text_density, num_figures, etc
- [ ] Implementar conversão PDF → imagem
- [ ] Adicionar cache de resultados
- [ ] Testes unitários

**Arquivos a Criar**:
```
app/services/
├── __init__.py
├── layout_analyzer.py  # Integração DocLayout-YOLO
└── pdf_processor.py    # Conversão PDF para imagem
```

**Exemplo de Código**:
```python
# app/services/layout_analyzer.py
class LayoutAnalyzer:
    def __init__(self, model_path: str):
        self.model = YOLOv10(model_path)

    async def analyze(self, image: bytes) -> LayoutFeatures:
        # Análise de layout
        results = self.model.predict(image)
        # Extrair features
        features = self.extract_features(results)
        return features
```

**Critérios de Aceitação**:
- Modelo carrega corretamente no startup
- Análise de imagem retorna features estruturadas
- PDFs são convertidos e analisados corretamente
- Performance: < 5s por documento

**Prioridade**: CRÍTICA
**Estimativa**: 2 dias

---

### 1.3 Classificador Heurístico [TODO]

**Objetivo**: Implementar classificador baseado em heurísticas (versão 1.2 do doclayout-yolo)

**Tarefas**:
- [ ] Portar código de classify_documents.py
- [ ] Criar service class (services/heuristic_classifier.py)
- [ ] Implementar todas as 17 categorias
- [ ] Ajustar heurísticas para cada categoria
- [ ] Adicionar suporte a "contract" (nova categoria)
- [ ] Retornar probabilidades normalizadas
- [ ] Retornar top-3 alternativas
- [ ] Testes unitários

**Arquivos a Criar**:
```
app/services/
└── heuristic_classifier.py  # Classificador baseado em regras
```

**Heurísticas a Implementar**:
```python
# Baseado em doclayout-yolo/classify_documents.py v1.2
def classify_from_features(features: LayoutFeatures) -> ClassificationResult:
    scores = {}

    # Email
    if features.text_density < 0.20:
        scores['email'] += 3.0
    if 1 <= features.num_paragraphs <= 4:
        scores['email'] += 2.5

    # Scientific Publication
    if features.text_density >= 0.45:
        scores['scientific_publication'] += 4.0
    if features.num_paragraphs >= 5:
        scores['scientific_publication'] += 4.0

    # Contract (nova categoria)
    if features.num_paragraphs >= 10:
        scores['contract'] += 3.0
    if features.text_density >= 0.50:
        scores['contract'] += 2.0

    # ... outras categorias

    return normalize_and_rank(scores)
```

**Critérios de Aceitação**:
- Classificação retorna tipo principal + top-3
- Probabilidades somam 1.0
- Acurácia mínima: 55% (baseado em v1.2)
- Tempo de classificação: < 100ms

**Prioridade**: CRÍTICA
**Estimativa**: 2 dias

---

### 1.4 Endpoint /classify Funcional [TODO]

**Objetivo**: Conectar todos os componentes no endpoint principal

**Tarefas**:
- [ ] Implementar validação de arquivo
- [ ] Implementar processamento completo
- [ ] Conectar layout_analyzer + heuristic_classifier
- [ ] Extrair e retornar document_metadata
- [ ] Implementar tratamento de erros
- [ ] Adicionar logging estruturado
- [ ] Testes de integração

**Fluxo de Processamento**:
```
1. Receber arquivo (multipart/form-data)
   ↓
2. Validar formato e tamanho
   ↓
3. Converter PDF → imagem (se necessário)
   ↓
4. LayoutAnalyzer.analyze(image) → LayoutFeatures
   ↓
5. HeuristicClassifier.classify(features) → ClassificationResult
   ↓
6. Montar DocumentMetadata
   ↓
7. Retornar ClassificationResponse
```

**Critérios de Aceitação**:
- Endpoint /classify funciona end-to-end
- Retorna JSON conforme schema Pydantic
- Trata erros graciosamente
- Tempo total: < 10s por documento

**Prioridade**: CRÍTICA
**Estimativa**: 1 dia (integração)

---

## Sprint 2: Integração LLM (Estimativa: 3 dias)

### 2.1 Integração com Anthropic Claude [TODO]

**Objetivo**: Adicionar LLM para validação e análise complementar

**Tarefas**:
- [ ] Criar service class (services/llm_service.py)
- [ ] Implementar cliente Anthropic API
- [ ] Criar prompt para classificação de documentos
- [ ] Implementar extração de resposta estruturada
- [ ] Calcular custos (tokens × preço)
- [ ] Implementar retry logic
- [ ] Implementar timeout
- [ ] Testes unitários

**Arquivos a Criar**:
```
app/services/
├── llm_service.py       # Cliente LLM genérico
├── llm_anthropic.py     # Implementação Anthropic
└── llm_openai.py        # Implementação OpenAI (futuro)
```

**Prompt Template**:
```python
CLASSIFICATION_PROMPT = """
Analise o documento fornecido e classifique-o em uma das categorias:

{categories}

Informações extraídas do layout:
- Número de parágrafos: {num_paragraphs}
- Densidade de texto: {text_density:.2%}
- Figuras: {num_figures}, Tabelas: {num_tables}, Equações: {num_equations}

Retorne APENAS um JSON com:
{{
  "predicted_type": "tipo_mais_provavel",
  "confidence": 0.0-1.0,
  "reasoning": "breve explicação"
}}
"""
```

**Critérios de Aceitação**:
- LLM retorna classificação estruturada
- Metadados de uso são calculados corretamente
- Custos são rastreados (tokens × preço)
- Fallback para heurísticas se LLM falhar

**Prioridade**: ALTA
**Estimativa**: 2 dias

---

### 2.2 Modo Híbrido: Heurísticas + LLM [TODO]

**Objetivo**: Combinar classificador heurístico com validação por LLM

**Tarefas**:
- [ ] Implementar estratégia de ensemble
- [ ] Se confidence < threshold → usar LLM
- [ ] Combinar scores (weighted average)
- [ ] Comparar predições (heurística vs LLM)
- [ ] Adicionar flag `use_llm` no endpoint
- [ ] Documentar quando LLM é acionado

**Estratégias de Ensemble**:
```python
# Opção 1: LLM como validador
if heuristic_confidence < 0.7:
    llm_result = await llm_service.classify(document)
    final_result = combine_predictions(heuristic_result, llm_result)

# Opção 2: Votação ponderada
final_score = (
    heuristic_score * 0.6 +
    llm_score * 0.4
)

# Opção 3: LLM apenas para casos ambíguos
top2_diff = heuristic_scores[0] - heuristic_scores[1]
if top2_diff < 0.1:
    llm_result = await llm_service.classify(document)
```

**Critérios de Aceitação**:
- Modo `use_llm=True` funciona corretamente
- LLMMetadata é retornado quando LLM é usado
- Ensemble melhora acurácia em casos ambíguos
- Custos são rastreados corretamente

**Prioridade**: ALTA
**Estimativa**: 1 dia

---

## Sprint 3: Otimizações e Produção (Estimativa: 4 dias)

### 3.1 Sistema de Cache [TODO]

**Objetivo**: Implementar cache para evitar reprocessamento

**Tarefas**:
- [ ] Implementar cache em memória (Redis ou similar)
- [ ] Gerar hash de arquivo (MD5/SHA256)
- [ ] Cache de resultados de classificação
- [ ] Cache de análise de layout
- [ ] TTL configurável
- [ ] Endpoint para invalidar cache
- [ ] Métricas de hit rate

**Arquivos a Criar**:
```
app/core/
├── cache.py         # Sistema de cache
└── config.py        # Configurações (Redis URL, TTL, etc)
```

**Critérios de Aceitação**:
- Documentos idênticos retornam resultado cacheado
- Cache hit < 50ms
- Configurável via variáveis de ambiente
- Métricas disponíveis

**Prioridade**: MÉDIA
**Estimativa**: 1 dia

---

### 3.2 Processamento em Lote [TODO]

**Objetivo**: Suportar classificação de múltiplos documentos

**Tarefas**:
- [ ] Implementar endpoint /classify/batch
- [ ] Processar documentos em paralelo
- [ ] Limitar concorrência (max 10 simultâneos)
- [ ] Retornar resultados parciais se algum falhar
- [ ] Adicionar barra de progresso (opcional)
- [ ] Testes de carga

**Endpoint**:
```python
@app.post("/classify/batch")
async def classify_batch(
    files: List[UploadFile],
    use_llm: bool = False
) -> List[ClassificationResponse]:
    # Processar em paralelo com asyncio.gather
    results = await asyncio.gather(*[
        classify_single(file, use_llm)
        for file in files
    ], return_exceptions=True)
    return results
```

**Critérios de Aceitação**:
- Processa até 50 documentos por requisição
- Processamento paralelo
- Retorna resultados mesmo se alguns falharem
- Tempo: ~10s para 10 documentos

**Prioridade**: MÉDIA
**Estimativa**: 1 dia

---

### 3.3 Monitoramento e Observabilidade [TODO]

**Objetivo**: Adicionar logging, métricas e tracing

**Tarefas**:
- [ ] Implementar logging estruturado (JSON)
- [ ] Adicionar métricas Prometheus
- [ ] Instrumentar endpoints com OpenTelemetry
- [ ] Criar dashboard Grafana
- [ ] Alertas para erros e latência
- [ ] Exportar logs para CloudWatch/Datadog

**Métricas a Rastrear**:
```python
# Contadores
- total_requests
- successful_classifications
- failed_classifications
- llm_calls
- cache_hits / cache_misses

# Histogramas
- request_duration_seconds
- document_size_bytes
- llm_latency_seconds
- processing_time_ms

# Gauges
- active_requests
- models_loaded
- cache_size
```

**Critérios de Aceitação**:
- Logs estruturados em JSON
- Métricas exportadas no formato Prometheus
- Dashboard funcional
- Alertas configurados

**Prioridade**: MÉDIA
**Estimativa**: 2 dias

---

### 3.4 Testes e Documentação [TODO]

**Objetivo**: Garantir qualidade e facilitar uso

**Tarefas**:
- [ ] Testes unitários (> 80% cobertura)
- [ ] Testes de integração
- [ ] Testes de carga (Locust)
- [ ] Documentação de API (OpenAPI/Swagger)
- [ ] README completo
- [ ] Exemplos de uso (Python, cURL, Postman)
- [ ] Guia de deploy

**Estrutura de Testes**:
```
tests/
├── unit/
│   ├── test_schemas.py
│   ├── test_layout_analyzer.py
│   ├── test_classifier.py
│   └── test_llm_service.py
├── integration/
│   ├── test_endpoints.py
│   └── test_full_pipeline.py
└── load/
    └── locustfile.py
```

**Critérios de Aceitação**:
- Cobertura de testes > 80%
- Documentação completa e clara
- Exemplos funcionais
- Guia de deploy testado

**Prioridade**: ALTA
**Estimativa**: 2 dias (distribuído)

---

## Sprint 4: Features Avançadas (Estimativa: 5 dias)

### 4.1 Suporte a Múltiplos Idiomas [TODO]

**Objetivo**: Classificar documentos em português, inglês, espanhol

**Tarefas**:
- [ ] Detectar idioma do documento
- [ ] Ajustar prompts de LLM por idioma
- [ ] Suportar nomes de categorias em múltiplos idiomas
- [ ] Retornar metadados de idioma

**Prioridade**: BAIXA
**Estimativa**: 2 dias

---

### 4.2 OCR Opcional [TODO]

**Objetivo**: Extrair texto de documentos escaneados

**Tarefas**:
- [ ] Integrar Tesseract ou AWS Textract
- [ ] Extrair texto completo
- [ ] Usar texto para melhorar classificação
- [ ] Análise de palavras-chave

**Prioridade**: BAIXA
**Estimativa**: 3 dias

---

### 4.3 Fine-tuning do Modelo [TODO]

**Objetivo**: Melhorar acurácia com dados específicos

**Tarefas**:
- [ ] Coletar dataset anotado (500+ por categoria)
- [ ] Treinar Random Forest com features
- [ ] Validação cruzada
- [ ] Comparar com heurísticas
- [ ] Deploy de modelo treinado

**Prioridade**: BAIXA
**Estimativa**: 1 semana (fora do sprint)

---

## Backlog de Bugs/Melhorias

### Bugs Conhecidos

Nenhum bug conhecido ainda (projeto novo)

---

### Melhorias Futuras

1. **Suporte a mais formatos**: DOC, DOCX, HTML
2. **Autenticação**: JWT tokens, API keys
3. **Rate limiting**: Limitar requisições por usuário
4. **Webhooks**: Notificar quando classificação estiver pronta
5. **UI Web**: Interface simples para upload e teste
6. **Marketplace**: Permitir modelos customizados de terceiros

---

## Definição de Pronto (Definition of Done)

Uma tarefa está pronta quando:

- [ ] Código implementado e revisado
- [ ] Testes unitários escritos e passando
- [ ] Testes de integração (se aplicável)
- [ ] Documentação atualizada
- [ ] Code review aprovado
- [ ] Deploy em ambiente de staging OK
- [ ] Validado pelo PO/Stakeholder

---

## Priorização

**Legenda**:
- **CRÍTICA**: Necessário para MVP funcionar
- **ALTA**: Importante para produção
- **MÉDIA**: Melhora experiência/performance
- **BAIXA**: Nice to have

---

## Estimativas Totais

| Sprint | Dias | Status |
|--------|------|--------|
| Sprint 1: Fundação e MVP | 5 dias | 20% concluído |
| Sprint 2: Integração LLM | 3 dias | Não iniciado |
| Sprint 3: Otimizações | 4 dias | Não iniciado |
| Sprint 4: Features Avançadas | 5 dias | Não iniciado |
| **TOTAL** | **17 dias** | - |

---

## Dependências Externas

1. **DocLayout-YOLO**: Modelo já treinado e disponível
2. **Anthropic API**: API key necessária
3. **Infraestrutura**: Docker, Redis, PostgreSQL (opcional)
4. **Dataset RVL-CDIP**: Disponível para testes

---

## Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Custos de LLM muito altos | MÉDIA | ALTO | Implementar cache agressivo, usar heurísticas como padrão |
| Performance lenta em PDFs grandes | MÉDIA | MÉDIO | Limitar tamanho máximo, otimizar conversão |
| Acurácia baixa para algumas categorias | ALTA | MÉDIO | Coletar mais dados, ajustar heurísticas, treinar ML |
| Latência alta da API | BAIXA | ALTO | Implementar cache, processamento assíncrono |

---

## Próximos Passos Imediatos

1. [ ] Criar `requirements.txt` com dependências
2. [ ] Criar `Dockerfile` e `docker-compose.yml`
3. [ ] Implementar `app/services/layout_analyzer.py`
4. [ ] Implementar `app/services/heuristic_classifier.py`
5. [ ] Testar endpoint `/classify` end-to-end

---

**Última Atualização**: 25 de outubro de 2025
**Responsável**: Equipe de Desenvolvimento
**Status**: Sprint 1 em andamento (20% concluído)
