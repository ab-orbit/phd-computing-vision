# Guia Educacional: Redução de Ruído em Imagens Digitais

## 📚 Índice
1. [Introdução ao Ruído em Imagens](#introdução)
2. [Tipos de Ruído](#tipos-de-ruído)
3. [Técnicas Implementadas](#técnicas-implementadas)
4. [Métricas de Avaliação](#métricas)
5. [Comparação de Resultados](#resultados)
6. [Quando Usar Cada Filtro](#recomendações)

---

## 🎯 Introdução

**Ruído em imagens** é uma variação indesejada nos valores de intensidade dos pixels, geralmente causada por:
- Imperfeições nos sensores da câmera
- Condições de iluminação ruins
- Transmissão de dados
- Processos de digitalização

A imagem `fotografo_gonzales.png` apresenta ruído do tipo **sal e pimenta** (salt and pepper noise), caracterizado por pixels aleatórios muito claros (sal) ou muito escuros (pimenta).

---

## 📊 Tipos de Ruído

### 1. Ruído Gaussiano
- **Características**: Distribuição normal (gaussiana) de valores
- **Causa**: Ruído eletrônico dos sensores
- **Aparência**: Granulosidade uniforme

### 2. Ruído Sal e Pimenta
- **Características**: Pixels aleatórios com valores extremos (0 ou 255)
- **Causa**: Erros na transmissão ou leitura de dados
- **Aparência**: Pontos brancos e pretos esparsos
- **Nossa imagem**: Este é o tipo presente!

### 3. Ruído Uniforme
- **Características**: Distribuição uniforme de valores
- **Causa**: Quantização imperfeita

### 4. Ruído Speckle
- **Características**: Multiplicativo, comum em radar/ultrassom
- **Causa**: Interferência de ondas coerentes

---

## 🔧 Técnicas Implementadas

### 1. Filtro de Mediana (Median Filter)

#### Como Funciona
```
Para cada pixel da imagem:
1. Define uma janela (kernel) ao redor do pixel
2. Ordena todos os valores da janela
3. Substitui o pixel pelo valor MEDIANO
```

#### Exemplo Numérico
```
Kernel 3x3:
[120, 122, 255]    Ordenado: [10, 115, 120, 122, 123, 125, 130, 132, 255]
[115, 125, 130]    Mediana = 123
[ 10, 132, 123]    Pixel central ← 123
```

#### Por Que Funciona
- A **mediana** é resistente a valores extremos (outliers)
- Pixels de ruído sal e pimenta (0 ou 255) são ignorados
- **Não usa média**, que seria afetada pelos extremos

#### Vantagens
✅ Excelente para ruído sal e pimenta
✅ Preserva bordas melhor que filtros de média
✅ Não introduz novos valores de intensidade

#### Desvantagens
❌ Pode borrar detalhes finos
❌ Computacionalmente mais caro que média
❌ Pode remover linhas finas

#### Quando Usar
- Ruído impulsivo (sal e pimenta)
- Quando preservação de bordas é importante
- Imagens médicas

#### Código
```python
# Kernel 5x5
filtered = cv2.medianBlur(image, 5)
```

#### Resultado na Nossa Imagem
- **PSNR: 28.68 dB**
- Remove bem os pontos de ruído
- Mantém os contornos do fotógrafo

---

### 2. Filtro Gaussiano (Gaussian Filter)

#### Como Funciona
```
1. Cria um kernel com distribuição gaussiana
2. Convolui o kernel com a imagem
3. Pesos centrais são maiores (suavização ponderada)
```

#### Fórmula Matemática
```
G(x,y) = (1/(2πσ²)) * e^(-(x²+y²)/(2σ²))

Onde:
- σ (sigma) = desvio padrão (controla a largura da gaussiana)
- x, y = distância do centro
```

#### Exemplo de Kernel Gaussiano 3x3 (σ=1.0)
```
[0.075  0.124  0.075]
[0.124  0.204  0.124]
[0.075  0.124  0.075]
```

#### Por Que Funciona
- Suaviza a imagem dando **mais peso aos pixels centrais**
- Pixels vizinhos têm influência proporcional à distância
- Simula um processo de difusão

#### Vantagens
✅ Suavização uniforme
✅ Reduz ruído gaussiano eficientemente
✅ Matematicamente bem fundamentado
✅ Separável (pode ser aplicado em 1D duas vezes)

#### Desvantagens
❌ Borra bordas
❌ Menos efetivo contra ruído sal e pimenta
❌ Pode perder detalhes finos

#### Parâmetros Importantes
- **kernel_size**: Tamanho da janela (deve ser ímpar: 3, 5, 7...)
- **sigma**: Controla o "alcance" da suavização
  - σ pequeno → suavização local
  - σ grande → suavização global

#### Código
```python
# Kernel 5x5, sigma=1.0
filtered = cv2.GaussianBlur(image, (5, 5), 1.0)
```

#### Resultado
- **PSNR: 25.69 dB**
- Suaviza a imagem mas borra detalhes
- Não é ideal para ruído sal e pimenta

---

### 3. Filtro Bilateral (Bilateral Filter)

#### Conceito Revolucionário
**"Suaviza a imagem MAS preserva as bordas!"**

#### Como Funciona
Usa **dois pesos** em vez de um:
1. **Peso Espacial** (como gaussiano): baseado na distância
2. **Peso de Intensidade**: baseado na diferença de cor/intensidade

```
Pixel suavizado = Σ(w_espacial * w_intensidade * pixel_vizinho)
```

#### Matemática Detalhada
```
w_espacial(x,y) = exp(-(x²+y²)/(2*σ_space²))
w_intensidade(I) = exp(-(ΔI²)/(2*σ_color²))

Onde:
- σ_space = controla alcance espacial
- σ_color = controla sensibilidade a diferenças de cor
- ΔI = diferença de intensidade entre pixels
```

#### Exemplo Prático
```
Pixel central: 100
Vizinhos: [100, 102, 180, 98, 101]

Gaussiano normal → média todos (incluindo 180)
Bilateral → ignora 180 (muito diferente) mas usa os outros
```

#### Por Que É Melhor
- **Bordas são áreas de grande mudança de intensidade**
- O filtro bilateral detecta isso e **reduz o peso** dos pixels do outro lado da borda
- Resultado: **suaviza sem borrar bordas**!

#### Vantagens
✅ Preserva bordas perfeitamente
✅ Remove ruído nas áreas homogêneas
✅ Não cria artefatos de halo
✅ Visualmente muito superior

#### Desvantagens
❌ Computacionalmente caro
❌ Não é linear (dificulta análise matemática)
❌ Pode criar efeito "cartoon" se exagerado

#### Parâmetros
- **d**: Diâmetro do pixel neighborhood
- **sigma_color**: Filtro sigma no espaço de cor (75-150 típico)
- **sigma_space**: Filtro sigma no espaço (75-150 típico)

#### Código
```python
filtered = cv2.bilateralFilter(image, d=9,
                               sigmaColor=75,
                               sigmaSpace=75)
```

#### Resultado
- **PSNR: 27.62 dB**
- Excelente preservação de bordas
- Fotógrafo permanece nítido, fundo suavizado

---

### 4. Filtro de Média (Mean Filter)

#### Conceito Mais Simples
**"Substitui cada pixel pela média dos vizinhos"**

#### Como Funciona
```
Kernel 3x3 (todos os pesos iguais):
[1/9  1/9  1/9]
[1/9  1/9  1/9]
[1/9  1/9  1/9]

Novo pixel = soma de todos / 9
```

#### Exemplo
```
Janela:
[120, 122, 125]
[115, 130, 132]
[110, 128, 123]

Média = (120+122+125+115+130+132+110+128+123)/9 = 122.78
```

#### Por Que É Simples
- Todos os vizinhos têm o **mesmo peso**
- Fácil de implementar
- Rápido computacionalmente

#### Vantagens
✅ Muito rápido
✅ Fácil de entender
✅ Reduz ruído gaussiano

#### Desvantagens
❌ Borra MUITO a imagem
❌ Péssimo para ruído sal e pimenta (média é afetada por extremos)
❌ Perde detalhes e bordas

#### Código
```python
kernel = np.ones((5,5), np.float32) / 25
filtered = cv2.filter2D(image, -1, kernel)
```

#### Resultado
- **PSNR: 23.15 dB**
- Muito borrado
- Não recomendado para esta imagem

---

### 5. Filtros Morfológicos

#### Conceito
Operações baseadas em **teoria dos conjuntos** e **morfologia matemática**.

#### 5.1 Abertura Morfológica (Opening)

**Operação**: Erosão seguida de Dilatação

```
1. EROSÃO: Remove pixels brancos nas bordas
   → Remove ruído SAL (pontos brancos)

2. DILATAÇÃO: Expande pixels brancos
   → Restaura tamanho original dos objetos
```

#### Visualização
```
Original:     Após Erosão:    Após Dilatação:
X X X X X     . . . . .       X X X X X
X ■ ■ ■ X  →  . ■ ■ ■ .  →    X ■ ■ ■ X
X ■ ■ ■ X     . ■ ■ ■ .       X ■ ■ ■ X
X X X X X     . . . . .       X X X X X
(X = ruído)   (removido)      (objeto preservado)
```

#### 5.2 Fechamento Morfológico (Closing)

**Operação**: Dilatação seguida de Erosão

```
1. DILATAÇÃO: Expande pixels brancos
   → Preenche buracos (ruído PIMENTA)

2. EROSÃO: Reduz de volta ao tamanho original
```

#### Por Que Funciona
- **Opening**: Remove pequenos objetos brancos (ruído sal)
- **Closing**: Remove pequenos buracos pretos (ruído pimenta)

#### Elemento Estruturante
Define a "forma" da operação:
```python
# Retangular 3x3
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

# Elíptico 5x5
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

# Cruz
kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
```

#### Vantagens
✅ Muito eficaz para ruído binário
✅ Preserva formas estruturais
✅ Rápido

#### Desvantagens
❌ Pode alterar geometria de objetos
❌ Escolha do elemento estruturante é crítica
❌ Funciona melhor em imagens binárias

#### Código
```python
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
opened = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
closed = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
```

#### Resultados
- **Opening PSNR: 23.20 dB**
- **Closing PSNR: 29.68 dB**
- Closing melhor para nossa imagem (remove ruído pimenta)

---

### 6. Non-Local Means (NLM)

#### Conceito Avançado
**"Use padrões similares de TODA a imagem para reduzir ruído"**

#### Como Funciona - Ideia Revolucionária
```
Filtros tradicionais:
- Olham apenas vizinhos PRÓXIMOS
- Pixel (10,10) só usa pixels ao redor de (10,10)

NLM:
- Busca padrões SIMILARES em TODA a imagem
- Se pixel (10,10) é similar a pixel (100,50), usa este para calcular média
- "Não-local" = não usa apenas vizinhança local
```

#### Algoritmo Detalhado
```
Para cada pixel p:
1. Define um patch (janela pequena) ao redor de p
2. Busca patches SIMILARES em toda imagem (ou em janela maior)
3. Calcula peso baseado na similaridade dos patches
4. Média ponderada usando estes pesos

Peso(p,q) = exp(-||Patch(p) - Patch(q)||² / h²)

Onde:
- h = parâmetro de filtragem (controla força)
- ||...|| = norma (diferença entre patches)
```

#### Exemplo Visual
```
Imagem tem textura de grama repetitiva:

Pixel em (10,10):    Patch similar em (150,80):
[50 52 51]           [51 52 50]
[52 48 50]           [53 49 51]
[51 50 49]           [50 51 48]

Similaridade alta → alto peso → usa para suavizar
```

#### Por Que É Superior
- **Preserva texturas**: Pixels com mesma textura se ajudam mutuamente
- **Melhor PSNR**: Usa mais informação da imagem
- **Preserva detalhes**: Não borra padrões estruturados

#### Vantagens
✅ **Melhor PSNR** (35.53 dB - o melhor!)
✅ Preserva texturas
✅ Remove ruído sem borrar
✅ Excelente para imagens naturais

#### Desvantagens
❌ **MUITO lento** (busca em toda imagem)
❌ Parâmetros difíceis de ajustar
❌ Pode criar artefatos em áreas sem padrões

#### Parâmetros
- **h**: Força da filtragem (maior = mais suavização)
- **templateWindowSize**: Tamanho do patch (7x7 típico)
- **searchWindowSize**: Área de busca (21x21 típico)

#### Código
```python
filtered = cv2.fastNlMeansDenoising(
    image,
    None,  # dst
    h=10,  # strength
    templateWindowSize=7,
    searchWindowSize=21
)
```

#### Resultado
- **PSNR: 35.53 dB** ⭐ MELHOR!
- Imagem muito limpa
- Detalhes preservados

---

### 7. Filtro de Mediana Adaptativo

#### Problema do Filtro de Mediana Normal
- **Kernel fixo** não se adapta ao ruído local
- Áreas com pouco ruído → kernel pequeno seria melhor
- Áreas com muito ruído → kernel grande seria melhor

#### Solução: Adaptar o Tamanho do Kernel!

#### Algoritmo
```
Para cada pixel:

ESTÁGIO A: Verifica se mediana é ruído
  A1 = Z_med - Z_min
  A2 = Z_med - Z_max

  Se A1 > 0 E A2 < 0:
    Mediana NÃO é ruído → vai para ESTÁGIO B
  Senão:
    Mediana É ruído → aumenta kernel e repete

ESTÁGIO B: Verifica se pixel atual é ruído
  B1 = Z_xy - Z_min
  B2 = Z_xy - Z_max

  Se B1 > 0 E B2 < 0:
    Pixel NÃO é ruído → mantém valor original
  Senão:
    Pixel É ruído → substitui pela mediana
```

#### Legenda
```
Z_min = mínimo na janela
Z_max = máximo na janela
Z_med = mediana na janela
Z_xy = valor do pixel atual
```

#### Exemplo Numérico
```
Janela 3x3:
[100, 102,   0]  ← 0 é ruído (sal e pimenta)
[101, 105, 103]
[102, 255, 104]  ← 255 é ruído

Ordenado: [0, 100, 101, 102, 103, 104, 105, 255]

Z_min = 0
Z_max = 255
Z_med = (102+103)/2 = 102.5

ESTÁGIO A:
A1 = 102.5 - 0 = 102.5 > 0 ✓
A2 = 102.5 - 255 = -152.5 < 0 ✓
→ Mediana é válida

ESTÁGIO B (para pixel central = 105):
B1 = 105 - 0 = 105 > 0 ✓
B2 = 105 - 255 = -150 < 0 ✓
→ Pixel é válido, mantém 105
```

#### Por Que É Melhor
- **Preserva pixels originais** quando possível
- **Adapta tamanho** à densidade local de ruído
- Menos blur em áreas limpas

#### Vantagens
✅ Preserva detalhes melhor que mediana fixa
✅ Adapta-se a diferentes níveis de ruído
✅ Mantém pixels não-ruidosos

#### Desvantagens
❌ **Muito lento** (tenta múltiplos tamanhos)
❌ Complexo de implementar
❌ Pode falhar em áreas muito ruidosas

#### Código (simplificado)
```python
def adaptive_median(img, max_size=7):
    for pixel in image:
        for k_size in range(3, max_size, 2):
            if median_not_noise(k_size):
                if pixel_not_noise():
                    keep_original()
                else:
                    use_median()
                break
```

#### Resultado
- **PSNR: 14.74 dB** (pior resultado)
- Implementação precisa de otimização
- Teoricamente superior, mas sensível a parâmetros

---

### 8. Filtro Combinado (Pipeline)

#### Filosofia
**"Use forças de múltiplos filtros em sequência"**

#### Pipeline Implementado
```
Imagem Original
    ↓
[1] Mediana 3x3
    ↓ (remove ruído impulsivo)
[2] Bilateral (d=5)
    ↓ (suaviza preservando bordas)
[3] Gaussiano leve 3x3 (σ=0.5)
    ↓ (suavização final sutil)
Imagem Final
```

#### Raciocínio
1. **Primeiro**: Remove ruído sal e pimenta (mediana)
2. **Segundo**: Suaviza mas preserva bordas (bilateral)
3. **Terceiro**: Suavização final muito leve (gaussiano)

#### Por Que Funciona
- Cada filtro resolve um problema específico
- **Sinergia**: Resultado melhor que filtros individuais
- Bilateral funciona melhor após remover ruído impulsivo

#### Vantagens
✅ Combina vantagens de múltiplos métodos
✅ Resultados balanceados
✅ Customizável (pode ajustar pipeline)

#### Desvantagens
❌ Mais lento (múltiplos passes)
❌ Difícil de otimizar parâmetros
❌ Pode sobre-processar

#### Código
```python
# Passo 1: Remove sal e pimenta
step1 = cv2.medianBlur(image, 3)

# Passo 2: Suaviza preservando bordas
step2 = cv2.bilateralFilter(step1, 5, 50, 50)

# Passo 3: Suavização final leve
step3 = cv2.GaussianBlur(step2, (3, 3), 0.5)
```

#### Resultado
- **PSNR: 28.01 dB**
- Bom equilíbrio geral
- Menos artefatos que filtros individuais

---

## 📊 Métricas de Avaliação

### 1. PSNR (Peak Signal-to-Noise Ratio)

#### Fórmula
```
PSNR = 20 * log₁₀(255 / √MSE)

Onde MSE = Mean Squared Error
```

#### O Que Significa
- **Maior é melhor**
- Mede quanto a imagem filtrada difere da original
- **30 dB**: Boa qualidade
- **40+ dB**: Excelente qualidade
- **20 dB**: Qualidade ruim

#### Limitação
- Não correlaciona perfeitamente com percepção humana
- Imagem com PSNR maior pode parecer pior visualmente

### 2. MSE (Mean Squared Error)

#### Fórmula
```
MSE = (1/MN) * Σ(Original[i,j] - Filtrada[i,j])²
```

#### O Que Significa
- **Menor é melhor**
- Média das diferenças quadráticas
- Penaliza grandes erros

### 3. STD (Standard Deviation)

#### O Que Significa
- Desvio padrão dos valores de pixel
- **Menor após filtragem** = mais suavização
- Indica variabilidade de intensidades

---

## 🏆 Comparação de Resultados

### Ranking por PSNR (Melhor para Pior)

| Rank | Filtro | PSNR | Comentário |
|------|--------|------|------------|
| 1 | **NLM** | 35.53 dB | ⭐ Melhor qualidade, preserva detalhes |
| 2 | Median 3x3 | 31.26 dB | Bom para ruído sal e pimenta |
| 3 | Morpho Close | 29.68 dB | Remove ruído pimenta |
| 4 | Median 5x5 | 28.68 dB | Mais suavização que 3x3 |
| 5 | **Combined** | 28.01 dB | Bom equilíbrio |
| 6 | Bilateral | 27.62 dB | Preserva bordas |
| 7 | Gaussian | 25.69 dB | Suavização uniforme |
| 8 | Morpho Open | 23.20 dB | Remove ruído sal |
| 9 | Mean | 23.15 dB | Muito borrado |
| 10 | Adaptive Median | 14.74 dB | Implementação precisa ajuste |

---

## 💡 Recomendações Práticas

### Para Ruído Sal e Pimenta (Nossa Imagem)
```
1ª Escolha: Non-Local Means
- Melhor qualidade (PSNR 35.53 dB)
- Preserva detalhes
- Desvantagem: Lento

2ª Escolha: Median 3x3
- Rápido
- Eficaz (PSNR 31.26 dB)
- Fácil de implementar

3ª Escolha: Combined Pipeline
- Bom balanço
- Menos artefatos
```

### Para Ruído Gaussiano
```
1ª Escolha: Gaussian Filter
2ª Escolha: Bilateral Filter
3ª Escolha: Non-Local Means
```

### Para Preservar Bordas
```
1ª Escolha: Bilateral Filter
2ª Escolha: Non-Local Means
3ª Escolha: Median (melhor que Gaussian)
```

### Para Processamento em Tempo Real
```
1ª Escolha: Median 3x3 (rápido)
2ª Escolha: Gaussian (muito rápido)
Evitar: NLM (muito lento)
```

---

## 🔬 Experimentos Sugeridos

### 1. Variação de Parâmetros
```python
# Teste diferentes tamanhos de kernel
for size in [3, 5, 7, 9]:
    result = cv2.medianBlur(image, size)

# Teste diferentes sigmas
for sigma in [0.5, 1.0, 2.0, 4.0]:
    result = cv2.GaussianBlur(image, (5,5), sigma)
```

### 2. Comparação Visual
- Aplique cada filtro
- Faça zoom em uma região com detalhes
- Compare preservação de bordas

### 3. Métricas Personalizadas
- Implemente SSIM (Structural Similarity)
- Teste com imagens diferentes
- Analise trade-off velocidade vs qualidade

---

## 📚 Referências e Leitura Adicional

### Livros
1. **Gonzalez & Woods** - "Digital Image Processing" (Capítulos 5 e 9)
2. **Pratt** - "Digital Image Processing"

### Papers Importantes
1. **Bilateral Filter**: Tomasi & Manduchi (1998)
2. **Non-Local Means**: Buades et al. (2005)
3. **Adaptive Median**: Hwang & Haddad (1995)

### Tutoriais Online
1. OpenCV Documentation: Smoothing Images
2. SciPy ndimage Tutorial
3. scikit-image Denoising Guide

---

## ✅ Conclusão

### Principais Aprendizados

1. **Não existe filtro universal**
   - Cada tipo de ruído precisa de técnica específica
   - Trade-offs entre velocidade, qualidade e preservação de detalhes

2. **Mediana é rei para sal e pimenta**
   - Resistente a outliers
   - Preserva bordas razoavelmente
   - Rápido e simples

3. **NLM é o estado da arte**
   - Melhor qualidade (quando bem parametrizado)
   - Computacionalmente caro
   - Vale a pena quando qualidade é crítica

4. **Bilateral é o meio termo**
   - Excelente preservação de bordas
   - Razoavelmente rápido
   - Versátil

5. **Pipeline combinado pode ser superior**
   - Aproveita forças de cada método
   - Requer experimentação
   - Resultados mais robustos

### Para Nossa Imagem Específica

**Melhor resultado**: Non-Local Means (35.53 dB PSNR)
- Imagem muito limpa
- Detalhes do fotógrafo preservados
- Ruído sal e pimenta quase completamente removido

**Melhor custo-benefício**: Median 3x3 (31.26 dB PSNR)
- Rápido
- Eficaz
- Simples de implementar

---

*Documento criado para fins educacionais - Visão Computacional 2024*