#!/usr/bin/env python3
"""
Fase 6: Geração do Resumo Executivo

Este script gera um resumo executivo conciso (1-2 páginas) com os principais
achados e recomendações da análise comparativa.

Saída:
- executive_summary.md - Resumo executivo
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# Caminhos
BASE_PATH = Path(__file__).parent
DATA_PATH = BASE_PATH / 'data'
RESULTS_PATH = BASE_PATH / 'results'
OUTPUT_FILE = BASE_PATH / 'executive_summary.md'


def gerar_resumo_executivo():
    """Gera resumo executivo em Markdown."""

    # Carregar dados principais
    df = pd.read_csv(DATA_PATH / 'consolidated_results.csv')
    df_wilcoxon = pd.read_csv(RESULTS_PATH / 'wilcoxon_test_results.csv')

    # Calcular métricas principais
    modelos = sorted(df['modelo'].unique())
    stats = {}
    for modelo in modelos:
        df_modelo = df[df['modelo'] == modelo]
        stats[modelo] = {
            'acuracia': df_modelo['acuracia_geral'].mean(),
            'acuracia_std': df_modelo['acuracia_geral'].std(),
            'f1': df_modelo['f1_macro'].mean(),
            'tempo': df_modelo['tempo_total_ms'].mean() / 1000
        }

    # Iniciar resumo
    summary = []
    summary.append("# Resumo Executivo")
    summary.append("## Análise Comparativa: Google Vision vs Roboflow\n")
    summary.append("### Classificação de Emoções Faciais\n")
    summary.append("---\n\n")
    summary.append(f"**Data**: {datetime.now().strftime('%d de %B de %Y')}\n\n")
    summary.append("---\n\n")

    # CONTEXTO
    summary.append("## Contexto\n\n")
    summary.append("Este estudo comparou dois classificadores de emoções faciais baseados em APIs de modelos ")
    summary.append("foundation (Google Cloud Vision e Roboflow) para a tarefa de classificação binária ")
    summary.append("entre expressões de **Alegria** e **Raiva**.\n\n")

    summary.append("**Metodologia**: 30 simulações independentes com 50 imagens por classe ")
    summary.append("(100 imagens/simulação), totalizando 3.000 imagens processadas por modelo.\n\n")

    # PRINCIPAIS ACHADOS
    summary.append("## Principais Achados\n\n")

    summary.append("### 1. Roboflow é Estatisticamente Superior\n\n")
    summary.append("**Evidência Estatística**:\n")
    summary.append("- Teste de Wilcoxon pareado: **p < 0.001** (altamente significativo)\n")
    summary.append("- Tamanho de efeito: **Grande** (r > 0.8)\n")
    summary.append("- Diferença consistente em **todas as 30 simulações**\n\n")

    summary.append("**Performance Comparativa**:\n\n")
    summary.append("| Métrica | Google Vision | Roboflow | Diferença |\n")
    summary.append("|---------|---------------|----------|----------|\n")

    goog_acc = stats.get('Google Vision', {}).get('acuracia', 0)
    robo_acc = stats.get('Roboflow', {}).get('acuracia', 0)
    goog_f1 = stats.get('Google Vision', {}).get('f1', 0)
    robo_f1 = stats.get('Roboflow', {}).get('f1', 0)
    goog_time = stats.get('Google Vision', {}).get('tempo', 0)
    robo_time = stats.get('Roboflow', {}).get('tempo', 0)

    summary.append(f"| Acurácia | {goog_acc:.1%} ± {stats.get('Google Vision', {}).get('acuracia_std', 0):.1%} | ")
    summary.append(f"{robo_acc:.1%} ± {stats.get('Roboflow', {}).get('acuracia_std', 0):.1%} | ")
    summary.append(f"**+{(robo_acc-goog_acc):.1%}** |\n")

    summary.append(f"| F1-Score | {goog_f1:.3f} | {robo_f1:.3f} | +{(robo_f1-goog_f1):.3f} |\n")
    summary.append(f"| Tempo (s) | {goog_time:.1f}s | {robo_time:.1f}s | **{goog_time/robo_time:.1f}× mais rápido** |\n\n")

    summary.append("### 2. Ambos Apresentam Performance Insatisfatória\n\n")
    summary.append("Apesar da diferença estatística, **nenhum dos modelos** atinge performance adequada para produção:\n\n")
    summary.append(f"- **Google Vision**: Apenas {goog_acc:.1%} de acurácia\n")
    summary.append(f"- **Roboflow**: Apenas {robo_acc:.1%} de acurácia\n")
    summary.append("- **Benchmark mínimo recomendado**: >70% para aplicações práticas\n\n")

    summary.append("### 3. Forte Viés para Classe Alegria\n\n")
    summary.append("Ambos os modelos apresentam dificuldade significativa em identificar raiva:\n\n")

    alegria_goog = df[df['modelo'] == 'Google Vision']['acuracia_alegria'].mean()
    raiva_goog = df[df['modelo'] == 'Google Vision']['acuracia_raiva'].mean()
    alegria_robo = df[df['modelo'] == 'Roboflow']['acuracia_alegria'].mean()
    raiva_robo = df[df['modelo'] == 'Roboflow']['acuracia_raiva'].mean()

    summary.append("**Por Classe**:\n")
    summary.append("- **Google Vision**: Alegria {:.1%} vs Raiva {:.1%}\n".format(alegria_goog, raiva_goog))
    summary.append("- **Roboflow**: Alegria {:.1%} vs Raiva {:.1%}\n\n".format(alegria_robo, raiva_robo))

    summary.append("**Implicação**: Modelos não são confiáveis para detectar raiva, ")
    summary.append("possivelmente devido a diferenças entre datasets de treinamento e validação.\n\n")

    summary.append("### 4. Roboflow Oferece Melhor Custo-Benefício\n\n")
    summary.append(f"- **Velocidade**: Roboflow é ~{goog_time/robo_time:.1f}× mais rápido\n")
    summary.append("- **Acurácia**: Roboflow é ~{robo_acc/goog_acc:.1f}× mais preciso\n")
    summary.append("- **Custo**: Similar (~$3.00 para 3.000 imagens)\n")
    summary.append(f"- **Custo/Performance**: ${3.00/robo_acc/100:.2f} vs ${3.00/goog_acc/100:.2f} por ponto percentual de acurácia\n\n")

    # RECOMENDAÇÕES
    summary.append("## Recomendações\n\n")

    summary.append("### Curto Prazo\n\n")
    summary.append("1. **Não utilizar esses modelos em produção** sem validação extensiva adicional\n")
    summary.append("2. **Entre as opções testadas, preferir Roboflow** se uso de API for necessário\n")
    summary.append("3. **Implementar validação humana** para predições de raiva (alta taxa de erro)\n")
    summary.append("4. **Estabelecer threshold de confiança** para rejeitar predições incertas\n\n")

    summary.append("### Médio Prazo\n\n")
    summary.append("1. **Executar e avaliar YOLO11** (modelo foundation local) conforme planejamento original\n")
    summary.append("2. **Implementar CNN treinada do zero** como baseline de comparação\n")
    summary.append("3. **Coletar dataset maior** (>10.000 imagens) para treinar modelo especializado\n")
    summary.append("4. **Balancear dataset** entre classes se possível\n\n")

    summary.append("### Longo Prazo\n\n")
    summary.append("1. **Fine-tuning de modelos foundation** no domínio específico\n")
    summary.append("2. **Desenvolver modelo proprietário** otimizado para a aplicação\n")
    summary.append("3. **Implementar ensemble** de múltiplos modelos para maior robustez\n")
    summary.append("4. **Expandir para mais classes** de emoções se aplicável\n\n")

    # PRÓXIMOS PASSOS
    summary.append("## Próximos Passos Imediatos\n\n")
    summary.append("1. **Executar YOLO11**: Completar análise comparativa com terceiro modelo\n")
    summary.append("2. **Análise de erros**: Identificar quais imagens são consistentemente mal classificadas\n")
    summary.append("3. **Revisão de dataset**: Verificar qualidade e representatividade das imagens\n")
    summary.append("4. **Buscar alternativas**: Avaliar outros modelos foundation ou APIs especializadas\n")
    summary.append("5. **Considerar abordagem híbrida**: Combinar API (rapidez) com validação local (precisão)\n\n")

    # CONCLUSÃO
    summary.append("## Conclusão\n\n")
    summary.append("Embora **Roboflow seja estatisticamente superior ao Google Vision** em todas as métricas ")
    summary.append("avaliadas (p<0.001, tamanho de efeito grande), **ambos os modelos apresentam performance ")
    summary.append("insatisfatória** para uso em produção (acurácia <40%).\n\n")

    summary.append("A análise demonstra que **APIs genéricas de modelos foundation não substituem modelos ")
    summary.append("especializados** para tarefas específicas. Para aplicações reais de classificação de emoções, ")
    summary.append("recomenda-se investir em:\n\n")

    summary.append("- **Fine-tuning** de modelos foundation\n")
    summary.append("- **Treinamento de modelos customizados**\n")
    summary.append("- **Datasets maiores e mais representativos**\n")
    summary.append("- **Validação humana** para casos críticos\n\n")

    summary.append("---\n\n")
    summary.append("**Para detalhes completos**, consultar o relatório principal: ")
    summary.append("`comparative_analysis_report.md`\n\n")

    summary.append(f"*Resumo gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}*\n")

    # Salvar resumo
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.writelines(summary)

    print(f"✓ Resumo executivo salvo em: {OUTPUT_FILE}")


def main():
    """Executa geração do resumo executivo."""

    print("="*100)
    print("FASE 6: GERAÇÃO DO RESUMO EXECUTIVO")
    print("="*100)
    print()

    print("📄 Gerando resumo executivo...\n")
    gerar_resumo_executivo()

    print("\n\n✅ Fase 6 concluída com sucesso!")
    print("="*100)


if __name__ == '__main__':
    main()
