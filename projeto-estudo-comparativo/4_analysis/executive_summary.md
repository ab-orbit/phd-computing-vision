# Resumo Executivo## Análise Comparativa: Google Vision vs Roboflow
### Classificação de Emoções Faciais
---

**Data**: 29 de November de 2025

---

## Contexto

Este estudo comparou dois classificadores de emoções faciais baseados em APIs de modelos foundation para a tarefa de classificação binária entre expressões de **Alegria** e **Raiva**:

1. **Google Cloud Vision API**: Modelo genérico de visão computacional
2. **Roboflow API**: Modelo especializado `computer-vision-projects-zhogq/emotion-detection-y0svj`

**Metodologia**: 30 simulações independentes com 50 imagens por classe (100 imagens/simulação), totalizando 3.000 imagens processadas por modelo.

## Principais Achados

### 1. Roboflow é Estatisticamente Superior

**Evidência Estatística**:
- Teste de Wilcoxon pareado: **p < 0.001** (altamente significativo)
- Tamanho de efeito: **Grande** (r > 0.8)
- Diferença consistente em **todas as 30 simulações**

**Performance Comparativa**:

| Métrica | Google Vision | Roboflow | Diferença |
|---------|---------------|----------|----------|
| Acurácia | 16.4% ± 4.0% | 38.5% ± 3.7% | **+22.1%** |
| F1-Score | 0.151 | 0.339 | +0.188 |
| Tempo (s) | 139.4s | 58.1s | **2.4× mais rápido** |

### 2. Ambos Apresentam Performance Insatisfatória

Apesar da diferença estatística, **nenhum dos modelos** atinge performance adequada para produção:

- **Google Vision**: Apenas 16.4% de acurácia
- **Roboflow**: Apenas 38.5% de acurácia
- **Benchmark mínimo recomendado**: >70% para aplicações práticas

### 3. Forte Viés para Classe Alegria

Ambos os modelos apresentam dificuldade significativa em identificar raiva:

**Por Classe**:
- **Google Vision**: Alegria 28.5% vs Raiva 4.4%
- **Roboflow**: Alegria 64.3% vs Raiva 12.7%

**Implicação**: Modelos não são confiáveis para detectar raiva, possivelmente devido a diferenças entre datasets de treinamento e validação.

### 4. Roboflow Oferece Melhor Custo-Benefício

- **Velocidade**: Roboflow é ~2.4× mais rápido
- **Acurácia**: Roboflow é ~{robo_acc/goog_acc:.1f}× mais preciso
- **Custo**: Similar (~$3.00 para 3.000 imagens)
- **Custo/Performance**: $0.08 vs $0.18 por ponto percentual de acurácia

## Recomendações

### Curto Prazo

1. **Não utilizar esses modelos em produção** sem validação extensiva adicional
2. **Entre as opções testadas, preferir Roboflow** se uso de API for necessário
3. **Implementar validação humana** para predições de raiva (alta taxa de erro)
4. **Estabelecer threshold de confiança** para rejeitar predições incertas

### Médio Prazo

1. **Executar e avaliar YOLO11** (modelo foundation local) conforme planejamento original
2. **Implementar CNN treinada do zero** como baseline de comparação
3. **Coletar dataset maior** (>10.000 imagens) para treinar modelo especializado
4. **Balancear dataset** entre classes se possível

### Longo Prazo

1. **Fine-tuning de modelos foundation** no domínio específico
2. **Desenvolver modelo proprietário** otimizado para a aplicação
3. **Implementar ensemble** de múltiplos modelos para maior robustez
4. **Expandir para mais classes** de emoções se aplicável

## Próximos Passos Imediatos

1. **Executar YOLO11**: Completar análise comparativa com terceiro modelo
2. **Análise de erros**: Identificar quais imagens são consistentemente mal classificadas
3. **Revisão de dataset**: Verificar qualidade e representatividade das imagens
4. **Buscar alternativas**: Avaliar outros modelos foundation ou APIs especializadas
5. **Considerar abordagem híbrida**: Combinar API (rapidez) com validação local (precisão)

## Conclusão

Embora **Roboflow seja estatisticamente superior ao Google Vision** em todas as métricas avaliadas (p<0.001, tamanho de efeito grande), **ambos os modelos apresentam performance insatisfatória** para uso em produção (acurácia <40%).

A análise demonstra que **APIs genéricas de modelos foundation não substituem modelos especializados** para tarefas específicas. Para aplicações reais de classificação de emoções, recomenda-se investir em:

- **Fine-tuning** de modelos foundation
- **Treinamento de modelos customizados**
- **Datasets maiores e mais representativos**
- **Validação humana** para casos críticos

---

**Para detalhes completos**, consultar o relatório principal: `comparative_analysis_report.md`

*Resumo gerado em 29/11/2025 às 14:17*
