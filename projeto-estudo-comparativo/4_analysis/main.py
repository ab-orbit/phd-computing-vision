import os
import glob
import pandas as pd
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def analise_wilcoxon_pareado(coluna, p, indicador):
    dados = np.column_stack((dfRoboflowEmotion[coluna].values, dfGemini[coluna].values))

    try:
        df = pd.DataFrame(dados)
    except Exception as e:
        print(f"Erro ao converter os dados para DataFrame: {e}")
        return None
        
    if df.shape[1] < 2:
        print(f"Aviso: Os dados de '{indicador}' têm menos de 2 colunas. Ignorado.")
        return None
            
    amostra1 = df.iloc[:, 0].dropna()
    amostra2 = df.iloc[:, 1].dropna()
        
    if len(amostra1) != len(amostra2) or len(amostra1) < 5: 
         print(f"Aviso: Os dados de '{indicador}' não possuem amostras pareadas válidas (tamanhos diferentes ou insuficientes, min 5). Ignorado.")
         return None

    diferencas = amostra1 - amostra2
        
    mediana = diferencas.median()
    media = diferencas.mean()
    desvio_padrao = diferencas.std()

    if diferencas.abs().sum() == 0:
        p_valor = 1.0
        resultado_teste = "Não se rejeita H0 (Sem diferença significativa - Dados idênticos)"
    else:
        stat, p_valor = stats.wilcoxon(amostra1, amostra2, alternative='two-sided')
        resultado_teste = "Rejeita-se H0 (Diferença significativa)" if p_valor < p else "Não se rejeita H0 (Sem diferença significativa)"

    return {
        'Indicador': indicador, 
        'mediana da diferença': mediana,
        'media da diferença': media,
        'desvio padrão da diferença': desvio_padrao,
        'p-valor de Wilcoxon': p_valor,
        'Resultado do Teste': resultado_teste
    }

def boxplot_comparativo():
    data1 = dfGemini['acuracia_alegria'].dropna()
    data2 = dfRoboflowEmotion['acuracia_alegria'].dropna()
    data3 = dfGemini['acuracia_raiva'].dropna()
    data4 = dfRoboflowEmotion['acuracia_raiva'].dropna()

    df_plot = pd.DataFrame({
        'Gemini Alegria': data1.reset_index(drop=True),
        'Yolo Alegria': data2.reset_index(drop=True),
        'Gemini Raiva': data3.reset_index(drop=True),
        'Yolo Raiva': data4.reset_index(drop=True)
    })
    
    plt.figure(figsize=(10, 7))
    
    sns.boxplot(data=df_plot, palette='Pastel1', width=0.5)
    
    plt.title('Comparativo Gemini x Yolo', fontsize=16)
    plt.xlabel('Fonte dos Dados e Emoção', fontsize=12)
    plt.ylabel('Acurácia', fontsize=12)
    plt.xticks(rotation=15, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    return plt

def salvar_df_como_imagem(df, nome_arquivo="tabela_resultado.png", titulo="Resultado do Teste Wilcoxon"):
    fig, ax = plt.subplots(figsize=(15, 3)) 
    
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.set_frame_on(False) 
    
    tabela = ax.table(cellText=df.values, 
                      colLabels=df.columns, 
                      loc='center', 
                      cellLoc='center')

    tabela.auto_set_column_width(col=list(range(len(df.columns))))
    
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(10)
    
    tabela.scale(1.0, 1.5) 

    ax.set_title(titulo, fontsize=14, pad=20, fontweight='bold')
    
    for key, cell in tabela.get_celld().items():
        if key[0] == 0:
            cell.get_text().set_weight('bold')
    
    plt.savefig(nome_arquivo, bbox_inches='tight', dpi=300)
    plt.close(fig) 
    print(f"Tabela salva como imagem: {nome_arquivo}")


dfRoboflowEmotion = pd.read_csv('3_simulation/results/roboflow_emotion/results.csv')
dfGemini = pd.read_csv('3_simulation/results/google_vision_emotion/results.csv')
p = 0.05

print('[dfPlot]------------------------------------------------------------------------------------')
dfPlot = pd.DataFrame(
        [
            analise_wilcoxon_pareado('acuracia_geral', p, 'Acurácia'),
            analise_wilcoxon_pareado('precisao_macro', p, 'Precisão'),
            analise_wilcoxon_pareado('recall_macro', p, 'Recall'),
            analise_wilcoxon_pareado('f1_macro', p, 'F1-Score'),
            analise_wilcoxon_pareado('total_alegria', p, 'Alegria'),
            analise_wilcoxon_pareado('total_raiva', p, 'Raiva')
        ]
    )
print(dfPlot)
print('------------------------------------------------------------------------------------')

salvar_df_como_imagem(
    dfPlot,
    "4_analysis/figures/wilcoxon_gemini_vs_yolo.png",
    "Teste de Wilcoxon Pareado (Gemini vs Yolo)"
)

boxPlot = boxplot_comparativo()
boxPlot.savefig('4_analysis/figures/boxploy_comparativo_gemini_vs_yolo.png')
boxPlot.show()
