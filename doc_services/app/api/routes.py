"""
Endpoints da API REST.

Define rotas HTTP para análise de documentos científicos.
"""

import logging
import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.models import AnalysisResult
from app.services import DocumentAnalysisOrchestrator, InvalidDocumentError
from app.api.dependencies import get_orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Document Analysis"])


@router.post(
    "/analyze",
    response_model=AnalysisResult,
    summary="Analisa documento científico",
    description="""
    Executa análise completa de documento:
    - UC1: Classifica e valida se é artigo científico
    - UC2: Detecta parágrafos usando docling
    - UC3: Analisa texto e conta palavras frequentes
    - UC4: Gera relatório de conformidade
    """
)
async def analyze_document(
    file: UploadFile = File(..., description="Arquivo PDF ou imagem"),
    orchestrator: DocumentAnalysisOrchestrator = Depends(get_orchestrator)
) -> AnalysisResult:
    """
    Analisa documento científico.

    EXPLICAÇÃO EDUCATIVA:
    Endpoint principal que:
    1. Recebe arquivo via multipart/form-data
    2. Salva temporariamente
    3. Executa pipeline de análise
    4. Retorna resultado JSON
    5. Remove arquivo temporário
    """
    # Validar formato
    allowed_formats = ["pdf", "png", "jpg", "jpeg", "tiff", "tif"]
    file_ext = Path(file.filename).suffix.lower().lstrip(".")

    if file_ext not in allowed_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato não suportado: {file_ext}. Use: {', '.join(allowed_formats)}"
        )

    # Salvar arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
        tmp_path = Path(tmp.name)
        content = await file.read()
        tmp.write(content)

    try:
        logger.info(f"Analisando arquivo: {file.filename}")

        # Executar análise passando o nome original do arquivo
        # EXPLICAÇÃO: tmp_path.name seria "tmpXYZ.pdf", mas queremos exibir
        # o nome original que o usuário enviou (ex: "artigo.pdf")
        result = await orchestrator.analyze_document(
            tmp_path,
            original_filename=file.filename
        )

        logger.info(f"Análise concluída: {file.filename}")

        return result

    except InvalidDocumentError as e:
        logger.warning(f"Documento inválido: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

    except Exception as e:
        logger.error(f"Erro ao analisar: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

    finally:
        # Remover arquivo temporário
        if tmp_path.exists():
            tmp_path.unlink()


@router.post(
    "/classify",
    summary="Classifica documento (apenas UC1)",
    description="Executa apenas classificação, retorna se é artigo científico"
)
async def classify_document(
    file: UploadFile = File(...),
    orchestrator: DocumentAnalysisOrchestrator = Depends(get_orchestrator)
) -> dict:
    """
    Classifica documento (apenas UC1).

    EXPLICAÇÃO EDUCATIVA:
    Endpoint simplificado que executa apenas classificação.
    Útil quando só precisa validar se é artigo científico.
    """
    # Validar formato
    file_ext = Path(file.filename).suffix.lower().lstrip(".")
    if file_ext not in ["pdf", "png", "jpg", "jpeg", "tiff", "tif"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato não suportado: {file_ext}"
        )

    # Salvar temporariamente
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
        tmp_path = Path(tmp.name)
        content = await file.read()
        tmp.write(content)

    try:
        is_scientific, confidence = await orchestrator.classification_service.is_scientific_paper(
            tmp_path
        )

        return {
            "filename": file.filename,
            "is_scientific_paper": is_scientific,
            "confidence": confidence
        }

    except Exception as e:
        logger.error(f"Erro na classificação: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    finally:
        if tmp_path.exists():
            tmp_path.unlink()


@router.get(
    "/health",
    summary="Health check",
    description="Verifica se API está operacional"
)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Document Analysis API",
        "version": "1.0.0"
    }
