# ─────────────────────────────────────────────
#  Stage 1: Builder — instala dependencias
# ─────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Instalar dependencias del sistema solo las necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ─────────────────────────────────────────────
#  Stage 2: Runtime — imagen final ligera
# ─────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Copiar paquetes instalados desde el builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar solo el código necesario para producción
COPY backend/ .
COPY frontend/ ./frontend/

# Cloud Run inyecta $PORT automáticamente (default 8080)
# --workers 1 es correcto para Cloud Run (escala horizontal, no vertical)
CMD exec uvicorn main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8080} \
    --workers 1 \
    --loop uvloop \
    --log-level info
