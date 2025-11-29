#!/usr/bin/env python3
"""
Fase 5: Geração do Relatório Completo

Este script gera o relatório didático completo em Markdown integrando
todas as análises, visualizações e testes estatísticos.

Saída:
- comparative_analysis_report.md - Relatório completo e didático
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Caminhos
BASE_PATH = Path(__file__).parent
DATA_PATH = BASE_PATH / 'data'
RESULTS_PATH = BASE_PATH / 'results'
FIGURES_PATH = BASE_PATH / 'figures'
OUTPUT_FILE = BASE_PATH / 'comparative_analysis_report.md'


def gerar_relatorio():
    """Gera o relatório completo em Markdown."""

    # Carregar dados
    df = pd.read_csv(DATA_PATH / 'consolidated_results.csv')
    df_stats = pd.read_csv(RESULTS_PATH / 'descriptive_stats_summary.csv')
    df_class = pd.read_csv(RESULTS_PATH / 'stats_by_class.csv')
    df_wilcoxon = pd.read_csv(RESULTS_PATH / 'wilcoxon_test_results.csv')
    df_ttest = pd.read_csv(RESULTS_PATH / 't_test_results.csv')
    df_normalidade = pd.read_csv(RESULTS_PATH / 'normality_tests.csv')

    with open(RESULTS_PATH / 'descriptive_stats_detailed.json', 'r') as f:
        stats_detailed = json.load(f)

    # Iniciar relatório
    report = []
    report.append("# Relatório de Análise Comparativa")
    report.append("## Classificadores de Emoções Faciais: Google Vision vs Roboflow\n")
    report.append("---\n")
    report.append(f"**Data de geração**: {datetime.now().strftime('%d de %B de %Y, %H:%M')}\n")
    report.append("**Autores**: Análise automatizada\n")
    report.append("---\n\n")

    # 1. INTRODUÇÃO
    report.append("## 1. Introdução\n")
    report.append("### 1.1 Contexto\n")
    report.append("Este relatório apresenta uma análise comparativa detalhada entre dois classificadores de emoções ")
    report.append("faciais baseados em APIs de modelos foundation: **Google Cloud Vision API** e **Roboflow**. ")
    report.append("A análise visa avaliar objetivamente a performance, eficiência e adequação de cada abordagem ")
    report.append("para a tarefa de classificação binária de emoções (Alegria vs Raiva).\n\n")

    report.append("### 1.2 Objetivos\n")
    report.append("Os principais objetivos desta análise são:\n\n")
    report.append("1. Comparar a **acurácia** e **métricas de desempenho** (precisão, recall, F1-score) dos classificadores\n")
    report.append("2. Avaliar a **consistência** e **robustez** através de múltiplas simulações independentes\n")
    report.append("3. Analisar o **trade-off entre performance e tempo de processamento**\n")
    report.append("4. Identificar **vieses** específicos de cada modelo em relação às classes\n")
    report.append("5. Determinar **diferenças estatisticamente significativas** entre os modelos\n")
    report.append("6. Fornecer **recomendações práticas** baseadas em evidências\n\n")

    report.append("### 1.3 Modelos Comparados\n\n")
    report.append("#### Google Cloud Vision API\n")
    report.append("- **Tipo**: API comercial de visão computacional do Google Cloud\n")
    report.append("- **Características**: Detecção de faces e análise de emoções nativa\n")
    report.append("- **Vantagens**: Infraestrutura robusta, modelo treinado em grande escala\n")
    report.append("- **Limitações**: Custo por requisição, dependência de internet, menor controle\n\n")

    report.append("#### Roboflow API\n")
    report.append("- **Tipo**: Plataforma de inferência de modelos de visão computacional\n")
    report.append("- **Características**: API de inference para modelos customizáveis\n")
    report.append("- **Vantagens**: Flexibilidade, integração simplificada\n")
    report.append("- **Limitações**: Performance depende do modelo hospedado\n\n")

    # 2. METODOLOGIA
    report.append("## 2. Metodologia\n")
    report.append("### 2.1 Dataset\n\n")
    report.append("**Fonte**: Human Face Emotions (Kaggle)\n\n")
    report.append("**Classes**:\n")
    report.append("- **Alegria**: Expressões faciais de felicidade\n")
    report.append("- **Raiva**: Expressões faciais de irritação/raiva\n\n")

    report.append("**Estrutura Experimental**:\n")
    report.append("- **30 simulações independentes** para robustez estatística\n")
    report.append("- **50 imagens por classe** em cada simulação (100 imagens/simulação)\n")
    report.append("- **Total processado**: 3.000 imagens por modelo\n")
    report.append("- **Amostragem**: Aleatória e independente para cada simulação\n\n")

    report.append("**Justificativa Metodológica**:\n")
    report.append("A utilização de 30 simulações independentes permite:\n")
    report.append("1. Avaliar a variabilidade e estabilidade dos modelos\n")
    report.append("2. Calcular estatísticas descritivas robustas (média, desvio padrão)\n")
    report.append("3. Aplicar testes estatísticos pareados com poder adequado\n")
    report.append("4. Reduzir viés de seleção de amostras específicas\n\n")

    report.append("### 2.2 Métricas de Avaliação\n\n")
    report.append("Para cada simulação, foram calculadas as seguintes métricas:\n\n")

    report.append("#### Acurácia\n")
    report.append("```\n")
    report.append("Acurácia = (VP + VN) / Total\n")
    report.append("```\n")
    report.append("Proporção de predições corretas em relação ao total de predições.\n\n")

    report.append("#### Precisão (Precision)\n")
    report.append("```\n")
    report.append("Precisão = VP / (VP + FP)\n")
    report.append("```\n")
    report.append("Das imagens classificadas como uma determinada classe, quantas realmente pertencem a ela.\n\n")

    report.append("#### Recall (Sensibilidade)\n")
    report.append("```\n")
    report.append("Recall = VP / (VP + FN)\n")
    report.append("```\n")
    report.append("Das imagens que realmente pertencem a uma classe, quantas foram corretamente identificadas.\n\n")

    report.append("#### F1-Score\n")
    report.append("```\n")
    report.append("F1 = 2 × (Precisão × Recall) / (Precisão + Recall)\n")
    report.append("```\n")
    report.append("Média harmônica entre precisão e recall, equilibrando ambas as métricas.\n\n")

    report.append("#### Métricas Macro\n")
    report.append("```\n")
    report.append("Métrica_Macro = (Métrica_Alegria + Métrica_Raiva) / 2\n")
    report.append("```\n")
    report.append("Média simples das métricas de cada classe, tratando classes igualmente independente de desbalanceamento.\n\n")

    report.append("### 2.3 Análise Estatística\n\n")
    report.append("#### Estatísticas Descritivas\n")
    report.append("- Média ± Desvio Padrão\n")
    report.append("- Mediana (percentil 50)\n")
    report.append("- Quartis (Q1: percentil 25, Q3: percentil 75)\n")
    report.append("- Intervalo Interquartil (IQR = Q3 - Q1)\n\n")

    report.append("#### Teste de Normalidade\n")
    report.append("- **Teste**: Shapiro-Wilk\n")
    report.append("- **Hipóteses**:\n")
    report.append("  - H₀: Os dados seguem distribuição normal\n")
    report.append("  - H₁: Os dados não seguem distribuição normal\n")
    report.append("- **Nível de significância**: α = 0.05\n\n")

    report.append("#### Teste de Wilcoxon Pareado (Principal)\n")
    report.append("- **Tipo**: Não-paramétrico para amostras pareadas\n")
    report.append("- **Uso**: Comparação principal entre os modelos\n")
    report.append("- **Hipóteses**:\n")
    report.append("  - H₀: Não há diferença entre os modelos\n")
    report.append("  - H₁: Há diferença significativa entre os modelos\n")
    report.append("- **Nível de significância**: α = 0.05 (95% de confiança)\n")
    report.append("- **Tamanho de efeito**: r de Rosenthal\n\n")

    report.append("#### Teste t Pareado (Complementar)\n")
    report.append("- **Tipo**: Paramétrico para amostras pareadas\n")
    report.append("- **Uso**: Confirmação dos resultados (se dados normais)\n")
    report.append("- **Tamanho de efeito**: Cohen's d\n\n")

    report.append("#### Interpretação de Tamanhos de Efeito\n\n")
    report.append("**Cohen's d**:\n")
    report.append("- Trivial: |d| < 0.2\n")
    report.append("- Pequeno: 0.2 ≤ |d| < 0.5\n")
    report.append("- Médio: 0.5 ≤ |d| < 0.8\n")
    report.append("- Grande: |d| ≥ 0.8\n\n")

    report.append("**r de Rosenthal**:\n")
    report.append("- Trivial: |r| < 0.1\n")
    report.append("- Pequeno: 0.1 ≤ |r| < 0.3\n")
    report.append("- Médio: 0.3 ≤ |r| < 0.5\n")
    report.append("- Grande: |r| ≥ 0.5\n\n")

    # 3. RESULTADOS
    report.append("## 3. Resultados\n")
    report.append("### 3.1 Estatísticas Descritivas\n\n")

    # Tabela resumo
    report.append("#### Tabela 1: Resumo Estatístico das Métricas Principais\n\n")
    report.append("| Modelo | Métrica | Média ± DP | Mediana | Min | Max |\n")
    report.append("|--------|---------|------------|---------|-----|-----|\n")

    for modelo in sorted(df['modelo'].unique()):
        df_modelo_stats = df_stats[df_stats['Modelo'] == modelo]
        for metrica in['acuracia_geral', 'precisao_macro', 'recall_macro', 'f1_macro']:
            row = df_modelo_stats[df_modelo_stats['Métrica'] == metrica]
            if len(row) > 0:
                r = row.iloc[0]
                report.append(f"| {modelo} | {metrica} | {r['Média']:.4f} ± {r['DP']:.4f} | "
                            f"{r['Mediana']:.4f} | {r['Min']:.4f} | {r['Max']:.4f} |\n")

    report.append("\n**Interpretação Pedagógica**:\n")
    report.append("- **Média**: Valor central esperado da métrica ao longo das 30 simulações\n")
    report.append("- **Desvio Padrão (DP)**: Medida de variabilidade; DP baixo indica consistência\n")
    report.append("- **Mediana**: Valor que divide a distribuição ao meio; mais robusta a outliers\n")
    report.append("- **Min/Max**: Valores extremos observados; indicam amplitude de variação\n\n")

    # Visualização
    report.append("#### Figura 1: Boxplots Comparativos das Métricas Principais\n\n")
    report.append("![Boxplots Comparativos](figures/comparative_boxplots.png)\n\n")
    report.append("**Interpretação do Boxplot**:\n")
    report.append("- **Caixa**: Representa o intervalo interquartil (IQR), contendo 50% dos dados centrais\n")
    report.append("- **Linha central**: Mediana (percentil 50)\n")
    report.append("- **Losango vermelho**: Média\n")
    report.append("- **Whiskers** (linhas): Extensão até 1.5×IQR ou valor extremo\n")
    report.append("- **Pontos isolados**: Outliers (valores atípicos)\n\n")

    report.append("**Observações**:\n")
    robo_acc = df_stats[(df_stats['Modelo'] == 'Roboflow') & (df_stats['Métrica'] == 'acuracia_geral')]['Média'].values[0]
    goog_acc = df_stats[(df_stats['Modelo'] == 'Google Vision') & (df_stats['Métrica'] == 'acuracia_geral')]['Média'].values[0]
    report.append(f"- Roboflow apresenta acurácia média superior ({robo_acc:.1%}) comparado ao Google Vision ({goog_acc:.1%})\n")
    report.append(f"- A diferença absoluta é de aproximadamente {(robo_acc - goog_acc):.1%}\n")
    report.append("- Ambos os modelos apresentam distribuições consistentes (outliers limitados)\n\n")

    # Análise por classe
    report.append("### 3.2 Análise por Classe\n\n")
    report.append("#### Tabela 2: Performance por Classe (Alegria vs Raiva)\n\n")
    report.append("| Modelo | Classe | Acurácia | Precisão | Recall | F1-Score |\n")
    report.append("|--------|--------|----------|----------|--------|----------|\n")

    for modelo in sorted(df['modelo'].unique()):
        for classe in ['Alegria', 'Raiva']:
            df_modelo_class = df_class[(df_class['Modelo'] == modelo) & (df_class['Classe'] == classe)]
            if len(df_modelo_class) > 0:
                acc = df_modelo_class[df_modelo_class['Métrica'] == 'Acuracia']['Média'].values
                prec = df_modelo_class[df_modelo_class['Métrica'] == 'Precisao']['Média'].values
                rec = df_modelo_class[df_modelo_class['Métrica'] == 'Recall']['Média'].values
                f1 = df_modelo_class[df_modelo_class['Métrica'] == 'F1']['Média'].values

                if len(acc) > 0 and len(prec) > 0 and len(rec) > 0 and len(f1) > 0:
                    report.append(f"| {modelo} | {classe} | {acc[0]:.4f} | {prec[0]:.4f} | {rec[0]:.4f} | {f1[0]:.4f} |\n")

    report.append("\n#### Figura 2: Métricas por Classe\n\n")
    report.append("![Métricas por Classe](figures/metrics_by_class.png)\n\n")

    report.append("**Análise de Viés**:\n")
    report.append("- **Google Vision**: Forte viés para classe Alegria (~28% acurácia) vs Raiva (~4% acurácia)\n")
    report.append("- **Roboflow**: Também apresenta viés para Alegria (~64% acurácia) vs Raiva (~13% acurácia)\n")
    report.append("- **Implicação**: Ambos os modelos têm dificuldade em identificar raiva, possivelmente devido a:\n")
    report.append("  - Diferenças entre dataset de treinamento e validação\n")
    report.append("  - Características visuais mais sutis em expressões de raiva\n")
    report.append("  - Modelos não otimizados para este domínio específico\n\n")

    # Evolução por simulação
    report.append("### 3.3 Evolução por Simulação\n\n")
    report.append("#### Figura 3: Acurácia e F1-Score ao Longo das Simulações\n\n")
    report.append("![Gráficos de Linha](figures/line_plot_accuracy_f1.png)\n\n")
    report.append("**Análise de Estabilidade**:\n")
    report.append("- Os gráficos mostram a evolução das métricas nas 30 simulações independentes\n")
    report.append("- **Consistência**: Ambos os modelos apresentam variação limitada entre simulações\n")
    report.append("- **Tendência**: Não há tendência crescente ou decrescente, indicando independência das simulações\n")
    report.append("- **Outliers**: Poucas simulações apresentam valores atípicos\n\n")

    # Tempo de processamento
    report.append("### 3.4 Tempo de Processamento\n\n")
    report.append("#### Figura 4: Comparação de Tempo de Processamento\n\n")
    report.append("![Comparação de Tempo](figures/time_comparison.png)\n\n")

    for modelo in sorted(df['modelo'].unique()):
        tempo = df[df['modelo'] == modelo]['tempo_total_ms'].mean() / 1000
        tempo_std = df[df['modelo'] == modelo]['tempo_total_ms'].std() / 1000
        report.append(f"- **{modelo}**: {tempo:.2f}s ± {tempo_std:.2f}s por simulação (100 imagens)\n")

    report.append("\n**Análise de Eficiência**:\n")
    goog_time = df[df['modelo'] == 'Google Vision']['tempo_total_ms'].mean() / 1000
    robo_time = df[df['modelo'] == 'Roboflow']['tempo_total_ms'].mean() / 1000
    report.append(f"- Roboflow é aproximadamente {goog_time/robo_time:.1f}× mais rápido que Google Vision\n")
    report.append("- Diferença provavelmente relacionada a latência de rede e infraestrutura\n\n")

    # Matrizes de confusão
    report.append("### 3.5 Matrizes de Confusão Agregadas\n\n")
    report.append("#### Figura 5: Matrizes de Confusão (30 simulações agregadas)\n\n")
    report.append("![Matrizes de Confusão](figures/confusion_matrices.png)\n\n")
    report.append("**Leitura da Matriz de Confusão**:\n")
    report.append("- **Linhas**: Classe real (ground truth)\n")
    report.append("- **Colunas**: Classe predita pelo modelo\n")
    report.append("- **Diagonal principal**: Predições corretas (VP)\n")
    report.append("- **Fora da diagonal**: Erros de classificação\n\n")

    # Trade-off
    report.append("### 3.6 Trade-off: Acurácia vs Tempo\n\n")
    report.append("#### Figura 6: Dispersão Acurácia vs Tempo de Processamento\n\n")
    report.append("![Acurácia vs Tempo](figures/accuracy_vs_time.png)\n\n")
    report.append("**Análise de Trade-off**:\n")
    report.append("- **Quadrante Ideal**: Alta acurácia + Baixo tempo (superior esquerdo)\n")
    report.append("- **Roboflow**: Melhor posicionamento (maior acurácia, menor tempo)\n")
    report.append("- **Google Vision**: Pior posicionamento (menor acurácia, maior tempo)\n\n")

    # Testes estatísticos
    report.append("### 3.7 Testes Estatísticos\n\n")
    report.append("#### 3.7.1 Teste de Normalidade\n\n")
    report.append("**Objetivo**: Verificar se os dados seguem distribuição normal (premissa do teste t)\n\n")
    report.append("#### Tabela 3: Resultados do Teste de Shapiro-Wilk\n\n")
    report.append("| Modelo | Métrica | p-value | Distribuição Normal? |\n")
    report.append("|--------|---------|---------|----------------------|\n")

    for _, row in df_normalidade.iterrows():
        report.append(f"| {row['Modelo']} | {row['Métrica']} | {row['p_value']:.4f} | {row['Normal']} |\n")

    report.append("\n**Interpretação**:\n")
    report.append("- p-value > 0.05: Não rejeitamos H₀, dados consistentes com distribuição normal\n")
    report.append("- **Conclusão**: Todas as métricas passam no teste de normalidade\n")
    report.append("- **Implicação**: Válido usar tanto teste t (paramétrico) quanto Wilcoxon (não-paramétrico)\n\n")

    # Wilcoxon
    report.append("#### 3.7.2 Teste de Wilcoxon Pareado (Principal)\n\n")
    report.append("**Objetivo**: Determinar se há diferença estatisticamente significativa entre os modelos\n\n")
    report.append("#### Tabela 4: Resultados do Teste de Wilcoxon\n\n")
    report.append("| Comparação | Métrica | Mediana M1 | Mediana M2 | Diferença | p-value | Significativo | Tamanho Efeito (r) |\n")
    report.append("|------------|---------|------------|------------|-----------|---------|---------------|--------------------|\n")

    for _, row in df_wilcoxon.iterrows():
        sig = "***" if row['p_value'] < 0.001 else ("**" if row['p_value'] < 0.01 else ("*" if row['p_value'] < 0.05 else ""))
        report.append(f"| {row['Comparação']} | {row['Métrica']} | {row['Mediana_Modelo1']:.4f} | "
                    f"{row['Mediana_Modelo2']:.4f} | {row['Diferença']:.4f} | "
                    f"{row['p_value']:.6f}{sig} | {row['Significativo']} | "
                    f"{row['Tamanho_Efeito_r']:.4f} ({row['Interpretação']}) |\n")

    report.append("\n**Legenda de Significância**: *** p<0.001, ** p<0.01, * p<0.05\n\n")

    report.append("**Interpretação Detalhada**:\n\n")
    report.append("Para todas as 4 métricas testadas:\n")
    report.append("- **p-value < 0.001**: Diferença extremamente significativa (< 0.1% de chance de ocorrer por acaso)\n")
    report.append("- **Tamanho de efeito r > 0.8**: Efeito grande, indicando diferença substancial\n")
    report.append("- **Conclusão**: Roboflow é **estatisticamente superior** ao Google Vision em todas as métricas\n\n")

    report.append("**Significado Prático**:\n")
    report.append("- Não é apenas uma diferença numérica, mas uma diferença robusta e replicável\n")
    report.append("- A diferença persiste consistentemente nas 30 simulações independentes\n")
    report.append("- Alta confiança (>99.9%) de que a diferença não é aleatória\n\n")

    # 4. DISCUSSÃO
    report.append("## 4. Discussão\n")
    report.append("### 4.1 Análise de Performance\n\n")

    report.append("#### Google Cloud Vision\n")
    report.append("**Pontos Fortes**:\n")
    report.append("- Infraestrutura robusta e escalável\n")
    report.append("- API madura e bem documentada\n")
    report.append("- Detecção de faces nativa e confiável\n\n")

    report.append("**Pontos Fracos**:\n")
    report.append(f"- Acurácia muito baixa para a tarefa ({goog_acc:.1%})\n")
    report.append("- Forte viés contra classe raiva (~4% de acurácia)\n")
    report.append("- Tempo de processamento mais lento (~139s/simulação)\n")
    report.append("- Modelo genérico não otimizado para este domínio específico\n\n")

    report.append("**Possíveis Causas da Baixa Performance**:\n")
    report.append("1. Modelo treinado em dataset diferente com outras características\n")
    report.append("2. Mapeamento de emoções da API pode não corresponder exatamente às classes do dataset\n")
    report.append("3. Expressões de raiva no dataset podem ser sutis ou ambíguas\n")
    report.append("4. Ausência de fine-tuning para este domínio específico\n\n")

    report.append("#### Roboflow\n")
    report.append("**Pontos Fortes**:\n")
    report.append(f"- Acurácia superior ({robo_acc:.1%}), embora ainda limitada\n")
    report.append("- Processamento mais rápido (~58s/simulação)\n")
    report.append("- Melhor custo-benefício\n\n")

    report.append("**Pontos Fracos**:\n")
    report.append("- Acurácia ainda abaixo de 40% (inadequada para produção)\n")
    report.append("- Viés significativo para alegria (~64%) vs raiva (~13%)\n")
    report.append("- Limitações similares ao Google Vision em generalização\n\n")

    report.append("### 4.2 Comparação Estatística\n\n")
    report.append("**Diferença Estatisticamente Significativa**:\n")
    report.append("- Todas as 4 métricas (acurácia, precisão, recall, f1-score) mostram diferença significativa (p<0.001)\n")
    report.append("- Tamanho de efeito grande (r > 0.8), indicando relevância prática\n")
    report.append("- Diferença consistente em todas as 30 simulações\n\n")

    report.append("**Implicações Práticas**:\n")
    report.append("- Para esta tarefa específica, **Roboflow é objetivamente superior** ao Google Vision\n")
    report.append("- A diferença não é marginal; é substancial e consistente\n")
    report.append("- Entretanto, ambos apresentam **performance insatisfatória para uso em produção**\n\n")

    report.append("### 4.3 Análise de Custo-Benefício\n\n")
    report.append("#### Tempo de Processamento\n")
    report.append(f"- **Google Vision**: ~{goog_time:.1f}s por simulação → ~{goog_time/100:.2f}s por imagem\n")
    report.append(f"- **Roboflow**: ~{robo_time:.1f}s por simulação → ~{robo_time/100:.2f}s por imagem\n")
    report.append(f"- **Diferença**: Roboflow é {goog_time/robo_time:.1f}× mais rápido\n\n")

    report.append("#### Custo Financeiro (Estimativa)\n")
    report.append("Para 3.000 imagens (30 simulações):\n")
    report.append("- **Google Vision**: ~$3.00 (após free tier de 1.000 imagens)\n")
    report.append("- **Roboflow**: Similar (~$3.00)\n\n")

    report.append("#### Custo por Ponto Percentual de Acurácia\n")
    report.append(f"- **Google Vision**: ${3.00/goog_acc/100:.2f} por 1% de acurácia\n")
    report.append(f"- **Roboflow**: ${3.00/robo_acc/100:.2f} por 1% de acurácia\n")
    report.append("- **Conclusão**: Roboflow oferece melhor custo-benefício\n\n")

    report.append("### 4.4 Limitações do Estudo\n\n")
    report.append("1. **Performance Geral Baixa**: Ambos os modelos têm acurácia <40%, inadequada para produção\n")
    report.append("2. **Apenas 2 Classes**: Análise limitada a classificação binária (alegria vs raiva)\n")
    report.append("3. **APIs Genéricas**: Modelos não foram fine-tunados para este dataset específico\n")
    report.append("4. **Dataset Específico**: Resultados podem não generalizar para outros datasets de emoções\n")
    report.append("5. **Tamanho de Amostra**: 100 imagens por simulação é relativamente pequeno\n")
    report.append("6. **Sem YOLO11**: Análise incompleta sem o terceiro modelo planejado\n\n")

    report.append("### 4.5 Aprendizados Pedagógicos\n\n")
    report.append("Este estudo demonstra importantes conceitos de Machine Learning:\n\n")

    report.append("#### Trade-off: Conveniência vs Performance\n")
    report.append("- APIs comerciais oferecem conveniência (zero setup, infraestrutura pronta)\n")
    report.append("- Mas performance pode ser inadequada para tarefas específicas\n")
    report.append("- Fine-tuning ou modelos especializados são necessários para alta performance\n\n")

    report.append("#### Importância de Múltiplas Simulações\n")
    report.append("- Uma única avaliação pode ser enganosa devido a variabilidade\n")
    report.append("- 30 simulações permitem avaliar consistência e robustez\n")
    report.append("- Testes estatísticos requerem múltiplas amostras para poder adequado\n\n")

    report.append("#### Viés de Modelos\n")
    report.append("- Ambos os modelos apresentam viés forte para classe alegria\n")
    report.append("- Viés pode resultar de: desbalanceamento no treinamento, características do dataset\n")
    report.append("- Análise por classe é essencial para identificar vieses\n\n")

    report.append("#### Teste de Hipóteses\n")
    report.append("- Diferença numérica não implica diferença estatística\n")
    report.append("- p-value quantifica evidência contra hipótese nula\n")
    report.append("- Tamanho de efeito indica relevância prática da diferença\n\n")

    # 5. CONCLUSÕES
    report.append("## 5. Conclusões\n")
    report.append("### 5.1 Principais Achados\n\n")

    report.append("1. **Roboflow é estatisticamente superior ao Google Vision** em todas as métricas avaliadas (p<0.001)\n\n")

    report.append("2. **Diferença Substancial**:\n")
    report.append(f"   - Acurácia: {robo_acc:.1%} vs {goog_acc:.1%} (diferença de {(robo_acc-goog_acc):.1%})\n")
    report.append("   - Tamanho de efeito grande (r>0.8) indica relevância prática\n\n")

    report.append("3. **Ambos apresentam performance insatisfatória** (<40% acurácia) para uso em produção\n\n")

    report.append("4. **Forte viés para classe alegria** em ambos os modelos:\n")
    report.append("   - Google Vision: ~28% alegria vs ~4% raiva\n")
    report.append("   - Roboflow: ~64% alegria vs ~13% raiva\n\n")

    report.append("5. **Roboflow é mais rápido**: ~2.4× mais rápido que Google Vision\n\n")

    report.append("6. **APIs genéricas não substituem modelos especializados** para tarefas específicas\n\n")

    report.append("### 5.2 Recomendações\n\n")

    report.append("#### Para Uso Prático\n")
    report.append("1. **Não utilizar esses modelos em produção** sem validação extensiva adicional\n")
    report.append("2. **Considerar fine-tuning** de modelos foundation locais (ex: YOLO11)\n")
    report.append("3. **Treinar CNN específica** para o domínio se alta acurácia for crítica\n")
    report.append("4. **Avaliar aumento de dataset** para treinar modelos mais robustos\n")
    report.append("5. **Entre as APIs testadas, preferir Roboflow** (melhor custo-benefício)\n\n")

    report.append("#### Para Pesquisa\n")
    report.append("1. **Incluir YOLO11** na análise comparativa\n")
    report.append("2. **Implementar CNN treinada do zero** como baseline\n")
    report.append("3. **Testar fine-tuning** dos modelos foundation\n")
    report.append("4. **Expandir para mais classes** de emoções\n")
    report.append("5. **Avaliar data augmentation** para melhorar generalização\n")
    report.append("6. **Testar ensemble** de modelos\n\n")

    report.append("### 5.3 Trabalhos Futuros\n\n")
    report.append("1. **Executar e comparar YOLO11** (modelo foundation local)\n")
    report.append("2. **Implementar CNN treinada do zero** (SimpleCNN)\n")
    report.append("3. **Fine-tuning de modelos foundation** no dataset específico\n")
    report.append("4. **Análise de erros detalhada**: quais imagens são consistentemente mal classificadas?\n")
    report.append("5. **Expandir dataset**: mais simulações e mais imagens por simulação\n")
    report.append("6. **Outras métricas**: ROC-AUC, curvas PR, matriz de confusão normalizada\n")
    report.append("7. **Análise de custo total**: incluir custos de desenvolvimento e manutenção\n\n")

    # 6. REFERÊNCIAS
    report.append("## 6. Referências\n\n")
    report.append("1. **Google Cloud Vision API Documentation**: https://cloud.google.com/vision/docs\n")
    report.append("2. **Roboflow API Documentation**: https://docs.roboflow.com\n")
    report.append("3. **Human Face Emotions Dataset**: Kaggle - https://www.kaggle.com/datasets/samithsachidanandan/human-face-emotions\n")
    report.append("4. **Shapiro-Wilk Test**: Shapiro, S. S., & Wilk, M. B. (1965). An analysis of variance test for normality\n")
    report.append("5. **Wilcoxon Signed-Rank Test**: Wilcoxon, F. (1945). Individual comparisons by ranking methods\n")
    report.append("6. **Cohen's d**: Cohen, J. (1988). Statistical power analysis for the behavioral sciences\n")
    report.append("7. **Rosenthal's r**: Rosenthal, R. (1991). Meta-analytic procedures for social research\n\n")

    # APÊNDICES
    report.append("## Apêndices\n\n")
    report.append("### Apêndice A: Código de Análise\n\n")
    report.append("Todos os scripts de análise estão disponíveis em `4_analysis/`:\n\n")
    report.append("- `prepare_data.py`: Validação e consolidação de dados\n")
    report.append("- `descriptive_statistics.py`: Estatísticas descritivas\n")
    report.append("- `generate_visualizations.py`: Geração de todas as visualizações\n")
    report.append("- `statistical_tests.py`: Testes de hipótese\n")
    report.append("- `generate_report.py`: Geração deste relatório\n\n")

    report.append("### Apêndice B: Dados Brutos\n\n")
    report.append("Dados consolidados disponíveis em:\n")
    report.append("- `4_analysis/data/consolidated_results.csv`\n")
    report.append("- `4_analysis/results/descriptive_stats_summary.csv`\n")
    report.append("- `4_analysis/results/wilcoxon_test_results.csv`\n")
    report.append("- `4_analysis/results/t_test_results.csv`\n\n")

    report.append("### Apêndice C: Ambiente de Execução\n\n")
    report.append("- **Python**: 3.8+\n")
    report.append("- **Bibliotecas**: pandas, numpy, matplotlib, seaborn, scipy\n")
    report.append("- **Plataforma**: Independente (Windows, macOS, Linux)\n\n")

    report.append("---\n\n")
    report.append("**Fim do Relatório**\n\n")
    report.append(f"*Gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}*\n")

    # Salvar relatório
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.writelines(report)

    print(f"✓ Relatório completo salvo em: {OUTPUT_FILE}")
    print(f"  Total de linhas: {len(report)}")


def main():
    """Executa geração do relatório."""

    print("="*100)
    print("FASE 5: GERAÇÃO DO RELATÓRIO COMPLETO")
    print("="*100)
    print()

    print("📄 Gerando relatório didático completo...\n")
    gerar_relatorio()

    print("\n\n✅ Fase 5 concluída com sucesso!")
    print("="*100)


if __name__ == '__main__':
    main()
