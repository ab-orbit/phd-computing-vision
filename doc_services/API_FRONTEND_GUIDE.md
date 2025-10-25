# Guia de Integração Frontend - API de Análise de Documentos

## Visão Geral

A API está rodando em: **http://localhost:8000**

Documentação interativa disponível em:
- Swagger UI: **http://localhost:8000/docs**
- ReDoc: **http://localhost:8000/redoc**

---

## Endpoints Disponíveis

### 1. Health Check
### 2. Análise Completa (Recomendado)
### 3. Classificação Simples

---

## 1. Health Check

**Verifica se a API está operacional**

### Especificações
- **URL**: `http://localhost:8000/api/v1/health`
- **Método**: `GET`
- **Autenticação**: Não requerida
- **Content-Type**: Não aplicável

### Resposta
```json
{
  "status": "healthy",
  "service": "Document Analysis API",
  "version": "1.0.0"
}
```

### Exemplo cURL
```bash
curl http://localhost:8000/api/v1/health
```

### Exemplo JavaScript (fetch)
```javascript
async function checkHealth() {
  const response = await fetch('http://localhost:8000/api/v1/health');
  const data = await response.json();
  console.log('Status:', data.status);
}
```

---

## 2. Análise Completa de Documento (PRINCIPAL)

**Executa análise completa com todos os casos de uso (UC1-UC4)**

### Especificações
- **URL**: `http://localhost:8000/api/v1/analyze`
- **Método**: `POST`
- **Content-Type**: `multipart/form-data`
- **Autenticação**: Não requerida

### Parâmetros da Requisição

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `file` | File | Sim | Arquivo do documento (PDF ou imagem) |

### Formatos Aceitos
- PDF: `.pdf`
- Imagens: `.png`, `.jpg`, `.jpeg`, `.tiff`, `.tif`

### Tamanho Máximo
Recomendado: até 10MB (configurável no servidor)

---

### Resposta de Sucesso (200 OK)

```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "artigo_cientifico.pdf",
  "is_scientific_paper": true,
  "classification_confidence": 0.95,
  "paragraphs": [
    {
      "index": 0,
      "text": "Este estudo apresenta uma análise detalhada sobre...",
      "word_count": 45,
      "confidence": 0.98
    },
    {
      "index": 1,
      "text": "A metodologia aplicada consiste em...",
      "word_count": 52,
      "confidence": 0.97
    }
  ],
  "text_analysis": {
    "total_words": 2534,
    "unique_words": 678,
    "word_frequencies": {
      "análise": 45,
      "dados": 32,
      "sistema": 28,
      "pesquisa": 25
    },
    "top_words": [
      {"word": "análise", "count": 45},
      {"word": "dados", "count": 32},
      {"word": "sistema", "count": 28},
      {"word": "pesquisa", "count": 25},
      {"word": "resultados", "count": 22}
    ]
  },
  "compliance": {
    "is_compliant": true,
    "words_compliant": true,
    "paragraphs_compliant": true,
    "word_count": 2534,
    "paragraph_count": 8,
    "word_difference": 534,
    "paragraph_difference": 0,
    "recommended_actions": []
  },
  "compliance_report_markdown": "# UC4 — Resumo de Conformidade do Texto\n\n**Arquivo:** artigo_cientifico.pdf...",
  "analyzed_at": "2025-10-25T14:30:00.123456",
  "processing_time_ms": 3452.5
}
```

### Estrutura da Resposta (Explicação Detalhada)

#### Campos Principais

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `document_id` | string | ID único gerado para este documento |
| `filename` | string | Nome original do arquivo enviado |
| `is_scientific_paper` | boolean | **UC1**: true se for artigo científico |
| `classification_confidence` | float | Confiança da classificação (0.0 a 1.0) |
| `paragraphs` | array | **UC2**: Lista de parágrafos detectados |
| `text_analysis` | object | **UC3**: Análise estatística do texto |
| `compliance` | object | **UC4**: Verificação de conformidade |
| `compliance_report_markdown` | string | **UC4**: Relatório em formato Markdown |
| `analyzed_at` | datetime | Timestamp da análise |
| `processing_time_ms` | float | Tempo total em milissegundos |

#### Objeto `paragraphs[]` (UC2)

Cada parágrafo contém:
```json
{
  "index": 0,           // Posição do parágrafo no documento
  "text": "...",        // Texto completo do parágrafo
  "word_count": 45,     // Número de palavras
  "confidence": 0.98    // Confiança da detecção (0.0 a 1.0)
}
```

#### Objeto `text_analysis` (UC3)

```json
{
  "total_words": 2534,              // Total de palavras no documento
  "unique_words": 678,               // Vocabulário (palavras únicas)
  "word_frequencies": {              // Dicionário: palavra → frequência
    "análise": 45,
    "dados": 32
  },
  "top_words": [                     // Top 10 palavras mais frequentes
    {"word": "análise", "count": 45}
  ]
}
```

#### Objeto `compliance` (UC4)

```json
{
  "is_compliant": true,              // True se TODAS as regras OK
  "words_compliant": true,           // >= 2000 palavras?
  "paragraphs_compliant": true,      // == 8 parágrafos?
  "word_count": 2534,                // Contagem atual
  "paragraph_count": 8,              // Contagem atual
  "word_difference": 534,            // Diferença vs 2000 (534 a mais)
  "paragraph_difference": 0,         // Diferença vs 8 (0 = exato)
  "recommended_actions": []          // Ações necessárias (vazio se conforme)
}
```

**Interpretação dos campos `*_difference`:**
- **Positivo**: Excesso (ex: 534 significa 534 palavras a mais que o mínimo)
- **Negativo**: Falta (ex: -150 significa falta 150 palavras)
- **Zero**: Exato

---

### Respostas de Erro

#### 400 Bad Request - Formato Inválido
```json
{
  "detail": "Formato não suportado: doc. Use: pdf, png, jpg, jpeg, tiff, tif"
}
```

#### 422 Unprocessable Entity - Documento Inválido
```json
{
  "detail": "Documento não é um artigo científico (UC1 falhou)"
}
```

**IMPORTANTE**: Este erro ocorre quando UC1 determina que o documento NÃO é um artigo científico. Neste caso, o processo para e os UCs 2-4 não são executados.

#### 500 Internal Server Error
```json
{
  "detail": "Erro interno: mensagem de erro detalhada"
}
```

---

## Exemplos de Implementação

### Exemplo 1: cURL (Terminal)

```bash
# Enviar PDF para análise completa
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "file=@/caminho/para/artigo.pdf" \
  -H "accept: application/json"

# Salvar resposta em arquivo
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "file=@/caminho/para/artigo.pdf" \
  -o resultado.json
```

### Exemplo 2: JavaScript (React / Next.js)

```javascript
async function analyzeDocument(file) {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('http://localhost:8000/api/v1/analyze', {
      method: 'POST',
      body: formData,
      // NÃO definir Content-Type, o browser faz automaticamente
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    const result = await response.json();

    console.log('Documento analisado:', result.filename);
    console.log('É científico?', result.is_scientific_paper);
    console.log('Total de palavras:', result.text_analysis.total_words);
    console.log('Conforme?', result.compliance.is_compliant);

    return result;

  } catch (error) {
    console.error('Erro na análise:', error.message);
    throw error;
  }
}

// Uso em componente React
function UploadComponent() {
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];

    if (!file) return;

    try {
      const result = await analyzeDocument(file);
      // Atualizar estado, mostrar resultados, etc.
      console.log('Resultado:', result);
    } catch (error) {
      alert('Erro: ' + error.message);
    }
  };

  return (
    <input
      type="file"
      accept=".pdf,.png,.jpg,.jpeg,.tiff,.tif"
      onChange={handleFileUpload}
    />
  );
}
```

### Exemplo 3: JavaScript (Vanilla - HTML puro)

```html
<!DOCTYPE html>
<html>
<head>
  <title>Análise de Documentos</title>
</head>
<body>
  <h1>Upload de Documento Científico</h1>

  <input type="file" id="fileInput" accept=".pdf,.png,.jpg,.jpeg,.tiff,.tif">
  <button onclick="uploadFile()">Analisar</button>

  <div id="result"></div>

  <script>
    async function uploadFile() {
      const fileInput = document.getElementById('fileInput');
      const file = fileInput.files[0];

      if (!file) {
        alert('Selecione um arquivo primeiro');
        return;
      }

      const formData = new FormData();
      formData.append('file', file);

      const resultDiv = document.getElementById('result');
      resultDiv.innerHTML = 'Analisando...';

      try {
        const response = await fetch('http://localhost:8000/api/v1/analyze', {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail);
        }

        const result = await response.json();

        // Mostrar resultados
        resultDiv.innerHTML = `
          <h2>Resultados</h2>
          <p><strong>Arquivo:</strong> ${result.filename}</p>
          <p><strong>É artigo científico?</strong> ${result.is_scientific_paper ? 'Sim' : 'Não'}</p>
          <p><strong>Total de palavras:</strong> ${result.text_analysis.total_words}</p>
          <p><strong>Parágrafos:</strong> ${result.compliance.paragraph_count}</p>
          <p><strong>Conforme?</strong> ${result.compliance.is_compliant ? 'Sim' : 'Não'}</p>

          ${!result.compliance.is_compliant ? `
            <h3>Ações Recomendadas:</h3>
            <ul>
              ${result.compliance.recommended_actions.map(action => `<li>${action}</li>`).join('')}
            </ul>
          ` : ''}

          <h3>Top 5 Palavras:</h3>
          <ol>
            ${result.text_analysis.top_words.slice(0, 5).map(w =>
              `<li>${w.word}: ${w.count} vezes</li>`
            ).join('')}
          </ol>
        `;

      } catch (error) {
        resultDiv.innerHTML = `<p style="color: red;">Erro: ${error.message}</p>`;
      }
    }
  </script>
</body>
</html>
```

### Exemplo 4: Python (requests)

```python
import requests

def analyze_document(file_path: str) -> dict:
    """
    Envia documento para análise completa.

    Args:
        file_path: Caminho para o arquivo PDF ou imagem

    Returns:
        Dicionário com resultado da análise
    """
    url = "http://localhost:8000/api/v1/analyze"

    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(url, files=files)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro {response.status_code}: {response.json()['detail']}")

# Uso
if __name__ == "__main__":
    try:
        result = analyze_document("artigo.pdf")

        print(f"Arquivo: {result['filename']}")
        print(f"É científico? {result['is_scientific_paper']}")
        print(f"Palavras: {result['text_analysis']['total_words']}")
        print(f"Parágrafos: {result['compliance']['paragraph_count']}")
        print(f"Conforme? {result['compliance']['is_compliant']}")

        if not result['compliance']['is_compliant']:
            print("\nAções recomendadas:")
            for action in result['compliance']['recommended_actions']:
                print(f"  - {action}")

    except Exception as e:
        print(f"Erro: {e}")
```

---

## 3. Classificação Simples (Opcional)

**Executa apenas UC1 - mais rápido**

### Especificações
- **URL**: `http://localhost:8000/api/v1/classify`
- **Método**: `POST`
- **Content-Type**: `multipart/form-data`

### Parâmetros
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `file` | File | Arquivo do documento |

### Resposta
```json
{
  "filename": "documento.pdf",
  "is_scientific_paper": true,
  "confidence": 0.95
}
```

### Quando usar?
- Quando você só precisa validar se é artigo científico
- Para pré-validação antes de análise completa
- Para economizar recursos de processamento

### Exemplo cURL
```bash
curl -X POST "http://localhost:8000/api/v1/classify" \
  -F "file=@documento.pdf"
```

### Exemplo JavaScript
```javascript
async function classifyOnly(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('http://localhost:8000/api/v1/classify', {
    method: 'POST',
    body: formData
  });

  return await response.json();
}
```

---

## Fluxo de Trabalho Recomendado

### Opção 1: Análise Direta (Simples)
```
1. Frontend: Usuário seleciona arquivo
2. Frontend: Envia para POST /api/v1/analyze
3. Backend: Executa UC1 → UC2 → UC3 → UC4
4. Frontend: Recebe e exibe resultados completos
```

### Opção 2: Validação + Análise (Otimizado)
```
1. Frontend: Usuário seleciona arquivo
2. Frontend: Envia para POST /api/v1/classify
3. Backend: Executa apenas UC1
4. Frontend: Se não for científico, exibe mensagem e PARA
5. Frontend: Se for científico, envia para POST /api/v1/analyze
6. Backend: Executa UC2 → UC3 → UC4 (UC1 já foi feito)
7. Frontend: Exibe resultados completos
```

**OBSERVAÇÃO**: Atualmente, mesmo na Opção 2, o endpoint `/analyze` re-executa UC1. Para otimização futura, pode-se implementar cache ou endpoint que recebe flag indicando que classificação já foi feita.

---

## Tratamento de Erros no Frontend

### Exemplo Completo
```javascript
async function analyzeWithErrorHandling(file) {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('http://localhost:8000/api/v1/analyze', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();

    switch(response.status) {
      case 200:
        // Sucesso
        return { success: true, data };

      case 400:
        // Formato inválido
        return {
          success: false,
          error: 'Formato de arquivo não suportado',
          detail: data.detail
        };

      case 422:
        // Documento não é científico
        return {
          success: false,
          error: 'Este documento não é um artigo científico',
          detail: data.detail
        };

      case 500:
        // Erro do servidor
        return {
          success: false,
          error: 'Erro no servidor. Tente novamente.',
          detail: data.detail
        };

      default:
        return {
          success: false,
          error: `Erro inesperado: ${response.status}`
        };
    }

  } catch (error) {
    // Erro de rede
    return {
      success: false,
      error: 'Erro de conexão com o servidor',
      detail: error.message
    };
  }
}
```

---

## CORS (Cross-Origin Resource Sharing)

A API está configurada com CORS habilitado para permitir requisições de diferentes origens.

**Configuração atual** (em `app/main.py`):
- Permite todas as origens (`origins=["*"]`)
- Métodos permitidos: GET, POST, PUT, DELETE, OPTIONS
- Headers permitidos: todos

**Para produção**, restrinja as origens:
```python
origins = [
    "http://localhost:3000",  # React dev
    "http://localhost:8080",  # Vue dev
    "https://seudominio.com"  # Produção
]
```

---

## Timeouts e Limites

### Tempo de Processamento
- **UC1** (Classificação): ~500ms - 2s
- **UC2** (Docling): ~2s - 10s (depende do tamanho do PDF)
- **UC3** (Análise textual): ~100ms - 500ms
- **UC4** (Conformidade): ~50ms

**Total estimado**: 3s - 15s para documentos típicos

### Recomendação para Frontend
```javascript
// Definir timeout de 30 segundos
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 30000);

try {
  const response = await fetch('http://localhost:8000/api/v1/analyze', {
    method: 'POST',
    body: formData,
    signal: controller.signal
  });

  clearTimeout(timeoutId);

  // processar resposta...

} catch (error) {
  if (error.name === 'AbortError') {
    console.error('Timeout: análise demorou muito');
  } else {
    console.error('Erro:', error);
  }
}
```

---

## Testando a API

### Via Swagger UI (Recomendado para testes iniciais)
1. Acesse http://localhost:8000/docs
2. Clique em "POST /api/v1/analyze"
3. Clique em "Try it out"
4. Clique em "Choose File" e selecione um PDF
5. Clique em "Execute"
6. Veja a resposta abaixo

### Via cURL
```bash
# Teste básico
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "file=@teste.pdf" \
  | jq '.'  # jq formata JSON (opcional)
```

### Via Postman
1. Crie nova requisição POST
2. URL: `http://localhost:8000/api/v1/analyze`
3. Body → form-data
4. Key: `file` (type: File)
5. Value: selecione arquivo
6. Send

---

## Checklist de Integração Frontend

- [ ] Verificar health check funciona
- [ ] Implementar upload de arquivo
- [ ] Validar formato antes de enviar
- [ ] Adicionar loading/spinner durante processamento
- [ ] Tratar erro 422 (não é científico)
- [ ] Tratar erro 400 (formato inválido)
- [ ] Tratar erro 500 (servidor)
- [ ] Tratar erro de rede (timeout, offline)
- [ ] Exibir resultados de forma legível
- [ ] Mostrar ações recomendadas se não conforme
- [ ] Exibir relatório markdown formatado
- [ ] Adicionar feedback visual de sucesso/erro
- [ ] Testar com diferentes formatos (PDF, PNG, JPEG)
- [ ] Testar com arquivos grandes (>5MB)

---

## Suporte e Documentação

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Código fonte**: `/Users/jwcunha/Documents/repos/phd-datascience/visao-computacional/doc_services/`
- **Especificação**: `spec.md`
- **Arquitetura**: `ARCHITECTURE_PLAN.md`

---

**Última atualização**: 2025-10-25
**Versão da API**: 1.0.0
