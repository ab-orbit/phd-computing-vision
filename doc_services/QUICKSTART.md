# Quickstart - Document Classification API

Guia rápido para começar a usar a API em 5 minutos.

## 1. Setup Rápido (Local)

```bash
# Clone e entre no diretório
cd doc_services

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Instale dependências mínimas
pip install fastapi uvicorn python-multipart pydantic pillow

# Execute o servidor
python -m app.main
```

Acesse: http://localhost:8000/docs

## 2. Setup com Docker

```bash
# Build e execute
docker-compose up -d

# Verifique logs
docker-compose logs -f api

# Teste health check
curl http://localhost:8000/health
```

## 3. Primeiro Teste

### Via cURL

```bash
# Baixe um PDF de teste (ou use seu próprio)
curl -X POST "http://localhost:8000/classify" \
  -F "file=@seu_documento.pdf" \
  -F "include_alternatives=true"
```

### Via Python

```python
import requests

# Classificar documento
with open('documento.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/classify',
        files={'file': f}
    )

result = response.json()
print(f"Tipo: {result['predicted_type']}")
print(f"Probabilidade: {result['probability']:.1%}")
```

## 4. Explorar Documentação

Acesse a documentação interativa Swagger:

```
http://localhost:8000/docs
```

Teste os endpoints diretamente no navegador!

## 5. Próximos Passos

1. **Configure LLM** (opcional):
   ```bash
   # Edite .env
   echo "ANTHROPIC_API_KEY=sk-ant-xxx" >> .env
   ```

2. **Teste com LLM**:
   ```bash
   curl -X POST "http://localhost:8000/classify" \
     -F "file=@documento.pdf" \
     -F "use_llm=true"
   ```

3. **Explore outros endpoints**:
   - `/health` - Status da API
   - `/models` - Modelos disponíveis
   - `/document-types` - Tipos suportados

## Exemplos de Uso

### Classificação Simples

```python
import requests

def classify_document(file_path):
    with open(file_path, 'rb') as f:
        response = requests.post(
            'http://localhost:8000/classify',
            files={'file': f}
        )
    return response.json()

# Usar
result = classify_document('email.pdf')
print(result['predicted_type'])  # 'email'
```

### Com Configurações Avançadas

```python
import requests

def classify_with_options(file_path, use_llm=False, threshold=0.5):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {
            'use_llm': use_llm,
            'include_alternatives': True,
            'confidence_threshold': threshold
        }
        response = requests.post(
            'http://localhost:8000/classify',
            files=files,
            data=data
        )
    return response.json()

# Usar
result = classify_with_options('documento.pdf', use_llm=True, threshold=0.7)
```

### Processar Múltiplos Documentos

```python
import requests
from pathlib import Path

def classify_batch(folder_path):
    results = []
    for file_path in Path(folder_path).glob('*.pdf'):
        with open(file_path, 'rb') as f:
            response = requests.post(
                'http://localhost:8000/classify',
                files={'file': f}
            )
            results.append({
                'file': file_path.name,
                'type': response.json()['predicted_type']
            })
    return results

# Usar
results = classify_batch('documentos/')
for r in results:
    print(f"{r['file']}: {r['type']}")
```

## Solução de Problemas

### Erro: Modelo não encontrado

```bash
# Verifique o caminho do modelo no .env
MODEL_PATH=../doclayout-yolo/doclayout_yolo_docstructbench_imgsz1024.pt
```

### Erro: Redis connection failed

```bash
# Inicie o Redis
docker-compose up -d redis

# Ou desabilite cache
ENABLE_CACHE=false
```

### Erro: Port 8000 already in use

```bash
# Use outra porta
uvicorn app.main:app --port 8001
```

## Performance Tips

1. **Use cache**: Habilite Redis para respostas mais rápidas
2. **Evite LLM quando possível**: Use apenas para casos ambíguos
3. **Processe em lote**: Use endpoint /classify/batch (quando implementado)
4. **Otimize imagens**: Documentos menores processam mais rápido

## Recursos

- **Documentação Completa**: [README.md](README.md)
- **Backlog**: [BACKLOG.md](BACKLOG.md)
- **API Docs**: http://localhost:8000/docs
- **Issues**: GitHub Issues

## Métricas Rápidas

```bash
# Ver métricas Prometheus
curl http://localhost:9090/metrics

# Ver health check
curl http://localhost:8000/health | jq
```

---

**Pronto!** Você tem uma API de classificação de documentos rodando. 🚀

Para informações detalhadas, consulte [README.md](README.md) e [BACKLOG.md](BACKLOG.md).
