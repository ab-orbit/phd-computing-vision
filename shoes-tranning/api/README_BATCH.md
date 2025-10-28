# Geração em Lote de Imagens

Script para automatizar a geração de múltiplas imagens a partir de uma lista de prompts.

---

## Uso

### Sintaxe Básica

```bash
cd api
./generate_batch.sh <prompt_file> <num_images> [model_name]
```

### Parâmetros

| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `prompt_file` | ✅ | Arquivo de texto com um prompt por linha |
| `num_images` | ✅ | Número de imagens a gerar por prompt (1-10) |
| `model_name` | ❌ | Nome do modelo. Se omitido, usa o checkpoint mais recente |

---

## Exemplos

### 1. Usar Modelo Mais Recente (Automático)

```bash
./generate_batch.sh example_prompts.txt 3
```

**O que faz**:
- Detecta automaticamente o checkpoint mais recente
- Gera 3 imagens para cada prompt
- Salva em `generated_batch/batch_TIMESTAMP/`

### 2. Especificar Modelo

```bash
./generate_batch.sh example_prompts.txt 5 lora_casual_shoes_3000steps_full/checkpoint-1500
```

**O que faz**:
- Usa o checkpoint-1500 especificado
- Gera 5 imagens para cada prompt

### 3. Usar Modelo Base

```bash
./generate_batch.sh example_prompts.txt 2 base
```

**O que faz**:
- Usa o modelo base Stable Diffusion 1.5
- Gera 2 imagens para cada prompt

---

## Formato do Arquivo de Prompts

### Estrutura

```text
# Comentários começam com #
# Linhas vazias são ignoradas

casual brown leather shoes, product photography
elegant black oxford shoes, studio lighting
comfortable white sneakers, modern design
```

### Regras

- ✅ Um prompt por linha
- ✅ Linhas começando com `#` são comentários
- ✅ Linhas vazias são ignoradas
- ✅ Prompts podem ter qualquer tamanho
- ❌ Não usar aspas ao redor dos prompts

### Exemplo Completo

Veja `example_prompts.txt` para um exemplo funcional.

---

## Estrutura de Saída

### Diretórios Criados

```
generated_batch/
└── batch_20251027_220000/          # Timestamp do lote
    ├── index.html                   # Galeria HTML para visualização
    ├── prompt_1_casual_brown/
    │   ├── prompt.txt               # Prompt original
    │   ├── image_01.png
    │   ├── image_02.png
    │   └── image_03.png
    ├── prompt_2_elegant_black/
    │   ├── prompt.txt
    │   ├── image_01.png
    │   ├── image_02.png
    │   └── image_03.png
    └── ...
```

### Arquivos Gerados

| Arquivo | Descrição |
|---------|-----------|
| `index.html` | Galeria HTML interativa com todas as imagens |
| `prompt_N_*/prompt.txt` | Prompt original usado |
| `prompt_N_*/image_*.png` | Imagens geradas |
| `prompt_N_*/error.json` | (Se houver erro) Detalhes do erro |

---

## Visualização dos Resultados

### 1. Abrir Galeria HTML

```bash
# No macOS
open generated_batch/batch_TIMESTAMP/index.html

# No Linux
xdg-open generated_batch/batch_TIMESTAMP/index.html

# No Windows
start generated_batch/batch_TIMESTAMP/index.html
```

### 2. Navegar pelos Arquivos

```bash
cd generated_batch/batch_TIMESTAMP
ls -R
```

---

## Output do Script

### Durante Execução

```
================================
Geração em Lote de Imagens
================================
Arquivo de prompts: example_prompts.txt
Total de prompts: 4
Imagens por prompt: 3
Modelo: lora_casual_shoes_3000steps_full/checkpoint-1500
Diretório de saída: generated_batch
================================

[1/4] Gerando imagens para: "casual brown leather shoes, product photography"
  ✓ Geração bem-sucedida
  ✓ 3 imagens salvas em: generated_batch/batch_20251027_220000/prompt_1_casual_brown

[2/4] Gerando imagens para: "elegant black oxford shoes, studio lighting"
  ✓ Geração bem-sucedida
  ✓ 3 imagens salvas em: generated_batch/batch_20251027_220000/prompt_2_elegant_black

...
```

### Resumo Final

```
================================
Resumo da Geração
================================
Total processado: 4 prompts
Bem-sucedidos: 4
Falhas: 0
Total de imagens: 12
Diretório: generated_batch/batch_20251027_220000
================================

✓ Índice HTML criado: generated_batch/batch_20251027_220000/index.html

Para visualizar os resultados, abra:
  open generated_batch/batch_20251027_220000/index.html
```

---

## Detecção Automática de Modelo

### Como Funciona

Quando o parâmetro `model_name` é omitido:

1. Script consulta a API para listar modelos disponíveis
2. Filtra modelos por prioridade:
   - **Checkpoints** (ex: checkpoint-1500) - Maior step primeiro
   - **Final** (modelo final treinado)
   - **Base** (fallback)
3. Seleciona o modelo com maior número de steps

### Exemplo de Seleção

Modelos disponíveis:
```
- base
- lora_casual_shoes_3000steps_full/checkpoint-500
- lora_casual_shoes_3000steps_full/checkpoint-1000
- lora_casual_shoes_3000steps_full/checkpoint-1500  ← Selecionado
- lora_casual_shoes_3000steps_full/final
```

**Resultado**: `checkpoint-1500` (maior step number)

---

## Configurações Avançadas

### Editar Script

Abra `generate_batch.sh` e modifique as variáveis:

```bash
# URL da API
API_URL="http://localhost:8011"

# Diretório de saída
OUTPUT_DIR="generated_batch"
```

### Parâmetros de Geração

No script, a seção `JSON_PAYLOAD` define os parâmetros:

```json
{
  "num_inference_steps": 50,    // Passos de inferência (mais = melhor qualidade)
  "guidance_scale": 7.5,         // Força de seguir o prompt (7-9 recomendado)
  "seed": null                   // Seed aleatório (ou fixo para reprodutibilidade)
}
```

Para modificar, edite as linhas 125-132 do script.

---

## Troubleshooting

### Erro: "Arquivo não encontrado"

**Problema**: Arquivo de prompts não existe

**Solução**:
```bash
# Verificar se arquivo existe
ls -la example_prompts.txt

# Usar caminho absoluto
./generate_batch.sh /caminho/completo/para/prompts.txt 3
```

### Erro: "Falha ao conectar à API"

**Problema**: API não está rodando

**Solução**:
```bash
# Verificar se API está ativa
curl http://localhost:8011/api/models

# Iniciar API
cd api
python main.py
```

### Erro: "Número de imagens deve ser entre 1 e 10"

**Problema**: Parâmetro inválido

**Solução**:
```bash
# Usar número válido
./generate_batch.sh prompts.txt 5  # ✅
./generate_batch.sh prompts.txt 15 # ❌
```

### Geração Falha para Alguns Prompts

**Problema**: Prompts muito longos ou caracteres especiais

**Solução**:
- Simplificar prompts
- Remover caracteres especiais (`"`, `'`, `\`)
- Limitar tamanho dos prompts a ~200 caracteres

---

## Performance

### Tempo de Geração

| Configuração | Tempo por Imagem | Tempo por Prompt (3 imgs) |
|--------------|------------------|---------------------------|
| MPS (Apple Silicon) | ~15-20s | ~45-60s |
| CPU | ~60-90s | ~3-5min |
| GPU NVIDIA | ~5-10s | ~15-30s |

### Estimativas para Lote

| Prompts | Imagens/Prompt | Total Imagens | Tempo Estimado (MPS) |
|---------|----------------|---------------|----------------------|
| 10 | 3 | 30 | ~8-10 min |
| 20 | 5 | 100 | ~25-30 min |
| 50 | 2 | 100 | ~25-30 min |

---

## Casos de Uso

### 1. Validação de Checkpoints

Testar diferentes checkpoints com os mesmos prompts:

```bash
./generate_batch.sh validation_prompts.txt 3 lora_casual_shoes_3000steps_full/checkpoint-500
./generate_batch.sh validation_prompts.txt 3 lora_casual_shoes_3000steps_full/checkpoint-1000
./generate_batch.sh validation_prompts.txt 3 lora_casual_shoes_3000steps_full/checkpoint-1500
```

### 2. Geração de Dataset

Criar dataset de imagens sintéticas:

```bash
./generate_batch.sh dataset_prompts.txt 10
```

### 3. A/B Testing

Comparar resultados de diferentes modelos:

```bash
./generate_batch.sh test_prompts.txt 5 base
./generate_batch.sh test_prompts.txt 5 lora_casual_shoes_3000steps_full/final
```

### 4. Exploração de Variações

Gerar múltiplas variações do mesmo conceito:

```bash
# prompts.txt com 10 variações do mesmo tema
./generate_batch.sh shoe_variations.txt 3
```

---

## Integração com Outros Workflows

### Exportar para Treinamento

```bash
# Gerar imagens
./generate_batch.sh prompts.txt 10

# Copiar para dataset de treinamento
cp generated_batch/batch_*/prompt_*/image_*.png ../data/synthetic_shoes/
```

### Pipeline de Avaliação

```bash
# 1. Gerar imagens
./generate_batch.sh eval_prompts.txt 5

# 2. Avaliar qualidade (exemplo com script Python)
python evaluate_quality.py generated_batch/batch_TIMESTAMP/

# 3. Gerar relatório
python generate_report.py generated_batch/batch_TIMESTAMP/
```

---

## Dicas e Boas Práticas

### ✅ Fazer

- Usar prompts descritivos e específicos
- Testar com poucos prompts primeiro
- Organizar prompts por categoria em arquivos separados
- Usar nomes descritivos para arquivos de prompts
- Manter backup dos melhores resultados

### ❌ Evitar

- Prompts muito longos (>200 caracteres)
- Caracteres especiais complexos
- Gerar centenas de imagens de uma vez (fazer em lotes menores)
- Usar o mesmo seed para todos (sem variação)

---

## Exemplo Completo

### 1. Criar Arquivo de Prompts

```bash
cat > shoes_catalog.txt <<EOF
casual brown leather loafers, product photography, white background
elegant black oxford dress shoes, studio lighting, side view
comfortable white canvas sneakers, modern minimal design
stylish suede desert boots, tan color, commercial photo
EOF
```

### 2. Gerar Imagens

```bash
./generate_batch.sh shoes_catalog.txt 4
```

### 3. Visualizar Resultados

```bash
open generated_batch/batch_*/index.html
```

### 4. Resultado Esperado

- 4 prompts processados
- 16 imagens geradas (4 prompts × 4 imagens)
- Galeria HTML interativa
- Tempo total: ~3-4 minutos (MPS)

---

## Changelog

### v1.0 (27/10/2025)
- Implementação inicial
- Detecção automática de modelo mais recente
- Geração de galeria HTML
- Suporte a comentários em arquivo de prompts
- Validação de parâmetros
- Tratamento de erros

---

**Autor**: Claude Code
**Data**: 27/10/2025
**Versão**: 1.0
