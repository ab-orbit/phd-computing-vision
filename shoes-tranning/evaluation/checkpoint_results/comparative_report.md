# Relatorio de Avaliacao Formal de Checkpoints

**Data da Avaliacao**: 2025-10-28 08:31:11
**Dataset Real**: /Users/jwcunha/Documents/COMPANIES/AB/repos/private/premium/researcher/phd-classes/shoes-tranning/data/casual_shoes/train/images
**Checkpoints Avaliados**: 4

## Resumo Comparativo

| Checkpoint | FID Score | CLIP Score | Num. Imagens | Interpretacao |
|------------|-----------|------------|--------------|---------------|
| 500 | 127.63 | N/A | 32 | N/A |
| 1500 | 73.08 | N/A | 32 | N/A |
| 2500 | 74.06 | N/A | 32 | N/A |
| 3000 | 91.98 | N/A | 32 | N/A |

## Analise Detalhada

### Melhor FID Score
**Checkpoint 1500**: FID = 73.08

O FID (Frechet Inception Distance) mede a qualidade e diversidade das imagens.
Valores menores indicam maior similaridade com o dataset real.

## Recomendacao para Producao


## Metodologia

### FID (Frechet Inception Distance)
- Extrai features usando Inception v3 pre-treinado
- Calcula distancia de Frechet entre distribuicoes
- Interpretacao: < 10 = Excelente, < 20 = Muito Bom, < 50 = Bom

### CLIP Score
- Usa modelo CLIP (OpenAI) para embeddings multimodais
- Calcula similaridade coseno entre texto e imagem
- Interpretacao: > 30 = Excelente, > 27 = Muito Bom, > 25 = Bom
