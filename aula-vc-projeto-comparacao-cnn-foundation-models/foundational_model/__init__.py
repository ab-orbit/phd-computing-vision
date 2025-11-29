"""
Foundational Model - Google Vision API Object Segmentation

Módulo para detecção e segmentação de objetos em imagens usando
a Google Cloud Vision API.

Uso básico:
    from foundational_model import GoogleVisionObjectSegmentation, DetectedObject

    segmenter = GoogleVisionObjectSegmentation()
    objects = segmenter.detect_objects("image.jpg")
"""

from .object_segmentation import (
    GoogleVisionObjectSegmentation,
    DetectedObject
)

__version__ = "1.0.0"
__author__ = "Sistema de Aprendizagem"

__all__ = [
    "GoogleVisionObjectSegmentation",
    "DetectedObject"
]