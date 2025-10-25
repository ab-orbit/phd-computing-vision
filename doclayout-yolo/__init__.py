"""
DocLayout-YOLO Document Classification

Classificação de documentos usando análise de layout.

Módulos:
    - sample_selector: Seleção de amostras do dataset
    - analyze_layout: Análise de layout de documentos individuais
    - classify_documents: Pipeline completo de classificação

Uso:
    from sample_selector import select_samples
    from analyze_layout import analyze_document_layout
    from classify_documents import classify_from_layout
"""

__version__ = '1.0.0'
__author__ = 'DocLayout-YOLO Classification Project'

# Imports principais
try:
    from .sample_selector import select_samples
    from .analyze_layout import (
        analyze_document_layout,
        extract_classification_features,
        save_annotated_image
    )
    from .classify_documents import (
        classify_from_layout,
        process_document,
        generate_report
    )
except ImportError:
    # Se importado como script standalone
    pass
