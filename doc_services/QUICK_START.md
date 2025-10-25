# Quick Start - Sistema de Análise de Documentos Científicos

Guia rápido para rodar o sistema completo (Backend + Frontend).

## Pré-requisitos

- Python 3.10+
- Node.js 18+
- npm ou yarn

## Instalação Rápida

### 1. Backend (FastAPI)

```bash
# 1. Criar e ativar ambiente virtual
cd doc_services
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 2. Instalar dependências
# Opção A: Instalação mínima (apenas LLM para classificação)
pip install -r requirements-minimal.txt

# Opção B: Instalação completa (com docling e todas as features)
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente
cp .env.example .env

# 4. Editar .env com suas API keys
nano .env  # ou use seu editor favorito
# Adicione:
# ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxx
# (ou outras API keys conforme necessário)

# 5. Iniciar servidor backend
python -m app.main
# Backend rodando em: http://localhost:8000
# Documentação: http://localhost:8000/docs
```

### 2. Frontend (React)

Em outro terminal:

```bash
# 1. Navegar para pasta frontend
cd doc_services/frontend

# 2. Instalar dependências
npm install

# 3. Configurar variáveis de ambiente
cp .env.example .env

# 4. Iniciar servidor de desenvolvimento
npm run dev
# Frontend rodando em: http://localhost:3000
```

## Testando o Sistema

### 1. Via Interface Web

1. Abra `http://localhost:3000` no navegador
2. Arraste ou selecione um documento (PDF ou imagem)
3. Aguarde a análise completa
4. Visualize os resultados dos 4 UCs

### 2. Via API (curl)

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Classificar documento (UC1-UC4)
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "file=@path/to/documento.pdf"
```

### 3. Via Documentação Interativa

Acesse `http://localhost:8000/docs` para testar diretamente na interface Swagger.

## Estrutura do Projeto

```
doc_services/
├── app/                    # Backend Python/FastAPI
│   ├── core/              # Configurações
│   ├── models/            # Schemas Pydantic
│   ├── services/          # Lógica de negócio
│   ├── integrations/      # APIs externas
│   └── main.py            # Entry point
│
├── frontend/              # Frontend React/TypeScript
│   ├── src/
│   │   ├── components/   # Componentes React
│   │   ├── services/     # API client
│   │   ├── types/        # Tipos TypeScript
│   │   └── App.tsx       # App principal
│   ├── package.json
│   └── vite.config.ts
│
├── tests/                 # Testes
├── requirements.txt       # Dependências Python (completo)
├── requirements-minimal.txt  # Dependências mínimas
└── README.md
```

## Casos de Uso Implementados

### UC1: Classificação

**Backend:** API externa já implementada (via LLM)
**Frontend:** `ClassificationResult` component
**Verifica:** Se documento é artigo científico

### UC2: Detecção de Parágrafos

**Backend:** Usando docling (a implementar completamente)
**Frontend:** `ParagraphsList` component
**Extrai:** Parágrafos com contagem de palavras

### UC3: Análise de Texto

**Backend:** Processamento básico Python
**Frontend:** `TextAnalysisView` component
**Calcula:** Frequência de palavras

### UC4: Relatório de Conformidade

**Backend:** Template + validação
**Frontend:** `ComplianceReportView` component
**Valida:** 2000 palavras + 8 parágrafos

## Fluxo de Análise

```
1. User faz upload do documento
   ↓
2. Backend recebe arquivo
   ↓
3. UC1: Classifica documento
   • Se não for artigo científico → PARA
   • Se for artigo científico → Continua
   ↓
4. UC2: Detecta parágrafos (docling)
   ↓
5. UC3: Analisa texto (contagem + frequências)
   ↓
6. UC4: Gera relatório de conformidade
   ↓
7. Frontend exibe todos os resultados
```

## Troubleshooting

### Backend não inicia

**Erro:** `ModuleNotFoundError`
```bash
# Verificar ambiente virtual ativado
which python  # Deve mostrar path do venv

# Reinstalar dependências
pip install -r requirements-minimal.txt
```

**Erro:** `ANTHROPIC_API_KEY not configured`
```bash
# Verificar .env existe
ls .env

# Verificar conteúdo
cat .env | grep ANTHROPIC
```

### Frontend não conecta ao backend

**Erro:** `Network Error` ou `ERR_CONNECTION_REFUSED`

```bash
# 1. Verificar backend rodando
curl http://localhost:8000/api/v1/health

# 2. Verificar URL em frontend/.env
cat frontend/.env
# Deve ter: VITE_API_URL=http://localhost:8000

# 3. Verificar CORS no backend
# Backend deve ter CORSMiddleware configurado
```

### Upload falha

**Erro:** `File too large` ou `Unsupported format`

Verificar limites em `frontend/src/components/FileUploader.tsx`:
- Formatos aceitos: `.pdf`, `.png`, `.jpg`, `.jpeg`, `.tiff`, `.tif`
- Tamanho máximo: 10MB

## Desenvolvimento

### Hot Reload

Ambos frontend e backend têm hot reload ativado:

- **Backend:** FastAPI reload automático quando arquivos mudam
- **Frontend:** Vite HMR (Hot Module Replacement) instantâneo

### Logs

**Backend:**
```bash
# Logs aparecem no terminal onde rodou `python -m app.main`
# Para debug detalhado:
LOG_LEVEL=DEBUG python -m app.main
```

**Frontend:**
```bash
# Console do navegador (F12)
# Logs de API aparecem automaticamente
```

## Build para Produção

### Backend

```bash
# Usar Gunicorn ou Uvicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend

```bash
cd frontend
npm run build
# Build em frontend/dist/

# Servir com qualquer servidor estático
npx serve dist
```

## Próximos Passos

### Para Completar Implementação

1. **Implementar serviços no backend:**
   - `ParagraphDetectionService` (docling)
   - `TextAnalysisService` (análise básica)
   - `ComplianceReportService` (template)

2. **Implementar orchestrator:**
   - `DocumentAnalysisOrchestrator`
   - Coordenar fluxo UC1 → UC2 → UC3 → UC4

3. **Implementar endpoint `/api/v1/analyze`:**
   - Receber arquivo
   - Executar orchestrator
   - Retornar resultado consolidado

### Para Melhorar Sistema

1. **Adicionar testes:**
   - Backend: pytest
   - Frontend: Jest + React Testing Library

2. **Adicionar autenticação:**
   - JWT tokens
   - Rate limiting

3. **Adicionar persistência:**
   - Banco de dados (PostgreSQL)
   - Histórico de análises

4. **Melhorar performance:**
   - Cache (Redis)
   - Processamento assíncrono (Celery)

## Documentação Adicional

- **Backend API:** http://localhost:8000/docs
- **Frontend README:** `frontend/README.md`
- **Arquitetura:** `ARCHITECTURE_PLAN.md`
- **Especificações:** `spec.md`
- **Implementação Frontend:** `frontend/IMPLEMENTATION_SUMMARY.md`

## Suporte

### Documentação

- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- Vite: https://vitejs.dev/
- TailwindCSS: https://tailwindcss.com/

### Issues Conhecidos

1. **UC2 (docling) ainda não totalmente implementado no backend**
   - Frontend está pronto para receber dados
   - Backend precisa implementar integração com docling

2. **UC3 e UC4 precisam implementação no backend**
   - Frontend está pronto
   - Lógica de negócio precisa ser implementada

### Como Contribuir

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Add nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Status Atual

- ✅ **Frontend React:** 100% implementado e funcional
- ✅ **Backend API:** Estrutura e UC1 implementados
- 🚧 **UC2 (Docling):** A implementar
- 🚧 **UC3 (Análise Textual):** A implementar
- 🚧 **UC4 (Conformidade):** A implementar
- 🚧 **Testes:** A implementar
- 🚧 **CI/CD:** A implementar

## Licença

MIT

---

**Pronto para começar!** Execute os comandos acima e comece a desenvolver.
