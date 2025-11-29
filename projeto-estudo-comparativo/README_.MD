# Projeto: Estudo Comparativo entre Inference (Classificação c/ Gemini) vs. Modelo de Classificação

## Dataset

1. [Human Face Emotions](https://www.kaggle.com/datasets/samithsachidanandan/human-face-emotions)

2. Classes:
- Raiva 
- Alegria

## 1. Preparar o Dataset de Validação

-   **Exemplo:**
    -   /sim01
        -   /classe01
        -   /classe02
    -   /sim02
        -   /classe01
        -   /classe02
-   **Fontes sugeridas:**
    -   Kaggle

## 2. Requisitos do Dataset

-   Pelo menos **3000 imagens** da classe 01 e classe 02.

## 3. Experimento e Métricas

### a. Para cada simulação:

-   Extrair **Acurácia**, **Precisão**, **Recall**, **F1-Score**.

### b. Executar **30 simulações**:

-   Plotar um gráfico de boxplot p/ cada métrica acima comparando as
    abordagens.
-   Gráfico de linha comparando **Acc** e **F1-score**.

## 4. Validação

-   **Teste Pareado de Wilcoxon** com **p = 0.05** (grau de confiança).
