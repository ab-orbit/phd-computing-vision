# Parsey Design System

## 1. Identidade Visual

### Elemento	Descrição
Espécie / Personalidade	Raposa feminina, analítica, inteligente e empática. Representa curiosidade científica e precisão técnica.
Estilo Visual	Clean tech + soft 3D cartoon. Combina tecnologia e simpatia. Equilíbrio entre mascote amigável e símbolo institucional.
Postura	Em pé, confiante, com um laptop holográfico e uma lupa. Expressão curiosa e confiante.
Símbolo Peitoral (P)	Logotipo minimalista integrado — base para favicon e variações de identidade.


⸻

## 2. Paleta de Cores

Nome	Hex	Uso
Parsey Blue	#3B82F6	Cor primária (olhos, detalhes luminosos)
Violet Insight	#6366F1	Cor secundária, usada em sombras e pelagem intermediária
Deep Indigo	#1E3A8A	Base da pelagem, dá contraste e profundidade
Soft Lilac	#A5B4FC	Destaques, gradientes suaves
Arctic White	#F9FAFB	Pelo interno e luz principal
Data Cyan	#22D3EE	Circuitos digitais e acentos tecnológicos
Graph Gray	#64748B	Sombras, elementos neutros
Background Neutral	#F3F4F6	Plano de fundo claro em dashboards


⸻

## 3. Tipografia Recomendada

Categoria	Fonte	Uso
Primária (UI)	Inter (sans-serif)	Interface, dashboards, texto técnico
Secundária (Brand)	Poppins	Títulos e headings da marca
Alternativa (Mascote/Promo)	Nunito	Materiais de marketing e comunicações visuais mais amigáveis


⸻

## 4. Componentização / UI Tokens (Tailwind)

// tailwind.config.js excerpt
theme: {
  extend: {
    colors: {
      parsey: {
        blue: '#3B82F6',
        violet: '#6366F1',
        indigo: '#1E3A8A',
        lilac: '#A5B4FC',
        cyan: '#22D3EE',
        white: '#F9FAFB',
        gray: '#64748B',
      },
    },
    fontFamily: {
      sans: ['Inter', 'sans-serif'],
      display: ['Poppins', 'sans-serif'],
      mascot: ['Nunito', 'sans-serif'],
    },
    boxShadow: {
      parsey: '0 4px 20px rgba(99, 102, 241, 0.25)',
    },
  },
}


⸻

## 5. Ícones e Estilo de Linhas
	•	Baseado em Lucide / Heroicons
	•	Linhas de 1.5–2px
	•	Cores: parsey.blue e parsey.violet
	•	Aplicar microglow (#22D3EE a 20%) para hover states

⸻

## 6. Personalidade de Marca

Atributo	Descrição
Tom de voz	Confiante, analítico, gentil e encorajador
Palavras-chave	“Precisão”, “Clareza”, “Curiosidade”, “Insight”
Arquétipo	O “Sábio” com traços do “Explorador”
Tagline sugerida	“Parsey analisa, você decide.” ou “Insights claros, análises confiáveis.”


⸻

## 7. Aplicações

Contexto	Variação
Logo principal	Raposa completa com laptop e lupa
Ícone app / favicon	Letra “P” no peito em fundo lilás ou azul
Splash / Onboarding	Parsey olhando gráficos flutuantes
Estado de erro / vazio	Parsey confusa com lupa virada
Animação (loop)	Piscar de olhos e brilho pulsante no laptop
