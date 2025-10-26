# Projeto de Geração de Dados Sintéticos - Fashion E-commerce

Este projeto visa desenvolver um sistema completo de geração de dados sintéticos para produtos de moda em e-commerce, incluindo imagens, descrições textuais e metadados estruturados.

## 📁 Estrutura do Projeto

```
shoes-tranning/
├── exploratory/          # Análise Exploratória de Dados (EDA)
│   ├── scripts/         # Scripts Python para análises
│   ├── notebooks/       # Notebooks Jupyter interativos
│   ├── outputs/         # Relatórios e resultados
│   ├── figures/         # Visualizações geradas
│   ├── requirements.txt # Dependências para EDA
│   └── README.md        # Documentação detalhada
├── planning/            # Planejamento e documentação
│   └── planning.md      # Plano de desenvolvimento completo
├── resource.md          # Informações sobre o dataset
└── README.md            # Este arquivo
```

## 📊 Dataset

### Fashion Product Images Dataset
- **Fonte**: Kaggle - Fashion Product Images Dataset
- **Tamanho**: ~30GB, 44,446 produtos únicos
- **Período**: 2010-2017
- **Conteúdo**:
  - 44,441 imagens de produtos (JPG, fundo limpo)
  - 44,446 metadados JSON (ricos e estruturados)
  - CSV com categorias e atributos

### Categorias Principais
1. **Apparel** (70%): Tshirts, Shirts, Jeans, Kurtas, Tops, etc.
2. **Footwear** (19%): Casual Shoes, Sports Shoes, Sandals, Formal Shoes, etc.
3. **Accessories** (9%): Watches, Handbags, Sunglasses, Belts, etc.

## ✅ Status do Projeto

### Fase 1: Exploração e Preparação de Dados - **CONCLUÍDA** ✅

#### Análise Exploratória (EDA)
- ✅ Scripts de análise implementados
  - `data_summary.py`: Análise de dados tabulares (CSV)
  - `image_analysis.py`: Análise de propriedades de imagens
  - `json_metadata_analysis.py`: Análise de metadados JSON
- ✅ Notebook interativo criado (`01_initial_eda.ipynb`)
- ✅ Visualizações geradas (distribuições, heatmaps, histogramas)
- ✅ Relatórios documentados

#### Insights Principais
1. **Qualidade do Dataset**:
   - ✓ Alta qualidade de imagens (fotografias profissionais)
   - ✓ Fundo limpo/branco (ideal para modelos generativos)
   - ✓ Metadados ricos e bem estruturados
   - ✓ Baixa taxa de valores faltantes (<0.01%)

2. **Distribuições**:
   - Top 10 categorias cobrem 57% do dataset
   - Tshirts: ~6,200 produtos (categoria ideal para MVP)
   - Distribuição equilibrada entre estações
   - 76% dos produtos são de uso casual

3. **Características Técnicas**:
   - Variação de resoluções (não padronizadas)
   - Aspect ratio predominante: ~0.75 (retrato)
   - Descrições em 3 formatos: description, style_note, materials_care_desc
   - Comprimento médio de descrições: 15-50 palavras

## 🎯 Próximas Etapas

### Fase 1 (Continuação): Pré-processamento
- [ ] Implementar pipeline de normalização de imagens
- [ ] Limpeza de descrições HTML
- [ ] Criação de embeddings (CLIP, BERT)
- [ ] Split treino/validação/teste

### Fase 2: Desenvolvimento de Modelos
- [ ] Fine-tuning de Stable Diffusion (geração de imagens)
- [ ] Fine-tuning de LLM (geração de descrições)
- [ ] Modelo para geração de metadados
- [ ] Baseline models e métricas

### Fase 3: Sistema Multimodal
- [ ] Pipeline integrado de geração
- [ ] Validação de consistência multimodal
- [ ] Interface de geração (API + UI)

### Fase 4: Avaliação
- [ ] Implementar métricas (FID, CLIP score, etc.)
- [ ] Avaliação humana
- [ ] Refinamento iterativo

### Fase 5: Deployment
- [ ] API de produção
- [ ] Documentação completa
- [ ] Casos de uso

## 🚀 Como Começar

### 1. Explorar o Dataset

```bash
# Navegar para diretório de análise exploratória
cd exploratory

# Instalar dependências
pip install -r requirements.txt

# Executar scripts de análise
cd scripts
python data_summary.py        # Análise de dados tabulares
python image_analysis.py      # Análise de imagens
python json_metadata_analysis.py  # Análise de metadados

# Ou usar o notebook interativo
cd ../notebooks
jupyter notebook 01_initial_eda.ipynb
```

### 2. Revisar o Planejamento

```bash
# Ler o plano de desenvolvimento completo
cat planning/planning.md
```

### 3. Visualizar Resultados

Os resultados da análise exploratória estão disponíveis em:
- **Relatórios**: `exploratory/outputs/`
- **Visualizações**: `exploratory/figures/`

## 📚 Documentação

### Análise Exploratória
- **README**: `exploratory/README.md`
- **Notebook**: `exploratory/notebooks/01_initial_eda.ipynb`
- **Scripts**: `exploratory/scripts/`

### Planejamento
- **Plano Completo**: `planning/planning.md`
  - Visão geral do projeto
  - Análise inicial do dataset (seção 1.3)
  - Fases do projeto (5 fases, 18-20 semanas)
  - Recursos necessários
  - Métricas de sucesso
  - Referências e próximos passos

## 🎓 Objetivos de Aprendizagem

Este projeto foi desenvolvido com fins educacionais e de pesquisa acadêmica, cobrindo:

1. **Análise de Dados**:
   - EDA com Python (pandas, matplotlib, seaborn)
   - Análise de imagens (PIL, OpenCV)
   - Análise de texto e metadados JSON

2. **Deep Learning** (futuro):
   - Modelos Generativos (Stable Diffusion, StyleGAN)
   - Fine-tuning de LLMs
   - Transfer Learning
   - Multimodalidade (CLIP)

3. **MLOps** (futuro):
   - Pipeline de dados
   - Versionamento de modelos
   - Deployment de modelos
   - Monitoramento e avaliação

## 📊 Estatísticas do Dataset

| Métrica | Valor |
|---------|-------|
| **Total de Produtos** | 44,446 |
| **Imagens** | 44,441 |
| **Metadados JSON** | 44,446 |
| **Tamanho Total** | ~30GB |
| **Período** | 2010-2017 |
| **Categorias Principais** | 3 (Apparel, Footwear, Accessories) |
| **Tipos de Artigos** | 140+ |
| **Marcas Únicas** | 2,000+ |
| **Cores Únicas** | 45+ |

## 🎯 MVP Proposto

### Categorias Prioritárias
1. **Tshirts** (~6,200 exemplos) - Fase 1
2. **Shirts** (~5,700 exemplos) - Fase 2
3. **Casual Shoes** (~2,500 exemplos) - Fase 2

### Objetivos do MVP
- Gerar imagens realistas de Tshirts
- Criar descrições coerentes com metadados
- Pipeline end-to-end funcional
- FID < 80 para categoria Tshirts

## 📖 Recursos

### Dataset
- [Fashion Product Images Dataset - Kaggle](https://www.kaggle.com/paramaggarwal/fashion-product-images-dataset)

### Ferramentas e Frameworks
- Python 3.10+
- PyTorch, Diffusers, Transformers (Hugging Face)
- pandas, numpy, matplotlib, seaborn
- PIL, OpenCV
- Jupyter Notebook

### Referências
Ver `planning/planning.md` seção 7 para papers e tutoriais recomendados.

---

**Última Atualização**: 2025-10-26
**Status**: Fase 1 (EDA) Concluída ✅
**Próximo Marco**: Pré-processamento de Dados