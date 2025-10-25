# Planejamento de Arquitetura - Sistema de Análise de Documentos Científicos

## Visão Geral da Arquitetura

Com base nos casos de uso especificados, proponho uma arquitetura em camadas com separação clara de responsabilidades:

```
┌─────────────────────────────────────────────┐
│         API Layer (FastAPI)                  │
│  - Endpoints REST para upload e análise      │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│      Orchestration Layer                     │
│  - DocumentAnalysisOrchestrator              │
│  - Coordena fluxo UC1 → UC2 → UC3 → UC4     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         Service Layer                        │
│  UC1: DocumentClassificationService          │
│  UC2: ParagraphDetectionService (docling)    │
│  UC3: TextAnalysisService                    │
│  UC4: ComplianceReportService                │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         Integration Layer                    │
│  - External API Client (classificação)       │
│  - Docling Integration                       │
└─────────────────────────────────────────────┘
```

## Estrutura de Diretórios Proposta

```
doc_services/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py              # Configurações centralizadas
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── document.py            # Modelo do documento
│   │   ├── analysis_result.py     # Resultado da análise
│   │   ├── paragraph.py           # Modelo de parágrafo
│   │   └── compliance_report.py   # Modelo do relatório UC4
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── classification_service.py  # UC1
│   │   ├── paragraph_service.py       # UC2 (docling)
│   │   ├── text_analysis_service.py   # UC3
│   │   ├── compliance_service.py      # UC4
│   │   └── orchestrator.py            # Coordenador principal
│   │
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── classification_api.py  # Cliente API externa UC1
│   │   └── docling_wrapper.py     # Wrapper para docling UC2
│   │
│   ├── templates/
│   │   └── compliance_report.md   # Template do relatório UC4
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py              # Endpoints REST
│   │   └── dependencies.py        # Dependências FastAPI
│   │
│   └── main.py                    # Entry point FastAPI
│
├── tests/
│   ├── test_classification.py
│   ├── test_paragraph_detection.py
│   ├── test_text_analysis.py
│   └── test_compliance.py
│
├── requirements.txt
└── README.md
```

## Detalhamento por Camada

### 1. **API Layer** (FastAPI)

**Responsabilidade**: Expor endpoints HTTP para recebimento de documentos e retorno de análises.

**Endpoints principais**:
```python
POST /api/v1/analyze
    - Recebe: arquivo (PDF ou imagem)
    - Retorna: análise completa (todos os UCs)

POST /api/v1/classify
    - Recebe: arquivo
    - Retorna: apenas classificação (UC1)

GET /api/v1/health
    - Health check do serviço
```

**Justificativa educativa**: FastAPI oferece validação automática, documentação Swagger/OpenAPI e performance assíncrona.

### 2. **Orchestration Layer**

**Classe principal**: `DocumentAnalysisOrchestrator`

**Responsabilidade**: Coordenar a execução sequencial dos casos de uso com tratamento de erros.

**Fluxo de execução**:
```python
async def analyze_document(file: UploadFile) -> AnalysisResult:
    # UC1: Classificação
    if not await classification_service.is_scientific_paper(file):
        raise InvalidDocumentError("Documento não é artigo científico")

    # UC2: Detecção de parágrafos
    paragraphs = await paragraph_service.detect_paragraphs(file)

    # UC3: Análise de texto
    text_analysis = await text_service.analyze_text(paragraphs)

    # UC4: Relatório de conformidade
    report = await compliance_service.generate_report(
        paragraphs, text_analysis
    )

    return AnalysisResult(...)
```

**Justificativa educativa**: O padrão Orchestrator centraliza a lógica de negócio complexa, facilitando manutenção e testes.

### 3. **Service Layer** - Detalhamento por UC

#### **UC1: DocumentClassificationService**

**Constraint**: Usar serviço API já implementado

**Responsabilidades**:
- Chamar API externa de classificação
- Validar se documento é artigo científico
- Tratar erros de comunicação

**Tecnologias**: httpx (cliente HTTP assíncrono)

```python
class DocumentClassificationService:
    async def is_scientific_paper(self, file: bytes) -> bool:
        # Chama API externa existente
        # Retorna True se for artigo científico
```

#### **UC2: ParagraphDetectionService**

**Constraint**: Usar docling

**Responsabilidades**:
- Integrar com biblioteca docling
- Detectar parágrafos no documento
- Retornar lista estruturada de parágrafos

**Tecnologias**: docling

```python
class ParagraphDetectionService:
    async def detect_paragraphs(self, file: bytes) -> List[Paragraph]:
        # Usa docling para análise de layout
        # Extrai parágrafos estruturados
        # Retorna lista com texto e metadados
```

**Justificativa educativa**: Docling é especializado em análise de layout de documentos, oferecendo detecção precisa de estruturas.

#### **UC3: TextAnalysisService**

**Constraint**: Técnica básica de programação

**Responsabilidades**:
- Extrair texto dos parágrafos
- Contar palavras totais
- Calcular frequência de palavras

**Tecnologias**: Python stdlib (Counter, re)

```python
class TextAnalysisService:
    def extract_and_analyze(self, paragraphs: List[Paragraph]) -> TextAnalysis:
        # Concatena textos
        # Tokeniza palavras (regex simples)
        # Usa Counter para frequências
        # Retorna estatísticas
```

**Justificativa educativa**: Demonstra uso de estruturas de dados nativas do Python (dict, Counter) para análise textual básica.

#### **UC4: ComplianceReportService**

**Constraint**: Programação básica com template fornecido

**Responsabilidades**:
- Validar regras (≥2000 palavras, =8 parágrafos)
- Calcular diferenças e ações recomendadas
- Renderizar template markdown

**Tecnologias**: Jinja2 ou string.Template

```python
class ComplianceReportService:
    def generate_report(
        self,
        paragraph_count: int,
        word_count: int,
        file_name: str
    ) -> str:
        # Valida regras
        # Calcula métricas
        # Preenche template
        # Retorna markdown
```

**Justificativa educativa**: Templates permitem separar lógica de apresentação, facilitando manutenção.

## Modelos de Dados

### Document
```python
class Document:
    id: str
    filename: str
    content: bytes
    mime_type: str
    uploaded_at: datetime
```

### Paragraph
```python
class Paragraph:
    index: int
    text: str
    word_count: int
    bbox: Optional[BoundingBox]  # Coordenadas do docling
```

### TextAnalysis
```python
class TextAnalysis:
    total_words: int
    word_frequencies: Dict[str, int]
    top_words: List[Tuple[str, int]]
```

### ComplianceReport
```python
class ComplianceReport:
    file_name: str
    document_id: Optional[str]
    analysis_datetime: datetime
    word_count: int
    paragraph_count: int
    is_compliant: bool
    words_compliant: bool
    paragraphs_compliant: bool
    recommended_actions: List[str]
    report_markdown: str
```

## Fluxo de Dados Completo

```
1. Cliente envia PDF/imagem → POST /api/v1/analyze

2. API valida arquivo → passa para Orchestrator

3. Orchestrator executa:

   3.1 UC1 → ClassificationService
       ├─→ Chama API externa
       └─→ Se não for científico: PARA e retorna erro

   3.2 UC2 → ParagraphDetectionService
       ├─→ Usa docling para análise
       └─→ Retorna List[Paragraph]

   3.3 UC3 → TextAnalysisService
       ├─→ Extrai texto dos parágrafos
       ├─→ Conta palavras
       └─→ Calcula frequências

   3.4 UC4 → ComplianceReportService
       ├─→ Valida regras (2000 palavras, 8 parágrafos)
       ├─→ Calcula ações recomendadas
       └─→ Renderiza template markdown

4. Orchestrator consolida resultados → AnalysisResult

5. API retorna JSON com:
   - Classificação
   - Parágrafos detectados
   - Análise textual
   - Relatório de conformidade
```

## Configuração e Dependências

### requirements.txt principais
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
docling>=1.0.0
httpx>=0.25.0
jinja2>=3.1.2
pydantic>=2.0.0
python-dotenv>=1.0.0
```

### Variáveis de ambiente (.env)
```
# UC1 - API Externa
CLASSIFICATION_API_URL=https://...
CLASSIFICATION_API_KEY=...

# Aplicação
APP_ENV=development
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=10
```

## Considerações de Implementação

1. **Validação de entrada**: Limitar tipos de arquivo (PDF, TIFF, PNG, JPG) e tamanho máximo

2. **Tratamento de erros**: Cada serviço deve ter exceções específicas para facilitar debugging

3. **Logging**: Usar logging estruturado para rastrear fluxo de execução

4. **Testes**: Cada UC deve ter testes unitários independentes

5. **Documentação**: Docstrings detalhadas para fins educativos

6. **Performance**: UC2 (docling) pode ser lento - considerar processamento assíncrono

## Próximos Passos

1. Configurar estrutura de diretórios
2. Implementar modelos de dados (Pydantic)
3. Implementar cada serviço isoladamente (UC1 → UC2 → UC3 → UC4)
4. Criar orchestrator
5. Implementar API endpoints
6. Adicionar testes
7. Documentar uso com exemplos

---

Este planejamento fornece uma base sólida e modular, respeitando todas as constraints especificadas e permitindo evolução incremental do sistema.
