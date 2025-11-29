# Classificador de Emoções - Roboflow API

## Visão Geral

Este módulo implementa um classificador de emoções faciais usando modelos pré-treinados disponíveis no Roboflow Universe. O objetivo é comparar o desempenho de modelos foundation (via API) com CNNs tradicionais treinadas do zero.

## Objetivo Pedagógico

### Por que usar Roboflow?

1. **Modelos Pré-treinados**: Acesso imediato a modelos de detecção de emoções sem necessidade de treinamento
2. **Comparação com CNNs**: Permite avaliar se vale a pena treinar um modelo próprio ou usar serviços pré-treinados
3. **Zero-shot Learning**: Testa capacidade de generalização em dados não vistos durante treinamento
4. **Infraestrutura Gerenciada**: Não precisa se preocupar com GPUs, escalabilidade, etc.

### Conceitos Aprendidos

- Diferença entre treinar modelo próprio vs usar APIs
- Trade-offs: controle vs conveniência
- Custos: tempo de desenvolvimento vs custos de API
- Avaliação de modelos foundation para tarefas específicas

## Instalação

### Dependências

```bash
pip install roboflow opencv-python pillow pandas numpy
```

### Obter API Key

1. Crie uma conta gratuita em [roboflow.com](https://roboflow.com)
2. Acesse [Settings > API](https://app.roboflow.com/settings/api)
3. Copie sua **Private API Key**

**Limites do Plano Gratuito:**
- 1,000 predições/mês
- ~100 requisições/minuto
- Acesso a modelos públicos do Universe

## Estrutura de Arquivos

```
2_classificators/others/
├── RoboflowEmotionClassifier.py   # Classe principal
├── example_roboflow_usage.py      # Exemplos de uso
└── README_ROBOFLOW.md             # Esta documentação

3_simulation/results/
└── roboflow_emotion.csv           # Resultados (após execução)
```

## Uso

### Via Linha de Comando

#### 1. Processar todas as 30 simulações

```bash
python RoboflowEmotionClassifier.py --api_key YOUR_API_KEY
```

**ATENÇÃO**: Isso fará ~3000 requisições (30 simulações × 100 imagens).
Verifique seu limite de API antes de executar!

#### 2. Processar apenas uma simulação (teste)

```bash
python RoboflowEmotionClassifier.py \
    --api_key YOUR_API_KEY \
    --simulation 1
```

#### 3. Processar primeiras N simulações

```bash
python RoboflowEmotionClassifier.py \
    --api_key YOUR_API_KEY \
    --num_simulations 5
```

#### 4. Usar modelo específico do Roboflow

```bash
python RoboflowEmotionClassifier.py \
    --api_key YOUR_API_KEY \
    --model_id workspace/project/version \
    --model_name meu_modelo_custom
```

### Via Python (importando a classe)

```python
from RoboflowEmotionClassifier import RoboflowEmotionClassifier

# Inicializa classificador
classifier = RoboflowEmotionClassifier(
    api_key='YOUR_API_KEY',
    model_id='emotions-dectection/human-face-emotions/1',
    dataset_dir='datasets',
    results_dir='3_simulation/results',
    model_name='roboflow_emotion'
)

# Processar uma simulação
results = classifier.process_simulation(1)
print(f"Acurácia: {results['acuracia_geral']:.2%}")

# Processar todas as simulações
df = classifier.process_all_simulations(num_simulations=30)
print(df.describe())
```

### Configuração com Variável de Ambiente

Para não expor sua API key no código:

```bash
# Linux/Mac
export ROBOFLOW_API_KEY="sua_api_key_aqui"
python example_roboflow_usage.py

# Windows
set ROBOFLOW_API_KEY=sua_api_key_aqui
python example_roboflow_usage.py
```

## Formato de Saída

### CSV Principal (roboflow_emotion.csv)

Colunas:
- `numero_simulacao`: 1-30
- `nome_modelo`: Identificador do modelo (ex: roboflow_emotion)
- `qtd_sucesso_alegria`: Número de acertos na classe alegria
- `qtd_sucesso_raiva`: Número de acertos na classe raiva
- `total_alegria`: Total de imagens da classe alegria (50)
- `total_raiva`: Total de imagens da classe raiva (50)
- `acuracia_alegria`: Acurácia na classe alegria (0.0 a 1.0)
- `acuracia_raiva`: Acurácia na classe raiva (0.0 a 1.0)
- `acuracia_geral`: Acurácia geral (média ponderada)
- `tempo_total_ms`: Tempo de processamento em milissegundos

### JSON de Estatísticas (roboflow_emotion_stats.json)

```json
{
  "modelo": "roboflow_emotion",
  "num_simulations": 30,
  "acuracia_alegria_mean": 0.75,
  "acuracia_alegria_std": 0.08,
  "acuracia_raiva_mean": 0.72,
  "acuracia_raiva_std": 0.09,
  "acuracia_geral_mean": 0.735,
  "acuracia_geral_std": 0.07,
  "tempo_total_segundos": 1234.56,
  "timestamp": "2025-11-29T10:30:00"
}
```

## Modelos Disponíveis no Roboflow

Alguns modelos públicos de detecção de emoções:

1. **emotions-dectection/human-face-emotions**
   - Emoções: angry, happy, sad, fear, surprise
   - Dataset: 9400+ imagens

2. **facial-emotion-hvq59/face-emotion-detection-multi**
   - Classificação multiclasse
   - Dataset: 4540+ imagens

3. **face-recognition-ixqtg/emotion-detection-cwq4g**
   - Object detection de emoções
   - Bounding boxes + classificação

Para usar outro modelo, basta alterar o `model_id`:

```bash
python RoboflowEmotionClassifier.py \
    --api_key YOUR_KEY \
    --model_id facial-emotion-hvq59/face-emotion-detection-multi/1
```

## Fluxo de Processamento

1. **Inicialização**
   - Conecta com API Roboflow
   - Carrega modelo especificado
   - Valida acesso e permissões

2. **Para cada simulação (sim01 - sim30)**
   - Para cada classe (raiva, alegria):
     - Lista todas as imagens (50 por classe)
     - Para cada imagem:
       - Envia para API Roboflow
       - Recebe predições de emoções
       - Mapeia para classe binária (raiva/alegria)
       - Compara com ground truth
       - Conta acerto/erro

3. **Agregação**
   - Calcula acurácia por classe
   - Calcula acurácia geral
   - Salva resultados em CSV
   - Gera estatísticas agregadas

## Mapeamento de Emoções

O classificador mapeia emoções detectadas pelo modelo para nossas 2 classes:

```python
emotion_mapping = {
    # Raiva
    'angry': 'raiva',
    'anger': 'raiva',
    'mad': 'raiva',
    'furious': 'raiva',

    # Alegria
    'happy': 'alegria',
    'happiness': 'alegria',
    'joy': 'alegria',
    'smile': 'alegria',

    # Ignoradas (não relevantes para estudo binário)
    'sad': None,
    'fear': None,
    'surprise': None,
    'neutral': None
}
```

## Comparação: Roboflow vs CNN Própria

### Vantagens do Roboflow

- Sem necessidade de treinamento
- Infraestrutura gerenciada (sem GPUs necessárias)
- Modelos já otimizados e validados
- Rápido para prototipar
- Atualizações automáticas

### Desvantagens do Roboflow

- Custo por requisição (após limite gratuito)
- Latência de rede (~100-500ms por imagem)
- Dependência de serviço externo
- Menos controle sobre arquitetura
- Impossível treinar em dados proprietários

### Quando usar cada abordagem?

**Use Roboflow quando:**
- Prototipando rapidamente
- Poucos dados ou tempo para treinar
- Orçamento para APIs
- Não tem hardware para treinamento

**Use CNN própria quando:**
- Precisa de customização específica
- Dados proprietários/sensíveis
- Alto volume de predições
- Latência crítica
- Orçamento limitado (longo prazo)

## Troubleshooting

### Erro: "Roboflow SDK não instalado"

```bash
pip install roboflow
```

### Erro: "API key inválida"

Verifique se copiou a **Private API Key** completa do Roboflow.

### Erro: "Rate limit exceeded"

O plano gratuito tem limite de ~100 req/min. O classificador já inclui delay de 100ms entre requisições. Se continuar o erro, aumente o delay em `predict_image()`.

### Erro: "Model not found"

Verifique se o `model_id` está no formato correto: `workspace/project/version`

### Baixa acurácia

Modelos pré-treinados podem não performar bem em datasets específicos. Considere:
- Testar outros modelos do Roboflow Universe
- Ajustar threshold de confiança
- Treinar modelo próprio com seus dados

## Estimativa de Custos e Tempo

### Tempo de Processamento

- Por imagem: ~0.5-1 segundo (incluindo latência de rede)
- Por simulação (100 imagens): ~1-2 minutos
- Todas as simulações (3000 imagens): ~50-100 minutos

### Custos (Plano Gratuito Roboflow)

- Limite: 1000 predições/mês grátis
- Dataset completo: 3000 predições
- **Conclusão**: Precisa de plano pago ou processar em 3 meses

**Plano Starter ($49/mês):**
- 10,000 predições/mês
- Suficiente para dataset completo + experimentos

## Próximos Passos

1. **Executar Classificação**
   ```bash
   python RoboflowEmotionClassifier.py --api_key YOUR_KEY
   ```

2. **Analisar Resultados**
   - Comparar CSV gerado com resultados da CNN
   - Avaliar acurácia relativa
   - Analisar custo-benefício

3. **Documentar Achados**
   - Qual modelo performou melhor?
   - Tempo de desenvolvimento vs tempo de inferência
   - Custos totais (infraestrutura + API)

4. **Explorar Melhorias**
   - Testar múltiplos modelos Roboflow
   - Ensemble de predições
   - Fine-tuning de thresholds

## Referências

- [Roboflow Universe](https://universe.roboflow.com) - Modelos públicos
- [Roboflow Docs](https://docs.roboflow.com) - Documentação oficial
- [Emotion Detection Models](https://universe.roboflow.com/search?q=emotion%20detection) - Modelos de emoções

## Licença e Termos

- Código do classificador: Use livremente para fins educacionais
- Modelos Roboflow: Sujeitos aos termos de cada modelo no Universe
- API Roboflow: Sujeita aos [Terms of Service](https://roboflow.com/terms) do Roboflow

## Contato e Suporte

Para dúvidas sobre o classificador, consulte a documentação ou logs de erro.
Para questões sobre a API Roboflow, consulte [Roboflow Support](https://roboflow.com/support).
