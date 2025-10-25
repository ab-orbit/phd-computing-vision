"""
Script de teste para verificar a estrutura retornada pelo docling.

FINALIDADE EDUCATIVA:
Quando uma biblioteca externa muda sua API, precisamos investigar
a nova estrutura de dados retornada. Este script ajuda a entender
como o docling atual organiza seus dados.
"""

from pathlib import Path
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

# Configurar docling
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.do_table_structure = True

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: pipeline_options,
    }
)

# Testar com um arquivo de exemplo
test_file = Path("/Users/jwcunha/Documents/repos/phd-datascience/visao-computacional/doclayout-yolo/sample/scientific_publication/10142638.tif")

print(f"Testando docling com: {test_file.name}")
print("=" * 80)

result = converter.convert(str(test_file))

print(f"\nTipo do result: {type(result)}")
print(f"Tipo do result.document: {type(result.document)}")
print(f"Tipo do result.document.body: {type(result.document.body)}")

# Verificar atributos de body
print(f"\nAtributos de body: {dir(result.document.body)}")

# Tentar diferentes formas de iterar
print("\n--- Tentando iterar sobre body.children ---")
if hasattr(result.document.body, 'children'):
    print(f"body.children existe: {result.document.body.children}")

if hasattr(result.document.body, 'items'):
    print(f"body.items existe: {result.document.body.items}")

# Tentar usar export_to_markdown para ver a estrutura
print("\n--- Tentando exportar para markdown ---")
markdown = result.document.export_to_markdown()
print(f"Markdown gerado (primeiros 500 chars):\n{markdown[:500]}")

# Tentar iterar sobre result.document.iterate_items()
print("\n--- Tentando iterate_items() ---")
if hasattr(result.document, 'iterate_items'):
    for i, (item_key, item_value) in enumerate(result.document.iterate_items()):
        if i >= 5:  # Apenas primeiros 5
            break
        print(f"\n--- Item {i} ---")
        print(f"Key: {item_key}")
        print(f"Value tipo: {type(item_value)}")

        # Se for tupla
        if isinstance(item_value, tuple):
            print(f"Tupla de tamanho: {len(item_value)}")
            print(f"  [0]: {type(item_value[0])}")
            print(f"  [1]: {type(item_value[1])}")
            # Examinar segundo elemento (geralmente o conteúdo)
            if len(item_value) > 1:
                content = item_value[1]
                print(f"  Atributos de content: {[attr for attr in dir(content) if not attr.startswith('_')]}")
                if hasattr(content, 'text'):
                    print(f"  text: {content.text[:100] if len(content.text) > 100 else content.text}")

print("\n" + "=" * 80)
print("Teste concluído!")
