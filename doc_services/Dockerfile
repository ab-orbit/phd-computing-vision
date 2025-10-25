# Multi-stage build para reduzir tamanho da imagem final

# Stage 1: Builder
FROM python:3.10-slim as builder

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /build

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


# Stage 2: Runtime
FROM python:3.10-slim

# Metadados da imagem
LABEL maintainer="support@docclassification.com"
LABEL description="Document Classification API"
LABEL version="1.0.0"

# Instalar apenas dependências de runtime
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN useradd -m -u 1000 apiuser

# Copiar dependências Python do builder
COPY --from=builder /root/.local /home/apiuser/.local

# Criar diretórios necessários
WORKDIR /app
RUN mkdir -p /app/logs /app/models && \
    chown -R apiuser:apiuser /app

# Copiar código da aplicação
COPY --chown=apiuser:apiuser app/ /app/app/
COPY --chown=apiuser:apiuser .env.example /app/.env

# Garantir que scripts Python estão no PATH
ENV PATH=/home/apiuser/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Mudar para usuário não-root
USER apiuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
