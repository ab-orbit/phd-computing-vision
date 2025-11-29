# Sumário de Resultados - Classificador Roboflow

## Status da Implementação

Implementação completa e funcional. A API key está configurada no arquivo `.env` na raiz do projeto.

## Teste Inicial - Simulação 01

### Configuração
- **Modelo**: computer-vision-projects-zhogq/emotion-detection-y0svj
- **Versão**: 1
- **Classes detectadas pelo modelo**: Angry, Happy, Sad, Neutral, Fearful
- **Threshold de confiança**: 0.4 (40%)

### Resultados da Simulação 01

```
Acurácia Alegria: 0.56 (28/50 acertos)
Acurácia Raiva: 0.14 (7/50 acertos)
Acurácia Geral: 0.35 (35/100 acertos)
Tempo de Processamento: ~64 segundos (~0.64s por imagem)
```

### Análise dos Resultados

1. **Boa performance em Alegria** (56%)
   - Modelo detecta bem faces felizes
   - Confiança alta (0.69-0.90) nas predições

2. **Baixa performance em Raiva** (14%)
   - Modelo tem dificuldade em detectar raiva
   - Confiança baixa (0.41-0.48) nas predições
   - Muitas imagens de raiva não recebem predição ou são classificadas como Sad/Neutral

3. **Possíveis Causas**
   - Dataset de treinamento do modelo pode ter poucas imagens de raiva
   - Imagens do nosso dataset podem ter características diferentes
   - Raiva vs Sad/Neutral são emoções próximas visualmente

## Debug das Predições

Executando `debug_roboflow_predictions.py`, observamos:

### Imagens de Raiva
```
7093.png      -> Angry: 0.48    (acertou, mas baixa confiança)
4438.png      -> Sad: 0.47      (errou - confundiu com tristeza)
39959586.png  -> (sem predição)  (errou - sem detecção)
5134.png      -> (sem predição)  (errou - sem detecção)
188.png       -> Neutral: 0.41   (errou - classificou como neutro)
```

### Imagens de Alegria
```
971899438.png -> Happy: 0.69 (acertou)
20418.png     -> Happy: 0.70 (acertou)
689650428.png -> Happy: 0.85 (acertou)
9269.png      -> Happy: 0.80 (acertou)
756501369.png -> Happy: 0.90 (acertou)
```

## Como Executar Todas as Simulações

### Opção 1: Executar com o script pronto

```bash
# Processar todas as 30 simulações
python run_roboflow_classification.py --num_simulations 30

# Tempo estimado: ~30-40 minutos
# Requisições: 3000 (30 simulações × 100 imagens)
```

### Opção 2: Executar diretamente

```bash
# API key já está no .env, então basta:
python RoboflowEmotionClassifier.py \
    --api_key $(grep ROBOFLOW_API_KEY ../../.env | cut -d '=' -f2) \
    --num_simulations 30
```

### Opção 3: Processar em lotes

```bash
# Processar simulações 1-10
python run_roboflow_classification.py --num_simulations 10

# Depois processar 11-20, 21-30, etc.
```

## Resultados Esperados

Baseado no teste inicial, esperamos:

- **Acurácia Geral**: ~30-40%
- **Acurácia Alegria**: ~50-60%
- **Acurácia Raiva**: ~10-20%
- **Tempo Total**: ~30-40 minutos para 30 simulações
- **Requisições**: 3000 (pode consumir limite de API)

## Comparação com CNN

Após executar, compare com CNN:

| Métrica | Roboflow (esperado) | CNN (a executar) |
|---------|---------------------|------------------|
| Acurácia Geral | ~35% | ? |
| Acurácia Alegria | ~55% | ? |
| Acurácia Raiva | ~15% | ? |
| Tempo de Desenvolvimento | 0 (modelo pronto) | Horas (treino) |
| Tempo de Inferência | ~0.6s/imagem | ~0.01s/imagem |
| Custo | API ($) | GPU ($) |

## Observações Importantes

### 1. Performance Limitada

O modelo Roboflow usado não foi treinado especificamente para este dataset,
resultando em performance subótima. Isso é esperado em modelos foundation
de propósito geral.

### 2. Trade-offs

- **Vantagem**: Zero treinamento, rápido para prototipar
- **Desvantagem**: Baixa acurácia, custo por requisição, latência de rede

### 3. Melhorias Possíveis

1. **Testar outros modelos do Roboflow Universe**
   ```bash
   python run_roboflow_classification.py \
       --model_id uni-o612z/facial-emotion-recognition \
       --model_name roboflow_v2
   ```

2. **Ajustar threshold de confiança**
   - Editar `RoboflowEmotionClassifier.py` linha 298
   - Tentar valores: 0.3, 0.35, 0.45, 0.5

3. **Ensemble de modelos**
   - Usar múltiplos modelos e combinar predições

4. **Fine-tuning**
   - Upload do dataset para Roboflow
   - Fine-tune do modelo (requer plano pago)

## Estrutura de Arquivos de Saída

Após executar, os seguintes arquivos serão gerados:

```
3_simulation/results/
├── roboflow_emotion.csv           # Resultados principais
├── roboflow_emotion_stats.json    # Estatísticas agregadas
└── roboflow_emotion_partial.csv   # Backup incremental
```

### Formato do CSV

```csv
numero_simulacao,nome_modelo,qtd_sucesso_alegria,qtd_sucesso_raiva,total_alegria,total_raiva,acuracia_alegria,acuracia_raiva,acuracia_geral,tempo_total_ms
1,roboflow_emotion,28,7,50,50,0.56,0.14,0.35,64473.34
2,roboflow_emotion,...
```

## Próximos Passos

1. ✅ Implementação completa
2. ✅ Teste inicial (sim01) executado
3. ⏳ Executar todas as 30 simulações
4. ⏳ Analisar resultados estatísticos
5. ⏳ Comparar com CNN
6. ⏳ Documentar conclusões

## Comandos Rápidos

```bash
# Teste rápido (1 simulação)
python run_roboflow_classification.py --simulation 1

# 5 simulações (teste de volume)
python run_roboflow_classification.py --num_simulations 5

# Todas as 30 simulações (produção)
python run_roboflow_classification.py --num_simulations 30

# Debug de predições
python debug_roboflow_predictions.py

# Ver resultados
cat ../../3_simulation/results/roboflow_emotion.csv
```

## Conclusão Preliminar

O classificador Roboflow está **funcional mas com performance limitada** (~35% acurácia).
Isso demonstra que modelos foundation de propósito geral podem não performar bem
em domínios específicos sem fine-tuning. A comparação com CNN treinada especificamente
será crucial para avaliar o trade-off entre conveniência e performance.
