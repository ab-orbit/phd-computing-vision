# Informações sobre .gitignore

## Estrutura do Controle de Versão

Este documento explica o que está sendo rastreado e o que está sendo ignorado pelo Git neste projeto.

---

## Arquivos e Diretórios IGNORADOS

### Python e Ambientes Virtuais
```
__pycache__/              # Cache de bytecode Python
*.pyc, *.pyo, *.pyd      # Arquivos compilados
venv/, env/, .venv/      # Ambientes virtuais
*.egg-info/              # Metadados de pacotes
```

### IDEs e Editores
```
.idea/                   # PyCharm
.vscode/                 # Visual Studio Code
*.swp, *.swo            # Vim
.DS_Store               # macOS Finder
```

### Jupyter Notebooks
```
.ipynb_checkpoints/      # Checkpoints automáticos
```

### Dados e Modelos (Arquivos Grandes)
```
rvlp/data/train/         # Dataset de treino (320k imagens)
rvlp/data/validation/    # Dataset de validação (40k imagens)
*.h5, *.hdf5            # Modelos Keras/TensorFlow
*.pt, *.pth             # Modelos PyTorch
*.onnx                  # Modelos ONNX
```

### Outputs e Resultados Temporários
```
pdi/output/*.png         # Imagens geradas pelo processamento
pdi/output/*.jpg         # (exceto .gitkeep)
output/                  # Diretórios de output gerais
results/                 # Resultados de experimentos
cache/                   # Cache de processamento
*.npy, *.npz            # Arrays NumPy salvos
*.pkl, *.pickle         # Objetos Python serializados
```

### Arquivos de Sistema
```
.DS_Store               # macOS
Thumbs.db               # Windows
*~                      # Backups temporários Linux
*.log                   # Logs
```

### Arquivos Compactados
```
*.zip, *.tar.gz         # Datasets compactados
*.rar, *.7z            # (devem ser baixados separadamente)
```

---

## Arquivos e Diretórios RASTREADOS

### Código Fonte
```
pdi/
├── __init__.py                    # Módulo Python
├── noise_reduction.py             # Implementação principal
├── interactive_demo.py            # Demo interativa
├── examples.py                    # Exemplos práticos
├── NOISE_REDUCTION_GUIDE.md      # Documentação educacional
├── README.md                      # Documentação
└── output/.gitkeep               # Mantém estrutura do diretório

rvlp/
├── __init__.py
├── simple_classifier.py           # Classificador determinístico
├── simple_classifier_cli.py       # Versão CLI
├── test_classifier.py             # Testes
├── analyze_categories.py          # Análise de categorias
├── run_classifier.sh              # Script de execução
├── examples.sh                    # Exemplos
└── CLASSIFIER_README.md          # Documentação

images/
└── fotografo_gonzales.png        # Imagem de exemplo (pequena)
```

### Documentação
```
README.MD                  # README principal
overview.md               # Visão geral do projeto
CLAUDE.md                 # Documentação do Claude Code
GITIGNORE_INFO.md         # Este arquivo
```

### Notebooks
```
rvlp/rvlp-cdip.ipynb     # Notebook principal do projeto
```

---

## Estrutura de Dados (Não Rastreada)

### Como Obter os Dados

Os datasets grandes não estão incluídos no repositório. Para obtê-los:

#### RVL-CDIP Dataset
```bash
# Usando kagglehub (método do notebook)
import kagglehub
path = kagglehub.dataset_download("pdavpoojan/the-rvlcdip-dataset-test")

# Ou manualmente do Kaggle:
# https://www.kaggle.com/datasets/pdavpoojan/the-rvlcdip-dataset-test
```

### Estrutura Esperada de Dados
```
rvlp/data/
├── test/                          # 40,000 imagens
│   ├── advertisement/             # ~2,500 imagens cada
│   ├── budget/
│   ├── email/
│   ├── file_folder/
│   ├── form/
│   ├── handwritten/
│   ├── invoice/
│   ├── letter/
│   ├── memo/
│   ├── news_article/
│   ├── presentation/
│   ├── questionnaire/
│   ├── resume/
│   ├── scientific_publication/
│   ├── scientific_report/
│   └── specification/
├── train/                         # 320,000 imagens (não incluído)
└── validation/                    # 40,000 imagens (não incluído)
```

---

## Outputs Gerados (Não Rastreados)

### PDI - Redução de Ruído
Ao executar `pdi/noise_reduction.py`, são gerados:
```
pdi/output/
├── comparison_best_filters.png    # Comparação visual
├── all_filters.png                # Todos os filtros
├── median_5x5.png                 # Resultado individual
├── bilateral_d9.png               # Resultado individual
├── nlm_h10.png                    # Resultado individual
└── combined.png                   # Resultado combinado
```

Estes arquivos podem ser regenerados executando o script.

### RVLP - Classificador
Possíveis outputs (dependendo do uso):
```
confusion_matrix.png               # Matriz de confusão
*.h5                              # Modelos treinados
logs/                             # Logs de treinamento
```

---

## Boas Práticas

### Adicionando Novos Arquivos

**RASTREAR (adicionar ao Git):**
- Código fonte (.py)
- Notebooks (.ipynb)
- Documentação (.md)
- Scripts (.sh)
- Imagens pequenas de exemplo (< 1MB)
- Arquivos de configuração

**NÃO RASTREAR (já no .gitignore):**
- Datasets grandes (> 10MB)
- Modelos treinados (.h5, .pt, etc)
- Outputs gerados (podem ser reproduzidos)
- Ambientes virtuais
- Caches e arquivos temporários
- Credenciais (kaggle.json, .env)

### Verificando o que Será Commitado

```bash
# Ver status
git status

# Ver diferenças
git diff

# Ver arquivos staged
git diff --cached

# Ver o que está sendo ignorado
git status --ignored
```

### Se Precisar Rastrear Arquivo Ignorado

```bash
# Adicionar arquivo específico mesmo estando no .gitignore
git add -f arquivo_especifico.png

# Ou criar exceção no .gitignore
echo "!arquivo_especifico.png" >> .gitignore
```

---

## Tamanho do Repositório

### Estimativa de Tamanhos

**Rastreado pelo Git:**
- Código Python: ~100 KB
- Documentação: ~60 KB
- Scripts: ~20 KB
- Imagens de exemplo: ~20 KB
- **Total: < 500 KB**

**Ignorado (local):**
- Dataset RVL-CDIP test: ~3.6 GB
- Outputs PDI: ~5 MB
- Ambiente virtual: ~100-500 MB
- **Total: ~4+ GB**

### Por Que Esta Abordagem

**Vantagens:**
1. Repositório leve e rápido para clonar
2. Cada desenvolvedor baixa apenas dados necessários
3. Evita problemas com limite de tamanho do GitHub (100MB por arquivo)
4. Facilita colaboração (não precisa versionar dados)
5. Separação clara: código vs dados

**Datasets Grandes:**
- Mantidos em plataformas especializadas (Kaggle, Zenodo)
- Documentamos como obtê-los (README, notebooks)
- Scripts podem baixá-los automaticamente

---

## Troubleshooting

### Arquivo Sendo Rastreado Mas Deveria Estar Ignorado

Se um arquivo já foi commitado antes de adicionar ao .gitignore:

```bash
# Remove do índice mas mantém localmente
git rm --cached arquivo.txt

# Para diretório
git rm -r --cached diretorio/

# Commit a remoção
git commit -m "Remove arquivo do versionamento"
```

### Ver Quais Arquivos Estão Ignorados

```bash
git status --ignored
```

### Testar .gitignore

```bash
# Verifica se um arquivo específico seria ignorado
git check-ignore -v arquivo.txt
```

---

## Manutenção

### Atualizar .gitignore

Se precisar adicionar novos padrões:

1. Editar `.gitignore`
2. Adicionar padrões novos
3. Commitar as mudanças
4. Aplicar retroativamente se necessário:
   ```bash
   git rm -r --cached .
   git add .
   git commit -m "Atualiza .gitignore"
   ```

---

## Referências

- [Git Documentation - gitignore](https://git-scm.com/docs/gitignore)
- [GitHub gitignore templates](https://github.com/github/gitignore)
- [gitignore.io](https://www.toptal.com/developers/gitignore) - Gerador de .gitignore

---

Última atualização: Outubro 2024