#!/usr/bin/env python3
"""
Script para análise de layout de documentos usando DocLayout-YOLO.

Este script processa um documento e detecta elementos de layout como
títulos, parágrafos, tabelas, figuras, equações, etc.

Uso:
    python analyze_layout.py --image-path sample/email/example.tif --model-path modelo.pt

Explicação:
    O DocLayout-YOLO detecta elementos estruturais no documento, que podem
    ser usados como features para classificação de tipo de documento.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
import cv2
import numpy as np


def detect_paragraphs(detections: List[Dict], img_height: int, img_width: int) -> Tuple[int, List[Dict]]:
    """
    Detecta e conta parágrafos baseado nas detecções de blocos de texto.

    Lógica de Detecção de Parágrafos:
    ---------------------------------
    Um parágrafo é definido como um bloco de texto contínuo. Para identificá-los:

    1. Filtra apenas elementos de texto (plain text, text, paragraph)
    2. Ordena blocos de texto por posição vertical (top to bottom)
    3. Agrupa blocos próximos verticalmente (< 5% da altura da imagem)
    4. Considera alinhamento horizontal (overlapping em X)
    5. Cada grupo é um parágrafo

    Heurísticas:
    - Distância vertical máxima: 5% da altura da imagem
    - Overlap horizontal mínimo: 50%
    - Blocos muito pequenos (< 1% da área) são ignorados

    Argumentos:
        detections: Lista de detecções do modelo
        img_height: Altura da imagem
        img_width: Largura da imagem

    Retorna:
        Tupla (num_paragraphs, paragraph_info)
        - num_paragraphs: Número de parágrafos detectados
        - paragraph_info: Lista de dicionários com info de cada parágrafo
    """
    # Classes que representam blocos de texto (após mapeamento)
    TEXT_CLASSES = {'text', 'paragraph', 'body text'}

    # Filtrar apenas detecções de texto
    text_blocks = []
    for det in detections:
        if det['class'] in TEXT_CLASSES:
            # Ignorar blocos muito pequenos (< 1% da área da imagem)
            if det['area_ratio'] > 0.01:
                text_blocks.append(det)

    if not text_blocks:
        return 0, []

    # Ordenar por posição vertical (top)
    text_blocks_sorted = sorted(text_blocks, key=lambda x: x['bbox'][1])

    # Agrupar blocos em parágrafos
    paragraphs = []
    current_paragraph = [text_blocks_sorted[0]]

    # Threshold de distância vertical (5% da altura)
    vertical_threshold = img_height * 0.05

    for i in range(1, len(text_blocks_sorted)):
        current_block = text_blocks_sorted[i]
        previous_block = text_blocks_sorted[i-1]

        # Coordenadas
        curr_x1, curr_y1, curr_x2, curr_y2 = current_block['bbox']
        prev_x1, prev_y1, prev_x2, prev_y2 = previous_block['bbox']

        # Distância vertical entre blocos (topo do atual - fundo do anterior)
        vertical_distance = curr_y1 - prev_y2

        # Verificar overlap horizontal (para detectar mudança de coluna)
        # Overlap = interseção / união do range X
        x_overlap_start = max(curr_x1, prev_x1)
        x_overlap_end = min(curr_x2, prev_x2)
        x_overlap = max(0, x_overlap_end - x_overlap_start)

        x_union = max(curr_x2, prev_x2) - min(curr_x1, prev_x1)
        overlap_ratio = x_overlap / x_union if x_union > 0 else 0

        # Blocos pertencem ao mesmo parágrafo se:
        # 1. Estão próximos verticalmente (< threshold)
        # 2. Têm overlap horizontal significativo (> 50%)
        if vertical_distance < vertical_threshold and overlap_ratio > 0.5:
            current_paragraph.append(current_block)
        else:
            # Novo parágrafo
            paragraphs.append(current_paragraph)
            current_paragraph = [current_block]

    # Adicionar último parágrafo
    if current_paragraph:
        paragraphs.append(current_paragraph)

    # Gerar informações sobre cada parágrafo
    paragraph_info = []
    for idx, para_blocks in enumerate(paragraphs, 1):
        # Calcular bounding box que engloba todo o parágrafo
        all_x1 = [b['bbox'][0] for b in para_blocks]
        all_y1 = [b['bbox'][1] for b in para_blocks]
        all_x2 = [b['bbox'][2] for b in para_blocks]
        all_y2 = [b['bbox'][3] for b in para_blocks]

        para_bbox = [
            min(all_x1), min(all_y1),
            max(all_x2), max(all_y2)
        ]

        # Área total do parágrafo
        para_area = sum(b['area'] for b in para_blocks)

        # Confiança média
        para_confidence = sum(b['confidence'] for b in para_blocks) / len(para_blocks)

        paragraph_info.append({
            'paragraph_id': idx,
            'num_blocks': len(para_blocks),
            'bbox': para_bbox,
            'area': float(para_area),
            'confidence': float(para_confidence)
        })

    return len(paragraphs), paragraph_info


def analyze_document_layout(
    image_path: Path,
    model,
    conf: float = 0.2,
    imgsz: int = 1024,
    device: str = 'cpu'
) -> Dict[str, Any]:
    """
    Analisa o layout de um documento usando DocLayout-YOLO.

    Argumentos:
        image_path: Caminho para a imagem do documento
        model: Modelo DocLayout-YOLO carregado
        conf: Threshold de confiança (0.0 a 1.0)
        imgsz: Tamanho da imagem para inferência
        device: Dispositivo ('cpu' ou 'cuda')

    Retorna:
        Dicionário com análise do layout contendo:
        - detections: Lista de elementos detectados
        - features: Features extraídas para classificação
        - metadata: Informações sobre a imagem
    """
    print(f"\nAnalisando layout de: {image_path.name}")
    print("-" * 80)

    # Fazer predição
    results = model.predict(
        str(image_path),
        imgsz=imgsz,
        conf=conf,
        device=device,
        verbose=False
    )

    # Processar resultados
    result = results[0]
    boxes = result.boxes

    # Carregar imagem para obter dimensões
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Não foi possível carregar a imagem: {image_path}")

    img_height, img_width = img.shape[:2]
    total_area = img_width * img_height

    # Mapeamento de classes do modelo para nomes padronizados
    # CRÍTICO: DocLayout-YOLO usa nomes diferentes dos esperados
    CLASS_MAPPING = {
        'plain text': 'text',           # Texto comum
        'isolate_formula': 'equation',  # Equações matemáticas
        'figure_caption': 'caption',    # Legendas de figuras
        'table_footnote': 'caption',    # Notas de rodapé de tabelas
        'abandon': None,                # Ruído - ignorar
        # Classes que já estão corretas
        'title': 'title',
        'figure': 'figure',
        'table': 'table',
        'header': 'header',
        'footer': 'footer',
        'reference': 'reference',
        'list': 'list',
        'caption': 'caption',
        'equation': 'equation',
        'text': 'text'
    }

    # Extrair detecções
    detections = []
    element_counts = {}
    element_areas = {}

    if boxes is not None and len(boxes) > 0:
        for box in boxes:
            # Coordenadas da bounding box
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

            # Área do elemento
            area = (x2 - x1) * (y2 - y1)

            # Classe e confiança
            cls_id = int(box.cls[0].cpu().numpy())
            conf_score = float(box.conf[0].cpu().numpy())

            # Nome da classe original detectada pelo modelo
            original_class_name = result.names[cls_id]

            # Aplicar mapeamento de classes
            mapped_class_name = CLASS_MAPPING.get(original_class_name, original_class_name)

            # Ignorar classes mapeadas para None (ruído)
            if mapped_class_name is None:
                continue

            detection = {
                'class': mapped_class_name,
                'original_class': original_class_name,  # Manter original para referência
                'confidence': conf_score,
                'bbox': [float(x1), float(y1), float(x2), float(y2)],
                'area': float(area),
                'area_ratio': float(area / total_area)
            }
            detections.append(detection)

            # Contar elementos por tipo (usando classe mapeada)
            element_counts[mapped_class_name] = element_counts.get(mapped_class_name, 0) + 1

            # Somar áreas por tipo (usando classe mapeada)
            element_areas[mapped_class_name] = element_areas.get(mapped_class_name, 0) + area

    # Detectar parágrafos
    num_paragraphs, paragraph_info = detect_paragraphs(
        detections, img_height, img_width
    )

    # Extrair features para classificação
    features = extract_classification_features(
        detections, element_counts, element_areas, total_area, num_paragraphs
    )

    # Montar análise completa
    analysis = {
        'image_path': str(image_path),
        'image_size': {
            'width': img_width,
            'height': img_height,
            'area': total_area
        },
        'total_detections': len(detections),
        'element_counts': element_counts,
        'element_areas': {
            k: float(v) for k, v in element_areas.items()
        },
        'num_paragraphs': num_paragraphs,
        'paragraph_info': paragraph_info,
        'detections': detections,
        'features': features
    }

    print(f"Total de elementos detectados: {len(detections)}")
    print(f"Parágrafos detectados: {num_paragraphs}")
    print(f"\nElementos por tipo:")
    for class_name, count in sorted(element_counts.items()):
        print(f"  {class_name:20s}: {count:3d}")

    return analysis


def extract_classification_features(
    detections: List[Dict],
    element_counts: Dict[str, int],
    element_areas: Dict[str, float],
    total_area: float,
    num_paragraphs: int = 0
) -> Dict[str, float]:
    """
    Extrai features para classificação baseadas no layout.

    Explicação das features:
        - num_*: Contagem de elementos de cada tipo
        - *_density: Proporção da área ocupada por cada tipo de elemento
        - has_*: Presença booleana de elementos específicos
        - avg_confidence: Confiança média das detecções
        - num_paragraphs: Número de parágrafos detectados no documento
    """
    features = {}

    # Contagens absolutas
    features['num_titles'] = element_counts.get('title', 0)
    features['num_texts'] = element_counts.get('text', 0)
    features['num_figures'] = element_counts.get('figure', 0)
    features['num_tables'] = element_counts.get('table', 0)
    features['num_equations'] = element_counts.get('equation', 0)
    features['num_captions'] = element_counts.get('caption', 0)
    features['num_headers'] = element_counts.get('header', 0)
    features['num_footers'] = element_counts.get('footer', 0)
    features['num_references'] = element_counts.get('reference', 0)
    features['num_lists'] = element_counts.get('list', 0)
    features['num_paragraphs'] = num_paragraphs

    # Densidades (área relativa)
    for element_type, area in element_areas.items():
        features[f'{element_type}_density'] = area / total_area if total_area > 0 else 0

    # Features booleanas (presença/ausência)
    features['has_equations'] = 1.0 if features['num_equations'] > 0 else 0.0
    features['has_tables'] = 1.0 if features['num_tables'] > 0 else 0.0
    features['has_figures'] = 1.0 if features['num_figures'] > 0 else 0.0
    features['has_references'] = 1.0 if features['num_references'] > 0 else 0.0

    # Densidade total de texto
    text_density = features.get('text_density', 0.0)
    features['text_density_category'] = classify_density(text_density)

    # Confiança média
    if detections:
        avg_conf = sum(d['confidence'] for d in detections) / len(detections)
        features['avg_confidence'] = avg_conf
    else:
        features['avg_confidence'] = 0.0

    # Total de elementos
    features['total_elements'] = sum(element_counts.values())

    return features


def classify_density(density: float) -> float:
    """
    Classifica densidade de texto em categorias.

    Explicação:
        0.0 = muito baixa (< 20%)
        0.33 = baixa (20-40%)
        0.66 = média (40-60%)
        1.0 = alta (> 60%)
    """
    if density < 0.2:
        return 0.0  # Muito baixa
    elif density < 0.4:
        return 0.33  # Baixa
    elif density < 0.6:
        return 0.66  # Média
    else:
        return 1.0  # Alta


def save_annotated_image(
    image_path: Path,
    result,
    output_path: Path
) -> None:
    """
    Salva imagem com anotações de elementos detectados.

    As bounding boxes são desenhadas com cores diferentes para cada tipo
    de elemento, facilitando a visualização do layout detectado.
    """
    print(f"\nSalvando imagem anotada em: {output_path}")

    # Gerar imagem anotada usando o método plot do YOLO
    annotated = result.plot(
        pil=True,  # Retornar como PIL Image
        line_width=3,
        font_size=12
    )

    # Converter de RGB (PIL) para BGR (OpenCV) se necessário
    if isinstance(annotated, np.ndarray):
        # Já é numpy array
        if annotated.shape[2] == 3:  # RGB
            annotated = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)
    else:
        # É PIL Image
        annotated = np.array(annotated)
        annotated = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)

    # Salvar
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), annotated)
    print(f"✓ Imagem anotada salva")


def main():
    """Função principal - parse de argumentos e execução."""
    parser = argparse.ArgumentParser(
        description='Analisa o layout de um documento usando DocLayout-YOLO',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--image-path',
        type=str,
        required=True,
        help='Caminho para a imagem do documento'
    )

    parser.add_argument(
        '--model-path',
        type=str,
        default='doclayout_yolo_docstructbench.pt',
        help='Caminho para o modelo DocLayout-YOLO (padrão: doclayout_yolo_docstructbench.pt)'
    )

    parser.add_argument(
        '--output-path',
        type=str,
        help='Caminho para salvar imagem anotada (opcional)'
    )

    parser.add_argument(
        '--conf',
        type=float,
        default=0.2,
        help='Threshold de confiança (padrão: 0.2)'
    )

    parser.add_argument(
        '--imgsz',
        type=int,
        default=1024,
        help='Tamanho da imagem para inferência (padrão: 1024)'
    )

    parser.add_argument(
        '--device',
        type=str,
        default='cpu',
        choices=['cpu', 'cuda', 'mps'],
        help='Dispositivo para inferência (padrão: cpu)'
    )

    parser.add_argument(
        '--save-json',
        type=str,
        help='Caminho para salvar análise em JSON (opcional)'
    )

    args = parser.parse_args()

    # Converter para Path
    image_path = Path(args.image_path)

    # Validar imagem
    if not image_path.exists():
        print(f"❌ ERRO: Imagem não encontrada: {image_path}")
        return 1

    print("=" * 80)
    print("ANÁLISE DE LAYOUT COM DOCLAYOUT-YOLO")
    print("=" * 80)
    print(f"\nImagem: {image_path}")
    print(f"Modelo: {args.model_path}")
    print(f"Confiança: {args.conf}")
    print(f"Tamanho inferência: {args.imgsz}")
    print(f"Dispositivo: {args.device}")

    try:
        # Importar DocLayout-YOLO
        print("\nCarregando modelo DocLayout-YOLO...")
        try:
            from doclayout_yolo import YOLOv10
        except ImportError:
            print("❌ ERRO: doclayout-yolo não instalado")
            print("Execute: pip install doclayout-yolo")
            return 1

        # Carregar modelo
        model_path = Path(args.model_path)
        if not model_path.exists():
            print(f"❌ ERRO: Modelo não encontrado: {model_path}")
            print("\nBaixe o modelo:")
            print("wget https://huggingface.co/juliozhao/DocLayout-YOLO-DocStructBench/"
                  "resolve/main/doclayout_yolo_docstructbench.pt")
            return 1

        model = YOLOv10(str(model_path))
        print(f"✓ Modelo carregado: {model_path}")

        # Analisar layout
        analysis = analyze_document_layout(
            image_path=image_path,
            model=model,
            conf=args.conf,
            imgsz=args.imgsz,
            device=args.device
        )

        # Salvar JSON se solicitado
        if args.save_json:
            json_path = Path(args.save_json)
            json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, 'w') as f:
                json.dump(analysis, f, indent=2)
            print(f"\n✓ Análise JSON salva em: {json_path}")

        # Salvar imagem anotada se solicitado
        if args.output_path:
            output_path = Path(args.output_path)

            # Re-executar predição para obter objeto result
            results = model.predict(
                str(image_path),
                imgsz=args.imgsz,
                conf=args.conf,
                device=args.device,
                verbose=False
            )

            save_annotated_image(image_path, results[0], output_path)

        # Exibir resumo das features
        print("\n" + "=" * 80)
        print("FEATURES EXTRAÍDAS PARA CLASSIFICAÇÃO")
        print("=" * 80)
        for feature_name, value in sorted(analysis['features'].items()):
            if isinstance(value, float):
                print(f"{feature_name:30s}: {value:.4f}")
            else:
                print(f"{feature_name:30s}: {value}")

        print("\n" + "=" * 80)
        print("✓ Análise concluída com sucesso!")
        print("=" * 80)

        return 0

    except Exception as e:
        print(f"\n❌ ERRO durante análise: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
