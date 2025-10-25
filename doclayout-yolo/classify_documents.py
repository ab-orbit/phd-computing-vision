#!/usr/bin/env python3
"""
Script principal para classificação de documentos usando DocLayout-YOLO.

Este script implementa um classificador de tipo de documento baseado em
análise de layout. Usa heurísticas baseadas nos elementos detectados pelo
DocLayout-YOLO para inferir o tipo de documento.

Categorias suportadas:
- Email: Emails impressos
- Advertisement: Anúncios e propagandas
- Scientific Publication: Publicações científicas

Uso:
    python classify_documents.py --dataset-path ../rvlp/data/test --num-samples 10

Explicação do funcionamento:
    1. Seleciona N amostras de cada categoria
    2. Para cada documento, detecta elementos de layout
    3. Extrai features baseadas nos elementos (contagens, densidades, etc.)
    4. Aplica heurísticas para classificar o tipo de documento
    5. Compara com a categoria verdadeira e calcula métricas
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
import cv2
import numpy as np
from datetime import datetime

# Importar módulos locais
from sample_selector import select_samples
from analyze_layout import analyze_document_layout, save_annotated_image


def classify_from_layout(features: Dict[str, float]) -> Tuple[str, float, Dict[str, float]]:
    """
    Classifica tipo de documento baseado em features de layout.

    Heurísticas de classificação:

    EMAIL:
    - Poucas ou nenhuma figura/tabela
    - Sem equações
    - Texto em blocos simples
    - Pode ter header/footer

    ADVERTISEMENT:
    - Muitas figuras
    - Títulos destacados
    - Baixa densidade de texto
    - Sem equações ou referências

    SCIENTIFIC PUBLICATION:
    - Presença de equações
    - Múltiplas tabelas e figuras
    - Alta densidade de texto
    - Presença de referências
    - Múltiplos títulos (seções)

    Argumentos:
        features: Dicionário de features extraídas do layout

    Retorna:
        Tupla (classe_predita, confiança, scores_por_classe)
    """
    # Scores para cada categoria (quanto maior, mais provável)
    scores = {
        'email': 0.0,
        'advertisement': 0.0,
        'scientific_publication': 0.0
    }

    # Features numéricas
    num_titles = features.get('num_titles', 0)
    num_figures = features.get('num_figures', 0)
    num_tables = features.get('num_tables', 0)
    num_equations = features.get('num_equations', 0)
    num_references = features.get('num_references', 0)
    num_paragraphs = features.get('num_paragraphs', 0)
    text_density = features.get('text_density', 0.0)
    total_elements = features.get('total_elements', 0)

    # HEURÍSTICAS PARA EMAIL
    # Características: simples, pouco texto, sem elementos complexos
    # Emails típicos: 1-4 parágrafos, MENOS TEXTO e MAIS ÁREA VAZIA
    if num_equations == 0:
        scores['email'] += 3.0
    if num_figures <= 1:
        scores['email'] += 2.0
    if num_tables == 0:
        scores['email'] += 2.0
    if num_references == 0:
        scores['email'] += 2.0
    if total_elements <= 5:  # Poucos elementos
        scores['email'] += 1.0

    # AJUSTADO: Heurística baseada em densidade de texto (CRÍTICA)
    # Emails têm MENOS texto (mais área em branco)
    if text_density < 0.20:  # Muito pouco texto (muita área vazia)
        scores['email'] += 3.0
    elif 0.20 <= text_density < 0.35:  # Densidade baixa-moderada (típico de email)
        scores['email'] += 2.0
    elif text_density >= 0.45:  # Alta densidade = não é email
        scores['email'] -= 3.0  # Penalizar fortemente

    # NOVO: Heurística baseada em parágrafos
    if 1 <= num_paragraphs <= 4:  # Faixa típica de emails
        scores['email'] += 2.5
    elif num_paragraphs >= 5:  # Muitos parágrafos indicam documento complexo
        scores['email'] -= 3.0  # Penalizar fortemente

    # HEURÍSTICAS PARA ADVERTISEMENT
    # Características: muitas imagens, pouco texto, títulos grandes
    # Advertisements típicos: 0-1 parágrafos, muitas figuras
    if num_figures >= 2:
        scores['advertisement'] += 5.0  # AUMENTADO: Figuras são críticas para ads
    elif num_figures == 1:
        scores['advertisement'] += 2.0
    if num_equations == 0:
        scores['advertisement'] += 2.0
    if num_tables == 0:
        scores['advertisement'] += 1.0
    if num_references == 0:
        scores['advertisement'] += 2.0
    if text_density < 0.3:  # Baixa densidade de texto
        scores['advertisement'] += 3.0
    elif text_density > 0.4:  # NOVO: Penalizar alta densidade de texto
        scores['advertisement'] -= 2.0
    if num_titles >= 1:  # Títulos destacados
        scores['advertisement'] += 2.0

    # NOVO: Heurística baseada em parágrafos
    if num_paragraphs <= 1:  # Advertisements têm poucos parágrafos
        scores['advertisement'] += 2.0
    elif num_paragraphs >= 3:  # Muitos parágrafos não é típico de advertisement
        scores['advertisement'] -= 1.5

    # HEURÍSTICAS PARA SCIENTIFIC PUBLICATION
    # Características: equações, tabelas, alta densidade, referências
    # Publicações típicas: 5-15 parágrafos, MAIS TEXTO e MENOS ÁREA EM BRANCO
    if num_equations >= 1:
        scores['scientific_publication'] += 5.0
    if num_tables >= 1:
        scores['scientific_publication'] += 3.0
    if num_figures >= 1:
        scores['scientific_publication'] += 2.0
    if num_references >= 1:
        scores['scientific_publication'] += 4.0
    if num_titles >= 3:  # Múltiplas seções
        scores['scientific_publication'] += 3.0  # AUMENTADO de 2.0 para 3.0
    elif num_titles >= 2:  # NOVO: Pelo menos 2 títulos
        scores['scientific_publication'] += 1.5

    # AJUSTADO: Heurística baseada em densidade de texto (CRÍTICA)
    # Publicações científicas têm MAIS texto (menos área em branco)
    if text_density >= 0.45:  # Alta densidade de texto (pouca área vazia)
        scores['scientific_publication'] += 4.0  # Boost forte
    elif text_density >= 0.35:  # Densidade moderada-alta
        scores['scientific_publication'] += 2.5
    elif text_density < 0.25:  # Baixa densidade = não é publicação
        scores['scientific_publication'] -= 2.0  # Penalizar

    # NOVO: Heurística baseada em parágrafos (CRÍTICA)
    if num_paragraphs >= 5:  # Publicações têm muitos parágrafos
        scores['scientific_publication'] += 4.0  # Boost forte
    elif num_paragraphs >= 3:  # Moderado número de parágrafos
        scores['scientific_publication'] += 2.0

    # Normalizar scores
    max_score = max(scores.values())
    if max_score > 0:
        normalized_scores = {k: v / max_score for k, v in scores.items()}
    else:
        # Se nenhum score, distribuir igualmente
        normalized_scores = {k: 1.0 / 3 for k in scores.keys()}

    # Classe predita é a com maior score
    predicted_class = max(normalized_scores, key=normalized_scores.get)
    confidence = normalized_scores[predicted_class]

    return predicted_class, confidence, normalized_scores


def process_document(
    image_path: Path,
    true_category: str,
    model,
    output_dir: Path,
    conf: float = 0.2,
    imgsz: int = 1024,
    device: str = 'cpu'
) -> Dict[str, Any]:
    """
    Processa um documento completo: análise de layout + classificação.

    Argumentos:
        image_path: Caminho para a imagem
        true_category: Categoria verdadeira (ground truth)
        model: Modelo DocLayout-YOLO
        output_dir: Diretório para salvar resultados
        conf: Threshold de confiança
        imgsz: Tamanho da imagem
        device: Dispositivo de inferência

    Retorna:
        Dicionário com análise completa e classificação
    """
    print(f"\nProcessando: {image_path.name}")
    print(f"Categoria verdadeira: {true_category}")

    # Analisar layout
    analysis = analyze_document_layout(
        image_path=image_path,
        model=model,
        conf=conf,
        imgsz=imgsz,
        device=device
    )

    # Classificar baseado no layout
    predicted_class, confidence, scores = classify_from_layout(analysis['features'])

    print(f"Classificação predita: {predicted_class} (confiança: {confidence:.2%})")
    print(f"Correto: {predicted_class == true_category}")

    # Re-executar para obter objeto result (para anotação)
    results = model.predict(
        str(image_path),
        imgsz=imgsz,
        conf=conf,
        device=device,
        verbose=False
    )

    # Salvar imagem anotada
    output_path = output_dir / true_category / f"{image_path.stem}_annotated.jpg"
    save_annotated_image(image_path, results[0], output_path)

    # Salvar análise JSON
    json_path = output_dir / true_category / f"{image_path.stem}_analysis.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)

    complete_analysis = {
        **analysis,
        'true_category': true_category,
        'predicted_category': predicted_class,
        'confidence': float(confidence),
        'class_scores': {k: float(v) for k, v in scores.items()},
        'correct': predicted_class == true_category
    }

    with open(json_path, 'w') as f:
        json.dump(complete_analysis, f, indent=2)

    return complete_analysis


def generate_report(
    all_results: Dict[str, List[Dict[str, Any]]],
    output_dir: Path
) -> Dict[str, Any]:
    """
    Gera relatório consolidado com métricas de classificação.

    Calcula:
    - Acurácia por categoria
    - Acurácia geral
    - Matriz de confusão
    - Confiança média
    - Estatísticas detalhadas

    Argumentos:
        all_results: Resultados organizados por categoria verdadeira
        output_dir: Diretório para salvar relatório

    Retorna:
        Dicionário com relatório completo
    """
    print("\n" + "=" * 80)
    print("GERANDO RELATÓRIO DE CLASSIFICAÇÃO")
    print("=" * 80)

    categories = list(all_results.keys())

    # Inicializar matriz de confusão
    confusion_matrix = {
        cat: {pred_cat: 0 for pred_cat in categories}
        for cat in categories
    }

    # Estatísticas por categoria
    category_stats = {}

    for true_cat, results in all_results.items():
        correct = sum(1 for r in results if r['correct'])
        total = len(results)
        accuracy = correct / total if total > 0 else 0.0

        confidences = [r['confidence'] for r in results]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Preencher matriz de confusão
        for result in results:
            pred_cat = result['predicted_category']
            confusion_matrix[true_cat][pred_cat] += 1

        category_stats[true_cat] = {
            'total_samples': total,
            'correct': correct,
            'incorrect': total - correct,
            'accuracy': accuracy,
            'avg_confidence': avg_confidence
        }

    # Calcular acurácia geral
    total_samples = sum(stats['total_samples'] for stats in category_stats.values())
    total_correct = sum(stats['correct'] for stats in category_stats.values())
    overall_accuracy = total_correct / total_samples if total_samples > 0 else 0.0

    # Montar relatório
    report = {
        'timestamp': datetime.now().isoformat(),
        'overall_accuracy': overall_accuracy,
        'total_samples': total_samples,
        'total_correct': total_correct,
        'category_stats': category_stats,
        'confusion_matrix': confusion_matrix
    }

    # Salvar relatório JSON
    report_path = output_dir / 'classification_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Relatório salvo em: {report_path}")

    # Exibir resumo
    print("\n" + "=" * 80)
    print("RESUMO DA CLASSIFICAÇÃO")
    print("=" * 80)
    print(f"\nAcurácia Geral: {overall_accuracy:.2%} ({total_correct}/{total_samples})")
    print(f"\nAcurácia por Categoria:")
    print("-" * 80)
    for cat, stats in category_stats.items():
        print(f"{cat:30s}: {stats['accuracy']:.2%} "
              f"({stats['correct']}/{stats['total_samples']}) "
              f"[conf avg: {stats['avg_confidence']:.2%}]")

    # Matriz de confusão
    print("\n" + "=" * 80)
    print("MATRIZ DE CONFUSÃO")
    print("=" * 80)
    print("\nLinhas = Verdadeiro | Colunas = Predito\n")

    # Header
    print(f"{'':30s} ", end='')
    for cat in categories:
        print(f"{cat[:15]:>15s} ", end='')
    print()
    print("-" * (30 + 16 * len(categories)))

    # Linhas
    for true_cat in categories:
        print(f"{true_cat[:30]:30s} ", end='')
        for pred_cat in categories:
            count = confusion_matrix[true_cat][pred_cat]
            print(f"{count:15d} ", end='')
        print()

    return report


def main():
    """Função principal - pipeline completo de classificação."""
    parser = argparse.ArgumentParser(
        description='Classifica documentos usando análise de layout com DocLayout-YOLO',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplo de uso:

  python classify_documents.py --dataset-path ../rvlp/data/test --num-samples 10

Este script irá:
1. Selecionar 10 amostras de email, advertisement e scientific_publication
2. Analisar o layout de cada documento
3. Classificar baseado nos elementos detectados
4. Gerar relatório com acurácia e matriz de confusão
        """
    )

    parser.add_argument(
        '--dataset-path',
        type=str,
        required=True,
        help='Caminho para o dataset RVL-CDIP (ex: ../rvlp/data/test)'
    )

    parser.add_argument(
        '--model-path',
        type=str,
        default='doclayout_yolo_docstructbench_imgsz1024.pt',
        help='Caminho para o modelo DocLayout-YOLO'
    )

    parser.add_argument(
        '--num-samples',
        type=int,
        default=10,
        help='Número de amostras por categoria (padrão: 10)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='results',
        help='Diretório de saída (padrão: results)'
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
        help='Dispositivo (padrão: cpu)'
    )

    args = parser.parse_args()

    # Converter para Path
    dataset_path = Path(args.dataset_path)
    output_dir = Path(args.output_dir)
    model_path = Path(args.model_path)

    print("=" * 80)
    print("CLASSIFICAÇÃO DE DOCUMENTOS COM DOCLAYOUT-YOLO")
    print("=" * 80)
    print(f"\nDataset: {dataset_path}")
    print(f"Modelo: {model_path}")
    print(f"Amostras por categoria: {args.num_samples}")
    print(f"Diretório de saída: {output_dir}")

    try:
        # Importar DocLayout-YOLO
        print("\n" + "=" * 80)
        print("CARREGANDO MODELO")
        print("=" * 80)
        try:
            from doclayout_yolo import YOLOv10
        except ImportError:
            print("❌ ERRO: doclayout-yolo não instalado")
            print("Execute: pip install doclayout-yolo")
            return 1

        # Verificar modelo
        if not model_path.exists():
            print(f"❌ ERRO: Modelo não encontrado: {model_path}")
            print("\nBaixe o modelo:")
            print("wget https://huggingface.co/juliozhao/DocLayout-YOLO-DocStructBench/resolve/main/doclayout_yolo_docstructbench_imgsz1024.pt")
            return 1

        # Carregar modelo
        model = YOLOv10(str(model_path))
        print(f"✓ Modelo carregado: {model_path}")

        # Selecionar amostras
        print("\n" + "=" * 80)
        print("SELECIONANDO AMOSTRAS")
        print("=" * 80)

        categories = ['email', 'advertisement', 'scientific_publication']
        selected_samples = select_samples(
            dataset_path=dataset_path,
            categories=categories,
            num_samples=args.num_samples,
            output_dir=Path('sample'),
            seed=42
        )

        # Processar documentos
        print("\n" + "=" * 80)
        print("PROCESSANDO DOCUMENTOS")
        print("=" * 80)

        all_results = {cat: [] for cat in categories}

        for category, sample_paths in selected_samples.items():
            print(f"\n{'=' * 80}")
            print(f"Categoria: {category.upper()}")
            print(f"{'=' * 80}")

            for i, sample_path in enumerate(sample_paths, 1):
                print(f"\n[{i}/{len(sample_paths)}] {sample_path.name}")
                print("-" * 80)

                result = process_document(
                    image_path=sample_path,
                    true_category=category,
                    model=model,
                    output_dir=output_dir,
                    conf=args.conf,
                    imgsz=args.imgsz,
                    device=args.device
                )

                all_results[category].append(result)

        # Gerar relatório
        report = generate_report(all_results, output_dir)

        print("\n" + "=" * 80)
        print("✓ CLASSIFICAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 80)
        print(f"\nResultados salvos em: {output_dir}")
        print(f"  - Imagens anotadas: {output_dir}/<categoria>/*_annotated.jpg")
        print(f"  - Análises JSON: {output_dir}/<categoria>/*_analysis.json")
        print(f"  - Relatório: {output_dir}/classification_report.json")

        return 0

    except Exception as e:
        print(f"\n❌ ERRO durante execução: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
