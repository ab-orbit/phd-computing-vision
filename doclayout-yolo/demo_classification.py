#!/usr/bin/env python3
"""
Script de demonstração rápida do classificador DocLayout-YOLO.

Este script demonstra o uso básico do sistema de classificação
em um workflow simplificado.

Uso:
    python demo_classification.py
"""

from pathlib import Path
import json


def quick_demo():
    """
    Demonstração rápida do sistema de classificação.

    Este exemplo mostra:
    1. Como carregar o modelo
    2. Como analisar um documento
    3. Como classificar baseado no layout
    4. Como interpretar os resultados
    """
    print("=" * 80)
    print("DEMONSTRAÇÃO - CLASSIFICAÇÃO DE DOCUMENTOS COM DOCLAYOUT-YOLO")
    print("=" * 80)

    # Importar módulos necessários
    try:
        from doclayout_yolo import YOLOv10
        from analyze_layout import analyze_document_layout, extract_classification_features
        from classify_documents import classify_from_layout
    except ImportError as e:
        print(f"\n❌ ERRO: {e}")
        print("\nExecute primeiro:")
        print("  1. pip install doclayout-yolo")
        print("  2. ./setup.sh")
        return

    # Verificar se existem amostras
    sample_dir = Path('sample')
    if not sample_dir.exists():
        print("\n⚠️  Diretório 'sample' não encontrado.")
        print("Execute primeiro:")
        print("  python sample_selector.py --dataset-path ../rvlp/data/test --num-samples 3")
        return

    # Procurar primeira amostra disponível
    categories = ['email', 'advertisement', 'scientific_publication']
    sample_image = None
    sample_category = None

    for cat in categories:
        cat_dir = sample_dir / cat
        if cat_dir.exists():
            images = list(cat_dir.glob('*.tif'))
            if images:
                sample_image = images[0]
                sample_category = cat
                break

    if sample_image is None:
        print("\n⚠️  Nenhuma amostra encontrada em sample/")
        print("Execute primeiro:")
        print("  python sample_selector.py --dataset-path ../rvlp/data/test --num-samples 3")
        return

    print(f"\n📄 Documento de exemplo: {sample_image.name}")
    print(f"📁 Categoria verdadeira: {sample_category}")

    # Carregar modelo
    print("\n" + "-" * 80)
    print("ETAPA 1: Carregando modelo DocLayout-YOLO")
    print("-" * 80)

    model_path = Path('doclayout_yolo_docstructbench.pt')
    if not model_path.exists():
        print(f"❌ Modelo não encontrado: {model_path}")
        print("\nBaixe com:")
        print("  wget https://huggingface.co/juliozhao/DocLayout-YOLO-DocStructBench/"
              "resolve/main/doclayout_yolo_docstructbench.pt")
        return

    try:
        model = YOLOv10(str(model_path))
        print(f"✓ Modelo carregado: {model_path}")
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        return

    # Analisar layout
    print("\n" + "-" * 80)
    print("ETAPA 2: Analisando layout do documento")
    print("-" * 80)

    try:
        analysis = analyze_document_layout(
            image_path=sample_image,
            model=model,
            conf=0.2,
            imgsz=1024,
            device='cpu'
        )
        print(f"✓ {analysis['total_detections']} elementos detectados")
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        return

    # Classificar
    print("\n" + "-" * 80)
    print("ETAPA 3: Classificando tipo de documento")
    print("-" * 80)

    try:
        predicted_class, confidence, scores = classify_from_layout(analysis['features'])

        print(f"\n🎯 Classificação:")
        print(f"   Categoria predita: {predicted_class}")
        print(f"   Confiança: {confidence:.2%}")
        print(f"   Correto: {'✓' if predicted_class == sample_category else '✗'}")

        print(f"\n📊 Scores por categoria:")
        for cat, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * int(score * 20)
            print(f"   {cat:30s}: {bar:20s} {score:.2%}")

    except Exception as e:
        print(f"❌ Erro na classificação: {e}")
        return

    # Explicação da decisão
    print("\n" + "-" * 80)
    print("ETAPA 4: Explicando a decisão")
    print("-" * 80)

    features = analysis['features']

    print("\n📋 Features-chave:")
    print(f"   Equações:     {features.get('num_equations', 0)}")
    print(f"   Tabelas:      {features.get('num_tables', 0)}")
    print(f"   Figuras:      {features.get('num_figures', 0)}")
    print(f"   Referências:  {features.get('num_references', 0)}")
    print(f"   Títulos:      {features.get('num_titles', 0)}")
    print(f"   Densidade texto: {features.get('text_density', 0):.2%}")

    print("\n💡 Raciocínio:")

    if predicted_class == 'email':
        print("   - Poucos elementos complexos (tabelas, equações)")
        print("   - Densidade de texto moderada")
        print("   - Layout simples e direto")

    elif predicted_class == 'advertisement':
        print("   - Presença de figuras")
        print("   - Baixa densidade de texto")
        print("   - Sem elementos acadêmicos (equações, referências)")

    elif predicted_class == 'scientific_publication':
        print("   - Elementos acadêmicos detectados")
        print("   - Alta densidade de texto")
        print("   - Estrutura formal (seções, referências)")

    # Salvar resultado
    print("\n" + "-" * 80)
    print("ETAPA 5: Salvando resultado")
    print("-" * 80)

    output_dir = Path('demo_output')
    output_dir.mkdir(exist_ok=True)

    # Salvar análise JSON
    output_json = output_dir / f"{sample_image.stem}_demo.json"
    with open(output_json, 'w') as f:
        demo_result = {
            'image': str(sample_image),
            'true_category': sample_category,
            'predicted_category': predicted_class,
            'confidence': float(confidence),
            'scores': {k: float(v) for k, v in scores.items()},
            'features': {k: float(v) if isinstance(v, (int, float)) else v
                        for k, v in features.items()},
            'total_detections': analysis['total_detections'],
            'element_counts': analysis['element_counts']
        }
        json.dump(demo_result, f, indent=2)

    print(f"✓ Resultado salvo em: {output_json}")

    # Salvar imagem anotada
    try:
        from analyze_layout import save_annotated_image

        results = model.predict(
            str(sample_image),
            imgsz=1024,
            conf=0.2,
            device='cpu',
            verbose=False
        )

        output_image = output_dir / f"{sample_image.stem}_annotated.jpg"
        save_annotated_image(sample_image, results[0], output_image)
        print(f"✓ Imagem anotada salva em: {output_image}")

    except Exception as e:
        print(f"⚠️  Não foi possível salvar imagem anotada: {e}")

    # Resumo final
    print("\n" + "=" * 80)
    print("✓ DEMONSTRAÇÃO CONCLUÍDA")
    print("=" * 80)
    print(f"\nResultado: {predicted_class.upper()}")
    print(f"Acurado: {'SIM' if predicted_class == sample_category else 'NÃO'}")
    print(f"Confiança: {confidence:.1%}")

    print(f"\nArquivos gerados:")
    print(f"  - {output_json}")
    if (output_dir / f"{sample_image.stem}_annotated.jpg").exists():
        print(f"  - {output_dir / f'{sample_image.stem}_annotated.jpg'}")

    print("\nPróximos passos:")
    print("  1. Execute o classificador completo:")
    print("     python classify_documents.py --dataset-path ../rvlp/data/test --num-samples 10")
    print("")
    print("  2. Veja o QUICKSTART.md para mais exemplos")
    print("=" * 80)


if __name__ == '__main__':
    try:
        quick_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demonstração interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
