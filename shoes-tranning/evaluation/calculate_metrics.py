"""
Script para calcular métricas automáticas de qualidade de imagens geradas.

Este script implementa duas métricas principais:
1. FID (Fréchet Inception Distance): Mede a qualidade e diversidade das imagens geradas
   comparando a distribuição de features entre imagens reais e geradas usando Inception v3.

2. CLIP Score: Mede a correspondência semântica entre os prompts de texto e as imagens geradas
   usando o modelo CLIP (Contrastive Language-Image Pre-training).

Explicação das Métricas:

FID (Fréchet Inception Distance):
- Valores mais baixos indicam melhor qualidade (0 = idêntico ao real)
- Compara estatísticas de features extraídas de um modelo Inception pré-treinado
- Mede tanto qualidade quanto diversidade das imagens geradas
- Tipicamente: FID < 10 = excelente, FID < 50 = bom, FID > 100 = ruim

CLIP Score:
- Valores mais altos indicam melhor alinhamento texto-imagem (0-100)
- Mede quão bem a imagem corresponde ao prompt de entrada
- Usa o modelo CLIP para embeddings multimodais
- Tipicamente: CLIP > 30 = excelente, CLIP > 25 = bom, CLIP < 20 = ruim

Uso:
    python calculate_metrics.py --real_images_dir ../data/casual_shoes/train/images \
                                --generated_images_dir ../api/generated_images \
                                --prompts_file prompts.json \
                                --output_file metrics_results.json
"""

import torch
import torch.nn as nn
import numpy as np
from PIL import Image
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from tqdm import tqdm
import warnings

# Importações para FID
from torchvision import transforms
from torchvision.models import inception_v3
from scipy import linalg

# CLIP Score importado dinamicamente quando necessário

warnings.filterwarnings('ignore')


class InceptionFeatureExtractor:
    """
    Extrator de features usando Inception v3 para cálculo de FID.

    O modelo Inception v3 é usado porque:
    1. Foi treinado em ImageNet com milhões de imagens
    2. Aprende features robustas e generalizáveis
    3. É o padrão de facto para calcular FID

    Usamos a camada antes da classificação final (pool3) que produz
    features de 2048 dimensões para cada imagem.
    """

    def __init__(self, device='cuda' if torch.cuda.is_available() else 'cpu'):
        """
        Inicializa o modelo Inception v3.

        Args:
            device: Dispositivo para executar o modelo ('cuda', 'mps', ou 'cpu')
        """
        self.device = device

        # Carrega Inception v3 pré-treinado
        # transform_input=False porque faremos nossa própria normalização
        self.model = inception_v3(pretrained=True, transform_input=False)
        self.model.fc = nn.Identity()  # Remove a camada de classificação final
        self.model.eval()
        self.model.to(device)

        # Transformações de pré-processamento para Inception v3
        # As imagens devem ser 299x299 e normalizadas com média e desvio padrão do ImageNet
        self.transform = transforms.Compose([
            transforms.Resize(299),
            transforms.CenterCrop(299),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])

    def extract_features(self, image_paths: List[Path], batch_size: int = 32) -> np.ndarray:
        """
        Extrai features de um conjunto de imagens.

        Args:
            image_paths: Lista de caminhos para as imagens
            batch_size: Número de imagens processadas por vez

        Returns:
            Array numpy com shape (n_images, 2048) contendo as features
        """
        features = []

        with torch.no_grad():
            for i in tqdm(range(0, len(image_paths), batch_size), desc="Extraindo features"):
                batch_paths = image_paths[i:i + batch_size]
                batch_images = []

                for img_path in batch_paths:
                    try:
                        img = Image.open(img_path).convert('RGB')
                        img_tensor = self.transform(img)
                        batch_images.append(img_tensor)
                    except Exception as e:
                        print(f"Erro ao processar {img_path}: {e}")
                        continue

                if batch_images:
                    batch_tensor = torch.stack(batch_images).to(self.device)
                    batch_features = self.model(batch_tensor)
                    features.append(batch_features.cpu().numpy())

        return np.concatenate(features, axis=0)


def calculate_fid(real_features: np.ndarray, generated_features: np.ndarray) -> float:
    """
    Calcula o FID (Fréchet Inception Distance) entre duas distribuições de features.

    O FID mede a distância entre duas distribuições gaussianas multivariadas
    usando a distância de Fréchet (também conhecida como distância de Wasserstein-2).

    Fórmula:
    FID = ||μ_real - μ_gen||² + Tr(Σ_real + Σ_gen - 2√(Σ_real · Σ_gen))

    onde:
    - μ_real, μ_gen são as médias das features reais e geradas
    - Σ_real, Σ_gen são as matrizes de covariância
    - Tr é o traço da matriz

    Args:
        real_features: Features extraídas das imagens reais (n_real, 2048)
        generated_features: Features extraídas das imagens geradas (n_gen, 2048)

    Returns:
        Valor do FID (quanto menor, melhor)
    """
    # Calcula média e covariância das features reais
    mu_real = np.mean(real_features, axis=0)
    sigma_real = np.cov(real_features, rowvar=False)

    # Calcula média e covariância das features geradas
    mu_gen = np.mean(generated_features, axis=0)
    sigma_gen = np.cov(generated_features, rowvar=False)

    # Calcula a diferença entre as médias
    diff = mu_real - mu_gen

    # Calcula o produto das matrizes de covariância
    # Usa sqrt da matriz para estabilidade numérica
    covmean, _ = linalg.sqrtm(sigma_real.dot(sigma_gen), disp=False)

    # Verifica se há valores complexos devido a erros numéricos
    if np.iscomplexobj(covmean):
        covmean = covmean.real

    # Calcula o FID usando a fórmula da distância de Fréchet
    fid = diff.dot(diff) + np.trace(sigma_real + sigma_gen - 2 * covmean)

    return float(fid)


class CLIPScoreCalculator:
    """
    Calculador de CLIP Score para medir alinhamento texto-imagem.

    CLIP (Contrastive Language-Image Pre-training) é um modelo que aprende
    representações visuais a partir de supervisão de linguagem natural.

    O CLIP Score mede a similaridade coseno entre:
    - Embedding da imagem gerada
    - Embedding do prompt de texto usado para gerar a imagem

    Valores mais altos indicam maior alinhamento semântico.
    """

    def __init__(self, device='cuda' if torch.cuda.is_available() else 'cpu',
                 model_name: str = 'ViT-B/32'):
        """
        Inicializa o modelo CLIP.

        Args:
            device: Dispositivo para executar o modelo
            model_name: Nome do modelo CLIP a usar. Opções:
                       - 'RN50': ResNet-50
                       - 'RN101': ResNet-101
                       - 'ViT-B/32': Vision Transformer (padrão, bom equilíbrio)
                       - 'ViT-B/16': Vision Transformer maior (mais preciso, mais lento)
        """
        # Importa CLIP dinamicamente
        try:
            import clip
        except ImportError:
            raise ImportError(
                "CLIP não está instalado. Instale com: "
                "pip install git+https://github.com/openai/CLIP.git"
            )

        self.device = device
        self.clip = clip
        self.model, self.preprocess = clip.load(model_name, device=device)
        self.model.eval()

    def calculate_score(self, image_path: Path, prompt: str) -> float:
        """
        Calcula CLIP Score para uma única imagem e seu prompt.

        Args:
            image_path: Caminho para a imagem gerada
            prompt: Texto do prompt usado para gerar a imagem

        Returns:
            CLIP Score (0-100, valores maiores = melhor alinhamento)
        """
        try:
            # Processa a imagem
            image = Image.open(image_path).convert('RGB')
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)

            # Processa o texto
            text_input = self.clip.tokenize([prompt]).to(self.device)

            # Calcula embeddings
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                text_features = self.model.encode_text(text_input)

                # Normaliza os features para cálculo de similaridade coseno
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)

                # Calcula similaridade coseno e converte para score (0-100)
                similarity = (image_features @ text_features.T).item()
                score = max(0, similarity * 100)  # Multiplica por 100 para escala 0-100

            return score

        except Exception as e:
            print(f"Erro ao calcular CLIP Score para {image_path}: {e}")
            return 0.0

    def calculate_batch_scores(self, image_prompt_pairs: List[Tuple[Path, str]]) -> Dict[str, float]:
        """
        Calcula CLIP Scores para múltiplas imagens.

        Args:
            image_prompt_pairs: Lista de tuplas (caminho_imagem, prompt)

        Returns:
            Dicionário com estatísticas:
            - mean: Média dos scores
            - std: Desvio padrão
            - min: Score mínimo
            - max: Score máximo
            - individual_scores: Lista de scores individuais
        """
        scores = []

        for img_path, prompt in tqdm(image_prompt_pairs, desc="Calculando CLIP Scores"):
            score = self.calculate_score(img_path, prompt)
            scores.append(score)

        return {
            'mean': float(np.mean(scores)),
            'std': float(np.std(scores)),
            'min': float(np.min(scores)),
            'max': float(np.max(scores)),
            'median': float(np.median(scores)),
            'individual_scores': scores
        }


def load_prompts_from_json(prompts_file: Path) -> Dict[str, str]:
    """
    Carrega prompts de um arquivo JSON.

    Formato esperado:
    {
        "image_name.png": "prompt text",
        ...
    }

    Args:
        prompts_file: Caminho para o arquivo JSON com prompts

    Returns:
        Dicionário mapeando nomes de arquivo para prompts
    """
    with open(prompts_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_image_paths(directory: Path, extensions: List[str] = ['.png', '.jpg', '.jpeg']) -> List[Path]:
    """
    Obtém todos os caminhos de imagens em um diretório.

    Args:
        directory: Diretório para buscar imagens
        extensions: Lista de extensões válidas

    Returns:
        Lista de caminhos para imagens
    """
    image_paths = []
    for ext in extensions:
        image_paths.extend(directory.glob(f'*{ext}'))
        image_paths.extend(directory.glob(f'*{ext.upper()}'))
    return sorted(image_paths)


def main():
    """
    Função principal que orquestra o cálculo das métricas.
    """
    parser = argparse.ArgumentParser(
        description='Calcula métricas de qualidade (FID e CLIP Score) para imagens geradas'
    )

    parser.add_argument(
        '--real_images_dir',
        type=str,
        required=True,
        help='Diretório contendo imagens reais (dataset original)'
    )

    parser.add_argument(
        '--generated_images_dir',
        type=str,
        required=True,
        help='Diretório contendo imagens geradas pelo modelo'
    )

    parser.add_argument(
        '--prompts_file',
        type=str,
        default=None,
        help='Arquivo JSON com prompts (necessário para CLIP Score). Formato: {"image.png": "prompt"}'
    )

    parser.add_argument(
        '--output_file',
        type=str,
        default='metrics_results.json',
        help='Arquivo de saída para salvar os resultados (JSON)'
    )

    parser.add_argument(
        '--batch_size',
        type=int,
        default=32,
        help='Tamanho do batch para processamento de imagens'
    )

    parser.add_argument(
        '--device',
        type=str,
        default='auto',
        choices=['auto', 'cuda', 'mps', 'cpu'],
        help='Dispositivo para executar os modelos (auto detecta automaticamente)'
    )

    parser.add_argument(
        '--skip_fid',
        action='store_true',
        help='Pula o cálculo do FID (útil se só quiser CLIP Score)'
    )

    parser.add_argument(
        '--skip_clip',
        action='store_true',
        help='Pula o cálculo do CLIP Score (útil se só quiser FID)'
    )

    args = parser.parse_args()

    # Converte para Path objects
    real_images_dir = Path(args.real_images_dir)
    generated_images_dir = Path(args.generated_images_dir)
    output_file = Path(args.output_file)

    # Valida diretórios
    if not real_images_dir.exists():
        raise ValueError(f"Diretório de imagens reais não encontrado: {real_images_dir}")

    if not generated_images_dir.exists():
        raise ValueError(f"Diretório de imagens geradas não encontrado: {generated_images_dir}")

    # Detecta dispositivo
    if args.device == 'auto':
        if torch.cuda.is_available():
            device = 'cuda'
        elif torch.backends.mps.is_available():
            device = 'mps'
        else:
            device = 'cpu'
    else:
        device = args.device

    print(f"\nUsando dispositivo: {device}")
    print(f"Imagens reais: {real_images_dir}")
    print(f"Imagens geradas: {generated_images_dir}")
    print(f"Arquivo de saída: {output_file}\n")

    # Carrega imagens
    print("Carregando imagens...")
    real_image_paths = get_image_paths(real_images_dir)
    generated_image_paths = get_image_paths(generated_images_dir)

    print(f"Imagens reais encontradas: {len(real_image_paths)}")
    print(f"Imagens geradas encontradas: {len(generated_image_paths)}")

    if len(real_image_paths) == 0:
        raise ValueError("Nenhuma imagem real encontrada!")

    if len(generated_image_paths) == 0:
        raise ValueError("Nenhuma imagem gerada encontrada!")

    results = {
        'metadata': {
            'real_images_count': len(real_image_paths),
            'generated_images_count': len(generated_image_paths),
            'device': device,
            'real_images_dir': str(real_images_dir),
            'generated_images_dir': str(generated_images_dir)
        }
    }

    # Calcula FID
    if not args.skip_fid:
        print("\n" + "="*60)
        print("Calculando FID (Fréchet Inception Distance)")
        print("="*60)

        extractor = InceptionFeatureExtractor(device=device)

        print("\nExtraindo features das imagens reais...")
        real_features = extractor.extract_features(real_image_paths, batch_size=args.batch_size)

        print("\nExtraindo features das imagens geradas...")
        generated_features = extractor.extract_features(generated_image_paths, batch_size=args.batch_size)

        print("\nCalculando FID...")
        fid_score = calculate_fid(real_features, generated_features)

        results['fid'] = {
            'score': fid_score,
            'interpretation': (
                'Excelente (< 10)' if fid_score < 10 else
                'Muito Bom (< 20)' if fid_score < 20 else
                'Bom (< 50)' if fid_score < 50 else
                'Razoável (< 100)' if fid_score < 100 else
                'Ruim (>= 100)'
            )
        }

        print(f"\nFID Score: {fid_score:.2f}")
        print(f"Interpretação: {results['fid']['interpretation']}")

    # Calcula CLIP Score
    if not args.skip_clip and args.prompts_file:
        print("\n" + "="*60)
        print("Calculando CLIP Score")
        print("="*60)

        prompts_file = Path(args.prompts_file)
        if not prompts_file.exists():
            print(f"AVISO: Arquivo de prompts não encontrado: {prompts_file}")
            print("Pulando cálculo de CLIP Score.")
        else:
            print(f"\nCarregando prompts de: {prompts_file}")
            prompts_dict = load_prompts_from_json(prompts_file)

            # Cria pares (imagem, prompt)
            image_prompt_pairs = []
            for img_path in generated_image_paths:
                img_name = img_path.name
                if img_name in prompts_dict:
                    image_prompt_pairs.append((img_path, prompts_dict[img_name]))
                else:
                    print(f"AVISO: Prompt não encontrado para {img_name}")

            print(f"\nPares imagem-prompt encontrados: {len(image_prompt_pairs)}")

            if image_prompt_pairs:
                calculator = CLIPScoreCalculator(device=device)
                clip_results = calculator.calculate_batch_scores(image_prompt_pairs)

                results['clip_score'] = clip_results
                results['clip_score']['interpretation'] = (
                    'Excelente (> 30)' if clip_results['mean'] > 30 else
                    'Muito Bom (> 27)' if clip_results['mean'] > 27 else
                    'Bom (> 25)' if clip_results['mean'] > 25 else
                    'Razoável (> 20)' if clip_results['mean'] > 20 else
                    'Ruim (<= 20)'
                )

                print(f"\nCLIP Score Médio: {clip_results['mean']:.2f}")
                print(f"Desvio Padrão: {clip_results['std']:.2f}")
                print(f"Min: {clip_results['min']:.2f} | Max: {clip_results['max']:.2f}")
                print(f"Mediana: {clip_results['median']:.2f}")
                print(f"Interpretação: {results['clip_score']['interpretation']}")
    elif not args.skip_clip and not args.prompts_file:
        print("\nAVISO: --prompts_file não fornecido. Pulando cálculo de CLIP Score.")

    # Salva resultados
    print(f"\n{'='*60}")
    print(f"Salvando resultados em: {output_file}")
    print(f"{'='*60}")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\nResultados salvos com sucesso!")
    print(f"\nResumo:")
    if 'fid' in results:
        print(f"  FID Score: {results['fid']['score']:.2f} ({results['fid']['interpretation']})")
    if 'clip_score' in results:
        print(f"  CLIP Score: {results['clip_score']['mean']:.2f} ± {results['clip_score']['std']:.2f} ({results['clip_score']['interpretation']})")


if __name__ == '__main__':
    main()
