# Guia de Assets - Parsey Document Analyzer

Documentação completa de todos os assets visuais da Parsey e suas utilizações na aplicação.

**Versão:** 1.2.0
**Data:** 2025-10-25

---

## 1. Inventário de Assets

### Imagens

| Arquivo | Tamanho | Uso Principal | Localização |
|---------|---------|---------------|-------------|
| `parsey-logo.png` | 122 KB | Logo no header | Header (topo) |
| `parsey.png` | 798 KB | Mascote painel principal | Card de upload |
| `parsey_layed.png` | 218 KB | Retorno não-científico | Mensagem de erro |
| `favicon.jpg` | 132 KB | Favicon navegador | Tab do browser |

### Vídeos

| Arquivo | Tamanho | Uso Principal | Localização |
|---------|---------|---------------|-------------|
| `parsey_video.mp4` | 2.4 MB | Animação mascote | Footer |

---

## 2. Uso por Contexto

### Header (Topo da Aplicação)

**Asset:** `parsey-logo.png`
**Tamanho:** h-16 (64px altura)
**Objetivo:** Identidade visual profissional

```tsx
import parseyLogoHeader from './images/parsey-logo.png';

<img
  src={parseyLogoHeader}
  alt="Parsey Logo"
  className="h-16 object-contain"
/>
```

**Características:**
- Logo completa da Parsey
- Altura fixa de 64px
- Largura proporcional (object-contain)
- Sem animação (profissionalismo)
- Posicionada à esquerda do título

**Visual:**
```
┌─────────────────────────────────────┐
│ [LOGO] Parsey Document Analyzer     │
│        Classificação • Detecção...  │
└─────────────────────────────────────┘
```

---

### Painel Principal (Área de Upload)

**Asset:** `parsey.png`
**Tamanho:** w-40 h-40 (160x160px)
**Objetivo:** Humanização e acolhimento

```tsx
import parseyLogo from './images/parsey.png';

<div className="relative mb-6">
  <div className="absolute -inset-4 bg-gradient-to-r
                  from-brand-primary via-brand-secondary to-brand-accent
                  rounded-full opacity-20 blur-xl animate-pulse"></div>
  <img
    src={parseyLogo}
    alt="Parsey - Sua assistente de análise"
    className="relative w-40 h-40 object-contain animate-bounce-soft"
  />
</div>
```

**Características:**
- Mascote grande e amigável
- Animação bounce-soft (movimento suave)
- Glow effect com gradiente pulsante
- Background gradiente suave
- Acompanhada de texto de apresentação

**Layout:**
```
┌───────────────────────────────────┐
│  ┌──────┐  ┌─────────────────┐   │
│  │  🦊  │  │  Arraste seu    │   │
│  │      │  │  documento      │   │
│  │Olá!  │  │                 │   │
│  │Sou a │  │                 │   │
│  │Parsey│  │                 │   │
│  └──────┘  └─────────────────┘   │
└───────────────────────────────────┘
```

---

### Retorno Não-Científico (Mensagem de Erro)

**Asset:** `parsey_layed.png`
**Tamanho:** w-48 h-48 (192x192px)
**Objetivo:** Comunicar erro de forma amigável

```tsx
import parseyLayed from './images/parsey_layed.png';

<div className="relative">
  <div className="absolute -inset-4 bg-gradient-to-r
                  from-semantic-warning to-amber-400
                  rounded-full opacity-10 blur-xl"></div>
  <img
    src={parseyLayed}
    alt="Parsey - Documento não científico"
    className="relative w-48 h-48 object-contain"
  />
</div>
```

**Características:**
- Mascote em postura "layed" (relaxada/deitada)
- Glow effect em tons amber (warning)
- Sem animação (mensagem séria)
- Acompanhada de explicação clara

**Quando aparece:**
- Documento classificado como NÃO-artigo científico
- UC2, UC3, UC4 não executados
- Mensagem explicativa ao lado

**Layout:**
```
┌─────────────────────────────────────────┐
│  ┌──────┐  ┌──────────────────────┐   │
│  │  😴  │  │ ⚠️ Análise           │   │
│  │      │  │    Interrompida      │   │
│  │Parsey│  │                      │   │
│  │Layed │  │ Documento não é      │   │
│  │      │  │ artigo científico    │   │
│  └──────┘  └──────────────────────┘   │
└─────────────────────────────────────────┘
```

---

### Footer (Rodapé)

**Asset:** `parsey_video.mp4`
**Tamanho:** w-8 h-8 (32x32px)
**Objetivo:** Branding sutil e moderno

```tsx
import parseyVideo from './images/parsey_video.mp4';

<video
  src={parseyVideo}
  autoPlay
  loop
  muted
  playsInline
  className="w-8 h-8 object-contain"
  poster={parseyLogo}
/>
<p className="font-mascot bg-gradient-to-r
              from-brand-primary to-brand-accent
              bg-clip-text text-transparent">
  Powered by Parsey
</p>
```

**Características:**
- Vídeo pequeno (32x32)
- Loop infinito silencioso
- Movimento sutil
- Texto com gradiente da marca

---

### Favicon (Tab do Browser)

**Asset:** `favicon.jpg`
**Tamanho:** 132 KB (16x16 renderizado)
**Objetivo:** Identidade visual em abas

```html
<link rel="icon" type="image/jpeg" href="/favicon.jpg" />
<link rel="apple-touch-icon" href="/favicon.jpg" />
```

**Características:**
- JPEG otimizado para web
- Compatível com iOS (Apple Touch Icon)
- Visível em tabs, favoritos, histórico

---

## 3. Matriz de Decisão de Assets

### Quando usar cada asset?

| Contexto | Asset | Razão |
|----------|-------|-------|
| **Branding profissional** | `parsey-logo.png` | Logo completa, sem animação |
| **Interação amigável** | `parsey.png` | Mascote expressiva com animação |
| **Erro/Warning** | `parsey_layed.png` | Postura relaxada indica pausa |
| **Movimento sutil** | `parsey_video.mp4` | Vídeo para dinamismo |
| **Identidade persistente** | `favicon.jpg` | Sempre visível na aba |

---

## 4. Especificações Técnicas

### Formatos

**PNG (parsey-logo.png, parsey.png, parsey_layed.png):**
- Transparência alfa
- Alta qualidade
- Ideal para logos e mascotes
- Peso maior, mas qualidade preservada

**JPEG (favicon.jpg):**
- Sem transparência
- Otimizado para tamanho
- Ideal para favicons
- Compatibilidade universal

**MP4 (parsey_video.mp4):**
- Codificação H.264
- Compressão eficiente
- Autoplay compatível
- Mobile-friendly

### Dimensões Renderizadas

| Asset | Desktop | Mobile | Contexto Especial |
|-------|---------|--------|-------------------|
| Logo Header | 64px altura | 48px altura | - |
| Mascote Principal | 160x160 | 120x120 | Grid 1 coluna |
| Parsey Layed | 192x192 | 144x144 | Erro não-científico |
| Vídeo Footer | 32x32 | 24x24 | - |
| Favicon | 16x16 | 16x16 | - |

---

## 5. Animações por Asset

### parsey.png (Painel Principal)

**Animação da Imagem:**
```css
animation: bounceSoft 2s infinite;

@keyframes bounceSoft {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
```

**Animação do Glow:**
```css
animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
```

**Resultado:**
- Movimento vertical suave
- Glow pulsante sincronizado
- Efeito acolhedor

### parsey_layed.png (Erro)

**Animação:** Nenhuma (estático)

**Razão:**
- Mensagem séria requer sobriedade
- Sem distração do conteúdo
- Glow sutil sem pulsar

### parsey-logo.png (Header)

**Animação:** Nenhuma (estático)

**Razão:**
- Profissionalismo
- Logo institucional não anima
- Estabilidade visual

### parsey_video.mp4 (Footer)

**Animação:** Nativa do vídeo

**Configuração:**
- `autoPlay` - Inicia automaticamente
- `loop` - Loop infinito
- `muted` - Sem áudio
- `playsInline` - Mobile sem fullscreen

---

## 6. Gradientes e Efeitos

### Glow Effect (Painel Principal)

```css
.glow-parsey {
  position: absolute;
  inset: -16px;
  background: linear-gradient(
    to right,
    #6366F1,  /* brand-primary */
    #3B82F6,  /* brand-secondary */
    #22D3EE   /* brand-accent */
  );
  border-radius: 9999px;
  opacity: 0.2;
  filter: blur(48px);
  animation: pulse 2s infinite;
}
```

### Glow Effect (Erro - Warning)

```css
.glow-warning {
  position: absolute;
  inset: -16px;
  background: linear-gradient(
    to right,
    #F59E0B,  /* semantic-warning */
    #FBBF24   /* amber-400 */
  );
  border-radius: 9999px;
  opacity: 0.1;
  filter: blur(48px);
  /* Sem animação */
}
```

---

## 7. Acessibilidade

### Texto Alternativo (Alt Text)

| Asset | Alt Text | Contexto |
|-------|----------|----------|
| `parsey-logo.png` | "Parsey Logo" | Identificação da marca |
| `parsey.png` | "Parsey - Sua assistente de análise" | Função e personalidade |
| `parsey_layed.png` | "Parsey - Documento não científico" | Estado e contexto |
| `parsey_video.mp4` | N/A (decorativo) | Não essencial para compreensão |

### Contraste

**Backgrounds:**
- Logo Header: Fundo branco (contraste máximo)
- Mascote Principal: Gradiente 5% opacidade (legível)
- Parsey Layed: Fundo amber 50 (WCAG AA)

**Texto Associado:**
- Sempre em cores de alto contraste
- Títulos: text-primary (#0F172A)
- Corpo: text-secondary (#334155)

---

## 8. Performance

### Lazy Loading

**Estratégia:**
- Header logo: Carregamento imediato (above fold)
- Mascote painel: Carregamento imediato (interação inicial)
- Parsey layed: Lazy (apenas em erro)
- Vídeo footer: Lazy (below fold)

### Otimização de Tamanho

| Asset | Tamanho Original | Compressão | Resultado |
|-------|------------------|------------|-----------|
| parsey-logo.png | ~300 KB | Otimizada | 122 KB |
| parsey.png | ~1.2 MB | Otimizada | 798 KB |
| parsey_layed.png | ~400 KB | Otimizada | 218 KB |
| favicon.jpg | ~200 KB | JPEG 85% | 132 KB |
| parsey_video.mp4 | ~5 MB | H.264 médio | 2.4 MB |

**Total:** ~3.67 MB de assets Parsey

---

## 9. Fallbacks

### Vídeo (Footer)

```tsx
<video
  poster={parseyLogo}  // Fallback durante carregamento
  onError={(e) => {
    // Fallback se vídeo falhar
    const img = document.createElement('img');
    img.src = parseyLogo;
    target.parentNode?.replaceChild(img, target);
  }}
/>
```

### Imagens

- Browser moderno: PNG com transparência
- Browser antigo: Degradação graciosa (sem transparência)

### Favicon

```html
<!-- JPEG primário -->
<link rel="icon" type="image/jpeg" href="/favicon.jpg" />

<!-- Fallback SVG se navegador suportar -->
<link rel="icon" type="image/svg+xml" href="/vite.svg" />
```

---

## 10. Guia de Uso Rápido

### Desenvolvedor: Como escolher o asset?

**Pergunta 1:** É para o header/topo?
→ **SIM:** Use `parsey-logo.png`

**Pergunta 2:** É para interação com usuário (upload, mensagem positiva)?
→ **SIM:** Use `parsey.png` com animação

**Pergunta 3:** É para mensagem de erro/warning?
→ **SIM:** Use `parsey_layed.png` sem animação

**Pergunta 4:** É para rodapé/branding sutil?
→ **SIM:** Use `parsey_video.mp4`

**Pergunta 5:** É para favicon/ícone?
→ **SIM:** Use `favicon.jpg`

---

## 11. Exemplos de Código

### Importar Assets

```tsx
// App.tsx
import parseyLogo from './images/parsey.png';
import parseyLogoHeader from './images/parsey-logo.png';
import parseyLayed from './images/parsey_layed.png';
import parseyVideo from './images/parsey_video.mp4';
```

### Header com Logo

```tsx
<header>
  <img
    src={parseyLogoHeader}
    alt="Parsey Logo"
    className="h-16 object-contain"
  />
  <h1>Parsey Document Analyzer</h1>
</header>
```

### Painel Principal com Mascote

```tsx
<div className="grid grid-cols-12">
  <div className="col-span-4">
    <div className="relative">
      <div className="glow-effect"></div>
      <img
        src={parseyLogo}
        alt="Parsey - Sua assistente"
        className="w-40 h-40 animate-bounce-soft"
      />
    </div>
    <h3>Olá! Sou a Parsey</h3>
  </div>
  <div className="col-span-8">
    <FileUploader />
  </div>
</div>
```

### Erro com Parsey Layed

```tsx
{!isScientific && (
  <div className="grid grid-cols-12">
    <div className="col-span-4">
      <img
        src={parseyLayed}
        alt="Parsey - Documento não científico"
        className="w-48 h-48"
      />
    </div>
    <div className="col-span-8">
      <h3>Análise Interrompida</h3>
      <p>Documento não é artigo científico...</p>
    </div>
  </div>
)}
```

---

## 12. Checklist de Implementação

### Ao adicionar novo asset Parsey:

- [ ] Otimizar tamanho (< 500 KB se possível)
- [ ] Adicionar alt text descritivo
- [ ] Definir dimensões responsivas
- [ ] Considerar animação (ou não)
- [ ] Definir glow effect (se aplicável)
- [ ] Testar em mobile e desktop
- [ ] Documentar uso neste arquivo
- [ ] Atualizar INTEGRATION_SUMMARY.md

---

## Resumo de Assets

| Asset | Contexto | Tamanho Render | Animação | Glow |
|-------|----------|----------------|----------|------|
| `parsey-logo.png` | Header | h-16 | ❌ | ❌ |
| `parsey.png` | Painel Upload | 160x160 | ✅ Bounce | ✅ Pulse |
| `parsey_layed.png` | Erro | 192x192 | ❌ | ✅ Estático |
| `parsey_video.mp4` | Footer | 32x32 | ✅ Nativa | ❌ |
| `favicon.jpg` | Browser Tab | 16x16 | ❌ | ❌ |

---

**Versão:** 1.2.0
**Design System:** Parsey v1.0.0
**Última atualização:** 2025-10-25
