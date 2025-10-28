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
- ✅ Dataset splits criados (70/15/15 train/val/test)

#### Insights Principais
1. **Qualidade do Dataset**:
   - ✓ Alta qualidade de imagens (fotografias profissionais)
   - ✓ Fundo limpo/branco (ideal para modelos generativos)
   - ✓ Metadados ricos e bem estruturados
   - ✓ Baixa taxa de valores faltantes (<0.01%)

2. **Distribuições**:
   - Top 10 categorias cobrem 57% do dataset
   - **Casual Shoes: ~2,845 produtos (CATEGORIA MVP ATUAL)**
   - Tshirts: ~7,067 produtos (futuro)
   - Shirts: ~3,217 produtos (futuro)
   - Distribuição equilibrada entre estações
   - 76% dos produtos são de uso casual

3. **Características Técnicas**:
   - Variação de resoluções (não padronizadas)
   - Aspect ratio predominante: ~0.75 (retrato)
   - Descrições em 3 formatos: description, style_note, materials_care_desc
   - Comprimento médio de descrições: 15-50 palavras

### Fase 1.5: Planejamento Otimizado - **CONCLUÍDA** ✅

#### Hardware e Estratégia de Treinamento
- ✅ Hardware identificado: Mac Studio M2 Max (32GB RAM)
- ✅ Modelos selecionados:
  - Stable Diffusion 1.5 + LoRA (imagens)
  - Mistral 7B + QLoRA (texto - futuro)
- ✅ Configurações otimizadas para Apple Silicon
- ✅ Estimativas de tempo e memória documentadas
- ✅ Backlog detalhado criado (BACKLOG.md)

## 🎯 Próximas Etapas - MVP: Casual Shoes

### SPRINT 1: Análise e Preparação (Semana 1) - **PRÓXIMO**
- [ ] Task 1.1: Análise específica de Casual Shoes
- [ ] Task 1.2: Preparação do subset de treinamento
- [ ] Task 1.3: Setup do ambiente (PyTorch MPS, Diffusers)
- [ ] Task 1.4: Download e teste de SD 1.5
- [ ] Task 1.5: Script de treinamento LoRA

### SPRINT 2: Prototipagem (Semana 2)
- [ ] Task 2.1: Treinamento protótipo (300-500 imagens)
- [ ] Task 2.2: Avaliação inicial (CLIP score, visual)
- [ ] Task 2.3: Ajuste de hiperparâmetros

### SPRINT 3: Treinamento Completo (Semana 3)
- [ ] Task 3.1: Treinamento com 2,845 imagens completas
- [ ] Task 3.2: Geração de 3,000-5,000 imagens sintéticas

### SPRINT 4: Validação (Semana 4)
- [ ] Task 4.1: Métricas completas (FID, IS, CLIP)
- [ ] Task 4.2: Análise de falhas e iteração
- [ ] Task 4.3: Documentação final do MVP

**Ver BACKLOG.md para detalhes completos de cada task**

### FUTURO (Postponed)
- [ ] Fine-tuning de Mistral 7B (geração de descrições)
- [ ] Expansão para outras categorias (Tshirts, Shirts)
- [ ] Sistema multimodal integrado
- [ ] Interface web (Gradio)

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
  - Hardware e estratégia (seção 1.4 - M2 Max optimizations)
  - Fases do projeto (5 fases)
  - Recursos necessários
  - Métricas de sucesso
  - Referências e próximos passos

- **Backlog Detalhado**: `planning/BACKLOG.md`
  - MVP: Casual Shoes - Geração de Imagens
  - 4 Sprints (4 semanas)
  - Tasks detalhadas com estimativas
  - Definition of Done
  - Métricas de sucesso
  - Riscos e mitigações

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

## 🎯 MVP: Geração de Imagens Sintéticas - Casual Shoes

### Escopo Atual (Sprint 1-4)
**Categoria**: Casual Shoes (~2,845 imagens)
**Foco**: APENAS geração de imagens sintéticas
**Timeline**: 4 semanas (20-25 dias úteis)

### Objetivos do MVP
- ✅ Treinar Stable Diffusion 1.5 + LoRA em M2 Max
- ✅ Gerar 3,000-5,000 imagens sintéticas de alta qualidade
- ✅ Expandir dataset de Casual Shoes
- ✅ Métricas de qualidade validadas

### Metas Quantitativas
- **FID Score**: < 50 (target: < 40)
- **CLIP Score**: > 0.25 (target: > 0.28)
- **Tempo de geração**: < 6 segundos/imagem
- **Taxa de sucesso**: > 90% de imagens aceitáveis
- **Diversidade**: Distribuição similar ao dataset real

### Tecnologias
- **Hardware**: Mac Studio M2 Max (32GB RAM)
- **Modelo Base**: Stable Diffusion 1.5
- **Método**: LoRA fine-tuning (rank=8-16)
- **Backend**: PyTorch com MPS (Metal Performance Shaders)
- **Frameworks**: Diffusers, Transformers, PEFT

### Categorias Futuras (Postponed)
1. **Tshirts** (~7,067 exemplos) - Sprint 5+
2. **Shirts** (~3,217 exemplos) - Sprint 6+
3. Geração de texto (Mistral 7B) - Sprint 7+

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
**Status**:
- Fase 1 (EDA) - CONCLUÍDA ✅
- Planejamento MVP Casual Shoes - CONCLUÍDO ✅
- Backlog Sprint 1-4 - PRONTO ✅

**Próximo Marco**: SPRINT 1 - Análise e Preparação Casual Shoes (Task 1.1)
**Timeline MVP**: 4 semanas (20-25 dias úteis)