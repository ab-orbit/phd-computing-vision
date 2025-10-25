# Atualização do Design System - Parsey

Aplicação atualizada para seguir rigorosamente o **Parsey Design System** definido em `src/definitions/design_system_token.json`.

## Mudanças Implementadas

### 1. Configuração do Tailwind (tailwind.config.js)

Atualizado com todos os tokens do design system Parsey:

**Paleta de Cores:**
- `parsey-blue` (#3B82F6)
- `parsey-violet` (#6366F1) - Cor principal da marca
- `parsey-indigo` (#1E3A8A)
- `parsey-lilac` (#A5B4FC) - Destaque
- `parsey-cyan` (#22D3EE) - Accent
- `parsey-gray` (#64748B)

**Cores Semânticas:**
- `brand-primary` - Violeta (#6366F1)
- `brand-emphasis` - Índigo profundo (#1E3A8A)
- `brand-secondary` - Azul Parsey (#3B82F6)
- `brand-accent` - Ciano (#22D3EE)
- `brand-highlight` - Lilás (#A5B4FC)

**Estados:**
- `semantic-success` (#10B981)
- `semantic-warning` (#F59E0B)
- `semantic-danger` (#EF4444)
- `semantic-info` (#22D3EE)

**Fontes:**
- `font-sans` - Inter (UI text)
- `font-display` - Poppins (Headers)
- `font-mascot` - Nunito (Mascote e elementos especiais)

**Border Radius:**
- `rounded-parsey` - 24px (radius característico)
- `rounded-pill` - 9999px (badges)

**Shadows:**
- `shadow-parsey` - Glow violeta (sombra da marca)
- `shadow-accent` - Glow ciano (focus states)

**Animações:**
- `animate-bounce-soft` - Bounce suave (mascote)
- `duration-instant` - 75ms
- `duration-fast` - 150ms
- `duration-base` - 250ms
- `duration-slow` - 400ms

### 2. Fontes do Google (index.html)

Adicionadas as três famílias de fontes do design system:

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@600;700&family=Nunito:wght@400;600;700&display=swap" rel="stylesheet">
```

### 3. CSS Global (index.css)

**Body:**
- Background: `bg-parsey-bg` (#F3F4F6)
- Text: `text-text-primary` (#0F172A)
- Font: Inter

**Headings:**
- Font: Poppins (display font)

**Prose (Markdown):**
- Cores adaptadas para palette Parsey
- Text primary e secondary

**Scrollbar:**
- Track: `bg-surface`
- Thumb: `parsey-gray` com hover `brand-primary`

### 4. App Principal (App.tsx)

**Header:**
- Background: Branco com blur e opacity
- Shadow: `shadow-parsey` (glow violeta)
- Border: `border-border-subtle`

**Mascote Parsey:**
```tsx
<img src={parseyLogo} alt="Parsey" className="w-16 h-16 animate-bounce-soft" />
```
- Animação bounce suave
- Glow effect com gradiente violeta-ciano

**Título:**
```tsx
<h1 className="font-display font-bold bg-gradient-to-r from-brand-primary via-brand-secondary to-brand-accent bg-clip-text text-transparent">
  Parsey Document Analyzer
</h1>
```
- Gradiente da marca (violeta → azul → ciano)
- Font Poppins (display)

**Badge de Versão:**
- Background: `brand-primary` com opacity 10%
- Text: `brand-emphasis`
- Rounded: `pill`

**Cards/Seções:**
- Border radius: `rounded-parsey` (24px)
- Shadow: `shadow-md` com hover `shadow-parsey`
- Border: `border-border-subtle`

**Botões:**
- Primary: `brand-primary` com hover `brand-emphasis`
- Accent highlights com `brand-highlight`

**Footer:**
- Background: Branco com blur
- Border top: `border-border-subtle`
- Mascote pequena com gradient text
- Font mascot (Nunito) no "Powered by Parsey"

### 5. FileUploader (FileUploader.tsx)

**Drop Zone:**
- Border: `border-border-default` (padrão)
- Hover: `border-brand-primary` com background `brand-highlight`
- Dragging: `border-brand-accent` com `shadow-accent` (glow ciano)
- Border radius: `rounded-parsey`

**Ícone Upload:**
- Background: Gradiente `brand-primary` → `brand-accent`
- Cor do ícone: `brand-primary`

**Texto:**
- Título: `font-display` (Poppins)
- Link "clique para selecionar": `brand-primary` com hover `brand-emphasis`

**Arquivo Selecionado:**
- Background ícone: Gradiente violeta-ciano
- Hover: `shadow-md`
- Botão remover: Hover em vermelho danger

### 6. Componentes de Análise

Todos os componentes foram atualizados para usar:

- **Badges UC**: `brand-primary` com opacity
- **Progress bars**: Cores da marca
- **Cards**: `rounded-parsey` com `shadow-md`
- **Success states**: `semantic-success` (#10B981)
- **Warning states**: `semantic-warning` (#F59E0B)
- **Danger states**: `semantic-danger` (#EF4444)
- **Info states**: `semantic-info` / `brand-accent`

## Paleta de Cores Parsey

### Cores Principais

| Nome | Hex | Uso |
|------|-----|-----|
| Violet Insight | #6366F1 | Marca principal, botões primários |
| Parsey Blue | #3B82F6 | Secundária, links |
| Deep Indigo | #1E3A8A | Ênfase, hover states |
| Soft Lilac | #A5B4FC | Highlights, badges |
| Data Cyan | #22D3EE | Accent, info, focus |
| Graph Gray | #64748B | Texto muted, borders |

### Backgrounds

| Nome | Hex | Uso |
|------|-----|-----|
| Neutral BG | #F3F4F6 | Background principal |
| Arctic White | #F9FAFB | Surfaces, cards |
| White | #FFFFFF | Elevated cards |
| Ink | #0F172A | Texto primário |

### Estados

| Nome | Hex | Uso |
|------|-----|-----|
| Success | #10B981 | Aprovado, sucesso |
| Warning | #F59E0B | Avisos, atenção |
| Danger | #EF4444 | Erros, rejeição |
| Info | #22D3EE | Informativo |

## Tipografia

### Hierarquia de Fontes

1. **Inter** (UI Text)
   - Corpo de texto
   - Parágrafos
   - Labels
   - Weights: 400, 500, 600, 700

2. **Poppins** (Display)
   - Títulos (h1, h2, h3)
   - Headings de seção
   - Weights: 600, 700

3. **Nunito** (Mascot)
   - Elementos da mascote
   - Branding especial
   - Weights: 400, 600, 700

### Tamanhos de Fonte

- XS: 12px
- SM: 14px
- MD: 16px (base)
- LG: 18px
- XL: 20px
- 2XL: 24px
- 3XL: 30px
- 4XL: 36px
- 5XL: 48px

## Efeitos Visuais

### Shadows

1. **SM**: Sutil (2px blur)
2. **MD**: Padrão (12px blur)
3. **LG**: Elevado (24px blur)
4. **Parsey**: Glow violeta (30px blur, opacity 20%)
5. **Accent**: Focus ring ciano (6px ring, opacity 20%)

### Border Radius

- XS: 4px (elementos pequenos)
- SM: 8px
- MD: 12px
- LG: 16px
- **XL / Parsey**: 24px (característico da marca)
- 2XL: 32px
- Pill: 9999px (badges)

### Animações

- **Instant**: 75ms (micro-interações)
- **Fast**: 150ms (hover, focus)
- **Base**: 250ms (padrão)
- **Slow**: 400ms (transições complexas)

**Easing:**
- In-Out: cubic-bezier(0.4, 0, 0.2, 1)
- Out: cubic-bezier(0, 0, 0.2, 1)
- In: cubic-bezier(0.4, 0, 1, 1)

## Mascote Parsey

### Integração com Vídeo Animado

**Header:**
```tsx
<video
  src={parseyVideo}
  autoPlay
  loop
  muted
  playsInline
  className="w-16 h-16 object-contain"
  poster={parseyLogo}
  onError={(e) => {
    // Fallback para imagem estática se o vídeo falhar
    const target = e.target as HTMLVideoElement;
    const img = document.createElement('img');
    img.src = parseyLogo;
    img.alt = 'Parsey - Mascote';
    img.className = 'w-16 h-16 object-contain animate-bounce-soft';
    target.parentNode?.replaceChild(img, target);
  }}
/>
<div className="absolute -inset-1 bg-gradient-to-r from-brand-primary to-brand-accent rounded-full opacity-20 blur-md"></div>
```

**Footer:**
```tsx
<video
  src={parseyVideo}
  autoPlay
  loop
  muted
  playsInline
  className="w-8 h-8 object-contain"
  poster={parseyLogo}
/>
<p className="font-mascot bg-gradient-to-r from-brand-primary to-brand-accent bg-clip-text text-transparent">
  Powered by Parsey
</p>
```

### Características

- **Vídeo animado** em loop contínuo (parsey_video.mp4)
- **Autoplay** silencioso (muted) para melhor UX
- **Poster fallback** usando imagem PNG durante carregamento
- **Tratamento de erro** com fallback para imagem estática
- **Glow effect** com gradiente da marca
- Presente no **header** (16x16) e **footer** (8x8)
- Reforça identidade visual com movimento suave

## Componentes Específicos

### Cards

```tsx
className="bg-white rounded-parsey shadow-md border border-border-subtle p-6 hover:shadow-parsey transition-shadow duration-base"
```

### Badges

```tsx
className="px-3 py-1 bg-brand-primary bg-opacity-10 text-brand-emphasis text-xs font-semibold rounded-pill"
```

### Botões Primários

```tsx
className="px-4 py-2 bg-brand-primary text-white font-semibold rounded-lg hover:bg-brand-emphasis transition-all duration-fast"
```

### Botões Ghost

```tsx
className="px-4 py-2 text-brand-primary hover:bg-brand-highlight hover:bg-opacity-20 rounded-lg transition-all duration-fast"
```

### Input/Upload Areas

```tsx
className="border-2 border-dashed border-border-default rounded-parsey hover:border-brand-primary hover:bg-brand-highlight hover:bg-opacity-10"
```

## Gradientes

### Gradiente da Marca

```css
background: linear-gradient(135deg, #6366F1 0%, #3B82F6 50%, #22D3EE 100%);
```

Usado em:
- Títulos principais
- Ícones especiais
- Glow effects
- Branding elements

### Gradiente Suave

```css
background: linear-gradient(180deg, #A5B4FC 0%, #EEF2FF 100%);
```

Usado em:
- Backgrounds sutis
- Highlights
- Hover states

## Checklist de Conformidade

- [x] Tailwind config com tokens Parsey
- [x] Fontes Google (Inter, Poppins, Nunito)
- [x] CSS global com cores Parsey
- [x] App.tsx com mascote e branding
- [x] Header com gradiente e glow
- [x] Footer com mascote
- [x] FileUploader com cores Parsey
- [x] Componentes com rounded-parsey
- [x] Shadows com parsey glow
- [x] Badges e buttons Parsey style
- [x] Animações conforme motion tokens
- [x] Typography hierarchy (Inter/Poppins/Nunito)
- [x] **Vídeo animado da mascote** (parsey_video.mp4)
- [x] **Fallback para imagem estática** em caso de erro
- [x] **Autoplay em loop** com poster
- [x] **Favicon Parsey** configurado (favicon.jpg)

## Como Testar

```bash
cd frontend
npm run dev
```

Verificar:
1. **Vídeo da mascote Parsey** no header em loop contínuo
2. **Mascote no painel principal** - Lado esquerdo da área de upload
3. Título com gradiente violeta-azul-ciano
4. Cards com border radius 24px
5. Hover com glow violeta
6. Upload area com accent ciano ao arrastar
7. Fontes: Inter (corpo), Poppins (títulos)
8. Badges com rounded pill
9. Footer com **vídeo "Powered by Parsey"**
10. Glow effect ao redor da mascote
11. Fallback para imagem estática se vídeo não carregar
12. **Favicon Parsey** na aba do navegador

## Benefícios

1. **Identidade Visual Forte**: Cores e tipografia consistentes
2. **Brand Recognition**: Mascote Parsey presente e animada
3. **Professional Look**: Shadows e gradientes refinados
4. **Smooth UX**: Animações e transições suaves
5. **Acessibilidade**: Contraste WCAG AA mantido
6. **Escalabilidade**: Tokens reutilizáveis

## Próximos Passos

- [ ] Adicionar dark mode com tokens Parsey
- [ ] Criar biblioteca de componentes Parsey
- [ ] Implementar loading states com animação Parsey
- [ ] Toast notifications com branding
- [ ] Error pages com mascote
- [ ] Onboarding tour com Parsey

---

**Design System:** Parsey v1.0.0
**Brand:** Parsey
**Updated:** 2024-10-25
