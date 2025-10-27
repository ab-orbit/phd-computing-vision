# Guia Completo de Deploy - API + Frontend

Guia passo a passo para executar a aplicação completa de geração de imagens.

---

## Pré-requisitos

### Sistema

- macOS com Apple Silicon (M1/M2/M3) ou Linux/Windows com GPU
- Python 3.10 ou superior
- Node.js 18 ou superior
- 8GB+ RAM disponível
- 10GB+ espaço em disco

### Modelo Treinado

Certifique-se de ter completado o treinamento LoRA:

```bash
# Verificar se o modelo existe
ls training/outputs/lora_casual_shoes_3000steps_full/final_pipeline/

# Deve conter:
# - model_index.json
# - unet/
# - vae/
# - text_encoder/
# - scheduler/
# - tokenizer/
```

---

## Parte 1: Setup do Backend (API)

### 1.1 Preparar Ambiente Python

```bash
# Navegar para o diretório da API
cd api

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # macOS/Linux
# OU
venv\Scripts\activate  # Windows
```

### 1.2 Instalar Dependências

```bash
# Instalar todas as dependências
pip install -r requirements.txt

# Verificar instalação do PyTorch MPS
python -c "import torch; print(f'MPS disponível: {torch.backends.mps.is_available()}')"
# Deve printar: MPS disponível: True
```

### 1.3 Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar se necessário (valores padrão já funcionam)
# vim .env
```

### 1.4 Testar API

```bash
# Iniciar servidor
python main.py

# Em outro terminal, testar health check
curl http://localhost:8000/health

# Resposta esperada:
# {
#   "status": "healthy",
#   "timestamp": "2025-01-27T10:00:00",
#   "device": "mps",
#   "models_cached": []
# }
```

### 1.5 Listar Modelos Disponíveis

```bash
curl http://localhost:8000/api/models | python -m json.tool

# Deve retornar lista de modelos incluindo:
# - base (Stable Diffusion 1.5)
# - lora_casual_shoes_3000steps_full (seu modelo treinado)
```

---

## Parte 2: Setup do Frontend (React)

### 2.1 Preparar Ambiente Node.js

```bash
# Abrir NOVO terminal
cd frontend

# Verificar versão do Node
node --version  # Deve ser 18+
npm --version
```

### 2.2 Instalar Dependências

```bash
# Instalar todas as dependências
npm install

# Aguardar conclusão (~2-3 minutos)
```

### 2.3 Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Conteúdo padrão já está correto:
# VITE_API_URL=http://localhost:8000
```

### 2.4 Iniciar Frontend

```bash
# Modo desenvolvimento com hot reload
npm run dev

# Aguardar mensagem:
# ➜  Local:   http://localhost:3000/
```

---

## Parte 3: Usando a Aplicação

### 3.1 Acessar Interface

Abra o navegador em: **http://localhost:3000**

Você verá a interface com:
- Header "Shoes Image Generator"
- Seletor de modelo
- Campo de prompt
- Botão "Ver exemplos"
- Controle de número de imagens
- Botão "Gerar Imagens"

### 3.2 Primeira Geração

1. **Selecione o Modelo:**
   - Clique no dropdown "Modelo"
   - Escolha "Lora Casual Shoes 3000Steps Full"

2. **Use um Exemplo:**
   - Clique em "Ver exemplos"
   - Navegue pelas categorias:
     - Cores Básicas
     - Materiais
     - Estilos
     - Detalhes Especiais
   - Clique em qualquer exemplo para usar o prompt

3. **Configure Parâmetros:**
   - Ajuste o slider "Número de Imagens" (recomendado: 4)

4. **Gere:**
   - Clique em "Gerar Imagens"
   - Aguarde (~45-60 segundos para 4 imagens)
   - Toast mostrará progresso

5. **Visualize:**
   - Imagens aparecem em galeria
   - Hover sobre imagem mostra botões de ação
   - Clique na imagem para ver em tamanho maior

6. **Download:**
   - Clique no ícone de download
   - Ou abra modal e clique em "Download"
   - Imagem salva automaticamente

### 3.3 Criar Prompt Customizado

Estrutura de prompt recomendada:

```
A professional product photo of [COR] [MATERIAL] [TIPO] shoes
on white background, [CARACTERÍSTICAS], product photography
```

Exemplos:

```
A professional product photo of burgundy suede casual loafers
on white background, elegant design, product photography

A professional product photo of white canvas sneakers with blue details
on white background, modern sporty design, product photography

A professional product photo of dark brown leather oxford shoes
on white background, classic formal style, product photography
```

---

## Parte 4: Teste End-to-End

### 4.1 Script de Teste Completo

```bash
# Criar script de teste
cat > test_e2e.sh << 'EOF'
#!/bin/bash
set -e

echo "=== Teste End-to-End ==="

# 1. Health check
echo "1. Testando health check..."
response=$(curl -s http://localhost:8000/health)
if echo "$response" | grep -q "healthy"; then
    echo "✓ API está healthy"
else
    echo "✗ API não está respondendo"
    exit 1
fi

# 2. Listar modelos
echo "2. Listando modelos..."
models=$(curl -s http://localhost:8000/api/models | python -m json.tool)
echo "$models"

# 3. Obter exemplos
echo "3. Obtendo exemplos de prompts..."
examples=$(curl -s http://localhost:8000/api/prompts/examples | python -m json.tool | head -20)
echo "$examples"

# 4. Gerar imagem de teste
echo "4. Gerando imagem de teste..."
curl -X POST "http://localhost:8000/api/generate" \
     -H "Content-Type: application/json" \
     -d '{
           "model_name": "lora_casual_shoes_3000steps_full",
           "prompt": "A professional product photo of black casual shoes on white background",
           "num_images": 1,
           "num_inference_steps": 30
         }' > test_response.json

echo "✓ Resposta salva em test_response.json"

# 5. Verificar resposta
if grep -q "success" test_response.json && grep -q "true" test_response.json; then
    echo "✓ Imagem gerada com sucesso!"
else
    echo "✗ Erro na geração"
    cat test_response.json
    exit 1
fi

echo ""
echo "=== Todos os testes passaram! ==="
EOF

chmod +x test_e2e.sh
./test_e2e.sh
```

### 4.2 Verificar Imagem Gerada

```bash
# Extrair imagem base64 e salvar
python << EOF
import json
import base64

with open('test_response.json', 'r') as f:
    data = json.load(f)

image_data = data['images'][0]['image_data']
image_bytes = base64.b64decode(image_data)

with open('test_output.png', 'wb') as f:
    f.write(image_bytes)

print("Imagem salva: test_output.png")
EOF

# Abrir imagem
open test_output.png  # macOS
# xdg-open test_output.png  # Linux
# start test_output.png  # Windows
```

---

## Parte 5: Monitoramento

### 5.1 Logs da API

```bash
# Terminal com API rodando mostra logs em tempo real:

# Log de startup
2025-01-27 10:00:00 - INFO - Shoes Image Generation API - Iniciando
2025-01-27 10:00:00 - INFO - Device: mps
2025-01-27 10:00:00 - INFO - Modelos disponíveis: 2

# Log de requisição
2025-01-27 10:01:00 - INFO - Iniciando geração: modelo='casual_shoes',
                             prompt='A professional product photo...',
                             num_images=4
2025-01-27 10:01:00 - INFO - Carregando modelo 'casual_shoes'...
2025-01-27 10:01:05 - INFO - Modelo 'casual_shoes' carregado com sucesso
2025-01-27 10:01:10 - INFO - Gerando imagem 1/4 (seed=12345)
2025-01-27 10:01:25 - INFO - Gerando imagem 2/4 (seed=12346)
...
2025-01-27 10:02:00 - INFO - Geração concluída: 4 imagens em 60.2s
```

### 5.2 Monitorar Uso de Memória

```bash
# macOS - Activity Monitor
# Buscar por "Python" e verificar uso de memória

# Ou via terminal
ps aux | grep python | grep main.py
```

### 5.3 Dashboard de Monitoramento (Opcional)

```bash
# Instalar htop para monitoramento visual
brew install htop  # macOS
# sudo apt install htop  # Linux

# Executar
htop
```

---

## Parte 6: Troubleshooting

### 6.1 API não inicia

**Erro: MPS not available**

```bash
# Verificar PyTorch
python -c "import torch; print(torch.__version__)"

# Reinstalar PyTorch com MPS
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

**Erro: Port 8000 already in use**

```bash
# Matar processo na porta 8000
lsof -ti:8000 | xargs kill -9

# Ou usar outra porta
uvicorn main:app --port 8001
```

### 6.2 Frontend não conecta

**Erro: Network Error**

```bash
# Verificar que API está rodando
curl http://localhost:8000/health

# Verificar CORS
# Editar api/main.py e adicionar origem do frontend em CORS
```

**Erro: Cannot find module**

```bash
# Limpar e reinstalar
rm -rf node_modules package-lock.json
npm install
```

### 6.3 Geração muito lenta

**Otimizações:**

```python
# Em api/main.py, adicionar após carregar pipeline:

# Reduzir precisão (mais rápido, menor qualidade)
pipeline.enable_attention_slicing()

# Ou usar menos steps (mais rápido)
# No frontend, ajustar num_inference_steps de 50 para 25-30
```

### 6.4 Out of Memory

```bash
# Reduzir batch size
# No frontend, gere menos imagens por vez (1-2 em vez de 4-8)

# Ou limpar cache de modelos
# Reiniciar API
```

---

## Parte 7: Produção

### 7.1 Build do Frontend

```bash
cd frontend

# Build otimizado
npm run build

# Arquivos em dist/
ls -lh dist/

# Servir localmente para testar
npm run preview
```

### 7.2 Deploy da API

```bash
cd api

# Instalar Gunicorn
pip install gunicorn

# Executar com workers
gunicorn main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300
```

### 7.3 Deploy do Frontend

**Vercel (Recomendado):**

```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

**Netlify:**

```bash
# Instalar Netlify CLI
npm i -g netlify-cli

# Deploy
cd frontend
netlify deploy --prod --dir=dist
```

### 7.4 Configurar HTTPS

**Nginx como Reverse Proxy:**

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

---

## Checklist Final

```
[ ] Python 3.10+ instalado
[ ] Node.js 18+ instalado
[ ] Modelo treinado existe em training/outputs/
[ ] Ambiente virtual Python criado e ativado
[ ] Dependências Python instaladas (pip install -r requirements.txt)
[ ] API iniciada e respondendo em localhost:8000
[ ] Health check retorna "healthy"
[ ] Modelos listados corretamente via /api/models
[ ] Dependências Node instaladas (npm install)
[ ] Frontend iniciado em localhost:3000
[ ] Interface carrega sem erros
[ ] Consegue selecionar modelo
[ ] Exemplos de prompts aparecem
[ ] Geração de imagem funciona
[ ] Imagens aparecem na galeria
[ ] Download de imagem funciona
[ ] Modal de visualização abre
```

---

## Recursos Adicionais

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Frontend DevTools**: F12 no navegador
- **API Logs**: Terminal onde API está rodando

---

## Próximos Passos

1. Testar diferentes prompts e estilos
2. Explorar variações com seeds diferentes
3. Comparar modelos (base vs fine-tuned)
4. Ajustar parâmetros (guidance_scale, inference_steps)
5. Implementar features adicionais (histórico, favoritos, etc.)

---

**Documentação criada:** 27/01/2025
**Última atualização:** 27/01/2025
