# Análise de Documentos Científicos - Frontend

Aplicação React moderna para análise de documentos científicos, integrando 4 casos de uso:

- **UC1**: Classificação de documentos (verificação de artigo científico)
- **UC2**: Detecção de parágrafos usando docling
- **UC3**: Análise textual e frequência de palavras
- **UC4**: Relatório de conformidade (2000 palavras, 8 parágrafos)

## Stack Tecnológica

- **React 18** - Framework UI
- **TypeScript** - Type safety
- **Vite** - Build tool (dev server rápido)
- **TailwindCSS** - Styling moderno e responsivo
- **React Query** - Gerenciamento de estado assíncrono
- **Axios** - HTTP client
- **React Markdown** - Renderização de markdown
- **Lucide Icons** - Ícones modernos
- **Recharts** - Visualização de dados

## Arquitetura

```
frontend/
├── src/
│   ├── components/          # Componentes React
│   │   ├── FileUploader.tsx
│   │   ├── AnalysisProgress.tsx
│   │   ├── ClassificationResult.tsx
│   │   ├── ParagraphsList.tsx
│   │   ├── TextAnalysisView.tsx
│   │   └── ComplianceReportView.tsx
│   │
│   ├── services/           # Integração com API
│   │   └── api.ts
│   │
│   ├── types/              # Tipos TypeScript
│   │   └── index.ts
│   │
│   ├── App.tsx             # Componente principal
│   ├── main.tsx            # Entry point
│   └── index.css           # Estilos globais
│
├── package.json
├── vite.config.ts
├── tsconfig.json
└── tailwind.config.js
```

## Instalação

### Pré-requisitos

- Node.js 18+ e npm
- Backend FastAPI rodando (porta 8000)

### Passos

1. **Instalar dependências:**

```bash
cd frontend
npm install
```

2. **Configurar variáveis de ambiente:**

```bash
cp .env.example .env
```

Edite `.env` se necessário:

```env
VITE_API_URL=http://localhost:8000
VITE_ENV=development
```

3. **Iniciar servidor de desenvolvimento:**

```bash
npm run dev
```

Aplicação estará disponível em: `http://localhost:3000`

## Scripts Disponíveis

```bash
# Desenvolvimento (hot reload)
npm run dev

# Build para produção
npm run build

# Preview da build
npm run preview

# Linting
npm run lint
```

## Uso da Aplicação

### 1. Upload de Documento

- Arraste e solte um documento (PDF ou imagem)
- Ou clique para selecionar arquivo
- Formatos suportados: `.pdf`, `.png`, `.jpg`, `.jpeg`, `.tiff`, `.tif`
- Tamanho máximo: 10MB

### 2. Análise Automática

Após o upload, a análise é executada automaticamente:

```
UC1: Classificação (2s)
   ↓
UC2: Detecção de Parágrafos (3-5s)
   ↓
UC3: Análise de Texto (1-2s)
   ↓
UC4: Relatório de Conformidade (1s)
```

### 3. Visualização de Resultados

#### UC1: Classificação
- Status: Artigo científico ou não
- Tipo do documento
- Nível de confiança

#### UC2: Parágrafos
- Lista de todos os parágrafos detectados
- Contagem de palavras por parágrafo
- Visualização expandível do texto completo

#### UC3: Análise Textual
- Total de palavras no documento
- Top 15 palavras mais frequentes
- Tabela com frequências e percentuais
- Gráfico de barras das frequências

#### UC4: Conformidade
- Status geral (conforme / não conforme)
- Métricas vs. Metas:
  - Palavras: ≥ 2000
  - Parágrafos: = 8
- Ações recomendadas (se não conforme)
- Relatório completo em markdown
- Download do relatório (.md)

## Componentes Principais

### FileUploader

Componente drag-and-drop para upload de arquivos.

**Funcionalidades:**
- Validação de formato e tamanho
- Preview do arquivo selecionado
- Mensagens de erro claras

### AnalysisProgress

Visualiza progresso através dos 4 UCs com indicadores visuais.

**Estados:**
- Idle, Uploading, Classifying, Detecting Paragraphs, Analyzing Text, Generating Report, Completed, Error

### ClassificationResult (UC1)

Exibe resultado da classificação do documento.

### ParagraphsList (UC2)

Lista interativa de parágrafos detectados com expansão/colapso.

### TextAnalysisView (UC3)

Visualização de análise textual com tabela e gráfico de frequências.

### ComplianceReportView (UC4)

Dashboard de conformidade com métricas, ações recomendadas e download do relatório.

## Integração com Backend

### Endpoint Principal

```typescript
POST /api/v1/analyze
Content-Type: multipart/form-data

Body:
- file: File (PDF ou imagem)

Response:
{
  status: 'success' | 'error',
  classification: ClassificationResult,
  paragraphs: Paragraph[],
  text_analysis: TextAnalysis,
  compliance_report: ComplianceReport,
  error_message?: string
}
```

### Tratamento de Erros

A aplicação trata diversos cenários:

1. **Documento não é artigo científico:** Mostra aviso e interrompe análise
2. **Erro de upload:** Exibe mensagem específica
3. **Timeout da API:** Mensagem de erro clara
4. **Erro de validação:** Feedback imediato no upload

## Customização

### Cores e Tema

Edite `tailwind.config.js` para customizar cores:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        50: '#eff6ff',
        // ... suas cores
      },
    },
  },
}
```

### Limites de Upload

Edite em `App.tsx`:

```typescript
<FileUploader
  acceptedFormats={['.pdf', '.png']}
  maxSizeMB={20}  // Alterar limite
  onFileSelect={handleFileSelect}
/>
```

## Desenvolvimento

### Estrutura de Componentes

Todos os componentes seguem padrão funcional com TypeScript:

```typescript
interface ComponentProps {
  // Props tipadas
}

export function Component({ ...props }: ComponentProps) {
  // Hooks
  // Lógica
  // Render
}
```

### Tipos TypeScript

Todos os tipos estão em `src/types/index.ts`, refletindo os modelos do backend:

- `ClassificationResult`
- `Paragraph`
- `TextAnalysis`
- `ComplianceReport`
- `AnalysisResult`

### Estado da Aplicação

Estado gerenciado com React hooks:

- `useState` - Estado local de componentes
- `useCallback` - Memoização de callbacks
- React Query - Cache de requisições (preparado para uso futuro)

## Build para Produção

```bash
# Gerar build otimizada
npm run build

# Preview da build
npm run preview
```

Build é gerada em `dist/` e pode ser servida por qualquer servidor estático:

```bash
# Exemplo com serve
npx serve dist
```

## Troubleshooting

### Erro de conexão com API

**Problema:** `Network Error` ou `ERR_CONNECTION_REFUSED`

**Solução:**
1. Verificar se backend está rodando: `curl http://localhost:8000/api/v1/health`
2. Verificar URL em `.env`: `VITE_API_URL=http://localhost:8000`
3. Verificar CORS no backend

### Build falha

**Problema:** Erros de TypeScript no build

**Solução:**
```bash
# Limpar e reinstalar
rm -rf node_modules package-lock.json
npm install

# Verificar tipos
npm run lint
```

### Gráficos não aparecem

**Problema:** Recharts não renderiza

**Solução:**
Verificar se há dados: `analysis.top_words.length > 0`

## Performance

### Otimizações Implementadas

- **Code Splitting:** Vite faz automaticamente
- **Lazy Loading:** Componentes carregados sob demanda
- **Memoização:** useCallback para funções pesadas
- **Imagens:** Compressão no upload

### Métricas

- **Initial Load:** ~200KB (gzipped)
- **First Contentful Paint:** < 1s
- **Time to Interactive:** < 2s

## Acessibilidade

- Suporte a teclado em todos os componentes
- ARIA labels apropriados
- Contraste de cores WCAG AA
- Mensagens de erro claras

## Próximas Melhorias

- [ ] WebSocket para progresso em tempo real
- [ ] Histórico de análises
- [ ] Comparação entre documentos
- [ ] Export em múltiplos formatos (PDF, DOCX)
- [ ] Temas dark/light
- [ ] Internacionalização (i18n)
- [ ] Testes E2E com Playwright
- [ ] PWA (offline support)

## Suporte

Para problemas:

1. Verificar logs do console (F12)
2. Verificar rede (Network tab)
3. Verificar se backend está respondendo
4. Criar issue no repositório

## Licença

MIT

## Autores

Sistema desenvolvido para análise de documentos científicos - Projeto de Visão Computacional
