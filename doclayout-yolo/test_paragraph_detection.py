#!/usr/bin/env python3
"""
Script de teste para demonstrar a detecção de parágrafos.

Este script processa algumas amostras de diferentes categorias e
mostra como a contagem de parágrafos varia entre tipos de documentos.
"""

import json
from pathlib import Path
from doclayout_yolo import YOLOv10
from analyze_layout import analyze_document_layout


def test_paragraph_detection():
    """Testa detecção de parágrafos em diferentes tipos de documentos."""
    print("=" * 80)
    print("TESTE DE DETECÇÃO DE PARÁGRAFOS")
    print("=" * 80)

    # Carregar modelo
    model_path = 'doclayout_yolo_docstructbench_imgsz1024.pt'
    if not Path(model_path).exists():
        print(f"❌ Modelo não encontrado: {model_path}")
        print("Execute: ./setup.sh")
        return

    print(f"\nCarregando modelo: {model_path}")
    model = YOLOv10(model_path)
    print("✓ Modelo carregado\n")

    # Documentos de teste de cada categoria
    test_samples = {
        'email': 'sample/email',
        'advertisement': 'sample/advertisement',
        'scientific_publication': 'sample/scientific_publication'
    }

    results = []

    for category, sample_dir in test_samples.items():
        sample_path = Path(sample_dir)

        if not sample_path.exists():
            print(f"⚠️  Diretório não encontrado: {sample_path}")
            continue

        # Pegar primeiro arquivo
        images = list(sample_path.glob('*.tif'))
        if not images:
            print(f"⚠️  Nenhuma imagem encontrada em: {sample_path}")
            continue

        image_path = images[0]

        print(f"\n{'='*80}")
        print(f"Categoria: {category.upper()}")
        print(f"Documento: {image_path.name}")
        print(f"{'='*80}")

        # Analisar layout
        analysis = analyze_document_layout(
            image_path=image_path,
            model=model,
            conf=0.2,
            imgsz=1024,
            device='cpu'
        )

        # Extrair informações relevantes
        num_paragraphs = analysis['num_paragraphs']
        paragraph_info = analysis['paragraph_info']
        features = analysis['features']

        result = {
            'category': category,
            'document': image_path.name,
            'num_paragraphs': num_paragraphs,
            'total_elements': features.get('total_elements', 0),
            'num_titles': features.get('num_titles', 0),
            'num_figures': features.get('num_figures', 0),
            'text_density': features.get('plain text_density', 0)
        }
        results.append(result)

        # Mostrar detalhes dos parágrafos
        print(f"\n📄 Parágrafos Detectados: {num_paragraphs}")
        if paragraph_info:
            print("\nDetalhes por parágrafo:")
            print("-" * 80)
            for para in paragraph_info:
                print(f"  Parágrafo {para['paragraph_id']}:")
                print(f"    - Blocos de texto: {para['num_blocks']}")
                print(f"    - Área: {para['area']:.0f} pixels²")
                print(f"    - Confiança: {para['confidence']:.2%}")
                print(f"    - Posição (x,y): ({para['bbox'][0]:.0f}, {para['bbox'][1]:.0f})")
        else:
            print("  (Nenhum parágrafo detectado)")

    # Resumo comparativo
    print("\n" + "=" * 80)
    print("RESUMO COMPARATIVO")
    print("=" * 80)
    print(f"\n{'Categoria':<30} {'Parágrafos':<12} {'Elementos':<12} {'Densidade Texto'}")
    print("-" * 80)

    for r in results:
        print(f"{r['category']:<30} {r['num_paragraphs']:<12} "
              f"{r['total_elements']:<12} {r['text_density']:.2%}")

    # Observações
    print("\n" + "=" * 80)
    print("OBSERVAÇÕES")
    print("=" * 80)
    print("""
Padrões esperados:

1. EMAILS:
   - Poucos parágrafos (1-3)
   - Blocos de texto simples
   - Densidade de texto moderada

2. ADVERTISEMENTS:
   - Poucos ou nenhum parágrafo
   - Muitos elementos gráficos (figuras)
   - Baixa densidade de texto

3. SCIENTIFIC PUBLICATIONS:
   - Múltiplos parágrafos (3-8+)
   - Alta densidade de texto
   - Estrutura formal com seções

A detecção de parágrafos pode ajudar a distinguir entre:
- Documentos densos em texto (publicações, relatórios)
- Documentos visuais (anúncios)
- Documentos simples (emails)
    """)

    print("=" * 80)
    print("✓ Teste concluído!")
    print("=" * 80)


if __name__ == '__main__':
    try:
        test_paragraph_detection()
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
