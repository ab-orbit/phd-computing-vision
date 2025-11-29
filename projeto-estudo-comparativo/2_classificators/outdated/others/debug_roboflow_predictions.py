"""
Script para Debug de Predições Roboflow

Este script analisa algumas imagens e mostra as predições brutas
do modelo Roboflow, para entender quais classes estão sendo retornadas.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from roboflow import Roboflow
import json

# Carrega API key
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)
api_key = os.getenv('ROBOFLOW_API_KEY')

print(f"API Key: {api_key[:10]}...")

# Inicializa Roboflow
rf = Roboflow(api_key=api_key)
workspace = "computer-vision-projects-zhogq"
project = "emotion-detection-y0svj"

project_obj = rf.workspace(workspace).project(project)
versions = project_obj.versions()
print(f"\nVersões disponíveis: {[v.version for v in versions]}")

# Usa versão mais recente
version = versions[-1].version
model = project_obj.version(version).model

print(f"Usando versão: {version}")

# Testa em algumas imagens
dataset_dir = Path("../../../datasets/sim01")

print("\n" + "="*70)
print("TESTANDO PREDIÇÕES EM IMAGENS DE RAIVA")
print("="*70)

raiva_dir = dataset_dir / "raiva"
raiva_images = list(raiva_dir.glob("*"))[:5]  # Primeiras 5 imagens

for img_path in raiva_images:
    print(f"\nImagem: {img_path.name}")
    result = model.predict(str(img_path), confidence=40, overlap=30)
    result_dict = result.json()

    print(f"Predições: {len(result_dict['predictions'])}")
    for pred in result_dict['predictions']:
        print(f"  - {pred['class']}: {pred['confidence']:.2f}")

print("\n" + "="*70)
print("TESTANDO PREDIÇÕES EM IMAGENS DE ALEGRIA")
print("="*70)

alegria_dir = dataset_dir / "alegria"
alegria_images = list(alegria_dir.glob("*"))[:5]  # Primeiras 5 imagens

for img_path in alegria_images:
    print(f"\nImagem: {img_path.name}")
    result = model.predict(str(img_path), confidence=40, overlap=30)
    result_dict = result.json()

    print(f"Predições: {len(result_dict['predictions'])}")
    for pred in result_dict['predictions']:
        print(f"  - {pred['class']}: {pred['confidence']:.2f}")

print("\n" + "="*70)
print("ANÁLISE DE CLASSES DETECTADAS")
print("="*70)

# Coleta todas as classes únicas detectadas
all_classes = set()

for img_dir, class_name in [(raiva_dir, "raiva"), (alegria_dir, "alegria")]:
    images = list(img_dir.glob("*"))[:10]  # Mais amostras

    for img_path in images:
        result = model.predict(str(img_path), confidence=40, overlap=30)
        result_dict = result.json()

        for pred in result_dict['predictions']:
            all_classes.add(pred['class'])

print(f"\nClasses únicas detectadas pelo modelo:")
for cls in sorted(all_classes):
    print(f"  - {cls}")

print("\n" + "="*70)
print("MAPEAMENTO SUGERIDO")
print("="*70)

print("\nBaseado nas classes detectadas, atualize emotion_mapping:")
print("emotion_mapping = {")
for cls in sorted(all_classes):
    cls_lower = cls.lower()
    if 'angry' in cls_lower or 'anger' in cls_lower:
        print(f"    '{cls}': 'raiva',  # Classe detectada pelo modelo")
    elif 'happy' in cls_lower or 'joy' in cls_lower:
        print(f"    '{cls}': 'alegria',  # Classe detectada pelo modelo")
    else:
        print(f"    '{cls}': None,  # Classe detectada mas não mapeada")
print("}")
