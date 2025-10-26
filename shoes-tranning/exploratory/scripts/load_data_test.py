"""
Script para testar carregamento do dataset e diagnosticar problemas.

Este script ajuda a identificar e corrigir problemas de parsing no CSV.
"""

import pandas as pd
import warnings
from pathlib import Path

# Suprimir warnings do pandas para output limpo
warnings.filterwarnings('ignore', category=pd.errors.ParserWarning)

# Caminho do dataset
STYLES_CSV = Path("/Users/jwcunha/.cache/kagglehub/datasets/paramaggarwal/fashion-product-images-dataset/versions/1/fashion-dataset/fashion-dataset/styles.csv")

print("=" * 80)
print("TESTE DE CARREGAMENTO DO DATASET")
print("=" * 80)

# Método 1: Carregamento básico com tratamento de erros
print("\n1. Tentando carregamento básico...")
try:
    df = pd.read_csv(STYLES_CSV)
    print(f"   [OK] Sucesso! {len(df):,} registros carregados")
except Exception as e:
    print(f"   [ERRO] {type(e).__name__}")
    print(f"   Mensagem: {str(e)[:100]}...")

# Método 2: Com on_bad_lines='skip'
print("\n2. Tentando com on_bad_lines='skip'...")
try:
    df = pd.read_csv(STYLES_CSV, on_bad_lines='skip')
    print(f"   [OK] Sucesso! {len(df):,} registros carregados")
    print(f"\n   Colunas: {list(df.columns)}")
    print(f"\n   Primeiras linhas:")
    print(df.head(3))
except Exception as e:
    print(f"   [ERRO] {type(e).__name__}")
    print(f"   Mensagem: {str(e)[:100]}...")

# Método 3: Com encoding específico (warnings suprimidos)
print("\n3. Tentando com encoding='utf-8' e on_bad_lines='skip' (silencioso)...")
try:
    df = pd.read_csv(STYLES_CSV, encoding='utf-8', on_bad_lines='skip')
    print(f"   [OK] Sucesso! {len(df):,} registros carregados")
except Exception as e:
    print(f"   [ERRO] {type(e).__name__}")

# Método 4: Identificar linhas problemáticas
print("\n4. Identificando linhas problemáticas...")
try:
    # Ler linha por linha e capturar erros
    problem_lines = []
    with open(STYLES_CSV, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            try:
                # Contar vírgulas (deve ter 9 para 10 colunas)
                comma_count = line.count(',')
                if comma_count != 9:
                    problem_lines.append((i+1, comma_count, line[:100]))
            except Exception as e:
                problem_lines.append((i+1, 'error', str(e)[:100]))

    if problem_lines:
        print(f"   [AVISO] Encontradas {len(problem_lines)} linhas potencialmente problemáticas:")
        for line_num, comma_count, preview in problem_lines[:5]:
            print(f"      Linha {line_num}: {comma_count} vírgulas - {preview}...")
    else:
        print(f"   [OK] Todas as linhas parecem estar corretas!")

except Exception as e:
    print(f"   [ERRO] Erro ao verificar: {e}")

# Método 5: Informações do arquivo
print("\n5. Informações do arquivo:")
print(f"   Tamanho: {STYLES_CSV.stat().st_size / (1024*1024):.2f} MB")

# Contar linhas
with open(STYLES_CSV, 'r') as f:
    line_count = sum(1 for _ in f)
print(f"   Total de linhas: {line_count:,}")

print("\n" + "=" * 80)
print("RECOMENDACAO:")
print("Use: pd.read_csv(STYLES_CSV, on_bad_lines='skip')")
print("Isso ira pular linhas malformadas (se houver) e carregar o resto dos dados.")
print("=" * 80)