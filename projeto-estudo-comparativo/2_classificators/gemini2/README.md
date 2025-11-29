# Classificador de Emoções - Google Cloud Vision API

Implementação de classificador de emoções faciais usando Google Cloud Vision API.

## Visão Geral

Este classificador utiliza a Google Cloud Vision API para detectar faces e analisar emoções faciais, classificando imagens em duas categorias: raiva (anger) e alegria (joy).

## Características

### Vantagens

- Detecção de faces de alta qualidade
- Análise nativa de emoções pela API
- Sem necessidade de treinamento
- API robusta e bem documentada
- Suporta múltiplas emoções (joy, sorrow, anger, surprise)
- Funciona imediatamente (zero setup)

### Desvantagens

- Custo por requisição (após free tier de 1000/mês)
- Requer internet
- Latência de rede (~500-1000ms por requisição)
- Menor controle sobre modelo
- Dependência de serviço externo

## Google Cloud Vision API

### O que é

API de visão computacional do Google Cloud que oferece:
- Detecção de faces
- Análise de emoções
- Detecção de objetos
- OCR (reconhecimento de texto)
- E muito mais

### Emoções Detectadas

A API retorna likelihood (probabilidade) para cada emoção:

- **joy**: Alegria
- **sorrow**: Tristeza
- **anger**: Raiva
- **surprise**: Surpresa

Cada emoção tem um score:
- VERY_UNLIKELY (1)
- UNLIKELY (2)
- POSSIBLE (3)
- LIKELY (4)
- VERY_LIKELY (5)

### Mapeamento para Dataset

Para nosso dataset binário (raiva vs alegria):

```python
if joy_score > anger_score and joy_score >= 3:
    return 'alegria'
elif anger_score > joy_score and anger_score >= 3:
    return 'raiva'
else:
    # Retorna maior score mesmo se baixo
    return 'alegria' if joy_score >= anger_score else 'raiva'
```

## Configuração

### 1. Criar Projeto no Google Cloud

1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Crie novo projeto ou selecione existente
3. Ative a Cloud Vision API

### 2. Configurar Autenticação

#### Opção A: Service Account (Recomendado para Produção)

1. No Google Cloud Console, vá em IAM & Admin > Service Accounts
2. Crie nova service account
3. Baixe arquivo JSON de credenciais
4. Configure variável de ambiente:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

#### Opção B: API Key (Mais Simples para Testes)

1. No Google Cloud Console, vá em APIs & Services > Credentials
2. Crie API Key
3. Adicione ao arquivo `.env` na raiz do projeto:

```bash
GOOGLE_API_KEY=sua_chave_api_aqui
```

### 3. Instalar Dependências

```bash
pip install -r 2_classificators/gemini2/requirements.txt
```

Ou manualmente:

```bash
pip install google-cloud-vision pillow pandas python-dotenv
```

## Uso

### Via Linha de Comando

#### 1. Processar todas as 30 simulações

```bash
cd /Users/jwcunha/Documents/repos/phd-datascience/visao-computacional/projeto-estudo-comparativo

python 2_classificators/gemini2/GoogleVisionEmotionClassifier.py --num_simulations 30
```

#### 2. Processar apenas uma simulação (teste)

```bash
python 2_classificators/gemini2/GoogleVisionEmotionClassifier.py --simulation 1
```

#### 3. Customizar diretórios

```bash
python 2_classificators/gemini2/GoogleVisionEmotionClassifier.py \
    --dataset_dir datasets \
    --results_dir 3_simulation/results \
    --model_name google_vision_emotion \
    --num_simulations 30
```

### Via Python (importando a classe)

```python
from GoogleVisionEmotionClassifier import GoogleVisionEmotionClassifier

# Inicializa classificador (API key do .env)
classifier = GoogleVisionEmotionClassifier(
    dataset_dir='../../datasets',
    results_dir='../../3_simulation/results',
    model_name='google_vision_emotion'
)

# Processar uma simulação
results = classifier.process_simulation(1)
print(f"Acurácia: {results['acuracia_geral']:.2%}")

# Processar todas
results_df = classifier.process_all_simulations(30)
print(results_df.describe())
```

## Formato de Saída

### Estrutura de Diretórios

```
3_simulation/results/google_vision_emotion/
├── results.csv           # CSV principal (formato especificado)
└── stats.json            # Estatísticas agregadas
```

### CSV (results.csv)

Formato idêntico aos outros classificadores:

```csv
numero_simulacao,nome_modelo,qtd_sucesso_alegria,qtd_sucesso_raiva,total_alegria,total_raiva,tempo_total_ms,acuracia_alegria,acuracia_raiva,acuracia_geral
1,google_vision_emotion,45,42,50,50,45230.45,0.90,0.84,0.87
2,google_vision_emotion,44,43,50,50,43120.32,0.88,0.86,0.87
...
```

### JSON (stats.json)

```json
{
  "modelo": "google_vision_emotion",
  "num_simulations": 30,
  "acuracia_alegria_mean": 0.88,
  "acuracia_alegria_std": 0.03,
  "acuracia_raiva_mean": 0.82,
  "acuracia_raiva_std": 0.04,
  "acuracia_geral_mean": 0.85,
  "acuracia_geral_std": 0.02,
  "tempo_total_segundos": 1350.67,
  "tempo_medio_por_simulacao": 45.02,
  "tempo_medio_ms": 45020.5,
  "tempo_std_ms": 2340.12,
  "timestamp": "2025-11-29T12:00:00"
}
```

## Performance Esperada

### Velocidade (por simulação - 100 imagens)

| Conexão | Tempo Esperado |
|---------|----------------|
| Boa (100+ Mbps) | ~30-45s |
| Média (10-100 Mbps) | ~45-90s |
| Lenta (<10 Mbps) | ~90-180s |

Nota: Cada imagem faz uma chamada HTTP à API, então velocidade depende muito da conexão de internet.

### Acurácia Esperada

| Métrica | Esperado |
|---------|----------|
| Acurácia Geral | 80-90% |
| Acurácia Alegria | 85-95% |
| Acurácia Raiva | 75-85% |

Google Vision é otimizado para detecção de alegria (joy), então pode ter performance ligeiramente melhor nessa classe.

### Custo

| Quantidade | Custo |
|------------|-------|
| 0-1000 imagens/mês | Grátis (free tier) |
| 1001-5000 imagens | $1.50 por 1000 |
| 5001+ imagens | $1.00 por 1000 |

Para 30 simulações × 100 imagens = 3000 imagens:
- Primeiras 1000: Grátis
- Restantes 2000: ~$3.00

## Comparação com Outros Classificadores

| Aspecto | CNN | Roboflow | YOLO11 | Google Vision |
|---------|-----|----------|--------|---------------|
| Acurácia | 85-95% | 30-40% | 0% (sem tuning) | 80-90% |
| Velocidade | ~10ms | ~600ms | ~2ms | ~450ms |
| Custo | GPU 1x | $/req | GPU 1x | $/req |
| Offline | Sim | Não | Sim | Não |
| Setup | Treinamento | Zero | Zero | API key |
| Qualidade | Alta | Baixa | N/A | Alta |

## Troubleshooting

### Erro: "GOOGLE_API_KEY não encontrada"

Solução:
```bash
# Adicione ao .env na raiz do projeto
echo "GOOGLE_API_KEY=sua_chave_aqui" >> .env
```

### Erro: "Failed to load credentials"

Solução:
```bash
# Configure service account
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"

# Ou use API key no .env
```

### Erro: "Quota exceeded"

Você excedeu o free tier de 1000 requisições/mês.

Soluções:
1. Aguarde próximo mês
2. Ative billing no Google Cloud
3. Use outro projeto do Google Cloud

### Lentidão Excessiva

Causas possíveis:
1. Conexão de internet lenta
2. Muitas requisições simultâneas (rate limiting)
3. Servidor da API sobrecarregado

Solução:
```python
# Adicione delay entre requisições
import time
time.sleep(0.5)  # 500ms de delay
```

### Erro: "No face detected"

A API não detectou face na imagem.

Possíveis causas:
1. Imagem muito pequena ou borrada
2. Face não visível ou cortada
3. Qualidade da imagem ruim

O classificador retorna `None` neste caso e conta como erro.

## Conceitos Pedagógicos

### Vantagens de APIs Comerciais

1. **Qualidade**: Modelos treinados em bilhões de imagens
2. **Manutenção**: Google mantém e melhora continuamente
3. **Escalabilidade**: Infraestrutura do Google
4. **Zero Setup**: Não precisa treinar ou configurar modelo

### Desvantagens de APIs Comerciais

1. **Custo Recorrente**: Paga por uso
2. **Vendor Lock-in**: Dependência do Google
3. **Latência**: Necessita internet
4. **Privacidade**: Dados enviados para Google
5. **Controle Limitado**: Não pode customizar modelo

### Quando Usar

Use Google Vision quando:
- Precisa de alta qualidade sem treinar
- Tem orçamento para API
- Conexão de internet confiável
- Dados não são sensíveis
- Prototipagem rápida

Não use quando:
- Precisa funcionar offline
- Dados são confidenciais
- Custo recorrente é problema
- Precisa customização específica
- Latência é crítica

## Recursos Adicionais

- [Google Cloud Vision API Docs](https://cloud.google.com/vision/docs)
- [Pricing Calculator](https://cloud.google.com/products/calculator)
- [Python Client Library](https://googleapis.dev/python/vision/latest/)
- [Face Detection Tutorial](https://cloud.google.com/vision/docs/detecting-faces)

## Próximos Passos

1. Execute teste com 1 simulação
2. Verifique acurácia e tempo
3. Execute todas as 30 simulações
4. Compare com outros classificadores
5. Analise trade-offs (acurácia vs custo vs velocidade)

## Comandos Rápidos

```bash
# Teste rápido (1 simulação)
python 2_classificators/gemini2/GoogleVisionEmotionClassifier.py --simulation 1

# Completo (30 simulações)
python 2_classificators/gemini2/GoogleVisionEmotionClassifier.py --num_simulations 30

# Ver resultados
cat 3_simulation/results/google_vision_emotion/results.csv | column -t -s,
cat 3_simulation/results/google_vision_emotion/stats.json | python -m json.tool
```

## Licença e Termos

Este código está sob licença do projeto. O uso da Google Cloud Vision API está sujeito aos [Termos de Serviço do Google Cloud](https://cloud.google.com/terms).
