# Processamento Digital de Imagens (PDI)
## Redução de Ruído - Material Educacional

Este diretório contém implementações completas e material educacional sobre técnicas de redução de ruído em imagens usando Processamento Digital de Imagens (PDI).

---

## 📁 Estrutura de Arquivos

```
pdi/
├── noise_reduction.py          # Implementação completa de todos os filtros
├── interactive_demo.py          # Demonstração interativa educacional
├── NOISE_REDUCTION_GUIDE.md    # Guia educacional detalhado
├── README.md                    # Este arquivo
└── output/                      # Resultados gerados
    ├── comparison_best_filters.png
    ├── all_filters.png
    ├── median_5x5.png
    ├── bilateral_d9.png
    ├── nlm_h10.png
    └── combined.png
```

---

## 🎯 Objetivo

Implementar e comparar diferentes técnicas de **redução de ruído** usando apenas métodos de **Processamento Digital de Imagens** (sem Machine Learning), aplicados à imagem `fotografo_gonzales.png` que contém ruído do tipo **sal e pimenta**.

---

## 🔧 Técnicas Implementadas

### 1. **Filtro de Mediana**
- ⭐ **Melhor para**: Ruído sal e pimenta
- **PSNR**: 28.68 dB (kernel 5x5)
- **Vantagem**: Preserva bordas, resistente a outliers
- **Como funciona**: Substitui pixel pela mediana da vizinhança

### 2. **Filtro Gaussiano**
- ⭐ **Melhor para**: Ruído gaussiano
- **PSNR**: 25.69 dB
- **Vantagem**: Suavização uniforme
- **Como funciona**: Convolução com kernel gaussiano

### 3. **Filtro Bilateral**
- ⭐ **Melhor para**: Preservar bordas
- **PSNR**: 27.62 dB
- **Vantagem**: Suaviza sem borrar bordas
- **Como funciona**: Combina distância espacial e similaridade de intensidade

### 4. **Filtro de Média**
- ⭐ **Melhor para**: Suavização rápida
- **PSNR**: 23.15 dB
- **Vantagem**: Muito rápido
- **Como funciona**: Média aritmética dos vizinhos

### 5. **Filtros Morfológicos**
- **Opening**: Remove ruído sal - PSNR: 23.20 dB
- **Closing**: Remove ruído pimenta - PSNR: 29.68 dB
- **Como funciona**: Erosão + Dilatação (ou vice-versa)

### 6. **Non-Local Means (NLM)**
- ⭐ **Melhor para**: Máxima qualidade
- **PSNR**: 35.53 dB ⭐ **MELHOR RESULTADO!**
- **Vantagem**: Preserva texturas, resultado superior
- **Desvantagem**: Muito lento
- **Como funciona**: Busca padrões similares em toda a imagem

### 7. **Filtro Adaptativo de Mediana**
- **PSNR**: 14.74 dB (implementação simplificada)
- **Vantagem**: Adapta kernel ao nível local de ruído
- **Como funciona**: Ajusta tamanho do kernel dinamicamente

### 8. **Filtro Combinado (Pipeline)**
- **PSNR**: 28.01 dB
- **Vantagem**: Combina forças de múltiplos filtros
- **Como funciona**: Mediana → Bilateral → Gaussiano leve

---

## 🚀 Como Usar

### Opção 1: Processamento Completo

```bash
# Aplica todos os filtros e gera relatório completo
cd pdi
python noise_reduction.py
```

**Saída**:
- Relatório de métricas no terminal
- Gráficos comparativos salvos em `output/`
- Melhores versões salvas individualmente

### Opção 2: Tutorial Interativo

```bash
# Demonstração educacional com explicações passo a passo
python interactive_demo.py
```

**Recursos**:
- Explicações detalhadas de cada filtro
- Exemplos numéricos
- Visualizações comparativas
- Modo interativo: escolha filtros específicos

---

## 📊 Resultados Obtidos

### Ranking de Qualidade (PSNR)

| Posição | Filtro | PSNR (dB) | Observação |
|---------|--------|-----------|------------|
| 🥇 1º | **Non-Local Means** | **35.53** | Melhor qualidade geral |
| 🥈 2º | Median 3x3 | 31.26 | Excelente para sal e pimenta |
| 🥉 3º | Morphological Closing | 29.68 | Remove ruído pimenta |
| 4º | Median 5x5 | 28.68 | Mais suavização |
| 5º | Combined Pipeline | 28.01 | Bom equilíbrio |
| 6º | Bilateral | 27.62 | Preserva bordas |
| 7º | Gaussian | 25.69 | Suavização geral |
| 8º | Morphological Opening | 23.20 | Remove ruído sal |
| 9º | Mean | 23.15 | Muito borrado |
| 10º | Adaptive Median | 14.74 | Precisa ajustes |

### Comparação Visual

![Comparação dos Melhores Filtros](output/comparison_best_filters.png)

---

## 📚 Material Educacional

### Guia Completo

Consulte **[NOISE_REDUCTION_GUIDE.md](NOISE_REDUCTION_GUIDE.md)** para:

- ✅ Explicação detalhada de cada técnica
- ✅ Exemplos numéricos passo a passo
- ✅ Fórmulas matemáticas
- ✅ Quando usar cada filtro
- ✅ Vantagens e desvantagens
- ✅ Comparações visuais
- ✅ Referências bibliográficas

### Tutorial Interativo

Execute **`interactive_demo.py`** para:

- 🎓 Aprender conceitos com exemplos práticos
- 🔍 Ver efeito de parâmetros em tempo real
- 📊 Comparar filtros lado a lado
- 💡 Entender quando usar cada técnica

---

## 🧮 Métricas Usadas

### PSNR (Peak Signal-to-Noise Ratio)
```
PSNR = 20 * log₁₀(255 / √MSE)
```
- **Maior é melhor**
- 30+ dB = Boa qualidade
- 40+ dB = Excelente qualidade

### MSE (Mean Squared Error)
```
MSE = média((Original - Filtrada)²)
```
- **Menor é melhor**
- Penaliza grandes erros

### STD (Standard Deviation)
- Desvio padrão dos pixels
- Menor após filtragem = mais suavização

---

## 💡 Recomendações Práticas

### Para Nossa Imagem (Ruído Sal e Pimenta)

#### 1ª Escolha: Non-Local Means
```python
filtered = cv2.fastNlMeansDenoising(image, None, h=10, templateWindowSize=7, searchWindowSize=21)
```
✅ Melhor qualidade (PSNR 35.53 dB)
❌ Muito lento

#### 2ª Escolha: Median 3x3
```python
filtered = cv2.medianBlur(image, 3)
```
✅ Rápido e eficaz (PSNR 31.26 dB)
✅ Fácil de implementar

#### 3ª Escolha: Pipeline Combinado
```python
step1 = cv2.medianBlur(image, 3)
step2 = cv2.bilateralFilter(step1, 5, 50, 50)
step3 = cv2.GaussianBlur(step2, (3, 3), 0.5)
```
✅ Bom balanço qualidade/velocidade
✅ Menos artefatos

---

## 🔬 Experimentos Sugeridos

### 1. Variar Parâmetros
```python
# Teste diferentes tamanhos de kernel
for size in [3, 5, 7, 9]:
    result = cv2.medianBlur(image, size)

# Teste diferentes sigmas
for sigma in [0.5, 1.0, 2.0, 4.0]:
    result = cv2.GaussianBlur(image, (5,5), sigma)
```

### 2. Adicionar Seu Próprio Ruído
```python
# Adicione ruído sal e pimenta
def add_salt_pepper(image, amount=0.05):
    noisy = image.copy()
    # Sal (branco)
    salt = np.random.random(image.shape) < amount/2
    noisy[salt] = 255
    # Pimenta (preto)
    pepper = np.random.random(image.shape) < amount/2
    noisy[pepper] = 0
    return noisy

# Teste filtros na imagem com ruído controlado
```

### 3. Comparar com Outras Imagens
```python
# Teste com diferentes tipos de imagens
images = ['paisagem.jpg', 'retrato.jpg', 'texto.jpg']
for img_path in images:
    # Aplicar filtros e comparar resultados
```

---

## 📖 Referências

### Livros
1. **Gonzalez & Woods** - "Digital Image Processing" (4ª ed.)
   - Capítulo 5: Image Enhancement in the Spatial Domain
   - Capítulo 9: Morphological Image Processing

2. **Pratt, William K.** - "Digital Image Processing" (4ª ed.)
   - Capítulo 15: Image Noise Models

### Papers Importantes

1. **Bilateral Filter**
   - Tomasi, C., & Manduchi, R. (1998)
   - "Bilateral filtering for gray and color images"
   - IEEE ICCV

2. **Non-Local Means**
   - Buades, A., Coll, B., & Morel, J. M. (2005)
   - "A non-local algorithm for image denoising"
   - IEEE CVPR

3. **Adaptive Median Filter**
   - Hwang, H., & Haddad, R. A. (1995)
   - "Adaptive median filters: new algorithms and results"
   - IEEE TIP

### Documentação Online
- [OpenCV: Smoothing Images](https://docs.opencv.org/master/d4/d13/tutorial_py_filtering.html)
- [SciPy ndimage](https://docs.scipy.org/doc/scipy/reference/ndimage.html)
- [scikit-image Denoising](https://scikit-image.org/docs/stable/auto_examples/filters/plot_denoise.html)

---

## 🎓 Conceitos Aprendidos

### 1. Tipos de Ruído
- Ruído Sal e Pimenta (impulse noise)
- Ruído Gaussiano (electronic noise)
- Ruído Uniforme
- Ruído Speckle

### 2. Técnicas de Filtragem
- **Domínio Espacial**: Mediana, Média, Bilateral
- **Morfológicas**: Erosão, Dilatação, Opening, Closing
- **Avançadas**: Non-Local Means, Adaptativas

### 3. Trade-offs
- **Velocidade vs Qualidade**: NLM (lento mas melhor) vs Mediana (rápido)
- **Suavização vs Detalhes**: Bilateral preserva bordas
- **Generalidade vs Especialização**: Mediana para sal e pimenta

### 4. Métricas de Avaliação
- PSNR, MSE, MAE
- Importância da avaliação visual
- Limitações de métricas automáticas

---

## 🛠️ Requisitos

```bash
pip install opencv-python numpy scipy matplotlib scikit-image seaborn
```

---

## 📝 Para Estudantes

Este material foi criado com fins educacionais. Use-o para:

1. **Entender** os fundamentos de cada técnica
2. **Experimentar** com diferentes parâmetros
3. **Comparar** resultados quantitativamente
4. **Implementar** suas próprias variações
5. **Aplicar** em seus projetos

### Exercícios Propostos

1. Implemente um filtro de Wiener
2. Compare PSNR com SSIM (Structural Similarity)
3. Crie um filtro híbrido próprio
4. Teste em imagens coloridas (RGB)
5. Otimize o filtro adaptativo de mediana

---

## 📧 Contato e Contribuições

Este é um projeto educacional. Sugestões e melhorias são bem-vindas!

---

## 📜 Licença

Material educacional - Uso livre para fins acadêmicos

---

**Última atualização**: Outubro 2024
**Disciplina**: Visão Computacional
**Projeto**: Processamento Digital de Imagens - Redução de Ruído