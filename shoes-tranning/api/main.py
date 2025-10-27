"""
API FastAPI para geração de imagens usando modelos Stable Diffusion com LoRA.

Endpoints:
- POST /api/generate: Gera imagens baseadas em prompt
- GET /api/models: Lista modelos disponíveis
- GET /api/prompts/examples: Retorna exemplos de prompts
- GET /health: Health check

Exemplo de uso:
    curl -X POST "http://localhost:8000/api/generate" \
         -H "Content-Type: application/json" \
         -d '{
               "model_name": "casual_shoes",
               "prompt": "A professional product photo of brown leather casual shoes",
               "num_images": 4,
               "num_inference_steps": 50,
               "guidance_scale": 7.5
             }'
"""

import os
import io
import base64
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

import torch
from PIL import Image
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from diffusers import StableDiffusionPipeline

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="Shoes Image Generation API",
    description="API para geração de imagens de sapatos usando Stable Diffusion com LoRA",
    version="1.0.0"
)

# Configurar CORS para permitir requests do React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite e Create React App
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração de diretórios
BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "training" / "outputs"
GENERATED_IMAGES_DIR = BASE_DIR / "api" / "generated_images"
GENERATED_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Cache de modelos carregados
models_cache = {}


# Modelos Pydantic para validação de requests/responses
class GenerateRequest(BaseModel):
    """Request para geração de imagens."""
    model_name: str = Field(
        ...,
        description="Nome do modelo a usar (ex: 'casual_shoes', 'base')",
        example="casual_shoes"
    )
    prompt: str = Field(
        ...,
        description="Prompt de texto descrevendo a imagem desejada",
        min_length=10,
        max_length=500,
        example="A professional product photo of brown leather casual shoes on white background"
    )
    num_images: int = Field(
        default=1,
        ge=1,
        le=8,
        description="Número de imagens a gerar (1-8)"
    )
    num_inference_steps: int = Field(
        default=50,
        ge=10,
        le=100,
        description="Número de steps de inferência (qualidade)"
    )
    guidance_scale: float = Field(
        default=7.5,
        ge=1.0,
        le=20.0,
        description="Escala de guidance (aderência ao prompt)"
    )
    seed: Optional[int] = Field(
        default=None,
        description="Seed para reprodutibilidade (opcional)"
    )


class GeneratedImage(BaseModel):
    """Representa uma imagem gerada."""
    image_data: str = Field(..., description="Imagem em base64")
    seed: int = Field(..., description="Seed usada para gerar a imagem")
    filename: str = Field(..., description="Nome do arquivo salvo")


class GenerateResponse(BaseModel):
    """Response de geração de imagens."""
    success: bool
    model_name: str
    prompt: str
    num_images: int
    images: List[GeneratedImage]
    generation_time_seconds: float
    metadata: dict


class ModelInfo(BaseModel):
    """Informações sobre um modelo disponível."""
    name: str
    display_name: str
    description: str
    path: str
    available: bool


class PromptExample(BaseModel):
    """Exemplo de prompt."""
    category: str
    title: str
    prompt: str
    description: str


# Funções auxiliares
def get_available_models() -> List[ModelInfo]:
    """
    Lista todos os modelos disponíveis no diretório de outputs.

    Detecta:
    - Modelo base (SD 1.5)
    - Modelos fine-tuned (final_pipeline/)
    - Checkpoints convertidos (checkpoint_pipelines/)

    Returns:
        Lista de informações sobre modelos disponíveis
    """
    models = [
        ModelInfo(
            name="base",
            display_name="Stable Diffusion 1.5 (Base)",
            description="Modelo base sem fine-tuning",
            path="runwayml/stable-diffusion-v1-5",
            available=True
        )
    ]

    # Procurar modelos fine-tuned e checkpoints
    if MODELS_DIR.exists():
        for model_dir in MODELS_DIR.iterdir():
            if not model_dir.is_dir():
                continue

            # 1. Modelo final (final_pipeline/)
            final_pipeline = model_dir / "final_pipeline"
            if final_pipeline.exists() and (final_pipeline / "model_index.json").exists():
                models.append(ModelInfo(
                    name=f"{model_dir.name}/final",
                    display_name=f"{model_dir.name.replace('_', ' ').title()} (Final)",
                    description=f"Modelo final treinado: {model_dir.name}",
                    path=str(final_pipeline),
                    available=True
                ))

            # 2. Checkpoints convertidos (checkpoint_pipelines/)
            checkpoint_pipelines_dir = model_dir / "checkpoint_pipelines"
            if checkpoint_pipelines_dir.exists():
                for checkpoint_dir in sorted(checkpoint_pipelines_dir.iterdir()):
                    if checkpoint_dir.is_dir() and (checkpoint_dir / "model_index.json").exists():
                        # Extrair step do nome do checkpoint
                        checkpoint_name = checkpoint_dir.name
                        step = checkpoint_name.split("-")[-1] if "-" in checkpoint_name else "?"

                        models.append(ModelInfo(
                            name=f"{model_dir.name}/checkpoint-{step}",
                            display_name=f"{model_dir.name.replace('_', ' ').title()} (Step {step})",
                            description=f"Checkpoint intermediário no step {step}",
                            path=str(checkpoint_dir),
                            available=True
                        ))

    return models


def load_model(model_name: str) -> StableDiffusionPipeline:
    """
    Carrega modelo Stable Diffusion (com cache).

    Suporta:
    - "base": Modelo base SD 1.5
    - "model_name/final": Modelo final treinado
    - "model_name/checkpoint-N": Checkpoint intermediário convertido

    Args:
        model_name: Nome do modelo a carregar

    Returns:
        Pipeline do Stable Diffusion carregado

    Raises:
        HTTPException: Se modelo não for encontrado
    """
    # Verificar cache
    if model_name in models_cache:
        logger.info(f"Modelo '{model_name}' carregado do cache")
        return models_cache[model_name]

    logger.info(f"Carregando modelo '{model_name}'...")

    try:
        # Determinar caminho do modelo
        if model_name == "base":
            model_path = "runwayml/stable-diffusion-v1-5"

        elif "/" in model_name:
            # Formato: "model_name/final" ou "model_name/checkpoint-N"
            parts = model_name.split("/")
            base_model_name = parts[0]
            variant = parts[1]

            if variant == "final":
                model_path = MODELS_DIR / base_model_name / "final_pipeline"
            elif variant.startswith("checkpoint-"):
                step = variant.split("-")[1]
                model_path = MODELS_DIR / base_model_name / "checkpoint_pipelines" / f"checkpoint-{step}"
            else:
                raise ValueError(f"Variante desconhecida: {variant}")

            if not model_path.exists():
                raise FileNotFoundError(f"Modelo não encontrado: {model_path}")

        else:
            # Legado: tentar model_name/final_pipeline
            model_path = MODELS_DIR / model_name / "final_pipeline"
            if not model_path.exists():
                raise FileNotFoundError(f"Modelo não encontrado: {model_path}")

        # Carregar pipeline
        pipeline = StableDiffusionPipeline.from_pretrained(
            str(model_path) if model_name != "base" else model_path,
            torch_dtype=torch.float32,  # MPS requer float32
            safety_checker=None
        )

        # Mover para device apropriado
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        pipeline = pipeline.to(device)

        # Configurar para menor uso de memória
        if device == "mps":
            pipeline.enable_attention_slicing()

        # Cache do modelo
        models_cache[model_name] = pipeline

        logger.info(f"Modelo '{model_name}' carregado com sucesso no device: {device}")
        return pipeline

    except Exception as e:
        logger.error(f"Erro ao carregar modelo '{model_name}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao carregar modelo: {str(e)}"
        )


def image_to_base64(image: Image.Image) -> str:
    """
    Converte imagem PIL para base64 string.

    Args:
        image: Imagem PIL

    Returns:
        String base64 da imagem
    """
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode()


def save_generated_image(image: Image.Image, model_name: str, seed: int) -> str:
    """
    Salva imagem gerada em disco.

    Args:
        image: Imagem PIL a salvar
        model_name: Nome do modelo usado
        seed: Seed usada na geração

    Returns:
        Caminho do arquivo salvo
    """
    # Sanitizar model_name para uso em filename (substituir "/" por "_")
    # Exemplo: "lora_casual_shoes/checkpoint-500" -> "lora_casual_shoes_checkpoint-500"
    safe_model_name = model_name.replace("/", "_")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_model_name}_{timestamp}_seed{seed}.png"
    filepath = GENERATED_IMAGES_DIR / filename

    image.save(filepath)
    logger.info(f"Imagem salva: {filepath}")

    return filename


# Endpoints
@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        Status da API
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "device": "mps" if torch.backends.mps.is_available() else "cpu",
        "models_cached": list(models_cache.keys())
    }


@app.get("/api/models", response_model=List[ModelInfo])
async def list_models():
    """
    Lista todos os modelos disponíveis.

    Returns:
        Lista de informações sobre modelos
    """
    try:
        models = get_available_models()
        logger.info(f"Listando {len(models)} modelos disponíveis")
        return models
    except Exception as e:
        logger.error(f"Erro ao listar modelos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/prompts/examples", response_model=List[PromptExample])
async def get_prompt_examples():
    """
    Retorna exemplos de prompts para geração de imagens.

    Returns:
        Lista de exemplos de prompts categorizados
    """
    examples = [
        # Cores Básicas
        PromptExample(
            category="Cores Básicas",
            title="Sapato Preto",
            prompt="A professional product photo of black casual shoes on white background, high quality, product photography",
            description="Sapato casual preto clássico"
        ),
        PromptExample(
            category="Cores Básicas",
            title="Sapato Branco",
            prompt="A professional product photo of white casual sneakers on white background, centered, product photography",
            description="Tênis casual branco clean"
        ),
        PromptExample(
            category="Cores Básicas",
            title="Sapato Marrom",
            prompt="A professional product photo of brown leather casual shoes on white background, high quality",
            description="Sapato de couro marrom elegante"
        ),
        PromptExample(
            category="Cores Básicas",
            title="Sapato Azul",
            prompt="A professional product photo of navy blue casual shoes on white background, modern design, product photography",
            description="Sapato casual azul marinho moderno"
        ),

        # Materiais
        PromptExample(
            category="Materiais",
            title="Couro Premium",
            prompt="A professional product photo of premium brown leather casual shoes on white background, high quality leather texture, product photography",
            description="Sapato de couro premium com textura visível"
        ),
        PromptExample(
            category="Materiais",
            title="Canvas/Lona",
            prompt="A professional product photo of beige canvas casual shoes on white background, fabric texture, product photography",
            description="Sapato de lona bege confortável"
        ),
        PromptExample(
            category="Materiais",
            title="Suede",
            prompt="A professional product photo of gray suede casual shoes on white background, soft texture, product photography",
            description="Sapato de camurça cinza macio"
        ),

        # Estilos
        PromptExample(
            category="Estilos",
            title="Sneaker Esportivo",
            prompt="A professional product photo of white and gray sporty casual sneakers on white background, modern athletic design, product photography",
            description="Tênis casual esportivo moderno"
        ),
        PromptExample(
            category="Estilos",
            title="Loafer Elegante",
            prompt="A professional product photo of black leather casual loafers on white background, elegant design, product photography",
            description="Mocassim casual elegante"
        ),
        PromptExample(
            category="Estilos",
            title="Oxford Casual",
            prompt="A professional product photo of brown leather casual oxford shoes on white background, classic design, product photography",
            description="Oxford casual clássico"
        ),
        PromptExample(
            category="Estilos",
            title="Slip-on",
            prompt="A professional product photo of navy blue casual slip-on shoes on white background, minimalist design, product photography",
            description="Slip-on minimalista azul marinho"
        ),

        # Detalhes Especiais
        PromptExample(
            category="Detalhes Especiais",
            title="Com Cadarço Colorido",
            prompt="A professional product photo of white casual shoes with red laces on white background, product photography",
            description="Sapato branco com cadarço vermelho destacado"
        ),
        PromptExample(
            category="Detalhes Especiais",
            title="Sola Contrastante",
            prompt="A professional product photo of gray casual shoes with white sole on white background, modern design, product photography",
            description="Sapato cinza com sola branca contrastante"
        ),
        PromptExample(
            category="Detalhes Especiais",
            title="Design Bicolor",
            prompt="A professional product photo of black and white casual shoes on white background, two-tone design, product photography",
            description="Sapato casual com design bicolor"
        ),
    ]

    return examples


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_images(request: GenerateRequest):
    """
    Gera imagens baseadas no prompt fornecido.

    Args:
        request: Requisição com parâmetros de geração

    Returns:
        Response com imagens geradas em base64

    Raises:
        HTTPException: Se houver erro na geração
    """
    start_time = datetime.now()

    try:
        logger.info(f"Iniciando geração: modelo='{request.model_name}', "
                   f"prompt='{request.prompt[:50]}...', num_images={request.num_images}")

        # Carregar modelo
        pipeline = load_model(request.model_name)

        # Configurar generator para reprodutibilidade
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        seed = request.seed if request.seed is not None else torch.randint(0, 2**32, (1,)).item()
        generator = torch.Generator(device=device).manual_seed(seed)

        # Gerar imagens
        generated_images = []

        for i in range(request.num_images):
            # Usar seed diferente para cada imagem (se não especificado)
            current_seed = seed + i if request.seed is None else seed

            generator = torch.Generator(device=device).manual_seed(current_seed)

            logger.info(f"Gerando imagem {i+1}/{request.num_images} (seed={current_seed})")

            # Gerar imagem
            output = pipeline(
                prompt=request.prompt,
                num_inference_steps=request.num_inference_steps,
                guidance_scale=request.guidance_scale,
                generator=generator,
                num_images_per_prompt=1
            )

            image = output.images[0]

            # Converter para base64
            image_base64 = image_to_base64(image)

            # Salvar imagem
            filename = save_generated_image(image, request.model_name, current_seed)

            generated_images.append(GeneratedImage(
                image_data=image_base64,
                seed=current_seed,
                filename=filename
            ))

        # Calcular tempo de geração
        generation_time = (datetime.now() - start_time).total_seconds()

        logger.info(f"Geração concluída: {request.num_images} imagens em {generation_time:.2f}s")

        return GenerateResponse(
            success=True,
            model_name=request.model_name,
            prompt=request.prompt,
            num_images=request.num_images,
            images=generated_images,
            generation_time_seconds=generation_time,
            metadata={
                "num_inference_steps": request.num_inference_steps,
                "guidance_scale": request.guidance_scale,
                "device": device,
                "timestamp": datetime.now().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"Erro na geração de imagens: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar imagens: {str(e)}"
        )


@app.on_event("startup")
async def startup_event():
    """
    Evento executado ao iniciar a API.
    Pode pré-carregar modelos se necessário.
    """
    logger.info("=" * 50)
    logger.info("Shoes Image Generation API - Iniciando")
    logger.info("=" * 50)
    logger.info(f"Base directory: {BASE_DIR}")
    logger.info(f"Models directory: {MODELS_DIR}")
    logger.info(f"Generated images directory: {GENERATED_IMAGES_DIR}")

    # Verificar device disponível
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    logger.info(f"Device: {device}")

    # Listar modelos disponíveis
    models = get_available_models()
    logger.info(f"Modelos disponíveis: {len(models)}")
    for model in models:
        logger.info(f"  - {model.name}: {model.display_name} ({'disponível' if model.available else 'indisponível'})")

    logger.info("API pronta para receber requests!")
    logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento executado ao desligar a API.
    Limpa cache de modelos.
    """
    logger.info("Encerrando API...")
    models_cache.clear()
    logger.info("Cache de modelos limpo. API encerrada.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
