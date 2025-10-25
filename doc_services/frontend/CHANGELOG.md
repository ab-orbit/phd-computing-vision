# Changelog - Parsey Document Analyzer Frontend

Histórico de alterações e melhorias implementadas.

---

## [1.4.1] - 2025-10-25

### 🐛 Correções de Bugs

#### 1. **Tratamento de Arquivos TIFF no Preview**
- **Problema:** Arquivos TIFF não renderizavam no navegador, mostrando ícone quebrado
- **Solução:** Detecção antecipada de TIFF com mensagem informativa ao usuário
- **Arquivo:** `src/components/DocumentPreview.tsx`

**Comportamento Implementado:**
```tsx
// Detecta TIFF por MIME type ou extensão
if (mimeType === 'image/tiff' || fileName.endsWith('.tif') || fileName.endsWith('.tiff')) {
  // Mostra mensagem amigável em amber (warning, não error)
  setError('Preview não disponível para arquivos TIFF...');
}
```

**Visual:**
- Fundo âmbar (warning) em vez de vermelho (error)
- Card com informações do arquivo:
  - Nome do arquivo
  - Tamanho em MB
  - Formato TIFF
  - "✓ Arquivo aceito pela análise" (confirmação)

**Benefícios:**
- UX melhorada: usuário entende que TIFF é válido mas sem preview
- Evita confusão: não parece erro, mas limitação do navegador
- Transparência: informa que análise processará normalmente

**Contexto Técnico:**
- Navegadores web não suportam renderização nativa de TIFF
- Arquivo TIFF continua válido para análise backend
- Alternativa seria conversão server-side (futura melhoria)

---

## [1.4.0] - 2025-10-25

### ✨ Novo Layout com Mascote Fixa

#### 1. **Mascote Parsey Fixa no Lado Direito**
- **Mudança:** Mascote agora está em `position: fixed` no lado direito
- **Tamanho:** 256x256px (w-64 h-64) - aumentado de 180px
- **Efeitos:** Glow animado + bounce suave + drop shadow
- **Responsivo:** Oculta em mobile (`hidden lg:block`)

**Implementação:**
```tsx
<div className="fixed right-8 top-1/2 -translate-y-1/2 z-10 pointer-events-none">
  <img src={parseyLogo} className="w-64 h-64 animate-bounce-soft" />
</div>
```

**Características:**
- Sempre visível durante scroll
- Não bloqueia interações (`pointer-events-none`)
- Centralizada verticalmente
- 32px da borda direita

#### 2. **Margens para Evitar Sobreposição**
- **Todas as seções:** `lg:mr-72` (288px margem direita)
- **Cálculo:** 256px (mascote) + 32px (padding) = 288px
- **Aplicado em:**
  - Upload Section
  - Preview Section
  - Progress Section
  - Results Sections (UC1-UC4)
  - Error Section (não-científico)

**Benefícios:**
- Layout limpo sem sobreposição
- Mascote como elemento decorativo permanente
- Branding constante
- Responsivo: margem removida em mobile

**Documentação:** Ver `FIXED_LAYOUT.md` para detalhes completos

---

## [1.3.0] - 2025-10-25

### ✨ Novos Recursos

#### 1. **Painel de Preview do Documento**
- **Componente:** `DocumentPreview.tsx` (novo)
- **Funcionalidade:**
  - Preview de PDFs via iframe
  - Preview de imagens (PNG, JPG, TIFF)
  - Controles de zoom (50% - 200%)
  - Informações do arquivo (nome, tamanho)
  - Estados vazios e de erro
- **Integração:** Seção 2 no fluxo principal

**Recursos:**
```tsx
- PDF Preview via blob URL
- Imagem Preview via data URL
- Zoom In/Out/Reset
- FileReader API para imagens
- Cleanup automático de URLs
- Design Parsey com rounded-parsey
```

**Benefícios:**
- Usuário visualiza documento antes da análise
- Confirmação visual do arquivo correto
- Melhor UX durante processamento
- Suporte completo a PDFs e imagens

#### 2. **Link para API Docs no Header**
- **Localização:** Header, ao lado do badge de versão
- **URL:** `http://localhost:8000/docs`
- **Estilo:** Botão com ícones (FileText + ExternalLink)
- **Comportamento:** Abre em nova aba

**Visual:**
```
[📄 API Docs 🔗] [v1.0.0]
```

**Benefícios:**
- Acesso rápido à documentação OpenAPI
- Facilita desenvolvimento e testes
- Link sempre visível no topo

### 🎨 Melhorias Visuais

#### 3. **Footer com Logo Estática**
- **Antes:** Vídeo animado (parsey_video.mp4)
- **Depois:** Logo estática (parsey-logo.png)
- **Tamanho:** h-6 (24px)
- **Razão:** Redução de assets carregados, profissionalismo

**Impacto:**
- Carregamento mais rápido do footer
- Consistência com header
- Menos distração visual

### 📁 Arquivos Criados

1. **DocumentPreview.tsx** - Componente de preview
   - 227 linhas
   - Suporte PDF e imagens
   - Controles de zoom
   - Estados vazios/erro

2. **CHANGELOG.md** - Este arquivo
   - Histórico de mudanças
   - Versionamento semântico

### 🔧 Arquivos Modificados

1. **App.tsx**
   - Import do `DocumentPreview`
   - Import do ícone `ExternalLink`
   - Estado `selectedFile`
   - Link "API Docs" no header
   - Seção de preview (condicional)
   - Footer com logo estática
   - Atualização da numeração de seções

### 📊 Fluxo Atualizado

```
1. Upload do Documento
   ↓
2. Preview do Documento (NOVO)
   ↓
3. Progresso da Análise
   ↓
4. Resultados (UC1-UC4)
```

### 🎯 Benefícios Gerais

**UX:**
- ✅ Preview antes da análise
- ✅ Confirmação visual do arquivo
- ✅ Acesso rápido aos docs da API
- ✅ Footer mais leve e profissional

**DX (Developer Experience):**
- ✅ Link direto para OpenAPI docs
- ✅ Componente reutilizável (DocumentPreview)
- ✅ Estado gerenciado centralmente

**Performance:**
- ✅ Footer sem vídeo (menos peso)
- ✅ Preview com cleanup automático
- ✅ Lazy loading de assets

---

## [1.2.0] - 2025-10-25

### ✨ Novos Assets

#### 1. **Logo Parsey no Header**
- **Asset:** `parsey-logo.png` (122KB)
- **Antes:** Vídeo animado
- **Depois:** Logo profissional estática
- **Benefício:** Identidade visual mais clara

#### 2. **Parsey Layed para Erros**
- **Asset:** `parsey_layed.png` (218KB)
- **Uso:** Retorno quando documento não é científico
- **Layout:** 2 colunas com mensagem explicativa
- **Benefício:** Comunicação amigável de erros

### 📚 Documentação Criada

1. **PARSEY_ASSETS.md**
   - Guia completo de todos assets
   - Matriz de decisão
   - Especificações técnicas
   - Exemplos de código

2. **UI_IMPROVEMENTS.md**
   - Melhorias de UX
   - Mascote no painel principal
   - Favicon personalizado

### 🎨 Melhorias Visuais

- Mascote no painel de upload (lado esquerdo)
- Grid responsivo 2 colunas
- Glow effects animados
- Favicon Parsey (favicon.jpg)

---

## [1.1.0] - 2025-10-25

### 🔧 Correções Críticas

#### 1. **Endpoints da API Corrigidos**
- **Problema:** Frontend chamava `/api/v1/analyze` (não existe)
- **Solução:** Atualizado para `/classify`
- **Arquivo:** `src/services/api.ts`

**Mudanças:**
```typescript
// ANTES
await api.post('/api/v1/analyze', formData);

// DEPOIS
await api.post('/classify', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});
```

#### 2. **Adaptação de Resposta**
- Backend retorna apenas UC1
- Frontend adapta para estrutura completa
- UC2-UC4 retornam dados mock/vazios

### 🎥 Integrações de Mídia

#### 1. **Vídeo da Mascote**
- **Asset:** `parsey_video.mp4` (2.4MB)
- **Uso:** Header e footer
- **Recursos:** Autoplay, loop, muted, playsInline
- **Fallback:** Imagem PNG se vídeo falhar

### 📝 Documentação

1. **INTEGRATION_SUMMARY.md**
   - Resumo completo de integrações
   - Status de UCs (UC1-UC4)
   - Guia de teste

2. **PARSEY_DESIGN_UPDATE.md**
   - Design system completo
   - Tokens Parsey
   - Paleta de cores
   - Tipografia

---

## [1.0.0] - 2025-10-25

### 🎉 Lançamento Inicial

#### Aplicação React Completa

**Componentes Criados:**
1. `FileUploader.tsx` - Upload drag-and-drop
2. `AnalysisProgress.tsx` - Progresso UC1-UC4
3. `ClassificationResult.tsx` - Resultado UC1
4. `ParagraphsList.tsx` - Resultado UC2
5. `TextAnalysisView.tsx` - Resultado UC3
6. `ComplianceReportView.tsx` - Resultado UC4
7. `App.tsx` - Componente principal

**Tecnologias:**
- React 18.2.0
- TypeScript 5.2.2
- Vite 5.0.8
- TailwindCSS 3.3.6
- Axios 1.6.2

**Design System:**
- Cores Parsey (violeta, azul, ciano)
- Fontes: Inter, Poppins, Nunito
- Border radius característico (24px)
- Shadows com glow effect

---

## Versionamento

Seguimos [Semantic Versioning](https://semver.org/):
- **MAJOR:** Mudanças incompatíveis
- **MINOR:** Novos recursos compatíveis
- **PATCH:** Correções de bugs

---

## Próximas Versões

### [1.5.0] - Planejado
- [ ] Dark mode
- [ ] Biblioteca de componentes
- [ ] Loading states melhorados
- [ ] Toast notifications
- [ ] Conversão server-side TIFF para PNG (preview)

### [2.0.0] - Futuro
- [ ] Backend UC2-UC4 completo
- [ ] WebSocket para progresso real-time
- [ ] Histórico de análises
- [ ] Exportação de relatórios

---

**Mantido por:** Claude Code
**Última atualização:** 2025-10-25
