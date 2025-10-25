# Guia de Integração Backend - API de Análise de Documentos

Última atualização: 2025-10-25

## Status do Servidor

O servidor está rodando em **http://localhost:8000** e pronto para receber requisições!

### Endpoints Disponíveis

- **Swagger UI** (Documentação Interativa): http://localhost:8000/docs
- **ReDoc** (Documentação Visual): http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

---

## Endpoints da API

### 1. Análise Completa (UC1-UC4)

Executa análise completa do documento científico incluindo:
- UC1: Classificação (é artigo científico?)
- UC2: Detecção de parágrafos com docling
- UC3: Análise textual e contagem de palavras
- UC4: Relatório de conformidade (2000 palavras, 8 parágrafos)

**Endpoint:** `POST /api/v1/analyze`

**Request:**
```javascript
// JavaScript/React
const formData = new FormData();
formData.append('file', arquivoSelecionado);

const response = await fetch('http://localhost:8000/api/v1/analyze', {
  method: 'POST',
  body: formData,
  // CORS está configurado - não precisa de headers adicionais
});

const resultado = await response.json();
```

**cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "file=@documento.pdf"
```

**Formatos Aceitos:**
- PDF: `.pdf`
- Imagens: `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`

**Tempo de Processamento Esperado:**
- Aproximadamente 30-45 segundos por documento
- Depende do tamanho e complexidade do documento

**Response (200 OK):**
```json
{
  "document_id": "ff1dc290-9e31-45b2-8d32-29efe1dfe416",
  "filename": "artigo.pdf",
  "is_scientific_paper": true,
  "classification_confidence": 1.0,

  "paragraphs": [
    {
      "index": 0,
      "text": "Este estudo apresenta uma análise...",
      "word_count": 45,
      "bbox": {
        "x1": 93.33,
        "y1": 900.0,
        "x2": 626.33,
        "y2": 849.33
      },
      "confidence": 1.0
    }
  ],

  "text_analysis": {
    "total_words": 533,
    "unique_words": 403,
    "word_frequencies": {
      "análise": 45,
      "dados": 32,
      "sistema": 28
    },
    "top_words": [
      {
        "word": "análise",
        "count": 45
      },
      {
        "word": "dados",
        "count": 32
      }
    ]
  },

  "compliance": {
    "is_compliant": false,
    "words_compliant": false,
    "paragraphs_compliant": false,
    "word_count": 533,
    "paragraph_count": 7,
    "word_difference": -1467,
    "paragraph_difference": -1,
    "recommended_actions": [
      "Adicionar 1467 palavras para atingir o mínimo de 2000",
      "Adicionar 1 parágrafo(s) para atingir exatamente 8"
    ]
  },

  "compliance_report_markdown": "# UC4 - Resumo de Conformidade do Texto\n\n...",
  "analyzed_at": "2025-10-25T17:28:41.138204",
  "processing_time_ms": 39043.75
}
```

---

### 2. Classificação Simples (UC1)

Executa apenas a classificação do documento (mais rápido).

**Endpoint:** `POST /api/v1/classify`

**Request:**
```javascript
const formData = new FormData();
formData.append('file', arquivoSelecionado);

const response = await fetch('http://localhost:8000/api/v1/classify', {
  method: 'POST',
  body: formData
});

const resultado = await response.json();
```

**Response (200 OK):**
```json
{
  "filename": "artigo.pdf",
  "is_scientific_paper": true,
  "confidence": 0.95
}
```

---

### 3. Health Check

Verifica se a API está operacional.

**Endpoint:** `GET /api/v1/health`

**Request:**
```javascript
const response = await fetch('http://localhost:8000/api/v1/health');
const status = await response.json();
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "Document Analysis API",
  "version": "1.0.0"
}
```

---

## Modelos de Dados

### AnalysisResult (Resposta Principal)

```typescript
interface AnalysisResult {
  document_id: string;                    // UUID do documento
  filename: string;                       // Nome do arquivo original
  is_scientific_paper: boolean;           // UC1: É artigo científico?
  classification_confidence: number;      // 0.0 a 1.0
  paragraphs: Paragraph[];                // UC2: Parágrafos detectados
  text_analysis: TextAnalysis;            // UC3: Análise textual
  compliance: ComplianceResult;           // UC4: Conformidade
  compliance_report_markdown: string;     // UC4: Relatório em Markdown
  analyzed_at: string;                    // ISO 8601 timestamp
  processing_time_ms: number;             // Tempo de processamento
}
```

### Paragraph

```typescript
interface Paragraph {
  index: number;                          // Índice sequencial (0-based)
  text: string;                           // Texto do parágrafo
  word_count: number;                     // Número de palavras
  bbox?: BoundingBox;                     // Posição no documento (opcional)
  confidence: number;                     // Confiança da detecção (0.0 a 1.0)
}

interface BoundingBox {
  x1: number;                             // Coordenada X esquerda
  y1: number;                             // Coordenada Y superior
  x2: number;                             // Coordenada X direita
  y2: number;                             // Coordenada Y inferior
}
```

### TextAnalysis

```typescript
interface TextAnalysis {
  total_words: number;                    // Total de palavras no documento
  unique_words: number;                   // Palavras únicas (vocabulário)
  word_frequencies: Record<string, number>; // {"palavra": frequência}
  top_words: WordFrequency[];             // Top 10 palavras mais frequentes
}

interface WordFrequency {
  word: string;                           // A palavra
  count: number;                          // Número de ocorrências
}
```

### ComplianceResult

```typescript
interface ComplianceResult {
  is_compliant: boolean;                  // Conforme com TODAS as regras?
  words_compliant: boolean;               // >= 2000 palavras?
  paragraphs_compliant: boolean;          // == 8 parágrafos?
  word_count: number;                     // Contagem atual de palavras
  paragraph_count: number;                // Contagem atual de parágrafos
  word_difference: number;                // Diferença em relação a 2000 (+/-)
  paragraph_difference: number;           // Diferença em relação a 8 (+/-)
  recommended_actions: string[];          // Ações para ficar conforme
}
```

---

## Códigos HTTP e Tratamento de Erros

| Código | Situação | Significado | Ação Frontend |
|--------|----------|-------------|---------------|
| **200** | Sucesso | Análise concluída com sucesso | Exibir resultados ao usuário |
| **400** | Bad Request | Formato de arquivo não suportado | Alertar: "Formato inválido. Use PDF, PNG, JPG ou TIFF" |
| **422** | Unprocessable Entity | Documento não é artigo científico | Informar: "Este documento não foi identificado como artigo científico" |
| **500** | Internal Server Error | Erro no processamento | Tentar novamente ou contatar suporte |

### Estrutura de Erro

```typescript
interface ErrorResponse {
  error: boolean;                         // Sempre true
  error_type: string;                     // "http_error" | "validation_error"
  errors: ErrorDetail[];                  // Lista de erros
  request_id: string;                     // ID da requisição (para debug)
  timestamp: string;                      // ISO 8601 timestamp
}

interface ErrorDetail {
  code: string;                           // Ex: "HTTP_400", "HTTP_500"
  message: string;                        // Mensagem de erro
  field?: string;                         // Campo relacionado (opcional)
  details?: any;                          // Detalhes adicionais (opcional)
}
```

**Exemplo de Erro:**
```json
{
  "error": true,
  "error_type": "http_error",
  "errors": [
    {
      "code": "HTTP_400",
      "message": "Formato não suportado: doc. Use: pdf, png, jpg, jpeg, tiff, tif",
      "field": null,
      "details": null
    }
  ],
  "request_id": "req_292feab6611b46f1",
  "timestamp": "2025-10-25T20:21:43.450766"
}
```

---

## CORS (Cross-Origin Resource Sharing)

A API está configurada para aceitar requisições de:
- `http://localhost:3000`
- `http://localhost:3001`
- `http://localhost:3002`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:3001`
- `http://127.0.0.1:3002`

Todos os métodos (GET, POST, PUT, DELETE, OPTIONS, PATCH) e headers estão permitidos.

---

## Exemplo de Integração React

```typescript
import { useState } from 'react';

interface AnalysisResult {
  // Use os tipos definidos acima
}

function DocumentAnalyzer() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileUpload = async (file: File) => {
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.errors[0]?.message || 'Erro na análise');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {loading && <p>Processando documento... (pode levar até 45s)</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {result && (
        <div>
          <h2>Resultado da Análise</h2>
          <p>Artigo Científico: {result.is_scientific_paper ? 'Sim' : 'Não'}</p>
          <p>Palavras: {result.text_analysis.total_words}</p>
          <p>Parágrafos: {result.paragraphs.length}</p>
          <p>Conforme: {result.compliance.is_compliant ? 'Sim' : 'Não'}</p>

          {!result.compliance.is_compliant && (
            <div>
              <h3>Ações Recomendadas:</h3>
              <ul>
                {result.compliance.recommended_actions.map((action, i) => (
                  <li key={i}>{action}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

---

## Indicadores de UX Recomendados

### Durante o Upload/Processamento
- Mostrar barra de progresso ou spinner
- Exibir mensagem: "Processando documento... (pode levar até 45 segundos)"
- Desabilitar botão de envio durante processamento

### Feedback de Sucesso
- Exibir badge verde se `is_scientific_paper: true`
- Mostrar métricas principais:
  - Total de palavras
  - Número de parágrafos
  - Status de conformidade
- Permitir visualização do relatório markdown

### Feedback de Não Conformidade
- Destacar em amarelo/laranja se `is_compliant: false`
- Listar `recommended_actions` de forma clara
- Mostrar diferenças:
  - "Faltam X palavras" se `word_difference < 0`
  - "Faltam/Sobram Y parágrafos" se `paragraph_difference != 0`

### Feedback de Erro
- Erro 400: "Formato de arquivo não suportado. Use PDF, PNG, JPG ou TIFF"
- Erro 422: "Este documento não foi identificado como artigo científico"
- Erro 500: "Erro ao processar documento. Tente novamente"

---

## Checklist de Implementação Frontend

- [ ] Implementar upload de arquivo (multipart/form-data)
- [ ] Validar formato no frontend (PDF, PNG, JPG, JPEG, TIFF)
- [ ] Mostrar indicador de loading durante processamento
- [ ] Tratar timeout (requisições podem levar 30-45s)
- [ ] Implementar tratamento de erros HTTP (400, 422, 500)
- [ ] Exibir resultados de forma clara e organizada
- [ ] Mostrar `recommended_actions` quando `is_compliant: false`
- [ ] Renderizar `compliance_report_markdown` (opcional)
- [ ] Implementar health check para verificar status da API
- [ ] Testar com diferentes tipos de arquivo
- [ ] Testar com documentos científicos e não-científicos

---

## Recursos Adicionais

### Documentação Completa
- Arquivo: `API_FRONTEND_GUIDE.md` no diretório raiz do backend
- Contém exemplos detalhados em cURL, JavaScript e Python

### Arquitetura do Sistema
- Arquivo: `ARCHITECTURE_PLAN.md`
- Explica a arquitetura completa do sistema (UC1-UC4)

### Correções de Dependências
- Arquivo: `DEPENDENCY_FIX.md`
- Documenta ajustes necessários no ambiente Python

---

## Notas Importantes

1. **Tempo de Processamento**: O processamento pode levar 30-45 segundos. Configure timeouts adequados nas requisições.

2. **Tamanho de Arquivo**: Não há limite explícito, mas arquivos muito grandes podem demorar mais.

3. **TIFF Support**: Arquivos TIFF são enviados como `application/octet-stream` pelo navegador. A API detecta automaticamente pela extensão.

4. **BoundingBox**: As coordenadas são relativas ao documento original. Útil para destacar parágrafos na visualização.

5. **Confidence**: Valores de `confidence` próximos a 1.0 indicam alta confiança na detecção.

6. **Word Frequencies**: Contém TODAS as palavras do documento. Use `top_words` para exibir as mais frequentes.

7. **Markdown Report**: O campo `compliance_report_markdown` contém um relatório formatado pronto para exibição.

---

## Suporte e Dúvidas

- Swagger UI para testes: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health
- Logs do servidor: Verificar console onde o uvicorn está rodando
