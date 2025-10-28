# Metodologia Formal de Avaliacao de Checkpoints LoRA

Este documento descreve a metodologia cientifica para avaliacao formal da qualidade dos checkpoints do modelo LoRA treinado para geracao de imagens de sapatos casuais.

## Indice

1. [Introducao](#introducao)
2. [Fundamentacao Teorica](#fundamentacao-teorica)
3. [Metodologia Proposta](#metodologia-proposta)
4. [Protocolo de Avaliacao](#protocolo-de-avaliacao)
5. [Interpretacao de Resultados](#interpretacao-de-resultados)
6. [Criterios de Selecao](#criterios-de-selecao)
7. [Limitacoes](#limitacoes)

## Introducao

### Problema

Durante o treinamento do modelo LoRA, multiplos checkpoints foram salvos em intervalos regulares (500, 1000, 1500, 2000, 2500, 3000 steps). A questao central e:

**"Qual checkpoint produz imagens de maior qualidade e melhor alinhamento com os prompts?"**

### Desafio

A avaliacao visual manual apresenta limitacoes:
- Subjetividade do avaliador
- Falta de reproducibilidade
- Dificuldade em escala
- Ausencia de metricas quantitativas

### Solucao

Implementar metodologia formal baseada em metricas quantitativas validadas pela literatura cientifica:
- **FID (Frechet Inception Distance)**: Qualidade e diversidade
- **CLIP Score**: Alinhamento semantico texto-imagem

## Fundamentacao Teorica

### FID (Frechet Inception Distance)

**Referencia**: Heusel et al. (2017) - "GANs Trained by a Two Time-Scale Update Rule Converge to a Local Nash Equilibrium"

**Definicao**:
O FID mede a distancia entre a distribuicao de features de imagens reais e geradas, extraidas usando o modelo Inception v3 pre-treinado em ImageNet.

**Formula**:

```
FID = ||μ_r - μ_g||² + Tr(Σ_r + Σ_g - 2√(Σ_r · Σ_g))
```

Onde:
- μ_r, μ_g: medias das features reais e geradas
- Σ_r, Σ_g: matrizes de covariancia
- Tr: traco da matriz

**Interpretacao**:
- FID = 0: Distribuicoes identicas (ideal teorico)
- FID < 10: Qualidade excelente (nivel state-of-the-art)
- FID < 20: Qualidade muito boa (producao)
- FID < 50: Qualidade boa (aceitavel)
- FID >= 100: Qualidade ruim (requer retreinamento)

**Vantagens**:
- Padrao ouro para avaliacao de modelos generativos
- Considera qualidade e diversidade simultaneamente
- Correlacao forte com avaliacao humana
- Amplamente usado em literatura (GANs, Diffusion Models)

**Limitacoes**:
- Requer numero significativo de amostras (minimo 50, ideal >1000)
- Sensivel a variacoes no dataset
- Nao captura aspectos semanticos especificos

### CLIP Score

**Referencia**: Radford et al. (2021) - "Learning Transferable Visual Models From Natural Language Supervision"

**Definicao**:
CLIP Score mede o alinhamento entre representacoes visuais e textuais usando o modelo CLIP, treinado em 400M pares imagem-texto.

**Formula**:

```
CLIP_Score = (E_img · E_text) / (||E_img|| × ||E_text||) × 100
```

Onde:
- E_img: embedding da imagem (512-dim)
- E_text: embedding do prompt (512-dim)
- ·: produto escalar
- || ||: norma L2

**Interpretacao**:
- CLIP > 30: Alinhamento excelente
- CLIP > 27: Alinhamento muito bom
- CLIP > 25: Alinhamento bom
- CLIP > 20: Alinhamento razoavel
- CLIP <= 20: Alinhamento ruim

**Vantagens**:
- Avalia alinhamento semantico especifico ao prompt
- Funciona com poucas amostras
- Multimodal (entende texto e imagem)
- Robusto a variacoes visuais

**Limitacoes**:
- Nao mede qualidade visual absoluta
- Pode dar scores altos para imagens de baixa resolucao se semanticamente corretas
- Dependente da qualidade do prompt

## Metodologia Proposta

### Abordagem Multi-Metrica

Nossa metodologia combina FID e CLIP Score para avaliacao holistica:

| Metrica | Aspecto Avaliado | Peso na Decisao |
|---------|------------------|-----------------|
| FID | Qualidade visual, diversidade, realismo | 60% |
| CLIP Score | Alinhamento semantico, fidelidade ao prompt | 40% |

**Justificativa dos Pesos**:
- FID tem peso maior pois qualidade visual e critica para producao
- CLIP Score garante que a qualidade esteja alinhada com os requisitos (prompts)
- Em caso de empate, FID desempata

### Pipeline de Avaliacao

```
┌─────────────────────────────────────────────────────────────┐
│ 1. PREPARACAO                                               │
│    - Verificar disponibilidade de checkpoints              │
│    - Validar numero de imagens por checkpoint              │
│    - Preparar arquivo de prompts                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. EXTRACAO DE FEATURES (FID)                               │
│    - Carregar modelo Inception v3                          │
│    - Extrair features das imagens reais (dataset)          │
│    - Extrair features das imagens geradas (checkpoint)     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. CALCULO DE FID                                           │
│    - Calcular media e covariancia das features             │
│    - Aplicar formula de Frechet Distance                   │
│    - Registrar score                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. CALCULO DE CLIP SCORE                                    │
│    - Carregar modelo CLIP                                  │
│    - Codificar imagens e prompts                           │
│    - Calcular similaridade coseno                          │
│    - Registrar media, std, min, max                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. ANALISE COMPARATIVA                                      │
│    - Comparar todos os checkpoints                         │
│    - Identificar melhor FID                                │
│    - Identificar melhor CLIP Score                         │
│    - Aplicar criterios de selecao                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. RECOMENDACAO                                             │
│    - Selecionar checkpoint para producao                   │
│    - Gerar relatorio tecnico                               │
│    - Documentar justificativa                              │
└─────────────────────────────────────────────────────────────┘
```

## Protocolo de Avaliacao

### Passo 1: Preparacao do Ambiente

```bash
# Navegar para diretorio de avaliacao
cd shoes-tranning/evaluation

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalacao
python -c "import torch; import clip; print('OK')"
```

### Passo 2: Verificacao de Dados

**Requisitos**:
- Dataset real: minimo 100 imagens (ideal: todo o conjunto de treino)
- Imagens geradas: minimo 10 por checkpoint (ideal: 50+)
- Prompts: arquivo JSON mapeando imagens para prompts

**Verificacao**:
```bash
# Verificar imagens reais
ls -1 ../data/casual_shoes/train/images/*.png | wc -l

# Verificar imagens geradas por checkpoint
for ckpt in 500 1000 1500 2000 2500 3000; do
    count=$(ls -1 ../training/outputs/lora_casual_shoes_3000steps_full/validation/checkpoint-$ckpt/*.png 2>/dev/null | wc -l)
    echo "Checkpoint $ckpt: $count imagens"
done
```

### Passo 3: Execucao da Avaliacao Automatizada

**Comando Principal**:
```bash
python evaluate_all_checkpoints.py \
    --real_images_dir ../data/casual_shoes/train/images \
    --validation_base_dir ../training/outputs/lora_casual_shoes_3000steps_full/validation \
    --output_dir ./checkpoint_evaluation_results
```

**Opcoes de Configuracao**:

```bash
# Avaliar apenas checkpoints especificos
python evaluate_all_checkpoints.py \
    --real_images_dir ../data/casual_shoes/train/images \
    --validation_base_dir ../training/outputs/lora_casual_shoes_3000steps_full/validation \
    --checkpoints 1500 2000 2500 3000

# Calcular apenas FID (mais rapido)
python evaluate_all_checkpoints.py \
    --real_images_dir ../data/casual_shoes/train/images \
    --validation_base_dir ../training/outputs/lora_casual_shoes_3000steps_full/validation \
    --skip_clip

# Calcular apenas CLIP Score
python evaluate_all_checkpoints.py \
    --real_images_dir ../data/casual_shoes/train/images \
    --validation_base_dir ../training/outputs/lora_casual_shoes_3000steps_full/validation \
    --skip_fid
```

### Passo 4: Analise dos Resultados

**Arquivos Gerados**:

```
checkpoint_evaluation_results/
├── consolidated_results.json          # Todos os resultados em JSON
├── comparative_report.md              # Relatorio comparativo
├── metrics_checkpoint_500.json        # Metricas checkpoint 500
├── metrics_checkpoint_1000.json       # Metricas checkpoint 1000
├── metrics_checkpoint_1500.json       # Metricas checkpoint 1500
├── metrics_checkpoint_2000.json       # Metricas checkpoint 2000
├── metrics_checkpoint_2500.json       # Metricas checkpoint 2500
├── metrics_checkpoint_3000.json       # Metricas checkpoint 3000
├── prompts_checkpoint_500.json        # Prompts checkpoint 500
├── prompts_checkpoint_1000.json       # ...
└── ...
```

**Analise do Relatorio**:

```bash
# Visualizar relatorio comparativo
cat checkpoint_evaluation_results/comparative_report.md

# Extrair apenas a tabela de resultados
cat checkpoint_evaluation_results/comparative_report.md | grep -A 10 "Resumo Comparativo"
```

## Interpretacao de Resultados

### Matriz de Decisao

| FID Score | CLIP Score | Interpretacao | Acao Recomendada |
|-----------|------------|---------------|------------------|
| < 20 | > 27 | Excelente em ambas metricas | **Usar em producao** |
| < 50 | > 25 | Bom equilibrio | **Validar com equipe, considerar producao** |
| < 20 | < 25 | Alta qualidade, baixo alinhamento | Revisar prompts ou continuar treinamento |
| > 50 | > 27 | Baixa qualidade, bom alinhamento | Aumentar steps de treinamento |
| > 50 | < 25 | Ruim em ambas metricas | **Retreinar modelo** |

### Analise de Tendencias

**Exemplo de Analise**:

```
Checkpoint 500:  FID=85.3, CLIP=22.1  -> Inicio do treinamento
Checkpoint 1000: FID=62.7, CLIP=24.8  -> Melhorando
Checkpoint 1500: FID=35.2, CLIP=27.3  -> Boa performance
Checkpoint 2000: FID=28.1, CLIP=28.9  -> Melhor FID e CLIP
Checkpoint 2500: FID=29.5, CLIP=28.7  -> Plateau
Checkpoint 3000: FID=31.2, CLIP=27.8  -> Possivel overfit
```

**Interpretacao**:
- Checkpoint 2000 apresenta melhor equilibrio
- Apos 2000 steps, ha estagnacao ou leve degradacao
- Recomendacao: Usar checkpoint 2000

### Significancia Estatistica

Para determinar se diferencas entre checkpoints sao significativas:

**Regra Pratica para FID**:
- Diferenca < 5: Nao significativa
- Diferenca 5-15: Moderadamente significativa
- Diferenca > 15: Altamente significativa

**Regra Pratica para CLIP Score**:
- Diferenca < 2: Nao significativa
- Diferenca 2-5: Moderadamente significativa
- Diferenca > 5: Altamente significativa

## Criterios de Selecao

### Criterio Primario: Qualidade Geral

```python
def select_best_checkpoint(results):
    """
    Seleciona melhor checkpoint baseado em criterios ponderados.

    Criterios:
    1. FID < 50 (obrigatorio)
    2. CLIP > 25 (obrigatorio)
    3. Minimizar FID (60% peso)
    4. Maximizar CLIP (40% peso)
    """

    # Filtra checkpoints que atendem criterios minimos
    candidates = {
        ckpt: data for ckpt, data in results.items()
        if data['fid']['score'] < 50 and data['clip_score']['mean'] > 25
    }

    if not candidates:
        return None  # Nenhum checkpoint atende criterios

    # Calcula score ponderado (normalizado)
    scores = {}
    for ckpt, data in candidates.items():
        # Normaliza FID (menor e melhor, inverte para 0-1)
        fid_normalized = 1 - (data['fid']['score'] / 100)

        # Normaliza CLIP (maior e melhor, escala 0-1)
        clip_normalized = data['clip_score']['mean'] / 35

        # Score ponderado
        weighted_score = (fid_normalized * 0.6) + (clip_normalized * 0.4)
        scores[ckpt] = weighted_score

    # Retorna checkpoint com maior score
    return max(scores, key=scores.get)
```

### Criterios Secundarios

1. **Eficiencia Computacional**:
   - Se dois checkpoints tem scores similares, preferir o anterior (menos steps)

2. **Consistencia (Desvio Padrao do CLIP)**:
   - Preferir checkpoint com menor std no CLIP Score

3. **Numero de Amostras**:
   - Maior numero de imagens geradas = mais confiavel

## Limitacoes

### Limitacoes Metodologicas

1. **Tamanho do Dataset de Validacao**:
   - Ideal: 1000+ imagens por checkpoint
   - Minimo aceitavel: 50 imagens
   - Menos que 50: resultados podem ser instáveis

2. **Dependencia de Prompts**:
   - CLIP Score depende da qualidade dos prompts
   - Prompts vagos podem resultar em scores artificialmente altos ou baixos

3. **Ausencia de Avaliacao Humana**:
   - Metricas automaticas sao proxies para qualidade percebida
   - Avaliacao humana (user study) seria complementar

### Limitacoes Tecnicas

1. **Hardware**:
   - Avaliacao completa pode levar 30-60 minutos em CPU
   - GPU/MPS reduz tempo significativamente

2. **Memoria**:
   - Modelos Inception v3 + CLIP requerem ~4GB RAM
   - Processar datasets grandes pode causar out-of-memory

3. **Reproducibilidade**:
   - Pequenas variacoes podem ocorrer entre execucoes
   - Fixar seed nao e suficiente (variacoes numericas)

## Boas Praticas

1. **Executar Multiplas Vezes**:
   - Rodar avaliacao 2-3 vezes para verificar consistencia

2. **Documentar Contexto**:
   - Registrar hardware usado
   - Registrar versoes de bibliotecas
   - Salvar configuracoes de treinamento

3. **Validacao Cruzada**:
   - Se possivel, usar multiple conjuntos de validacao
   - Comparar resultados entre diferentes seeds de geracao

4. **Complementar com Avaliacao Visual**:
   - Metricas guiam, mas nao substituem inspecao visual
   - Revisar imagens do checkpoint selecionado

## Conclusao

Esta metodologia fornece framework rigoroso e reproducivel para selecao de checkpoints baseado em metricas quantitativas validadas pela literatura. A combinacao de FID e CLIP Score permite avaliacao holistica considerando qualidade visual e alinhamento semantico.

**Proximos Passos**:
1. Executar avaliacao usando `evaluate_all_checkpoints.py`
2. Analisar relatorio comparativo
3. Selecionar checkpoint para producao
4. Validar com amostra de usuarios (opcional)
5. Deploy do modelo selecionado

## Referencias

1. Heusel, M., Ramsauer, H., Unterthiner, T., Nessler, B., & Hochreiter, S. (2017). GANs trained by a two time-scale update rule converge to a local nash equilibrium. NeurIPS.

2. Radford, A., Kim, J. W., Hallacy, C., Ramesh, A., Goh, G., Agarwal, S., ... & Sutskever, I. (2021). Learning transferable visual models from natural language supervision. ICML.

3. Parmar, G., Zhang, R., & Zhu, J. Y. (2021). On Aliased Resizing and Surprising Subtleties in GAN Evaluation. CVPR 2022.

4. Hessel, J., Holtzman, A., Forbes, M., Bras, R. L., & Choi, Y. (2021). CLIPScore: A Reference-free Evaluation Metric for Image Captioning. EMNLP 2021.
