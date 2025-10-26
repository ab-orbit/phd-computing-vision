# Troubleshooting - Dataset Loading Issues

## Problema Identificado: ParserError ao Carregar CSV

### Sintoma
```
ParserError: Error tokenizing data. C error: Expected 10 fields in line 6044, saw 11
```

### Causa Raiz
O arquivo `styles.csv` contém **22 linhas malformadas** (de um total de 44,447 linhas).

Estas linhas têm vírgulas extras no campo `productDisplayName`, o que confunde o parser do pandas:

**Exemplos de linhas problemáticas**:
- Linha 6044: "Boss Men Perfume, After Shave" (vírgula extra no nome)
- Linha 6569: "Myntra Men's Yes, its all about me White T-shirt"
- Linha 7399: "Turtle Men Formal Pink Tie, Cufflinks and Pocket Square Set"

### Impacto
- **Total de linhas**: 44,447
- **Linhas problemáticas**: 22 (0.05%)
- **Registros carregados com sucesso**: 44,424 (99.95%)
- **Impacto negligível**: Perda de apenas 0.05% dos dados

### Solução ✅

Use o parâmetro `on_bad_lines='skip'` ao carregar o CSV:

```python
import pandas as pd

# Solução recomendada
df = pd.read_csv('styles.csv', on_bad_lines='skip')

# Com avisos (para debug)
df = pd.read_csv('styles.csv', on_bad_lines='warn')
```

### Implementação no Notebook

O notebook `01_initial_eda.ipynb` foi atualizado com tratamento robusto de erros:

```python
# Carregar CSV com tratamento de erros
print("Carregando dataset...")
try:
    df_styles = pd.read_csv(STYLES_CSV, encoding='utf-8', on_bad_lines='skip')
    print(f"✓ CSV carregado com sucesso!")
except Exception as e:
    print(f"⚠️  Erro com UTF-8, tentando encoding alternativo...")
    df_styles = pd.read_csv(STYLES_CSV, encoding='latin1', on_bad_lines='skip')
    print(f"✓ CSV carregado com encoding alternativo!")

print(f"\nTotal de produtos: {len(df_styles):,}")
```

### Script de Diagnóstico

Um script de diagnóstico completo está disponível:

```bash
cd exploratory/scripts
python load_data_test.py
```

Este script:
- Testa múltiplos métodos de carregamento
- Identifica linhas problemáticas específicas
- Fornece recomendações

### Linhas Afetadas

Lista completa das 22 linhas com problemas:
```
6044, 6569, 7399, 7939, 9026, 10264, 10427, 10905,
11373, 11945, 14112, 14532, 15076, 29906, 31625, 33020,
35748, 35962, 37770, 38105, 38275, 38404
```

### Alternativas

#### Opção 1: Carregar e Pular (Recomendado)
```python
df = pd.read_csv('styles.csv', on_bad_lines='skip')
# Resultado: 44,424 registros (99.95% dos dados)
```

#### Opção 2: Carregar com Avisos
```python
df = pd.read_csv('styles.csv', on_bad_lines='warn')
# Mostra quais linhas foram puladas
```

#### Opção 3: Engine Python (Mais Lento, Mais Tolerante)
```python
df = pd.read_csv('styles.csv', engine='python', on_bad_lines='skip')
# Usa parser Python em vez de C (mais lento mas mais robusto)
```

#### Opção 4: Corrigir o CSV (Não Recomendado)
Você poderia limpar o CSV manualmente, mas não é necessário dado o baixo impacto.

## Verificação Rápida

Para verificar se o carregamento foi bem-sucedido:

```python
import pandas as pd

df = pd.read_csv('styles.csv', on_bad_lines='skip')

print(f"Registros carregados: {len(df):,}")
print(f"Colunas: {list(df.columns)}")
print(f"Valores faltantes: {df.isnull().sum().sum()}")

# Esperado:
# Registros carregados: 44,424
# Colunas: ['id', 'gender', 'masterCategory', 'subCategory',
#           'articleType', 'baseColour', 'season', 'year',
#           'usage', 'productDisplayName']
# Valores faltantes: baixo número
```

## Conclusão

✅ **Solução Implementada**: Notebook atualizado com `on_bad_lines='skip'`
✅ **Impacto**: Negligível (0.05% de perda de dados)
✅ **Status**: Problema resolvido

A perda de 22 produtos de um total de 44,447 (0.05%) é aceitável e não afeta a qualidade da análise ou do treinamento de modelos.

---

**Data**: 2025-10-26
**Status**: ✅ Resolvido