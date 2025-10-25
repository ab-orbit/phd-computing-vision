"""
API FastAPI para Classificação de Documentos.

Esta API fornece endpoints para classificar documentos em tipos específicos
usando modelos de machine learning e opcionalmente LLMs.
"""

import time
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import (
    ClassificationResponse,
    HealthResponse,
    ErrorResponse,
    ErrorDetail,
)

# ============================================================================
# Configuração da Aplicação
# ============================================================================

# Timestamp de início da aplicação
START_TIME = time.time()

app = FastAPI(
    title="Document Classification API",
    description="""
    API para classificação automática de documentos em tipos específicos.

    ## Funcionalidades

    * **Classificação de Documentos**: Identifica o tipo de documento (email, contrato, publicação, etc)
    * **Múltiplos Formatos**: Suporta PDF, PNG, JPG, TIFF
    * **Top-K Predictions**: Retorna as 3 classificações mais prováveis
    * **Metadados Detalhados**: Extrai informações sobre o documento
    * **Rastreamento LLM**: Monitora uso de tokens e custos quando LLM é usado

    ## Tipos de Documentos Suportados

    * advertisement, budget, email, file_folder, form
    * handwritten, invoice, letter, memo, news_article
    * presentation, questionnaire, resume, scientific_publication
    * scientific_report, specification, contract
    """,
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@docclassification.com",
    },
    license_info={
        "name": "MIT",
    },
)

# CORS middleware
# EXPLICAÇÃO EDUCATIVA:
# CORS (Cross-Origin Resource Sharing) permite que aplicações frontend
# rodando em uma porta/domínio diferente possam fazer requisições para esta API.
# Sem CORS, navegadores bloqueiam requisições entre diferentes origens por segurança.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "*"  # Permite todas as origens (usar apenas em desenvolvimento)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests por 1 hora
)


# ============================================================================
# Incluir Routers - SPEC.MD (UC1-UC4)
# ============================================================================

# EXPLICAÇÃO EDUCATIVA:
# Os endpoints do spec.md (análise de documentos científicos com UC1-UC4)
# estão implementados em app/api/routes.py e são incluídos aqui.
# Isso mantém o código modular e separado por funcionalidade.
try:
    from app.api.routes import router as spec_router
    app.include_router(spec_router)
    print("[INFO] Endpoints do spec.md (UC1-UC4) carregados em /api/v1/")
except Exception as e:
    print(f"[WARNING] Não foi possível carregar endpoints do spec.md: {e}")


# ============================================================================
# Endpoints - Sistema de Classificação Original
# ============================================================================

@app.get(
    "/",
    tags=["Root"],
    summary="Root endpoint",
    description="Informações básicas sobre a API"
)
async def root():
    """Endpoint raiz da API."""
    return {
        "name": "Document Classification API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs",
        "health": "/health"
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check",
    description="Verifica o status e disponibilidade dos serviços"
)
async def health_check():
    """
    Verifica o status de saúde da API.

    Retorna informações sobre:
    - Status geral do serviço
    - Tempo de atividade
    - Disponibilidade dos modelos
    - Disponibilidade do serviço LLM
    """
    uptime = time.time() - START_TIME

    # TODO: Implementar checagem real dos serviços
    models_loaded = True  # Placeholder
    llm_available = True  # Placeholder

    # Determinar status
    if models_loaded and llm_available:
        service_status = "healthy"
    elif models_loaded:
        service_status = "degraded"
    else:
        service_status = "unhealthy"

    return HealthResponse(
        status=service_status,
        version="1.0.0",
        uptime_seconds=uptime,
        models_loaded=models_loaded,
        llm_available=llm_available,
        timestamp=datetime.utcnow()
    )


@app.post(
    "/classify",
    response_model=ClassificationResponse,
    tags=["Classification"],
    summary="Classificar documento",
    description="Classifica um documento enviado e retorna o tipo mais provável",
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Documento classificado com sucesso",
            "model": ClassificationResponse,
        },
        400: {
            "description": "Requisição inválida",
            "model": ErrorResponse,
        },
        413: {
            "description": "Arquivo muito grande",
            "model": ErrorResponse,
        },
        415: {
            "description": "Formato de arquivo não suportado",
            "model": ErrorResponse,
        },
        500: {
            "description": "Erro interno do servidor",
            "model": ErrorResponse,
        },
    }
)
async def classify_document(
    file: UploadFile = File(
        ...,
        description="Arquivo do documento (PDF ou imagem)"
    ),
    use_llm: bool = Form(
        default=False,
        description="Usar LLM para análise adicional"
    ),
    include_alternatives: bool = Form(
        default=True,
        description="Incluir top 3 alternativas"
    ),
    extract_metadata: bool = Form(
        default=True,
        description="Extrair metadados detalhados"
    ),
    confidence_threshold: float = Form(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Threshold mínimo de confiança"
    )
):
    """
    Classifica um documento enviado.

    **Funcionamento**:
    1. Recebe o arquivo do documento
    2. Valida formato e tamanho
    3. Processa com modelo de classificação
    4. Opcionalmente usa LLM para validação
    5. Extrai metadados do documento
    6. Retorna resultado com top-K predições

    **Exemplo de uso**:
    ```python
    import requests

    files = {'file': open('documento.pdf', 'rb')}
    data = {
        'use_llm': True,
        'include_alternatives': True,
        'extract_metadata': True,
        'confidence_threshold': 0.7
    }

    response = requests.post(
        'http://localhost:8000/classify',
        files=files,
        data=data
    )

    result = response.json()
    print(f"Tipo: {result['predicted_type']}")
    print(f"Probabilidade: {result['probability']:.2%}")
    ```

    **Argumentos**:
    - **file**: Arquivo do documento (PDF, PNG, JPG, TIFF)
    - **use_llm**: Se True, usa LLM para análise complementar
    - **include_alternatives**: Se True, retorna top 3 alternativas
    - **extract_metadata**: Se True, extrai metadados detalhados
    - **confidence_threshold**: Threshold mínimo de confiança (0.0 - 1.0)

    **Retorna**:
    - **predicted_type**: Tipo de documento predito
    - **probability**: Probabilidade da predição
    - **alternatives**: Top 3 tipos alternativos
    - **document_metadata**: Metadados do documento
    - **llm_metadata**: Metadados do LLM (se usado)
    """

    request_id = f"req_{uuid.uuid4().hex[:16]}"
    start_time = time.time()

    try:
        # Validar formato do arquivo
        content_type = file.content_type
        filename = file.filename

        # EXPLICAÇÃO EDUCATIVA:
        # Alguns clientes (curl, browsers) enviam TIFF como 'application/octet-stream'.
        # Vamos detectar o formato pela extensão do arquivo como fallback.
        file_ext = filename.lower().split('.')[-1] if filename else ''

        # Mapear extensão para content-type correto
        ext_to_mime = {
            'pdf': 'application/pdf',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'tif': 'image/tiff',
            'tiff': 'image/tiff'
        }

        # Se content_type for genérico, usar extensão
        if content_type in ['application/octet-stream', None] and file_ext in ext_to_mime:
            content_type = ext_to_mime[file_ext]

        # Validar formato
        supported_formats = ['application/pdf', 'image/png', 'image/jpeg', 'image/tiff', 'image/tif']

        if content_type not in supported_formats:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Formato não suportado: {content_type}. Use: PDF, PNG, JPG, TIFF"
            )

        # Ler conteúdo do arquivo
        file_content = await file.read()
        file_size = len(file_content)

        # Validar tamanho (máximo 50MB)
        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Arquivo muito grande: {file_size} bytes (máximo: {MAX_FILE_SIZE})"
            )

        # Classificação com LLM
        processing_time = (time.time() - start_time) * 1000  # ms

        from app.models.schemas import (
            DocumentType,
            ClassificationScore,
            DocumentMetadata,
            FileFormat,
        )

        predicted_type = None
        probability = 0.0
        confidence_level = "low"
        alternatives_list = []
        llm_metadata_result = None

        # EXPLICAÇÃO EDUCATIVA:
        # A API Anthropic (Claude) só aceita imagens nos formatos:
        # JPEG, PNG, GIF, WebP. TIFF não é suportado.
        # Se o usuário tentar usar LLM com TIFF, retornamos erro claro.
        if use_llm and content_type in ['image/tiff', 'image/tif']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Formato TIFF não é suportado com análise LLM. "
                    "A API Anthropic aceita apenas: JPEG, PNG, GIF, WebP. "
                    "Tente usar use_llm=false ou converter para JPEG/PNG."
                )
            )

        # Se use_llm=True, usar Anthropic para classificação
        if use_llm:
            import base64
            from app.core.config import settings
            from app.services.llm_anthropic import create_anthropic_service
            from app.services.llm_base import LLMServiceError

            # Verificar se API key está configurada
            if not settings.ANTHROPIC_API_KEY:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="ANTHROPIC_API_KEY não configurada. Configure no arquivo .env"
                )

            try:
                # Criar service Anthropic
                llm_service = create_anthropic_service(
                    api_key=settings.ANTHROPIC_API_KEY,
                    model=settings.ANTHROPIC_MODEL
                )

                # Lista de todos os tipos disponíveis
                available_types = [t.value for t in DocumentType]

                # Preparar dados da imagem para análise visual
                image_data = None
                if content_type.startswith('image/'):
                    # Converter imagem para base64
                    base64_data = base64.b64encode(file_content).decode('utf-8')
                    image_data = {
                        "base64_data": base64_data,
                        "mime_type": content_type
                    }

                # Classificar usando LLM (com análise visual se for imagem)
                llm_result = await llm_service.classify_document(
                    document_name=filename,
                    available_types=available_types,
                    features=None,  # TODO: Adicionar features quando layout analyzer estiver pronto
                    image_data=image_data  # Passar imagem para análise visual
                )

                # Extrair resultados
                predicted_type = DocumentType(llm_result["predicted_type"])
                probability = float(llm_result.get("confidence", 0.5))
                llm_metadata_result = llm_result["llm_metadata"]

                # Determinar nível de confiança
                if probability >= 0.8:
                    confidence_level = "high"
                elif probability >= 0.5:
                    confidence_level = "medium"
                else:
                    confidence_level = "low"

                # Gerar alternativas (mock por enquanto, pois LLM retorna apenas 1 predição)
                # TODO: Melhorar para retornar top-K do LLM ou combinar com heurísticas
                if include_alternatives:
                    # Criar alternativas fictícias com probabilidades menores
                    remaining_prob = 1.0 - probability
                    alt_types = [t for t in DocumentType if t != predicted_type][:3]

                    for i, alt_type in enumerate(alt_types):
                        alt_prob = remaining_prob * (0.5 ** (i + 1))
                        alt_conf = "low"
                        alternatives_list.append(
                            ClassificationScore(
                                document_type=alt_type,
                                probability=alt_prob,
                                confidence=alt_conf
                            )
                        )

            except LLMServiceError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro ao classificar com LLM: {str(e)}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro inesperado na classificação LLM: {str(e)}"
                )
        else:
            # Classificação sem LLM (mock)
            # TODO: Implementar classificador heurístico
            predicted_type = DocumentType.SCIENTIFIC_PUBLICATION
            probability = 0.75
            confidence_level = "medium"

            if include_alternatives:
                alternatives_list = [
                    ClassificationScore(
                        document_type=DocumentType.SCIENTIFIC_REPORT,
                        probability=0.15,
                        confidence="low"
                    ),
                    ClassificationScore(
                        document_type=DocumentType.PRESENTATION,
                        probability=0.07,
                        confidence="low"
                    ),
                    ClassificationScore(
                        document_type=DocumentType.SPECIFICATION,
                        probability=0.03,
                        confidence="low"
                    ),
                ]

        # Determinar formato do arquivo
        file_format = FileFormat.PDF
        if content_type == "image/png":
            file_format = FileFormat.PNG
        elif content_type in ["image/jpeg", "image/jpg"]:
            file_format = FileFormat.JPG
        elif content_type in ["image/tiff", "image/tif"]:
            file_format = FileFormat.TIFF

        # Montar resposta
        response = ClassificationResponse(
            predicted_type=predicted_type,
            probability=probability,
            confidence=confidence_level,
            alternatives=alternatives_list,
            document_metadata=DocumentMetadata(
                file_name=filename,
                file_format=file_format,
                file_size_bytes=file_size,
                file_size_human=format_file_size(file_size),
                mime_type=content_type,
                num_pages=None,  # TODO: Extrair de PDF quando implementado
                processing_time_ms=processing_time,
            ),
            llm_metadata=llm_metadata_result,
            request_id=request_id,
            timestamp=datetime.utcnow(),
            api_version="1.0.0"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        # Log do erro (em produção, usar logging adequado)
        print(f"Erro ao processar documento: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar documento: {str(e)}"
        )


@app.post(
    "/classify/batch",
    tags=["Classification"],
    summary="Classificar múltiplos documentos",
    description="Classifica múltiplos documentos em lote",
    status_code=status.HTTP_501_NOT_IMPLEMENTED
)
async def classify_batch():
    """
    Endpoint para classificação em lote.

    TODO: Implementar processamento em lote de documentos.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Classificação em lote não implementada ainda"
    )


@app.get(
    "/models",
    tags=["Models"],
    summary="Listar modelos disponíveis",
    description="Lista todos os modelos de classificação disponíveis"
)
async def list_models():
    """
    Lista informações sobre os modelos disponíveis.

    TODO: Implementar listagem de modelos.
    """
    return {
        "models": [
            {
                "name": "DocLayout-YOLO",
                "version": "1.2.0",
                "type": "layout_analysis",
                "loaded": True
            },
            {
                "name": "Heuristic Classifier",
                "version": "1.2.0",
                "type": "rule_based",
                "loaded": True
            }
        ]
    }


@app.get(
    "/document-types",
    tags=["Information"],
    summary="Listar tipos de documentos",
    description="Lista todos os tipos de documentos suportados"
)
async def list_document_types():
    """
    Lista todos os tipos de documentos suportados pela API.
    """
    from app.models.schemas import DocumentType

    types = [
        {
            "type": doc_type.value,
            "display_name": doc_type.value.replace("_", " ").title(),
            "description": get_document_type_description(doc_type)
        }
        for doc_type in DocumentType
    ]

    return {
        "total": len(types),
        "document_types": types
    }


# ============================================================================
# Funções Auxiliares
# ============================================================================

def format_file_size(size_bytes: int) -> str:
    """
    Formata tamanho de arquivo em formato legível.

    **Argumentos**:
        size_bytes: Tamanho em bytes

    **Retorna**:
        String formatada (ex: "2.3 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def get_document_type_description(doc_type) -> str:
    """
    Retorna descrição de um tipo de documento.

    **Argumentos**:
        doc_type: Enum DocumentType

    **Retorna**:
        String com descrição
    """
    descriptions = {
        "advertisement": "Anúncios publicitários e propagandas",
        "budget": "Planilhas de orçamento e documentos financeiros",
        "email": "Emails impressos ou digitalizados",
        "file_folder": "Capas de pastas e arquivos",
        "form": "Formulários diversos",
        "handwritten": "Documentos manuscritos",
        "invoice": "Notas fiscais e faturas",
        "letter": "Cartas formais",
        "memo": "Memorandos internos",
        "news_article": "Artigos de jornal",
        "presentation": "Slides de apresentação",
        "questionnaire": "Questionários e pesquisas",
        "resume": "Currículos",
        "scientific_publication": "Artigos científicos e papers",
        "scientific_report": "Relatórios técnicos e científicos",
        "specification": "Documentos de especificação técnica",
        "contract": "Contratos legais",
    }

    return descriptions.get(doc_type.value, "Tipo de documento")


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Handler para exceções HTTP.

    EXPLICAÇÃO EDUCATIVA:
    Captura erros HTTP (400, 404, 500, etc) e retorna resposta JSON formatada.
    Converte datetime para string ISO format para evitar erro de serialização JSON.
    """
    error_response = ErrorResponse(
        error=True,
        error_type="http_error",
        errors=[
            ErrorDetail(
                code=f"HTTP_{exc.status_code}",
                message=exc.detail,
            )
        ],
        request_id=f"req_{uuid.uuid4().hex[:16]}",
        timestamp=datetime.utcnow()
    )

    # Converter para dict e serializar datetime manualmente
    response_dict = error_response.model_dump()
    if 'timestamp' in response_dict and isinstance(response_dict['timestamp'], datetime):
        response_dict['timestamp'] = response_dict['timestamp'].isoformat()

    return JSONResponse(
        status_code=exc.status_code,
        content=response_dict
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Handler para exceções gerais.

    EXPLICAÇÃO EDUCATIVA:
    Captura qualquer exceção não tratada e retorna erro 500.
    Evita que o servidor quebre completamente em caso de erro inesperado.
    """
    error_response = ErrorResponse(
        error=True,
        error_type="internal_error",
        errors=[
            ErrorDetail(
                code="INTERNAL_SERVER_ERROR",
                message=str(exc),
            )
        ],
        request_id=f"req_{uuid.uuid4().hex[:16]}",
        timestamp=datetime.utcnow()
    )

    # Converter para dict e serializar datetime manualmente
    response_dict = error_response.model_dump()
    if 'timestamp' in response_dict and isinstance(response_dict['timestamp'], datetime):
        response_dict['timestamp'] = response_dict['timestamp'].isoformat()

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_dict
    )


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Executado ao iniciar a aplicação."""
    print("=" * 80)
    print("Document Classification API - Inicializando")
    print("=" * 80)
    print(f"Versão: 1.0.0")
    print(f"Documentação: http://localhost:8000/docs")
    print(f"Health Check: http://localhost:8000/health")
    print("=" * 80)

    # TODO: Carregar modelos
    # TODO: Inicializar conexão com LLM
    # TODO: Verificar dependências


@app.on_event("shutdown")
async def shutdown_event():
    """Executado ao desligar a aplicação."""
    print("=" * 80)
    print("Document Classification API - Encerrando")
    print("=" * 80)

    # TODO: Liberar recursos
    # TODO: Fechar conexões
    # TODO: Salvar estado se necessário


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
