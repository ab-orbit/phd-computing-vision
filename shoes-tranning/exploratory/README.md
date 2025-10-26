# Análise Exploratória - Fashion Product Images Dataset

Este diretório contém scripts e notebooks para análise exploratória de dados (EDA) do Fashion Product Images Dataset.

## Estrutura

```
exploratory/
├── scripts/              # Scripts Python para análises específicas
│   ├── config.py        # Configurações e caminhos
│   ├── data_summary.py  # Análise de dados tabulares (CSV)
│   ├── image_analysis.py # Análise de imagens
│   └── json_metadata_analysis.py # Análise de metadados JSON
├── notebooks/            # Notebooks Jupyter para EDA interativa
├── outputs/              # Relatórios e dados processados
└── figures/              # Visualizações geradas
```

## Dataset

### Localização
- **Base**: `/Users/jwcunha/.cache/kagglehub/datasets/paramaggarwal/fashion-product-images-dataset/versions/1/fashion-dataset/fashion-dataset/`
- **Imagens**: `images/` (~44,441 arquivos .jpg)
- **Metadados JSON**: `styles/` (~44,446 arquivos .json)
- **CSV Principal**: `styles.csv` (44,446 registros)
- **CSV de Imagens**: `images.csv`
- **Tamanho Total**: ~30GB

### Estrutura dos Dados

#### styles.csv
Contém metadados básicos de cada produto:
- `id`: Identificador único do produto
- `gender`: Gênero (Men, Women, Boys, Girls, Unisex)
- `masterCategory`: Categoria principal (Apparel, Footwear, Accessories, etc.)
- `subCategory`: Subcategoria (Topwear, Bottomwear, Shoes, etc.)
- `articleType`: Tipo específico (Shirts, Jeans, Watches, etc.)
- `baseColour`: Cor base do produto
- `season`: Estação (Summer, Winter, Fall, Spring)
- `year`: Ano (2010-2017)
- `usage`: Uso (Casual, Formal, Sports, Ethnic)
- `productDisplayName`: Nome de exibição do produto

#### JSON Metadata (styles/[ID].json)
Metadados ricos incluindo:
- Informações de preço (`price`, `discountedPrice`)
- Marca (`brandName`, `brandUserProfile`)
- Descrições detalhadas (`productDescriptors`)
  - `description`: Descrição do produto
  - `style_note`: Notas de estilo
  - `materials_care_desc`: Materiais e cuidados
- Atributos (`articleAttributes`): Fit, Fabric, Occasion, etc.
- URLs de imagens em múltiplas resoluções
- Informações de categoria detalhadas
- Opções de tamanho

#### Imagens
- Formato: JPG
- Produtos em fundo branco/limpo
- Fotografias profissionais de alta qualidade
- Variação nas resoluções

## Instalação

```bash
# Criar ambiente virtual (opcional)
python -m venv venv
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

## ⚠️ Problema Conhecido: ParserError no CSV

Se você encontrar um erro ao carregar o CSV (`ParserError: Error tokenizing data`), isso é esperado.

**Causa**: 22 linhas do CSV (0.05%) têm vírgulas extras em nomes de produtos.

**Solução**: O notebook já foi atualizado com tratamento de erros usando `on_bad_lines='skip'`.

Para mais detalhes, consulte: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Status**: ✅ Resolvido automaticamente no notebook

## Uso

### Scripts de Análise

#### 1. Análise de Dados Tabulares
```bash
cd scripts
python data_summary.py
```

**Outputs**:
- `outputs/data_summary_report.txt`: Relatório textual
- `figures/category_distributions.png`: Distribuições de categorias
- `figures/top_article_types.png`: Top tipos de artigos
- `figures/top_colors.png`: Cores mais frequentes
- `figures/category_gender_heatmap.png`: Heatmap categoria vs gênero

**Análises incluídas**:
- Estatísticas básicas (total, duplicatas, valores faltantes)
- Distribuições de categorias
- Análise temporal
- Verificação de integridade

#### 2. Análise de Imagens
```bash
python image_analysis.py
```

**Outputs**:
- `outputs/image_analysis_report.txt`: Relatório de imagens
- `outputs/image_analysis_stats.json`: Estatísticas em JSON
- `figures/image_dimensions.png`: Distribuições de dimensões
- `figures/width_vs_height.png`: Scatter plot largura vs altura
- `figures/top_resolutions.png`: Resoluções mais comuns
- `figures/brightness_distribution.png`: Distribuição de brilho
- `figures/rgb_channels.png`: Distribuição de canais RGB

**Análises incluídas**:
- Dimensões (largura, altura, aspect ratio)
- Tamanhos de arquivo
- Resoluções comuns
- Análise de cores (RGB, brilho)
- Modos de cor

#### 3. Análise de Metadados JSON
```bash
python json_metadata_analysis.py
```

**Outputs**:
- `outputs/metadata_analysis_report.txt`: Relatório de metadados
- `figures/description_lengths.png`: Comprimento de descrições
- `figures/price_distribution.png`: Distribuição de preços

**Análises incluídas**:
- Estrutura e completude de campos
- Análise de descrições (comprimento, conteúdo)
- Distribuição de preços e descontos
- Atributos de produtos
- Análise de marcas

### Configurações

Edite `scripts/config.py` para ajustar:
- `SAMPLE_SIZE`: Número de registros para análise rápida (None = todos)
- `RANDOM_SEED`: Seed para reprodutibilidade
- Estilos de visualização

## Notebooks Jupyter

```bash
cd notebooks
jupyter notebook
```

Os notebooks fornecem análise interativa e exploração detalhada.

## Próximos Passos

1. **Análise de Texto Avançada**:
   - NLP nas descrições de produtos
   - Extração de entidades
   - Análise de sentimento

2. **Análise de Imagens Avançada**:
   - Extração de features com CNNs
   - Embeddings visuais (CLIP)
   - Detecção de similaridade

3. **Análise Multimodal**:
   - Correlação entre imagem e texto
   - Consistência de atributos

4. **Preparação para Modelagem**:
   - Criação de datasets de treino/validação/teste
   - Identificação de categorias para geração sintética

## Insights Iniciais

### Dataset Overview
- **Tamanho**: ~44,446 produtos únicos
- **Período**: 2010-2017
- **Completude**: Alta (poucos valores faltantes)
- **Diversidade**:
  - Múltiplos gêneros, categorias, e tipos de artigos
  - Ampla gama de cores e estilos
  - Produtos de diferentes estações e usos

### Características Principais
- **Categorias balanceadas**: Boa distribuição entre Apparel, Footwear, e Accessories
- **Gênero**: Predominância de produtos masculinos e femininos
- **Qualidade**: Imagens profissionais com fundo limpo
- **Metadados ricos**: Descrições detalhadas, atributos, e informações de marca

### Desafios Identificados
- Algumas imagens faltantes (~5)
- Variação em resoluções de imagem
- Descrições em HTML (necessitam limpeza)
- Diferentes níveis de completude em atributos opcionais

---

**Última Atualização**: 2025-10-26