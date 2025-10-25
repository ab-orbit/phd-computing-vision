# Atualização: Análise Visual de Documentos com Claude

## O que mudou?

A API agora suporta **análise visual completa** de imagens usando Claude Vision. Anteriormente, o LLM classificava documentos baseado apenas no **nome do arquivo**, o que resultava em classificações incorretas como "file_folder" para arquivos com nomes genéricos.

## Problema Corrigido

**Antes:**
- LLM recebia apenas: `document_name="50535944-5945.tif"`
- Tentava adivinhar o tipo baseado no nome
- Resultado: classificações incorretas (ex: "file_folder")

**Depois:**
- LLM recebe a **imagem completa** em base64
- Analisa o **conteúdo visual**: layout, estrutura, elementos gráficos
- Considera cabeçalhos, rodapés, tabelas, formatação, logotipos, etc.
- Resultado: classificação baseada no que está **visualmente** na imagem

## Mudanças Técnicas

### 1. `llm_anthropic.py`

**Método `generate()` atualizado:**
```python
async def generate(self, request: LLMRequest, image_data: Optional[Dict[str, Any]] = None)
```
- Aceita parâmetro `image_data` com base64 e mime_type
- Envia imagem para Claude Vision API
- Formato: `{"base64_data": "...", "mime_type": "image/tiff"}`

**Novo método `create_classification_prompt_with_image()`:**
- Cria prompt específico para análise visual
- Instrui o LLM a ignorar o nome do arquivo
- Foca em características visuais do documento

**Método `classify_document()` atualizado:**
```python
async def classify_document(
    document_name: str,
    available_types: list,
    features: Optional[Dict] = None,
    image_data: Optional[Dict] = None  # NOVO
)
```

### 2. `main.py`

**Preparação de dados da imagem:**
```python
# Preparar dados da imagem para análise visual
image_data = None
if content_type.startswith('image/'):
    base64_data = base64.b64encode(file_content).decode('utf-8')
    image_data = {
        "base64_data": base64_data,
        "mime_type": content_type
    }

# Classificar usando LLM (com análise visual se for imagem)
llm_result = await llm_service.classify_document(
    document_name=filename,
    available_types=available_types,
    features=None,
    image_data=image_data  # Passa imagem para análise
)
```

## Como Testar

### 1. Reiniciar a API

Se a API já estiver rodando, reinicie para aplicar as mudanças:

```bash
# Parar API
lsof -ti:8000 | xargs kill -9

# Iniciar API
python -m app.main
```

### 2. Testar com sua imagem TIFF

Use o mesmo curl que você usou antes:

```bash
curl -X 'POST' \
  'http://localhost:8000/classify' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@50535944-5945.tif;type=image/tiff' \
  -F 'use_llm=true' \
  -F 'include_alternatives=true' \
  -F 'extract_metadata=true' \
  -F 'confidence_threshold=0.5'
```

### 3. Resultado Esperado

Agora a resposta deve incluir:

```json
{
  "predicted_type": "invoice",  // Exemplo: baseado no CONTEÚDO visual
  "probability": 0.92,
  "confidence": "high",
  "llm_metadata": {
    "reasoning": "A imagem mostra um documento com layout típico de fatura,
                  contendo tabelas de itens, valores monetários, cabeçalho
                  com logotipo empresarial e informações de cobrança."
  }
}
```

## Tipos de Documentos Suportados

A API classifica em 17 tipos do dataset RVL-CDIP + contract:

- advertisement
- budget
- email
- **file_folder** (capas de pastas - válido quando há uma pasta física na imagem)
- form
- handwritten
- invoice
- letter
- memo
- news_article
- presentation
- questionnaire
- resume
- scientific_publication
- scientific_report
- specification
- contract

## Custos de Análise Visual

**Claude 3.5 Haiku (modelo padrão):**
- Input: $1.00 / 1M tokens
- Output: $5.00 / 1M tokens
- **Análise visual de imagem:** ~2000-3000 tokens de input
- **Custo por imagem:** ~$0.002-0.003 USD

**Projeção para 1000 imagens:**
- Custo total: ~$2.50 USD
- Latência média: 2-3 segundos por imagem

## Debug e Logs

Para ver detalhes da análise:

```bash
# Ver logs da API
tail -f /tmp/api_output.log

# Ver reasoning do LLM na resposta
jq '.llm_metadata.reasoning' response.json
```

## Nota Importante sobre "file_folder"

O tipo "file_folder" **É VÁLIDO** quando:
- A imagem mostra uma **capa de pasta física**
- Há etiquetas ou rótulos de arquivo
- É literalmente uma pasta/arquivo de documentos

Se você esperava outro tipo (invoice, letter, etc.), isso indica que:
1. **Antes:** O LLM estava adivinhando baseado no nome genérico
2. **Agora:** O LLM deve ver o conteúdo real e classificar corretamente

## Resolução de Problemas

### Erro: "Extra tokens in input"

**Causa:** Imagem muito grande (>5MB)

**Solução:** Redimensionar imagem antes de enviar

### Classificação ainda incorreta

**Debug:** Verifique o campo `reasoning` na resposta para entender o que o LLM "viu"

**Ajuste:** Considere adicionar features extraídas (num_paragraphs, text_density) para melhorar a precisão

### Custos elevados

**Alternativa:** Use modelos menores ou adicione cache para imagens similares

## Próximos Passos

Para melhorar ainda mais a precisão:

1. **Adicionar features de layout:**
   - Usar DocLayout-YOLO para extrair elementos
   - Passar `features` com detecção de tabelas, figuras, etc.

2. **Implementar cache:**
   - Cache de classificações para documentos similares
   - Reduzir custos com Redis

3. **Suporte a PDFs:**
   - Converter primeira página de PDF para imagem
   - Enviar para análise visual

## Referências

- [Claude Vision API](https://docs.anthropic.com/claude/docs/vision)
- [RVL-CDIP Dataset](https://www.cs.cmu.edu/~aharley/rvl-cdip/)
- [Anthropic Pricing](https://www.anthropic.com/api)
