# Shoes Image Generator - Frontend

Interface React moderna para geração de imagens de sapatos usando IA.

## Features

- Interface moderna e responsiva com Tailwind CSS
- Animações suaves com Framer Motion
- Seleção de modelos LoRA treinados
- Biblioteca de prompts de exemplo categorizados
- Galeria de imagens com visualização em modal
- Download de imagens geradas
- Notificações toast elegantes
- Suporte para geração em lote (1-8 imagens)

## Tecnologias

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Framer Motion
- Axios
- React Hot Toast
- Lucide Icons

## Instalação

```bash
# Navegar para o diretório frontend
cd frontend

# Instalar dependências
npm install
```

## Configuração

```bash
# Copiar arquivo de ambiente
cp .env.example .env

# Editar .env se necessário (URL da API)
```

## Execução

```bash
# Modo desenvolvimento (http://localhost:3000)
npm run dev

# Build para produção
npm run build

# Preview do build
npm run preview
```

## Uso

1. **Selecione um Modelo**: Escolha entre o modelo base ou modelos fine-tuned
2. **Insira um Prompt**: Digite a descrição da imagem desejada ou selecione um exemplo
3. **Configure Parâmetros**: Ajuste o número de imagens (1-8)
4. **Gere**: Clique em "Gerar Imagens" e aguarde
5. **Visualize**: Imagens aparecem em galeria interativa
6. **Download**: Clique no botão de download em cada imagem

## Estrutura do Projeto

```
frontend/
├── src/
│   ├── App.tsx           # Componente principal
│   ├── main.tsx          # Entry point
│   ├── api.ts            # Serviço de API
│   ├── types.ts          # Tipos TypeScript
│   └── index.css         # Estilos globais
├── public/               # Assets estáticos
├── index.html            # HTML template
├── package.json          # Dependências
├── vite.config.ts        # Configuração Vite
├── tailwind.config.js    # Configuração Tailwind
└── tsconfig.json         # Configuração TypeScript
```

## Customização

### Cores e Tema

Edite `tailwind.config.js` para customizar o tema:

```javascript
theme: {
  extend: {
    colors: {
      primary: '#8b5cf6',  // Purple
      secondary: '#ec4899', // Pink
    },
  },
}
```

### API URL

Altere a URL da API em `.env`:

```
VITE_API_URL=http://seu-servidor:8000
```

## Build e Deploy

```bash
# Build para produção
npm run build

# Arquivos otimizados estarão em dist/
```

Deploy em:
- **Vercel**: `vercel --prod`
- **Netlify**: `netlify deploy --prod`
- **GitHub Pages**: Configure workflow action

## Performance

- Lazy loading de imagens
- Otimização de bundle com Vite
- Code splitting automático
- Assets otimizados

## Browser Support

- Chrome/Edge (últimas 2 versões)
- Firefox (últimas 2 versões)
- Safari (últimas 2 versões)

## Desenvolvimento

### Adicionar Nova Feature

1. Crie componente em `src/components/`
2. Adicione tipos em `src/types.ts`
3. Importe e use em `App.tsx`

### Estilização

Use classes Tailwind diretamente nos componentes:

```tsx
<div className="bg-gray-800 rounded-lg p-4 hover:bg-gray-700 transition-colors">
  Conteúdo
</div>
```

## Troubleshooting

### Erro de CORS

Certifique-se que a API está rodando e configurada para aceitar requisições do frontend (porta 3000).

### Imagens não aparecem

Verifique que a API retorna `image_data` em base64 válido.

### Build falha

Limpe cache e reinstale:
```bash
rm -rf node_modules package-lock.json
npm install
```

## Screenshots

[Adicione screenshots da aplicação aqui]

## Licença

Este projeto é para fins educacionais.
