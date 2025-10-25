# Guia de Instalação - Document Classification API

## Opções de Instalação

### Opção 1: Instalação Mínima (Recomendado para Testes)

Para testar apenas a funcionalidade de LLM sem instalar dependências pesadas (PyTorch, etc):

```bash
cd doc_services

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# Instalar dependências mínimas
pip install -r requirements-minimal.txt

# Configurar API key
cp .env.example .env
echo "ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxx" >> .env

# Testar
python test_llm_classification.py
```

**Tempo de instalação**: ~2 minutos
**Tamanho**: ~200MB

### Opção 2: Instalação Completa

Para usar todas as funcionalidades (incluindo DocLayout-YOLO):

```bash
cd doc_services

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate

# Instalar dependências completas
pip install -r requirements.txt

# Configurar
cp .env.example .env
nano .env  # Adicionar ANTHROPIC_API_KEY

# Executar
python -m app.main
```

**Tempo de instalação**: ~10-15 minutos (PyTorch é grande)
**Tamanho**: ~2-3GB

### Opção 3: Docker (Produção)

```bash
# Build
docker-compose build

# Configurar .env
cp .env.example .env
echo "ANTHROPIC_API_KEY=sk-ant-xxx" >> .env

# Executar
docker-compose up -d

# Testar
curl http://localhost:8000/health
```

## Resolução de Problemas

### Erro: Conflito de Dependências pytest

**Problema**:
```
ERROR: Cannot install pytest==8.0.0 and pytest-asyncio==0.23.4
```

**Solução**:
```bash
# Já corrigido! Use:
pip install -r requirements-minimal.txt
# ou
pip install pytest==7.4.4 pytest-asyncio==0.23.4
```

### Erro: PyTorch muito grande

**Problema**: PyTorch demora muito para instalar

**Solução**: Use instalação mínima para testes:
```bash
pip install -r requirements-minimal.txt
```

### Erro: anthropic module not found

**Solução**:
```bash
pip install anthropic==0.9.0 httpx==0.26.0
```

### Erro: ANTHROPIC_API_KEY não configurada

**Solução**:
```bash
# 1. Obter API key em https://console.anthropic.com/
# 2. Adicionar no .env
echo "ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxx" >> .env
```

## Verificação da Instalação

### 1. Verificar Python

```bash
python --version
# Deve ser >= 3.10
```

### 2. Verificar Pacotes Instalados

```bash
pip list | grep -E "fastapi|anthropic|pydantic"
```

Deve mostrar:
```
anthropic    0.9.0
fastapi      0.109.0
pydantic     2.5.3
```

### 3. Testar Import

```python
python -c "from app.services.llm_anthropic import create_anthropic_service; print('✓ OK')"
```

### 4. Testar API Key

```bash
python test_llm_classification.py
```

Se aparecer:
```
ERRO: ANTHROPIC_API_KEY não configurada
```

Então configure:
```bash
echo "ANTHROPIC_API_KEY=sk-ant-xxx" >> .env
```

## Instalação por Plataforma

### macOS

```bash
# Instalar Python 3.10+
brew install python@3.10

# Criar venv e instalar
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements-minimal.txt
```

### Linux (Ubuntu/Debian)

```bash
# Instalar Python e dependências
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev

# Criar venv e instalar
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements-minimal.txt
```

### Windows

```powershell
# Baixar Python 3.10+ de python.org

# Criar venv e instalar
python -m venv venv
venv\Scripts\activate
pip install -r requirements-minimal.txt
```

## Dependências por Funcionalidade

### Apenas LLM (Mínimo)

```bash
pip install fastapi uvicorn pydantic pydantic-settings anthropic httpx python-dotenv
```

### + Processamento de PDFs

```bash
pip install Pillow PyPDF2 pdf2image
```

### + DocLayout-YOLO (Análise de Layout)

```bash
pip install ultralytics torch torchvision
```

### + Testes

```bash
pip install pytest==7.4.4 pytest-asyncio pytest-cov
```

### + Desenvolvimento

```bash
pip install black flake8 mypy pre-commit
```

## Instalação no Google Colab

```python
# No notebook Colab
!pip install -q fastapi pydantic anthropic httpx python-dotenv

# Configurar API key
import os
os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-xxx'

# Testar
from app.services.llm_anthropic import create_anthropic_service
```

## Próximos Passos

Após instalação bem-sucedida:

1. **Testar LLM**:
   ```bash
   python test_llm_classification.py
   ```

2. **Iniciar API**:
   ```bash
   python -m app.main
   # Acesse: http://localhost:8000/docs
   ```

3. **Classificar documento**:
   ```bash
   curl -X POST "http://localhost:8000/classify" \
     -F "file=@documento.pdf" \
     -F "use_llm=true"
   ```

## Suporte

Se tiver problemas:

1. Verificar versão Python: `python --version` (>= 3.10)
2. Verificar ambiente virtual ativado
3. Tentar instalação mínima primeiro: `requirements-minimal.txt`
4. Verificar logs: `python -m app.main --log-level DEBUG`

## Referências

- Python 3.10+: https://www.python.org/downloads/
- Anthropic API: https://console.anthropic.com/
- FastAPI: https://fastapi.tiangolo.com/
- Documentação completa: README.md
